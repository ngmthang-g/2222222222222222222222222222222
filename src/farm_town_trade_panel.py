"""S130: REAL Tk source-backed hidden H02 town trade/medicine configuration.

Independent mountable child of existing S128 town.lower, not a replacement
FarmTab, not a fake player. This reconstructs CONFIG ONLY: no NPCShop,
network calls, anti-auth shortcuts, potion purchases or clicks.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from farm_town_trade_settings import (
    TRADE_BOOL_KEYS, HP_ITEMS, MP_ITEMS, TownTradeConfig, TownTradeStore,
    TownTradeSnapshot, FarmTownTradeError, town_destination_choices,
)
from permission_guard import PermissionGuard


class TkFarmTownTradeSettings(ttk.Frame):
    """Actual controls persist genuine [Farm] keys to real settings.ini."""

    def __init__(self, parent, *, store: TownTradeStore | None = None,
                 permission_guard: PermissionGuard | None = None,
                 running_count: Callable[[], int] | None = None):
        super().__init__(parent)
        self.store = store if store is not None else TownTradeStore()
        self.guard = permission_guard
        self.running_count = running_count
        self._closed = False
        self._blocked = False
        self._restoring = False
        self.error: str | None = None
        self.snapshot: TownTradeSnapshot | None = None
        self.destination_choices: tuple[str, ...] = ()
        try:
            self.snapshot = self.store.load()
            self.destination_choices = town_destination_choices(self.store.path)
        except Exception as exc:
            self._blocked = True
            self.error = type(exc).__name__
        initial = self.snapshot.value if self.snapshot else TownTradeConfig()
        self.vars = {
            key: (tk.BooleanVar(master=self, value=getattr(initial, key))
                  if key in TRADE_BOOL_KEYS
                  else tk.StringVar(master=self, value=getattr(initial, key)))
            for key in TownTradeConfig.__dataclass_fields__
        }
        self.widgets: dict[str, ttk.Widget] = {}
        self.group = ttk.LabelFrame(self, text="Khi về thành:")
        self.group.pack(fill="x", padx=5, pady=(3, 5))
        first = ttk.Frame(self.group)
        first.pack(fill="x", padx=5, pady=2)
        self.widgets["sell_equip"] = ttk.Checkbutton(
            first, text="Bán trang bị", variable=self.vars["sell_equip"],
            command=lambda: self._on_flag("sell_equip"))
        self.widgets["sell_equip"].pack(side="left", padx=(0, 5))
        self._combo(first, "sell_map", self.destination_choices, width=17)
        ttk.Label(first, text="Bớt lại:").pack(side="left", padx=(6, 2))
        self._numeric(first, "sell_tab", width=5)
        second = ttk.Frame(self.group)
        second.pack(fill="x", padx=5, pady=2)
        self.widgets["buy_hp"] = ttk.Checkbutton(
            second, text="Mua HP", variable=self.vars["buy_hp"],
            command=lambda: self._on_flag("buy_hp"))
        self.widgets["buy_hp"].pack(side="left")
        self._combo(second, "hp_item", HP_ITEMS, width=18)
        ttk.Label(second, text="Số lượng:").pack(side="left", padx=(4, 2))
        self._numeric(second, "hp_qty", width=6)
        third = ttk.Frame(self.group)
        third.pack(fill="x", padx=5, pady=2)
        self.widgets["buy_mp"] = ttk.Checkbutton(
            third, text="Mua MP", variable=self.vars["buy_mp"],
            command=lambda: self._on_flag("buy_mp"))
        self.widgets["buy_mp"].pack(side="left")
        self._combo(third, "mp_item", MP_ITEMS, width=18)
        ttk.Label(third, text="Số lượng:").pack(side="left", padx=(4, 2))
        self._numeric(third, "mp_qty", width=6)
        fourth = ttk.Frame(self.group)
        fourth.pack(fill="x", padx=5, pady=2)
        ttk.Label(fourth, text="Tọa độ Dược:").pack(side="left")
        self._combo(fourth, "meds_map", self.destination_choices, width=22)
        self.status = ttk.Label(self, text="", anchor="w")
        self.status.pack(fill="x", padx=5)
        self.reapply_permission()
        if self._blocked:
            self.status.configure(text="Cấu hình bán/mua chưa an toàn để chỉnh sửa")
        self.bind("<Destroy>", self._on_destroy, add="+")

    def _combo(self, parent, key, options, *, width):
        cb = ttk.Combobox(
            parent, textvariable=self.vars[key], state="disabled",
            values=options, width=width)
        cb.pack(side="left", padx=(4, 1))
        cb.bind("<<ComboboxSelected>>", lambda _ev, k=key: self._on_select(k),
                add="+")
        self.widgets[key] = cb

    def _numeric(self, parent, key, *, width):
        entry = ttk.Entry(parent, textvariable=self.vars[key], width=width)
        entry.pack(side="left", padx=(1, 5))
        entry.bind("<Return>", lambda _ev, k=key: self._on_numeric(k), add="+")
        entry.bind("<FocusOut>", lambda _ev, k=key: self._on_numeric(k), add="+")
        self.widgets[key] = entry

    def _permitted(self):
        if (self._closed or self._blocked or type(self.guard) is not PermissionGuard
                or not callable(self.running_count)):
            return False
        try:
            count = self.running_count()
            return (type(count) is int and count > 0
                    and self.guard.snapshot.has_verified_payload
                    and self.guard.has_permission_with_limit("farm_tab", count))
        except Exception:
            return False

    def reapply_permission(self):
        valid = self._permitted()
        for key, widget in self.widgets.items():
            if key in ("sell_map", "meds_map", "hp_item", "mp_item"):
                state = "readonly" if valid else "disabled"
            else:
                state = "normal" if valid else "disabled"
            widget.configure(state=state)

    def _restore(self):
        if self.snapshot is None:
            return
        self._restoring = True
        try:
            for key in self.vars:
                self.vars[key].set(getattr(self.snapshot.value, key))
        finally:
            self._restoring = False

    def _commit(self, candidate: TownTradeConfig):
        if self._closed or self._restoring or not self._permitted() or self.snapshot is None:
            self._restore()
            return False
        try:
            self.snapshot = self.store.save(
                candidate.validated(), expected_bytes=self.snapshot.file_bytes)
        except Exception as exc:
            self.error = type(exc).__name__
            self.status.configure(text="Không lưu: cấu hình trước được giữ nguyên")
            self._restore()
            return False
        self.error = None
        self.status.configure(text="Đã lưu cấu hình Về thành")
        self._restore()
        return True

    def _on_flag(self, key):
        if key not in TRADE_BOOL_KEYS or self.snapshot is None:
            self._restore()
            return False
        return self._commit(self.snapshot.value.change(key, self.vars[key].get()))

    def _on_numeric(self, key):
        if key not in ("sell_tab", "hp_qty", "mp_qty") or self.snapshot is None:
            self._restore()
            return False
        try:
            proposed = self.snapshot.value.change(key, self.vars[key].get())
        except FarmTownTradeError:
            self._restore()
            return False
        return self._commit(proposed)

    def _on_select(self, key):
        if key not in ("sell_map", "meds_map", "hp_item", "mp_item") or self.snapshot is None:
            self._restore()
            return False
        selected = self.vars[key].get()
        choices = (
            self.destination_choices if key in ("sell_map", "meds_map")
            else HP_ITEMS if key == "hp_item" else MP_ITEMS
        )
        if selected not in choices:
            self._restore()
            return False
        return self._commit(self.snapshot.value.change(key, selected))

    def refresh_destinations(self):
        """Reload H11 names, without silently changing persisted selections."""
        if self._closed or self._blocked:
            return False
        try:
            updated = town_destination_choices(self.store.path)
        except FarmTownTradeError as exc:
            self.error = type(exc).__name__
            self.status.configure(text="Tọa độ đã lưu không an toàn")
            return False
        self.destination_choices = updated
        self.widgets["sell_map"].configure(values=updated)
        self.widgets["meds_map"].configure(values=updated)
        return True

    def _on_destroy(self, event):
        if event.widget is self:
            self._closed = True
