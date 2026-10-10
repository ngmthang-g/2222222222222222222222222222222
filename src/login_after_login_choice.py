"""S112: F01/F10 saved post-login RADIO CHOICE, never an action dispatcher.

The original F01 has Chờ/Party/Train/Train LSV/Dồn vàng radios with exact
values wait/party/train/train_lsv/don and [Settings].after_login persistence.
This module only handles config selection; it never sends a game command or
starts a destination tab. The real F05/F06/F10 controller is still absent.
"""
from __future__ import annotations

from datetime import datetime
import os
from pathlib import Path
import re
import shutil
import tempfile
from typing import Callable

from settings_store import _settings_lock, read_settings, settings_path

AFTER_CHOICES = (
    ("Chờ", "wait"),
    ("Party", "party"),
    ("Train", "train"),
    ("Train LSV", "train_lsv"),
    ("Dồn vàng", "don"),
)
ALLOWED_VALUES = frozenset(value for _, value in AFTER_CHOICES)
KEY = "after_login"
SECTION = re.compile(r"^\[([^\]\r\n]+)\][ \t]*$")
ENTRY = re.compile(r"^([A-Za-z_][A-Za-z_0-9]*)([ \t]*[=:][ \t]*)([^\r\n]*)$")
MAX_INI_BYTES = 2 * 1024 * 1024


class AfterLoginChoiceError(ValueError):
    """Sanitized error: never expose INI contents or credentials."""


def read_after_login_choice(path: str | Path | None = None) -> tuple[str, str]:
    """F10 original default 'wait'; ambiguous/invalid raw never promoted."""
    try:
        cfg = read_settings(path)
        raw = cfg.get("Settings", KEY, fallback="wait", raw=True)
    except (ValueError, OSError, RuntimeError, Exception):
        return "", "BLOCKED_CONFIG"
    if raw not in ALLOWED_VALUES:
        return "", "UNKNOWN_SAVED_DESTINATION"
    return raw, "READ_ONLY_VERIFIED_CHOICE"


def save_after_login_choice(choice: str, path: str | Path | None = None) -> str:
    """Replace exactly [Settings].after_login, without rewriting accounts/INI.

    Fails closed on duplicate keys or sections, BOM/unknown encoding, unsafe
    bodies. Uses E05 shared lock, daily backup and atomic replace. In no case
    invokes the selected Party/Train/Dồn destination.
    """
    if type(choice) is not str or choice not in ALLOWED_VALUES:
        raise AfterLoginChoiceError("INVALID_AFTER_LOGIN_CHOICE")
    target = Path(path) if path is not None else settings_path()
    with _settings_lock:
        try:
            exists = target.is_file()
            raw = target.read_bytes() if exists else b""
            if len(raw) > MAX_INI_BYTES or b"\x00" in raw:
                raise AfterLoginChoiceError("UNSAFE_AFTER_LOGIN_INI")
            text = raw.decode("utf-8")
        except (UnicodeError, OSError):
            raise AfterLoginChoiceError("UNREADABLE_AFTER_LOGIN_INI") from None
        if text.startswith("\ufeff"):
            raise AfterLoginChoiceError("UNSUPPORTED_AFTER_LOGIN_BOM")
        newline = "\r\n" if "\r\n" in text else "\n"
        lines = text.splitlines(keepends=True)
        sections = [
            (i, m.group(1).strip().casefold())
            for i, line in enumerate(lines)
            if (m := SECTION.fullmatch(line.rstrip("\r\n")))
        ]
        matches = [i for i, name in sections if name == "settings"]
        if len(matches) > 1:
            raise AfterLoginChoiceError("DUPLICATE_SETTINGS_SECTION")
        if not matches and text.strip():
            raise AfterLoginChoiceError("MISSING_SETTINGS_SECTION")
        if not matches:
            new_text = "[Settings]" + newline + KEY + " = " + choice + newline
        else:
            start = matches[0]
            end = next((i for i, _ in sections if i > start), len(lines))
            candidates = []
            for i in range(start + 1, end):
                body = lines[i].rstrip("\r\n")
                if body[:1].isspace() and body.lstrip(" \t").casefold().startswith(KEY):
                    raise AfterLoginChoiceError("AMBIGUOUS_INDENTED_AFTER_LOGIN")
                m = ENTRY.fullmatch(body)
                if m and m.group(1).casefold() == KEY:
                    candidates.append((i, m))
            if len(candidates) > 1:
                raise AfterLoginChoiceError("DUPLICATE_AFTER_LOGIN_KEY")
            if candidates:
                i, m = candidates[0]
                if m.group(3) not in ALLOWED_VALUES:
                    raise AfterLoginChoiceError("UNKNOWN_SAVED_DESTINATION")
                terminator = "\r\n" if lines[i].endswith("\r\n") else ("\n" if lines[i].endswith("\n") else "")
                lines[i] = m.group(1) + m.group(2) + choice + terminator
            else:
                if end and not lines[end - 1].endswith(("\r", "\n")):
                    lines[end - 1] += newline
                lines.insert(end, KEY + " = " + choice + newline)
            new_text = "".join(lines)
        data = new_text.encode("utf-8")
        if data == raw:
            return "UNCHANGED"
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            if exists:
                backup = target.with_name("settings." + datetime.now().strftime("%Y%m%d") + ".ini")
                if not backup.exists():
                    shutil.copy2(target, backup)
            fd, temp = tempfile.mkstemp(prefix="settings.", suffix=".tmp", dir=str(target.parent))
            try:
                with os.fdopen(fd, "wb") as f:
                    f.write(data)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(temp, target)
            finally:
                if os.path.exists(temp):
                    os.unlink(temp)
        except OSError:
            raise AfterLoginChoiceError("AFTER_LOGIN_SAVE_FAILED") from None
        return "UPDATED_AFTER_LOGIN_ONLY"


class TLMLoginAfterLoginChoice:
    """Actual F01 Tk radio selection, no hidden routing action."""

    def __init__(self, parent, *, settings_file: str | Path | None = None,
                 show_error: Callable[[str, str], object] | None = None):
        import tkinter as tk
        from tkinter import ttk

        self._closed = False
        self._path = settings_file
        self._show_error = show_error
        selected, status = read_after_login_choice(settings_file)
        self.last_status = status
        self._stored = selected
        self.selection_var = tk.StringVar(master=parent, value=selected)
        self.label = ttk.Label(parent, text="Sau khi login:")
        self.label.place(x=9, y=105, width=89, height=21)
        self.radios = []
        for (title, value), x, width in zip(
            AFTER_CHOICES, (94, 143, 194, 249, 323), (48, 50, 54, 73, 98)
        ):
            radio = ttk.Radiobutton(parent, text=title, value=value,
                                    variable=self.selection_var,
                                    command=self._change_selection)
            radio.place(x=x, y=105, width=width, height=21)
            if status != "READ_ONLY_VERIFIED_CHOICE":
                radio.configure(state="disabled")
            self.radios.append(radio)

    def _change_selection(self) -> bool:
        if self._closed:
            return False
        value = self.selection_var.get()
        try:
            result = save_after_login_choice(value, self._path)
        except (AfterLoginChoiceError, RuntimeError):
            self.selection_var.set(self._stored)
            self.last_status = "BLOCKED_AFTER_LOGIN_SAVE"
            if callable(self._show_error):
                self._show_error("Không thể lưu Sau khi login",
                                 "Cấu hình không hợp lệ hoặc không thể ghi an toàn.")
            return False
        self._stored = value
        self.last_status = result
        return True

    def shutdown(self) -> None:
        self._closed = True
