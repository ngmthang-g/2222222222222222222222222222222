"""S10/S11: real read-only Tk Start window-list + DWM preview slice.

Only S08 Win32-observed HWND/PID/title snapshots delivered by S09's worker
are displayed. S11 DWM previews use actual Win32 HWND+PID and real compositor
thumbnail API. No game command, character-memory read, master selection,
mouse binding, layout buttons or entitlement is reconstructed here.
The shell must grant the Start tab from a separately verified server snapshot.
"""
from __future__ import annotations

from dataclasses import dataclass

from dwm_preview import (
    ITEM_WIDTH, ITEM_HEIGHT, THUMB_WIDTH, THUMB_HEIGHT,
    NativeDwmBackend, PreviewPlacement, ReadOnlyDwmPreviews,
)

from start_polling import (
    START_UI_POLL_MS, StartCacheEvent, StartWindowProducer,
    TkStartCachePoller, WindowSnapshot,
)


@dataclass(frozen=True)
class StartWindowRow:
    hwnd: int
    pid: int
    title: str


@dataclass(frozen=True)
class StartReadOnlyState:
    code: str
    caption: str
    rows: tuple[StartWindowRow, ...] = ()


def readonly_state(snapshot: WindowSnapshot) -> StartReadOnlyState:
    """Pure presentation of actual cache state; no synthetic game/window names."""
    if not snapshot.valid:
        if snapshot.error:
            return StartReadOnlyState("ERROR", "Không thể đọc danh sách cửa sổ game")
        return StartReadOnlyState("PENDING", "Đang kiểm tra cửa sổ game...")
    rows = tuple(StartWindowRow(w.hwnd, w.pid, w.title) for w in snapshot.windows)
    if not rows:
        return StartReadOnlyState("EMPTY", "Không phát hiện cửa sổ game")
    return StartReadOnlyState("LIVE", f"Đã phát hiện {len(rows)} cửa sổ game", rows)


class TLMStartTab:
    """Passive Start view; factory MUST NOT be installed as an auth bypass.

    TabLifecycle controls visibility and calls _start_refresh/_stop_refresh.
    Worker scans on its own thread. Widgets are modified only by Tk callbacks.
    """

    def __init__(self, parent, *, producer: StartWindowProducer | None = None,
                 interval_ms: int = START_UI_POLL_MS,
                 preview_backend_factory=None):
        from tkinter import ttk
        self.parent = parent
        self.container = ttk.Frame(parent)
        self.container.pack(fill="both", expand=True)
        self._closed = False
        self._state = StartReadOnlyState("STOPPED", "Chưa quét cửa sổ game")
        self.status = ttk.Label(self.container, text=self._state.caption, anchor="w")
        self.status.pack(fill="x", padx=10, pady=(10, 5))
        self.group = ttk.LabelFrame(self.container, text="Danh sách cửa sổ game (chỉ xem)")
        self.group.pack(fill="x", padx=9, pady=(0, 5))
        self.table = ttk.Treeview(
            self.group, columns=("title", "pid", "hwnd"),
            show="headings", selectmode="none", height=8,
        )
        for key, heading, width, stretch in (
            ("title", "Tên cửa sổ", 206, True),
            ("pid", "PID", 68, False),
            ("hwnd", "HWND", 104, False),
        ):
            self.table.heading(key, text=heading)
            self.table.column(key, width=width, stretch=stretch, anchor="w")
        self.scroll = ttk.Scrollbar(self.group, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=self.scroll.set)
        self.scroll.pack(side="right", fill="y")
        self.table.pack(side="left", fill="both", expand=True)
        self.preview_group = ttk.LabelFrame(
            self.container, text="DWM preview (đọc trực tiếp)")
        self.preview_group.pack(fill="x", padx=9, pady=(0, 9))
        self.preview_status = ttk.Label(
            self.preview_group, text="Chưa có cửa sổ game", anchor="w")
        self.preview_status.pack(fill="x", padx=4)
        self.preview_tiles = ttk.Frame(self.preview_group)
        self.preview_tiles.pack(fill="x", padx=2)
        self._tile_items = {}
        self._active_windows = ()
        self._preview_after = None
        self._preview_controller = None
        self._preview_backend_factory = preview_backend_factory or NativeDwmBackend
        self.poller = TkStartCachePoller(
            self.container, producer if producer is not None else StartWindowProducer(),
            self._on_cache_event, interval_ms=interval_ms,
        )
        self.container.bind("<Destroy>", self._on_destroy, add="+")

    @property
    def readonly_view(self) -> StartReadOnlyState:
        return self._state

    def _render(self, state: StartReadOnlyState) -> None:
        self._state = state
        self.status.configure(text=state.caption)
        for iid in self.table.get_children():
            self.table.delete(iid)
        for row in state.rows:
            # HWND+PID makes reused handles distinct; no row can be a game action.
            self.table.insert(
                "", "end", iid=f"{row.hwnd}:{row.pid}",
                values=(row.title, str(row.pid), str(row.hwnd)),
            )

    def _on_cache_event(self, event: StartCacheEvent) -> None:
        if self._closed or not self.poller.active:
            return
        self._render(readonly_state(event.snapshot))
        self._sync_tiles(event.snapshot.windows if event.snapshot.valid else ())
        self._schedule_preview()

    def _sync_tiles(self, windows) -> None:
        """Only genuine S09 discovery rows get preview surfaces, never fakes."""
        import tkinter as tk
        from tkinter import ttk
        wanted = {(w.hwnd, w.pid) for w in windows}
        # A vanished/reused HWND invalidates DWM immediately, before Tk redraw.
        old_keys = set(self._tile_items)
        if self._preview_controller is not None and old_keys - wanted:
            self._preview_controller.clear()
        if not windows:
            self._drop_previews()
        for key in tuple(self._tile_items):
            if key not in wanted:
                tile, _, _ = self._tile_items.pop(key)
                tile.destroy()
        self._active_windows = tuple(windows)
        for w in windows:
            key = (w.hwnd, w.pid)
            if key not in self._tile_items:
                tile = ttk.Frame(self.preview_tiles, width=ITEM_WIDTH,
                                 height=ITEM_HEIGHT, relief="solid", borderwidth=1)
                tile.grid_propagate(False)
                label = ttk.Label(tile, text=w.title or f"HWND {w.hwnd}", anchor="w")
                label.place(x=4, y=3, width=THUMB_WIDTH, height=19)
                surface = tk.Frame(tile, bg="#000000", width=THUMB_WIDTH,
                                   height=THUMB_HEIGHT)
                surface.place(x=4, y=23, width=THUMB_WIDTH, height=THUMB_HEIGHT)
                surface.bind("<Configure>", lambda _event: self._schedule_preview(), add="+")
                self._tile_items[key] = (tile, label, surface)
            else:
                self._tile_items[key][1].configure(text=w.title or f"HWND {w.hwnd}")
        for index, w in enumerate(windows):
            self._tile_items[(w.hwnd, w.pid)][0].grid(
                row=index // 2, column=index % 2, padx=2, pady=2)
        self.preview_status.configure(
            text=f"{len(windows)} cửa sổ có nguồn DWM thực" if windows
            else "Chưa có cửa sổ game")

    def _schedule_preview(self) -> None:
        if self._closed or not self.poller.active or not self._active_windows:
            return
        if self._preview_after is not None:
            return
        # Debounce Tk geometry changes; not a game capture/frame timer.
        self._preview_after = self.container.after(80, self._refresh_dwm)

    def _refresh_dwm(self) -> None:
        self._preview_after = None
        if self._closed or not self.poller.active:
            return
        if not self.container.winfo_viewable():
            if self._preview_controller is not None:
                self._preview_controller.clear()
            return
        placements = []
        owner = int(self.container.winfo_toplevel().winfo_id())
        for w in self._active_windows:
            item = self._tile_items.get((w.hwnd, w.pid))
            if item is None:
                continue
            surface = item[2]
            if not surface.winfo_viewable():
                continue
            width, height = surface.winfo_width(), surface.winfo_height()
            if width <= 1 or height <= 1:
                continue
            placements.append(PreviewPlacement(
                w.hwnd, w.pid, owner, surface.winfo_rootx(), surface.winfo_rooty(),
                width, height))
        if not placements:
            if self._preview_controller is not None:
                self._preview_controller.clear()
            return
        try:
            if self._preview_controller is None:
                self._preview_controller = ReadOnlyDwmPreviews(
                    self._preview_backend_factory())
            result = self._preview_controller.sync(placements)
            if result.errors:
                self.preview_status.configure(text=(
                    "Preview lỗi: " + ", ".join(str(hwnd) + " " + reason
                                                for hwnd, reason in result.errors)))
            else:
                self.preview_status.configure(
                    text=f"DWM: {len(result.rendered)} cửa sổ đang hiển thị")
        except Exception as exc:
            self._drop_previews()
            self.preview_status.configure(
                text=f"Preview lỗi: {type(exc).__name__}: {exc}")

    def _drop_previews(self) -> None:
        if self._preview_after is not None:
            try:
                self.container.after_cancel(self._preview_after)
            except Exception:
                pass
            self._preview_after = None
        if self._preview_controller is not None:
            self._preview_controller.shutdown()
            self._preview_controller = None

    def _start_refresh(self) -> None:
        if self._closed or self.poller.active:
            return
        self._render(StartReadOnlyState("PENDING", "Đang kiểm tra cửa sổ game..."))
        self.poller._start_refresh()

    def _stop_refresh(self) -> None:
        self.poller._stop_refresh()
        self._drop_previews()
        self._sync_tiles(())
        if not self._closed:
            # Do not show stale HWND/PID when Start is hidden/revoked.
            self._render(StartReadOnlyState("STOPPED", "Chưa quét cửa sổ game"))

    def _on_destroy(self, event) -> None:
        if event.widget is self.container:
            self.shutdown()

    def shutdown(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._drop_previews()
        self.poller.shutdown()
