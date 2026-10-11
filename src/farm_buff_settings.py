"""S131 original TLM 2.1.2 Farm manual buff-row INI persistence ONLY.

Frozen FarmTab._add_buff_row, _load_buffs, _save_config prove:
- original [Farm] buff_N sequential keys, value enabled|key|minutes|seconds;
- Tk checkbox, F1-F10/1/2/3 key selector, numeric minute/second edits,
  add/remove rows and actual config persistence.

Original fresh-row default tuple, timing clamp, exact autosave debounce and
live game key execution are not proven. No game or signed Info operations.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import os
from pathlib import Path
import re
import shutil
import tempfile
from typing import Sequence

from farm_town_config import FarmTownSettingsStore
from settings_store import _settings_lock, settings_path
from train_saved_coordinates import MAX_SETTINGS_BYTES, FarmCoordinateError

BUFF_KEYS = tuple(f"F{i}" for i in range(1, 11)) + ("1", "2", "3")
_BUFF_KEY = re.compile(r"^[ \t]*buff_(\d+)[ \t]*[=:][ \t]*(.*?)(\r?\n)?$", re.I)
_BUFF_PREFIX = re.compile(r"^[ \t]*buff_", re.I)


class FarmBuffSettingsError(ValueError):
    """Malformed/ambiguous/stale Farm buffs must never corrupt settings."""


@dataclass(frozen=True)
class FarmBuffRow:
    enabled: bool
    key: str
    minutes: str
    seconds: str

    def validated(self) -> "FarmBuffRow":
        if type(self.enabled) is not bool or type(self.key) is not str or self.key not in BUFF_KEYS:
            raise FarmBuffSettingsError("INVALID_BUFF_TOGGLE_OR_KEY")
        # The original Tk _only_digits checker validates numeric characters.
        # No source-backed clamp to 59s or max minute value is claimed.
        for number in (self.minutes, self.seconds):
            if (type(number) is not str or not number or not number.isascii()
                    or not number.isdecimal() or len(number) > 9):
                raise FarmBuffSettingsError("INVALID_BUFF_TIME")
        return self

    def change(self, field: str, value: bool | str) -> "FarmBuffRow":
        if field not in ("enabled", "key", "minutes", "seconds"):
            raise FarmBuffSettingsError("INVALID_BUFF_FIELD")
        from dataclasses import replace
        return replace(self, **{field: value}).validated()


@dataclass(frozen=True)
class FarmBuffSnapshot:
    rows: tuple[FarmBuffRow, ...]
    file_bytes: bytes


class FarmBuffSettingsStore:
    """Byte-preserving, real [Farm] buff_N reader/writer for existing INI."""

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path is not None else settings_path()

    def _read(self):
        try:
            return FarmTownSettingsStore(self.path)._read()
        except (FarmCoordinateError, ValueError) as exc:
            raise FarmBuffSettingsError("UNSAFE_FARM_BUFF_SETTINGS") from exc

    @staticmethod
    def _records(lines: Sequence[str], start: int | None, end: int):
        if start is None:
            return ()
        found = []
        numbers = set()
        for line_id in range(start + 1, end):
            line = lines[line_id]
            if not _BUFF_PREFIX.match(line):
                continue
            match = _BUFF_KEY.fullmatch(line)
            if not match:
                raise FarmBuffSettingsError("MALFORMED_BUFF_KEY")
            number = int(match.group(1))
            if number < 1 or number in numbers:
                raise FarmBuffSettingsError("DUPLICATE_OR_INVALID_BUFF_INDEX")
            if line_id + 1 < end and lines[line_id + 1][:1] in (" ", "\t"):
                raise FarmBuffSettingsError("AMBIGUOUS_BUFF_CONTINUATION")
            numbers.add(number)
            raw = match.group(2).strip()
            parts = raw.split("|")
            if len(parts) != 4:
                raise FarmBuffSettingsError("INVALID_BUFF_RECORD_ARITY")
            enabled = parts[0].strip()
            if enabled not in ("True", "False"):
                raise FarmBuffSettingsError("INVALID_BUFF_ENABLED_ENCODING")
            row = FarmBuffRow(
                enabled == "True", *(p.strip() for p in parts[1:]))
            row.validated()
            found.append((number, line_id, row))
        return tuple(sorted(found))

    def load(self) -> FarmBuffSnapshot:
        with _settings_lock:
            source, lines, _, start, end = self._read()
            matches = self._records(lines, start, end)
            return FarmBuffSnapshot(tuple(row for _, _, row in matches), source)

    def save(self, rows: Sequence[FarmBuffRow], *,
             expected_bytes: bytes) -> FarmBuffSnapshot:
        if type(rows) not in (tuple, list) or type(expected_bytes) is not bytes:
            raise FarmBuffSettingsError("INVALID_BUFF_SAVE_REQUEST")
        for row in rows:
            if type(row) is not FarmBuffRow:
                raise FarmBuffSettingsError("INVALID_BUFF_ROW")
            row.validated()
        rows = tuple(rows)
        with _settings_lock:
            original, lines, newline, start, end = self._read()
            if original != expected_bytes:
                raise FarmBuffSettingsError("STALE_BUFF_SETTINGS")
            old = self._records(lines, start, end)
            old_positions = {index for _, index, _ in old}
            inserts = [
                f"buff_{index} = {'True' if row.enabled else 'False'}|"
                f"{row.key}|{row.minutes}|{row.seconds}{newline}"
                for index, row in enumerate(rows, 1)
            ]
            if start is None:
                prefix = "" if not lines or lines[-1].endswith(("\r", "\n")) else newline
                revised = "".join(lines) + prefix + "[Farm]" + newline + "".join(inserts)
            else:
                insert_at = min(old_positions) if old_positions else end
                if (inserts and insert_at > 0
                        and not lines[insert_at-1].endswith(("\r", "\n"))):
                    raise FarmBuffSettingsError("UNTERMINATED_FARM_SECTION")
                updated = []
                for i, line in enumerate(lines):
                    if i == insert_at:
                        updated.extend(inserts)
                    if i not in old_positions:
                        updated.append(line)
                if insert_at == len(lines):
                    updated.extend(inserts)
                revised = "".join(updated)
            encoded = revised.encode("utf-8")
            if encoded == original:
                return FarmBuffSnapshot(rows, original)
            if len(encoded) > MAX_SETTINGS_BYTES:
                raise FarmBuffSettingsError("BUFF_SETTINGS_TOO_LARGE")
            self.path.parent.mkdir(parents=True, exist_ok=True)
            fd, temporary = tempfile.mkstemp(
                prefix="settings.", suffix=".tmp", dir=str(self.path.parent))
            try:
                with os.fdopen(fd, "wb") as stream:
                    stream.write(encoded)
                    stream.flush()
                    os.fsync(stream.fileno())
                actual = self.path.read_bytes() if self.path.exists() else b""
                if actual != original:
                    raise FarmBuffSettingsError("BUFF_SETTINGS_CHANGED_CONCURRENTLY")
                if self.path.exists():
                    backup = self.path.with_name(
                        "settings." + datetime.now().strftime("%Y%m%d") + ".ini")
                    if not backup.exists():
                        shutil.copy2(self.path, backup)
                os.replace(temporary, self.path)
            except OSError as exc:
                raise FarmBuffSettingsError("BUFF_SETTINGS_WRITE_FAILED") from exc
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
            return FarmBuffSnapshot(rows, encoded)
