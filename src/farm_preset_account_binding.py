"""S122 H11: sync actual existing account Sell/Train ttk.Combobox widgets by preset name.

Original FarmTab: _refresh_coord_combos immediately propagates rename;
_apply_coord_to_all uses preset NAME (target sell/farm). No game action,
fabricated HWND/character, persistence of unknown account key encoding, or Proxy.
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
import weakref
from typing import Mapping, Sequence
from train_saved_coordinates import FarmCoordinate


def preset_names(rows: Sequence[FarmCoordinate]) -> tuple[str, ...]:
    if not isinstance(rows, (list, tuple)) or any(
        not isinstance(row, FarmCoordinate) for row in rows
    ):
        raise ValueError("INVALID_PRESET_ROWS")
    return tuple(row.name for row in rows)


def renamed_selection(name: str, changes: Mapping[str, str] | None) -> str:
    if not isinstance(name, str):
        raise ValueError("INVALID_NAME")
    return changes.get(name, name) if changes else name


class FarmAccountPresetBindings:
    """Actual caller-owned Tk combo pairs; Tk owner thread only."""

    def __init__(self):
        self._pairs: list[tuple] = []
        self._names: tuple[str, ...] = ()

    @staticmethod
    def _exists(combo) -> bool:
        try:
            return bool(combo is not None and combo.winfo_exists())
        except tk.TclError:
            return False

    def _live(self):
        kept, pairs = [], []
        for a, b in self._pairs:
            sell, farm = a(), b()
            if self._exists(sell) and self._exists(farm):
                kept.append((a, b))
                pairs.append((sell, farm))
        self._pairs = kept
        return pairs

    def active_count(self) -> int:
        return len(self._live())

    def register(self, sell: ttk.Combobox, farm: ttk.Combobox,
                 *, rows: Sequence[FarmCoordinate]) -> None:
        if (not isinstance(sell, ttk.Combobox)
                or not isinstance(farm, ttk.Combobox) or sell is farm
                or not self._exists(sell) or not self._exists(farm)):
            raise ValueError("NOT_EXISTING_TK_ACCOUNT_COMBOS")
        if any(s is sell or f is farm for s, f in self._live()):
            raise ValueError("DUPLICATE_COMBO_BINDING")
        names = preset_names(rows)
        self._pairs.append((weakref.ref(sell), weakref.ref(farm)))
        self._names = names
        sell.configure(values=names)
        farm.configure(values=names)

    def unregister(self, sell: ttk.Combobox, farm: ttk.Combobox) -> None:
        self._pairs = [(a, b) for a, b in self._pairs
                       if a() is not sell or b() is not farm]

    def refresh(self, rows: Sequence[FarmCoordinate],
                rename_map: Mapping[str, str] | None = None) -> int:
        names = preset_names(rows)
        if rename_map is not None and (
            not isinstance(rename_map, Mapping)
            or any(not isinstance(k, str) or not isinstance(v, str)
                   for k, v in rename_map.items())
        ):
            raise ValueError("INVALID_RENAME_MAP")
        self._names = names
        count = 0
        for sell, farm in self._live():
            for combo in (sell, farm):
                old = combo.get()
                combo.configure(values=names)
                new = renamed_selection(old, rename_map)
                if new != old:
                    combo.set(new)
            count += 1
        return count

    def editable_count(self, target: str) -> int:
        """Count real, currently permission-enabled H11 selectors."""
        if target not in ("sell", "farm"):
            raise ValueError("UNKNOWN_H11_TARGET")
        index = 0 if target == "sell" else 1
        return sum(not pair[index].instate(["disabled"])
                   for pair in self._live())

    def restore_if_known(self, combo: ttk.Combobox, name: str) -> bool:
        if (not isinstance(combo, ttk.Combobox) or not self._exists(combo)
                or not isinstance(name, str) or name not in self._names):
            return False
        combo.set(name)
        return True

    def apply_to_all(self, preset_name: str, *, target: str) -> int:
        if target not in ("sell", "farm"):
            raise ValueError("UNKNOWN_H11_TARGET")
        if not isinstance(preset_name, str) or preset_name not in self._names:
            raise ValueError("UNKNOWN_PRESET_NAME")
        count = 0
        for sell, farm in self._live():
            chosen = sell if target == "sell" else farm
            if chosen.instate(["disabled"]):
                continue
            chosen.set(preset_name)
            count += 1
        return count
