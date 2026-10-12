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
from login_original_reader_probe_worker import OriginalReaderWorker
from start_polling import StartWindowProducer, WindowSnapshot
from tlm_existing_game_reader import ExistingGameOriginalReader
from tlm_existing_game_reader_worker import ExistingOriginalReaderWorker
from login_frozen_client_fingerprint import (
    FrozenClientFingerprintWorker,
    FrozenClientMatch,
)


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
    "PID_WINDOW_NOT_VERIFIED_AS_GAME": (
        "Có cửa sổ thuộc PID nhưng không xác minh được đó là game thật."),
    "WORKER_START_FAILED": "Không khởi động được tác vụ mở game.",
    "HWND_CHECK_FAILED": "Không xác minh được cửa sổ game.",
}


class TLMIndependentLoginTab(TLMLoginPathTab):
    """Independent runnable F04/F05 normal launch, not credential automation."""

    def __init__(
        self, parent, *, settings_file: str | Path,
        start_producer: StartWindowProducer | None = None,
    ):
        super().__init__(parent, settings_file=settings_file)
        self._launch_closed = False
        self._launch_poll_token = None
        self._launch_status_full = ""
        self._owned_selection_map = {}
        self._selected_game_pid = None
        self._fingerprint_status = "Chưa đối chiếu client DATA-2222."
        self._fingerprint_started_exe = None
        self._client_fingerprint = FrozenClientFingerprintWorker()
        self.launch_controller = IndependentGameLaunchController()
        self._original_reader = OriginalReaderWorker(
            self.launch_controller.inspect_original_reader)
        self._original_reader_exe = None
        self._original_reader_pid = None
        self._original_reader_status = (
            "Chưa kiểm tra bộ đọc TLM gốc trên tiến trình game.")
        self._start_producer = start_producer
        self._existing_selected_game_exe = self.get_exe_path()
        self._existing_reader = (
            ExistingGameOriginalReader(
                start_producer,
                # Worker only reads immutable Python Path set on Tk thread.
                # Never access a Tk widget or disk settings in this callback.
                selected_game_exe=lambda: self._existing_selected_game_exe)
            if isinstance(start_producer, StartWindowProducer) else None)
        self._existing_probe = (
            ExistingOriginalReaderWorker(self._existing_reader.inspect)
            if self._existing_reader is not None else None)
        self._existing_probe_status = (
            "Chưa kiểm tra game đang mở sẵn bằng memory_reader TLM.")
        self._existing_probe_target = None
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
        menu.add_command(
            label="Đối chiếu bản client DATA-2222 (SHA-256)",
            state=("disabled" if self.get_exe_path() is None
                   or self._client_fingerprint.busy else "normal"),
            command=self._request_client_fingerprint)
        menu.add_command(
            label="Kiểm tra memory_reader TLM gốc (chỉ đọc)",
            state=("normal" if self._selected_game_pid is not None
                   and self.get_exe_path() is not None
                   and not self._original_reader.busy
                   and not self.launch_controller.busy
                   else "disabled"),
            command=self._request_original_reader)
        if self._existing_probe is not None:
            sub = tk.Menu(menu, tearoff=0)
            observed = self._start_producer.read_snapshot()
            existing = (
                observed.windows if type(observed) is WindowSnapshot
                and observed.valid and self._start_producer.active else ())
            if not existing or self.get_exe_path() is None:
                sub.add_command(
                    label="Chưa có cửa sổ game/đường dẫn hợp lệ",
                    state="disabled")
            elif self._existing_probe.busy:
                sub.add_command(
                    label="Đang kiểm tra một cửa sổ...", state="disabled")
            else:
                # Popup presentation bound, NOT a limit on game accounts.
                for current in existing[:30]:
                    sub.add_command(
                        label=f"PID {current.pid} | HWND {current.hwnd}",
                        command=lambda w=current: (
                            self._request_existing_game_probe(w)))
                if len(existing) > 30:
                    sub.add_command(
                        label=f"Còn {len(existing)-30} cửa sổ; xem tab Start",
                        state="disabled")
            menu.add_cascade(
                label="Kiểm tra game đang chạy sẵn (chỉ đọc)",
                menu=sub)
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
            "Trạng thái Mở game",
            self._launch_status_full + "\n\nKiểm tra client: "
            + self._fingerprint_status
            + "\n\nĐọc bộ nhớ TLM gốc: "
            + self._original_reader_status
            + "\n\nGame mở sẵn: " + self._existing_probe_status,
            parent=self.container.winfo_toplevel())
        return True

    def _request_existing_game_probe(self, window) -> bool:
        if (self._launch_closed or self._closed
                or self._existing_probe is None):
            return False
        exe = self.get_exe_path()
        if exe is None:
            self._existing_probe_status = "Chưa chọn file game thực."
            return False
        self._existing_selected_game_exe = exe
        if not self._existing_probe.request(window):
            return False
        self._existing_probe_target = (window.hwnd, window.pid, str(exe))
        self._existing_probe_status = (
            f"Đang kiểm tra PID {window.pid}, HWND {window.hwnd} "
            "qua cache Start + native TLM Reader...")
        self._schedule_launch_poll()
        return True

    def _accept_existing_game_probe(self, result):
        if self._launch_closed or self._closed:
            return
        exe = self.get_exe_path()
        actual = (
            result.hwnd, result.pid, str(exe) if exe is not None else None)
        if self._existing_probe_target != actual:
            self._existing_probe_status = (
                "Không nhận kết quả cũ: PID/HWND/đường dẫn game đã đổi.")
            return
        self._existing_probe_status = (
            f"PID {result.pid} / HWND {result.hwnd}: {result.code}. "
            "Chưa chứng minh đang đăng nhập; không gửi game action.")
        self._show_launch_status(
            "Game đang chạy sẵn: " + result.code
            + ". Xem trạng thái đầy đủ.")

    def _request_original_reader(self) -> bool:
        """Explicit original TLM Reader pointer-only probe; NO game actions."""
        if (self._launch_closed or self._closed
                or self._selected_game_pid is None
                or self.launch_controller.busy):
            return False
        exe = self.get_exe_path()
        if exe is None:
            self._original_reader_status = "Chưa có file game được chọn."
            return False
        pid = self._selected_game_pid
        if pid not in {w.pid for w in self.launch_controller.list_owned_windows()}:
            self._original_reader_status = "PID không còn thuộc game do tool mở."
            return False
        if not self._original_reader.request(pid, exe):
            return False
        self._original_reader_pid = pid
        self._original_reader_exe = str(exe)
        self._original_reader_status = (
            f"Đang đọc CHỈ ĐỌC PID {pid}: mô-đun, con trỏ RoleData, "
            "điểm neo SessionData. Chưa đọc RoleName/HP.")
        self._schedule_launch_poll()
        return True

    def _accept_original_reader(self, result):
        if self._launch_closed or self._closed:
            return
        exe = self.get_exe_path()
        if (exe is None or str(exe) != self._original_reader_exe
                or result.pid != self._original_reader_pid):
            self._original_reader_status = (
                "Đã thay đổi file/PID game; loại bỏ chẩn đoán cũ.")
            return
        if result.pid not in {
                row.pid for row in self.launch_controller.list_owned_windows()}:
            self._original_reader_status = (
                "Tiến trình đã thoát hoặc phiên HWND không hợp lệ; "
                "không chấp nhận dữ liệu cũ.")
            return
        self._original_reader_status = (
            f"PID {result.pid}: {result.status}. "
            "Đây CHỈ là trạng thái bộ đọc gốc; "
            "không xác minh được tên nhân vật, HP hoặc đăng nhập.")
        self._show_launch_status(
            f"memory_reader PID {result.pid}: {result.status}. "
            "Xem trạng thái đầy đủ trong menu.")

    def _request_client_fingerprint(self) -> bool:
        """Read-only frozen build check; NEVER authorizes memory/game input."""
        if self._launch_closed or self._closed:
            return False
        selected = self.get_exe_path()
        if selected is None:
            self._fingerprint_status = "Chưa có file game để đối chiếu."
            return False
        if not self._client_fingerprint.request(selected):
            return False
        self._fingerprint_started_exe = str(selected)
        self._fingerprint_status = "Đang tính SHA-256 DLL + metadata..."
        self._schedule_launch_poll()
        return True

    def _accept_fingerprint(self, outcome: FrozenClientMatch):
        if self._launch_closed or self._closed:
            return
        # A user may change Settings.game_dir while a large DLL is hashed;
        # its result MUST NOT authorize or label the newly selected folder.
        selected = self.get_exe_path()
        if selected is None or str(selected) != self._fingerprint_started_exe:
            self._fingerprint_status = (
                "Thư mục game đã thay đổi; kết quả kiểm tra cũ bị loại bỏ.")
            return
        if outcome.known_static_files:
            self._fingerprint_status = (
                "Khớp 2 file SHA-256 bản DATA-2222. "
                "CHƯA chứng minh game đang chạy tương thích/đọc RoleName/HP.")
        elif outcome.code == "INSTALLED_CLIENT_DIFFERS_FROM_FROZEN_SNAPSHOT":
            self._fingerprint_status = (
                "Client không khớp bản DATA-2222: GameAssembly="
                + ("khớp" if outcome.gameassembly_match else "khác")
                + ", metadata="
                + ("khớp" if outcome.metadata_match else "khác")
                + ". Không sử dụng địa chỉ/ABI đoán từ snapshot cũ.")
        else:
            self._fingerprint_status = (
                f"Không đối chiếu được client: {outcome.code}. "
                "Chưa có quyền đọc dữ liệu nhân vật thật.")

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
        before = self.get_exe_path()
        selected = super()._select_game_directory()
        if selected and before != self.get_exe_path():
            self._client_fingerprint.invalidate()
            self._original_reader.invalidate()
            if self._existing_probe is not None:
                self._existing_probe.invalidate()
                self._existing_selected_game_exe = self.get_exe_path()
                self._existing_probe_status = (
                    "Đã thay đổi thư mục game; cần kiểm tra lại.")
            self._original_reader_status = (
                "Client mới chưa kiểm tra memory_reader TLM gốc.")
            self._fingerprint_status = "Client mới chưa đối chiếu SHA-256."
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
        # F05 native resize ticks once per second. Poll Tk status at
        # 1s once all launch workers finish; 350ms only while waiting
        # for a new PID/HWND handoff. Avoid permanent 350ms GUI churn.
        delay_ms = 350 if self.launch_controller.busy else 1000
        self._launch_poll_token = self.container.after(
            delay_ms, self._drain_launch_results)

    def _drain_launch_results(self):
        self._launch_poll_token = None
        if self._launch_closed or self._closed:
            return
        for outcome in self.launch_controller.drain():
            self._show_result(outcome)
        for fingerprint in self._client_fingerprint.drain():
            self._accept_fingerprint(fingerprint)
        for checked in self._original_reader.drain():
            self._accept_original_reader(checked)
        if self._existing_probe is not None:
            for result in self._existing_probe.drain():
                self._accept_existing_game_probe(result)
        for resize_event in self.launch_controller.drain_size_events():
            self._show_size_event(resize_event.code, resize_event.pid,
                                  resize_event.hwnd)
        self._refresh_launch_button()
        # A Login-owned F05 size worker continues each second after the
        # launch worker's PID/HWND handoff has completed.
        if (self.launch_controller.busy
                or self._client_fingerprint.busy
                or self._original_reader.busy
                or (self._existing_probe is not None
                    and self._existing_probe.busy)
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
        if result.pid is not None and result.code in (
                "STARTED_NO_WINDOW_YET", "PID_WINDOW_NOT_VERIFIED_AS_GAME"):
            self._show_launch_status(
                f"PID {result.pid} đã mở; chưa xác minh được cửa sổ game.")
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
        if self._existing_probe is not None:
            self._existing_probe.shutdown()
        self._original_reader.shutdown()
        self._client_fingerprint.shutdown()
        self.launch_controller.shutdown()
        super().shutdown()
