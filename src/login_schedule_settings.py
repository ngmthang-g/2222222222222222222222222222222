"""S40 F09/E05 schedule settings reader: REAL read-only config, no actions.

The original binary proves four keys in [Settings], but NOT the encoding
of the persisted boolean tokens. NEVER coerce schedule_on/shutdown tokens
to bool, arm a worker, launch a game, close HWNDs or shut down the PC here.

Only verified HH:MM time fields can be used for a pure S39 preview.
The legacy F02 Settings.accounts value is neither read nor rewritten.
"""
from __future__ import annotations

import configparser
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from login_schedule_clock import (
    DEFAULT_CLOSE, DEFAULT_OPEN, LoginScheduleClock, parse_hhmm,
)
from settings_store import read_settings

SETTINGS_SECTION = "Settings"
SCHEDULE_KEYS = (
    "schedule_on", "schedule_close", "schedule_open", "shutdown_after_close",
)
MAX_UNKNOWN_TOKEN_LENGTH = 64


@dataclass(frozen=True)
class SchedulePreview:
    next_close: datetime
    next_open: datetime
    countdown: str


@dataclass(frozen=True)
class ReadOnlyScheduleSettings:
    status: str
    close_hhmm: str | None = None
    open_hhmm: str | None = None
    schedule_on_raw: str | None = None
    shutdown_after_close_raw: str | None = None

    @property
    def preview_available(self) -> bool:
        return self.status in ("DEFAULTS_ONLY", "READ_ONLY_VALIDATED")

    def preview(self, now: datetime) -> SchedulePreview:
        """Calculate dates only. NEVER interpret schedule_on or start a worker."""
        if not self.preview_available:
            raise RuntimeError("SCHEDULE_SETTINGS_BLOCKED")
        clock = LoginScheduleClock(
            close_hhmm=self.close_hhmm, open_hhmm=self.open_hhmm)
        clock.enable(now)
        events = {event.kind: event.planned_time for event in clock.upcoming()}
        return SchedulePreview(
            next_close=events["close"], next_open=events["open"],
            countdown=clock.countdown(now))


def _bounded_opaque_token(value: str | None) -> bool:
    """Opaque values must be bounded; no login credentials in diagnostics."""
    return (value is None or
            (type(value) is str and len(value) <= MAX_UNKNOWN_TOKEN_LENGTH
             and not any(ch in value for ch in ("\\r", "\\n", "\\x00"))))


def read_schedule_settings(settings_file: str | Path | None = None) -> ReadOnlyScheduleSettings:
    """Read original E05 [Settings] F09 keys without changing INI bytes.

    With no [Settings], show original screenshot defaults but keep the
    schedule DISARMED and do NOT imply the saved schedule_on is enabled.
    Malformed time values block even the preview, not silently normalized.
    Invalid/unexpected opaque bool tokens are PRESERVED, never reinterpreted.
    """
    try:
        parser = read_settings(settings_file)
        if not parser.has_section(SETTINGS_SECTION):
            return ReadOnlyScheduleSettings(
                "DEFAULTS_ONLY", DEFAULT_CLOSE, DEFAULT_OPEN)
        values = {
            key: parser.get(SETTINGS_SECTION, key, fallback=None, raw=True)
            for key in SCHEDULE_KEYS
        }
        if not _bounded_opaque_token(values["schedule_on"]) or not _bounded_opaque_token(
                values["shutdown_after_close"]):
            return ReadOnlyScheduleSettings("BLOCKED_OPAQUE_TOKEN")
        close = values["schedule_close"]
        opened = values["schedule_open"]
        close = DEFAULT_CLOSE if close is None else close
        opened = DEFAULT_OPEN if opened is None else opened
        try:
            parse_hhmm(close)
            parse_hhmm(opened)
        except ValueError:
            return ReadOnlyScheduleSettings("BLOCKED_TIME_FORMAT")
        return ReadOnlyScheduleSettings(
            "READ_ONLY_VALIDATED", close, opened,
            values["schedule_on"], values["shutdown_after_close"])
    except (OSError, UnicodeError, ValueError, RuntimeError, configparser.Error):
        # Underlying error strings can contain settings.ini user credentials.
        return ReadOnlyScheduleSettings("BLOCKED_SETTINGS_READ")
