"""S18 original C05/C08 grid state and E05 settings.ini persistence.

Original proofs: Settings.grid_cols/grid_rows defaults 3/4; HWND-backed master
selection is runtime-only; +/- update stored grid and labels. Original
min/max bounds are UNKNOWN, so S18 applies explicit LOCAL safety 1..12.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from settings_store import read_settings, write_settings

GRID_LOCAL_MIN = 1
GRID_LOCAL_MAX = 12
GRID_BOUNDS_ORIGINAL = "UNKNOWN_S18_LOCAL_SAFE_RANGE_1_TO_12"


def valid_dimension(value) -> bool:
    return type(value) is int and GRID_LOCAL_MIN <= value <= GRID_LOCAL_MAX


def update_dimension(value: int, delta: int) -> int:
    if not valid_dimension(value) or delta not in (-1, 1):
        raise ValueError("INVALID_GRID_DIMENSION_CHANGE")
    return max(GRID_LOCAL_MIN, min(GRID_LOCAL_MAX, value + delta))


@dataclass(frozen=True)
class GridSettings:
    cols: int = 3
    rows: int = 4


class GridSettingsStore:
    """Reuse existing atomic E05 ini writer; NEVER wipe unrelated sections."""

    def __init__(self, path: str | Path | None = None):
        self.path = path

    def load(self) -> GridSettings:
        try:
            p = read_settings(self.path)
            c = p.getint("Settings", "grid_cols", fallback=3)
            r = p.getint("Settings", "grid_rows", fallback=4)
        except (OSError, RuntimeError, ValueError):
            return GridSettings()
        return GridSettings(c if valid_dimension(c) else 3,
                            r if valid_dimension(r) else 4)

    def save(self, cols: int, rows: int) -> None:
        if not valid_dimension(cols) or not valid_dimension(rows):
            raise ValueError("INVALID_GRID_NOT_SAVED")
        p = read_settings(self.path)
        if not p.has_section("Settings"):
            p.add_section("Settings")
        p.set("Settings", "grid_cols", str(cols))
        p.set("Settings", "grid_rows", str(rows))
        write_settings(p, self.path)


class MasterSelection:
    """HWND+PID identity; labels are presentation, NEVER control keys.

    In absence of original C05 auto-selection rule, use explicit local
    first-discovered fallback only when no manual selection remains.
    Reused HWND with a different PID must never inherit old selection.
    """

    def __init__(self):
        self.selected: tuple[int, int] | None = None
        self.sources: tuple[tuple[int, int], ...] = ()

    def update(self, windows):
        identities = tuple((w.hwnd, w.pid) for w in windows)
        if len({h for h, _ in identities}) != len(identities):
            raise ValueError("AMBIGUOUS_HWND")
        if any(type(h) is not int or type(p) is not int or h <= 0 or p <= 0
               for h, p in identities):
            raise ValueError("INVALID_HWND_PID")
        changed = identities != self.sources
        self.sources = identities
        if self.selected not in identities:
            self.selected = identities[0] if identities else None
        return changed

    def choose(self, hwnd: int, pid: int) -> bool:
        if (hwnd, pid) not in self.sources:
            return False
        self.selected = (hwnd, pid)
        return True

    @property
    def hwnd(self) -> int | None:
        return self.selected[0] if self.selected else None

    @property
    def pid(self) -> int | None:
        return self.selected[1] if self.selected else None
