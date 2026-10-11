"""S119 H11: authentic on-disk Farm saved-coordinate records, not a Train UI.

The original writes [Farm] coord_1, coord_2, ... as name|map_id|x|y.
This source-only store requires a supplied, verified MapID registry. It
never guesses a map, launches a game, grants Info, or calls movement.
It edits ONLY coordinate lines; unrelated settings bytes are preserved.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import os
from pathlib import Path
import re
import shutil
import tempfile
from typing import Mapping, Sequence

from settings_store import _settings_lock, settings_path

MAX_SETTINGS_BYTES = 2_097_152
_HEADER = re.compile(r"^[ \t]*\[([^\]\r\n]+)\][ \t]*(?:[;#].*)?$")
_KEY = re.compile(r"^[ \t]*coord_(\d+)[ \t]*[=:][ \t]*(.*)$", re.I)
_COORD_PREFIX = re.compile(r"^[ \t]*coord_", re.I)


class FarmCoordinateError(ValueError):
    """No persisted change is permitted on malformed/ambiguous input."""


@dataclass(frozen=True)
class FarmCoordinate:
    name: str
    map_id: int
    x: str
    y: str


@dataclass(frozen=True)
class FarmCoordinatesLoad:
    rows: tuple[FarmCoordinate, ...]
    skipped_retired_map_ids: tuple[int, ...] = ()


class FarmCoordinatesStore:
    """H11 actual sequential INI records; caller must supply known MapIDs.

    This is an independently usable configuration backend; original Tk
    defaults, combo-delete microbehavior and coordinate autosave delay are
    UNKNOWN and deliberately not invented.
    """

    def __init__(self, path: str | Path | None = None,
                 *, known_map_ids: Mapping[int, str] | None = None):
        # S120 default is verified from frozen TLM EXE, never client aliases.
        if known_map_ids is None:
            from farm_original_maps import FARM_MAP_ID_TO_NAME
            known_map_ids = FARM_MAP_ID_TO_NAME
        if not isinstance(known_map_ids, Mapping) or any(
            type(k) is not int or k < 0 or not isinstance(v, str) or not v
            for k, v in known_map_ids.items()
        ):
            raise FarmCoordinateError("UNVERIFIED_MAP_REGISTRY")
        self.path = Path(path) if path is not None else settings_path()
        self.known_map_ids = dict(known_map_ids)

    def _lines(self) -> tuple[bytes, list[str], str]:
        try:
            raw = self.path.read_bytes() if self.path.exists() else b""
        except OSError as exc:
            raise FarmCoordinateError("SETTINGS_READ_FAILED") from exc
        if len(raw) > MAX_SETTINGS_BYTES or raw.startswith(b"\xef\xbb\xbf") or b"\x00" in raw:
            raise FarmCoordinateError("UNSAFE_SETTINGS_FORMAT")
        try:
            text = raw.decode("utf-8")
        except UnicodeError as exc:
            raise FarmCoordinateError("UNSAFE_SETTINGS_ENCODING") from exc
        # Do not normalize CRLF; preserve all unrelated record bytes.
        newline = "\r\n" if "\r\n" in text else "\n"
        return raw, text.splitlines(keepends=True), newline

    @staticmethod
    def _span(lines: Sequence[str]) -> tuple[int | None, int]:
        sections = []
        for index, line in enumerate(lines):
            m = _HEADER.fullmatch(line.rstrip("\r\n"))
            if m:
                sections.append((index, m.group(1).strip().casefold()))
        farms = [index for index, name in sections if name == "farm"]
        if len(farms) > 1:
            raise FarmCoordinateError("AMBIGUOUS_FARM_SECTION")
        if not farms:
            return None, len(lines)
        begin = farms[0]
        end = next((index for index, _ in sections if index > begin), len(lines))
        return begin, end

    @staticmethod
    def _coordinate_lines(lines: Sequence[str], start: int, end: int):
        found = []
        keys = set()
        for index in range(start + 1, end):
            line = lines[index].rstrip("\r\n")
            if not _COORD_PREFIX.match(line):
                continue
            m = _KEY.fullmatch(line)
            if not m or int(m.group(1)) <= 0:
                raise FarmCoordinateError("MALFORMED_COORDINATE_KEY")
            number = int(m.group(1))
            if number in keys:
                raise FarmCoordinateError("DUPLICATE_COORDINATE_KEY")
            keys.add(number)
            # Continuations must not be deleted as if they were independent rows.
            if index + 1 < end and lines[index + 1][:1] in (" ", "\t"):
                raise FarmCoordinateError("AMBIGUOUS_COORDINATE_CONTINUATION")
            found.append((index, number, m.group(2).strip()))
        return sorted(found, key=lambda record: record[1])

    @staticmethod
    def _parse_value(value: str) -> FarmCoordinate:
        fields = value.split("|")
        if len(fields) != 4 or not fields[1].strip().isascii() or not fields[1].strip().isdecimal():
            raise FarmCoordinateError("INVALID_COORDINATE_VALUE")
        map_id = int(fields[1].strip())
        if any("\n" in f or "\r" in f for f in fields):
            raise FarmCoordinateError("INVALID_COORDINATE_VALUE")
        return FarmCoordinate(fields[0], map_id, fields[2], fields[3])

    def load(self) -> FarmCoordinatesLoad:
        with _settings_lock:
            _, lines, _ = self._lines()
            start, end = self._span(lines)
            if start is None:
                return FarmCoordinatesLoad(())
            found = self._coordinate_lines(lines, start, end)
            rows, skipped = [], []
            for _, _, value in found:
                record = self._parse_value(value)
                if record.map_id not in self.known_map_ids:
                    skipped.append(record.map_id)
                else:
                    rows.append(record)
            return FarmCoordinatesLoad(tuple(rows), tuple(skipped))

    def save(self, rows: Sequence[FarmCoordinate]) -> str:
        """Persist a complete snapshot of coordinate rows only; no arbitrary keys."""
        if not isinstance(rows, (list, tuple)):
            raise FarmCoordinateError("INVALID_COORDINATE_ROWS")
        values = []
        for row in rows:
            if (not isinstance(row, FarmCoordinate)
                or type(row.map_id) is not int
                or row.map_id not in self.known_map_ids
                or any(not isinstance(v, str) or "\n" in v or "\r" in v or "|" in v
                       for v in (row.name, row.x, row.y))):
                raise FarmCoordinateError("INVALID_OR_UNVERIFIED_COORDINATE")
            values.append(f"{row.name}|{row.map_id}|{row.x}|{row.y}")
        with _settings_lock:
            original, lines, newline = self._lines()
            start, end = self._span(lines)
            if start is not None:
                old = self._coordinate_lines(lines, start, end)
                # Fail closed on malformed prior values, even when being replaced.
                for _, _, value in old:
                    self._parse_value(value)
                old_positions = {index for index, _, _ in old}
                insert_at = min(old_positions) if old_positions else end
            else:
                old_positions = set()
                insert_at = len(lines)
            inserts = [f"coord_{i} = {v}{newline}" for i, v in enumerate(values, 1)]
            if start is None:
                prefix = "" if not lines or lines[-1].endswith(("\n", "\r")) else newline
                updated = "".join(lines) + prefix + "[Farm]" + newline + "".join(inserts)
            else:
                if (inserts and insert_at > 0
                        and not lines[insert_at - 1].endswith(("\r", "\n"))):
                    raise FarmCoordinateError("UNTERMINATED_SETTINGS_LINE")
                updated_lines = []
                for i, line in enumerate(lines):
                    if i == insert_at:
                        updated_lines.extend(inserts)
                    if i not in old_positions:
                        updated_lines.append(line)
                if insert_at == len(lines):
                    updated_lines.extend(inserts)
                updated = "".join(updated_lines)
            encoded = updated.encode("utf-8")
            if encoded == original:
                return "UNCHANGED"
            if len(encoded) > MAX_SETTINGS_BYTES:
                raise FarmCoordinateError("SETTINGS_TOO_LARGE")
            self.path.parent.mkdir(parents=True, exist_ok=True)
            fd, temp = tempfile.mkstemp(prefix="settings.", suffix=".tmp",
                                        dir=str(self.path.parent))
            try:
                with os.fdopen(fd, "wb") as stream:
                    stream.write(encoded)
                    stream.flush()
                    os.fsync(stream.fileno())
                # Refuse obvious outside writes during preparation.
                current = self.path.read_bytes() if self.path.exists() else b""
                if current != original:
                    raise FarmCoordinateError("SETTINGS_CHANGED_CONCURRENTLY")
                if self.path.exists():
                    backup = self.path.with_name(
                        "settings." + datetime.now().strftime("%Y%m%d") + ".ini")
                    if not backup.exists():
                        shutil.copy2(self.path, backup)
                os.replace(temp, self.path)
            except OSError as exc:
                raise FarmCoordinateError("SETTINGS_WRITE_FAILED") from exc
            finally:
                if os.path.exists(temp):
                    os.unlink(temp)
            return "SAVED_FARM_COORDINATES"
