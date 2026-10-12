"""S172 TrainLSV passive account/window list from the EXISTING S09 cache.

Original I01: shared StartTab window list, 5-second incremental Tk refresh,
PID-aware add/remove; real RoleName/MapID unavailable without a verified
native character reader, so never infer names or save acc_<name>_train.
No second Win32 enumerator, license service, command/input or game write.
"""
from __future__ import annotations

import threading
from tkinter import ttk
from typing import Callable

from start_polling import StartWindowProducer, WindowSnapshot
from start_windows import GameWindow, NativeWin32Backend, is_game_candidate
from train_account_rows import TrainAccountRegistry

LSV_ACCOUNT_REFRESH_MS = 5000


class TkTrainLsvPassiveAccounts(ttk.LabelFrame):
    def __init__(self, parent, *, producer: StartWindowProducer,
                 backend_factory: Callable = NativeWin32Backend):
        if not isinstance(producer, StartWindowProducer):
            raise ValueError("REQUIRES_EXISTING_SHARED_S09_PRODUCER")
        super().__init__(parent, text="Danh sách nhân vật Train LSV (chỉ đọc)")
        self.producer = producer
        self.backend_factory = backend_factory
        self.registry = TrainAccountRegistry()
        self.rows: dict[int, dict] = {}
        self.owner_thread = threading.get_ident()
        self._active = False
        self._closed = False
        self._owns_producer = False
        self._generation = 0
        self._after_id = None
        self._last_revision = None
        self.status = ttk.Label(
            self, text="Chưa quét cửa sổ game; tên nhân vật chưa xác minh")
        self.status.pack(anchor="w", padx=6, pady=3)
        header = ttk.Frame(self)
        header.pack(fill="x", padx=6)
        ttk.Label(header, text="Nhân vật / HWND + PID", width=39).pack(side="left")
        ttk.Label(header, text="Tọa độ Train", width=20).pack(side="left")
        self.body = ttk.Frame(self)
        self.body.pack(fill="x", padx=6, pady=(1, 4))
        self.bind("<Destroy>", self._on_destroy, add="+")

    def _check_owner(self):
        if threading.get_ident() != self.owner_thread:
            raise RuntimeError("LSV_TK_OWNER_THREAD_REQUIRED")

    def _valid_window(self, w: GameWindow, backend) -> bool:
        if (type(w) is not GameWindow
                or type(w.hwnd) is not int or w.hwnd <= 0
                or type(w.pid) is not int or w.pid <= 0
                or not is_game_candidate(w.process_name, w.class_name, w.title)):
            return False
        try:
            return bool(backend.is_window(w.hwnd) and
                        backend.is_visible(w.hwnd) and
                        backend.process_id(w.hwnd) == w.pid)
        except (OSError, RuntimeError, ValueError, TypeError):
            return False

    def apply_snapshot(self, snapshot: WindowSnapshot) -> bool:
        """Tk only. Invalid/error cache retains known rows; no fabricated zero.

        A valid S09 snapshot is still revalidated against current Win32
        HWND/PID to avoid stale recycled targets. Duplicate HWNDs fail closed.
        """
        self._check_owner()
        if self._closed or not self._active or type(snapshot) is not WindowSnapshot:
            return False
        if not snapshot.valid:
            self.status.configure(text="Không xác nhận được quét cửa sổ — giữ trạng thái cũ")
            return False
        try:
            backend = self.backend_factory()
            known = []
            seen = set()
            for w in snapshot.windows:
                if type(w) is not GameWindow or w.hwnd in seen:
                    raise ValueError("INVALID_OR_DUPLICATE_WINDOW_IDENTITY")
                seen.add(w.hwnd)
                if self._valid_window(w, backend):
                    known.append(w)
        except (OSError, RuntimeError, ValueError, TypeError):
            self.status.configure(text="Lỗi kiểm tra danh tính cửa sổ — chưa cập nhật")
            return False
        # S123 reconciler preserves HWND+PID and reports recycled HWNDs.
        delta = self.registry.reconcile(WindowSnapshot(
            revision=snapshot.revision, windows=tuple(known),
            valid=True, captured_at=snapshot.captured_at))
        for w in delta.removed:
            self._drop(w.hwnd)
        for old, _ in delta.reused:
            self._drop(old.hwnd)
        for w in delta.added:
            self._new(w)
        for _, w in delta.reused:
            self._new(w)
        self.status.configure(text=(
            f"Cửa sổ game xác minh: {len(known)}. "
            "RoleName / vị trí Train: chưa có nguồn dữ liệu an toàn."))
        self._last_revision = snapshot.revision
        return True

    def _new(self, w: GameWindow):
        line = ttk.Frame(self.body)
        line.pack(fill="x", pady=1)
        # PID/HWND truthful. Do NOT guess original RoleName from window title.
        label = ttk.Label(line,
            text=f"Nhân vật: ? (HWND {w.hwnd} / PID {w.pid})", width=39)
        label.pack(side="left")
        ttk.Label(line, text="Chưa gán — cần RoleName", width=24).pack(side="left")
        self.rows[w.hwnd] = {"pid":w.pid, "frame":line, "label":label}

    def _drop(self, hwnd: int):
        row = self.rows.pop(hwnd, None)
        if row is not None:
            row["frame"].destroy()

    def _clear(self):
        self.registry.clear()
        for hwnd in tuple(self.rows):
            self._drop(hwnd)
        self._last_revision = None

    def _schedule(self, ms: int, generation: int):
        if not self._closed and self._active and generation == self._generation:
            self._after_id = self.after(ms, lambda:self._tick(generation))

    def _tick(self, generation: int):
        self._after_id = None
        if self._closed or not self._active or generation != self._generation:
            return
        if not self.producer.active:
            # S09 refuses concurrent worker while previous epoch exits;
            # retry next fixed I01 5s tick rather than creating a clone.
            if self.producer.start():
                self._owns_producer = True
        snapshot = self.producer.read_snapshot()
        if snapshot.revision != self._last_revision or not snapshot.valid:
            self.apply_snapshot(snapshot)
        self._schedule(LSV_ACCOUNT_REFRESH_MS, generation)

    def _start_refresh(self):
        self._check_owner()
        if self._closed or self._active:
            return False
        self._active = True
        self._generation += 1
        if not self.producer.active:
            if self.producer.start():
                self._owns_producer = True
        self._schedule(0, self._generation)
        return True

    def _stop_refresh(self):
        self._check_owner()
        self._active = False
        self._generation += 1
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except (RuntimeError, ValueError):
                pass
            self._after_id = None
        self._clear()
        if self._owns_producer:
            self._owns_producer = False
            self.producer.stop()
        if not self._closed:
            self.status.configure(text="Danh sách Train LSV đã dừng cập nhật")

    def shutdown(self):
        if self._closed:
            return
        self._stop_refresh()
        self._closed = True

    def _on_destroy(self, event):
        if event.widget is self:
            self.shutdown()
