"""S98 native two-PID read-epoch check; entirely TEST OWNED, NEVER GAME."""
from __future__ import annotations
import json,os,subprocess,sys,threading,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s98"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"s98_native_epoch.json"
CHILD=r"""
import ctypes,os,tkinter as tk
root=tk.Tk();root.title('S98 CHILD TEST NOT GAME')
root.geometry('250x110+720+70');root.update_idletasks();root.update()
u=ctypes.windll.user32.GetAncestor
u.argtypes=[ctypes.c_void_p,ctypes.c_uint];u.restype=ctypes.c_void_p
print(str(int(u(int(root.winfo_id()),2)))+','+str(os.getpid()),flush=True)
root.after(25000,root.destroy);root.mainloop()
"""

def main():
    info={"task":"S98","status":"NOT_RUN","invites_sent":0,
          "two_processes":"REAL_TEST_PYTHON_HWND_PIDS",
          "game_process":"NEVER_USED","Info":"NOT_SIGNED"}
    root=None;child=None
    try:
        if os.name!="nt":raise RuntimeError("WINDOWS_REQUIRED")
        import ctypes,tkinter as tk
        from start_windows import NativeWin32Backend,GameWindow
        from start_polling import WindowSnapshot
        from party_team_identity import PartyTeamIdentityPreflight
        from party_team_wait import PartyTeamReadOnlyWait
        from party_join_report import PartyJoinTwoRoundDiagnostic
        from party_member_snapshot import PartyJoinDetailedDiagnostic
        from party_member_epoch import PartyJoinReadEpochDiagnostic

        root=tk.Tk();root.title("S98 PARENT TEST NOT GAME")
        root.geometry("250x110+100+70");root.update_idletasks();root.update()
        u=ctypes.windll.user32.GetAncestor
        u.argtypes=[ctypes.c_void_p,ctypes.c_uint];u.restype=ctypes.c_void_p
        hwnd_a=int(u(int(root.winfo_id()),2));pid_a=os.getpid()
        child=subprocess.Popen([sys.executable,"-u","-c",CHILD],
            stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,text=True)
        lines=[]
        t=threading.Thread(target=lambda:lines.append(child.stdout.readline()),daemon=True)
        t.start();t.join(timeout=9)
        if t.is_alive() or not lines or "," not in lines[0]:raise RuntimeError("CHILD_WINDOW_TIMEOUT")
        hwnd_b,pid_b=map(int,lines[0].strip().split(","))
        backend=NativeWin32Backend()
        assert hwnd_a!=hwnd_b and pid_a!=pid_b
        assert backend.is_window(hwnd_a) and backend.process_id(hwnd_a)==pid_a
        assert backend.is_window(hwnd_b) and backend.process_id(hwnd_b)==pid_b
        info["two_distinct_physical_pids"]=True
        class Cache:
            def __init__(self):
                self.value=WindowSnapshot(1,(
                    GameWindow(hwnd_a,pid_a,"NOT ROLE","TEST","python.exe"),
                    GameWindow(hwnd_b,pid_b,"NOT ROLE","TEST","python.exe")),True)
            def read_snapshot(self):return self.value
        cache=Cache()
        teams={hwnd_a:852,hwnd_b:0}
        names=("Leader S98","Member S98")
        records=((pid_a,11,names[0],10),(pid_b,12,names[1],10))
        def make(team_reader,permission=lambda:True):
            p=PartyTeamIdentityPreflight(start_producer=cache,
                backend=backend,read_own_ids=lambda:records,
                read_team_id=team_reader,allowed=permission)
            return PartyJoinReadEpochDiagnostic(
                PartyJoinDetailedDiagnostic(
                    PartyJoinTwoRoundDiagnostic(PartyTeamReadOnlyWait(p))))
        kwargs=dict(leader_name=names[0],timeout_seconds=0,poll_seconds=.01)
        r=make(lambda hwnd:teams[hwnd]).inspect(names,**kwargs)
        assert r.code=="DIAGNOSTIC_SEQUENTIAL_STABLE_SAME_GENERATION_NO_GAME_ACTION",r
        assert r.compared_native_windows==2 and r.start_revision==r.end_revision==1
        assert len(r.detailed.base.rounds)==2
        assert not r.atomic and r.invites_sent==0
        info["stable_snapshot_not_atomic"]=True
        reads=[0]
        def change(hwnd):
            if hwnd==hwnd_b:
                reads[0]+=1
                return 0 if reads[0]<=3 else 852
            return 852
        changed=make(change).inspect(names,**kwargs)
        assert changed.changes[1].class_code=="OBSERVED_TEAM_ID_CHANGED",changed
        assert changed.changes[1].from_team_id==0
        assert changed.changes[1].to_team_id==852
        assert changed.start_revision==changed.end_revision
        info["TeamID_changed_same_verified_HWND_PID"]=True
        gate=make(lambda hwnd:teams[hwnd],lambda:False).inspect(names,**kwargs)
        assert gate.code.startswith("BLOCKED_") and not gate.changes,gate
        info["signed_gate_not_faked"]=True
        child.terminate();child.wait(timeout=8)
        until=time.monotonic()+4
        while backend.is_window(hwnd_b) and time.monotonic()<until:
            root.update();time.sleep(.01)
        assert not backend.is_window(hwnd_b)
        gone=make(lambda hwnd:teams[hwnd]).inspect(names,**kwargs)
        assert gone.code.startswith("BLOCKED_") and not gone.changes,gone
        info["physically_destroyed_window_blocks"]=True
        info["status"]="PASS_NATIVE_S98_G10_TWO_PID_READ_EPOCH_NO_GAME"
    except Exception as ex:
        info["status"]="FAIL_NATIVE_S98"
        info["error"]=str(ex)[:350]
        info["traceback"]=traceback.format_exc(limit=12)
        print(info["traceback"])
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
        REPORT.write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding="utf-8")
        for k,v in info.items():
            if k!="traceback":print("S98_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if info["status"]=="PASS_NATIVE_S98_G10_TWO_PID_READ_EPOCH_NO_GAME" else 1

if __name__=="__main__":
    raise SystemExit(main())
