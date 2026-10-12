"""S128 H02: real Tk radio/Spinbox and nav-priority UI -> real Farm INI.

Only original H02 user configuration is implemented. The lower town body
still lacks independently unbuilt Sell/Buy/Medicine controls, so this widget
must NOT be advertised as a full FarmTab or mounted as product gameplay UI.
No game HWND, movement, mouse action, real signed Info verifier or Proxy.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from farm_town_config import (
    FarmTownConfig, FarmTownSettingsStore, FarmTownSnapshot,
    NAV_METHODS, TOWN_RADIOS,
)
from permission_guard import PermissionGuard
from local_feature_policy import LocalFeaturePolicy


class TkFarmTownConfig(ttk.Frame):
    """Original H02 control behavior, backed by a real safe settings.ini.

    PermissionGuard MUST have been populated by an independently verified
    issuer; test-only fake verifier in CI is NOT an auth implementation.
    An external source-backed Farm-route observer may call apply_route_lock.
    The boolean can only force restrictive 'never', never grant permission.
    """

    def __init__(self, parent, *, store: FarmTownSettingsStore | None = None,
                 permission_guard: PermissionGuard | None = None,
                 running_count: Callable[[], int] | None = None):
        super().__init__(parent)
        self.store = store if store is not None else FarmTownSettingsStore()
        self.guard = permission_guard
        self.running_count = running_count
        self._closed = False
        self._updating = False
        self._locked_route = False
        self._body_visible = False
        self._blocked = False
        self.error: str | None = None
        self.snapshot: FarmTownSnapshot | None = None
        try:
            self.snapshot = self.store.load()
        except Exception as exc:
            self._blocked = True
            self.error = type(exc).__name__
        defaults = self.snapshot.value if self.snapshot else FarmTownConfig()
        self.mode_var = tk.StringVar(master=self, value=defaults.mode)
        self.minutes_var = tk.StringVar(master=self, value=defaults.minutes)
        self.nav_vars = [
            tk.StringVar(master=self, value=value)
            for value in defaults.navigation
        ]
        self.group = ttk.LabelFrame(self, text="Cấu hình Về thành")
        self.group.pack(fill="x", padx=5, pady=4)
        self.head = ttk.Frame(self.group)
        self.head.pack(fill="x", padx=6, pady=4)
        self.radios = []
        for text, mode in TOWN_RADIOS:
            radio = ttk.Radiobutton(
                self.head, text=text, value=mode, variable=self.mode_var,
                command=self._on_mode)
            radio.pack(side="left", padx=(0, 7))
            self.radios.append(radio)
        self.spin = ttk.Spinbox(self.head, textvariable=self.minutes_var,
                                width=6, from_=0, to=999999999)
        self.spin.pack(side="left")
        self.spin.bind("<Return>", self._on_minutes, add="+")
        self.spin.bind("<FocusOut>", self._on_minutes, add="+")
        # H02 original lower town pane begins hidden. Only its verified
        # priority subset exists here; other original settings remain absent.
        self.toggle = ttk.Button(
            self.group, text="Hiện cấu hình", command=self.toggle_lower_body)
        self.toggle.pack(anchor="e", padx=6, pady=(0, 3))
        self.lower = ttk.Frame(self.group)
        ttk.Label(self.lower, text="Phương thức về thành — Ưu tiên lần lượt:").pack(
            anchor="w", padx=6)
        self.nav_combos = []
        line = ttk.Frame(self.lower)
        line.pack(fill="x", padx=6, pady=3)
        for i in range(4):
            combo = ttk.Combobox(
                line, textvariable=self.nav_vars[i], width=9,
                values=NAV_METHODS, state="disabled")
            combo.pack(side="left", padx=(0, 5))
            combo.bind("<<ComboboxSelected>>",
                       lambda _ev, index=i: self._on_nav(index), add="+")
            self.nav_combos.append(combo)
        self.status = ttk.Label(self, text="")
        self.status.pack(fill="x", padx=6)
        self._refresh_options()
        self.reapply_permission()
        if self._blocked:
            self.status.configure(text="Cấu hình Về thành không an toàn để sửa")
        self.bind("<Destroy>", self._on_destroy, add="+")

    def _permitted(self) -> bool:
        # Independent tool's implemented local config is NOT TLM entitlement.
        if isinstance(self.guard, LocalFeaturePolicy):
            return (not self._closed and not self._blocked
                    and self.guard.config_available("farm_tab"))
        if (self._closed or self._blocked
                or type(self.guard) is not PermissionGuard
                or not callable(self.running_count)):
            return False
        try:
            count = self.running_count()
            return (type(count) is int and count > 0
                    and self.guard.snapshot.has_verified_payload
                    and self.guard.has_permission_with_limit("farm_tab", count))
        except Exception:
            return False

    def reapply_permission(self) -> None:
        allowed = self._permitted()
        for radio in self.radios:
            radio.configure(state="normal" if allowed and not self._locked_route
                            else "disabled")
        self.spin.configure(state="normal" if allowed else "disabled")
        self.toggle.configure(state="normal" if allowed else "disabled")
        for combo in self.nav_combos:
            combo.configure(state="readonly" if allowed else "disabled")

    def _refresh_options(self) -> None:
        # A method is offered once across the four priority rows; blank is
        # reusable. Recompute available values without destroying each
        # currently selected valid value.
        selected = tuple(x.get() for x in self.nav_vars)
        for index, combo in enumerate(self.nav_combos):
            used = {value for i, value in enumerate(selected)
                    if i != index and value}
            available = tuple(
                value for value in NAV_METHODS
                if not value or value == selected[index] or value not in used)
            combo.configure(values=available)

    def _restore(self) -> None:
        if self.snapshot is None:
            return
        value = self.snapshot.value
        self._updating = True
        try:
            self.mode_var.set(value.mode)
            self.minutes_var.set(value.minutes)
            for variable, method in zip(self.nav_vars, value.navigation):
                variable.set(method)
            self._refresh_options()
        finally:
            self._updating = False

    def _commit(self, candidate: FarmTownConfig) -> bool:
        if self._updating or not self._permitted() or self.snapshot is None:
            self._restore()
            return False
        try:
            candidate.validated()
            self.snapshot = self.store.save(
                candidate, expected_bytes=self.snapshot.file_bytes)
        except Exception as exc:
            self.error = type(exc).__name__
            self.status.configure(text="Không lưu: dữ liệu cũ được giữ nguyên")
            self._restore()
            return False
        self.error = None
        self.status.configure(text="Đã lưu cấu hình Về thành")
        self._restore()
        return True

    def _on_mode(self) -> bool:
        if self.snapshot is None or self._locked_route:
            self._restore()
            return False
        return self._commit(self.snapshot.value.change_mode(self.mode_var.get()))

    def _on_minutes(self, _event=None) -> bool:
        if self.snapshot is None:
            self._restore()
            return False
        try:
            proposal = self.snapshot.value.change_minutes(self.minutes_var.get())
        except Exception:
            self._restore()
            return False
        return self._commit(proposal)

    def _on_nav(self, index: int) -> bool:
        if self.snapshot is None:
            self._restore()
            return False
        try:
            proposal = self.snapshot.value.change_nav(
                index, self.nav_vars[index].get())
        except Exception:
            self._restore()
            return False
        result = self._commit(proposal)
        self._refresh_options()
        return result

    def apply_route_lock(self, locked: bool) -> bool:
        """Require external H02 route-lock evidence; true only RESTRICTS.

        A real Farm account-route producer has not yet been wired. This
        method is not bound to Tk button and cannot start a game action.
        """
        if type(locked) is not bool or self._closed or self.snapshot is None:
            return False
        if locked:
            # Fail closed on disk write error: do not claim a successful
            # persisted lock if the old auto-town mode could remain stored.
            if self.snapshot.value.mode != "never":
                if not self._commit(self.snapshot.value.change_mode("never")):
                    return False
            self._locked_route = True
        else:
            self._locked_route = False
        self.reapply_permission()
        return True

    def toggle_lower_body(self) -> bool:
        if not self._permitted():
            return False
        self._body_visible = not self._body_visible
        if self._body_visible:
            self.lower.pack(fill="x", padx=5, pady=3)
            self.toggle.configure(text="Ẩn cấu hình")
        else:
            self.lower.pack_forget()
            self.toggle.configure(text="Hiện cấu hình")
        return self._body_visible

    def _on_destroy(self, event) -> None:
        if event.widget is self:
            self._closed = True
