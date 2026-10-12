"""S180 / PLAN K16: genuine Daily top-configuration INI persistence.

The independent tool owns its implementation; it never calls TLM original
license/Info, and does NOT send any game action. Static authority:
docs/daily/K16_SHARED_INTEGRATION_FLOW.md, K03, K10, B08.

Write ONLY one user-edited Daily key in [Settings], preserving all other
original INI bytes. daily_move_mode versus legacy daily_tele_use precedence
remains unknown; never rewrite or silently migrate the legacy key.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
import os
from pathlib import Path
import re
import shutil
import tempfile

from settings_store import _settings_lock, settings_path
from train_saved_coordinates import (
    FarmCoordinatesStore, FarmCoordinateError, MAX_SETTINGS_BYTES, _HEADER,
)
from farm_town_config import _KEYLINE


_DAILY_BOOL_KEYS = frozenset({
    "daily_punish_heal",
    "daily_punish_discard_equip",
    "daily_punish_dc_reconnect",
    "daily_punish_respawn",
    "daily_treasure_heal",
    "daily_treasure_dc_reconnect",
    "daily_treasure_respawn",
})
_DAILY_INTEGER_KEYS = frozenset({
    "daily_punish_duration",
    "daily_treasure_map_tomb_dur",
})
_DAILY_OTHER_KEYS = frozenset({
    "daily_tele_hotkey",
    "daily_treasure_heal_map",
    "daily_move_mode",
})
# daily_tele_use is a read-only compatibility datum, NEVER overwritten here.
_DAILY_COMPAT_KEYS = frozenset({"daily_tele_use"})
DAILY_EDITABLE_KEYS = _DAILY_BOOL_KEYS | _DAILY_INTEGER_KEYS | _DAILY_OTHER_KEYS
DAILY_READ_KEYS = DAILY_EDITABLE_KEYS | _DAILY_COMPAT_KEYS
_DAILY_PREFIX = re.compile(r"^[ \t]*(daily_[A-Za-z0-9_]+)\b", re.I)
_TRUE = frozenset({"1", "true", "yes", "on"})
_FALSE = frozenset({"0", "false", "no", "off"})
TREASURE_HEAL_COORDS = {
    "Đại Lý": (43, 178),
    "Lạc Dương": (255, 126),
    "Tô Châu": (155, 252),
    "Lâu Lan": (27, 183),
}
PUNISH_MOVE_MODES = ("horse", "teleport")
PUNISH_HOTKEYS = ("", "1", "2", "3")


class DailyConfigError(ValueError):
    """Ambiguous/stale configuration must fail closed without clobbering."""


@dataclass(frozen=True)
class DailyTopConfig:
    # 15s is the captured B08 reference state (clean default not fully proven).
    # Treasure 30s, heal flags and reconnect/respawn defaults are static-backed.
    daily_punish_duration: str = "15"
    daily_move_mode: str = "horse"
    daily_tele_hotkey: str = ""
    daily_punish_heal: bool = False
    daily_punish_discard_equip: bool = False
    daily_punish_dc_reconnect: bool = True
    daily_punish_respawn: bool = True
    daily_treasure_map_tomb_dur: str = "30"
    daily_treasure_heal: bool = False
    daily_treasure_heal_map: str = "Tô Châu"
    daily_treasure_dc_reconnect: bool = True
    daily_treasure_respawn: bool = True

    def validated(self) -> "DailyTopConfig":
        for key in _DAILY_BOOL_KEYS:
            if type(getattr(self, key)) is not bool:
                raise DailyConfigError("INVALID_DAILY_BOOLEAN")
        for key in _DAILY_INTEGER_KEYS:
            value = getattr(self, key)
            # Original validator supports digit-oriented edits; exact upper
            # bound/zero behavior is UNKNOWN. Don't invent another clamp.
            if (type(value) is not str or not value
                    or not value.isascii() or not value.isdecimal()
                    or len(value) > 9):
                raise DailyConfigError("INVALID_DAILY_DURATION")
        if self.daily_move_mode not in PUNISH_MOVE_MODES:
            raise DailyConfigError("INVALID_DAILY_MOVE_MODE")
        if self.daily_tele_hotkey not in PUNISH_HOTKEYS:
            raise DailyConfigError("INVALID_DAILY_TELE_HOTKEY")
        if self.daily_treasure_heal_map not in TREASURE_HEAL_COORDS:
            raise DailyConfigError("UNKNOWN_DAILY_TREASURE_HEAL_MAP")
        return self

    def change(self, key: str, value: bool | str) -> "DailyTopConfig":
        if type(key) is not str or key not in DAILY_EDITABLE_KEYS:
            raise DailyConfigError("UNSUPPORTED_DAILY_CONFIG_KEY")
        return replace(self, **{key: value}).validated()


@dataclass(frozen=True)
class DailyTopSnapshot:
    value: DailyTopConfig
    file_bytes: bytes
    legacy_tele_use: str | None = None
    mode_conflict: bool = False


class DailyTopSettingsStore:
    """Strict byte-preserving writer; preserve unrelated [Settings] records."""

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path is not None else settings_path()

    def _read(self):
        try:
            raw, lines, newline = FarmCoordinatesStore(self.path)._lines()
        except (FarmCoordinateError, OSError, UnicodeError) as exc:
            raise DailyConfigError("UNSAFE_DAILY_SETTINGS") from exc
        sections = []
        for i, line in enumerate(lines):
            m = _HEADER.fullmatch(line.rstrip("\r\n"))
            if m:
                sections.append((i, m.group(1).strip().casefold()))
        found = [i for i, name in sections if name == "settings"]
        if len(found) > 1:
            raise DailyConfigError("DUPLICATE_SETTINGS_SECTION")
        start = found[0] if found else None
        end = (next((i for i, _ in sections if i > start), len(lines))
               if start is not None else len(lines))
        return raw, lines, newline, start, end

    @staticmethod
    def _entries(lines, start, end):
        found = {}
        if start is None:
            return found
        for i in range(start + 1, end):
            line = lines[i]
            if _DAILY_PREFIX.match(line) is None:
                continue
            parsed = _KEYLINE.fullmatch(line)
            if parsed is None:
                raise DailyConfigError("MALFORMED_DAILY_OPTION")
            key = parsed.group(2).casefold()
            if key not in DAILY_READ_KEYS:
                continue  # preserve unknown newer Daily keys without changes
            if key in found:
                raise DailyConfigError("DUPLICATE_DAILY_OPTION")
            if i + 1 < end and lines[i + 1][:1] in (" ", "\t"):
                raise DailyConfigError("AMBIGUOUS_DAILY_CONTINUATION")
            found[key] = (i, parsed.group(4).strip())
        return found

    @staticmethod
    def _bool(raw: str, key: str):
        low = raw.casefold()
        if low in _TRUE:
            return True
        if low in _FALSE:
            return False
        raise DailyConfigError("INVALID_DAILY_BOOLEAN_" + key.upper())

    @classmethod
    def _decode(cls, entries):
        defaults = DailyTopConfig()
        fields = {}
        for key in _DAILY_BOOL_KEYS:
            old = entries.get(key)
            fields[key] = (cls._bool(old[1], key)
                           if old is not None else getattr(defaults, key))
        for key in _DAILY_INTEGER_KEYS:
            old = entries.get(key)
            fields[key] = old[1] if old is not None else getattr(defaults, key)
        for key in ("daily_tele_hotkey", "daily_treasure_heal_map"):
            old = entries.get(key)
            fields[key] = old[1] if old is not None else getattr(defaults, key)
        mode = entries.get("daily_move_mode")
        legacy = entries.get("daily_tele_use")
        if mode is not None:
            # The original precedence over daily_tele_use is NOT proven.
            # Surface conflicts explicitly; do not silently overwrite either.
            fields["daily_move_mode"] = mode[1]
        elif legacy is not None:
            fields["daily_move_mode"] = (
                "teleport" if cls._bool(legacy[1], "daily_tele_use")
                else "horse")
        else:
            fields["daily_move_mode"] = defaults.daily_move_mode
        value = DailyTopConfig(**fields).validated()
        conflict = False
        if legacy is not None and mode is not None:
            legacy_mode = ("teleport" if cls._bool(legacy[1], "daily_tele_use")
                           else "horse")
            conflict = legacy_mode != value.daily_move_mode
        return value, legacy[1] if legacy else None, conflict

    def load(self) -> DailyTopSnapshot:
        with _settings_lock:
            raw, lines, _, start, end = self._read()
            value, old_tele, conflict = self._decode(
                self._entries(lines, start, end))
            return DailyTopSnapshot(value, raw, old_tele, conflict)

    def save_change(self, key: str, value: bool | str, *,
                    expected_bytes: bytes) -> DailyTopSnapshot:
        if (type(key) is not str or key not in DAILY_EDITABLE_KEYS
                or type(expected_bytes) is not bytes):
            raise DailyConfigError("INVALID_DAILY_WRITE_REQUEST")
        with _settings_lock:
            raw, lines, newline, start, end = self._read()
            if raw != expected_bytes:
                raise DailyConfigError("STALE_DAILY_SETTINGS")
            entries = self._entries(lines, start, end)
            current, legacy, _ = self._decode(entries)
            updated = current.change(key, value)
            serialized = (
                ("1" if value else "0") if key in _DAILY_BOOL_KEYS
                else str(value))
            modified = list(lines)
            if key in entries:
                pos, _ = entries[key]
                match = _KEYLINE.fullmatch(modified[pos])
                if match is None:
                    raise DailyConfigError("MALFORMED_DAILY_OPTION")
                modified[pos] = (
                    match.group(1) + match.group(2) + match.group(3)
                    + serialized + (match.group(5) or ""))
            elif start is None:
                prefix = ("" if not modified or modified[-1].endswith(("\r", "\n"))
                          else newline)
                modified.append(prefix + "[Settings]" + newline
                                + f"{key} = {serialized}" + newline)
            else:
                if end > 0 and not modified[end-1].endswith(("\r", "\n")):
                    raise DailyConfigError("UNTERMINATED_SETTINGS_SECTION")
                modified.insert(end, f"{key} = {serialized}" + newline)
            encoded = "".join(modified).encode("utf-8")
            if encoded == raw:
                return DailyTopSnapshot(updated, raw, legacy,
                                        self._decode(entries)[2])
            if len(encoded) > MAX_SETTINGS_BYTES:
                raise DailyConfigError("DAILY_SETTINGS_TOO_LARGE")
            self.path.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(
                prefix="settings.", suffix=".tmp", dir=str(self.path.parent))
            try:
                with os.fdopen(fd, "wb") as out:
                    out.write(encoded)
                    out.flush()
                    os.fsync(out.fileno())
                actual = self.path.read_bytes() if self.path.exists() else b""
                if actual != raw:
                    raise DailyConfigError("DAILY_SETTINGS_CHANGED_CONCURRENTLY")
                if self.path.exists():
                    backup = self.path.with_name(
                        "settings." + datetime.now().strftime("%Y%m%d") + ".ini")
                    if not backup.exists():
                        shutil.copy2(self.path, backup)
                os.replace(tmp, self.path)
            except OSError as exc:
                raise DailyConfigError("DAILY_SETTINGS_WRITE_FAILED") from exc
            finally:
                if os.path.exists(tmp):
                    os.unlink(tmp)
            return self.load()
