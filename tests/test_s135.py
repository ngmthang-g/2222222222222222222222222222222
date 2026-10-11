"""S135 O03 test-owned Site10 read-only dictionary boundaries."""
from __future__ import annotations
import ast
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from train_role_chain_validation import OwnedMemoryRange, ReadQword, SelfOwnedWin32QwordReader
from train_bag_tristate_fixture import (
    BAG_TEST_VERSION, SITE_BAG, MAX_TEST_ROWS, TestBagLayout,
    TestBagRow, TestBagResult, inspect_test_owned_site10,
)

class Reader:
    def __init__(self, values):
        self.values=values
        self.calls=[]
    def read_u64(self, address):
        self.calls.append(address)
        v=self.values.get(address,ReadQword('UNMAPPED_OR_UNKNOWN_REGION'))
        return v if isinstance(v,ReadQword) else ReadQword('READ_QWORD',v)

class TestS135(unittest.TestCase):
    def setUp(self):
        self.items=0x2000; self.entries=0x3000; self.slot=0x1000
        self.layout=TestBagLayout(BAG_TEST_VERSION,self.slot,0,8,40,(
            OwnedMemoryRange(self.slot,64),
            OwnedMemoryRange(self.items,64),
            OwnedMemoryRange(self.entries,256),
        ))
        self.data={self.slot:self.items,self.items:2,self.items+8:self.entries}
        self.row(0,11,101,10,0,3)
        self.row(1,12,102,2,1,7)
    def row(self,i,*fields):
        for j,v in enumerate(fields):self.data[self.entries+i*40+j*8]=v
    def result(self,data=None,layout=None):
        reader=Reader(self.data if data is None else data)
        return inspect_test_owned_site10(self.layout if layout is None else layout,reader),reader
    def test_01_version_is_test_only(self):
        self.assertEqual(BAG_TEST_VERSION,'S135_TEST_OWNED_BAG_ONLY')
    def test_02_valid_mixed_sites(self):
        r,_=self.result()
        self.assertEqual(r.status,'TEST_SITE10_ROWS_OBSERVED')
        self.assertEqual(r.rows,(TestBagRow(11,101,10,0,3),))
        self.assertEqual(r.observed_dictionary_count,2)
        self.assertEqual(r.observed_other_site_rows,1)
    def test_03_test_success_never_real_game(self):
        r,_=self.result()
        self.assertFalse(r.verified_game_bag or r.verified_game_memory or r.item_action_sent)
    def test_04_reader_unattached_not_zero(self):
        r=inspect_test_owned_site10(self.layout,None)
        self.assertEqual(r.status,'READER_NOT_ATTACHED')
        self.assertIsNone(r.rows)
    def test_05_items_null_not_empty(self):
        r,_=self.result({**self.data,self.slot:0})
        self.assertEqual(r.status,'ITEMS_NULL_UNLOADED')
        self.assertIsNone(r.observed_dictionary_count)
    def test_06_count_zero_is_true_empty(self):
        r,reader=self.result({**self.data,self.items:0})
        self.assertEqual(r.status,'TEST_EMPTY_ITEMS_DICTIONARY')
        self.assertEqual(r.rows,())
        self.assertNotIn(self.items+8,reader.calls)
    def test_07_only_other_sites_is_valid_empty_site10(self):
        data={**self.data,self.entries+2*8:2}
        r,_=self.result(data)
        self.assertEqual(r.status,'TEST_SITE10_EMPTY_OTHER_SITES_ONLY')
        self.assertEqual(r.rows,())
        self.assertEqual(r.observed_dictionary_count,2)
    def test_08_count_unreadable_is_not_zero(self):
        data=dict(self.data);data.pop(self.items)
        r,_=self.result(data)
        self.assertTrue(r.status.startswith('COUNT_'))
        self.assertIsNone(r.rows)
    def test_09_items_pointer_unreadable_is_not_empty(self):
        data=dict(self.data);data.pop(self.slot)
        r,_=self.result(data)
        self.assertTrue(r.status.startswith('ITEMS_'))
        self.assertIsNone(r.rows)
    def test_10_items_pointer_outside(self):
        r,_=self.result({**self.data,self.slot:0x9000})
        self.assertEqual(r.status,'ITEMS_POINTER_OUTSIDE_TEST_MEMORY')
    def test_11_entries_null_count_nonzero(self):
        r,_=self.result({**self.data,self.items+8:0})
        self.assertEqual(r.status,'ENTRIES_NULL_WHILE_COUNT_NONZERO')
    def test_12_entries_unmapped_not_empty(self):
        r,_=self.result({**self.data,self.items+8:0x9000})
        self.assertEqual(r.status,'ENTRIES_POINTER_OUTSIDE_TEST_MEMORY')
    def test_13_count_cap_refuses(self):
        r,_=self.result({**self.data,self.items:MAX_TEST_ROWS+1})
        self.assertEqual(r.status,'TEST_DICTIONARY_COUNT_OUT_OF_BOUNDS')
    def test_14_row_read_error_discards_partial(self):
        data=dict(self.data);data.pop(self.entries+40+4*8)
        r,_=self.result(data)
        self.assertTrue(r.status.startswith('ROW_1_qty'))
        self.assertIsNone(r.rows)
    def test_15_invalid_qty_refuses(self):
        r,_=self.result({**self.data,self.entries+4*8:0})
        self.assertEqual(r.status,'TEST_ROW_INVALID_FIELD_VALUES')
    def test_16_not_a_pixel_pos(self):
        r,_=self.result()
        self.assertEqual(r.rows[0].pos,0)
    def test_17_bad_layout_version_fails_before_read(self):
        r,rd=self.result(layout=replace(self.layout,version='GAME_UNKNOWN'))
        self.assertEqual(r.status,'UNKNOWN_OR_INVALID_TEST_DICTIONARY_LAYOUT')
        self.assertEqual(rd.calls,[])
    def test_18_bad_stride_fails_before_read(self):
        r,rd=self.result(layout=replace(self.layout,row_stride=4))
        self.assertEqual(r.status,'UNKNOWN_OR_INVALID_TEST_DICTIONARY_LAYOUT')
        self.assertEqual(rd.calls,[])
    def test_19_cannot_turn_test_pass_into_game(self):
        r,_=self.result()
        with self.assertRaises(FrozenInstanceError):r.verified_game_bag=True
    def test_20_reader_exception_never_empty(self):
        class Broken:
            def read_u64(self,_):raise OSError('no')
        r=inspect_test_owned_site10(self.layout,Broken())
        self.assertEqual(r.status,'ITEMS_READ_EXCEPTION')
    def test_21_bad_reader_shape(self):
        class Broken:
            def read_u64(self,_):return 0
        r=inspect_test_owned_site10(self.layout,Broken())
        self.assertEqual(r.status,'ITEMS_INVALID_READ_RESULT')
    def test_22_invalid_qword(self):
        r,_=self.result({**self.data,self.items:ReadQword('READ_QWORD',-1)})
        self.assertEqual(r.status,'COUNT_INVALID_VALUE')
    def test_23_no_external_process_reader(self):
        import inspect
        self.assertNotIn('pid',inspect.signature(SelfOwnedWin32QwordReader.__init__).parameters)
        raw=(ROOT/'src/train_bag_tristate_fixture.py').read_text(encoding='utf8')
        for name in ('WriteProcessMemory','CreateRemoteThread','SendInput(', 'RequestSellItem(', '0x355B208'):
            self.assertNotIn(name,raw)
    def test_24_syntax_source_and_tests(self):
        for p in ('src/train_bag_tristate_fixture.py','tests/test_s135.py'):
            ast.parse((ROOT/p).read_text(encoding='utf8'))

if __name__=='__main__':unittest.main()
