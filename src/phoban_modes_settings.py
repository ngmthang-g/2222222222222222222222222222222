"""S185: original J01/J03/J08/J09/J10 Phó Bản local mode persistence.

Each checkbox is a real [Settings] key. This is CONFIG ONLY: it does not
start team/follow/pickup/discard/buff game workers. Existing schedules,
legacy keys, other module data, original license and client are untouched.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
import os
from pathlib import Path
import re
import shutil
import tempfile

from farm_town_config import _KEYLINE
from phoban_schedule_settings import PhoBanConfigStore, PhoBanConfigError
from settings_store import _settings_lock
from train_saved_coordinates import MAX_SETTINGS_BYTES


MODE_LABELS = (
    ("phoban_recreate_team", "Tạo lại đội"),
    ("phoban_follow", "Theo sau đội trưởng"),
    ("phoban_pickup", "Nhặt không hồ lô"),
    ("phoban_discard_equip", "Vứt trang bị"),
    ("phoban_discard_items", "Vứt vật phẩm"),
    ("phoban_discard_meds", "Vứt thuốc"),
    ("phoban_nga_my_buff", "Nga My buff (Sát Tinh)"),
)
MODE_KEYS = tuple(k for k, _ in MODE_LABELS)
_MODE_PREFIX = re.compile(
    r"^[ \t]*(?:"
    + "|".join(re.escape(key) for key in MODE_KEYS)
    + r")\b", re.I)
_TRUE = frozenset(("1", "true", "yes", "on"))
_FALSE = frozenset(("0", "false", "no", "off"))


class PhoBanModesError(ValueError):
    """No write on malformed, ambiguous, or concurrently changed settings."""


@dataclass(frozen=True)
class PhoBanModes:
    phoban_recreate_team: bool = False
    phoban_follow: bool = False
    phoban_pickup: bool = False
    phoban_discard_equip: bool = False
    phoban_discard_items: bool = False
    phoban_discard_meds: bool = False
    phoban_nga_my_buff: bool = False

    def validated(self) -> "PhoBanModes":
        if any(type(getattr(self, key)) is not bool for key in MODE_KEYS):
            raise PhoBanModesError("INVALID_PHOBAN_MODE_VALUE")
        return self

    def change(self, key: str, checked: bool) -> "PhoBanModes":
        if type(key) is not str or key not in MODE_KEYS or type(checked) is not bool:
            raise PhoBanModesError("UNSUPPORTED_PHOBAN_MODE_CHANGE")
        return replace(self, **{key: checked}).validated()

    def enabled_discard_presets(self) -> tuple[str, ...]:
        """Documented J08 key ordering, metadata only: never drops items."""
        return tuple(
            preset for key, preset in (
                ("phoban_discard_equip", "discard_equip"),
                ("phoban_discard_items", "discard_items"),
                ("phoban_discard_meds", "discard_meds"),
            ) if getattr(self, key))


@dataclass(frozen=True)
class PhoBanModesSnapshot:
    modes: PhoBanModes
    file_bytes: bytes


class PhoBanModesStore:
    """Single-key INI writer, preserving schedule and other tabs byte-exact."""

    def __init__(self, path: str | Path):
        self.settings = PhoBanConfigStore(path)
        self.path = self.settings.path

    @staticmethod
    def _entries(lines, begin, end):
        result = {}
        if begin is None:
            return result
        for i in range(begin + 1, end):
            if not _MODE_PREFIX.match(lines[i]):
                continue
            match = _KEYLINE.fullmatch(lines[i])
            if match is None:
                raise PhoBanModesError("MALFORMED_PHOBAN_MODE_OPTION")
            key = match.group(2).casefold()
            if key not in MODE_KEYS or key in result:
                raise PhoBanModesError("DUPLICATE_OR_INVALID_PHOBAN_MODE")
            if i + 1 < end and lines[i + 1][:1] in (" ", "\t"):
                raise PhoBanModesError("AMBIGUOUS_PHOBAN_MODE_CONTINUATION")
            result[key] = (i, match.group(4).strip())
        return result

    @staticmethod
    def _as_bool(raw: str):
        v = raw.casefold()
        if v in _TRUE:
            return True
        if v in _FALSE:
            return False
        raise PhoBanModesError("UNKNOWN_PHOBAN_MODE_ENCODING")

    @classmethod
    def _decode(cls, existing):
        vals = {}
        for k in MODE_KEYS:
            vals[k] = cls._as_bool(existing[k][1]) if k in existing else False
        return PhoBanModes(**vals).validated()

    def _current(self):
        try:
            raw, lines, nl, begin, end, _ = self.settings._read()
        except PhoBanConfigError as exc:
            raise PhoBanModesError("UNSAFE_PHOBAN_MODE_SETTINGS") from exc
        existing = self._entries(lines, begin, end)
        return raw, lines, nl, begin, end, existing, self._decode(existing)

    def load(self) -> PhoBanModesSnapshot:
        with _settings_lock:
            raw, _, _, _, _, _, modes = self._current()
            return PhoBanModesSnapshot(modes, raw)

    def save_change(self, key: str, checked: bool, *,
                    expected_bytes: bytes) -> PhoBanModesSnapshot:
        if (type(expected_bytes) is not bytes
                or type(key) is not str or key not in MODE_KEYS
                or type(checked) is not bool):
            raise PhoBanModesError("INVALID_PHOBAN_MODE_SAVE_REQUEST")
        with _settings_lock:
            raw, lines, nl, begin, end, existing, modes = self._current()
            if expected_bytes != raw:
                raise PhoBanModesError("STALE_PHOBAN_MODE_SETTINGS")
            next_modes = modes.change(key, checked)
            old = existing.get(key)
            # Respect explicit legacy true/false format when it exists.
            previous = old[1].casefold() if old else ""
            if previous in ("true", "false"):
                serialized = "True" if checked else "False"
            else:
                serialized = "1" if checked else "0"
            target = list(lines)
            if old:
                i, _ = old
                match = _KEYLINE.fullmatch(target[i])
                if match is None:
                    raise PhoBanModesError("MALFORMED_PHOBAN_MODE_OPTION")
                target[i] = (match.group(1) + match.group(2)
                             + match.group(3) + serialized
                             + (match.group(5) or ""))
            elif begin is None:
                prefix = ("" if not target or target[-1].endswith(("\r", "\n"))
                          else nl)
                target.append(prefix + "[Settings]" + nl
                              + f"{key} = {serialized}" + nl)
            else:
                if end and not target[end - 1].endswith(("\r", "\n")):
                    raise PhoBanModesError("UNTERMINATED_SETTINGS_SECTION")
                target.insert(end, f"{key} = {serialized}" + nl)
            encoded = "".join(target).encode("utf-8")
            if encoded == raw:
                return PhoBanModesSnapshot(next_modes, raw)
            if len(encoded) > MAX_SETTINGS_BYTES:
                raise PhoBanModesError("PHOBAN_MODE_SETTINGS_TOO_LARGE")
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
                    raise PhoBanModesError("PHOBAN_MODE_SETTINGS_CHANGED")
                if self.path.exists():
                    backup = self.path.with_name(
                        "settings." + datetime.now().strftime("%Y%m%d") + ".ini")
                    if not backup.exists():
                        shutil.copy2(self.path, backup)
                os.replace(tmp, self.path)
            except OSError as exc:
                raise PhoBanModesError("PHOBAN_MODE_WRITE_FAILED") from exc
            finally:
                if os.path.exists(tmp):
                    os.unlink(tmp)
            return PhoBanModesSnapshot(next_modes, encoded)
