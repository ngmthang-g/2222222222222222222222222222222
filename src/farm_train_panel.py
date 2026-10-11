"""S129 real Tk original H06-H09 Train configuration, not Farm gameplay.

Supports four documented original checkboxes, keep-mode radio group, H06
builtin and saved-coordinate treatment selection, actual safe INI writes.
Only a real signed Info+account-limit authority may allow editing; test
stubs are exclusively in native Windows CI, not in production code.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Callable

from farm_train_settings import (
    FarmTrainConfig, FarmTrainSettingsStore, FarmTrainSnapshot,
    FarmTrainSettingsError, KEEP_RADIOS, HEAL_BUILTIN_SEPARATOR,
    HEAL_MANUAL_SEPARATOR, HEAL_DEFAULT, heal_options,
    is_real_heal_destination,
)
from permission_guard import PermissionGuard

BOOL_CONTROLS = (
    ("respawn", "Quay lại train khi chết"),
    ("auto_reconnect", "Tự kết nối lại khi mất mạng"),
    ("pickup_no_cankhon", "Nhặt đồ không dùng hồ lô (càn khôn hồ)"),
    ("trist", "Trị liệu sau khi chết"),
)


class TkFarmTrainSettings(ttk.Frame):
    """Genuine original config surface. Does NOT imply Farm FSM exists."""

    def __init__(self, parent, *, store: FarmTrainSettingsStore | None = None,
                 permission_guard: PermissionGuard | None = None,
                 running_count: Callable[[], int] | None = None):
        super().__init__(parent)
        self.store = store if store is not None else FarmTrainSettingsStore()
        self.guard = permission_guard
        self.running_count = running_count
        self._closed = False
        self._blocked = False
        self._updating = False
        self.error: str | None = None
        self.snapshot: FarmTrainSnapshot | None = None
        self._heal_values: tuple[str, ...] = ()
        try:
            self.snapshot = self.store.load()
            self._heal_values = heal_options(self.store.path)
        except Exception as exc:
            self._blocked = True
            self.error = type(exc).__name__
        initial = self.snapshot.value if self.snapshot else FarmTrainConfig()
        self.flags = {
            key: tk.BooleanVar(master=self, value=getattr(initial, key))
            for key, _ in BOOL_CONTROLS
        }
        self.pickup_var = tk.StringVar(master=self, value=initial.pickup_mode)
        self.heal_var = tk.StringVar(master=self, value=initial.heal_map)
        group = ttk.LabelFrame(self, text="Cấu hình Train")
        group.pack(fill="x", padx=5, pady=4)
        line1 = ttk.Frame(group)
        line1.pack(fill="x", padx=6, pady=(5, 2))
        self.checks: dict[str, ttk.Checkbutton] = {}
        for key, caption in BOOL_CONTROLS[:2]:
            check = ttk.Checkbutton(
                line1, text=caption, variable=self.flags[key],
                command=lambda k=key: self._on_flag(k))
            check.pack(side="left", padx=(0, 9))
            self.checks[key] = check
        for key, caption in BOOL_CONTROLS[2:]:
            line = ttk.Frame(group)
            line.pack(fill="x", padx=6, pady=(0, 2))
            check = ttk.Checkbutton(
                line, text=caption, variable=self.flags[key],
                command=lambda k=key: self._on_flag(k))
            check.pack(side="left")
            self.checks[key] = check
            if key == "trist":
                self.heal_combo = ttk.Combobox(
                    line, textvariable=self.heal_var,
                    values=self._heal_values, state="disabled",
                    width=24)
                self.heal_combo.pack(side="left", padx=(8, 0))
                self.heal_combo.bind("<<ComboboxSelected>>",
                                     self._on_heal_select, add="+")
        row = ttk.Frame(group)
        row.pack(fill="x", padx=6, pady=4)
        ttk.Label(row, text="Lọc đồ giữ lại:").pack(side="left")
        self.pickup_radios: dict[str, ttk.Radiobutton] = {}
        for caption, code in KEEP_RADIOS:
            radio = ttk.Radiobutton(
                row, text=caption, value=code, variable=self.pickup_var,
                command=self._on_pickup)
            radio.pack(side="left", padx=(8, 0))
            self.pickup_radios[code] = radio
        self.status = ttk.Label(self, text="")
        self.status.pack(fill="x", padx=6)
        self.reapply_permission()
        if self._blocked:
            self.status.configure(text="Cấu hình Train không an toàn để chỉnh sửa")
        self.bind("<Destroy>", self._on_destroy, add="+")

    def _permitted(self) -> bool:
        if (self._closed or self._blocked
                or type(self.guard) is not PermissionGuard
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
        allowed = self._permitted()
        for widget in self.checks.values():
            widget.configure(state="normal" if allowed else "disabled")
        for radio in self.pickup_radios.values():
            radio.configure(state="normal" if allowed else "disabled")
        self.heal_combo.configure(state="readonly" if allowed else "disabled")

    def _restore(self):
        if self.snapshot is None:
            return
        self._updating = True
        try:
            value = self.snapshot.value
            for key, _ in BOOL_CONTROLS:
                self.flags[key].set(getattr(value, key))
            self.pickup_var.set(value.pickup_mode)
            self.heal_var.set(value.heal_map)
        finally:
            self._updating = False

    def _commit(self, value: FarmTrainConfig) -> bool:
        if self._updating or not self._permitted() or self.snapshot is None:
            self._restore()
            return False
        try:
            self.snapshot = self.store.save(
                value.validated(), expected_bytes=self.snapshot.file_bytes)
        except Exception as exc:
            self.error = type(exc).__name__
            self.status.configure(text="Không lưu: giữ nguyên cấu hình trước")
            self._restore()
            return False
        self.error = None
        self.status.configure(text="Đã lưu cấu hình Train")
        self._restore()
        return True

    def _on_flag(self, key: str) -> bool:
        if self.snapshot is None or key not in self.flags:
            self._restore()
            return False
        return self._commit(self.snapshot.value.change(key, self.flags[key].get()))

    def _on_pickup(self) -> bool:
        if self.snapshot is None:
            self._restore()
            return False
        try:
            value = self.snapshot.value.change("pickup_mode", self.pickup_var.get())
        except ValueError:
            self._restore()
            return False
        return self._commit(value)

    def _on_heal_select(self, _event=None) -> bool:
        if self.snapshot is None:
            self._restore()
            return False
        desired = self.heal_var.get()
        if desired in (HEAL_BUILTIN_SEPARATOR, HEAL_MANUAL_SEPARATOR):
            # H06: selecting a separator jumps forward to first real value.
            if desired == HEAL_BUILTIN_SEPARATOR:
                desired = next((s for s in self._heal_values
                                if is_real_heal_destination(s, self._heal_values)), "")
            else:
                position = self._heal_values.index(HEAL_MANUAL_SEPARATOR)
                desired = next((s for s in self._heal_values[position + 1:]
                                if is_real_heal_destination(s, self._heal_values)), "")
            if not desired:
                self._restore()
                return False
        if not is_real_heal_destination(desired, self._heal_values):
            self._restore()
            return False
        return self._commit(self.snapshot.value.change("heal_map", desired))

    def refresh_heal_destinations(self) -> bool:
        """Update only the H11 saved-coordinate choices; never choose silently."""
        if self._closed or self._blocked:
            return False
        try:
            next_values = heal_options(self.store.path)
        except FarmTrainSettingsError as exc:
            self.error = type(exc).__name__
            self.status.configure(text="Không thể đọc tọa độ trị liệu đã lưu")
            return False
        self._heal_values = next_values
        self.heal_combo.configure(values=next_values)
        # A preset removed from disk stays in the stored value until the user
        # selects a valid replacement; never auto-reset/scrub their setting.
        return True

    def _on_destroy(self, event):
        if event.widget is self:
            self._closed = True
