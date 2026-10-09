"""S19 / original C19 — bounded master-to-slave input model, NO GAME SENDER.

Verified: master client-coordinate scaling, serialized down/up queue, stale
slave lock watchdog (~10s), input stop on master/permission change.
NOT reconstructed: WM_MY_SYNC_KEY payload, live pynput listeners, DLL slave
blocking/unblocking, SendMessage input dispatcher, throttle/retry protocol.

This model will NEVER emit Win32 mouse/key messages: dispatch requires an
explicit injected sink + live HWND/PID verifier and is only used with the
S19 test-owned Tk adapter. A session is not a working TLM input-sync toggle.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import os
import threading
from typing import Callable, Mapping, Protocol

from start_polling import WindowSnapshot
from start_windows import GameWindow, is_game_candidate

WATCHDOG_UNLOCK_SECONDS = 10.0
INPUT_KEEPALIVE_SECONDS = 1.5  # original C19, NOT C18 layout worker
ORIGINAL_MOUSE_MOVE_THROTTLE = "UNKNOWN"
ORIGINAL_KEYBOARD_PAYLOAD = "UNKNOWN_WM_MY_SYNC_KEY"
SCALING_ROUNDING = "S19_LOCAL_INTEGER_FLOOR_NOT_ORIGINAL_VERIFIED"
VALID_MOUSE_BUTTONS = frozenset({"left", "right", "middle"})


@dataclass(frozen=True)
class ClientSize:
    width: int
    height: int

    def __post_init__(self):
        if (type(self.width) is not int or type(self.height) is not int
                or self.width <= 0 or self.height <= 0):
            raise ValueError("INVALID_CLIENT_RECT_SIZE")


def scale_client_point(x: int, y: int, master: ClientSize,
                       slave: ClientSize) -> tuple[int, int]:
    """Map relative master CLIENT pixels to slave CLIENT pixels.

    Original proves proportional mapping, not rounding. S19 uses integer
    floor and clamps to live slave bounds as a documented local policy.
    """
    if (type(x) is not int or type(y) is not int
            or not isinstance(master, ClientSize)
            or not isinstance(slave, ClientSize)):
        raise ValueError("INVALID_MASTER_CLIENT_POINT")
    if x < 0 or y < 0 or x >= master.width or y >= master.height:
        raise ValueError("MASTER_POINT_OUTSIDE_CLIENT")
    sx = min(slave.width - 1, x * slave.width // master.width)
    sy = min(slave.height - 1, y * slave.height // master.height)
    return sx, sy


@dataclass(frozen=True)
class InputEvent:
    sequence: int
    generation: int
    source: tuple[int, int]
    target: tuple[int, int]
    button: str
    action: str
    x: int
    y: int


class LiveIdentity(Protocol):
    def __call__(self, hwnd: int, pid: int) -> bool: ...


class InputSyncModel:
    """Explicit injection-only click planner; no default sender or listener.

    Authorization belongs to an independent verified shell; a caller MUST
    check it before starting and provide a live permission check for every
    dispatch. No native activation/blocking occurs inside this class.
    """

    def __init__(self):
        self._mutex = threading.RLock()
        self.active = False
        self.generation = 0
        self.master: tuple[int, int] | None = None
        self.slaves: tuple[tuple[int, int], ...] = ()
        self._events: deque[InputEvent] = deque()
        self._buttons: set[str] = set()  # logical planned down/up, NOT OS locks
        self._last_down_at: float | None = None
        self.last_stop = "INITIAL_DENY"
        self._serial = 0

    @property
    def pending(self) -> int:
        with self._mutex:
            return len(self._events)

    @property
    def planned_buttons(self) -> frozenset[str]:
        with self._mutex:
            return frozenset(self._buttons)

    def start(self, snapshot: WindowSnapshot, master: tuple[int, int],
              *, max_windows: int) -> bool:
        with self._mutex:
            self.stop("RESTART")
            if (not isinstance(snapshot, WindowSnapshot) or not snapshot.valid
                    or type(max_windows) is not int or max_windows <= 0):
                return False
            windows = snapshot.windows
            if not 2 <= len(windows) <= max_windows:
                return False
            if any(not isinstance(w, GameWindow) or w.hwnd <= 0 or w.pid <= 0
                   or not is_game_candidate(w.process_name,w.class_name,w.title)
                   for w in windows):
                return False
            identities = tuple((w.hwnd, w.pid) for w in windows)
            if len(set(identities)) != len(identities):
                return False
            if len({hwnd for hwnd, _ in identities}) != len(identities):
                return False
            if (type(master) is not tuple or len(master) != 2
                    or master not in identities):
                return False
            self.master = master
            self.slaves = tuple(i for i in identities if i != master)
            self.active = True
            self.last_stop = "ACTIVE_MODEL_ONLY"
            return True

    def queue_mouse(self, x: int, y: int, *, button: str, pressed: bool,
                    sizes: Mapping[tuple[int,int], ClientSize],
                    now: float) -> int:
        """Append ordered events for every slave; never dispatch on enqueue."""
        with self._mutex:
            if not self.active or self.master is None:
                return 0
            if (button not in VALID_MOUSE_BUTTONS or type(pressed) is not bool
                    or type(now) not in (int, float) or not isinstance(sizes, Mapping)):
                return 0
            if (pressed and button in self._buttons
                    or not pressed and button not in self._buttons):
                return 0  # repeated DOWN or orphan UP never mutates slaves
            try:
                msize = sizes[self.master]
                coords = [
                    (*target, *scale_client_point(x,y,msize,sizes[target]))
                    for target in self.slaves
                ]
            except (KeyError, ValueError, TypeError):
                return 0
            action = "down" if pressed else "up"
            for hwnd, pid, sx, sy in coords:
                self._serial += 1
                self._events.append(InputEvent(
                    self._serial, self.generation, self.master, (hwnd,pid),
                    button, action, sx, sy))
            if pressed:
                self._buttons.add(button)
                self._last_down_at = float(now)
            else:
                self._buttons.discard(button)
                if not self._buttons:
                    self._last_down_at = None
            return len(coords)

    def dispatch_one(self, *, sink: Callable[[InputEvent], None],
                     identity_ok: LiveIdentity,
                     permission_ok: Callable[[], bool]) -> InputEvent | None:
        """Exactly one FIFO item; explicit sink required, no native default.

        Holding the lock around validation+callback makes stop/revoke
        linearizable: once stop returns, no further callbacks can occur.
        Any identity/permission failure invalidates the ENTIRE pending batch.
        """
        if not all(callable(x) for x in (sink, identity_ok, permission_ok)):
            raise ValueError("S19_EXPLICIT_SINK_IDENTITY_PERMISSION_REQUIRED")
        with self._mutex:
            if not self.active or not self._events:
                return None
            event = self._events[0]
            try:
                valid = (permission_ok()
                         and self.master == event.source
                         and identity_ok(*event.source)
                         and identity_ok(*event.target))
            except Exception:
                valid = False
            if not valid:
                self.stop("REVOKED_OR_STALE_HWND")
                return None
            self._events.popleft()
            try:
                sink(event)
            except Exception:
                self.stop("TEST_SINK_EXCEPTION")
                raise
            return event

    def watchdog(self, now: float) -> bool:
        """Conservative S19 model safety: clear planned clicks after 10 s.

        This is NOT the original DLL slave unlock implementation; no actual
        native OS input lock is ever taken by this model.
        """
        with self._mutex:
            if (not self.active or self._last_down_at is None
                    or type(now) not in (int,float)):
                return False
            if float(now) - self._last_down_at < WATCHDOG_UNLOCK_SECONDS:
                return False
            self.stop("WATCHDOG_LOGICAL_RELEASE")
            return True

    def master_changed(self, new_master: tuple[int,int] | None = None) -> None:
        """C05: master change auto-stops input sync, never auto-restarts."""
        self.stop("MASTER_CHANGED")

    def stop(self, reason: str = "STOPPED") -> None:
        with self._mutex:
            self.generation += 1
            self.active = False
            self._events.clear()
            self._buttons.clear()
            self._last_down_at = None
            self.master = None
            self.slaves = ()
            self.last_stop = reason


class NativeClientRectReader:
    """Read-only Win32 GetClientRect on known HWND/PID; never send input."""

    def __init__(self):
        if os.name != "nt":
            raise OSError("S19_CLIENT_GEOMETRY_WINDOWS_ONLY")
        import ctypes
        from ctypes import wintypes
        from start_windows import NativeWin32Backend
        self.ctypes = ctypes
        self.wintypes = wintypes
        self.identity = NativeWin32Backend()
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        self._get_client = user32.GetClientRect
        self._get_client.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
        self._get_client.restype = wintypes.BOOL

    def size(self, hwnd: int, pid: int) -> ClientSize:
        if (type(hwnd) is not int or type(pid) is not int or hwnd <= 0 or pid <= 0
                or not self.identity.is_window(hwnd)
                or self.identity.process_id(hwnd) != pid):
            raise ValueError("STALE_CLIENT_HWND_PID")
        rect = self.wintypes.RECT()
        if not self._get_client(hwnd, self.ctypes.byref(rect)):
            raise OSError("GetClientRect failed")
        # Reject same numeric HWND immediately reused while querying.
        if (not self.identity.is_window(hwnd)
                or self.identity.process_id(hwnd) != pid):
            raise ValueError("CLIENT_HWND_REUSED_DURING_READ")
        return ClientSize(rect.right - rect.left, rect.bottom - rect.top)
