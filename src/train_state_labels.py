"""S127 H12: passive original Farm state text + dot-color projection.

The original frozen farm_data.STATE_STYLE documents these eleven label colors.
This module NEVER infers Farm running from a HWND or locally grants Info.
Only a future verified Farm lifecycle may supply a row-bound state + generation.
Exact generation increment/transition order in the compiled EXE is UNKNOWN;
the monotonic stale-update guard is a conservative implementation boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType

DEFAULT_STATE = "Đã dừng"
DEFAULT_COLOR = "#555555"
STATE_COLORS = MappingProxyType({
    "Đã dừng": "#555555",
    "Về bán đồ": "#1565c0",
    "Bán đồ": "#1565c0",
    "Mua thuốc": "#555555",
    "Trị liệu": "#555555",
    "Tới bãi train": "#1565c0",
    "Đang train": "#2e7d32",
    "Về địa phủ": "#c62828",
    "Đang hồi sinh": "#e65100",
    "Đang lọc đồ": "#8e24aa",
    "Mất kết nối": "#b71c1c",
})


def color_for_state(value: str) -> str:
    """Unknown dynamic original state strings use the documented gray."""
    return STATE_COLORS.get(value, DEFAULT_COLOR) if type(value) is str else DEFAULT_COLOR


@dataclass
class PassiveTrainState:
    """Row-local state, NEVER an observed/authorized game lifecycle itself."""
    text: str = DEFAULT_STATE
    generation: int = -1

    @property
    def color(self) -> str:
        return color_for_state(self.text)

    def accept_confirmed(self, text: str, generation: int) -> bool:
        """Caller MUST already hold a genuine verified Farm-event source.

        Numeric generation is an external row-session stamp, never created
        by this model. Reject old events; within the same generation multiple
        states can be emitted in order on the Tk owner thread.
        """
        if (type(text) is not str or not text or len(text) > 160
                or type(generation) is not int or generation < 0
                or generation < self.generation):
            return False
        self.text = text
        self.generation = generation
        return True

    def reset(self) -> None:
        """On Info revoke or identity loss, cannot claim live gameplay."""
        self.text = DEFAULT_STATE
        self.generation = -1
