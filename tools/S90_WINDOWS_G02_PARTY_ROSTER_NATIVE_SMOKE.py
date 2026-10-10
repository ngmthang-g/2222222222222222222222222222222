"""S90 real Windows/Tk HWND/PID Party roster lifecycle — TEST-OWNED, NO GAME.

Exercises the existing S09 immutable snapshot consumer and original G02
3000ms Tk timer with real Windows HWND/PID identity. The RoleReading
provider below is explicitly TEST ONLY. It does not touch a game process
or implement an authentic character reader.
"""
from __future__ import annotations
import json
import os
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / "src"))
OUT = ROOT / "artifacts" / "s90"
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT / "native_party_hwnd_pid_lifecycle.json"


def run():
    report = {
        "task":"S90",
        "status":"NOT_RUN",
        "test_owned_sources":"REAL_WIN32_TK_HWND_PID",
        "cache":"EXPLICIT_TEST_S09_IMMUTABLE_SNAPSHOT",
        "role_names":"TEST_ONLY_NOT_GAME_ROLE_NAMES",
        "game":"NOT_RUN",
        "license":"NOT_CONNECTED",
        "product_exe":"NOT_PRODUCT",
    }
    root=None
    ctl=None
    try:
        if os.name!="nt":
            raise RuntimeError("WINDOWS_REQUIRED")
        import tkinter as tk
        from dwm_preview import NativeDwmBackend
        from auto_role_provenance import RoleReading
        from start_windows import GameWindow
        from start_polling import WindowSnapshot
        from party_roster import TkPartyRosterRefresh, PARTY_REFRESH_MS

        native=NativeDwmBackend()
        root=tk.Tk()
        root.title("S90 Tk test owner NO GAME")
        root.geometry("520x320+50+50")
        game=tk.Toplevel(root)
        game.title("S90 TEST WINDOW TITLE NOT ROLE NAME")
        game.geometry("240x160+620+70")
        tk.Label(game, text="TEST-OWNED PYTHON WINDOW").pack()
        root.update_idletasks()
        root.update()
        hwnd=int(native._ancestor(int(game.winfo_id()), 2))
        pid=os.getpid()
        assert native.source_matches(hwnd,pid), (hwnd,pid)
        assert native._is_window(hwnd)
        row=GameWindow(hwnd,pid,"TITLE IS NOT GAME ROLE","TEST_ONLY","NOT_GAME.exe")
        class Source:
            def __init__(self):
                self.value=WindowSnapshot(1,(row,),True)
                self.reads=0
            def read_snapshot(self):
                self.reads +=1
                return self.value
        producer=Source()
        def trusted_test_reader(h, p):
            # Recheck real Windows state before mapping the test-owned RoleName.
            assert (h,p)==(hwnd,pid) and native.source_matches(h,p)
            return RoleReading(h,p,"<b>Nhân vật thử S90</b>")

        states=[]
        ctl=TkPartyRosterRefresh(
            root,producer,
            lambda roster:states.append((roster.code,roster.ready_names())),
            read_role=trusted_test_reader)
        ctl.start()
        assert PARTY_REFRESH_MS==3000
        assert states==[] and producer.reads==0
        deadline=time.monotonic()+8.0
        while time.monotonic()<deadline:
            root.update()
            if ctl.roster.ready_names()==("Nhân vật thử S90",):
                break
            time.sleep(0.016)
        assert ctl.roster.ready_names()==("Nhân vật thử S90",), states
        assert ctl.roster.members[0].hwnd==hwnd
        assert ctl.roster.members[0].pid==pid
        report["real_start_cache_3s_to_test_role_ready"] = True
        report["real_native_hwnd_pid_verified"]=True

        # Genuine Windows HWND destroyed. Next S09 cache revision removes it;
        # Party must forget its name WITHOUT a second EnumWindows.
        game.destroy()
        root.update()
        assert not native._is_window(hwnd)
        producer.value=WindowSnapshot(2,(),True)
        deadline=time.monotonic()+8.0
        while time.monotonic()<deadline:
            root.update()
            if ctl.roster.members==() and ctl.roster.revision==2:
                break
            time.sleep(0.016)
        # An empty successful Party snapshot is an empty real ready list, not
        # stale character identity or "still on team" inference.
        assert ctl.roster.members==(), (ctl.roster,states)
        assert ctl.roster.ready_names()==()
        report["real_native_source_destroy_clears_ready_name"]=True

        before=tuple(states)
        ctl.shutdown()
        root.update()
        assert not ctl.active and ctl.roster.ready_names()==()
        assert states[-1][0]=="STOPPED"
        report["tk_shutdown_cancels_callbacks"]=True
        report["status"]="PASS_NATIVE_S90_G02_PARTY_REAL_HWND_PID_CACHED_ROSTER"
    except Exception as exc:
        report["status"]="FAIL_NATIVE_S90"
        report["error_type"]=type(exc).__name__
        report["error_text"]=str(exc)[:400]
        report["traceback"]=traceback.format_exc(limit=15)
        print(report["traceback"])
    finally:
        if ctl is not None:
            try:ctl.shutdown()
            except Exception:pass
        if root is not None:
            try:root.destroy()
            except Exception:pass
        REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
        for k,v in report.items():
            if k!="traceback":
                print("S90_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if report["status"]=="PASS_NATIVE_S90_G02_PARTY_REAL_HWND_PID_CACHED_ROSTER" else 1


if __name__=="__main__":
    raise SystemExit(run())
