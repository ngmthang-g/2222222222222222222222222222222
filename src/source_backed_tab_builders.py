"""S35 E03/F01/F04: register ONLY source-backed existing Start and Login tabs.

Original E03 registers TLMStartTab and LoginTab lazily; their constructors
already exist in S10-S25 but were not wired by the Stage-S bootstrap. This
module *only* connects existing working widgets to E03 builder keys. No
permission, license verification, Info service, Proxy, new controls, actual
game launching, or fake UI behavior. Tabs remain hidden until verified
external Info snapshot. The public entrypoint still exits with status 2.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from grid_master import GridSettingsStore
from login_tab import TLMLoginPathTab
from shell import INFO_KEY
from start_tab import TLMStartTab


SOURCE_BACKED_KEYS = frozenset({INFO_KEY, "start_tab", "login_tab"})


def source_backed_tab_builders(
    info_factory: Callable[[Any], Any],
    *,
    settings_file: str | Path | None = None,
    start_producer: Any = None,
    choose_directory: Callable[..., str] | None = None,
    show_error: Callable[..., object] | None = None,
) -> dict[str, Callable[[Any], Any]]:
    """Return real lazy constructors; never create a tab or grant access here.

    Optional substitutions are for bounded TEST-owned native integration.
    Production uses the original-backed OS file picker and Windows producer.
    The verified permission guard lives ONLY in Info/TabLifecycle.
    """
    if not callable(info_factory):
        raise ValueError("S35 real Info factory is required")
    if choose_directory is not None and not callable(choose_directory):
        raise ValueError("S35 directory picker must be callable")
    if show_error is not None and not callable(show_error):
        raise ValueError("S35 error dialog must be callable")

    def build_start(frame: Any) -> TLMStartTab:
        return TLMStartTab(
            frame, producer=start_producer,
            grid_settings_store=GridSettingsStore(settings_file))

    def build_login(frame: Any) -> TLMLoginPathTab:
        return TLMLoginPathTab(
            frame, settings_file=settings_file,
            choose_directory=choose_directory, show_error=show_error)

    return {
        INFO_KEY: info_factory,
        "start_tab": build_start,
        "login_tab": build_login,
    }
