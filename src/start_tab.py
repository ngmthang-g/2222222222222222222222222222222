"""S10–S18: Start DWM, close, bounded layout and master/grid controls.

S08 Win32-observed HWND/PID/title snapshots arrive from the S09 worker.
S11 DWM thumbnails are live; S16 posts WM_CLOSE only after native HWND/PID
verification; S17 offers a bounded, verified-limit C18 layout mover on its
own worker thread. Original C18 geometry/cadence and C19 keyboard/mouse sync
are NOT reconstructed. No game memory reader, Proxy or local license grant.
The shell must grant Start from an independently verified server snapshot.
"""
from __future__ import annotations

from dataclasses import dataclass
import threading

from layout_windows import (
    C18LayoutSync, GRID_COLS_DEFAULT, GRID_ROWS_DEFAULT,
)
from window_stacking import C10C11WindowStacker, StackResult
from grid_master import GridSettingsStore, MasterSelection, update_dimension
from close_windows import C16CloseAll
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
                 preview_backend_factory=None, close_service_factory=None,
                 layout_service_factory=None, grid_settings_store=None,
                 stack_service_factory=None):
        from tkinter import ttk
        self.parent = parent
        self.container = ttk.Frame(parent)
        self.container.pack(fill="both", expand=True)
        self._closed = False
        self._state = StartReadOnlyState("STOPPED", "Chưa quét cửa sổ game")
        self._build_verified_auto_controls()
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
        # C15: verified main-preview "Làm mới" is a full DWM rebuild,
        # NOT just a label update or forced memory/game-process scan.
        self.btn_refresh_preview = ttk.Button(
            self.preview_controls, text="Làm mới",
            command=self.refresh_window_preview_list)
        self.btn_refresh_preview.pack(side="left", padx=(8, 0))
        # C16: real, normal WM_CLOSE on a fresh-validated game HWND, never
        # a preview-only widget close or force-kill/Unity handler cleanup.
        self.btn_close_all = ttk.Button(
            self.preview_controls, text="Đóng hết",
            command=self._close_all_preview_windows)
        self.btn_close_all.pack(side="left", padx=(6, 0))
        self._close_service_factory = close_service_factory or C16CloseAll
        self.last_close_result = None
        # C18 layout sync is separate from C19 input synchronization.
        # Original C18 cadence and grid arithmetic UNKNOWN. This bounded
        # S17 worker consumes the immutable cache and uses local MOVE-ONLY
        # geometry. No server max_windows => no operational layout action.
        self._grid_settings = (grid_settings_store if grid_settings_store is not None
                               else GridSettingsStore())
        loaded_grid = self._grid_settings.load()
        self.grid_cols = loaded_grid.cols
        self.grid_rows = loaded_grid.rows
        self.master_selection = MasterSelection()
        self.layout_max_windows = 0
        self.layout_master_hwnd = None
        self.layout_active = False
        self.sync_layout_running = False
        self.sync_loop_id = 0
        self._grid_slots = {}
        self._layout_service_factory = layout_service_factory or C18LayoutSync
        self._layout_allow = threading.Event()
        self._layout_thread = None
        self._layout_last_result = None
        self._layout_reported_result = None
        # S59 recovered the exact B14 Auto bitmap. Only C10/C11 controls
        # are wired; C07 mode automation and C12 restore remain unverified.
        self._stack_service_factory = stack_service_factory or C10C11WindowStacker
        self._stack_thread = None
        self._stack_allow = threading.Event()
        self._stack_generation = 0
        self._stack_last_result = None
        self.layout_controls = ttk.LabelFrame(
            self.container, text="Xếp lưới — đồng bộ vị trí cửa sổ")
        self.layout_controls.pack(fill="x", padx=9, pady=(0, 6))
        import tkinter as tk
        self.btn_layout = tk.Button(
            self.layout_controls, text="Đồng bộ các cửa sổ",
            background="#f44336", foreground="#ffffff",
            command=self._toggle_layout)
        self.btn_layout.pack(side="left", padx=5, pady=4)
        self.btn_decrease_cols = ttk.Button(
            self.layout_controls, text="−", width=2, command=self._decrease_cols)
        self.btn_decrease_cols.pack(side="left", padx=(5, 0))
        self.grid_cols_label = ttk.Label(self.layout_controls, text="")
        self.grid_cols_label.pack(side="left", padx=(2, 2))
        self.btn_increase_cols = ttk.Button(
            self.layout_controls, text="+", width=2, command=self._increase_cols)
        self.btn_increase_cols.pack(side="left")
        self.btn_decrease_rows = ttk.Button(
            self.layout_controls, text="−", width=2, command=self._decrease_rows)
        self.btn_decrease_rows.pack(side="left", padx=(8, 0))
        self.grid_rows_label = ttk.Label(self.layout_controls, text="")
        self.grid_rows_label.pack(side="left", padx=(2, 2))
        self.btn_increase_rows = ttk.Button(
            self.layout_controls, text="+", width=2, command=self._increase_rows)
        self.btn_increase_rows.pack(side="left")
        self.layout_status = ttk.Label(
            self.layout_controls, text="Chưa có quyền số cửa sổ", anchor="w")
        self.layout_status.pack(side="left", padx=5)
        # C05: live HWND-backed master radios; not a dropdown nor a saved HWND.
        self.master_radio_group = ttk.LabelFrame(
            self.container, text="Cửa sổ chính:")
        self.master_radio_group.pack(fill="x", padx=9, pady=(0, 5))
        self._master_radio_frame = ttk.Frame(self.master_radio_group)
        self._master_radio_frame.pack(fill="x", padx=4, pady=3)
        self._master_var = tk.StringVar(value="")
        self._master_hwnd_cache = ()
        self._master_radio_buttons = []
        self._hwnd_by_name = {}
        self._on_grid_change()
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
        elif hasattr(self, "master_selection"):
            self._update_master_combobox(windows)

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
        # Worker uses S09 cached HWND set. Native validation/movement is
        # NEVER executed on Tk's UI thread.
        if self.layout_active:
            self._layout_worker(snapshot)
        if self._layout_last_result is not self._layout_reported_result:
            self._layout_reported_result = self._layout_last_result
            if self._layout_last_result is not None:
                self.layout_status.configure(text=self._layout_last_result.code)

    def _sync_tiles(self, windows) -> None:
        """Bind only S09-discovered HWND/PID values to C09/C17 tile widgets."""
        import tkinter as tk
        from tkinter import ttk
        windows = tuple(windows)
        self._update_master_combobox(windows)
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

    def _clear_window_preview_list(self) -> None:
        """C15: unregister DWM BEFORE destroying preview Tk item frames.

        Keep the C09 choice and C17 source-HWND ordering; they are user state,
        not disposable DWM frame resources.
        """
        self._drop_previews()
        for item in tuple(self._tile_items.values()):
            item[0].destroy()
        self._tile_items.clear()
        self._active_windows = ()
        self._observed_windows = ()

    def refresh_window_preview_list(self) -> bool:
        """C15: explicit real full-refresh from S09's immutable cache only.

        No Win32 EnumWindows, game memory reads or new authorization. Must
        clear stale DWM resources even when snapshot access fails. E03 owns
        Start visibility and permits this command only while selected/active.
        """
        if self._closed or not self.poller.active:
            return False
        try:
            if not self.container.winfo_viewable():
                return False
        except Exception:
            return False

        # Read only the existing O(1) S09 cache. Do not guess whether the
        # original "Làm mới" caused fresh game-process discovery.
        try:
            snapshot = self.poller.producer.read_snapshot()
            if not isinstance(snapshot, WindowSnapshot):
                raise TypeError("INVALID_WINDOW_SNAPSHOT")
        except Exception:
            self._clear_window_preview_list()
            self._render(StartReadOnlyState(
                "ERROR", "Không thể đọc danh sách cửa sổ game"))
            self.preview_status.configure(text="Preview lỗi: không đọc được cache")
            return False

        self._clear_window_preview_list()
        try:
            self._present_cached_snapshot(snapshot)
        except Exception as exc:
            self._clear_window_preview_list()
            self._render(StartReadOnlyState(
                "ERROR", "Không thể đọc danh sách cửa sổ game"))
            self.preview_status.configure(text=f"Preview lỗi: {type(exc).__name__}")
            return False
        if not snapshot.valid:
            self.preview_status.configure(text="Preview lỗi: cache không hợp lệ")
        elif not snapshot.windows:
            self.preview_status.configure(
                text="Không tìm thấy cửa sổ game, hãy mở game trước.")
        else:
            self._schedule_preview()
        return True

    def _close_all(self):
        """C16 original wrapper name; never bypass the selected-Start gate."""
        return self._close_all_preview_windows()

    def _close_all_preview_windows(self):
        """Post WM_CLOSE only to fresh-validated genuine HWND+PID game sources.

        Do not interpret PostMessage success as proof game has exited. S09/S13
        will refresh preview from actual subsequently observed windows; the
        original immediate post-close refresh rule is explicitly UNKNOWN.
        """
        if self._closed or not self.poller.active:
            return None
        try:
            if not self.container.winfo_viewable():
                return None
            snapshot = self.poller.producer.read_snapshot()  # only current cache
            result = self._close_service_factory().close_all_game_windows(snapshot)
        except Exception:
            self.preview_status.configure(text="Đóng hết: lỗi kiểm tra HWND")
            return None
        self.last_close_result = result
        # WM_CLOSE is asynchronous: messages POSTED is not windows CLOSED.
        self.preview_status.configure(
            text=f"Đóng hết: đã gửi WM_CLOSE {len(result.posted)}/{result.requested}"
            if result.posted else "Đóng hết: không có cửa sổ hợp lệ để đóng")
        return result

    def _on_grid_change(self) -> None:
        """C08 original label updater, using strictly local safety bounds."""
        self.grid_cols_label.configure(text=f"Cột: {self.grid_cols}")
        self.grid_rows_label.configure(text=f"Hàng: {self.grid_rows}")

    def _change_grid(self, axis: str, delta: int) -> bool:
        if self._closed or not self.poller.active:
            return False
        try:
            field = "grid_cols" if axis == "cols" else "grid_rows"
            current = getattr(self, field)
            changed = update_dimension(current, delta)
        except (ValueError, AttributeError):
            return False
        if changed == current:
            return False
        setattr(self, field, changed)
        self._on_grid_change()
        try:
            self._grid_settings.save(self.grid_cols, self.grid_rows)
        except (OSError, RuntimeError, ValueError):
            self.layout_status.configure(text="Lỗi lưu cấu hình lưới")
        if self.layout_active:
            self._reschedule_layout_for_user_choice()
        return True

    def _decrease_cols(self) -> bool:
        return self._change_grid("cols", -1)

    def _increase_cols(self) -> bool:
        return self._change_grid("cols", 1)

    def _decrease_rows(self) -> bool:
        return self._change_grid("rows", -1)

    def _increase_rows(self) -> bool:
        return self._change_grid("rows", 1)

    def _update_master_combobox(self, windows) -> None:
        """C05 name is historical: UI is dynamic RADIOs keyed by HWND + PID."""
        from tkinter import ttk
        if not hasattr(self, "master_selection"):
            return
        windows = tuple(windows)
        previous = self.master_selection.selected
        try:
            changed = self.master_selection.update(windows)
        except ValueError:
            # Invalid cache cannot result in a new HWND identity choice.
            return
        if self.layout_active and self.master_selection.selected != previous:
            # A vanished/reused chosen HWND must cancel pending native work
            # against the old generation before any new layout pass.
            self._reschedule_layout_for_user_choice()
        self.layout_master_hwnd = self.master_selection.hwnd
        identity = self.master_selection.selected
        self._master_var.set(
            f"{identity[0]}:{identity[1]}" if identity else "")
        self._hwnd_by_name = {}
        if changed:
            for radio in self._master_radio_buttons:
                radio.destroy()
            self._master_radio_buttons.clear()
        for index, window in enumerate(windows):
            # S09 does NOT yet expose actual RoleName/HP; only real titles
            # can be shown. The suffix guarantees non-colliding labels.
            title = (window.title or "Cửa sổ").strip()
            label = f"{title} [HWND {window.hwnd}]"
            self._hwnd_by_name[label] = window.hwnd
            key = f"{window.hwnd}:{window.pid}"
            if changed:
                radio = ttk.Radiobutton(
                    self._master_radio_frame, text=label,
                    variable=self._master_var, value=key,
                    command=lambda h=window.hwnd,p=window.pid:
                    self._on_master_change(h, p))
                radio.pack(side="top", anchor="w", padx=(2, 5), pady=1)
                self._master_radio_buttons.append(radio)
            else:
                self._master_radio_buttons[index].configure(text=label)

    def _on_master_change(self, hwnd: int, pid: int) -> bool:
        """C05 manual master; no C19 input sync to stop/unlock yet."""
        if self._closed or not self.poller.active:
            return False
        if not self.container.winfo_viewable():
            return False
        if not self.master_selection.choose(hwnd, pid):
            return False
        self.layout_master_hwnd = hwnd
        self._cancel_stack_worker()  # a pending stack has the old master
        self._master_var.set(f"{hwnd}:{pid}")
        if self.layout_active:
            self._reschedule_layout_for_user_choice()
        return True

    def _reschedule_layout_for_user_choice(self) -> None:
        """Discard worker's old generation, keep layout sync enabled.

        C05 only verifies input-sync must stop on changing master; it does
        not say layout sync stops. Existing S13 tick starts new generation.
        """
        old = self._layout_allow
        old.clear()
        self.sync_loop_id += 1
        self._layout_allow = threading.Event()
        self._layout_allow.set()

    def set_layout_max_windows(self, max_windows: int) -> None:
        """Only shell's verified PermissionSnapshot should call this.

        A direct user toggle cannot invent a client-side 999 fallback.
        """
        self.layout_max_windows = (max_windows if type(max_windows) is int
                                   and max_windows > 0 else 0)
        if not self.layout_max_windows:
            self._cancel_stack_worker()
            self._stop_sync_loop()
            if not self._closed:
                self.layout_status.configure(text="Chưa có quyền số cửa sổ")

    def _cancel_stack_worker(self) -> None:
        """S56: lock-free cancel; never join a native move on the Tk thread."""
        event = getattr(self, "_stack_allow", None)
        if event is not None:
            event.clear()
        self._stack_generation = getattr(self, "_stack_generation", 0) + 1
        self._stack_last_result = None

    def _build_verified_auto_controls(self) -> None:
        """S59 partial Auto frame, measured from the hash-locked B14 raster.

        Coordinates are relative to the original tab content origin (7,57)
        in the 452x1032 screenshot. The reserved mode area and unimplemented
        quick actions remain empty: no decorative nonfunctional buttons.
        Existing diagnostic controls follow BELOW this measured fragment.
        This is not full Start UI parity or an implementation of C07 Auto.
        """
        import tkinter as tk
        from tkinter import ttk
        self.auto_region = tk.Frame(self.container, height=244, bg="#f0f0f0")
        self.auto_region.pack(fill="x")
        ttk.Style(self.container).configure(
            "Bold.TLabelframe.Label", font=("Segoe UI", 9, "bold"))
        self.auto_frame = ttk.LabelFrame(
            self.auto_region, text=" Điều khiển nhanh ",
            style="Bold.TLabelframe")
        self.auto_frame.place(x=4, y=56, width=428, height=188)
        self.btn_stack_tight = tk.Button(
            self.auto_frame, text="Xếp gọn", command=self._stack_tight_cmd,
            bg="#4169e1", fg="white", font=("Segoe UI", 8, "bold"),
            relief="raised", bd=1, highlightthickness=0, cursor="hand2")
        self.btn_stack_tight.place(x=165, y=22, width=78, height=21,
                                   bordermode="outside")
        self.btn_stack_diagonal = tk.Button(
            self.auto_frame, text="Xếp chéo", command=self._stack_diagonal_cmd,
            bg="#4169e1", fg="white", font=("Segoe UI", 8, "bold"),
            relief="raised", bd=1, highlightthickness=0, cursor="hand2")
        self.btn_stack_diagonal.place(x=245, y=22, width=78, height=21,
                                      bordermode="outside")

    def _stack_tight_cmd(self) -> bool:
        """C10 original callback, wired to the measured S59 button."""
        return self._dispatch_auto_stack("tight")

    def _stack_diagonal_cmd(self) -> bool:
        """C11 original callback, wired to the measured S59 button."""
        return self._dispatch_auto_stack("diagonal")

    def _dispatch_auto_stack(self, mode: str) -> bool:
        """S56: existing native C10/C11 engine, always off the Tk thread.

        Only source-backed HWND cache, externally granted max_windows and
        selected Start are accepted. Xếp-lưới's separate sync must be off;
        C07 Auto mode/tiler is still unavailable; S59 adds only stack buttons.
        """
        if (mode not in ("tight", "diagonal") or self._closed
                or not self.poller.active or not self.layout_max_windows
                or self.layout_active):
            return False
        # A cancelled grid may still be inside SetWindowPos. Tk dispatch
        # must wait for its native worker to EXIT, not just its active flag.
        layout_thread = getattr(self, "_layout_thread", None)
        if layout_thread is not None and layout_thread.is_alive():
            return False
        try:
            if not self.container.winfo_viewable():
                return False
            snapshot = self.poller.producer.read_snapshot()
        except Exception:
            return False
        if (not isinstance(snapshot, WindowSnapshot) or not snapshot.valid
                or not snapshot.windows
                or len(snapshot.windows) > self.layout_max_windows):
            return False
        previous = getattr(self, "_stack_thread", None)
        if previous is not None and previous.is_alive():
            return False
        self._cancel_stack_worker()
        event = threading.Event()
        event.set()
        self._stack_allow = event
        generation = self._stack_generation
        factory = self._stack_service_factory
        max_windows = self.layout_max_windows
        master_hwnd = self.layout_master_hwnd

        def worker() -> None:
            try:
                outcome = factory().apply(
                    snapshot, mode=mode, max_windows=max_windows,
                    master_hwnd=master_hwnd, allowed=event.is_set)
            except Exception:
                outcome = StackResult("STACK_WORKER_ERROR")
            # Data publication only; no Tk calls from this native worker.
            if (event.is_set() and self._stack_generation == generation
                    and not self._closed and self.poller.active
                    and self.layout_max_windows > 0):
                self._stack_last_result = outcome

        thread = threading.Thread(target=worker,
                                  name="TLM-Start-C10-C11-Stack-Worker",
                                  daemon=True)
        self._stack_thread = thread
        try:
            thread.start()
        except (RuntimeError, OSError):
            self._cancel_stack_worker()
            self._stack_thread = None
            return False
        return True

    def _stop_sync_loop(self) -> None:
        self._layout_allow.clear()
        self.layout_active = False
        self.sync_layout_running = False
        self.sync_loop_id += 1  # invalidate stale worker's status publication
        if not self._closed:
            self.btn_layout.configure(background="#f44336")

    def _toggle_layout(self) -> bool:
        """C18 real toggle: no fake status or client-side permission grants."""
        if self.layout_active:
            self._stop_sync_loop()
            self.layout_status.configure(text="Đồng bộ bố cục: tắt")
            return False
        stack_thread = getattr(self, "_stack_thread", None)
        if stack_thread is not None and stack_thread.is_alive():
            return False
        if self._closed or not self.poller.active or not self.layout_max_windows:
            return False
        if not self.container.winfo_viewable():
            return False
        try:
            snap = self.poller.producer.read_snapshot()
        except Exception:
            return False
        if not isinstance(snap, WindowSnapshot) or not snap.valid or not snap.windows:
            self.layout_status.configure(text="Chưa có cache cửa sổ hợp lệ")
            return False
        if len(snap.windows) > self.layout_max_windows:
            self.layout_status.configure(text="Vượt giới hạn cửa sổ đã xác minh")
            return False
        if len(snap.windows) > self.grid_cols * self.grid_rows:
            self.layout_status.configure(text="Vượt số ô lưới")
            return False
        self.layout_active = True
        self.sync_layout_running = True
        # Fresh cancellation event per session: never revive an old worker.
        self._layout_allow = threading.Event()
        self._layout_allow.set()
        self.btn_layout.configure(background="#388e3c")
        self.layout_status.configure(text="Đồng bộ vị trí: đang kiểm tra")
        self._layout_worker(snap)
        return True

    def _layout_worker(self, snapshot: WindowSnapshot) -> None:
        """C18: non-Tk worker + S09 cache, no guessed C18 sleep/cadence."""
        if self._closed or not self.layout_active or not self._layout_allow.is_set():
            return
        if not isinstance(snapshot, WindowSnapshot) or not snapshot.valid:
            self._stop_sync_loop()
            self.layout_status.configure(text="Cache không hợp lệ: tự tắt")
            return
        if len(snapshot.windows) > self.layout_max_windows:
            self._stop_sync_loop()
            self.layout_status.configure(text="Vượt giới hạn: tự tắt")
            return
        if self._layout_thread is not None and self._layout_thread.is_alive():
            return
        generation = self.sync_loop_id
        allow = self._layout_allow
        factory = self._layout_service_factory
        limit = self.layout_max_windows
        cols, rows = self.grid_cols, self.grid_rows
        master = self.layout_master_hwnd

        def work() -> None:
            try:
                outcome = factory().arrange(
                    snapshot, max_windows=limit, cols=cols, rows=rows,
                    master_hwnd=master, allowed=allow.is_set)
            except Exception:
                from layout_windows import LayoutResult
                outcome = LayoutResult("LAYOUT_WORKER_ERROR")
            if allow.is_set() and self.sync_loop_id == generation:
                # Pure data publication; widgets only updated by Tk
                # _on_maintenance_tick callback, NEVER from worker.
                self._layout_last_result = outcome

        self._layout_thread = threading.Thread(
            target=work, name="TLM-Start-C18-Layout-Worker", daemon=True)
        self._layout_thread.start()

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
        self._cancel_stack_worker()
        self._stop_sync_loop()
        self.maintenance.stop()
        self.poller._stop_refresh()
        self._drop_previews()
        if self._closed:
            # E08: child <Destroy> may already have removed its Tk widgets.
            return
        self._sync_tiles(())
        # Do not show stale HWND/PID when Start is hidden/revoked.
        self._render(StartReadOnlyState("STOPPED", "Chưa quét cửa sổ game"))

    def _on_destroy(self, event) -> None:
        if event.widget is self.container:
            self.shutdown()

    def shutdown(self) -> None:
        if self._closed:
            return
        # During Tk <Destroy>, children (including btn_layout) can already
        # be gone: fence widget updates BEFORE disabling the layout worker.
        self._closed = True
        self._cancel_stack_worker()
        self._stop_sync_loop()
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
