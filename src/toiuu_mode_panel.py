"""S186 original N05 Tối ưu mode selection widgets, no TLMP game actions.

The three original gray buttons ONLY assign a mode in the present list.
No names or rows are created from HWND/window titles. A future verified
RoleName+PID+HWND+generation reader must call apply_attested_roster() on Tk's
owner thread; until that day all gray selection controls remain disabled.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from toiuu_mode_selection import (
    AttestedGameRole, KEY_TO_LABEL, LABEL_TO_KEY, MODE_NAMES,
    MODE_ORDER, ToiuuSelectionError, ToiuuSelectionState,
)


class TkToiuuModeSelectionPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.state = ToiuuSelectionState()
        self._closed = False
        self._drawing = False
        self._buttons = []
        actions = ttk.Frame(self)
        actions.pack(fill="x", padx=4, pady=(3, 5))
        for mode in MODE_ORDER:
            button = ttk.Button(
                actions, text=KEY_TO_LABEL[mode],
                command=lambda value=mode: self.select_all(value))
            button.pack(side="left", fill="x", expand=True, padx=2)
            self._buttons.append(button)
        self.account_table = ttk.Frame(self)
        self.account_table.pack(fill="both", expand=True, padx=4, pady=(0, 4))
        heading = ttk.Frame(self.account_table)
        heading.pack(fill="x")
        ttk.Label(heading, text="Nhân vật", width=19).pack(side="left")
        ttk.Label(heading, text="Giảm cấu hình").pack(side="left")
        self.rows = ttk.Frame(self.account_table)
        self.rows.pack(fill="both", expand=True)
        self.status = ttk.Label(
            self,
            text=("Chưa có nguồn RoleName đã xác minh. "
                  "Nút xám chỉ chọn chế độ, không tối ưu game."),
            wraplength=405, justify="left")
        self.status.pack(fill="x", padx=4, pady=(1, 4))
        self._render()
        self.bind("<Destroy>", self._on_destroy, add="+")

    def _render(self):
        if self._closed:
            return
        self._drawing = True
        try:
            for child in self.rows.winfo_children():
                child.destroy()
            enabled = bool(self.state.accounts)
            for button in self._buttons:
                button.configure(state="normal" if enabled else "disabled")
            for record in self.state.accounts:
                line = ttk.Frame(self.rows)
                line.pack(fill="x", pady=1)
                ttk.Label(line, text=record.role.name, width=19).pack(
                    side="left")
                selected = tk.StringVar(master=self, value=record.display_mode)
                combo = ttk.Combobox(
                    line, textvariable=selected, values=MODE_NAMES,
                    state="readonly", width=17)
                combo.pack(side="left", padx=2)
                ident = record.role.identity
                combo.bind(
                    "<<ComboboxSelected>>",
                    lambda _e, target=ident, val=selected:
                        self.select_one(target, val.get()), add="+")
            if not enabled:
                self.status.configure(text=(
                    "Chưa có dữ liệu tên nhân vật thật từ client; "
                    "không tạo hàng hoặc chọn cấu hình giả."))
        finally:
            self._drawing = False

    def apply_attested_roster(self, observations: tuple[AttestedGameRole, ...],
                              *, revision: int) -> bool:
        """Only call from UI thread after original/client adapter attestation.

        No production caller is supplied now. This refuses ambiguous/stale
        identities and cannot turn selecting a mode into native application.
        """
        if self._closed:
            return False
        try:
            updated = self.state.with_roster(observations, revision=revision)
        except ToiuuSelectionError:
            self.clear_unverified_roster()
            return False
        self.state = updated
        self._render()
        if updated.accounts:
            self.status.configure(text=(
                f"Đã đồng bộ {len(updated.accounts)} tên nhân vật được xác minh. "
                "Chọn chế độ chỉ đổi lựa chọn, chưa kích hoạt tối ưu game."))
        return True

    def clear_unverified_roster(self):
        if self._closed:
            return
        self.state = self.state.clear_roster()
        self._render()

    def select_all(self, mode: str) -> bool:
        if self._closed:
            return False
        try:
            self.state = self.state.select_all(mode)
        except ToiuuSelectionError:
            return False
        self._render()
        self.status.configure(
            text=f"Đã chọn {KEY_TO_LABEL[mode]} cho các dòng đã xác minh; "
                 "không gửi lệnh tối ưu game.")
        return True

    def select_one(self, identity: tuple[str, int, int, int],
                   display_mode: str) -> bool:
        if self._closed:
            return False
        if display_mode not in LABEL_TO_KEY:
            self._render()
            return False
        try:
            self.state = self.state.select_account(
                identity, LABEL_TO_KEY[display_mode])
        except ToiuuSelectionError:
            self._render()
            return False
        self._render()
        self.status.configure(text=(
            "Đã đổi lựa chọn cho một nhân vật đã xác minh. "
            "Không gửi TLMP; Không là bỏ qua, không phải khôi phục."))
        return True

    def shutdown(self):
        if self._closed:
            return
        self._closed = True
        self.state = self.state.clear_roster()

    def _on_destroy(self, event):
        if event.widget is self:
            self.shutdown()
