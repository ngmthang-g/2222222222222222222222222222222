"""S86 evidence-grade source/build audit, NOT a TLM product implementation.

Read every Python source/test/tool file, compile its AST without importing
game modules or touching user data, inventory registered vs unreconstructed
tabs, and explicitly test the ordinary product bootstrap refuses unverified
Info. Produces JSON evidence under artifacts/s86. S36 separately proves its
*DIAGNOSTIC*, never a runnable complete product.
"""
from __future__ import annotations
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "artifacts" / "s86" / "source_and_product_gate_audit.json"

def collect_syntax(root: Path) -> dict:
    manifest = []
    failures = []
    for folder in ("src", "tests", "tools"):
        directory = root / folder
        for path in sorted(directory.rglob("*.py")) if directory.is_dir() else ():
            relative = path.relative_to(root).as_posix()
            try:
                raw = path.read_bytes()
                text = raw.decode("utf-8-sig")
                tree = ast.parse(text, filename=relative)
                compile(tree, relative, "exec")
                manifest.append({"path": relative, "sha256": hashlib.sha256(raw).hexdigest()})
            except (OSError, UnicodeError, SyntaxError, ValueError, TypeError) as error:
                failures.append({"path": relative, "type": type(error).__name__,
                                 "details": str(error)[:180]})
    digest = hashlib.sha256(
        "\n".join(row["path"] + "\t" + row["sha256"] for row in manifest)
        .encode("utf-8")).hexdigest()
    return {
        "files_compiled": len(manifest),
        "source_modules": sum(x["path"].startswith("src/") for x in manifest),
        "test_modules": sum(x["path"].startswith("tests/test_") for x in manifest),
        "tool_modules": sum(x["path"].startswith("tools/") for x in manifest),
        "compiled_sources_digest": digest,
        "syntax_failures": failures,
    }

def audit_registration(root: Path) -> dict:
    shell_path = root / "src" / "shell.py"
    builder_path = root / "src" / "source_backed_tab_builders.py"
    shell = ast.parse(shell_path.read_text(encoding="utf-8"))
    builders = ast.parse(builder_path.read_text(encoding="utf-8"))
    slots = []
    for node in ast.walk(shell):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "TabSpec" and node.args
                and isinstance(node.args[0], ast.Constant)
                and type(node.args[0].value) is str):
            slots.append(node.args[0].value)
    build_keys = []
    for node in ast.walk(builders):
        if not isinstance(node, ast.Return) or not isinstance(node.value, ast.Dict):
            continue
        keys = []
        for key in node.value.keys:
            if isinstance(key, ast.Constant) and type(key.value) is str:
                keys.append(key.value)
            elif isinstance(key, ast.Name) and key.id == "INFO_KEY":
                keys.append("info_tab")
        if {"info_tab", "start_tab", "login_tab"} <= set(keys):
            build_keys = keys
            break
    if len(slots) != len(set(slots)) or not build_keys or not set(build_keys) <= set(slots):
        raise ValueError("INVALID_REAL_TAB_REGISTRATION")
    missing = [key for key in slots if key not in build_keys]
    return {
        "original_potential_tab_slots": slots,
        "registered_partial_or_external_tabs": build_keys,
        "no_registered_builder_for": missing,
        "external_real_Info_factory_required": True,
        "note": "Start/Login are PARTIAL. Info is externally injected, NOT genuine signed server.",
    }

def verify_product_bootstrap(root: Path, *, timeout: int = 15) -> dict:
    path = root / "src" / "TLMTool.py"
    if not path.is_file():
        return {"status": "ENTRYPOINT_MISSING"}
    try:
        completed = subprocess.run(
            [sys.executable, str(path)],
            cwd=str(root), text=True, capture_output=True,
            timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"status": "EXECUTION_FAILED", "error": type(error).__name__}
    combined = completed.stderr + completed.stdout
    refused = (completed.returncode == 2
               and "S01 BLOCKED:" in completed.stderr
               and "genuine InfoTab/server authorization" in combined)
    return {
        "status": "EXPLICITLY_BLOCKED_NO_GUI" if refused else "UNEXPECTED_BOOTSTRAP_BEHAVIOR",
        "returncode": completed.returncode,
        "stderr_excerpt": completed.stderr[:240],
    }

def build_report(root: Path = ROOT) -> dict:
    source = collect_syntax(root)
    try:
        tabs = audit_registration(root)
    except (OSError, SyntaxError, ValueError, UnicodeError) as error:
        tabs = {"audit_error": type(error).__name__ + ": " + str(error)[:150]}
    gate = verify_product_bootstrap(root)
    valid = (not source["syntax_failures"]
             and source["source_modules"] >= 45
             and source["test_modules"] >= 80
             and not tabs.get("audit_error")
             and gate["status"] == "EXPLICITLY_BLOCKED_NO_GUI")
    return {
        "task": "S86",
        "status": ("PASS_SOURCE_AUDIT_PRODUCT_STILL_BLOCKED"
                   if valid else "FAIL_SOURCE_AUDIT"),
        "source": source,
        "tabs": tabs,
        "product_bootstrap": gate,
        "product_exe": "NOT_BUILT_NOT_WORKING",
        "S36_windows_exe": "CI_SEPARATELY_VERIFIED_DIAGNOSTIC_NOT_PRODUCT",
        "true_game_native_runtime": "NOT_EXECUTED",
        "auth_server": "NOT_RECONSTRUCTED",
        "no_original_proxy_development": True,
    }

def main() -> int:
    result = build_report()
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print("S86_STATUS=" + result["status"])
    print("S86_SOURCE_MODULES=" + str(result["source"]["source_modules"]))
    print("S86_TEST_MODULES=" + str(result["source"]["test_modules"]))
    print("S86_ALL_COMPILED=" + str(result["source"]["files_compiled"]))
    print("S86_UNBUILT_TABS=" + str(result["tabs"].get("no_registered_builder_for")))
    print("S86_PRODUCT_BOOTSTRAP=" + result["product_bootstrap"]["status"])
    print("S86_SOURCE_MANIFEST_SHA256=" + result["source"]["compiled_sources_digest"])
    print("S86_REPORT=" + str(REPORT))
    return 0 if result["status"] == "PASS_SOURCE_AUDIT_PRODUCT_STILL_BLOCKED" else 1

if __name__ == "__main__":
    raise SystemExit(main())
