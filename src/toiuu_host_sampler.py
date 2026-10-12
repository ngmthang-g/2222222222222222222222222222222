"""Stage N02/N03 genuine Windows host CPU/GPU sampler for independent Tối ưu.

Original evidence: psutil.cpu_percent(interval=None), nvidia-smi CSV,
background sampling and Tk-owner drawing. No process injection, no TLMP
game graphics commands, no fake percent. Exact original tick/history and
multi-GPU policy are UNKNOWN; local safe bounded decisions are labeled.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
from queue import Empty, Full, Queue
import subprocess
import threading
from time import monotonic


# Original embedded doc says 1 second/sample; original GRAPH_TICK_MS binding
# remains UNKNOWN. Do not certify 1:1 timer parity from this local choice.
LOCAL_SAMPLE_SECONDS = 1.0
NVIDIA_QUERY = (
    "nvidia-smi", "--query-gpu=utilization.gpu",
    "--format=csv,noheader,nounits",
)


@dataclass(frozen=True)
class HostPerformanceSample:
    cpu_percent: float | None
    gpu_percent: float | None
    timestamp: float


class _NativeCpuCounter:
    """Real system-wide Win32 fallback only if original psutil is missing."""

    def __init__(self):
        self._last = None
        self._kernel32 = None
        if os.name == "nt":
            import ctypes
            from ctypes import wintypes

            class FILETIME(ctypes.Structure):
                _fields_ = [
                    ("low", wintypes.DWORD), ("high", wintypes.DWORD),
                ]

            lib = ctypes.WinDLL("kernel32", use_last_error=True)
            func = lib.GetSystemTimes
            func.argtypes = [ctypes.POINTER(FILETIME)] * 3
            func.restype = wintypes.BOOL
            self._kernel32 = func
            self._struct = FILETIME
            self._ctypes = ctypes

    def sample(self) -> float | None:
        if self._kernel32 is None:
            return None
        a = self._struct()
        b = self._struct()
        c = self._struct()
        if not self._kernel32(self._ctypes.byref(a),
                              self._ctypes.byref(b),
                              self._ctypes.byref(c)):
            return None
        as_int = lambda t: (int(t.high) << 32) | int(t.low)
        now = as_int(a), as_int(b), as_int(c)
        before, self._last = self._last, now
        if before is None:
            return None
        idle = now[0] - before[0]
        total = now[1] - before[1] + now[2] - before[2]
        if total <= 0 or idle < 0:
            return None
        return max(0.0, min(100.0, 100 * (total - idle) / total))


def _read_gpu_nvidia_smi() -> float | None:
    """Documented NVIDIA query. Missing/failed output is UNKNOWN, not 0%."""
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
    try:
        proc = subprocess.run(
            NVIDIA_QUERY, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, check=False,
            timeout=2.0, creationflags=flags)
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    raw = proc.stdout.decode("utf-8", errors="replace")
    # Multiple-GPU original selection/aggregation is UNKNOWN. Use first
    # valid row for a local observed value, never pretend to represent all GPUs.
    for line in raw.splitlines():
        item = line.strip()
        if item.isascii() and item.isdecimal():
            value = int(item)
            if 0 <= value <= 100:
                return float(value)
    return None


class HostPerformanceSampler:
    """Single daemon background sampler, no Tk calls from thread.

    start_refresh/stop_refresh pause without restarting workers, avoiding
    races when the user switches between Notebook tabs quickly.
    """

    def __init__(self):
        self._active = threading.Event()
        self._closed = threading.Event()
        self._thread: threading.Thread | None = None
        self._queue: Queue[HostPerformanceSample] = Queue(maxsize=2)
        self._counter = None

    def start_refresh(self) -> bool:
        if self._closed.is_set():
            return False
        if self._thread is None:
            self._thread = threading.Thread(
                name="TLM-Independent-N02-N03-Host-Performance",
                target=self._loop, daemon=True)
            self._thread.start()
        self._active.set()
        return True

    def stop_refresh(self):
        self._active.clear()
        self.drain()
        
    def shutdown(self):
        self._closed.set()
        self._active.set()  # Wake stopped worker to observe close event.
        self.drain()

    def drain(self) -> HostPerformanceSample | None:
        latest = None
        try:
            while True:
                latest = self._queue.get_nowait()
        except Empty:
            pass
        return latest

    def _cpu_reader(self):
        try:
            import psutil
        except ImportError:
            psutil = None
        native = None
        if psutil is None:
            try:
                native = _NativeCpuCounter()
            except (OSError, AttributeError):
                native = None
        if psutil is not None:
            # Non-blocking priming read from original code signature.
            try:
                psutil.cpu_percent(interval=None)
            except (OSError, RuntimeError, ValueError):
                pass

            def read():
                try:
                    value = psutil.cpu_percent(interval=None)
                    return float(value) if 0 <= value <= 100 else None
                except (OSError, RuntimeError, ValueError):
                    return None
            return read
        return native.sample if native is not None else lambda: None

    def _loop(self):
        read_cpu = self._cpu_reader()
        while not self._closed.is_set():
            if not self._active.wait(timeout=0.25):
                continue
            if self._closed.is_set():
                break
            start = monotonic()
            cpu = read_cpu()
            gpu = _read_gpu_nvidia_smi()
            if self._closed.is_set() or not self._active.is_set():
                continue
            sample = HostPerformanceSample(cpu, gpu, monotonic())
            try:
                self._queue.put_nowait(sample)
            except Full:
                self.drain()
                try:
                    self._queue.put_nowait(sample)
                except Full:
                    pass
            elapsed = monotonic() - start
            remaining = max(0.0, LOCAL_SAMPLE_SECONDS - elapsed)
            # A paused tab does not need new monitoring samples.
            self._closed.wait(timeout=remaining)
