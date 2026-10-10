"""S93 / G09: read-only Tk-owner Party status display, NOT action controls.

Original G09 visible texts: Bắt đầu, Dừng lại, Đang dừng...,
▶ Tạo nhóm N, ⏳ Đang vào...; running red #f44336, stopping orange
#ef6c00. Exact idle BTN_GREEN_PARTY RGB is UNKNOWN; leave native
Tk theme foreground rather than inventing a green value.

S92 PartyRunCoordinator calls on_change from worker threads. This adapter
NEVER invokes Tk from that callback: only writes to a thread-safe queue,
then the Tk owner drains on its own after() clock. Every UI update obtains
a FRESH coordinator.snapshot(), so delayed/old worker notifications cannot
restore stale progress after STOP or window destruction.

Production lacks actual G10 executor and signed Info. All widgets here are
READ-ONLY status labels; no fake ▶ Tạo nhóm / Bắt đầu clickable buttons,
no fabricated permission, role name, RoleID/TeamID or game operations.
Injected callbacks, if supplied, are still explicitly diagnostic, not
proof of a live game or signed Info.
"""
from __future__ import annotations

from dataclasses import dataclass
from queue import Empty, SimpleQueue
import threading
from tkinter import ttk
from typing import Callable

from party_action_coordinator import PartyJob, PartyRunCoordinator, PartyRunStatus

S93_TK_DRAIN_MS = 50  # safe local timer, NOT a verified original after() delay
RUNNING_COLOR = "#f44336"  # G09 exact
STOPPING_COLOR = "#ef6c00"  # G09 exact
UNVERIFIED_IDLE_COLOR = None  # BTN_GREEN_PARTY exact original RGB unknown


@dataclass(frozen=True)
class PartyDisplay:
    code: str
    global_text: str
    global_color: str | None
    groups: tuple[tuple[int, str], ...]


def render_party_state(
    status: PartyRunStatus, groups: tuple[int, ...],
    *, backend_diagnostic: bool = False, closed: bool = False,
) -> PartyDisplay:
    """Pure UI state mapping; never pretends that diagnostics are authorized."""
    if not isinstance(status, PartyRunStatus):
        raise ValueError("G09 PartyRunStatus required")
    if (not isinstance(groups, tuple)
            or any(type(n) is not int or n <= 0 for n in groups)
            or len(set(groups)) != len(groups)):
        raise ValueError("Distinct numbered Party groups required")
    if closed:
        return PartyDisplay("CLOSED", "Party đã đóng", None, ())
    if not backend_diagnostic:
        return PartyDisplay(
            "UNAVAILABLE", "Party không khả dụng: thiếu backend đội hoặc xác thực Info",
            None, tuple((n, "Không khả dụng") for n in groups))
    if status.global_state == "RUNNING":
        text, color = "Dừng lại", RUNNING_COLOR
    elif status.global_state == "STOPPING":
        text, color = "Đang dừng...", STOPPING_COLOR
    elif status.global_state == "IDLE":
        text, color = "Bắt đầu", UNVERIFIED_IDLE_COLOR
    else:
        return PartyDisplay("UNKNOWN_STATE", "Trạng thái Party không xác định",
                            None, ())
    active = set(status.active_groups) | set(status.running_single)
    return PartyDisplay(
        status.global_state, text, color,
        tuple((n, f"⏳ Đang vào... ({n})" if n in active
               else f"▶ Tạo nhóm {n} (chỉ xem)") for n in groups))


class TkPartyRunStatus(ttk.Frame):
    """READ-ONLY, testable G09 Tk status bridge; no game command UI."""

    def __init__(
        self, parent, *, groups: tuple[int, ...] = (),
        execute: Callable | None = None, permission: Callable | None = None,
        after_party: Callable[[], None] | None = None,
    ):
        self._owner = threading.get_ident()
        if (not isinstance(groups, tuple)
                or any(type(n) is not int or n <= 0 for n in groups)
                or len(set(groups)) != len(groups)):
            raise ValueError("Invalid G09 Party group numbers")
        super().__init__(parent)
        self._closed = False
        self._epoch = 1
        self._queue: SimpleQueue[int] = SimpleQueue()
        self._pending_after = None
        # Supplying test callbacks is NOT permission/auth in the product.
        # It enables visual diagnostics from actual injected worker events
        # only; there are STILL no real action buttons on this UI.
        self._diagnostic = callable(execute) and callable(permission)
        self._groups = groups
        self.coordinator = PartyRunCoordinator(
            execute=execute, permission=permission,
            after_party=after_party, on_change=self._worker_changed)
        self.heading = ttk.Label(
            self, text="Trạng thái Party (chẩn đoán — không điều khiển game)")
        self.heading.pack(anchor="w", padx=4, pady=2)
        self.summary = ttk.Label(self, text="", anchor="w")
        self.summary.pack(anchor="w", padx=4, pady=2)
        self.group_frame = ttk.Frame(self)
        self.group_frame.pack(fill="x", padx=4, pady=2)
        self.group_labels: dict[int, ttk.Label] = {}
        self.current = render_party_state(
            self.coordinator.snapshot(), groups,
            backend_diagnostic=self._diagnostic)
        self._apply(self.current)
        self.bind("<Destroy>", self._on_destroy, add="+")
        self._arm()

    def _check_owner(self):
        if threading.get_ident() != self._owner:
            raise RuntimeError("Tk Party widget can only be read/modified on Tk owner")

    def _worker_changed(self, _status: PartyRunStatus) -> None:
        # Called from background Party worker threads. NEVER root.after(),
        # .configure(), .winfo_exists(), StringVar.set() or any Tk API here.
        if not self._closed:
            self._queue.put(self._epoch)

    def _arm(self) -> None:
        self._check_owner()
        if not self._closed and self._pending_after is None:
            self._pending_after = self.after(
                S93_TK_DRAIN_MS, self._drain)

    def _apply(self, view: PartyDisplay) -> None:
        self._check_owner()
        self.current = view
        self.summary.configure(text=f"Trạng thái (chỉ xem): {view.global_text}")
        # Only source-proven running/stopping colors; do not guess BTN_GREEN.
        self.summary.configure(foreground=(
            view.global_color if view.global_color is not None else ""))
        target = dict(view.groups)
        for number, label in tuple(self.group_labels.items()):
            if number not in target:
                label.destroy()
                self.group_labels.pop(number, None)
        for number, value in view.groups:
            if number not in self.group_labels:
                label = ttk.Label(self.group_frame, text=value)
                label.pack(anchor="w", padx=2, pady=1)
                self.group_labels[number] = label
            else:
                self.group_labels[number].configure(text=value)

    def _drain(self) -> None:
        self._check_owner()
        self._pending_after = None
        if self._closed:
            return
        saw_event = False
        try:
            while True:
                event_epoch = self._queue.get_nowait()
                if event_epoch == self._epoch:
                    saw_event = True
        except Empty:
            pass
        if saw_event:
            # An EVENT is only a wake-up. The authoritative current state
            # is the FRESH locked S92 snapshot, not an old queued event.
            view = render_party_state(
                self.coordinator.snapshot(), self._groups,
                backend_diagnostic=self._diagnostic)
            if view != self.current:
                self._apply(view)
        self._arm()

    def set_groups(self, groups: tuple[int, ...]) -> None:
        self._check_owner()
        if self._closed:
            return
        view = render_party_state(
            self.coordinator.snapshot(), groups,
            backend_diagnostic=self._diagnostic)
        self._groups = groups
        self._apply(view)

    def shutdown(self) -> None:
        self._check_owner()
        if self._closed:
            return
        self._closed = True
        self._epoch += 1
        self.coordinator.close()  # signals cancel, does NOT wait/block Tk
        if self._pending_after is not None:
            self.after_cancel(self._pending_after)
            self._pending_after = None
        # Discard pending old events; future worker events are ignored.
        try:
            while True:
                self._queue.get_nowait()
        except Empty:
            pass
        self._apply(render_party_state(
            self.coordinator.snapshot(), (), closed=True))

    def _on_destroy(self, event) -> None:
        if event.widget is self:
            self.shutdown()
