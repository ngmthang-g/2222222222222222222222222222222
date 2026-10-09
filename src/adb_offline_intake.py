"""S34 offline-only intake facade enforcing S31 -> S32 -> S33 checks.

Never call adb.exe, initialize its daemon, connect to LDPlayer, start a
game, infer emulator account totals, or grant any permission. A diagnostic
serial is *not* an action or device-control authorization. The caller must
provide already-captured transport output AND separately observed hints
with monotonic timestamps. The original E04 Windows emulator counting rule
and exact original ADB cache invalidation remain UNKNOWN.

Only this facade's strict S33 lookup is exposed to future offline reports;
the S31/S32 lower-level objects are not exposed through facade receipts.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Mapping

from adb_identity_evidence import (
    GuestIdentityHint, inspect_captured_adb_devices,
    LOCAL_CAPTURE_TTL_SECONDS,
)
from adb_hint_provenance import HintTimes, with_hint_times, REVERSE_FIELDS
from adb_serial_epochs import SerialEpochSnapshot, advance_serial_epochs


@dataclass(frozen=True)
class CapturedAdbFrame:
    """Input captured by someone else; never claims to be real device proof."""
    text: str | None
    captured_at: float
    hints_by_serial: Mapping[str, GuestIdentityHint] | None = None
    times_by_serial: Mapping[str, HintTimes] | None = None
    observed_reboots: tuple[str, ...] = ()


@dataclass(frozen=True)
class IntakeReceipt:
    """Sanitized diagnostics only; deliberately contains no inner S31/S32."""
    status: str
    epoch_status: str
    observed_at: float | None
    transport_rows: int
    epoch_events: tuple[str, ...]
    detail: str | None = None

    @property
    def combined_running_count(self) -> None:
        return None

    @property
    def emulator_account_count(self) -> None:
        return None

    @property
    def is_authoritative_account_total(self) -> bool:
        return False


@dataclass(frozen=True)
class IdentityLookup:
    """Explicitly non-authoritative diagnostic, never a command target."""
    code: str
    serial: str | None = None

    @property
    def may_control_device(self) -> bool:
        return False

    @property
    def is_authoritative_account_total(self) -> bool:
        return False


class OfflineAdbIntake:
    """Single strict stateful entry point; no external I/O and no auto-rebind.

    Every rejected or missing frame breaks chronology. The next valid frame
    must establish a new S33 baseline; hints at/before that boundary are
    refused. A replayed frame also clears history, never reuses an older
    authoritative-looking result. This is a LOCAL diagnostic policy.
    """

    def __init__(self) -> None:
        self._epoch: SerialEpochSnapshot | None = None
        self._last = IntakeReceipt("NO_CAPTURE", "NO_EPOCH", None, 0, ())

    @property
    def last_receipt(self) -> IntakeReceipt:
        return self._last

    def _reject(self, reason: str, observed_at: float | None = None) -> IntakeReceipt:
        self._epoch = None
        self._last = IntakeReceipt("REJECTED", "EPOCH_RESET",
                                   observed_at, 0, (), reason)
        return self._last

    def ingest(self, frame: CapturedAdbFrame, *, now: float) -> IntakeReceipt:
        """Always S31 parse, S32 per-hint provenance, S33 epoch progression."""
        if type(frame) is not CapturedAdbFrame:
            return self._reject("INVALID_FRAME")
        if (type(now) not in (int, float) or not math.isfinite(now)
                or type(frame.captured_at) not in (int, float)
                or not math.isfinite(frame.captured_at)):
            return self._reject("INVALID_CAPTURE_CLOCK")
        if (now < frame.captured_at
                or now - frame.captured_at > LOCAL_CAPTURE_TTL_SECONDS):
            return self._reject("CAPTURE_OUTSIDE_LOCAL_WINDOW",
                                frame.captured_at)
        try:
            # Don't prefilter transport states: S31 distinguishes offline and
            # unauthorized from absent, S33 uses them as invalidation events.
            parsed = inspect_captured_adb_devices(
                frame.text, captured_at=frame.captured_at,
                hints_by_serial=frame.hints_by_serial)
            if parsed.status != "PARSED":
                return self._reject("S31_" + parsed.status, frame.captured_at)
            timed = with_hint_times(
                parsed, {} if frame.times_by_serial is None else frame.times_by_serial)
            if timed.provenance_error is not None:
                return self._reject("S32_" + timed.provenance_error,
                                    frame.captured_at)
            snapshot = advance_serial_epochs(
                self._epoch, timed, observed_reboots=frame.observed_reboots)
            if snapshot.status not in ("BASELINE", "CONSISTENT_HISTORY"):
                return self._reject("S33_" + snapshot.status, frame.captured_at)
        except (TypeError, ValueError, OverflowError, AttributeError):
            return self._reject("INVALID_OFFLINE_EVIDENCE", frame.captured_at)
        self._epoch = snapshot
        events = tuple(event.code for event in snapshot.events)
        self._last = IntakeReceipt(
            "ACCEPTED_DIAGNOSTIC_ONLY", snapshot.status,
            frame.captured_at, len(parsed.transports), events)
        return self._last

    def lookup(self, field: str, value: str, *, now: float) -> IdentityLookup:
        """No caller-accessible direct S31 or S32 lookup; S33 is mandatory."""
        if field not in REVERSE_FIELDS or type(value) is not str or not value:
            return IdentityLookup("INVALID_LOOKUP")
        if type(now) not in (int, float) or not math.isfinite(now):
            return IdentityLookup("INVALID_CLOCK")
        if self._last.status != "ACCEPTED_DIAGNOSTIC_ONLY" or self._epoch is None:
            return IdentityLookup("NO_ACCEPTED_EPOCH")
        if self._epoch.view.capture.freshness(now) != "FRESH_CAPTURE_DIAGNOSTIC_ONLY":
            return IdentityLookup("STALE_OR_INVALID_CAPTURE")
        serial = self._epoch.unique_serial_for(field, value, now)
        return (IdentityLookup("UNIQUE_DIAGNOSTIC_ONLY", serial)
                if serial is not None else IdentityLookup("AMBIGUOUS_OR_UNVERIFIED"))

    def replay(self, frames: Iterable[CapturedAdbFrame],
               *, now: float) -> tuple[IntakeReceipt, ...]:
        """Process in caller-provided order, never sort or silently drop rows.

        Nonmonotonic timestamps are rejected by S33. Invalid/missing frames
        reset epoch state. These results are not a signed playback record.
        """
        try:
            iterator = iter(frames)
        except TypeError:
            return (self._reject("INVALID_BATCH"),)
        receipts: list[IntakeReceipt] = []
        for frame in iterator:
            receipts.append(self.ingest(frame, now=now))
        return tuple(receipts)
