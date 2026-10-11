"""S131: true Tk manual Farm buff-row editor → source-backed real settings.ini.

The original Frozen FarmTab has "+ Thêm", enabled/check, Phím selector
F1..F10/1/2/3, Thời gian: minutes + seconds and per-row delete. No game
key press/loop worker is implemented; the UI is a standalone config editor.
New-row values are expressly LOCAL safe defaults, not proven original ones.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from farm_buff_settings import (
    FarmBuffRow, FarmBuffSettingsStore, FarmBuffSnapshot,
    FarmBuffSettingsError, BUFF_KEYS,
)
from permission_guard import PermissionGuard


class TkFarmBuffEditor(ttk.Frame):
    """Authenticated user settings editor; never uses a game HWND."""

    def __init__(self, parent, *, store: FarmBuffSettingsStore | None = None,
                 permission_guard: PermissionGuard | None = None,
                 running_count: Callable[[], int] | None = None):
        super().__init__(parent)
        self.store = store if store is not None else FarmBuffSettingsStore()
        self.guard = permission_guard
        self.running_count = running_count
        self._closed = False
        self._blocked = False
        self._updating = False
        self.error: str | None = None
        self.snapshot: FarmBuffSnapshot | None = None
        try:
            self.snapshot = self.store.load()
        except Exception as exc:
            self._blocked = True
            self.error = type(exc).__name__
        self.group = ttk.LabelFrame(self, text="Dùng thuốc (buff) thủ công")
        self.group.pack(fill="x", padx=5, pady=4)
        self.row_host = ttk.Frame(self.group)
        self.row_host.pack(fill="x", padx=5)
        self.row_widgets: list[dict] = []
        controls = ttk.Frame(self.group)
        controls.pack(fill="x", padx=5, pady=(4, 5))
        self.add_button = ttk.Button(controls, text="+ Thêm",
                                     command=self.add_local_row)
        self.add_button.pack(side="left")
        self.status = ttk.Label(self, text="")
        self.status.pack(fill="x", padx=5)
        self._render()
        self.reapply_permission()
        if self._blocked:
            self.status.configure(text="Dữ liệu buff chưa an toàn để chỉnh sửa")
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

    def _render(self):
        for widget in self.row_host.winfo_children():
            widget.destroy()
        self.row_widgets.clear()
        rows = self.snapshot.rows if self.snapshot is not None else ()
        for index, data in enumerate(rows):
            line = ttk.Frame(self.row_host)
            line.pack(fill="x", pady=2)
            flag = tk.BooleanVar(master=self, value=data.enabled)
            key = tk.StringVar(master=self, value=data.key)
            mins = tk.StringVar(master=self, value=data.minutes)
            secs = tk.StringVar(master=self, value=data.seconds)
            check = ttk.Checkbutton(
                line, variable=flag,
                command=lambda i=index: self.commit_field(i, "enabled"))
            check.pack(side="left")
            ttk.Label(line, text="Phím:").pack(side="left", padx=(4, 3))
            combo = ttk.Combobox(
                line, values=BUFF_KEYS, textvariable=key,
                state="disabled", width=5)
            combo.pack(side="left", padx=2)
            combo.bind("<<ComboboxSelected>>",
                       lambda _ev, i=index: self.commit_field(i, "key"), add="+")
            ttk.Label(line, text="Thời gian:").pack(side="left", padx=(9, 3))
            minute = ttk.Entry(line, textvariable=mins, width=5)
            minute.pack(side="left")
            ttk.Label(line, text="ph").pack(side="left", padx=(2, 8))
            second = ttk.Entry(line, textvariable=secs, width=5)
            second.pack(side="left")
            ttk.Label(line, text="giây").pack(side="left", padx=(2, 8))
            for fld, entry in (("minutes", minute), ("seconds", second)):
                entry.bind("<Return>",
                           lambda _ev, i=index, f=fld: self.commit_field(i,f), add="+")
                entry.bind("<FocusOut>",
                           lambda _ev, i=index, f=fld: self.commit_field(i,f), add="+")
            delete = ttk.Button(line, text="✕", width=3,
                                command=lambda i=index: self.delete_row(i))
            delete.pack(side="left")
            self.row_widgets.append({
                "flag":flag,"key":key,"minutes":mins,"seconds":secs,
                "check":check,"combo":combo,"minute":minute,
                "second":second,"delete":delete,
            })
        self.reapply_permission()

    def reapply_permission(self):
        allowed = self._permitted()
        self.add_button.configure(state="normal" if allowed else "disabled")
        for row in self.row_widgets:
            for field in ("check","minute","second","delete"):
                row[field].configure(state="normal" if allowed else "disabled")
            row["combo"].configure(state="readonly" if allowed else "disabled")

    def _commit(self, rows):
        if self._closed or self._updating or not self._permitted() or self.snapshot is None:
            self._render()
            return False
        try:
            self.snapshot = self.store.save(
                tuple(rows), expected_bytes=self.snapshot.file_bytes)
        except Exception as exc:
            self.error = type(exc).__name__
            self.status.configure(text="Không lưu: giữ nguyên cấu hình buff trước")
            self._render()
            return False
        self.error = None
        self.status.configure(text="Đã lưu buff")
        self._render()
        return True

    def commit_field(self, index: int, field: str):
        if (self.snapshot is None or type(index) is not int
                or not 0 <= index < len(self.snapshot.rows)
                or field not in ("enabled","key","minutes","seconds")):
            return False
        if not self._permitted():
            self._render()
            return False
        row = self.row_widgets[index]
        try:
            updated = self.snapshot.rows[index].change(field,row[field].get())
        except FarmBuffSettingsError:
            self._render()
            return False
        values = list(self.snapshot.rows)
        values[index] = updated
        return self._commit(values)

    def add_local_row(self):
        if self.snapshot is None or not self._permitted():
            return False
        # Safe LOCAL default only. Original _add_buff_row default tuple
        # micro-order is not proven by readable binary constants.
        candidate = FarmBuffRow(False, "F1", "0", "30")
        return self._commit(self.snapshot.rows+(candidate,))

    def delete_row(self,index):
        if (self.snapshot is None or not self._permitted()
                or type(index) is not int
                or not 0 <= index < len(self.snapshot.rows)):
            return False
        return self._commit(self.snapshot.rows[:index]+self.snapshot.rows[index+1:])

    def refresh_from_disk(self):
        """Explicit reload if another existing tab modified shared config."""
        if self._closed or self._blocked:
            return False
        try:
            self.snapshot = self.store.load()
        except Exception as exc:
            self.error = type(exc).__name__
            return False
        self.error = None
        self._render()
        return True

    def _on_destroy(self,event):
        if event.widget is self:
            self._closed = True
