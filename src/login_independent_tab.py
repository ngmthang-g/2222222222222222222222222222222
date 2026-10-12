"""S188 independent Login Mở game: *real* Windows normal process launch.

This subclass changes ONLY the owner-independent Login builder; original
source-backed TLMLoginPathTab and historical signed-Info/diagnostic tests
remain untouched. F01/F04 exact button placement and F05 PID/HWND handoff
are grounded in the frozen client evidence. F05 original suspended DLL
injection and original login/proxy aren't replicated or advertised.

A game process is never treated as a logged-in character. Nothing happens
automatically; the user must click the actual button.
"""
from __future__ import annotations

from pathlib import Path
import tkinter as tk

from login_independent_game_launcher import (
    IndependentGameLaunchController, IndependentLaunchResult,
)
from login_tab import TLMLoginPathTab


RESULT_TEXT = {
    "WINDOWS_ONLY": "Chỉ hỗ trợ mở game trên Windows.",
    "INVALID_GAME_OR_ENV": "Đường dẫn game hoặc môi trường Windows không an toàn.",
    "PROCESS_SNAPSHOT_UNAVAILABLE": "Chưa xác minh được số tiến trình game; không mở.",
    "CANCELLED_BEFORE_START": "Đã hủy trước khi mở game.",
    "OS_PROCESS_CREATE_FAILED": "Windows không khởi động được file game.",
    "INVALID_CREATED_PID": "Không xác minh được PID vừa tạo.",
    "PROCESS_EXITED_BEFORE_WINDOW": "Game đã thoát trước khi có cửa sổ.",
    "CANCELLED_AFTER_START": "Tool dừng theo dõi; tiến trình game không bị đóng.",
    "STARTED_NO_WINDOW_YET": "Đã tạo PID nhưng chưa xác minh được cửa sổ game.",
    "WORKER_START_FAILED": "Không khởi động được tác vụ mở game.",
    "HWND_CHECK_FAILED": "Không xác minh được cửa sổ game.",
}


class TLMIndependentLoginTab(TLMLoginPathTab):
    """Independent runnable F04/F05 normal launch, not credential automation."""

    def __init__(self, parent, *, settings_file: str | Path):
        super().__init__(parent, settings_file=settings_file)
        self._launch_closed = False
        self._launch_poll_token = None
        self._launch_status_full = ""
        self._owned_selection_map = {}
        self._selected_game_pid = None
        self.launch_controller = IndependentGameLaunchController()
        self.btn_open = tk.Button(
            self.container, text="Mở game",
            background="#388e3c", foreground="white",
            font=("Segoe UI", 9, "bold"),
            command=self._request_open_game)
        # F01 original second button x≈157..232, y24..48 relative tab.
        self.btn_open.place(x=157, y=24, width=75, height=24)
        # Original F01 leaves no dedicated "switch to opened game" button.
        # Keep native F01 "Mở game" geometry; this additional independent
        # action is explicitly C03 native HWND foreground, NOT game login.
        self.btn_activate = tk.Button(
            self.container, text="Đến game",
            background="#616161", foreground="white",
            font=("Segoe UI", 8),
            state="disabled", command=self._activate_game)
        self.btn_activate.place(x=340, y=24, width=88, height=24)
        self.lbl_launch_status = tk.Label(
            self.container, text="",
            anchor="w", font=("Segoe UI", 8),
            cursor="hand2", foreground="#444444")
        self.lbl_launch_status.place(x=238, y=24, width=96, height=24)
        # S191: click status to choose from real own-launched PID/HWNDs.
        # Keep original F04 path label at y54..72 completely unobstructed.
        # Popup menu rows are NOT RoleName or authenticated game accounts.
        self.lbl_launch_status.bind(
            "<Button-1>", self._show_owned_games_menu, add="+")
        self._refresh_launch_button()
        self._show_launch_status("Chưa mở game; thao tác cần bấm tay")

    def _show_launch_status(self, message: str):
        if self._launch_closed or self._closed:
            return
        self._launch_status_full = message
        short = message if len(message) <= 19 else message[:17] + "…"
        self.lbl_launch_status.configure(text=short)

    def _refresh_launch_button(self):
        if self._launch_closed or self._closed:
            return
        exe = self.get_exe_path()
        ready = exe is not None and not self.launch_controller.busy
        self.btn_open.configure(state="normal" if ready else "disabled")
        self._refresh_owned_games()
        self.btn_activate.configure(
            state=("normal" if self._selected_game_pid is not None
                   and not self.launch_controller.busy else "disabled"))

    def _refresh_owned_games(self):
        """Track real own-created process HWNDs without rewriting login UI."""
        rows = self.launch_controller.list_owned_windows()
        options = {
            f"PID {row.pid} | HWND {row.hwnd}": row.pid for row in rows
        }
        chosen = self._selected_game_pid
        if chosen not in options.values():
            chosen = rows[-1].pid if rows else None
        self._selected_game_pid = chosen
        self._owned_selection_map = options

    def _choose_owned_pid(self, pid: int):
        if self._launch_closed or self._closed or pid not in self._owned_selection_map.values():
            return
        self._selected_game_pid = pid
        self._show_launch_status(
            f"Đã chọn PID {pid} (cửa sổ đã được nhận diện lúc mở); "
            "bấm Đến game để kiểm tra HWND thật trước khi chuyển cửa sổ.")
        self._refresh_launch_button()

    def _show_owned_games_menu(self, event=None):
        if self._launch_closed or self._closed:
            return
        self._refresh_owned_games()
        menu = tk.Menu(self.container, tearoff=0)
        menu.add_command(
            label="Xem trạng thái đầy đủ...",
            command=self._show_full_launch_status)
        if self._owned_selection_map:
            menu.add_separator()
            for label, pid in self._owned_selection_map.items():
                selected = "✓ " if pid == self._selected_game_pid else "  "
                menu.add_command(
                    label=selected + label,
                    command=lambda n=pid: self._choose_owned_pid(n))
        else:
            menu.add_separator()
            menu.add_command(
                label="Chưa có PID/HWND do tool mở", state="disabled")
        try:
            x = event.x_root if event is not None else self.lbl_launch_status.winfo_rootx()
            y = event.y_root if event is not None else self.lbl_launch_status.winfo_rooty()
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    def _show_full_launch_status(self, _event=None):
        """User can inspect the full diagnostic without exposing credentials."""
        if self._launch_closed or self._closed:
            return False
        from tkinter import messagebox
        messagebox.showinfo(
            "Trạng thái Mở game", self._launch_status_full,
            parent=self.container.winfo_toplevel())
        return True

    def _activate_game(self) -> bool:
        """S189 click: C03 foreground only for same live PID-owned HWND."""
        if (self._launch_closed or self._closed
                or self._selected_game_pid is None
                or self.launch_controller.busy):
            return False
        result = self.launch_controller.activate_window(
            self._selected_game_pid)
        if result.code == "OS_FOREGROUND_ACCEPTED_NOT_LOGIN":
            self._show_launch_status(
                f"Đã yêu cầu hiện PID {result.pid}/HWND {result.hwnd}; "
                "chưa xác minh đã đăng nhập game.")
        elif result.code == "OS_FOREGROUND_REFUSED":
            self._show_launch_status(
                "Windows không cho phép chuyển cửa sổ; không gửi phím chuột.")
        elif result.code in ("LAUNCHED_PROCESS_EXITED",
                             "WINDOW_NOT_CURRENT_GAME",
                             "WINDOW_CHANGED_AFTER_ACTIVATE"):
            self._show_launch_status(
                "Cửa sổ game không còn đúng PID/HWND; đã hủy yêu cầu.")
        else:
            self._show_launch_status(
                "Không thể xác minh cửa sổ game để kích hoạt.")
        self._refresh_launch_button()
        return result.code == "OS_FOREGROUND_ACCEPTED_NOT_LOGIN"

    def _select_game_directory(self) -> bool:
        selected = super()._select_game_directory()
        if hasattr(self, "launch_controller"):
            self._refresh_launch_button()
        return selected

    def _request_open_game(self) -> bool:
        if self._launch_closed or self._closed:
            return False
        exe = self.get_exe_path()
        if exe is None:
            self._show_launch_status("Chưa chọn file game có thật.")
            self._refresh_launch_button()
            return False
        started = self.launch_controller.start(exe)
        if started:
            self._show_launch_status("Đang mở tiến trình game; chờ PID/HWND...")
        self._refresh_launch_button()
        self._schedule_launch_poll()
        return started

    def _schedule_launch_poll(self):
        if (self._launch_closed or self._closed
                or self._launch_poll_token is not None):
            return
        self._launch_poll_token = self.container.after(
            350, self._drain_launch_results)

    def _drain_launch_results(self):
        self._launch_poll_token = None
        if self._launch_closed or self._closed:
            return
        for outcome in self.launch_controller.drain():
            self._show_result(outcome)
        for resize_event in self.launch_controller.drain_size_events():
            self._show_size_event(resize_event.code, resize_event.pid,
                                  resize_event.hwnd)
        self._refresh_launch_button()
        # A Login-owned F05 size worker continues each second after the
        # launch worker's PID/HWND handoff has completed.
        if (self.launch_controller.busy
                or self.launch_controller.list_owned_windows()):
            self._schedule_launch_poll()

    def _show_size_event(self, code: str, pid: int, hwnd: int) -> None:
        if code == "RESIZED_TO_1366X768":
            self._show_launch_status(
                f"Đã chuẩn hóa PID {pid} / HWND {hwnd} về 1366×768; chưa login.")
        elif code == "ALREADY_1366X768":
            self._show_launch_status(
                f"Cửa sổ PID {pid} đúng 1366×768; chưa login.")
        elif code.startswith("RESIZE_"):
            # Never misreport a native SetWindowPos attempt as success.
            self._show_launch_status(
                f"Không chuẩn hóa được HWND {hwnd}: {code}. "
                "Không thay đổi nhân vật/game login.")

    def _show_result(self, result: IndependentLaunchResult):
        if result.code == "WINDOW_VERIFIED":
            self._selected_game_pid = result.pid
            self._show_launch_status(
                f"Đã mở PID {result.pid}, HWND {result.hwnd}; chưa login.")
            return
        if result.pid is not None and result.code == "STARTED_NO_WINDOW_YET":
            self._show_launch_status(
                f"PID {result.pid} đã mở; chưa xác minh HWND.")
            return
        reason = RESULT_TEXT.get(result.code, "Chưa xác minh trạng thái mở game.")
        self._show_launch_status(
            f"PID {result.pid}: {reason}" if result.pid else reason)

    def _start_refresh(self):
        """Re-evaluate only F04 game-dir presence; no automatic game spawn."""
        if self._launch_closed:
            return False
        self._refresh_launch_button()
        return True

    def _stop_refresh(self):
        # The worker owns an explicit click; switching tabs must not kill
        # an actual game or report fake login completion.
        return None

    def shutdown(self) -> None:
        if self._launch_closed:
            return
        self._launch_closed = True
        if self._launch_poll_token is not None:
            token, self._launch_poll_token = self._launch_poll_token, None
            try:
                self.container.after_cancel(token)
            except tk.TclError:
                pass
        self.launch_controller.shutdown()
        super().shutdown()
