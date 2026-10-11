"""S122 source-backed name selections, actual Tk native separately."""
from __future__ import annotations
import ast
from pathlib import Path
import sys
import unittest
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"src"))
from farm_preset_account_binding import preset_names,renamed_selection
from train_saved_coordinates import FarmCoordinate
class TestS122(unittest.TestCase):
    def test_01_names(self):
        self.assertEqual(preset_names([FarmCoordinate("A",26,"1","2")]),("A",))
    def test_02_rows_type(self):
        with self.assertRaises(ValueError):preset_names(["fake"])
    def test_03_rename(self):
        self.assertEqual(renamed_selection("A",{"A":"B"}),"B")
    def test_04_unrelated_not_renamed(self):
        self.assertEqual(renamed_selection("C",{"A":"B"}),"C")
    def test_05_no_rename_changes(self):
        self.assertEqual(renamed_selection("A",None),"A")
    def test_06_bad_name_type(self):
        with self.assertRaises(ValueError):renamed_selection(None,{})
    def test_07_real_tk_api(self):
        s=(R/"src/farm_preset_account_binding.py").read_text(encoding="utf-8")
        for part in ("weakref.ref(", "combo.configure(values=names)", "combo.set(new)", "chosen.set(preset_name)"):
            self.assertIn(part,s)
    def test_08_no_mock_account_row(self):
        s=(R/"src/farm_preset_account_binding.py").read_text(encoding="utf-8")
        for word in ("PostMessage(", "ReadProcessMemory(", "CreateProcess(", "TokenInfo(", "proxy_tab"):
            self.assertNotIn(word,s)
    def test_09_actual_ui_buttons(self):
        s=(R/"src/farm_saved_editor.py").read_text(encoding="utf-8")
        for word in ('text="Bán"','text="Train"','self.account_bindings.apply_to_all(', 'self.account_bindings.refresh(', 'self.account_bindings.register('):
            self.assertIn(word,s)
    def test_10_unknown_add_defaults_not_invented(self):
        self.assertNotIn('text="+ Thêm tọa độ"',(R/"src/farm_saved_editor.py").read_text(encoding="utf-8"))
    def test_11_no_autosave_interval_guess(self):
        self.assertNotIn("after(300", (R/"src/farm_saved_editor.py").read_text(encoding="utf-8"))
    def test_12_map_source_kept(self):
        from farm_original_maps import FARM_MAP_LIST
        self.assertEqual(len(FARM_MAP_LIST),72)
if __name__=="__main__":unittest.main()
