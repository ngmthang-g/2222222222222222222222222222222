"""Owner-selected independent rebuild policy; NEVER a TLM license emulator.

Only source-backed local capabilities are exposed. OS, HWND/PID, process
identity, disk-safety, and actual-game readiness checks are separate.
Historical permission_guard.py remains for forensic comparisons only.
"""
from __future__ import annotations

from dataclasses import dataclass

LOCAL_TAB_KEYS = frozenset({"info_tab", "start_tab", "login_tab", "party_tab", "farm_tab", "trainlsv_tab", "rao_tab", "toiuu_tab"})


@dataclass(frozen=True)
class LocalFeaturePolicy:
    """Explicit local code availability, not permissions from TLM's server.

    A registered module is a config/read-only UI capability, NOT proof of
    an implemented gameplay sender. An empty set never unlocks anything.
    """

    available: frozenset[str]

    def __post_init__(self):
        if (type(self.available) is not frozenset
                or any(type(k) is not str or k not in LOCAL_TAB_KEYS
                       for k in self.available)):
            raise ValueError("UNIMPLEMENTED_OR_INVALID_LOCAL_FEATURE")

    def config_available(self, key: str) -> bool:
        return key in self.available

    def window_observation_allowed(self, key: str, running: int) -> bool:
        # Read-only observation still requires actual live processes and
        # independent native HWND/PID verification at the call site.
        return (self.config_available(key) and type(running) is int
                and running > 0)
