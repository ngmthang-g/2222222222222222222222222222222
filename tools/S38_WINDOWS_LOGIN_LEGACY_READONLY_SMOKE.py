"""S38 native Windows Tk F02 read-only hydration proof; dummy credentials only."""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "artifacts" / "s38"
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT / "windows_login_readonly_legacy.json"


def run():
    result = {
        "task": "S38",
        "status": "NOT_RUN",
        "real_game": "NOT_RUN",
        "real_info": "NOT_AVAILABLE",
        "product_exe": "NOT_BUILT",
        "account_writer": False,
        "legacy_check_semantics": "UNKNOWN",
        "legacy_co_mapping": "UNKNOWN",
        "proxy_runtime": "EXCLUDED",
        "credential_values_in_artifact": False,
    }
    root = None
    try:
        if os.name != "nt":
            raise RuntimeError("Native Windows Tk required")
        import tkinter as tk
        from tkinter import ttk
        from login_tab import TLMLoginPathTab
        from login_account_legacy import read_legacy_accounts
        with tempfile.TemporaryDirectory(prefix="S38_TEST_ONLY_") as td:
            cfg = Path(td) / "APPDATA" / "TLMTool" / "settings.ini"
            cfg.parent.mkdir(parents=True)
            cfg.write_text(
                "[Settings]\n"
                "accounts = UNKNOWN|S38_DUMMY_USER|S38_DUMMY_PASSWORD|Có|opaque\n"
                "  ?|OTHER_DUMMY|SECOND_DUMMY_PASSWORD|Tool|\n"
                "grid_rows = 4\n[Unrelated]\nkeep = yes\n",
                encoding="utf-8",
            )
            before = cfg.read_bytes()
            root = tk.Tk()
            root.geometry("620x1050+0+0")
            tab = TLMLoginPathTab(root, settings_file=cfg,
                                  choose_directory=lambda **_: "",
                                  show_error=lambda *_: None)
            root.update()
            model = tab.account_rows
            result["real_tk_100_entries"] = (len(model.entry_user) == 100
                                            and len(model.entry_pass) == 100)
            result["actual_legacy_two_rows_loaded"] = (
                tab.legacy_account_load_status == "READY"
                and model.username_vars[0].get() == "S38_DUMMY_USER"
                and model.password_vars[1].get() == "SECOND_DUMMY_PASSWORD")
            result["original_unknown_selection_not_guessed"] = (
                not model.snapshot(0).selected and
                model.row_selectors[0].cget("text") == "❔")
            result["co_shown_literally_not_migrated"] = (
                model.captcha_boxes[0].get() == "Có"
                and str(model.captcha_boxes[0].cget("state")) == "readonly"
                and "Có" not in tuple(model.captcha_boxes[0].cget("values")))
            result["password_mask_preserved"] = all(
                entry.cget("show") == "*" for entry in model.entry_pass)
            result["no_action_columns"] = all(
                model.rows_inner.grid_slaves(row=i, column=4) == []
                and model.rows_inner.grid_slaves(row=i, column=5) == []
                for i in range(1,101))
            model.show_password_toggle.invoke()
            model.show_password_toggle.invoke()
            result["password_mask_toggle_keeps_value"] = (
                model.snapshot(0).password == "S38_DUMMY_PASSWORD"
                and model.entry_pass[0].cget("show") == "*")
            result["legacy_file_unchanged_after_ui"] = cfg.read_bytes() == before
            tab.shutdown()
            root.destroy()
            root = None
            result["legacy_file_unchanged_after_destroy"] = cfg.read_bytes() == before
            result["reader_preserves_opaque_values"] = (
                read_legacy_accounts(cfg).records[0].check_raw == "UNKNOWN")
            # Malformed INI: never show a partially loaded account.
            cfg.write_text("[Settings]\naccounts = X|u|p|Tool|\n"
                           "  X|u|p|INVALID|\n", encoding="utf-8")
            root = tk.Tk()
            root.geometry("620x1050+0+0")
            blocked = TLMLoginPathTab(root, settings_file=cfg,
                                      choose_directory=lambda **_: "",
                                      show_error=lambda *_: None)
            root.update()
            result["malformed_batch_blocked_no_partial_rows"] = (
                blocked.legacy_account_load_status == "BLOCKED_CAPTCHA"
                and all(not v.get() for v in blocked.account_rows.username_vars))
            blocked.shutdown()
            root.destroy()
            root = None
            required = [key for key in result if key not in (
                "task", "status", "real_game", "real_info", "product_exe",
                "account_writer", "legacy_check_semantics", "legacy_co_mapping",
                "proxy_runtime", "credential_values_in_artifact")]
            assert all(result[key] is True for key in required), required
            result["status"] = "PASS_NATIVE_S38_READ_ONLY_F02_TK"
    except Exception as exc:
        # Exception type only: never leak credentials from exception text.
        result["status"] = "FAIL_NATIVE_S38"
        result["error_type"] = type(exc).__name__
    finally:
        if root is not None:
            try:
                root.destroy()
            except Exception:
                pass
        REPORT.write_text(json.dumps(result, ensure_ascii=False, indent=2),
                          encoding="utf-8")
        for k, v in result.items():
            print("S38_" + k.upper() + "=" + json.dumps(v, ensure_ascii=True))
    return 0 if result["status"] == "PASS_NATIVE_S38_READ_ONLY_F02_TK" else 1


if __name__ == "__main__":
    raise SystemExit(run())
