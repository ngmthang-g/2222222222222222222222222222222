"""S10: smallest real, read-only Tk Start window-list slice.

Only S08 Win32-observed HWND/PID/title snapshots delivered by S09's worker
are displayed. No DWM preview, game command, character-memory read, master
selection, mouse binding, layout buttons or entitlement is reconstructed here.
The shell must grant the Start tab from a separately verified server snapshot.
"""
from __future__ import annotations

from dataclasses import dataclass

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
                 interval_ms: int = START_UI_POLL_MS):
        from tkinter import ttk
        self.parent = parent
        self.container = ttk.Frame(parent)
        self.container.pack(fill="both", expand=True)
        self._closed = False
        self._state = StartReadOnlyState("STOPPED", "Chưa quét cửa sổ game")
        self.status = ttk.Label(self.container, text=self._state.caption, anchor="w")
        self.status.pack(fill="x", padx=10, pady=(10, 5))
        self.group = ttk.LabelFrame(self.container, text="Danh sách cửa sổ game (chỉ xem)")
        self.group.pack(fill="both", expand=True, padx=9, pady=(0, 9))
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

    def _start_refresh(self) -> None:
        if self._closed or self.poller.active:
            return
        self._render(StartReadOnlyState("PENDING", "Đang kiểm tra cửa sổ game..."))
        self.poller._start_refresh()

    def _stop_refresh(self) -> None:
        self.poller._stop_refresh()
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
        self.poller.shutdown()
