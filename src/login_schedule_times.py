"""S111: genuine F01 schedule clock selectors and byte-preserving F09 time edits.

Only schedule_close/schedule_open HH:MM are edited. Never interpret schedule_on,
arm a worker, start/close a game, touch accounts or modify Proxy. The 24 hours
and 60 minutes are evidenced by original F01 serialized range limits.
"""
from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import tempfile
from datetime import datetime
from typing import Callable

from login_schedule_clock import parse_hhmm
from login_schedule_settings import read_schedule_settings
from settings_store import _settings_lock, settings_path

TIME_KEYS = frozenset(("schedule_close", "schedule_open"))
MAX_INI_BYTES = 2 * 1024 * 1024
SECTION = re.compile(r"^\[([^\]\r\n]+)\][ \t]*$")
KEY = re.compile(r"^([A-Za-z_][A-Za-z_0-9]*)([ \t]*[=:][ \t]*)([^\r\n]*)$")


class ScheduleTimeWriteError(ValueError):
    """Sanitized error: do not emit user INI/account contents."""


def save_schedule_time(value: str, key: str, path: str | Path | None = None) -> str:
    """Atomically change exactly one F09 HH:MM key, keep other bytes untouched.

    Fails closed for duplicate [Settings]/target keys, non-UTF8, unknown
    target-key serialization, and ambiguous continuation. Existing files
    receive E05's dated backup before an actual change; no backup if unchanged.
    """
    if key not in TIME_KEYS or type(value) is not str:
        raise ScheduleTimeWriteError("INVALID_SCHEDULE_KEY_OR_TIME")
    try:
        parse_hhmm(value)
    except (ValueError, TypeError):
        raise ScheduleTimeWriteError("INVALID_SCHEDULE_HHMM") from None
    target = Path(path) if path is not None else settings_path()
    with _settings_lock:
        try:
            exists = target.is_file()
            raw = target.read_bytes() if exists else b""
            if len(raw) > MAX_INI_BYTES or b"\x00" in raw:
                raise ScheduleTimeWriteError("UNSAFE_SCHEDULE_INI")
            content = raw.decode("utf-8")
        except (UnicodeError, OSError) as exc:
            raise ScheduleTimeWriteError("UNREADABLE_SCHEDULE_INI") from None
        if content.startswith("\ufeff"):
            raise ScheduleTimeWriteError("UNSUPPORTED_INI_BOM")
        newline = "\r\n" if "\r\n" in content else "\n"
        lines = content.splitlines(keepends=True)
        section_starts = [
            (i, m.group(1).strip().casefold())
            for i, line in enumerate(lines)
            if (m := SECTION.fullmatch(line.rstrip("\r\n")))
        ]
        settings_indices = [i for i, name in section_starts if name == "settings"]
        if len(settings_indices) > 1:
            raise ScheduleTimeWriteError("DUPLICATE_SETTINGS_SECTION")
        if not settings_indices and content.strip():
            # Do not rewrite a nonempty unrecognized configuration.
            raise ScheduleTimeWriteError("MISSING_SETTINGS_SECTION")
        if not settings_indices:
            output = "[Settings]" + newline + key + " = " + value + newline
        else:
            start = settings_indices[0]
            end = next((i for i, _ in section_starts if i > start), len(lines))
            matches = []
            for i in range(start + 1, end):
                body = lines[i].rstrip("\r\n")
                # Any indented key could be a multiline account continuation.
                if body.lstrip(" \t").casefold().startswith(key.casefold()) and body[:1].isspace():
                    raise ScheduleTimeWriteError("AMBIGUOUS_INDENTED_TIME_KEY")
                m = KEY.fullmatch(body)
                if m and m.group(1).casefold() == key:
                    matches.append((i, m))
            if len(matches) > 1:
                raise ScheduleTimeWriteError("DUPLICATE_SCHEDULE_TIME_KEY")
            if matches:
                i, m = matches[0]
                try:
                    parse_hhmm(m.group(3))
                except (TypeError, ValueError):
                    raise ScheduleTimeWriteError("UNVERIFIED_STORED_TIME") from None
                terminator = "\r\n" if lines[i].endswith("\r\n") else ("\n" if lines[i].endswith("\n") else "")
                lines[i] = m.group(1) + m.group(2) + value + terminator
            else:
                # If an account continuation is immediately before the next
                # section, insertion remains a new unindented option.
                if end and not lines[end - 1].endswith(("\r", "\n")):
                    lines[end - 1] += newline
                lines.insert(end, key + " = " + value + newline)
            output = "".join(lines)
        new_bytes = output.encode("utf-8")
        if new_bytes == raw:
            return "UNCHANGED"
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            if exists:
                backup = target.with_name("settings." + datetime.now().strftime("%Y%m%d") + ".ini")
                if not backup.exists():
                    shutil.copy2(target, backup)
            fd, tmp = tempfile.mkstemp(prefix="settings.", suffix=".tmp", dir=str(target.parent))
            try:
                with os.fdopen(fd, "wb") as out:
                    out.write(new_bytes)
                    out.flush()
                    os.fsync(out.fileno())
                os.replace(tmp, target)
            finally:
                if os.path.exists(tmp):
                    os.unlink(tmp)
        except OSError:
            raise ScheduleTimeWriteError("SCHEDULE_TIME_WRITE_FAILED") from None
        return "UPDATED_ONLY_" + key.upper()


class TLMLoginScheduleTimes:
    """Real F01 time selectors; not the unavailable schedule toggle/worker."""

    def __init__(self, parent, *, settings_file: str | Path | None = None,
                 show_error: Callable[[str, str], object] | None = None):
        import tkinter as tk
        from tkinter import ttk

        self._closed = False
        self._path = settings_file
        self._show_error = show_error
        self.last_status = "DEFAULTS_ONLY"
        self.group = ttk.LabelFrame(parent, text="Cấu hình lịch trình")
        # Screenshot group y=147 relative to Login content origin near y=59.
        self.group.place(x=6, y=88, width=428, height=136)
        read = read_schedule_settings(settings_file)
        self.last_status = read.status
        close = read.close_hhmm if read.preview_available else "04:00"
        opened = read.open_hhmm if read.preview_available else "04:20"
        self._stored = {"schedule_close": close, "schedule_open": opened}
        self.vars: dict[str, tuple[tk.StringVar, tk.StringVar]] = {}
        self.combos: dict[str, tuple[object, object]] = {}
        for key, title, value, y in (
            ("schedule_close", "Hẹn giờ tắt game:", close, 35),
            ("schedule_open", "Hẹn giờ mở game:", opened, 72),
        ):
            tk.Label(self.group, text=title, font=("Segoe UI", 9),
                     anchor="w").place(x=9, y=y, width=136, height=22)
            hour, minute = value.split(":")
            hvar = tk.StringVar(master=self.group, value=hour)
            mvar = tk.StringVar(master=self.group, value=minute)
            hbox = ttk.Combobox(self.group, textvariable=hvar, state="readonly",
                                values=[f"{i:02d}" for i in range(24)], width=3)
            mbox = ttk.Combobox(self.group, textvariable=mvar, state="readonly",
                                values=[f"{i:02d}" for i in range(60)], width=3)
            hbox.place(x=148, y=y, width=49, height=23)
            mbox.place(x=209, y=y, width=49, height=23)
            self.vars[key] = (hvar, mvar)
            self.combos[key] = (hbox, mbox)
            for combo in (hbox, mbox):
                combo.bind("<<ComboboxSelected>>",
                           lambda _event, field=key: self._save_field(field), add="+")
            if not read.preview_available:
                hbox.configure(state="disabled")
                mbox.configure(state="disabled")

    def _save_field(self, key: str) -> bool:
        if self._closed or key not in TIME_KEYS:
            return False
        hour, minute = self.vars[key]
        value = hour.get() + ":" + minute.get()
        try:
            result = save_schedule_time(value, key, self._path)
        except (ScheduleTimeWriteError, RuntimeError):
            old_h, old_m = self._stored[key].split(":")
            hour.set(old_h)
            minute.set(old_m)
            self.last_status = "BLOCKED_TIME_SAVE"
            if callable(self._show_error):
                self._show_error("Không thể lưu giờ lịch trình",
                                 "Cấu hình không hợp lệ hoặc không thể ghi an toàn.")
            return False
        self._stored[key] = value
        self.last_status = result
        return True

    def shutdown(self) -> None:
        self._closed = True
