"""S206 independent Phó Bản/Dồn original pixel read-only diagnostics.

These are NOT new functional Shop/Bag tabs. Both original independent
configuration editors are preserved; the added small panel can request
ONE genuine source-backed Win32 screenshot comparison in the original
PhoBan/DonVang/Shop/Bag pixel catalog. No game click, item discard, team
command, login or automatic schedule execution is reachable here.

Tk only reads the real S09 Start HWND/PID cache and immutable completed
worker results. All SHA256, PrintWindow and pixel scanning runs off Tk.
"""
from __future__ import annotations

from tkinter import ttk
import tkinter as tk

from don_return_tab import TkDonReturnTab
from phoban_schedule_tab import TkPhoBanScheduleTab
from independent_original_roi_worker import IndependentOriginalRoiWorker
from start_polling import StartWindowProducer, WindowSnapshot
from tlm_original_pixel_catalog import (
    FROZEN_PIXEL_CATALOG, original_pixel_spec,
)

SOURCE_UI_REFRESH_MS = 2000
MAX_VISIBLE_GAME_WINDOWS = 30
GROUP_NAMES = {
    "phoBan": "Phó Bản", "trungAc": "Trừng Ác",
    "shop": "Shop", "tuido": "Túi đồ", "donVang": "Dồn Vàng",
    "common": "Chung",
}
PHOBAN_SECTIONS = ("phoBan", "trungAc", "tuido", "shop", "common")
DONVANG_SECTIONS = ("donVang", "shop", "tuido", "common")


class TkOriginalRoiDiagnosticPanel(ttk.LabelFrame):
    """On-demand proof display only; not a gameplay action controller."""

    def __init__(self, parent, *, worker: IndependentOriginalRoiWorker,
                 producer: StartWindowProducer, sections: tuple[str, ...]):
        if (not isinstance(worker, IndependentOriginalRoiWorker)
                or not isinstance(producer, StartWindowProducer)
                or not sections or
                any(group not in FROZEN_PIXEL_CATALOG for group in sections)):
            raise ValueError("REAL_ORIGINAL_PIXEL_DIAGNOSTIC_INPUT_REQUIRED")
        super().__init__(parent, text="Nhận diện pixel TLM gốc (chưa kiểm thử)")
        self.worker = worker
        self.producer = producer
        self.sections = sections
        self._closed = False
        self._active = False
        self._after = None
        self._own_ticket = None
        self._requested_window = None
        self._requested_key = None
        self._window_map = {}
        self._section_by_display = {
            GROUP_NAMES.get(section, section): section for section in sections}
        self.group_var = tk.StringVar(value=next(iter(self._section_by_display)))
        self.key_var = tk.StringVar()
        self.window_var = tk.StringVar()
        selectors = ttk.Frame(self)
        selectors.pack(fill="x", padx=5, pady=4)
        self.section_box = ttk.Combobox(
            selectors, textvariable=self.group_var, state="readonly",
            width=12, values=tuple(self._section_by_display))
        self.section_box.pack(side="left", padx=(0, 4))
        self.section_box.bind("<<ComboboxSelected>>", self._on_section_change)
        self.key_box = ttk.Combobox(
            selectors, textvariable=self.key_var, width=22, state="readonly")
        self.key_box.pack(side="left", padx=(0, 4))
        self.key_box.bind("<<ComboboxSelected>>", self._on_selection_change)
        self.window_box = ttk.Combobox(
            selectors, textvariable=self.window_var,
            width=23, state="readonly")
        self.window_box.pack(side="left", padx=(0, 4))
        self.window_box.bind("<<ComboboxSelected>>", self._on_selection_change)
        self.btn_probe = ttk.Button(
            selectors, text="Quét 1 lần (chỉ đọc)",
            command=self._request_probe)
        self.btn_probe.pack(side="left")
        self.status = ttk.Label(
            self, justify="left", wraplength=660,
            text="Chỉ so pixel gốc; không tự điều khiển game hoặc xác nhận online.")
        self.status.pack(fill="x", padx=5, pady=(0, 4))
        self._on_section_change()
        self.bind("<Destroy>", self._on_destroy, add="+")

    def _selected_section(self):
        return self._section_by_display.get(self.group_var.get())

    def _on_section_change(self, _event=None):
        section = self._selected_section()
        keys = tuple(FROZEN_PIXEL_CATALOG.get(section, {}))
        self.key_box.configure(values=keys)
        self.key_var.set(keys[0] if keys else "")
        self._on_selection_change()

    def _on_selection_change(self, _event=None):
        self._own_ticket = None
        self._requested_window = None
        self._requested_key = None
        if self._active and not self._closed:
            self._update_status()

    def _refresh_windows(self):
        snap = self.producer.read_snapshot()
        windows = (
            snap.windows if type(snap) is WindowSnapshot
            and snap.valid and self.producer.active else ())
        current = self.window_var.get()
        self._window_map = {
            f"PID {w.pid} | HWND {w.hwnd}": w
            for w in windows[:MAX_VISIBLE_GAME_WINDOWS]
        }
        self.window_box.configure(values=tuple(self._window_map))
        if current in self._window_map:
            self.window_var.set(current)
        elif self._window_map:
            self.window_var.set(next(iter(self._window_map)))
            self._own_ticket = None
        else:
            self.window_var.set("")
            self._own_ticket = None

    def _update_status(self):
        if self._closed:
            return
        section, key = self._selected_section(), self.key_var.get()
        spec = original_pixel_spec(section, key) if section else None
        if spec is None:
            self.status.configure(text="Chưa chọn mẫu pixel từ dữ liệu gốc.")
            self.btn_probe.configure(state="disabled")
            return
        if spec.reader_kind.startswith("UNSUPPORTED"):
            self.status.configure(text=(
                f"{section}.{key}: dữ liệu gốc không đủ để so ảnh: "
                f"{spec.reader_kind}. KHÔNG tự sửa màu/tolerance."))
            self.btn_probe.configure(state="disabled")
            return
        if not self._window_map:
            self.status.configure(
                text="Chưa có game thật trong bộ quét HWND/PID Start.")
            self.btn_probe.configure(state="disabled")
            return
        if self.worker.busy:
            self.status.configure(
                text="Worker đang đọc ảnh một cửa sổ. Không gửi thao tác game.")
            self.btn_probe.configure(state="disabled")
            return
        self.btn_probe.configure(state="normal")
        if self._own_ticket is None:
            self.status.configure(text=(
                f"{section}.{key}: {spec.reader_kind}. "
                "Chưa quét; kết quả không xác minh trạng thái game."))
            return
        data = self.worker.read_result(self._own_ticket)
        if data is None:
            self.status.configure(text=(
                "Chưa có kết quả hoặc kết quả đã hết hạn. "
                "Không được hiểu là pixel khớp."))
            return
        expected = self._requested_window
        if (expected is None or data.pid != expected.pid
                or data.hwnd != expected.hwnd
                or (data.section, data.key) != self._requested_key
                or (data.hwnd, data.pid) not in {
                    (w.hwnd, w.pid) for w in self._window_map.values()}):
            self.status.configure(
                text="Game/PID/HWND hoặc mẫu đã thay đổi; loại bỏ ảnh cũ.")
            self._own_ticket = None
            return
        located = (
            str(data.found_client_xy)
            if data.found_client_xy is not None else "không có vị trí")
        self.status.configure(text=(
            f"{data.section}.{data.key}, PID {data.pid}: {data.code}. "
            f"Đã quét {data.scanned_candidates} điểm; tọa độ ứng viên: "
            f"{located}. CHƯA XÁC MINH; không gửi click/game action."))

    def _request_probe(self):
        if self._closed or not self._active or self.worker.busy:
            return False
        window = self._window_map.get(self.window_var.get())
        section, key = self._selected_section(), self.key_var.get()
        spec = original_pixel_spec(section, key) if section else None
        if (window is None or spec is None
                or spec.reader_kind.startswith("UNSUPPORTED")):
            return False
        ticket = self.worker.request(window, section, key)
        if ticket is None:
            self.status.configure(
                text="Chưa bắt đầu: worker bận hoặc nguồn không hợp lệ.")
            return False
        self._own_ticket = ticket
        self._requested_window = window
        self._requested_key = (section, key)
        self._update_status()
        return True

    def _tick(self):
        self._after = None
        if self._closed or not self._active:
            return
        self._refresh_windows()
        self._update_status()
        self._after = self.after(SOURCE_UI_REFRESH_MS, self._tick)

    def start(self):
        if self._closed or self._active:
            return
        self._active = True
        self._tick()

    def stop(self):
        self._active = False
        if self._after is not None:
            token, self._after = self._after, None
            try:
                self.after_cancel(token)
            except tk.TclError:
                pass

    def shutdown(self):
        if self._closed:
            return
        self.stop()
        self._closed = True

    def _on_destroy(self, event):
        if event.widget is self:
            self.shutdown()


class TkIndependentPhoBanRoiTab(TkPhoBanScheduleTab):
    """Real schedule editor unchanged, separate read-only pixel panel."""

    def __init__(self, parent, *, roi_worker, start_producer, **kwargs):
        super().__init__(parent, **kwargs)
        self.roi_panel = TkOriginalRoiDiagnosticPanel(
            self, worker=roi_worker, producer=start_producer,
            sections=PHOBAN_SECTIONS)
        self.roi_panel.pack(side="bottom", fill="x", padx=4, pady=4)

    def _start_refresh(self):
        status = super()._start_refresh()
        self.roi_panel.start()
        return status

    def _stop_refresh(self):
        self.roi_panel.stop()
        return super()._stop_refresh()

    def shutdown(self):
        panel = getattr(self, "roi_panel", None)
        if panel is not None:
            panel.shutdown()
        return super().shutdown()


class TkIndependentDonVangRoiTab(TkDonReturnTab):
    """Dồn Vàng local settings intact, diagnostic action entirely separate."""

    def __init__(self, parent, *, roi_worker, start_producer, **kwargs):
        super().__init__(parent, **kwargs)
        self.roi_panel = TkOriginalRoiDiagnosticPanel(
            self, worker=roi_worker, producer=start_producer,
            sections=DONVANG_SECTIONS)
        self.roi_panel.pack(side="bottom", fill="x", padx=4, pady=4)

    def _start_refresh(self):
        status = super()._start_refresh()
        self.roi_panel.start()
        return status

    def _stop_refresh(self):
        self.roi_panel.stop()
        return super()._stop_refresh()

    def shutdown(self):
        panel = getattr(self, "roi_panel", None)
        if panel is not None:
            panel.shutdown()
        return super().shutdown()
