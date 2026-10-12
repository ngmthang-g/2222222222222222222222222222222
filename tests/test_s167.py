"""S167: real E03 Info heartbeat updates an already built Train permission owner.

All positive snapshots are isolated test fixtures; production still has
no signed Info issuer and refuses to launch the finished tool.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest
from unittest.mock import Mock
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))

from permission_guard import PermissionSnapshot
from shell import TLMMainApp


def snapshot(*, allowed=True, blocked=False):
    return PermissionSnapshot(
        has_verified_payload=allowed,
        permissions=frozenset({"farm_tab"}) if allowed else frozenset(),
        plan_status="active",
        max_windows=2,
        server_locked=blocked,
    )


def app_fixture(train=None, *, selected="farm_tab"):
    obj=TLMMainApp.__new__(TLMMainApp)
    root=Mock()
    root.after.side_effect=lambda _delay,cb: cb()
    obj.root=root
    obj._closed=False
    obj._verified_max_windows=0
    obj.apply_verified_permissions=Mock()
    obj.lifecycle=Mock()
    obj.lifecycle._instances=({"farm_tab":train} if train is not None else {})
    obj.lifecycle.current=selected
    return obj


def fake_train(permitted=True, *, active=False):
    panel=Mock()
    panel.reapply_permissions.return_value=permitted
    panel._readonly_refresh_requested=active
    return panel


class S167InfoToTrain(unittest.TestCase):
    def test_01_no_train_built_no_constructor_or_side_effect(self):
        app=app_fixture(None)
        app.apply_info_snapshot(snapshot())
        app.apply_verified_permissions.assert_called_once()
        self.assertEqual(app.lifecycle._instances,{})
        self.assertEqual(app.root.after.call_args.args[0],0)

    def test_02_constructed_train_rechecks_when_info_authorized(self):
        train=fake_train()
        app=app_fixture(train)
        app.apply_info_snapshot(snapshot())
        train.reapply_permissions.assert_called_once()
        train._start_refresh.assert_called_once()

    def test_03_train_denied_by_own_guard_never_resumes(self):
        train=fake_train(permitted=False)
        app=app_fixture(train)
        app.apply_info_snapshot(snapshot())
        train.reapply_permissions.assert_called_once()
        train._start_refresh.assert_not_called()

    def test_04_unverified_info_never_resumes_train(self):
        train=fake_train()
        app=app_fixture(train)
        app.apply_info_snapshot(PermissionSnapshot())
        train.reapply_permissions.assert_called_once()
        train._start_refresh.assert_not_called()

    def test_05_server_block_even_with_claims_never_resumes(self):
        train=fake_train()
        app=app_fixture(train)
        app.apply_info_snapshot(snapshot(blocked=True))
        train._start_refresh.assert_not_called()

    def test_06_when_info_page_selected_cannot_restart_hidden_train(self):
        train=fake_train()
        app=app_fixture(train,selected="info_tab")
        app.apply_info_snapshot(snapshot())
        train.reapply_permissions.assert_called_once()
        train._start_refresh.assert_not_called()

    def test_07_when_train_refresh_already_running_no_duplicate_worker(self):
        train=fake_train(active=True)
        app=app_fixture(train)
        app.apply_info_snapshot(snapshot())
        train.reapply_permissions.assert_called_once()
        train._start_refresh.assert_not_called()

    def test_08_unapproved_train_key_does_not_start(self):
        train=fake_train()
        app=app_fixture(train)
        snap=PermissionSnapshot(has_verified_payload=True,
                                permissions=frozenset({"start_tab"}),
                                plan_status="active",max_windows=2)
        app.apply_info_snapshot(snap)
        train._start_refresh.assert_not_called()

    def test_09_closed_app_does_not_refresh_train_or_tabs(self):
        train=fake_train()
        app=app_fixture(train)
        app._closed=True
        app.apply_info_snapshot(snapshot())
        train.reapply_permissions.assert_not_called()
        app.apply_verified_permissions.assert_not_called()

    def test_10_original_unit_test_seam_without_lifecycle_safe(self):
        train=fake_train()
        app=app_fixture(train)
        del app.lifecycle
        app.apply_info_snapshot(snapshot())
        self.assertEqual(app.root.after.call_count,1)
        train.reapply_permissions.assert_not_called()

    def test_11_invalid_snapshot_does_not_queue_tk(self):
        app=app_fixture(fake_train())
        with self.assertRaises(TypeError):
            app.apply_info_snapshot({"permissions":["farm_tab"]})
        app.root.after.assert_not_called()

    def test_12_default_shell_source_has_no_game_or_token_grant(self):
        code=(ROOT/"src/shell.py").read_text(encoding="utf-8")
        for bad in ("VerifiedClaims(", "receive_token(", "SendInput(",
                    "ReadProcessMemory(", "PostMessage(",
                    "CreateProcess(", "ProxyTab(", "bypass_info("):
            self.assertNotIn(bad,code)
        self.assertIn("refresh_train = getattr(train, 'reapply_permissions', None)",code)
        self.assertIn("self.root.after(0, update_on_tk_thread)",code)

if __name__=="__main__":
    unittest.main()
