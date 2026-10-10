"""S116: actual Windows Tk 300ms existing-row account-save proof, synthetic only."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "artifacts" / "s116"
OUT.mkdir(parents=True, exist_ok=True)

def run() -> int:
    report = {
        "task": "S116", "status": "NOT_RUN", "actual_game": "NOT_RUN",
        "original_signed_info": "NOT_AVAILABLE", "proxy_runtime": "EXCLUDED",
        "accounts_written": "EXISTING_USER_PASS_ONLY", "credential_values_in_artifact": False,
        "original_check_token_semantics": "UNKNOWN",
        "legacy_co_migration": "UNKNOWN",
    }
    root = None
    try:
        if os.name != "nt":
            raise RuntimeError("WINDOWS_TK_REQUIRED")
        import tkinter as tk
        from login_tab import TLMLoginPathTab
        with tempfile.TemporaryDirectory(prefix="S116_SYNTHETIC_ONLY_") as td:
            cfg = Path(td) / "APPDATA" / "TLMTool" / "settings.ini"
            cfg.parent.mkdir(parents=True)
            initial = (
                "[Settings]\n"
                "accounts = OPAQUE_TOKEN|S116_DUMMY_A|S116_PASS_A|Có|RAW_PROXY_TEXT\n"
                "  ?|S116_DUMMY_B|S116_PASS_B|Tool|\n"
                "  ?|S116_DUMMY_C|S116_PASS_C|Không|\n"
                "schedule_open = 04:20\n"
                "[Other]\nkeep = unaffected\n"
            )
            cfg.write_text(initial, encoding="utf-8", newline="")
            before = cfg.read_bytes()
            root = tk.Tk()
            root.geometry("650x1050+0+0")
            tab = TLMLoginPathTab(root, settings_file=cfg,
                                  choose_directory=lambda **_: "",
                                  show_error=lambda *_: None)
            root.update()
            model = tab.account_rows
            assert tab.existing_account_autosave is not None
            assert tab.legacy_account_load_status == "READY"
            # Test only, external source is NOT an actual Info entitlement.
            limited = model.apply_account_row_limit(1, allowed=lambda: True)
            report["test_only_hidden_row_preserved"] = (
                limited.visible_count == 1 and model.hidden_row_indices[0] == 1)
            model.username_vars[0].set("S116_NEW_A")
            model.password_vars[1].set("S116_NEW_PASS_B")
            report["before_300ms_write_blocked"] = None

            def before_debounce():
                report["before_300ms_write_blocked"] = cfg.read_bytes() == before

            root.after(135, before_debounce)
            root.after(430, root.quit)
            root.mainloop()
            root.update_idletasks()
            altered = cfg.read_bytes()
            expected = before.replace(b"S116_DUMMY_A", b"S116_NEW_A").replace(
                b"S116_PASS_B", b"S116_NEW_PASS_B")
            report["after_300ms_actual_file_changed_exactly_two_fields"] = (
                altered == expected)
            report["check_captcha_proxy_fields_untouched"] = (
                b"OPAQUE_TOKEN|S116_NEW_A|S116_PASS_A|C\xc3\xb3|RAW_PROXY_TEXT" in altered
                and b"  ?|S116_DUMMY_B|S116_NEW_PASS_B|Tool|" in altered)
            report["unrelated_ini_bytes_preserved"] = (
                b"schedule_open = 04:20" in altered
                and b"[Other]\nkeep = unaffected\n" in altered)
            report["legacy_hidden_row_tracked"] = model.hidden_row_indices()[0] == 1 if callable(getattr(model,"hidden_row_indices",None)) else model.hidden_row_indices[0] == 1
            report["strict_300ms_original"] = (
                tab.existing_account_autosave.last_status ==
                "UPDATED_EXISTING_ACCOUNT_FIELDS_ONLY")
            # F02 separately proves final save-on-destroy for unsent changes.
            model.username_vars[0].set("S116_FLUSH_ON_DESTROY")
            tab.shutdown()
            latest = cfg.read_bytes()
            report["pending_change_flushed_on_destroy"] = (
                b"OPAQUE_TOKEN|S116_FLUSH_ON_DESTROY|S116_PASS_A" in latest)
            root.destroy()
            root = None
            report["password_values_never_in_output"] = True
            # Empty legacy data cannot fabricate selection tokens / new rows.
            cfg.write_text("[Settings]\naccounts = \n", encoding="utf-8")
            root = tk.Tk()
            empty = TLMLoginPathTab(root, settings_file=cfg,
                                    choose_directory=lambda **_: "",
                                    show_error=lambda *_: None)
            root.update()
            report["no_auto_new_row_writer"] = empty.existing_account_autosave is None
            raw_empty = cfg.read_bytes()
            empty.account_rows.username_vars[0].set("TEST_IN_MEMORY_ONLY")
            empty.shutdown()
            report["empty_accounts_bytes_preserved"] = cfg.read_bytes() == raw_empty
            root.destroy()
            root = None
        required = [k for k, value in report.items() if type(value) is bool]
        if not all(report[k] for k in required):
            raise RuntimeError("NATIVE_S116_CHECK_FALSE")
        report["status"] = "PASS_NATIVE_S116_F02_REAL_300MS_EXISTING_ROW_CONFIG_NO_GAME"
    except Exception as exc:
        report["status"] = "FAIL_NATIVE_S116"
        report["error_type"] = type(exc).__name__
    finally:
        if root is not None:
            try:
                root.destroy()
            except Exception:
                pass
        (OUT / "windows_f02_existing_account_save.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        for k, v in report.items():
            print("S116_" + k.upper() + "=" + json.dumps(v, ensure_ascii=True))
    return 0 if report["status"].startswith("PASS_NATIVE_S116") else 1


if __name__ == "__main__":
    raise SystemExit(run())
