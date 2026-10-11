"""S119 H11 real saved Train coordinates: no fake movement or MapID registry."""
import pathlib
import sys
import tempfile
import unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from train_saved_coordinates import (
    FarmCoordinate, FarmCoordinateError, FarmCoordinatesStore,
)

class TestS119FarmCoordinatePersistence(unittest.TestCase):
    def make(self, folder):
        return FarmCoordinatesStore(
            pathlib.Path(folder) / "settings.ini",
            known_map_ids={101: "Map fixture A", 202: "Map fixture B"})

    def test_01_empty_returns_no_rows(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(self.make(td).load().rows, ())

    def test_02_save_and_load_real_file(self):
        with tempfile.TemporaryDirectory() as td:
            store = self.make(td)
            rows = (FarmCoordinate("Bãi 1", 101, "10", "20"),
                    FarmCoordinate("Bãi 2", 202, "x", "y"))
            self.assertEqual(store.save(rows), "SAVED_FARM_COORDINATES")
            self.assertEqual(store.load().rows, rows)
            self.assertEqual(store.save(rows), "UNCHANGED")

    def test_03_byte_preserves_unrelated_credentials_and_sections(self):
        with tempfile.TemporaryDirectory() as td:
            store = self.make(td)
            original = b"[Settings]\r\naccounts = opaque|SECRET|x|y|z\r\n  second row\r\n[Farm]\r\nother_key = keep\r\ncoord_8 = Old|101|0|0\r\n[Other]\r\nabc = 1\r\n"
            store.path.write_bytes(original)
            self.assertEqual(store.save((FarmCoordinate("New", 202, "7", "8"),)),
                             "SAVED_FARM_COORDINATES")
            actual = store.path.read_bytes()
            self.assertIn(b"accounts = opaque|SECRET|x|y|z\r\n  second row\r\n", actual)
            self.assertIn(b"other_key = keep\r\n", actual)
            self.assertIn(b"[Other]\r\nabc = 1\r\n", actual)
            self.assertIn(b"coord_1 = New|202|7|8\r\n", actual)
            self.assertNotIn(b"coord_8", actual)
            self.assertEqual(len(list(store.path.parent.glob("settings.????????.ini"))), 1)

    def test_04_numeric_order_not_lexicographic(self):
        with tempfile.TemporaryDirectory() as td:
            store = self.make(td)
            raw = "[Farm]\n" + "".join(f"coord_{i} = M{i}|101|{i}|0\n" for i in range(1, 12))
            store.path.write_text(raw, encoding="utf-8")
            self.assertEqual([row.name for row in store.load().rows],
                             [f"M{i}" for i in range(1, 12)])

    def test_05_retired_map_skip_without_guess(self):
        with tempfile.TemporaryDirectory() as td:
            store = self.make(td)
            store.path.write_text("[Farm]\ncoord_1 = Old|999|1|2\ncoord_2 = Good|101|1|2\n",encoding="utf-8")
            loaded = store.load()
            self.assertEqual(loaded.rows, (FarmCoordinate("Good",101,"1","2"),))
            self.assertEqual(loaded.skipped_retired_map_ids, (999,))

    def test_06_unknown_id_refuses_write(self):
        with tempfile.TemporaryDirectory() as td:
            store = self.make(td)
            with self.assertRaises(FarmCoordinateError):
                store.save((FarmCoordinate("A",999,"1","2"),))
            self.assertFalse(store.path.exists())

    def test_07_non_numeric_xy_remain_as_entered(self):
        with tempfile.TemporaryDirectory() as td:
            store = self.make(td)
            row = FarmCoordinate("X",101,"abc","?999")
            store.save((row,))
            self.assertEqual(store.load().rows,(row,))

    def test_08_duplicate_key_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            store = self.make(td)
            raw=b"[Farm]\ncoord_01 = A|101|1|2\ncoord_1 = B|101|3|4\n"
            store.path.write_bytes(raw)
            with self.assertRaises(FarmCoordinateError):
                store.save(())
            self.assertEqual(store.path.read_bytes(),raw)

    def test_09_duplicate_farm_section_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            store = self.make(td)
            raw=b"[Farm]\ncoord_1 = A|101|1|2\n[Farm]\ncoord_2 = B|101|3|4\n"
            store.path.write_bytes(raw)
            with self.assertRaises(FarmCoordinateError):
                store.save(())
            self.assertEqual(store.path.read_bytes(),raw)

    def test_10_invalid_fields_cannot_inject_ini(self):
        with tempfile.TemporaryDirectory() as td:
            store = self.make(td)
            for name in ("A\nbad", "A|bad"):
                with self.assertRaises(FarmCoordinateError):
                    store.save((FarmCoordinate(name,101,"1","2"),))
            self.assertFalse(store.path.exists())

    def test_11_missing_map_registry_is_no_authority(self):
        with tempfile.TemporaryDirectory() as td:
            store = FarmCoordinatesStore(pathlib.Path(td)/"settings.ini",known_map_ids={})
            with self.assertRaises(FarmCoordinateError):
                store.save((FarmCoordinate("A",101,"1","2"),))

    def test_12_crlf_roundtrip_preserves_old_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            store = self.make(td)
            original=b"[Settings]\r\nx=1\r\n[Farm]\r\ncoord_1 = A|101|1|2\r\nother=1\r\n"
            store.path.write_bytes(original)
            store.save((FarmCoordinate("B", 202, "3", "4"),))
            self.assertEqual(store.path.read_bytes(),
                original.replace(b"coord_1 = A|101|1|2",b"coord_1 = B|202|3|4"))

    def test_13_no_game_or_auth_or_proxy_imports(self):
        source=(ROOT/"src/train_saved_coordinates.py").read_text(encoding="utf-8")
        for forbidden in ("ReadProcessMemory", "Frida(", "SendInput(", "PostMessage(",
                          "has_permission_with_limit(", "_toggle_single_farm(",
                          "TOKEN_HMAC_SECRET", "ProxyServer("):
            self.assertNotIn(forbidden,source)

if __name__=="__main__":
    unittest.main()
