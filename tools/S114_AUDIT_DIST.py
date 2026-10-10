"""S114: same-scope A07 frozen original vs S113 actual Nuitka diagnostic manifest.

Read-only comparison; a diagnostic-only absence is NOT missing TLM source proof.
This tool must not copy/download original binaries, edit the frozen manifest,
or interpret a product capability from matching runtime filenames.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import sys
from collections import Counter

ORIGINAL_PREFIX = "TLMTool_2.1.2/TLMTool.dist/"
ORIGINAL_MANIFEST_SHA256 = "c906b837c1c804984f26a262ebc563300076981e4008ce36b0c768a18513f4ee"
ORIGINAL_ALL_ROWS = 1002
S113_DIAGNOSTIC_EXE = "S113_NUITKA_DIAGNOSTIC_NOT_PRODUCT.exe"
S113_DIAGNOSTIC_EXE_SHA256 = "fd0ed86b32e9cf9b8873aaeca6a0ed013c90f5be94759952723951a6cce108fd"
S113_DIAGNOSTIC_FILES = 937
RESULT_STATUS = "PASS_S114_A07_S113_DIAGNOSTIC_SCOPE_COMPARE_NOT_PRODUCT"


class DistAuditError(ValueError):
    """Sanitized explicit failure; do not silently ignore malformed manifests."""


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(1024 * 1024)
            if not chunk:
                return h.hexdigest()
            h.update(chunk)


def safe_relative(raw: str) -> str:
    if not isinstance(raw, str) or not raw or "\\" in raw:
        raise DistAuditError("UNSAFE_RELATIVE_PATH")
    p = PurePosixPath(raw)
    if p.is_absolute() or any(x in ("..", ".", "") for x in raw.split("/")) or raw.startswith("/"):
        raise DistAuditError("UNSAFE_RELATIVE_PATH")
    return str(p)


def load_original(manifest: Path, *, expected_sha: str | None = ORIGINAL_MANIFEST_SHA256,
                  expected_rows: int = ORIGINAL_ALL_ROWS) -> dict[str, dict]:
    if expected_sha is not None:
        source = manifest.read_bytes()
        observed = hashlib.sha256(source).hexdigest()
        if observed != expected_sha:
            # Windows git checkout can expand committed LF to CRLF.
            # Accept only an all-CRLF checkout if the reconstituted original
            # LF bytes hash EXACTLY to A07's immutable known SHA256.
            # Never mutate the manifest or bypass the checksum.
            pure_crlf = (b"\r\n" in source and
                         source.count(b"\n") == source.count(b"\r\n"))
            canonical = source.replace(b"\r\n", b"\n") if pure_crlf else b""
            if hashlib.sha256(canonical).hexdigest() != expected_sha:
                raise DistAuditError("ORIGINAL_MANIFEST_SHA_MISMATCH")
    with manifest.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        required = {"SHA256", "SIZE_BYTES", "CATEGORY", "PACKAGE_PATH"}
        if not required.issubset(reader.fieldnames or ()):
            raise DistAuditError("ORIGINAL_MANIFEST_SCHEMA_INVALID")
        rows = list(reader)
    if len(rows) != expected_rows:
        raise DistAuditError("ORIGINAL_MANIFEST_ROW_COUNT_MISMATCH")
    found = {}
    casefold = set()
    for row in rows:
        raw = safe_relative(row["PACKAGE_PATH"])
        if not raw.startswith("TLMTool_2.1.2/"):
            raise DistAuditError("ORIGINAL_PACKAGE_PREFIX_INVALID")
        if not raw.startswith(ORIGINAL_PREFIX):
            continue
        rel = safe_relative(raw[len(ORIGINAL_PREFIX):])
        if rel.casefold() in casefold or rel in found:
            raise DistAuditError("ORIGINAL_DIST_DUPLICATE_PATH")
        casefold.add(rel.casefold())
        try:
            size = int(row["SIZE_BYTES"])
        except (ValueError, TypeError):
            raise DistAuditError("ORIGINAL_SIZE_INVALID") from None
        if size < 0 or len(row["SHA256"]) != 64:
            raise DistAuditError("ORIGINAL_METADATA_INVALID")
        found[rel] = {
            "sha256": row["SHA256"].lower(),
            "size": size,
            "category": row["CATEGORY"],
        }
    if not found:
        raise DistAuditError("ORIGINAL_DIST_EMPTY")
    return found


def inspect_diagnostic(dist: Path, *, expected_count: int = S113_DIAGNOSTIC_FILES,
                       expected_exe_sha: str | None = S113_DIAGNOSTIC_EXE_SHA256) -> dict[str, dict]:
    if dist.name != "TLMTool.dist" or not dist.is_dir():
        raise DistAuditError("S113_DIST_LOCATION_INVALID")
    exe = dist / S113_DIAGNOSTIC_EXE
    if not exe.is_file():
        raise DistAuditError("S113_DIAGNOSTIC_EXE_MISSING")
    if expected_exe_sha is not None and digest(exe) != expected_exe_sha:
        raise DistAuditError("S113_EXE_SHA_MISMATCH")
    if (dist / "TLMTool.exe").exists():
        raise DistAuditError("MISLEADING_PRODUCT_EXE_NAME")
    seen = {}
    casefold = set()
    for p in sorted(dist.rglob("*")):
        if p.is_symlink():
            raise DistAuditError("UNSAFE_DIAGNOSTIC_SYMLINK")
        if not p.is_file():
            continue
        rel = safe_relative(p.relative_to(dist).as_posix())
        if rel.casefold() in casefold:
            raise DistAuditError("DIAGNOSTIC_CASEFOLD_COLLISION")
        casefold.add(rel.casefold())
        seen[rel] = {
            "sha256": digest(p),
            "size": p.stat().st_size,
            "category": p.suffix.lower() or "(no extension)",
        }
    if len(seen) != expected_count:
        raise DistAuditError("S113_DIST_COUNT_MISMATCH")
    if "python310.dll" not in seen:
        raise DistAuditError("S113_PYTHON_RUNTIME_MISSING")
    return seen


def summarize(original: dict[str, dict], diagnostic: dict[str, dict]) -> tuple[dict, list[dict]]:
    original_keys = set(original)
    diagnostic_keys = set(diagnostic)
    common = original_keys & diagnostic_keys
    original_only = original_keys - diagnostic_keys
    diagnostic_only = diagnostic_keys - original_keys
    same = {p for p in common if original[p]["sha256"] == diagnostic[p]["sha256"]}
    different = common - same
    report = {
        "task": "S114",
        "kind": "A07_INNER_DIST_VS_S113_DIAGNOSTIC_ONLY",
        "status": RESULT_STATUS,
        "comparable_scope": ORIGINAL_PREFIX,
        "original_inner_file_count": len(original),
        "s113_diagnostic_file_count": len(diagnostic),
        "paths_common": len(common),
        "paths_exact_sha256": len(same),
        "paths_different_sha256": len(different),
        "paths_only_original": len(original_only),
        "paths_only_s113_diagnostic": len(diagnostic_only),
        "original_top_categories": dict(sorted(Counter(
            m["category"] for m in original.values()).items())),
        "s113_top_extensions": dict(sorted(Counter(
            m["category"] for m in diagnostic.values()).items())),
        "parity": "UNVERIFIED_FULL_PRODUCT_BUILD_NOT_PRESENT",
        "missing_code_claim": "NONE; absence from this minimal diagnostic is NOT evidence of omitted product source",
        "original_files_copied": 0,
        "game_launched": False,
        "signed_info_reconstructed": False,
    }
    rows = []
    for path in sorted(original_keys | diagnostic_keys):
        status = ("COMMON_EXACT" if path in same else
                  "COMMON_DIFFERENT" if path in different else
                  "NOT_IN_DIAGNOSTIC" if path in original_only else
                  "DIAGNOSTIC_ONLY")
        old, new = original.get(path), diagnostic.get(path)
        rows.append({
            "status": status,
            "relative_path": path,
            "original_sha256": old["sha256"] if old else "",
            "diagnostic_sha256": new["sha256"] if new else "",
            "original_bytes": old["size"] if old else "",
            "diagnostic_bytes": new["size"] if new else "",
        })
    return report, rows


def audit(manifest: Path, dist: Path, *, expected_manifest_sha: str | None = ORIGINAL_MANIFEST_SHA256,
          expected_orig_rows: int = ORIGINAL_ALL_ROWS,
          expected_dist_count: int = S113_DIAGNOSTIC_FILES,
          expected_exe_sha: str | None = S113_DIAGNOSTIC_EXE_SHA256) -> tuple[dict, list[dict]]:
    original = load_original(manifest, expected_sha=expected_manifest_sha,
                             expected_rows=expected_orig_rows)
    diag = inspect_diagnostic(dist, expected_count=expected_dist_count,
                              expected_exe_sha=expected_exe_sha)
    return summarize(original, diag)


def main() -> int:
    if len(sys.argv) != 4:
        print("Usage: S114_AUDIT_DIST.py <A07.tsv> <TLMTool.dist> <output-dir>", file=sys.stderr)
        return 2
    outdir = Path(sys.argv[3])
    try:
        report, rows = audit(Path(sys.argv[1]), Path(sys.argv[2]))
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / "s114_summary.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        with (outdir / "s114_paths.tsv").open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t")
            w.writeheader()
            w.writerows(rows)
        for k, v in report.items():
            if k not in {"original_top_categories", "s113_top_extensions"}:
                print("S114_" + k.upper() + "=" + json.dumps(v, ensure_ascii=True))
        return 0
    except (OSError, DistAuditError, ValueError) as exc:
        print("S114_AUDIT_FAILED=" + type(exc).__name__ + ":" +
              (str(exc) if isinstance(exc, DistAuditError) else "INPUT_OR_IO"), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
