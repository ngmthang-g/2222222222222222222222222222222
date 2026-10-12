"""S182 original-backed [DonVang] Train / inventory / recovery config ONLY.

PLAN L04/L08/L10, original B09. No game inventory scanner, navigation,
memory write, respawn click or reconnect worker is created by this module.
The historical key auto_reconnect means STOP when disconnected in DonVang,
NOT reconnect like Farm. Save edits individually without touching receivers.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
import os
from pathlib import Path
import re
import shutil
import tempfile

from don_return_settings import DonReturnSettingsStore, DonReturnSettingsError
from farm_town_config import _KEYLINE
from settings_store import _settings_lock
from train_saved_coordinates import MAX_SETTINGS_BYTES

DON_BOOL_KEYS = (
    "respawn", "auto_reconnect", "unstuck", "pickup_no_cankhon", "trist")
DON_OTHER_KEYS = ("pickup_mode", "heal_map")
DON_TRAIN_KEYS = DON_BOOL_KEYS + DON_OTHER_KEYS
_PICKUP_MODES = ("all", "weapons")  # NO "none" mode in Dồn L04.
PICKUP_CHOICES = (("Tất cả", "all"), ("Chỉ vũ khí", "weapons"))
HEAL_DESTINATIONS = {
    "Trị liệu Đại Lý": (2, 43, 178),
    "Trị liệu Lạc Dương": (3, 255, 126),
    "Trị liệu Tô Châu": (4, 155, 252),
    "Trị liệu Lâu Lan": (5, 294, 170),
}
_TRUE = frozenset({"true", "1", "yes", "on"})
_FALSE = frozenset({"false", "0", "no", "off"})
_DON_TRAIN_PREFIX = re.compile(
    r"^[ \t]*(respawn|auto_reconnect|unstuck|pickup_no_cankhon|trist|pickup_mode|heal_map)\b", re.I)


class DonTrainSettingsError(ValueError):
    """Malformed/stale DonVang config may not be silently overwritten."""


@dataclass(frozen=True)
class DonTrainConfig:
    # For options without verified first-install defaults, use B09 *captured*
    # unchecked/checked UI as a LOCAL SEED, not a universal original default.
    respawn: bool = False
    auto_reconnect: bool = False  # UI label is STOP on disconnect.
    unstuck: bool = True          # B09 screenshot, universal default UNKNOWN.
    pickup_no_cankhon: bool = False
    pickup_mode: str = "all"       # L04 actual default.
    trist: bool = False
    heal_map: str = "Trị liệu Tô Châu"  # B09 displayed sample.

    def validated(self) -> "DonTrainConfig":
        if any(type(getattr(self, k)) is not bool for k in DON_BOOL_KEYS):
            raise DonTrainSettingsError("INVALID_DON_TRAIN_BOOLEAN")
        if (type(self.pickup_mode) is not str
                or self.pickup_mode not in _PICKUP_MODES):
            raise DonTrainSettingsError("INVALID_DON_PICKUP_MODE")
        if (type(self.heal_map) is not str
                or self.heal_map not in HEAL_DESTINATIONS):
            raise DonTrainSettingsError("UNKNOWN_DON_HEAL_DESTINATION")
        return self

    def change(self, key: str, value: bool | str) -> "DonTrainConfig":
        if type(key) is not str or key not in DON_TRAIN_KEYS:
            raise DonTrainSettingsError("UNKNOWN_DON_TRAIN_SETTING")
        return replace(self, **{key: value}).validated()

    def filter_presets(self) -> tuple[str, ...]:
        """L04: description-only keep policy; DOES NOT drop game items."""
        return (() if self.pickup_mode == "all" else ("discard_nonweapon",))

    def full_bag_threshold(self) -> int:
        """L04: Site-10 occupied-slot reference for future verified reader."""
        return 98 if self.pickup_no_cankhon else 100


@dataclass(frozen=True)
class DonTrainSnapshot:
    value: DonTrainConfig
    file_bytes: bytes


class DonTrainSettingsStore:
    """Isolated original [DonVang] Train family reader/one-key atomic writer."""

    def __init__(self, path: str | Path):
        self.section = DonReturnSettingsStore(path)
        self.path = self.section.path

    @staticmethod
    def _entries(lines, begin, end):
        found = {}
        if begin is None:
            return found
        for i in range(begin + 1, end):
            line = lines[i]
            if _DON_TRAIN_PREFIX.match(line) is None:
                continue
            match = _KEYLINE.fullmatch(line)
            if match is None:
                raise DonTrainSettingsError("MALFORMED_DON_TRAIN_KEY")
            key = match.group(2).casefold()
            if key not in DON_TRAIN_KEYS or key in found:
                raise DonTrainSettingsError("DUPLICATE_DON_TRAIN_KEY")
            if i + 1 < end and lines[i + 1][:1] in (" ", "\t"):
                raise DonTrainSettingsError("AMBIGUOUS_DON_TRAIN_CONTINUATION")
            found[key] = (i, match.group(4).strip())
        return found

    @staticmethod
    def _parse_bool(raw: str, key: str) -> bool:
        normalized = raw.casefold()
        if normalized in _TRUE:
            return True
        if normalized in _FALSE:
            return False
        raise DonTrainSettingsError("INVALID_DON_BOOL_" + key.upper())

    @classmethod
    def _decode(cls, found):
        defaults = DonTrainConfig()
        vals = {}
        for key in DON_BOOL_KEYS:
            row = found.get(key)
            vals[key] = (cls._parse_bool(row[1], key)
                         if row is not None else getattr(defaults, key))
        for key in DON_OTHER_KEYS:
            row = found.get(key)
            vals[key] = row[1] if row is not None else getattr(defaults, key)
        return DonTrainConfig(**vals).validated()

    def load(self) -> DonTrainSnapshot:
        with _settings_lock:
            try:
                raw, lines, _, begin, end = self.section._read()
            except DonReturnSettingsError as exc:
                raise DonTrainSettingsError("UNSAFE_DON_TRAIN_SETTINGS") from exc
            return DonTrainSnapshot(
                self._decode(self._entries(lines, begin, end)), raw)

    def save_change(self, key: str, value: bool | str, *,
                    expected_bytes: bytes) -> DonTrainSnapshot:
        if (type(key) is not str or key not in DON_TRAIN_KEYS
                or type(expected_bytes) is not bytes):
            raise DonTrainSettingsError("INVALID_DON_TRAIN_WRITE_REQUEST")
        with _settings_lock:
            try:
                raw, lines, nl, begin, end = self.section._read()
            except DonReturnSettingsError as exc:
                raise DonTrainSettingsError("UNSAFE_DON_TRAIN_SETTINGS") from exc
            if expected_bytes != raw:
                raise DonTrainSettingsError("STALE_DON_TRAIN_SETTINGS")
            found = self._entries(lines, begin, end)
            config = self._decode(found).change(key, value)
            actual = getattr(config, key)
            # Keep boolean serialization matching the EXISTING option when
            # possible. New option uses numeric 1/0 without changing others.
            if key in DON_BOOL_KEYS:
                previous = found.get(key, (None, ""))[1].casefold()
                if previous in ("true", "false"):
                    serialized = "True" if actual else "False"
                else:
                    serialized = "1" if actual else "0"
            else:
                serialized = actual
            changed = list(lines)
            if key in found:
                idx, _old = found[key]
                match = _KEYLINE.fullmatch(changed[idx])
                if match is None:
                    raise DonTrainSettingsError("MALFORMED_DON_TRAIN_KEY")
                changed[idx] = (
                    match.group(1) + match.group(2) + match.group(3)
                    + serialized + (match.group(5) or ""))
            elif begin is None:
                prefix = ("" if not changed or changed[-1].endswith(("\r", "\n"))
                          else nl)
                changed.append(
                    prefix + "[DonVang]" + nl +
                    f"{key} = {serialized}" + nl)
            else:
                if end > 0 and not changed[end - 1].endswith(("\r", "\n")):
                    raise DonTrainSettingsError("UNTERMINATED_DONVANG_SECTION")
                changed.insert(end, f"{key} = {serialized}" + nl)
            encoded = "".join(changed).encode("utf-8")
            if encoded == raw:
                return DonTrainSnapshot(config, raw)
            if len(encoded) > MAX_SETTINGS_BYTES:
                raise DonTrainSettingsError("DON_TRAIN_SETTINGS_TOO_LARGE")
            self.path.parent.mkdir(parents=True, exist_ok=True)
            fd, temp = tempfile.mkstemp(
                prefix="settings.", suffix=".tmp", dir=str(self.path.parent))
            try:
                with os.fdopen(fd, "wb") as output:
                    output.write(encoded)
                    output.flush()
                    os.fsync(output.fileno())
                on_disk = self.path.read_bytes() if self.path.exists() else b""
                if on_disk != raw:
                    raise DonTrainSettingsError("DON_TRAIN_SETTINGS_CHANGED")
                if self.path.exists():
                    backup = self.path.with_name(
                        "settings." + datetime.now().strftime("%Y%m%d") + ".ini")
                    if not backup.exists():
                        shutil.copy2(self.path, backup)
                os.replace(temp, self.path)
            except OSError as exc:
                raise DonTrainSettingsError("DON_TRAIN_SETTINGS_WRITE_FAILED") from exc
            finally:
                if os.path.exists(temp):
                    os.unlink(temp)
            return self.load()
