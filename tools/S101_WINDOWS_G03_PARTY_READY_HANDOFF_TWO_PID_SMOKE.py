"""S101 native G03 test-only S100->S90->S91 READY Handoff, 2 PIDs.

Two genuine Windows Tk HWNDs owned by separate Python test processes.
Synthetic external names. No game memory, signed Info, packet or actions.
"""
from __future__ import annotations
import json,os,subprocess,sys,threading,time,traceback
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s101";OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"s101_two_native_test_pid_party_ready_handoff.json"
CHILD=r"""
import ctypes,os,tkinter as tk
root=tk.Tk();root.title("S101 CHILD TEST WINDOW NOT GAME")
root.geometry("230x110+720+80")
root.update_idletasks();root.update()
a=ctypes.windll.user32.GetAncestor
a.argtypes=[ctypes.c_void_p,ctypes.c_uint];a.restype=ctypes.c_void_p
print(str(int(a(int(root.winfo_id()),2)))+","+str(os.getpid()),flush=True)
root.after(25000,root.destroy);root.mainloop()
"""

def main():
    log={"task":"S101","status":"NOT_RUN",
         "source":"TWO_DISTINCT_TEST_OWNED_WIN32_PIDS_EXTERNAL_SYNTHETIC_NAMES",
         "original_game_used":False,"signed_Info":False,"actions_sent":0}
    root=None;child=None
    try:
        if os.name!="nt":raise RuntimeError("WINDOWS_REQUIRED")
        import ctypes,tkinter as tk
        from start_windows import NativeWin32Backend,GameWindow
        from start_polling import WindowSnapshot
        from party_rolename_source import PartyRoleNameExternalSource
        from party_ready_handoff import PartyExternalReadyHandoff
        from party_roster import PartyRoster
        from party_ready_list import PartyReadyList

        root=tk.Tk();root.title("S101 PARENT TEST NOT GAME")
        root.geometry("380x230+100+50");root.update_idletasks();root.update()
        a=ctypes.windll.user32.GetAncestor
        a.argtypes=[ctypes.c_void_p,ctypes.c_uint];a.restype=ctypes.c_void_p
        hwnd_a=int(a(int(root.winfo_id()),2));pid_a=os.getpid()
        child=subprocess.Popen([sys.executable,"-u","-c",CHILD],
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,text=True)
        lines=[]
        t=threading.Thread(target=lambda:lines.append(child.stdout.readline()),daemon=True)
        t.start();t.join(timeout=9)
        if t.is_alive() or not lines or "," not in lines[0]:
            raise RuntimeError("TEST_CHILD_NATIVE_TIMEOUT")
        hwnd_b,pid_b=map(int,lines[0].strip().split(","))
        backend=NativeWin32Backend()
        assert hwnd_a!=hwnd_b and pid_a!=pid_b
        assert backend.is_window(hwnd_a) and backend.process_id(hwnd_a)==pid_a
        assert backend.is_window(hwnd_b) and backend.process_id(hwnd_b)==pid_b
        log["two_real_windows_separate_process_ids"]=True

        class Producer:
            def __init__(self):
                self.value=WindowSnapshot(revision=1,windows=(
                    GameWindow(hwnd_a,pid_a,"NOT ACCOUNT NAME","TEST","python.exe"),
                    GameWindow(hwnd_b,pid_b,"NOT ACCOUNT NAME","TEST","python.exe")),valid=True)
            def read_snapshot(self):return self.value
        producer=Producer()
        names={hwnd_a:{"RoleName":"<b>Đội</b> Trưởng"},
               hwnd_b:{"RoleName":"Hòa✨"}}
        src=PartyRoleNameExternalSource(
            start_producer=producer,backend=backend,
            get_character_info=lambda h:names[h])
        hand=PartyExternalReadyHandoff(src)
        roster=PartyRoster();view=PartyReadyList(root)
        view.pack(fill="x")
        batch=hand.collect(producer.read_snapshot())
        assert batch.code=="EXTERNAL_ROLE_ROSTER_PREPARED_NO_GAME",batch
        assert view.names==()
        out=hand.deliver(batch,roster=roster,ready_list=view)
        assert out.displayed_ready_names==("Đội Trưởng","Hòa✨"),out
        assert out.action_authorized is False and out.game_role_verified is False
        assert len(view.labels)==2
        assert (int(view.labels[0].grid_info()["row"]),
                int(view.labels[1].grid_info()["column"]))==(0,1)
        log["s100_to_existing_s90_s91_real_tk_ready_names"]=True

        # Window death before Start cache detects it cannot leave stale label.
        old=hand.collect(producer.read_snapshot())
        child.terminate();child.wait(timeout=8)
        deadline=time.monotonic()+4
        while backend.is_window(hwnd_b) and time.monotonic()<deadline:
            root.update();time.sleep(.01)
        assert not backend.is_window(hwnd_b)
        gone=hand.deliver(old,roster=roster,ready_list=view)
        assert gone.code.startswith("BLOCKED_PRE_DRAW_STALE_NATIVE_HWND_PID"),gone
        assert view.names==() and not view.labels
        assert roster.ready_names()==()
        log["actual_child_process_death_clears_stale_ready_rows"]=True

        # Changing cache generation blocks a previously prepared name.
        producer.value=WindowSnapshot(2,producer.value.windows,True)
        stale=hand.deliver(old,roster=roster,ready_list=view)
        assert stale.code.startswith("BLOCKED_") and view.names==()
        log["cache_epoch_rejects_stale_worker_names"]=True

        # Original game source missing: no fabricated fallback or RoleID.
        absent=PartyExternalReadyHandoff(PartyRoleNameExternalSource(
            start_producer=producer,backend=backend,get_character_info=None))
        empty=absent.collect(producer.value)
        assert empty.code.startswith("BLOCKED_") or not any(
            member.role_name for member in empty.roster_result.members)
        log["no_original_reader_has_no_fabricated_role"]=True
        log["status"]="PASS_NATIVE_S101_G03_READY_HANDOFF_2_WIN32_TEST_PIDS_NO_GAME"
    except Exception as ex:
        log["status"]="FAIL_NATIVE_S101"
        log["error"]=str(ex)[:500]
        log["traceback"]=traceback.format_exc(limit=15)
        print(log["traceback"])
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
        REPORT.write_text(json.dumps(log,indent=2,ensure_ascii=False),encoding="utf-8")
        for key,val in log.items():
            if key!="traceback":print("S101_"+key.upper()+"="+json.dumps(val,ensure_ascii=True))
    return 0 if log["status"]=="PASS_NATIVE_S101_G03_READY_HANDOFF_2_WIN32_TEST_PIDS_NO_GAME" else 1

if __name__=="__main__":raise SystemExit(main())
