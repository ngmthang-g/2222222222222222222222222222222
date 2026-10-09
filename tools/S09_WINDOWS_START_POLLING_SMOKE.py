"""S09 Windows Tk main-thread cache consumer + genuine Win32 background producer.

Read-only. No game launch, process memory access, clicks, authorization bypass
or synthetic game handles. The native worker is independent from Tk.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import threading
import time
import traceback

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s09"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"win32_start_cache.json"


def run():
    info={"task":"S09","status":"NOT_RUN","platform":os.name,
          "real_game_running":False,"auth_server":"NOT_RUN",
          "game_actions":0,"pixel_parity":"NOT_RUN","exe_build":"NOT_BUILT"}
    root=None
    poller=None
    producer=None
    try:
        if os.name!="nt":
            raise RuntimeError("S09 native Win32 smoke requires Windows")
        import tkinter as tk
        from start_windows import NativeWin32Backend
        from start_polling import (
            StartWindowProducer,TkStartCachePoller,START_UI_POLL_MS,
            DISCOVERY_INTERVAL_SECONDS,
        )

        info["discovery_interval_seconds"]=DISCOVERY_INTERVAL_SECONDS
        info["ui_poll_interval_ms"]=START_UI_POLL_MS
        main_ident=threading.get_ident()
        worker_threads=[]
        windows_seen=[]
        consumed=[]
        events=[]

        class TracedBackend:
            def __init__(self):
                worker_threads.append(threading.get_ident())
                self.native=NativeWin32Backend()
            def enumerate_top_level(self):
                worker_threads.append(threading.get_ident())
                visible=self.native.enumerate_top_level()
                windows_seen.append(len(visible))
                return visible
            def __getattr__(self, attr):
                return getattr(self.native,attr)

        root=tk.Tk()
        root.title("S09 native polling test (not Thần Long Mobile)")
        root.geometry("340x120+30+30")
        producer=StartWindowProducer(TracedBackend) # actual 3s cadence
        def on_snapshot(event):
            consumed.append(threading.get_ident())
            events.append({
                "revision":event.snapshot.revision,
                "valid":event.snapshot.valid,
                "window_count":len(event.snapshot.windows),
                "error":event.snapshot.error,
                "added":len(event.delta.added),
                "removed":len(event.delta.removed),
                "reused":len(event.delta.reused),
            })
        poller=TkStartCachePoller(root,producer,on_snapshot) # actual 2000ms cadence
        start=time.monotonic()
        poller._start_refresh()
        root.after(2550,root.quit)
        root.mainloop()
        duration=time.monotonic()-start
        info.update({
            "duration_seconds":round(duration,3),
            "worker_thread_is_background":bool(worker_threads) and all(t!=main_ident for t in worker_threads),
            "worker_enumeration_count":len(windows_seen),
            "worker_enumeration_top_hwnds":windows_seen,
            "tk_consumption_on_main_thread":bool(consumed) and all(t==main_ident for t in consumed),
            "tk_events":events,
            "game_window_count":sum(x["window_count"] for x in events if x["valid"]),
            "real_game_running":False, # CI does not include actual game; never infer from zero.
        })
        assert info["worker_thread_is_background"]
        assert info["worker_enumeration_count"]>=1
        assert info["tk_consumption_on_main_thread"]
        assert any(e["valid"] for e in events), "No valid worker cache reached Tk after 2s poll"
        assert all(e["window_count"]==0 for e in events), "Unexpected candidate on game-free CI"
        assert duration>=2.0
        poller._stop_refresh()
        info["stop_revoked_cache"]=not producer.read_snapshot().valid
        info["stopped_producer"]=not producer.active
        assert info["stop_revoked_cache"] and info["stopped_producer"]
        info["status"]="PASS_NATIVE_WINDOWS_THREADED_START_CACHE"
    except Exception as exc:
        info["status"]="FAIL_NATIVE_START_CACHE"
        info["error"]=type(exc).__name__+": "+str(exc)
        info["traceback"]=traceback.format_exc(limit=8)
    finally:
        if poller is not None:
            poller.shutdown()
            info["poller_closed"]=poller._closed
        if root is not None:
            try: root.destroy()
            except Exception as exc:
                info["status"]="FAIL_TK_CLOSE"
                info["close_error"]=str(exc)
        REPORT.write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding="utf-8")
        for key,value in info.items():
            if key not in {"traceback"}:
                print("S09_"+key.upper()+"="+json.dumps(value,ensure_ascii=False))
    return 0 if info["status"]=="PASS_NATIVE_WINDOWS_THREADED_START_CACHE" else 1


if __name__=="__main__":
    raise SystemExit(run())
