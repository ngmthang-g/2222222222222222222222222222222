"""S183 original L05 saved-coordinate editor for independent Dồn config.

User supplies every value when adding a row (original new-row coordinate
defaults UNKNOWN). Existing rows can be edited/deleted only when references
remain safe. Apply "Train" is disabled until genuine managed character rows
exist: this panel NEVER fabricates accounts or sends movement commands.
"""
from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import ttk

from don_preset_store import (
    DonPresetError, DonPresetStore, next_don_preset_name,
)
from farm_original_maps import (
    FARM_MAP_LIST, coord_id_for_name, coord_name_for_id,
)
from train_saved_coordinates import FarmCoordinate


class TkDonPresetEditor(ttk.Frame):
    def __init__(self, parent, *, settings_file: str | Path, on_saved=None):
        super().__init__(parent)
        self.store = DonPresetStore(settings_file)
        self.on_saved = on_saved
        self.snapshot = None
        self._blocked = False
        self._closed = False
        self._hidden = False
        self.last_error = None
        self.widgets = []
        self._map_choices = tuple(label for label, _ in FARM_MAP_LIST)
        self.group = ttk.LabelFrame(self, text="Cấu hình tọa độ lưu sẵn")
        self.group.pack(fill="x")
        self.head = ttk.Frame(self.group)
        self.head.pack(fill="x", padx=5, pady=(2, 0))
        for col, (text, width) in enumerate((
                ("Tên", 11), ("Map", 19), ("X", 5),
                ("Y", 5), ("Áp dụng", 7), ("Xóa", 4))):
            ttk.Label(self.head, text=text, width=width).grid(
                row=0, column=col, sticky="w")
        self.body = ttk.Frame(self.group)
        self.body.pack(fill="x", padx=5)
        toolbar = ttk.Frame(self.group)
        toolbar.pack(fill="x", padx=5, pady=(3, 4))
        self.add_button = ttk.Button(
            toolbar, text="+ Thêm tọa độ", command=self.open_add)
        self.add_button.pack(side="left")
        self.toggle_button = ttk.Button(
            toolbar, text="Ẩn danh sách tọa độ", command=self.toggle)
        self.toggle_button.pack(side="right")
        self.add_form = ttk.Frame(self.group)
        self._add_open = False
        self.new_name = tk.StringVar(master=self, value="")
        self.new_map = tk.StringVar(master=self, value="")
        self.new_x = tk.StringVar(master=self, value="")
        self.new_y = tk.StringVar(master=self, value="")
        self._new_vars = (self.new_name, self.new_map, self.new_x, self.new_y)
        ttk.Label(self.add_form, text="Tên / Map / X / Y:").pack(
            anchor="w", padx=4)
        entry_line = ttk.Frame(self.add_form)
        entry_line.pack(fill="x", padx=4)
        ttk.Entry(entry_line, textvariable=self.new_name, width=12).pack(
            side="left")
        self.new_map_combo = ttk.Combobox(
            entry_line, textvariable=self.new_map, width=16,
            state="readonly", values=self._map_choices)
        self.new_map_combo.pack(side="left", padx=2)
        self.new_map_combo.bind(
            "<<ComboboxSelected>>", lambda _e: self._normalize_new_map(),
            add="+")
        ttk.Entry(entry_line, textvariable=self.new_x, width=5).pack(
            side="left")
        ttk.Entry(entry_line, textvariable=self.new_y, width=5).pack(
            side="left", padx=2)
        ttk.Button(
            entry_line, text="Lưu", command=self.add_explicit).pack(
            side="left", padx=2)
        ttk.Button(
            entry_line, text="Hủy", command=self.close_add).pack(
            side="left")
        self.status = ttk.Label(self, text="", wraplength=413)
        self.status.pack(fill="x", pady=2)
        self._load()
        self.bind("<Destroy>", self._on_destroy, add="+")

    def _load(self):
        try:
            self.snapshot = self.store.load()
            self._blocked = bool(self.snapshot.skipped_retired_map_ids)
        except (DonPresetError, OSError, ValueError) as exc:
            self.last_error = type(exc).__name__
            self._blocked = True
        self._render()
        if self._blocked:
            self._status("MapID/dữ liệu cũ chưa an toàn; không chỉnh sửa")
        else:
            self._status("Lưu tọa độ vào [DonVang] sau khi xác nhận từng ô")

    def _status(self, message):
        if not self._closed:
            self.status.configure(text=message)

    def _enabled(self):
        return not self._closed and not self._blocked and self.snapshot is not None

    def _map_next(self, combo, var):
        if var.get() != "===================":
            return True
        selected = combo.current()
        for name, mid in FARM_MAP_LIST[selected + 1:]:
            if mid is not None:
                var.set(name)
                return True
        return False

    def _normalize_new_map(self):
        self._map_next(self.new_map_combo, self.new_map)

    def _render(self):
        for w in self.body.winfo_children():
            w.destroy()
        self.widgets.clear()
        rows = self.snapshot.rows if self.snapshot else ()
        for i, row in enumerate(rows):
            cell = {}
            for key, val in (
                    ("name", row.name),
                    ("map", coord_name_for_id(row.map_id) or ""),
                    ("x", row.x), ("y", row.y)):
                cell[key] = tk.StringVar(master=self, value=val)
            widgets = (
                ttk.Entry(self.body, textvariable=cell["name"], width=11),
                ttk.Combobox(
                    self.body, textvariable=cell["map"],
                    values=self._map_choices, state="readonly", width=19),
                ttk.Entry(self.body, textvariable=cell["x"], width=5),
                ttk.Entry(self.body, textvariable=cell["y"], width=5),
            )
            for j, widget in enumerate(widgets):
                widget.grid(row=i, column=j, padx=1, pady=1, sticky="ew")
                if not self._enabled():
                    widget.configure(state="disabled")
            for widget in (widgets[0], widgets[2], widgets[3]):
                widget.bind(
                    "<Return>", lambda _e, n=i: self.save_row(n), add="+")
                widget.bind(
                    "<FocusOut>", lambda _e, n=i: self.save_row(n), add="+")
            widgets[1].bind(
                "<<ComboboxSelected>>",
                lambda _e, n=i: self.select_map(n), add="+")
            # L05 Train is a real apply-to-account UI action, not equivalent
            # to editing/saving a config. No authenticated roles -> disabled.
            btn = ttk.Button(
                self.body, text="Train", width=6, state="disabled")
            btn.grid(row=i, column=4, padx=1)
            delete = ttk.Button(
                self.body, text="✕", width=3,
                command=lambda n=i: self.delete_row(n))
            delete.grid(row=i, column=5, padx=1)
            if not self._enabled():
                delete.configure(state="disabled")
            cell["combobox"] = widgets[1]
            self.widgets.append(cell)
        self.add_button.configure(
            state="normal" if self._enabled() else "disabled")

    def _fresh(self):
        if not self._enabled():
            return False
        try:
            now = self.store.load()
        except (DonPresetError, OSError):
            self._blocked = True
            self._render()
            return False
        if now.file_bytes != self.snapshot.file_bytes:
            self._blocked = True
            self._render()
            self._status("settings.ini đã đổi bên ngoài; mở lại tab")
            return False
        return True

    def _commit(self, rows):
        if not self._fresh():
            return False
        try:
            self.snapshot = self.store.save(
                tuple(rows), expected_bytes=self.snapshot.file_bytes)
        except (DonPresetError, OSError, ValueError) as exc:
            self.last_error = str(exc)
            self._status("Không lưu tọa độ: dữ liệu/MapID/tham chiếu không hợp lệ")
            # Keep last valid stored snapshot and restore invalid edits.
            self._render()
            return False
        self.last_error = None
        self._render()
        self._status("Đã lưu tọa độ Dồn vào settings.ini")
        if callable(self.on_saved):
            self.on_saved()
        return True

    def select_map(self, index):
        if not 0 <= index < len(self.widgets):
            return False
        row = self.widgets[index]
        if not self._map_next(row["combobox"], row["map"]):
            self._render()
            return False
        return self.save_row(index)

    def save_row(self, index):
        if not self._enabled() or not 0 <= index < len(self.widgets):
            return False
        c = self.widgets[index]
        mid = coord_id_for_name(c["map"].get())
        if mid is None:
            self._status("MapID chưa được xác minh")
            return False
        rows = list(self.snapshot.rows)
        updated = FarmCoordinate(
            c["name"].get(), mid, c["x"].get(), c["y"].get())
        if rows[index] == updated:
            return True
        rows[index] = updated
        return self._commit(rows)

    def delete_row(self, index):
        if not self._enabled() or not 0 <= index < len(self.snapshot.rows):
            return False
        rows = list(self.snapshot.rows)
        del rows[index]
        return self._commit(rows)

    def toggle(self):
        self._hidden = not self._hidden
        if self._hidden:
            self.head.pack_forget()
            self.body.pack_forget()
        else:
            self.head.pack(fill="x", padx=5, pady=(2, 0),
                           before=self._toolbar())
            self.body.pack(fill="x", padx=5, before=self._toolbar())
        self.toggle_button.configure(
            text="Hiện danh sách tọa độ" if self._hidden
            else "Ẩn danh sách tọa độ")

    def _toolbar(self):
        return self.toggle_button.master

    def open_add(self):
        if not self._enabled():
            return False
        if not self._add_open:
            self.new_name.set(next_don_preset_name(self.snapshot.rows))
            # Original new map/X/Y defaults UNKNOWN: deliberately blank.
            self.new_map.set("")
            self.new_x.set("")
            self.new_y.set("")
            self.add_form.pack(fill="x", padx=5, pady=2)
            self._add_open = True
        return True

    def close_add(self):
        if self._add_open:
            self.add_form.pack_forget()
        self._add_open = False

    def add_explicit(self):
        if not self._enabled() or not self._add_open:
            return False
        mid = coord_id_for_name(self.new_map.get())
        if mid is None:
            self._status("Chọn Map có MapID hợp lệ")
            return False
        row = FarmCoordinate(
            self.new_name.get(), mid, self.new_x.get(), self.new_y.get())
        if self._commit(tuple(self.snapshot.rows) + (row,)):
            self.close_add()
            return True
        return False

    def reload_after_other_save(self):
        if not self._enabled():
            return False
        try:
            self.snapshot = self.store.load()
            if self.snapshot.skipped_retired_map_ids:
                self._blocked = True
                self._render()
                return False
            self._render()
            return True
        except (DonPresetError, OSError, ValueError):
            self._blocked = True
            self._render()
            return False

    def shutdown(self):
        self._closed = True

    def _on_destroy(self, event):
        if event.widget is self:
            self.shutdown()
