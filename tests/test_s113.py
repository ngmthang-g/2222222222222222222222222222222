"""S113 diagnostic Nuitka folder verifier: safe negative cases, no real TLM EXE."""
from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from S113_VERIFY_NUITKA_DIAGNOSTIC import (
    BINARY, FOLDER, REQUIRED_GUARD, diagnose_structure, run_from_unrelated_cwd,
)


class S113NuitkaGuardTests(unittest.TestCase):
    def test_01_only_explicit_not_product_exe_name(self):
        self.assertIn("NOT_PRODUCT", BINARY)
        self.assertNotEqual(BINARY, "TLMTool.exe")
        self.assertEqual(FOLDER, "TLMTool.dist")

    def test_02_missing_folder_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / FOLDER
            self.assertEqual(diagnose_structure(path)[1], "DIAGNOSTIC_BINARY_MISSING")

    def test_03_refuse_directory_without_correct_name(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "a-different-dist"
            self.assertEqual(diagnose_structure(path)[1], "NOT_EXPECTED_NUITKA_DIST_FOLDER")

    def test_04_no_python_runtime_must_refuse_before_pe(self):
        with tempfile.TemporaryDirectory() as td:
            dist = Path(td) / FOLDER
            dist.mkdir()
            (dist / BINARY).write_bytes(b"no real PE here")
            self.assertEqual(diagnose_structure(dist)[1], "CPYTHON_310_RUNTIME_MISSING")

    def test_05_forbidden_product_name_must_refuse(self):
        with tempfile.TemporaryDirectory() as td:
            dist = Path(td) / FOLDER
            dist.mkdir()
            (dist / BINARY).write_bytes(b"x")
            (dist / "TLMTool.exe").write_bytes(b"x")
            self.assertEqual(diagnose_structure(dist)[1], "FORBIDDEN_PRODUCT_FILENAME")

    def test_06_original_gate_is_exact(self):
        self.assertEqual(REQUIRED_GUARD,
                         "S01 BLOCKED: genuine InfoTab/server authorization has not been reconstructed; no GUI started.")

    def test_07_cannot_run_nonexistent_diagnostic(self):
        with tempfile.TemporaryDirectory() as td:
            record = run_from_unrelated_cwd(Path(td) / "no.exe")
            self.assertEqual(record["status"], "NATIVE_EXE_LOAD_FAILURE")


if __name__ == "__main__":
    unittest.main()
