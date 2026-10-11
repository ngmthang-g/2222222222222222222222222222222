"""S124 H12: double guard; test-only stub verification is NOT signed Info."""
from __future__ import annotations
import sys
from pathlib import Path
import unittest
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"src"))
from permission_guard import PermissionGuard, VerifiedClaims
from start_windows import GameWindow
from train_row_permission import TrainRowPermissionGate

def win(pid=123,hwnd=456):
    return GameWindow(hwnd,pid,"Test HWND","TestWnd","NOT_GAME.exe")

class FakeNative:
    def __init__(self):
        self.visible=True
        self.exists=True
        self.pid=123
        self.fail=False
    def is_window(self, hwnd):
        if self.fail: raise OSError("native-fail")
        return self.exists
    def is_visible(self, hwnd): return self.visible
    def process_id(self, hwnd): return self.pid

def fake_guard(*,allowed=True,limit=2,expired=False):
    """TEST ONLY: stub signing callback is not a real token verification."""
    guard=PermissionGuard()
    guard.receive_token("CI_ONLY_FAKE",lambda _:VerifiedClaims(
        permissions=frozenset({"farm_tab"} if allowed else {"login_tab"}),
        plan_status="active",max_windows=limit,expires=expired))
    return guard

class S124GateTests(unittest.TestCase):
    def setUp(self):
        self.backend=FakeNative()
        self.guard=fake_guard()
        self.running=1
        self.gate=TrainRowPermissionGate(
            self.guard, lambda:self.running, lambda:self.backend)
    def test_01_defaults_denied(self):
        self.assertFalse(TrainRowPermissionGate().permitted(win()))
    def test_02_auth_fixture_and_matching_native_id(self):
        self.assertTrue(self.gate.permitted(win()))
    def test_03_wrong_pid_denies(self):
        self.assertFalse(self.gate.permitted(win(pid=124)))
    def test_04_hidden_window_denies(self):
        self.backend.visible=False
        self.assertFalse(self.gate.permitted(win()))
    def test_05_closed_window_denies(self):
        self.backend.exists=False
        self.assertFalse(self.gate.permitted(win()))
    def test_06_expired_denies(self):
        self.assertFalse(TrainRowPermissionGate(
            fake_guard(expired=True),lambda:1,lambda:self.backend).permitted(win()))
    def test_07_missing_farm_tab_denies(self):
        self.assertFalse(TrainRowPermissionGate(
            fake_guard(allowed=False),lambda:1,lambda:self.backend).permitted(win()))
    def test_08_limit_exceeded_denies(self):
        self.running=3
        self.assertFalse(self.gate.permitted(win()))
    def test_09_invalid_running_bool_denies(self):
        self.assertFalse(TrainRowPermissionGate(
            self.guard,lambda:True,lambda:self.backend).permitted(win()))
    def test_10_running_zero_denies(self):
        self.running=0
        self.assertFalse(self.gate.permitted(win()))
    def test_11_revoked_same_identity_denies(self):
        self.assertTrue(self.gate.permitted(win()))
        self.guard.clear()
        self.assertFalse(self.gate.permitted(win()))
    def test_12_native_error_denies(self):
        self.backend.fail=True
        self.assertFalse(self.gate.permitted(win()))
    def test_13_bad_native_pid_type_denies(self):
        self.backend.pid=True
        self.assertFalse(self.gate.permitted(win()))
    def test_14_no_running_provider_denies(self):
        self.assertFalse(TrainRowPermissionGate(
            self.guard,None,lambda:self.backend).permitted(win()))
    def test_15_no_bare_bool_authorization(self):
        self.assertFalse(TrainRowPermissionGate(
            True,lambda:1,lambda:self.backend).permitted(win()))
    def test_16_heartbeat_reapplies_even_if_cache_same(self):
        source=(R/"src/train_account_rows.py").read_text(encoding="utf-8")
        self.assertIn("self.reapply_permissions()",source)
        self.assertIn("self._permission_gate.permitted(window)",source)
        self.assertIn("self.editor._sync_apply_buttons()",source)
        self.assertNotIn("WriteProcessMemory(",source)
if __name__=="__main__":unittest.main()
