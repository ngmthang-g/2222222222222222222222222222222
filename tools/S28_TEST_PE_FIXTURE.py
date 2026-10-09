"""S28 TEST-OWNED synthetic minimal PE32+ headers; NEVER real executable.

These deliberately have structurally valid PE headers and arbitrary data,
only to test the bounded inspection rules. No build, load, inject or execute.
"""
from __future__ import annotations
from pathlib import Path
import struct


def write_test_pe(path: str | Path, *, dll: bool, machine: int = 0x8664,
                  optional_magic: int = 0x20B, malformed: str = "") -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    binary = bytearray(1024)
    binary[:2] = b"MZ"
    struct.pack_into("<I", binary, 0x3c, 0x80)
    binary[0x80:0x84] = b"PE\x00\x00"
    struct.pack_into("<HHIIIHH", binary, 0x84,
                     machine, 1, 0, 0, 0, 240, 0x0002 | (0x2000 if dll else 0))
    optional_start = 0x98
    struct.pack_into("<H", binary, optional_start, optional_magic)
    struct.pack_into("<I", binary, optional_start + 56, 4096)  # SizeOfImage
    struct.pack_into("<I", binary, optional_start + 60, 512)   # SizeOfHeaders
    section = 0x98 + 240
    binary[section:section+8] = b".text\x00\x00\x00"
    struct.pack_into("<IIII", binary, section + 8, 128, 0x1000, 16, 512)
    binary[512:528] = b"S28_NOT_EXECUTE!!"
    if malformed == "bad_mz":
        binary[:2] = b"XX"
    elif malformed == "bad_pe":
        binary[0x80:0x84] = b"XXXX"
    elif malformed == "bad_offset":
        struct.pack_into("<I", binary, 0x3c, 0xfffffff0)
    elif malformed == "no_section":
        struct.pack_into("<H", binary, 0x86, 0)
    elif malformed == "raw_truncated":
        struct.pack_into("<I", binary, section+16, 9999)
    elif malformed == "no_executable":
        struct.pack_into("<H", binary, 0x96, 0x2000 if dll else 0)
    elif malformed == "bad_image_size":
        struct.pack_into("<I", binary, optional_start + 56, 0)
    elif malformed == "truncated":
        binary = binary[:128]
    elif malformed:
        raise ValueError("Unknown synthetic fixture")
    path.write_bytes(binary)
    return path
