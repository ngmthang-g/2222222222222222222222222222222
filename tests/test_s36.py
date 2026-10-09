"""S36 diagnostics packaging verifier unit checks; no build here."""
from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from S36_VERIFY_STANDALONE import (
    DIAGNOSTIC_NAME, GUARD_SENTENCE, assess_blocked_run,
    inspect_diagnostic_path, run_diagnostic,
)


class S36Tests(unittest.TestCase):
    def test_normal_refusal_exit_2_in_stderr_is_not_auth_grant(self):
        self.assertEqual(
            assess_blocked_run(2,"","S01 BLOCKED: "+GUARD_SENTENCE),
            "EXPLICITLY_BLOCKED_NO_GUI")

    def test_success_exit_0_is_explicit_failure(self):
        self.assertEqual(
            assess_blocked_run(0,"","S01 BLOCKED: "+GUARD_SENTENCE),
            "NOT_FAIL_CLOSED_EXIT_2")

    def test_any_non_2_exit_code_is_a_failure(self):
        for code in (-9,1,3,126):
            self.assertEqual(
                assess_blocked_run(code,"","S01 BLOCKED: "+GUARD_SENTENCE),
                "NOT_FAIL_CLOSED_EXIT_2")

    def test_missing_refusal_or_unrelated_error_is_not_success(self):
        for msg in ("", "Traceback: missing import", "WARNING: no license",
                    GUARD_SENTENCE, "S01 BLOCKED:"):
            self.assertEqual(
                assess_blocked_run(2,"",msg),
                "MISSING_EXPLICIT_AUTH_REFUSAL")

    def test_guard_on_stdout_only_is_not_success(self):
        self.assertEqual(
            assess_blocked_run(2,"S01 BLOCKED: "+GUARD_SENTENCE,""),
            "MISSING_EXPLICIT_AUTH_REFUSAL")

    def test_guard_repeated_on_stdout_is_detected(self):
        self.assertEqual(
            assess_blocked_run(2,GUARD_SENTENCE,
                               "S01 BLOCKED: "+GUARD_SENTENCE),
            "GUARD_NOT_ON_STDERR")

    def test_bad_result_types_fail(self):
        for code,out,err in ((True,"",""),(2,None,""),(2,"",None)):
            self.assertEqual(assess_blocked_run(code,out,err),
                             "MALFORMED_PROCESS_RESULT")

    def test_diagnostic_executable_has_unmistakable_non_product_name(self):
        self.assertIn("NOT_PRODUCT",DIAGNOSTIC_NAME)
        self.assertNotEqual(DIAGNOSTIC_NAME,"TLMTool")
        self.assertNotIn("2.1.2_REBUILT",DIAGNOSTIC_NAME)

    def test_missing_binary_is_not_reported_as_built(self):
        with tempfile.TemporaryDirectory() as td:
            exe,why=inspect_diagnostic_path(td)
            self.assertIsNone(exe)
            self.assertEqual(why,"DIAGNOSTIC_EXE_MISSING")

    def test_fake_named_exe_bytes_are_not_accepted_as_real_pe(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/DIAGNOSTIC_NAME
            p.mkdir()
            (p/(DIAGNOSTIC_NAME+".exe")).write_bytes(b"S36 FAKE EXE")
            exe,why=inspect_diagnostic_path(td)
            self.assertIsNone(exe)
            self.assertTrue(why.startswith("DIAGNOSTIC_PE_INVALID_"))

    def test_nonexistent_subprocess_reports_not_run_not_a_pass(self):
        with tempfile.TemporaryDirectory() as td:
            result=run_diagnostic(Path(td)/"does-not-exist.exe")
            self.assertNotEqual(result["status"],"EXPLICITLY_BLOCKED_NO_GUI")
            self.assertIsNone(result["returncode"])


if __name__=="__main__":
    unittest.main()
