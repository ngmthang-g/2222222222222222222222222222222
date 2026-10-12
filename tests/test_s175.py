"""S175 real read-only HWND/PID readiness evidence; no game automation.

Fixtures prove old S08 game-window candidate rules and S139 build identity
are reused, never promoted into original game-control authorization.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import S175_GAME_READINESS_PROBE as probe


class FakeBackend:
    def __init__(self):
        self.windows=[42]
        self.valid=True
        self.visible=True
        self.pid=1234
        self.exe=r"C:\Games\Thần Long Mobile.exe"
        self.title="Thần Long  Mobile"
        self.cls="UnityWndClass"
        self.reused_pid=None

    def enumerate_top_level(self):return tuple(self.windows)
    def is_window(self,hwnd):return self.valid
    def is_visible(self,hwnd):return self.visible
    def process_id(self,hwnd):
        return self.pid if self.reused_pid is None else self.reused_pid
    def process_executable(self,pid):return self.exe
    def window_class(self,hwnd):return self.cls
    def title_with_timeout(self,hwnd,timeout):return self.title


class S175ReadinessProbeTests(unittest.TestCase):
    def setUp(self):
        self.backend=FakeBackend()

    def test_01_zero_windows_is_not_any_game_ready(self):
        self.backend.windows=[]
        s=probe.scan_and_report(self.backend)
        self.assertEqual(s["scan_status"],"WINDOW_SCAN_COMPLETED")
        self.assertEqual(s["verified_candidate_count"],0)
        self.assertFalse(s["game_action_ready"])
        self.assertFalse(any(s["capabilities"].values()))

    def test_02_candidate_exact_hwnd_pid_but_no_character_identity(self):
        s=probe.scan_and_report(self.backend)
        self.assertEqual(s["verified_candidate_count"],1)
        self.assertEqual(s["windows"],[{"hwnd":42,"pid":1234}])
        self.assertFalse(s["game_action_ready"])
        self.assertNotIn("RoleName",str(s["windows"]))

    def test_03_unrelated_executable_not_game(self):
        self.backend.exe=r"C:\Python\python.exe"
        s=probe.scan_and_report(self.backend)
        self.assertEqual(s["verified_candidate_count"],0)

    def test_04_title_only_without_exe_fails_closed(self):
        self.backend.exe="FakeGame.exe"
        self.backend.title="Thần Long  Mobile"
        self.assertEqual(probe.scan_and_report(self.backend)["verified_candidate_count"],0)

    def test_05_reject_hidden_and_closed(self):
        self.backend.visible=False
        self.assertFalse(probe.scan_and_report(self.backend)["windows"])
        self.backend.visible=True
        self.backend.valid=False
        self.assertFalse(probe.scan_and_report(self.backend)["windows"])

    def test_06_reject_class_and_title_mismatch(self):
        self.backend.cls="FakeClass"
        self.backend.title="FakeName"
        self.assertEqual(probe.scan_and_report(self.backend)["verified_candidate_count"],0)

    def test_07_uncertain_scanner_errors_do_not_claim_zero(self):
        class Broken:
            def enumerate_top_level(self):
                raise RuntimeError("test")
        s=probe.scan_and_report(Broken())
        self.assertEqual(s["scan_status"],"WINDOW_SCAN_FAILED_RUNTIMEERROR")
        self.assertIsNone(s["verified_candidate_count"])
        self.assertFalse(s["game_action_ready"])

    def test_08_no_folder_path_or_account_username_exposed(self):
        self.backend.exe=r"C:\Secret Users\Private\Thần Long Mobile.exe"
        s=probe.scan_and_report(self.backend)
        encoded=json.dumps(s,ensure_ascii=False)
        self.assertNotIn("C:\\Secret Users",encoded)
        # Generic privacy advice may mention passwords/tokens, but no
        # *actual* private account values are serialized.
        self.assertNotIn("REAL_PRIVATE_ACCOUNT_NAME",encoded)
        self.assertNotIn("REAL_PASSWORD_VALUE",encoded)
        self.assertNotIn("REAL_LICENSE_TOKEN",encoded)

    def test_09_false_game_actions_even_with_valid_game_candidate(self):
        s=probe.scan_and_report(self.backend)
        self.assertEqual(s["verified_candidate_count"],1)
        for key in ("real_role_name_reader","real_map_id_reader",
                    "runtime_game_input_transport","runtime_train_actions",
                    "runtime_login_actions","runtime_lsv_actions"):
            self.assertIs(s["capabilities"][key],False)

    def test_10_metadata_cannot_be_supplied_without_dll(self):
        with self.assertRaisesRegex(ValueError,"METADATA_REQUIRES"):
            probe.scan_and_report(self.backend,metadata="global-metadata.dat")

    def test_11_optional_invalid_build_file_never_authorizes_offsets(self):
        with tempfile.TemporaryDirectory(prefix="S175_") as td:
            p=Path(td)/"GameAssembly.dll"
            p.write_bytes(b"NOT_A_REAL_GAME_DLL")
            s=probe.scan_and_report(self.backend,gameassembly=p)
            g=s["game_build"]
            self.assertTrue(g["status"].startswith("CANDIDATE_DLL_NOT_VALID_"))
            self.assertFalse(g["ready_for_game_actions"])
            self.assertFalse(g["real_roledata_read"])
            self.assertNotIn(td,json.dumps(s,ensure_ascii=False))

    def test_12_build_no_file_does_not_claim_game_ready(self):
        s=probe.scan_and_report(self.backend,gameassembly="missing/GameAssembly.dll")
        self.assertEqual(s["game_build"]["status"],"GAMEASSEMBLY_FILE_UNAVAILABLE")
        self.assertFalse(s["game_build"]["ready_for_game_actions"])

    def test_13_metadata_filename_must_match_when_dll_is_valid_not_faked(self):
        self.assertEqual(probe.FORMAT_VERSION,"S175_READ_ONLY_V1")
        self.assertEqual(probe.MAX_REPORTED_WINDOWS,64)

    def test_14_existing_report_is_not_overwritten(self):
        with tempfile.TemporaryDirectory(prefix="S175_OUTPUT_") as td:
            out=Path(td)/"probe.json"
            out.write_text("NEVER_OVERWRITE",encoding="utf-8")
            result=probe.main(["--output",str(out)])
            self.assertEqual(result,3)
            self.assertEqual(out.read_text(encoding="utf-8"),"NEVER_OVERWRITE")

    def test_15_helper_api_has_no_input_game_transport(self):
        src=(ROOT/"tools"/"S175_GAME_READINESS_PROBE.py").read_text(encoding="utf-8")
        for forbidden in ("ReadProcessMemory(", "VirtualAllocEx(", "WriteProcessMemory(",
                          "SendInput(", "PostMessage(", "CreateRemoteThread(",
                          "PermissionGuard(", "read_role_name(", "RequestSellItem("):
            self.assertNotIn(forbidden,src)
        self.assertIn("discover_game_windows(backend)",src)

    def test_16_no_windows_supported_only_with_real_native_adapter(self):
        if sys.platform!="win32":
            s=probe.run_native()
            self.assertEqual(s["scan_status"],"REQUIRES_WINDOWS")
            self.assertFalse(s["game_action_ready"])

if __name__=="__main__":
    unittest.main()
