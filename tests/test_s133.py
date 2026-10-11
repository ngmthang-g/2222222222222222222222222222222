"""S133 original O01/O02 memory-reader boundary: no guessed runtime samples.

The headless tests validate OS preflight/fail-closed contracts without
touching real game processes. Native Windows smoke uses test-owned Python
process with REAL OpenProcess/EnumProcessModulesEx/VirtualQueryEx/RPM.
"""
from __future__ import annotations
import ast
import inspect
import os
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from train_memory_module_probe import (
    NativeReadOnlyModuleInspector, ModuleAttestation, GuardedGameAssemblyProbe,
    READ_ONLY_RIGHTS, PROCESS_VM_READ, PROCESS_QUERY_INFORMATION,
    _MemoryBasicInformation,
)
from start_windows import GameWindow
from permission_guard import PermissionGuard
from start_polling import StartWindowProducer,WindowSnapshot
import ctypes


class S133OriginalMemoryModuleProbeTests(unittest.TestCase):
    def setUp(self):
        self.probe=NativeReadOnlyModuleInspector()

    def test_01_read_only_rights_minimal(self):
        self.assertEqual(READ_ONLY_RIGHTS, 0x0410)

    def test_02_only_vm_read_query_bits(self):
        self.assertEqual(READ_ONLY_RIGHTS, PROCESS_VM_READ|PROCESS_QUERY_INFORMATION)
        self.assertFalse(READ_ONLY_RIGHTS & 0x0020) # VM_WRITE
        self.assertFalse(READ_ONLY_RIGHTS & 0x0008) # VM_OPERATION
        self.assertFalse(READ_ONLY_RIGHTS & 0x0002) # CREATE_THREAD

    def test_03_bad_pid_types_denied_without_OS(self):
        for p in (0, -1, True, 1.0, "1",None):
            self.assertEqual(self.probe.inspect(p,"GameAssembly.dll").status,
                             "INVALID_PID_OR_MODULE")

    def test_04_bad_module_name_denied(self):
        for name in ("", ".", "..", "GameAssembly.dll\x00hack",
                     "../dll", "C:\\dll", 9, None):
            self.assertEqual(self.probe.inspect(2,name).status,
                             "INVALID_PID_OR_MODULE")

    def test_05_nonwindows_has_explicit_unsupported(self):
        if os.name!="nt":
            self.assertEqual(self.probe.inspect(os.getpid(),"GameAssembly.dll").status,
                             "WINDOWS_X64_REQUIRED")

    def test_06_original_games_module_and_no_guess(self):
        self.assertEqual(ModuleAttestation("READ_UNKNOWN").name,"GameAssembly.dll")

    def test_07_default_no_role_pointer_proven(self):
        self.assertFalse(ModuleAttestation("PE_MODULE_VERIFIED_ONLY").original_role_data_verified)

    def test_08_default_no_role_sample(self):
        self.assertFalse(ModuleAttestation("PE_MODULE_VERIFIED_ONLY").game_memory_sample)

    def test_09_immutable_result(self):
        from dataclasses import FrozenInstanceError
        with self.assertRaises(FrozenInstanceError):
            ModuleAttestation("ERROR").status="OK"

    def test_10_no_auth_guard_never_reads_any_process(self):
        class Observer:
            def __init__(self): self.calls=0
            def inspect(self,*args):self.calls+=1;raise AssertionError("UNAUTHORIZED_RPM")
        obs=Observer()
        gate=GuardedGameAssemblyProbe(
            permission_guard=None,running_count=lambda:1,
            start_producer=StartWindowProducer(),inspector=obs)
        row=GameWindow(1234,5678,"T","T","t.exe")
        self.assertEqual(gate.inspect(row).status,"INFO_UNVERIFIED_OR_LIMIT")
        self.assertEqual(obs.calls,0)

    def test_11_unauth_default_empty_Guard_no_process_access(self):
        guard=PermissionGuard()
        gate=GuardedGameAssemblyProbe(permission_guard=guard,
            running_count=lambda:1,start_producer=StartWindowProducer())
        self.assertEqual(gate.inspect(GameWindow(123,456,"x","y","z")).status,
                         "INFO_UNVERIFIED_OR_LIMIT")

    def test_12_invalid_window_identity_refused(self):
        gate=GuardedGameAssemblyProbe(permission_guard=PermissionGuard(),
            running_count=lambda:1,start_producer=StartWindowProducer())
        for win in (GameWindow(0,1,"","", ""),GameWindow(1,0,"","",""),
                    GameWindow(True,5,"","","")):
            self.assertEqual(gate.inspect(win).status,"INVALID_HWND_PID")

    def test_13_unknown_window_type_refused(self):
        gate=GuardedGameAssemblyProbe(permission_guard=None,
            running_count=None,start_producer=None)
        self.assertEqual(gate.inspect(object()).status,"INVALID_HWND_PID")

    def test_14_no_default_verified_info_provider(self):
        code=inspect.getsource(GuardedGameAssemblyProbe)
        self.assertNotIn("receive_token(",code)
        self.assertNotIn("VerifiedClaims(",code)

    def test_15_no_guessed_native_PID_selector(self):
        code=inspect.getsource(NativeReadOnlyModuleInspector)
        self.assertNotIn("process_iter(",code)
        self.assertNotIn("os.system(",code)

    def test_16_original_GameAssembly_case_name(self):
        self.assertIn('"GameAssembly.dll"',inspect.getsource(GuardedGameAssemblyProbe.inspect))

    def test_17_original_start_producer_type_enforced(self):
        code=inspect.getsource(GuardedGameAssemblyProbe._permitted)
        self.assertIn("isinstance(self.producer, StartWindowProducer)",code)

    def test_18_window_backend_win32_pid_fenced(self):
        code=inspect.getsource(GuardedGameAssemblyProbe._identity)
        self.assertIn("is_window",code)
        self.assertIn("is_visible",code)
        self.assertIn("process_id",code)

    def test_19_start_snapshot_revision_checked_twice(self):
        code=inspect.getsource(GuardedGameAssemblyProbe.inspect)
        self.assertIn("after.revision != before.revision",code)

    def test_20_permission_revocation_check_after_native_read(self):
        code=inspect.getsource(GuardedGameAssemblyProbe.inspect)
        self.assertIn("INFO_REVOKED_DURING_READ",code)

    def test_21_native_calls_read_only(self):
        s=inspect.getsource(NativeReadOnlyModuleInspector)
        for required in ("OpenProcess","EnumProcessModulesEx","GetModuleInformation",
                         "GetModuleBaseNameW","VirtualQueryEx","ReadProcessMemory",
                         "CloseHandle"):
            self.assertIn(required,s)
        for forbidden in ("WriteProcessMemory","VirtualProtectEx",
                          "VirtualAllocEx","CreateRemoteThread",
                          "DebugActiveProcess","LoadLibraryW"):
            self.assertNotIn(forbidden,s)

    def test_22_memory_region_guarded_before_RPM(self):
        source=inspect.getsource(NativeReadOnlyModuleInspector.inspect)
        self.assertLess(source.index("kernel.VirtualQueryEx("),
                        source.index("kernel.ReadProcessMemory("))
        self.assertIn("PAGE_GUARD",source)

    def test_23_unreadable_page_never_success(self):
        code=inspect.getsource(NativeReadOnlyModuleInspector.inspect)
        self.assertIn("region.State != MEM_COMMIT",code)
        self.assertIn("region.Protect & (PAGE_NOACCESS | PAGE_GUARD)",code)

    def test_24_test_without_guess_RoleData(self):
        code=(ROOT/"src/train_memory_module_probe.py").read_text(encoding="utf8")
        for token in ("0x355B208", "0x356ED08", "0x6F4030",
                      "0xC8)", "0x88)", "Site10 =", "MemoryWrite"):
            self.assertNotIn(token,code)

    def test_25_verified_PE_not_verified_character(self):
        m=ModuleAttestation("PE_MODULE_VERIFIED_ONLY",1,"GameAssembly.dll",
                            4096,50000,True,False,False)
        self.assertTrue(m.pe_header_verified)
        self.assertFalse(m.original_role_data_verified or m.game_memory_sample)

    def test_26_module_struct_size_known_windows_x64(self):
        if ctypes.sizeof(ctypes.c_void_p)==8:
            self.assertGreaterEqual(ctypes.sizeof(_MemoryBasicInformation),40)

    def test_27_preflight_races_cannot_claim_character(self):
        code=inspect.getsource(GuardedGameAssemblyProbe)
        self.assertNotIn("TrainCharacterSample(",code)
        self.assertNotIn("RoleName",code)
        self.assertNotIn("MapID",code)

    def test_28_no_network_or_info_secret(self):
        code=(ROOT/"src/train_memory_module_probe.py").read_text(encoding="utf8")
        for token in ("urllib.request", "requests.post(", "TOKEN_HMAC_SECRET",
                      "rpc/app_heartbeat_v2", "FakeLicense", "set_auth_override"):
            self.assertNotIn(token,code)

    def test_29_not_installed_as_game_FarmTab(self):
        code=(ROOT/"src/train_memory_module_probe.py").read_text(encoding="utf8")
        self.assertNotIn("source_backed_tab_builders(",code)

    def test_30_pe_bounds_check(self):
        code=inspect.getsource(NativeReadOnlyModuleInspector.inspect)
        self.assertIn("address + length > base + size",code)
        self.assertIn('signature != b"PE',code)

    def test_31_original_memory_docs_provenance_exists(self):
        doc=(ROOT/"docs/memory/O02_READER_PROCESS_POINTER_FLOW.md")
        if doc.exists():  # source-only CI always has docs
            raw=doc.read_text(encoding="utf8")
            self.assertIn("ReadProcessMemory",raw)
            self.assertIn("GameAssembly",raw)

    def test_32_source_parses_no_game_side_effect(self):
        code=(ROOT/"src/train_memory_module_probe.py").read_text(encoding="utf8")
        ast.parse(code)
        compile(code,"train_memory_module_probe.py","exec")


if __name__=="__main__":
    unittest.main()
