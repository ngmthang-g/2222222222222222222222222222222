"""S39 native Windows deterministic F09 clock smoke. NO product game actions."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "artifacts" / "s39"
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT / "windows_schedule_clock_only.json"


def run() -> int:
    result = {
        "task": "S39",
        "status": "NOT_RUN",
        "real_game": "NOT_RUN",
        "launcher_callbacks": "NOT_CONNECTED",
        "close_all": "NOT_CONNECTED",
        "shutdown_pc": "NOT_CONNECTED",
        "schedule_tk_controls": "NOT_INSTALLED",
        "proxy_runtime": "EXCLUDED",
        "product_exe": "NOT_BUILT",
    }
    try:
        if os.name != "nt":
            raise RuntimeError("Windows required")
        from login_schedule_clock import (
            LoginScheduleClock, EVENT_CLOSE, EVENT_OPEN,
            WORKER_CHECK_SECONDS, COUNTDOWN_REFRESH_SECONDS,
        )
        start = datetime(2026, 10, 9, 3, 59, 50)
        clock = LoginScheduleClock()
        result["documented_worker_seconds"] = WORKER_CHECK_SECONDS == 20
        result["documented_countdown_seconds"] = COUNTDOWN_REFRESH_SECONDS == 1
        result["initially_disabled_no_events"] = clock.poll(start) == ()
        clock.enable(start)
        result["enable_does_not_immediately_emit"] = clock.poll(start) == ()
        result["countdown_has_both_deadlines"] = (
            "Tắt 04:00 09/10 còn" in clock.countdown(start)
            and "Mở 04:20 09/10 còn" in clock.countdown(start))
        close = clock.poll(datetime(2026, 10, 9, 4, 0, 10))
        result["real_clock_close_event_once"] = (
            len(close) == 1 and close[0].kind == EVENT_CLOSE)
        result["no_duplicate_early_close"] = (
            clock.poll(datetime(2026, 10, 9, 4, 0, 15)) == ())
        op = clock.poll(datetime(2026, 10, 9, 4, 20, 10))
        result["real_clock_open_event_once"] = (
            len(op) == 1 and op[0].kind == EVENT_OPEN)
        result["next_day_advanced"] = (
            all(event.planned_time.day == 10 for event in clock.upcoming()))
        clock.disable()
        result["disable_cancels_future_clock_events"] = (
            not clock.enabled and
            clock.poll(datetime(2026, 10, 10, 4, 20)) == ())
        late = LoginScheduleClock()
        late.enable(datetime(2026, 10, 9, 15, 0))
        result["enable_late_waits_tomorrow"] = (
            late.poll(datetime(2026, 10, 9, 15, 0)) == ()
            and all(event.planned_time.day == 10 for event in late.upcoming()))
        required = [k for k in result if k not in (
            "task", "status", "real_game", "launcher_callbacks", "close_all",
            "shutdown_pc", "schedule_tk_controls", "proxy_runtime", "product_exe")]
        assert all(result[k] is True for k in required)
        result["status"] = "PASS_NATIVE_S39_F09_CLOCK_ONLY_NO_ACTION"
    except Exception as exc:
        result["status"] = "FAIL_NATIVE_S39"
        result["error_type"] = type(exc).__name__
    finally:
        REPORT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        for key, value in result.items():
            print("S39_" + key.upper() + "=" + json.dumps(value, ensure_ascii=True))
    return 0 if result["status"] == "PASS_NATIVE_S39_F09_CLOCK_ONLY_NO_ACTION" else 1


if __name__ == "__main__":
    raise SystemExit(run())
