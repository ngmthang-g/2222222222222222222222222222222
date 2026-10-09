"""S31 P02/P05 emulator ADB transport + clone identity evidence, offline parser ONLY.

Consumes already-captured 'adb devices' text and optional independently
observed per-serial hints. Absolutely no subprocess, ADB server startup,
Frida/Android calls, process execution, emulator counting or permission grant.

Original P02: ADB serial can change; aid (Android ID) and hwid can COLLIDE
on clones, guest IPv4 can disambiguate only if reverse map is UNIQUE. P05
UI rows are keyed by aid while preset/commands are serial-keyed: never
automatically reconcile a cloned aid to a live target.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import re
from typing import Mapping

# S31 local diagnostics freshness window, NOT original P02's 5-minute aid
# cache. In particular 'fresh' does not prove a guest/game is operational.
LOCAL_CAPTURE_TTL_SECONDS = 30.0

_ADB_LINE = re.compile(r"^([^\s]+)\s+(device|offline|unauthorized|recovery|sideload|bootloader|unknown)(?:\s+.*)?$")


@dataclass(frozen=True)
class GuestIdentityHint:
    """Already observed by an independent future adapter; NOT fetched here."""
    android_id: str | None = None
    guest_ipv4: str | None = None
    hwid: str | None = None
    guest_game_pid: int | None = None


@dataclass(frozen=True)
class AdbTransport:
    serial: str
    state: str
    hint: GuestIdentityHint


@dataclass(frozen=True)
class AdbIdentityEvidence:
    captured_at: float
    transports: tuple[AdbTransport, ...]
    status: str
    error: str | None
    duplicate_serials: tuple[str, ...] = ()
    duplicate_aids: tuple[str, ...] = ()
    duplicate_hwids: tuple[str, ...] = ()
    duplicate_guest_ips: tuple[str, ...] = ()
    unknown_states: tuple[str, ...] = ()

    @property
    def observed_online_serials(self) -> tuple[str, ...]:
        duplicate = set(self.duplicate_serials)
        return tuple(sorted(row.serial for row in self.transports
                            if row.state == "device" and row.serial not in duplicate))

    @property
    def emulator_account_count(self) -> None:
        return None

    @property
    def combined_running_count(self) -> None:
        return None

    @property
    def is_authoritative_account_total(self) -> bool:
        return False

    def freshness(self, now: float, *, max_age_seconds: float = LOCAL_CAPTURE_TTL_SECONDS) -> str:
        if (type(now) not in (int, float) or not math.isfinite(now)
                or type(max_age_seconds) not in (int, float)
                or not math.isfinite(max_age_seconds) or max_age_seconds < 0):
            raise ValueError("Finite non-negative local diagnostic timestamp required")
        if not math.isfinite(self.captured_at) or now < self.captured_at:
            return "CLOCK_INVALID_OR_REGRESSED"
        if self.status != "PARSED":
            return "CAPTURE_UNAVAILABLE_OR_AMBIGUOUS"
        if now - self.captured_at > max_age_seconds:
            return "STALE_CAPTURE"
        return "FRESH_CAPTURE_DIAGNOSTIC_ONLY"

    def unique_serial_for(self, field: str, value: str, now: float) -> str | None:
        """Read-only reverse identity. Never force a clone/aid to a serial."""
        if field not in ("android_id", "guest_ipv4", "hwid") or not value:
            return None
        if self.freshness(now) != "FRESH_CAPTURE_DIAGNOSTIC_ONLY":
            return None
        candidates = [row.serial for row in self.transports
                      if row.state == "device"
                      and getattr(row.hint, field) == value]
        if len(candidates) != 1:
            return None
        if candidates[0] in self.duplicate_serials:
            return None
        return candidates[0]


def _normal_hint(hint: GuestIdentityHint) -> GuestIdentityHint:
    if type(hint) is not GuestIdentityHint:
        raise ValueError("Per-serial hints require GuestIdentityHint")
    for name in ("android_id", "guest_ipv4", "hwid"):
        value = getattr(hint, name)
        if value is not None and (type(value) is not str or not value.strip()
                                  or value != value.strip()
                                  or len(value) > 255
                                  or "\x00" in value):
            raise ValueError("Malformed guest identity " + name)
    if (hint.guest_game_pid is not None
            and (type(hint.guest_game_pid) is not int or hint.guest_game_pid <= 0)):
        raise ValueError("Invalid guest game PID")
    return hint


def inspect_captured_adb_devices(
    captured_text: str | None,
    *,
    captured_at: float,
    hints_by_serial: Mapping[str, GuestIdentityHint] | None = None,
) -> AdbIdentityEvidence:
    """Parse an existing *captured* stdout string; never executes adb.

    Only the conventional 'List of devices attached' header and transport
    states are accepted. A diagnostic is not a verified real ADB capture.
    Hints are optional and not treated as independently authenticated.
    """
    if type(captured_at) not in (int, float) or not math.isfinite(captured_at):
        raise ValueError("Captured monotonic timestamp required")
    if captured_text is None:
        return AdbIdentityEvidence(captured_at, (), "NO_CAPTURE", "NO_ADB_OUTPUT")
    if type(captured_text) is not str or len(captured_text) > 1024 * 1024:
        return AdbIdentityEvidence(captured_at, (), "INVALID_CAPTURE", "INVALID_TEXT")
    hints = {} if hints_by_serial is None else hints_by_serial
    if not isinstance(hints, Mapping):
        return AdbIdentityEvidence(captured_at, (), "INVALID_CAPTURE", "INVALID_HINTS")
    lines = [x.strip() for x in captured_text.lstrip("\ufeff").splitlines()
             if x.strip()]
    if not lines or lines[0] != "List of devices attached":
        return AdbIdentityEvidence(captured_at, (), "INVALID_CAPTURE", "MISSING_HEADER")
    if len(lines) > 4097:
        return AdbIdentityEvidence(captured_at, (), "INVALID_CAPTURE", "TOO_MANY_DEVICES")
    rows: list[AdbTransport] = []
    for line in lines[1:]:
        match = _ADB_LINE.fullmatch(line)
        if match is None:
            return AdbIdentityEvidence(captured_at, (), "INVALID_CAPTURE", "INVALID_DEVICE_ROW")
        serial, state = match.group(1), match.group(2)
        if serial == "*" or len(serial) > 255:
            return AdbIdentityEvidence(captured_at, (), "INVALID_CAPTURE", "INVALID_SERIAL")
        hint = hints.get(serial, GuestIdentityHint())
        try:
            _normal_hint(hint)
        except ValueError:
            return AdbIdentityEvidence(captured_at, (), "INVALID_CAPTURE", "INVALID_HINT")
        rows.append(AdbTransport(serial, state, hint))
    unknown_hint_keys = set(hints) - {r.serial for r in rows}
    if unknown_hint_keys:
        return AdbIdentityEvidence(captured_at, (), "INVALID_CAPTURE", "HINT_NOT_IN_CAPTURE")

    def duplicates(values):
        counts: dict[str, int] = {}
        for value in values:
            if value:
                counts[value] = counts.get(value, 0) + 1
        return tuple(sorted(v for v, c in counts.items() if c > 1))

    dup_serial = duplicates(row.serial for row in rows)
    connected = tuple(row for row in rows if row.state == "device")
    dup_aid = duplicates(row.hint.android_id for row in connected)
    dup_hwid = duplicates(row.hint.hwid for row in connected)
    dup_ip = duplicates(row.hint.guest_ipv4 for row in connected)
    unknown_states = tuple(sorted({row.state for row in rows if row.state != "device"}))
    status = "AMBIGUOUS_DUPLICATE_SERIAL" if dup_serial else "PARSED"
    return AdbIdentityEvidence(captured_at, tuple(rows), status, None,
                               dup_serial, dup_aid, dup_hwid, dup_ip, unknown_states)


@dataclass(frozen=True)
class PossibleRebindEvidence:
    android_id: str
    previous_serial: str
    current_serial: str
    certainty: str = "POSSIBLE_ONLY_NOT_VERIFIED"


def identify_possible_serial_rebinds(
    previous: AdbIdentityEvidence,
    current: AdbIdentityEvidence,
    *,
    now: float,
) -> tuple[PossibleRebindEvidence, ...]:
    """S31 diagnostics only: aid moving serial may also be a CLONE.

    Fails closed on stale/ambiguous snapshots, aid duplication, non-device
    rows and missing aid. Never rebinds actual device control or credentials.
    """
    if (previous.freshness(now) != "FRESH_CAPTURE_DIAGNOSTIC_ONLY"
            or current.freshness(now) != "FRESH_CAPTURE_DIAGNOSTIC_ONLY"):
        return ()
    ambiguous = set(previous.duplicate_aids) | set(current.duplicate_aids)
    old = {r.hint.android_id: r.serial for r in previous.transports
           if r.state == "device" and r.hint.android_id
           and r.hint.android_id not in ambiguous}
    new = {r.hint.android_id: r.serial for r in current.transports
           if r.state == "device" and r.hint.android_id
           and r.hint.android_id not in ambiguous}
    return tuple(PossibleRebindEvidence(aid, old[aid], new[aid])
                 for aid in sorted(old.keys() & new.keys()) if old[aid] != new[aid])
