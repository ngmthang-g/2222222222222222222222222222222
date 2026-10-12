"""Source-first independent Tối ưu N02/N03/N04 real host-monitor interface.

Live Windows CPU/GPU measurements, bounded Canvas history, detachable
read-only CPU/GPU view. No game optimization, DLL sender, TLMP ping, fake
account modes or simulated Start/Stop. Exact original history/tick and
detached geometry require later combined Windows parity testing.
"""
from __future__ import annotations

from collections import deque
import tkinter as tk
from tkinter import ttk

from toiuu_host_sampler import HostPerformanceSampler


CPU_COLOR = "#1565c0"
GPU_COLOR = "#e65100"
GRID_COLOR = "#e0e0e0"
OUTLINE_COLOR = "#bbbbbb"
# Original GRAPH_HIST value is not independently recovered; this is a
# bounded local display implementation rather than certified original length.
LOCAL_HISTORY_LIMIT = 64
UI_DRAIN_MS = 250


class TkToiuuHostTab(ttk.Frame):
    """Real host monitor only. No original game performance-controller claim."""

    def __init__(self, parent):
        super().__init__(parent)
        self._closed = False
        self._selected = False
        self._after = None
        self.monitor = HostPerformanceSampler()
        self._cpu_hist = deque(maxlen=LOCAL_HISTORY_LIMIT)
        self._gpu_hist = deque(maxlen=LOCAL_HISTORY_LIMIT)
        self._cpu_value = None
        self._gpu_value = None
        self.detached = None
        self._detached_parts: dict[str, object] = {}

        monitor_group = ttk.LabelFrame(self, text="Giám sát CPU/GPU")
        monitor_group.pack(fill="x", padx=6, pady=(7, 6))
        heading = ttk.Frame(monitor_group)
        heading.pack(fill="x", padx=5, pady=(4, 2))
        ttk.Label(heading, text="Theo dõi hiệu năng.").pack(side="left")
        ttk.Button(
            heading, text="Tách theo dõi", command=self.toggle_detached
        ).pack(side="right")
        self.cpu_label = ttk.Label(
            monitor_group, text="CPU: --%", foreground=CPU_COLOR)
        self.cpu_label.pack(anchor="w", padx=6, pady=(2, 0))
        self.cpu_graph = self._canvas(monitor_group)
        self.gpu_label = ttk.Label(
            monitor_group, text="GPU: N/A (không có nvidia-smi)",
            foreground=GPU_COLOR)
        self.gpu_label.pack(anchor="w", padx=6, pady=(4, 0))
        self.gpu_graph = self._canvas(monitor_group)

        accounts = ttk.LabelFrame(self, text="Danh sách tài khoản")
        accounts.pack(fill="both", expand=True, padx=6, pady=(1, 4))
        body = ttk.Frame(accounts)
        body.pack(fill="both", expand=True)
        self.account_table = ttk.Treeview(
            body, columns=("character", "mode"), show="headings",
            selectmode="none", height=8)
        self.account_table.heading("character", text="Nhân vật")
        self.account_table.heading("mode", text="Giảm cấu hình")
        self.account_table.column("character", width=160, stretch=True)
        self.account_table.column("mode", width=176, stretch=True)
        scroll = ttk.Scrollbar(
            body, orient="vertical", command=self.account_table.yview)
        self.account_table.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.account_table.pack(side="left", fill="both", expand=True)
        ttk.Label(
            self, text=("Biểu đồ CPU/GPU đang đọc hiệu năng máy thật. "
                        "Đọc tên nhân vật, thay đổi đồ họa game và "
                        "điều khiển tất cả tài khoản chưa được kết nối."),
            wraplength=418, justify="left",
        ).pack(fill="x", padx=6, pady=(0, 6))
        self.cpu_graph.bind("<Configure>", lambda _e: self._redraw())
        self.gpu_graph.bind("<Configure>", lambda _e: self._redraw())
        self.bind("<Destroy>", self._on_destroy, add="+")

    def _canvas(self, parent):
        canvas = tk.Canvas(
            parent, background="white", height=64,
            highlightbackground=OUTLINE_COLOR, highlightthickness=1)
        canvas.pack(fill="x", padx=5, pady=(1, 3))
        return canvas

    @staticmethod
    def _fmt(value, prefix):
        if value is None:
            return ("CPU: --%" if prefix == "CPU" else
                    "GPU: N/A (không có nvidia-smi)")
        return f"{prefix}: {value:.0f}%"

    @staticmethod
    def _draw_one(canvas, history, color):
        width = max(2, int(canvas.winfo_width()))
        height = max(2, int(canvas.winfo_height()))
        canvas.delete("all")
        for pct in (25, 50, 75):
            y = height * (1.0 - pct / 100.0)
            canvas.create_line(0, y, width, y, fill=GRID_COLOR)
        if not history:
            return
        points = []
        for i, value in enumerate(history):
            x = i * (width - 2) / max(1, len(history) - 1) + 1
            if value is None:
                if len(points) >= 4:
                    canvas.create_line(*points, fill=color, width=1.5)
                points = []
                continue
            y = (height - 2) * (1 - max(0, min(100, value)) / 100.0) + 1
            points.extend((x, y))
        if len(points) >= 4:
            canvas.create_line(*points, fill=color, width=1.5)

    def _redraw(self):
        if self._closed:
            return
        self.cpu_label.configure(text=self._fmt(self._cpu_value, "CPU"))
        self.gpu_label.configure(text=self._fmt(self._gpu_value, "GPU"))
        self._draw_one(self.cpu_graph, self._cpu_hist, CPU_COLOR)
        self._draw_one(self.gpu_graph, self._gpu_hist, GPU_COLOR)
        self._redraw_detached()

    def _poll(self):
        self._after = None
        if self._closed or not (self._selected or self.detached is not None):
            return
        sample = self.monitor.drain()
        if sample is not None:
            self._cpu_value = sample.cpu_percent
            self._gpu_value = sample.gpu_percent
            self._cpu_hist.append(sample.cpu_percent)
            self._gpu_hist.append(sample.gpu_percent)
            self._redraw()
        self._schedule_poll()

    def _schedule_poll(self):
        if (not self._closed and self._after is None
                and (self._selected or self.detached is not None)):
            self._after = self.after(UI_DRAIN_MS, self._poll)

    def _start_refresh(self):
        if self._closed:
            return False
        self._selected = True
        self.monitor.start_refresh()
        self._schedule_poll()
        return True

    def _stop_refresh(self):
        self._selected = False
        if self.detached is None:
            self.monitor.stop_refresh()
            self._cancel_poll()

    def _cancel_poll(self):
        if self._after is not None:
            token, self._after = self._after, None
            try:
                self.after_cancel(token)
            except tk.TclError:
                pass

    def toggle_detached(self):
        if self._closed:
            return False
        if self.detached is not None:
            self._close_detached()
            return False
        top = tk.Toplevel(self)
        top.title("CPU / GPU")
        root = self.winfo_toplevel()
        root.update_idletasks()
        # Original nominal height=768 and left-of-parent placement. Exact
        # original width/screen-edge/HiDPI formula remains UNKNOWN.
        height = min(768, max(240, root.winfo_screenheight() - 60))
        top.geometry(f"190x{height}+{max(0, root.winfo_rootx() - 190)}+"
                     f"{max(0, root.winfo_rooty())}")
        top.protocol("WM_DELETE_WINDOW", self._close_detached)
        frame = ttk.Frame(top)
        frame.pack(fill="both", expand=True, padx=5, pady=5)
        columns = ttk.Frame(frame)
        columns.pack(fill="both", expand=True)
        parts = {}
        for index, (title, color) in enumerate((
                ("CPU", CPU_COLOR), ("GPU", GPU_COLOR))):
            col = ttk.LabelFrame(columns, text=title)
            col.grid(row=0, column=index, sticky="nsew", padx=1)
            columns.columnconfigure(index, weight=1)
            columns.rowconfigure(0, weight=1)
            label = ttk.Label(col, text="--%", foreground=color)
            label.pack(padx=3, pady=3)
            canvas = tk.Canvas(col, width=55, height=375,
                               background="white",
                               highlightbackground=OUTLINE_COLOR,
                               highlightthickness=1)
            canvas.pack(fill="both", expand=True, padx=4, pady=4)
            parts[title] = (label, canvas, color)
        ttk.Button(
            frame, text="Đóng theo dõi", command=self._close_detached
        ).pack(pady=(4, 0))
        self.detached = top
        self._detached_parts = parts
        self.monitor.start_refresh()
        self._schedule_poll()
        self._redraw_detached()
        return True

    def _redraw_detached(self):
        if self._closed or self.detached is None:
            return
        for name, value in (("CPU", self._cpu_value),
                            ("GPU", self._gpu_value)):
            label, canvas, color = self._detached_parts[name]
            label.configure(text=("--%" if value is None else
                                  f"{value:.0f}%"))
            w = max(2, canvas.winfo_width())
            h = max(2, canvas.winfo_height())
            canvas.delete("all")
            canvas.create_rectangle(
                1, 1, w-1, h-1, outline=GRID_COLOR)
            if value is not None:
                filled = h * max(0.0, min(100.0, value)) / 100.0
                canvas.create_rectangle(
                    2, h - filled, w - 2, h - 2,
                    fill=color, outline=color)

    def _close_detached(self):
        top, self.detached = self.detached, None
        self._detached_parts = {}
        if top is not None:
            try:
                top.destroy()
            except tk.TclError:
                pass
        if not self._selected:
            self.monitor.stop_refresh()
            self._cancel_poll()

    def shutdown(self):
        if self._closed:
            return
        self._closed = True
        self._cancel_poll()
        self._close_detached()
        self.monitor.shutdown()

    def _on_destroy(self, event):
        if event.widget is self:
            self.shutdown()
