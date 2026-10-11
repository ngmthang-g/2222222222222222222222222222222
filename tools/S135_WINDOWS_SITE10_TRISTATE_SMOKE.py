"""S135 native Win64 real self-owned RPM Site10 fixture, NOT GAME."""
from __future__ import annotations
import ctypes
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
OUT=ROOT/'artifacts'/'s135'
OUT.mkdir(parents=True,exist_ok=True)

def run():
    report={'status':'NOT_RUN','real_game_attached':False,
            'real_game_bag_site10_read':False,'auth_signed_info':False,
            'game_packet_or_memory_write':False,'proxy':'EXCLUDED'}
    buffers=[]
    try:
        from train_bag_tristate_fixture import (
            BAG_TEST_VERSION, TestBagLayout, inspect_test_owned_site10)
        from train_role_chain_validation import OwnedMemoryRange, SelfOwnedWin32QwordReader
        if os.name!='nt' or ctypes.sizeof(ctypes.c_void_p)!=8:
            raise RuntimeError('REAL_WINDOWS_X64_REQUIRED')
        slot=ctypes.create_string_buffer(64)
        dic=ctypes.create_string_buffer(64)
        entries=ctypes.create_string_buffer(128)
        buffers.extend((slot,dic,entries))
        s,d,e=[ctypes.addressof(b) for b in buffers]
        def put(addr,value):
            v=ctypes.c_uint64(value)
            ctypes.memmove(addr,ctypes.byref(v),8)
        put(s,d);put(d,2);put(d+8,e)
        for i,fields in enumerate(((101,201,10,3,5),(102,202,2,1,7))):
            for j,value in enumerate(fields):put(e+i*40+j*8,value)
        ranges=tuple(OwnedMemoryRange(ctypes.addressof(b),len(b)) for b in buffers)
        layout=TestBagLayout(BAG_TEST_VERSION,s,0,8,40,ranges)
        reader=SelfOwnedWin32QwordReader(ranges)
        baseline=inspect_test_owned_site10(layout,reader)
        report['true_win64_readonly_owned_dictionary_rows']=(
            baseline.status=='TEST_SITE10_ROWS_OBSERVED'
            and len(baseline.rows)==1 and baseline.rows[0].dbID==101
            and baseline.rows[0].itemID==201
            and baseline.observed_other_site_rows==1
            and not baseline.verified_game_bag)
        put(s,0)
        unattached=inspect_test_owned_site10(layout,reader)
        report['unloaded_items_not_empty']=(
            unattached.status=='ITEMS_NULL_UNLOADED' and unattached.rows is None)
        put(s,d);put(d,0)
        empty=inspect_test_owned_site10(layout,reader)
        report['real_zero_count_is_valid_empty']=(
            empty.status=='TEST_EMPTY_ITEMS_DICTIONARY' and empty.rows==())
        put(d,2);put(d+8,0)
        corrupt=inspect_test_owned_site10(layout,reader)
        report['missing_entries_never_becomes_empty']=(
            corrupt.status=='ENTRIES_NULL_WHILE_COUNT_NONZERO' and corrupt.rows is None)
        put(d+8,e)
        report['snapshot_restores']=(
            inspect_test_owned_site10(layout,reader).status=='TEST_SITE10_ROWS_OBSERVED')
        missing=inspect_test_owned_site10(layout,None)
        report['no_reader_is_detached_not_empty']=(
            missing.status=='READER_NOT_ATTACHED' and missing.rows is None)
        checks=[v for k,v in report.items() if k not in (
            'real_game_attached','real_game_bag_site10_read',
            'auth_signed_info','game_packet_or_memory_write') and type(v) is bool]
        if not all(checks):raise RuntimeError('S135_TEST_OWNED_NATIVE_TRISTATE_FAILED')
        report['status']='PASS_S135_TEST_OWNED_REAL_WINDOWS_RPM_BAG_TRISTATE'
    except Exception as e:
        report['status']='FAIL_S135_NATIVE'
        report['error_type']=type(e).__name__
        report['error_details']=str(e)[:400]
    finally:
        _=buffers
        (OUT/'site10_test_owned_windows.json').write_text(
            json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        print(json.dumps(report,ensure_ascii=False))
    if not report['status'].startswith('PASS_'):raise SystemExit(1)

if __name__=='__main__':run()
