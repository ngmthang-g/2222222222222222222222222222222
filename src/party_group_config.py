"""S89 / G08: source-backed Party group configuration, NOT live team creation.

Only active Party keys from the original TLM 2.1.2 evidence are owned here.
All HWND/PID/RoleID/TeamID and team run/cancel state stay outside settings.
A real Party action tab is NOT installed by this module.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from settings_store import _settings_lock, read_settings, write_settings

SECTION = "Settings"
AFTER_KEY = "party_after"
GROUPS_KEY = "party_groups"
LEGACY_KEY = "party_group1"
AFTER_VALUES = ("wait", "train", "train_lsv", "don", "phoban")
AFTER_LABELS = ("Chờ", "Train", "Train LSV", "Dồn vàng", "Phó bản")
MAX_GROUP_MEMBERS = 6
DORMANT_KEYS = ("party_corps_groups", "party_corps_group1", "party_follow", "party_pick")


def _names(value):
    """Read only selected names. Never reinterpret dicts as runtime identity."""
    if not isinstance(value, (list, tuple)) or len(value) > MAX_GROUP_MEMBERS:
        raise ValueError("Party group must have at most six name slots")
    seen = set()
    names = []
    for entry in value:
        if type(entry) is not str:
            raise ValueError("Party member must be a character name")
        name = entry.strip()
        if name and name not in seen:
            seen.add(name)
            names.append(name)
    return tuple(names)


@dataclass(frozen=True)
class PartyGroup:
    num: int
    members: tuple[str, ...]

    def __post_init__(self):
        if type(self.num) is not int or self.num < 1:
            raise ValueError("Party group number must be positive")
        _names(self.members)


@dataclass(frozen=True)
class PartySettings:
    after: str = "wait"
    groups: tuple[PartyGroup, ...] = (PartyGroup(1, ()),)

    def __post_init__(self):
        if self.after not in AFTER_VALUES or not self.groups:
            raise ValueError("Invalid Party configuration")
        for i, group in enumerate(self.groups, 1):
            if type(group) is not PartyGroup or group.num != i:
                raise ValueError("Party groups must be consecutively numbered")

    def change_after(self, value: str) -> "PartySettings":
        return PartySettings(value, self.groups)

    def add_group(self) -> "PartySettings":
        return PartySettings(self.after, self.groups + (PartyGroup(len(self.groups) + 1, ()),))

    def remove_group(self, num: int) -> "PartySettings":
        if type(num) is not int or not 1 <= num <= len(self.groups):
            raise ValueError("Unknown Party group")
        if len(self.groups) == 1:
            return self  # G09: last Party group may not be deleted
        rest = tuple(PartyGroup(i, group.members) for i, group in enumerate(
            (g for g in self.groups if g.num != num), 1))
        return PartySettings(self.after, rest)

    def select_member(self, group_num: int, slot: int, name: str) -> "PartySettings":
        if (type(group_num) is not int or group_num < 1 or group_num > len(self.groups)
                or type(slot) is not int or not 0 <= slot < MAX_GROUP_MEMBERS
                or type(name) is not str):
            raise ValueError("Invalid Party selection")
        current = list(self.groups[group_num - 1].members)
        padded = current + [""] * (MAX_GROUP_MEMBERS - len(current))
        padded[slot] = name.strip()
        # Each active group stores selected names, blank/duplicate removed.
        members = _names(padded)
        groups = list(self.groups)
        groups[group_num - 1] = PartyGroup(group_num, members)
        return PartySettings(self.after, tuple(groups))


def _parse_groups(raw: str):
    data = json.loads(raw)
    if type(data) is not list or not data:
        raise ValueError("Missing or invalid Party group list")
    groups = []
    for item in data:
        if type(item) is not dict or type(item.get("members")) is not list:
            raise ValueError("Bad Party current schema")
        # G08: saved 'num' handling exact micro-order is UNKNOWN. Current
        # list order is authoritative for safe contiguous UI renumbering.
        groups.append(PartyGroup(len(groups) + 1, _names(item["members"])))
    return tuple(groups)


class PartyConfigStore:
    """G08 backed by shared E05 atomic settings file and shared RLock.

    The full read/modify/write takes the SAME shared settings lock to avoid
    dropping unrelated keys modified by another registered tab.
    """

    def __init__(self, settings_file: str | Path | None = None):
        self.settings_file = Path(settings_file) if settings_file is not None else None

    def load(self) -> PartySettings:
        with _settings_lock:
            parser = read_settings(self.settings_file)
            after = parser.get(SECTION, AFTER_KEY, fallback="wait").strip()
            if after not in AFTER_VALUES:
                after = "wait"
            raw = parser.get(SECTION, GROUPS_KEY, fallback="")
            groups = None
            if raw.strip():
                try:
                    groups = _parse_groups(raw)
                except (ValueError, TypeError, json.JSONDecodeError):
                    pass  # G08 malformed-schema precise branch UNKNOWN
            if groups is None:
                legacy = parser.get(SECTION, LEGACY_KEY, fallback="")
                if legacy.strip():
                    try:
                        names = _names(json.loads(legacy))
                        groups = (PartyGroup(1, names),)
                    except (ValueError, TypeError, json.JSONDecodeError):
                        pass
            return PartySettings(after, groups or (PartyGroup(1, ()),))

    def save(self, state: PartySettings) -> None:
        if type(state) is not PartySettings:
            raise ValueError("PartySettings instance required")
        # Validate completely BEFORE touching disk or writing any setting.
        state.__post_init__()
        payload = []
        for group in state.groups:
            payload.append({"num": group.num, "members": list(_names(group.members))})
        current = json.dumps(payload, ensure_ascii=False)
        legacy = json.dumps(payload[0]["members"], ensure_ascii=False)
        with _settings_lock:
            parser = read_settings(self.settings_file)
            if not parser.has_section(SECTION):
                parser.add_section(SECTION)
            parser.set(SECTION, AFTER_KEY, state.after)
            parser.set(SECTION, GROUPS_KEY, current)
            parser.set(SECTION, LEGACY_KEY, legacy)
            # Original G08 lists these as dormant cleanup keys. Only
            # remove keys in the active Settings section; never touch
            # unrelated settings or create their old UI.
            for key in DORMANT_KEYS:
                parser.remove_option(SECTION, key)
            write_settings(parser, self.settings_file)
