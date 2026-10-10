"""S86 proof-oriented audit of ALL current source files and unbuilt tabs."""
from __future__ import annotations
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from S86_AUDIT_SOURCE_BUILD_GAPS import (
    audit_registration, build_report, collect_syntax, verify_product_bootstrap)

class S86SourceBuildAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.structure = collect_syntax(ROOT)
        cls.registration = audit_registration(ROOT)

    def test_01_all_source_and_test_python_compiles_from_actual_repo(self):
        self.assertEqual(self.structure["syntax_failures"], [])
        self.assertGreaterEqual(self.structure["source_modules"], 45)
        self.assertGreaterEqual(self.structure["test_modules"], 80)
        self.assertGreaterEqual(self.structure["tool_modules"], 80)

    def test_02_manifest_digest_repeatable_read_only(self):
        digest = self.structure["compiled_sources_digest"]
        self.assertEqual(len(digest), 64)
        self.assertEqual(digest, collect_syntax(ROOT)["compiled_sources_digest"])

    def test_03_recovered_shell_slots_all_known_and_unique(self):
        keys = self.registration["original_potential_tab_slots"]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertIn("start_tab", keys)
        self.assertIn("login_tab", keys)
        self.assertIn("phoban_tab", keys)
        self.assertIn("donvang_tab", keys)

    def test_04_registered_tabs_are_exact_partial_Start_Login_external_Info(self):
        self.assertEqual(set(self.registration["registered_partial_or_external_tabs"]),
                         {"info_tab", "start_tab", "login_tab"})
        self.assertTrue(self.registration["external_real_Info_factory_required"])

    def test_05_major_absent_tab_builders_must_be_explicitly_reported(self):
        missing = self.registration["no_registered_builder_for"]
        for tab in ("phoban_tab", "daily_tab", "farm_tab", "trainlsv_tab",
                    "donvang_tab", "rao_tab", "toiuu_tab", "party_tab"):
            self.assertIn(tab, missing)

    def test_06_production_main_still_refuses_unverified_Info(self):
        output = verify_product_bootstrap(ROOT)
        self.assertEqual(output["status"], "EXPLICITLY_BLOCKED_NO_GUI")
        self.assertEqual(output["returncode"], 2)

    def test_07_invalid_python_source_detected_without_running(self):
        with tempfile.TemporaryDirectory(prefix="s86_audit_") as td:
            root = Path(td)
            path = root / "src" / "broken.py"
            path.parent.mkdir()
            path.write_text("def x(:\n    pass\n", encoding="utf-8")
            scan = collect_syntax(root)
            self.assertEqual(len(scan["syntax_failures"]), 1)
            self.assertEqual(scan["syntax_failures"][0]["path"], "src/broken.py")
            self.assertEqual(scan["syntax_failures"][0]["type"], "SyntaxError")

    def test_08_bad_utf8_source_cannot_be_silently_skipped(self):
        with tempfile.TemporaryDirectory(prefix="s86_audit_") as td:
            root = Path(td)
            path = root / "src" / "broken.py"
            path.parent.mkdir()
            path.write_bytes(b"\xff\xfe")
            scan = collect_syntax(root)
            self.assertEqual(scan["syntax_failures"][0]["type"], "UnicodeDecodeError")

    def test_09_real_report_never_reports_finished_product(self):
        report = build_report(ROOT)
        self.assertEqual(report["status"], "PASS_SOURCE_AUDIT_PRODUCT_STILL_BLOCKED")
        self.assertEqual(report["product_exe"], "NOT_BUILT_NOT_WORKING")
        self.assertEqual(report["S36_windows_exe"], "CI_SEPARATELY_VERIFIED_DIAGNOSTIC_NOT_PRODUCT")
        self.assertEqual(report["true_game_native_runtime"], "NOT_EXECUTED")
        self.assertTrue(report["no_original_proxy_development"])

if __name__ == "__main__":
    unittest.main()
