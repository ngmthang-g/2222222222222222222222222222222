"""S154 E03/G08: include real Party config-only editor under Info gate.

Original E03 registers TLMStartTab and LoginTab lazily; their constructors
already exist in S10-S25 but were not wired by the Stage-S bootstrap. This
module *only* connects existing working widgets to E03 builder keys. No
permission, license verification, Info service, Proxy, new controls, actual
game launching, or fake UI behavior. Tabs remain hidden until verified
external Info snapshot. The public entrypoint still exits with status 2.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Sequence

from grid_master import GridSettingsStore
from login_tab import TLMLoginPathTab
from party_group_config import PartyConfigStore
from party_settings_editor import PartySettingsEditor
from party_ready_authorized_tab import AuthorizedPartyReadyTab
from auto_role_provenance import RoleReading
from shell import INFO_KEY
from start_tab import TLMStartTab


SOURCE_BACKED_KEYS = frozenset({INFO_KEY, "start_tab", "login_tab", "party_tab"})


def source_backed_tab_builders(
    info_factory: Callable[[Any], Any],
    *,
    settings_file: str | Path | None = None,
    start_producer: Any = None,
    choose_directory: Callable[..., str] | None = None,
    show_error: Callable[..., object] | None = None,
    party_names_provider: Callable[[], Sequence[str]] | None = None,
    party_role_reader: Callable[[int, int], RoleReading] | None = None,
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
    if party_names_provider is not None and not callable(party_names_provider):
        raise ValueError("S154 Party names provider must be callable")
    if party_role_reader is not None:
        if not callable(party_role_reader) or party_names_provider is not None:
            raise ValueError("S155 Party cannot mix a roster reader and name-list provider")
        if start_producer is None or not callable(getattr(start_producer,"read_snapshot",None)):
            raise ValueError("S155 G02 needs the SAME verified S09 Start cache producer")

    def build_start(frame: Any) -> TLMStartTab:
        return TLMStartTab(
            frame, producer=start_producer,
            grid_settings_store=GridSettingsStore(settings_file))

    def build_login(frame: Any) -> TLMLoginPathTab:
        return TLMLoginPathTab(
            frame, settings_file=settings_file,
            choose_directory=choose_directory, show_error=show_error)

    def build_party(frame: Any) -> PartySettingsEditor:
        """G08 config works; optional G02 live read-only roster when verified.

        No verified G03 RoleName reader yet. The default list remains empty,
        never synthetic HWND/title-derived accounts. Saved group names are
        preserved; external providers must be validated by their caller.
        """
        if party_role_reader is not None:
            # Reuse S90/S91's TRUE Start-cache-driven 3-column ready list.
            # Production has NO reader: this path is unreachable until a
            # genuine game identity adapter is externally supplied.
            editor = AuthorizedPartyReadyTab(
                frame, store=PartyConfigStore(settings_file),
                start_producer=start_producer, read_role=party_role_reader)
        else:
            # S154's already working config-only UI remains exact default.
            names = party_names_provider if party_names_provider is not None else (lambda: ())
            editor = PartySettingsEditor(
                frame, store=PartyConfigStore(settings_file),
                available_names=names)
        editor.pack(fill="both", expand=True)
        return editor

    return {
        INFO_KEY: info_factory,
        "start_tab": build_start,
        "login_tab": build_login,
        "party_tab": build_party,
    }
