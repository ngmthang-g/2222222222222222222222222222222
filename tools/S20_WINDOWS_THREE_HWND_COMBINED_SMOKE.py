"""S20 / original C20 combined 3-HWND native *test-owned* integration.

Three actual Win32 Tk top-level HWNDs: C03 native DWM preview, C09 2x
preview grid, C05 second-card Master, C18 physical 3x4 moving-only grid,
C17 independent preview reorder and C19 SAFE INPUT MODEL (NO NATIVE SENDER).
Check 3->2 HWND loss and E03 auth revoke/native resource cleanup.

Original RoleName/HP and actual Thần Long game are NOT emulated as facts.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "artifacts" / "s20"
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT / "three_hwnd_combined_native.json"


def run():
    report = {
        "task": "S20", "status": "NOT_RUN",
        "sources": "THREE_REAL_TEST_OWNED_TK_TOP_LEVEL_HWND_NOT_GAME",
        "real_game": "NOT_RUN", "license_server": "TEST_ONLY_VERIFIER",
        "real_role_names_hp": "NOT_AVAILABLE", "original_pixel_parity": "NOT_RUN",
        "original_c06_grid_math": "UNKNOWN_LOCAL_S17_MOVE_ONLY",
        "real_c19_mouse_keyboard_sender": "NOT_IMPLEMENTED",
        "product_exe": "NOT_BUILT", "proxy": "NOT_DEVELOPED",
    }
    root = None
    app = None
    sources = []
    other = None
    temp_ini = None
    try:
        if os.name != "nt":
            raise RuntimeError("S20 real HWND native smoke is Windows-only")
        import tkinter as tk

        from dwm_preview import NativeDwmBackend
        from grid_master import GridSettingsStore
        from info_tab import TLMInfoTab
        from input_sync_core import InputSyncModel, NativeClientRectReader
        from layout_windows import C18LayoutSync, NativeLayoutBackend
        from permission_guard import PermissionGuard, VerifiedClaims
        from preview_layout import preview_position
        from shell import TLMMainApp
        from start_polling import WindowSnapshot
        from start_tab import TLMStartTab
        from start_windows import (
            GAME_PROCESS, GAME_TITLE, UNITY_WINDOW_CLASS,
            GameWindow, NativeWin32Backend,
        )

        root = tk.Tk()
        root.title("S20 three-HWND integration - NO GAME")
        root.geometry("960x930+12+12")
        outer = ((180, 135), (205, 160), (220, 180))
        for index, (width, height) in enumerate(outer):
            source = tk.Toplevel(root)
            source.title(f"S20 TEST-OWNED HWND #{index + 1}, NOT GAME")
            source.geometry(f"{width}x{height}+{20+index*265}+{90+index*175}")
            tk.Label(source, text=f"S20 TEST-OWNED SOURCE {index+1}").pack(
                fill="both", expand=True)
            sources.append(source)
        other = tk.Toplevel(root)
        other.title("S20 unrelated HWND - DO NOT MODIFY")
        other.geometry("135x100+1050+450")
        root.update()
        probe = NativeDwmBackend()
        native = NativeWin32Backend()
        hwnds = tuple(int(probe._ancestor(int(w.winfo_id()), 2))
                      for w in sources)
        foreign = int(probe._ancestor(int(other.winfo_id()), 2))
        pid = os.getpid()
        assert len(set(hwnds)) == 3 and foreign not in hwnds
        assert all(native.is_window(h) and native.process_id(h) == pid
                   and probe.source_matches(h, pid) for h in hwnds)
        original_rows = tuple(GameWindow(
            h, pid, f"S20 real TEST-OWNED source #{index+1}, NOT GAME",
            UNITY_WINDOW_CLASS, GAME_PROCESS)
            for index, h in enumerate(hwnds))
        # Identity labels here explicitly say TEST-OWNED: no fake character HP.
        rect_before = {h:NativeLayoutBackend().window_rect(h) for h in hwnds}
        unrelated_rect = NativeLayoutBackend().window_rect(foreign)
        report["source_hwnds"] = hwnds
        report["unrelated_hwnd"] = foreign

        class TestOwnedLayoutBackend:
            """Only test-owned HWNDs can ever be passed to SetWindowPos."""
            def __init__(self):
                self.backend = NativeLayoutBackend()
                self.moves = []
            def __getattr__(self, name):
                return getattr(self.backend, name)
            def process_executable(self, target_pid):
                return GAME_PROCESS if target_pid == pid else ""
            def window_class(self, hwnd):
                return UNITY_WINDOW_CLASS if hwnd in hwnds else "Unrelated"
            def title_with_timeout(self, hwnd, timeout_ms):
                assert timeout_ms == 150
                return GAME_TITLE if hwnd in hwnds else "UNRELATED"
            def move_no_resize(self, hwnd, x, y):
                assert hwnd in hwnds and native.is_window(hwnd), (
                    "S20 NON-TEST NATIVE MOVE BLOCKED", hwnd)
                self.moves.append((hwnd, x, y))
                return self.backend.move_no_resize(hwnd, x, y)

        layout_backend = TestOwnedLayoutBackend()

        class TestOnlyCache:
            def __init__(self):
                self.active = False
                self.revision = 0
                self.rows = original_rows
            def start(self):
                self.active = True
                self.revision += 1
                return True
            def stop(self):
                self.active = False
                self.revision += 1
            def read_snapshot(self):
                return WindowSnapshot(self.revision,
                                      self.rows if self.active else (),
                                      self.active)
            def replace(self, rows):
                self.rows = tuple(rows)
                self.revision += 1

        producer = TestOnlyCache()
        temp_ini = tempfile.TemporaryDirectory(prefix="s20_native_ini_")
        store = GridSettingsStore(Path(temp_ini.name)/"TLMTool"/"settings.ini")
        tabs = []
        def make_start(parent):
            tab = TLMStartTab(
                parent, producer=producer,
                layout_service_factory=lambda:C18LayoutSync(layout_backend),
                grid_settings_store=store)
            tabs.append(tab)
            return tab

        app = TLMMainApp(root, {
            "info_tab":lambda frame:TLMInfoTab(frame),
            "start_tab":make_start,
        })
        app.position_window_top_right()
        root.geometry("960x930+12+12")
        root.update()
        report["initial_info_only"] = (
            app.lifecycle.visible == {"info_tab"} and not tabs)
        assert report["initial_info_only"]

        claims = PermissionGuard()
        assert claims.receive_token(
            "S20_ONLY_TEST_VERIFIED_CLAIMS", lambda _:VerifiedClaims(
                permissions=frozenset({"info_tab","start_tab"}),
                plan_status="TEST_ONLY",max_windows=3))
        def allowed():
            ss = claims.snapshot
            return (ss.has_verified_payload and not ss.blocked
                    and "start_tab" in ss.authorized_keys
                    and ss.max_windows >= 3)
        app.apply_info_snapshot(claims.snapshot)
        root.update()
        app.notebook.select(app._tab_frames["start_tab"])
        root.update()

        def pump(ms=175):
            root.after(ms, root.quit)
            root.mainloop()

        pump(340)
        tab = tabs[0]
        assert tab.poller.active and tab.maintenance.active
        report["physical_grid_3x4"] = (tab.grid_cols, tab.grid_rows) == (3,4)
        report["preview_grid_2x"] = tab.preview_grid_var.get() == "2x"
        report["three_preview_cards"] = (
            len(tab._tile_items) == 3
            and tuple(w.hwnd for w in tab._active_windows) == hwnds)
        report["real_three_master_radios"] = len(tab._master_radio_buttons) == 3
        assert all(report[key] for key in (
            "physical_grid_3x4","preview_grid_2x",
            "three_preview_cards","real_three_master_radios"))

        def preview_positions():
            return [(
                int(tab._tile_items[(w.hwnd,w.pid)][0].grid_info()["row"]),
                int(tab._tile_items[(w.hwnd,w.pid)][0].grid_info()["column"]))
                for w in tab._active_windows]
        assert preview_positions() == [(0,0),(0,1),(1,0)]
        report["original_C20_preview_2x_positions"] = preview_positions()

        for i in range(8):
            pump(150)
            if (tab._preview_controller is not None
                    and set(tab._preview_controller.active_hwnds) == set(hwnds)):
                break
        controller = tab._preview_controller
        assert controller is not None
        assert set(controller.active_hwnds) == set(hwnds)
        before_slots = {h:(controller._slots[h].thumbnail,
                           controller._slots[h].destination) for h in hwnds}
        report["real_native_dwm_3_sources"] = sorted(controller.active_hwnds)

        # Select second preview via ACTUAL radio. This must not reorder
        # thumbnails but MUST put that HWND at physical layout slot 0.
        tab._master_radio_buttons[1].invoke()
        assert tab.master_selection.selected == (hwnds[1],pid)
        assert tab.layout_master_hwnd == hwnds[1]
        report["master_second_preview_card"] = (
            tab._active_windows[0].hwnd == hwnds[0]
            and tab.master_selection.hwnd == hwnds[1])
        assert report["master_second_preview_card"]
        assert tab._toggle_layout()

        for i in range(17):
            pump(200)
            if (tab._layout_last_result is not None
                    and tab._layout_last_result.code == "GRID_APPLIED"):
                break
        assert tab._layout_last_result is not None
        assert tab._layout_last_result.code == "GRID_APPLIED"
        physical = {h:layout_backend.window_rect(h) for h in hwnds}
        width = rect_before[hwnds[1]][2]-rect_before[hwnds[1]][0]
        expected_xy = {
            hwnds[1]:(0,0), hwnds[0]:(width+8,0),
            hwnds[2]:(2*(width+8),0),
        }
        assert all(physical[h][:2] == point for h,point in expected_xy.items())
        assert all((physical[h][2]-physical[h][0],
                    physical[h][3]-physical[h][1]) == (
                    rect_before[h][2]-rect_before[h][0],
                    rect_before[h][3]-rect_before[h][1]) for h in hwnds)
        report["physical_grid_master_first_local_policy"] = {
            str(h):physical[h][:2] for h in hwnds}
        report["preview_still_2x_while_physical_3x4"] = (
            preview_positions() == [(0,0),(0,1),(1,0)]
            and (tab.grid_cols,tab.grid_rows) == (3,4)
            and tab.preview_grid_var.get() == "2x")
        assert report["preview_still_2x_while_physical_3x4"]

        # ACTUAL preview header arrow: third moves left. It does NOT
        # select/alter Master nor move physical source windows.
        wthird = original_rows[2]
        tab._tile_items[(wthird.hwnd,wthird.pid)][3].invoke()
        root.update()
        pump(190)
        report["preview_reordered_independent"] = (
            tuple(w.hwnd for w in tab._active_windows)
            == (hwnds[0],hwnds[2],hwnds[1])
            and tab.master_selection.selected == (hwnds[1],pid)
            and (tab.grid_cols,tab.grid_rows) == (3,4)
            and tab.preview_grid_var.get() == "2x"
            and preview_positions() == [(0,0),(0,1),(1,0)])
        assert report["preview_reordered_independent"]
        assert {h:(controller._slots[h].thumbnail,
                   controller._slots[h].destination) for h in hwnds} == before_slots

        # S19 model: source is selected 2nd preview/master HWND, two
        # SLAVES are the two OTHER HWNDs. No native input is ever posted.
        read = NativeClientRectReader()
        metrics = {(h,pid):read.size(h,pid) for h in hwnds}
        model = InputSyncModel()
        assert allowed() and model.start(producer.read_snapshot(),
                                         (hwnds[1],pid), max_windows=3)
        report["s19_two_slave_hwnds"] = tuple(h for h,p in model.slaves)
        assert report["s19_two_slave_hwnds"] == (hwnds[0],hwnds[2])
        master_client = metrics[(hwnds[1],pid)]
        px = master_client.width // 3
        py = master_client.height // 4
        assert model.queue_mouse(px,py,button="left",pressed=True,
                                 sizes=metrics,now=100.0) == 2
        assert model.queue_mouse(px,py,button="left",pressed=False,
                                 sizes=metrics,now=101.0) == 2
        dispatched = []
        def live_ok(h,p):
            return (h in hwnds and p == pid
                    and native.is_window(h) and native.process_id(h) == p)
        while model.pending:
            assert model.dispatch_one(sink=dispatched.append,
                                      identity_ok=live_ok,
                                      permission_ok=allowed) is not None
        report["s19_fifo_safe_model_actions"] = [
            [e.target[0],e.action,e.x,e.y] for e in dispatched]
        assert [(e.target[0],e.action) for e in dispatched] == [
            (hwnds[0],"down"),(hwnds[2],"down"),
            (hwnds[0],"up"),(hwnds[2],"up")]
        report["s19_actual_client_sizes"] = {
            str(h):[metrics[h,pid].width, metrics[h,pid].height] for h in hwnds}
        assert layout_backend.window_rect(foreign) == unrelated_rect
        report["unrelated_hwnd_untouched"] = True

        # 3 -> 2: close ONLY a test-owned Tk source, publish revised S09
        # snapshot, verify C03/C05/C17 stale HWND resource cleanup.
        pending = InputSyncModel()
        assert pending.start(producer.read_snapshot(),
                             (hwnds[1],pid),max_windows=3)
        assert pending.queue_mouse(px,py,button="middle",pressed=True,
                                   sizes=metrics,now=200.0) == 2
        sources[2].destroy()
        root.update()
        producer.replace(original_rows[:2])
        for i in range(10):
            pump(220)
            active = tab._preview_controller
            if (tuple(w.hwnd for w in tab._active_windows)
                    == hwnds[:2] and active is not None
                    and set(active.active_hwnds) == set(hwnds[:2])):
                break
        report["three_to_two_tiles"] = (
            tuple(w.hwnd for w in tab._active_windows) == hwnds[:2]
            and len(tab._tile_items) == 2)
        report["three_to_two_dwm"] = (
            tab._preview_controller is not None
            and set(tab._preview_controller.active_hwnds) == set(hwnds[:2])
            and hwnds[2] not in tab._preview_controller.active_hwnds)
        report["three_to_two_master_survives"] = (
            tab.master_selection.selected == (hwnds[1],pid)
            and len(tab._master_radio_buttons) == 2)
        assert all(report[k] for k in (
            "three_to_two_tiles", "three_to_two_dwm",
            "three_to_two_master_survives"))
        assert tab._preview_controller is controller
        assert hwnds[2] not in controller._slots
        assert preview_positions() == [(0,0),(0,1)]

        # Old 3-window C19 model cannot send to dead slave HWND. First
        # queued event can target still-live #1; the next must fail-closed.
        first = pending.dispatch_one(sink=lambda e:None,
                                     identity_ok=live_ok,
                                     permission_ok=allowed)
        blocked = pending.dispatch_one(sink=lambda e:None,
                                       identity_ok=live_ok,
                                       permission_ok=allowed)
        report["stale_third_hwnd_blocks_input_model"] = (
            first is not None and blocked is None and
            not pending.active and pending.pending == 0)
        assert report["stale_third_hwnd_blocks_input_model"]

        # Revoke simulated verified token: Start returns to Info,
        # background layout stops, actual old DWM thumbnails are freed.
        remaining_slots = tuple(controller.active_hwnds)
        claims.clear()
        app.apply_info_snapshot(claims.snapshot)
        root.update()
        report["revoke_info_only"] = (
            app.lifecycle.current == "info_tab"
            and app.lifecycle.visible == {"info_tab"})
        report["revoke_cleans_dwm_and_layout"] = (
            tab._preview_controller is None
            and tab._tile_items == {}
            and not controller.active_hwnds
            and not tab.layout_active
            and not tab.sync_layout_running
            and tab.layout_max_windows == 0
            and not tab.poller.active and not tab.maintenance.active)
        assert report["revoke_info_only"]
        assert report["revoke_cleans_dwm_and_layout"]
        report["previous_dwm_hwnds_released"] = remaining_slots
        previous_moves = len(layout_backend.moves)
        # Another user move of a remaining TEST HWND will not be overridden.
        assert layout_backend.backend.move_no_resize(hwnds[0],620,380)
        pump(950)
        report["revoke_no_late_layout_move"] = (
            len(layout_backend.moves) == previous_moves
            and layout_backend.window_rect(hwnds[0])[:2] == (620,380))
        assert report["revoke_no_late_layout_move"]
        assert layout_backend.window_rect(foreign) == unrelated_rect
        report["native_game_input_events_sent"] = 0
        report["status"] = "PASS_NATIVE_S20_THREE_HWND_DWM_MASTER_LAYOUT_INPUT_MODEL"
    except Exception as exc:
        report["status"] = "FAIL_NATIVE_S20_THREE_HWND_COMBINED"
        report["error"] = f"{type(exc).__name__}: {exc}"
        report["traceback"] = traceback.format_exc(limit=25)
    finally:
        if app is not None:
            try: app.shutdown()
            except Exception as exc:
                report["cleanup_error"] = str(exc)
                report["status"] = "FAIL_CLEANUP"
        for source in sources:
            try: source.destroy()
            except Exception: pass
        if other is not None:
            try: other.destroy()
            except Exception: pass
        if root is not None:
            try: root.destroy()
            except Exception as exc:
                report["destroy_error"] = str(exc)
                report["status"] = "FAIL_CLEANUP"
        if temp_ini is not None:
            temp_ini.cleanup()
        REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),
                          encoding="utf-8")
        for name,value in report.items():
            if name != "traceback":
                print("S20_"+name.upper()+"="+json.dumps(value,ensure_ascii=True))
    return 0 if report["status"] == (
        "PASS_NATIVE_S20_THREE_HWND_DWM_MASTER_LAYOUT_INPUT_MODEL") else 1


if __name__ == "__main__":
    raise SystemExit(run())
