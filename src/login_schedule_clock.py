"""S39 F09 original-backed deterministic DAILY Login schedule clock.

NO game launcher, no shutdown command, no background worker, no fake UI.
The real F09 integration must provide independently verified F05/F06 open
and native close-all callbacks in a later milestone. This module ONLY models
the next-occurrence rule and emits due events for a trusted controller.

Evidence: docs/tasks/F09.md, docs/login/F09_SCHEDULER_MODEL.json.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

DEFAULT_CLOSE = "04:00"
DEFAULT_OPEN = "04:20"
WORKER_CHECK_SECONDS = 20
COUNTDOWN_REFRESH_SECONDS = 1
EVENT_CLOSE = "close"
EVENT_OPEN = "open"


def parse_hhmm(value: str) -> tuple[int, int]:
    """Reject ambiguous/dangerous timer values, including non-ASCII digits."""
    if (type(value) is not str or len(value) != 5 or value[2] != ":"
            or not all("0" <= value[i] <= "9" for i in (0, 1, 3, 4))):
        raise ValueError("INVALID_SCHEDULE_HHMM")
    hour = int(value[:2])
    minute = int(value[3:])
    if hour > 23 or minute > 59:
        raise ValueError("INVALID_SCHEDULE_HHMM")
    return hour, minute


def next_occurrence(now: datetime, hhmm: str) -> datetime:
    """F09: today if in the future, otherwise tomorrow; NEVER catch up.

    At equality we conservatively treat the wall-clock event as passed;
    F09 exact equality boundary is not proven by available binary evidence.
    """
    if not isinstance(now, datetime):
        raise TypeError("SCHEDULE_NOW_MUST_BE_DATETIME")
    hour, minute = parse_hhmm(hhmm)
    candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    return candidate if candidate > now else candidate + timedelta(days=1)


def format_remaining(seconds: int) -> str:
    """F09 duration display examples: 45s, 15p30s, 2h05p, 1d2h05p."""
    if type(seconds) is not int or seconds < 0:
        raise ValueError("INVALID_REMAINING_SECONDS")
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, secs = divmod(rem, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if days or hours:
        parts.append(f"{minutes:02d}p")
    elif minutes:
        parts.append(f"{minutes}p")
    if secs and not (days or hours):
        parts.append(f"{secs}s")
    if not parts:
        parts.append("0s")
    return "".join(parts)


@dataclass(frozen=True)
class ScheduleEvent:
    kind: str
    planned_time: datetime


class LoginScheduleClock:
    """F09 pure clock state. poll() emits events; it NEVER executes actions.

    No implicit persistence, no automatic startup after reload, no threads.
    Caller MUST separately implement/verify action dispatch and cadence.
    """
    def __init__(self, *, close_hhmm: str = DEFAULT_CLOSE,
                 open_hhmm: str = DEFAULT_OPEN):
        parse_hhmm(close_hhmm)
        parse_hhmm(open_hhmm)
        self.close_hhmm = close_hhmm
        self.open_hhmm = open_hhmm
        self._enabled = False
        self._next_close: datetime | None = None
        self._next_open: datetime | None = None
        self._last_poll: datetime | None = None

    @property
    def enabled(self) -> bool:
        return self._enabled

    def enable(self, now: datetime) -> None:
        if not isinstance(now, datetime):
            raise TypeError("SCHEDULE_NOW_MUST_BE_DATETIME")
        self._next_close = next_occurrence(now, self.close_hhmm)
        self._next_open = next_occurrence(now, self.open_hhmm)
        self._last_poll = now
        self._enabled = True

    def disable(self) -> None:
        """Only stop scheduling; do not close any game/window."""
        self._enabled = False
        self._next_close = self._next_open = self._last_poll = None

    def upcoming(self) -> tuple[ScheduleEvent, ...]:
        if not self._enabled or self._next_close is None or self._next_open is None:
            return ()
        return tuple(sorted((
            ScheduleEvent(EVENT_CLOSE, self._next_close),
            ScheduleEvent(EVENT_OPEN, self._next_open),
        ), key=lambda event: (event.planned_time, 0 if event.kind == EVENT_CLOSE else 1)))

    def poll(self, now: datetime) -> tuple[ScheduleEvent, ...]:
        """Return each newly due event once, then move its date forward.

        Avoid repeated dispatch after one due event. Poll past multiple days
        never returns N backlogged actions; original long-suspension policy
        is unknown, so we only emit the latest due instance per event.
        """
        if not isinstance(now, datetime):
            raise TypeError("SCHEDULE_NOW_MUST_BE_DATETIME")
        if not self._enabled:
            return ()
        if self._last_poll is not None and now < self._last_poll:
            # System clock moved backward: do not dispatch stale actions.
            self.disable()
            raise ValueError("SCHEDULE_CLOCK_MOVED_BACKWARD")
        self._last_poll = now
        due = []
        for kind, attr in ((EVENT_CLOSE, "_next_close"), (EVENT_OPEN, "_next_open")):
            when = getattr(self, attr)
            if when is None or now < when:
                continue
            due.append(ScheduleEvent(kind, when))
            # Never emit all missed days as a catch-up burst.
            while when <= now:
                when += timedelta(days=1)
            setattr(self, attr, when)
        return tuple(sorted(due, key=lambda event: (
            event.planned_time, 0 if event.kind == EVENT_CLOSE else 1)))

    def countdown(self, now: datetime) -> str:
        """Pure F09 string; owner must update a real Tk Label on main thread."""
        if not self._enabled:
            return ""
        if not isinstance(now, datetime):
            raise TypeError("SCHEDULE_NOW_MUST_BE_DATETIME")
        def item(prefix: str, stamp: datetime) -> str:
            diff = stamp - now
            # Avoid a negative countdown while awaiting the next 20s poll.
            seconds = max(0, int(diff.total_seconds() + 0.999999))
            return (f"{prefix} {stamp:%H:%M %d/%m} còn "
                    f"{format_remaining(seconds)}")
        return item("Tắt", self._next_close) + " | " + item("Mở", self._next_open)
