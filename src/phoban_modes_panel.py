"""S185 source-backed Phó Bản mode checkboxes (J01/J03/J08/J09/J10).

All seven original controls actually persist their own Settings key. This
panel has no in-game worker and cannot recreate teams, move, pickup, discard,
or buff without a real, authorized client bridge. The saved user intent
is kept intact for future independently verified game integration.
"""
from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import ttk

from phoban_modes_settings import (
    MODE_KEYS, MODE_LABELS,
    PhoBanModes, PhoBanModesError, PhoBanModesStore,
)


class TkPhoBanModesPanel(ttk.Frame):
    def __init__(self, parent, *, settings_file: str | Path, on_saved=None):
        if not isinstance(settings_file, (str, Path)) or not str(settings_file):
            raise ValueError("PHOBAN_MODE_SETTINGS_FILE_REQUIRED")
        super().__init__(parent)
        self.store = PhoBanModesStore(settings_file)
        self.on_saved = on_saved
        self.snapshot = None
        self.last_error = None
        self._closed = False
        self._blocked = False
        self._restoring = False
        try:
            self.snapshot = self.store.load()
        except (PhoBanModesError, ValueError, OSError) as exc:
            self.last_error = type(exc).__name__
            self._blocked = True
        saved = self.snapshot.modes if self.snapshot else PhoBanModes()
        self.variables = {
            key: tk.BooleanVar(master=self, value=getattr(saved, key))
            for key in MODE_KEYS
        }
        self.group = ttk.LabelFrame(self, text="Cấu hình phó bản")
        self.group.pack(fill="x", padx=6, pady=(2, 4))
        self.inputs = {}
        for index, (key, text) in enumerate(MODE_LABELS):
            # B07 exact visual grouping: three columns, 3/3/1 rows.
            control = ttk.Checkbutton(
                self.group, text=text, variable=self.variables[key],
                command=lambda k=key: self._commit(k))
            control.grid(
                row=index // 3, column=index % 3,
                sticky="w", padx=(5, 2), pady=(2, 1))
            self.inputs[key] = control
        for column in range(3):
            self.group.columnconfigure(column, weight=1)
        self.status = ttk.Label(
            self, text="", anchor="w", wraplength=414)
        self.status.pack(fill="x", padx=7, pady=(0, 2))
        self._refresh_controls()
        self._status(
            "Dữ liệu tùy chọn Phó Bản không an toàn; không ghi đè"
            if self._blocked else
            "Tùy chọn chỉ lưu cấu hình; chưa khởi chạy chức năng trong game")
        self.bind("<Destroy>", self._on_destroy, add="+")

    def _enabled(self) -> bool:
        return not self._closed and not self._blocked and self.snapshot is not None

    def _status(self, message: str):
        if not self._closed:
            self.status.configure(text=message)

    def _refresh_controls(self):
        state = "normal" if self._enabled() else "disabled"
        for widget in self.inputs.values():
            widget.configure(state=state)

    def _restore(self):
        if self.snapshot is None or self._closed:
            return
        self._restoring = True
        try:
            for key, variable in self.variables.items():
                variable.set(getattr(self.snapshot.modes, key))
        finally:
            self._restoring = False

    def _commit(self, key: str) -> bool:
        if self._restoring or not self._enabled() or key not in MODE_KEYS:
            self._restore()
            return False
        checked = self.variables[key].get()
        try:
            self.snapshot = self.store.save_change(
                key, checked, expected_bytes=self.snapshot.file_bytes)
        except (PhoBanModesError, ValueError, OSError) as exc:
            self.last_error = str(exc)
            self._restore()
            self._status("Không thể lưu tùy chọn Phó Bản; settings.ini đã đổi hoặc sai")
            if self.last_error in (
                    "STALE_PHOBAN_MODE_SETTINGS", "PHOBAN_MODE_SETTINGS_CHANGED",
                    "DUPLICATE_OR_INVALID_PHOBAN_MODE", "MALFORMED_PHOBAN_MODE_OPTION"):
                self._blocked = True
                self._refresh_controls()
            return False
        self.last_error = None
        self._restore()
        self._status("Đã lưu tùy chọn Phó Bản, chưa thực hiện thao tác game")
        if callable(self.on_saved):
            self.on_saved()
        return True

    def sync_after_other_save(self) -> bool:
        """Refresh the full-file snapshot after schedule settings are saved."""
        if not self._enabled():
            return False
        try:
            self.snapshot = self.store.load()
        except (PhoBanModesError, ValueError, OSError) as exc:
            self.last_error = str(exc)
            self._blocked = True
            self._refresh_controls()
            self._status("Không thể đồng bộ cấu hình Phó Bản; mở lại tab")
            return False
        self._restore()
        return True

    def shutdown(self):
        self._closed = True

    def _on_destroy(self, event):
        if event.widget is self:
            self.shutdown()
