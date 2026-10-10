"""S99 G10 presentation native smoke on TWO actual TEST-owned Windows PIDs.
No game memory or game process, signed Info unavailable, no packet or invite.
"""
from __future__ import annotations
import json, os, subprocess, sys, threading, time, traceback
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s99"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"s99_two_pid_snapshot_presentation.json"
CHILD=r"""
import ctypes, os, tkinter as tk
root=tk.Tk()
root.title('S99 CHILD TEST OWNED NOT GAME')
root.geometry('240x110+730+70')
root.update_idletasks();root.update()
u=ctypes.windll.user32.GetAncestor
u.argtypes=[ctypes.c_void_p,ctypes.c_uint];u.restype=ctypes.c_void_p
print(str(int(u(int(root.winfo_id()),2)))+','+str(os.getpid()),flush=True)
root.after(25000,root.destroy)
root.mainloop()
"""

def main():
    report=dict(task="S99",status="NOT_RUN",invites_sent=0,
                real_game_access=False,signed_Info_issuer=False,
                owner="TWO_TEST_PYTHON_PROCESSES")
    root=None;child=None
    try:
        if os.name!="nt":raise RuntimeError("WINDOWS_REQUIRED")
        import ctypes
        import tkinter as tk
        from start_windows import NativeWin32Backend, GameWindow
        from start_polling import WindowSnapshot
        from party_team_identity import PartyTeamIdentityPreflight
        from party_team_wait import PartyTeamReadOnlyWait
        from party_join_report import PartyJoinTwoRoundDiagnostic
        from party_member_snapshot import PartyJoinDetailedDiagnostic
        from party_member_epoch import PartyJoinReadEpochDiagnostic
        from party_snapshot_presentation import present_party_team_snapshot

        root=tk.Tk()
        root.title("S99 TEST OWNED LEADER NOT GAME")
        root.geometry("260x120+110+65")
        root.update_idletasks();root.update()
        u=ctypes.windll.user32.GetAncestor
        u.argtypes=[ctypes.c_void_p,ctypes.c_uint];u.restype=ctypes.c_void_p
        hwnd_a=int(u(int(root.winfo_id()),2));pid_a=os.getpid()
        child=subprocess.Popen(
            [sys.executable,"-u","-c",CHILD],stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        lines=[]
        reader=threading.Thread(target=lambda:lines.append(child.stdout.readline()),daemon=True)
        reader.start();reader.join(timeout=9)
        if reader.is_alive() or not lines or "," not in lines[0]:
            raise RuntimeError("CHILD_TEST_WINDOW_TIMEOUT")
        hwnd_b,pid_b=map(int,lines[0].strip().split(","))
        backend=NativeWin32Backend()
        assert hwnd_a!=hwnd_b and pid_a!=pid_b
        assert backend.is_window(hwnd_a) and backend.process_id(hwnd_a)==pid_a
        assert backend.is_window(hwnd_b) and backend.process_id(hwnd_b)==pid_b
        report["two_actual_win32_hwnd_pids"]=True
        class Producer:
            def __init__(self):
                self.value=WindowSnapshot(1,(
                    GameWindow(hwnd_a,pid_a,"NOT A ROLE","TEST","python.exe"),
                    GameWindow(hwnd_b,pid_b,"NOT A ROLE","TEST","python.exe")),True)
            def read_snapshot(self):return self.value
        producer=Producer()
        team={hwnd_a:144,hwnd_b:0}
        names=("S99 LãnhĐạo","S99 Hòa")
        records=[(pid_a,11,names[0],10),(pid_b,12,names[1],10)]
        def make(read_team=None,allowed=lambda:True):
            pre=PartyTeamIdentityPreflight(
                start_producer=producer,backend=backend,
                read_own_ids=lambda:tuple(records),
                read_team_id=read_team or (lambda hwnd:team[hwnd]),
                allowed=allowed)
            return PartyJoinReadEpochDiagnostic(
                PartyJoinDetailedDiagnostic(
                    PartyJoinTwoRoundDiagnostic(PartyTeamReadOnlyWait(pre))))
        args=dict(leader_name=names[0],timeout_seconds=0,poll_seconds=.01)
        observed=present_party_team_snapshot(make().inspect(names,**args))
        assert [r.original_style_field for r in observed.rows] == [
            "S99 LãnhĐạo=144","S99 Hòa=0"],observed
        assert observed.rows[1].diagnostic_state=="KNOWN_OUTSIDE"
        assert observed.s96_round_missing_names==((names[1],),(names[1],))
        assert observed.sequential_non_atomic and not observed.action_authorized
        report["known_outside_display_and_round_provenance"]=True

        team[hwnd_b]=None
        unreadable=present_party_team_snapshot(make().inspect(names,**args))
        assert unreadable.rows[1].original_style_field=="S99 Hòa=?",unreadable
        assert unreadable.rows[1].diagnostic_state=="UNREADABLE_TEAMID"
        report["unreadable_is_question_not_outside"]=True

        team[hwnd_b]=144
        joined=present_party_team_snapshot(make().inspect(names,**args))
        assert joined.rows[1].original_style_field=="S99 Hòa=144",joined
        assert len(joined.s96_round_codes)==1
        assert not joined.action_authorized and not joined.game_parity_verified
        report["joined_observed_not_action_authorized"]=True

        records.pop()
        offline=present_party_team_snapshot(make().inspect(names,**args))
        assert offline.rows[1].original_style_field=="S99 Hòa=?",offline
        assert offline.rows[1].diagnostic_state=="OFFLINE_NAME"
        report["offline_distinguished"]=True
        records.append((pid_b,12,names[1],10))

        unsigned=present_party_team_snapshot(make(allowed=lambda:False).inspect(names,**args))
        assert unsigned.code.startswith("BLOCKED_PRESENTATION_") and not unsigned.rows,unsigned
        report["missing_signed_gate_blocks"]=True

        child.terminate();child.wait(timeout=8)
        until=time.monotonic()+4
        while backend.is_window(hwnd_b) and time.monotonic()<until:
            root.update();time.sleep(.01)
        assert not backend.is_window(hwnd_b)
        stale=present_party_team_snapshot(make().inspect(names,**args))
        assert stale.code.startswith("BLOCKED_PRESENTATION_") and not stale.rows,stale
        report["physically_destroyed_HWND_blocks"]=True
        report["status"]="PASS_NATIVE_S99_G10_TWO_WIN32_PID_READONLY_PRESENTATION"
    except Exception as ex:
        report["status"]="FAIL_NATIVE_S99"
        report["error"]=str(ex)[:350]
        report["traceback"]=traceback.format_exc(limit=12)
        print(report["traceback"])
    finally:
        if child is not None:
            try:
                if child.poll() is None:child.terminate()
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
        REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
        for k,v in report.items():
            if k!="traceback":print("S99_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if report["status"]=="PASS_NATIVE_S99_G10_TWO_WIN32_PID_READONLY_PRESENTATION" else 1

if __name__=="__main__":
    raise SystemExit(main())
