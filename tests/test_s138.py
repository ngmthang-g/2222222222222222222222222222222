"""S138 strict offline exported catalog and deterministic portable pack checks.

CI deliberately does NOT contain the user's original ZIP or real catalog
payload. Synthetic fixtures only exercise failure boundaries and deterministic
zip construction; real original payload is verified separately offline.
"""
from __future__ import annotations

from contextlib import redirect_stdout, redirect_stderr
import ast
from dataclasses import FrozenInstanceError
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from types import MappingProxyType
from unittest import mock
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"tools"))
import original_item_catalog as base
import original_item_catalog_resource as resource
import S138_CATALOG_LOOKUP as cli
import S138_PACKAGE_OFFLINE_CATALOG as pack


def tiny_catalog_and_export():
    rows=[
        [10,"Vật phẩm thử 1","IconA","Equips","0"],
        [20,"Vật phẩm thử 2","IconB","Items",None],
    ]
    doc={
        "source":"OFFLINE_EXACT_ORIGINAL_TLMTOOL_2_1_2",
        "original_exe_sha256":base.EXE_SHA256,
        "game_runtime_verified":False,
        "item_schema":["itemID","name","icon","src","type"],
        "entries":rows,
        "weapon_ids":[10],
        "weapon_types":list(base.TYPES_EXPECTED),
    }
    row_digest=hashlib.sha256(
        "".join(f"{i}\t{n}\t{icon}\t{s}\t{t or ''}\n"
                for i,n,icon,s,t in rows).encode("utf-8")
    ).hexdigest()
    weapon_digest=hashlib.sha256(b"10\n").hexdigest()
    return doc, row_digest, weapon_digest


def patch_test_only_shape(row_digest,weapon_digest):
    return (
        mock.patch.object(resource,"TOTAL_ITEMS",2),
        mock.patch.object(resource,"TOTAL_WEAPONS",1),
        mock.patch.object(resource,"SOURCE_COUNTS",{"Equips":1,"Items":1}),
        mock.patch.object(resource,"METADATA_ROWS_SHA256",row_digest),
        mock.patch.object(resource,"WEAPON_IDS_SHA256",weapon_digest),
    )


class S138OfflineResourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc, cls.mdigest, cls.wdigest=tiny_catalog_and_export()
    def validate_small(self,doc=None):
        import contextlib
        with contextlib.ExitStack() as stack:
            for p in patch_test_only_shape(self.mdigest,self.wdigest):stack.enter_context(p)
            return resource._validate_export_structure(self.doc if doc is None else doc)

    def test_01_pinned_export_hash(self):
        self.assertEqual(resource.EXPORTED_GZIP_SHA256,
                         "e9322e4c6e5f0a832ae76316ad9be5fc9dc0fd2ebd0043f02bef0da360fb220a")
    def test_02_pinned_json_hash_and_sizes(self):
        self.assertEqual(resource.EXPORTED_JSON_SHA256,
                         "2f93cd68415ce102b79d3a8ba2e827a38e463580050433da71a50f5b1ff859fe")
        self.assertEqual((resource.GZIP_SIZE,resource.JSON_SIZE),(193833,2155301))
    def test_03_exact_original_counts(self):
        self.assertEqual((resource.TOTAL_ITEMS,resource.TOTAL_WEAPONS),(29983,5477))
    def test_04_missing_input_fail_closed(self):
        with self.assertRaises(FileNotFoundError):
            resource.load_verified_export(ROOT/"tests"/"_S138_missing.json.gz")
    def test_05_mismatched_bytes_refused_before_decompression(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"bad.gz";p.write_bytes(b"bogus")
            with self.assertRaisesRegex(ValueError,"SHA256_MISMATCH"):
                resource.load_verified_export(p)
    def test_06_good_synthetic_schema_is_only_unit_shape_test(self):
        catalog=self.validate_small()
        self.assertEqual(catalog.lookup(10).name,"Vật phẩm thử 1")
        self.assertIs(catalog.weapon_membership(10),True)
        self.assertIs(catalog.weapon_membership(20),False)
        self.assertIsNone(catalog.weapon_membership(30))
        self.assertFalse(catalog.live_game_version_verified)
        self.assertFalse(catalog.runtime_read_bag_verified)
        self.assertFalse(catalog.action_authorized)
    def test_07_bad_provenance_refused(self):
        doc=dict(self.doc);doc["original_exe_sha256"]="X"*64
        with self.assertRaisesRegex(ValueError,"PROVENANCE"):
            self.validate_small(doc)
    def test_08_runtime_game_claim_refused(self):
        doc=dict(self.doc);doc["game_runtime_verified"]=True
        with self.assertRaisesRegex(ValueError,"PROVENANCE"):
            self.validate_small(doc)
    def test_09_schema_extra_key_refused(self):
        doc=dict(self.doc);doc["arbitrary"]="anything"
        with self.assertRaisesRegex(ValueError,"SCHEMA"):
            self.validate_small(doc)
    def test_10_count_mismatch_refused(self):
        doc=dict(self.doc);doc["entries"]=self.doc["entries"][:1]
        with self.assertRaisesRegex(ValueError,"COUNT"):
            self.validate_small(doc)
    def test_11_unsorted_itemid_refused(self):
        doc=dict(self.doc);doc["entries"]=list(reversed(self.doc["entries"]))
        with self.assertRaisesRegex(ValueError,"UNSORTED"):
            self.validate_small(doc)
    def test_12_bool_itemid_refused(self):
        doc=dict(self.doc); doc["entries"]=[ [True,*self.doc["entries"][0][1:]], self.doc["entries"][1] ]
        with self.assertRaisesRegex(ValueError,"INVALID"):
            self.validate_small(doc)
    def test_13_modified_name_canonical_digest_refused(self):
        doc=dict(self.doc);doc["entries"]=[list(row) for row in self.doc["entries"]]
        doc["entries"][1][1]="tampered"
        with self.assertRaisesRegex(ValueError,"CANONICAL"):
            self.validate_small(doc)
    def test_14_unknown_weapon_refused(self):
        doc=dict(self.doc);doc["weapon_ids"]=[15]
        with self.assertRaisesRegex(ValueError,"WEAPON"):
            self.validate_small(doc)
    def test_15_wrong_weapon_metadata_refused(self):
        doc=dict(self.doc);doc["weapon_ids"]=[20]
        import contextlib
        with contextlib.ExitStack() as stack:
            for p in patch_test_only_shape(self.mdigest,hashlib.sha256(b"20\n").hexdigest()):
                stack.enter_context(p)
            with self.assertRaisesRegex(ValueError,"CROSSJOIN"):
                resource._validate_export_structure(doc)
    def test_16_catalog_immutable_after_loaded(self):
        c=self.validate_small()
        with self.assertRaises(TypeError):c.entries[10]="fake"
    def test_17_strict_int_rejects_bool(self):
        self.assertTrue(resource._is_strict_int(10))
        self.assertFalse(resource._is_strict_int(True))
        self.assertFalse(resource._is_strict_int("10"))
        self.assertFalse(resource._is_strict_int(0))
    def test_18_cli_valid_itemid_is_metadata_only(self):
        c=self.validate_small()
        o=io.StringIO()
        with mock.patch.object(cli,"load_verified_export",return_value=c),redirect_stdout(o):
            code=cli.main(["--item-id","10"])
        out=json.loads(o.getvalue())
        self.assertEqual(code,0)
        self.assertEqual(out["itemID"],10)
        self.assertTrue(out["is_weapon"])
        self.assertFalse(out["game_attached"])
        self.assertFalse(out["runtime_bag_read_verified"])
        self.assertFalse(out["game_actions_sent"])
    def test_19_cli_unknown_id_not_fabricated(self):
        c=self.validate_small(); o=io.StringIO()
        with mock.patch.object(cli,"load_verified_export",return_value=c),redirect_stdout(o):
            code=cli.main(["--item-id","999"])
        self.assertEqual(code,3)
        self.assertEqual(json.loads(o.getvalue())["status"],"UNKNOWN_ITEMID_IN_ORIGINAL_2_1_2")
    def test_20_cli_corrupt_catalog_returns_blocked(self):
        with mock.patch.object(cli,"load_verified_export",side_effect=ValueError("bad SHA")),redirect_stderr(io.StringIO()) as out:
            code=cli.main(["--item-id","10"])
        self.assertEqual(code,2)
        self.assertIn("BLOCKED_CATALOG_NOT_VERIFIED",out.getvalue())
    def test_21_cli_real_missing_default_fail_closed(self):
        with redirect_stderr(io.StringIO()):
            self.assertEqual(cli.main(["--item-id","10","--catalog",
                                       str(ROOT/"tests"/"_S138_missing.gz")]),2)
    def test_22_bundle_rejects_wrong_catalog_sha(self):
        with tempfile.TemporaryDirectory() as d:
            bad=Path(d)/"fake.gz";bad.write_bytes(b"anything")
            with self.assertRaisesRegex(ValueError,"SHA256"):
                pack.build_offline_bundle(bad,Path(d)/"out.zip")
    def test_23_bundle_requires_separate_output(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"one.gz"
            with self.assertRaisesRegex(ValueError,"MUST_DIFFER"):
                pack.build_offline_bundle(p,p)
    def test_24_bundle_deterministic_and_testonly(self):
        c=self.validate_small()
        with tempfile.TemporaryDirectory() as d:
            original=Path(d)/"test_gzip";original.write_bytes(b"TEST_OWNED_ONLY")
            first=Path(d)/"one.zip";second=Path(d)/"two.zip"
            with mock.patch.object(pack,"load_verified_export",return_value=c):
                a=pack.build_offline_bundle(original,first)
                b=pack.build_offline_bundle(original,second)
            self.assertEqual(first.read_bytes(),second.read_bytes())
            self.assertEqual(a["bundle_sha256"],b["bundle_sha256"])
            with zipfile.ZipFile(first) as z:
                names=z.namelist()
                self.assertTrue(any(s.endswith("original_item_catalog.json.gz") for s in names))
                self.assertTrue(any(s.endswith("lookup_item_windows.cmd") for s in names))
                mf=json.loads(z.read("S138_ORIGINAL_ITEM_CATALOG_OFFLINE/manifest.json"))
                self.assertFalse(mf["real_game_reader"])
                self.assertFalse(mf["runtime_read_bag"])
                self.assertFalse(mf["game_actions"])
                self.assertFalse(mf["contains_original_game_executable"])
    def test_25_source_ast_parse(self):
        for name in ("src/original_item_catalog_resource.py",
                     "tools/S138_CATALOG_LOOKUP.py",
                     "tools/S138_PACKAGE_OFFLINE_CATALOG.py",
                     "tests/test_s138.py"):
            compile(ast.parse((ROOT/name).read_text(encoding="utf8")),name,"exec")
    def test_26_no_action_game_or_network_production(self):
        for name in ("src/original_item_catalog_resource.py",
                     "tools/S138_CATALOG_LOOKUP.py",
                     "tools/S138_PACKAGE_OFFLINE_CATALOG.py"):
            data=(ROOT/name).read_text(encoding="utf8")
            for forbidden in ("ReadProcessMemory(", "WriteProcessMemory(", "SendInput(",
                              "CreateRemoteThread(", "Game.GetItemsAtSite(",
                              "RequestSellItem(", "requests.get(", "OpenProcess("):
                self.assertNotIn(forbidden,data)

if __name__=="__main__":
    unittest.main()
