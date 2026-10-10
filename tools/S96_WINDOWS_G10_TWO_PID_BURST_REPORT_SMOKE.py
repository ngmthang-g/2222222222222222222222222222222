"""S96 G10 B3 two-round Party diagnostic on TWO REAL TEST-OWNED Win32 PIDs.

Parent actual Tk HWND + child actual Tk subprocess HWND, two different
physical PIDs. All RoleID and TeamID readings + permission are TEST-ONLY
injected callbacks. This NEVER reads game memory, sends invites or runs the
original EXE, and is NOT legitimate signed Info.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
OUT = ROOT/"artifacts"/"s96"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"s96_native_two_process_party_join_report.json"

CHILD_CODE = r"""
import ctypes
import os
import tkinter as tk
root=tk.Tk()
root.title("S96 TEST OWNED CHILD NOT GAME")
root.geometry("255x180+700+90")
tk.Label(root,text="S96 TEST CHILD, NO GAME").pack()
root.update_idletasks()
root.update()
ancestor=ctypes.windll.user32.GetAncestor
ancestor.argtypes=[ctypes.c_void_p,ctypes.c_uint]
ancestor.restype=ctypes.c_void_p
hwnd=int(ancestor(int(root.winfo_id()),2))
print(str(hwnd)+","+str(os.getpid()),flush=True)
root.after(25000,root.destroy)
root.mainloop()
"""


def main():
    info={"task":"S96","status":"NOT_RUN",
          "windows":"TWO_REAL_WINDOWS_TEST_OWNED_PROCESSES",
          "game_process":"NEVER_USED",
          "roleid_teamid":"EXTERNAL_TEST_CALLBACK_NOT_GAME",
          "Info":"NOT_SIGNED",
          "invites_sent":0}
    root=None
    child=None
    try:
        if os.name!="nt":raise RuntimeError("WINDOWS_REQUIRED")
        import ctypes
        import tkinter as tk
        from start_windows import NativeWin32Backend, GameWindow
        from start_polling import WindowSnapshot
        from party_team_identity import PartyTeamIdentityPreflight
        from party_team_wait import PartyTeamReadOnlyWait
        from party_join_report import PartyJoinTwoRoundDiagnostic

        root=tk.Tk()
        root.title("S96 TEST OWNED LEADER NOT GAME")
        root.geometry("265x175+180+95")
        tk.Label(root,text="S96 TEST LEADER, NO GAME").pack()
        root.update_idletasks()
        root.update()
        get_ancestor=ctypes.windll.user32.GetAncestor
        get_ancestor.argtypes=[ctypes.c_void_p,ctypes.c_uint]
        get_ancestor.restype=ctypes.c_void_p
        hwnd_a=int(get_ancestor(int(root.winfo_id()),2))
        pid_a=os.getpid()

        child=subprocess.Popen(
            [sys.executable,"-u","-c",CHILD_CODE],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL, text=True)
        stdout_lines=[]
        def read_child():
            stdout_lines.append(child.stdout.readline())
        reader=threading.Thread(target=read_child,daemon=True)
        reader.start()
        reader.join(timeout=9)
        if reader.is_alive():
            raise RuntimeError("CHILD_TEST_TK_HWND_TIMEOUT")
        assert stdout_lines and "," in stdout_lines[0],stdout_lines
        hwnd_b,pid_b=map(int,stdout_lines[0].strip().split(","))
        assert pid_a!=pid_b and hwnd_a!=hwnd_b
        backend=NativeWin32Backend()
        assert backend.is_window(hwnd_a) and backend.process_id(hwnd_a)==pid_a
        assert backend.is_window(hwnd_b) and backend.process_id(hwnd_b)==pid_b
        info["two_distinct_actual_hwnd_pid_verified"]=True

        class StartCache:
            def __init__(self):
                self.snapshot=WindowSnapshot(1,(
                    GameWindow(hwnd_a,pid_a,"TITLE NOT NAME","TEST_TK","python.exe"),
                    GameWindow(hwnd_b,pid_b,"TITLE NOT NAME","TEST_TK","python.exe")
                ),True)
            def read_snapshot(self):return self.snapshot
        cache=StartCache()
        read_counts=[0]
        game_team={hwnd_a:177,hwnd_b:0}
        def role_records():
            return [(pid_a,33,"S96 Leader",10),
                    (pid_b,44,"S96 Member",11)]
        def team_reader(hwnd):
            if hwnd==hwnd_b:
                read_counts[0]+=1
            return game_team[hwnd]
        def diag(team_fn=team_reader,permission=lambda:True):
            pre=PartyTeamIdentityPreflight(
                start_producer=cache,backend=backend,
                read_own_ids=role_records,read_team_id=team_fn,
                allowed=permission)
            return PartyJoinTwoRoundDiagnostic(PartyTeamReadOnlyWait(pre))
        args=dict(leader_name="S96 Leader",timeout_seconds=0,poll_seconds=.01)
        names=("S96 Leader","S96 Member")

        # Original signed Info and live game readers are absent by default.
        unconnected=PartyJoinTwoRoundDiagnostic(PartyTeamReadOnlyWait(
            PartyTeamIdentityPreflight(start_producer=cache,backend=backend)))
        blocked=unconnected.inspect(names,**args)
        assert blocked.code=="BLOCKED_FIRST_OBSERVATION_BLOCKED_LIVE_IDENTITY_PROVIDER_UNAVAILABLE"
        assert blocked.invites_sent==0
        info["default_missing_live_source_blocks"]=True

        report=diag().inspect(names,**args)
        assert report.code=="DIAGNOSTIC_STILL_MISSING_AFTER_TWO_OBSERVATIONS_NO_GAME_ACTION",report
        assert len(report.rounds)==2
        assert report.rounds[0].missing_names==("S96 Member",)
        assert report.rounds[1].missing_names==("S96 Member",)
        assert report.potential_resend_names==("S96 Member",)
        assert report.invites_sent==0
        info["two_round_missing_member_no_packets"]=True

        # Test external change in team status exactly BETWEEN observations.
        reads=[0]
        def joins_second_round(hwnd):
            if hwnd==hwnd_b:
                reads[0]+=1
                return 0 if reads[0]==1 else 177
            return 177
        recovered=diag(team_fn=joins_second_round).inspect(names,**args)
        assert recovered.code=="DIAGNOSTIC_ALL_JOINED_SECOND_OBSERVATION_NO_GAME_ACTION",recovered
        assert recovered.rounds[0].missing_names==("S96 Member",)
        assert recovered.rounds[1].missing_names==()
        assert recovered.invites_sent==0
        info["joined_on_second_observation_without_invite"]=True

        # Two outside sentinel IDs cannot be considered a team.
        game_team[hwnd_a]=0
        game_team[hwnd_b]=0xFFFFFFFF
        not_a_team=diag().inspect(names,**args)
        assert "ALL_JOINED" not in not_a_team.code
        assert not_a_team.invites_sent==0
        info["out_of_team_sentinels_do_not_fake_join"]=True

        # Physically terminate the member process while the stale Start
        # cache still references its HANDLE/PID; reject before any command.
        child.terminate()
        child.wait(timeout=8)
        deadline=time.monotonic()+4
        while backend.is_window(hwnd_b) and time.monotonic()<deadline:
            root.update()
            time.sleep(.015)
        assert not backend.is_window(hwnd_b)
        stale=diag().inspect(names,**args)
        assert stale.code=="BLOCKED_FIRST_OBSERVATION_BLOCKED_STALE_NATIVE_HWND_PID",stale
        info["real_closed_member_process_blocks"]=True
        info["status"]="PASS_NATIVE_S96_G10_TWO_WIN32_PID_JOIN_READONLY_NO_RESEND"
    except Exception as exc:
        info["status"]="FAIL_NATIVE_S96"
        info["error_type"]=type(exc).__name__
        info["error_text"]=str(exc)[:500]
        info["traceback"]=traceback.format_exc(limit=18)
        print(info["traceback"])
    finally:
        if child is not None:
            try:
                if child.poll() is None:
                    child.terminate()
                child.wait(timeout=4)
            except Exception:
                try:child.kill()
                except Exception:pass
            try:
                if child.stdout:child.stdout.close()
                if child.stderr:child.stderr.close()
            except Exception:pass
        if root is not None:
            try:root.destroy()
            except Exception:pass
        REPORT.write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding="utf-8")
        for key,value in info.items():
            if key!="traceback":
                print("S96_"+key.upper()+"="+json.dumps(value,ensure_ascii=True))
    return 0 if info["status"]=="PASS_NATIVE_S96_G10_TWO_WIN32_PID_JOIN_READONLY_NO_RESEND" else 1

if __name__=="__main__":
    raise SystemExit(main())
