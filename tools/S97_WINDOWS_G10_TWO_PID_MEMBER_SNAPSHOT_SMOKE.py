"""S97 Windows native G10 per-member evidence: TWO TEST-OWNED processes.
No game processes, no signed Info, no invites, zero packets.
"""
from __future__ import annotations
import json,os,subprocess,sys,threading,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s97"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"s97_native_two_pid_member_snapshot.json"

CHILD=r"""
import ctypes,os,tkinter as tk
root=tk.Tk()
root.title('S97 CHILD TEST NO GAME')
root.geometry('220x120+800+80')
root.update_idletasks();root.update()
u=ctypes.windll.user32.GetAncestor
u.argtypes=[ctypes.c_void_p,ctypes.c_uint]
u.restype=ctypes.c_void_p
print(str(int(u(int(root.winfo_id()),2)))+','+str(os.getpid()),flush=True)
root.after(25000,root.destroy)
root.mainloop()
"""

def main():
    info=dict(task="S97",status="NOT_RUN",invites_sent=0,
              windows="TWO_REAL_TEST_OWNED_WIN32_PIDS",
              source="INJECTED_TEST_CALLBACKS_NOT_GAME",
              signed_info="NOT_AVAILABLE")
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
        root=tk.Tk()
        root.title("S97 PARENT TEST NO GAME")
        root.geometry("240x120+120+70")
        root.update_idletasks();root.update()
        u=ctypes.windll.user32.GetAncestor
        u.argtypes=[ctypes.c_void_p,ctypes.c_uint];u.restype=ctypes.c_void_p
        hwnd_a=int(u(int(root.winfo_id()),2));pid_a=os.getpid()
        child=subprocess.Popen([sys.executable,"-u","-c",CHILD],
            stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,text=True)
        lines=[]
        reader=threading.Thread(target=lambda:lines.append(child.stdout.readline()),daemon=True)
        reader.start();reader.join(9)
        if reader.is_alive() or not lines or "," not in lines[0]:
            raise RuntimeError("CHILD_TEST_HWND_TIMEOUT")
        hwnd_b,pid_b=map(int,lines[0].strip().split(","))
        backend=NativeWin32Backend()
        assert hwnd_a!=hwnd_b and pid_a!=pid_b
        assert backend.is_window(hwnd_a) and backend.process_id(hwnd_a)==pid_a
        assert backend.is_window(hwnd_b) and backend.process_id(hwnd_b)==pid_b
        info["two_physical_pid_verified"]=True
        class Producer:
            def __init__(self):
                self.value=WindowSnapshot(1,(
                    GameWindow(hwnd_a,pid_a,"NOT A ROLE","S97_TEST","python.exe"),
                    GameWindow(hwnd_b,pid_b,"NOT A ROLE","S97_TEST","python.exe")),True)
            def read_snapshot(self):return self.value
        producer=Producer()
        member_team={hwnd_a:444,hwnd_b:0}
        records=[(pid_a,7,"S97 Lead",10),(pid_b,8,"S97 Other",10)]
        def make(permission=lambda:True):
            pre=PartyTeamIdentityPreflight(
                start_producer=producer,backend=backend,
                read_own_ids=lambda:tuple(records),
                read_team_id=lambda hwnd:member_team[hwnd],
                allowed=permission)
            return PartyJoinDetailedDiagnostic(
                PartyJoinTwoRoundDiagnostic(PartyTeamReadOnlyWait(pre)))
        names=("S97 Lead","S97 Other")
        args=dict(leader_name=names[0],timeout_seconds=0,poll_seconds=.01)
        d=make()
        r=d.inspect(names,**args)
        assert len(r.base.rounds)==2,r
        assert r.post_snapshot.members[0].state=="LEADER_REAL_TEAM",r
        assert r.post_snapshot.members[1].state=="KNOWN_OUTSIDE",r
        assert r.invites_sent==r.base.invites_sent==r.post_snapshot.invites_sent==0
        info["known_outside_vs_joined"]=True
        member_team[hwnd_b]=544
        r=make().inspect(names,**args)
        assert r.post_snapshot.members[1].state=="DIFFERENT_REAL_TEAM",r
        info["different_real_team"]=True
        member_team[hwnd_b]=None
        r=make().inspect(names,**args)
        assert r.post_snapshot.members[1].state=="UNREADABLE_TEAMID",r
        info["unreadable_not_outside"]=True
        member_team[hwnd_b]=444
        r=make().inspect(names,**args)
        assert len(r.base.rounds)==1 and r.post_snapshot.members[1].state=="JOINED_LEADER_TEAM",r
        info["same_real_team"]=True
        records.pop()
        r=make().inspect(names,**args)
        assert r.post_snapshot.members[1].state=="OFFLINE_NAME",r
        info["offline_name"]=True
        records.append((pid_b,8,"S97 Other",10))
        blocked=make(permission=lambda:False).inspect(names,**args)
        assert blocked.post_snapshot is None and blocked.base.code.startswith("BLOCKED_"),blocked
        info["unsigned_gate_blocks"]=True
        child.terminate();child.wait(timeout=8)
        until=time.monotonic()+4
        while backend.is_window(hwnd_b) and time.monotonic()<until:
            root.update();time.sleep(.01)
        assert not backend.is_window(hwnd_b)
        stale=make().inspect(names,**args)
        assert stale.post_snapshot is None and "STALE_NATIVE_HWND_PID" in stale.base.code,stale
        info["terminated_native_window_blocked"]=True
        info["status"]="PASS_NATIVE_S97_TWO_WIN32_PID_G10_PER_MEMBER_READONLY"
    except Exception as exc:
        info["status"]="FAIL_NATIVE_S97"
        info["error"]=str(exc)[:350]
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
            if k!="traceback":print("S97_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if info["status"]=="PASS_NATIVE_S97_TWO_WIN32_PID_G10_PER_MEMBER_READONLY" else 1

if __name__=="__main__":
    raise SystemExit(main())
