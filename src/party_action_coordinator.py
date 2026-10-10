"""S92 G09: cancellable Party group *orchestration*, NOT game/team protocol.

Original-backed: global one-thread-per-cluster, per-cluster cancellation,
aggregate completion+once-only after-action/reset, independent single-cluster
workers and duplicate guard. Same-group global/single collision behavior is
UNKNOWN in original: this reconstruction deliberately rejects overlap.

There is NO default authorization issuer or action backend. Without both a
genuine external permission check and a verified team protocol executor all
start requests FAIL CLOSED. No Tk buttons are exposed. This module never
constructs RoleIDs/TeamIDs, memory reads, game packets, Win32 mouse input or
post-party Train/Phoban actions. Callbacks run on worker threads, NOT Tk.
"""
from __future__ import annotations

from dataclasses import dataclass
import threading
import time
from typing import Callable, Protocol


@dataclass(frozen=True)
class PartyJob:
    number: int
    members: tuple[str, ...]

    def __post_init__(self):
        if (type(self.number) is not int or self.number < 1
                or not isinstance(self.members, tuple)
                or any(type(n) is not str or not n.strip() for n in self.members)
                or len(self.members) != len(set(self.members))):
            raise ValueError("PartyJob requires real selected names and group number")


@dataclass(frozen=True)
class PartyRunStatus:
    global_state: str = "IDLE"
    active_groups: tuple[int, ...] = ()
    running_single: tuple[int, ...] = ()
    completed_global: int = 0
    post_calls: int = 0
    errors: tuple[int, ...] = ()


class PartyProtocol(Protocol):
    """Must be a separately verified G10 game team adapter, NOT supplied here."""
    def __call__(self, job: PartyJob, cancel: threading.Event) -> bool: ...


class PartyPermission(Protocol):
    """Must be backed by legitimate signed Info + live verified account limit."""
    def __call__(self, operation: str, count: int) -> bool: ...


class PartyRunCoordinator:
    """G09 thread/event lifecycle prerequisite, fail-closed if unwired.

    The exact original _run_lock critical section and global/single
    collision policy are not recoverable. This conservative implementation
    never double-targets the SAME cluster, and never sends a game command.
    """

    def __init__(
        self,
        *, execute: PartyProtocol | None = None,
        permission: PartyPermission | None = None,
        after_party: Callable[[], None] | None = None,
        on_change: Callable[[PartyRunStatus], None] | None = None,
    ):
        self._execute = execute
        self._permission = permission
        self._after_party = after_party
        self._on_change = on_change
        self._lock = threading.RLock()
        self._global_state = "IDLE"
        self._global_stop = threading.Event()
        self._global_thread: threading.Thread | None = None
        self._global_jobs: dict[int, tuple[threading.Thread, threading.Event]] = {}
        self._single_jobs: dict[int, tuple[threading.Thread, threading.Event]] = {}
        self._active_global: set[int] = set()
        self._completed_global = 0
        self._post_calls = 0
        self._errors: set[int] = set()
        self._closed = False

    def snapshot(self) -> PartyRunStatus:
        with self._lock:
            return PartyRunStatus(
                global_state=self._global_state,
                active_groups=tuple(sorted(self._active_global)),
                running_single=tuple(sorted(self._single_jobs)),
                completed_global=self._completed_global,
                post_calls=self._post_calls,
                errors=tuple(sorted(self._errors)),
            )

    def _notify(self) -> None:
        # G09 main-thread Tk handoff timing is UNKNOWN. A future UI adapter
        # must marshal this callback onto its Tk owner thread.
        if self._on_change is not None:
            try:
                self._on_change(self.snapshot())
            except Exception:
                pass

    def _ready(self, operation: str, size: int) -> str:
        if self._execute is None or not callable(self._execute):
            return "TEAM_PROTOCOL_UNAVAILABLE"
        if self._permission is None or not callable(self._permission):
            return "SIGNED_PERMISSION_UNAVAILABLE"
        try:
            # Equality with bool identity, not truthiness or sample license.
            if self._permission(operation, size) is not True:
                return "PERMISSION_DENIED"
        except Exception:
            return "PERMISSION_ERROR"
        return "OK"

    def start_global(self, jobs: tuple[PartyJob, ...]) -> str:
        if not isinstance(jobs, tuple) or any(type(j) is not PartyJob for j in jobs):
            return "INVALID_JOBS"
        jobs = tuple(j for j in jobs if j.members)
        if not jobs:
            return "NO_GROUPS_SELECTED"  # G09 original
        nums = [j.number for j in jobs]
        if len(set(nums)) != len(nums):
            return "DUPLICATE_GROUP"
        with self._lock:
            if self._closed:
                return "CLOSED"
            if self._global_state != "IDLE":
                return "ALREADY_RUNNING"
            if set(nums) & self._single_jobs.keys():
                # Exact original collision rule UNKNOWN: fail closed.
                return "SAME_GROUP_COLLISION_BLOCKED"
            permission = self._ready("party", sum(len(j.members) for j in jobs))
            if permission != "OK":
                return permission
            self._global_stop = threading.Event()
            self._global_state = "RUNNING"
            self._active_global = set(nums)
            self._errors.clear()
            worker = threading.Thread(
                target=self._run_global, args=(jobs, self._global_stop),
                name="TLM-Party-G09-Global", daemon=True)
            self._global_thread = worker
            try:
                worker.start()
            except RuntimeError:
                self._global_state = "IDLE"
                self._active_global.clear()
                self._global_thread = None
                return "THREAD_START_FAILED"
        self._notify()
        return "STARTED"

    def _run_job(self, job: PartyJob, cancelled: threading.Event) -> bool:
        try:
            if cancelled.is_set():
                return False
            return self._execute(job, cancelled) is True
        except Exception:
            return False

    def _run_global(self, jobs: tuple[PartyJob, ...], stop: threading.Event) -> None:
        children = []
        try:
            for job in jobs:
                evt = threading.Event()
                def run_child(j=job, c=evt):
                    ok = self._run_job(j, c)
                    with self._lock:
                        if not ok and not c.is_set():
                            self._errors.add(j.number)
                        self._active_global.discard(j.number)
                    self._notify()
                thread = threading.Thread(
                    target=run_child, daemon=True,
                    name=f"TLM-Party-G09-Group-{job.number}")
                with self._lock:
                    if stop.is_set():
                        evt.set()
                    self._global_jobs[job.number] = (thread, evt)
                try:
                    thread.start()
                except RuntimeError:
                    with self._lock:
                        self._errors.add(job.number)
                        self._active_global.discard(job.number)
                    evt.set()
                else:
                    children.append(thread)
            for thread in children:
                thread.join()
            # G09: after_party once, AFTER all worker threads finish.
            # Post action is explicitly injected; do not invent dispatch.
            with self._lock:
                should_post = not stop.is_set() and self._after_party is not None
            if should_post:
                try:
                    self._after_party()
                except Exception:
                    pass
                with self._lock:
                    self._post_calls += 1
        finally:
            with self._lock:
                self._global_jobs.clear()
                self._active_global.clear()
                self._global_state = "IDLE"
                self._completed_global += 1
                self._global_thread = None
            self._notify()

    def stop_global(self) -> str:
        with self._lock:
            if self._global_state == "IDLE":
                return "NOT_RUNNING"
            if self._global_state == "STOPPING":
                return "ALREADY_STOPPING"
            self._global_state = "STOPPING"
            self._global_stop.set()
            for _thread, cancel in self._global_jobs.values():
                cancel.set()
        self._notify()
        return "STOPPING"

    def start_single(self, job: PartyJob) -> str:
        if type(job) is not PartyJob:
            return "INVALID_JOB"
        if len(job.members) < 2:
            return "AT_LEAST_TWO_MEMBERS"  # G09 original
        with self._lock:
            if self._closed:
                return "CLOSED"
            if job.number in self._single_jobs:
                return "ALREADY_RUNNING"
            if job.number in self._active_global:
                return "SAME_GROUP_COLLISION_BLOCKED"
            permission = self._ready("party", len(job.members))
            if permission != "OK":
                return permission
            cancel = threading.Event()
            thread = threading.Thread(
                target=self._run_single, args=(job, cancel),
                name=f"TLM-Party-G09-Single-{job.number}", daemon=True)
            self._single_jobs[job.number] = (thread, cancel)
            try:
                thread.start()
            except RuntimeError:
                self._single_jobs.pop(job.number, None)
                return "THREAD_START_FAILED"
        self._notify()
        return "STARTED"

    def _run_single(self, job: PartyJob, cancel: threading.Event) -> None:
        try:
            self._run_job(job, cancel)
        finally:
            with self._lock:
                # Remove only SAME worker generation; a later group may
                # use this number after the current worker has finished.
                pair = self._single_jobs.get(job.number)
                if pair is not None and pair[1] is cancel:
                    self._single_jobs.pop(job.number, None)
            self._notify()

    def stop_single(self, number: int) -> str:
        with self._lock:
            pair = self._single_jobs.get(number)
            if pair is None:
                return "NOT_RUNNING"
            pair[1].set()
        return "STOPPING"

    def close(self) -> None:
        with self._lock:
            self._closed = True
            self._global_stop.set()
            self._global_state = "STOPPING" if self._global_state != "IDLE" else "IDLE"
            for _, cancel in (*self._global_jobs.values(), *self._single_jobs.values()):
                cancel.set()
        self._notify()

    def wait_idle(self, timeout: float = 5.0) -> bool:
        """Only for callers/test owners outside Tk; never block Tk callbacks."""
        if timeout < 0:
            raise ValueError("Invalid wait timeout")
        deadline = time.monotonic() + timeout
        while time.monotonic() <= deadline:
            with self._lock:
                idle = self._global_state == "IDLE" and not self._single_jobs
                threads = ([self._global_thread] if self._global_thread is not None else []) + [
                    t for t, _ in self._single_jobs.values()]
            if idle:
                return True
            if any(thread is threading.current_thread() for thread in threads):
                return False
            time.sleep(min(.005, max(0.0, deadline-time.monotonic())))
        return self.snapshot().global_state == "IDLE" and not self.snapshot().running_single
