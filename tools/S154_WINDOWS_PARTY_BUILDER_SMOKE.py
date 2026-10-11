"""S154 native Win64 E03 Party G08 real settings editor with test-only permission.

No actual signed Info issuer, original live game RoleName or G10 team action.
A TEST-OWNED authorization set is injected solely to prove the existing E03
lazy factory and real ttk event handlers are wired correctly.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s154"
OUT.mkdir(parents=True,exist_ok=True)


def run():
    result={"status":"NOT_RUN","real_signed_info":False,
            "test_injected_permission_only":True,
            "original_game_used":False,"team_commands_sent":0,
            "full_original_Party_UI_recovered":False,
            "product_exe_built":False}
    root=None
    tmp=None
    try:
        if os.name!="nt":raise OSError("WINDOWS_REQUIRED")
        import tkinter as tk
        from shell import ALL_KEYS,INFO_KEY,TabLifecycle,MissingFeatureError
        from source_backed_tab_builders import source_backed_tab_builders
        from settings_store import read_settings

        tmp=tempfile.TemporaryDirectory()
        ini=Path(tmp.name)/"settings.ini"
        ini.write_bytes(b"[Settings]\r\ngame_dir = Z:\\NoGame\r\n")
        root=tk.Tk()
        root.title("S154 TEST-ONLY verified partial Party config")
        root.geometry("760x680+30+30")
        frames={key:tk.Frame(root) for key in ALL_KEYS}
        builder=source_backed_tab_builders(
            lambda parent: tk.Label(parent,text="TEST_INFO_ONLY"),
            settings_file=ini,party_names_provider=lambda:("TEST_ONE","TEST_TWO"))
        life=TabLifecycle(builder,frames)
        checks={}
        checks["party_exists_only_in_original_spec"]=(
            "party_tab" in builder and len(ALL_KEYS)==15)
        checks["initial_unapproved_party_not_constructed"]=(
            "party_tab" not in life.visible and
            "party_tab" not in life._instances)
        try:
            life.ensure_built("party_tab")
            checks["unapproved_build_prohibited"]=False
        except MissingFeatureError:
            checks["unapproved_build_prohibited"]=True

        # Explicit local TEST OWNED verified entitlement. No product grant.
        life.apply_authorized_keys({"party_tab"})
        panel=life.select("party_tab")
        frames["party_tab"].pack(fill="both",expand=True)
        root.update_idletasks()
        root.update()
        checks["lazy_genuine_tk_editor_only_after_test_grant"]=(
            life._instances.get("party_tab") is panel
            and panel.winfo_exists() and panel.winfo_ismapped())
        checks["five_original_modes_and_six_widgets"]=(
            len(panel.mode_radios)==5 and len(panel.group_inputs)==1
            and len(panel.group_inputs[0])==6)
        checks["no_fake_create_group_action_button"]=(
            all(not w.cget("text").startswith("▶ Tạo nhóm")
                for w in panel.winfo_children() if isinstance(w,tk.Button))
            and not hasattr(panel,"btn_toggle"))

        panel.mode_radios[2].invoke() # Train LSV = train_lsv
        root.update()
        checks["real_party_after_radio_persisted"]=(
            read_settings(ini).get("Settings","party_after")=="train_lsv")

        panel.group_inputs[0][0].set("TEST_ONE")
        panel.group_inputs[0][0].event_generate("<<ComboboxSelected>>")
        root.update()
        checks["actual_combo_event_saved_original_group1"]=(
            json.loads(read_settings(ini).get("Settings","party_group1"))==["TEST_ONE"])

        panel.add_btn.invoke()
        root.update()
        checks["real_plus_group_tk_button_and_json_write"]=(
            len(panel.group_inputs)==2 and
            len(json.loads(read_settings(ini).get("Settings","party_groups")))==2)

        panel.group_inputs[1][4].set("TEST_TWO")
        panel.group_inputs[1][4].event_generate("<<ComboboxSelected>>")
        root.update()
        checks["actual_second_group_slot_four_save"]=(
            json.loads(read_settings(ini).get("Settings","party_groups"))[1]
                      ["members"][4]=="TEST_TWO")
        checks["unrelated_login_directory_remains_semantically_same"]=(
            read_settings(ini).get("Settings","game_dir")==r"Z:\NoGame")

        # Re-read persisted config in a fresh truly mapped Tk editor.
        panel.destroy()
        frames["party_tab"].destroy()
        fresh=tk.Frame(root)
        fresh.pack(fill="both",expand=True)
        rebuilt=builder["party_tab"](fresh)
        root.update_idletasks()
        root.update()
        checks["reopening_real_widget_restores_both_groups"]=(
            len(rebuilt.group_inputs)==2 and
            rebuilt.group_inputs[0][0].get()=="TEST_ONE"
            and rebuilt.group_inputs[1][4].get()=="TEST_TWO")

        rebuilt.remove_buttons[0].invoke()
        root.update()
        checks["real_delete_and_renumber_group"]=(
            len(rebuilt.group_inputs)==1 and
            rebuilt.group_inputs[0][4].get()=="TEST_TWO")
        rebuilt.destroy()
        result["checks"]=checks
        result["status"]=(
            "PASS_NATIVE_S154_E03_REAL_PARTY_G08_CONFIG_TEST_OWNED_NOT_PRODUCT"
            if all(checks.values()) else "FAIL_NATIVE_S154_PARTY_INTEGRATION")
    except Exception as exc:
        result["status"]="FAIL_NATIVE_S154_PARTY_INTEGRATION"
        result["error_type"]=type(exc).__name__
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        if tmp is not None:tmp.cleanup()
        target=OUT/"party_config_authorized_only.json"
        target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",
                          encoding="utf-8")
        print(json.dumps(result,ensure_ascii=False))
    return 0 if result["status"].startswith("PASS_") else 1


if __name__=="__main__":
    raise SystemExit(run())
