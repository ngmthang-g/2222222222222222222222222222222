"""S169: real original-backed Train LSV *top config*, independent app only.

I01/B06/I06 prove [TrainLSV] respawn/auto_reconnect/trist/pickup_mode;
this module NEVER sends commands or claims game runtime. Persist ONLY the
single user-edited key, retaining unrelated bytes including Farm/Login/Party.
Unseen clean-boot boolean defaults are UNKNOWN: False represents only the
B06 captured unchecked UI baseline, never original global reset policy.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path
import os
import re
import shutil
import tempfile

from settings_store import _settings_lock, settings_path
from train_saved_coordinates import FarmCoordinatesStore, FarmCoordinateError, MAX_SETTINGS_BYTES, _HEADER
from farm_town_config import _KEYLINE

LSV_TOP_KEYS = ("respawn", "auto_reconnect", "trist", "pickup_mode")
LSV_BOOL_KEYS = ("respawn", "auto_reconnect", "trist")
LSV_KEEP_RADIOS = (("Không", "none"), ("Chỉ vũ khí", "weapons"), ("Tất cả", "all"))
LSV_DISCARD_PRESETS = {
    "none": ("discard_weapons", "discard_nonweapon"),
    "weapons": ("discard_nonweapon",),
    "all": (),
}
_TRUE = frozenset({"1", "true", "yes", "on"})
_FALSE = frozenset({"0", "false", "no", "off"})
_TARGET_LINE = re.compile(r"^[ \t]*(respawn|auto_reconnect|trist|pickup_mode)\b", re.I)


class TrainLsvSettingsError(ValueError):
    """Refuse missing evidence, ambiguous source records and stale writes."""


@dataclass(frozen=True)
class TrainLsvTopConfig:
    respawn: bool = False
    auto_reconnect: bool = False
    trist: bool = False
    pickup_mode: str = "all"

    def validated(self) -> "TrainLsvTopConfig":
        if (any(type(getattr(self, k)) is not bool for k in LSV_BOOL_KEYS)
                or type(self.pickup_mode) is not str
                or self.pickup_mode not in LSV_DISCARD_PRESETS):
            raise TrainLsvSettingsError("INVALID_LSV_TOP_CONFIG")
        return self

    def change(self, key: str, value: bool | str) -> "TrainLsvTopConfig":
        if key not in LSV_TOP_KEYS or type(key) is not str:
            raise TrainLsvSettingsError("UNSUPPORTED_LSV_TOP_KEY")
        return replace(self, **{key: value}).validated()

    def discard_preset_keys(self) -> tuple[str, ...]:
        """Description-only I06 keep-filter policy; never drops a game item."""
        return LSV_DISCARD_PRESETS[self.validated().pickup_mode]


@dataclass(frozen=True)
class TrainLsvTopSnapshot:
    value: TrainLsvTopConfig
    file_bytes: bytes


class TrainLsvTopStore:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path is not None else settings_path()

    def _read(self):
        try:
            raw, lines, newline = FarmCoordinatesStore(self.path)._lines()
        except (FarmCoordinateError, OSError) as exc:
            raise TrainLsvSettingsError("UNSAFE_LSV_SETTINGS") from exc
        headers = []
        for index, line in enumerate(lines):
            match = _HEADER.fullmatch(line.rstrip("\r\n"))
            if match:
                headers.append((index, match.group(1).strip().casefold()))
        sections = [i for i, name in headers if name == "trainlsv"]
        if len(sections) > 1:
            raise TrainLsvSettingsError("DUPLICATE_TRAINLSV_SECTION")
        begin = sections[0] if sections else None
        end = (next((i for i, _ in headers if i > begin), len(lines))
               if begin is not None else len(lines))
        return raw, lines, newline, begin, end

    @staticmethod
    def _entries(lines, begin, end):
        found = {}
        if begin is None:
            return found
        for i in range(begin + 1, end):
            if not _TARGET_LINE.match(lines[i]):
                continue
            match = _KEYLINE.fullmatch(lines[i])
            if match is None:
                raise TrainLsvSettingsError("MALFORMED_LSV_SETTING")
            key = match.group(2).casefold()
            if key not in LSV_TOP_KEYS or key in found:
                raise TrainLsvSettingsError("AMBIGUOUS_LSV_SETTING")
            if i + 1 < end and lines[i + 1][:1] in (" ", "\t"):
                raise TrainLsvSettingsError("AMBIGUOUS_LSV_MULTILINE")
            found[key] = (i, match.group(4).strip())
        return found

    @staticmethod
    def _decode(found):
        options = {}
        for key in LSV_BOOL_KEYS:
            v = found.get(key, (None, "false"))[1].casefold()
            if v in _TRUE:
                options[key] = True
            elif v in _FALSE:
                options[key] = False
            else:
                raise TrainLsvSettingsError("INVALID_LSV_BOOLEAN")
        mode = found.get("pickup_mode", (None, "all"))[1]
        if mode not in LSV_DISCARD_PRESETS:
            raise TrainLsvSettingsError("UNKNOWN_LSV_PICKUP_MODE")
        return TrainLsvTopConfig(**options, pickup_mode=mode).validated()

    def load(self) -> TrainLsvTopSnapshot:
        with _settings_lock:
            raw, lines, _, begin, end = self._read()
            return TrainLsvTopSnapshot(
                self._decode(self._entries(lines, begin, end)), raw)

    def save_change(self, key: str, value: bool | str, *,
                    expected_bytes: bytes) -> TrainLsvTopSnapshot:
        """Only user-changed proven key is written, never absent/unknown keys.

        Backups/atomic commit use existing H02/H06 file rules. Re-read current
        complete bytes under global lock before replacing, preserving all
        other original sections and unknown TrainLSV keys byte-for-byte.
        """
        if (type(key) is not str or key not in LSV_TOP_KEYS
                or type(expected_bytes) is not bytes):
            raise TrainLsvSettingsError("INVALID_LSV_WRITE_REQUEST")
        with _settings_lock:
            raw, lines, newline, begin, end = self._read()
            if raw != expected_bytes:
                raise TrainLsvSettingsError("STALE_LSV_SETTINGS")
            found = self._entries(lines, begin, end)
            updated = self._decode(found).change(key, value)
            setting = str(value) if key in LSV_BOOL_KEYS else value
            modified = list(lines)
            if key in found:
                pos, _ = found[key]
                match = _KEYLINE.fullmatch(modified[pos])
                if match is None:
                    raise TrainLsvSettingsError("MALFORMED_LSV_SETTING")
                modified[pos] = (match.group(1) + match.group(2)
                                 + match.group(3) + setting
                                 + (match.group(5) or ""))
            elif begin is None:
                prefix = ("" if not modified or modified[-1].endswith(("\n", "\r"))
                          else newline)
                modified.append(prefix + "[TrainLSV]" + newline
                                + f"{key} = {setting}" + newline)
            else:
                if end > 0 and not modified[end - 1].endswith(("\n", "\r")):
                    raise TrainLsvSettingsError("UNTERMINATED_TRAINLSV_SECTION")
                modified.insert(end, f"{key} = {setting}" + newline)
            encoded = "".join(modified).encode("utf-8")
            if encoded == raw:
                return TrainLsvTopSnapshot(updated, raw)
            if len(encoded) > MAX_SETTINGS_BYTES:
                raise TrainLsvSettingsError("LSV_SETTINGS_TOO_LARGE")
            self.path.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(
                prefix="settings.", suffix=".tmp", dir=str(self.path.parent))
            try:
                with os.fdopen(fd, "wb") as out:
                    out.write(encoded)
                    out.flush()
                    os.fsync(out.fileno())
                current = self.path.read_bytes() if self.path.exists() else b""
                if current != raw:
                    raise TrainLsvSettingsError("LSV_SETTINGS_CHANGED_CONCURRENTLY")
                if self.path.exists():
                    backup = self.path.with_name(
                        "settings." + datetime.now().strftime("%Y%m%d") + ".ini")
                    if not backup.exists():
                        shutil.copy2(self.path, backup)
                os.replace(tmp, self.path)
            except OSError as exc:
                raise TrainLsvSettingsError("LSV_SETTINGS_WRITE_FAILED") from exc
            finally:
                if os.path.exists(tmp):
                    os.unlink(tmp)
            return TrainLsvTopSnapshot(updated, encoded)
