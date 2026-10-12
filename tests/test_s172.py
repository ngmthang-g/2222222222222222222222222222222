"""S172 original I01 LSV passive HWND+PID account discovery proof.

Never infer RoleName/MapID or write acc_<character>_train. The real
independent Tk integration/native backend is tested by the Win64 smoke.
"""
from __future__ import annotations
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))

from start_polling import WindowSnapshot, StartWindowProducer
from start_windows import GameWindow
from train_lsv_passive_accounts import TkTrainLsvPassiveAccounts, LSV_ACCOUNT_REFRESH_MS
from train_account_rows import TrainAccountRegistry
from TLMToolIndependent import make_independent_builders
from local_feature_policy import LocalFeaturePolicy


def game(hwnd=16,pid=123):
    return GameWindow(hwnd,pid,"Thần Long  Mobile","UnityWndClass",
                      "thần long mobile.exe")


class Backend:
    is_visible_value=True
    process_pid=123
    def is_window(self,hwnd):return hwnd==16
    def is_visible(self,hwnd):return self.is_visible_value
    def process_id(self,hwnd):return self.process_pid


class S172RosterTests(unittest.TestCase):
    def setUp(self):
        self.backend=Backend()
        self.seam=TkTrainLsvPassiveAccounts.__new__(TkTrainLsvPassiveAccounts)

    def test_01_refresh_exact_original_I01_5000ms(self):
        self.assertEqual(LSV_ACCOUNT_REFRESH_MS,5000)

    def test_02_source_verified_identity_accepts_exact_window(self):
        self.assertTrue(self.seam._valid_window(game(),self.backend))

    def test_03_wrong_pid_fail_closed(self):
        self.backend.process_pid=77
        self.assertFalse(self.seam._valid_window(game(),self.backend))

    def test_04_recycled_hwnd_not_trusted(self):
        self.assertFalse(self.seam._valid_window(game(hwnd=42),self.backend))

    def test_05_unseen_and_non_visible_windows_denied(self):
        self.backend.is_visible_value=False
        self.assertFalse(self.seam._valid_window(game(),self.backend))

    def test_06_python_or_random_unity_window_not_game(self):
        fake=GameWindow(16,123,"Thần Long  Mobile","UnityWndClass","python.exe")
        self.assertFalse(self.seam._valid_window(fake,self.backend))

    def test_07_invalid_class_and_title_not_game(self):
        fake=GameWindow(16,123,"Game","MockClass","thần long mobile.exe")
        self.assertFalse(self.seam._valid_window(fake,self.backend))

    def test_08_wrong_shapes_never_trusted(self):
        self.assertFalse(self.seam._valid_window(None,self.backend))
        self.assertFalse(self.seam._valid_window(game(hwnd=0),self.backend))
        self.assertFalse(self.seam._valid_window(game(pid=0),self.backend))

    def test_09_backend_failure_denies_without_game_access(self):
        class Broken:
            def is_window(self,*_):raise OSError("TEST_SIMULATED")
        self.assertFalse(self.seam._valid_window(game(),Broken()))

    def test_10_shared_S123_registry_handles_pid_reuse(self):
        registry=TrainAccountRegistry()
        s=lambda win:WindowSnapshot(valid=True,windows=tuple(win))
        first=registry.reconcile(s([game()]))
        self.assertEqual(len(first.added),1)
        self.assertEqual(len(registry.reconcile(s([game()])).retained),1)
        reused=registry.reconcile(s([game(pid=77)]))
        self.assertEqual(reused.reused,((game(),game(pid=77)),))
        self.assertEqual(len(registry.reconcile(s([])).removed),1)

    def test_11_transient_unknown_window_read_preserves_real_identity(self):
        reg=TrainAccountRegistry()
        reg.reconcile(WindowSnapshot(valid=True,windows=(game(),)))
        result=reg.reconcile(WindowSnapshot(valid=False,error="TEST_TIMEOUT"))
        self.assertTrue(result.unknown)
        self.assertEqual(reg.rows,(game(),))

    def test_12_no_persistent_role_or_key_implemented(self):
        text=(ROOT/"src/train_lsv_passive_accounts.py").read_text("utf-8")
        for prohibited in ("read_role_name(", "acc_<character>_train =", "SendInput(",
                           "PostMessage(", "ReadProcessMemory(", "receive_token(",
                           "RequestSellItem(", "press_single_key_dll("):
            self.assertNotIn(prohibited,text)
        self.assertIn("Nhân vật: ? (HWND",text)

    def test_13_shared_producer_required_without_new_scanner(self):
        # Widget construction cannot be invoked without real Tk, so inspect
        # signature contract and exclude guessed independent scanner.
        import inspect
        sig=inspect.signature(TkTrainLsvPassiveAccounts.__init__)
        self.assertIn("producer",sig.parameters)
        self.assertIn("StartWindowProducer",str(sig))
        source=(ROOT/"src/train_lsv_passive_accounts.py").read_text("utf-8")
        self.assertNotIn("StartWindowProducer()",source)
        self.assertNotIn("EnumWindows(",source)

    def test_14_production_independent_builder_reuses_same_source(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            producer=StartWindowProducer()
            builders=make_independent_builders(Path(tmp)/"settings.ini",producer)
            self.assertIn("trainlsv_tab",builders)
            self.assertIn("farm_tab",builders)
            self.assertNotIn("proxy_tab",builders)

    def test_15_local_config_available_even_zero_games_no_issuer(self):
        policy=LocalFeaturePolicy(frozenset({"trainlsv_tab"}))
        self.assertTrue(policy.config_available("trainlsv_tab"))
        self.assertFalse(policy.window_observation_allowed("trainlsv_tab",0))

if __name__=="__main__":
    unittest.main()
