"""S182 independent Dồn Train configuration UI, no game automation.

These checkboxes/combos write real [DonVang] keys from L04/L08/L10.
Legacy auto_reconnect is correctly labeled 'Dừng khi mất kết nối mạng'.
"""
from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import ttk

from don_train_settings import (
    DonTrainConfig, DonTrainSettingsError, DonTrainSettingsStore,
    HEAL_DESTINATIONS, PICKUP_CHOICES,
)


class TkDonTrainSettingsPanel(ttk.Frame):
    """S182 bounded Train option editor embedded under S181 return controls."""

    def __init__(self, parent, *, settings_file: str | Path, on_saved=None):
        super().__init__(parent)
        self.store = DonTrainSettingsStore(settings_file)
        self.snapshot = None
        self.last_error = None
        self._blocked = False
        self._closed = False
        self._restoring = False
        self.on_saved = on_saved
        try:
            self.snapshot = self.store.load()
        except (OSError, ValueError, DonTrainSettingsError) as exc:
            self._blocked = True
            self.last_error = type(exc).__name__
        starting = self.snapshot.value if self.snapshot else DonTrainConfig()
        self.vars = {}
        for key in DonTrainConfig.__dataclass_fields__:
            val = getattr(starting, key)
            kind = tk.BooleanVar if type(val) is bool else tk.StringVar
            self.vars[key] = kind(master=self, value=val)

        self.group = ttk.LabelFrame(self, text="Cấu hình Train")
        self.group.pack(fill="x")
        self.controls = []
        first = ttk.Frame(self.group)
        first.pack(fill="x", padx=5, pady=(4, 1))
        self._check(first, "Quay lại train khi chết", "respawn")
        self._check(first, "Dừng khi mất kết nối mạng", "auto_reconnect")
        self._check(first, "Tự gỡ kẹt", "unstuck")
        second = ttk.Frame(self.group)
        second.pack(fill="x", padx=5, pady=(2, 1))
        self._check(second, "Nhặt đồ không dùng hồ lô (càn khôn hồ)",
                    "pickup_no_cankhon")
        third = ttk.Frame(self.group)
        third.pack(fill="x", padx=5, pady=(2, 1))
        ttk.Label(third, text="Lọc đồ:").pack(side="left")
        for title, mode in PICKUP_CHOICES:
            btn = ttk.Radiobutton(
                third, text=title,
                variable=self.vars["pickup_mode"], value=mode,
                command=lambda: self._commit("pickup_mode"))
            btn.pack(side="left", padx=(8, 0))
            self.controls.append(btn)
        last = ttk.Frame(self.group)
        last.pack(fill="x", padx=5, pady=(2, 5))
        self._check(last, "Trị liệu sau khi chết", "trist")
        ttk.Label(last, text="Tọa độ trị liệu:").pack(
            side="left", padx=(2, 4))
        loc = ttk.Combobox(
            last, values=tuple(HEAL_DESTINATIONS), width=17,
            state="readonly", textvariable=self.vars["heal_map"])
        loc.pack(side="left")
        loc.bind(
            "<<ComboboxSelected>>",
            lambda _e: self._commit("heal_map"), add="+")
        self.controls.append(loc)
        self.status = ttk.Label(
            self, text="", wraplength=414, anchor="w")
        self.status.pack(fill="x", padx=5, pady=(2, 3))
        if self._blocked:
            self._status(
                "Cấu hình Train của Dồn không an toàn để sửa; không ghi đè")
        else:
            self._status("Chỉ lưu cấu hình Train; không điều khiển nhân vật")
        self._refresh_controls()
        self.bind("<Destroy>", self._on_destroy, add="+")

    def _check(self, parent, caption, field):
        button = ttk.Checkbutton(
            parent, text=caption, variable=self.vars[field],
            command=lambda f=field: self._commit(f))
        button.pack(side="left", padx=(0, 7))
        self.controls.append(button)

    def _enabled(self):
        return not self._closed and not self._blocked and self.snapshot is not None

    def _status(self, message):
        if not self._closed:
            self.status.configure(text=message)

    def _refresh_controls(self):
        for control in self.controls:
            control.configure(state=(
                "readonly" if isinstance(control, ttk.Combobox)
                and self._enabled() else
                "normal" if self._enabled() else "disabled"))

    def _restore(self):
        if self.snapshot is None or self._closed:
            return
        self._restoring = True
        try:
            for key, var in self.vars.items():
                var.set(getattr(self.snapshot.value, key))
        finally:
            self._restoring = False

    def sync_after_other_save(self) -> bool:
        """Refresh sibling file snapshot without changing on-screen identity."""
        if self._closed or self._blocked:
            return False
        try:
            self.snapshot = self.store.load()
        except (OSError, ValueError, DonTrainSettingsError) as exc:
            self.last_error = type(exc).__name__
            self._blocked = True
            self._refresh_controls()
            self._status("Cấu hình Dồn đã thay đổi; mở lại tab để xác minh")
            return False
        self._restore()
        return True

    def _commit(self, field):
        if not self._enabled() or self._restoring:
            return False
        try:
            self.snapshot = self.store.save_change(
                field, self.vars[field].get(),
                expected_bytes=self.snapshot.file_bytes)
        except (OSError, ValueError, DonTrainSettingsError) as exc:
            self.last_error = type(exc).__name__
            self._restore()
            self._status("Không lưu được tùy chọn Dồn; kiểm tra settings.ini")
            if self.last_error in (
                    "STALE_DON_TRAIN_SETTINGS",
                    "DON_TRAIN_SETTINGS_CHANGED",
                    "DUPLICATE_DON_TRAIN_KEY"):
                self._blocked = True
                self._refresh_controls()
            return False
        self.last_error = None
        self._restore()
        self._status("Đã lưu tùy chọn Dồn trong settings.ini")
        if callable(self.on_saved):
            self.on_saved()
        return True

    def shutdown(self):
        self._closed = True

    def _on_destroy(self, event):
        if event.widget is self:
            self.shutdown()
