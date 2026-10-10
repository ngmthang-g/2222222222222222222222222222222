"""S114 comparison is scoped to original TLMTool.dist, not ZIP root or product."""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from S114_AUDIT_DIST import (
    ORIGINAL_PREFIX, DistAuditError, RESULT_STATUS, S113_DIAGNOSTIC_EXE,
    audit, digest, load_original, safe_relative, summarize,
)


class S114SameScopeTests(unittest.TestCase):
    @staticmethod
    def setup(td):
        home = Path(td)
        original = home / "ORIGINAL_MANIFEST.tsv"
        dist = home / "TLMTool.dist"
        dist.mkdir()
        common = b"python310 runtime"
        (dist / "python310.dll").write_bytes(common)
        (dist / S113_DIAGNOSTIC_EXE).write_bytes(b"distinct test diagnostic PE fixture")
        (dist / "new.dll").write_bytes(b"only in diagnostic")
        with original.open("w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, delimiter="\t", lineterminator="\n")
            w.writerow(("SHA256", "SIZE_BYTES", "CATEGORY", "PACKAGE_PATH"))
            w.writerow((hashlib.sha256(common).hexdigest(), len(common), "DLL",
                        ORIGINAL_PREFIX + "python310.dll"))
            w.writerow((hashlib.sha256(b"old library").hexdigest(), len(b"old library"),
                        "DLL", ORIGINAL_PREFIX + "old.dll"))
            w.writerow((hashlib.sha256(b"root launcher").hexdigest(), len(b"root launcher"),
                        "EXE", "TLMTool_2.1.2/TLMTool.exe"))
        return original, dist

    def test_01_original_inner_scope_excludes_root_launcher(self):
        with tempfile.TemporaryDirectory() as td:
            original, _ = self.setup(td)
            result = load_original(original, expected_sha=None, expected_rows=3)
            self.assertEqual(set(result), {"python310.dll", "old.dll"})

    def test_02_not_claiming_missing_source_when_diagnostic_does_not_contain_original(self):
        with tempfile.TemporaryDirectory() as td:
            original, dist = self.setup(td)
            report, rows = audit(original, dist, expected_manifest_sha=None,
                                 expected_orig_rows=3, expected_dist_count=3,
                                 expected_exe_sha=None)
            self.assertEqual(report["status"], RESULT_STATUS)
            self.assertEqual(report["original_inner_file_count"], 2)
            self.assertEqual(report["s113_diagnostic_file_count"], 3)
            self.assertEqual(report["paths_exact_sha256"], 1)
            self.assertEqual(report["paths_only_original"], 1)
            self.assertEqual(report["paths_only_s113_diagnostic"], 2)
            self.assertEqual(report["parity"], "UNVERIFIED_FULL_PRODUCT_BUILD_NOT_PRESENT")
            self.assertEqual({v["relative_path"]: v["status"] for v in rows}["old.dll"],
                             "NOT_IN_DIAGNOSTIC")

    def test_03_common_same_path_but_different_contents_is_not_exact(self):
        base = {"same.dll": {"sha256": "a" * 64, "size": 1, "category": "DLL"}}
        other = {"same.dll": {"sha256": "b" * 64, "size": 1, "category": ".dll"}}
        report, rows = summarize(base, other)
        self.assertEqual(report["paths_common"], 1)
        self.assertEqual(report["paths_exact_sha256"], 0)
        self.assertEqual(rows[0]["status"], "COMMON_DIFFERENT")

    def test_04_original_manifest_sha_is_required(self):
        with tempfile.TemporaryDirectory() as td:
            original, _ = self.setup(td)
            with self.assertRaisesRegex(DistAuditError, "SHA_MISMATCH"):
                load_original(original, expected_sha="0" * 64, expected_rows=3)

    def test_05_original_manifest_row_count_is_exact(self):
        with tempfile.TemporaryDirectory() as td:
            original, _ = self.setup(td)
            with self.assertRaisesRegex(DistAuditError, "ROW_COUNT"):
                load_original(original, expected_sha=None, expected_rows=1002)

    def test_06_guard_against_path_escape(self):
        for value in ("", "../secret", "/etc/passwd", "a/../b", "a\\b", "./a", "a//b"):
            with self.subTest(value=value):
                with self.assertRaises(DistAuditError):
                    safe_relative(value)

    def test_07_actual_manifest_root_scope_requires_prefix(self):
        with tempfile.TemporaryDirectory() as td:
            original, _ = self.setup(td)
            text = original.read_text(encoding="utf-8")
            original.write_text(text.replace("TLMTool_2.1.2/TLMTool.exe",
                                            "another-root/TLMTool.exe"), encoding="utf-8")
            with self.assertRaisesRegex(DistAuditError, "PACKAGE_PREFIX"):
                load_original(original, expected_sha=None, expected_rows=3)

    def test_08_fixture_count_mismatch_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            original, dist = self.setup(td)
            with self.assertRaisesRegex(DistAuditError, "COUNT_MISMATCH"):
                audit(original, dist, expected_manifest_sha=None,
                      expected_orig_rows=3, expected_dist_count=937, expected_exe_sha=None)

    def test_09_fixture_exe_digest_mismatch_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            original, dist = self.setup(td)
            with self.assertRaisesRegex(DistAuditError, "S113_EXE_SHA"):
                audit(original, dist, expected_manifest_sha=None,
                      expected_orig_rows=3, expected_dist_count=3,
                      expected_exe_sha="0" * 64)

    def test_10_diagnostic_filename_cannot_be_product_name(self):
        self.assertIn("NOT_PRODUCT", S113_DIAGNOSTIC_EXE)
        self.assertNotEqual(S113_DIAGNOSTIC_EXE, "TLMTool.exe")

    def test_11_original_manifest_is_never_written(self):
        with tempfile.TemporaryDirectory() as td:
            original, dist = self.setup(td)
            before = digest(original)
            audit(original, dist, expected_manifest_sha=None,
                  expected_orig_rows=3, expected_dist_count=3, expected_exe_sha=None)
            self.assertEqual(digest(original), before)

    def test_13_windows_crlf_checkout_requires_matching_canonical_lf_sha(self):
        with tempfile.TemporaryDirectory() as td:
            original, _ = self.setup(td)
            lf = original.read_bytes()
            self.assertNotIn(b"\r\n", lf)
            canonical_sha = hashlib.sha256(lf).hexdigest()
            original.write_bytes(lf.replace(b"\n", b"\r\n"))
            loaded = load_original(original, expected_sha=canonical_sha, expected_rows=3)
            self.assertIn("old.dll", loaded)
            # The canonical comparison did NOT modify the Windows checkout.
            self.assertIn(b"\r\n", original.read_bytes())

    def test_14_crlf_also_rejects_mutated_content_not_matching_pin(self):
        with tempfile.TemporaryDirectory() as td:
            original, _ = self.setup(td)
            lf = original.read_bytes()
            canonical_sha = hashlib.sha256(lf).hexdigest()
            original.write_bytes(lf.replace(b"\n", b"\r\n") + b"  ")
            with self.assertRaisesRegex(DistAuditError, "SHA_MISMATCH"):
                load_original(original, expected_sha=canonical_sha, expected_rows=3)

    def test_12_common_casefold_collision_invalid(self):
        with tempfile.TemporaryDirectory() as td:
            original, _ = self.setup(td)
            with original.open("a", encoding="utf-8") as fh:
                fh.write("0" * 64 + "\t1\tDLL\t" + ORIGINAL_PREFIX + "PYTHON310.DLL\n")
            with self.assertRaisesRegex(DistAuditError, "DUPLICATE"):
                load_original(original, expected_sha=None, expected_rows=4)


if __name__ == "__main__":
    unittest.main()
