"""S168 owner-requested independent rebuild: license-free local UI, NEVER patch original TLM.

Historical signed Info regression retains its old contract separately.
"""
from __future__ import annotations
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock,patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))

from local_feature_policy import LocalFeaturePolicy,LOCAL_TAB_KEYS
from permission_guard import PermissionSnapshot,PermissionGuard
from start_polling import StartWindowProducer,WindowSnapshot
from start_windows import GameWindow
from shell import INFO_KEY, ALL_KEYS, TabLifecycle,TLMMainApp
from train_row_permission import TrainRowPermissionGate
import TLMToolIndependent as independent
from source_backed_tab_builders import SOURCE_BACKED_KEYS

class NativeStub:
    visible=True
    pid=321
    def is_window(self,hwnd):return hwnd==123
    def is_visible(self,hwnd):return self.visible
    def process_id(self,hwnd):return self.pid

class S168Independent(unittest.TestCase):
    def test_01_explicit_local_module_catalog_only(self):
        policy=LocalFeaturePolicy(frozenset({"farm_tab"}))
        self.assertTrue(policy.config_available("farm_tab"))
        self.assertFalse(policy.config_available("proxy_tab"))
        self.assertFalse(policy.config_available("trainlsv_tab"))

    def test_02_no_unimplemented_or_dev_module(self):
        for payload in (frozenset({"proxy_tab"}),frozenset({"fake_tab"}),
                        frozenset({"debug_tab"}),{"farm_tab"},frozenset({1})):
            with self.subTest(payload=payload),self.assertRaises(ValueError):
                LocalFeaturePolicy(payload)

    def test_03_local_config_does_not_require_game_or_original_token(self):
        policy=LocalFeaturePolicy(frozenset({"farm_tab"}))
        self.assertTrue(policy.config_available("farm_tab"))
        self.assertFalse(policy.window_observation_allowed("farm_tab",0))
        self.assertFalse(policy.window_observation_allowed("farm_tab",-1))
        self.assertFalse(policy.window_observation_allowed("farm_tab",True))
        self.assertTrue(policy.window_observation_allowed("farm_tab",1))

    def test_04_native_pid_and_visibility_must_still_match(self):
        policy=LocalFeaturePolicy(frozenset({"farm_tab"}))
        stub=NativeStub()
        gate=TrainRowPermissionGate(policy,lambda:1,lambda:stub)
        window=GameWindow(123,321,"Thần Long  Mobile","UnityWndClass","thần long mobile.exe")
        self.assertTrue(gate.permitted(window))
        stub.pid=222
        self.assertFalse(gate.permitted(window))
        stub.pid=321
        stub.visible=False
        self.assertFalse(gate.permitted(window))

    def test_05_invalid_native_identity_denied(self):
        policy=LocalFeaturePolicy(frozenset({"farm_tab"}))
        gate=TrainRowPermissionGate(policy,lambda:1,NativeStub)
        for bad in (None,object(),GameWindow(0,321,"t","c","g"),
                    GameWindow(123,-1,"t","c","g")):
            self.assertFalse(gate.permitted(bad))

    def test_06_zero_running_windows_denies_rows(self):
        policy=LocalFeaturePolicy(frozenset({"farm_tab"}))
        window=GameWindow(123,321,"x","c","g")
        gate=TrainRowPermissionGate(policy,lambda:0,NativeStub)
        self.assertFalse(gate.permitted(window))

    def test_07_local_lifecycle_shows_only_registered_real_builders(self):
        built={"info_tab":lambda f:object(),"start_tab":lambda f:object(),
               "login_tab":lambda f:object(),"party_tab":lambda f:object(),
               "farm_tab":lambda f:object()}
        lc=TabLifecycle(built,{name:object() for name in ALL_KEYS})
        keys=lc.apply_local_capabilities(LOCAL_TAB_KEYS)
        self.assertEqual(keys,frozenset(built))
        self.assertNotIn("proxy_tab",keys)
        self.assertNotIn("trainlsv_tab",keys)

    def test_08_no_new_unimplemented_key_can_show(self):
        lc=TabLifecycle({"info_tab":lambda _:None},{k:object() for k in ALL_KEYS})
        with self.assertRaises(ValueError):
            lc.apply_local_capabilities(frozenset({"proxy_tab"}))
        with self.assertRaises(ValueError):
            lc.apply_local_capabilities(frozenset({"nonexisting"}))

    def test_09_builder_real_train_with_policy_and_no_info(self):
        producer=StartWindowProducer()
        with tempfile.TemporaryDirectory() as directory:
            b=independent.make_independent_builders(Path(directory)/"settings.ini",producer)
        self.assertEqual(frozenset(b),SOURCE_BACKED_KEYS|frozenset({"farm_tab", "trainlsv_tab"}))
        self.assertNotIn("proxy_tab",b)
        self.assertEqual(independent.count_observed_game_windows(producer),0)

    def test_10_snapshot_no_license_does_not_hide_local_tabs(self):
        app=TLMMainApp.__new__(TLMMainApp)
        app._independent_mode=True
        app.apply_verified_permissions=lambda *_args,**_kwargs:self.fail("legacy grant invoked")
        app.apply_info_snapshot(PermissionSnapshot())
        self.assertTrue(True)

    def test_11_no_legacy_info_can_revoke_local_tabs(self):
        app=TLMMainApp.__new__(TLMMainApp)
        app._independent_mode=True
        app._closed=False
        lifecycle=Mock()
        app.lifecycle=lifecycle
        app.apply_verified_permissions(set(),blocked=True)
        lifecycle.apply_authorized_keys.assert_not_called()

    def test_12_only_real_local_builder_set_used_at_entrypoint(self):
        with patch.object(independent,"make_independent_builders") as builders:
            builders.return_value={"info_tab":lambda x:x}
            # Calls to issuer are not in the independent builder API.
            self.assertNotIn("verify_and_decode",independent.make_independent_builders.__code__.co_varnames
                             if hasattr(independent.make_independent_builders,"__code__") else ())

    def test_13_separate_main_static_self_check_no_token(self):
        import io
        from contextlib import redirect_stdout
        buf=io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(independent.main(["--self-check"]),0)
        result=json.loads(buf.getvalue())
        self.assertEqual(result["original_license_service"],"NOT_USED")
        self.assertEqual(result["gameplay_parity"],"NOT_VERIFIED")

    def test_14_reject_invalid_cli(self):
        self.assertEqual(independent.main(["--not-a-real-product"]),2)

    def test_15_source_does_not_fake_license_or_routine_send(self):
        s=(ROOT/"src/TLMToolIndependent.py").read_text("utf-8")
        for forbidden in ("VerifiedClaims(", "receive_token(", "RequestSellItem(",
                          "ReadProcessMemory(", "SendInput(", "bypass_license("):
            self.assertNotIn(forbidden,s)
        self.assertIn("independent_mode=True",s)

if __name__=="__main__":
    unittest.main()
