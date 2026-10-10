"""S88 genuine Windows DWM source-list loss with one injected unregister fault.

The two real native Tk HWNDs belong solely to this smoke process. Source-list
removal is simulated by a new immutable S09 test snapshot, NOT a game event.
"""
from __future__ import annotations

import json
import os
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tests")]
OUT = ROOT / "artifacts" / "s88"
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT / "native_auto_source_loss_dwm_fault.json"


def run():
    report = {
        "task": "S88",
        "status": "NOT_RUN",
        "windows": "REAL_TEST_OWNED_TK_HWND_PID",
        "source_loss": "SIMULATED_C04_CACHE_DISAPPEARANCE",
        "fault": "THROW_AFTER_FIRST_REAL_DWM_UNREGISTER",
        "actual_game": "NOT_RUN",
        "real_info": "NOT_AVAILABLE",
        "product_exe": "NOT_BUILT",
    }
    root = None
    preview = None
    try:
        if os.name != "nt":
            raise RuntimeError("WINDOWS_REQUIRED")
        import tkinter as tk
        from test_s15 import prepared
        from start_tab import TLMStartTab
        from dwm_preview import NativeDwmBackend, ReadOnlyDwmPreviews, PreviewPlacement
        from start_windows import GameWindow
        from start_polling import WindowSnapshot

        events = []

        class NativeTraced(NativeDwmBackend):
            def __init__(self):
                super().__init__()
                self.destinations = []
                self.unregister_count = 0

            def create_destination(self, *args):
                destination = super().create_destination(*args)
                self.destinations.append(destination)
                events.append(("destination_created", int(destination)))
                return destination

            def unregister(self, thumb):
                super().unregister(thumb)
                self.unregister_count += 1
                events.append(("real_native_unregister", int(thumb)))
                if self.unregister_count == 1:
                    raise OSError("S88_TEST_THROW_AFTER_REAL_NATIVE_UNREGISTER")

            def destroy_destination(self, hwnd):
                events.append(("real_native_destination_destroy", int(hwnd)))
                return super().destroy_destination(hwnd)

        backend = NativeTraced()
        root = tk.Tk()
        root.title("S88 native DWM automatic C04 test-owned host")
        root.geometry("540x245+110+50")
        sources = []
        for idx in range(2):
            source = tk.Toplevel(root)
            source.title(f"S88 SOURCE {idx + 1} TEST ONLY")
            source.geometry(f"210x145+{80 + 230 * idx}+420")
            tk.Label(source, text="TEST OWNED SOURCE NOT GAME").pack()
            sources.append(source)
        root.update_idletasks()
        root.update()

        owner = int(backend._ancestor(int(root.winfo_id()), 2))
        pid = os.getpid()
        hwnds = tuple(int(backend._ancestor(int(w.winfo_id()), 2)) for w in sources)
        assert len(set(hwnds)) == 2 and all(
            backend.source_matches(h, pid) for h in hwnds), hwnds

        placements = tuple(
            PreviewPlacement(h, pid, owner, 25 + i * 235, 40, 190, 110)
            for i, h in enumerate(hwnds))
        preview = ReadOnlyDwmPreviews(backend)
        result = preview.sync(placements)
        assert result.rendered == hwnds and not result.errors, result
        assert all(backend._is_window(d) for d in backend.destinations)
        report["two_real_dwm_sources_registered"] = True

        rows = tuple(
            GameWindow(h, pid, f"S88 test window {i}", "TEST_OWNED", "NOT_GAME.exe")
            for i, h in enumerate(hwnds))
        obj = prepared(rows)
        obj._preview_cleanup_faulted = False
        obj._preview_controller = preview
        obj._update_master_combobox = lambda windows: None
        # S15 test fixture overrides _sync_tiles; restore the real bound
        # Start C04 callback for this actual Windows/native DWM test.
        obj._sync_tiles = lambda windows: TLMStartTab._sync_tiles(obj, windows)
        obj._schedule_preview = lambda: None

        class NativeTkFrame(tk.Frame):
            def destroy(self):
                events.append(("real_tk_frame_destroy", int(self.winfo_id())))
                return super().destroy()

        frames = [NativeTkFrame(root) for _ in rows]
        obj._tile_items = {
            (w.hwnd, w.pid): (frames[i], None, None)
            for i, w in enumerate(rows)}

        # Real DWM thumbnails, but test-generated cached list loses one HWND.
        # This exercises _sync_tiles() automatic native clear, NOT C15 click.
        obj._sync_tiles((rows[1],))
        assert obj._preview_cleanup_faulted
        assert obj._preview_controller is None
        assert obj._tile_items == {} and obj._active_windows == ()
        assert obj._observed_windows == ()
        assert "DWM" in obj.preview_status.value
        assert backend.unregister_count == 2, backend.unregister_count
        assert preview.active_hwnds == ()
        assert all(not backend._is_window(d) for d in backend.destinations)
        assert all(not f.winfo_exists() for f in frames)
        first_frame_destroy = min(
            i for i, e in enumerate(events) if e[0] == "real_tk_frame_destroy")
        last_native_teardown = max(
            i for i, e in enumerate(events)
            if e[0] in ("real_native_unregister", "real_native_destination_destroy"))
        assert last_native_teardown < first_frame_destroy, events

        # Even a subsequent valid S09 cache cannot silently recreate native
        # DWM after uncertain cleanup in the current Tk owner lifetime.
        obj._present_cached_snapshot(WindowSnapshot(89, rows, True))
        assert not obj._tile_items and obj._preview_controller is None
        assert backend.unregister_count == 2
        report["native_unregisters"] = backend.unregister_count
        report["native_destinations_destroyed"] = len(backend.destinations)
        report["tk_frames_destroyed"] = len(frames)
        report["status"] = "PASS_NATIVE_S88_C04_AUTO_SOURCE_LOSS_DWM_FAILURE_LATCH"
    except Exception as exc:
        report["status"] = "FAIL_NATIVE_S88"
        report["error_type"] = type(exc).__name__
        report["error_text"] = str(exc)[:400]
        report["traceback"] = traceback.format_exc(limit=16)
    finally:
        if preview is not None:
            try:
                preview.shutdown()
            except Exception:
                pass
        if root is not None:
            try:
                root.destroy()
            except Exception:
                pass
        REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2),
                          encoding="utf-8")
        for k, v in report.items():
            if k != "traceback":
                print("S88_" + k.upper() + "=" + json.dumps(v, ensure_ascii=True))
    return 0 if report["status"] == (
        "PASS_NATIVE_S88_C04_AUTO_SOURCE_LOSS_DWM_FAILURE_LATCH") else 1


if __name__ == "__main__":
    raise SystemExit(run())
