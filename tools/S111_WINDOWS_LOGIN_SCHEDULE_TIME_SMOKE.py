"""S111 true native Windows Tk Login schedule HH/MM edit smoke. No game."""
from __future__ import annotations
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
ART = ROOT / "artifacts" / "s111"
ART.mkdir(parents=True, exist_ok=True)


def main():
    if os.name != "nt":
        raise RuntimeError("S111 requires Windows-native Tk test")
    import tkinter as tk
    from login_tab import TLMLoginPathTab
    from settings_store import read_settings
    from login_schedule_settings import read_schedule_settings

    report = dict(task="S111", status="NOT_RUN", real_tk=True, real_game=False,
                  real_info=False, schedule_dispatched=False, proxy_actions=False,
                  verified_times=False, account_bytes_preserved=False)
    root = None
    try:
        with tempfile.TemporaryDirectory(prefix="s111_tk_schedule_") as td:
            cfg = Path(td) / "TLMTool" / "settings.ini"
            cfg.parent.mkdir(parents=True, exist_ok=True)
            before = ("[Settings]\r\n"
                      "accounts = UNKNOWN|synthetic_user|fake_password|Có|opaque\r\n"
                      " UNKNOWN|second_user|other_password|Tool|opaque\r\n"
                      "schedule_close = 04:00\r\nschedule_open=04:20\r\n"
                      "schedule_on = UNKNOWN\r\n"
                      "shutdown_after_close = UNKNOWN\r\n"
                      "[Another]\r\npreserve = yes\r\n").encode("utf-8")
            cfg.write_bytes(before)
            account_before = read_settings(cfg).get("Settings", "accounts")
            root = tk.Tk()
            root.title("S111 TEST ONLY NO LIVE GAME")
            root.geometry("650x1050+15+15")
            tab = TLMLoginPathTab(root, settings_file=cfg,
                                  choose_directory=lambda **_: "",
                                  show_error=lambda *_: None)
            root.update()
            clock = tab.schedule_times
            assert clock.group.winfo_manager() == "place"
            assert clock.group.winfo_y() == 88
            assert tab.account_rows.group_accounts.winfo_y() == 238
            assert clock.group.winfo_height() == 136
            assert len(clock.combos) == 2
            for key in ("schedule_close", "schedule_open"):
                for cb in clock.combos[key]:
                    assert str(cb.cget("state")) == "readonly"
            chour, cmin = clock.vars["schedule_close"]
            ohour, omin = clock.vars["schedule_open"]
            assert (chour.get(), cmin.get(), ohour.get(), omin.get()) == ("04", "00", "04", "20")

            chour.set("07")
            clock.combos["schedule_close"][0].event_generate("<<ComboboxSelected>>")
            root.update()
            assert clock.last_status == "UPDATED_ONLY_SCHEDULE_CLOSE"
            assert read_schedule_settings(cfg).close_hhmm == "07:00"

            omin.set("35")
            clock.combos["schedule_open"][1].event_generate("<<ComboboxSelected>>")
            root.update()
            assert clock.last_status == "UPDATED_ONLY_SCHEDULE_OPEN"
            assert read_schedule_settings(cfg).open_hhmm == "04:35"
            expected = before.replace(b"schedule_close = 04:00", b"schedule_close = 07:00").replace(
                b"schedule_open=04:20", b"schedule_open=04:35")
            assert cfg.read_bytes() == expected, "unrelated config/account content modified"
            assert read_settings(cfg).get("Settings", "accounts") == account_before
            report["verified_times"] = True
            report["account_bytes_preserved"] = True

            tab.shutdown()
            root.destroy()
            root = None
            report["status"] = "PASS_NATIVE_S111_REAL_F01_TIME_SELECTORS_ONLY_NO_GAME"
    finally:
        if root is not None:
            try:
                root.destroy()
            except Exception:
                pass
        (ART / "s111_test_only.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(report["status"])


if __name__ == "__main__":
    main()
