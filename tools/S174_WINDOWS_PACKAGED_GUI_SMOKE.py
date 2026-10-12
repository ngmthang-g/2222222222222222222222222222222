"""S174: real packaged PyInstaller independent EXE in NORMAL GUI mode.

Not --self-check, not a source-only Tk window. Launches EXACT onedir EXE
built by this workflow; identifies a real OS top-level HWND + PID, checks
visible/responsive title/bounds, captures *only that window* in Windows CI,
checks E01 duplicate-instance mutex, WM_CLOSE graceful teardown + relaunch.

No game process, original issuer, fabricated character, synthetic license,
game keyboard/memory access or modification of the original executable.
"""
from __future__ import annotations

import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "s174"
OUT.mkdir(parents=True, exist_ok=True)

WINDOW_TITLE = "TLMTool — Độc lập"
STARTUP_TIMEOUT_S = 22
EXIT_TIMEOUT_S = 12
WM_NULL = 0
WM_CLOSE = 0x0010
SMTO_ABORTIFHUNG = 0x0002


def accepted_window(pid: int, title: str, visible: bool,
                    width: int, height: int) -> bool:
    """Exact Win32 PID/title/visibility/bounds, NEVER title-only discovery."""
    return (type(pid) is int and pid > 0
            and type(title) is str and title == WINDOW_TITLE
            and type(visible) is bool and visible
            and type(width) is int and width >= 400
            and type(height) is int and height >= 200)


def isolated_env(base: Path, parent: dict | None = None) -> dict:
    """No developer's local settings or logs touched by the smoke."""
    env = dict(os.environ if parent is None else parent)
    roaming = base / "Roaming"
    local = base / "Local"
    roaming.mkdir(parents=True, exist_ok=True)
    local.mkdir(parents=True, exist_ok=True)
    env["APPDATA"] = str(roaming)
    env["LOCALAPPDATA"] = str(local)
    return env


class Win32Gui:
    """Only official user32 read-only enumeration + WM_CLOSE."""

    def __init__(self):
        if os.name != "nt":
            raise OSError("REAL_WINDOWS_DESKTOP_REQUIRED")
        u = ctypes.WinDLL("user32", use_last_error=True)
        self.u = u
        self.enum = u.EnumWindows
        self.enum.argtypes = [ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND,
                                                wintypes.LPARAM), wintypes.LPARAM]
        self.enum.restype = wintypes.BOOL
        self.getpid = u.GetWindowThreadProcessId
        self.getpid.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
        self.getpid.restype = wintypes.DWORD
        self.visible = u.IsWindowVisible
        self.visible.argtypes = [wintypes.HWND]
        self.visible.restype = wintypes.BOOL
        self.title_len = u.GetWindowTextLengthW
        self.title_len.argtypes = [wintypes.HWND]
        self.title_len.restype = ctypes.c_int
        self.title = u.GetWindowTextW
        self.title.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
        self.title.restype = ctypes.c_int
        self.rect = u.GetWindowRect
        self.rect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
        self.rect.restype = wintypes.BOOL
        self.responsive = u.SendMessageTimeoutW
        self.responsive.argtypes = [wintypes.HWND, wintypes.UINT,
                                   wintypes.WPARAM, wintypes.LPARAM,
                                   wintypes.UINT, wintypes.UINT,
                                   ctypes.POINTER(ctypes.c_size_t)]
        self.responsive.restype = wintypes.LPARAM
        self.close = u.PostMessageW
        self.close.argtypes = [wintypes.HWND, wintypes.UINT,
                               wintypes.WPARAM, wintypes.LPARAM]
        self.close.restype = wintypes.BOOL

    def windows_for(self, owner: int):
        found = []
        callback_type = ctypes.WINFUNCTYPE(
            wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

        def callback(hwnd, _unused):
            pid = wintypes.DWORD(0)
            self.getpid(hwnd, ctypes.byref(pid))
            if pid.value != owner:
                return True
            length = self.title_len(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            self.title(hwnd, buf, length + 1)
            rec = wintypes.RECT()
            if not self.rect(hwnd, ctypes.byref(rec)):
                return True
            item = dict(
                hwnd=int(hwnd), pid=int(pid.value), title=buf.value,
                visible=bool(self.visible(hwnd)),
                left=rec.left, top=rec.top,
                width=rec.right-rec.left, height=rec.bottom-rec.top)
            found.append(item)
            return True

        cb = callback_type(callback)
        if not self.enum(cb, 0):
            raise RuntimeError("ENUMWINDOWS_FAILED")
        return found

    def wait_window(self, process: subprocess.Popen, seconds: int):
        start = time.monotonic()
        while time.monotonic() - start < seconds:
            if process.poll() is not None:
                raise RuntimeError(f"PACKAGED_GUI_EXITED_PREMATURELY_{process.returncode}")
            for item in self.windows_for(process.pid):
                if accepted_window(item["pid"], item["title"], item["visible"],
                                   item["width"], item["height"]):
                    answer = ctypes.c_size_t(0)
                    ok = self.responsive(
                        item["hwnd"], WM_NULL, 0, 0,
                        SMTO_ABORTIFHUNG, 1500, ctypes.byref(answer))
                    if ok:
                        item["responsive"] = True
                        return item
            time.sleep(.2)
        raise RuntimeError("PACKAGED_REAL_TK_WINDOW_NOT_VISIBLE_OR_RESPONSIVE")

    def graceful_close(self, process: subprocess.Popen, hwnd: int):
        if not self.close(hwnd, WM_CLOSE, 0, 0):
            raise RuntimeError("WM_CLOSE_POST_FAILED")
        try:
            code = process.wait(timeout=EXIT_TIMEOUT_S)
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError("PACKAGED_GUI_WM_CLOSE_DID_NOT_SHUT_DOWN") from exc
        if code != 0:
            raise RuntimeError(f"PACKAGED_GUI_NORMAL_CLOSE_CODE_{code}")


def launch(executable: Path, env: dict, cwd: Path, label: str):
    stdout = OUT / f"{label}.stdout.txt"
    stderr = OUT / f"{label}.stderr.txt"
    out = stdout.open("wb")
    err = stderr.open("wb")
    try:
        child = subprocess.Popen(
            [str(executable)], cwd=str(cwd), env=env,
            stdin=subprocess.DEVNULL, stdout=out, stderr=err,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        return child
    finally:
        out.close()
        err.close()


def capture_window(item: dict):
    """Proof image from the *CI-owned* fresh GUI, no user desktop/files."""
    from PIL import ImageGrab
    x, y = item["left"], item["top"]
    w, h = item["width"], item["height"]
    if min(w, h) <= 0 or w > 2000 or h > 3000:
        raise RuntimeError("INVALID_PACKAGED_GUI_WINDOW_BOUNDS")
    im = ImageGrab.grab(bbox=(x, y, x+w, y+h), all_screens=True)
    if im.width != w or im.height != h:
        raise RuntimeError("WINDOW_SCREENSHOT_SIZE_MISMATCH")
    dst = OUT / "real_packaged_gui_window.png"
    im.save(dst)
    return dst


def run(exe: Path) -> dict:
    proof = {
        "status": "NOT_RUN",
        "actual_game": False,
        "source_only_tk_test": False,
        "original_info_issuer": False,
        "gameplay_controls": False,
        "original_executable_patched": False,
    }
    processes = []
    try:
        if os.name != "nt" or not exe.is_file():
            raise RuntimeError("S174_REQUIRES_REAL_BUILT_WINDOWS_EXE")
        native = Win32Gui()
        with tempfile.TemporaryDirectory(prefix="S174_REAL_PACKAGED_") as folder:
            base = Path(folder)
            env = isolated_env(base)
            first = launch(exe, env, base, "first_gui")
            processes.append(first)
            item = native.wait_window(first, STARTUP_TIMEOUT_S)
            proof["normal_packaged_exe_not_selfcheck"] = first.args == [str(exe)]
            proof["real_visible_responsive_win32_hwnd_pid"] = (
                item["hwnd"] > 0 and item["pid"] == first.pid and
                item["responsive"] and item["width"] >= 400)
            proof["actual_packaged_gui_title"] = item["title"]
            proof["actual_packaged_gui_bounds"] = {
                k:item[k] for k in ("left","top","width","height")}
            proof["actual_packaged_gui_pid"] = int(first.pid)
            # Screenshot is supplemental: the HWND is real, source-only
            # inherited native Tk tests prove Notebook+implemented tabs.
            image = capture_window(item)
            proof["actual_packaged_window_screenshot"] = image.name
            proof["screenshot_is_from_exact_hwnd_bounds"] = image.is_file()
            proof["appdata_isolated"] = (
                str(base / "Roaming") == env["APPDATA"]
                and str(base / "Local") == env["LOCALAPPDATA"])
            proof["private_crash_diagnostic_created"] = (
                (base/"Local"/"TLMTool"/"crash_fault.log").is_file())
            proof["session_log_written_next_to_test_exe"] = (
                (exe.parent/"log"/"tlmtool.log").is_file())
            # S21 mutex collision: second normal binary is rejected; first
            # must remain alive. No test override or tampering with mutex.
            second = launch(exe, env, base, "duplicate_gui")
            processes.append(second)
            try:
                duplicate_code = second.wait(timeout=7)
            except subprocess.TimeoutExpired as exc:
                raise RuntimeError("DUPLICATE_INSTANCE_STARTED_OR_HUNG") from exc
            proof["same_real_exe_second_instance_rejected"] = (
                duplicate_code != 0 and first.poll() is None)
            proof["duplicate_process_has_no_second_gui"] = not any(
                accepted_window(v["pid"],v["title"],v["visible"],
                                v["width"],v["height"])
                for v in native.windows_for(second.pid))
            native.graceful_close(first, item["hwnd"])
            proof["wm_close_full_exe_exits_zero"] = (
                first.poll() == 0)
            # The S21 instance mutex MUST be released, not only the window.
            third = launch(exe, env, base, "reopened_gui")
            processes.append(third)
            again = native.wait_window(third, STARTUP_TIMEOUT_S)
            proof["reopen_after_clean_shutdown_real_hwnd"] = (
                again["hwnd"] > 0 and again["pid"] == third.pid
                and again["responsive"])
            native.graceful_close(third, again["hwnd"])
            proof["second_full_shutdown_exits_zero"] = third.poll() == 0
            proof["all_direct_test_owned_processes_exited"] = (
                all(p.poll() is not None for p in processes))
        flags = {k:v for k,v in proof.items() if type(v) is bool and k not in (
            "actual_game","source_only_tk_test","original_info_issuer",
            "gameplay_controls","original_executable_patched")}
        if not all(flags.values()):
            raise RuntimeError("PACKAGED_GUI_ACCEPTANCE_FAILED:"+",".join(
                k for k,v in flags.items() if not v))
        proof["status"] = "PASS_NATIVE_S174_REAL_PACKAGED_INDEPENDENT_EXE_GUI_OPEN_CLOSE"
    except Exception as exc:
        proof["status"] = "FAILED_S174_PACKAGED_GUI"
        proof["error_type"] = type(exc).__name__
        proof["error_detail"] = str(exc)[:850]
        # Direct children are test-created only. No game/PID-wide kill.
        for process in reversed(processes):
            if process.poll() is None:
                try:
                    process.kill()
                    process.wait(timeout=5)
                except Exception:
                    pass
    return proof


def main():
    proof = {"status":"NOT_RUN"}
    try:
        if len(sys.argv) != 2:
            raise ValueError("USAGE: S174_WINDOWS_PACKAGED_GUI_SMOKE.py <REAL_EXE_PATH>")
        proof = run(Path(sys.argv[1]).resolve())
    except Exception as exc:
        proof = {"status":"FAILED_S174_PACKAGED_GUI",
                 "error_type":type(exc).__name__,
                 "error_detail":str(exc)[:850]}
    finally:
        (OUT/"real_packaged_gui_acceptance.json").write_text(
            json.dumps(proof, ensure_ascii=False, indent=2)+"\n",
            encoding="utf-8")
        for k,v in proof.items():
            print("S174_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if proof["status"].startswith("PASS_NATIVE_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
