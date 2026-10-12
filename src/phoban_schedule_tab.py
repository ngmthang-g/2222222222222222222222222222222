"""S184 real Phó Bản group/schedule editor, NOT dungeon game execution.

J04/J05/J06/J11 original group/schedule controls are source-backed. Every
edit actually persists to [Settings]/phoban_groups. Leader/member dropdowns
stay unavailable without verified RoleName/HWND/PID. No pretend Start,
Tắt auto PB or in-game map dispatch.
"""
from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import ttk

from phoban_modes_panel import TkPhoBanModesPanel
from phoban_schedule_settings import (
    ACTIVITIES, PHOBAN_NAMES, TRAIN_NAMES,
    PhoBanConfig, PhoBanConfigError, PhoBanConfigStore,
)

class TkPhoBanScheduleTab(ttk.Frame):
    def __init__(self, parent, *, settings_file: str | Path):
        if not isinstance(settings_file, (str, Path)) or not str(settings_file):
            raise ValueError("PHOBAN_SETTINGS_FILE_REQUIRED")
        super().__init__(parent)
        self.store = PhoBanConfigStore(settings_file)
        self.snapshot = None
        self._closed = False
        self._blocked = False
        self._refreshing = False
        self.last_error = None
        try:
            self.snapshot = self.store.load()
            self._blocked = self.snapshot.legacy_only
        except (PhoBanConfigError, OSError, ValueError) as exc:
            self.last_error = type(exc).__name__
            self._blocked = True

        team = ttk.LabelFrame(self, text="Cấu hình tổ đội")
        team.pack(fill="x", padx=6, pady=(7, 3))
        ttk.Label(
            team, text=("Danh sách acc sẵn sàng: "
                        "Chưa có RoleName thật đã xác minh"),
            wraplength=410).pack(anchor="w", padx=6, pady=5)
        # S185: exact original persisted checkbox modes. No game workers.
        self.modes_panel = TkPhoBanModesPanel(
            self, settings_file=settings_file,
            on_saved=self._sync_after_mode_save)
        self.modes_panel.pack(fill="x")

        ttk.Label(
            self, text=("Lịch trình và cấu hình nhóm được lưu thực tế. "
                        "Không tạo/điều khiển đội, đánh quái hoặc chạy Phó Bản "
                        "khi chưa có bộ đọc game thật."),
            wraplength=412).pack(fill="x", padx=7, pady=(1, 3))
        group = ttk.LabelFrame(self, text="Cấu hình lịch trình")
        group.pack(fill="both", expand=True, padx=6, pady=(2, 4))
        scrollhost = ttk.Frame(group)
        scrollhost.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(
            scrollhost, highlightthickness=0, background="#f1f1f1")
        self.scrollbar = ttk.Scrollbar(
            scrollhost, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.clusters = ttk.Frame(self.canvas)
        self.content_window = self.canvas.create_window(
            (0, 0), window=self.clusters, anchor="nw")
        self.clusters.bind(
            "<Configure>",
            lambda _e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")),
            add="+")
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfigure(
                self.content_window, width=e.width),
            add="+")
        self.add_group_button = ttk.Button(
            group, text="+ Thêm nhóm", command=self.add_group)
        self.add_group_button.pack(anchor="w", padx=6, pady=4)
        self.status = ttk.Label(self, text="", wraplength=410)
        self.status.pack(fill="x", padx=7, pady=(1, 5))
        self._render()
        if self.snapshot is None:
            self._message("Không thể đọc cấu hình Phó Bản; giữ nguyên file")
        elif self.snapshot.legacy_only:
            self._message(
                "Chỉ có cấu hình Phó Bản cũ: giữ nguyên cho đến khi "
                "biết quy tắc chuyển đổi")
        else:
            self._message("Lịch trình hiện là cấu hình, chưa chạy game")
        self.bind("<Destroy>", self._on_destroy, add="+")

    def _enabled(self):
        return not self._closed and not self._blocked and self.snapshot is not None

    def _message(self, text):
        if not self._closed:
            self.status.configure(text=text)

    def _save(self, updated: PhoBanConfig) -> bool:
        if not self._enabled():
            return False
        try:
            self.snapshot = self.store.save(
                updated, expected_bytes=self.snapshot.file_bytes)
        except (PhoBanConfigError, OSError, ValueError) as exc:
            self.last_error = str(exc)
            if self.last_error in ("STALE_PHOBAN_SETTINGS",
                                   "PHOBAN_SETTINGS_CHANGED"):
                self._blocked = True
            self._message("Không lưu Phó Bản: dữ liệu không an toàn hoặc đã đổi")
            self._render()
            return False
        self.last_error = None
        self.modes_panel.sync_after_other_save()
        self._render()
        self._message("Đã lưu nhóm/lịch trình Phó Bản vào settings.ini")
        return True

    def _render(self):
        self._refreshing = True
        try:
            for child in self.clusters.winfo_children():
                child.destroy()
            self.add_group_button.configure(
                state="normal" if self._enabled() else "disabled")
            cfg = self.snapshot.config if self.snapshot else PhoBanConfig()
            for gi, group in enumerate(cfg.groups):
                self._render_group(gi, group)
        finally:
            self._refreshing = False

    def _render_group(self, gi, group):
        block = ttk.LabelFrame(self.clusters, text=f"Nhóm {gi+1}")
        block.pack(fill="x", padx=3, pady=(2, 5))
        topline = ttk.Frame(block)
        topline.pack(fill="x", padx=4, pady=(2, 3))
        label = ("(đã lưu, chưa xác minh)" if any(group.members)
                 else "(chưa chọn)")
        ttk.Label(
            topline, text=f"Đội trưởng: {label}").pack(side="left")
        remove = ttk.Button(
            topline, text="✕ Xóa nhóm",
            command=lambda g=gi: self.remove_group(g))
        remove.pack(side="right")
        if not self._enabled():
            remove.configure(state="disabled")
        members = ttk.Frame(block)
        members.pack(fill="x", padx=4)
        # Six original slots, read-only saved names. DO NOT populate with
        # Windows titles or assume the saved names are logged into game.
        for slot in range(6):
            name = group.members[slot] if slot < len(group.members) else ""
            box = ttk.Combobox(
                members, values=(), state="disabled", width=14)
            box.grid(row=slot // 3, column=slot % 3, padx=2, pady=1, sticky="ew")
            box.set(name)
        for col in range(3):
            members.columnconfigure(col, weight=1)
        header = ttk.Frame(block)
        header.pack(fill="x", padx=4, pady=(4, 1))
        for col, (caption, width) in enumerate((
                ("", 3), ("Hoạt động", 9), ("Tên Map", 19),
                ("Lần", 5), ("Status", 6), ("Xóa", 4))):
            ttk.Label(header, text=caption, width=width).grid(
                row=0, column=col, sticky="w")
        row_host = ttk.Frame(block)
        row_host.pack(fill="x", padx=4)
        for ri, row in enumerate(group.schedule):
            self._render_schedule(row_host, gi, ri, row)
        ttk.Button(
            block, text="+ Thêm Lịch trình",
            command=lambda g=gi: self.add_schedule(g),
            state="normal" if self._enabled() else "disabled",
        ).pack(anchor="w", padx=5, pady=(2, 4))

    def _render_schedule(self, parent, gi, ri, row):
        enabled = tk.BooleanVar(master=self, value=row.enabled)
        activity = tk.StringVar(master=self, value=row.activity or "")
        name = tk.StringVar(master=self, value=row.name or "")
        times = tk.StringVar(master=self, value=str(row.times))
        state = "normal" if self._enabled() else "disabled"
        check = ttk.Checkbutton(
            parent, variable=enabled,
            command=lambda g=gi,r=ri,v=enabled:
                self.edit_schedule(g,r,"enabled",v.get()))
        check.grid(row=ri,column=0,sticky="w")
        combo_a = ttk.Combobox(
            parent, values=ACTIVITIES, textvariable=activity,
            state="readonly" if self._enabled() else "disabled", width=9)
        combo_a.grid(row=ri,column=1,padx=1)
        combo_a.bind(
            "<<ComboboxSelected>>",
            lambda _e,g=gi,r=ri,v=activity:
                self.edit_schedule(g,r,"activity",v.get()),
            add="+")
        choices = (PHOBAN_NAMES if row.activity=="Phó bản"
                   else TRAIN_NAMES if row.activity=="Train" else ())
        combo_n = ttk.Combobox(
            parent, values=choices, textvariable=name, width=19,
            state=("readonly" if self._enabled() and choices else "disabled"))
        combo_n.grid(row=ri,column=2,padx=1)
        combo_n.bind(
            "<<ComboboxSelected>>",
            lambda _e,g=gi,r=ri,v=name:
                self.edit_schedule(g,r,"name",v.get()),
            add="+")
        count = ttk.Entry(parent, textvariable=times, width=5, state=state)
        count.grid(row=ri,column=3,padx=1)
        for event in ("<Return>","<FocusOut>"):
            count.bind(
                event, lambda _e,g=gi,r=ri,v=times:
                    self.edit_schedule(g,r,"times",v.get()),
                add="+")
        ttk.Label(parent, text="Chưa", foreground="#808080", width=6).grid(
            row=ri,column=4,padx=1)
        ttk.Button(
            parent, text="✕", width=3,
            state=state,
            command=lambda g=gi,r=ri:self.remove_schedule(g,r),
        ).grid(row=ri,column=5,padx=1)

    def add_group(self):
        if self._enabled():
            return self._save(self.snapshot.config.add_group())
        return False

    def remove_group(self, index):
        if not self._enabled():
            return False
        try:
            return self._save(self.snapshot.config.delete_group(index))
        except PhoBanConfigError:
            return False

    def add_schedule(self, group):
        if not self._enabled():
            return False
        try:
            return self._save(self.snapshot.config.add_schedule(group))
        except PhoBanConfigError:
            return False

    def remove_schedule(self, group, row):
        if not self._enabled():
            return False
        try:
            return self._save(self.snapshot.config.delete_schedule(group,row))
        except PhoBanConfigError:
            return False

    def edit_schedule(self, group, row, field, value):
        if not self._enabled() or self._refreshing:
            return False
        try:
            cfg=self.snapshot.config.edit_schedule(group,row,field,value)
        except PhoBanConfigError:
            self._render()
            self._message("Giá trị hoạt động/tên Map/số lần chưa hợp lệ")
            return False
        return self._save(cfg)

    def _sync_after_mode_save(self) -> bool:
        """A checkbox's single-key write refreshes schedule's file snapshot."""
        if self._closed:
            return False
        try:
            snapshot = self.store.load()
        except (PhoBanConfigError, OSError, ValueError) as exc:
            self.last_error = str(exc)
            self._blocked = True
            self._render()
            self._message("Cấu hình Phó Bản không an toàn, mở lại tab")
            return False
        self.snapshot = snapshot
        self._blocked = snapshot.legacy_only
        return True

    def shutdown(self):
        if self._closed:
            return
        self.modes_panel.shutdown()
        self._closed=True

    def _on_destroy(self, event):
        if event.widget is self:
            self.shutdown()
