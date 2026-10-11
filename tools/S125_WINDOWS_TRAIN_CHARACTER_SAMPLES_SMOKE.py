"""S125 real Windows HWND/PID + Tk-main-thread H12 sample-consumer smoke.

Character reader is a TEST-ONLY deterministic stand-in; NO original game
memory or signed Info provider exists. The actual window tested belongs to
this Tk process and MUST NOT be described as a real game process.
"""
from __future__ import annotations
import json, os, sys, tempfile, threading, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s125"
OUT.mkdir(parents=True,exist_ok=True)


def await_samples(sampler):
    for _ in range(300):
        samples=sampler.drain()
        if samples:
            return samples
        time.sleep(0.005)
    return ()


def run():
    q={"status":"NOT_RUN","actual_game":False,"signed_info":False,"proxy":"EXCLUDED"}
    root=None
    try:
        if os.name!="nt":
            raise RuntimeError("WINDOWS_NATIVE_REQUIRED")
        import tkinter as tk
        from permission_guard import PermissionGuard, VerifiedClaims
        from farm_saved_editor import FarmSavedCoordinatesEditor
        from train_saved_coordinates import FarmCoordinate, FarmCoordinatesStore
        from train_account_rows import TkTrainAccountRows
        from train_character_samples import TrainCharacterSample
        from start_windows import NativeWin32Backend, GameWindow
        from start_polling import WindowSnapshot

        with tempfile.TemporaryDirectory(prefix="S125_NATIVE_READONLY_") as td:
            path=Path(td)/"settings.ini"
            path.write_bytes(b"[Settings]\r\ncredentials = untouched\r\n[Farm]\r\nkeep = yes\r\n")
            store=FarmCoordinatesStore(path)
            store.save([FarmCoordinate("A",26,"1","2")])
            root=tk.Tk()
            root.geometry("800x450+0+0")
            editor=FarmSavedCoordinatesEditor(root,store=store)
            editor.pack(fill="x")
            root.update()
            native=NativeWin32Backend()
            hwnd=int(root.winfo_id())
            pid=native.process_id(hwnd)
            q["native_win32_current_hwnd_pid"]=(
                hwnd>0 and pid==os.getpid() and native.is_window(hwnd)
                and native.is_visible(hwnd))
            window=GameWindow(hwnd,pid,"CI Tk owned window","TkTopLevel","NOT_GAME.exe")

            class StubCharacterReader:
                def __init__(self):
                    self.worker_threads=[]
                    self.calls=0
                def read(self,w):
                    self.worker_threads.append(threading.get_ident())
                    self.calls+=1
                    if self.calls==1:
                        return TrainCharacterSample(
                            w.hwnd,w.pid,"<font color='red'>Mộ Dung</font>",
                            90,33,200000,300000)
                    if self.calls==2:
                        # Original H12 bag read failure => PRESERVE prior bag.
                        return TrainCharacterSample(
                            w.hwnd,w.pid,role_name=None,map_id=91,bag_slots=None)
                    return TrainCharacterSample(w.hwnd,w.pid,"STALE",33,0)

            reader=StubCharacterReader()
            guard=PermissionGuard()
            owner=TkTrainAccountRows(
                root,editor,allow_account=lambda _:True,
                permission_guard=guard,running_count=lambda:1,
                identity_backend_factory=NativeWin32Backend,
                character_reader=reader)
            owner.apply_snapshot(
                WindowSnapshot(revision=1,windows=(window,),valid=True))
            row=owner._rows[hwnd]
            q["default_unknown_never_invents_character_fields"]=(
                row["label"].cget("text")==f"HWND {hwnd} / PID {pid}"
                and row["label_map"].cget("text")=="MapID: ?"
                and row["label_bag"].cget("text")=="Túi: ?")
            q["no_unsigned_info_means_no_read"]=(
                not owner.character_sampler.request(
                    tuple(w for w in owner.registry.rows if owner._allowed(w)))
                and reader.calls==0)

            # The fake verifier is solely a CI fixture. NOT a signed Info grant.
            guard.receive_token(
                "CI_TEST_ONLY",
                lambda _:VerifiedClaims(frozenset({"farm_tab"}),"active",2))
            owner.reapply_permissions()
            q["fixture_authorization_can_exercise_reader_seam"]=(
                owner._allowed(window) and reader.calls==0)
            main_tid=threading.get_ident()
            q["real_background_reader_accepted"]=owner.character_sampler.request((window,))
            received=await_samples(owner.character_sampler)
            q["actual_worker_not_tk_main_thread"]=(
                reader.worker_threads and all(x!=main_tid for x in reader.worker_threads))
            q["no_worker_mutated_tk_before_main_apply"]=(
                row["label_map"].cget("text")=="MapID: ?"
                and row["label_bag"].cget("text")=="Túi: ?")
            owner.apply_character_samples(received)
            q["sanitized_role_live_map_and_site10_update_on_tk"]=(
                row["label"].cget("text")=="Mộ Dung"
                and row["label_map"].cget("text")=="MapID: 90"
                and row["label_bag"].cget("text")=="Túi: 33")

            q["second_read_background_started"]=owner.character_sampler.request((window,))
            second=await_samples(owner.character_sampler)
            owner.apply_character_samples(second)
            q["partial_bag_failure_preserves_previous_value"]=(
                row["label_map"].cget("text")=="MapID: 91"
                and row["label_bag"].cget("text")=="Túi: 33")
            fake_reused=TrainCharacterSample(hwnd,pid+1,"FAKE",222,0)
            q["reused_pid_sample_denied_even_if_hwnd_number_equal"]=(
                owner.apply_character_samples((fake_reused,))==0
                and row["label_map"].cget("text")=="MapID: 91")
            guard.clear()
            owner.reapply_permissions()
            q["revoked_info_clears_real_character_details"]=(
                row["sell"].instate(["disabled"])
                and row["label"].cget("text")==f"HWND {hwnd} / PID {pid}"
                and row["label_map"].cget("text")=="MapID: ?"
                and row["label_bag"].cget("text")=="Túi: ?")
            q["revoked_info_cannot_read_again"]=not owner.character_sampler.request(
                tuple(w for w in owner.registry.rows if owner._allowed(w)))

            # Reuse invalidates any earlier permission-backed mailbox.
            owner.apply_snapshot(WindowSnapshot(revision=2,windows=(),valid=True))
            q["valid_empty_destroys_row_and_unbinds"]=(
                not owner._rows and editor.account_bindings.active_count()==0)
            owner.shutdown()
            q["shutdown_revokes_readonly_worker"]=not owner.character_sampler.enabled
            owner.container.destroy()
            editor.destroy()
            root.destroy()
            root=None
            q["settings_credentials_unchanged"]=(
                b"credentials = untouched\r\n" in path.read_bytes()
                and b"keep = yes\r\n" in path.read_bytes())
        if not all(v for k,v in q.items() if type(v) is bool and k not in ("actual_game","signed_info")):
            raise RuntimeError("S125_REAL_NATIVE_TK_READONLY_ASSERTION_FAILED")
        q["status"]="PASS_NATIVE_S125_H12_BACKGROUND_CHARACTER_SAMPLE_TK_NO_REAL_GAME"
    except Exception as exc:
        q["status"]="FAIL_NATIVE_S125"
        q["error_type"]=type(exc).__name__
        q["error_message"]=str(exc)[:150]
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        (OUT/"s125_windows_character_sample.json").write_text(
            json.dumps(q,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        for k,v in q.items():
            print("S125_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if q["status"].startswith("PASS_NATIVE_S125_") else 1

if __name__=="__main__":
    raise SystemExit(run())
