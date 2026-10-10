"""S91: G02 real Party ready-member list, 3 accounts per row, composable ONLY.

Original source-backed G02 behavior:
- "Cấu hình tổ đội" / "Danh sách acc sẵn sàng:"
- a 3-column Tk grid of live RoleName-derived member names
- already-selected members hidden from ready list
- Combo options updated with live roster, earlier clusters reserved,
  saved selection stays visible even when offline

S90 provides HWND+PID generation checks. S89 provides durable Party group
editing. There is NO real RoleName reader, signed Info, team action or complete
PartyTab/EXE in this module. Never use HWND/title to guess a name.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from auto_role_provenance import RoleReading
from party_group_config import PartyConfigStore
from party_roster import PartyRoster, TkPartyRosterRefresh
from party_settings_editor import PartySettingsEditor


READY_COLUMNS = 3


class PartyReadyList(ttk.LabelFrame):
    """Render only externally verified S90 RoleName readings, not account IDs."""

    def __init__(self, parent):
        super().__init__(parent, text="Cấu hình tổ đội")
        ttk.Label(self, text="Danh sách acc sẵn sàng:").pack(
            anchor="w", padx=4, pady=(3, 1))
        self.body = ttk.Frame(self)
        self.body.pack(fill="x", padx=4, pady=3)
        self.labels: list[ttk.Label] = []
        self.names: tuple[str, ...] = ()

    def show(self, roster: PartyRoster, selected: tuple[str, ...] = ()) -> None:
        if not isinstance(roster, PartyRoster):
            raise TypeError("Ready accounts require a verified PartyRoster")
        names = roster.ready_names(selected)
        if names == self.names:
            return
        # Destroy obsolete rows: never retain a label from an old PID
        # generation, invalid Start cache or stopped Party consumer.
        for child in self.body.winfo_children():
            child.destroy()
        self.labels = []
        self.names = names
        for index, name in enumerate(names):
            label = ttk.Label(self.body, text=name)
            label.grid(row=index // READY_COLUMNS,
                       column=index % READY_COLUMNS,
                       sticky="w", padx=4, pady=2)
            self.labels.append(label)


class PartyReadyConfigEditor(PartySettingsEditor):
    """S89 config editor + S90 genuine generation roster + G02 ready list.

    This is NOT registered as the original PartyTab. In particular no team
    create/leave buttons, automatic matching, packet sender or fake names.
    """

    def __init__(self, parent, *, store: PartyConfigStore,
                 start_producer, read_role: Callable[[int, int], RoleReading] | None = None):
        self._roster = PartyRoster()
        self._closing_ready = False
        super().__init__(
            parent, store=store, available_names=lambda: self._roster.ready_names())
        self.ready_list = PartyReadyList(self)
        # Original G01 order: "Sau khi party", "Cấu hình tổ đội", "Cấu hình nhóm".
        self.ready_list.pack(fill="x", padx=4, pady=3, before=self.group_box)
        self._roster_reader = TkPartyRosterRefresh(
            self, start_producer, self._on_roster,
            read_role=read_role)
        self.bind("<Destroy>", self._on_destroy, add="+")
        self._refresh_ready()
        self._roster_reader.start()

    def _selected_names(self) -> tuple[str, ...]:
        return tuple(name for group in self.state.groups
                     for name in group.members if name)

    def _refresh_ready(self) -> None:
        self.ready_list.show(self._roster, self._selected_names())

    def _refresh_dropdown_values(self) -> None:
        """Refresh options without replacing existing focused Tk Comboboxes."""
        live = self._roster.ready_names()
        used_before: set[str] = set()
        for group, combos in zip(self.state.groups, self.group_inputs):
            for combo in combos:
                current = combo.get()
                opts = ("",) + tuple(
                    name for name in live if name not in used_before
                    or name == current)
                # Keep saved offline choice rather than discard from config.
                if current and current not in opts:
                    opts += (current,)
                combo.configure(values=tuple(dict.fromkeys(opts)))
            used_before.update(name for name in group.members if name)

    def _on_roster(self, roster: PartyRoster) -> None:
        if self._closing_ready:
            return
        self._roster = roster
        self._refresh_ready()
        self._refresh_dropdown_values()

    def _persist(self, updated, *, redraw=True) -> bool:
        ok = super()._persist(updated, redraw=redraw)
        # Parent __init__ does not save, so ready_list exists for all edits.
        if ok and hasattr(self, "ready_list"):
            self._refresh_ready()
            self._refresh_dropdown_values()
        return ok

    def shutdown(self) -> None:
        if self._closing_ready:
            return
        self._closing_ready = True
        if hasattr(self, "_roster_reader"):
            self._roster_reader.shutdown()
        self._roster.clear("STOPPED")
        if hasattr(self, "ready_list") and self.ready_list.winfo_exists():
            self.ready_list.show(self._roster)

    def _on_destroy(self, event) -> None:
        if event.widget is self:
            self.shutdown()
