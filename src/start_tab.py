"""S10–S14: read-only Tk Start, live DWM preview, grid and ordering.

Only S08 Win32-observed HWND/PID/title snapshots delivered by S09's worker
are displayed. S11 DWM previews use actual Win32 HWND+PID and real compositor
thumbnail API. No game command, character-memory read, master selection,
mouse binding, layout buttons or entitlement is reconstructed here.
The shell must grant the Start tab from a separately verified server snapshot.
"""
from __future__ import annotations

from dataclasses import dataclass

from preview_maintenance import TkPreviewMaintenance
from preview_layout import (
    DEFAULT_PREVIEW_GRID, PREVIEW_GRID_CHOICES, PreviewOrder,
    preview_columns, preview_position,
)

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
        # C09 native readonly combobox, initial 2x from original baseline.
        self.preview_controls = ttk.Frame(self.preview_group)
        self.preview_controls.pack(fill="x", padx=4, pady=(2, 0))
        ttk.Label(self.preview_controls, text="Cột:").pack(side="left")
        import tkinter as tk
        self.preview_grid_var = tk.StringVar(value=DEFAULT_PREVIEW_GRID)
        self.preview_grid_manual = False
        self.preview_grid_select = ttk.Combobox(
            self.preview_controls, textvariable=self.preview_grid_var,
            values=PREVIEW_GRID_CHOICES, state="readonly", width=4)
        self.preview_grid_select.pack(side="left", padx=(4, 0))
        self.preview_grid_select.bind(
            "<<ComboboxSelected>>", self._set_manual_preview_grid, add="+")
        self.preview_order = PreviewOrder()
        self._observed_windows = ()
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
        # C03/C04: root movement changes screen origin without resizing Tk
        # thumbnail anchors. Register lifecycle-safe root/child observers.
        self._top = self.container.winfo_toplevel()
        self._top_handlers = [
            ("<Configure>", self._top.bind("<Configure>", self._on_top_configure, add="+")),
            ("<Unmap>", self._top.bind("<Unmap>", self._on_top_unmap, add="+")),
            ("<Map>", self._top.bind("<Map>", self._on_top_map, add="+")),
        ]
        self.container.bind("<Unmap>", self._on_container_unmap, add="+")
        self.container.bind("<Map>", self._on_container_map, add="+")
        self.poller = TkStartCachePoller(
            self.container, producer if producer is not None else StartWindowProducer(),
            self._on_cache_event, interval_ms=interval_ms,
        )
        # C04: independent 800/2000ms housekeeping, *not* DWM image FPS.
        # It consumes the exact same S09 cache, never invokes EnumWindows.
        self.maintenance = TkPreviewMaintenance(
            self.container, self.poller.producer, self._on_maintenance_tick)
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

    def _present_cached_snapshot(self, snapshot: WindowSnapshot) -> None:
        """Rebuild only when a real cached state/window list changed (C04)."""
        state = readonly_state(snapshot)
        if state != self._state:
            self._render(state)
        windows = snapshot.windows if snapshot.valid else ()
        if windows != self._observed_windows:
            self._sync_tiles(windows)

    def _on_cache_event(self, event: StartCacheEvent) -> None:
        if self._closed or not self.poller.active:
            return
        self._present_cached_snapshot(event.snapshot)
        self._schedule_preview()

    def _on_maintenance_tick(self, snapshot: WindowSnapshot) -> None:
        """Selected Start housekeeping on Tk: no discovery and no fake HP."""
        if self._closed or not self.poller.active or not self.maintenance.active:
            return
        self._present_cached_snapshot(snapshot)
        # With same revision, still re-check source HWND+PID using native DWM
        # backend; this can drop a closed HWND before the next 2s list poll.
        # No BitBlt, screenshot, frame extraction or game input.
        if self._preview_after is None:
            self._refresh_dwm()

    def _sync_tiles(self, windows) -> None:
        """Bind only S09-discovered HWND/PID values to C09/C17 tile widgets."""
        import tkinter as tk
        from tkinter import ttk
        windows = tuple(windows)
        ordered = self.preview_order.update(windows)
        self._observed_windows = windows
        wanted = {(w.hwnd, w.pid) for w in ordered}
        # A vanished/reused HWND invalidates DWM immediately, before Tk redraw.
        old_keys = set(self._tile_items)
        if self._preview_controller is not None and old_keys - wanted:
            self._preview_controller.clear()
        if not windows:
            self._drop_previews()
        for key in tuple(self._tile_items):
            if key not in wanted:
                item = self._tile_items.pop(key)
                item[0].destroy()
        self._active_windows = ordered
        for w in ordered:
            key = (w.hwnd, w.pid)
            if key not in self._tile_items:
                tile = ttk.Frame(self.preview_tiles, width=ITEM_WIDTH,
                                 height=ITEM_HEIGHT, relief="solid", borderwidth=1)
                tile.grid_propagate(False)
                label = ttk.Label(tile, text=w.title or f"HWND {w.hwnd}", anchor="w")
                label.place(x=4, y=3, width=121, height=19)
                # C17: real functioning logical preview-order arrows, NOT
                # game controls, Win32 activation or mouse interception.
                left = ttk.Button(tile, text="◀", width=2,
                                  command=lambda hwnd=w.hwnd, pid=w.pid:
                                  self._move_preview_item(hwnd, pid, -1))
                right = ttk.Button(tile, text="▶", width=2,
                                   command=lambda hwnd=w.hwnd, pid=w.pid:
                                   self._move_preview_item(hwnd, pid, 1))
                left.place(x=128, y=3, width=31, height=19)
                right.place(x=163, y=3, width=31, height=19)
                surface = tk.Frame(tile, bg="#000000", width=THUMB_WIDTH,
                                   height=THUMB_HEIGHT)
                surface.place(x=4, y=23, width=THUMB_WIDTH, height=THUMB_HEIGHT)
                surface.bind("<Configure>", lambda _event: self._schedule_preview(), add="+")
                self._tile_items[key] = (tile, label, surface, left, right)
            else:
                self._tile_items[key][1].configure(text=w.title or f"HWND {w.hwnd}")
        self._relayout_tiles()
        self.preview_status.configure(
            text=f"{len(ordered)} cửa sổ có nguồn DWM thực" if ordered
            else "Chưa có cửa sổ game")

    def _get_preview_columns(self) -> int:
        return preview_columns(self.preview_grid_var.get())

    def _relayout_tiles(self) -> None:
        columns = self._get_preview_columns()
        for index, w in enumerate(self._active_windows):
            key = (w.hwnd, w.pid)
            tile = self._tile_items[key][0]
            row, col = preview_position(index, columns)
            tile.grid(row=row, column=col, padx=2, pady=2)
        self._schedule_preview()

    def _set_manual_preview_grid(self, _event=None) -> bool:
        """C09: change actual Tk column positions without new game commands."""
        try:
            self._get_preview_columns()
        except ValueError:
            self.preview_grid_var.set(DEFAULT_PREVIEW_GRID)
            return False
        if self._closed or not self.poller.active:
            return False
        self.preview_grid_manual = True  # S14 local model; original order UNKNOWN
        self._relayout_tiles()
        return True

    def _move_preview_item(self, hwnd: int, pid: int, delta: int) -> bool:
        """C17 logical one-step order; no source HWND/window activation."""
        if self._closed or not self.poller.active:
            return False
        if not self.preview_order.move(hwnd, pid, delta):
            return False
        self._active_windows = self.preview_order.ordered(self._observed_windows)
        self._relayout_tiles()
        return True

    def _on_top_configure(self, event) -> None:
        # The root can MOVE without resizing the child preview surfaces.
        if event.widget is self._top:
            self._schedule_preview()

    def _on_top_unmap(self, event) -> None:
        if event.widget is self._top:
            self._drop_previews()

    def _on_top_map(self, event) -> None:
        if event.widget is self._top:
            self._schedule_preview()

    def _on_container_unmap(self, event) -> None:
        if event.widget is self.container:
            self._drop_previews()

    def _on_container_map(self, event) -> None:
        if event.widget is self.container:
            self._schedule_preview()

    def _schedule_preview(self) -> None:
        if self._closed or not self.poller.active or not self._active_windows:
            return
        if self._preview_after is not None:
            return
        # Original C04 recovers 60ms reposition debounce, not a DWM FPS.
        self._preview_after = self.container.after(60, self._refresh_dwm)

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
        self.maintenance.start()

    def _stop_refresh(self) -> None:
        self.maintenance.stop()
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
        self.maintenance.shutdown()
        self._drop_previews()
        for sequence, binding in self._top_handlers:
            if binding:
                try:
                    self._top.unbind(sequence, binding)
                except Exception:
                    # Tk may already be destroyed during shutdown.
                    pass
        self._top_handlers.clear()
        self.poller.shutdown()
