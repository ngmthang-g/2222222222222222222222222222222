"""S137 exact original OFFLINE item metadata catalog regressions.

Unit tests never need the user's 90-MB original ZIP; the independent local
original archive byte-for-byte verification is recorded separately. No game.
"""
from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
import hashlib
from pathlib import Path
import sys
import unittest
from types import MappingProxyType

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import original_item_catalog as cat


class S137OriginalItemCatalog(unittest.TestCase):
    def setUp(self):
        self.rows = {
            101: cat.OriginalItemMeta(101, "Mẫu A", "iconA", "Equips", "0"),
            102: cat.OriginalItemMeta(102, "Mẫu B", "iconA", "Items", None),
            103: cat.OriginalItemMeta(103, "Mẫu A", "iconC", "Equips", "24"),
        }
        self.catalog = cat.OriginalItemCatalog(
            cat.EXE_SHA256, MappingProxyType(self.rows),
            frozenset({101}), cat.TYPES_EXPECTED
        )

    def test_01_known_original_hashes(self):
        self.assertEqual(len(cat.EXE_SHA256),64)
        self.assertEqual(len(cat.ARCHIVE_SHA256),64)
        self.assertNotEqual(cat.EXE_SHA256,cat.ARCHIVE_SHA256)
    def test_02_embedded_exact_counts(self):
        self.assertEqual(cat.META_EXPECTED,29983)
        self.assertEqual(cat.WEAPON_EXPECTED,5477)
    def test_03_exact_weapon_types(self):
        self.assertEqual(cat.TYPES_EXPECTED,(0,1,2,3,4,5,6,7,8,16,17,100))
    def test_04_lookup_by_itemid_not_duplicate_name(self):
        self.assertEqual(self.catalog.lookup(101).name,self.catalog.lookup(103).name)
        self.assertNotEqual(self.catalog.lookup(101).item_id,self.catalog.lookup(103).item_id)
    def test_05_no_name_based_weapon_guess(self):
        self.assertEqual(self.catalog.weapon_membership(101),True)
        self.assertEqual(self.catalog.weapon_membership(103),False)
    def test_06_known_nonweapon_is_false(self):
        self.assertIs(self.catalog.weapon_membership(102),False)
    def test_07_unknown_id_is_unknown_not_false(self):
        self.assertIsNone(self.catalog.weapon_membership(999))
    def test_08_negative_and_bool_are_not_ids(self):
        for v in (-1,0,True,False,3.14,"101",None):
            with self.subTest(v=v):
                self.assertIsNone(self.catalog.lookup(v))
    def test_09_metadata_only_no_game_identity_claim(self):
        self.assertEqual(self.catalog.basic_bag_metadata(101),
                         {"name":"Mẫu A","icon":"iconA","src":"Equips","type":"0"})
    def test_10_non_equip_type_none(self):
        self.assertIsNone(self.catalog.basic_bag_metadata(102)["type"])
    def test_11_metadata_result_no_dbid_or_game_action(self):
        self.assertFalse({"dbID","qty","pos","site"}.intersection(
            self.catalog.basic_bag_metadata(101)))
    def test_12_no_unknown_metadata_fabrication(self):
        self.assertIsNone(self.catalog.basic_bag_metadata(999))
    def test_13_catalog_flags_unverified_in_real_game(self):
        self.assertFalse(self.catalog.live_game_version_verified)
        self.assertFalse(self.catalog.runtime_read_bag_verified)
        self.assertFalse(self.catalog.action_authorized)
    def test_14_catalog_frozen_record(self):
        with self.assertRaises(FrozenInstanceError):
            self.catalog.lookup(101).name="wrong"
    def test_15_mapping_proxy_immutable(self):
        with self.assertRaises(TypeError):
            self.catalog.entries[101]="wrong"
    def test_16_uleb_known_values(self):
        for raw,num in ((b"\xc8\x01",200),(b"\x90N",10000),
                        (b"\x80\x80\x04",65536)):
            self.assertEqual(cat._uleb(raw,0),(num,len(raw)))
    def test_17_truncated_and_overlong_varint(self):
        for raw in (b"",b"\x80",b"\x80"*11):
            with self.subTest(raw=raw),self.assertRaises(ValueError):
                cat._uleb(raw,0)
    def test_18_tagged_text_varieties(self):
        for raw,value in ((b"uHello\0","Hello"),(b"aWorld\0","World"),
                          (b"n",None),(b"wX","X")):
            with self.subTest(raw=raw):
                self.assertEqual(cat._text_field(raw,0),(value,len(raw)))
    def test_19_truncated_tagged_text_fails(self):
        for raw in (b"",b"uNoTerm",b"w",b"?",b"a\xff\0"):
            with self.subTest(raw=raw),self.assertRaises(ValueError):
                cat._text_field(raw,0)
    def test_20_missing_marker_does_not_guess_layout(self):
        with self.assertRaises(ValueError):
            cat._after_marker(b"x"*400,(10,200))
    def test_21_unpinned_exe_refused(self):
        for data in (b"",b"MZ"+b"0"*1000):
            with self.subTest(size=len(data)),self.assertRaisesRegex(ValueError,"UNPINNED"):
                cat.decode_original_exe(data)
    def test_22_unpinned_archive_refused_before_zip_open(self):
        with self.assertRaisesRegex(ValueError,"UNPINNED"):
            cat.load_original_archive(ROOT/"tests"/"test_s137.py")
    def test_23_no_native_game_or_network_and_production_auto_start(self):
        text=(ROOT/"src/original_item_catalog.py").read_text(encoding="utf8")
        for token in ("ReadProcessMemory(", "WriteProcessMemory(", "SendInput(",
                      "RequestSellItem(", "Game.GetItemsAtSite(", "requests.get(",
                      "CreateRemoteThread(", "VerifiedClaims(", "start_farm("):
            self.assertNotIn(token,text)
    def test_24_source_and_test_ast_parse(self):
        for f in ("src/original_item_catalog.py","tests/test_s137.py"):
            ast.parse((ROOT/f).read_text(encoding="utf8"))
    def test_25_row_schema_preserves_original_fields_not_trading(self):
        m=self.catalog.lookup(101)
        self.assertEqual((m.item_id,m.name,m.icon,m.src,m.equip_type),
                         (101,"Mẫu A","iconA","Equips","0"))
    def test_26_unknown_does_not_trigger_weapon_protection_bypass(self):
        self.assertIsNone(self.catalog.weapon_membership(234000000))
    def test_27_no_mutable_positive_runtime_flags(self):
        with self.assertRaises(FrozenInstanceError):
            self.catalog.runtime_read_bag_verified=True
    def test_28_original_metadata_window_is_not_game_offset(self):
        self.assertEqual(cat.META_WINDOW,(0x2977206,0x2977400))
        self.assertEqual(cat.WEAPON_WINDOW,(0x2C54798,0x2C54A00))
        self.assertNotIn("GameAssembly", (ROOT/"src/original_item_catalog.py").read_text(encoding="utf8"))

    def test_29_export_is_deterministic_and_has_source_flags(self):
        import importlib.util, tempfile, gzip, json
        modpath=ROOT/"tools/S137_EXPORT_ORIGINAL_CATALOG.py"
        spec=importlib.util.spec_from_file_location("s137_exporter",modpath)
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as d:
            first=Path(d)/"one.json.gz"
            second=Path(d)/"two.json.gz"
            module.export_catalog(self.catalog,first)
            module.export_catalog(self.catalog,second)
            self.assertEqual(first.read_bytes(),second.read_bytes())
            with gzip.open(first,"rt",encoding="utf8") as stream:
                saved=json.load(stream)
            self.assertFalse(saved["game_runtime_verified"])
            self.assertEqual(saved["item_schema"],["itemID","name","icon","src","type"])
            self.assertEqual(len(saved["entries"]),3)
            self.assertEqual(saved["weapon_ids"],[101])
    def test_30_export_digest_independent_of_metadata_insertion_order(self):
        import importlib.util
        modpath=ROOT/"tools/S137_EXPORT_ORIGINAL_CATALOG.py"
        spec=importlib.util.spec_from_file_location("s137_exporter2",modpath)
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        backwards=cat.OriginalItemCatalog(
            cat.EXE_SHA256, MappingProxyType(dict(reversed(list(self.rows.items())))),
            self.catalog.weapon_ids,cat.TYPES_EXPECTED)
        self.assertEqual(module.canonical_digests(self.catalog),
                         module.canonical_digests(backwards))
    def test_31_export_tool_no_live_game_or_network_action(self):
        code=(ROOT/"tools/S137_EXPORT_ORIGINAL_CATALOG.py").read_text(encoding="utf8")
        for forbidden in ("ReadProcessMemory(", "WriteProcessMemory(",
                          "SendInput(", "requests.get(", "CreateRemoteThread(",
                          "Game.GetItemsAtSite(", "RequestSellItem("):
            self.assertNotIn(forbidden,code)
    def test_32_exporter_ast_compiles(self):
        p=ROOT/"tools/S137_EXPORT_ORIGINAL_CATALOG.py"
        compile(ast.parse(p.read_text(encoding="utf8")),str(p),"exec")

if __name__=="__main__":
    unittest.main()
