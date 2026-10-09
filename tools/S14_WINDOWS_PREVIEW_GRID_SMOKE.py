"""S14 real Windows Tk 1x–5x columns / C17 arrows with real test-owned DWM.

The window sources are actual native Tk Toplevel HWND/PIDs, and the producer
is TEST-ONLY, never wired into the production S09 Thần Long scanner.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "artifacts" / "s14"
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT / "native_grid_order.json"


def run():
    result = {
        "task": "S14", "status": "NOT_RUN",
        "source_type": "FOUR_REAL_TEST_OWNED_TK_TOP_LEVEL_WINDOWS_NOT_GAME",
        "real_game": "NOT_RUN", "real_license_server": "NOT_RUN",
        "pixel_parity": "NOT_RUN", "product_exe": "NOT_BUILT",
        "game_commands": 0,
    }
    root, app = None, None
    sources = []
    try:
        if os.name != "nt":
            raise RuntimeError("S14 native test requires Windows")
        import tkinter as tk
        from tkinter import ttk
        from info_tab import TLMInfoTab
        from shell import TLMMainApp
        from permission_guard import PermissionGuard, VerifiedClaims
        from start_tab import TLMStartTab
        from start_windows import GameWindow
        from start_polling import WindowSnapshot
        from dwm_preview import NativeDwmBackend
        from preview_layout import PREVIEW_GRID_CHOICES, preview_position

        root = tk.Tk()
        root.title("S14 validation - NO GAME")
        backend = NativeDwmBackend()
        for index in range(4):
            top = tk.Toplevel(root)
            top.title(f"S14 source {index + 1} - TEST ONLY")
            top.geometry(f"220x170+{30 + (index % 2) * 225}+{30 + (index // 2) * 180}")
            tk.Label(top, text=f"Real test-owned HWND #{index + 1}").pack(
                fill="both", expand=True)
            sources.append(top)
        root.update()
        pid = os.getpid()
        hwnds = [
            int(backend._ancestor(int(window.winfo_id()), 2))
            for window in sources
        ]
        assert len(set(hwnds)) == 4 and all(backend.source_matches(h, pid) for h in hwnds)
        rows = tuple(GameWindow(
            hwnd, pid, f"S14 TEST HWND {i + 1} - NOT GAME",
            "TkTop", "python.exe") for i, hwnd in enumerate(hwnds))

        class OnlyTestProducer:
            def __init__(self):
                self.active = False
                self.rev = 0
                self.rows = rows
            def start(self):
                self.active = True
                self.rev += 1
                return True
            def stop(self):
                self.active = False
                self.rev += 1
            def read_snapshot(self):
                return WindowSnapshot(self.rev, self.rows if self.active else (),
                                      self.active)
            def replace(self, next_rows):
                self.rows = tuple(next_rows)
                self.rev += 1

        producer = OnlyTestProducer()
        built = []
        def start_factory(frame):
            tab = TLMStartTab(frame, producer=producer)
            built.append(tab)
            return tab
        app = TLMMainApp(root, {
            "info_tab": lambda parent: TLMInfoTab(parent),
            "start_tab": start_factory,
        })
        app.position_window_top_right()
        root.geometry("940x830+20+20")
        root.update()
        result["initial_info_only"] = app.lifecycle.visible == {"info_tab"} and not built
        assert result["initial_info_only"]

        claims = PermissionGuard()
        assert claims.receive_token(
            "S14-ONLY-TEST-CLAIM-NOT-PRODUCTION",
            lambda _: VerifiedClaims(
                permissions=frozenset({"info_tab", "start_tab"}),
                plan_status="TEST_ONLY", max_windows=4))
        app.apply_info_snapshot(claims.snapshot)
        root.update()
        app.notebook.select(app._tab_frames["start_tab"])
        root.update()

        def pump(milliseconds=160):
            root.after(milliseconds, root.quit)
            root.mainloop()

        pump(280)
        tab = built[0]
        assert tab.poller.active and tab.maintenance.active
        result["initial_column_choice"] = tab.preview_grid_var.get()
        result["initial_columns"] = tab._get_preview_columns()
        result["initial_tile_count"] = len(tab._tile_items)
        assert tab._get_preview_columns() == 2
        assert len(tab._tile_items) == 4
        def placement_list():
            return [
                (
                    int(tab._tile_items[(w.hwnd, w.pid)][0].grid_info()["row"]),
                    int(tab._tile_items[(w.hwnd, w.pid)][0].grid_info()["column"]),
                ) for w in tab._active_windows
            ]
        assert placement_list() == [preview_position(i, 2) for i in range(4)]

        pump(190)
        native = tab._preview_controller
        assert native is not None and len(native.active_hwnds) == 4
        native_before = {
            h: (native._slots[h].destination, native._slots[h].thumbnail)
            for h in native.active_hwnds
        }
        result["real_dwm_sources"] = sorted(native.active_hwnds)

        # Every C09 value MUST move real Tk grid widget positions. None
        # should unregister/recreate a surviving HWND's DWM thumbnail.
        grid_positions = {}
        for choice in PREVIEW_GRID_CHOICES:
            tab.preview_grid_var.set(choice)
            tab.preview_grid_select.event_generate("<<ComboboxSelected>>")
            root.update()
            pump(170)
            expected = [preview_position(i, int(choice[0])) for i in range(4)]
            actual = placement_list()
            assert actual == expected, (choice, expected, actual)
            grid_positions[choice] = actual
            assert tab._preview_controller is native
            assert {
                h: (native._slots[h].destination, native._slots[h].thumbnail)
                for h in native.active_hwnds
            } == native_before, choice
        result["all_1x_to_5x_layouts"] = grid_positions
        result["manual_grid_choice"] = tab.preview_grid_manual
        assert tab.preview_grid_manual

        # Actual ttk Button.invoke should reorder the actual tile; not
        # SetForegroundWindow, not move or activate a game source HWND.
        third = rows[2]
        old = tab._active_windows
        btn_left = tab._tile_items[(third.hwnd, third.pid)][3]
        assert isinstance(btn_left, ttk.Button)
        btn_left.invoke()
        root.update()
        pump(170)
        result["after_left_arrow"] = [w.hwnd for w in tab._active_windows]
        assert result["after_left_arrow"] == [
            old[0].hwnd, old[2].hwnd, old[1].hwnd, old[3].hwnd]
        assert placement_list() == [preview_position(i, 5) for i in range(4)]
        assert {
            h: (native._slots[h].destination, native._slots[h].thumbnail)
            for h in native.active_hwnds
        } == native_before

        # Actual right-arrow restores original order.
        tab._tile_items[(third.hwnd, third.pid)][4].invoke()
        root.update()
        pump(170)
        result["restored_order"] = [w.hwnd for w in tab._active_windows]
        assert result["restored_order"] == [w.hwnd for w in rows]

        # Preserve saved order across a reordered producer snapshot.
        tab._tile_items[(third.hwnd, third.pid)][3].invoke()
        root.update()
        producer.replace(tuple(reversed(rows)))
        pump(1100)  # real S13 housekeeping consumes revised producer cache
        result["refresh_keeps_manual_order"] = [
            w.hwnd for w in tab._active_windows] == [
                rows[0].hwnd, rows[2].hwnd, rows[1].hwnd, rows[3].hwnd]
        assert result["refresh_keeps_manual_order"]

        # TEST: the numerical HWND is reused under another PID, so even a
        # stale button referencing OLD identity must be refused.
        bad_hwnd = rows[2].hwnd
        old_pid = rows[2].pid
        newer = GameWindow(bad_hwnd, old_pid + 1000,
                           "TEST REUSED HWND - WRONG REAL PID",
                           "TkTop", "NOT_GAME.exe")
        producer.replace(tuple(newer if w.hwnd == bad_hwnd else w for w in rows))
        pump(1100)
        result["pid_reuse_old_arrow_rejected"] = not tab._move_preview_item(
            bad_hwnd, old_pid, -1)
        assert result["pid_reuse_old_arrow_rejected"]

        # A wrong process PID is never registered as a DWM source.
        pump(200)
        result["wrong_pid_not_dwm_registered"] = bool(
            tab._preview_controller and bad_hwnd not in tab._preview_controller.active_hwnds)
        assert result["wrong_pid_not_dwm_registered"]

        prior_native = tab._preview_controller
        current_slots = tuple(prior_native.active_hwnds)
        claims.clear()
        app.apply_info_snapshot(claims.snapshot)
        root.update()
        result["revoked_info_fallback"] = app.lifecycle.current == "info_tab"
        result["revoked_preview_clean"] = (
            tab._preview_controller is None
            and tab._tile_items == {}
            and not tab.poller.active and not tab.maintenance.active)
        assert result["revoked_info_fallback"] and result["revoked_preview_clean"]
        result["native_resources_released"] = not prior_native.active_hwnds
        assert result["native_resources_released"]
        result["native_hwnd_count_before_revoke"] = len(current_slots)
        result["status"] = "PASS_NATIVE_S14_REAL_DWM_GRID_AND_ORDER_LIFECYCLE"
    except Exception as exc:
        result["status"] = "FAIL_NATIVE_S14_PREVIEW_LAYOUT"
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc(limit=15)
    finally:
        if app is not None:
            try: app.shutdown()
            except Exception as exc:
                result["cleanup_error"] = str(exc)
                result["status"] = "FAIL_CLEANUP"
        for src in sources:
            try: src.destroy()
            except Exception: pass
        if root is not None:
            try: root.destroy()
            except Exception as exc:
                result["destroy_error"] = str(exc)
                result["status"] = "FAIL_CLEANUP"
        REPORT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        for key, val in result.items():
            if key != "traceback":
                print("S14_" + key.upper() + "=" + json.dumps(val, ensure_ascii=False))
    return 0 if result["status"] == "PASS_NATIVE_S14_REAL_DWM_GRID_AND_ORDER_LIFECYCLE" else 1


if __name__ == "__main__":
    raise SystemExit(run())
