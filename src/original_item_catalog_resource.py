"""S138 — strictly pinned offline *exported* original item catalog resource.

S137 verified 29,983 original ItemIDs and 5,477 weapon ItemIDs by decoding
the SHA-pinned original ZIP. This loads that exact exported JSON.gz, without
requiring the 90 MB original distribution after export. It is a developer-only
OFFLINE metadata lookup: NOT a game inventory sample, live reader, signed Info
token, GUI, gameplay action or product authentication.
"""
from __future__ import annotations

from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
from types import MappingProxyType

from original_item_catalog import (
    EXE_SHA256, OriginalItemCatalog, OriginalItemMeta, TYPES_EXPECTED,
)

EXPORTED_GZIP_SHA256 = "e9322e4c6e5f0a832ae76316ad9be5fc9dc0fd2ebd0043f02bef0da360fb220a"
EXPORTED_JSON_SHA256 = "2f93cd68415ce102b79d3a8ba2e827a38e463580050433da71a50f5b1ff859fe"
METADATA_ROWS_SHA256 = "3a7ca5a89aceff58c3067f0372b939725bc6b88b0e466a5c0abab63e1101d439"
WEAPON_IDS_SHA256 = "3cc0fc17ea3a1a72f07204ae0a483d0b432db338a848e9a04d97ca0a2dfc1dfd"
GZIP_SIZE = 193833
JSON_SIZE = 2155301
TOTAL_ITEMS = 29983
TOTAL_WEAPONS = 5477
SOURCE_COUNTS = {"Equips":22776, "Items":5289, "Gems":1154,
                 "Medicines":694, "PetEquips":70}
EXPORT_SCHEMA = ["itemID","name","icon","src","type"]


def _is_strict_int(value: object) -> bool:
    return type(value) is int and value > 0


def load_verified_export(path: str | Path) -> OriginalItemCatalog:
    """Fail closed on ANY different export. No network, no implicit fallback."""
    raw = Path(path).read_bytes()
    if len(raw) != GZIP_SIZE or hashlib.sha256(raw).hexdigest() != EXPORTED_GZIP_SHA256:
        raise ValueError("S138_ORIGINAL_CATALOG_EXPORT_SHA256_MISMATCH")
    try:
        plain = gzip.decompress(raw)
    except (OSError, EOFError) as exc:
        raise ValueError("S138_ORIGINAL_CATALOG_CORRUPT_GZIP") from exc
    if len(plain) != JSON_SIZE or hashlib.sha256(plain).hexdigest() != EXPORTED_JSON_SHA256:
        raise ValueError("S138_ORIGINAL_CATALOG_JSON_SHA256_MISMATCH")
    try:
        doc = json.loads(plain)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("S138_ORIGINAL_CATALOG_INVALID_JSON") from exc
    return _validate_export_structure(doc)


def _validate_export_structure(doc: object) -> OriginalItemCatalog:
    if not isinstance(doc, dict) or set(doc) != {
        "source","original_exe_sha256","game_runtime_verified","item_schema",
        "entries","weapon_ids","weapon_types"
    }:
        raise ValueError("S138_CATALOG_SCHEMA_MISMATCH")
    if (doc["source"] != "OFFLINE_EXACT_ORIGINAL_TLMTOOL_2_1_2"
        or doc["original_exe_sha256"] != EXE_SHA256
        or doc["game_runtime_verified"] is not False
        or doc["item_schema"] != EXPORT_SCHEMA
        or doc["weapon_types"] != list(TYPES_EXPECTED)):
        raise ValueError("S138_CATALOG_PROVENANCE_MISMATCH")
    rows = doc["entries"]
    weapon_list = doc["weapon_ids"]
    if (not isinstance(rows, list) or len(rows) != TOTAL_ITEMS
        or not isinstance(weapon_list,list) or len(weapon_list) != TOTAL_WEAPONS):
        raise ValueError("S138_CATALOG_COUNT_MISMATCH")

    rows_digest = hashlib.sha256()
    entries = {}
    prev_id = 0
    count_by_src = Counter()
    for row in rows:
        if not isinstance(row, list) or len(row) != 5:
            raise ValueError("S138_ITEM_ROW_SHAPE_MISMATCH")
        item_id, name, icon, src, equip_type = row
        if (not _is_strict_int(item_id) or item_id <= prev_id
            or not isinstance(name,str) or not name.strip()
            or not isinstance(icon,str) or not icon.strip()
            or not isinstance(src,str) or src not in SOURCE_COUNTS
            or (equip_type is not None and not isinstance(equip_type,str))):
            raise ValueError("S138_INVALID_OR_UNSORTED_ITEM_ROW")
        prev_id = item_id
        count_by_src[src] += 1
        rows_digest.update(
            f"{item_id}\t{name}\t{icon}\t{src}\t{equip_type or ''}\n".encode("utf-8")
        )
        entries[item_id] = OriginalItemMeta(item_id,name,icon,src,equip_type)
    if (dict(count_by_src) != SOURCE_COUNTS
        or rows_digest.hexdigest() != METADATA_ROWS_SHA256):
        raise ValueError("S138_ITEM_METADATA_CANONICAL_DIGEST_MISMATCH")

    prev_weapon = 0
    for wid in weapon_list:
        if not _is_strict_int(wid) or wid <= prev_weapon or wid not in entries:
            raise ValueError("S138_INVALID_OR_UNSORTED_WEAPON_IDS")
        prev_weapon = wid
    w_digest = hashlib.sha256(
        ("\n".join(str(wid) for wid in weapon_list)+"\n").encode("ascii")
    ).hexdigest()
    if w_digest != WEAPON_IDS_SHA256:
        raise ValueError("S138_WEAPON_ID_CANONICAL_DIGEST_MISMATCH")
    w_set = frozenset(weapon_list)
    allowed_types = {str(t) for t in TYPES_EXPECTED}
    expected_weapons = {
        k for k,v in entries.items()
        if v.src == "Equips" and v.equip_type in allowed_types
    }
    if w_set != expected_weapons:
        raise ValueError("S138_WEAPON_METADATA_CROSSJOIN_MISMATCH")

    return OriginalItemCatalog(
        source_exe_sha256=EXE_SHA256,
        entries=MappingProxyType(entries),
        weapon_ids=w_set,
        weapon_types=TYPES_EXPECTED,
    )
