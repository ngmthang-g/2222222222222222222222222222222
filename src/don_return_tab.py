"""S181 real Dồn local settings editor for PLAN L02/L03 return & priority.

This tab edits original [DonVang] INI values, not the game's inventory,
movement, selling or donor/receiver commands. No fake Start button. Kept
separate from known-good Farm/Train and original licensing modules.
"""
from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import ttk

from don_train_panel import TkDonTrainSettingsPanel
from don_preset_editor import TkDonPresetEditor
from don_receiver_panel import TkDonReceiverReadOnlyPanel
from farm_original_maps import coord_name_for_id
from don_return_settings import (
    DON_RETURN_OPTIONS, NAV_DEFAULTS, NAV_OPTIONS,
    DonReturnConfig, DonReturnSettingsError, DonReturnSettingsStore,
)


class TkDonReturnTab(ttk.Frame):
    """Byte-preserving Dồn configuration panel with live INI saving."""

    def __init__(self, parent, *, settings_file: str | Path):
        if not isinstance(settings_file, (str, Path)) or not str(settings_file):
            raise ValueError("DON_SHARED_SETTINGS_FILE_REQUIRED")
        super().__init__(parent)
        self.store = DonReturnSettingsStore(settings_file)
        self.snapshot = None
        self.last_error: str | None = None
        self._closed = False
        self._blocked = False
        self._restoring = False
        try:
            self.snapshot = self.store.load()
        except (DonReturnSettingsError, OSError, ValueError) as exc:
            self.last_error = type(exc).__name__
            self._blocked = True
        initial = self.snapshot.value if self.snapshot else DonReturnConfig()

        self.mode_var = tk.StringVar(master=self, value=initial.mode)
        self.minutes_var = tk.StringVar(master=self, value=initial.minutes)
        self.nav_vars = [
            tk.StringVar(master=self, value=v) for v in initial.navigation
        ]
        self.inputs = []

        group = ttk.LabelFrame(self, text="Cấu hình Về thành")
        group.pack(fill="x", padx=6, pady=(7, 5))
        ttk.Label(group, text="Điều kiện về thành:").pack(
            anchor="w", padx=6, pady=(4, 1))
        radio_line = ttk.Frame(group)
        radio_line.pack(fill="x", padx=6, pady=(0, 5))
        for caption, code in DON_RETURN_OPTIONS:
            btn = ttk.Radiobutton(
                radio_line, text=caption,
                value=code, variable=self.mode_var,
                command=self._change_mode)
            btn.pack(side="left", padx=(0, 8))
            self.inputs.append(btn)
        minutes = ttk.Entry(
            radio_line, width=6, textvariable=self.minutes_var)
        minutes.pack(side="left")
        self.inputs.append(minutes)
        minutes.bind("<Return>", lambda _e: self._change_minutes(), add="+")
        minutes.bind("<FocusOut>", lambda _e: self._change_minutes(), add="+")

        ttk.Label(group, text="Phương thức về thành:").pack(
            anchor="w", padx=6, pady=(0, 2))
        ttk.Label(group, text="Ưu tiên lần lượt:").pack(
            anchor="w", padx=6, pady=(0, 2))
        priorities = ttk.Frame(group)
        priorities.pack(fill="x", padx=5, pady=(0, 6))
        self.nav_combos = []
        for i, var in enumerate(self.nav_vars):
            combo = ttk.Combobox(
                priorities, width=9, textvariable=var, state="readonly",
                values=NAV_OPTIONS)
            combo.grid(row=0, column=i, padx=(0, 4), sticky="ew")
            combo.bind(
                "<<ComboboxSelected>>",
                lambda _e, n=i: self._change_priority(n),
                add="+")
            priorities.columnconfigure(i, weight=1)
            self.nav_combos.append(combo)
            self.inputs.append(combo)

        # S182 joins real original [DonVang] Train/recovery option writes.
        # Both independent panels must keep the same full-file snapshot fresh.
        self.train_panel = TkDonTrainSettingsPanel(
            self, settings_file=settings_file,
            on_saved=self._sync_after_train_save)
        self.train_panel.pack(fill="x", padx=6, pady=(1, 5))

        # L05/L06 saved coordinates live in the SAME [DonVang] section.
        # Never infer selected receiver accounts from a window title.
        self.preset_panel = TkDonPresetEditor(
            self, settings_file=settings_file,
            on_saved=self._sync_after_preset_save)
        self.preset_panel.pack(fill="x", padx=6, pady=(1, 4))
        self.receiver_panel = TkDonReceiverReadOnlyPanel(
            self, settings_file=settings_file)
        self.receiver_panel.pack(fill="x", padx=6, pady=(0, 3))

        self.status = ttk.Label(self, text="", wraplength=420, anchor="w")
        self.status.pack(fill="x", padx=6, pady=(0, 4))
        # Original has Train/bag/recovery/receivers and account buttons.
        # Do not offer non-working commands in the independent executable.
        accounts = ttk.LabelFrame(self, text="Danh sách tài khoản")
        accounts.pack(fill="both", expand=True, padx=6, pady=(3, 4))
        list_frame = ttk.Frame(accounts)
        list_frame.pack(fill="both", expand=True, padx=3, pady=3)
        self.account_table = ttk.Treeview(
            list_frame, columns=("character", "coordinate"),
            show="headings", height=7, selectmode="none")
        self.account_table.heading("character", text="Nhân vật")
        self.account_table.heading("coordinate", text="Tọa độ Train / Bán")
        self.account_table.column("character", width=152, stretch=True)
        self.account_table.column("coordinate", width=206, stretch=True)
        scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical",
            command=self.account_table.yview)
        self.account_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.account_table.pack(side="left", fill="both", expand=True)
        ttk.Label(
            self, wraplength=410, justify="left",
            text=("Đã hỗ trợ lưu cấu hình Về thành / ưu tiên Phù. "
                  "Chức năng Dồn, nhận/vàng, tương tác game và "
                  "danh sách nhân vật thật chưa được kết nối."),
        ).pack(fill="x", padx=6, pady=(0, 7))
        self._refresh_controls()
        self._priority_choices()
        if self._blocked:
            self._set_status(
                "Cấu hình Dồn chưa an toàn để chỉnh sửa; giữ nguyên dữ liệu")
        elif self.snapshot is not None and self.snapshot.loaded_legacy_full_bag:
            self._set_status(
                "Đã đọc full_bag cũ; sẽ chỉ đổi khóa khi bạn sửa trực tiếp")
        else:
            self._set_status("Đã nạp cấu hình Dồn từ settings.ini")
        self.bind("<Destroy>", self._on_destroy, add="+")

    def _allowed(self) -> bool:
        return not self._closed and not self._blocked and self.snapshot is not None

    def _set_status(self, message: str):
        if not self._closed:
            self.status.configure(text=message)

    def _priority_choices(self):
        """Recreate original L03 no-new-duplicate combobox selection policy."""
        current = [var.get() for var in self.nav_vars]
        for i, combo in enumerate(self.nav_combos):
            used = {v for j, v in enumerate(current) if j != i and v}
            values = tuple(
                v for v in NAV_OPTIONS
                if not v or v == current[i] or v not in used)
            combo.configure(values=values)

    def _refresh_controls(self):
        for w in self.inputs:
            w.configure(
                state=("readonly" if isinstance(w, ttk.Combobox)
                       and self._allowed() else
                       "normal" if self._allowed() else "disabled"))

    def _restore(self):
        if self._closed or self.snapshot is None:
            return
        self._restoring = True
        try:
            self.mode_var.set(self.snapshot.value.mode)
            self.minutes_var.set(self.snapshot.value.minutes)
            for var, value in zip(self.nav_vars, self.snapshot.value.navigation):
                var.set(value)
        finally:
            self._restoring = False
        self._priority_choices()

    def _commit(self, key: str, value: str) -> bool:
        if not self._allowed() or self._restoring:
            return False
        try:
            self.snapshot = self.store.save_change(
                key, value, expected_bytes=self.snapshot.file_bytes)
        except (DonReturnSettingsError, OSError, ValueError) as exc:
            self.last_error = type(exc).__name__
            self._set_status(
                "Không lưu Dồn: dữ liệu không hợp lệ hoặc settings.ini thay đổi")
            # Strict write stale state must force a new tab/open rather than
            # rolling back to an old local snapshot and overwriting the file.
            if (self.last_error in (
                    "STALE_DON_RETURN_SETTINGS",
                    "DON_RETURN_SETTINGS_CHANGED_CONCURRENTLY",
                    "AMBIGUOUS_DON_RETURN_OPTION",
                    "DUPLICATE_DONVANG_SECTION")):
                self._blocked = True
                self._refresh_controls()
            self._restore()
            return False
        self.last_error = None
        self._restore()
        self.train_panel.sync_after_other_save()
        self.preset_panel.reload_after_other_save()
        self.receiver_panel.reload()
        self._set_status("Đã lưu cấu hình Dồn vào settings.ini")
        return True

    def _change_mode(self):
        return self._commit("town_condition", self.mode_var.get())

    def _change_minutes(self):
        return self._commit("loop_minutes", self.minutes_var.get())

    def _change_priority(self, index: int):
        if not isinstance(index, int) or index not in range(4):
            return False
        if not self._allowed():
            self._restore()
            return False
        # Prevent any new duplicate even when a manual Tk variable mutation
        # bypasses the readonly Combobox options.
        value = self.nav_vars[index].get()
        if value and any(
                j != index and v.get() == value
                for j, v in enumerate(self.nav_vars)):
            self.last_error = "DUPLICATE_DON_NAV_PRIORITY"
            self._set_status("Mỗi phương thức về thành chỉ được chọn 1 lần")
            self._restore()
            return False
        return self._commit(f"nav_priority_{index + 1}", value)

    def _sync_after_train_save(self):
        """Reload return snapshot after a sibling atomic write to settings.ini."""
        if self._closed or self._blocked:
            return False
        try:
            self.snapshot = self.store.load()
        except (OSError, ValueError, DonReturnSettingsError) as exc:
            self.last_error = type(exc).__name__
            self._blocked = True
            self._refresh_controls()
            self._set_status(
                "Cấu hình Dồn đã thay đổi; đóng/mở lại tab trước khi chỉnh")
            return False
        self._restore()
        self.preset_panel.reload_after_other_save()
        self.receiver_panel.reload()
        return True

    def _sync_after_preset_save(self):
        """Coordinate save updates snapshots for both S181/S182 editors."""
        if self._closed:
            return False
        self.train_panel.sync_after_other_save()
        self.receiver_panel.reload()
        if self._blocked:
            return False
        try:
            self.snapshot = self.store.load()
        except (DonReturnSettingsError, OSError, ValueError) as exc:
            self.last_error = type(exc).__name__
            self._blocked = True
            self._refresh_controls()
            self._set_status("Không thể đồng bộ cấu hình Dồn; hãy mở lại tab")
            return False
        self._restore()
        return True

    def _start_refresh(self) -> bool:
        """E08 notebook return: refresh all Dồn editors from one INI revision.

        Avoid discarding pending numeric/coordinate edits and incomplete
        + Thêm tọa độ forms. Nothing is written on tab selection.
        """
        if not self._allowed():
            return False
        if (self.mode_var.get() != self.snapshot.value.mode
                or self.minutes_var.get() != self.snapshot.value.minutes
                or tuple(v.get() for v in self.nav_vars)
                != self.snapshot.value.navigation):
            self._set_status("Có chỉnh sửa Về thành chưa lưu; không nạp đè")
            return False
        trainer = self.train_panel
        if (trainer.snapshot is None or trainer._blocked
                or any(var.get() != getattr(trainer.snapshot.value, key)
                       for key, var in trainer.vars.items())):
            self._set_status("Có chỉnh sửa Train chưa lưu; giữ nguyên nội dung")
            return False
        preset = self.preset_panel
        if preset.snapshot is None or preset._blocked or preset._add_open:
            self._set_status(
                "Đang thêm tọa độ hoặc cấu hình Map chưa an toàn; không nạp đè")
            return False
        if len(preset.widgets) != len(preset.snapshot.rows):
            self._set_status("Danh sách tọa độ đang chỉnh sửa; không nạp đè")
            return False
        for cell, row in zip(preset.widgets, preset.snapshot.rows):
            if (cell["name"].get() != row.name
                    or cell["map"].get() != (coord_name_for_id(row.map_id) or "")
                    or cell["x"].get() != row.x
                    or cell["y"].get() != row.y):
                self._set_status(
                    "Tọa độ đang chỉnh sửa chưa lưu; giữ nguyên nội dung")
                return False
        try:
            latest = self.store.load()
        except (DonReturnSettingsError, OSError, ValueError) as exc:
            self.last_error = type(exc).__name__
            self._blocked = True
            self._refresh_controls()
            self._set_status("Dồn không thể nạp lại dữ liệu an toàn; mở lại tab")
            return False
        if latest.file_bytes != self.snapshot.file_bytes:
            self.snapshot = latest
            self._restore()
            if not trainer.sync_after_other_save():
                self._blocked = True
            if not preset.reload_after_other_save():
                self._blocked = True
            self.receiver_panel.reload()
            self._refresh_controls()
            if self._blocked:
                self._set_status("Cấu hình Dồn có phần dữ liệu không an toàn")
                return False
            self._set_status("Đã đồng bộ cấu hình Dồn từ các tab khác")
        return True

    def _stop_refresh(self):
        # User controls save explicitly. Tab exit never sends/writes.
        return None

    def shutdown(self):
        if self._closed:
            return
        self.train_panel.shutdown()
        self.preset_panel.shutdown()
        self.receiver_panel.shutdown()
        self._closed = True

    def _on_destroy(self, event):
        if event.widget is self:
            self.shutdown()
