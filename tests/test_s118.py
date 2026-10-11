"""S118 B04/G01 five genuine Party-after radio choices, G08 persistence."""
from __future__ import annotations

import ast
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from party_group_config import AFTER_LABELS, AFTER_VALUES, PartySettings, PartyConfigStore


class S118PartyAfterRadioSourceTests(unittest.TestCase):
    def test_01_exact_original_b04_labels_order(self):
        self.assertEqual(AFTER_LABELS, ("Chờ", "Train", "Train LSV",
                                        "Dồn vàng", "Phó bản"))

    def test_02_exact_original_g08_saved_modes_order(self):
        self.assertEqual(AFTER_VALUES, ("wait", "train", "train_lsv",
                                        "don", "phoban"))

    def test_03_5_choice_durable_roundtrip_without_changing_groups(self):
        with tempfile.TemporaryDirectory() as folder:
            store = PartyConfigStore(Path(folder) / "settings.ini")
            original = PartySettings().add_group().select_member(2, 3, "Test Party")
            store.save(original)
            for mode in AFTER_VALUES:
                original = original.change_after(mode)
                store.save(original)
                loaded = store.load()
                self.assertEqual(loaded.after, mode)
                self.assertEqual(loaded.groups, original.groups)

    def test_04_true_ttk_radio_widgets_not_combo_by_ast(self):
        code = (ROOT / "src/party_settings_editor.py").read_text(encoding="utf-8")
        tree = ast.parse(code)
        clazz = next(n for n in tree.body
                     if isinstance(n, ast.ClassDef) and n.name == "PartySettingsEditor")
        constructor = next(n for n in clazz.body
                           if isinstance(n, ast.FunctionDef) and n.name == "__init__")
        calls = [n for n in ast.walk(constructor) if isinstance(n, ast.Call)]
        self.assertTrue(any(isinstance(n.func, ast.Attribute)
                            and n.func.attr == "Radiobutton" for n in calls))
        self.assertFalse(any(isinstance(n.func, ast.Attribute)
                             and n.func.attr == "Combobox"
                             for n in ast.walk(constructor) if isinstance(n, ast.Call)))
        self.assertTrue(any(isinstance(n.func, ast.Attribute)
                            and n.func.attr == "trace_add" for n in calls))

    def test_05_original_group_slot_editor_kept(self):
        code = (ROOT / "src/party_settings_editor.py").read_text(encoding="utf-8")
        self.assertIn('text="+ Thêm nhóm"', code)
        self.assertIn("for slot in range(MAX_GROUP_MEMBERS)", code)
        self.assertIn('state="readonly"', code)
        self.assertIn("self.store.save(updated)", code)

    def test_06_invalid_mode_never_writes_g08_state(self):
        with self.assertRaises(ValueError):
            PartySettings().change_after("not-original")

    def test_07_no_game_auth_or_proxy_action_in_party_editor(self):
        text = (ROOT / "src/party_settings_editor.py").read_text(encoding="utf-8")
        for forbidden in ("CreateRemoteThread(", "ReadProcessMemory(",
                          "PostMessage(", "TOKEN_HMAC_SECRET", "200051",
                          "_run_one_group(", "ProxyServer(", "TkPartyTab("):
            self.assertNotIn(forbidden, text)

    def test_08_true_trace_guard_and_redundant_no_save(self):
        code = (ROOT / "src/party_settings_editor.py").read_text(encoding="utf-8")
        self.assertIn("self._restoring_after = True", code)
        self.assertIn("if next_mode == self.state.after:", code)
        self.assertIn("self._restore_after_var()", code)


if __name__ == "__main__":
    unittest.main()
