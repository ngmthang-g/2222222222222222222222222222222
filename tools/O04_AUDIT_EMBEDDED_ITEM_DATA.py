#!/usr/bin/env python3
"""Read-only O04 verifier for the frozen TLMTool 2.1.2 portable ZIP.

Never executes the EXE, uses Windows APIs, accesses a game, or writes items.
Strictly supports the SHA-pinned 2.1.2 binary, not arbitrary Nuitka formats.
"""
import collections
import hashlib
import json
import sys
import zipfile

ZIP_SHA = "c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd"
EXE_SHA = "15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22"
INNER = "TLMTool_2.1.2/TLMTool.dist/TLMTool.exe"


def uleb(blob, pos):
    result = 0
    for shift in range(0, 70, 7):
        byte = blob[pos]
        pos += 1
        result |= (byte & 127) << shift
        if byte < 128:
            return result, pos
    raise ValueError("Malformed varint")


def nul_utf8(blob, pos):
    end = blob.index(b"\x00", pos)
    return blob[pos:end].decode("utf-8"), end + 1


def tagged_text(blob, pos):
    tag = chr(blob[pos])
    pos += 1
    if tag in ("u", "a"):
        value, pos = nul_utf8(blob, pos)
    elif tag == "w":
        value = chr(blob[pos])
        pos += 1
    elif tag == "n":
        value = None
    else:
        raise ValueError("Unexpected metadata value tag %r" % tag)
    return value, pos, tag


def after_has_location(blob, start, end):
    marker = b"ahas_location\x00"
    pos = blob.index(marker, start, end)
    return pos + len(marker)


def metadata(blob):
    pos = after_has_location(blob, 0x2977206, 0x2977400)
    assert blob[pos:pos + 1] == b"D"
    count, pos = uleb(blob, pos + 1)
    keys = []
    for _ in range(count):
        assert blob[pos:pos + 1] == b"u"
        value, pos = nul_utf8(blob, pos + 1)
        assert value.isdecimal()
        keys.append(int(value))
    rows = []
    tags = collections.Counter()
    for _ in range(count):
        assert blob[pos:pos + 2] == b"T\x04"
        pos += 2
        row = []
        for _ in range(4):
            value, pos, tag = tagged_text(blob, pos)
            tags[tag] += 1
            row.append(value)
        rows.append(tuple(row))
    assert blob[pos:pos + 6] == b"aMETA\x00"
    assert len(set(keys)) == count
    return dict(zip(keys, rows)), dict(tags), pos


def weapon_set(blob):
    pos = after_has_location(blob, 0x2c54798, 0x2c54a00)
    assert blob[pos:pos + 1] == b"L"
    ntypes, pos = uleb(blob, pos + 1)
    types = []
    for _ in range(ntypes):
        assert blob[pos:pos + 1] == b"l"
        value, pos = uleb(blob, pos + 1)
        types.append(value)
    marker = b"aWEAPON_TYPES\x00"
    assert blob[pos:pos + len(marker)] == marker
    pos += len(marker)
    assert blob[pos:pos + 1] == b"S"
    n, pos = uleb(blob, pos + 1)
    ids = []
    for _ in range(n):
        assert blob[pos:pos + 1] == b"l"
        value, pos = uleb(blob, pos + 1)
        ids.append(value)
    assert blob[pos:pos + len(b"ais_weapon\x00")] == b"ais_weapon\x00"
    assert len(set(ids)) == n
    return set(ids), types, pos


def main(path):
    with open(path, "rb") as fp:
        zip_bytes = fp.read()
    assert hashlib.sha256(zip_bytes).hexdigest() == ZIP_SHA, "Archive SHA mismatch"
    with zipfile.ZipFile(path) as zf:
        assert zf.testzip() is None, "Corrupt ZIP member"
        blob = zf.read(INNER)
    assert hashlib.sha256(blob).hexdigest() == EXE_SHA, "EXE SHA mismatch"
    meta, tags, mend = metadata(blob)
    weapons, weapon_types, wend = weapon_set(blob)
    allowed = {item_id for item_id, row in meta.items() if row[2] == "Equips" and row[3] in {str(t) for t in weapon_types}}
    counts = collections.Counter(r[2] for r in meta.values())
    output = {
        "authority": {"zip_sha256": ZIP_SHA, "exe_sha256": EXE_SHA},
        "metadata_entries": len(meta),
        "metadata_unique_names": len({row[0] for row in meta.values()}),
        "metadata_unique_icons": len({row[1] for row in meta.values()}),
        "metadata_source_counts": dict(sorted(counts.items())),
        "metadata_equipment_type_null": sum(row[3] is None for row in meta.values()),
        "metadata_value_tags": tags,
        "metadata_end_offset": hex(mend),
        "weapon_ids": len(weapons),
        "weapon_types": weapon_types,
        "weapon_ids_missing_metadata": len(weapons - set(meta)),
        "weapon_ids_non_equip_or_other_type": len(weapons - allowed),
        "equip_allowed_ids_not_in_weapon_set": len(allowed - weapons),
        "weapon_end_offset": hex(wend),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python tools/O04_AUDIT_EMBEDDED_ITEM_DATA.py TLMTool_2.1.2.zip")
    main(sys.argv[1])
