"""S130 H01/H02/B05 frozen original Train town sell/medicine SETTINGS ONLY.

EXE was inspected directly: source bytes lock [Farm] keys, four SELL_MAP_LIST
cities, HP/MP item labels, "Bán trang bị", "Bớt lại" and numeric entry
validation. Exact missing-config defaults for some fields / real NPC shopping
runtime are NOT safely recovered, so conservative local defaults are explicitly
NOT claims about the original GUI. No game actions/entitlement/Proxy.

Writes precisely ten original [Farm] town sell/medicine keys and preserves all
existing H02 town, S129 train, H11 coord and other section bytes.
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
from train_saved_coordinates import FarmCoordinatesStore, FarmCoordinateError, MAX_SETTINGS_BYTES
from farm_town_config import FarmTownSettingsStore, _KEYLINE

TRADE_KEYS = (
    "sell_equip", "sell_map", "sell_tab", "buy_hp", "hp_item",
    "hp_qty", "buy_mp", "mp_item", "mp_qty", "meds_map",
)
TRADE_BOOL_KEYS = ("sell_equip", "buy_hp", "buy_mp")
SELL_MAP_LIST = ("Đại Lý", "Lạc Dương", "Tô Châu", "Lâu Lan")
HP_ITEMS = ("Hành huyết tán", "Hoạt huyết tán", "Kim sang dược")
MP_ITEMS = ("Hành khí tán", "Hoài linh đan", "Qui linh hoàn")
TRUE_WORDS = frozenset(("1", "yes", "true", "on"))
FALSE_WORDS = frozenset(("0", "no", "false", "off"))
_TRADE_PREFIX = re.compile(
    r"^[ \t]*(sell_equip|sell_map|sell_tab|buy_hp|hp_item|hp_qty|"
    r"buy_mp|mp_item|mp_qty|meds_map)\b", re.I
)


class FarmTownTradeError(ValueError):
    """Fail closed rather than corrupt or silently alter unrelated settings."""


@dataclass(frozen=True)
class TownTradeConfig:
    # Off/empty are LOCAL safe fallback values, not original-default parity.
    sell_equip: bool = False
    sell_map: str = ""
    sell_tab: str = "0"
    buy_hp: bool = False
    hp_item: str = HP_ITEMS[0]
    hp_qty: str = "50"
    buy_mp: bool = False
    mp_item: str = MP_ITEMS[0]
    mp_qty: str = "50"
    meds_map: str = ""

    def validated(self) -> "TownTradeConfig":
        if any(type(getattr(self, key)) is not bool for key in TRADE_BOOL_KEYS):
            raise FarmTownTradeError("INVALID_TOWN_TRADE_BOOLEAN")
        for key in ("sell_map", "meds_map"):
            val = getattr(self, key)
            # Saved manual coordinates can outlive their preset; keep the
            # stored name but never claim a live game action can resolve it.
            if (type(val) is not str or len(val) > 180
                    or any(c in val for c in ("\r", "\n", "\x00"))):
                raise FarmTownTradeError("INVALID_TOWN_DESTINATION")
        if (self.hp_item not in HP_ITEMS or self.mp_item not in MP_ITEMS
                or type(self.hp_item) is not str or type(self.mp_item) is not str):
            raise FarmTownTradeError("UNKNOWN_TOWN_MEDICINE")
        for key in ("sell_tab", "hp_qty", "mp_qty"):
            val = getattr(self, key)
            if (type(val) is not str or not val or not val.isascii()
                    or not val.isdecimal() or len(val) > 9):
                raise FarmTownTradeError("INVALID_TOWN_NUMERIC")
        return self

    def change(self, key: str, value: str | bool) -> "TownTradeConfig":
        if type(key) is not str or key not in TRADE_KEYS:
            raise FarmTownTradeError("UNSUPPORTED_TOWN_SETTING")
        return replace(self, **{key: value}).validated()


@dataclass(frozen=True)
class TownTradeSnapshot:
    value: TownTradeConfig
    file_bytes: bytes


class TownTradeStore:
    """Real settings.ini edits, never issues sell, buy or movement commands."""

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path is not None else settings_path()

    @staticmethod
    def _entries(lines, begin, end):
        entries = {}
        if begin is None:
            return entries
        for i in range(begin + 1, end):
            if not _TRADE_PREFIX.match(lines[i]):
                continue
            m = _KEYLINE.fullmatch(lines[i])
            if m is None:
                raise FarmTownTradeError("MALFORMED_TRADE_SETTING")
            name = m.group(2).casefold()
            if name not in TRADE_KEYS or name in entries:
                raise FarmTownTradeError("DUPLICATE_OR_UNKNOWN_TRADE_SETTING")
            if i + 1 < end and lines[i + 1][:1] in (" ", "\t"):
                raise FarmTownTradeError("AMBIGUOUS_TRADE_CONTINUATION")
            entries[name] = (i, m.group(4).strip())
        return entries

    @staticmethod
    def _decode(entries):
        defaults = TownTradeConfig()
        data = {}
        for key in TRADE_KEYS:
            value = entries.get(key, (-1, getattr(defaults, key)))[1]
            if key in TRADE_BOOL_KEYS:
                if type(value) is bool:
                    data[key] = value
                elif value.casefold() in TRUE_WORDS:
                    data[key] = True
                elif value.casefold() in FALSE_WORDS:
                    data[key] = False
                else:
                    raise FarmTownTradeError("INVALID_SAVED_TRADE_BOOLEAN")
            else:
                data[key] = value
        return TownTradeConfig(**data).validated()

    def _read(self):
        try:
            return FarmTownSettingsStore(self.path)._read()
        except (FarmCoordinateError, ValueError) as exc:
            raise FarmTownTradeError("UNSAFE_TRADE_SETTINGS") from exc

    def load(self) -> TownTradeSnapshot:
        with _settings_lock:
            data, lines, _, begin, end = self._read()
            return TownTradeSnapshot(
                self._decode(self._entries(lines, begin, end)), data)

    def save(self, value: TownTradeConfig, *, expected_bytes: bytes) -> TownTradeSnapshot:
        if type(value) is not TownTradeConfig or type(expected_bytes) is not bytes:
            raise FarmTownTradeError("INVALID_TRADE_SAVE_REQUEST")
        value.validated()
        with _settings_lock:
            old, lines, newline, begin, end = self._read()
            if old != expected_bytes:
                raise FarmTownTradeError("STALE_TRADE_SETTINGS")
            prior = self._entries(lines, begin, end)
            self._decode(prior)
            wanted = {key: ("True" if getattr(value, key) else "False")
                      if key in TRADE_BOOL_KEYS else getattr(value, key)
                      for key in TRADE_KEYS}
            updated = list(lines)
            for key, (i, _) in prior.items():
                m = _KEYLINE.fullmatch(lines[i])
                if m is None:
                    raise FarmTownTradeError("MALFORMED_TRADE_SETTING")
                updated[i] = (m.group(1)+m.group(2)+m.group(3)
                              +wanted[key]+(m.group(5) or ""))
            missing = [f"{key} = {wanted[key]}{newline}" for key in TRADE_KEYS
                       if key not in prior]
            if begin is None:
                prefix = ("" if not updated or updated[-1].endswith(("\r", "\n"))
                          else newline)
                output = "".join(updated) + prefix + "[Farm]" + newline + "".join(missing)
            else:
                if (missing and end > 0
                        and not updated[end - 1].endswith(("\r", "\n"))):
                    raise FarmTownTradeError("UNTERMINATED_FARM_SECTION")
                updated[end:end] = missing
                output = "".join(updated)
            encoded = output.encode("utf-8")
            if encoded == old:
                return TownTradeSnapshot(value, old)
            if len(encoded) > MAX_SETTINGS_BYTES:
                raise FarmTownTradeError("TRADE_SETTINGS_TOO_LARGE")
            self.path.parent.mkdir(parents=True, exist_ok=True)
            fd, temporary = tempfile.mkstemp(
                prefix="settings.", suffix=".tmp", dir=str(self.path.parent))
            try:
                with os.fdopen(fd, "wb") as stream:
                    stream.write(encoded)
                    stream.flush()
                    os.fsync(stream.fileno())
                actual = self.path.read_bytes() if self.path.exists() else b""
                if actual != old:
                    raise FarmTownTradeError("TRADE_SETTINGS_CHANGED_CONCURRENTLY")
                if self.path.exists():
                    backup = self.path.with_name(
                        "settings."+datetime.now().strftime("%Y%m%d")+".ini")
                    if not backup.exists():
                        shutil.copy2(self.path, backup)
                os.replace(temporary, self.path)
            except OSError as exc:
                raise FarmTownTradeError("TRADE_SETTINGS_WRITE_FAILED") from exc
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
            return TownTradeSnapshot(value, encoded)


def town_destination_choices(path: str | Path | None = None):
    """Frozen four built-in shop-city labels + valid saved H11 coordinates."""
    try:
        loaded = FarmCoordinatesStore(path).load()
    except FarmCoordinateError as exc:
        raise FarmTownTradeError("UNSAFE_SAVED_TOWN_COORDS") from exc
    if loaded.skipped_retired_map_ids:
        raise FarmTownTradeError("RETIRED_SAVED_TOWN_COORDS")
    manual = tuple(row.name for row in loaded.rows)
    if (len(manual) != len(set(manual))
            or any(not name or name in SELL_MAP_LIST for name in manual)):
        raise FarmTownTradeError("AMBIGUOUS_SAVED_TOWN_COORDS")
    return SELL_MAP_LIST + manual
