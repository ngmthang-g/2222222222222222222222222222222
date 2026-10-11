"""S135 O03: TEST-OWNED read-only Site-10 dictionary state classifier.

Original binary evidence differentiates reader missing, Items null/unloaded,
valid count=0, and valid inventory rows. Dictionary offsets, stride, capacity,
read return variants, and the current game layout are UNKNOWN. All numeric
layout offsets here come from an explicit TEST fixture; they are NOT game
memory addresses. No native PID target, UI, packet, or product reader is added.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from train_role_chain_validation import (
    MAX_64, OwnedMemoryRange, ReadQword,
)

BAG_TEST_VERSION = "S135_TEST_OWNED_BAG_ONLY"
SITE_BAG = 10
MAX_TEST_ROWS = 16  # test allocation bound; not the game's dictionary cap
FIELDS = ("dbID", "itemID", "site", "pos", "qty")


@dataclass(frozen=True)
class TestBagLayout:
    version: str
    items_pointer_slot: int
    count_offset: int
    entries_offset: int
    row_stride: int
    owned_ranges: tuple[OwnedMemoryRange, ...]

    def valid(self) -> bool:
        return (
            type(self.version) is str and self.version == BAG_TEST_VERSION
            and type(self.items_pointer_slot) is int
            and type(self.count_offset) is int and 0 <= self.count_offset <= 4096
            and type(self.entries_offset) is int and 0 <= self.entries_offset <= 4096
            and self.count_offset != self.entries_offset
            and type(self.row_stride) is int and 40 <= self.row_stride <= 4096
            and self.row_stride % 8 == 0
            and type(self.owned_ranges) is tuple
            and 1 <= len(self.owned_ranges) <= 16
            and all(type(r) is OwnedMemoryRange and r.covers(r.start)
                    for r in self.owned_ranges)
        )


@dataclass(frozen=True)
class TestBagRow:
    dbID: int
    itemID: int
    site: int
    pos: int
    qty: int


@dataclass(frozen=True)
class TestBagResult:
    status: str
    rows: tuple[TestBagRow, ...] | None = None
    observed_dictionary_count: int | None = None
    observed_other_site_rows: int | None = None
    verified_game_bag: bool = False
    verified_game_memory: bool = False
    item_action_sent: bool = False

    @property
    def valid_test_snapshot(self) -> bool:
        return self.status in (
            "TEST_EMPTY_ITEMS_DICTIONARY",
            "TEST_SITE10_ROWS_OBSERVED",
            "TEST_SITE10_EMPTY_OTHER_SITES_ONLY",
        )


class BagFixtureQwordReader(Protocol):
    def read_u64(self, address: int) -> ReadQword: ...


def inspect_test_owned_site10(
    layout: TestBagLayout, reader: BagFixtureQwordReader | None,
) -> TestBagResult:
    """Reject unreadable/unloaded/moving data, preserve valid zero distinctly.

    This is a fixture parser, not original read_bag/get_bag parity. It never
    produces a TrainCharacterSample or a game-facing inventory object.
    """
    def fail(code: str) -> TestBagResult:
        return TestBagResult(code)

    if type(layout) is not TestBagLayout or not layout.valid():
        return fail("UNKNOWN_OR_INVALID_TEST_DICTIONARY_LAYOUT")
    if reader is None or not callable(getattr(reader, "read_u64", None)):
        return fail("READER_NOT_ATTACHED")

    def read(address: int, label: str) -> tuple[str, int | None]:
        if type(address) is not int or not 0 < address <= MAX_64 - 8:
            return label + "_INVALID_ADDRESS", None
        if not any(r.covers(address, 8) for r in layout.owned_ranges):
            return label + "_OUTSIDE_TEST_MEMORY", None
        try:
            word = reader.read_u64(address)
        except Exception:
            return label + "_READ_EXCEPTION", None
        if type(word) is not ReadQword:
            return label + "_INVALID_READ_RESULT", None
        if word.status != "READ_QWORD":
            return label + "_" + str(word.status), None
        if type(word.value) is not int or not 0 <= word.value <= MAX_64:
            return label + "_INVALID_VALUE", None
        return "OK", word.value

    status, items = read(layout.items_pointer_slot, "ITEMS")
    if status != "OK":
        return fail(status)
    if items == 0:
        return fail("ITEMS_NULL_UNLOADED")
    if not any(r.covers(items, 8) for r in layout.owned_ranges):
        return fail("ITEMS_POINTER_OUTSIDE_TEST_MEMORY")
    if (items > MAX_64 - layout.count_offset
            or items > MAX_64 - layout.entries_offset):
        return fail("ITEMS_FIELD_ADDRESS_OVERFLOW")
    status, count = read(items + layout.count_offset, "COUNT")
    if status != "OK":
        return fail(status)
    if count > MAX_TEST_ROWS:
        return fail("TEST_DICTIONARY_COUNT_OUT_OF_BOUNDS")

    records: list[TestBagRow] = []
    other_sites = 0
    if count:
        status, entries = read(items + layout.entries_offset, "ENTRIES")
        if status != "OK":
            return fail(status)
        if entries == 0:
            return fail("ENTRIES_NULL_WHILE_COUNT_NONZERO")
        if not any(r.covers(entries, 8) for r in layout.owned_ranges):
            return fail("ENTRIES_POINTER_OUTSIDE_TEST_MEMORY")
        if entries > MAX_64 - ((count - 1) * layout.row_stride + 40):
            return fail("ENTRIES_ADDRESS_OVERFLOW")
        for i in range(count):
            values = []
            for j, field in enumerate(FIELDS):
                status, value = read(entries + i * layout.row_stride + j * 8,
                                     f"ROW_{i}_{field}")
                if status != "OK":
                    return fail(status)
                values.append(value)
            dbid, itemid, site, pos, qty = values
            if not (0 < dbid <= MAX_64 and 0 < itemid <= MAX_64
                    and 0 <= site <= 65535 and 0 <= pos <= 65535
                    and 0 < qty <= 1000000):
                return fail("TEST_ROW_INVALID_FIELD_VALUES")
            if site == SITE_BAG:
                records.append(TestBagRow(dbid, itemid, site, pos, qty))
            else:
                other_sites += 1

    # A second count read detects a common torn-snapshot case. It does not
    # prove atomicity when the underlying dictionary mutates and returns to
    # the same count; game-side snapshot parity remains unverified.
    status, after = read(items + layout.count_offset, "COUNT_RECHECK")
    if status != "OK":
        return fail(status)
    if after != count:
        return fail("DICTIONARY_COUNT_CHANGED_DURING_TEST_READ")
    state = ("TEST_EMPTY_ITEMS_DICTIONARY" if count == 0 else
             "TEST_SITE10_ROWS_OBSERVED" if records else
             "TEST_SITE10_EMPTY_OTHER_SITES_ONLY")
    return TestBagResult(state, tuple(records), count, other_sites)
