"""S115 — inventory exactly 65 original-only A07 files from VERIFIED S114 artifact.

This is static metadata classification, NEVER executable reconciliation.
No missing resource is copied, loaded, injected, rewritten, or given a guessed
authorization role. Input is the A07 manifest + SHA-verified S114 *report*.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import sys

from S114_AUDIT_DIST import ORIGINAL_PREFIX, load_original

A07_SHA = "c906b837c1c804984f26a262ebc563300076981e4008ce36b0c768a18513f4ee"
CATEGORIES = {
    "ORIGINAL_COMPILED_APPLICATION": ("TLMTool.exe",),
    "BOOTSTRAP_UPDATER_ARCHIVE_TOOLS": (
        "bootstrap.exe", "update.exe", "tools/7z.exe", "tools/7z.dll",
    ),
    "ACTIVE_GAME_AND_VERSION_PAYLOADS": ("data/resources.dat", "version.dat"),
    "ARCHIVED_INJECTION_PAYLOAD_VARIANTS": (
        "data/resources.dat.bak-20260923", "data/resources.dat.old",
        "data/resources.dat.old-locked", "data/resources.old2.dat",
        "data/resources.old3.dat",
    ),
    "OPAQUE_PE_LIKE_DATA_ROLE_UNKNOWN": (
        "data/accounts.dat", "data/app_state.dat", "data/auth_token.dat",
        "data/cache.dat", "data/config.dat", "data/license.dat",
        "data/logs.dat", "data/manifest.dat", "data/package.dat",
        "data/sec_key.dat", "data/session.dat", "data/settings.dat",
        "data/signature.dat", "data/user_profile.dat",
    ),
    "HISTORICAL_RUNTIME_LOG_NOT_APP_SOURCE": ("data/automove_log.txt",),
    "PROXY_NETWORK_RUNTIME_EXCLUDED": (
        "forwarder.exe", "ppx/Default.ppx", "ppx/ProxifierSetup.exe",
        "proxy_working.txt",
    ),
    "EMULATOR_FRIDA_HELPER_DEPENDENCIES": (
        "emu_client.js", "ld_remote.js", "frida/_frida.pyd",
    ),
    "ORIGINAL_PRESENTATION_ASSETS": ("icon.ico", "splash.png"),
    "THIRD_PARTY_CRYPTO_IMAGE_MONITOR_DEPS": (
        "PIL/_avif.pyd", "PIL/_imaging.pyd", "PIL/_imagingcms.pyd",
        "PIL/_imagingft.pyd", "PIL/_imagingmath.pyd", "PIL/_imagingtk.pyd",
        "PIL/_webp.pyd", "_brotli.pyd", "_cffi_backend.pyd",
        "cryptography/hazmat/bindings/_rust.pyd", "psutil/_psutil_windows.pyd",
        "certifi/cacert.pem", "libssl-1_1.dll",
    ),
    "PYTHON_WIN32_NATIVE_SUPPORT": (
        "_asyncio.pyd", "_multiprocessing.pyd", "_overlapped.pyd",
        "_queue.pyd", "_socket.pyd", "_ssl.pyd", "_uuid.pyd", "pyexpat.pyd",
        "python3.dll", "pythoncom310.dll", "pywintypes310.dll",
        "vcruntime140_1.dll", "win32api.pyd", "win32gui.pyd",
        "win32process.pyd", "win32ui.pyd",
    ),
}
# Observed usage contracts, NOT conclusions of runtime readiness.
EVIDENCE = {
    "ORIGINAL_COMPILED_APPLICATION": "A04/D01/S87: compiled source and Info auth missing; hard blocker",
    "BOOTSTRAP_UPDATER_ARCHIVE_TOOLS": "A05/A06/D07: launcher/updater archive helpers; lifecycle parity pending",
    "ACTIVE_GAME_AND_VERSION_PAYLOADS": "D06/F05/C19: active injection+version proxy, original binary-only; no execution",
    "ARCHIVED_INJECTION_PAYLOAD_VARIANTS": "D06: old/backup payloads; not proven active, never copy",
    "OPAQUE_PE_LIKE_DATA_ROLE_UNKNOWN": "D06: 14 PE-like invalid packages; semantic meaning UNKNOWN",
    "HISTORICAL_RUNTIME_LOG_NOT_APP_SOURCE": "H15/D06: historic automove evidence; not a runnable dependency",
    "PROXY_NETWORK_RUNTIME_EXCLUDED": "F08/Q: forbidden Proxy development by user scope lock",
    "EMULATOR_FRIDA_HELPER_DEPENDENCIES": "D07/P: emulator/Frida optional and live provenance unknown",
    "ORIGINAL_PRESENTATION_ASSETS": "B01/B14/E02: assets; no evidence of complete UI parity",
    "THIRD_PARTY_CRYPTO_IMAGE_MONITOR_DEPS": "D03: dependencies, availability not feature implementation",
    "PYTHON_WIN32_NATIVE_SUPPORT": "A04/D03: CPython/Win32 native dependencies; not TLM source",
}
STATUS = "PASS_S115_CLASSIFIED_65_ORIGINAL_ONLY_METADATA_NO_PRODUCT"

class S115Error(ValueError):
    pass


def classification_map() -> dict[str, str]:
    flat = {}
    for category, paths in CATEGORIES.items():
        for p in paths:
            if p in flat:
                raise S115Error("DUPLICATE_CLASSIFICATION_PATH")
            flat[p] = category
    if len(flat) != 65:
        raise S115Error("CLASSIFICATION_IS_NOT_65")
    return flat


def _as_int(raw: str, reason: str) -> int:
    try:
        result = int(raw)
    except (TypeError, ValueError):
        raise S115Error(reason) from None
    if result < 0:
        raise S115Error(reason)
    return result


def classify(rows: list[dict], original: dict[str, dict]) -> tuple[dict, list[dict]]:
    table = classification_map()
    if len(rows) != 1002:
        raise S115Error("S114_REPORT_NOT_1002_PATHS")
    allowed = {"COMMON_EXACT", "COMMON_DIFFERENT", "NOT_IN_DIAGNOSTIC", "DIAGNOSTIC_ONLY"}
    counts = Counter()
    missing = {}
    for row in rows:
        path, stat = row.get("relative_path", ""), row.get("status", "")
        if stat not in allowed:
            raise S115Error("UNEXPECTED_S114_ROW_STATUS")
        counts[stat] += 1
        if stat != "NOT_IN_DIAGNOSTIC":
            continue
        if path in missing:
            raise S115Error("S114_DUPLICATE_ORIGINAL_ONLY")
        ref = original.get(path)
        if ref is None:
            raise S115Error("S114_PATH_NOT_IN_ORIGINAL_A07")
        if (row["original_sha256"].lower() != ref["sha256"]
                or _as_int(row["original_bytes"], "S114_SIZE_INVALID") != ref["size"]):
            raise S115Error("S114_MISMATCH_WITH_AUTHENTIC_A07_METADATA")
        missing[path] = (row, ref)
    if (counts != {"COMMON_EXACT": 936, "NOT_IN_DIAGNOSTIC": 65,
                   "DIAGNOSTIC_ONLY": 1}):
        raise S115Error("S114_REPORT_COUNTS_NOT_VERIFIED")
    if set(missing) != set(table):
        raise S115Error("S115_UNCLASSIFIED_OR_UNKNOWN_ORIGINAL_PATH")
    grouped = defaultdict(lambda: {"files": 0, "bytes": 0})
    details = []
    for path in sorted(missing):
        row, meta = missing[path]
        cat = table[path]
        grouped[cat]["files"] += 1
        grouped[cat]["bytes"] += meta["size"]
        details.append({
            "relative_path": path,
            "group": cat,
            "original_a07_category": meta["category"],
            "original_size_bytes": meta["size"],
            "original_sha256": meta["sha256"],
            "evidence_boundary": EVIDENCE[cat],
            "status": "NOT_IN_MINIMAL_S113_DIAGNOSTIC_NOT_PROOF_OF_MISSING_SOURCE",
        })
    summary = {
        "task": "S115", "status": STATUS, "input": "verified S114 11678242351",
        "original_inner_count": 1001, "s113_diagnostic_count": 937,
        "same_hash_paths": 936, "original_only_count": len(details),
        "original_only_total_size_bytes": sum(x["original_size_bytes"] for x in details),
        "not_product": True, "signed_info_available": False,
        "real_game_action_executed": False, "copied_original_payloads": 0,
        "source_completion_claim": False,
        "groups": {k: {"file_count": grouped[k]["files"], "total_bytes": grouped[k]["bytes"],
                       "original_evidence": EVIDENCE[k]}
                   for k in CATEGORIES},
        "blockers": [
            "S87: legitimate signed Info issuer/public key/token schema and heartbeat unavailable",
            "F05: original compiled game suspended-create/inject and resources.dat activation not rebuilt",
            "F06: actual game login HWND proof/credential action unverified",
            "E03/PLAN: nine full product tab builders and 1:1 visual/game runtime parity absent",
            "F08/Q: Proxy runtime explicitly outside user scope; must not develop",
            "F02: account checkbox serialization token and legacy captcha mapping UNKNOWN",
        ],
        "next_action": "S116: choose original-backed complete action only with genuine auth/input evidence; do not invent implementation",
    }
    return summary, details


def verify_and_write(manifest: Path, s114_tsv: Path, dest: Path) -> dict:
    original = load_original(manifest, expected_sha=A07_SHA, expected_rows=1002)
    with s114_tsv.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        needed = {"status", "relative_path", "original_sha256", "original_bytes"}
        if not needed.issubset(reader.fieldnames or ()):
            raise S115Error("S114_INPUT_SCHEMA_INVALID")
        rows = list(reader)
    summary, details = classify(rows, original)
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "s115_classification_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (dest / "s115_original_only_65.tsv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, delimiter="\t", fieldnames=list(details[0]))
        writer.writeheader()
        writer.writerows(details)
    return summary


def main() -> int:
    if len(sys.argv) != 4:
        print("Usage: S115_CLASSIFY_ORIGINAL_ONLY.py <A07.tsv> <s114_paths.tsv> <out>", file=sys.stderr)
        return 2
    try:
        report = verify_and_write(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
        print("S115_STATUS=" + report["status"])
        print("S115_ORIGINAL_ONLY_COUNT=" + str(report["original_only_count"]))
        print("S115_ORIGINAL_ONLY_BYTES=" + str(report["original_only_total_size_bytes"]))
        for group, s in report["groups"].items():
            print("S115_GROUP=" + group + ":" + str(s["file_count"]))
        print("S115_PRODUCT=EXPLICITLY_NOT_BUILT")
        return 0
    except (OSError, ValueError) as exc:
        print("S115_FAILED=" + str(exc if isinstance(exc, S115Error) else type(exc).__name__), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
