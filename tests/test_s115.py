"""S115 immutable original-only file classification; no binary reads/actions."""
from __future__ import annotations

import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from S115_CLASSIFY_ORIGINAL_ONLY import (
    CATEGORIES, EVIDENCE, S115Error, STATUS, classification_map, classify,
)


class S115OriginalOnlyTest(unittest.TestCase):
    @staticmethod
    def fixture():
        paths = classification_map()
        original = {}
        rows = []
        for i, path in enumerate(sorted(paths)):
            sha = f"{i+100:064x}"
            original[path] = {"sha256": sha, "size": i + 1, "category": "TEST_ONLY"}
            rows.append({"relative_path": path, "status": "NOT_IN_DIAGNOSTIC",
                         "original_sha256": sha, "original_bytes": str(i + 1)})
        for i in range(936):
            rows.append({"relative_path": f"common{i:04}.tcl", "status": "COMMON_EXACT",
                         "original_sha256": "", "original_bytes": ""})
        rows.append({"relative_path": "S113_NUITKA_DIAGNOSTIC_NOT_PRODUCT.exe",
                     "status": "DIAGNOSTIC_ONLY", "original_sha256": "",
                     "original_bytes": ""})
        return rows, original

    def test_01_exactly_65_paths_no_overlap(self):
        index = classification_map()
        self.assertEqual(len(index), 65)
        self.assertEqual(sum(map(len, CATEGORIES.values())), 65)

    def test_02_full_s114_count_match_and_no_product_claim(self):
        rows, original = self.fixture()
        report, details = classify(rows, original)
        self.assertEqual(report["status"], STATUS)
        self.assertEqual(report["original_only_count"], 65)
        self.assertEqual(len(details), 65)
        self.assertFalse(report["source_completion_claim"])
        self.assertTrue(report["not_product"])
        self.assertFalse(report["signed_info_available"])
        self.assertFalse(report["real_game_action_executed"])

    def test_03_misleading_auth_filenames_are_opaque(self):
        m = classification_map()
        for file in ("data/auth_token.dat", "data/license.dat", "data/sec_key.dat",
                     "data/accounts.dat", "data/signature.dat"):
            self.assertEqual(m[file], "OPAQUE_PE_LIKE_DATA_ROLE_UNKNOWN")

    def test_04_actual_injection_payload_is_separate_from_backups(self):
        m = classification_map()
        self.assertEqual(m["data/resources.dat"], "ACTIVE_GAME_AND_VERSION_PAYLOADS")
        self.assertEqual(m["data/resources.dat.old"], "ARCHIVED_INJECTION_PAYLOAD_VARIANTS")
        self.assertEqual(m["version.dat"], "ACTIVE_GAME_AND_VERSION_PAYLOADS")

    def test_05_no_proxy_runtime_development(self):
        m = classification_map()
        self.assertEqual(m["forwarder.exe"], "PROXY_NETWORK_RUNTIME_EXCLUDED")
        self.assertEqual(m["ppx/Default.ppx"], "PROXY_NETWORK_RUNTIME_EXCLUDED")
        self.assertIn("F08/Q", EVIDENCE["PROXY_NETWORK_RUNTIME_EXCLUDED"])

    def test_06_no_match_for_original_compiled_core_in_diagnostic(self):
        rows, original = self.fixture()
        _, details = classify(rows, original)
        m = {d["relative_path"]: d for d in details}
        self.assertEqual(m["TLMTool.exe"]["group"], "ORIGINAL_COMPILED_APPLICATION")
        self.assertIn("NOT_PROOF_OF_MISSING_SOURCE", m["TLMTool.exe"]["status"])

    def test_07_mutated_original_sha_refused(self):
        rows, original = self.fixture()
        rows[0]["original_sha256"] = "0" * 64
        with self.assertRaisesRegex(S115Error, "MISMATCH_WITH_AUTHENTIC"):
            classify(rows, original)

    def test_08_mutated_original_size_refused(self):
        rows, original = self.fixture()
        rows[0]["original_bytes"] = "999999"
        with self.assertRaisesRegex(S115Error, "MISMATCH_WITH_AUTHENTIC"):
            classify(rows, original)

    def test_09_missing_one_original_file_refused(self):
        rows, original = self.fixture()
        rows[0]["status"] = "COMMON_EXACT"
        with self.assertRaisesRegex(S115Error, "COUNTS_NOT_VERIFIED"):
            classify(rows, original)

    def test_10_unrecognized_path_rejected(self):
        rows, original = self.fixture()
        old = rows[0]["relative_path"]
        rows[0]["relative_path"] = "TLMTool_original_missing_game.py"
        original["TLMTool_original_missing_game.py"] = original.pop(old)
        with self.assertRaisesRegex(S115Error, "UNCLASSIFIED"):
            classify(rows, original)

    def test_11_duplicate_s114_row_rejected(self):
        rows, original = self.fixture()
        rows[1] = copy.deepcopy(rows[0])
        with self.assertRaisesRegex(S115Error, "DUPLICATE"):
            classify(rows, original)

    def test_12_original_metadata_no_mutation(self):
        rows, original = self.fixture()
        cloned = copy.deepcopy(original)
        classify(rows, original)
        self.assertEqual(original, cloned)

    def test_13_group_bytes_sum_to_original_only_bytes(self):
        rows, original = self.fixture()
        report, details = classify(rows, original)
        self.assertEqual(sum(v["total_bytes"] for v in report["groups"].values()),
                         sum(d["original_size_bytes"] for d in details))
        self.assertEqual(sum(v["file_count"] for v in report["groups"].values()), 65)

    def test_14_a07_other_file_not_mistaken_for_opaque_accounts(self):
        m = classification_map()
        self.assertNotIn("settings.ini", m)
        self.assertEqual(m["data/accounts.dat"], "OPAQUE_PE_LIKE_DATA_ROLE_UNKNOWN")

    def test_15_third_party_frida_remains_emulator_not_game_launcher(self):
        self.assertEqual(classification_map()["frida/_frida.pyd"],
                         "EMULATOR_FRIDA_HELPER_DEPENDENCIES")

    def test_16_reject_malformed_status(self):
        rows, original = self.fixture()
        rows[0]["status"] = "UNSAFE_SUCCESS"
        with self.assertRaisesRegex(S115Error, "UNEXPECTED_S114_ROW_STATUS"):
            classify(rows, original)


if __name__ == "__main__":
    unittest.main()
