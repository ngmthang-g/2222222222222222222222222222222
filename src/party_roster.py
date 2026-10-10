"""S90 G02/G03: Party roster from EXISTING S09 Start HWND/PID snapshots.

Original Party consumes cached Start.get_windows and refreshes every 3000ms.
This component NEVER enumerates windows, reads game memory, guesses RoleName
from a window title, saves runtime IDs, or provides team actions.

RoleName is accepted only from an EXTERNAL, explicitly injected
(hwnd,pid) -> RoleReading reader, NOT supplied by this project. Test-only
readers do not make actual game RoleName available in the product.

The exact original first-tick and Tk worker-apply delay are UNKNOWN.
"""
from __future__ import annotations

from dataclasses import dataclass
from queue import Empty, Queue
import re
import threading
from typing import Callable

from auto_role_provenance import RoleReading
from start_polling import WindowSnapshot
from start_windows import GameWindow

PARTY_REFRESH_MS = 3000
# Implementation-only Tk queue drain; NOT a recovered original timing.
S90_UI_HANDOFF_MS = 100
_TAGS = re.compile(r"<[^>]+>")


@dataclass(frozen=True)
class PartyMember:
    hwnd: int
    pid: int
    role_name: str | None  # None -> no authoritative character reader yet


@dataclass(frozen=True)
class PartyRosterResult:
    code: str
    revision: int
    members: tuple[PartyMember, ...] = ()


def _valid_snapshot(snapshot: WindowSnapshot) -> bool:
    if not isinstance(snapshot, WindowSnapshot) or not snapshot.valid:
        return False
    seen = set()
    for window in snapshot.windows:
        if (not isinstance(window, GameWindow)
                or type(window.hwnd) is not int or window.hwnd <= 0
                or type(window.pid) is not int or window.pid <= 0
                or window.hwnd in seen):
            return False
        seen.add(window.hwnd)
    return True


def _identity_set(snapshot: WindowSnapshot) -> frozenset[tuple[int, int]]:
    return frozenset((x.hwnd, x.pid) for x in snapshot.windows)


def prepare_roster(
    snapshot: WindowSnapshot,
    read_role: Callable[[int, int], RoleReading] | None = None,
) -> PartyRosterResult:
    """Worker-only: build immutable Party model; NEVER invoke Tk/EnumWindows.

    Input is cached Start data. No role source -> retain physical identities
    only; an account may NOT be offered as a verified ready character.
    """
    if not _valid_snapshot(snapshot):
        return PartyRosterResult("INVALID_START_CACHE", getattr(snapshot, "revision", 0))
    members = []
    errors = False
    for window in snapshot.windows:
        name = None
        if read_role is not None:
            try:
                reading = read_role(window.hwnd, window.pid)
                if (isinstance(reading, RoleReading)
                        and type(reading.hwnd) is int and reading.hwnd == window.hwnd
                        and type(reading.pid) is int and reading.pid == window.pid
                        and isinstance(reading.role_name, str)):
                    cleaned = _TAGS.sub("", reading.role_name).strip()
                    if cleaned:
                        name = cleaned
                    else:
                        errors = True
                else:
                    errors = True
            except Exception:
                errors = True
        members.append(PartyMember(window.hwnd, window.pid, name))
    return PartyRosterResult(
        "ROLE_READ_PARTIAL" if errors else
        "ROLE_READER_UNAVAILABLE" if read_role is None else "ROLE_NAMES_READ",
        snapshot.revision, tuple(members))


class PartyRoster:
    """Tk-owner-thread-only state: stale/reused PID never inherits a name."""

    def __init__(self):
        self.members: tuple[PartyMember, ...] = ()
        self.code = "UNVERIFIED"
        self.revision = 0

    def clear(self, code: str = "STOPPED") -> None:
        self.members = ()
        self.code = code

    def apply(self, result: PartyRosterResult, latest: WindowSnapshot) -> bool:
        # Revalidate generation after the background RoleName read. An
        # old result for HWND=5/PID=10 cannot rename HWND=5/PID=11.
        if not _valid_snapshot(latest):
            self.clear("INVALID_START_CACHE")
            return False
        if not isinstance(result, PartyRosterResult):
            self.clear("INVALID_PARTY_RESULT")
            return False
        live = _identity_set(latest)
        observed = frozenset((m.hwnd, m.pid) for m in result.members)
        if (result.revision != latest.revision or observed != live
                or len(observed) != len(result.members)):
            # Never continue displaying a now-replaced former PID.
            self.members = ()
            self.code = "STALE_WORKER_RESULT"
            return False
        self.members = result.members
        self.revision = latest.revision
        self.code = result.code
        return True

    def ready_names(self, selected: tuple[str, ...] = ()) -> tuple[str, ...]:
        """G02 names only from live original-style RoleReading; selected hide.

        Ambiguous duplicate names are not offered to configuration because
        G03 uses names for saved data, separate from live RoleID identity.
        """
        used = set(selected)
        names = [m.role_name for m in self.members
                 if m.role_name is not None and m.role_name not in used]
        return tuple(name for name in dict.fromkeys(names)
                     if names.count(name) == 1)


class TkPartyRosterRefresh:
    """Party G02 3s Tk refresh reading SAME S09 Start producer cache.

    One bounded daemon worker per pass for potential external RoleName reads;
    worker NEVER accesses Tk. A Tk-owned 100ms queue poll applies responses,
    an implementation-safe handoff, not alleged original Tk-after delay.
    """

    def __init__(self, root, start_producer,
                 on_change: Callable[[PartyRoster], None], *,
                 read_role: Callable[[int, int], RoleReading] | None = None):
        self.root = root
        self.start_producer = start_producer
        self.on_change = on_change
        self.read_role = read_role
        self.roster = PartyRoster()
        self._generation = 0
        self._active = False
        self._closed = False
        self._refresh_job = None
        self._handoff_job = None
        self._working = False
        self._queue: Queue[tuple[int, PartyRosterResult]] = Queue()

    @property
    def active(self) -> bool:
        return self._active

    def start(self) -> None:
        if self._active or self._closed:
            return
        self._generation += 1
        self._active = True
        # G02 first original refresh time UNKNOWN: conservatively schedule
        # first work after the only confirmed Party cadence 3000ms.
        self._schedule_refresh(self._generation)

    def _schedule_refresh(self, generation: int) -> None:
        if self._active and generation == self._generation:
            self._refresh_job = self.root.after(
                PARTY_REFRESH_MS, lambda: self._refresh(generation))

    def _refresh(self, generation: int) -> None:
        if not self._active or generation != self._generation:
            return
        self._refresh_job = None
        snapshot = self.start_producer.read_snapshot()
        if not _valid_snapshot(snapshot):
            self.roster.clear("INVALID_START_CACHE")
            self.on_change(self.roster)
        elif not self._working:
            self._working = True
            thread = threading.Thread(
                target=self._read_worker,
                args=(generation, snapshot),
                daemon=True, name="TLM-Party-ReadOnly-Roster")
            try:
                thread.start()
            except RuntimeError:
                self._working = False
                self.roster.clear("WORKER_START_FAILED")
                self.on_change(self.roster)
            else:
                self._schedule_handoff(generation)
        self._schedule_refresh(generation)

    def _read_worker(self, generation: int, snapshot: WindowSnapshot) -> None:
        try:
            result = prepare_roster(snapshot, self.read_role)
        except Exception:
            result = PartyRosterResult("ROLE_WORKER_ERROR", snapshot.revision)
        # A stale worker may put into an old queue, but _apply_result fences
        # generation and compares fresh Start cache before state mutation.
        self._queue.put((generation, result))

    def _schedule_handoff(self, generation: int) -> None:
        if self._active and generation == self._generation and self._handoff_job is None:
            self._handoff_job = self.root.after(
                S90_UI_HANDOFF_MS, lambda: self._handoff(generation))

    def _handoff(self, generation: int) -> None:
        if not self._active or generation != self._generation:
            return
        self._handoff_job = None
        try:
            while True:
                epoch, result = self._queue.get_nowait()
                if epoch != self._generation:
                    continue
                self._working = False
                self.roster.apply(result, self.start_producer.read_snapshot())
                self.on_change(self.roster)
        except Empty:
            pass
        if self._working:
            self._schedule_handoff(generation)

    def stop(self) -> None:
        self._generation += 1
        self._active = False
        for job in (self._refresh_job, self._handoff_job):
            if job is not None:
                try:
                    self.root.after_cancel(job)
                except Exception:
                    pass
        self._refresh_job = self._handoff_job = None
        self._working = False
        self.roster.clear("STOPPED")
        self.on_change(self.roster)

    def shutdown(self) -> None:
        if self._closed:
            return
        self.stop()
        self._closed = True
