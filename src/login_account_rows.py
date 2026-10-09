"""S37 F01/F02/F03 source-backed, in-memory Login 100-row account grid.

Real Tk Canvas/Scrollbar, custom selection buttons, editable username and
masked password, readonly F01 captcha mode. No online/login/proxy buttons:
those original actions are not implemented and fake buttons are forbidden.

F02's account selector token and legacy 'Có' migration remain UNKNOWN.
Therefore this slice deliberately NEVER loads, serializes, rewrites or
deletes Settings.accounts; even closing the tab preserves original bytes
for that key. In-memory test-owned changes are NOT persistent accounts.
"""
from __future__ import annotations

from dataclasses import dataclass

MAX_ACCOUNT_ROWS = 100
CAPTCHA_MODES = ("Không", "Tool", "Proxy")
ROW_PITCH = 35


@dataclass(frozen=True)
class AccountRowSnapshot:
    selected: bool
    username: str
    password: str
    captcha_mode: str


class AccountSelectionModel:
    """Only verified F01 selection state, independent of guessed storage."""
    def __init__(self, count: int = MAX_ACCOUNT_ROWS) -> None:
        if type(count) is not int or count != MAX_ACCOUNT_ROWS:
            raise ValueError("F01 requires exactly 100 logical account rows")
        self._checks = [False] * count

    def checked(self, index: int) -> bool:
        return self._checks[index]

    @property
    def selected_count(self) -> int:
        return sum(self._checks)

    def toggle(self, index: int) -> bool:
        self._checks[index] = not self._checks[index]
        return self._checks[index]

    def toggle_all(self) -> bool:
        """F01 original: if ANY unchecked -> select all, otherwise clear all."""
        target = not all(self._checks)
        self._checks[:] = [target] * len(self._checks)
        return target


class TLMAccountRows:
    """Real in-memory F01 widgets; not a login/credential storage service."""
    def __init__(self, parent):
        import tkinter as tk
        from tkinter import ttk

        self._closed = False
        self.selection = AccountSelectionModel()
        self.group_accounts = ttk.LabelFrame(parent, text="Cấu hình tài khoản")
        # F01 accounts screenshot parent starts ~x11,y297; Login tab origin
        # is near x5,y59. This is a partial local anchor, NOT pixel parity.
        self.group_accounts.place(x=6, y=238, width=428, height=716)
        tk.Label(self.group_accounts, text="Chọn tài khoản muốn login",
                 font=("Segoe UI", 9)).place(x=9, y=7)
        self.show_password_var = tk.BooleanVar(master=self.group_accounts, value=False)
        self.show_password_toggle = ttk.Checkbutton(
            self.group_accounts, text="Hiện mật khẩu",
            variable=self.show_password_var, command=self._toggle_password)
        self.show_password_toggle.place(x=265, y=5)

        self.canvas = tk.Canvas(self.group_accounts, borderwidth=0,
                                highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(
            self.group_accounts, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.place(x=8, y=34, width=390, height=655)
        self.scrollbar.place(x=398, y=34, width=16, height=655)
        self.rows_inner = tk.Frame(self.canvas)
        self._window = self.canvas.create_window(
            (0, 0), window=self.rows_inner, anchor="nw")
        self.rows_inner.bind("<Configure>", self._on_rows_configure, add="+")
        self.canvas.bind("<Configure>", self._on_canvas_configure, add="+")
        self.canvas.bind("<MouseWheel>", self._scroll_wheel, add="+")

        self.header_selector = tk.Button(
            self.rows_inner, text="✅", command=self.toggle_all,
            font=("Segoe UI", 9, "bold"), width=2)
        self.header_selector.grid(row=0, column=0, sticky="ew")
        for column, name in enumerate(
                ("Tài khoản", "Mật khẩu", "Ẩn captcha", "Login", "Proxy"), 1):
            tk.Label(self.rows_inner, text=name, background="#e8e8e8",
                     font=("Segoe UI", 9, "bold")).grid(
                         row=0, column=column, sticky="ew")
        self.rows_inner.grid_rowconfigure(0, minsize=30)

        self.row_selectors = []
        self.username_vars = []
        self.password_vars = []
        self.captcha_vars = []
        self.entry_user = []
        self.entry_pass = []
        self.captcha_boxes = []
        for index in range(MAX_ACCOUNT_ROWS):
            self.rows_inner.grid_rowconfigure(index+1, minsize=ROW_PITCH)
            checkbox=tk.Button(
                self.rows_inner, text="⬜", width=2,
                command=lambda i=index:self.toggle_row(i),
                font=("Segoe UI", 9))
            checkbox.grid(row=index+1, column=0, padx=2)
            user=tk.StringVar(master=self.group_accounts, value="")
            secret=tk.StringVar(master=self.group_accounts, value="")
            captcha=tk.StringVar(master=self.group_accounts, value="Không")
            entry_user=tk.Entry(
                self.rows_inner, textvariable=user, font=("Consolas",10),
                width=12, relief="solid", bd=1)
            entry_pass=tk.Entry(
                self.rows_inner, textvariable=secret, show="*",
                font=("Consolas",10), width=10, relief="solid", bd=1)
            combo=ttk.Combobox(
                self.rows_inner, values=CAPTCHA_MODES, textvariable=captcha,
                state="readonly", width=8)
            entry_user.grid(row=index+1,column=1,padx=2,sticky="ew")
            entry_pass.grid(row=index+1,column=2,padx=2,sticky="ew")
            combo.grid(row=index+1,column=3,padx=2,sticky="ew")
            # F01 names Login/Proxy action columns, but their F06/F08
            # functional handlers are unavailable. No inert fake buttons.
            self.row_selectors.append(checkbox)
            self.username_vars.append(user)
            self.password_vars.append(secret)
            self.captcha_vars.append(captcha)
            self.entry_user.append(entry_user)
            self.entry_pass.append(entry_pass)
            self.captcha_boxes.append(combo)
            for widget in (checkbox,entry_user,entry_pass,combo):
                widget.bind("<MouseWheel>",self._scroll_wheel,add="+")

    def _on_rows_configure(self, event=None) -> None:
        if not self._closed:
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event) -> None:
        if not self._closed:
            self.canvas.itemconfigure(
                self._window, width=max(1, event.width))

    def _scroll_wheel(self, event) -> str:
        if not self._closed:
            delta=int(getattr(event,"delta",0))
            if delta:
                self.canvas.yview_scroll(-1 if delta>0 else 1,"units")
        return "break"

    def _toggle_password(self) -> None:
        if self._closed:
            return
        show="" if self.show_password_var.get() else "*"
        for entry in self.entry_pass:
            entry.configure(show=show)

    def toggle_row(self, index: int) -> bool:
        if self._closed:
            return False
        checked=self.selection.toggle(index)
        self.row_selectors[index].configure(text="✅️" if checked else "⬜")
        return checked

    def toggle_all(self) -> bool:
        if self._closed:
            return False
        checked=self.selection.toggle_all()
        for selector in self.row_selectors:
            selector.configure(text="✅️" if checked else "⬜")
        return checked

    def snapshot(self, index: int) -> AccountRowSnapshot:
        """Memory-only row read. Do not log/serialize passwords."""
        if self._closed:
            raise RuntimeError("ACCOUNT_VIEW_CLOSED")
        return AccountRowSnapshot(
            selected=self.selection.checked(index),
            username=self.username_vars[index].get(),
            password=self.password_vars[index].get(),
            captcha_mode=self.captcha_vars[index].get())

    def hydrate_legacy_read_only(self, records) -> None:
        """S38: show verified fields, never infer original checkbox token.

        S37 account view selection remains its own in-memory state. An '❔'
        marker means original check semantics are unknown, not unchecked.
        Legacy 'Có' is displayed literally without adding it as a choice or
        silently translating it to a current captcha mode.
        """
        if self._closed:
            raise RuntimeError("ACCOUNT_VIEW_CLOSED")
        from login_account_legacy import (
            ALLOWED_CAPTCHA_RAW, LegacyAccountRecord, MAX_LEGACY_ROWS,
        )
        records = tuple(records)
        if len(records) > MAX_LEGACY_ROWS or any(
            not isinstance(row, LegacyAccountRecord)
            or row.captcha_raw not in ALLOWED_CAPTCHA_RAW
            for row in records
        ):
            raise ValueError("UNSAFE_LEGACY_RECORDS")
        for index, row in enumerate(records):
            self.username_vars[index].set(row.username)
            self.password_vars[index].set(row.password)
            self.captcha_vars[index].set(row.captcha_raw)
            self.row_selectors[index].configure(text="❔")
        # No transfer of raw check/proxy tokens to actionable UI, no writes.
        self.read_only_legacy_count = len(records)

    def show_legacy_load_status(self, status: str) -> None:
        """Small, sanitized footer below Canvas; never show credential text."""
        if self._closed or status == "EMPTY":
            return
        import tkinter as tk
        text = ("Tài khoản cũ: chỉ đọc; dấu chọn chưa xác minh"
                if status == "READY"
                else "Dữ liệu tài khoản cũ chưa an toàn để nạp (" + status + ")")
        self.legacy_status_label = tk.Label(
            self.group_accounts, text=text, anchor="w",
            font=("Segoe UI", 8), foreground="#8a3300")
        self.legacy_status_label.place(x=9, y=690, width=400, height=18)

    def shutdown(self) -> None:
        if self._closed:
            return
        self._closed=True
        # Destruction is intentionally not a save event: the legacy
        # 5-field check/captcha serialization rules remain unverified.
        for value in self.password_vars:
            value.set("")
        self.group_accounts.destroy()
