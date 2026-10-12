"""S169 Train LSV original B06 top controls with REAL isolated INI writes.

Local-config-only Tk module. No account actions, Farm FSM, keyboard/DLL
transport, gameplay, token/heartbeat checks, or fake Start/Attack buttons.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from pathlib import Path

from train_lsv_top_settings import (
    TrainLsvTopStore, TrainLsvTopSnapshot, TrainLsvTopConfig,
    LSV_KEEP_RADIOS,
)

_CHECKS = (
    ("respawn", "Quay lại train khi chết"),
    ("auto_reconnect", "Tự kết nối lại khi mất mạng"),
    ("trist", "Trị liệu sau khi chết tại Lạc Dương LSV"),
)


class TkTrainLsvTopTab(ttk.Frame):
    """Real, useful settings tab; not the unimplemented TrainLsvTab engine."""

    def __init__(self, parent, *, settings_file: str | Path):
        if not isinstance(settings_file, (str, Path)) or not str(settings_file):
            raise ValueError("LSV_SHARED_SETTINGS_FILE_REQUIRED")
        super().__init__(parent)
        self.store = TrainLsvTopStore(settings_file)
        self._closed = False
        self._restoring = False
        self._blocked = False
        self.error: str | None = None
        self.snapshot: TrainLsvTopSnapshot | None = None
        try:
            self.snapshot = self.store.load()
        except Exception as exc:
            self._blocked = True
            self.error = type(exc).__name__
        current = self.snapshot.value if self.snapshot else TrainLsvTopConfig()
        self.flags = {
            key: tk.BooleanVar(master=self, value=getattr(current, key))
            for key, _ in _CHECKS
        }
        self.pickup_var = tk.StringVar(master=self, value=current.pickup_mode)
        group = ttk.LabelFrame(self, text="Cấu hình Train LSV")
        group.pack(fill="x", padx=6, pady=(6, 2))
        self.checks = {}
        first = ttk.Frame(group)
        first.pack(fill="x", padx=6, pady=(4, 1))
        for key, caption in _CHECKS[:2]:
            cb = ttk.Checkbutton(
                first, text=caption, variable=self.flags[key],
                command=lambda k=key: self._on_flag(k))
            cb.pack(side="left", padx=(0, 6))
            self.checks[key] = cb
        row = ttk.Frame(group)
        row.pack(fill="x", padx=6, pady=(0, 3))
        key, caption = _CHECKS[2]
        cb = ttk.Checkbutton(row, text=caption, variable=self.flags[key],
                             command=lambda: self._on_flag("trist"))
        cb.pack(side="left")
        self.checks[key] = cb

        modes = ttk.Frame(group)
        modes.pack(fill="x", padx=6, pady=(2, 6))
        ttk.Label(modes, text="Nhặt đồ:").pack(side="left")
        self.pickup_radios = {}
        for title, code in LSV_KEEP_RADIOS:
            radio = ttk.Radiobutton(
                modes, text=title, variable=self.pickup_var,
                value=code, command=self._on_pickup)
            radio.pack(side="left", padx=(8, 0))
            self.pickup_radios[code] = radio
        self.status = ttk.Label(self, text="")
        self.status.pack(fill="x", padx=6)
        # Do not create fake LSV travel/fight/start/buff/edit commands.
        ttk.Label(
            self,
            text=("Đã hỗ trợ lưu cấu hình Train LSV. "
                  "Tọa độ, Dạ Minh Châu, danh sách tài khoản và "
                  "điều khiển game chưa được kết nối."),
            wraplength=408, justify="left",
        ).pack(fill="x", padx=6, pady=5)
        self._refresh_controls()
        self.bind("<Destroy>", self._on_destroy, add="+")

    def _permitted(self) -> bool:
        # This is only local editable config. No original TLM licensing.
        return not self._closed and not self._blocked and self.snapshot is not None

    def _refresh_controls(self):
        state = "normal" if self._permitted() else "disabled"
        for widget in self.checks.values():
            widget.configure(state=state)
        for widget in self.pickup_radios.values():
            widget.configure(state=state)
        if self._blocked:
            self.status.configure(text="Dữ liệu cấu hình LSV không an toàn để chỉnh sửa")

    def _restore(self):
        if self.snapshot is None:
            return
        self._restoring = True
        try:
            for key, _ in _CHECKS:
                self.flags[key].set(getattr(self.snapshot.value, key))
            self.pickup_var.set(self.snapshot.value.pickup_mode)
        finally:
            self._restoring = False

    def _commit(self, key: str, value: bool | str) -> bool:
        if self._restoring or not self._permitted():
            self._restore()
            return False
        try:
            self.snapshot = self.store.save_change(
                key, value, expected_bytes=self.snapshot.file_bytes)
        except Exception as exc:
            self.error = type(exc).__name__
            self.status.configure(text="Không lưu: cấu hình đã thay đổi hoặc không hợp lệ")
            self._restore()
            return False
        self.error = None
        self.status.configure(text="Đã lưu cấu hình Train LSV")
        self._restore()
        return True

    def _on_flag(self, key: str) -> bool:
        if key not in self.flags:
            return False
        return self._commit(key, self.flags[key].get())

    def _on_pickup(self) -> bool:
        return self._commit("pickup_mode", self.pickup_var.get())

    def _on_destroy(self, event):
        if event.widget is self:
            self._closed = True
