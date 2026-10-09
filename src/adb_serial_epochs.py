"""S33: offline per-serial connection epoch guard for cached ADB hints.

S31/S32 captured transport/hint observations are diagnostic only.  Even a
fresh Android ID, HWID, guest IP or guest PID must not be replayed across a
disconnect, missing-device interval, or independently observed reboot.

A conservative epoch boundary requires a hint timestamp STRICTLY LATER
than the observed start of each online epoch. A newly observed serial has
no trusted prehistory; initial hints only become eligible on a subsequent
fresh capture. An explicit reboot marker is *caller-supplied evidence* and
does not constitute our own detection of a reboot or authentication.

No ADB commands/server, Frida, process spawning, VM/game actions, Proxy,
license grants, UI, or inferred running-account totals.
"""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Iterable, Mapping
import math

from adb_hint_provenance import TimedAdbIdentity, HintAssessment, REVERSE_FIELDS
from adb_identity_evidence import LOCAL_CAPTURE_TTL_SECONDS


@dataclass(frozen=True)
class EpochEvent:
    serial: str
    code: str
    generation: int
    boundary_at: float | None


@dataclass(frozen=True)
class SerialEpochSnapshot:
    view: TimedAdbIdentity
    boundary_by_serial: Mapping[str, float | None]
    state_by_serial: Mapping[str, str]
    generation_by_serial: Mapping[str, int]
    status: str
    events: tuple[EpochEvent, ...] = ()

    @property
    def emulator_account_count(self) -> None:
        return None

    @property
    def combined_running_count(self) -> None:
        return None

    @property
    def is_authoritative_account_total(self) -> bool:
        return False

    def assess(self, serial: str, field: str, now: float) -> HintAssessment:
        """Read-only diagnostic, never validated identity/command routing."""
        base = self.view.assess(serial, field, now)
        if self.status not in ("BASELINE", "CONSISTENT_HISTORY"):
            return HintAssessment(serial, field, base.value, "EPOCH_UNVERIFIED",
                                  base.observed_at)
        if not base.is_fresh_diagnostic:
            return base
        boundary = self.boundary_by_serial.get(serial)
        if boundary is None:
            return HintAssessment(serial, field, base.value,
                                  "NO_ONLINE_EPOCH", base.observed_at)
        if base.observed_at is None or base.observed_at <= boundary:
            return HintAssessment(serial, field, base.value,
                                  "HINT_NOT_AFTER_EPOCH", base.observed_at)
        return base

    def unique_serial_for(self, field: str, value: str, now: float) -> str | None:
        """All online peers must have *same-field* fresh, post-epoch hints."""
        if field not in REVERSE_FIELDS or type(value) is not str or not value:
            return None
        if self.status not in ("BASELINE", "CONSISTENT_HISTORY"):
            return None
        if self.view.capture.freshness(now) != "FRESH_CAPTURE_DIAGNOSTIC_ONLY":
            return None
        if self.view.provenance_error is not None or self.view.capture.duplicate_serials:
            return None
        online = [row.serial for row in self.view.capture.transports
                  if row.state == "device"]
        if not online:
            return None
        hints = [self.assess(serial, field, now) for serial in online]
        if any(not x.is_fresh_diagnostic for x in hints):
            return None
        matches = [x.serial for x in hints if x.value == value]
        return matches[0] if len(matches) == 1 else None


def _frozen(value: Mapping) -> Mapping:
    return MappingProxyType(dict(value))


def advance_serial_epochs(
    previous: SerialEpochSnapshot | None,
    current: TimedAdbIdentity,
    *,
    observed_reboots: Iterable[str] = (),
) -> SerialEpochSnapshot:
    """Advance from explicitly captured offline transport observations only.

    S33 local epoch model:
      * first ONLINE observation sets a boundary and rejects old/equal hints;
      * OFFLINE/UNAUTHORIZED/ABSENT clears that serial's online epoch;
      * a later return to ONLINE creates a NEW generation and boundary;
      * independently observed reboot also forces a new generation;
      * never infer reboot from matching Android ID or guest PID;
      * non-monotonic, stale/gapped or ambiguous captures fail closed.

    Reboot markers must be supplied by a future trusted observation provider,
    not guessed from an IP/aid change. No external processes are called.
    """
    if type(current) is not TimedAdbIdentity:
        raise ValueError("TimedAdbIdentity required")
    if previous is not None and type(previous) is not SerialEpochSnapshot:
        raise ValueError("SerialEpochSnapshot required")
    try:
        reboot_list = tuple(observed_reboots)
    except (TypeError, ValueError):
        reboot_list = ()
        invalid_markers = True
    else:
        invalid_markers = (any(type(x) is not str for x in reboot_list)
                           or len(set(reboot_list)) != len(reboot_list))
    rows = {row.serial: row.state for row in current.capture.transports}
    timestamp = current.capture.captured_at
    if (not math.isfinite(timestamp) or current.capture.status != "PARSED"
            or current.provenance_error is not None
            or invalid_markers or any(s not in rows for s in reboot_list)):
        return SerialEpochSnapshot(current, _frozen({}), _frozen({}), _frozen({}),
                                   "INVALID_CAPTURE_OR_EPOCH_MARKERS")

    before = previous.state_by_serial if previous is not None else {}
    boundaries = dict(previous.boundary_by_serial) if previous is not None else {}
    generations = dict(previous.generation_by_serial) if previous is not None else {}
    if previous is not None:
        last = previous.view.capture.captured_at
        if timestamp <= last:
            return SerialEpochSnapshot(current, _frozen({}), _frozen({}), _frozen({}),
                                       "NON_INCREASING_CAPTURE_TIME")
        if (previous.status not in ("BASELINE", "CONSISTENT_HISTORY")
                or timestamp - last > LOCAL_CAPTURE_TTL_SECONDS):
            # A gap might hide a disconnect/reboot, even when a serial looks
            # unchanged. Start from fresh boundary, discard past hints.
            before = {}
            boundaries = {}
            generations = {}
            history_gap = True
        else:
            history_gap = False
    else:
        history_gap = False

    events: list[EpochEvent] = []
    next_states = dict(rows)
    for serial in before:
        if serial not in rows:
            next_states[serial] = "ABSENT"
    for serial in sorted(next_states):
        old = before.get(serial, "ABSENT")
        new = next_states[serial]
        generation = generations.get(serial, 0)
        if new != "device":
            if old == "device":
                events.append(EpochEvent(serial, "EPOCH_ENDED_" + new,
                                         generation, None))
            boundaries[serial] = None
            generations.setdefault(serial, generation)
            continue
        new_epoch = (old != "device" or serial in reboot_list
                     or serial not in boundaries or boundaries[serial] is None)
        if new_epoch:
            generation += 1
            boundaries[serial] = timestamp
            generations[serial] = generation
            reason = ("EXPLICIT_REBOOT_NEW_EPOCH" if serial in reboot_list
                      else "ONLINE_FIRST_OBSERVATION" if old == "ABSENT"
                      else "ONLINE_AFTER_UNAVAILABLE")
            events.append(EpochEvent(serial, reason, generation, timestamp))
    status = "BASELINE" if previous is None or history_gap else "CONSISTENT_HISTORY"
    if history_gap:
        events.append(EpochEvent("*", "HISTORY_GAP_REBASELINE", 0, timestamp))
    return SerialEpochSnapshot(current, _frozen(boundaries), _frozen(next_states),
                               _frozen(generations), status, tuple(events))
