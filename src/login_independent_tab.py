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
        self.launch_controller = IndependentGameLaunchController()
        self.btn_open = tk.Button(
            self.container, text="Mở game",
            background="#388e3c", foreground="white",
            font=("Segoe UI", 9, "bold"),
            command=self._request_open_game)
        # F01 original second button x≈157..232, y24..48 relative tab.
        self.btn_open.place(x=157, y=24, width=75, height=24)
        self.lbl_launch_status = tk.Label(
            self.container, text="",
            anchor="w", font=("Segoe UI", 8),
            foreground="#444444")
        self.lbl_launch_status.place(x=238, y=24, width=190, height=24)
        self._refresh_launch_button()
        self._show_launch_status("Chưa mở game; thao tác cần bấm tay")

    def _show_launch_status(self, message: str):
        if self._launch_closed or self._closed:
            return
        self.lbl_launch_status.configure(text=message)

    def _refresh_launch_button(self):
        if self._launch_closed or self._closed:
            return
        exe = self.get_exe_path()
        ready = exe is not None and not self.launch_controller.busy
        self.btn_open.configure(state="normal" if ready else "disabled")

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
            200, self._drain_launch_results)

    def _drain_launch_results(self):
        self._launch_poll_token = None
        if self._launch_closed or self._closed:
            return
        for outcome in self.launch_controller.drain():
            self._show_result(outcome)
        self._refresh_launch_button()
        if self.launch_controller.busy:
            self._schedule_launch_poll()

    def _show_result(self, result: IndependentLaunchResult):
        if result.code == "WINDOW_VERIFIED":
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
