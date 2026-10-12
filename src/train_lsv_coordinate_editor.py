"""S170 real source-backed TrainLSV saved-coordinate Tk editing, NO move.

The original I10 has Train apply action, but the independent product
does not implement LSV gameplay movement. We expose only working
add/save/delete/hide and never present an inert Train button.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Callable

from train_lsv_coordinates import (
    LSV_MAP_IDS, LSV_MAP_NAMES, LsvCoordinate, LsvCoordinatesSnapshot,
    TrainLsvCoordinatesStore,
)


class TkTrainLsvCoordinates(ttk.LabelFrame):
    def __init__(self, parent, *, settings_file: str | Path,
                 on_saved: Callable[[], None] | None = None):
        super().__init__(parent, text="Cấu hình tọa độ lưu sẵn")
        self.store = TrainLsvCoordinatesStore(settings_file)
        self._on_saved = on_saved
        self._closed = False
        self._blocked = False
        self._show_list = True
        self.snapshot: LsvCoordinatesSnapshot | None = None
        self.error: str | None = None
        self.rows: dict[int, dict] = {}
        self.content = ttk.Frame(self)
        self.content.pack(fill="x", padx=5, pady=(4, 0))
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=5, pady=3)
        self.add_btn = ttk.Button(toolbar, text="+ Thêm tọa độ", command=self._show_add)
        self.add_btn.pack(side="left")
        self.toggle_btn = ttk.Button(
            toolbar, text="Ẩn danh sách tọa độ", command=self._toggle_list)
        self.toggle_btn.pack(side="right")
        self.reload_btn = ttk.Button(toolbar, text="Nạp lại", command=self.reload)
        self.reload_btn.pack(side="right", padx=(0, 7))
        self.status = ttk.Label(self, text="")
        self.status.pack(fill="x", padx=6, pady=(0, 2))
        self.reload()
        self.bind("<Destroy>", self._on_destroy, add="+")

    def reload(self):
        if self._closed:
            return False
        try:
            self.snapshot = self.store.load()
            self._blocked = False
            self.error = None
        except Exception as exc:
            self._blocked = True
            self.snapshot = None
            self.error = type(exc).__name__
        self._render()
        return not self._blocked

    def sync_after_top_save(self):
        """Top checkbox save changes file bytes but NOT coordinate records.

        Keep existing coordinate drafts in widgets so a user does not lose
        typing from an unrelated verified top-settings click.
        """
        if self._closed or self.snapshot is None:
            return
        try:
            refreshed = self.store.load()
            if (refreshed.rows != self.snapshot.rows or
                    refreshed.skipped_retired != self.snapshot.skipped_retired):
                self.status.configure(text="Tọa độ đã thay đổi; bấm Nạp lại")
                return
            self.snapshot = refreshed
        except Exception:
            self.status.configure(text="Cấu hình thay đổi; bấm Nạp lại")

    def _toggle_list(self):
        self._show_list = not self._show_list
        if self._show_list:
            self.content.pack(fill="x", padx=5, pady=(4, 0), before=self.add_btn.master)
        else:
            self.content.pack_forget()
        self.toggle_btn.configure(text=(
            "Ẩn danh sách tọa độ" if self._show_list
            else "Hiện danh sách tọa độ"))

    def _render(self):
        for child in self.content.winfo_children():
            child.destroy()
        self.rows = {}
        if self.snapshot is None:
            self.status.configure(text="Tọa độ Train LSV không an toàn để chỉnh sửa")
            self.add_btn.configure(state="disabled")
            return
        self.add_btn.configure(state="normal")
        headings = ttk.Frame(self.content)
        headings.pack(fill="x")
        for text, width in (("Tên", 16), ("Map", 20), ("X", 6), ("Y", 6),
                            ("Lưu", 5), ("Xóa", 5)):
            ttk.Label(headings, text=text, width=width).pack(side="left")
        for record in self.snapshot.rows:
            self._make_row(record)
        skipped = len(self.snapshot.skipped_retired)
        if skipped:
            self.status.configure(text=(
                f"Bỏ qua {skipped} tọa độ có MapID không còn hợp lệ. "
                "Bản ghi gốc vẫn được giữ nguyên."))
        else:
            self.status.configure(text="Tọa độ lưu trên đĩa; chưa tự di chuyển game")

    def _make_row(self, record: LsvCoordinate | None = None):
        new = record is None
        row = ttk.Frame(self.content)
        row.pack(fill="x", pady=1)
        name=tk.StringVar(master=self, value=record.name if record else "")
        map_name=tk.StringVar(
            master=self, value=LSV_MAP_IDS[record.map_id] if record else
            next(iter(LSV_MAP_NAMES)))
        x=tk.StringVar(master=self, value=record.x if record else "")
        y=tk.StringVar(master=self, value=record.y if record else "")
        ttk.Entry(row, textvariable=name, width=16).pack(side="left")
        ttk.Combobox(row, textvariable=map_name, width=19,
                     values=tuple(LSV_MAP_NAMES),
                     state="readonly").pack(side="left")
        ttk.Entry(row, textvariable=x, width=6).pack(side="left")
        ttk.Entry(row, textvariable=y, width=6).pack(side="left")
        number=record.key_number if record else None
        save=ttk.Button(
            row, text="Lưu", width=5,
            command=lambda: self._save(number,name.get(),map_name.get(),x.get(),y.get()))
        save.pack(side="left")
        deleter=ttk.Button(
            row, text="✕" if not new else "Hủy", width=5,
            command=(lambda: row.destroy() if new else self._delete(number)))
        deleter.pack(side="left")
        entry={"frame":row,"name":name,"map":map_name,"x":x,"y":y,
               "save":save,"delete":deleter}
        if not new:
            self.rows[number]=entry
        return entry

    def _show_add(self):
        if not self._blocked and self.snapshot is not None:
            self._make_row(None)

    def _save(self, number, name, map_name, x, y):
        if self._closed or self._blocked or self.snapshot is None:
            return False
        try:
            if map_name not in LSV_MAP_NAMES:
                raise ValueError("UNKNOWN_LSV_MAP_NAME")
            self.snapshot = self.store.save_row(
                expected_bytes=self.snapshot.file_bytes,
                key_number=number, name=name,
                map_id=LSV_MAP_NAMES[map_name],x=x,y=y)
        except Exception as exc:
            self.error=type(exc).__name__
            self.status.configure(text="Không lưu: tọa độ không hợp lệ hoặc file đã đổi")
            return False
        self._render()
        if callable(self._on_saved):
            self._on_saved()
        return True

    def _delete(self, number):
        if self._closed or self._blocked or self.snapshot is None:
            return False
        try:
            self.snapshot=self.store.delete_row(
                number,expected_bytes=self.snapshot.file_bytes)
        except Exception as exc:
            self.error=type(exc).__name__
            self.status.configure(text="Không xóa: file đã đổi hoặc tọa độ không hợp lệ")
            return False
        self._render()
        if callable(self._on_saved):
            self._on_saved()
        return True

    def _on_destroy(self,event):
        if event.widget is self:
            self._closed=True
