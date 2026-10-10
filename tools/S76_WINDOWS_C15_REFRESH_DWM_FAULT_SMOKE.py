"""S76 actual Windows C15 user refresh native DWM exception safety.

Use REAL DWM register, update, unregister, native destination HWNDs, and
real Tk-owned source HWNDs / frames. Source windows are TEST OWNED PYTHON,
NOT original game/authorization/product. Inject one exception AFTER the
genuine Windows DwmUnregisterThumbnail succeeds. No fake live game.
"""
from __future__ import annotations
import json
import os
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/"src"), str(ROOT/"tests")]
OUT = ROOT/"artifacts"/"s76"
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT/"native_c15_refresh_cleanup.json"


def run():
    report = {
        "task":"S76","status":"NOT_RUN",
        "sources":"TWO_TEST_OWNED_REAL_TK_NATIVE_HWNDS_NOT_GAME",
        "test_fault":"THROW_AFTER_FIRST_REAL_DWM_UNREGISTER",
        "original_game":"NOT_EXECUTED",
        "signed_info":"NOT_CONNECTED",
        "product_exe":"DIAGNOSTIC_NOT_PRODUCT",
    }
    root = None
    preview = None
    try:
        if os.name != "nt":
            raise RuntimeError("WINDOWS_REQUIRED")
        import tkinter as tk
        from test_s15 import prepared
        from dwm_preview import NativeDwmBackend, ReadOnlyDwmPreviews, PreviewPlacement
        from start_windows import GameWindow
        from start_polling import WindowSnapshot

        events = []
        class TracedNative(NativeDwmBackend):
            def __init__(self):
                super().__init__()
                self.destinations = []
                self.native_unregister_count = 0
            def create_destination(self, *args):
                handle = super().create_destination(*args)
                self.destinations.append(handle)
                events.append(("create_destination", handle))
                return handle
            def unregister(self, thumb):
                super().unregister(thumb)
                self.native_unregister_count += 1
                events.append(("native_unregister", int(thumb)))
                if self.native_unregister_count == 1:
                    raise OSError("S76_INJECTED_AFTER_REAL_DWM_UNREGISTER")
            def destroy_destination(self, h):
                events.append(("destroy_destination", int(h)))
                return super().destroy_destination(h)

        backend = TracedNative()
        root = tk.Tk()
        root.title("S76 DWM native original-free test root")
        root.geometry("530x240+95+40")
        sources = []
        for i in range(2):
            source = tk.Toplevel(root)
            source.title(f"S76 TEST source {i+1} NO GAME")
            source.geometry(f"210x145+{80+i*235}+410")
            tk.Label(source,text="TEST-OWNED WINDOW NO GAME").pack()
            sources.append(source)
        root.update_idletasks()
        root.update()
        owner = int(backend._ancestor(int(root.winfo_id()), 2))
        pid = os.getpid()
        hwnds = tuple(int(backend._ancestor(int(w.winfo_id()),2))
                      for w in sources)
        assert len(set(hwnds))==2
        assert all(backend.source_matches(h,pid) for h in hwnds)
        report["native_hwnd_pid_identity_readback"] = True

        # Native actual DWM preview thumbnails; test-owned placement does NOT
        # assert original C15 per-thumbnail UI pixel geometry.
        places = tuple(PreviewPlacement(h,pid,owner,25+i*235,40,190,110)
                       for i,h in enumerate(hwnds))
        preview = ReadOnlyDwmPreviews(backend)
        result = preview.sync(places)
        assert result.rendered == hwnds and not result.errors, result
        assert len(backend.destinations)==2
        assert all(backend._is_window(h) for h in backend.destinations)
        report["two_REAL_native_DWM_thumbnails_registered"] = True

        rows = tuple(GameWindow(h,pid,f"TEST source {i}","TEST_OWNED","NOT_GAME.exe")
                     for i,h in enumerate(hwnds))
        obj = prepared(rows)
        obj.poller.producer.snap = WindowSnapshot(76, rows, True)
        obj._preview_controller = preview
        class TracedFrame(tk.Frame):
            def destroy(self):
                events.append(("destroy_frame",int(self.winfo_id())))
                return super().destroy()
        frames = tuple(TracedFrame(root) for _ in rows)
        for i,(h,_) in enumerate(zip(hwnds,rows)):
            obj._tile_items[(h,pid)] = (frames[i],None,None)
        # Drop three S15 fixture frames; this script exclusively owns two
        # native Tk frames corresponding to its two test-owned HWNDs.
        for key in list(obj._tile_items):
            if key not in {(h,pid) for h in hwnds}:
                del obj._tile_items[key]

        # User-visible "Làm mới" callback with a true native teardown fault.
        returned = obj.refresh_window_preview_list()
        report["refresh_reports_explicit_native_failure"] = (
            returned is False and obj._preview_cleanup_faulted
            and obj._state.code=="ERROR"
            and "DWM" in obj.preview_status.value)
        assert report["refresh_reports_explicit_native_failure"]
        report["all_native_thumbnails_deregistered_attempted"] = (
            backend.native_unregister_count==2
            and not preview.active_hwnds)
        assert report["all_native_thumbnails_deregistered_attempted"]
        report["all_real_native_destination_hwnds_destroyed"] = (
            all(not backend._is_window(h) for h in backend.destinations))
        assert report["all_real_native_destination_hwnds_destroyed"]
        report["all_native_Tk_frames_destroyed_after_DWM"] = (
            all(not w.winfo_exists() for w in frames)
            and len([e for e in events if e[0]=="destroy_frame"])==2
            and max(i for i,e in enumerate(events)
                    if e[0] in ("native_unregister","destroy_destination"))
             < min(i for i,e in enumerate(events)
                   if e[0]=="destroy_frame"))
        assert report["all_native_Tk_frames_destroyed_after_DWM"],events
        report["no_ghost_Tk_or_repeat_DWM_rebuild"] = (
            not obj._tile_items and obj._preview_controller is None
            and not obj._active_windows
            and obj.refresh_window_preview_list() is False
            and len(backend.destinations)==2)
        assert report["no_ghost_Tk_or_repeat_DWM_rebuild"]
        report["status"]="PASS_NATIVE_S76_C15_REAL_DWM_FAULT_CLEANS_ALL_TK_FRAMES"
    except Exception as exc:
        report["status"]="FAIL_NATIVE_S76"
        report["error_type"]=type(exc).__name__
        report["error_text"]=str(exc)[:300]
        report["traceback"]=traceback.format_exc(limit=15)
    finally:
        if preview is not None:
            try:preview.shutdown()
            except Exception:pass
        if root is not None:
            try:root.destroy()
            except Exception:pass
        REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),
                          encoding="utf-8")
        for key,value in report.items():
            if key!="traceback":
                print("S76_"+key.upper()+"="+json.dumps(value,ensure_ascii=True))
    return 0 if report["status"]==        "PASS_NATIVE_S76_C15_REAL_DWM_FAULT_CLEANS_ALL_TK_FRAMES" else 1


if __name__ == "__main__":
    raise SystemExit(run())
