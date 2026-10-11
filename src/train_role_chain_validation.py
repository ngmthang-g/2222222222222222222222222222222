"""S134 O02 source-backed pointer-chain / SessionData anchor safety proof.

Original frozen TLM 2.1.2 memory_reader.Reader documents _resolve_chain:
  dereference intermediate steps and return the object address BEFORE its
  terminal field offset, never apply the last offset twice. SessionData's
  RoleData slot must match the independently resolved role pointer.

This module is intentionally RESTRICTED TO MEMORY ALLOCATED BY THE CURRENT
TEST PYTHON PROCESS. It is NOT a live game reader, has no validated current
game build/layout/Info issuer, and does not create TrainCharacterSample.
The O02 original GA RVA and any other module offsets are NOT used in source.
Fixtures supply their own address/offsets and a strict owner-memory fence.
Native reads: Win64 OpenProcess(self, READ|QUERY), VirtualQueryEx then
ReadProcessMemory of an eight-byte value, CloseHandle. No writes/injection.
"""
from __future__ import annotations

from dataclasses import dataclass
import ctypes
import os
import sys
from typing import Protocol

from train_memory_module_probe import (
    READ_ONLY_RIGHTS, _MemoryBasicInformation,
    MEM_COMMIT, PAGE_GUARD, PAGE_NOACCESS, _READABLE,
)

TEST_LAYOUT_VERSION = "S134_TEST_OWNED_MEMORY_ONLY"
MAX_HOPS = 6
MAX_FIXTURE_RANGES = 16
MAX_64 = (1 << 64) - 1


@dataclass(frozen=True)
class OwnedMemoryRange:
    start: int
    size: int

    def covers(self, address: int, length: int = 8) -> bool:
        return (type(self.start) is int and type(self.size) is int
                and type(address) is int and type(length) is int
                and self.start > 0 and self.size >= 8 and length > 0
                and self.start <= address
                and address <= MAX_64 - length
                and address + length <= self.start + self.size
                and self.start + self.size <= MAX_64)


@dataclass(frozen=True)
class ReadQword:
    status: str
    value: int | None = None


class FixtureQwordReader(Protocol):
    """Read a single qword; errors are NEVER represented as zero."""
    def read_u64(self, address: int) -> ReadQword: ...


class SelfOwnedWin32QwordReader:
    """Real read-only Windows API against THIS process, within owned buffers.

    External PIDs are impossible by contract; no active game process can be
    targeted by this module. Ranges are supplied from live ctypes allocations
    owned by the test. On non-Win64 hosts, return an explicit unsupported code.
    """

    def __init__(self, ranges: tuple[OwnedMemoryRange, ...]):
        if (type(ranges) is not tuple or not 1 <= len(ranges) <= MAX_FIXTURE_RANGES
                or any(type(r) is not OwnedMemoryRange
                       or not r.covers(r.start) for r in ranges)):
            raise ValueError("INVALID_TEST_OWNED_MEMORY_RANGES")
        self.ranges = ranges

    def read_u64(self, address: int) -> ReadQword:
        if type(address) is not int or address <= 0 or address > MAX_64 - 8:
            return ReadQword("INVALID_POINTER_ADDRESS")
        if not any(region.covers(address, 8) for region in self.ranges):
            return ReadQword("POINTER_OUTSIDE_TEST_OWNED_RANGES")
        if os.name != "nt" or sys.maxsize <= 2**32 or ctypes.sizeof(ctypes.c_void_p) != 8:
            return ReadQword("WINDOWS_X64_REQUIRED")
        try:
            kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            dword, handle_t = ctypes.c_uint32, ctypes.c_void_p
            kernel.OpenProcess.argtypes = [dword, ctypes.c_int, dword]
            kernel.OpenProcess.restype = handle_t
            kernel.CloseHandle.argtypes = [handle_t]
            kernel.CloseHandle.restype = ctypes.c_int
            kernel.VirtualQueryEx.argtypes = [
                handle_t, handle_t, ctypes.POINTER(_MemoryBasicInformation),
                ctypes.c_size_t]
            kernel.VirtualQueryEx.restype = ctypes.c_size_t
            kernel.ReadProcessMemory.argtypes = [
                handle_t, handle_t, handle_t, ctypes.c_size_t,
                ctypes.POINTER(ctypes.c_size_t)]
            kernel.ReadProcessMemory.restype = ctypes.c_int
        except (AttributeError, OSError):
            return ReadQword("WIN32_READ_API_UNAVAILABLE")
        handle = kernel.OpenProcess(READ_ONLY_RIGHTS, 0, os.getpid())
        if not handle:
            return ReadQword("TEST_SELF_OPEN_PROCESS_FAILED")
        try:
            region = _MemoryBasicInformation()
            length = kernel.VirtualQueryEx(
                handle, handle_t(address), ctypes.byref(region),
                ctypes.sizeof(region))
            if length != ctypes.sizeof(region):
                return ReadQword("UNMAPPED_OR_UNKNOWN_REGION")
            if (region.State != MEM_COMMIT
                    or region.Protect & (PAGE_NOACCESS | PAGE_GUARD)
                    or (region.Protect & 0xFF) not in _READABLE
                    or region.BaseAddress is None
                    or not region.BaseAddress <= address
                    or address + 8 > region.BaseAddress + region.RegionSize):
                return ReadQword("UNREADABLE_OR_UNCOMMITTED_REGION")
            result = ctypes.c_uint64(0)
            num = ctypes.c_size_t(0)
            ok = kernel.ReadProcessMemory(
                handle, handle_t(address), ctypes.byref(result), 8,
                ctypes.byref(num))
            if not ok or num.value != 8:
                return ReadQword("INCOMPLETE_MEMORY_READ")
            return ReadQword("READ_QWORD", int(result.value))
        finally:
            kernel.CloseHandle(handle)


@dataclass(frozen=True)
class FixtureChainContract:
    # No original GameAssembly RVA/hard-coded game role offset is accepted.
    # All addresses are temporary user-owned test buffers.
    version: str
    root_slot: int
    hop_offsets: tuple[int, ...]
    terminal_offset: int
    session_role_slot: int
    owned_ranges: tuple[OwnedMemoryRange, ...]

    def valid(self) -> bool:
        return (type(self.version) is str and self.version == TEST_LAYOUT_VERSION
                and type(self.root_slot) is int
                and type(self.session_role_slot) is int
                and type(self.terminal_offset) is int
                and 0 <= self.terminal_offset <= 0x1000
                and type(self.hop_offsets) is tuple
                and 1 <= len(self.hop_offsets) <= MAX_HOPS
                and all(type(x) is int and 0 <= x <= 0x1000
                        for x in self.hop_offsets)
                and type(self.owned_ranges) is tuple
                and 1 <= len(self.owned_ranges) <= MAX_FIXTURE_RANGES
                and all(type(r) is OwnedMemoryRange
                        and r.covers(r.start) for r in self.owned_ranges))


@dataclass(frozen=True)
class FixtureChainResult:
    status: str
    traversed_hops: int = 0
    fixture_anchor_matches: bool = False
    role_data_verified_in_real_game: bool = False
    role_name_read: bool = False
    map_id_read: bool = False
    bag_site_10_read: bool = False


def validate_test_owned_role_chain(
    contract: FixtureChainContract, reader: FixtureQwordReader | None
) -> FixtureChainResult:
    """Read pointer steps and compare independently supplied fixture anchor.

    All positive outcomes are labelled TEST_ONLY and cannot be forwarded as
    RoleName/MapID/bag or real-game RoleData validation. A read failure,
    null pointer, outside ownership or mismatch never becomes zero/empty.
    """
    def fail(status: str, hops: int = 0) -> FixtureChainResult:
        return FixtureChainResult(status, hops)

    if type(contract) is not FixtureChainContract or not contract.valid():
        return fail("UNATTESTED_OR_INVALID_TEST_LAYOUT_VERSION")
    if reader is None or not callable(getattr(reader, "read_u64", None)):
        return fail("TEST_MEMORY_READER_UNAVAILABLE")

    def read_owned(address: int):
        if (type(address) is not int or address <= 0
                or address > MAX_64 - 8):
            return ReadQword("INVALID_POINTER_ADDRESS")
        if not any(r.covers(address) for r in contract.owned_ranges):
            return ReadQword("POINTER_OUTSIDE_TEST_OWNED_RANGES")
        try:
            observed = reader.read_u64(address)
        except Exception:
            return ReadQword("TEST_MEMORY_READ_EXCEPTION")
        if type(observed) is not ReadQword:
            return ReadQword("INVALID_READ_RESULT")
        if observed.status != "READ_QWORD":
            return ReadQword(observed.status)
        if type(observed.value) is not int or not 0 <= observed.value <= MAX_64:
            return ReadQword("INVALID_QWORD_VALUE")
        return observed

    first = read_owned(contract.root_slot)
    if first.status != "READ_QWORD":
        return fail("ROOT_" + first.status)
    node = first.value
    if not node:
        return fail("NULL_ROOT_POINTER")
    traversed = 0
    for offset in contract.hop_offsets:
        if not any(r.covers(node) for r in contract.owned_ranges):
            return fail("HOP_POINTER_OUTSIDE_TEST_MEMORY", traversed)
        if node > MAX_64 - offset:
            return fail("POINTER_OFFSET_OVERFLOW", traversed)
        field = read_owned(node + offset)
        if field.status != "READ_QWORD":
            return fail("HOP_" + field.status, traversed)
        traversed += 1
        if not field.value:
            return fail("NULL_INTERMEDIATE_POINTER", traversed)
        node = field.value
    # Crucial original _resolve_chain contract: node is the object BEFORE
    # adding the last field offset, not the final field/pointer itself.
    if not any(r.covers(node) for r in contract.owned_ranges):
        return fail("FINAL_OBJECT_OUTSIDE_TEST_MEMORY", traversed)
    if node > MAX_64 - contract.terminal_offset:
        return fail("TERMINAL_OFFSET_OVERFLOW", traversed)
    final_field = read_owned(node + contract.terminal_offset)
    if final_field.status != "READ_QWORD":
        return fail("ROLE_FIELD_" + final_field.status, traversed)
    role = final_field.value
    if not role:
        return fail("NULL_ROLE_FIELD_POINTER", traversed)
    if not any(r.covers(role) for r in contract.owned_ranges):
        return fail("ROLE_POINTER_OUTSIDE_TEST_MEMORY", traversed)
    anchor = read_owned(contract.session_role_slot)
    if anchor.status != "READ_QWORD":
        return fail("SESSION_ANCHOR_" + anchor.status, traversed)
    if not anchor.value:
        return fail("NULL_SESSION_ANCHOR", traversed)
    if anchor.value != role:
        return fail("SESSION_ROLE_ANCHOR_MISMATCH", traversed)
    return FixtureChainResult(
        "TEST_ONLY_POINTER_CHAIN_AND_SESSION_ANCHOR_VALIDATED",
        traversed, True)
