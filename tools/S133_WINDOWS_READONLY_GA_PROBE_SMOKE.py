"""S133 native Windows x64 REAL READ-ONLY process memory attestation.

Uses only THIS test runner's OWN python.exe and Tk HWND/PID. The real
OpenProcess(PROCESS_VM_READ|QUERY_INFORMATION), EnumProcessModulesEx,
VirtualQueryEx, ReadProcessMemory MZ/PE proof is not a real game read.
Only synthetic TEST-OWNED PermissionGuard claims inside this CI script;
no issuer, no game pointers or authorizations are fabricated in source.
"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s133"
OUT.mkdir(parents=True,exist_ok=True)

def run():
    e={"status":"NOT_RUN","real_game":False,"original_roledata_read":False,
       "real_signed_info":False,"actual_item_packet_sent":False,"proxy":"EXCLUDED"}
    root=None
    try:
        if os.name!="nt":
            raise RuntimeError("TRUE_WINDOWS_REQUIRED")
        import tkinter as tk
        from train_memory_module_probe import (
            NativeReadOnlyModuleInspector, GuardedGameAssemblyProbe,
            READ_ONLY_RIGHTS, ModuleAttestation)
        from start_windows import GameWindow,NativeWin32Backend
        from start_polling import StartWindowProducer,WindowSnapshot
        from permission_guard import PermissionGuard,VerifiedClaims

        root=tk.Tk()
        root.geometry("460x250+0+0")
        root.update()
        backend=NativeWin32Backend()
        hwnd=int(root.winfo_id())
        pid=backend.process_id(hwnd)
        e["actual_test_owned_Win32_HWND_PID"]=(
            pid==os.getpid() and backend.is_window(hwnd)
            and backend.is_visible(hwnd))
        inspector=NativeReadOnlyModuleInspector()
        e["actual_x64_readonly_capabilities"]=(
            inspector.supported and READ_ONLY_RIGHTS==0x0410)
        # This reads the PE header from THIS Python process, not a game.
        module=Path(sys.executable).name
        own=inspector.inspect(os.getpid(),module)
        e["real_ReadProcessMemory_virtualqueryx_PE_header"]=(
            own.status=="PE_MODULE_VERIFIED_ONLY"
            and own.pe_header_verified
            and type(own.base) is int and own.base>0
            and type(own.image_size) is int and own.image_size>0
            and not own.original_role_data_verified
            and not own.game_memory_sample)
        e["real_unknown_GameAssembly_absent_in_python_process"]=(
            inspector.inspect(os.getpid(),"GameAssembly.dll").status==
                "MODULE_NOT_FOUND")
        e["invalid_pid_and_no_module_no_fake_success"]=(
            inspector.inspect(0,module).status=="INVALID_PID_OR_MODULE"
            and inspector.inspect(os.getpid(),"missing_dll_s133.bin").status==
                "MODULE_NOT_FOUND")
        guard=PermissionGuard()
        producer=StartWindowProducer()
        win=GameWindow(hwnd,pid,"Test-owned tkinter Windows", "TkTopLevel","TEST_NOT_GAME.exe")
        revision=[1]
        def snap():
            return WindowSnapshot(
                revision=revision[0],windows=(win,),valid=True)
        # Test-owned Start snapshot shim is used ONLY in CI.
        producer.read_snapshot=snap
        probe=GuardedGameAssemblyProbe(
            permission_guard=guard,running_count=lambda:1,
            start_producer=producer,backend=backend,inspector=inspector)
        e["no_auth_no_OpenProcess_regardless_of_window"]=(
            probe.inspect(win).status=="INFO_UNVERIFIED_OR_LIMIT")
        # The official public application still cannot create such a
        # genuine signed token. This test stub is not a server credential.
        guard.receive_token("CI_TEST_ONLY_NEVER_VALID_IN_PRODUCT", lambda _:
            VerifiedClaims(frozenset({"farm_tab"}),"active",2))
        valid=probe.inspect(win)
        e["test_permission_native_start_HWND_then_GameAssembly_missing"]=(
            valid.status=="MODULE_NOT_FOUND" and valid.pid==pid
            and not valid.pe_header_verified
            and not valid.original_role_data_verified)
        recycled=GameWindow(hwnd,pid+7777,"Fake stale PID","test","no.exe")
        e["reused_HWND_different_PID_cannot_read"]=(
            probe.inspect(recycled).status=="START_HWND_PID_NOT_ATTESTED")
        # Explicit external probe injected for controlled in-flight
        # revoke: no real game/native read in this case.
        class Revoker:
            def inspect(self,_pid,_module):
                guard.clear()
                return ModuleAttestation(
                    "PE_MODULE_VERIFIED_ONLY", _pid, _module, 4096,65536,True)
        probe.inspector=Revoker()
        e["auth_revoke_during_read_never_publishes_positive"]=(
            probe.inspect(win).status=="INFO_REVOKED_DURING_READ")
        guard.receive_token("CI_TEST_ONLY_NOT_SIGNED", lambda _:
            VerifiedClaims(frozenset({"farm_tab"}),"active",2))
        class Changer:
            def inspect(self,_pid,_module):
                revision[0]+=1
                return ModuleAttestation("MODULE_NOT_FOUND",_pid,_module)
        probe.inspector=Changer()
        e["Start_cache_revision_change_after_read_refused"]=(
            probe.inspect(win).status=="STALE_START_GENERATION")
        root.destroy()
        root=None
        flags={k:v for k,v in e.items()
               if type(v) is bool and k not in (
                   "real_game","original_roledata_read","real_signed_info",
                   "actual_item_packet_sent")}
        if not all(flags.values()):
            raise RuntimeError("S133_NATIVE_REAL_WIN32_FAILED:"+
                               ",".join(k for k,v in flags.items() if not v))
        e["status"]="PASS_S133_REAL_WINDOWS_READONLY_PE_MODULE_NO_GAME"
    except Exception as exc:
        e["status"]="FAIL_S133_NATIVE"
        e["error_type"]=type(exc).__name__
        e["error_detail"]=str(exc)[:440]
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        (OUT/"native_win32_readonly_probe.json").write_text(
            json.dumps(e,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
        for key,value in e.items():
            print("S133_"+key.upper()+"="+json.dumps(value,ensure_ascii=True))
    return 0 if e["status"].startswith("PASS_S133_") else 1

if __name__=="__main__":
    raise SystemExit(run())
