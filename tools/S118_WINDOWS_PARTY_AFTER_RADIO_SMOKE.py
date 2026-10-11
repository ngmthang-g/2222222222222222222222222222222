"""S118 actual Windows Tk: original B04 5 Party after-action radios persist G08.

No game process, character/role reader, team action, real Info or Proxy.
Only temporary test-owned Settings.ini data, no user credentials.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "artifacts" / "s118"
OUT.mkdir(parents=True, exist_ok=True)


def run() -> int:
    result = {
        "task": "S118", "status": "NOT_RUN", "game_run": False,
        "real_info": "NOT_AVAILABLE", "proxy": "EXCLUDED",
        "team_actions": "NOT_IMPLEMENTED", "no_credentials_in_report": True,
    }
    root = None
    try:
        if os.name != "nt":
            raise RuntimeError("WINDOWS_TK_REQUIRED")
        import tkinter as tk
        from tkinter import ttk
        from party_group_config import PartyConfigStore, AFTER_LABELS, AFTER_VALUES
        from party_settings_editor import PartySettingsEditor
        from settings_store import read_settings
        with tempfile.TemporaryDirectory(prefix="S118_PARTY_RADIO_TEST_") as td:
            p = Path(td) / "settings.ini"
            p.write_text("[Settings]\ngame_dir = Z:\\OnlyFixture\n"
                         "schedule_open = 04:20\n[Unrelated]\nkeep = yes\n",
                         encoding="utf-8", newline="")
            store = PartyConfigStore(p)
            root = tk.Tk()
            root.geometry("650x820+0+0")
            editor = PartySettingsEditor(root, store=store,
                                         available_names=lambda: ("AliceTEST", "BobTEST"))
            editor.pack(fill="both", expand=True)
            root.update()

            result["five_real_ttk_radio_widgets"] = (
                len(editor.mode_radios) == 5 and
                all(isinstance(r, ttk.Radiobutton) for r in editor.mode_radios))
            result["original_b04_order_and_labels"] = (
                tuple(r.cget("text") for r in editor.mode_radios) == AFTER_LABELS and
                tuple(r.cget("value") for r in editor.mode_radios) == AFTER_LABELS)
            result["initial_wait_selected_without_disk_save"] = (
                editor.mode_var.get() == "Chờ" and
                not read_settings(p).has_option("Settings", "party_after"))

            # Give the existing G08 groups non-empty state; changing radio
            # must never remove or reorder these six account-slot widgets.
            editor.group_inputs[0][0].set("AliceTEST")
            editor.group_inputs[0][0].event_generate("<<ComboboxSelected>>")
            root.update()
            count = len(editor.group_inputs[0])
            all_passed = True
            for radio, label, saved in zip(editor.mode_radios, AFTER_LABELS, AFTER_VALUES):
                radio.invoke()  # ACTUAL Tk command, not direct store.save
                root.update()
                all_passed = all_passed and (
                    editor.mode_var.get() == label
                    and store.load().after == saved
                    and store.load().groups[0].members[0] == "AliceTEST"
                    and len(editor.group_inputs[0]) == count)
            result["all_five_real_radio_changes_durable_g08"] = all_passed
            raw = p.read_text(encoding="utf-8")
            result["unrelated_config_values_preserved"] = (
                "game_dir = Z:\\OnlyFixture" in raw
                and "schedule_open = 04:20" in raw
                and "[Unrelated]" in raw and "keep = yes" in raw)
            # Repeat currently selected radio: must not rewrite settings.ini.
            prev = p.read_bytes()
            editor.mode_radios[-1].invoke()
            root.update()
            result["reselect_same_option_no_disk_rewrite"] = p.read_bytes() == prev

            # Strict no-write failure: valid editor, but the independent store
            # refuses any further writes. Trace must restore previous value
            # without recursive save loops or forged success.
            original_save = editor.store.save
            failed_calls = []
            def fail_save(_value):
                failed_calls.append(True)
                raise OSError("S118_TEST_ONLY_IO_REFUSAL")
            editor.store.save = fail_save
            try:
                editor.mode_radios[0].invoke()
                root.update()
                result["real_save_failure_restores_last_good_radio"] = (
                    editor.mode_var.get() == "Phó bản" and
                    editor.state.after == "phoban" and
                    len(failed_calls) == 1 and
                    editor.last_error == "OSError" and
                    p.read_bytes() == prev)
            finally:
                editor.store.save = original_save
            editor.destroy()
            root.destroy()
            root = None
            # The stored selection survives a genuinely rebuilt new editor.
            root = tk.Tk()
            root.geometry("650x820+0+0")
            rebuilt = PartySettingsEditor(root, store=store,
                                          available_names=lambda: ("AliceTEST", "BobTEST"))
            rebuilt.pack(fill="both", expand=True)
            root.update()
            result["saved_radio_and_group_restored_from_disk"] = (
                rebuilt.mode_var.get() == "Phó bản"
                and rebuilt.group_inputs[0][0].get() == "AliceTEST")
            rebuilt.destroy()
            root.destroy()
            root = None

        required = [k for k,v in result.items() if type(v) is bool
                    and k not in ("game_run",)]
        if not all(result[k] for k in required):
            raise RuntimeError("S118_REAL_NATIVE_RADIO_CHECK_FAILED")
        result["status"] = "PASS_NATIVE_S118_B04_FIVE_PARTY_RADIOS_REAL_G08_INI_NO_GAME"
    except Exception as exc:
        result["status"] = "FAIL_NATIVE_S118"
        result["error_type"] = type(exc).__name__
    finally:
        if root is not None:
            try:
                root.destroy()
            except Exception:
                pass
        (OUT / "windows_party_after_radios.json").write_text(
            json.dumps(result, indent=2, ensure_ascii=False)+"\n",encoding="utf-8")
        for k,v in result.items():
            print("S118_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if result["status"].startswith("PASS_NATIVE_S118_") else 1

if __name__ == "__main__":
    raise SystemExit(run())
