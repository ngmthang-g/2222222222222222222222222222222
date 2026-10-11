"""S157 F05 clean Windows child environment unit regressions.

Original binary proves minimal env + TLM_PROFILE, not full _SAFE_ENV_KEYS;
tests assert the documented contract and the stated conservative subset.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from login_safe_env import (
    make_safe_launch_env, WINDOWS_ESSENTIAL_CANDIDATES,
    PROFILE_ENV_KEY, BLOCKED_VARIABLE_PREFIXES,
)


class S157F05SafeChildEnv(unittest.TestCase):
    def test_01_core_original_windows_env_names_present(self):
        self.assertTrue({"SYSTEMROOT","COMSPEC","PATH","TEMP","TMP",
                         "WINDIR","APPDATA","USERPROFILE"}.issubset(
                             WINDOWS_ESSENTIAL_CANDIDATES))

    def test_02_original_profile_key_is_selected_by_invoker(self):
        self.assertEqual(PROFILE_ENV_KEY,"TLM_PROFILE")
        result=make_safe_launch_env("2",{"SYSTEMROOT":r"C:\Windows",
                                         "TLM_PROFILE":"UNTRUSTED_OLD"})
        self.assertEqual(result,{"SYSTEMROOT":r"C:\Windows","TLM_PROFILE":"2"})

    def test_03_profile_value_not_guessed_or_reformatted(self):
        for name in ("1","5","profile_03"," 4 ","Chế độ 2"):
            self.assertEqual(make_safe_launch_env(name,{})["TLM_PROFILE"],name)

    def test_04_unrelated_account_password_and_tlm_internals_not_in_child(self):
        incoming={"SYSTEMROOT":r"C:\Windows","CHATGPT_SESSION_SECRET":"DO_NOT_COPY",
                  "TEST_PASSWORD":"not-a-real-password",
                  "TLM_PROXY_HOST":"127.0.0.1","TLM_PROXY_PORT":"9999"}
        result=make_safe_launch_env("1",incoming)
        self.assertEqual(set(result),{"SYSTEMROOT","TLM_PROFILE"})
        self.assertNotIn("TEST_PASSWORD",result)

    def test_05_python_virtualenv_conda_pip_environment_stripped(self):
        incoming={"PATH":r"C:\Windows\System32","PYTHONPATH":r"Z:\bad",
                  "PYTHONHOME":r"Z:\python","VIRTUAL_ENV":r"Z:\venv",
                  "CONDA_PREFIX":r"Z:\conda","PIP_INDEX_URL":"secret",
                  "TLM_PROXY_ENABLE":"1"}
        self.assertEqual(make_safe_launch_env("3",incoming),
                         {"PATH":r"C:\Windows\System32","TLM_PROFILE":"3"})

    def test_06_windows_key_casing_retained_for_path(self):
        self.assertEqual(make_safe_launch_env("3",{"Path":"C:\\Windows","ComSpec":"cmd.exe"}),
                         {"Path":"C:\\Windows","ComSpec":"cmd.exe","TLM_PROFILE":"3"})

    def test_07_empty_source_produces_only_profile(self):
        self.assertEqual(make_safe_launch_env("5",{}),{"TLM_PROFILE":"5"})

    def test_08_mixed_case_duplicate_windows_key_denied(self):
        with self.assertRaisesRegex(ValueError,"F05_AMBIGUOUS"):
            make_safe_launch_env("1",{"PATH":"a","Path":"b"})

    def test_09_invalid_profiles_rejected_locally(self):
        for bad in (None,0,True,""," ","X\0Y","1\n2","1\r2","a=b","Z"*257):
            with self.subTest(bad=repr(bad)):
                with self.assertRaises(ValueError):
                    make_safe_launch_env(bad,{})

    def test_10_non_mapping_source_rejected(self):
        with self.assertRaises(TypeError):
            make_safe_launch_env("2",[("PATH","x")])

    def test_11_invalid_source_env_types_rejected(self):
        for invalid in ({7:"a"},{"PATH":0},{"A=B":"v"},{"A\0B":"v"},
                        {"PATH":"v\0w"}):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    make_safe_launch_env("2",invalid)

    def test_12_no_python_or_proxy_name_in_allowed_list(self):
        for key in WINDOWS_ESSENTIAL_CANDIDATES:
            self.assertEqual(key,key.upper())
            self.assertFalse(any(key.startswith(p) for p in BLOCKED_VARIABLE_PREFIXES))

    def test_13_no_invented_original_whitelist_parity_claim(self):
        src=(ROOT/"src/login_safe_env.py").read_text(encoding="utf-8")
        self.assertIn("original _SAFE_ENV_KEYS = UNKNOWN",src)
        self.assertIn("conservative documented subset",src)
        self.assertNotIn("_apply_proxy_hook_env(",src)

    def test_14_no_child_launch_injection_or_game_memory_action(self):
        src=(ROOT/"src/login_safe_env.py").read_text(encoding="utf-8")
        for dangerous in ("subprocess.Popen(","CreateRemoteThread(","NtResumeProcess(",
                          "WriteProcessMemory(","ReadProcessMemory(","os.system(",
                          "SetWindowsHookEx(","SendInput(","TLM_PROXY_HOST = "):
            self.assertNotIn(dangerous,src)

    def test_15_source_mapping_never_mutated(self):
        source={"Path":"C:\\Windows","TLM_PROFILE":"original","PYTHONPATH":"evil"}
        before=source.copy()
        got=make_safe_launch_env("5",source)
        self.assertEqual(source,before)
        self.assertEqual(got["TLM_PROFILE"],"5")

    def test_16_missing_os_essential_does_not_get_fake_value(self):
        got=make_safe_launch_env("4",{"TEST_FAKE_SYSTEMROOT":r"C:\Windows"})
        self.assertNotIn("SYSTEMROOT",got)
        self.assertEqual(got,{"TLM_PROFILE":"4"})


if __name__=="__main__":
    unittest.main()
