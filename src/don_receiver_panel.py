"""S183 original saved Dồn receiver settings presentation — NO active accounts.

Reads the one shared coordinate and compatible receiver account row labels
from settings.ini, shows conflicts instead of choosing a migration winner.
The game-dependent account selection remains disabled pending genuine
RoleName+live HWND/PID evidence; no fake receiver or running-state button.
"""
from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import ttk

from don_receiver_readonly import (
    DonReceiverConfigError, DonReceiverConfigReader,
)


class TkDonReceiverReadOnlyPanel(ttk.Frame):
    def __init__(self, parent, *, settings_file: str | Path):
        super().__init__(parent)
        self.reader = DonReceiverConfigReader(settings_file)
        self._closed = False
        self.group = ttk.LabelFrame(self, text="Danh sách tài khoản nhận")
        self.group.pack(fill="x")
        coords = ttk.Frame(self.group)
        coords.pack(fill="x", padx=5, pady=(3, 2))
        ttk.Label(coords, text="Tọa độ dồn:").pack(side="left")
        self.coord = tk.StringVar(master=self, value="")
        self.coord_display = ttk.Entry(
            coords, textvariable=self.coord, state="readonly", width=27)
        self.coord_display.pack(side="left", padx=4)
        self.rows = ttk.Frame(self.group)
        self.rows.pack(fill="x", padx=5, pady=3)
        self.status = ttk.Label(
            self, text="", wraplength=412, anchor="w")
        self.status.pack(fill="x", padx=3, pady=(2, 3))
        self.reload()

    def reload(self):
        if self._closed:
            return
        for child in self.rows.winfo_children():
            child.destroy()
        self.coord.set("")
        try:
            saved = self.reader.load()
        except (DonReceiverConfigError, OSError, ValueError) as exc:
            self.status.configure(
                text="Không thể xác minh cấu hình người nhận; giữ nguyên file")
            return
        if saved.resolved_shared_coordinate:
            self.coord.set(saved.resolved_shared_coordinate)
        if saved.migration_conflict:
            self.status.configure(text=(
                "recv_coord và recv_N_coord mâu thuẫn: không tự chọn "
                "tọa độ dồn hoặc ghi đè cấu hình cũ"))
        else:
            self.status.configure(text=(
                "Tên bên dưới chỉ là cấu hình đã lưu; chưa xác minh "
                "nhân vật đang đăng nhập. Không bật chọn tài khoản/giao dịch"))
        for i, label in enumerate(saved.saved_receiver_labels, 1):
            row = ttk.Frame(self.rows)
            row.pack(fill="x", pady=1)
            ttk.Label(row, text=f"Acc nhận {i}:", width=13).pack(side="left")
            field = ttk.Entry(row, width=31)
            field.pack(side="left", fill="x", expand=True)
            field.insert(0, label)
            field.configure(state="readonly")

    def shutdown(self):
        self._closed = True

    def _on_destroy(self, event):
        if event.widget is self:
            self.shutdown()
