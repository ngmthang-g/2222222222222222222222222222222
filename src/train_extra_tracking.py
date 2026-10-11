"""S126 H12 passive per-HWND/PID Farm-session statistics, NO game runner.

Original H12: session time/first live refresh baseline; positive-only
BoundMoney and EXP deltas; Site-10 occupied-slot preservation; whole-session
hourly rates; Vietnamese grouped values. A session is never inferred from a
visible window. It starts ONLY via an explicit confirmed Farm lifecycle event.
No native memory reader, Play/Bán/Đánh buttons, Info bypass or Proxy.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
import math
import time
from typing import Callable

from train_character_samples import TrainCharacterSample


def _positive_integer(value) -> bool:
    return type(value) is int and value >= 0


def vn_integer(value: int) -> str:
    if not _positive_integer(value):
        raise ValueError("INVALID_VN_INTEGER")
    return f"{value:,}".replace(",", ".")


def vn_money_2(value: Decimal) -> str:
    """Two Vietnamese decimals; HALF_UP is a documented reconstruction."""
    if not isinstance(value, Decimal) or not value.is_finite() or value < 0:
        raise ValueError("INVALID_VN_MONEY")
    quant = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{quant:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


@dataclass(frozen=True)
class TrainSessionStats:
    active: bool
    elapsed_seconds: float
    bag_slots: int | None
    deaths: int
    earned_bound_money_raw: int
    earned_exp: int
    money_per_hour: Decimal
    exp_per_hour: int


class TrainSessionTracker:
    """Only original 5-second samples feed this counter on the Tk owner.

    START is an external verified Farm engine lifecycle event, not the
    existence of a GameWindow and not a Tk button without an engine.
    First money/EXP sample *after* START establishes baseline (earns zero).
    Missing/failed samples preserve previous baseline, bag count and totals.
    """

    def __init__(self, *, clock: Callable[[], float] = time.monotonic):
        self._clock = clock
        self.reset()

    def reset(self) -> None:
        self.active = False
        self.start_time: float | None = None
        self.bag_slots: int | None = None
        self.deaths = 0
        self.earned_bound_money_raw = 0
        self.earned_exp = 0
        self._last_bound_money: int | None = None
        self._last_exp: int | None = None

    def start_confirmed_session(self, *, now: float | None = None) -> None:
        when = self._clock() if now is None else now
        if not isinstance(when, (int, float)) or not math.isfinite(when):
            raise ValueError("INVALID_FARM_SESSION_START_CLOCK")
        self.reset()
        self.active = True
        self.start_time = float(when)

    def stop(self) -> None:
        """Conservatively revoke the tracking generation; do not guess resume."""
        self.reset()

    def accept(self, sample: TrainCharacterSample) -> bool:
        if type(sample) is not TrainCharacterSample:
            return False
        for val in (sample.bag_slots, sample.bound_money, sample.exp):
            if val is not None and not _positive_integer(val):
                return False
        if sample.bag_slots is not None:
            self.bag_slots = sample.bag_slots
        if not self.active:
            return True
        if sample.bound_money is not None:
            previous = self._last_bound_money
            if previous is not None and sample.bound_money > previous:
                self.earned_bound_money_raw += sample.bound_money - previous
            self._last_bound_money = sample.bound_money
        if sample.exp is not None:
            previous_exp = self._last_exp
            if previous_exp is not None and sample.exp > previous_exp:
                self.earned_exp += sample.exp - previous_exp
            self._last_exp = sample.exp
        return True

    def record_confirmed_death(self) -> bool:
        """Only authenticated H07 death-episode latch can call this later."""
        if not self.active:
            return False
        self.deaths += 1
        return True

    def stats(self, *, now: float | None = None) -> TrainSessionStats:
        clock_now = self._clock() if now is None else now
        if not isinstance(clock_now, (int, float)) or not math.isfinite(clock_now):
            raise ValueError("INVALID_TRACKER_CLOCK")
        elapsed = max(0.0, float(clock_now) - self.start_time) if self.active else 0.0
        hours = Decimal(str(elapsed)) / Decimal(3600)
        if hours <= 0:
            gold_rate = Decimal(0)
            exp_rate = 0
        else:
            # Original raw BoundMoney measures 1/10000 displayed gold.
            gold_rate = (Decimal(self.earned_bound_money_raw) / Decimal(10000)) / hours
            exp_rate = int((Decimal(self.earned_exp) / hours).quantize(
                Decimal("1"), rounding=ROUND_HALF_UP))
        return TrainSessionStats(
            active=self.active, elapsed_seconds=elapsed,
            bag_slots=self.bag_slots, deaths=self.deaths,
            earned_bound_money_raw=self.earned_bound_money_raw,
            earned_exp=self.earned_exp,
            money_per_hour=gold_rate, exp_per_hour=exp_rate)

    def text(self, *, now: float | None = None) -> str:
        data = self.stats(now=now)
        total_minutes = int(data.elapsed_seconds // 60)
        duration = f"{total_minutes // 60}h:{total_minutes % 60:02d}p"
        bag = "?" if data.bag_slots is None else str(data.bag_slots)
        gold = Decimal(data.earned_bound_money_raw) / Decimal(10000)
        return (" | ".join((
            duration,
            f"Túi: {bag}",
            f"Chết: {data.deaths}",
            f"Vàng: {vn_money_2(gold)}",
            f"{vn_money_2(data.money_per_hour)} vàng/h",
            f"{vn_integer(data.exp_per_hour)} exp/h",
        )))
