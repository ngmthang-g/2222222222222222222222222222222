"""S180 source-first Daily (Trừng Ác / Tàng Bảo Đồ) top configuration.

A real Tk editor for frozen K03/K10/K16 [Settings] keys. No game client
transport exists yet, so no fake Daily Start/apply-to-account/game controls.
"""
from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import ttk

from daily_top_settings import (
    DailyConfigError, DailyTopConfig, DailyTopSettingsStore,
    DailyTopSnapshot, TREASURE_HEAL_COORDS,
)


class TkDailyTopTab(ttk.Frame):
    """Original-backed Daily persisted settings, independent of TLM license."""

    def __init__(self, parent, *, settings_file: str | Path):
        if not isinstance(settings_file, (str, Path)) or not str(settings_file):
            raise ValueError("DAILY_SHARED_SETTINGS_FILE_REQUIRED")
        super().__init__(parent)
        self.store = DailyTopSettingsStore(settings_file)
        self.snapshot: DailyTopSnapshot | None = None
        self._restoring = False
        self._closed = False
        self._blocked = False
        self.last_error: str | None = None
        try:
            self.snapshot = self.store.load()
        except (DailyConfigError, OSError, ValueError) as exc:
            self.last_error = type(exc).__name__
            self._blocked = True
        value = self.snapshot.value if self.snapshot else DailyTopConfig()
        self.vars = {}
        for field in DailyTopConfig.__dataclass_fields__:
            initial = getattr(value, field)
            kind = tk.BooleanVar if type(initial) is bool else tk.StringVar
            self.vars[field] = kind(master=self, value=initial)

        self.inputs = []
        punish = ttk.LabelFrame(self, text="Trừng ác")
        punish.pack(fill="x", padx=6, pady=(7, 5))
        self._duration_field(
            punish, "Thời gian đánh ác tặc (giây):",
            "daily_punish_duration")
        mode_line = ttk.Frame(punish)
        mode_line.pack(fill="x", padx=6, pady=(4, 1))
        ttk.Label(mode_line, text="Cách về NPC nhận nhiệm vụ:").pack(
            anchor="w")
        choices = ttk.Frame(punish)
        choices.pack(fill="x", padx=6, pady=(1, 5))
        self._radio(choices, "Ngựa", "daily_move_mode", "horse")
        self._radio(choices, "Định vị phù", "daily_move_mode", "teleport")
        ttk.Label(choices, text="Phím tắt phù:").pack(
            side="left", padx=(9, 3))
        tele = ttk.Combobox(
            choices, state="readonly", width=4,
            textvariable=self.vars["daily_tele_hotkey"],
            values=("", "1", "2", "3"))
        tele.pack(side="left")
        tele.bind("<<ComboboxSelected>>",
                  lambda _e: self._commit("daily_tele_hotkey"), add="+")
        self.inputs.append(tele)
        self._check(
            punish, "Trị liệu khi HP < 30%",
            "daily_punish_heal", right_text="Vị trí trị liệu: Tô Châu")
        self._check(
            punish, "Lọc trang bị (vứt vũ khí, trang bị trong quá trình làm nhiệm vụ)",
            "daily_punish_discard_equip")
        checks = ttk.Frame(punish)
        checks.pack(fill="x", padx=6, pady=(1, 5))
        self._check(checks, "Tự kết nối lại khi mất mạng",
                    "daily_punish_dc_reconnect", inline=True)
        self._check(checks, "Hồi sinh khi chết/Địa phủ",
                    "daily_punish_respawn", inline=True)

        treasure = ttk.LabelFrame(self, text="Tàng bảo đồ")
        treasure.pack(fill="x", padx=6, pady=(2, 5))
        self._duration_field(
            treasure, "Thời gian đánh trong huyệt mộ (giây):",
            "daily_treasure_map_tomb_dur")
        heal_line = ttk.Frame(treasure)
        heal_line.pack(fill="x", padx=6, pady=(1, 2))
        self._check(
            heal_line, "Trị liệu sau khi đào nếu HP < 30%",
            "daily_treasure_heal", inline=True)
        ttk.Label(heal_line, text="Vị trí trị liệu:").pack(
            side="left", padx=(4, 3))
        location = ttk.Combobox(
            heal_line, state="readonly", width=10,
            textvariable=self.vars["daily_treasure_heal_map"],
            values=tuple(TREASURE_HEAL_COORDS))
        location.pack(side="left")
        location.bind("<<ComboboxSelected>>",
                      lambda _e: self._commit("daily_treasure_heal_map"),
                      add="+")
        self.inputs.append(location)
        check_row = ttk.Frame(treasure)
        check_row.pack(fill="x", padx=6, pady=(1, 5))
        self._check(check_row, "Tự kết nối lại khi mất mạng",
                    "daily_treasure_dc_reconnect", inline=True)
        self._check(check_row, "Hồi sinh khi chết/Địa phủ",
                    "daily_treasure_respawn", inline=True)

        self.status = ttk.Label(self, text="", anchor="w", wraplength=410)
        self.status.pack(fill="x", padx=6, pady=(2, 4))
        accounts = ttk.LabelFrame(self, text="Danh sách tài khoản")
        accounts.pack(fill="both", expand=True, padx=6, pady=(0, 5))
        table_frame = ttk.Frame(accounts)
        table_frame.pack(fill="both", expand=True)
        self.account_table = ttk.Treeview(
            table_frame, columns=("character", "activity"),
            show="headings", selectmode="none", height=8)
        self.account_table.heading("character", text="Nhân vật")
        self.account_table.heading("activity", text="Hoạt động")
        self.account_table.column("character", width=160, stretch=True)
        self.account_table.column("activity", width=166, stretch=True)
        bar = ttk.Scrollbar(table_frame, orient="vertical",
                            command=self.account_table.yview)
        self.account_table.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y")
        self.account_table.pack(side="left", fill="both", expand=True)
        ttk.Label(
            self, text=("Đã kết nối lưu cấu hình Daily. Chưa có dữ liệu "
                        "nhân vật/HP thật hoặc bộ điều khiển Trừng Ác và "
                        "Tàng Bảo Đồ được xác minh; không chạy game."),
            wraplength=410, justify="left",
        ).pack(fill="x", padx=6, pady=(1, 6))
        if self._blocked:
            self._set_status("Không thể sửa: cấu hình Daily chưa an toàn")
        else:
            self._set_status(
                "Đã nạp cấu hình Daily; chỉ chỉnh các tùy chọn được chứng thực")
        self._refresh_controls()
        self.bind("<Destroy>", self._on_destroy, add="+")

    def _set_status(self, message: str):
        if not self._closed:
            self.status.configure(text=message)

    def _duration_field(self, parent, caption: str, key: str):
        row = ttk.Frame(parent)
        row.pack(fill="x", padx=6, pady=(5, 1))
        ttk.Label(row, text=caption).pack(side="left")
        entry = ttk.Entry(row, width=5, textvariable=self.vars[key])
        entry.pack(side="left", padx=(8, 0))
        self.inputs = getattr(self, "inputs", [])
        self.inputs.append(entry)
        # Focus-out or Enter respects transient empty edits unlike saving
        # partially typed digit strings on each keystroke.
        entry.bind("<FocusOut>",
                   lambda _e, k=key: self._commit(k), add="+")
        entry.bind("<Return>",
                   lambda _e, k=key: self._commit(k), add="+")

    def _radio(self, parent, caption: str, key: str, value: str):
        widget = ttk.Radiobutton(
            parent, text=caption, value=value,
            variable=self.vars[key],
            command=lambda k=key: self._commit(k))
        widget.pack(side="left", padx=(0, 8))
        self.inputs.append(widget)

    def _check(self, parent, caption: str, key: str, *,
               inline: bool = False, right_text: str = ""):
        line = parent if inline else ttk.Frame(parent)
        if not inline:
            line.pack(fill="x", padx=6, pady=(1, 2))
        widget = ttk.Checkbutton(
            line, text=caption, variable=self.vars[key],
            command=lambda k=key: self._commit(k))
        widget.pack(side="left", padx=(0, 9))
        self.inputs.append(widget)
        if right_text:
            ttk.Label(line, text=right_text).pack(side="left")

    def _allowed(self):
        return not self._closed and not self._blocked and self.snapshot is not None

    def _refresh_controls(self):
        state = "normal" if self._allowed() else "disabled"
        for widget in self.inputs:
            if isinstance(widget, ttk.Combobox):
                widget.configure(state="readonly" if self._allowed() else "disabled")
            else:
                widget.configure(state=state)

    def _restore(self):
        if self.snapshot is None or self._closed:
            return
        self._restoring = True
        try:
            for name, var in self.vars.items():
                var.set(getattr(self.snapshot.value, name))
        finally:
            self._restoring = False

    def _commit(self, key: str) -> bool:
        if self._restoring or not self._allowed():
            return False
        value = self.vars[key].get()
        try:
            self.snapshot = self.store.save_change(
                key, value, expected_bytes=self.snapshot.file_bytes)
        except (DailyConfigError, OSError, ValueError) as exc:
            self.last_error = type(exc).__name__
            self._set_status("Không lưu Daily: dữ liệu sai hoặc settings.ini đã đổi")
            self._restore()
            if self.last_error in (
                    "STALE_DAILY_SETTINGS", "DAILY_SETTINGS_CHANGED_CONCURRENTLY",
                    "DUPLICATE_SETTINGS_SECTION", "DUPLICATE_DAILY_OPTION"):
                self._blocked = True
                self._refresh_controls()
            return False
        self.last_error = None
        self._restore()
        if self.snapshot.mode_conflict:
            self._set_status(
                "Đã lưu; daily_tele_use cũ khác daily_move_mode. "
                "Chưa tự chuyển đổi dữ liệu cũ.")
        else:
            self._set_status("Đã lưu cấu hình Daily vào settings.ini")
        return True

    def shutdown(self):
        self._closed = True

    def _on_destroy(self, event):
        if event.widget is self:
            self.shutdown()
