"""S181 / PLAN L02-L03: persistent [DonVang] return-mode/priority settings.

Original-backed, independent of TLM license, character readers and senders.
Exact keys: town_condition, loop_minutes, nav_priority_1..4.
Values: cycle/full_bag_timer (legacy full_bag) and Phù 1/2/3/Ngựa/"";
per L02/L03/L10. This is NOT a DonVang execution controller.

Only one user-edited option is written at a time. Unrelated settings.ini
bytes, receiver/account config, Farm settings and secrets are preserved.
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
    FarmCoordinateError, FarmCoordinatesStore, MAX_SETTINGS_BYTES, _HEADER,
)
from farm_town_config import _KEYLINE

DON_MODES = ("full_bag_timer", "cycle")
DON_RETURN_OPTIONS = (
    ("Khi đầy túi", "full_bag_timer"),
    ("Theo chu kỳ (phút)", "cycle"),
)
NAV_OPTIONS = ("", "Phù 1", "Phù 2", "Phù 3", "Ngựa")
NAV_DEFAULTS = ("Phù 1", "Phù 2", "Phù 3", "Ngựa")
RETURN_KEYS = ("town_condition", "loop_minutes",
               "nav_priority_1", "nav_priority_2",
               "nav_priority_3", "nav_priority_4")
_RETURN_PREFIX = re.compile(
    r"^[ \t]*(town_condition|loop_minutes|nav_priority_[1-4])\b", re.I)


class DonReturnSettingsError(ValueError):
    """Unproved, stale or malformed Dồn settings cannot be overwritten."""


@dataclass(frozen=True)
class DonReturnConfig:
    mode: str = "cycle"
    minutes: str = "30"
    navigation: tuple[str, str, str, str] = NAV_DEFAULTS

    def validated(self) -> "DonReturnConfig":
        if type(self.mode) is not str or self.mode not in DON_MODES:
            raise DonReturnSettingsError("UNKNOWN_DON_RETURN_MODE")
        # Original exact Spinbox range/clamping is not recovered.
        if (type(self.minutes) is not str or not self.minutes
                or not self.minutes.isascii() or not self.minutes.isdecimal()
                or len(self.minutes) > 9):
            raise DonReturnSettingsError("INVALID_DON_RETURN_MINUTES")
        if (type(self.navigation) is not tuple
                or len(self.navigation) != 4
                or any(type(v) is not str or v not in NAV_OPTIONS
                       for v in self.navigation)):
            raise DonReturnSettingsError("INVALID_DON_NAV_PRIORITY")
        unique = [x for x in self.navigation if x]
        if len(unique) != len(set(unique)):
            # Original handling of already-duplicated legacy config UNKNOWN.
            # Do not invent a migration or silently throw away a priority.
            raise DonReturnSettingsError("DUPLICATE_DON_NAV_PRIORITY")
        return self

    def change(self, key: str, value: str) -> "DonReturnConfig":
        if type(key) is not str or type(value) is not str:
            raise DonReturnSettingsError("INVALID_DON_EDIT")
        if key == "town_condition":
            updated = replace(self, mode=value)
        elif key == "loop_minutes":
            updated = replace(self, minutes=value)
        elif key in RETURN_KEYS[2:]:
            index = int(key.rsplit("_", 1)[1]) - 1
            nav = list(self.navigation)
            nav[index] = value
            updated = replace(self, navigation=tuple(nav))
        else:
            raise DonReturnSettingsError("UNSUPPORTED_DON_RETURN_KEY")
        return updated.validated()

    def active_navigation(self) -> tuple[str, ...]:
        """L03: output priority list for the *sell-home* movement only."""
        return tuple(x for x in self.validated().navigation if x)


@dataclass(frozen=True)
class DonReturnSnapshot:
    value: DonReturnConfig
    file_bytes: bytes
    loaded_legacy_full_bag: bool = False


class DonReturnSettingsStore:
    """Strict UTF-8/byte-preserving isolated [DonVang] return-option writer."""

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path is not None else settings_path()

    def _read(self):
        try:
            raw, lines, newline = FarmCoordinatesStore(self.path)._lines()
        except (FarmCoordinateError, OSError, UnicodeError) as exc:
            raise DonReturnSettingsError("UNSAFE_DON_SETTINGS") from exc
        headers = []
        for pos, line in enumerate(lines):
            head = _HEADER.fullmatch(line.rstrip("\r\n"))
            if head:
                headers.append((pos, head.group(1).strip().casefold()))
        spans = [pos for pos, name in headers if name == "donvang"]
        if len(spans) > 1:
            raise DonReturnSettingsError("DUPLICATE_DONVANG_SECTION")
        begin = spans[0] if spans else None
        end = (next((pos for pos, _ in headers if pos > begin), len(lines))
               if begin is not None else len(lines))
        return raw, lines, newline, begin, end

    @staticmethod
    def _entries(lines, begin, end):
        found = {}
        if begin is None:
            return found
        for pos in range(begin + 1, end):
            line = lines[pos]
            if not _RETURN_PREFIX.match(line):
                continue
            match = _KEYLINE.fullmatch(line)
            if match is None:
                raise DonReturnSettingsError("MALFORMED_DON_RETURN_OPTION")
            key = match.group(2).casefold()
            if key not in RETURN_KEYS or key in found:
                raise DonReturnSettingsError("AMBIGUOUS_DON_RETURN_OPTION")
            if pos + 1 < end and lines[pos + 1][:1] in (" ", "\t"):
                raise DonReturnSettingsError("AMBIGUOUS_DON_MULTILINE_OPTION")
            found[key] = (pos, match.group(4).strip())
        return found

    @staticmethod
    def _decode(found):
        original_mode = found.get("town_condition", (None, "cycle"))[1]
        legacy = original_mode == "full_bag"
        mode = "full_bag_timer" if legacy else original_mode
        mins = found.get("loop_minutes", (None, "30"))[1]
        navigation = tuple(found.get(
            f"nav_priority_{i}", (None, NAV_DEFAULTS[i - 1]))[1]
                           for i in range(1, 5))
        return DonReturnConfig(mode, mins, navigation).validated(), legacy

    def load(self) -> DonReturnSnapshot:
        with _settings_lock:
            raw, lines, _, begin, end = self._read()
            value, legacy = self._decode(self._entries(lines, begin, end))
            return DonReturnSnapshot(value, raw, legacy)

    def save_change(self, key: str, value: str, *,
                    expected_bytes: bytes) -> DonReturnSnapshot:
        if (type(key) is not str or key not in RETURN_KEYS
                or type(value) is not str or type(expected_bytes) is not bytes):
            raise DonReturnSettingsError("INVALID_DON_RETURN_WRITE_REQUEST")
        with _settings_lock:
            raw, lines, newline, begin, end = self._read()
            if raw != expected_bytes:
                raise DonReturnSettingsError("STALE_DON_RETURN_SETTINGS")
            found = self._entries(lines, begin, end)
            previous, _ = self._decode(found)
            updated = previous.change(key, value)
            # Even if a legacy "full_bag" was loaded, write only the
            # user-edited key. A different option must not silently migrate it.
            actual_value = getattr(updated, "mode" if key == "town_condition"
                                   else "minutes") if key in RETURN_KEYS[:2] else (
                                       updated.navigation[int(key[-1]) - 1])
            modified = list(lines)
            if key in found:
                pos, _ = found[key]
                match = _KEYLINE.fullmatch(modified[pos])
                if match is None:
                    raise DonReturnSettingsError("MALFORMED_DON_RETURN_OPTION")
                modified[pos] = (match.group(1) + match.group(2)
                                 + match.group(3) + actual_value
                                 + (match.group(5) or ""))
            elif begin is None:
                prefix = ("" if not modified or modified[-1].endswith(("\r", "\n"))
                          else newline)
                modified.append(prefix + "[DonVang]" + newline
                                + f"{key} = {actual_value}" + newline)
            else:
                if end > 0 and not modified[end - 1].endswith(("\r", "\n")):
                    raise DonReturnSettingsError("UNTERMINATED_DONVANG_SECTION")
                modified.insert(end, f"{key} = {actual_value}" + newline)
            encoded = "".join(modified).encode("utf-8")
            if encoded == raw:
                return DonReturnSnapshot(updated, raw,
                                         found.get("town_condition",
                                                   (None, ""))[1] == "full_bag")
            if len(encoded) > MAX_SETTINGS_BYTES:
                raise DonReturnSettingsError("DON_RETURN_SETTINGS_TOO_LARGE")
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
                    raise DonReturnSettingsError(
                        "DON_RETURN_SETTINGS_CHANGED_CONCURRENTLY")
                if self.path.exists():
                    backup = self.path.with_name(
                        "settings." + datetime.now().strftime("%Y%m%d") + ".ini")
                    if not backup.exists():
                        shutil.copy2(self.path, backup)
                os.replace(tmp, self.path)
            except OSError as exc:
                raise DonReturnSettingsError("DON_RETURN_SETTINGS_WRITE_FAILED") from exc
            finally:
                if os.path.exists(tmp):
                    os.unlink(tmp)
            return self.load()
