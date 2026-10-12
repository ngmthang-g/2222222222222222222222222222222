"""S194: frozen-client Game.RoleData / C_TeamData semantic snapshot intake.

SOURCE:
  DATA-2222 analysis/35_RUNTIME_SNAPSHOT_CONTRACT.md sections 2,3,13.
This is a rigorous NORMALIZER for values supplied by an external reader.
It does NOT provide that external reader, decode its binary wire protocol,
attach to GameAssembly, know field offsets, read game memory, or attest
the sender. In particular, static Game.RoleData *field semantics* do not
prove that a test-supplied RoleName/HP is live in-game truth.

The independent tool MUST NOT register this as a native/game reader until
a version-attested, verified read-only producer actually exists.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import math
import re
from typing import Any

from auto_role_provenance import RoleReading
from start_windows import GameWindow
from train_character_samples import TrainCharacterSample

_TAGS = re.compile(r"<[^>]*>")
MAX_TEAM_MEMBERS_LOCAL_POLICY = 40
MAX_ROLE_NAME_CHARS_LOCAL_POLICY = 120
SOURCE_STATUS = "EXTERNAL_SEMANTIC_PAYLOAD_UNATTESTED_NOT_GAME_PROOF"


class SemanticSnapshotError(ValueError):
    """A malformed or ambiguous external snapshot must fail closed."""


def _positive_integer(value: object, label: str, *, allow_zero=False) -> int:
    if type(value) is not int or value < 0 or (not allow_zero and value == 0):
        raise SemanticSnapshotError("INVALID_" + label)
    return value


def _clean_name(value: object, field: str) -> str:
    if type(value) is not str:
        raise SemanticSnapshotError("MISSING_" + field)
    result = _TAGS.sub("", value).strip()
    if (not result or len(result) > MAX_ROLE_NAME_CHARS_LOCAL_POLICY
            or any(ch in result for ch in ("\0", "\r", "\n"))):
        raise SemanticSnapshotError("INVALID_" + field)
    return result


@dataclass(frozen=True)
class LocalRoleValues:
    name: str
    hp: int
    max_hp: int
    map_id: int
    team_id: int

    @property
    def hp_percent(self) -> float:
        # Same captured publication, NOT a separately cached UI HP%.
        return 100.0 * self.hp / self.max_hp


@dataclass(frozen=True)
class TeamMemberValues:
    role_id: int
    name: str
    hp: int
    max_hp: int
    map_id: int

    @property
    def hp_percent(self) -> float:
        return 100.0 * self.hp / self.max_hp


@dataclass(frozen=True)
class TeamValues:
    team_id: int
    leader_id: int | None
    members: tuple[TeamMemberValues, ...]


@dataclass(frozen=True)
class SemanticGameObservation:
    hwnd: int
    pid: int
    revision: int
    captured_monotonic: float
    role: LocalRoleValues
    team: TeamValues | None = None
    source_status: str = SOURCE_STATUS
    # This must remain False: schema shape/identity checks are NOT proof
    # that an unverified source actually read live game state.
    live_game_producer_attested: bool = False
    can_send_game_actions: bool = False


def _hp(record: Mapping, name: str) -> tuple[int, int]:
    raw = _positive_integer(record.get("HP" if name == "LOCAL"
                                        else "Hp"), name + "_HP", allow_zero=True)
    maximum = _positive_integer(record.get("MaxHP" if name == "LOCAL"
                                            else "MaxHp"), name + "_MAX_HP")
    if raw > maximum:
        raise SemanticSnapshotError(name + "_HP_EXCEEDS_MAX")
    return raw, maximum


def normalize_semantic_observation(
    raw: Mapping[str, Any], window: GameWindow, *,
    revision: int, captured_monotonic: float,
) -> SemanticGameObservation:
    """Read-only canonical normalization, NEVER a bridge authorization.

    Input keys match source-proven semantic Lua RoleData/C_TeamData names,
    NOT the unknown AUTO-train 0x00010007 shared-memory binary structure.
    Caller-supplied values are UNATTESTED even after passing shape checks.
    """
    if type(window) is not GameWindow or not isinstance(raw, Mapping):
        raise SemanticSnapshotError("NATIVE_WINDOW_AND_MAPPING_REQUIRED")
    if (type(window.hwnd) is not int or type(window.pid) is not int
            or window.hwnd <= 0 or window.pid <= 0
            or raw.get("HWND") != window.hwnd or raw.get("PID") != window.pid
            or type(raw.get("HWND")) is not int or type(raw.get("PID")) is not int):
        raise SemanticSnapshotError("EXTERNAL_SNAPSHOT_HWND_PID_MISMATCH")
    _positive_integer(revision, "GENERATION")
    if (type(captured_monotonic) not in (float, int)
            or not math.isfinite(captured_monotonic)
            or captured_monotonic < 0):
        raise SemanticSnapshotError("INVALID_CAPTURE_MONOTONIC")
    local = raw.get("RoleData")
    if not isinstance(local, Mapping):
        raise SemanticSnapshotError("LOCAL_ROLEDATA_MISSING")
    hp, max_hp = _hp(local, "LOCAL")
    role = LocalRoleValues(
        _clean_name(local.get("Name"), "LOCAL_ROLE_NAME"),
        hp, max_hp,
        _positive_integer(local.get("MapID"), "LOCAL_MAP_ID", allow_zero=True),
        _positive_integer(local.get("TeamID"), "LOCAL_TEAM_ID", allow_zero=True),
    )
    team_raw = raw.get("TeamData")
    team = None
    if team_raw is not None:
        if not isinstance(team_raw, Mapping):
            raise SemanticSnapshotError("INVALID_TEAM_DATA")
        team_id = _positive_integer(team_raw.get("TeamID"), "TEAM_ID")
        if team_id != role.team_id:
            raise SemanticSnapshotError("TEAM_ID_CONFLICT_WITH_LOCAL_ROLE")
        leader_id = team_raw.get("LeaderID")
        if leader_id is not None:
            _positive_integer(leader_id, "LEADER_ROLE_ID")
        members_raw = team_raw.get("Members")
        if (not isinstance(members_raw, (tuple, list))
                or len(members_raw) > MAX_TEAM_MEMBERS_LOCAL_POLICY):
            raise SemanticSnapshotError("TEAM_MEMBER_ARRAY_UNSAFE")
        members = []
        seen_roles = set()
        for member in members_raw:
            if not isinstance(member, Mapping):
                raise SemanticSnapshotError("INVALID_TEAM_MEMBER")
            member_id = _positive_integer(member.get("RoleID"), "MEMBER_ROLE_ID")
            if member_id in seen_roles:
                raise SemanticSnapshotError("DUPLICATE_TEAM_MEMBER_ROLE_ID")
            seen_roles.add(member_id)
            mhp, mmax = _hp(member, "TEAM")
            members.append(TeamMemberValues(
                member_id,
                _clean_name(member.get("RoleName"), "MEMBER_ROLE_NAME"),
                mhp, mmax,
                _positive_integer(member.get("MapID"), "MEMBER_MAP_ID",
                                  allow_zero=True),
            ))
        if leader_id is not None and members and leader_id not in seen_roles:
            # Team might be partially paginated/AOI-limited: do not invent
            # a missing leader or guess another member.
            raise SemanticSnapshotError("LEADER_NOT_IN_COMPLETE_TEAM_MEMBERS")
        team = TeamValues(team_id, leader_id, tuple(members))
    return SemanticGameObservation(
        window.hwnd, window.pid, revision, float(captured_monotonic),
        role, team)


def _fresh_for_window(
    observation: SemanticGameObservation,
    window: GameWindow,
    *,
    now_monotonic: float,
    max_age_seconds: float,
) -> bool:
    """Consumer freshness/identity only, NOT game-producer authentication."""
    if type(observation) is not SemanticGameObservation or type(window) is not GameWindow:
        return False
    if (type(now_monotonic) not in (int, float)
            or type(max_age_seconds) not in (int, float)
            or not math.isfinite(now_monotonic)
            or not math.isfinite(max_age_seconds)
            or max_age_seconds <= 0):
        return False
    age = now_monotonic - observation.captured_monotonic
    return (
        0 <= age <= max_age_seconds
        and observation.hwnd == window.hwnd
        and observation.pid == window.pid
        and not observation.can_send_game_actions)


def project_train_sample(
    observation: SemanticGameObservation, window: GameWindow,
    *, now_monotonic: float, max_age_seconds: float,
) -> TrainCharacterSample | None:
    """Future verified reader projection; no bag or currency guessed."""
    if not _fresh_for_window(
            observation, window,
            now_monotonic=now_monotonic,
            max_age_seconds=max_age_seconds):
        return None
    return TrainCharacterSample(
        window.hwnd, window.pid, observation.role.name,
        observation.role.map_id,
        bag_slots=None, bound_money=None, exp=None)


def project_party_role_name(
    observation: SemanticGameObservation, window: GameWindow,
    *, now_monotonic: float, max_age_seconds: float,
) -> RoleReading | None:
    """Party user-visible RoleName, NEVER online/game-control authority."""
    if not _fresh_for_window(
            observation, window,
            now_monotonic=now_monotonic,
            max_age_seconds=max_age_seconds):
        return None
    return RoleReading(window.hwnd, window.pid, observation.role.name)
