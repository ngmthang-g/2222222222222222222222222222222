"""S40 Windows native E05 F09 INI config + S39 clock, no real game actions.

Temporary test-owned APPDATA only; original settings.ini and passwords untouched.
"""
from __future__ import annotations
import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s40"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"windows_schedule_settings_readonly.json"


def run() -> int:
    r={
        "task":"S40","status":"NOT_RUN",
        "real_game":"NOT_RUN", "real_info":"NOT_AVAILABLE",
        "proxy_runtime":"EXCLUDED", "real_schedule_worker":"NOT_WIRED",
        "real_game_action_callbacks":"NOT_CONNECTED",
        "product_exe":"NOT_BUILT", "account_passwords_in_artifact":False,
    }
    try:
        if os.name != "nt":
            raise RuntimeError("Windows native smoke required")
        from login_schedule_settings import read_schedule_settings
        from login_account_legacy import read_legacy_accounts
        with tempfile.TemporaryDirectory(prefix="S40_TEST_ONLY_") as td:
            config=Path(td)/"APPDATA"/"TLMTool"/"settings.ini"
            config.parent.mkdir(parents=True)
            config.write_text(
                "[Settings]\n"
                "accounts = LEGACY_UNKNOWN|S40_TEST_USER|S40_DUMMY_PASSWORD|Có|opaque\n"
                "  X|S40_OTHER|S40_SECOND_PASSWORD|Tool|\n"
                "schedule_on = ORIGINAL_RAW_UNVERIFIED\n"
                "schedule_close = 04:00\n"
                "schedule_open = 04:20\n"
                "shutdown_after_close = UNVERIFIED_POWER_TOKEN\n"
                "[Unrelated]\nkeep = yes\n",
                encoding="utf-8")
            before=config.read_bytes()
            schedule=read_schedule_settings(config)
            r["genuine_e05_config_loaded"]=schedule.status=="READ_ONLY_VALIDATED"
            r["unknown_bool_preserved"]=(
                schedule.schedule_on_raw=="ORIGINAL_RAW_UNVERIFIED"
                and schedule.shutdown_after_close_raw=="UNVERIFIED_POWER_TOKEN")
            p=schedule.preview(datetime(2026,10,9,15,0))
            r["next_occurrences_tomorrow"]=(
                p.next_close==datetime(2026,10,10,4,0)
                and p.next_open==datetime(2026,10,10,4,20))
            r["countdown_is_deterministic"]=(
                "Tắt 04:00 10/10 còn" in p.countdown
                and "Mở 04:20 10/10 còn" in p.countdown)
            r["accounts_still_read_by_s38_unchanged"]=(
                read_legacy_accounts(config).status=="READY"
                and read_legacy_accounts(config).count==2)
            r["settings_ini_byte_identical"]=config.read_bytes()==before
            r["no_backup_or_new_files"]=len(list(config.parent.iterdir()))==1
            config.write_text(
                "[Settings]\nschedule_close = invalid\n"
                "schedule_open = 04:20\n", encoding="utf-8")
            bad=read_schedule_settings(config)
            r["invalid_time_refused_without_dispatch"]=(
                bad.status=="BLOCKED_TIME_FORMAT" and not bad.preview_available)
            required=[k for k in r if k not in (
                "task","status","real_game","real_info","proxy_runtime",
                "real_schedule_worker","real_game_action_callbacks",
                "product_exe","account_passwords_in_artifact")]
            assert all(r[k] is True for k in required), "S40 check failed"
            r["status"]="PASS_NATIVE_S40_E05_F09_READONLY_CONFIG_CLOCK"
    except Exception as exc:
        r["status"]="FAIL_NATIVE_S40"
        # No exception messages or traceback: settings may contain secrets.
        r["error_type"]=type(exc).__name__
    finally:
        REPORT.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
        for k,v in r.items():
            print("S40_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if r["status"]=="PASS_NATIVE_S40_E05_F09_READONLY_CONFIG_CLOCK" else 1

if __name__=="__main__":
    raise SystemExit(run())
