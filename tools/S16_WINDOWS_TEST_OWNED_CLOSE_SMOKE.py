"""S16 native Windows smoke: PostMessageW(WM_CLOSE) to TEST-OWNED Tk HWNDs.

The sole posted HWNDs must be actual Toplevel windows created HERE.
The production native backend is NEVER pointed at a game in this CI.
TEST-ONLY identity adapter is intentionally NOT shipped in src.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import traceback

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "src"))
OUT = BASE / "artifacts" / "s16"
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT / "native_wmclose.json"


def run():
    report = {
        "task": "S16", "status": "NOT_RUN",
        "source_type": "THREE_REAL_TEST_OWNED_TK_TOP_LEVEL_WINDOWS_NOT_GAME",
        "test_owned_only": True, "actual_thanh_long_game": "NOT_RUN",
        "real_license_server": "NOT_RUN", "game_commands_to_real_game": 0,
        "full_exe": "NOT_BUILT", "unity_crash_handler_cleanup": "NOT_IMPLEMENTED",
        "original_confirmation": "NOT_RECOVERED",
        "original_immediate_preview_refresh": "UNKNOWN",
    }
    root = None
    app = None
    sources = []
    other = None
    try:
        if os.name != "nt":
            raise RuntimeError("Windows required for actual native WM_CLOSE")
        import ctypes
        from ctypes import wintypes
        import tkinter as tk

        from close_windows import C16CloseAll, NativeWmClosePoster, WM_CLOSE
        from info_tab import TLMInfoTab
        from shell import TLMMainApp
        from permission_guard import PermissionGuard, VerifiedClaims
        from start_tab import TLMStartTab
        from start_windows import (
            GAME_PROCESS, GAME_TITLE, UNITY_WINDOW_CLASS,
            GameWindow, NativeWin32Backend,
        )
        from start_polling import WindowSnapshot

        native = NativeWin32Backend()
        root = tk.Tk()
        root.title("S16 native tests only - NOT GAME")
        root.geometry("810x690+180+80")

        deleted_by_wm_close = []
        pid = os.getpid()
        for i in range(3):
            top = tk.Toplevel(root)
            top.title(f"S16 TARGET {i} TEST OWNED - NOT GAME")
            top.geometry(f"230x160+{30+245*i}+80")
            tk.Label(top, text=f"S16 ONLY TEST-OWNED {i}").pack(fill="both", expand=True)
            # Normal Tk WM_DELETE_WINDOW callback is entered by real WM_CLOSE.
            def on_delete(win=top, number=i):
                deleted_by_wm_close.append(number)
                win.destroy()
            top.protocol("WM_DELETE_WINDOW", on_delete)
            sources.append(top)

        other = tk.Toplevel(root)
        other.title("S16 unrelated window - NEVER WM_CLOSE")
        other.geometry("200x140+10+440")
        tk.Label(other, text="NOT A C16 TARGET").pack(fill="both", expand=True)
        root.update()
        targets = tuple(int(top.winfo_id()) for top in sources)
        # Tk child widget winfo_id may be an inner HWND; GA_ROOT resolves real
        # top-level HWND. Original S11 NativeDwmBackend._ancestor proved this.
        from dwm_preview import NativeDwmBackend
        ancestor = NativeDwmBackend()
        targets = tuple(int(ancestor._ancestor(int(top.winfo_id()), 2))
                        for top in sources)
        unrelated = int(ancestor._ancestor(int(other.winfo_id()), 2))
        assert len(set(targets)) == 3 and unrelated not in targets
        assert all(native.is_window(h) and native.process_id(h) == pid for h in targets)
        assert native.is_window(unrelated)
        report["test_owned_source_hwnds"] = targets
        report["unrelated_hwnd"] = unrelated
        rows = tuple(GameWindow(h, pid, GAME_TITLE, UNITY_WINDOW_CLASS, GAME_PROCESS)
                     for h in targets)

        class TestOnlyBackend:
            """Real HWND lifetime/PID, TEST-ONLY game-identity mapping for CI.

            This cannot be used from production src: only this test file
            vouches for the exact HWNDs created above.
            """
            def enumerate_top_level(self):
                return native.enumerate_top_level()
            def is_window(self, hwnd):
                return native.is_window(hwnd)
            def is_visible(self, hwnd):
                return native.is_visible(hwnd)
            def process_id(self, hwnd):
                return native.process_id(hwnd)
            def process_executable(self, process_id):
                # Test-only override for the very same PID that owns real Tk
                # windows. Other/unlisted HWNDs never match class or title.
                return GAME_PROCESS if process_id == pid else ""
            def window_class(self, hwnd):
                return UNITY_WINDOW_CLASS if hwnd in targets else "TkTop"
            def title_with_timeout(self, hwnd, timeout_ms):
                return GAME_TITLE if hwnd in targets else "UNRELATED"

        class TracedPoster(NativeWmClosePoster):
            def __init__(self):
                super().__init__()
                self.posted = []
            def post_close(self, hwnd):
                # Fail hard if a production code regression tries any HWND
                # other than three explicitly test-owned source windows.
                assert hwnd in targets, ("S16 UNSAFE NON-TEST HWND", hwnd)
                if not native.is_window(hwnd):
                    return False
                answer = super().post_close(hwnd)  # REAL PostMessageW
                self.posted.append((hwnd, WM_CLOSE, answer))
                return answer

        poster = TracedPoster()
        fixed = TestOnlyBackend()
        class Cache:
            def __init__(self):
                self.active = False
                self.rev = 0
                self.rows = rows
                self.reads = 0
            def start(self):
                self.active = True
                self.rev += 1
                return True
            def stop(self):
                self.active = False
                self.rev += 1
            def read_snapshot(self):
                self.reads += 1
                return WindowSnapshot(
                    self.rev, self.rows if self.active else (), self.active)
            def replace(self, next_rows):
                self.rows = tuple(next_rows)
                self.rev += 1
        cache = Cache()
        built = []
        def build(frame):
            item = TLMStartTab(
                frame, producer=cache,
                close_service_factory=lambda: C16CloseAll(fixed, poster))
            built.append(item)
            return item

        app = TLMMainApp(root, {
            "info_tab": lambda parent: TLMInfoTab(parent),
            "start_tab": build,
        })
        root.update()
        report["default_info_only"] = app.lifecycle.visible == {"info_tab"} and not built
        assert report["default_info_only"]
        assert not poster.posted

        guard = PermissionGuard()
        assert guard.receive_token(
            "S16_TEST_ONLY_SIGNED_CLAIMS_ADAPTER_NOT_PRODUCTION",
            lambda _: VerifiedClaims(
                permissions=frozenset({"info_tab", "start_tab"}),
                plan_status="TEST_ONLY", max_windows=3))
        app.apply_info_snapshot(guard.snapshot)
        root.update()
        app.notebook.select(app._tab_frames["start_tab"])
        root.update()
        tab = built[0]

        def pump(ms):
            root.after(ms, root.quit)
            root.mainloop()

        pump(220)
        assert tab.poller.active and tab.maintenance.active
        assert tab.btn_close_all.cget("text") == "Đóng hết"
        assert len(tab._active_windows) == 3

        # First: an injected unrelated GUI HWND with game-looking cached name
        # cannot be targeted because live source class/title do not match.
        unsafe = GameWindow(
            unrelated, pid, GAME_TITLE, UNITY_WINDOW_CLASS, GAME_PROCESS)
        service = C16CloseAll(fixed, poster)
        bad = service.close_all_game_windows(WindowSnapshot(
            3, (unsafe,), True))
        report["unrelated_cached_spoof_rejected"] = (
            not bad.posted and bad.skipped == (
                (unrelated, "LIVE_GAME_IDENTITY_MISMATCH"),))
        assert report["unrelated_cached_spoof_rejected"]
        assert native.is_window(unrelated)
        assert not poster.posted

        # Now invoke the real GUI button. Three native top-level sources must
        # receive genuine PostMessageW(WM_CLOSE,0,0).
        reads = cache.reads
        tab.btn_close_all.invoke()
        requested = tab.last_close_result
        report["button_cache_read_once"] = cache.reads == reads + 1
        report["wm_close_posted_targets"] = [h for h, _, _ in poster.posted]
        report["wm_close_posted_3_of_3"] = (
            len(poster.posted) == 3 and requested.posted == targets
            and all(msg == 0x10 and ok for _, msg, ok in poster.posted))
        report["status_says_posted_not_closed"] = (
            "đã gửi WM_CLOSE 3/3" in tab.preview_status.cget("text"))
        assert all(report[k] for k in (
            "button_cache_read_once", "wm_close_posted_3_of_3",
            "status_says_posted_not_closed"))

        # Posting is asynchronous; pump Tk to deliver WM_CLOSE and invoke
        # the real protocol callback for each source.
        pump(550)
        report["tk_deleted_by_actual_wm_close"] = sorted(deleted_by_wm_close)
        report["source_hwnds_gone"] = all(not native.is_window(h) for h in targets)
        report["unrelated_window_survives"] = native.is_window(unrelated)
        assert report["tk_deleted_by_actual_wm_close"] == [0, 1, 2]
        assert report["source_hwnds_gone"]
        assert report["unrelated_window_survives"]

        # Click again with STALE worker cache: identity checks must prevent
        # sending WM_CLOSE to any re-used numeric HWND or non-target app.
        tab.btn_close_all.invoke()
        report["second_click_stale_cache_posts_zero"] = len(poster.posted) == 3
        assert report["second_click_stale_cache_posts_zero"]

        # C16 original does NOT prove immediate preview refresh; only S09/S13
        # normally reconciles on next actual updated discovery snapshot.
        cache.replace(())
        pump(1100)
        report["eventual_preview_cleanup_from_updated_cache"] = (
            not tab._active_windows and not tab._tile_items)
        assert report["eventual_preview_cleanup_from_updated_cache"]

        guard.clear()
        app.apply_info_snapshot(guard.snapshot)
        root.update()
        count = len(poster.posted)
        before_read = cache.reads
        report["revoked_start_falls_back_info"] = app.lifecycle.current == "info_tab"
        report["revoked_rejects_close"] = (
            tab._close_all_preview_windows() is None and
            cache.reads == before_read and len(poster.posted) == count)
        assert report["revoked_start_falls_back_info"]
        assert report["revoked_rejects_close"]
        report["no_process_force_termination"] = True
        report["status"] = "PASS_NATIVE_S16_TEST_OWNED_WM_CLOSE_WITH_AUTH_PID_GUARDS"
    except Exception as exc:
        report["status"] = "FAIL_NATIVE_S16_TEST_OWNED_WM_CLOSE"
        report["error"] = f"{type(exc).__name__}: {exc}"
        report["traceback"] = traceback.format_exc(limit=18)
    finally:
        if app is not None:
            try: app.shutdown()
            except Exception as exc:
                report["cleanup_error"] = str(exc)
                report["status"] = "FAIL_CLEANUP"
        for top in sources:
            try: top.destroy()
            except Exception: pass
        if other is not None:
            try: other.destroy()
            except Exception: pass
        if root is not None:
            try: root.destroy()
            except Exception as exc:
                report["destroy_error"] = str(exc)
                report["status"] = "FAIL_CLEANUP"
        REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2),
                          encoding="utf-8")
        for k, v in report.items():
            if k != "traceback":
                # GitHub Windows cp1252 console cannot emit Unicode Vietnamese.
                print("S16_" + k.upper() + "=" + json.dumps(v, ensure_ascii=True))
    return 0 if report["status"] == "PASS_NATIVE_S16_TEST_OWNED_WM_CLOSE_WITH_AUTH_PID_GUARDS" else 1


if __name__ == "__main__":
    raise SystemExit(run())
