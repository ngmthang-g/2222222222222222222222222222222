"""S69 C14 original detached-preview Settings.ini persistence (NO auto-open).

Original C14/E05 static evidence proves [Settings] keys:
  detached_auto_open: getboolean fallback True
  detached_grid: string-like default "3"
The source does NOT prove exact combobox list, accepted grid min/max,
auto-open activation time or post-undock embedded-preview UI transitions.

Use the existing E05 atomic settings writer, preserve all unrelated keys,
and expose settings data only (no fake preview, game, UI or auto-activation).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from settings_store import read_settings, write_settings

DETACHED_AUTO_OPEN_DEFAULT = True
DETACHED_GRID_DEFAULT = "3"
DETACHED_GRID_ORIGINAL_CHOICES = "UNKNOWN"


def valid_detached_grid(value: object) -> bool:
    """S69 conservative scalar safety, NOT recovered original UI choices.

    Accept a canonical positive decimal string; never guess a max column
    count or silently coerce invalid values into a new persisted choice.
    """
    return (isinstance(value, str)
            and len(value) > 0
            and value[0] in "123456789"
            and all(c in "0123456789" for c in value))


@dataclass(frozen=True)
class DetachedSettings:
    auto_open: bool = DETACHED_AUTO_OPEN_DEFAULT
    grid: str = DETACHED_GRID_DEFAULT


class DetachedSettingsStore:
    """Data-only C14 state, not a `Tách rời` UI or runtime mode switch."""

    def __init__(self, path: str | Path | None = None):
        self.path = path

    def load(self) -> DetachedSettings:
        try:
            p = read_settings(self.path)
        except (OSError, RuntimeError, ValueError):
            return DetachedSettings()

        # Each field is independently recoverable. A malformed boolean must
        # not discard a separately valid detached_grid setting, or vice versa.
        try:
            enabled = p.getboolean(
                "Settings", "detached_auto_open",
                fallback=DETACHED_AUTO_OPEN_DEFAULT)
        except (ValueError, TypeError):
            enabled = DETACHED_AUTO_OPEN_DEFAULT

        try:
            grid = p.get("Settings", "detached_grid",
                         fallback=DETACHED_GRID_DEFAULT)
        except (ValueError, TypeError):
            grid = DETACHED_GRID_DEFAULT
        if not valid_detached_grid(grid):
            grid = DETACHED_GRID_DEFAULT
        return DetachedSettings(bool(enabled), grid)

    def save(self, auto_open: bool, grid: str) -> None:
        if type(auto_open) is not bool or not valid_detached_grid(grid):
            raise ValueError("INVALID_DETACHED_SETTINGS_NOT_SAVED")
        p = read_settings(self.path)
        if not p.has_section("Settings"):
            p.add_section("Settings")
        # RawConfigParser accepts text; match original field semantics and
        # do not touch shared grid_cols/grid_rows or any other feature keys.
        p.set("Settings", "detached_auto_open", "True" if auto_open else "False")
        p.set("Settings", "detached_grid", grid)
        write_settings(p, self.path)
