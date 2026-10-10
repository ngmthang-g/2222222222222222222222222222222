"""S94 native Windows TEST-OWNED real HWND/PID G03/G10 preflight.

Real Win32/Tk lifetime and own-PID evidence, externally supplied TEST-only
own-ID/team status readers. Does NOT read the game, issue a permission token,
send a packet or imply S92/G10 real team creation works.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import sys
import tempfile
import traceback

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s94"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"native_team_identity_test_owned_windows.json"


def main():
    report={
        "task":"S94","status":"NOT_RUN",
        "windows":"REAL_WIN32_TK_TEST_OWNED_HWND_PID",
        "records":"INJECTED_TEST_ONLY_NOT_GAME_MEMORY",
        "Info":"NO_ACTUAL_SIGNED_INFO",
        "protocol":"NO_GAME_COMMAND_SENT",
    }
    root=None
    try:
        if os.name!="nt":raise RuntimeError("NATIVE_WINDOWS_REQUIRED")
        import tkinter as tk
        from start_polling import WindowSnapshot
        from start_windows import GameWindow, NativeWin32Backend
        from dwm_preview import NativeDwmBackend
        from party_team_identity import PartyTeamIdentityPreflight

        root=tk.Tk()
        root.title("S94 TEST owned root no game")
        root.geometry("300x220+60+60")
        windows=[]
        for i in range(2):
            w=tk.Toplevel(root)
            w.title(f"S94 TEST WINDOW #{i}, NOT GAME ROLE")
            w.geometry(f"235x170+{450+i*250}+70")
            tk.Label(w,text="TEST HWND ONLY").pack()
            windows.append(w)
        root.update_idletasks()
        root.update()
        dwm=NativeDwmBackend()
        native=NativeWin32Backend()
        handles=[int(dwm._ancestor(int(w.winfo_id()),2)) for w in windows]
        pid=os.getpid()
        assert len(set(handles))==2
        assert all(dwm.source_matches(h,pid) for h in handles)
        assert all(native.is_window(h) and native.process_id(h)==pid for h in handles)
        report["actual_win32_hwnd_pid_verified"]=True

        class Producer:
            def __init__(self):
                self.value=WindowSnapshot(
                    1,tuple(GameWindow(h,pid,"TITLE NOT CHARACTER",
                                       "TEST_TK","python.exe") for h in handles),True)
            def read_snapshot(self):
                return self.value
        producer=Producer()
        team={handles[0]:0,handles[1]:0xFFFFFFFF}
        roles=[
            # Both HWNDs have the same owning process PID in this test-owned
            # Tk process; original S09 game windows are per PID. To exercise
            # two *distinct* actual native PIDs needs a second process, so
            # here select only ONE real HWND in one cached snapshot.
            (pid,0,"Nhân vật thử S94",20)
        ]
        producer.value=WindowSnapshot(2,producer.value.windows[:1],True)
        def names():return roles
        def read_team(h):return team[h]
        def pre(**kw):
            kwargs=dict(start_producer=producer,backend=native,
                        read_own_ids=names,read_team_id=read_team,allowed=lambda:True)
            kwargs.update(kw)
            return PartyTeamIdentityPreflight(**kwargs)
        # Without explicit game reader and entitlement, fail closed.
        no_reader=PartyTeamIdentityPreflight(
            start_producer=producer,backend=native).inspect(("Nhân vật thử S94",))
        assert no_reader.code=="LIVE_IDENTITY_PROVIDER_UNAVAILABLE"
        no_info=pre(allowed=None).inspect(("Nhân vật thử S94",))
        assert no_info.code=="SIGNED_INFO_GATE_UNAVAILABLE"
        report["missing_game_reader_and_info_blocked"]=True

        ok=pre().inspect(("Nhân vật thử S94",))
        assert ok.code=="DIAGNOSTIC_OBSERVED_NO_GAME_ACTION",ok
        assert len(ok.targets)==1
        assert ok.targets[0].hwnd==handles[0] and ok.targets[0].pid==pid
        assert ok.targets[0].role_id==0  # DO NOT invent RoleID 0 sentinel
        assert ok.targets[0].team_state=="KNOWN_OUTSIDE_TEAM"
        report["test_owned_live_record_and_roleid_zero_not_invented_invalid"]=True
        # Exact original TeamID sentinel 0xFFFFFFFF for the SAME HWND.
        team[handles[0]]=0xFFFFFFFF
        second=pre().inspect(("Nhân vật thử S94",))
        assert second.targets[0].team_state=="KNOWN_OUTSIDE_TEAM"
        team[handles[0]]=None
        unknown=pre().inspect(("Nhân vật thử S94",))
        assert unknown.code=="TEAMID_UNKNOWN_NOT_OUTSIDE"
        assert not unknown.targets
        report["none_teamid_never_outside_success"]=True
        team[handles[0]]=0

        # Actual HWND destruction, while cached S09 identity is still older:
        # even the external test role record MUST NOT become an action target.
        windows[0].destroy()
        root.update()
        assert not native.is_window(handles[0])
        stale=pre().inspect(("Nhân vật thử S94",))
        assert stale.code=="STALE_NATIVE_HWND_PID",stale.code
        report["destroyed_real_window_fails_closed"]=True

        # Native second HWND is still real and is a separate generation:
        # no inferred RoleName from its title, fresh immutable S09 revision.
        assert native.is_window(handles[1]) and native.process_id(handles[1])==pid
        producer.value=WindowSnapshot(3,(
            GameWindow(handles[1],pid,"DIFFERENT TEST TITLE",
                       "TEST_TK","python.exe"),),True)
        team[handles[1]]=314
        result=pre().inspect(("Nhân vật thử S94",))
        assert result.code=="DIAGNOSTIC_OBSERVED_NO_GAME_ACTION"
        assert len(result.targets)==1 and result.targets[0].hwnd==handles[1]
        assert result.targets[0].team_state=="KNOWN_IN_TEAM"
        report["new_real_hwnd_generation_requires_fresh_start_cache"]=True
        report["status"]="PASS_NATIVE_S94_G10_READONLY_TEST_HWND_PID_SENTINELS"
    except Exception as exc:
        report["status"]="FAIL_NATIVE_S94"
        report["error_type"]=type(exc).__name__
        report["error_text"]=str(exc)[:500]
        report["traceback"]=traceback.format_exc(limit=16)
        print(report["traceback"])
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
        for k,v in report.items():
            if k!="traceback":print("S94_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if report["status"]=="PASS_NATIVE_S94_G10_READONLY_TEST_HWND_PID_SENTINELS" else 1

if __name__=="__main__":
    raise SystemExit(main())
