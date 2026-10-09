"""S28 F05/D06 safe environment and structural x64 file preflight only."""
from __future__ import annotations
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"tools"))
from login_launch_preflight import LaunchPreflight
from login_launch_inputs import (
    PAYLOAD_RELATIVE, build_audited_windows_env, inspect_x64_pe,
    prepare_launch_inputs,
)
from S28_TEST_PE_FIXTURE import write_test_pe

ENV={"SystemRoot":r"C:\\Windows","WINDIR":r"C:\\Windows",
     "PATH":r"C:\\Windows\\System32","TEMP":r"C:\\Temp",
     "PYTHONPATH":r"C:\\test_python_injection",
     "VIRTUAL_ENV":r"C:\\fakevenv","TLM_PROXY_ENABLE":"1",
     "NO_PROXY":"*"}
KEYS=("SystemRoot","WINDIR","PATH")


class S28Tests(unittest.TestCase):
    def paths(self, td):
        base=Path(td)
        game=write_test_pe(base/"game"/"Thần Long  Mobile.exe",dll=False)
        payload=write_test_pe(base/"tool"/"data"/"resources.dat",dll=True)
        return game,payload,base/"tool"

    def allowed(self,game):
        return LaunchPreflight(True,"PREFLIGHT_ONLY_NOT_LAUNCHED",game,0,1)

    def test_original_active_payload_exact(self):
        self.assertEqual(PAYLOAD_RELATIVE,Path("data")/"resources.dat")
        self.assertEqual(str(PAYLOAD_RELATIVE).replace("\\\\","/"),"data/resources.dat")

    def test_synthetic_x64_exe_and_dll_structurally_valid_only(self):
        with tempfile.TemporaryDirectory() as td:
            game,payload,_=self.paths(td)
            e=inspect_x64_pe(game,dll_required=False)
            p=inspect_x64_pe(payload,dll_required=True)
            self.assertTrue(e.valid and p.valid)
            self.assertFalse(e.dll)
            self.assertTrue(p.dll)
            self.assertEqual(e.reason,"STRUCTURAL_PE32_PLUS_AMD64_ONLY")

    def test_reject_file_missing_short_and_not_mz(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"bad.dat"
            self.assertEqual(inspect_x64_pe(p,dll_required=True).reason,"FILE_MISSING")
            p.write_bytes(b"abc")
            self.assertEqual(inspect_x64_pe(p,dll_required=True).reason,"DOS_HEADER_SHORT")
            write_test_pe(p,dll=True,malformed="bad_mz")
            self.assertEqual(inspect_x64_pe(p,dll_required=True).reason,"NOT_MZ")

    def test_reject_bad_pe_offset_or_signature(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"x"
            write_test_pe(p,dll=True,malformed="bad_offset")
            self.assertEqual(inspect_x64_pe(p,dll_required=True).reason,"INVALID_PE_OFFSET")
            write_test_pe(p,dll=True,malformed="bad_pe")
            self.assertEqual(inspect_x64_pe(p,dll_required=True).reason,"NOT_PE_SIGNATURE")

    def test_reject_x86_and_magic_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"x"
            write_test_pe(p,dll=True,machine=0x14c)
            self.assertEqual(inspect_x64_pe(p,dll_required=True).reason,"NOT_AMD64")
            write_test_pe(p,dll=True,optional_magic=0x10b)
            self.assertEqual(inspect_x64_pe(p,dll_required=True).reason,"NOT_PE32_PLUS")

    def test_reject_dll_used_as_game_exe_and_exe_as_payload(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"x"
            write_test_pe(p,dll=True)
            self.assertEqual(inspect_x64_pe(p,dll_required=False).reason,"PE_KIND_MISMATCH")
            write_test_pe(p,dll=False)
            self.assertEqual(inspect_x64_pe(p,dll_required=True).reason,"PE_KIND_MISMATCH")

    def test_reject_malformed_sections_and_image(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"x"
            for bad,expected in (
                ("no_section","INVALID_HEADER_SIZES"),
                ("raw_truncated","SECTION_RAW_TRUNCATED"),
                ("no_executable","NOT_EXECUTABLE_IMAGE"),
                ("bad_image_size","INVALID_IMAGE_SIZES"),
                ("truncated","INVALID_PE_OFFSET")):
                with self.subTest(bad=bad):
                    write_test_pe(p,dll=True,malformed=bad)
                    self.assertEqual(inspect_x64_pe(p,dll_required=True).reason,expected)

    def test_invalid_expected_kind(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"x"
            write_test_pe(p,dll=False)
            self.assertEqual(inspect_x64_pe(p,dll_required=1).reason,"INVALID_EXPECTED_KIND")

    def test_exact_environment_only_approved_essentials_plus_profile(self):
        env=build_audited_windows_env(profile_index=3,
                                      source_env=ENV,essential_keys=KEYS)
        self.assertEqual(env,{"SystemRoot":ENV["SystemRoot"],
                              "WINDIR":ENV["WINDIR"],"PATH":ENV["PATH"],
                              "TLM_PROFILE":"3"})
        for key in ("PYTHONPATH","VIRTUAL_ENV","TLM_PROXY_ENABLE","NO_PROXY"):
            self.assertNotIn(key,env)

    def test_wrong_profile_zero_boolean_outside_one_to_five(self):
        for index in (0,6,True,"1",None):
            with self.subTest(index=index),self.assertRaises(ValueError):
                build_audited_windows_env(profile_index=index,
                                          source_env=ENV,essential_keys=KEYS)

    def test_no_guessed_default_essentials(self):
        for keys in ([],(),None,("PATH",)):
            with self.subTest(keys=keys),self.assertRaises(ValueError):
                build_audited_windows_env(profile_index=1,source_env=ENV,
                                          essential_keys=keys)

    def test_no_python_or_proxy_even_if_explicitly_allowed(self):
        for key in ("PYTHONPATH","VIRTUAL_ENV","TLM_PROXY_ENABLE","NO_PROXY"):
            with self.subTest(key=key),self.assertRaises(ValueError):
                build_audited_windows_env(profile_index=1,source_env=ENV,
                                          essential_keys=("SystemRoot",key))

    def test_casefold_environment_keys_and_missing_required(self):
        env=build_audited_windows_env(profile_index=1,
                source_env={"systemroot":"X","winDir":"Y"},
                essential_keys=("SYSTEMROOT","WINDIR"))
        self.assertEqual(env,{"systemroot":"X","winDir":"Y","TLM_PROFILE":"1"})
        with self.assertRaises(ValueError):
            build_audited_windows_env(profile_index=1,source_env=ENV,
                                      essential_keys=("SystemRoot","DoesNotExist"))

    def test_duplicate_reserved_case_collision_rejected(self):
        for keys in (("SystemRoot","SYSTEMROOT"),("SystemRoot","TLM_PROFILE")):
            with self.assertRaises(ValueError):
                build_audited_windows_env(profile_index=1,source_env=ENV,
                                          essential_keys=keys)
        with self.assertRaises(ValueError):
            build_audited_windows_env(profile_index=1,source_env={
                "SystemRoot":"X","systemroot":"Y"},essential_keys=("SystemRoot",))

    def test_reject_invalid_environment_key_or_value(self):
        for bad in ({**ENV,"X=Y":"Z"},{**ENV,"Bad":"\0"},
                    {**ENV,"A":42}):
            with self.assertRaises(ValueError):
                build_audited_windows_env(profile_index=1,source_env=bad,
                                          essential_keys=KEYS)

    def test_denied_preflight_leaves_files_and_environment_untouched(self):
        with tempfile.TemporaryDirectory() as td:
            game,payload,root=self.paths(td)
            bad=LaunchPreflight(False,"UNVERIFIED_INFO",game,0,1)
            result=prepare_launch_inputs(bad,package_root=root,profile_index=1,
                    source_env=ENV,essential_keys=KEYS)
            self.assertFalse(result.prepared)
            self.assertEqual(result.reason,"LAUNCH_PREFLIGHT_DENIED")
            self.assertIsNone(result.payload)
            self.assertIsNone(result.environment)

    def test_success_is_structural_only(self):
        with tempfile.TemporaryDirectory() as td:
            game,payload,root=self.paths(td)
            result=prepare_launch_inputs(self.allowed(game),package_root=root,
                profile_index=5,source_env=ENV,essential_keys=KEYS)
            self.assertTrue(result.prepared)
            self.assertEqual(result.reason,"STRUCTURAL_INPUTS_ONLY_NOT_LAUNCHED")
            self.assertEqual((result.executable,result.payload),(game,payload))
            self.assertEqual(result.environment["TLM_PROFILE"],"5")
            self.assertTrue(result.game_pe.valid and result.payload_pe.valid)

    def test_missing_payload_and_missing_package_root(self):
        with tempfile.TemporaryDirectory() as td:
            game,payload,root=self.paths(td)
            payload.unlink()
            self.assertEqual(prepare_launch_inputs(self.allowed(game),
                package_root=root,profile_index=1,source_env=ENV,
                essential_keys=KEYS).reason,"PAYLOAD_FILE_MISSING")
            self.assertEqual(prepare_launch_inputs(self.allowed(game),
                package_root=Path(td)/"doesnotexist",profile_index=1,
                source_env=ENV,essential_keys=KEYS).reason,"PACKAGE_ROOT_MISSING")

    def test_missing_exe_or_wrong_game_architecture(self):
        with tempfile.TemporaryDirectory() as td:
            game,payload,root=self.paths(td)
            write_test_pe(game,dll=False,machine=0x14c)
            result=prepare_launch_inputs(self.allowed(game),package_root=root,
                profile_index=1,source_env=ENV,essential_keys=KEYS)
            self.assertEqual(result.reason,"GAME_NOT_AMD64")
            game.unlink()
            self.assertEqual(prepare_launch_inputs(self.allowed(game),
                package_root=root,profile_index=1,source_env=ENV,
                essential_keys=KEYS).reason,"GAME_FILE_MISSING")

    def test_bogus_environment_blocks_even_valid_files(self):
        with tempfile.TemporaryDirectory() as td:
            game,payload,root=self.paths(td)
            result=prepare_launch_inputs(self.allowed(game),package_root=root,
                profile_index=1,source_env=ENV,essential_keys=("SystemRoot","PYTHONPATH"))
            self.assertEqual(result.reason,"ESSENTIAL_ENVIRONMENT_UNVERIFIED")
            self.assertIsNone(result.environment)

    def test_bak_dll_does_not_substitute_active_resources(self):
        with tempfile.TemporaryDirectory() as td:
            game,payload,root=self.paths(td)
            payload.rename(root/"data"/"resources.dat.bak-20260923")
            r=prepare_launch_inputs(self.allowed(game),package_root=root,
                profile_index=1,source_env=ENV,essential_keys=KEYS)
            self.assertEqual(r.reason,"PAYLOAD_FILE_MISSING")

    def test_structurally_invalid_mz_opaque_dat_not_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            game,payload,root=self.paths(td)
            payload.write_bytes(b"MZ"+b"\xff"*512)
            r=prepare_launch_inputs(self.allowed(game),package_root=root,
                profile_index=1,source_env=ENV,essential_keys=KEYS)
            self.assertFalse(r.prepared)
            self.assertTrue(r.reason.startswith("PAYLOAD_"))


if __name__=="__main__":
    unittest.main()
