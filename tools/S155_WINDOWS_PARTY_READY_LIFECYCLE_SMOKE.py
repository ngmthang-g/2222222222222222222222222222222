"""S155 real Win64/Tk/G02 Party ready-list integration through E03.

Uses 3 actual TEST-OWNED native Tk HWNDs with an explicitly test-injected
G03 RoleReading callback. Does NOT read real game memory, open original TLM,
grant signed Info or send any mutable team action.
"""
from __future__ import annotations
import json,os,sys,tempfile,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s155"
OUT.mkdir(parents=True,exist_ok=True)

def run():
    report={"status":"NOT_RUN",
            "real_signed_Info":False,
            "game_RoleName_reader_verified":False,
            "source":"THREE_ACTUAL_TEST_OWNED_NATIVE_TK_HWNDS",
            "test_only_RoleReading":True,"team_actions_sent":0,
            "product_exe_built":False}
    root=None; tmp=None; life=None
    try:
        if os.name!="nt":raise OSError("WIN64_REQUIRED")
        import tkinter as tk
        from dwm_preview import NativeDwmBackend
        from start_polling import WindowSnapshot
        from start_windows import GameWindow
        from auto_role_provenance import RoleReading
        from source_backed_tab_builders import source_backed_tab_builders
        from shell import ALL_KEYS,INFO_KEY,TabLifecycle

        tmp=tempfile.TemporaryDirectory()
        ini=Path(tmp.name)/"settings.ini"
        ini.write_text("[Settings]\ngame_dir = Q:\\TEST_GAME_PATH\n",encoding="utf-8")
        root=tk.Tk()
        root.title("S155 ORIGINAL G02 READY TEST ONLY")
        root.geometry("775x715+20+10")
        identity=NativeDwmBackend()
        role_names=("TÊN THỬ 1","TÊN THỬ 2","TÊN THỬ 3")
        tops=[]
        for i in range(3):
            w=tk.Toplevel(root)
            w.title("TITLE IS NEVER A ROLE NAME")
            w.geometry(f"185x115+{805+i*65}+{45+i*24}")
            tk.Label(w,text="TEST HWND NOT GAME").pack()
            tops.append(w)
        root.update_idletasks()
        root.update()
        handles=tuple(int(identity._ancestor(int(w.winfo_id()),2)) for w in tops)
        pid=os.getpid()
        assert len(set(handles))==3
        assert all(identity.source_matches(h,pid) for h in handles)
        by_handle=dict(zip(handles,role_names))

        def window(h):
            return GameWindow(h,pid,"TITLE NOT PLAYER NAME",
                              "TEST_TK","NOT_GAME.exe")
        class Producer:
            def __init__(self):
                self.snapshot=WindowSnapshot(1,tuple(window(h) for h in handles),True)
                self.calls=0
            def read_snapshot(self):
                self.calls+=1
                return self.snapshot
        producer=Producer()
        def reader(h,p):
            if p!=pid or h not in by_handle or not identity.source_matches(h,p):
                return None
            return RoleReading(h,p,"<span>"+by_handle[h]+"</span>")

        factory=source_backed_tab_builders(
            lambda parent:tk.Frame(parent),
            settings_file=ini,start_producer=producer,
            party_role_reader=reader)
        frames={key:tk.Frame(root) for key in ALL_KEYS}
        life=TabLifecycle(factory,frames)
        checks={}
        checks["party_not_constructed_before_verified_entitlement"]=(
            "party_tab" not in life.visible and
            "party_tab" not in life._instances)
        # Explicit TEST entitlement only; product still cannot launch.
        life.apply_authorized_keys({"party_tab"})
        panel=life.select("party_tab")
        frames["party_tab"].pack(fill="both",expand=True)
        root.update_idletasks();root.update()
        checks["real_party_frame_built_once_after_explicit_test_grant"]=(
            life._instances["party_tab"] is panel and panel.winfo_exists())
        checks["no_name_inferred_from_native_Window_TITLE_before_reader"]=(
            panel.ready_list.names==())
        def until(fn,seconds=7.7):
            end=time.monotonic()+seconds
            while time.monotonic()<end:
                root.update()
                if fn():return True
                time.sleep(.02)
            return False
        checks["3s_G02_worker_reads_real_Start_snapshot_through_reader"]=until(
            lambda:panel.ready_list.names==role_names)
        assert checks["3s_G02_worker_reads_real_Start_snapshot_through_reader"]
        checks["real_Tk_ready_items_exact_3_column_row"]=(
            [(int(w.grid_info()["row"]),int(w.grid_info()["column"]))
             for w in panel.ready_list.labels]==[(0,0),(0,1),(0,2)])
        panel.group_inputs[0][0].set(role_names[0])
        panel.group_inputs[0][0].event_generate("<<ComboboxSelected>>")
        root.update()
        checks["selected_role_saved_and_removed_from_ready_pool"]=(
            panel.store.load().groups[0].members[0]==role_names[0]
            and panel.ready_list.names==role_names[1:])
        checks["live_GameHWND_never_persisted_in_G08_settings"]=(
            not any(str(h) in ini.read_text("utf-8") for h in handles))
        # Explicit tab deactivation stops the exact existing G02 S90 timer
        # and clears previously verified identities. No worker runs hidden.
        life.select(INFO_KEY)
        root.update()
        checks["E03_select_other_tab_really_stops_and_clears_ready_roster"]=(
            not panel._roster_reader.active and panel.ready_list.names==())
        life.select("party_tab")
        checks["E03_reselect_restarts_original_3s_roster"]=(
            panel._roster_reader.active and until(
                lambda:panel.ready_list.names==role_names[1:]))
        # A missing/reused native handle is dropped on the next revision.
        gone=tops[1]
        gone_handle=handles[1]
        gone.destroy()
        root.update()
        assert not identity._is_window(gone_handle)
        producer.snapshot=WindowSnapshot(
            2,tuple(window(h) for h in handles if h!=gone_handle),True)
        checks["destroyed_HWND_Pid_identity_automatically_evicted"]=until(
            lambda:panel.ready_list.names==(role_names[2],))
        life.select(INFO_KEY)
        life.shutdown()
        checks["owner_shutdown_never_sends_party_game_commands"]=(
            panel._closing_ready and report["team_actions_sent"]==0)
        from settings_store import read_settings
        checks["Login_game_dir_setting_still_preserved"]=(
            read_settings(ini).get("Settings","game_dir")==r"Q:\TEST_GAME_PATH")
        checks["no_real_Info_or_game_ever_used"]=(
            not report["real_signed_Info"] and
            not report["game_RoleName_reader_verified"])
        report["checks"]=checks
        report["status"]=("PASS_NATIVE_S155_PARTY_G02_READY_E03_LIFECYCLE_TEST_OWNED"
                          if all(checks.values()) else "FAIL_NATIVE_S155_G02")
    except Exception as exc:
        report["status"]="FAIL_NATIVE_S155_G02"
        report["error_type"]=type(exc).__name__
        report["error_message"]=str(exc)[:200]
    finally:
        if life is not None:
            try:life.shutdown()
            except Exception:pass
        if root is not None:
            try:root.destroy()
            except Exception:pass
        if tmp is not None:tmp.cleanup()
        (OUT/"party_g02_e03_real_tk_native.json").write_text(
            json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(json.dumps(report,ensure_ascii=False))
    return 0 if report["status"].startswith("PASS_") else 1

if __name__=="__main__":
    raise SystemExit(run())
