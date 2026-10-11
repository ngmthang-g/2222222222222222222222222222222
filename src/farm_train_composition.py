"""S132: compose only already source-backed Train Tk settings/readonly rows.

Original H01/B05 order: Về thành (hidden lower sell/nav), Train config +
manual buff, saved coordinates, passive HWND/PID account list.
S128/129/130/131 configuration implementations remain unchanged.
No fake Farm start/sell/buy/auto-buff buttons, no game packets/memory,
no proxy, no invented populated-row geometry and NO product tab grant.
Only a real independently verified farm_tab PermissionGuard from a host
may unlock edit-capable H11 coordinates and S123 passive account rows.

The composition adds a *cross-panel INI rebase* after successful writes,
because the S128–S131 stores intentionally reject stale snapshots: without
the rebase changing one original settings section would leave all other
subpanels trying to write out-of-date file bytes.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Callable

from permission_guard import PermissionGuard
from farm_town_panel import TkFarmTownConfig
from farm_town_config import FarmTownSettingsStore
from farm_town_trade_panel import TkFarmTownTradeSettings
from farm_town_trade_settings import TownTradeStore
from farm_train_panel import TkFarmTrainSettings
from farm_train_settings import FarmTrainSettingsStore
from farm_buff_editor import TkFarmBuffEditor
from farm_buff_settings import FarmBuffSettingsStore
from farm_saved_editor import FarmSavedCoordinatesEditor
from train_saved_coordinates import FarmCoordinatesStore
from train_account_rows import TkTrainAccountRows, TRAIN_ACCOUNT_REFRESH_MS
from start_polling import StartWindowProducer, WindowSnapshot
from start_windows import GameWindow

TRAIN_SECTIONS = ("Cấu hình Về thành", "Cấu hình Train",
                  "Cấu hình tọa độ lưu sẵn", "Danh sách tài khoản")


class TkTrainComposition(ttk.Frame):
    """Actual Tk config composition, deliberately NOT a playable FarmTab.

    Life cycle owner must call reapply_permissions() on Info/Start changes;
    start_readonly_window_refresh() starts only native passive HWND reading
    AFTER independent farm permission + account-limit proof. No startup
    side effects, no fabricated gameplay buttons.
    """

    def __init__(self, parent, *, settings_file: str | Path,
                 permission_guard: PermissionGuard | None = None,
                 running_count: Callable[[], int] | None = None,
                 window_producer: StartWindowProducer | None = None,
                 allow_account: Callable[[GameWindow], bool] | None = None,
                 identity_backend_factory=None):
        if not isinstance(settings_file, (str, Path)) or not str(settings_file):
            raise ValueError("EXPLICIT_SHARED_FARM_SETTINGS_REQUIRED")
        super().__init__(parent)
        self.settings_file = Path(settings_file)
        self.guard = permission_guard
        self.running_count = running_count
        self.window_producer = window_producer
        self.allow_account = allow_account
        self.identity_backend_factory = identity_backend_factory
        self._closed = False
        self._syncing = False
        self._readonly_refresh_requested = False
        self._sensitive_host = None
        self.coords: FarmSavedCoordinatesEditor | None = None
        self.accounts: TkTrainAccountRows | None = None
        self._coord_change_wrapped = False
        # Use one unique file for ALL original [Farm] config families.
        common = {"permission_guard":permission_guard,
                  "running_count":running_count}
        self.town = TkFarmTownConfig(
            self, store=FarmTownSettingsStore(self.settings_file), **common)
        self.trade = TkFarmTownTradeSettings(
            self.town.lower, store=TownTradeStore(self.settings_file), **common)
        self.trade.pack(fill="x")
        self.train = TkFarmTrainSettings(
            self, store=FarmTrainSettingsStore(self.settings_file), **common)
        self.train.pack(fill="x")
        # The original manual medicine/buff block belongs to Train config,
        # never before H02 town nor after H11 coordinate/account areas.
        self.buffs = TkFarmBuffEditor(
            next(w for w in self.train.winfo_children() if isinstance(w, ttk.LabelFrame) and str(w.cget('text')) == 'Cấu hình Train'), store=FarmBuffSettingsStore(self.settings_file),
            **common)
        self.buffs.pack(fill="x")
        self.coords_section = ttk.Frame(self)
        self.coords_section.pack(fill="x")
        self.coords_status = ttk.Label(
            self.coords_section, text="Cấu hình tọa độ lưu sẵn: cần quyền Farm")
        self.coords_status.pack(fill="x")
        self.accounts_section = ttk.LabelFrame(self, text="Danh sách tài khoản")
        self.accounts_section.pack(fill="both", expand=True)
        self.accounts_status = ttk.Label(
            self.accounts_section, text="Chưa xác minh quyền Farm / cửa sổ game")
        self.accounts_status.pack(fill="x")
        # Retain original source B05 all-account action names only as audit:
        # do NOT render interactive but inert Tới bán/Bán/Tới train/Đánh or
        # a fake green Bắt đầu Farm button. Not a finished 1:1 FarmTab.
        self._install_cross_panel_rebases()
        self.reapply_permissions()
        self.bind("<Destroy>", self._on_destroy, add="+")

    def _authorized(self) -> bool:
        if (self._closed or type(self.guard) is not PermissionGuard
                or not callable(self.running_count)):
            return False
        try:
            current = self.running_count()
            return (type(current) is int and current > 0
                    and self.guard.snapshot.has_verified_payload
                    and self.guard.has_permission_with_limit("farm_tab",current))
        except Exception:
            return False

    def _install_cross_panel_rebases(self) -> None:
        """Decorate only this composition's S128–S131 live instances.

        A successful real disk commit is followed by clean rereads of ALL
        other source-backed stores, so no other control loses its optimistic
        concurrency token. The original individual modules stay byte-identical.
        """
        for panel in (self.town, self.trade, self.train, self.buffs):
            original = panel._commit
            def delegate(*args, _original=original, _source=panel, **kwargs):
                result = _original(*args, **kwargs)
                if result and not self._syncing and not self._closed:
                    self.sync_from_disk(exclude=_source)
                return result
            panel._commit = delegate

    def sync_from_disk(self, *, exclude=None) -> bool:
        """Rebase verified independent INI snapshots, never *write* on sync.

        A failed/unsafe section stays denied in its existing child editor.
        No silent game action, account start or password change.
        """
        if self._closed or self._syncing:
            return False
        self._syncing = True
        successful = True
        try:
            for panel in (self.town,self.trade,self.train,self.buffs):
                if panel is exclude or panel._blocked or panel._closed:
                    continue
                try:
                    panel.snapshot=panel.store.load()
                    if panel is self.buffs:
                        panel._render()
                    else:
                        panel._restore()
                except Exception as exc:
                    panel.error=type(exc).__name__
                    successful=False
            # Coordinates may have been saved by an independent H11 editor.
            if self.coords is not None:
                try:
                    choices = self.coords.store.load()
                    if (choices.rows != self.coords.rows
                            or bool(choices.skipped_retired_map_ids) != self.coords._blocked):
                        self.coords._load_initial()
                except Exception:
                    successful=False
            if not self.trade.refresh_destinations():
                successful=False
            # Rebase the standalone train H06 saved-heal choices.
            if not self.train.refresh_heal_destinations():
                successful=False
        finally:
            self._syncing = False
        self._reapply_all_controls()
        return successful

    def _reapply_all_controls(self):
        for widget in (self.town,self.trade,self.train,self.buffs):
            widget.reapply_permission()
        if self.accounts is not None:
            self.accounts.reapply_permissions()

    def _bind_coordinate_actions(self):
        """H11 editor existed before S124; guard its callbacks at integration.

        This wrapper also guards direct callback calls made before the UI
        owner processes an Info revocation, without modifying legacy source.
        """
        editor=self.coords
        if editor is None:
            return
        for name in ("commit_row","delete_row","apply_row_to_all"):
            original=getattr(editor,name)
            def guard_it(*args, _method=original, _name=name, **kwargs):
                if self._closed or not self._authorized() or self.coords is not editor:
                    return 0 if _name=="apply_row_to_all" else False
                result=_method(*args,**kwargs)
                if result and _name in ("commit_row","delete_row"):
                    self.sync_from_disk()
                return result
            setattr(editor,name,guard_it)

    def _make_sensitive(self):
        """Create original H11 editor/S123 rows only with real verified right."""
        if not self._authorized() or self.coords is not None or self._closed:
            return False
        host=ttk.Frame(self.coords_section)
        # Validate/load the real coord store before hiding the block-status.
        editor=FarmSavedCoordinatesEditor(
            host,store=FarmCoordinatesStore(self.settings_file))
        editor.pack(fill="x")
        if editor._blocked:
            editor.destroy();host.destroy()
            self.coords_status.configure(text="Tọa độ chưa an toàn để chỉnh sửa")
            return False
        host.pack(fill="x")
        self._sensitive_host=host
        self.coords=editor
        self._bind_coordinate_actions()
        self.coords_status.pack_forget()
        self.accounts_status.configure(text="Chưa có danh tính cửa sổ xác minh")
        # H01 account section: actual Canvas+Scrollbar, not fake account rows.
        self.accounts_canvas=tk.Canvas(self.accounts_section,
                                       highlightthickness=0, height=180)
        self.accounts_scrollbar=ttk.Scrollbar(
            self.accounts_section, orient="vertical",
            command=self.accounts_canvas.yview)
        self.accounts_canvas.configure(yscrollcommand=self.accounts_scrollbar.set)
        self.accounts_scrollbar.pack(side="right",fill="y")
        self.accounts_canvas.pack(side="left",fill="both",expand=True)
        self.accounts_host=ttk.Frame(self.accounts_canvas)
        self.accounts_window=self.accounts_canvas.create_window(
            0,0,window=self.accounts_host,anchor="nw")
        self.accounts_host.bind(
            "<Configure>",
            lambda _ev: self.accounts_canvas.configure(
                scrollregion=self.accounts_canvas.bbox("all")),add="+")
        self.accounts_canvas.bind(
            "<Configure>",
            lambda ev: self.accounts_canvas.itemconfigure(
                self.accounts_window,width=ev.width),add="+")
        self.accounts=TkTrainAccountRows(
            self.accounts_host,editor,
            producer=self.window_producer,
            allow_account=self.allow_account,
            interval_ms=TRAIN_ACCOUNT_REFRESH_MS,
            permission_guard=self.guard,
            running_count=self.running_count,
            identity_backend_factory=self.identity_backend_factory)
        if self._readonly_refresh_requested:
            self.accounts._start_refresh()
        return True

    def _teardown_sensitive(self):
        if self.accounts is not None:
            self.accounts.shutdown()
            self.accounts.container.destroy()
            self.accounts=None
        if self.coords is not None:
            self.coords.destroy()
            self.coords=None
        if self._sensitive_host is not None:
            self._sensitive_host.destroy()
            self._sensitive_host=None
        if hasattr(self,"accounts_canvas"):
            self.accounts_canvas.destroy()
            self.accounts_scrollbar.destroy()
            self.accounts_host=None
            del self.accounts_canvas
            del self.accounts_scrollbar
        self._readonly_refresh_requested=False
        if not self._closed:
            self.coords_status.configure(
                text="Cấu hình tọa độ lưu sẵn: cần quyền Farm")
            self.coords_status.pack(fill="x")
            self.accounts_status.configure(
                text="Chưa xác minh quyền Farm / cửa sổ game")

    def reapply_permissions(self) -> bool:
        """Owner calls on signed Info/Start changes, in addition to row ticks."""
        if self._closed:
            return False
        self._reapply_all_controls()
        if not self._authorized():
            self._teardown_sensitive()
            return False
        if self.coords is None:
            return self._make_sensitive()
        return True

    def start_readonly_window_refresh(self) -> bool:
        """Start real S09 HWND reading only after external verified permission."""
        if not self.reapply_permissions() or self.accounts is None:
            return False
        self._readonly_refresh_requested=True
        self.accounts._start_refresh()
        return self.accounts._active

    def stop_readonly_window_refresh(self) -> None:
        self._readonly_refresh_requested=False
        if self.accounts is not None:
            self.accounts._stop_refresh()

    def apply_trusted_window_snapshot(self, snapshot: WindowSnapshot) -> bool:
        """Tk-owner caller may supply genuine S09 snapshot; no forged rows."""
        return bool(self.reapply_permissions() and self.accounts is not None
                    and self.accounts.apply_snapshot(snapshot))

    def shutdown(self) -> None:
        if self._closed:
            return
        self._teardown_sensitive()
        self._closed=True

    def _on_destroy(self,event) -> None:
        if event.widget is self:
            self.shutdown()
