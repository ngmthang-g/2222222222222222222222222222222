"""S136 OFFLINE, hash-pinned evidence audit of TLMTool 2.1.2 memory_items.

Reads the user-supplied frozen ZIP as immutable bytes. Reports EXACT Nuitka
embedded strings, fields, nearby tagged integer constants and uncertainty.
It does NOT decompile expressions, infer original offsets/stride, execute
the binary, query game memory, use packets or authenticate a product.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ARCHIVE_SHA256="c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd"
EXE_SHA256="15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22"
INNER="TLMTool_2.1.2/TLMTool.dist/TLMTool.exe"
REGION_BEGIN=0x2B69C5F
REGION_END=0x2B6AA00
PINNED={
    "module_marker":(0x2B69C5F,b".memory_items\x00"),
    "reader_unattached":(0x2B6A6DA,b"uReader chua attach\x00"),
    "role_items_provenance":(0x2B6A6F4,b"ard\x00l\xc8\x01"),
    "items_unloaded":(0x2B6A6FB,b"uItems null (nhan vat chua load?)\x00"),
    "empty_dictionary":(0x2B6A727,b"uTui rong (count=0)\x00"),
    "read_bag_row_doc":(
        0x2B6A7AF,
        b"u(rows, info). rows: [{dbID, itemID, site, pos, qty}]. Giu ten cu cho tuong thich.\x00"),
    "read_bag_symbol":(0x2B6A802,b"aread_bag\x00"),
    "bag_site_symbol":(0x2B6A814,b"aBAG_SITE\x00"),
    "get_bag_sort_lambda":(0x2B6A828,b"uget_bag.<locals>.<lambda>\x00"),
    "get_bag_doc":(
        0x2B6A8A2,b"uTong hop tui Site 10 + enrich ten. Tra dict hoac None.\x00"),
}
READ_ROW_FIELDS=("dbID","itemID","site","pos","qty")
GET_BAG_FIELDS=("name","icon","src","type","etype","slots","distinct","total_qty","non_bag","info")
UNCERTAIN=(
    "Exact original Python read_bag return tuple per failure branch",
    "Type and shape of info for every read_bag failure",
    "Actual dictionary count offset and entries pointer",
    "Actual dictionary entry stride and field byte offsets",
    "Meaning/usage of adjacent integers 24, 32, 10000, 65536, 1000000",
    "Full KNOWN_SITES membership and original filtering predicates",
    "get_bag sort key, field nesting, and aggregate arithmetic",
    "Read concurrency consistency/retry and actual live game version",
    "Genuine signed Info and authorized live process reader",
)

def decode_uleb(data: bytes, pos: int) -> tuple[int,int]:
    number=0
    for i in range(10):
        if pos >= len(data):
            raise ValueError("TRUNCATED_UNSIGNED_LEB128")
        byte=data[pos];pos+=1
        number |= (byte & 127) << (7*i)
        if byte < 128:
            if number >= 1 << 64:
                raise ValueError("OVERFLOW_UNSIGNED_LEB128")
            return number,pos
    raise ValueError("OVERLONG_UNSIGNED_LEB128")

def pinned_at(data: bytes, offset: int, literal: bytes) -> bool:
    return (type(data) is bytes and type(offset) is int and
            type(literal) is bytes and data[offset:offset+len(literal)]==literal)

def occurrences(data: bytes, pattern: bytes, lo: int, hi: int) -> list[int]:
    found=[]
    pos=lo
    while pos < hi:
        next_pos=data.find(pattern,pos,hi)
        if next_pos<0:
            break
        found.append(next_pos)
        pos=next_pos+1
    return found

def audit_exe(data: bytes, *, enforce_hash: bool = True) -> dict:
    if type(data) is not bytes or len(data)<REGION_END:
        raise ValueError("NOT_PINNED_TLM_INNER_EXE")
    digest=hashlib.sha256(data).hexdigest()
    if enforce_hash and digest!=EXE_SHA256:
        raise ValueError("ORIGINAL_EXE_HASH_MISMATCH")
    checks={}
    for key,(offset,literal) in PINNED.items():
        if not pinned_at(data,offset,literal):
            raise ValueError("ORIGINAL_BINARY_MARKER_CHANGED_"+key)
        checks[key]={"offset":hex(offset),"literal_utf8":literal.decode("utf-8","replace").rstrip("\x00")}
    start,end=0x2B6A6DA,0x2B6A8A2
    for f in READ_ROW_FIELDS:
        # Original site appears in the read_bag embedded doc, but there is
        # NO adjacent 'asite' emitted-field symbol in this binary section.
        if f=="site":
            continue
        token=("a"+f+"\x00").encode("utf8")
        if not occurrences(data,token,start,end):
            raise ValueError("MISSING_PINNED_ROW_FIELD_"+f)
    for f in GET_BAG_FIELDS:
        # The original adjacent etype text begins 'saetype': the 'aetype'
        # substring is observable, but bytecode field assignment is unknown.
        tags=("a",)
        if not any(occurrences(data,(tag+f+"\x00").encode(),start,end) for tag in tags):
            raise ValueError("MISSING_PINNED_GET_BAG_FIELD_"+f)
    # These typed literals are adjacent to read_bag constants, but cannot
    # be assigned to source-level dictionary fields on this evidence alone.
    numeric_lo=data.index(b"uItems null (nhan vat chua load?)\x00",start,end)
    numeric_hi=data.index(b"aout\x00",numeric_lo,end)
    integers={}
    pinned_num_offsets={24:0x2B6A71D,32:0x2B6A725,
                        10000:0x2B6A740,65536:0x2B6A758,1000000:0x2B6A76D}
    for val,observed_offset in pinned_num_offsets.items():
        encoded=[]
        n=val
        while True:
            b=n & 127;n >>= 7
            encoded.append(b | (128 if n else 0))
            if not n:break
        # Unanchored substring search would mistake the literal 'null '
        # for the tagged constant 'l\\x20'. A pinned byte offset proves
        # the numeric token rather than merely matching arbitrary text.
        pos=observed_offset
        if not (numeric_lo <= pos < numeric_hi and
                pinned_at(data,pos,b"l"+bytes(encoded))):
            raise ValueError("UNEXPECTED_NEARBY_TAGGED_INT_"+str(val))
        decoded,last=decode_uleb(data,pos+1)
        if decoded!=val or last!=pos+1+len(encoded):
            raise ValueError("INCONSISTENT_TAGGED_INT")
        integers[str(val)]={"offset":hex(pos),"tag":"l","association":"ADJACENT_ONLY_NOT_FIELD_BINDING"}
    return {
        "status":"PASS_S136_OFFLINE_ORIGINAL_EMBEDDED_BAG_EVIDENCE_ONLY",
        "authority":{"original_inner_exe_sha256":digest,"hash_pinned":bool(enforce_hash)},
        "pinned_literals":checks,
        "embedded_read_bag":{"tuple_shape_documented":"(rows, info)",
                             "row_fields_documented":list(READ_ROW_FIELDS),
                             "failure_diagnostics":["reader_unattached","items_unloaded","empty_dictionary"],
                             "live_return_shapes_verified":False},
        "embedded_get_bag":{"site_documented":10,"return_documented":"dict or None",
                            "observed_field_symbols":list(GET_BAG_FIELDS),
                            "sort_and_aggregation_expression_verified":False},
        "adjacent_typed_numeric_literals":integers,
        "unknowns":list(UNCERTAIN),
        "live_game_inventory_read":False,
        "full_original_python_ast_recovered":False,
        "game_or_auth_actions":False,
    }

def audit_zip(path: Path) -> dict:
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=ARCHIVE_SHA256:
        raise ValueError("ORIGINAL_ZIP_HASH_MISMATCH")
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:
            raise ValueError("ORIGINAL_ZIP_BAD_CRC")
        original=z.read(INNER)
    report=audit_exe(original)
    report["authority"]["original_zip_sha256"]=ARCHIVE_SHA256
    return report

def synthetic_self_test() -> None:
    assert decode_uleb(bytes((0xC8,0x01)),0)==(200,2)
    assert decode_uleb(bytes((0x80,0x80,0x04)),0)==(65536,3)
    for bad in (b"\x80",b"\x80"*11):
        try:decode_uleb(bad,0)
        except ValueError:pass
        else:raise AssertionError("INVALID_VARINT_ACCEPTED")
    assert pinned_at(b"xxuItem\0zz",2,b"uItem\0")
    assert not pinned_at(b"xxuItem\0zz",3,b"uItem\0")
    assert occurrences(b"abcabc",b"abc",0,6)==[0,3]
    print("S136_SYNTHETIC_PARSER_SELFTEST=PASS_NO_ORIGINAL_EXE_REQUIRED")

def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument("original_zip",nargs="?",type=Path)
    parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--out",type=Path)
    args=parser.parse_args(argv)
    if args.self_test:
        synthetic_self_test()
        return 0
    if args.original_zip is None:
        parser.error("Original user-supplied ZIP path required unless --self-test")
    report=audit_zip(args.original_zip)
    result=json.dumps(report,ensure_ascii=False,indent=2)+"\n"
    if args.out:args.out.write_text(result,encoding="utf-8")
    print(result)
    return 0

if __name__=="__main__":
    sys.exit(main())
