"""S136 no-live-game O03 original binary evidence audit regressions."""
from __future__ import annotations
import ast
from pathlib import Path
import subprocess
import sys
import unittest
from dataclasses import FrozenInstanceError

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import S136_AUDIT_ORIGINAL_BAG_CONSTANTS as mod

class TestS136(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Synthetic sparse byte array only. The genuine frozen ZIP is NOT
        # committed, downloaded, executed or required by GitHub CI.
        raw=bytearray(mod.REGION_END+40)
        for offset,marker in mod.PINNED.values():
            raw[offset:offset+len(marker)]=marker
        for i,field in enumerate(("dbID","itemID","pos","qty")):
            tok=("a"+field+"\0").encode()
            offset=0x2B6A780+i*9
            raw[offset:offset+len(tok)]=tok
        for i,field in enumerate(mod.GET_BAG_FIELDS):
            tok=("a"+field+"\0").encode()
            offset=0x2B6A83A+i*11
            raw[offset:offset+len(tok)]=tok
        for val,offset in ((24,0x2B6A71D),(32,0x2B6A725),
                           (10000,0x2B6A740),(65536,0x2B6A758),
                           (1000000,0x2B6A76D)):
            n=val;seq=[]
            while True:
                part=n&127;n>>=7;seq.append(part | (128 if n else 0))
                if not n:break
            raw[offset:offset+len(seq)+1]=b"l"+bytes(seq)
        raw[0x2B6A77D:0x2B6A782]=b"aout\0"
        cls.synthetic=bytes(raw)
    def test_01_tagged_varint_24(self):
        self.assertEqual(mod.decode_uleb(b"\x18",0),(24,1))
    def test_02_tagged_varint_32(self):
        self.assertEqual(mod.decode_uleb(b"\x20",0),(32,1))
    def test_03_tagged_varint_10000(self):
        self.assertEqual(mod.decode_uleb(b"\x90N",0),(10000,2))
    def test_04_tagged_varint_65536(self):
        self.assertEqual(mod.decode_uleb(b"\x80\x80\x04",0),(65536,3))
    def test_05_tagged_varint_1000000(self):
        self.assertEqual(mod.decode_uleb(b"\xc0\x84=",0),(1000000,3))
    def test_06_reject_truncated_integer(self):
        with self.assertRaises(ValueError):mod.decode_uleb(b"\x80",0)
    def test_07_reject_overlong_integer(self):
        with self.assertRaises(ValueError):mod.decode_uleb(b"\x80"*11,0)
    def test_08_pinned_exact_boundary(self):
        self.assertTrue(mod.pinned_at(b"xxuTest\0zz",2,b"uTest\0"))
        self.assertFalse(mod.pinned_at(b"xxuTest\0zz",3,b"uTest\0"))
    def test_09_multi_occurrence_with_bounds(self):
        self.assertEqual(mod.occurrences(b"abcdabcdabcd",b"abcd",4,12),[4,8])
    def test_10_refuse_non_exe_short(self):
        with self.assertRaisesRegex(ValueError,"NOT_PINNED_TLM"):
            mod.audit_exe(b"small",enforce_hash=False)
    def test_11_pin_original_fingerprint_must_not_accept_synthetic(self):
        with self.assertRaisesRegex(ValueError,"HASH_MISMATCH"):
            mod.audit_exe(self.synthetic,enforce_hash=True)
    def test_12_bad_original_zip_must_not_open_random_payload(self):
        with self.assertRaises((ValueError,OSError)):
            mod.audit_zip(ROOT/"tests/test_s136.py")
    def test_13_mock_evidence_asserts_no_game_parity(self):
        report=mod.audit_exe(self.synthetic,enforce_hash=False)
        self.assertEqual(report["status"],"PASS_S136_OFFLINE_ORIGINAL_EMBEDDED_BAG_EVIDENCE_ONLY")
        self.assertFalse(report["authority"]["hash_pinned"])
        self.assertFalse(report["live_game_inventory_read"])
        self.assertFalse(report["game_or_auth_actions"])
        self.assertFalse(report["embedded_read_bag"]["live_return_shapes_verified"])
        self.assertFalse(report["embedded_get_bag"]["sort_and_aggregation_expression_verified"])
    def test_14_no_dictionary_offsets_claimed(self):
        report=mod.audit_exe(self.synthetic,enforce_hash=False)
        self.assertIn("Actual dictionary count offset and entries pointer",report["unknowns"])
        for item in report["adjacent_typed_numeric_literals"].values():
            self.assertEqual(item["association"],"ADJACENT_ONLY_NOT_FIELD_BINDING")
    def test_15_original_row_site_documented_not_assumed_symbol(self):
        self.assertIn("site",mod.READ_ROW_FIELDS)
        report=mod.audit_exe(self.synthetic,enforce_hash=False)
        self.assertEqual(report["embedded_read_bag"]["tuple_shape_documented"],"(rows, info)")
        self.assertIn("site",report["embedded_read_bag"]["row_fields_documented"])
    def test_16_tampered_literal_refused(self):
        changed=bytearray(self.synthetic)
        changed[mod.PINNED["read_bag_symbol"][0]]=ord("x")
        with self.assertRaisesRegex(ValueError,"ORIGINAL_BINARY_MARKER_CHANGED"):
            mod.audit_exe(bytes(changed),enforce_hash=False)
    def test_17_tampered_numeric_tag_refused(self):
        changed=bytearray(self.synthetic)
        changed[0x2B6A725]=ord("x")
        with self.assertRaisesRegex(ValueError,"UNEXPECTED_NEARBY_TAGGED_INT"):
            mod.audit_exe(bytes(changed),enforce_hash=False)
    def test_18_tool_selftest_without_zip(self):
        result=subprocess.run([sys.executable,str(ROOT/"tools/S136_AUDIT_ORIGINAL_BAG_CONSTANTS.py"),
                               "--self-test"],text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn("S136_SYNTHETIC_PARSER_SELFTEST=PASS",result.stdout)
    def test_19_tool_has_no_native_game_actions(self):
        src=(ROOT/"tools/S136_AUDIT_ORIGINAL_BAG_CONSTANTS.py").read_text(encoding="utf8")
        for danger in ("WriteProcessMemory(", "SendInput(", "RequestSellItem(",
                       "ReadProcessMemory(", "CreateRemoteThread(", "get_bag(\""):
            self.assertNotIn(danger,src)
    def test_20_source_ast_compiles(self):
        for relative in ("tools/S136_AUDIT_ORIGINAL_BAG_CONSTANTS.py","tests/test_s136.py"):
            p=ROOT/relative
            compile(ast.parse(p.read_text(encoding="utf8")),relative,"exec")

if __name__=="__main__": unittest.main()
