"""Original-backed Rao M02-M05 configuration storage, independent from game sends.

This is real user-editable [Rao] config persistence (not a chat sender).
Original proof: docs/rao/M02_MESSAGE_STORAGE_FLOW.md,
M03_CHANNEL_MAPPING_FLOW.md, M04_INTERVAL_FLOW.md and M05_ACCOUNT_ASSIGNMENT_FLOW.md.
Keep source-uncertain behavior explicit and preserve all unrelated INI bytes.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
from typing import Sequence

from settings_store import _settings_lock, settings_path
from train_saved_coordinates import MAX_SETTINGS_BYTES


RAO_CHANNELS = {
    "Thế giới": 8, "Bang hội": 2, "Môn phái": 6,
    "Tổ đội": 4, "Liên minh": 3, "Quân đoàn": 11, "Lân cận": 5,
}
RAO_DEFAULT_CHANNEL = "Thế giới"
RAO_DEFAULT_SECONDS = "30"

_SECTION = re.compile(r"^[ \t]*\[([^\]\r\n]+)\][ \t]*(?:\r?\n)?$")
_RAO_START = re.compile(r"^[ \t]*rao_", re.I)
_RAO_LINE = re.compile(
    r"^([ \t]*)(rao_([^=:\r\n]*?))([ \t]*[=:][ \t]*)([^\r\n]*)(\r?\n)?$", re.I
)
_VALID_NAME = re.compile(r"^[^=:\[\]\r\n]+$")
_DIGITS = re.compile(r"^[0-9]*$")


class RaoConfigError(ValueError):
    """Do not alter malformed, stale or concurrently modified settings."""


@dataclass(frozen=True)
class RaoDefinition:
    name: str
    content: str = ""
    channel: str = RAO_DEFAULT_CHANNEL
    seconds: str = RAO_DEFAULT_SECONDS

    def validated(self) -> "RaoDefinition":
        if (type(self.name) is not str or self.name != self.name.strip()
                or not self.name or _VALID_NAME.fullmatch(self.name) is None
                or self.name.startswith(("#", ";"))):
            raise RaoConfigError("INVALID_RAO_NAME")
        if type(self.content) is not str or "\x00" in self.content:
            raise RaoConfigError("INVALID_RAO_CONTENT")
        if type(self.channel) is not str or self.channel not in RAO_CHANNELS:
            # A nonempty obsolete channel must never be silently sent as a new ID.
            raise RaoConfigError("UNKNOWN_RAO_CHANNEL")
        if (type(self.seconds) is not str
                or _DIGITS.fullmatch(self.seconds) is None
                or (self.seconds and int(self.seconds) > 60)):
            raise RaoConfigError("INVALID_RAO_INTERVAL")
        # Zero/blank can be stored as config but NEVER trigger a send loop.
        return self


@dataclass(frozen=True)
class RaoConfigSnapshot:
    rows: tuple[RaoDefinition, ...]
    file_bytes: bytes


def next_rao_name(rows: Sequence[RaoDefinition]) -> str:
    """M02: use smallest currently unused Rao N, starting at 1."""
    names = {r.name for r in rows}
    n = 1
    while f"Rao {n}" in names:
        n += 1
    return f"Rao {n}"


def resolve_rao(rows: Sequence[RaoDefinition], name: str):
    """Pure M02/M03/M04 resolver, no memory/network/game sends.

    Returns (content, seconds_int, numeric_channel_id, display_name)
    or (None, source-backed Vietnamese failure explanation).
    """
    name = name.strip() if type(name) is str else ""
    if not name:
        return None, "Chưa chọn nội dung rao"
    matches = [r for r in rows if r.name == name]
    if not matches:
        return None, f"'{name}' không còn tồn tại"
    if len(matches) != 1:
        return None, "Tên rao bị trùng"
    row = matches[0]
    if not row.content.strip():
        return None, f"Rao '{name}' chưa có nội dung"
    if row.channel not in RAO_CHANNELS:
        return None, f"'{name}' chưa chọn kênh"
    if (not row.seconds or _DIGITS.fullmatch(row.seconds) is None
            or not 1 <= int(row.seconds) <= 60):
        return None, f"'{name}' chưa đặt thời gian lặp"
    return row.content, int(row.seconds), RAO_CHANNELS[row.channel], row.channel


def _load_seconds(value) -> str:
    """M04: persisted bad/missing -> 30, numeric stored data 0..60."""
    try:
        if type(value) not in (str, int):
            return RAO_DEFAULT_SECONDS
        number = int(value)
    except (TypeError, ValueError, OverflowError):
        return RAO_DEFAULT_SECONDS
    return str(min(60, max(0, number)))


class RaoDefinitionStore:
    """Optimistic-byte-snapshot atomic editor of only the rao_ family.

    The four-selection acc_<real character> JSON family is kept byte-exact.
    Such entries must NOT be inferred from HWND/PID/window titles.
    """

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path is not None else settings_path()

    def _read(self):
        try:
            source = self.path.read_bytes() if self.path.exists() else b""
        except OSError as exc:
            raise RaoConfigError("RAO_SETTINGS_UNREADABLE") from exc
        if len(source) > MAX_SETTINGS_BYTES or b"\x00" in source:
            raise RaoConfigError("RAO_SETTINGS_UNSAFE_SIZE_OR_NUL")
        try:
            text = source.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise RaoConfigError("RAO_SETTINGS_NOT_UTF8") from exc
        if text.startswith("\ufeff"):
            raise RaoConfigError("RAO_SETTINGS_BOM_UNKNOWN")
        lines = text.splitlines(keepends=True)
        newline = "\r\n" if "\r\n" in text else "\n"
        headers = []
        for position, line in enumerate(lines):
            match = _SECTION.fullmatch(line)
            if match:
                headers.append((position, match.group(1).strip()))
        rao_sections = [pos for pos, title in headers if title.casefold() == "rao"]
        if len(rao_sections) > 1:
            raise RaoConfigError("DUPLICATE_RAO_SECTION")
        begin = rao_sections[0] if rao_sections else None
        end = (next((pos for pos, _ in headers if begin is not None and pos > begin),
                    len(lines)) if begin is not None else len(lines))
        return source, lines, newline, begin, end

    @staticmethod
    def _definitions(lines, begin, end):
        if begin is None:
            return ()
        result = []
        seen = set()
        for index in range(begin + 1, end):
            line = lines[index]
            if not _RAO_START.match(line):
                continue
            match = _RAO_LINE.fullmatch(line)
            if match is None:
                raise RaoConfigError("MALFORMED_RAO_DEFINITION")
            if index + 1 < end and lines[index + 1][:1] in (" ", "\t"):
                raise RaoConfigError("AMBIGUOUS_RAO_CONTINUATION")
            name = match.group(3).strip()
            if not name or name.casefold() in seen:
                raise RaoConfigError("DUPLICATE_OR_BLANK_RAO_NAME")
            seen.add(name.casefold())
            try:
                value = json.loads(match.group(5))
            except (json.JSONDecodeError, ValueError) as exc:
                raise RaoConfigError("MALFORMED_RAO_JSON") from exc
            if not isinstance(value, dict):
                raise RaoConfigError("INVALID_RAO_JSON_SHAPE")
            content = value.get("content", "")
            channel = value.get("channel", RAO_DEFAULT_CHANNEL)
            seconds = _load_seconds(value.get("sec", RAO_DEFAULT_SECONDS))
            row = RaoDefinition(name, content, channel, seconds).validated()
            result.append((index, row))
        # Exact original sort comparator unknown; this is stable local ordering.
        return tuple(sorted(result, key=lambda entry: entry[1].name.casefold()))

    def load(self) -> RaoConfigSnapshot:
        with _settings_lock:
            source, lines, _, begin, end = self._read()
            found = self._definitions(lines, begin, end)
            return RaoConfigSnapshot(tuple(row for _, row in found), source)

    def save(self, rows: Sequence[RaoDefinition], *,
             expected_bytes: bytes) -> RaoConfigSnapshot:
        if type(expected_bytes) is not bytes or type(rows) not in (list, tuple):
            raise RaoConfigError("INVALID_RAO_SAVE_REQUEST")
        validated = tuple(rows)
        seen = set()
        for row in validated:
            if type(row) is not RaoDefinition:
                raise RaoConfigError("INVALID_RAO_ROW")
            row.validated()
            if row.name.casefold() in seen:
                # M02 exact manual duplicate winner UNKNOWN: fail safely.
                raise RaoConfigError("DUPLICATE_RAO_DEFINITION")
            seen.add(row.name.casefold())
        with _settings_lock:
            original, lines, newline, begin, end = self._read()
            if original != expected_bytes:
                raise RaoConfigError("STALE_RAO_SETTINGS")
            old = self._definitions(lines, begin, end)
            if not old and not validated:
                return RaoConfigSnapshot(validated, original)
            positions = {idx for idx, _ in old}
            new_records = [
                "rao_" + row.name + " = " + json.dumps(
                    {"content": row.content, "channel": row.channel,
                     "sec": row.seconds}, ensure_ascii=False) + newline
                for row in validated
            ]
            if begin is None:
                prefix = ("" if not lines or lines[-1].endswith(("\n", "\r"))
                          else newline)
                revised = "".join(lines) + prefix + "[Rao]" + newline + "".join(new_records)
            else:
                insertion = min(positions) if positions else end
                if insertion > 0 and not lines[insertion - 1].endswith(("\n", "\r")):
                    raise RaoConfigError("UNTERMINATED_RAO_SECTION")
                target = []
                for index, line in enumerate(lines):
                    if index == insertion:
                        target.extend(new_records)
                    if index not in positions:
                        target.append(line)
                if insertion == len(lines):
                    target.extend(new_records)
                revised = "".join(target)
            encoded = revised.encode("utf-8")
            if encoded == original:
                return RaoConfigSnapshot(validated, original)
            if len(encoded) > MAX_SETTINGS_BYTES:
                raise RaoConfigError("RAO_SETTINGS_TOO_LARGE")
            self._atomic_write(original, encoded)
            return RaoConfigSnapshot(validated, encoded)

    def _atomic_write(self, expected: bytes, replacement: bytes):
        if len(replacement) > MAX_SETTINGS_BYTES:
            raise RaoConfigError("RAO_SETTINGS_TOO_LARGE")
        if replacement == expected:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp = tempfile.mkstemp(
            prefix="settings.", suffix=".tmp", dir=str(self.path.parent))
        try:
            with os.fdopen(fd, "wb") as out:
                out.write(replacement)
                out.flush()
                os.fsync(out.fileno())
            current = self.path.read_bytes() if self.path.exists() else b""
            if current != expected:
                raise RaoConfigError("RAO_SETTINGS_CHANGED_CONCURRENTLY")
            if self.path.exists():
                backup = self.path.with_name(
                    "settings." + datetime.now().strftime("%Y%m%d") + ".ini")
                if not backup.exists():
                    shutil.copy2(self.path, backup)
            os.replace(temp, self.path)
        except OSError as exc:
            raise RaoConfigError("RAO_SETTINGS_WRITE_FAILED") from exc
        finally:
            if os.path.exists(temp):
                os.unlink(temp)
