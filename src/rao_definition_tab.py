"""Independent Rao M01-M04 real configuration UI, NOT a fake send-chat worker.

Original Tk fields: name/content/channel/seconds/delete/add. This module
edits actual original [Rao] JSON definition keys and preserves account keys;
until a valid game RoleName/source and chat transport exist, no account
selection or Bắt đầu button is presented as operational.
"""
from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import ttk

from rao_definition_config import (
    RAO_CHANNELS, RaoConfigSnapshot, RaoConfigError,
    RaoDefinition, RaoDefinitionStore, next_rao_name,
)


class TkRaoConfigTab(ttk.Frame):
    """Editable M01-M04 definition rows with actual durable settings changes."""

    def __init__(self, parent, *, settings_file: str | Path):
        if not isinstance(settings_file, (Path, str)) or not str(settings_file):
            raise ValueError("RAO_SETTINGS_FILE_REQUIRED")
        super().__init__(parent)
        self.store = RaoDefinitionStore(settings_file)
        self.snapshot: RaoConfigSnapshot | None = None
        self._closed = False
        self._blocked = False
        self._rendering = False
        self._rows: list[dict] = []
        self.last_error: str | None = None
        try:
            self.snapshot = self.store.load()
        except (RaoConfigError, OSError, ValueError) as exc:
            self._blocked = True
            self.last_error = type(exc).__name__

        self.definition_group = ttk.LabelFrame(self, text="Cấu hình rao tự động")
        self.definition_group.pack(fill="x", padx=6, pady=(7, 4))
        head = ttk.Frame(self.definition_group)
        head.pack(fill="x", padx=4)
        for index, (label, width) in enumerate((
            ("Tên", 10), ("Nội dung rao", 24), ("Kênh", 12),
            ("Lặp (s)", 7), ("Xóa", 4),
        )):
            ttk.Label(head, text=label, width=width).grid(
                row=0, column=index, sticky="w")
        self.rows_container = ttk.Frame(self.definition_group)
        self.rows_container.pack(fill="x", padx=4)
        bar = ttk.Frame(self.definition_group)
        bar.pack(fill="x", padx=4, pady=(3, 5))
        self.add_button = ttk.Button(
            bar, text="+ Thêm rao", command=self.add_definition)
        self.add_button.pack(side="left")

        self.status = ttk.Label(self, text="", anchor="w", wraplength=415)
        self.status.pack(fill="x", padx=6, pady=(0, 4))
        accounts = ttk.LabelFrame(self, text="Danh sách tài khoản")
        accounts.pack(fill="both", expand=True, padx=6, pady=4)
        # Genuine G03 RoleName and send_chat interface missing from product.
        # This table remains EMPTY instead of inventing a character or offering
        # clickable fake account/start automation.
        self.account_table = ttk.Treeview(
            accounts, show="headings", selectmode="none",
            columns=("character", "rao"), height=9)
        self.account_table.heading("character", text="Nhân vật")
        self.account_table.heading("rao", text="Nội dung rao")
        self.account_table.column("character", width=140, stretch=True)
        self.account_table.column("rao", width=230, stretch=True)
        self.account_table.pack(fill="both", expand=True, padx=3, pady=3)
        ttk.Label(
            self, text=("Cấu hình Rao đã lưu vào settings.ini. "
                        "Đọc tên nhân vật và gửi chat trong game "
                        "chưa được kết nối; không tự chạy Rao."),
            wraplength=420, justify="left",
        ).pack(fill="x", padx=6, pady=4)

        # If original user settings contained no Rao definitions, the
        # screenshot's Rao 1 is shown as an uncommitted UI default. It is
        # persisted only when an actual user edit/add occurs.
        self._display = list(self.snapshot.rows) if self.snapshot else []
        if not self._display and not self._blocked:
            self._display = [RaoDefinition("Rao 1")]
        self._render_rows()
        if self._blocked:
            self._set_status("Cấu hình Rao hiện tại không an toàn để sửa; không ghi đè")
        self.bind("<Destroy>", self._on_destroy, add="+")

    def _set_status(self, message: str):
        if not self._closed:
            self.status.configure(text=message)

    def _enabled(self) -> bool:
        return not self._closed and not self._blocked and self.snapshot is not None

    def _render_rows(self):
        self._rendering = True
        try:
            for child in self.rows_container.winfo_children():
                child.destroy()
            self._rows.clear()
            for index, row in enumerate(self._display):
                vars_ = {
                    "name": tk.StringVar(master=self, value=row.name),
                    "content": tk.StringVar(master=self, value=row.content),
                    "channel": tk.StringVar(master=self, value=row.channel),
                    "seconds": tk.StringVar(master=self, value=row.seconds),
                }
                widgets = (
                    ttk.Entry(self.rows_container, textvariable=vars_["name"],
                              width=10),
                    ttk.Entry(self.rows_container, textvariable=vars_["content"],
                              width=24),
                    ttk.Combobox(self.rows_container, textvariable=vars_["channel"],
                                 values=tuple(RAO_CHANNELS),
                                 state="readonly" if self._enabled() else "disabled",
                                 width=12),
                    ttk.Entry(self.rows_container, textvariable=vars_["seconds"],
                              width=7),
                )
                for col, widget in enumerate(widgets):
                    widget.grid(row=index, column=col, padx=1, pady=1, sticky="ew")
                    if not self._enabled():
                        widget.configure(state="disabled")
                delete = ttk.Button(
                    self.rows_container, text="✕", width=3,
                    command=lambda n=index: self.delete_definition(n))
                delete.grid(row=index, column=4, padx=1, pady=1)
                if not self._enabled():
                    delete.configure(state="disabled")
                for var in vars_.values():
                    # M02 original StringVar trace-based live config save.
                    var.trace_add("write",
                                  lambda *_args, n=index: self._on_row_edit(n))
                self._rows.append({"vars": vars_, "widgets": widgets,
                                   "delete": delete})
            self.add_button.configure(
                state="normal" if self._enabled() else "disabled")
        finally:
            self._rendering = False

    def _models(self) -> tuple[RaoDefinition, ...]:
        return tuple(RaoDefinition(
            name=entry["vars"]["name"].get().strip(),
            content=entry["vars"]["content"].get(),
            channel=entry["vars"]["channel"].get(),
            seconds=entry["vars"]["seconds"].get(),
        ).validated() for entry in self._rows)

    def _commit(self, rows: tuple[RaoDefinition, ...]) -> bool:
        if not self._enabled():
            return False
        try:
            self.snapshot = self.store.save(
                rows, expected_bytes=self.snapshot.file_bytes)
        except (RaoConfigError, OSError, ValueError) as exc:
            self.last_error = type(exc).__name__
            self._set_status("Không lưu Rao: tên/kênh/giây sai hoặc settings.ini đã đổi")
            if self.last_error in (
                    "STALE_RAO_SETTINGS", "RAO_SETTINGS_CHANGED_CONCURRENTLY",
                    "MALFORMED_RAO_DEFINITION", "DUPLICATE_RAO_SECTION"):
                self._blocked = True
                self._render_rows()
            return False
        self.last_error = None
        self._display = list(rows)
        self._set_status("Đã lưu cấu hình Rao; chưa thực hiện gửi chat game")
        return True

    def _on_row_edit(self, index: int):
        if self._rendering or not self._enabled():
            return False
        try:
            rows = self._models()
        except RaoConfigError:
            self._set_status("Chưa lưu: tên hoặc số giây không hợp lệ")
            return False
        return self._commit(rows)

    def add_definition(self) -> bool:
        if not self._enabled():
            return False
        try:
            old = self._models()
            newer = old + (RaoDefinition(next_rao_name(old)),)
        except RaoConfigError:
            self._set_status("Sửa dòng Rao hiện tại trước khi thêm")
            return False
        if not self._commit(newer):
            return False
        self._render_rows()
        return True

    def delete_definition(self, index: int) -> bool:
        if not self._enabled() or not 0 <= index < len(self._rows):
            return False
        try:
            rows = self._models()
        except RaoConfigError:
            self._set_status("Sửa dữ liệu Rao chưa hợp lệ trước khi xóa")
            return False
        updated = rows[:index] + rows[index + 1:]
        if not self._commit(updated):
            return False
        self._render_rows()
        return True

    def shutdown(self):
        self._closed = True

    def _on_destroy(self, event):
        if event.widget is self:
            self.shutdown()
