"""S89: functional original-backed Party configuration widgets (G01/G08 only).

This is a composable partial configuration section. It is deliberately NOT
registered as PartyTab: create/invite/leave/team run/RoleName are unavailable.
The controls shown here only change and actually persist original Party
settings. No fake run, game actions, process identity or authorization.
"""
from __future__ import annotations

from tkinter import ttk
import tkinter as tk
from typing import Callable, Sequence

from party_group_config import (
    AFTER_LABELS, AFTER_VALUES, MAX_GROUP_MEMBERS,
    PartyConfigStore, PartySettings,
)


class PartySettingsEditor(ttk.Frame):
    """G01 after-Party selection and G08 real group-config edit operations."""

    def __init__(self, parent, *, store: PartyConfigStore,
                 available_names: Callable[[], Sequence[str]]):
        if not isinstance(store, PartyConfigStore) or not callable(available_names):
            raise ValueError("Verified config store and external name provider required")
        super().__init__(parent)
        self.store = store
        self.available_names = available_names
        self.state = store.load()  # read-only; never rewrite during restore
        self.last_error = ""
        self.mode_var = tk.StringVar(value=AFTER_LABELS[AFTER_VALUES.index(self.state.after)])
        self.after_box = ttk.LabelFrame(self, text="Sau khi party")
        self.after_box.pack(fill="x", padx=4, pady=3)
        ttk.Label(self.after_box, text="Sau khi party:").pack(side="left", padx=4)
        self.mode_combo = ttk.Combobox(
            self.after_box, state="readonly", textvariable=self.mode_var,
            values=AFTER_LABELS, width=15)
        self.mode_combo.pack(side="left", padx=4)
        self.mode_combo.bind("<<ComboboxSelected>>", self._change_after, add="+")
        self.group_box = ttk.LabelFrame(self, text="Cấu hình nhóm")
        self.group_box.pack(fill="both", expand=True, padx=4, pady=3)
        self.clusters = ttk.Frame(self.group_box)
        self.clusters.pack(fill="x", padx=4, pady=3)
        self.group_inputs = []
        self.remove_buttons = []
        self.add_btn = ttk.Button(
            self.group_box, text="+ Thêm nhóm", command=self.add_group)
        self.add_btn.pack(anchor="w", padx=4, pady=2)
        self.status = ttk.Label(self, text="", anchor="w")
        self.status.pack(fill="x", padx=4)
        self._render_groups()

    def _names(self) -> tuple[str, ...]:
        # RoleName comes from original G02/G03 shared character reader in
        # production. A TEST-owned supplier can populate the offline editor,
        # but the widget itself must NEVER invent name/HWND/RoleID data.
        raw = self.available_names()
        if not isinstance(raw, (list, tuple)):
            raise ValueError("Live Party names must be an explicit sequence")
        return tuple(dict.fromkeys(
            x.strip() for x in raw if type(x) is str and x.strip()))

    def _persist(self, updated: PartySettings, *, redraw: bool = True) -> bool:
        try:
            self.store.save(updated)
        except (OSError, ValueError, RuntimeError) as exc:
            self.last_error = type(exc).__name__
            self.status.configure(text="Không thể lưu cấu hình Party")
            self.mode_var.set(AFTER_LABELS[AFTER_VALUES.index(self.state.after)])
            return False
        self.state = updated
        self.last_error = ""
        self.status.configure(text="Đã lưu cấu hình Party")
        if redraw:
            self._render_groups()
        return True

    def _change_after(self, _event=None):
        value = self.mode_var.get()
        if value not in AFTER_LABELS:
            self.mode_var.set(AFTER_LABELS[AFTER_VALUES.index(self.state.after)])
            return False
        return self._persist(self.state.change_after(AFTER_VALUES[AFTER_LABELS.index(value)]),
                             redraw=False)

    def _selection(self, group_num: int, slot: int, variable: tk.StringVar):
        value = variable.get()
        # The readonly Combo may keep a saved/offline name; do not synthesize
        # a current game HWND from it. Selection edits configuration ONLY.
        choices = self._names()
        if value and value not in choices:
            self._render_groups()
            return False
        try:
            state = self.state.select_member(group_num, slot, value)
        except ValueError:
            self._render_groups()
            return False
        return self._persist(state)

    def add_group(self) -> bool:
        return self._persist(self.state.add_group())

    def remove_group(self, num: int) -> bool:
        try:
            next_state = self.state.remove_group(num)
        except ValueError:
            return False
        return next_state != self.state and self._persist(next_state)

    def _render_groups(self) -> None:
        # Deliberately no game action controls; they require actual G09/G10
        # worker + real Info grant + RoleID/TeamID/protocol parity.
        for child in self.clusters.winfo_children():
            child.destroy()
        self.group_inputs.clear()
        self.remove_buttons.clear()
        names = self._names()
        used_before = set()
        for group in self.state.groups:
            frame = ttk.LabelFrame(self.clusters, text=f"Nhóm {group.num}")
            frame.pack(fill="x", padx=2, pady=3)
            remove = ttk.Button(
                frame, text=f"✕ Xóa {group.num}",
                command=lambda num=group.num: self.remove_group(num))
            remove.grid(row=0, column=2, sticky="e", padx=4)
            if len(self.state.groups) == 1:
                remove.configure(state="disabled")
            self.remove_buttons.append(remove)
            inputs = []
            for slot in range(MAX_GROUP_MEMBERS):
                chosen = group.members[slot] if slot < len(group.members) else ""
                options = ("",) + tuple(
                    name for name in names
                    if name not in used_before or name == chosen)
                value = tk.StringVar(value=chosen)
                combo = ttk.Combobox(
                    frame, state="readonly", textvariable=value,
                    values=options, width=18)
                combo.grid(row=1 + slot // 3, column=slot % 3,
                           padx=3, pady=2, sticky="w")
                combo.bind(
                    "<<ComboboxSelected>>",
                    lambda _ev, num=group.num, idx=slot, var=value:
                        self._selection(num, idx, var),
                    add="+")
                inputs.append(combo)
            self.group_inputs.append(inputs)
            used_before.update(name for name in group.members if name)
