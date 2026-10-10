"""S102 native saved Party Combobox values versus test external live RoleName.

REAL Tk widgets and two real Windows HWNDs in two independent TEST-OWNED
Python PIDs. Source RoleName values are injected TEST ONLY, not actual game.
Never launches or accesses the game or sends any packet/click.
"""
from __future__ import annotations

import json,os,subprocess,sys,tempfile,threading,time,traceback
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s102"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"s102_two_pid_native_saved_vs_ready_combobox.json"
CHILD=r"""
import ctypes,os,tkinter as tk
root=tk.Tk()
root.title("S102 TEST CHILD NOT GAME")
root.geometry("230x125+720+90")
root.update_idletasks();root.update()
a=ctypes.windll.user32.GetAncestor
a.argtypes=[ctypes.c_void_p,ctypes.c_uint];a.restype=ctypes.c_void_p
print(str(int(a(int(root.winfo_id()),2)))+","+str(os.getpid()),flush=True)
root.after(25000,root.destroy)
root.mainloop()
"""

def main():
    details=dict(task="S102",status="NOT_RUN",
        owner="TWO_SEPARATE_TEST_OWNED_PYTHON_WINDOWS",
        external_role_data="SYNTHETIC_NEVER_GAME",
        original_game_access=False,actions_sent=0,signed_Info=False)
    root=None;child=None
    try:
        if os.name!="nt":raise RuntimeError("WINDOWS_REQUIRED")
        import ctypes,tkinter as tk
        from start_windows import NativeWin32Backend,GameWindow
        from start_polling import WindowSnapshot
        from party_group_config import PartyConfigStore,PartySettings,PartyGroup
        from party_ready_list import PartyReadyConfigEditor
        from party_rolename_source import PartyRoleNameExternalSource
        from party_ready_handoff import PartyExternalReadyHandoff
        from party_combo_provenance import PartySavedComboHandoff

        root=tk.Tk()
        root.title("S102 TEST PARENT NOT GAME")
        root.geometry("1040x820+50+50")
        root.update_idletasks();root.update()
        get=ctypes.windll.user32.GetAncestor
        get.argtypes=[ctypes.c_void_p,ctypes.c_uint]
        get.restype=ctypes.c_void_p
        ha=int(get(int(root.winfo_id()),2));pa=os.getpid()
        child=subprocess.Popen([sys.executable,"-u","-c",CHILD],
            stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,text=True)
        received=[]
        th=threading.Thread(target=lambda:received.append(child.stdout.readline()),daemon=True)
        th.start();th.join(timeout=9)
        if th.is_alive() or not received or "," not in received[0]:
            raise RuntimeError("TEST_CHILD_WINDOW_TIMEOUT")
        hb,pb=map(int,received[0].strip().split(","))
        backend=NativeWin32Backend()
        assert pa!=pb and ha!=hb
        assert backend.is_window(ha) and backend.process_id(ha)==pa
        assert backend.is_window(hb) and backend.process_id(hb)==pb
        details["real_native_two_pid_hwnds"]=True

        class Producer:
            def __init__(self):
                self.value=WindowSnapshot(1,(
                    GameWindow(ha,pa,"NOT NAME","TEST","python.exe"),
                    GameWindow(hb,pb,"NOT NAME","TEST","python.exe")),True)
            def read_snapshot(self):return self.value
        producer=Producer()
        names={ha:{"RoleName":"<b>Đội</b> Trưởng"},
               hb:{"RoleName":"Hòa✨"}}
        source=PartyRoleNameExternalSource(
            start_producer=producer,backend=backend,
            get_character_info=lambda hwnd:names[hwnd])
        hand=PartySavedComboHandoff(PartyExternalReadyHandoff(source))
        with tempfile.TemporaryDirectory(prefix="s102-party-config-") as d:
            store=PartyConfigStore(Path(d)/"Settings.ini")
            saved=PartySettings(groups=(
                PartyGroup(1,("Đội Trưởng","Offline")),
                PartyGroup(2,("Hòa✨",))))
            store.save(saved)
            editor=PartyReadyConfigEditor(root,store=store,
                start_producer=producer,read_role=source.read_role)
            editor.pack(fill="both",expand=True)
            editor._roster_reader.stop()
            root.update_idletasks();root.update()
            assert editor.state==saved

            batch=hand.handoff.collect(producer.value)
            observed=hand.deliver(batch,editor=editor)
            assert observed.code=="DIAGNOSTIC_S102_S91_SAVED_VS_TEST_READY_NO_GAME_ACTION",observed
            assert "Offline" in observed.retained_saved_names,observed
            one=tuple(editor.group_inputs[0][1]["values"])
            two=tuple(editor.group_inputs[1][0]["values"])
            assert "Offline" in one and "Offline" not in two,(one,two)
            assert "Đội Trưởng" not in two,(one,two)
            assert editor.group_inputs[0][1].get()=="Offline"
            assert store.load()==saved
            assert not observed.game_role_verified and not observed.action_authorized
            details["real_tk_combobox_saved_offline_preserved_separate_live"]=True

            # Actual second process terminates but Start cache stays frozen.
            batch=hand.handoff.collect(producer.value)
            child.terminate();child.wait(timeout=8)
            deadline=time.monotonic()+4
            while backend.is_window(hb) and time.monotonic()<deadline:
                root.update();time.sleep(.01)
            assert not backend.is_window(hb)
            stale=hand.deliver(batch,editor=editor)
            assert stale.code.startswith("BLOCKED_"),stale
            for cluster in editor.group_inputs:
                for combo in cluster:
                    values=tuple(combo["values"])
                    current=combo.get()
                    assert set(values).issubset({"",current}),values
            assert editor.group_inputs[0][1].get()=="Offline"
            assert "Offline" in editor.group_inputs[0][1]["values"]
            assert editor.ready_list.names==()
            assert store.load()==saved
            details["dead_child_hwnd_removes_live_options_keeps_saved_ini"]=True

            editor.shutdown();editor.destroy()
        details["status"]="PASS_NATIVE_S102_G02_COMBO_SAVED_OFFLINE_TWO_TEST_PIDS_NO_GAME"
    except Exception as exc:
        details["status"]="FAIL_NATIVE_S102"
        details["error"]=str(exc)[:420]
        details["traceback"]=traceback.format_exc(limit=14)
        print(details["traceback"])
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
        REPORT.write_text(json.dumps(details,ensure_ascii=False,indent=2),encoding="utf-8")
        for k,v in details.items():
            if k!="traceback":
                print("S102_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if details["status"]=="PASS_NATIVE_S102_G02_COMBO_SAVED_OFFLINE_TWO_TEST_PIDS_NO_GAME" else 1

if __name__=="__main__":
    raise SystemExit(main())
