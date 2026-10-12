"""S165 real H01 Train Tk composition lazy builder; S164 external blockers deferred.

Tests never manufacture a production Info license. Real Windows native
S165 smoke (separate) covers physically constructed Tk widgets.
"""
from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))

import source_backed_tab_builders as factory
from permission_guard import PermissionGuard
from shell import ALL_KEYS, INFO_KEY, MissingFeatureError, TabLifecycle


class S165TrainBuilder(unittest.TestCase):
    def test_01_existing_default_builders_do_not_change(self):
        b=factory.source_backed_tab_builders(lambda frame: "TEST_ONLY_INFO")
        self.assertEqual(frozenset(b),factory.SOURCE_BACKED_KEYS)
        self.assertNotIn("farm_tab",b)

    def test_02_no_train_when_only_info_no_producer(self):
        g=PermissionGuard()
        with self.assertRaises(ValueError):
            factory.source_backed_tab_builders(
                lambda _:None,train_permission_guard=g)
        with self.assertRaises(ValueError):
            factory.source_backed_tab_builders(
                lambda _:None,train_running_count=lambda:1)

    def test_03_reject_invalid_guard_or_missing_settings(self):
        for guard in (object(),True,"TEST"):
            with self.subTest(guard=guard),self.assertRaises(ValueError):
                factory.source_backed_tab_builders(
                    lambda _:None,settings_file="test.ini",
                    train_permission_guard=guard,train_running_count=lambda:1)
        with self.assertRaises(ValueError):
            factory.source_backed_tab_builders(
                lambda _:None,train_permission_guard=PermissionGuard(),
                train_running_count=lambda:1)

    def test_04_reject_invalid_count_and_identity_provider(self):
        for count in (None,1,"1"):
            with self.subTest(count=count),self.assertRaises(ValueError):
                factory.source_backed_tab_builders(
                    lambda _:None,settings_file="test.ini",
                    train_permission_guard=PermissionGuard(),
                    train_running_count=count)
        with self.assertRaises(ValueError):
            factory.source_backed_tab_builders(
                lambda _:None,settings_file="test.ini",
                train_permission_guard=PermissionGuard(),
                train_running_count=lambda:1,
                train_allow_account=True)

    def test_05_no_early_train_creation(self):
        g=PermissionGuard()
        with patch.object(factory,"TkTrainComposition") as ui:
            b=factory.source_backed_tab_builders(
                lambda _:None,settings_file="test.ini",
                train_permission_guard=g,train_running_count=lambda:1)
            self.assertIn("farm_tab",b)
            ui.assert_not_called()

    def test_06_real_composition_constructed_only_on_explicit_use(self):
        g=PermissionGuard()
        count=lambda:1
        allowed=lambda w:False
        with tempfile.TemporaryDirectory() as d:
            settings=Path(d)/"settings.ini"
            with patch.object(factory,"TkTrainComposition") as ui:
                b=factory.source_backed_tab_builders(
                    lambda _:None,settings_file=settings,
                    train_permission_guard=g,train_running_count=count,
                    train_allow_account=allowed)
                pane=object()
                self.assertIs(b["farm_tab"](pane),ui.return_value)
                ui.assert_called_once_with(
                    pane,settings_file=settings,
                    permission_guard=g,running_count=count,
                    window_producer=None,allow_account=allowed,
                    identity_backend_factory=None)
                ui.return_value.pack.assert_called_once_with(
                    fill="both",expand=True)

    def test_07_missing_server_grant_never_instantiates_train(self):
        g=PermissionGuard()
        with patch.object(factory,"TkTrainComposition") as ui:
            b=factory.source_backed_tab_builders(
                lambda _:None,settings_file="test.ini",
                train_permission_guard=g,train_running_count=lambda:1)
            lifecycle=TabLifecycle(b,{name:object() for name in ALL_KEYS})
            self.assertEqual(
                lifecycle.apply_authorized_keys(set()),
                frozenset({INFO_KEY}))
            with self.assertRaises(MissingFeatureError):
                lifecycle.ensure_built("farm_tab")
            ui.assert_not_called()

    def test_08_blocked_info_revocation_denies_train(self):
        g=PermissionGuard()
        b=factory.source_backed_tab_builders(
            lambda _:None,settings_file="test.ini",
            train_permission_guard=g,train_running_count=lambda:1)
        lifecycle=TabLifecycle(b,{name:object() for name in ALL_KEYS})
        self.assertEqual(lifecycle.apply_authorized_keys(
            {"farm_tab"},blocked=True),frozenset({INFO_KEY}))

    def test_09_preserves_signed_info_product_gate(self):
        source=(ROOT/"src/TLMTool.py").read_text("utf-8")
        self.assertIn("return 2",source)
        self.assertIn("genuine InfoTab/server authorization",source)

    def test_10_no_faked_farm_run_or_network(self):
        src=(ROOT/"src/source_backed_tab_builders.py").read_text("utf-8")
        for disallowed in ("VerifiedClaims(", "receive_token(",
                           "CreateProcess(", "click_at(", "send_packet(",
                           "ProxyTab(", "command=self._toggle_farm"):
            self.assertNotIn(disallowed,src)
        self.assertIn('"farm_tab": build_train',src)


if __name__=="__main__":
    unittest.main()
