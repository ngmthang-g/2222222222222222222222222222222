"""S116/F02: narrowly scoped existing Login-account field persistence.

Edit ONLY username/password of an existing, unambiguous five-field account
record. Preserve check/captcha/proxy fields and every unrelated settings.ini
byte (including legacy 'Có' and hidden plan rows). No new record creation,
selection token interpretation, captcha migration, Proxy or game activity.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import os
from pathlib import Path
import re
import shutil
import tempfile

from login_account_legacy import parse_legacy_accounts
from settings_store import _settings_lock, settings_path

SECTION = re.compile(r"^\[([^\]\r\n]+)\][ \t]*$")
KEY = re.compile(r"^([A-Za-z_][A-Za-z_0-9]*)([ \t]*[=:][ \t]*)([^\r\n]*)$")
MAX_INI_BYTES = 2 * 1024 * 1024


class ExistingAccountEditError(ValueError):
    """Only sanitized reasons: never include credentials/raw INI contents."""


@dataclass(frozen=True)
class ExistingAccountEdit:
    row_index: int
    expected_username: str
    expected_password: str
    username: str
    password: str


def _valid_field(value: str) -> bool:
    return (type(value) is str and
            all(char not in value for char in ("|", "\n", "\r", "\x00")))


def update_existing_accounts(
    changes: tuple[ExistingAccountEdit, ...] | list[ExistingAccountEdit],
    path: str | Path | None = None,
) -> str:
    """Update one/more *pre-existing* records atomically, with stale-value guard.

    Reject creation of a new account or writing guessed checkbox boolean.
    The unknown raw check/captcha/proxy values remain literally unchanged.
    Only raw username/password columns in the addressed rows can change.
    """
    if type(changes) not in (tuple, list) or not changes:
        raise ExistingAccountEditError("INVALID_EXISTING_ACCOUNT_EDITS")
    indices = set()
    for change in changes:
        if (type(change) is not ExistingAccountEdit
                or type(change.row_index) is not int
                or not 0 <= change.row_index < 100
                or change.row_index in indices
                or not all(_valid_field(x) for x in (
                    change.expected_username, change.expected_password,
                    change.username, change.password))):
            raise ExistingAccountEditError("UNSAFE_EXISTING_ACCOUNT_CHANGE")
        indices.add(change.row_index)

    target = Path(path) if path is not None else settings_path()
    with _settings_lock:
        try:
            raw = target.read_bytes()  # no new file and no guessed records
            if len(raw) > MAX_INI_BYTES or b"\x00" in raw:
                raise ExistingAccountEditError("UNSAFE_ACCOUNT_INI")
            content = raw.decode("utf-8")
        except (OSError, UnicodeError):
            raise ExistingAccountEditError("ACCOUNT_SETTINGS_UNREADABLE") from None
        if content.startswith("\ufeff"):
            raise ExistingAccountEditError("UNSUPPORTED_ACCOUNT_INI_BOM")
        lines = content.splitlines(keepends=True)
        sections = [
            (i, m.group(1).strip().casefold())
            for i, line in enumerate(lines)
            if (m := SECTION.fullmatch(line.rstrip("\r\n")))
        ]
        settings_starts = [i for i, name in sections if name == "settings"]
        if len(settings_starts) != 1:
            raise ExistingAccountEditError("SETTINGS_SECTION_AMBIGUOUS")
        start = settings_starts[0]
        end = next((i for i, _ in sections if i > start), len(lines))
        matches = []
        for i in range(start + 1, end):
            body = lines[i].rstrip("\r\n")
            if body[:1].isspace() and body.lstrip(" \t").casefold().startswith("accounts"):
                raise ExistingAccountEditError("AMBIGUOUS_INDENTED_ACCOUNTS_KEY")
            m = KEY.fullmatch(body)
            if m and m.group(1).casefold() == "accounts":
                matches.append((i, m))
        if len(matches) != 1:
            raise ExistingAccountEditError("ACCOUNTS_KEY_AMBIGUOUS")
        first, first_match = matches[0]
        row_lines = [(first, first_match.group(3), first_match.group(1) + first_match.group(2))]
        cursor = first + 1
        while cursor < end:
            line = lines[cursor]
            body = line.rstrip("\r\n")
            if not body or not body[:1].isspace():
                break
            # Parser continuation: preserve indent, no inferred raw values.
            leading = body[:len(body) - len(body.lstrip(" \t"))]
            if not leading or not body[len(leading):]:
                raise ExistingAccountEditError("MALFORMED_ACCOUNT_CONTINUATION")
            row_lines.append((cursor, body[len(leading):], leading))
            cursor += 1
        if len(row_lines) > 100:
            raise ExistingAccountEditError("ACCOUNT_ROW_OVER_CAPACITY")
        parsed = parse_legacy_accounts("\n".join(row[1] for row in row_lines))
        if parsed.status != "READY" or parsed.count != len(row_lines):
            raise ExistingAccountEditError("UNVERIFIED_EXISTING_ACCOUNT_FORMAT")
        if max(indices) >= parsed.count:
            raise ExistingAccountEditError("NOT_AN_EXISTING_ACCOUNT_ROW")
        for change in changes:
            row = parsed.records[change.row_index]
            if (row.username != change.expected_username
                    or row.password != change.expected_password):
                raise ExistingAccountEditError("ACCOUNT_EDIT_STALE_DATA")
            line_idx, _, prefix = row_lines[change.row_index]
            # Parse and modify ONLY these two fields, preserve unknown raw tokens.
            fields = [row.check_raw, change.username, change.password,
                      row.captcha_raw, row.proxy_raw]
            term = ("\r\n" if lines[line_idx].endswith("\r\n") else
                    "\n" if lines[line_idx].endswith("\n") else "")
            lines[line_idx] = prefix + "|".join(fields) + term
        new_raw = "".join(lines).encode("utf-8")
        if new_raw == raw:
            return "UNCHANGED"
        if len(new_raw) > MAX_INI_BYTES:
            raise ExistingAccountEditError("ACCOUNT_SETTINGS_TOO_LARGE")
        try:
            dated = target.with_name("settings." + datetime.now().strftime("%Y%m%d") + ".ini")
            if not dated.exists():
                shutil.copy2(target, dated)
            fd, tmp = tempfile.mkstemp(prefix="settings.", suffix=".tmp", dir=str(target.parent))
            try:
                with os.fdopen(fd, "wb") as out:
                    out.write(new_raw)
                    out.flush()
                    os.fsync(out.fileno())
                os.replace(tmp, target)
            finally:
                if os.path.exists(tmp):
                    os.unlink(tmp)
        except OSError:
            raise ExistingAccountEditError("ACCOUNT_PERSISTENCE_FAILED") from None
        return "UPDATED_EXISTING_ACCOUNT_FIELDS_ONLY"
