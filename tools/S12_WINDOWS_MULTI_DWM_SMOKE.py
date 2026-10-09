"""S12 Windows: three real TEST-OWNED Tk top-level HWNDs, DWM + Start auth lifecycle.

No game installed, no fake game window in S09 production discovery, and no
game action. An isolated test-only Producer feeds real Tk HWNDs to the Start
view solely for native Win32 geometry/lifetime testing.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "artifacts" / "s12"
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT / "native_multi_dwm.json"


def run():
    report = {
        "task": "S12", "status": "NOT_RUN", "os": os.name,
        "source_kind": "THREE_REAL_TEST_OWNED_TK_TOP_LEVELS_NOT_GAME",
        "actual_game": "NOT_RUN", "server_auth": "NOT_RUN",
        "game_actions": 0, "original_pixel_diff": "NOT_RUN",
        "standalone_exe": "NOT_BUILT",
    }
    root = None
    win_sources = []
    view = None
    app = None
    controller = None
    try:
        if os.name != "nt":
            raise RuntimeError("Real Windows desktop required")
        import ctypes
        from ctypes import wintypes
        import tkinter as tk
        from tkinter import ttk
        from dwm_preview import NativeDwmBackend, PreviewPlacement, ReadOnlyDwmPreviews
        from start_windows import GameWindow
        from start_polling import WindowSnapshot
        from start_tab import TLMStartTab
        from info_tab import TLMInfoTab
        from shell import TLMMainApp
        from permission_guard import PermissionGuard, VerifiedClaims

        class CountedNative(NativeDwmBackend):
            def __init__(self):
                super().__init__()
                self.created = []
                self.registered = []
                self.unregistered = []
                self.destroyed = []
            def create_destination(self, *args):
                handle = super().create_destination(*args)
                self.created.append(handle)
                return handle
            def register(self, *args):
                handle = super().register(*args)
                self.registered.append(handle)
                return handle
            def unregister(self, thumbnail):
                self.unregistered.append(thumbnail)
                return super().unregister(thumbnail)
            def destroy_destination(self, destination):
                self.destroyed.append(destination)
                return super().destroy_destination(destination)

        native = CountedNative()
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        iswindow = user32.IsWindow
        iswindow.argtypes = [wintypes.HWND]
        iswindow.restype = wintypes.BOOL
        get_rect = user32.GetWindowRect
        get_rect.argtypes = [wintypes.HWND, ctypes.c_void_p]
        get_rect.restype = wintypes.BOOL
        class Rect(ctypes.Structure):
            _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                        ("right", ctypes.c_long), ("bottom", ctypes.c_long)]
        def bounds(hwnd):
            rc = Rect()
            assert get_rect(hwnd, ctypes.byref(rc)), "GetWindowRect failed"
            return (rc.left, rc.top, rc.right - rc.left, rc.bottom - rc.top)
        def pump(ms=250):
            root.after(ms, root.quit)
            root.mainloop()
        def tally(ctrl):
            return [ctrl._slots[h].destination for h in ctrl.active_hwnds]

        root = tk.Tk()
        root.title("S12 host (NOT a Thần Long game)")
        root.geometry("540x425+400+100")
        owner_test = tk.Toplevel(root)
        owner_test.title("S12 3-source DWM owner test")
        owner_test.geometry("500x400+375+150")

        for i in range(3):
            source = tk.Toplevel(root)
            source.title(f"S12 test-owned real Tk window {i+1} -- NOT GAME")
            source.geometry(f"215x160+{35 + (i % 2)*240}+{40+(i//2)*230}")
            tk.Label(source, text=f"Native Win32 source {i+1}\nNOT a game",
                     bg=("#ddddee", "#e1e1e1", "#eeeecc")[i]).pack(
                         fill="both", expand=True)
            win_sources.append(source)

        tiles = []
        for i in range(3):
            tile = tk.Frame(owner_test, width=197, height=110, bg="black")
            tile.place(x=14 + (i % 2)*211, y=30 + (i//2)*142, width=197, height=110)
            tiles.append(tile)
        root.update()
        hwnds = [
            int(native._ancestor(int(src.winfo_id()), 2)) for src in win_sources
        ]
        owner = int(native._ancestor(int(owner_test.winfo_id()), 2))
        pid = os.getpid()
        assert len(set(hwnds)) == 3 and all(native.source_matches(h, pid) for h in hwnds)
        report["source_hwnds"] = hwnds
        report["source_pid"] = pid

        def placements():
            root.update_idletasks()
            return [
                PreviewPlacement(hwnds[i], pid, owner,
                                 tiles[i].winfo_rootx(), tiles[i].winfo_rooty(),
                                 tiles[i].winfo_width(), tiles[i].winfo_height())
                for i in range(3)
            ]

        controller = ReadOnlyDwmPreviews(native)
        first = controller.sync(placements())
        assert len(first.rendered) == 3 and not first.errors, first.errors
        initial_dest = tally(controller)
        initial_rect = [bounds(d) for d in initial_dest]
        expected_initial = [(p.x, p.y, p.width, p.height) for p in placements()]
        report["three_registration_pass"] = initial_rect == expected_initial
        assert report["three_registration_pass"], (initial_rect, expected_initial)

        # Root move must result in a screen-space position change, not re-register.
        owner_test.geometry("500x400+400+210")
        root.update()
        moved = controller.sync(placements())
        assert len(moved.rendered) == 3 and not moved.errors, moved.errors
        report["move_keeps_same_destinations"] = tally(controller) == initial_dest
        report["move_geometry_pass"] = [bounds(d) for d in initial_dest] == [
            (p.x, p.y, p.width, p.height) for p in placements()]
        assert report["move_keeps_same_destinations"] and report["move_geometry_pass"]

        # Resize a preview surface: same DWM registration, new destination rect.
        tiles[2].place_configure(width=175, height=94)
        owner_test.geometry("525x440+425+180")
        root.update()
        resized = controller.sync(placements())
        assert len(resized.rendered) == 3 and not resized.errors, resized.errors
        report["resize_geometry_pass"] = (
            [bounds(d) for d in initial_dest] ==
            [(p.x, p.y, p.width, p.height) for p in placements()])
        assert report["resize_geometry_pass"]

        # A real source closes; its HWND must be removed, others stay registered.
        vanished = hwnds[1]
        win_sources[1].destroy()
        root.update()
        survivor = [p for p in placements() if p.hwnd != vanished]
        alive = controller.sync(survivor)
        report["closed_source_cleanup"] = (
            len(alive.rendered) == 2 and
            not iswindow(initial_dest[1]) and
            set(controller.active_hwnds) == {hwnds[0], hwnds[2]})
        assert report["closed_source_cleanup"]

        # Invalid PID must revoke the source's previous DWM resources.
        bad = PreviewPlacement(hwnds[0], pid + 1, owner,
                               survivor[0].x, survivor[0].y, 197, 110)
        denied = controller.sync((bad, survivor[-1]))
        report["pid_mismatch_clears_old_destination"] = (
            denied.rendered == (hwnds[2],) and
            denied.errors[0][1] == "STALE_CLOSED_OR_HUNG_SOURCE"
            and not iswindow(initial_dest[0]))
        assert report["pid_mismatch_clears_old_destination"]

        # Manual owner hide/restore: a hidden tab must release compositor
        # resources; a new valid source snapshot can register again.
        owner_test.withdraw()
        root.update()
        controller.clear()
        report["hide_all_cleared"] = not controller.active_hwnds and all(
            not iswindow(d) for d in initial_dest)
        assert report["hide_all_cleared"]
        owner_test.deiconify()
        root.update()
        resumed = controller.sync((survivor[0], survivor[-1]))
        assert len(resumed.rendered) == 2 and not resumed.errors, resumed.errors
        controller.shutdown()
        assert not controller.active_hwnds
        report["native_handles_balanced"] = (
            len(native.registered) == len(native.unregistered)
            and len(native.created) == len(native.destroyed))
        report["native_created"] = len(native.created)
        report["native_destroyed"] = len(native.destroyed)
        assert report["native_handles_balanced"]

        # Separate integration: actual Start tab on real Windows/Tk, but
        # EXPLICIT TEST-ONLY producer supplies real test-owned HWNDs. This
        # never reaches production S09 game discovery and grants no app token.
        owner_test.destroy()
        class TestOwnedProducer:
            def __init__(self):
                self.active = False
                self.revision = 0
            def start(self):
                self.active = True
                self.revision += 1
                return True
            def stop(self):
                self.active = False
                self.revision += 1
            def read_snapshot(self):
                # This is a test fixture, NOT game matching or fake process PID.
                windows = tuple(GameWindow(
                    h, pid, f"S12 Test Tk window {i} (NOT GAME)",
                    "TkTop", "python.exe") for i, h in enumerate((hwnds[0], hwnds[2])))
                return WindowSnapshot(self.revision, windows, self.active)

        source_test = TestOwnedProducer()
        def create_start(parent):
            nonlocal view
            view = TLMStartTab(
                parent, producer=source_test, preview_backend_factory=CountedNative)
            return view
        app = TLMMainApp(root, {
            "info_tab": lambda parent: TLMInfoTab(parent),
            "start_tab": create_start,
        })
        app.position_window_top_right()
        root.update()
        report["default_info_only"] = app.lifecycle.visible == {"info_tab"} and view is None
        assert report["default_info_only"]

        guard = PermissionGuard()
        ok = guard.receive_token(
            "S12-ISOLATED-TEST-CLAIMS-ONLY",
            lambda _: VerifiedClaims(
                permissions=frozenset({"start_tab", "info_tab"}),
                plan_status="TEST_ONLY", max_windows=3))
        assert ok
        app.apply_info_snapshot(guard.snapshot)
        root.update()
        app.notebook.select(app._tab_frames["start_tab"])
        root.update()
        pump(420)
        assert view is not None and view.poller.active
        report["tk_view_real_sources"] = len(view._preview_controller.active_hwnds) if view._preview_controller else 0
        report["tk_view_tiles"] = len(view._tile_items)
        assert report["tk_view_real_sources"] == 2, view.preview_status.cget("text")

        tk_before = tally(view._preview_controller)
        # Main root translation triggers real <Configure> callback; no need
        # for a changed S09 cache revision or a game input event.
        root.geometry("450x610+500+55")
        root.update()
        pump(240)
        report["tk_root_move_repositions"] = (
            bool(view._preview_controller) and
            tally(view._preview_controller) == tk_before and
            all(bounds(view._preview_controller._slots[w.hwnd].destination) ==
                (view._tile_items[(w.hwnd, w.pid)][2].winfo_rootx(),
                 view._tile_items[(w.hwnd, w.pid)][2].winfo_rooty(),
                 view._tile_items[(w.hwnd, w.pid)][2].winfo_width(),
                 view._tile_items[(w.hwnd, w.pid)][2].winfo_height())
                for w in view._active_windows))
        assert report["tk_root_move_repositions"]

        root.withdraw()
        root.update()
        report["tk_owner_unmap_teardown"] = (
            view._preview_controller is None and
            all(not iswindow(d) for d in tk_before))
        assert report["tk_owner_unmap_teardown"]
        root.deiconify()
        root.update()
        pump(290)
        report["tk_owner_restore_recreates"] = (
            view._preview_controller is not None and
            len(view._preview_controller.active_hwnds) == 2)
        assert report["tk_owner_restore_recreates"]

        tk_old = tally(view._preview_controller)
        guard.clear()
        app.apply_info_snapshot(guard.snapshot)
        root.update()
        report["revocation_clears_tk_and_dwm"] = (
            app.lifecycle.current == "info_tab" and
            not view.poller.active and
            view._preview_controller is None and
            not view.table.get_children() and
            all(not iswindow(d) for d in tk_old))
        assert report["revocation_clears_tk_and_dwm"]
        report["status"] = "PASS_NATIVE_S12_THREE_HWND_DWM_AND_AUTH_LIFECYCLE"
    except Exception as exc:
        report["status"] = "FAIL_NATIVE_S12_MULTI_DWM"
        report["error"] = f"{type(exc).__name__}: {exc}"
        report["traceback"] = traceback.format_exc(limit=15)
    finally:
        if app is not None:
            try: app.shutdown()
            except Exception as exc:
                report["cleanup_error"] = str(exc)
                report["status"] = "FAIL_CLEANUP"
        if controller is not None:
            try: controller.shutdown()
            except Exception: pass
        for source in win_sources:
            try: source.destroy()
            except Exception: pass
        if root is not None:
            try: root.destroy()
            except Exception as exc:
                report["destroy_error"] = str(exc)
                report["status"] = "FAIL_CLEANUP"
        REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        for key, value in report.items():
            if key != "traceback":
                print("S12_" + key.upper() + "=" + json.dumps(value, ensure_ascii=False))
    return 0 if report["status"] == "PASS_NATIVE_S12_THREE_HWND_DWM_AND_AUTH_LIFECYCLE" else 1


if __name__ == "__main__":
    raise SystemExit(run())
