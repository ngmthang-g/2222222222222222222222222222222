"""S89 REAL Windows/Tk Party G01/G08 configuration-only editor smoke.

All dropdown choices are EXPLICITLY TEST-OWNED, never fake read_role,
HWND, TeamID or a game packet. Real Tk button/combobox callbacks write
the actual E05 INI file and persist across a second real editor instance.
"""
from __future__ import annotations
import json
import os
import sys
import tempfile
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "artifacts" / "s89"
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT / "native_party_config_editor.json"


def run():
    report = {
        "task": "S89", "status": "NOT_RUN",
        "host": "REAL_WINDOWS_TK_EDITOR_TEST_ONLY",
        "source_roles": "EXPLICIT_TEST_NAMES_NOT_GAME_ROLE_NAMES",
        "party_create_invite": "NOT_IMPLEMENTED_NOT_EXPOSED",
        "original_exe": "NOT_RUN",
        "signed_info": "NOT_CONNECTED",
        "product_exe": "NOT_BUILT",
    }
    root = None
    temp = None
    try:
        if os.name != "nt":
            raise RuntimeError("WINDOWS_REQUIRED")
        import tkinter as tk
        from party_group_config import PartyConfigStore
        from party_settings_editor import PartySettingsEditor
        from settings_store import read_settings

        temp = tempfile.TemporaryDirectory()
        file = Path(temp.name) / "settings.ini"
        file.write_text("[Settings]\ngame_dir = Z:\\OriginalGame\n", encoding="utf-8")
        store = PartyConfigStore(file)
        root = tk.Tk()
        root.title("S89 Party configuration component TEST OWNED")
        root.geometry("670x450+20+15")
        names = ("Thiên Địa", "Bạch Vân", "Đội Viên")
        editor = PartySettingsEditor(root, store=store, available_names=lambda: names)
        editor.pack(fill="both", expand=True)
        root.update_idletasks()
        root.update()

        assert not editor.group_inputs[0][0].get()
        assert editor.mode_combo.get() == "Chờ"
        editor.mode_combo.set("Train")
        editor.mode_combo.event_generate("<<ComboboxSelected>>")
        root.update()
        assert store.load().after == "train"

        # One actual readonly ttk.Combobox event persists its selected name.
        editor.group_inputs[0][0].set("Thiên Địa")
        editor.group_inputs[0][0].event_generate("<<ComboboxSelected>>")
        root.update()
        assert store.load().groups[0].members[0] == "Thiên Địa"

        # Actual ttk button click, not direct store.save or fake game command.
        editor.add_btn.invoke()
        root.update()
        assert len(editor.group_inputs) == 2
        assert editor.group_inputs[1][4].cget("state") == "readonly"
        editor.group_inputs[1][4].set("Bạch Vân")
        editor.group_inputs[1][4].event_generate("<<ComboboxSelected>>")
        root.update()
        state = store.load()
        assert state.groups[1].members[4] == "Bạch Vân"

        # Closing/reopening genuinely reconstructs both groups and slots.
        editor.destroy()
        editor2 = PartySettingsEditor(root, store=store, available_names=lambda: names)
        editor2.pack(fill="both", expand=True)
        root.update_idletasks()
        root.update()
        assert editor2.mode_combo.get() == "Train"
        assert editor2.group_inputs[0][0].get() == "Thiên Địa"
        assert editor2.group_inputs[1][4].get() == "Bạch Vân"

        # Real group removal button; remaining cluster renumbers to Group 1.
        editor2.remove_buttons[0].invoke()
        root.update()
        assert len(editor2.group_inputs) == 1
        assert editor2.group_inputs[0][4].get() == "Bạch Vân"
        assert editor2.remove_buttons[0].cget("state") == "disabled"

        parser = read_settings(file)
        assert parser.get("Settings", "game_dir") == r"Z:\OriginalGame"
        raw = parser.get("Settings", "party_groups")
        assert "\\u" not in raw
        groups = json.loads(raw)
        assert groups[0]["num"] == 1 and groups[0]["members"][4] == "Bạch Vân"
        assert json.loads(parser.get("Settings", "party_group1")) == ["Bạch Vân"]
        report["real_tk_button_combobox_events"] = True
        report["durable_ini_reload_unicode"] = True
        report["no_fake_game_actions"] = True
        report["status"] = "PASS_NATIVE_S89_PARTY_CONFIG_ONLY_REAL_TK_INI"
    except Exception as exc:
        report["status"] = "FAIL_NATIVE_S89"
        report["error_type"] = type(exc).__name__
        report["error_text"] = str(exc)[:380]
        report["traceback"] = traceback.format_exc(limit=15)
    finally:
        if root is not None:
            try:
                root.destroy()
            except Exception:
                pass
        if temp is not None:
            temp.cleanup()
        REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2),
                          encoding="utf-8")
        for key, value in report.items():
            if key != "traceback":
                print("S89_" + key.upper() + "=" + json.dumps(value, ensure_ascii=True))
    return 0 if report["status"] == "PASS_NATIVE_S89_PARTY_CONFIG_ONLY_REAL_TK_INI" else 1


if __name__ == "__main__":
    raise SystemExit(run())
