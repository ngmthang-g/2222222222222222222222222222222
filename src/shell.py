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
    TabSpec('donvang_tab', 'Đồn'), TabSpec('rao_tab', 'Rao'),
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

    def ensure_built(self, key: str) -> Any:
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
        if self._active_refresh is not None:
            obj = self._instances.get(self._active_refresh)
            cb = getattr(obj, '_stop_refresh', None)
            if callable(cb):
                cb()
            self._active_refresh = None

    def shutdown(self) -> None:
        self._stop_old_refresh()


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
        self.lifecycle.ensure_built(INFO_KEY)  # fail closed if real Info service fails
        self.notebook.select(self._tab_frames[INFO_KEY])
        self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_changed)
        self.lifecycle.select(INFO_KEY)

    def _on_tab_changed(self, _event: Any = None) -> None:
        frame = self.notebook.select()
        key = self._tab_keys.get(str(frame), INFO_KEY)
        if key not in self.lifecycle.visible:
            self.notebook.select(self._tab_frames[INFO_KEY])
            key = INFO_KEY
        self.lifecycle.select(key)

    def apply_verified_permissions(self, authorized_keys: set[str] | frozenset[str], *,
                                   dev_allowed: bool = False, blocked: bool = False) -> None:
        previous = self.lifecycle.current
        visible = self.lifecycle.apply_authorized_keys(authorized_keys,dev_allowed=dev_allowed,blocked=blocked)
        for spec in TAB_SPECS:
            self.notebook.tab(self._tab_frames[spec.key],state='normal' if spec.key in visible else 'hidden')
        if previous not in visible:
            self.notebook.select(self._tab_frames[INFO_KEY])
        self._on_tab_changed()

    def position_window_top_right(self) -> None:
        """E02 high-confidence *model*, not original source-equivalent arithmetic."""
        self.root.update_idletasks()
        w = 450
        h = max(1, int(self.root.winfo_screenheight()) - 80)
        x = max(0, int(self.root.winfo_screenwidth()) - w - 10)
        self.root.geometry(f'{w}x{h}+{x}+0')
        self.root.deiconify()

    def shutdown(self) -> None:
        self.lifecycle.shutdown()
