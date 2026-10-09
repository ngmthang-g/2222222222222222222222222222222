"""Small verified TLMMainApp shell slice.

The Info startup service and feature controllers are NOT reconstructed in S01.
This module never grants permissions; callers must supply authorized keys.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping


class MissingFeatureError(RuntimeError):
    """A real tab constructor/authorization service has not been rebuilt."""


@dataclass(frozen=True)
class TabSpec:
    key: str
    label: str


# From E03_TAB_ORDER.tsv. The usual 11-tab screenshot is NOT a grant policy.
TAB_SPECS = (
    TabSpec('start_tab', '▶'), TabSpec('login_tab', 'Login'),
    TabSpec('party_tab', 'Party'), TabSpec('farm_tab', 'Train'),
    TabSpec('trainlsv_tab', 'Train LSV'), TabSpec('emu_farm_tab', 'Train LD'),
    TabSpec('phoban_tab', 'Phó Bản'), TabSpec('daily_tab', 'Daily'),
    TabSpec('donvang_tab', 'Dồn'), TabSpec('rao_tab', 'Rao'),
    TabSpec('toiuu_tab', 'Tối ưu'), TabSpec('info_tab', 'ℹ'),
    TabSpec('proxy_tab', 'Proxy'), TabSpec('debug_tab', '🔎'),
    TabSpec('android_tab', '🔍'),
)
INFO_KEY = 'info_tab'
ALL_KEYS = frozenset(s.key for s in TAB_SPECS)
DEV_KEYS = frozenset({'proxy_tab', 'debug_tab', 'android_tab'})


class TabLifecycle:
    """Model-only tab authorization, lazy factories and selected refresh.

    Authorization is **provided** by Info/permission_guard; this object NEVER
    decides entitlements. Missing constructors can never become visible tabs.
    """

    def __init__(self, builders: Mapping[str, Callable[[Any], Any]], frames: Mapping[str, Any]):
        if INFO_KEY not in builders:
            raise MissingFeatureError('InfoTab factory is required; no dummy Info view allowed')
        if set(frames) != ALL_KEYS:
            raise ValueError('Frames must match original E03 potential tab slots')
        unknown = set(builders) - ALL_KEYS
        if unknown:
            raise ValueError('Unknown tab factories: ' + repr(sorted(unknown)))
        self._builders = dict(builders)
        self._frames = dict(frames)
        self._instances: dict[str, Any] = {}
        self.visible = {INFO_KEY}
        self.current = INFO_KEY
        self._active_refresh: str | None = None
        self._closed = False

    def ensure_built(self, key: str) -> Any:
        if self._closed:
            raise MissingFeatureError('Closed tab lifecycle cannot build widgets')
        if key not in self.visible or key not in self._builders:
            raise MissingFeatureError('Unapproved or unimplemented tab: ' + key)
        if key not in self._instances:
            # Failed constructors are not cached or treated as implemented.
            self._instances[key] = self._builders[key](self._frames[key])
        return self._instances[key]

    def apply_authorized_keys(self, authorized: set[str] | frozenset[str], *, dev_allowed: bool = False,
                              blocked: bool = False) -> frozenset[str]:
        """Caller passes ALREADY VERIFIED server/plan grants (not a local grant).

        No guessed fallback when no Info heartbeat / license data is available.
        """
        if self._closed:
            return frozenset({INFO_KEY})
        if not set(authorized) <= ALL_KEYS:
            raise ValueError('Unknown keys in permission snapshot')
        new_visible = {INFO_KEY}
        if not blocked:
            new_visible |= (set(authorized) & set(self._builders) - {INFO_KEY})
            if not dev_allowed:
                new_visible -= DEV_KEYS
        if self.current not in new_visible:
            self.select(INFO_KEY)
        self.visible = new_visible
        return frozenset(new_visible)

    def select(self, key: str) -> Any:
        if self._closed:
            raise MissingFeatureError('Closed tab lifecycle cannot select widgets')
        if key not in self.visible:
            key = INFO_KEY
        instance = self.ensure_built(key)
        if key != self.current or self._active_refresh != key:
            self._stop_old_refresh()
            self.current = key
            cb = getattr(instance, '_start_refresh', None)
            if callable(cb):
                cb()
                self._active_refresh = key
        return instance

    def _stop_old_refresh(self) -> None:
        key, self._active_refresh = self._active_refresh, None
        if key is not None:
            obj = self._instances.get(key)
            cb = getattr(obj, '_stop_refresh', None)
            if callable(cb):
                cb()

    def shutdown(self) -> None:
        """E08: stop the active refresh, then close each built tab OWNER once.

        A failing owner must not prevent cleanup of other owners. This is
        local bounded cleanup, not a game-window or forwarder-kill policy.
        """
        if self._closed:
            return
        self._closed = True
        error = None
        try:
            self._stop_old_refresh()
        except Exception as exc:
            error = exc
        for obj in reversed(tuple(self._instances.values())):
            close = getattr(obj, 'shutdown', None)
            if callable(close):
                try:
                    close()
                except Exception as exc:
                    if error is None:
                        error = exc
        self.visible = {INFO_KEY}
        self.current = INFO_KEY
        if error is not None:
            raise error


class TLMMainApp:
    """Small real Tk Notebook shell; no unimplemented functional controls.

    Requires the reconstructed real InfoTab at construction; without it the
    production entrypoint refuses to open a deceptive blank shell.
    """

    def __init__(self, root: Any, builders: Mapping[str, Callable[[Any], Any]], *,
                 notebook_factory: Callable[..., Any] | None = None,
                 frame_factory: Callable[..., Any] | None = None):
        if INFO_KEY not in builders:
            raise MissingFeatureError('S01: real InfoTab/authentication has not been reconstructed')
        if notebook_factory is None or frame_factory is None:
            from tkinter import ttk
            notebook_factory = notebook_factory or ttk.Notebook
            frame_factory = frame_factory or ttk.Frame
        self.root = root
        self._closed = False
        self.root.title('TLMTool')
        self.root.geometry('250x20')  # E02 transient only
        self.root.withdraw()
        self.root.option_add('*Font', ('Segoe UI', 9))
        self.root.attributes('-topmost', True)
        self.notebook = notebook_factory(root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        self._tab_frames = {}
        self._tab_keys = {}
        for spec in TAB_SPECS:
            frame = frame_factory(self.notebook)
            self._tab_frames[spec.key] = frame
            self._tab_keys[str(frame)] = spec.key
            self.notebook.add(frame, text=spec.label)
            if spec.key != INFO_KEY:
                self.notebook.tab(frame, state='hidden')
        self.lifecycle = TabLifecycle(builders, self._tab_frames)
        self._verified_max_windows = 0  # never infer client-side 999
        self.lifecycle.ensure_built(INFO_KEY)  # fail closed if real Info service fails
        self.notebook.select(self._tab_frames[INFO_KEY])
        self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_changed)
        self.lifecycle.select(INFO_KEY)
        # E08: root <Destroy> follows descendant events. No invented
        # WM_DELETE_WINDOW handler or helper-process termination.
        bind = getattr(self.root, 'bind', None)
        if callable(bind):
            bind('<Destroy>', self._on_root_destroy, add='+')

    def _on_root_destroy(self, event: Any) -> None:
        if getattr(event, 'widget', None) is self.root:
            self.shutdown()

    def _on_tab_changed(self, _event: Any = None) -> None:
        if self._closed:
            return
        frame = self.notebook.select()
        key = self._tab_keys.get(str(frame), INFO_KEY)
        if key not in self.lifecycle.visible:
            self.notebook.select(self._tab_frames[INFO_KEY])
            key = INFO_KEY
        self.lifecycle.select(key)
        if key == 'start_tab':
            instance = self.lifecycle._instances.get('start_tab')
            setter = getattr(instance, 'set_layout_max_windows', None)
            if callable(setter):
                setter(self._verified_max_windows)

    def apply_verified_permissions(self, authorized_keys: set[str] | frozenset[str], *,
                                   dev_allowed: bool = False, blocked: bool = False) -> None:
        if self._closed:
            return
        previous = self.lifecycle.current
        # Generic visible-tab grants do NOT independently certify a limit;
        # only apply_info_snapshot's verified guard source below can do so.
        self._verified_max_windows = 0
        visible = self.lifecycle.apply_authorized_keys(authorized_keys,dev_allowed=dev_allowed,blocked=blocked)
        for spec in TAB_SPECS:
            self.notebook.tab(self._tab_frames[spec.key],state='normal' if spec.key in visible else 'hidden')
        if previous not in visible:
            self.notebook.select(self._tab_frames[INFO_KEY])
        self._on_tab_changed()

    def apply_info_snapshot(self, snapshot: Any) -> None:
        """Bridge the Info/permission_guard snapshot back onto Tk's UI thread.

        Only the future real Info transport may supply verified token claims.
        No client-side permission validation or fake license policy is added.
        """
        from permission_guard import PermissionSnapshot
        if type(snapshot) is not PermissionSnapshot:
            raise TypeError('Info permission snapshot required')

        def update_on_tk_thread() -> None:
            # S02 verifies marshaling on an __new__ shell fixture; a real
            # constructed shell always has _closed, but that test seam does not.
            if getattr(self, '_closed', False):
                return
            self.apply_verified_permissions(
                set(snapshot.authorized_keys) if snapshot.has_verified_payload else set(),
                dev_allowed=snapshot.developer and not snapshot.blocked,
                blocked=snapshot.blocked,
            )
            self._verified_max_windows = (
                snapshot.max_windows
                if snapshot.has_verified_payload and not snapshot.blocked
                and 'start_tab' in snapshot.authorized_keys
                and type(snapshot.max_windows) is int and snapshot.max_windows > 0
                else 0)
            # S02 tests use an intentionally unconstructed shell (__new__)
            # to verify UI-thread marshaling. Never invent lifecycle access.
            lifecycle = getattr(self, 'lifecycle', None)
            instance = (lifecycle._instances.get('start_tab')
                        if lifecycle is not None else None)
            setter = getattr(instance, 'set_layout_max_windows', None)
            if callable(setter):
                setter(self._verified_max_windows)

        self.root.after(0, update_on_tk_thread)

    def position_window_top_right(self) -> None:
        """E02 high-confidence *model*, not original source-equivalent arithmetic."""
        self.root.update_idletasks()
        w = 450
        h = max(1, int(self.root.winfo_screenheight()) - 80)
        x = max(0, int(self.root.winfo_screenwidth()) - w - 10)
        self.root.geometry(f'{w}x{h}+{x}+0')
        self.root.deiconify()

    def shutdown(self) -> None:
        if self._closed:
            return
        self._closed = True
        self.lifecycle.shutdown()
