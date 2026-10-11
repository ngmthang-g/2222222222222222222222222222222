"""S129: original H06-H09 Train UI configuration, not live gameplay.

Backed by frozen TLM H01/H06/H07/H08/H09 and B05. These source-backed
[Farm] settings configure future authentic Farm handlers; this module does
NOT connect to a game, authorize Info, discard items or heal a character.

Write only six owned keys; preserve all other settings.ini bytes (including
the S128 town settings, saved coordinates, Party and Login secrets).
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
import os
from pathlib import Path
import re
import shutil
import tempfile
from typing import Mapping

from settings_store import _settings_lock, settings_path
from train_saved_coordinates import FarmCoordinatesStore, FarmCoordinateError, MAX_SETTINGS_BYTES
from farm_town_config import FarmTownSettingsStore, _KEYLINE

TRAIN_KEYS = (
    "respawn", "auto_reconnect", "pickup_no_cankhon",
    "trist", "pickup_mode", "heal_map",
)
BOOL_KEYS = ("respawn", "auto_reconnect", "pickup_no_cankhon", "trist")
KEEP_MODES = ("none", "weapons", "all")
KEEP_RADIOS = (("Không", "none"), ("Chỉ vũ khí", "weapons"), ("Tất cả", "all"))
KEEP_PRESET_KEYS = {
    "none": ("discard_weapons", "discard_nonweapon"),
    "weapons": ("discard_nonweapon",),
    "all": (),
}
BUILTIN_HEAL = {
    "Trị liệu Đại Lý": (2, 43, 178),
    "Trị liệu Lạc Dương": (3, 255, 126),
    "Trị liệu Tô Châu": (4, 155, 252),
    "Trị liệu Lâu Lan": (5, 294, 170),
}
HEAL_BUILTIN_SEPARATOR = "======Có sẵn======"
HEAL_MANUAL_SEPARATOR = "=====Thủ công====="
HEAL_DEFAULT = "Trị liệu Tô Châu"
_TRUE = frozenset(("1", "yes", "true", "on"))
_FALSE = frozenset(("0", "no", "false", "off"))
_TRAIN_PREFIX = re.compile(
    r"^[ \t]*(respawn|auto_reconnect|pickup_no_cankhon|trist|pickup_mode|heal_map)\b", re.I
)


class FarmTrainSettingsError(ValueError):
    """Unsupported or ambiguous configuration is not overwritten."""


@dataclass(frozen=True)
class FarmTrainConfig:
    respawn: bool = False
    auto_reconnect: bool = False
    pickup_no_cankhon: bool = False
    trist: bool = False
    pickup_mode: str = "all"
    heal_map: str = HEAL_DEFAULT

    def validated(self) -> "FarmTrainConfig":
        if (any(type(getattr(self, name)) is not bool for name in BOOL_KEYS)
                or type(self.pickup_mode) is not str
                or self.pickup_mode not in KEEP_MODES
                or type(self.heal_map) is not str
                or len(self.heal_map) > 180
                or any(x in self.heal_map for x in "\r\n\x00")):
            raise FarmTrainSettingsError("INVALID_FARM_TRAIN_CONFIG")
        return self

    def change(self, key: str, value: bool | str) -> "FarmTrainConfig":
        if type(key) is not str or key not in TRAIN_KEYS:
            raise FarmTrainSettingsError("UNSUPPORTED_TRAIN_KEY")
        return replace(self, **{key: value}).validated()

    def pickup_discard_preset_keys(self) -> tuple[str, ...]:
        """H09: descriptive plan ONLY; never invokes destructive discard."""
        return KEEP_PRESET_KEYS[self.validated().pickup_mode]


@dataclass(frozen=True)
class FarmTrainSnapshot:
    value: FarmTrainConfig
    file_bytes: bytes


class FarmTrainSettingsStore:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path is not None else settings_path()

    def _read(self):
        return FarmTownSettingsStore(self.path)._read()

    @staticmethod
    def _entries(lines, begin, end):
        values = {}
        if begin is None:
            return values
        for i in range(begin + 1, end):
            line = lines[i]
            if not _TRAIN_PREFIX.match(line):
                continue
            match = _KEYLINE.fullmatch(line)
            if match is None:
                raise FarmTrainSettingsError("MALFORMED_TRAIN_SETTING")
            key = match.group(2).casefold()
            if key not in TRAIN_KEYS or key in values:
                raise FarmTrainSettingsError("AMBIGUOUS_TRAIN_SETTING")
            if i + 1 < end and lines[i + 1][:1] in (" ", "\t"):
                raise FarmTrainSettingsError("AMBIGUOUS_TRAIN_CONTINUATION")
            values[key] = (i, match.group(4).strip())
        return values

    @staticmethod
    def _decode(entries):
        defaults = FarmTrainConfig()
        props = {}
        for key in BOOL_KEYS:
            val = entries.get(key, (None, str(getattr(defaults, key))))[1]
            clean = val.casefold()
            if clean in _TRUE:
                props[key] = True
            elif clean in _FALSE:
                props[key] = False
            else:
                raise FarmTrainSettingsError("INVALID_TRAIN_BOOLEAN")
        mode = entries.get("pickup_mode", (None, "all"))[1]
        # Frozen H09 explicitly requires unsupported saved modes fall back
        # to a valid original choice rather than becoming a fourth radio.
        props["pickup_mode"] = mode if mode in KEEP_MODES else "all"
        props["heal_map"] = entries.get("heal_map", (None, HEAL_DEFAULT))[1]
        return FarmTrainConfig(**props).validated()

    def load(self) -> FarmTrainSnapshot:
        with _settings_lock:
            try:
                raw, lines, _, begin, end = self._read()
            except (FarmCoordinateError, ValueError) as exc:
                raise FarmTrainSettingsError("UNSAFE_TRAIN_SETTINGS") from exc
            return FarmTrainSnapshot(
                self._decode(self._entries(lines, begin, end)), raw)

    def save(self, value: FarmTrainConfig, *, expected_bytes: bytes) -> FarmTrainSnapshot:
        if type(value) is not FarmTrainConfig or type(expected_bytes) is not bytes:
            raise FarmTrainSettingsError("INVALID_TRAIN_WRITE_REQUEST")
        value.validated()
        with _settings_lock:
            try:
                raw, lines, newline, begin, end = self._read()
            except (FarmCoordinateError, ValueError) as exc:
                raise FarmTrainSettingsError("UNSAFE_TRAIN_SETTINGS") from exc
            if raw != expected_bytes:
                raise FarmTrainSettingsError("STALE_TRAIN_SETTINGS")
            existing = self._entries(lines, begin, end)
            self._decode(existing)  # never replace unreadable or ambiguous rows
            requested = {
                **{key: str(getattr(value, key)) for key in BOOL_KEYS},
                "pickup_mode": value.pickup_mode,
                "heal_map": value.heal_map,
            }
            modified = list(lines)
            for key, (i, _) in existing.items():
                m = _KEYLINE.fullmatch(modified[i])
                if m is None:
                    raise FarmTrainSettingsError("MALFORMED_TRAIN_SETTING")
                modified[i] = (
                    m.group(1) + m.group(2) + m.group(3)
                    + requested[key] + (m.group(5) or ""))
            inserts = [
                f"{key} = {requested[key]}{newline}"
                for key in TRAIN_KEYS if key not in existing
            ]
            if begin is None:
                prefix = ("" if not modified or modified[-1].endswith(("\r", "\n"))
                          else newline)
                text = "".join(modified) + prefix + "[Farm]" + newline + "".join(inserts)
            else:
                if (inserts and end > 0
                        and not modified[end - 1].endswith(("\r", "\n"))):
                    raise FarmTrainSettingsError("UNTERMINATED_FARM_SECTION")
                modified[end:end] = inserts
                text = "".join(modified)
            encoded = text.encode("utf-8")
            if encoded == raw:
                return FarmTrainSnapshot(value, raw)
            if len(encoded) > MAX_SETTINGS_BYTES:
                raise FarmTrainSettingsError("SETTINGS_TOO_LARGE")
            self.path.parent.mkdir(parents=True, exist_ok=True)
            fd, temporary = tempfile.mkstemp(
                prefix="settings.", suffix=".tmp", dir=str(self.path.parent))
            try:
                with os.fdopen(fd, "wb") as stream:
                    stream.write(encoded)
                    stream.flush()
                    os.fsync(stream.fileno())
                current = self.path.read_bytes() if self.path.exists() else b""
                if current != raw:
                    raise FarmTrainSettingsError("SETTINGS_CHANGED_CONCURRENTLY")
                if self.path.exists():
                    backup = self.path.with_name(
                        "settings." + datetime.now().strftime("%Y%m%d") + ".ini")
                    if not backup.exists():
                        shutil.copy2(self.path, backup)
                os.replace(temporary, self.path)
            except OSError as exc:
                raise FarmTrainSettingsError("SETTINGS_WRITE_FAILED") from exc
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
            return FarmTrainSnapshot(value, encoded)


def heal_options(path: str | Path | None = None):
    """H06 builtins + live H11 saved presets; no game memory is touched.

    Invalid or retired preset records must not silently become a viable
    treatment destination. A real game action runner remains unavailable.
    """
    raw_names = ()
    try:
        loaded = FarmCoordinatesStore(path).load()
        if loaded.skipped_retired_map_ids:
            raise FarmTrainSettingsError("RETIRED_TRAIN_HEAL_MAP")
        raw_names = tuple(row.name for row in loaded.rows)
    except (FarmCoordinateError, OSError) as exc:
        raise FarmTrainSettingsError("UNSAFE_SAVED_HEAL_COORDINATES") from exc
    if (len(raw_names) != len(set(raw_names))
            or any(not name or name in BUILTIN_HEAL or name in (
                HEAL_BUILTIN_SEPARATOR, HEAL_MANUAL_SEPARATOR)
                for name in raw_names)):
        raise FarmTrainSettingsError("AMBIGUOUS_TRAIN_HEAL_COORDINATES")
    return ((HEAL_BUILTIN_SEPARATOR,) + tuple(BUILTIN_HEAL)
            + (HEAL_MANUAL_SEPARATOR,) + raw_names)


def is_real_heal_destination(name: str, choices: tuple[str, ...]) -> bool:
    return (type(name) is str and name in choices
            and name not in (HEAL_BUILTIN_SEPARATOR, HEAL_MANUAL_SEPARATOR))
