"""S197 exact 42-field RoleData layout reconstructed from ORIGINAL TLM 2.1.2.

Authority: user's byte-identical TLMTool.dist/TLMTool.exe SHA256
15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22.
The Nuitka memory_reader constants payload begins at file 0x2B7576F.
At payload +0x1F2B: D* (42-name dictionary), followed exactly 42
T\x02, l<varint-offset>, w<type I/Q/P> tuple constants starting
+0x20CE. Name/value order is exact, not inferred from neighboring tags.

This proves original *table metadata*, NOT that the running client's
RoleData matches it. It is an independent numeric-only read diagnostic
for an ALREADY ANCHORED live RoleData pointer (S196); no UI, license,
memory writes, game actions or account authorization. RoleName is a
pointer to an IL2CPP string whose exact decoder must be verified
separately, so this module NEVER emits a character name.
"""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Protocol

ORIGINAL_TLM_ROLE_FIELDS = MappingProxyType({
    "RoleID": (0x010, "I"),
    "RoleName": (0x018, "P"),
    "Sex": (0x020, "I"),
    "FactionID": (0x024, "I"),
    "Level": (0x028, "I"),
    "MapID": (0x050, "I"),
    "PosX": (0x054, "I"),
    "PosY": (0x058, "I"),
    "Exp": (0x060, "Q"),
    "MaxExp": (0x068, "Q"),
    "Direction": (0x0A0, "I"),
    "CurrentHP": (0x0A4, "I"),
    "MaxHP": (0x0A8, "I"),
    "CurrentMP": (0x0AC, "I"),
    "MaxMP": (0x0B0, "I"),
    "CurrentRage": (0x0B4, "I"),
    "MaxRage": (0x0B8, "I"),
    "CurrentStrike": (0x0BC, "I"),
    "Money": (0x078, "I"),
    "BoundMoney": (0x07C, "I"),
    "Token": (0x080, "I"),
    "BoundToken": (0x084, "I"),
    "BankMoney": (0x088, "I"),
    "PKMode": (0x070, "I"),
    "PKValue": (0x074, "I"),
    "GuildID": (0x09C, "I"),
    "GuildRank": (0x170, "I"),
    "TeamID": (0x0E8, "I"),
    "ServerID": (0x0F8, "I"),
    "Strength": (0x12C, "I"),
    "Energy": (0x130, "I"),
    "Stamina": (0x134, "I"),
    "Intelligence": (0x138, "I"),
    "Dexterity": (0x13C, "I"),
    "MoveSpeed": (0x100, "I"),
    "CurrentPetID": (0x140, "I"),
    "IsRiding": (0x108, "I"),
    "IsGM": (0x0FC, "I"),
    "CombatRelationship": (0x104, "I"),
    "QuickSkills": (0x150, "P"),
    "AutoSettings": (0x158, "P"),
    "SystemSettings": (0x160, "P"),
})

SIZE_BY_ORIGINAL_TYPE = MappingProxyType({"I": 4, "Q": 8, "P": 8})
MAX_CANONICAL_USER_POINTER = 0x00007FFFFFFFFFFF


class OriginalReadOnlyBytes(Protocol):
    def bytes(self, address: int, size: int) -> bytes | None: ...


@dataclass(frozen=True)
class OriginalNumericRoleCandidate:
    status: str
    role_id: int | None = None
    current_hp: int | None = None
    max_hp: int | None = None
    map_id: int | None = None
    team_id: int | None = None
    level: int | None = None
    name_pointer_observed: bool = False
    role_name: None = None
    # A matching original dictionary + numeric shape is not proof
    # the external player is logged in or that its runtime is compatible.
    source_proven_live_character: bool = False
    game_action_authorized: bool = False


def _field(reader: OriginalReadOnlyBytes, role: int, field: str) -> int | None:
    if (type(role) is not int or role < 0x10000
            or role > MAX_CANONICAL_USER_POINTER or role % 8
            or field not in ORIGINAL_TLM_ROLE_FIELDS):
        return None
    offset, descriptor = ORIGINAL_TLM_ROLE_FIELDS[field]
    width = SIZE_BY_ORIGINAL_TYPE[descriptor]
    address = role + offset
    if address > MAX_CANONICAL_USER_POINTER - width:
        return None
    try:
        raw = reader.bytes(address, width)
    except (OSError, ValueError, RuntimeError, TypeError, OverflowError):
        return None
    if type(raw) is not bytes or len(raw) != width:
        return None
    return int.from_bytes(raw, "little", signed=False)


def read_original_role_numeric_candidate(
    reader: OriginalReadOnlyBytes, role: int,
) -> OriginalNumericRoleCandidate:
    """Only after S196 version/PID/mapped RoleData+SessionData validation.

    The repeated core identity read rejects mutation/memory reuse while
    gathering fields. An independently verified original RoleName string
    reader is NOT available yet; therefore numeric candidates are not
    promoted to Party/Train or any game action.
    """
    if (not callable(getattr(reader, "bytes", None))
            or type(role) is not int or role < 0x10000 or role % 8):
        return OriginalNumericRoleCandidate("INVALID_ROLE_READER_OR_POINTER")
    names = ("RoleID", "CurrentHP", "MaxHP", "MapID",
             "TeamID", "Level", "RoleName")
    vals = {name: _field(reader, role, name) for name in names}
    if any(value is None for value in vals.values()):
        return OriginalNumericRoleCandidate("ROLE_FIELD_MEMORY_UNREADABLE")
    if (vals["RoleID"] == 0 or vals["Level"] == 0
            or vals["Level"] > 10000
            or vals["MapID"] == 0 or vals["MaxHP"] == 0
            or vals["CurrentHP"] > vals["MaxHP"]):
        return OriginalNumericRoleCandidate("ROLE_FIELD_VALUES_IMPLAUSIBLE")
    name_ptr = vals["RoleName"]
    if (name_ptr < 0x10000 or name_ptr > MAX_CANONICAL_USER_POINTER
            or name_ptr % 8):
        return OriginalNumericRoleCandidate("ROLE_NAME_POINTER_INVALID")
    # Independently double-read core identity; HP can change during combat.
    for name in ("RoleID", "MapID", "TeamID", "RoleName"):
        if _field(reader, role, name) != vals[name]:
            return OriginalNumericRoleCandidate("ROLE_CHANGED_DURING_NUMERIC_READ")
    return OriginalNumericRoleCandidate(
        "ORIGINAL_42_FIELD_NUMERIC_CANDIDATE_NO_ROLENAME_PROOF",
        vals["RoleID"], vals["CurrentHP"], vals["MaxHP"],
        vals["MapID"], vals["TeamID"], vals["Level"], True)
