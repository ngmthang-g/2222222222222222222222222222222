"""S13 native Windows: real Tk timer + Win32 DWM on test-owned HWNDs.

The TEST-ONLY cache/adaptor is isolated from production S09 game enumeration.
No claims of a real game, original product license, HP or pixel parity.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "artifacts" / "s13"
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT / "native_maintenance.json"


def run():
    result = {
        "task": "S13", "status": "NOT_RUN",
        "sources": "REAL_TEST_OWNED_TK_TOP_LEVEL_HWND_NOT_GAME",
        "real_game_positive": "NOT_RUN", "real_server": "NOT_RUN",
        "pixel_parity": "NOT_RUN", "game_control_count": 0,
        "exe_build": "NOT_BUILT",
        "boundary_at_six": "S13_CONSERVATIVE_LONG_ORIGINAL_COMPARISON_UNKNOWN",
    }
    root = None
    app = None
    sources = []
    try:
        if os.name != "nt":
            raise RuntimeError("Windows required")
        import tkinter as tk
        from info_tab import TLMInfoTab
        from permission_guard import PermissionGuard, VerifiedClaims
        from shell import TLMMainApp
        from start_tab import TLMStartTab
        from start_windows import GameWindow
        from start_polling import WindowSnapshot
        from dwm_preview import NativeDwmBackend

        class TestCacheProducer:
            """TEST ONLY: real Windows Tk HWNDs; never installed in production."""
            def __init__(self):
                self.active = False
                self.rev = 0
                self.windows = ()
                self.error = False
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
                    self.rev, self.windows if not self.error else (),
                    self.active and not self.error,
                    error="TEST_ONLY_BACKEND_FAILURE" if self.error else None)
            def set_windows(self, rows):
                self.windows = tuple(rows)
                self.error = False
                self.rev += 1

        root = tk.Tk()
        root.geometry("670x720+240+90")
        native = NativeDwmBackend()
        pid = os.getpid()
        all_rows = []
        for i in range(6):
            top = tk.Toplevel(root)
            top.title("S13 native Tk source %d NOT GAME" % (i + 1))
            top.geometry("230x160+%d+%d" % (25 + 235 * (i % 3), 50 + 170 * (i // 3)))
            tk.Label(top, text="S13 TEST-OWNED HWND %d" % i).pack(fill="both", expand=True)
            sources.append(top)
        root.update()
        for i, top in enumerate(sources):
            hwnd = int(native._ancestor(int(top.winfo_id()), 2))
            assert native.source_matches(hwnd, pid)
            all_rows.append(GameWindow(
                hwnd, pid, f"S13 test-owned Tk {i} -- NOT GAME",
                "TkTop", "python.exe"))

        producer = TestCacheProducer()
        producer.set_windows(all_rows[:1])
        holder = []
        def create_start(frame):
            item = TLMStartTab(frame, producer=producer)
            holder.append(item)
            return item

        app = TLMMainApp(root, {
            "info_tab": lambda frame: TLMInfoTab(frame),
            "start_tab": create_start,
        })
        app.position_window_top_right()
        root.update()
        assert app.lifecycle.visible == {"info_tab"} and not holder
        guard = PermissionGuard()
        assert guard.receive_token(
            "S13-TEST-ONLY-TOKEN-NOT-PRODUCTION",
            lambda _: VerifiedClaims(
                permissions=frozenset({"info_tab", "start_tab"}),
                plan_status="TEST_ONLY", max_windows=6))
        app.apply_info_snapshot(guard.snapshot)
        root.update()
        app.notebook.select(app._tab_frames["start_tab"])
        root.update()
        view = holder[0]
        assert view.poller.active and view.maintenance.active

        def pump(ms):
            root.after(ms, root.quit)
            root.mainloop()

        pump(1100)
        result["single_count_cycles"] = view.maintenance.cycles
        result["single_window_delay_ms"] = view.maintenance.last_delay_ms
        assert view.maintenance.cycles >= 1
        assert view.maintenance.last_delay_ms == 800
        result["initial_native_thumb"] = bool(
            view._preview_controller and view._preview_controller.active_hwnds)
        assert result["initial_native_thumb"], "No actual DWM source preview installed"

        producer.set_windows(all_rows)
        pump(1100)
        result["six_count_cycles"] = view.maintenance.cycles
        result["six_window_delay_ms"] = view.maintenance.last_delay_ms
        result["six_cached_window_rows"] = len(view.readonly_view.rows)
        assert view.maintenance.last_delay_ms == 2000
        assert len(view.readonly_view.rows) == 6

        # Deliberately return an invalid source snapshot at the next long tick.
        # It MUST clear all native DWM thumbnails even before S09's next 2s
        # list poll, and show an actual error rather than stale account values.
        producer.error = True
        producer.rev += 1
        pump(2120)
        result["error_state"] = view.readonly_view.code
        result["error_clears_preview_items"] = len(view._tile_items) == 0
        result["error_clears_native_dwm"] = view._preview_controller is None
        result["error_fallback_delay_ms"] = view.maintenance.last_delay_ms
        assert result["error_state"] == "ERROR"
        assert result["error_clears_preview_items"]
        assert result["error_clears_native_dwm"]
        assert result["error_fallback_delay_ms"] == 800

        producer.set_windows(all_rows[:1])
        pump(1030)
        result["recovered_live_cache"] = view.readonly_view.code == "LIVE"
        result["recovered_native_dwm"] = bool(
            view._preview_controller and view._preview_controller.active_hwnds)
        assert result["recovered_live_cache"]
        assert result["recovered_native_dwm"]

        # Native HWND is DESTROYED without any change to the producer's
        # last cached snapshot. Maintenance must check actual PID/IsWindow,
        # remove old destination and never send game commands.
        target = all_rows[0].hwnd
        sources[0].destroy()
        root.update()
        pump(1000)
        result["closed_source_dwm_discarded"] = bool(
            view._preview_controller and target not in view._preview_controller.active_hwnds)
        assert result["closed_source_dwm_discarded"]

        # E03: verified entitlement revoked; selected Start stops BOTH timers.
        guard.clear()
        app.apply_info_snapshot(guard.snapshot)
        root.update()
        result["revoked_info_fallback"] = app.lifecycle.current == "info_tab"
        result["revoked_cache_worker_off"] = not view.poller.active
        result["revoked_maintenance_off"] = not view.maintenance.active
        result["revoked_preview_off"] = view._preview_controller is None
        after_revoke = view.maintenance.cycles
        pump(1090)
        result["revoked_prevents_late_cycles"] = view.maintenance.cycles == after_revoke
        assert all(result[k] for k in (
            "revoked_info_fallback", "revoked_cache_worker_off",
            "revoked_maintenance_off", "revoked_preview_off",
            "revoked_prevents_late_cycles"))
        result["maintenance_cycles"] = view.maintenance.cycles
        result["producer_cache_reads"] = producer.reads
        result["status"] = "PASS_NATIVE_S13_ADAPTIVE_CACHE_MAINTENANCE_AND_REVOCATION"
    except Exception as exc:
        result["status"] = "FAIL_S13_WINDOWS_MAINTENANCE"
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc(limit=16)
    finally:
        if app is not None:
            try: app.shutdown()
            except Exception as exc:
                result["shutdown_error"] = str(exc)
                result["status"] = "FAIL_CLEANUP"
        for top in sources:
            try: top.destroy()
            except Exception: pass
        if root is not None:
            try: root.destroy()
            except Exception as exc:
                result["destroy_error"] = str(exc)
                result["status"] = "FAIL_CLEANUP"
        REPORT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        for key, value in result.items():
            if key != "traceback":
                print("S13_" + key.upper() + "=" + json.dumps(value, ensure_ascii=False))
    return 0 if result["status"] == "PASS_NATIVE_S13_ADAPTIVE_CACHE_MAINTENANCE_AND_REVOCATION" else 1


if __name__ == "__main__":
    raise SystemExit(run())
