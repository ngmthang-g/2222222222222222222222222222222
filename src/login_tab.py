"""S25: genuine Login 'Cấu hình game' path-selection widget slice.

F01/B03 geometry and F04 directory picker/path status only. S25 deliberately
does NOT display a fake 'Mở game', captcha, Proxy or Login action; they require
real independently verified F05/F06 functionality in later checkpoints.
Production server/Info gate still blocks unverified tab creation.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable

from login_path import (
    EXE_NAME, EXAMPLE_PATH, INVALID_TITLE, PICKER_TITLE,
    GameDirectoryResult, GameDirectoryStore, resolve_game_dir,
)

GAME_GROUP_SIZE = (428, 65)
# Relative to Login tab content frame; screenshot tab begins at x~5,y~59.
# Place as siblings over LabelFrame to avoid ttk.LabelFrame's variable title inset.
CHOOSER_BOUNDS = (11, 24, 135, 24)
STATUS_BOUNDS = (18, 54, 406, 18)
# F01 screenshot outer game group x11,y69..133; frame top y~59, outer
# Login-tab geometry x6,y10 is a S25 anchor, not a full pixel parity claim.
GROUP_FRAME_BOUNDS = (6, 10, *GAME_GROUP_SIZE)


class TLMLoginPathTab:
    """Partial real Login tab, only the functioning directory selection slice."""

    def __init__(self, parent, *, settings_file: str | Path | None = None,
                 choose_directory: Callable[..., str] | None = None,
                 show_error: Callable[..., object] | None = None):
        import tkinter as tk
        from tkinter import filedialog, messagebox, ttk

        self.parent = parent
        self._closed = False
        self.store = GameDirectoryStore(settings_file)
        self._choose_directory = choose_directory or filedialog.askdirectory
        self._show_error = show_error or messagebox.showerror
        self.game_dir = GameDirectoryResult(None, "")
        self.container = ttk.Frame(parent)
        self.container.pack(fill="both", expand=True)
        self.group_game = ttk.LabelFrame(self.container, text="Cấu hình game")
        self.group_game.place(x=GROUP_FRAME_BOUNDS[0], y=GROUP_FRAME_BOUNDS[1],
                              width=GAME_GROUP_SIZE[0], height=GAME_GROUP_SIZE[1])
        self.btn_choose = tk.Button(
            self.container, text="Chọn thư mục game",
            background="RoyalBlue", foreground="white",
            font=("Segoe UI", 9, "bold"),
            command=self._select_game_directory,
        )
        self.btn_choose.place(x=CHOOSER_BOUNDS[0], y=CHOOSER_BOUNDS[1],
                              width=CHOOSER_BOUNDS[2], height=CHOOSER_BOUNDS[3])
        # F01 shows a second 'Mở game' button at x157..232. F05 game launch
        # is absent, so S25 reserves its area instead of adding a fake action.
        self.lbl_game_dir = tk.Label(self.container, anchor="w", font=("Segoe UI", 8),
                                      text="Đường dẫn game: (Chưa chọn)")
        # Original F04 initial label was hidden until _show_game_dir_status.
        self.lbl_game_dir.place_forget()
        self._load_config()
        # S37: F01 100 real selection/entry/captcha widgets, memory-only.
        # F02 persistent check boolean token and legacy 'Có' migration UNKNOWN:
        # NEVER load/rewrite Settings.accounts with guessed serialization.
        from login_account_rows import TLMAccountRows
        self.account_rows = TLMAccountRows(self.container)
        # S38 only reads legacy Settings.accounts. Never save/migrate it.
        from login_account_legacy import read_legacy_accounts
        legacy = read_legacy_accounts(settings_file)
        self.legacy_account_load_status = legacy.status
        if legacy.status == "READY":
            try:
                self.account_rows.hydrate_legacy_read_only(legacy.records)
            except (ValueError, RuntimeError):
                self.legacy_account_load_status = "BLOCKED_UI"
        self.account_rows.show_legacy_load_status(
            self.legacy_account_load_status)
        self.container.bind("<Destroy>", self._on_destroy, add="+")

    def _show_game_dir_status(self, text: str) -> None:
        if self._closed:
            return
        self.lbl_game_dir.configure(text=text)
        self.lbl_game_dir.place(
            x=STATUS_BOUNDS[0], y=STATUS_BOUNDS[1],
            width=STATUS_BOUNDS[2], height=STATUS_BOUNDS[3])

    def _load_config(self) -> None:
        try:
            value = self.store.load()
        except (OSError, ValueError, RuntimeError):
            # An unreadable config must not grant a selected game exe.
            self.game_dir = GameDirectoryResult(None, "Không thể đọc cấu hình")
            self._show_game_dir_status("Đường dẫn game: Không thể đọc cấu hình")
            return
        self.game_dir = value if value.executable else GameDirectoryResult(None, value.note)
        if self.game_dir.executable is not None:
            self._show_game_dir_status(
                "✅ Đã chọn game thành công: " + str(self.game_dir.directory))
        elif value.note:
            self._show_game_dir_status("Đường dẫn game: " + value.note)

    def _select_game_directory(self) -> bool:
        if self._closed:
            return False
        try:
            selected = self._choose_directory(title=PICKER_TITLE)
        except Exception as exc:
            self._show_game_dir_status("Đường dẫn game: Không thể mở hộp chọn thư mục")
            return False
        if not selected:
            # User canceled native picker: do not corrupt previous valid path.
            return False
        result = resolve_game_dir(selected)
        if result.executable is None:
            self._show_game_dir_status("Đường dẫn game: " + result.note)
            self._show_error(
                INVALID_TITLE,
                f"Thư mục đã chọn: {selected}\n"
                f"Cần có file: {EXE_NAME}\nVí dụ: {EXAMPLE_PATH}",
            )
            return False
        try:
            self.store.save(result)
        except (OSError, ValueError, RuntimeError):
            # Never claim a successful persistent selection if disk write failed.
            self._show_game_dir_status("Đường dẫn game: Không thể lưu cấu hình")
            self._show_error("Không thể lưu thư mục game",
                             "Không thể ghi game_dir vào settings.ini")
            return False
        self.game_dir = result
        suffix = (" (" + result.note + ")" if result.note else "")
        self._show_game_dir_status(
            "✅ Đã chọn game thành công: " + str(result.directory) + suffix)
        return True

    def get_exe_path(self) -> Path | None:
        return None if self._closed else self.store.get_exe_path(self.game_dir)

    def _on_destroy(self, event) -> None:
        if getattr(event, "widget", None) is self.container:
            self.shutdown()

    def shutdown(self) -> None:
        if self._closed:
            return
        self._closed = True
        self.account_rows.shutdown()
        self.game_dir = GameDirectoryResult(None, "")
