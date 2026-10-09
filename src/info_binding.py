"""S04 InfoState -> Tk main-thread read-only view and tab-permission binding.

This is *not* a license verifier, heartbeat implementation or production entry.
The existing S01 executable still refuses to start without authentic Info RPC.
"""
from __future__ import annotations

import tkinter as tk
from typing import Any

from info_state import InfoState
from info_tab import TLMInfoTab
from permission_guard import PermissionSnapshot
from shell import INFO_KEY, TLMMainApp


class InfoShellBinding:
    """Owns one real InfoState, one passive Info tab and the Tk update lifecycle.

    Tk callbacks are queued via root.after as in E04. A sequence check and
    snapshot identity check prevent late positive grants after newer revocation.
    """

    def __init__(self, root: Any, app: TLMMainApp, info: InfoState, view: TLMInfoTab):
        self.root = root
        self.app = app
        self.info = info
        self.view = view
        self._closed = False
        self._sequence = 0

    def on_snapshot(self, snapshot: PermissionSnapshot) -> None:
        if type(snapshot) is not PermissionSnapshot:
            raise TypeError("verified permission snapshot required")
        if self._closed:
            return
        self._sequence += 1
        sequence = self._sequence

        def apply_latest() -> None:
            if (self._closed or sequence != self._sequence
                    or snapshot is not self.info.permission_guard.snapshot):
                return
            self.app.apply_verified_permissions(
                set(snapshot.authorized_keys) if snapshot.has_verified_payload else set(),
                dev_allowed=snapshot.developer and not snapshot.blocked,
                blocked=snapshot.blocked,
            )
            self.view.refresh_readonly()

        try:
            self.root.after(0, apply_latest)
        except (tk.TclError, RuntimeError):
            # Destroyed Tk interpreter: do not retry or resurrect a closed UI.
            self.close()

    def on_destroy(self, event: Any) -> None:
        # A root <Destroy> bind also sees descendant events. Only close at root.
        if getattr(event, "widget", None) is self.root:
            self.close()

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._sequence += 1
        self.info.stop_heartbeat()
        self.app.shutdown()


def create_info_only_shell(
    root: Any, *, notebook_factory: Any = None,
    frame_factory: Any = None, ttk_module: Any = None,
) -> InfoShellBinding:
    """Construct a real, passive Info-only Tk shell without an auth adapter.

    No actions or other tabs are supplied. This is an internal integration
    seam, NOT called by the public entrypoint until server/auth is verified.
    """
    pending: dict[str, InfoShellBinding] = {}

    def on_state_change(snapshot: PermissionSnapshot) -> None:
        binding = pending.get("binding")
        if binding is not None:
            binding.on_snapshot(snapshot)

    info = InfoState(on_update=on_state_change)
    app = TLMMainApp(
        root,
        {INFO_KEY: lambda frame: TLMInfoTab(frame, info, ttk_module=ttk_module)},
        notebook_factory=notebook_factory,
        frame_factory=frame_factory,
    )
    view = app.lifecycle.ensure_built(INFO_KEY)
    binding = InfoShellBinding(root, app, info, view)
    pending["binding"] = binding
    root.bind("<Destroy>", binding.on_destroy, add="+")
    return binding
