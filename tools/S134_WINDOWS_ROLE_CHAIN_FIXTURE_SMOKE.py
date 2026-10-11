"""S134 real Win64 QWORD chain through TEST-OWNED ctypes memory ONLY.

This test writes to its OWN temporary Python buffers, then genuinely reads
them using OpenProcess(SELF, READ|QUERY), VirtualQueryEx, ReadProcessMemory.
No target game PID/module, no original EXE run, no role/MapID/bag values.
O02 original structure semantics: root -> +(intermediate B8) -> object
before +(terminal 88), final pointer and independent Session RoleData anchor.
The numeric steps here are TEST FIXTURE SHAPE, not live game offsets.
"""
from __future__ import annotations
import ctypes
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s134"
OUT.mkdir(parents=True,exist_ok=True)


def run():
    q={"status":"NOT_RUN","real_game_attached":False,
       "real_game_RoleData_verified":False,
       "real_RoleName_read":False,"real_MapID_read":False,
       "real_Site10_bag_read":False,"auth_signed_info":False,
       "game_packet_or_memory_write":False,"proxy":"EXCLUDED"}
    buffers=()
    try:
        from train_role_chain_validation import (
            OwnedMemoryRange, ReadQword, FixtureChainContract,
            TEST_LAYOUT_VERSION, SelfOwnedWin32QwordReader,
            validate_test_owned_role_chain,
        )
        from train_memory_module_probe import READ_ONLY_RIGHTS
        if os.name!="nt" or ctypes.sizeof(ctypes.c_void_p)!=8:
            raise RuntimeError("REAL_WINDOWS_X64_REQUIRED")
        # All five buffers are ALLOCATED and owned by this Python script.
        root=ctypes.create_string_buffer(64)
        n1=ctypes.create_string_buffer(256)
        n2=ctypes.create_string_buffer(256)
        role=ctypes.create_string_buffer(64)
        session=ctypes.create_string_buffer(256)
        buffers=(root,n1,n2,role,session)
        addresses=tuple(ctypes.addressof(buffer) for buffer in buffers)
        root_addr,n1_addr,n2_addr,role_addr,session_addr=addresses
        ranges=tuple(OwnedMemoryRange(addr,len(buffer))
                     for addr,buffer in zip(addresses,buffers))

        def own_write(pointer,value):
            # Purely TEST-owned local ctypes buffers; no WinAPI write to
            # any external process, memory injection or game command.
            raw=ctypes.c_uint64(value)
            ctypes.memmove(pointer,ctypes.byref(raw),8)

        own_write(root_addr,n1_addr)
        own_write(n1_addr+0xB8,n2_addr)
        own_write(n2_addr+0x88,role_addr)
        own_write(session_addr+0x88,role_addr)
        contract=FixtureChainContract(
            TEST_LAYOUT_VERSION,root_addr,(0xB8,),0x88,
            session_addr+0x88,ranges)
        reader=SelfOwnedWin32QwordReader(ranges)
        first=reader.read_u64(root_addr)
        q["real_Windows_RPM_reads_self_owned_64bit_pointer"]=(
            first.status=="READ_QWORD" and first.value==n1_addr
            and READ_ONLY_RIGHTS==0x410)
        # S140: record the ACTUAL native RPM-address sequence during the
        # positive validation. An unrelated ctypes buffer may be allocated
        # at role_addr+0x88 on Windows. That does NOT imply our algorithm
        # dereferenced the role object twice, and it previously caused a
        # flaky false failure here. Assert the exact executed read sequence
        # instead of assuming a global allocator address gap.
        class TrackingReadOnlyReader:
            def __init__(self, wrapped):
                self.wrapped=wrapped
                self.calls=[]
            def read_u64(self, address):
                self.calls.append(address)
                return self.wrapped.read_u64(address)

        tracked=TrackingReadOnlyReader(reader)
        result=validate_test_owned_role_chain(contract,tracked)
        q["true_Win32_validates_fixture_chain_and_independent_anchor"]=(
            result.status=="TEST_ONLY_POINTER_CHAIN_AND_SESSION_ANCHOR_VALIDATED"
            and result.traversed_hops==1 and result.fixture_anchor_matches
            and not result.role_data_verified_in_real_game
            and not result.role_name_read
            and not result.map_id_read
            and not result.bag_site_10_read)
        q["O02_returns_object_before_last_offset"]=(
            reader.read_u64(n2_addr+0x88).value==role_addr
            and tracked.calls==[
                root_addr, n1_addr+0xB8, n2_addr+0x88, session_addr+0x88
            ])

        own_write(root_addr,0)
        empty=validate_test_owned_role_chain(contract,reader)
        q["real_null_root_is_error_not_empty_character"]=(
            empty.status=="NULL_ROOT_POINTER"
            and not empty.fixture_anchor_matches)
        own_write(root_addr,n1_addr)

        own_write(n1_addr+0xB8,0)
        broken=validate_test_owned_role_chain(contract,reader)
        q["real_broken_intermediate_pointer_is_error"]=(
            broken.status=="NULL_INTERMEDIATE_POINTER")
        own_write(n1_addr+0xB8,n2_addr)

        own_write(n2_addr+0x88,0)
        absent=validate_test_owned_role_chain(contract,reader)
        q["real_null_final_RoleData_field_not_success"]=(
            absent.status=="NULL_ROLE_FIELD_POINTER")
        own_write(n2_addr+0x88,role_addr)

        own_write(session_addr+0x88,n1_addr)
        mismatch=validate_test_owned_role_chain(contract,reader)
        q["real_session_RoleData_anchor_mismatch_refused"]=(
            mismatch.status=="SESSION_ROLE_ANCHOR_MISMATCH")
        own_write(session_addr+0x88,role_addr)

        own_write(n1_addr+0xB8,0x1000)
        out_of_range=validate_test_owned_role_chain(contract,reader)
        q["foreign_pointer_never_traversed"]=(
            out_of_range.status=="FINAL_OBJECT_OUTSIDE_TEST_MEMORY")
        own_write(n1_addr+0xB8,n2_addr)

        q["real_self_reader_refuses_address_outside_fixture"]=(
            reader.read_u64(0x1000).status=="POINTER_OUTSIDE_TEST_OWNED_RANGES"
            and reader.read_u64(root_addr+len(root)-4).status==
                "POINTER_OUTSIDE_TEST_OWNED_RANGES")
        fake=SelfOwnedWin32QwordReader((OwnedMemoryRange(0x1000,256),))
        q["native_VirtualQueryEx_unmapped_page_not_read"]=(
            fake.read_u64(0x1000).status in (
                "UNMAPPED_OR_UNKNOWN_REGION",
                "UNREADABLE_OR_UNCOMMITTED_REGION",
                "INCOMPLETE_MEMORY_READ"))
        from dataclasses import replace
        wrong=replace(contract,version="UNVERIFIED_GAME_BUILD")
        q["unattested_version_refused_before_RPM"]=(
            validate_test_owned_role_chain(wrong,reader).status==
                "UNATTESTED_OR_INVALID_TEST_LAYOUT_VERSION")
        q["restored_fixture_reads_still_valid"]=(
            validate_test_owned_role_chain(contract,reader).fixture_anchor_matches)

        checks={k:v for k,v in q.items()
                if type(v) is bool and k not in (
                    "real_game_attached","real_game_RoleData_verified",
                    "real_RoleName_read","real_MapID_read",
                    "real_Site10_bag_read","auth_signed_info",
                    "game_packet_or_memory_write")}
        if not all(checks.values()):
            raise RuntimeError("S134_FIXTURE_CHAIN_FAILED:"+
                               ",".join(k for k,v in checks.items() if not v))
        q["status"]="PASS_S134_NATIVE_READONLY_SELF_OWNED_ROLE_POINTER_FIXTURE"
    except Exception as exc:
        q["status"]="FAIL_S134_NATIVE"
        q["error_type"]=type(exc).__name__
        q["error_detail"]=str(exc)[:420]
    finally:
        # Hold source buffers alive until AFTER all RPM reads complete.
        _=buffers
        (OUT/"win64_owned_pointer_chain.json").write_text(
            json.dumps(q,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
        for name,value in q.items():
            print("S134_"+name.upper()+"="+json.dumps(value,ensure_ascii=True))
    return 0 if q["status"].startswith("PASS_S134_") else 1

if __name__=="__main__":
    raise SystemExit(run())
