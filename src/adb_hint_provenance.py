"""S32: offline P02/P05 per-hint monotonic timestamps and transport transitions.

The S31 capture may be fresh while cached Android ID, HWID, guest IPv4,
or Android guest PID is STALE. Never infer hint age from adb devices output.
Consume explicitly timestamped, pre-collected observations only. All results
are non-authoritative diagnostics, never emulator account counts, command
targets, credentials, ADB/Frida actions, or a game-launch grant.

P02 documents a ~5min aid cache, NOT a freshness/authorization guarantee.
S32 LOCAL 30s hint age is conservative diagnostic policy, not original logic.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from types import MappingProxyType
from typing import Mapping

from adb_identity_evidence import (
    AdbIdentityEvidence, AdbTransport, PossibleRebindEvidence,
    LOCAL_CAPTURE_TTL_SECONDS,
)

HINT_LOCAL_TTL_SECONDS = 30.0
IDENTITY_FIELDS = ("android_id", "hwid", "guest_ipv4", "guest_game_pid")
REVERSE_FIELDS = ("android_id", "hwid", "guest_ipv4")


@dataclass(frozen=True)
class HintTimes:
    """Independent per-field observation times in the capture clock's domain."""
    android_id_at: float | None = None
    hwid_at: float | None = None
    guest_ipv4_at: float | None = None
    guest_game_pid_at: float | None = None


@dataclass(frozen=True)
class HintAssessment:
    serial: str
    field: str
    value: str | int | None
    code: str
    observed_at: float | None = None

    @property
    def is_fresh_diagnostic(self) -> bool:
        return self.code == "FRESH_HINT_DIAGNOSTIC_ONLY"


@dataclass(frozen=True)
class TimedAdbIdentity:
    """S31 captured transport plus independent timestamps, not authentication."""
    capture: AdbIdentityEvidence
    times_by_serial: Mapping[str, HintTimes]
    provenance_error: str | None = None

    @property
    def emulator_account_count(self) -> None:
        return None

    @property
    def combined_running_count(self) -> None:
        return None

    @property
    def is_authoritative_account_total(self) -> bool:
        return False

    def assess(self, serial: str, field: str, now: float,
               *, max_age_seconds: float = HINT_LOCAL_TTL_SECONDS) -> HintAssessment:
        if field not in IDENTITY_FIELDS:
            raise ValueError("Unsupported hint field")
        if (type(now) not in (int, float) or not math.isfinite(now)
                or type(max_age_seconds) not in (int, float)
                or not math.isfinite(max_age_seconds) or max_age_seconds < 0):
            raise ValueError("Finite clock and non-negative hint TTL required")

        row = next((r for r in self.capture.transports if r.serial == serial), None)
        value = getattr(row.hint, field) if row is not None else None
        stamp = getattr(self.times_by_serial.get(serial, HintTimes()),
                        field + "_at")
        if self.capture.freshness(now) != "FRESH_CAPTURE_DIAGNOSTIC_ONLY":
            return HintAssessment(serial, field, value, "CAPTURE_NOT_FRESH", stamp)
        if self.provenance_error is not None:
            return HintAssessment(serial, field, value, "PROVENANCE_INVALID", stamp)
        if row is None:
            return HintAssessment(serial, field, None, "SERIAL_NOT_PRESENT")
        if serial in self.capture.duplicate_serials:
            return HintAssessment(serial, field, value, "DUPLICATE_SERIAL", stamp)
        if row.state != "device":
            return HintAssessment(serial, field, value, "TRANSPORT_NOT_ONLINE", stamp)
        if value is None:
            return HintAssessment(serial, field, None, "HINT_ABSENT", stamp)
        if stamp is None:
            return HintAssessment(serial, field, value, "TIMESTAMP_UNKNOWN")
        if stamp > now or stamp > self.capture.captured_at:
            return HintAssessment(serial, field, value, "HINT_TIMESTAMP_IN_FUTURE", stamp)
        if now - stamp > max_age_seconds:
            return HintAssessment(serial, field, value, "STALE_HINT", stamp)
        return HintAssessment(serial, field, value,
                              "FRESH_HINT_DIAGNOSTIC_ONLY", stamp)

    def unique_serial_for(self, field: str, value: str, now: float) -> str | None:
        """Strict diagnostic identity hint, NEVER a command destination.

        Every online device must have a fresh value for this field: a stale
        or unknown peer might have the same value, so uniqueness is unproven.
        """
        if field not in REVERSE_FIELDS or type(value) is not str or not value:
            return None
        if self.capture.freshness(now) != "FRESH_CAPTURE_DIAGNOSTIC_ONLY":
            return None
        if self.provenance_error is not None or self.capture.duplicate_serials:
            return None
        online = [r for r in self.capture.transports if r.state == "device"]
        if not online:
            return None
        observations = [self.assess(r.serial, field, now) for r in online]
        if any(not a.is_fresh_diagnostic for a in observations):
            return None
        matches = [a.serial for a in observations if a.value == value]
        return matches[0] if len(matches) == 1 else None


def with_hint_times(
    capture: AdbIdentityEvidence, times_by_serial: Mapping[str, HintTimes],
) -> TimedAdbIdentity:
    """Snapshot timestamp provenance, fail closed instead of guessing."""
    if not isinstance(capture, AdbIdentityEvidence):
        raise ValueError("S31 AdbIdentityEvidence required")
    if not isinstance(times_by_serial, Mapping):
        return TimedAdbIdentity(capture, MappingProxyType({}),
                                "INVALID_TIMESTAMP_MAPPING")
    copy: dict[str, HintTimes] = {}
    known = {r.serial for r in capture.transports}
    failure = None
    for serial, times in times_by_serial.items():
        if type(serial) is not str or serial not in known or type(times) is not HintTimes:
            failure = "INVALID_SERIAL_OR_TIMES"
            break
        for field in IDENTITY_FIELDS:
            stamp = getattr(times, field + "_at")
            if stamp is not None and (type(stamp) not in (int, float)
                                      or not math.isfinite(stamp)
                                      or stamp > capture.captured_at):
                failure = "INVALID_HINT_TIMESTAMP"
                break
            if stamp is not None:
                row = next(r for r in capture.transports if r.serial == serial)
                if getattr(row.hint, field) is None:
                    failure = "TIMESTAMP_WITHOUT_HINT"
                    break
        if failure is not None:
            break
        copy[serial] = times
    return TimedAdbIdentity(capture, MappingProxyType(copy), failure)


@dataclass(frozen=True)
class TransportTransition:
    serial: str
    previous_state: str
    current_state: str
    code: str


@dataclass(frozen=True)
class AdbLifecycleEvidence:
    status: str
    transitions: tuple[TransportTransition, ...] = ()
    possible_rebinds: tuple[PossibleRebindEvidence, ...] = ()

    @property
    def is_authoritative_rebinding(self) -> bool:
        return False

    @property
    def combined_running_count(self) -> None:
        return None


def compare_adb_lifecycle(
    previous: TimedAdbIdentity, current: TimedAdbIdentity, *,
    now: float,
) -> AdbLifecycleEvidence:
    """Offline transitions only. No inferred device ownership or replay."""
    if (previous.capture.freshness(now) != "FRESH_CAPTURE_DIAGNOSTIC_ONLY"
            or current.capture.freshness(now) != "FRESH_CAPTURE_DIAGNOSTIC_ONLY"
            or previous.provenance_error or current.provenance_error):
        return AdbLifecycleEvidence("INCOMPLETE_OR_STALE")
    if current.capture.captured_at < previous.capture.captured_at:
        return AdbLifecycleEvidence("CHRONOLOGY_INVALID")
    before = {r.serial: r for r in previous.capture.transports}
    after = {r.serial: r for r in current.capture.transports}
    transitions: list[TransportTransition] = []
    for serial in sorted(set(before) | set(after)):
        state1 = before[serial].state if serial in before else "ABSENT"
        state2 = after[serial].state if serial in after else "ABSENT"
        if state1 != state2:
            kind = ("SERIAL_APPEARED" if state1 == "ABSENT"
                    else "SERIAL_DISAPPEARED" if state2 == "ABSENT"
                    else "OFFLINE_TO_ONLINE" if state1 != "device" and state2 == "device"
                    else "ONLINE_TO_UNAVAILABLE" if state1 == "device" and state2 != "device"
                    else "TRANSPORT_STATE_CHANGED")
            transitions.append(TransportTransition(serial, state1, state2, kind))

    # Only a single, fresh AID on EVERY online peer can support a diagnostic
    # possible remap. A possible remap is NEVER verified (could be a clone).
    def aids(view: TimedAdbIdentity) -> dict[str, str] | None:
        online = [r for r in view.capture.transports if r.state == "device"]
        assessments = [view.assess(r.serial, "android_id", now) for r in online]
        if any(not a.is_fresh_diagnostic for a in assessments):
            return None
        if len({a.value for a in assessments}) != len(assessments):
            return None
        return {str(a.value): a.serial for a in assessments}

    old_aids, new_aids = aids(previous), aids(current)
    possible: list[PossibleRebindEvidence] = []
    if old_aids is not None and new_aids is not None:
        old_online = {r.serial for r in before.values() if r.state == "device"}
        new_online = {r.serial for r in after.values() if r.state == "device"}
        for aid in sorted(old_aids.keys() & new_aids.keys()):
            s1, s2 = old_aids[aid], new_aids[aid]
            if s1 != s2 and s1 not in new_online and s2 not in old_online:
                possible.append(PossibleRebindEvidence(aid, s1, s2))
    return AdbLifecycleEvidence("DIAGNOSTIC_ONLY",tuple(transitions),
                                tuple(possible))
