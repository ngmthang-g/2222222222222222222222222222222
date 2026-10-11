"""S117 Windows native Tk: F02 saved/failed text follows real disk IO only.

Synthetic credentials in a temporary folder. No original ZIP, credentials,
game/Info server or proxy. No credential string printed to CI or JSON.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "artifacts" / "s117"
OUT.mkdir(parents=True, exist_ok=True)

def _pump(root, millis: int) -> None:
    root.after(millis, root.quit)
    root.mainloop()

def run() -> int:
    report = {
        "task": "S117", "status": "NOT_RUN", "game_run": False,
        "product": "NOT_BUILT", "signed_info": "NOT_AVAILABLE",
        "original_checkbox_token": "UNKNOWN", "co_migration": "UNKNOWN",
        "proxy_runtime": "EXCLUDED", "credentials_in_report": False,
    }
    root = None
    try:
        if os.name != "nt":
            raise RuntimeError("WINDOWS_REQUIRED")
        import tkinter as tk
        from login_tab import TLMLoginPathTab
        with tempfile.TemporaryDirectory(prefix="S117_FAKE_CONFIG_ONLY_") as td:
            cfg = Path(td) / "APPDATA" / "TLMTool" / "settings.ini"
            cfg.parent.mkdir(parents=True)
            cfg.write_text(
                "[Settings]\n"
                "accounts = UNKNOWN|FAKEUSER_S117|FAKEPASS_S117|Có|opaque_proxy\n"
                "  ?|ANOTHER_FAKE_USER|ANOTHER_FAKE_PASS|Tool|\n"
                "schedule_open = 04:20\n"
                "[Other]\nkeep = unchanged\n",
                encoding="utf-8", newline="")
            original = cfg.read_bytes()
            dialogs = []
            root = tk.Tk()
            root.geometry("600x1050+0+0")
            tab = TLMLoginPathTab(root, settings_file=cfg,
                    choose_directory=lambda **_: "",
                    show_error=lambda title, body: dialogs.append((title, body)))
            root.update()
            label = tab.account_rows.legacy_status_label
            report["initial_status_no_false_saved"] = "✅ Đã lưu tài khoản" not in label.cget("text")
            tab.account_rows.username_vars[0].set("EDITED_FAKEUSER_S117")
            report["still_no_success_immediately"] = "✅ Đã lưu tài khoản" not in label.cget("text")
            _pump(root, 450)
            report["saved_status_after_actual_write"] = label.cget("text") == "✅ Đã lưu tài khoản"
            changed = cfg.read_bytes()
            report["first_write_only_existing_username_field"] = (
                changed == original.replace(b"FAKEUSER_S117", b"EDITED_FAKEUSER_S117"))
            # Simulate legitimate external edit after previous save. This
            # causes backend stale-account refusal; no UI false success.
            external = changed.replace(b"EDITED_FAKEUSER_S117", b"EXTERNAL_FAKE_USERNAME")
            cfg.write_bytes(external)
            tab.account_rows.password_vars[0].set("CHANGED_FAKEPASS_S117")
            _pump(root, 450)
            report["error_text_only_on_failed_save"] = (
                label.cget("text").startswith("❌ Lỗi lưu:"))
            report["failure_does_not_clobber_external_edit"] = cfg.read_bytes() == external
            report["error_dialog_sanitized"] = (
                len(dialogs) >= 1
                and "CHANGED_FAKEPASS_S117" not in str(dialogs)
                and "EXTERNAL_FAKE_USERNAME" not in str(dialogs))
            # Failure remains unresolved on destroy; no silent mutation.
            tab.shutdown()
            root.destroy()
            root = None
            report["failure_still_no_credential_overwrite_on_shutdown"] = (
                cfg.read_bytes() == external)
        required = [v for v in report if isinstance(report[v], bool)
                    and v not in ("game_run", "credentials_in_report")]
        if not all(report[k] for k in required):
            raise RuntimeError("S117_NATIVE_BEHAVIOR_CHECK_FAILED")
        report["status"] = "PASS_NATIVE_S117_ORIGINAL_F02_SAVE_ERROR_AFTER_REAL_DISK_NO_GAME"
    except Exception as exc:
        report["status"] = "FAIL_NATIVE_S117"
        report["error_type"] = type(exc).__name__
    finally:
        if root is not None:
            try:
                root.destroy()
            except Exception:
                pass
        (OUT / "windows_f02_save_feedback.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        for k, v in report.items():
            print("S117_" + k.upper() + "=" + json.dumps(v, ensure_ascii=True))
    return 0 if report["status"].startswith("PASS_NATIVE_S117_") else 1

if __name__ == "__main__":
    raise SystemExit(run())
