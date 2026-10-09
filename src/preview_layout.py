"""S14 C09/C17: preview-only grid and HWND-keyed logical ordering.

Verified original: default 2x, manual column choices 1x..5x, left/right
preview movement by -1/+1 and order retention keyed by HWND.
Not recovered: edge behavior, new-window insertion and same-HWND PID reuse.

S14 explicit local safety policy: out-of-range move does nothing; new HWNDs
append; a PID-reused HWND is treated as fresh and appended, preventing a stale
old account's position from silently controlling a new window.
No window focus/click, game input, licensing, fake game metadata or Proxy.
"""
from __future__ import annotations

from typing import Sequence
from start_windows import GameWindow

PREVIEW_GRID_CHOICES = ("1x", "2x", "3x", "4x", "5x")
DEFAULT_PREVIEW_GRID = "2x"
EDGE_POLICY = "S14_NO_WRAP_UNKNOWN_ORIGINAL"
NEW_SOURCE_POLICY = "S14_APPEND_UNKNOWN_ORIGINAL"
REUSED_HWND_POLICY = "S14_APPEND_NEW_PID_SAFETY"


def preview_columns(value: str) -> int:
    """Parse only evidenced combobox choices; do not invent other sizes."""
    if value not in PREVIEW_GRID_CHOICES:
        raise ValueError("Unsupported C09 preview grid: " + repr(value))
    return int(value[:-1])


def preview_position(index: int, columns: int) -> tuple[int, int]:
    if not isinstance(index, int) or index < 0 or not isinstance(columns, int) or not 1 <= columns <= 5:
        raise ValueError("Invalid preview position")
    return divmod(index, columns)


class PreviewOrder:
    """Retains logical HWND order with PID reuse fencing across live snapshots."""

    def __init__(self):
        self._order: tuple[int, ...] = ()
        self._pid: dict[int, int] = {}

    @property
    def hwnds(self) -> tuple[int, ...]:
        return self._order

    def update(self, windows: Sequence[GameWindow]) -> tuple[GameWindow, ...]:
        seen = set()
        current = {}
        for item in windows:
            if not isinstance(item, GameWindow) or item.hwnd <= 0 or item.pid <= 0:
                raise ValueError("Unverified HWND/PID in preview source")
            if item.hwnd in seen:
                raise ValueError("Duplicate HWND in preview source")
            seen.add(item.hwnd)
            current[item.hwnd] = item

        # A source's numerical HWND reused with a different PID is NEW, so
        # its old logical position cannot silently follow the old account.
        kept = [hwnd for hwnd in self._order
                if hwnd in current and self._pid[hwnd] == current[hwnd].pid]
        new = [item.hwnd for item in windows if item.hwnd not in kept]
        self._order = tuple(kept + new)
        self._pid = {hwnd: current[hwnd].pid for hwnd in self._order}
        return tuple(current[hwnd] for hwnd in self._order)

    def move(self, hwnd: int, pid: int, delta: int) -> bool:
        if delta not in (-1, 1) or self._pid.get(hwnd) != pid or hwnd not in self._order:
            return False
        idx = self._order.index(hwnd)
        target = idx + delta
        if target < 0 or target >= len(self._order):
            return False  # S14 conservative unknown edge: no wrap-around
        items = list(self._order)
        items[idx], items[target] = items[target], items[idx]
        self._order = tuple(items)
        return True

    def ordered(self, windows: Sequence[GameWindow]) -> tuple[GameWindow, ...]:
        return self.update(windows)

    def clear(self) -> None:
        self._order = ()
        self._pid.clear()
