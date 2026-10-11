"""S134 test-owned memory pointer-chain reader: O02 source semantics only.

No external game, no authentication grant. Static fixtures use made-up
addresses with O02's evidence-backed +B8 and +88 traversal shape; they
are NOT asserted as a valid role offset for any live Than Long build.
"""
from __future__ import annotations
import ast
from dataclasses import FrozenInstanceError
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from train_role_chain_validation import (
    TEST_LAYOUT_VERSION, MAX_HOPS, MAX_FIXTURE_RANGES, MAX_64,
    OwnedMemoryRange, ReadQword, SelfOwnedWin32QwordReader,
    FixtureChainContract, FixtureChainResult, validate_test_owned_role_chain,
)


class FakeOwnedReader:
    def __init__(self, memory):
        self.memory=dict(memory)
        self.calls=[]
    def read_u64(self,address):
        self.calls.append(address)
        if address not in self.memory:
            return ReadQword("UNMAPPED_OR_UNKNOWN_REGION")
        val=self.memory[address]
        return val if type(val) is ReadQword else ReadQword("READ_QWORD",val)


class S134RoleFixtureTests(unittest.TestCase):
    def setUp(self):
        self.root=0x1000
        self.a=0x2000
        self.b=0x3000
        self.role=0x4000
        self.session=0x5000
        self.ranges=tuple(OwnedMemoryRange(a,0x200)
                           for a in (self.root,self.a,self.b,
                                     self.role,self.session))
        self.contract=FixtureChainContract(
            TEST_LAYOUT_VERSION,self.root,(0xB8,),0x88,
            self.session+0x88,self.ranges)
        self.data={
            self.root:self.a,
            self.a+0xB8:self.b,
            self.b+0x88:self.role,
            self.session+0x88:self.role
        }

    def resolve(self, data=None, contract=None):
        reader=FakeOwnedReader(self.data if data is None else data)
        result=validate_test_owned_role_chain(
            self.contract if contract is None else contract,reader)
        return result,reader

    def test_01_test_layout_only_version(self):
        self.assertEqual(TEST_LAYOUT_VERSION,"S134_TEST_OWNED_MEMORY_ONLY")

    def test_02_positive_fixture_chain_anchor(self):
        r,reader=self.resolve()
        self.assertEqual(r.status,"TEST_ONLY_POINTER_CHAIN_AND_SESSION_ANCHOR_VALIDATED")
        self.assertEqual(r.traversed_hops,1)
        self.assertTrue(r.fixture_anchor_matches)
        self.assertEqual(reader.calls,[
            self.root,self.a+0xB8,self.b+0x88,self.session+0x88])

    def test_03_even_positive_never_real_game_role(self):
        r,_=self.resolve()
        self.assertFalse(r.role_data_verified_in_real_game)
        self.assertFalse(r.role_name_read or r.map_id_read or r.bag_site_10_read)

    def test_04_last_offset_read_exactly_once(self):
        _,reader=self.resolve()
        self.assertNotIn(self.role+0x88,reader.calls)
        self.assertEqual(reader.calls.count(self.b+0x88),1)

    def test_05_mismatching_build_version_refused_without_reads(self):
        from dataclasses import replace
        bad=replace(self.contract,version="GAME_UNKNOWN")
        r,reader=self.resolve(contract=bad)
        self.assertEqual(r.status,"UNATTESTED_OR_INVALID_TEST_LAYOUT_VERSION")
        self.assertFalse(reader.calls)

    def test_06_null_root(self):
        data={**self.data,self.root:0}
        r,_=self.resolve(data)
        self.assertEqual(r.status,"NULL_ROOT_POINTER")

    def test_07_root_read_error_not_empty_character(self):
        data={**self.data,self.root:ReadQword("UNMAPPED_OR_UNKNOWN_REGION")}
        r,_=self.resolve(data)
        self.assertEqual(r.status,"ROOT_UNMAPPED_OR_UNKNOWN_REGION")

    def test_08_intermediate_null(self):
        data={**self.data,self.a+0xB8:0}
        r,_=self.resolve(data)
        self.assertEqual(r.status,"NULL_INTERMEDIATE_POINTER")

    def test_09_broken_next_pointer_fenced_before_access(self):
        data={**self.data,self.root:0xF000}
        r,reader=self.resolve(data)
        self.assertEqual(r.status,"HOP_POINTER_OUTSIDE_TEST_MEMORY")
        self.assertEqual(reader.calls,[self.root])

    def test_10_hop_field_unmapped(self):
        data=dict(self.data);data.pop(self.a+0xB8)
        r,_=self.resolve(data)
        self.assertEqual(r.status,"HOP_UNMAPPED_OR_UNKNOWN_REGION")

    def test_11_final_object_outside_fixture(self):
        data={**self.data,self.a+0xB8:0xE000}
        r,_=self.resolve(data)
        self.assertEqual(r.status,"FINAL_OBJECT_OUTSIDE_TEST_MEMORY")

    def test_12_final_field_null(self):
        data={**self.data,self.b+0x88:0}
        r,_=self.resolve(data)
        self.assertEqual(r.status,"NULL_ROLE_FIELD_POINTER")

    def test_13_final_pointer_outside_fixture(self):
        data={**self.data,self.b+0x88:0xE000}
        r,_=self.resolve(data)
        self.assertEqual(r.status,"ROLE_POINTER_OUTSIDE_TEST_MEMORY")

    def test_14_final_field_unreadable(self):
        data={**self.data,self.b+0x88:ReadQword("UNREADABLE_OR_UNCOMMITTED_REGION")}
        r,_=self.resolve(data)
        self.assertEqual(r.status,"ROLE_FIELD_UNREADABLE_OR_UNCOMMITTED_REGION")

    def test_15_independent_anchor_mismatch(self):
        data={**self.data,self.session+0x88:self.a}
        r,_=self.resolve(data)
        self.assertEqual(r.status,"SESSION_ROLE_ANCHOR_MISMATCH")

    def test_16_null_anchor(self):
        data={**self.data,self.session+0x88:0}
        r,_=self.resolve(data)
        self.assertEqual(r.status,"NULL_SESSION_ANCHOR")

    def test_17_anchor_unreadable(self):
        data=dict(self.data);data.pop(self.session+0x88)
        r,_=self.resolve(data)
        self.assertEqual(r.status,"SESSION_ANCHOR_UNMAPPED_OR_UNKNOWN_REGION")

    def test_18_root_unowned(self):
        from dataclasses import replace
        c=replace(self.contract,root_slot=0x7777)
        r,reader=self.resolve(contract=c)
        self.assertEqual(r.status,"ROOT_POINTER_OUTSIDE_TEST_OWNED_RANGES")
        self.assertFalse(reader.calls)

    def test_19_terminal_offset_exceeds_buffer(self):
        from dataclasses import replace
        c=replace(self.contract,terminal_offset=0x400)
        r,_=self.resolve(contract=c)
        self.assertEqual(r.status,"ROLE_FIELD_POINTER_OUTSIDE_TEST_OWNED_RANGES")

    def test_20_invalid_offset_negative_fails_preflight(self):
        from dataclasses import replace
        r,reader=self.resolve(contract=replace(self.contract,hop_offsets=(-1,)))
        self.assertEqual(r.status,"UNATTESTED_OR_INVALID_TEST_LAYOUT_VERSION")
        self.assertFalse(reader.calls)

    def test_21_too_many_hops_fails_preflight(self):
        from dataclasses import replace
        r,_=self.resolve(contract=replace(self.contract,hop_offsets=(1,)*(MAX_HOPS+1)))
        self.assertEqual(r.status,"UNATTESTED_OR_INVALID_TEST_LAYOUT_VERSION")

    def test_22_missing_reader_fail_closed(self):
        r=validate_test_owned_role_chain(self.contract,None)
        self.assertEqual(r.status,"TEST_MEMORY_READER_UNAVAILABLE")

    def test_23_throwing_reader_fail_closed(self):
        class Broken:
            def read_u64(self,_address):raise RuntimeError("NO ACCESS")
        r=validate_test_owned_role_chain(self.contract,Broken())
        self.assertEqual(r.status,"ROOT_TEST_MEMORY_READ_EXCEPTION")

    def test_24_malformed_reader_result(self):
        class Invalid:
            def read_u64(self,_address):return 12345
        r=validate_test_owned_role_chain(self.contract,Invalid())
        self.assertEqual(r.status,"ROOT_INVALID_READ_RESULT")

    def test_25_bad_qword_value_not_cast_or_accepted(self):
        data={**self.data,self.root:ReadQword("READ_QWORD",-1)}
        r,_=self.resolve(data)
        self.assertEqual(r.status,"ROOT_INVALID_QWORD_VALUE")

    def test_26_duplicate_chain_absolute_addr_not_guessed(self):
        txt=(ROOT/"src/train_role_chain_validation.py").read_text(encoding="utf8")
        for token in ("0x355B208","0x356ED08","0x6F4030",
                      "WriteProcessMemory","CreateRemoteThread","VirtualAllocEx"):
            self.assertNotIn(token,txt)

    def test_27_region_cover_full_qword_only(self):
        r=OwnedMemoryRange(0x1000,0x10)
        self.assertTrue(r.covers(0x1008))
        self.assertFalse(r.covers(0x1009))
        self.assertFalse(r.covers(0x0FFF))
        self.assertFalse(r.covers(0x1010))

    def test_28_regions_reject_overflow_and_zero(self):
        self.assertFalse(OwnedMemoryRange(0,20).covers(0))
        self.assertFalse(OwnedMemoryRange(MAX_64-1,100).covers(MAX_64-1))
        self.assertFalse(OwnedMemoryRange(1,7).covers(1))

    def test_29_self_reader_reject_bad_owned_ranges(self):
        for values in ((),(OwnedMemoryRange(0,64),),[OwnedMemoryRange(100,64)]):
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    SelfOwnedWin32QwordReader(values)

    def test_30_self_reader_rejects_outside_before_OS(self):
        reader=SelfOwnedWin32QwordReader((OwnedMemoryRange(0x1000,16),))
        self.assertEqual(reader.read_u64(0x2000).status,
                         "POINTER_OUTSIDE_TEST_OWNED_RANGES")

    def test_31_self_reader_not_authorized_to_target_PID(self):
        import inspect
        s=inspect.signature(SelfOwnedWin32QwordReader.__init__)
        self.assertNotIn("pid",s.parameters)
        txt=(ROOT/"src/train_role_chain_validation.py").read_text(encoding="utf8")
        self.assertIn("os.getpid()",txt)

    def test_32_conservation_of_no_game_output(self):
        obj=FixtureChainResult("TEST_ONLY_POINTER_CHAIN_AND_SESSION_ANCHOR_VALIDATED",
                               1,True)
        for k in ("role_data_verified_in_real_game","role_name_read",
                  "map_id_read","bag_site_10_read"):
            self.assertFalse(getattr(obj,k))

    def test_33_frozen_results_no_mutable_positive_flip(self):
        r,_=self.resolve()
        with self.assertRaises(FrozenInstanceError):
            r.role_data_verified_in_real_game=True

    def test_34_disallow_zero_hops(self):
        from dataclasses import replace
        r,_=self.resolve(contract=replace(self.contract,hop_offsets=()))
        self.assertEqual(r.status,"UNATTESTED_OR_INVALID_TEST_LAYOUT_VERSION")

    def test_35_bad_contract_type(self):
        self.assertEqual(
            validate_test_owned_role_chain(object(),FakeOwnedReader({})).status,
            "UNATTESTED_OR_INVALID_TEST_LAYOUT_VERSION")

    def test_36_no_auto_inventory_or_farm_actions(self):
        txt=(ROOT/"src/train_role_chain_validation.py").read_text(encoding="utf8")
        for x in ("RequestSellItem(", "Game.GetItemData(", "SendInput(",
                  "inject_into_pid(", "start_farm(", "VerifiedClaims(",
                  "receive_server_token("):
            self.assertNotIn(x,txt)

    def test_37_source_and_tests_ast_parse(self):
        for name in ("src/train_role_chain_validation.py","tests/test_s134.py"):
            p=ROOT/name
            ast.parse(p.read_text(encoding="utf8"))

if __name__ == "__main__":
    unittest.main()
