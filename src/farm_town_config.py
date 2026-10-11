"""S128 H02: original Train return-town INI configuration (NO game actions).

The frozen TLM 2.1.2 H01/H02/H04 documents the real [Farm] keys,
mode radio values, legacy full_bag alias, four unique nav priorities and
loop_minutes=30. Original invalid-minute clamping and live movement are
UNKNOWN. This module stores only proven configuration; nothing starts Farm.

Unlike a generic configparser rewrite, unrelated settings.ini bytes are
preserved (including Login secrets, Party and coordinate records).
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

from settings_store import _settings_lock, settings_path
from train_saved_coordinates import FarmCoordinatesStore, FarmCoordinateError, MAX_SETTINGS_BYTES

TOWN_MODES = ("never", "full_bag_timer", "cycle")
TOWN_RADIOS = (
    ("Không về", "never"),
    ("Khi đầy túi", "full_bag_timer"),
    ("Theo chu kỳ (phút)", "cycle"),
)
NAV_METHODS = ("", "Phù 1", "Phù 2", "Phù 3", "Ngựa")
DEFAULT_NAV = ("Phù 1", "Phù 2", "Phù 3", "Ngựa")
TOWN_KEYS = ("town_condition", "loop_minutes",
             "nav_priority_1", "nav_priority_2",
             "nav_priority_3", "nav_priority_4")
_KEYLINE = re.compile(r"^([ \t]*)([\w]+)([ \t]*[=:][ \t]*)(.*?)(\r?\n)?$")
_PREFIX = re.compile(r"^[ \t]*(town_condition|loop_minutes|nav_priority_[1-4])\b", re.I)


class FarmTownSettingsError(ValueError):
    """Invalid, ambiguous or stale Farm config refuses writes."""


@dataclass(frozen=True)
class FarmTownConfig:
    mode: str = "cycle"
    minutes: str = "30"
    navigation: tuple[str, str, str, str] = DEFAULT_NAV

    def validated(self) -> "FarmTownConfig":
        # Exact clamping behavior of original Spinbox not recovered: keep raw
        # valid whole-minute representation; do not invent min/max auto-clamp.
        if (type(self.mode) is not str or self.mode not in TOWN_MODES
                or type(self.minutes) is not str
                or not self.minutes or not self.minutes.isascii()
                or not self.minutes.isdecimal() or len(self.minutes) > 9
                or type(self.navigation) is not tuple
                or len(self.navigation) != 4
                or any(type(x) is not str or x not in NAV_METHODS
                       for x in self.navigation)):
            raise FarmTownSettingsError("INVALID_OR_UNKNOWN_FARM_TOWN_SETTING")
        taken = tuple(x for x in self.navigation if x)
        if len(taken) != len(set(taken)):
            raise FarmTownSettingsError("DUPLICATE_FARM_NAV_METHOD")
        return self

    def change_mode(self, value: str) -> "FarmTownConfig":
        return FarmTownConfig(value, self.minutes, self.navigation).validated()

    def change_minutes(self, value: str) -> "FarmTownConfig":
        return FarmTownConfig(self.mode, value, self.navigation).validated()

    def change_nav(self, index: int, value: str) -> "FarmTownConfig":
        if type(index) is not int or not 0 <= index < 4:
            raise FarmTownSettingsError("INVALID_NAV_INDEX")
        updated = list(self.navigation)
        updated[index] = value
        return FarmTownConfig(self.mode, self.minutes, tuple(updated)).validated()


@dataclass(frozen=True)
class FarmTownSnapshot:
    value: FarmTownConfig
    file_bytes: bytes


class FarmTownSettingsStore:
    """Durable source-backed H02 settings only. Fail closed on stale files."""

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path is not None else settings_path()

    def _read(self) -> tuple[bytes, list[str], str, int | None, int]:
        try:
            raw, lines, newline = FarmCoordinatesStore(self.path)._lines()
            begin, end = FarmCoordinatesStore._span(lines)
        except (FarmCoordinateError, OSError) as exc:
            raise FarmTownSettingsError("UNSAFE_FARM_SETTINGS") from exc
        return raw, lines, newline, begin, end

    @staticmethod
    def _entries(lines: Sequence[str], begin: int | None,
                 end: int) -> dict[str, tuple[int, str]]:
        values = {}
        if begin is None:
            return values
        for i in range(begin + 1, end):
            source = lines[i].rstrip("\r\n")
            if not _PREFIX.match(source):
                continue
            hit = _KEYLINE.fullmatch(lines[i])
            if hit is None:
                raise FarmTownSettingsError("MALFORMED_FARM_TOWN_KEY")
            key = hit.group(2).casefold()
            if key not in TOWN_KEYS or key in values:
                raise FarmTownSettingsError("AMBIGUOUS_FARM_TOWN_KEY")
            # Continuation lines are not safe to overwrite as scalar settings.
            if i + 1 < end and lines[i + 1][:1] in (" ", "\t"):
                raise FarmTownSettingsError("AMBIGUOUS_FARM_CONTINUATION")
            values[key] = (i, hit.group(4).strip())
        return values

    @staticmethod
    def _decode(entries: dict[str, tuple[int, str]]) -> FarmTownConfig:
        default = FarmTownConfig()
        mode = entries.get("town_condition", (-1, default.mode))[1]
        if mode == "full_bag":
            mode = "full_bag_timer"   # legacy value, not a fourth radio
        minutes = entries.get("loop_minutes", (-1, default.minutes))[1]
        nav = tuple(entries.get(f"nav_priority_{i}", (-1, DEFAULT_NAV[i - 1]))[1]
                    for i in range(1, 5))
        return FarmTownConfig(mode, minutes, nav).validated()

    def load(self) -> FarmTownSnapshot:
        with _settings_lock:
            raw, lines, _, begin, end = self._read()
            settings = self._decode(self._entries(lines, begin, end))
            return FarmTownSnapshot(settings, raw)

    def save(self, config: FarmTownConfig, *, expected_bytes: bytes) -> FarmTownSnapshot:
        if type(config) is not FarmTownConfig or type(expected_bytes) is not bytes:
            raise FarmTownSettingsError("INVALID_FARM_TOWN_WRITE_REQUEST")
        config.validated()
        with _settings_lock:
            original, lines, newline, begin, end = self._read()
            if original != expected_bytes:
                raise FarmTownSettingsError("FARM_SETTINGS_CHANGED_CONCURRENTLY")
            entries = self._entries(lines, begin, end)
            self._decode(entries)  # reject ambiguous/unparseable prior data
            requested = {
                "town_condition": config.mode, "loop_minutes": config.minutes,
                **{f"nav_priority_{i}": v
                   for i, v in enumerate(config.navigation, 1)},
            }
            modified = list(lines)
            for key, (pos, _) in entries.items():
                parsed = _KEYLINE.fullmatch(lines[pos])
                if parsed is None:
                    raise FarmTownSettingsError("MALFORMED_FARM_TOWN_KEY")
                endline = parsed.group(5) or ""
                modified[pos] = (parsed.group(1) + parsed.group(2)
                                 + parsed.group(3) + requested[key] + endline)
            additional = [
                f"{key} = {requested[key]}{newline}"
                for key in TOWN_KEYS if key not in entries
            ]
            if begin is None:
                prefix = ("" if not modified or modified[-1].endswith(("\r", "\n"))
                          else newline)
                updated = ("".join(modified) + prefix + "[Farm]" + newline
                           + "".join(additional))
            else:
                if (additional and end > 0
                        and not modified[end - 1].endswith(("\r", "\n"))):
                    raise FarmTownSettingsError("UNTERMINATED_FARM_SECTION")
                modified[end:end] = additional
                updated = "".join(modified)
            encoded = updated.encode("utf-8")
            if encoded == original:
                return FarmTownSnapshot(config, original)
            if len(encoded) > MAX_SETTINGS_BYTES:
                raise FarmTownSettingsError("FARM_SETTINGS_TOO_LARGE")
            self.path.parent.mkdir(parents=True, exist_ok=True)
            fd, temporary = tempfile.mkstemp(
                prefix="settings.", suffix=".tmp", dir=str(self.path.parent))
            try:
                with os.fdopen(fd, "wb") as stream:
                    stream.write(encoded)
                    stream.flush()
                    os.fsync(stream.fileno())
                current = self.path.read_bytes() if self.path.exists() else b""
                if current != original:
                    raise FarmTownSettingsError("FARM_SETTINGS_CHANGED_CONCURRENTLY")
                if self.path.exists():
                    backup = self.path.with_name(
                        "settings." + datetime.now().strftime("%Y%m%d") + ".ini")
                    if not backup.exists():
                        shutil.copy2(self.path, backup)
                os.replace(temporary, self.path)
            except OSError as exc:
                raise FarmTownSettingsError("FARM_SETTINGS_WRITE_FAILED") from exc
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
            return FarmTownSnapshot(config, encoded)
