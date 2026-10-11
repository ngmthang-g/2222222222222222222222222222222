"""S137 original 2.1.2 embedded item metadata — exact OFFLINE reader.

This decodes the hash-pinned original package's item_meta_data.META and
weapon_ids.WEAPON_ITEM_IDS without running original EXE or a game. Unlike
S135's synthetic inventory, records are real immutable original binary data.
It is an offline build/reference capability, NOT a live bag reader, original
runtime key-conversion proof, account entitlement or game action.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from types import MappingProxyType
from typing import Mapping
import zipfile

ARCHIVE_SHA256 = "c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd"
EXE_SHA256 = "15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22"
INNER = "TLMTool_2.1.2/TLMTool.dist/TLMTool.exe"
META_WINDOW = (0x2977206, 0x2977400)
WEAPON_WINDOW = (0x2C54798, 0x2C54A00)
META_EXPECTED = 29983
WEAPON_EXPECTED = 5477
TYPES_EXPECTED = (0, 1, 2, 3, 4, 5, 6, 7, 8, 16, 17, 100)


@dataclass(frozen=True)
class OriginalItemMeta:
    item_id: int
    name: str
    icon: str
    src: str
    equip_type: str | None


@dataclass(frozen=True)
class OriginalItemCatalog:
    """Only positive ids present in PINNED original 2.1.2 are authoritative."""
    source_exe_sha256: str
    entries: Mapping[int, OriginalItemMeta]
    weapon_ids: frozenset[int]
    weapon_types: tuple[int, ...]
    live_game_version_verified: bool = False
    runtime_read_bag_verified: bool = False
    action_authorized: bool = False

    def lookup(self, item_id: int) -> OriginalItemMeta | None:
        if type(item_id) is not int or item_id <= 0:
            return None
        return self.entries.get(item_id)

    def weapon_membership(self, item_id: int) -> bool | None:
        """None means unknown ID, NOT safe-to-discard False."""
        if self.lookup(item_id) is None:
            return None
        return item_id in self.weapon_ids

    def basic_bag_metadata(self, item_id: int) -> dict[str, str | None] | None:
        """Metadata only: no dbID/slot/qty/read_bag/get_bag runtime semantics."""
        item = self.lookup(item_id)
        if item is None:
            return None
        return {
            "name": item.name, "icon": item.icon,
            "src": item.src, "type": item.equip_type,
        }


def _uleb(data: bytes, position: int) -> tuple[int, int]:
    value = 0
    for shift in range(0, 70, 7):
        if position >= len(data):
            raise ValueError("TRUNCATED_EMBEDDED_ULEB")
        c = data[position]
        position += 1
        value |= (c & 127) << shift
        if c < 128:
            if value >= 1 << 64:
                raise ValueError("EMBEDDED_ULEB_OVERFLOW")
            return value, position
    raise ValueError("EMBEDDED_ULEB_TOO_LONG")


def _terminated(data: bytes, position: int) -> tuple[str, int]:
    end = data.find(b"\x00", position)
    if end < 0:
        raise ValueError("EMBEDDED_STRING_NOT_TERMINATED")
    try:
        return data[position:end].decode("utf-8"), end + 1
    except UnicodeError as exc:
        raise ValueError("INVALID_EMBEDDED_UTF8") from exc


def _text_field(data: bytes, position: int) -> tuple[str | None, int]:
    if position >= len(data):
        raise ValueError("TRUNCATED_EMBEDDED_TEXT")
    tag = chr(data[position])
    position += 1
    if tag in ("a", "u"):
        return _terminated(data, position)
    if tag == "n":
        return None, position
    if tag == "w":
        if position >= len(data):
            raise ValueError("TRUNCATED_WIDE_CHAR")
        return chr(data[position]), position + 1
    raise ValueError("UNKNOWN_EMBEDDED_TEXT_TAG")


def _after_marker(data: bytes, window: tuple[int, int]) -> int:
    offset = data.find(b"ahas_location\x00", *window)
    if offset < 0:
        raise ValueError("ORIGINAL_MODULE_LOCATION_MARKER_MISSING")
    return offset + len(b"ahas_location\x00")


def _metadata(data: bytes) -> dict[int, OriginalItemMeta]:
    pos = _after_marker(data, META_WINDOW)
    if data[pos:pos + 1] != b"D":
        raise ValueError("ORIGINAL_METADATA_DICTIONARY_TAG_MISMATCH")
    count, pos = _uleb(data, pos + 1)
    if count != META_EXPECTED:
        raise ValueError("ORIGINAL_METADATA_COUNT_MISMATCH")
    keys = []
    for _ in range(count):
        if data[pos:pos + 1] != b"u":
            raise ValueError("ORIGINAL_METADATA_KEY_TAG_MISMATCH")
        text, pos = _terminated(data, pos + 1)
        if not text.isascii() or not text.isdecimal() or int(text) <= 0:
            raise ValueError("INVALID_ORIGINAL_ITEMID_KEY")
        keys.append(int(text))
    if len(set(keys)) != count:
        raise ValueError("DUPLICATE_ORIGINAL_ITEMID_KEY")
    result = {}
    for item_id in keys:
        if data[pos:pos + 2] != b"T\x04":
            raise ValueError("ORIGINAL_METADATA_ROW_TAG_MISMATCH")
        pos += 2
        values = []
        for _ in range(4):
            field, pos = _text_field(data, pos)
            values.append(field)
        name, icon, src, typ = values
        if (not isinstance(name, str) or not name.strip()
                or not isinstance(icon, str) or not icon.strip()
                or not isinstance(src, str)
                or (typ is not None and not isinstance(typ, str))):
            raise ValueError("INVALID_ORIGINAL_METADATA_ROW")
        result[item_id] = OriginalItemMeta(item_id, name, icon, src, typ)
    if data[pos:pos + len(b"aMETA\x00")] != b"aMETA\x00":
        raise ValueError("ORIGINAL_METADATA_END_MARKER_MISMATCH")
    return result


def _weapons(data: bytes) -> tuple[frozenset[int], tuple[int, ...]]:
    pos = _after_marker(data, WEAPON_WINDOW)
    if data[pos:pos + 1] != b"L":
        raise ValueError("ORIGINAL_WEAPON_TYPES_TAG_MISMATCH")
    total, pos = _uleb(data, pos + 1)
    if total != len(TYPES_EXPECTED):
        raise ValueError("ORIGINAL_WEAPON_TYPE_COUNT_MISMATCH")
    types = []
    for _ in range(total):
        if data[pos:pos + 1] != b"l":
            raise ValueError("ORIGINAL_WEAPON_TYPE_TAG_MISMATCH")
        value, pos = _uleb(data, pos + 1)
        types.append(value)
    if tuple(types) != TYPES_EXPECTED:
        raise ValueError("ORIGINAL_WEAPON_TYPES_MISMATCH")
    marker = b"aWEAPON_TYPES\x00"
    if data[pos:pos + len(marker)] != marker:
        raise ValueError("ORIGINAL_WEAPON_TYPES_END_MISMATCH")
    pos += len(marker)
    if data[pos:pos + 1] != b"S":
        raise ValueError("ORIGINAL_WEAPON_SET_TAG_MISMATCH")
    count, pos = _uleb(data, pos + 1)
    if count != WEAPON_EXPECTED:
        raise ValueError("ORIGINAL_WEAPON_SET_COUNT_MISMATCH")
    ids = []
    for _ in range(count):
        if data[pos:pos + 1] != b"l":
            raise ValueError("ORIGINAL_WEAPON_ID_TAG_MISMATCH")
        value, pos = _uleb(data, pos + 1)
        ids.append(value)
    if len(set(ids)) != count:
        raise ValueError("DUPLICATE_WEAPON_ID")
    if data[pos:pos + len(b"ais_weapon\x00")] != b"ais_weapon\x00":
        raise ValueError("ORIGINAL_WEAPON_SET_END_MARKER_MISMATCH")
    return frozenset(ids), tuple(types)


def decode_original_exe(data: bytes) -> OriginalItemCatalog:
    """Full exact binary fingerprint is required, even for plausible rows."""
    if type(data) is not bytes or hashlib.sha256(data).hexdigest() != EXE_SHA256:
        raise ValueError("UNPINNED_ORIGINAL_TLM_EXE")
    entries = _metadata(data)
    weapons, types = _weapons(data)
    allowed = {
        item_id for item_id, item in entries.items()
        if item.src == "Equips" and item.equip_type in {str(t) for t in types}
    }
    if allowed != weapons:
        raise ValueError("ORIGINAL_WEAPON_METADATA_INTEGRITY_MISMATCH")
    return OriginalItemCatalog(
        source_exe_sha256=EXE_SHA256,
        entries=MappingProxyType(entries),
        weapon_ids=weapons,
        weapon_types=types,
    )


def load_original_archive(path: str | Path) -> OriginalItemCatalog:
    """Explicit OFFLINE user-provided ZIP; never a game process or network."""
    archive = Path(path)
    digest = hashlib.sha256()
    with archive.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    if digest.hexdigest() != ARCHIVE_SHA256:
        raise ValueError("UNPINNED_ORIGINAL_TLM_ARCHIVE")
    with zipfile.ZipFile(archive) as zf:
        if len(zf.infolist()) != 1050 or zf.testzip() is not None:
            raise ValueError("DAMAGED_ORIGINAL_TLM_ARCHIVE")
        data = zf.read(INNER)
    return decode_original_exe(data)
