"""S139 read-only original O02 candidate game-build identity evidence tests.

Tests are NOT an actual game/client build or signed TLM Info authentication.
"""
from __future__ import annotations
import ast
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from dataclasses import FrozenInstanceError

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"tools"))
import unittest
from unittest import mock
from game_build_identity import (
    inspect_explicit_game_build,public_report,GameBuildIdentity,
    CandidateFileIdentity,EXPECTED_DLL,EXPECTED_METADATA,
)
from S28_TEST_PE_FIXTURE import write_test_pe
from S139_GAME_BUILD_FILE_AUDIT import main as cli


class S139OriginalBuildIdentityTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder=Path(self.tmp.name)
        self.dll=write_test_pe(self.folder/"GameAssembly.dll",dll=True)
        self.meta=self.folder/"global-metadata.dat"
        self.meta.write_bytes(b"S139_TEST_OWNED_METADATA_NOT_A_REAL_GAME")
    def identity(self,include_metadata=True):
        return inspect_explicit_game_build(self.dll,self.meta if include_metadata else None)
    def test_01_x64_pe_structure_and_hash(self):
        r=self.identity()
        self.assertEqual(r.status,"UNATTESTED_DLL_AND_METADATA_FINGERPRINTS_ONLY")
        self.assertTrue(r.dll_x64_pe_structure)
        self.assertEqual(r.candidate_dll.sha256,
                         hashlib.sha256(self.dll.read_bytes()).hexdigest())
    def test_02_real_metadata_hash(self):
        r=self.identity()
        self.assertEqual(r.candidate_metadata.sha256,
                         hashlib.sha256(self.meta.read_bytes()).hexdigest())
    def test_03_optional_metadata_still_unattested(self):
        r=self.identity(False)
        self.assertEqual(r.status,"UNATTESTED_X64_GAMEASSEMBLY_CANDIDATE_METADATA_NOT_SUPPLIED")
        self.assertIsNone(r.candidate_metadata)
    def test_04_no_authorization_from_valid_pe(self):
        r=self.identity()
        for field in ("is_authoritatively_known_game_build","signed_info_verified",
                      "game_process_attached","original_tlm_pointer_offsets_compatible",
                      "real_roledata_read","ready_for_game_actions"):
            self.assertIs(getattr(r,field),False)
    def test_05_reject_wrong_dll_basename(self):
        p=self.folder/"random.dll"
        p.write_bytes(self.dll.read_bytes())
        self.assertEqual(inspect_explicit_game_build(p).status,
                         "NOT_EXPLICIT_GAMEASSEMBLY_DLL")
    def test_06_reject_missing_dll(self):
        self.dll.unlink()
        self.assertEqual(inspect_explicit_game_build(self.dll).status,
                         "GAMEASSEMBLY_FILE_UNAVAILABLE")
    def test_07_reject_empty_dll(self):
        self.dll.write_bytes(b"")
        self.assertEqual(inspect_explicit_game_build(self.dll).status,
                         "CANDIDATE_FILES_UNREADABLE_OR_CHANGED")
    def test_08_reject_not_pe(self):
        self.dll.write_bytes(b"this is NOT a PE header")
        r=self.identity()
        self.assertTrue(r.status.startswith("CANDIDATE_DLL_NOT_VALID_X64_PE"))
        self.assertFalse(r.dll_x64_pe_structure)
    def test_09_reject_x86_module(self):
        write_test_pe(self.dll,dll=True,machine=0x14c)
        self.assertIn("NOT_AMD64",self.identity().status)
    def test_10_reject_exe_renamed_to_dll(self):
        write_test_pe(self.dll,dll=False)
        self.assertIn("PE_KIND_MISMATCH",self.identity().status)
    def test_11_reject_truncated_pe(self):
        write_test_pe(self.dll,dll=True,malformed="truncated")
        self.assertTrue(self.identity().status.startswith("CANDIDATE_DLL_NOT_VALID"))
    def test_12_case_insensitive_real_file_name(self):
        self.dll.rename(self.folder/"GAMEASSEMBLY.DLL")
        self.dll=self.folder/"GAMEASSEMBLY.DLL"
        self.assertEqual(self.identity().status,
                         "UNATTESTED_DLL_AND_METADATA_FINGERPRINTS_ONLY")
    def test_13_wrong_metadata_filename_refused(self):
        p=self.folder/"item.csv";p.write_bytes(b"fake")
        self.assertEqual(inspect_explicit_game_build(self.dll,p).status,
                         "METADATA_BASENAME_NOT_VERIFIED")
    def test_14_missing_metadata_refused(self):
        self.meta.unlink()
        self.assertEqual(self.identity().status,"METADATA_FILE_UNAVAILABLE")
    def test_15_empty_metadata_refused(self):
        self.meta.write_bytes(b"")
        self.assertEqual(self.identity().status,
                         "CANDIDATE_FILES_UNREADABLE_OR_CHANGED")
    def test_16_metadata_is_not_inferred_by_path(self):
        self.assertIsNone(self.identity(False).candidate_metadata)
    def test_17_original_candidate_paths_are_not_reported(self):
        result=public_report(self.identity())
        self.assertNotIn(str(self.folder),json.dumps(result))
        self.assertEqual(result["candidate_dll"]["name"],"gameassembly.dll")
    def test_18_no_tokens_or_local_settings_in_report(self):
        result=json.dumps(public_report(self.identity())).lower()
        for key in ("token", "authorization_granted", "appdata", "user_id",
                    "password","license_key"):
            self.assertNotIn(key,result)
    def test_19_different_metadata_changes_hash_not_build_status(self):
        original=self.identity()
        self.meta.write_bytes(b"DIFFERENT_STILL_TEST_ONLY")
        modified=self.identity()
        self.assertNotEqual(original.candidate_metadata.sha256,
                            modified.candidate_metadata.sha256)
        self.assertEqual(modified.status,original.status)
        self.assertFalse(modified.is_authoritatively_known_game_build)
    def test_20_different_dll_changes_hash_not_authorization(self):
        original=self.identity()
        data=bytearray(self.dll.read_bytes());data[-1]^=1;self.dll.write_bytes(data)
        new=self.identity()
        self.assertNotEqual(original.candidate_dll.sha256,new.candidate_dll.sha256)
        self.assertFalse(new.original_tlm_pointer_offsets_compatible)
    def test_21_frozen_outcome(self):
        r=self.identity()
        with self.assertRaises(FrozenInstanceError):
            r.signed_info_verified=True
    def test_22_public_report_rejects_fake_outcome(self):
        with self.assertRaises(TypeError):public_report({})
    def test_23_cli_valid_candidate_unverified_not_runtime(self):
        from contextlib import redirect_stdout
        import io
        buf=io.StringIO()
        with redirect_stdout(buf):
            code=cli(["--gameassembly",str(self.dll),"--metadata",str(self.meta)])
        doc=json.loads(buf.getvalue())
        self.assertEqual(code,0)
        self.assertEqual(doc["status"],"UNATTESTED_DLL_AND_METADATA_FINGERPRINTS_ONLY")
        self.assertFalse(doc["signed_info_verified"])
    def test_24_cli_missing_refused(self):
        from contextlib import redirect_stdout
        import io
        buf=io.StringIO()
        with redirect_stdout(buf):
            code=cli(["--gameassembly",str(self.folder/"absent"/"GameAssembly.dll")])
        self.assertEqual(code,2)
        self.assertIn("GAMEASSEMBLY_FILE_UNAVAILABLE",buf.getvalue())
    def test_25_source_cannot_load_game_or_talk_to_server(self):
        for name in ("src/game_build_identity.py","tools/S139_GAME_BUILD_FILE_AUDIT.py"):
            txt=(ROOT/name).read_text(encoding="utf8")
            for forbidden in ("OpenProcess(", "ReadProcessMemory(", "CreateRemoteThread(",
                              "WriteProcessMemory(", "requests.post(", "Game.GetItem",
                              "SendInput(", "subprocess.Popen(", "VerifyClaims(",
                              "TOKEN_PUBLIC_KEY"):
                self.assertNotIn(forbidden,txt)
    def test_26_unchanged_pe_inspector_reused(self):
        import game_build_identity
        self.assertIn("from login_launch_inputs import inspect_x64_pe",
                      (ROOT/"src/game_build_identity.py").read_text())
        self.assertTrue(callable(game_build_identity.inspect_x64_pe))
    def test_27_non_path_input_fail_closed(self):
        self.assertEqual(inspect_explicit_game_build(None).status,
                         "CANDIDATE_FILES_UNREADABLE_OR_CHANGED")
    def test_28_ast_parses(self):
        for p in ("src/game_build_identity.py","tools/S139_GAME_BUILD_FILE_AUDIT.py",
                  "tests/test_s139.py"):
            compile(ast.parse((ROOT/p).read_text(encoding="utf8")),p,"exec")


if __name__=="__main__":
    unittest.main()
