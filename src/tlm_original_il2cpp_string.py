"""S198 bounded read-only IL2CPP string decoding for original TLM RoleName.

Source basis:
- S197 original Nuitka memory_reader constant layout gives RoleName at
  RoleData+0x18 of pointer format P and original _rstr uses UTF-16-LE.
- Public Unity libil2cpp struct Il2CppString = Il2CppObject { klass,
  monitor pointers } + int32 length + Il2CppChar chars[], for Win64:
  length at +0x10, UTF-16 data at +0x14. This is an ABI candidate,
  NOT direct proof that the original binary's _rstr had exactly the
  same bounds/implementation, and NOT proof a live user game shares ABI.

Only a caller that already validated correct source HWND/PID, build files,
RoleData chain and SessionData anchor may attempt this native memory read.
Never report candidate names as a logged-in character, connect to Party,
write process memory, spoof game values or send commands.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata
from typing import Protocol

IL2CPP_STRING_LENGTH_OFFSET_WIN64 = 0x10
IL2CPP_STRING_CHARS_OFFSET_WIN64 = 0x14
MAX_ROLE_NAME_CODE_UNITS_LOCAL = 80
CHUNK_MAX_BYTES = 64
MAX_USER_POINTER = 0x00007FFFFFFFFFFF
_TAGS = re.compile(r"<[^>]*>")


class ReadOnlyBytes(Protocol):
    def bytes(self, address: int, size: int) -> bytes | None: ...


@dataclass(frozen=True)
class OriginalRoleStringCandidate:
    status: str
    role_name: str | None = None
    # An ordinary IL2CPP layout guess + valid UTF16 bytes is not a live
    # original TLM reader equivalence or character login attestation.
    character_identity_verified: bool = False
    gameplay_action_authorized: bool = False


def _read_utf16_chunks(reader: ReadOnlyBytes, pointer: int,
                       length_bytes: int) -> bytes | None:
    result = bytearray()
    offset = 0
    while offset < length_bytes:
        step = min(CHUNK_MAX_BYTES, length_bytes-offset)
        if (pointer + offset > MAX_USER_POINTER-step
                or pointer+offset < 0x10000):
            return None
        try:
            raw = reader.bytes(pointer+offset, step)
        except (OSError, ValueError, RuntimeError, TypeError, OverflowError):
            return None
        if type(raw) is not bytes or len(raw) != step:
            return None
        result.extend(raw)
        offset += step
    return bytes(result)


def read_original_role_name_candidate(
    reader: ReadOnlyBytes, name_pointer: int,
) -> OriginalRoleStringCandidate:
    """Conservative managed UTF-16 decode with pre/post header+body proof.

    Uses NO user-facing fallback such as window title, saved account
    config, simulated RoleName or untrusted network data. A zero-length,
    changed string, control character or invalid surrogate rejects.
    """
    def fail(status):
        return OriginalRoleStringCandidate(status)

    if (not callable(getattr(reader, "bytes", None))
            or type(name_pointer) is not int
            or name_pointer < 0x10000
            or name_pointer > MAX_USER_POINTER-0x20
            or name_pointer % 8):
        return fail("INVALID_ROLE_NAME_POINTER")
    # Conventional x64 IL2CPP object: class pointer at +0,
    # monitor pointer at +8, length int32 +16, chars wchar16 +20.
    header = _read_utf16_chunks(reader, name_pointer, 20)
    if header is None:
        return fail("IL2CPP_STRING_HEADER_UNREADABLE")
    klass = int.from_bytes(header[0:8], "little")
    length = int.from_bytes(header[16:20], "little", signed=True)
    if (klass < 0x10000 or klass > MAX_USER_POINTER or klass % 8):
        return fail("IL2CPP_CLASS_POINTER_IMPLAUSIBLE")
    if not 1 <= length <= MAX_ROLE_NAME_CODE_UNITS_LOCAL:
        return fail("IL2CPP_ROLE_NAME_LENGTH_INVALID")
    text_ptr = name_pointer + IL2CPP_STRING_CHARS_OFFSET_WIN64
    first = _read_utf16_chunks(reader, text_ptr, length*2)
    if first is None:
        return fail("IL2CPP_UTF16_BODY_UNREADABLE")
    # Fail closed on a UI/map/relogin generation change that replaces the
    # string or modifies its contents during a remote memory scan.
    second_header = _read_utf16_chunks(reader, name_pointer, 20)
    second = _read_utf16_chunks(reader, text_ptr, length*2)
    if second_header != header or second != first:
        return fail("IL2CPP_ROLE_NAME_CHANGED_DURING_READ")
    try:
        raw_name = first.decode("utf-16-le", errors="strict")
    except UnicodeDecodeError:
        return fail("IL2CPP_ROLE_NAME_INVALID_UTF16")
    # Original S90 and S125 sanitize embedded name formatting tags for
    # display. Keep this as a separate presentation step, not source proof.
    cleaned = _TAGS.sub("", raw_name).strip()
    if (not cleaned or len(cleaned) > MAX_ROLE_NAME_CODE_UNITS_LOCAL
            or any(unicodedata.category(ch) in ("Cc", "Cs")
                   for ch in cleaned)):
        return fail("IL2CPP_ROLE_NAME_NOT_PLAUSIBLE")
    return OriginalRoleStringCandidate(
        "IL2CPP_UTF16_CANDIDATE_NEEDS_ACTUAL_GAME_ATTESTATION", cleaned)
