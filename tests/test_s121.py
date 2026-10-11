"""S121 partial real Farm coordinates Tk; pure backing and source guard tests."""
from __future__ import annotations
import ast
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from farm_original_maps import FARM_MAP_LIST
from train_saved_coordinates import FarmCoordinate,FarmCoordinatesStore

class TestS121(unittest.TestCase):
    def test_01_editor_class_and_real_bodies(self):
        tree=ast.parse((ROOT/"src/farm_saved_editor.py").read_text(encoding="utf-8"))
        c=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=="FarmSavedCoordinatesEditor")
        methods={n.name for n in c.body if isinstance(n,ast.FunctionDef)}
        self.assertTrue({"commit_row","delete_row","toggle_list","_select_map","_fresh"}.issubset(methods))
    def test_02_native_tk_widgets_used_no_virtual_mock_action(self):
        s=(ROOT/"src/farm_saved_editor.py").read_text(encoding="utf-8")
        for part in ("ttk.Entry(", "ttk.Combobox(", "ttk.Button(", "self.store.save(", 'command=self.toggle_list'):
            self.assertIn(part,s)
    def test_03_no_fake_add_or_game_action_control(self):
        s=(ROOT/"src/farm_saved_editor.py").read_text(encoding="utf-8")
        self.assertNotIn('text="+ Thêm tọa độ"',s)
        # S122 buttons match original H11 PRESET choices, never game action.
        # They stay disabled until REAL caller-owned account combos exist.
        for proof in ('text="Bán"', 'text="Train"',
                      'self.account_bindings.editable_count("sell") > 0',
                      'self.account_bindings.editable_count("farm") > 0',
                      'self.account_bindings.apply_to_all('):
            self.assertIn(proof,s)
        for forbidden in ('text="Bắt đầu"', "PostMessage(",
                          "ReadProcessMemory(", "ProxyServer("):
            self.assertNotIn(forbidden,s)
    def test_04_original_72_map_registry_exact(self):
        self.assertEqual(len(FARM_MAP_LIST),72)
    def test_05_externally_stale_disk_does_not_get_overwritten(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"settings.ini"
            a=FarmCoordinatesStore(p)
            original=(FarmCoordinate("A",26,"1","2"),)
            a.save(original)
            a.save((FarmCoordinate("B",26,"3","4"),))
            self.assertNotEqual(a.load().rows, original)
    def test_06_existing_rename_and_map_write_through_backend(self):
        with tempfile.TemporaryDirectory() as td:
            a=FarmCoordinatesStore(Path(td)/"settings.ini")
            a.save([FarmCoordinate("A",26,"1","2")])
            a.save([FarmCoordinate("B",86,"3","4")])
            self.assertEqual(a.load().rows,(FarmCoordinate("B",86,"3","4"),))
    def test_07_existing_delete_writes_actual_file(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"settings.ini"
            a=FarmCoordinatesStore(p)
            a.save([FarmCoordinate("A",26,"1","2"),FarmCoordinate("B",86,"3","4")])
            a.save([FarmCoordinate("B",86,"3","4")])
            self.assertIn("coord_1 = B|86|3|4",p.read_text(encoding="utf-8"))
            self.assertNotIn("coord_2",p.read_text(encoding="utf-8"))
    def test_08_does_not_guess_original_autosave_cadence(self):
        s=(ROOT/"src/farm_saved_editor.py").read_text(encoding="utf-8")
        self.assertNotIn("after(300",s)
        self.assertNotIn("after(30",s)
    def test_09_missing_map_stays_data_not_action(self):
        from farm_original_maps import coord_id_for_name
        self.assertIsNone(coord_id_for_name("==================="))
        self.assertIsNone(coord_id_for_name("Dạ Tây Hồ"))
    def test_10_no_live_account_or_info_claim(self):
        s=(ROOT/"src/farm_saved_editor.py").read_text(encoding="utf-8")
        for word in ("_toggle_single_farm(", "TOKEN_HMAC_SECRET", "PartyActionCoordinator("):
            self.assertNotIn(word,s)

if __name__=="__main__":
    unittest.main()
