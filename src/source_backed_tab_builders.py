"""S154/S165 E03/G08/H01: lazy real Party and opt-in Train config under Info gate.

Original E03 registers TLMStartTab and LoginTab lazily; their constructors
already exist in S10-S25 but were not wired by the Stage-S bootstrap. This
module *only* connects existing working widgets to E03 builder keys.
S165 can optionally register the existing S132 Train composition only when
caller explicitly supplies a real PermissionGuard, account count and settings
path. No permission, license verification, Info service, Proxy, game launch
or fake UI behavior is added. Tabs remain hidden until verified Info. The public entrypoint still exits with status 2.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Sequence

from farm_train_composition import TkTrainComposition
from permission_guard import PermissionGuard
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
    train_permission_guard: PermissionGuard | None = None,
    train_running_count: Callable[[], int] | None = None,
    train_allow_account: Callable[[Any], bool] | None = None,
    train_identity_backend_factory=None,
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

    # S165: an existing functional Train configuration component may be
    # *registered* only when an externally controlled Info guard and a
    # trustworthy account-count callback are explicitly supplied together.
    # Registration is not permission or proof that the original game runs.
    train_requested = (train_permission_guard is not None
                       or train_running_count is not None
                       or train_allow_account is not None
                       or train_identity_backend_factory is not None)
    if train_requested:
        if (type(train_permission_guard) is not PermissionGuard
                or not callable(train_running_count)
                or settings_file is None or not str(settings_file)
                or (train_allow_account is not None
                    and not callable(train_allow_account))):
            raise ValueError("S165_TRAIN_REQUIRES_EXPLICIT_INFO_GUARD_COUNT_AND_SETTINGS")

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

    def build_train(frame: Any) -> TkTrainComposition:
        # Actual S132 Train widgets and INI callbacks. They themselves
        # recheck signed Info permission and max_windows before any edits.
        # Missing shared Start producer => no background HWND scanner.
        panel = TkTrainComposition(
            frame, settings_file=settings_file,
            permission_guard=train_permission_guard,
            running_count=train_running_count,
            window_producer=start_producer,
            allow_account=train_allow_account,
            identity_backend_factory=train_identity_backend_factory,
        )
        panel.pack(fill="both", expand=True)
        return panel

    builders = {
        INFO_KEY: info_factory,
        "start_tab": build_start,
        "login_tab": build_login,
        "party_tab": build_party,
    }
    if train_requested:
        builders["farm_tab"] = build_train
    return builders
