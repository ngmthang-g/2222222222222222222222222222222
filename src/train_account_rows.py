"""S123 H12: passive Train account-row lifecycle from real Start HWND/PID cache.

Original: rows keyed HWND + bound PID, incremental 5000ms refresh,
Tk-main-thread UI apply, keep Sell/Train preset selections on same identity,
destroy/replace on recycled HWND/PID, fail-preserve on transient read error.

This does NOT pretend to be the full FarmTab: actual RoleName/MapID/bag,
Farm/play controls, account-config character keys and game movement require
separate verified runtime/Info evidence. Only source-backed read-only HWND
identity and existing H11 name-choice widgets are represented.
"""
from __future__ import annotations

from dataclasses import dataclass
from tkinter import ttk
from typing import Callable

from start_polling import StartWindowProducer, WindowSnapshot
from start_windows import GameWindow
from farm_saved_editor import FarmSavedCoordinatesEditor
from train_row_permission import TrainRowPermissionGate
from train_character_samples import (
    TrainCharacterSampler, TrainCharacterSample, validated_sample,
)
from train_extra_tracking import TrainSessionTracker

TRAIN_ACCOUNT_REFRESH_MS = 5000


@dataclass(frozen=True)
class AccountRowChange:
    added: tuple[GameWindow, ...] = ()
    removed: tuple[GameWindow, ...] = ()
    reused: tuple[tuple[GameWindow, GameWindow], ...] = ()
    retained: tuple[GameWindow, ...] = ()
    unknown: bool = False


class TrainAccountRegistry:
    """No real Tk widgets here. Snapshot must come from trusted S09 source."""

    def __init__(self):
        self._by_hwnd: dict[int, GameWindow] = {}

    @property
    def rows(self) -> tuple[GameWindow, ...]:
        return tuple(self._by_hwnd.values())

    def clear(self) -> tuple[GameWindow, ...]:
        old = self.rows
        self._by_hwnd.clear()
        return old

    def reconcile(self, snapshot: WindowSnapshot) -> AccountRowChange:
        if not isinstance(snapshot, WindowSnapshot):
            raise ValueError("INVALID_OR_UNVERIFIED_WINDOW_SNAPSHOT")
        if not snapshot.valid:
            # H12 transient-read failure: do not destroy an otherwise live row.
            return AccountRowChange(unknown=True)
        new: dict[int, GameWindow] = {}
        for window in snapshot.windows:
            if (not isinstance(window, GameWindow)
                or type(window.hwnd) is not int or window.hwnd <= 0
                or type(window.pid) is not int or window.pid <= 0
                or not isinstance(window.title, str)):
                raise ValueError("INVALID_ACCOUNT_WINDOW_IDENTITY")
            if window.hwnd in new:
                raise ValueError("AMBIGUOUS_ACCOUNT_HWND")
            new[window.hwnd] = window
        old = self._by_hwnd
        removed = tuple(x for hwnd, x in old.items() if hwnd not in new)
        replaced = tuple((old[hwnd], w) for hwnd, w in new.items()
                         if hwnd in old and old[hwnd].pid != w.pid)
        added = tuple(w for hwnd, w in new.items() if hwnd not in old)
        kept = tuple(w for hwnd, w in new.items()
                     if hwnd in old and old[hwnd].pid == w.pid)
        self._by_hwnd = new
        return AccountRowChange(added, removed, replaced, kept)


class TkTrainAccountRows:
    """Small *passive* Tk account-row owner, not complete original FarmTab.

    No account HWND is synthesized. Default source is the real verified S09
    Win32 background producer. All Tk construction and changes occur only in
    this controller's owner thread via root.after, not in the S09 worker.
    No local permission grant: missing farm entitlement leaves combos disabled.
    """

    def __init__(self, parent, coordinate_editor: FarmSavedCoordinatesEditor,
                 *, producer: StartWindowProducer | None = None,
                 allow_account: Callable[[GameWindow], bool] | None = None,
                 interval_ms: int = TRAIN_ACCOUNT_REFRESH_MS,
                 permission_guard=None, running_count=None,
                 identity_backend_factory=None,
                 character_reader=None):
        if not isinstance(coordinate_editor, FarmSavedCoordinatesEditor):
            raise ValueError("REAL_H11_COORDINATE_EDITOR_REQUIRED")
        if interval_ms != TRAIN_ACCOUNT_REFRESH_MS:
            raise ValueError("ORIGINAL_TRAIN_REFRESH_5000MS_REQUIRED")
        self.parent = parent
        self.editor = coordinate_editor
        self.producer = producer if producer is not None else StartWindowProducer()
        self._own_producer = producer is None
        # The callback is an additional restriction only, NEVER a grant.
        self._allow_account = allow_account
        self._permission_gate = TrainRowPermissionGate(
            permission_guard, running_count, identity_backend_factory)
        # NO native reader supplied => no game memory sampling in product.
        self.character_sampler = TrainCharacterSampler(character_reader)
        self.registry = TrainAccountRegistry()
        self._rows: dict[int, dict] = {}
        self._active = False
        self._closed = False
        self._epoch = 0
        self._after_id = None
        self._revision = None
        self.container = ttk.Frame(parent)
        self.container.pack(fill="x")
        self.status = ttk.Label(self.container, text="Train: chưa quét cửa sổ")
        self.status.pack(fill="x")
        self.body = ttk.Frame(self.container)
        self.body.pack(fill="x")
        self.container.bind("<Destroy>", self._on_destroy, add="+")

    def _allowed(self, window: GameWindow) -> bool:
        try:
            return (self._permission_gate.permitted(window)
                    and (bool(self._allow_account(window))
                         if callable(self._allow_account) else False))
        except Exception:
            return False

    def _create(self, window: GameWindow) -> None:
        row = ttk.Frame(self.body)
        row.pack(fill="x")
        # Real verified HWND+PID, NOT a guessed RoleName/character name.
        label = ttk.Label(row, text=f"HWND {window.hwnd} / PID {window.pid}")
        label.pack(side="left")
        sell = ttk.Combobox(row, state="disabled", width=13)
        farm = ttk.Combobox(row, state="disabled", width=13)
        sell.pack(side="left")
        farm.pack(side="left")
        # These are UNKNOWN until verified read-only background samples exist.
        label_map = ttk.Label(row, text="MapID: ?")
        label_bag = ttk.Label(row, text="Túi: ?")
        label_map.pack(side="left")
        label_bag.pack(side="left")
        tracker = TrainSessionTracker()
        # H12: original third-line status is passive until genuine Farm starts.
        extra = ttk.Label(row, text=tracker.text())
        extra.pack(side="bottom", anchor="w")
        try:
            self.editor.register_account_combos(sell, farm)
        except Exception:
            row.destroy()
            raise
        self._rows[window.hwnd] = {
            "pid": window.pid, "frame": row,
            "label": label, "sell": sell, "farm": farm,
            "label_map": label_map, "label_bag": label_bag,
            "label_extra": extra, "tracker": tracker,
        }
        self._set_row_permission(window)

    def _set_row_permission(self, window: GameWindow) -> None:
        row = self._rows.get(window.hwnd)
        if row is None or row["pid"] != window.pid:
            return
        state = "readonly" if self._allowed(window) and not self.editor._blocked else "disabled"
        row["sell"].configure(state=state)
        row["farm"].configure(state=state)
        if state == "disabled":
            # Do not retain a formerly authorized character's details after
            # Info revocation. Unknown remains '?', not a fabricated zero.
            row["label"].configure(
                text=f"HWND {window.hwnd} / PID {window.pid}")
            row["label_map"].configure(text="MapID: ?")
            row["label_bag"].configure(text="Túi: ?")
            row["tracker"].stop()
            row["label_extra"].configure(text=row["tracker"].text())
            # Revoked authority can never release an in-flight mailbox.
            self.character_sampler.invalidate()
        self.editor._sync_apply_buttons()

    def reapply_permissions(self) -> None:
        """H12 heartbeat: recheck existing HWND/PID/Info even if cache unchanged."""
        if self._closed:
            return
        for window in self.registry.rows:
            self._set_row_permission(window)

    def start_confirmed_tracking(self, hwnd: int, pid: int) -> bool:
        """Only a FUTURE authenticated Farm engine may announce actual start.

        This does not move/attack/start Farm in game, and does not start merely
        because a matching window is present. No Game session engine is wired.
        """
        if self._closed or type(hwnd) is not int or type(pid) is not int:
            return False
        row = self._rows.get(hwnd)
        window = next((w for w in self.registry.rows
                       if w.hwnd == hwnd and w.pid == pid), None)
        if (row is None or row["pid"] != pid or window is None
                or not self._allowed(window)):
            return False
        row["tracker"].start_confirmed_session()
        row["label_extra"].configure(text=row["tracker"].text())
        return True

    def stop_tracking(self, hwnd: int, pid: int) -> bool:
        """Only lifecycle stop, not a command sent to a game."""
        row = self._rows.get(hwnd)
        if row is None or row["pid"] != pid:
            return False
        row["tracker"].stop()
        row["label_extra"].configure(text=row["tracker"].text())
        return True

    def record_confirmed_death(self, hwnd: int, pid: int) -> bool:
        """H07 HP-zero latched event hook; no reader/click is simulated."""
        row = self._rows.get(hwnd)
        window = next((w for w in self.registry.rows
                       if w.hwnd == hwnd and w.pid == pid), None)
        if (row is None or row["pid"] != pid or window is None
                or not self._allowed(window)
                or not row["tracker"].record_confirmed_death()):
            return False
        row["label_extra"].configure(text=row["tracker"].text())
        return True

    def refresh_session_labels(self) -> None:
        """Tk-owner time display only; does not read native game memory."""
        for window in self.registry.rows:
            row = self._rows.get(window.hwnd)
            if (row is not None and row["pid"] == window.pid
                    and self._allowed(window)):
                row["label_extra"].configure(text=row["tracker"].text())

    def apply_character_samples(self, samples) -> int:
        """Apply only samples for currently authorized, same HWND/PID rows.

        Runs on the caller's Tk thread. A failed/partial sample leaves the
        previous known value untouched; retired HWND/PID never receives data.
        """
        if self._closed or not isinstance(samples, (tuple, list)):
            return 0
        updated = 0
        for sample in samples:
            if type(sample) is not TrainCharacterSample:
                continue
            row = self._rows.get(sample.hwnd)
            if row is None or row["pid"] != sample.pid:
                continue
            window = next((w for w in self.registry.rows
                           if w.hwnd == sample.hwnd and w.pid == sample.pid), None)
            if window is None or not self._allowed(window):
                continue
            try:
                sample = validated_sample(sample, window)
            except ValueError:
                continue
            if sample.role_name is not None:
                row["label"].configure(text=sample.role_name)
            if sample.map_id is not None:
                row["label_map"].configure(text=f"MapID: {sample.map_id}")
            if sample.bag_slots is not None:
                row["label_bag"].configure(text=f"Túi: {sample.bag_slots}")
            row["tracker"].accept(sample)
            row["label_extra"].configure(text=row["tracker"].text())
            updated += 1
        return updated

    def _remove(self, hwnd: int) -> None:
        row = self._rows.pop(hwnd, None)
        if row is None:
            return
        self.editor.unregister_account_combos(row["sell"], row["farm"])
        row["frame"].destroy()

    def apply_snapshot(self, snapshot: WindowSnapshot) -> bool:
        """Tk owner thread only; true valid-empty snapshot removes closed rows."""
        if self._closed or not isinstance(snapshot, WindowSnapshot):
            return False
        if self.editor._blocked or self.editor._closed:
            # Refuse misleading partially-registered account choices.
            self.status.configure(text="Train: chưa xác minh cấu hình tọa độ")
            return False
        try:
            change = self.registry.reconcile(snapshot)
        except ValueError:
            self.status.configure(text="Train: dữ liệu cửa sổ không hợp lệ")
            return False
        if change.unknown:
            self.status.configure(text="Train: lỗi đọc tạm thời, giữ dòng trước")
            return False
        if change.removed or change.reused:
            self.character_sampler.invalidate()
        for window in change.removed:
            self._remove(window.hwnd)
        for old, new in change.reused:
            self._remove(old.hwnd)
        for window in change.added + tuple(new for _, new in change.reused):
            self._create(window)
        for window in change.retained:
            self._set_row_permission(window)
        self.status.configure(text=f"Train: {len(self._rows)} cửa sổ có HWND/PID")
        return True

    def _tick(self, epoch: int) -> None:
        if self._closed or not self._active or epoch != self._epoch:
            return
        self._after_id = None
        if self._own_producer and not self.producer.active:
            self.producer.start()
        snapshot = self.producer.read_snapshot()
        if snapshot.revision != self._revision:
            self._revision = snapshot.revision
            self.apply_snapshot(snapshot)
        # Info heartbeat revocations need not change the Start window cache.
        self.reapply_permissions()
        # Both functions below only touch Tk here, never from the worker.
        self.apply_character_samples(self.character_sampler.drain())
        self.refresh_session_labels()
        eligible = tuple(w for w in self.registry.rows if self._allowed(w))
        if eligible:
            self.character_sampler.request(eligible)
        else:
            self.character_sampler.invalidate()
        if self._active and epoch == self._epoch:
            self._schedule(TRAIN_ACCOUNT_REFRESH_MS, epoch)

    def _schedule(self, delay: int, epoch: int) -> None:
        if not self._active or self._closed or epoch != self._epoch:
            return
        try:
            self._after_id = self.container.after(delay, lambda: self._tick(epoch))
        except Exception:
            self._stop_refresh()

    def _start_refresh(self) -> None:
        if self._closed or self._active:
            return
        self._active = True
        self._epoch += 1
        self._revision = None
        if self._own_producer:
            self.producer.start()
        self._schedule(0, self._epoch)

    def _stop_refresh(self) -> None:
        # Shutdown also owns teardown of rows applied before refresh start.
        # A real Tk owner must never leave dangling S122 account bindings.
        was_active = self._active
        self._active = False
        self._epoch += 1
        handle, self._after_id = self._after_id, None
        if handle is not None:
            try:
                self.container.after_cancel(handle)
            except Exception:
                pass
        for hwnd in tuple(self._rows):
            self._remove(hwnd)
        self.registry.clear()
        self.character_sampler.invalidate()
        self._revision = None
        if self._own_producer and was_active:
            self.producer.stop()

    def shutdown(self) -> None:
        if self._closed:
            return
        self._stop_refresh()
        self.character_sampler.shutdown()
        self._closed = True

    def _on_destroy(self, event) -> None:
        if event.widget is self.container:
            self.shutdown()
