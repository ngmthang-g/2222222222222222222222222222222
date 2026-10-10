"""S94 G03/G10: read-only Party RoleID/TeamID identity preflight.

The ORIGINAL Party action resolver consumes memory_items.read_own_ids()
records (pid, RoleID, Name, Lv), NOT the utils.get_character_info RoleName
display cache. It matches stored names exactly, then lowercase fallback,
and obtains current HWND from PID; read_team_id(hwnd) is a separate source.

IMPORTANT: No original TLM game memory reader, signed Info issuer or team
protocol is present here. Callback injection is only an explicitly external
/test-only diagnostic probe; even a successful result is NOT an authorized
sendable command, genuine game assertion, or original-role validation. This
module NEVER sends packets, clicks, reads game memory or enables S92 actions.

TeamID 0 and 0xFFFFFFFF = KNOWN_OUTSIDE; None = UNKNOWN READ FAILURE.
An unrecognized/unreadable team ID may never silently count as outside.
Original RoleID numeric sentinel has NOT been established (G03); DO NOT
invent a sentinel at 0 or 0xFFFFFFFF for RoleID.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from start_polling import WindowSnapshot
from start_windows import GameWindow, WindowBackend

NO_TEAM_IDS = frozenset((0, 0xFFFFFFFF))


@dataclass(frozen=True)
class OwnRoleRecord:
    pid: int
    role_id: int
    name: str
    level: int


@dataclass(frozen=True)
class PartyTeamTarget:
    saved_name: str
    hwnd: int
    pid: int
    role_id: int
    team_id: int
    team_state: str


@dataclass(frozen=True)
class PartyTeamPreflightResult:
    code: str
    targets: tuple[PartyTeamTarget, ...] = ()
    unavailable_names: tuple[str, ...] = ()
    observed_revision: int = 0


def classify_team_id(team_id: int | None) -> str:
    """Exact original Party G03/G10 no-team sentinels; no invented default."""
    if team_id is None:
        return "UNKNOWN_READ_FAILURE"
    if type(team_id) is not int or team_id < 0 or team_id > 0xFFFFFFFF:
        return "INVALID_TEAM_ID"
    if team_id in NO_TEAM_IDS:
        return "KNOWN_OUTSIDE_TEAM"
    return "KNOWN_IN_TEAM"


def _snapshot_pairs(value: object) -> frozenset[tuple[int, int]] | None:
    if not isinstance(value, WindowSnapshot) or not value.valid:
        return None
    windows = value.windows
    if (not isinstance(windows, tuple)
            or any(not isinstance(w, GameWindow)
                   or type(w.hwnd) is not int or type(w.pid) is not int
                   or w.hwnd <= 0 or w.pid <= 0 for w in windows)):
        return None
    pairs = frozenset((w.hwnd, w.pid) for w in windows)
    if (len(pairs) != len(windows)
            or len({w.hwnd for w in windows}) != len(windows)
            or len({w.pid for w in windows}) != len(windows)):
        return None
    return pairs


def _parse_live_records(value: object) -> tuple[OwnRoleRecord, ...] | None:
    if not isinstance(value, (list, tuple)):
        return None
    records: list[OwnRoleRecord] = []
    pids: set[int] = set()
    for row in value:
        if not isinstance(row, (tuple, list)) or len(row) != 4:
            return None
        pid, role_id, name, lv = row
        # Numeric RoleID 0 remains possible: original RoleID sentinel unknown.
        if (type(pid) is not int or pid <= 0 or type(role_id) is not int
                or type(name) is not str or not name.strip()
                or type(lv) is not int or pid in pids):
            return None
        pids.add(pid)
        records.append(OwnRoleRecord(pid, role_id, name.strip(), lv))
    return tuple(records)


def _match_record(name: str, rows: tuple[OwnRoleRecord, ...]
                  ) -> tuple[OwnRoleRecord | None, str]:
    exact = tuple(r for r in rows if r.name == name)
    if len(exact) == 1:
        return exact[0], "EXACT"
    if len(exact) > 1:
        return None, "AMBIGUOUS_EXACT"
    lowered = tuple(r for r in rows if r.name.lower() == name.lower())
    if len(lowered) == 1:
        return lowered[0], "LOWERCASE"
    if len(lowered) > 1:
        return None, "AMBIGUOUS_LOWERCASE"
    return None, "OFFLINE"


class PartyTeamIdentityPreflight:
    """Conservative read-only intake; mandatory *external* live providers.

    The injectable 'allowed' is NEVER a signed Info implementation.
    Callers must not treat a matching result as authorization to send to game.
    """

    def __init__(self, *, start_producer, backend: WindowBackend | None = None,
                 read_own_ids: Callable[[], object] | None = None,
                 read_team_id: Callable[[int], object] | None = None,
                 allowed: Callable[[], bool] | None = None):
        self.start_producer = start_producer
        self.backend = backend
        self.read_own_ids = read_own_ids
        self.read_team_id = read_team_id
        self.allowed = allowed

    def inspect(self, selected_names: tuple[str, ...]) -> PartyTeamPreflightResult:
        if (not isinstance(selected_names, tuple)
                or any(type(n) is not str or not n.strip()
                       for n in selected_names)
                or len({n.strip() for n in selected_names}) != len(selected_names)):
            return PartyTeamPreflightResult("INVALID_SELECTION")
        if not selected_names:
            return PartyTeamPreflightResult("NO_SELECTED_MEMBERS")
        if (not callable(self.read_own_ids) or not callable(self.read_team_id)
                or self.backend is None
                or not callable(getattr(self.start_producer, "read_snapshot", None))):
            return PartyTeamPreflightResult("LIVE_IDENTITY_PROVIDER_UNAVAILABLE")
        if not callable(self.allowed):
            return PartyTeamPreflightResult("SIGNED_INFO_GATE_UNAVAILABLE")
        try:
            if self.allowed() is not True:
                return PartyTeamPreflightResult("PERMISSION_NOT_VERIFIED")
        except Exception:
            return PartyTeamPreflightResult("PERMISSION_READ_ERROR")

        try:
            initial = self.start_producer.read_snapshot()
            pairs = _snapshot_pairs(initial)
        except Exception:
            return PartyTeamPreflightResult("START_CACHE_READ_ERROR")
        if pairs is None:
            return PartyTeamPreflightResult("INVALID_START_CACHE")
        if not pairs:
            return PartyTeamPreflightResult("NO_LIVE_WINDOWS", observed_revision=initial.revision)
        # Verify the physical HWND→PID generation, not just saved role labels.
        by_pid = {w.pid: w.hwnd for w in initial.windows}
        try:
            for hwnd, pid in pairs:
                if (not self.backend.is_window(hwnd)
                        or self.backend.process_id(hwnd) != pid):
                    return PartyTeamPreflightResult("STALE_NATIVE_HWND_PID")
        except Exception:
            return PartyTeamPreflightResult("NATIVE_WINDOW_CHECK_FAILED")

        try:
            rows = _parse_live_records(self.read_own_ids())
        except Exception:
            return PartyTeamPreflightResult("ROLEID_READ_ERROR")
        if rows is None:
            return PartyTeamPreflightResult("INVALID_ROLEID_RECORDS")
        targets: list[PartyTeamTarget] = []
        missing: list[str] = []
        used_pid: set[int] = set()
        for requested in selected_names:
            saved_name = requested.strip()
            record, match_code = _match_record(saved_name, rows)
            if record is None:
                if match_code != "OFFLINE":
                    return PartyTeamPreflightResult(match_code, unavailable_names=(saved_name,))
                missing.append(saved_name)
                continue
            hwnd = by_pid.get(record.pid)
            if hwnd is None:
                missing.append(saved_name)
                continue
            if record.pid in used_pid:
                return PartyTeamPreflightResult("DUPLICATE_ACTION_TARGET")
            used_pid.add(record.pid)
            try:
                if (not self.backend.is_window(hwnd)
                        or self.backend.process_id(hwnd) != record.pid):
                    return PartyTeamPreflightResult("STALE_NATIVE_HWND_PID")
                team_value = self.read_team_id(hwnd)
                if (not self.backend.is_window(hwnd)
                        or self.backend.process_id(hwnd) != record.pid):
                    return PartyTeamPreflightResult("STALE_NATIVE_HWND_PID")
            except Exception:
                return PartyTeamPreflightResult("TEAMID_READ_ERROR")
            team_state = classify_team_id(team_value)
            if team_state == "UNKNOWN_READ_FAILURE":
                return PartyTeamPreflightResult("TEAMID_UNKNOWN_NOT_OUTSIDE", unavailable_names=(saved_name,))
            if team_state == "INVALID_TEAM_ID":
                return PartyTeamPreflightResult("INVALID_TEAMID_DATA", unavailable_names=(saved_name,))
            targets.append(PartyTeamTarget(
                saved_name, hwnd, record.pid, record.role_id,
                team_value, team_state))

        # A backend read might be slow: recheck exact START revision and HWND/PID
        # generation before publishing even diagnostic identity observations.
        try:
            latest = self.start_producer.read_snapshot()
            if (not isinstance(latest, WindowSnapshot)
                    or latest.revision != initial.revision
                    or _snapshot_pairs(latest) != pairs):
                return PartyTeamPreflightResult("STALE_START_REVISION")
            for hwnd, pid in pairs:
                if (not self.backend.is_window(hwnd)
                        or self.backend.process_id(hwnd) != pid):
                    return PartyTeamPreflightResult("STALE_NATIVE_HWND_PID")
            if self.allowed() is not True:
                return PartyTeamPreflightResult("PERMISSION_REVOKED")
        except Exception:
            return PartyTeamPreflightResult("FINAL_REVALIDATION_FAILED")
        if missing:
            return PartyTeamPreflightResult(
                "UNRESOLVED_ONLINE_MEMBERS", unavailable_names=tuple(missing),
                observed_revision=initial.revision)
        return PartyTeamPreflightResult(
            "DIAGNOSTIC_OBSERVED_NO_GAME_ACTION", targets=tuple(targets),
            observed_revision=initial.revision)
