"""S140 regression of real S134 flaky TEST-owned allocator-address assumption.

The original S134 smoke used to read role_addr+0x88 and ASSERT that no
unrelated, test-owned buffer happened to cover it. On real Windows heap
layouts this is false intermittently. The original pointer algorithm must
instead read EXACTLY root, intermediate, terminal, independent anchor.
"""
from __future__ import annotations
import ast
from pathlib import Path
import sys
import unittest
from dataclasses import FrozenInstanceError

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from train_role_chain_validation import (
    OwnedMemoryRange, FixtureChainContract, TEST_LAYOUT_VERSION,
    ReadQword, validate_test_owned_role_chain,
)


class AddressTraceReader:
    def __init__(self,data):
        self.data=data
        self.calls=[]
    def read_u64(self,address):
        self.calls.append(address)
        return ReadQword("READ_QWORD",self.data.get(address,0))


class S140NativeFixtureTraceTests(unittest.TestCase):
    def setUp(self):
        self.root=0x1000
        self.n1=0x2000
        self.n2=0x3000
        self.role=0x4000
        self.sess=0x5000
        self.adjacent=0x4080
        self.ranges=tuple(OwnedMemoryRange(a,n) for a,n in (
            (self.root,64),(self.n1,256),(self.n2,256),
            (self.role,64),(self.sess,256),(self.adjacent,256)
        ))
        self.contract=FixtureChainContract(
            TEST_LAYOUT_VERSION,self.root,(0xB8,),0x88,
            self.sess+0x88,self.ranges)
        self.data={
            self.root:self.n1,
            self.n1+0xB8:self.n2,
            self.n2+0x88:self.role,
            self.sess+0x88:self.role,
            self.role+0x88:0x1234,  # Test-owned neighbor, not RoleData!
        }
    def run_fixture(self):
        reader=AddressTraceReader(self.data)
        result=validate_test_owned_role_chain(self.contract,reader)
        return result,reader

    def test_01_adjacent_role_plus_offset_is_allocated_without_game(self):
        self.assertTrue(self.ranges[-1].covers(self.role+0x88))
    def test_02_old_allocator_gap_assumption_would_have_failed(self):
        self.assertTrue(any(r.covers(self.role+0x88) for r in self.ranges))
        self.assertNotEqual(self.data[self.role+0x88],self.role)
    def test_03_exact_original_intermediate_terminal_anchor_trace(self):
        r,reader=self.run_fixture()
        self.assertEqual(r.status,"TEST_ONLY_POINTER_CHAIN_AND_SESSION_ANCHOR_VALIDATED")
        self.assertEqual(reader.calls,[
            self.root,self.n1+0xB8,self.n2+0x88,self.sess+0x88])
    def test_04_never_reads_doubly_offset_role_even_if_allocated(self):
        _,reader=self.run_fixture()
        self.assertNotIn(self.role+0x88,reader.calls)
        self.assertEqual(reader.calls.count(self.n2+0x88),1)
    def test_05_unchanged_behavior_fences_outside_owned_ranges(self):
        self.data[self.n1+0xB8]=0x9999
        r,reader=self.run_fixture()
        self.assertEqual(r.status,"FINAL_OBJECT_OUTSIDE_TEST_MEMORY")
        self.assertEqual(reader.calls,[self.root,self.n1+0xB8])
    def test_06_no_real_game_success_flags(self):
        r,_=self.run_fixture()
        self.assertFalse(r.role_data_verified_in_real_game)
        self.assertFalse(r.role_name_read)
        self.assertFalse(r.map_id_read)
        self.assertFalse(r.bag_site_10_read)
    def test_07_actual_smoke_tests_observed_addresses_not_gap(self):
        text=(ROOT/"tools/S134_WINDOWS_ROLE_CHAIN_FIXTURE_SMOKE.py").read_text(encoding="utf8")
        self.assertIn("tracked.calls==[",text)
        self.assertIn("root_addr, n1_addr+0xB8, n2_addr+0x88, session_addr+0x88",text)
        self.assertNotIn('reader.read_u64(role_addr+0x88).status==',text)
    def test_08_no_production_memory_or_auth_modification(self):
        p=ROOT/"tools/S140_REPEAT_S134_NATIVE.py"
        contents=p.read_text(encoding="utf8")
        for banned in ("WriteProcessMemory(", "CreateRemoteThread(", "GameAssembly.dll",
                       "SendInput(", "VerifiedClaims(", "source_env("):
            self.assertNotIn(banned,contents)
    def test_09_repeated_process_count_bounded(self):
        from pathlib import Path
        script=(ROOT/"tools/S140_REPEAT_S134_NATIVE.py").read_text(encoding="utf8")
        self.assertIn("RUNS=12",script)
        self.assertIn("timeout=40",script)
    def test_10_python_ast_all_new_test_tools(self):
        for p in ("tests/test_s140.py", "tools/S140_REPEAT_S134_NATIVE.py",
                  "tools/S134_WINDOWS_ROLE_CHAIN_FIXTURE_SMOKE.py"):
            ast.parse((ROOT/p).read_text(encoding="utf8"))
if __name__=="__main__":
    unittest.main()
