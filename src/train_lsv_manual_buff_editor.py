"""S171 genuine Tk manual TrainLSV buff configuration, no DLL/key sending.

The fixed Dạ Minh Châu index is UNKNOWN; render its proven defaults as
a readonly, non-deletable reference. Every existing buff_* row is
unclassified and protected. Only rows created THIS UI session may be
removed; saved dynamic rows from previous sessions remain read-only.
"""
from __future__ import annotations

from pathlib import Path
from tkinter import ttk
import tkinter as tk
from typing import Callable

from train_lsv_manual_buffs import (
    BUFF_KEYS,BUFF_DEFAULT,TrainLsvBuffStore,LsvBuffSnapshot,
)


class TkTrainLsvManualBuffs(ttk.LabelFrame):
    def __init__(self,parent,*,settings_file: str | Path,
                 on_saved: Callable[[],None] | None=None):
        super().__init__(parent,text="Dùng thủ công châu, đan dược (2x, 4x...)")
        self.store=TrainLsvBuffStore(settings_file)
        self.on_saved=on_saved
        self._closed=False
        self._blocked=False
        self.snapshot: LsvBuffSnapshot | None=None
        self.session_owned: dict[int,str]={}
        self.error: str | None=None
        ttk.Label(self,text=(
            "Dạ Minh Châu — luôn bật, mặc định phím 1 / 0 phút 5 giây. "
            "Chưa chỉnh/lưu dòng cố định: số buff_* gốc chưa xác định."),
            wraplength=440,justify="left").pack(anchor="w",padx=5,pady=3)
        self.body=ttk.Frame(self)
        self.body.pack(fill="x",padx=5)
        bar=ttk.Frame(self)
        bar.pack(fill="x",padx=5,pady=3)
        self.add_btn=ttk.Button(bar,text="+ Thêm lịch thủ công",command=self.add_draft)
        self.add_btn.pack(side="left")
        self.reload_btn=ttk.Button(bar,text="Nạp lại",command=self.reload)
        self.reload_btn.pack(side="right")
        self.status=ttk.Label(self,text="",wraplength=440)
        self.status.pack(fill="x",padx=5,pady=(0,3))
        self.reload()
        self.bind("<Destroy>",self._on_destroy,add="+")

    def reload(self):
        if self._closed:return False
        # A reload after external editing invalidates proof of ownership.
        # A saved row from another session may be the fixed Dạ Minh Châu.
        self.session_owned.clear()
        try:
            self.snapshot=self.store.load()
            self._blocked=False
            self.error=None
        except Exception as exc:
            self.snapshot=None
            self._blocked=True
            self.error=type(exc).__name__
        self._render()
        return not self._blocked

    def sync_after_other_save(self):
        """Other S169/S170 section edits update file bytes without losing drafts."""
        if self._closed or self.snapshot is None:
            return False
        try:
            new=self.store.load()
            if new.rows!=self.snapshot.rows:
                self.status.configure(text="Lịch buff trên đĩa đã đổi; bấm Nạp lại")
                return False
            self.snapshot=new
            return True
        except Exception:
            self.status.configure(text="Không đọc được cấu hình; bấm Nạp lại")
            return False

    def _render(self):
        for child in self.body.winfo_children():
            child.destroy()
        self.row_widgets={}
        if self.snapshot is None:
            self.add_btn.configure(state="disabled")
            self.status.configure(text="Cấu hình buff không an toàn để chỉnh sửa")
            return
        self.add_btn.configure(state="normal")
        title=ttk.Frame(self.body)
        title.pack(fill="x")
        for text,width in (("Bật",5),("Phím",11),("Phút",7),
                           ("Giây",7),("Chế độ",11)):
            ttk.Label(title,text=text,width=width).pack(side="left")
        for rec in self.snapshot.rows:
            line=ttk.Frame(self.body)
            line.pack(fill="x")
            label=("Bật" if rec.enabled else "Tắt") if rec.key else "?"
            ttk.Label(line,text=label,width=5).pack(side="left")
            ttk.Label(line,text=rec.key if rec.key else "?",width=11).pack(side="left")
            ttk.Label(line,text=rec.minutes if rec.minutes else "?",width=7).pack(side="left")
            ttk.Label(line,text=rec.seconds if rec.seconds else "?",width=7).pack(side="left")
            is_owned=self.session_owned.get(rec.number)==rec.raw
            if is_owned:
                ttk.Button(line,text="Sửa",command=lambda n=rec.number:self.edit_owned(n)).pack(side="left")
                btn=ttk.Button(line,text="Xóa",command=lambda n=rec.number:self.delete_owned(n))
                btn.pack(side="left")
            else:
                ttk.Label(line,text="Bảo vệ",width=11).pack(side="left")
            self.row_widgets[rec.number]=line
        self.status.configure(text=(
            "Lịch thủ công đã lưu; các dòng có sẵn được bảo vệ vì "
            "chưa phân biệt được dòng Dạ Minh Châu cố định."))

    def add_draft(self):
        if self._closed or self._blocked or self.snapshot is None:
            return None
        line=ttk.Frame(self.body)
        line.pack(fill="x")
        enabled=tk.BooleanVar(master=self,value=BUFF_DEFAULT[0])
        key=tk.StringVar(master=self,value=BUFF_DEFAULT[1])
        minute=tk.StringVar(master=self,value=BUFF_DEFAULT[2])
        second=tk.StringVar(master=self,value=BUFF_DEFAULT[3])
        ttk.Checkbutton(line,variable=enabled,width=5).pack(side="left")
        ttk.Combobox(line,textvariable=key,values=BUFF_KEYS,
                     state="readonly",width=9).pack(side="left")
        def digits(candidate):
            return candidate=="" or (candidate.isascii() and candidate.isdecimal())
        vcmd=(self.register(digits),"%P")
        ttk.Entry(line,textvariable=minute,width=7,validate="key",
                  validatecommand=vcmd).pack(side="left")
        ttk.Entry(line,textvariable=second,width=7,validate="key",
                  validatecommand=vcmd).pack(side="left")
        save=ttk.Button(line,text="Lưu",
            command=lambda:self._append(enabled.get(),key.get(),minute.get(),second.get()))
        save.pack(side="left")
        ttk.Button(line,text="Hủy",command=line.destroy).pack(side="left")
        return {"frame":line,"enabled":enabled,"key":key,
                "minutes":minute,"seconds":second,"save":save}

    def _append(self,enabled,key,minute,second):
        if self._closed or self._blocked or self.snapshot is None:
            return False
        try:
            number,new=self.store.append(
                expected_bytes=self.snapshot.file_bytes,enabled=enabled,
                key=key,minutes=minute,seconds=second)
            record=next(r for r in new.rows if r.number==number)
            self.session_owned[number]=record.raw
            self.snapshot=new
        except Exception as exc:
            self.error=type(exc).__name__
            self.status.configure(text="Không lưu: lịch buff không hợp lệ hoặc file đã đổi")
            return False
        self._render()
        if callable(self.on_saved):self.on_saved()
        return True

    def edit_owned(self, number: int):
        """Show actual I05 editable variables for an in-session-owned row only."""
        if (self._closed or self._blocked or self.snapshot is None
                or number not in self.session_owned):
            return None
        rec = next((r for r in self.snapshot.rows
                    if r.number == number and
                    self.session_owned.get(number) == r.raw), None)
        if rec is None or not rec.key or number not in self.row_widgets:
            return None
        row = self.row_widgets[number]
        for child in row.winfo_children():
            child.destroy()
        enabled = tk.BooleanVar(master=self, value=rec.enabled)
        key = tk.StringVar(master=self, value=rec.key)
        minute = tk.StringVar(master=self, value=rec.minutes)
        second = tk.StringVar(master=self, value=rec.seconds)
        ttk.Checkbutton(row, variable=enabled, width=5).pack(side="left")
        ttk.Combobox(row, textvariable=key, values=BUFF_KEYS,
                     width=9, state="readonly").pack(side="left")
        def digits(candidate):
            return candidate == "" or (
                candidate.isascii() and candidate.isdecimal())
        vcmd = (self.register(digits), "%P")
        ttk.Entry(row, textvariable=minute, width=7, validate="key",
                  validatecommand=vcmd).pack(side="left")
        ttk.Entry(row, textvariable=second, width=7, validate="key",
                  validatecommand=vcmd).pack(side="left")
        save = ttk.Button(row, text="Lưu", command=lambda:
            self.update_owned(number, enabled.get(), key.get(),
                              minute.get(), second.get()))
        save.pack(side="left")
        ttk.Button(row, text="Hủy", command=self._render).pack(side="left")
        # Return the actual Tk variables/widgets for deterministic test.
        return {"frame":row, "enabled":enabled, "key":key,
                "minutes":minute, "seconds":second, "save":save}

    def update_owned(self, number: int, enabled: bool, key: str,
                     minutes: str, seconds: str) -> bool:
        if (self._closed or self._blocked or self.snapshot is None
                or number not in self.session_owned):
            return False
        try:
            new = self.store.update_session_row(
                number, expected_bytes=self.snapshot.file_bytes,
                expected_raw=self.session_owned[number],
                enabled=enabled, key=key, minutes=minutes, seconds=seconds)
            row = next(r for r in new.rows if r.number == number)
            self.snapshot = new
            # The same session still owns this exact row, now at its new
            # value. No permission is ever assigned to other legacy rows.
            self.session_owned[number] = row.raw
        except Exception as exc:
            self.error = type(exc).__name__
            self.status.configure(
                text="Không sửa: lịch buff đã đổi hoặc không hợp lệ")
            return False
        self.error = None
        self._render()
        if callable(self.on_saved):
            self.on_saved()
        return True

    def delete_owned(self,number:int):
        if (self._closed or self.snapshot is None
                or number not in self.session_owned):
            return False
        try:
            new=self.store.delete_session_row(
                number,expected_bytes=self.snapshot.file_bytes,
                expected_raw=self.session_owned[number])
            self.snapshot=new
            del self.session_owned[number]
        except Exception as exc:
            self.error=type(exc).__name__
            self.status.configure(text="Không xóa: lịch buff đã đổi hoặc không thuộc phiên này")
            return False
        self._render()
        if callable(self.on_saved):self.on_saved()
        return True

    def _on_destroy(self,event):
        if event.widget is self:self._closed=True
