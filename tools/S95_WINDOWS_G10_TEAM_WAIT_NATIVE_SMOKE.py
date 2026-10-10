"""S95 true Windows/Tk HWND/PID G10 read-only bounded TeamID waiter.

ONE REAL TEST-OWNED HWND in real Python process. TeamID and RoleID are
explicit test-injected callback data, NEVER actual game memory or packets.
Exercises original outside-team sentinels, unknown read state,
threading.Event cancellation, closed HWND generation after read.
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
OUT=ROOT/"artifacts"/"s95"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"native_party_readonly_team_wait.json"


def main():
    report={"task":"S95","status":"NOT_RUN",
            "hwnd":"REAL_WINDOWS_TK_TEST_OWNED",
            "teamid_source":"TEST_CALLBACK_NOT_GAME",
            "signed_info":"NOT_CONNECTED",
            "commands_sent":"NONE",
            "product":"NOT_PRODUCT"}
    root=None
    try:
        if os.name!="nt":raise RuntimeError("WINDOWS_REQUIRED")
        import tkinter as tk
        from dwm_preview import NativeDwmBackend
        from start_windows import GameWindow, NativeWin32Backend
        from start_polling import WindowSnapshot
        from party_team_identity import PartyTeamIdentityPreflight
        from party_team_wait import PartyTeamReadOnlyWait

        root=tk.Tk()
        root.title("S95 READ ONLY TEST WINDOW NO GAME")
        root.geometry("310x205+50+60")
        subject=tk.Toplevel(root)
        subject.title("S95 TEST HWND TITLE IS NOT ROLE")
        subject.geometry("220x175+500+80")
        tk.Label(subject,text="TEST-ONLY HWND/PID").pack()
        root.update_idletasks();root.update()
        dwm=NativeDwmBackend()
        native=NativeWin32Backend()
        hwnd=int(dwm._ancestor(int(subject.winfo_id()),2))
        pid=os.getpid()
        assert native.is_window(hwnd) and native.process_id(hwnd)==pid
        report["native_hwnd_pid_real"]=True

        class Source:
            def __init__(self):
                self.value=WindowSnapshot(
                    1,(GameWindow(hwnd,pid,"NOT A CHARACTER",
                                   "TEST_ONLY","python.exe"),),True)
            def read_snapshot(self):return self.value
        src=Source()
        team=[0]
        calls=[0]
        def game_id_records():
            return [(pid,0,"S95 TEST ROLE",10)]
        def read_team(h):
            assert h==hwnd
            calls[0]+=1
            return team[0]
        def preflight(team_reader=read_team):
            return PartyTeamIdentityPreflight(
                start_producer=src,backend=native,
                read_own_ids=game_id_records,
                read_team_id=team_reader,
                allowed=lambda:True)
        def await_out(team_reader=read_team,timeout=.08,poll=.01,cancel=None):
            return PartyTeamReadOnlyWait(preflight(team_reader)).wait(
                ("S95 TEST ROLE",),mode="OUTSIDE",
                timeout_seconds=timeout,poll_seconds=poll,cancel=cancel)

        # Explicit test external sources: diagnostic observation is not
        # authorization to issue any game command.
        r=await_out()
        assert r.code=="DIAGNOSTIC_OBSERVED_ALL_OUTSIDE_NO_GAME_ACTION"
        team[0]=0xFFFFFFFF
        assert await_out().code=="DIAGNOSTIC_OBSERVED_ALL_OUTSIDE_NO_GAME_ACTION"
        report["both_original_no_team_sentinels"]=True

        team[0]=None
        r=await_out()
        assert r.code=="TIMEOUT_NOT_CONFIRMED"
        assert r.last_preflight_code=="TEAMID_UNKNOWN_NOT_OUTSIDE"
        report["none_never_promoted_to_no_team_success"]=True

        team[0]=None
        recovery=[0]
        def transient(h):
            recovery[0]+=1
            return 0 if recovery[0]>2 else None
        r=await_out(team_reader=transient,timeout=.15)
        assert r.code=="DIAGNOSTIC_OBSERVED_ALL_OUTSIDE_NO_GAME_ACTION"
        assert r.attempts>1
        report["transient_unknown_recovers_only_after_real_test_observation"]=True

        team[0]=123
        cancel=threading.Event()
        thread=threading.Thread(
            target=lambda:(time.sleep(.03),cancel.set()),daemon=True)
        thread.start()
        r=await_out(timeout=2,poll=1,cancel=cancel)
        thread.join(1)
        assert r.code=="CANCELLED"
        report["real_cancellation_interrupts_1s_wait"]=True

        # Do NOT claim a stale HWND valid even when the cached S09 snapshot
        # and externally injected own-account record still mention its PID.
        subject.destroy()
        root.update()
        assert not native.is_window(hwnd)
        r=await_out(timeout=.01)
        assert r.code=="BLOCKED_STALE_NATIVE_HWND_PID",r.code
        report["actual_destroyed_hwnd_blocks_observation"]=True
        report["status"]="PASS_NATIVE_S95_G10_READONLY_TEAM_WAIT_CANCEL_HWND"
    except Exception as exc:
        report["status"]="FAIL_NATIVE_S95"
        report["error_type"]=type(exc).__name__
        report["error_text"]=str(exc)[:500]
        report["traceback"]=traceback.format_exc(limit=18)
        print(report["traceback"])
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
        for k,v in report.items():
            if k!="traceback":print("S95_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if report["status"]=="PASS_NATIVE_S95_G10_READONLY_TEAM_WAIT_CANCEL_HWND" else 1

if __name__=="__main__":
    raise SystemExit(main())
