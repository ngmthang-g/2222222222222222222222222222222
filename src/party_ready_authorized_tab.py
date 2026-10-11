"""S155 — G02 Party ready list with original E03 tab selected lifecycle.

G02 has a 3-second read-only cached Start HWND consumer. S90/S91 already
implemented its true list, 3-column Tk widgets, selected-name suppression,
stale HWND/PID rejection, and stopping. This adapter ONLY hooks that
already verified component into E03's select/deselect lifecycle.

A real RoleName reader is still UNKNOWN; no production external reader is
installed. Never infer a character name from a window title/HWND or save PID.
"""
from __future__ import annotations

from party_ready_list import PartyReadyConfigEditor


class AuthorizedPartyReadyTab(PartyReadyConfigEditor):
    """G02 passive roster + G08 real config; NO G09/G10 game actions."""

    def _start_refresh(self) -> None:
        if not self._closing_ready and self.winfo_exists():
            self._roster_reader.start()

    def _stop_refresh(self) -> None:
        if not self._closing_ready:
            self._roster_reader.stop()
