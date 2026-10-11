"""S121: real Tk editor of EXISTING H11 Farm coordinate presets.

Partial verified H11 UI behavior only. No new-row defaults, autosave timer,
live per-account combobox, Train, Sell, game, authorization or Proxy.
User commits edits on Return/FocusOut/map selection, an explicitly local
commit boundary rather than an asserted original auto-save cadence.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from farm_original_maps import FARM_MAP_LIST, coord_id_for_name, coord_name_for_id
from farm_preset_account_binding import FarmAccountPresetBindings
from train_saved_coordinates import FarmCoordinate, FarmCoordinatesStore


class FarmSavedCoordinatesEditor(ttk.Frame):
    """Real Tk -> real H11 [Farm].coord_N, existing presets ONLY.

    If stored rows contain retired MapIDs or cannot be parsed, editing is
    disabled; otherwise a replacement would silently lose unknown data.
    """

    def __init__(self, parent, *, store: FarmCoordinatesStore | None = None,
                 account_bindings: FarmAccountPresetBindings | None = None):
        super().__init__(parent)
        self.store = store if store is not None else FarmCoordinatesStore()
        self.account_bindings = (account_bindings if account_bindings is not None
                                 else FarmAccountPresetBindings())
        self.rows: tuple[FarmCoordinate, ...] = ()
        self.last_error: str | None = None
        self._blocked = False
        self._closed = False
        self._body_visible = True
        self.row_widgets: list[dict] = []
        self.group = ttk.LabelFrame(self, text="Cấu hình tọa độ lưu sẵn")
        self.group.pack(fill="x", padx=6, pady=(4, 0))
        self._header = ttk.Frame(self.group)
        for i, (caption, width) in enumerate((
            ("Tên", 17), ("Map", 25), ("X", 6), ("Y", 6),
            ("Áp dụng hết", 12), ("", 6), ("Xóa", 4))):
            ttk.Label(self._header, text=caption, width=width).grid(
                row=0, column=i, sticky="w")
        self._header.pack(fill="x", padx=5)
        self._body = ttk.Frame(self.group)
        self._body.pack(fill="x", padx=5)
        self._toolbar = ttk.Frame(self.group)
        self._toolbar.pack(fill="x", padx=5, pady=(3, 4))
        # The original "+ Thêm tọa độ" needs unverified map/X/Y defaults.
        # Do not display an inert/guessed button.
        self.toggle_button = ttk.Button(
            self._toolbar, text="Ẩn danh sách tọa độ",
            command=self.toggle_list)
        self.toggle_button.pack(side="right")
        self.status = ttk.Label(self, text="", anchor="w")
        self.status.pack(fill="x", padx=6)
        self._load_initial()
        self.bind("<Destroy>", self._on_destroy, add="+")

    def _load_initial(self):
        try:
            loaded = self.store.load()
            self.rows = loaded.rows
            self._blocked = bool(loaded.skipped_retired_map_ids)
            if self._blocked:
                self._set_status("Có MapID cũ: giữ nguyên dữ liệu, chỉ xem")
            else:
                self._set_status("Chỉnh sửa tọa độ đã lưu; Enter hoặc rời ô để lưu")
        except Exception as exc:
            self._blocked = True
            self.last_error = type(exc).__name__
            self._set_status("Dữ liệu tọa độ chưa an toàn để chỉnh sửa")
        self.account_bindings.refresh(self.rows)
        self._render()

    def _set_status(self, message: str):
        if not self._closed:
            self.status.configure(text=message)

    def _render(self):
        for child in self._body.winfo_children():
            child.destroy()
        self.row_widgets.clear()
        choices = tuple(name for name, _mid in FARM_MAP_LIST)
        for index, record in enumerate(self.rows):
            name = tk.StringVar(master=self, value=record.name)
            mapname = tk.StringVar(master=self, value=coord_name_for_id(record.map_id) or "")
            x = tk.StringVar(master=self, value=record.x)
            y = tk.StringVar(master=self, value=record.y)
            entries = [
                ttk.Entry(self._body, textvariable=name, width=17),
                ttk.Combobox(self._body, textvariable=mapname, values=choices,
                             state="readonly" if not self._blocked else "disabled",
                             width=25),
                ttk.Entry(self._body, textvariable=x, width=6),
                ttk.Entry(self._body, textvariable=y, width=6),
            ]
            for col, w in enumerate(entries):
                w.grid(row=index, column=col, sticky="ew")
                if self._blocked and isinstance(w, ttk.Entry):
                    w.configure(state="disabled")
            entry_name, combo, entry_x, entry_y = entries
            for widget in (entry_name, entry_x, entry_y):
                widget.bind("<Return>", lambda ev, i=index: self.commit_row(i), add="+")
                widget.bind("<FocusOut>", lambda ev, i=index: self.commit_row(i), add="+")
            combo.bind("<<ComboboxSelected>>",
                       lambda ev, i=index: self._select_map(i), add="+")
            apply_sell = ttk.Button(
                self._body, text="Bán", width=5,
                command=lambda i=index: self.apply_row_to_all(i, target="sell"))
            apply_train = ttk.Button(
                self._body, text="Train", width=5,
                command=lambda i=index: self.apply_row_to_all(i, target="farm"))
            apply_sell.grid(row=index, column=4)
            apply_train.grid(row=index, column=5)
            delete = ttk.Button(
                self._body, text="✕", width=4,
                command=lambda i=index: self.delete_row(i))
            delete.grid(row=index, column=6)
            if self._blocked:
                delete.configure(state="disabled")
            self.row_widgets.append({
                "name": name, "map": mapname, "x": x, "y": y,
                "combo": combo, "delete": delete, "entries": entries,
                "apply_sell": apply_sell, "apply_train": apply_train,
            })
        self._sync_apply_buttons()

    def register_account_combos(self, sell: ttk.Combobox, farm: ttk.Combobox) -> None:
        """Connect ONLY real caller-owned account-row selectors."""
        if self._closed or self._blocked:
            raise ValueError("UNAVAILABLE_FARM_EDITOR")
        self.account_bindings.register(sell, farm, rows=self.rows)
        self._sync_apply_buttons()

    def unregister_account_combos(self, sell: ttk.Combobox, farm: ttk.Combobox):
        self.account_bindings.unregister(sell, farm)
        self._sync_apply_buttons()

    def _sync_apply_buttons(self):
        sell_enabled = (not self._blocked and
                        self.account_bindings.editable_count("sell") > 0)
        farm_enabled = (not self._blocked and
                        self.account_bindings.editable_count("farm") > 0)
        for row in self.row_widgets:
            row["apply_sell"].configure(state="normal" if sell_enabled else "disabled")
            row["apply_train"].configure(state="normal" if farm_enabled else "disabled")

    def apply_row_to_all(self, index: int, *, target: str) -> int:
        """Original name-based apply-all; NEVER trigger game Sell/Train action."""
        if (self._closed or self._blocked
                or not 0 <= index < len(self.rows)
                or not self._fresh()):
            return 0
        try:
            count = self.account_bindings.apply_to_all(
                self.rows[index].name, target=target)
        except ValueError:
            return 0
        self._set_status("Đã áp dụng tọa độ" if count else "Không có tài khoản khả dụng")
        return count

    def _select_map(self, index: int) -> bool:
        if self._closed or self._blocked or not 0 <= index < len(self.row_widgets):
            return False
        cell = self.row_widgets[index]
        if cell["map"].get() == "===================":
            # Use the selected INDEX, since five separator labels are equal.
            current = cell["combo"].current()
            for name, mid in FARM_MAP_LIST[current + 1:]:
                if mid is not None:
                    cell["map"].set(name)
                    break
            else:
                self._restore(index)
                return False
        return self.commit_row(index)

    def _restore(self, index: int) -> None:
        if not 0 <= index < len(self.rows):
            return
        record = self.rows[index]
        cell = self.row_widgets[index]
        cell["name"].set(record.name)
        cell["map"].set(coord_name_for_id(record.map_id) or "")
        cell["x"].set(record.x)
        cell["y"].set(record.y)

    def _fresh(self) -> bool:
        try:
            loaded = self.store.load()
        except Exception as exc:
            self.last_error = type(exc).__name__
            return False
        return (not loaded.skipped_retired_map_ids and loaded.rows == self.rows)

    def commit_row(self, index: int) -> bool:
        if (self._closed or self._blocked
                or not 0 <= index < len(self.rows)):
            return False
        cell = self.row_widgets[index]
        mid = coord_id_for_name(cell["map"].get())
        if mid is None or not self._fresh():
            self.last_error = "INVALID_MAP_OR_STALE_FILE"
            self._restore(index)
            self._set_status("Không lưu: MapID hoặc dữ liệu đĩa chưa hợp lệ")
            return False
        candidate = FarmCoordinate(cell["name"].get(), mid,
                                   cell["x"].get(), cell["y"].get())
        if candidate == self.rows[index]:
            return True
        updated = list(self.rows)
        updated[index] = candidate
        try:
            self.store.save(tuple(updated))
        except Exception as exc:
            self.last_error = type(exc).__name__
            self._restore(index)
            self._set_status("Lỗi lưu tọa độ: dữ liệu cũ được giữ lại")
            return False
        previous = self.rows[index]
        self.rows = tuple(updated)
        self.account_bindings.refresh(
            self.rows,
            {previous.name: candidate.name} if previous.name != candidate.name else None)
        self.last_error = None
        self._set_status("Đã lưu tọa độ")
        return True

    def delete_row(self, index: int) -> bool:
        if (self._closed or self._blocked
                or not 0 <= index < len(self.rows)):
            return False
        if not self._fresh():
            self.last_error = "STALE_OR_UNSAFE_FILE"
            self._set_status("Không xóa: dữ liệu đĩa đã thay đổi")
            return False
        updated = self.rows[:index] + self.rows[index + 1:]
        try:
            self.store.save(updated)
        except Exception as exc:
            self.last_error = type(exc).__name__
            self._set_status("Không xóa được: giữ nguyên tọa độ")
            return False
        self.rows = updated
        self.account_bindings.refresh(self.rows)
        self.last_error = None
        self._render()
        self._set_status("Đã xóa tọa độ")
        return True

    def toggle_list(self) -> bool:
        if self._closed:
            return False
        self._body_visible = not self._body_visible
        if self._body_visible:
            # Repack body first: Tk cannot use an unpacked widget as "before".
            self._body.pack(fill="x", padx=5, before=self._toolbar)
            self._header.pack(fill="x", padx=5, before=self._body)
            self.toggle_button.configure(text="Ẩn danh sách tọa độ")
        else:
            self._header.pack_forget()
            self._body.pack_forget()
            self.toggle_button.configure(text="Hiện danh sách tọa độ")
        return self._body_visible

    def _on_destroy(self, event):
        if event.widget is self:
            self._closed = True
