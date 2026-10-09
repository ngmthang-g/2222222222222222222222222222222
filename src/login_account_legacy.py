"""S38 read-only, fail-closed F02 legacy Settings.accounts reader.

Source evidence: docs/tasks/F02.md and F03.md.  Persisted format is
check|user|pass|captcha|proxy, one row per line, maximum 100 logical rows.
The checkbox token encoding and legacy 'Có' meaning remain UNKNOWN.
No writer, guessed migration, logging or Proxy action is permitted here.
"""
from __future__ import annotations

import configparser
from dataclasses import dataclass
from pathlib import Path

from settings_store import read_settings

ALLOWED_CAPTCHA_RAW = frozenset(("Không", "Tool", "Proxy", "Có"))
MAX_LEGACY_ROWS = 100


@dataclass(frozen=True)
class LegacyAccountRecord:
    check_raw: str
    username: str
    password: str
    captcha_raw: str
    proxy_raw: str


@dataclass(frozen=True)
class LegacyAccountLoad:
    status: str
    records: tuple[LegacyAccountRecord, ...] = ()

    @property
    def count(self) -> int:
        return len(self.records)


def parse_legacy_accounts(raw: str) -> LegacyAccountLoad:
    """Parse only unambiguous five-field rows, never infer checked or migrate Có.

    On ANY malformed, over-capacity or unsupported record, return zero records;
    do not silently truncate or display a partial account set. Status strings
    are safe for diagnostics and never contain credentials.
    """
    if not isinstance(raw, str):
        return LegacyAccountLoad("BLOCKED_FORMAT")
    if raw == "":
        return LegacyAccountLoad("EMPTY")
    if "\x00" in raw or "\r" in raw:
        return LegacyAccountLoad("BLOCKED_FORMAT")
    rows = raw.split("\n")
    if rows and rows[-1] == "":
        rows.pop()  # one optional trailing row separator, never a data row
    if not rows or any(row == "" for row in rows):
        return LegacyAccountLoad("BLOCKED_FORMAT")
    if len(rows) > MAX_LEGACY_ROWS:
        return LegacyAccountLoad("BLOCKED_CAPACITY")
    parsed = []
    for row in rows:
        fields = row.split("|")
        if len(fields) != 5 or not fields[0]:
            return LegacyAccountLoad("BLOCKED_FORMAT")
        if fields[3] not in ALLOWED_CAPTCHA_RAW:
            return LegacyAccountLoad("BLOCKED_CAPTCHA")
        # Do NOT .strip() any field: credentials may contain significant spaces.
        parsed.append(LegacyAccountRecord(*fields))
    return LegacyAccountLoad("READY", tuple(parsed))


def read_legacy_accounts(settings_file: str | Path | None = None) -> LegacyAccountLoad:
    """Read existing E05 parser only; never create, modify or normalize files."""
    try:
        parser = read_settings(settings_file)
        if not parser.has_section("Settings") or not parser.has_option("Settings", "accounts"):
            return LegacyAccountLoad("EMPTY")
        return parse_legacy_accounts(parser.get("Settings", "accounts", raw=True))
    except (OSError, UnicodeError, RuntimeError, ValueError, configparser.Error):
        # Deliberately suppress exception text, which may include credentials.
        return LegacyAccountLoad("BLOCKED_READ")
