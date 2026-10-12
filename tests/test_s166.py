"""S166: original Train passive window lifecycle via real shared S09 producer.

Unit fixtures never create an entitlement. Win64 native source + Tk ownership
is separately checked in S166_WINDOWS_TRAIN_LIFECYCLE_SMOKE.py.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest
from unittest.mock import Mock

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))

from farm_train_composition import TkTrainComposition
from start_polling import StartWindowProducer

class FakeSharedProducer(StartWindowProducer):
    """A StartWindowProducer *subclass* with no worker, unit-only."""
    def __init__(self, active=False, will_start=True):
        self.running=active
        self.will_start=will_start
        self.starts=0
        self.stops=0
    @property
    def active(self):
        return self.running
    def start(self):
        self.starts+=1
        if self.will_start:
            self.running=True
            return True
        return False
    def stop(self):
        self.stops+=1
        self.running=False

def make_comp(producer=None, *, allowed=True, refresh_success=True):
    # Pure lifecycle method exercise: no Tk widgets or disk are constructed.
    panel=TkTrainComposition.__new__(TkTrainComposition)
    panel._closed=False
    panel.window_producer=producer
    panel._lifecycle_owns_producer=False
    panel._readonly_refresh_requested=False
    panel.accounts=None
    panel._authorized=Mock(return_value=allowed)
    panel.start_readonly_window_refresh=Mock(return_value=refresh_success)
    panel.stop_readonly_window_refresh=Mock()
    return panel

class S166LifecycleUnit(unittest.TestCase):
    def test_01_no_producer_never_starts_its_own_worker(self):
        p=make_comp()
        self.assertFalse(p._start_refresh())
        p.start_readonly_window_refresh.assert_not_called()
        self.assertFalse(p._lifecycle_owns_producer)

    def test_02_original_shared_stopped_owned_exactly_once(self):
        shared=FakeSharedProducer()
        p=make_comp(shared)
        self.assertTrue(p._start_refresh())
        self.assertTrue(p._lifecycle_owns_producer)
        self.assertEqual(shared.starts,1)
        self.assertTrue(shared.active)
        self.assertTrue(p._start_refresh())
        self.assertEqual(shared.starts,1)
        p._stop_refresh()
        p._stop_refresh()
        self.assertFalse(shared.active)
        self.assertEqual(shared.stops,1)
        self.assertFalse(p._lifecycle_owns_producer)

    def test_03_external_owner_never_stopped(self):
        shared=FakeSharedProducer(active=True)
        p=make_comp(shared)
        self.assertTrue(p._start_refresh())
        self.assertFalse(p._lifecycle_owns_producer)
        self.assertEqual(shared.starts,0)
        p._stop_refresh()
        self.assertTrue(shared.active)
        self.assertEqual(shared.stops,0)

    def test_04_missing_permission_never_starts_worker(self):
        shared=FakeSharedProducer()
        p=make_comp(shared,allowed=False)
        self.assertFalse(p._start_refresh())
        self.assertEqual(shared.starts,0)
        p.stop_readonly_window_refresh.assert_called_once()

    def test_05_start_returns_false_due_stopping_previous_worker(self):
        shared=FakeSharedProducer(will_start=False)
        p=make_comp(shared)
        self.assertFalse(p._start_refresh())
        self.assertEqual(shared.starts,1)
        self.assertEqual(shared.stops,0)
        p.start_readonly_window_refresh.assert_not_called()

    def test_06_readonly_account_binding_failure_rolls_back_owned_scan(self):
        shared=FakeSharedProducer()
        p=make_comp(shared,refresh_success=False)
        self.assertFalse(p._start_refresh())
        self.assertEqual(shared.starts,1)
        self.assertEqual(shared.stops,1)
        self.assertFalse(shared.active)

    def test_07_readonly_account_failure_cannot_stop_external_owner(self):
        shared=FakeSharedProducer(active=True)
        p=make_comp(shared,refresh_success=False)
        self.assertFalse(p._start_refresh())
        self.assertTrue(shared.active)
        self.assertEqual(shared.stops,0)

    def test_08_native_start_error_not_exposed_as_permission(self):
        shared=FakeSharedProducer()
        def fail():
            raise OSError("test-owned backend error")
        shared.start=fail
        p=make_comp(shared)
        self.assertFalse(p._start_refresh())
        self.assertFalse(p._lifecycle_owns_producer)

    def test_09_refresh_exception_releases_only_our_worker(self):
        shared=FakeSharedProducer()
        p=make_comp(shared)
        p.start_readonly_window_refresh.side_effect=RuntimeError("no HWND")
        self.assertFalse(p._start_refresh())
        self.assertEqual(shared.stops,1)

    def test_10_permission_revoke_stops_own_worker_then_tears_down_rows(self):
        shared=FakeSharedProducer()
        p=make_comp(shared)
        self.assertTrue(p._start_refresh())
        p._reapply_all_controls=Mock()
        p._teardown_sensitive=Mock()
        p._authorized.return_value=False
        self.assertFalse(p.reapply_permissions())
        self.assertFalse(shared.active)
        p._teardown_sensitive.assert_called_once()

    def test_11_revocation_never_stops_external_worker(self):
        shared=FakeSharedProducer(active=True)
        p=make_comp(shared)
        self.assertTrue(p._start_refresh())
        p._reapply_all_controls=Mock()
        p._teardown_sensitive=Mock()
        p._authorized.return_value=False
        self.assertFalse(p.reapply_permissions())
        self.assertTrue(shared.active)
        self.assertEqual(shared.stops,0)

    def test_12_shutdown_releases_owned_scan_and_original_teardown(self):
        shared=FakeSharedProducer()
        p=make_comp(shared)
        self.assertTrue(p._start_refresh())
        p._teardown_sensitive=Mock()
        p.shutdown()
        self.assertTrue(p._closed)
        self.assertEqual(shared.stops,1)
        p._teardown_sensitive.assert_called_once()
        p.shutdown()
        self.assertEqual(shared.stops,1)

    def test_13_closed_train_never_starts(self):
        shared=FakeSharedProducer()
        p=make_comp(shared)
        p._closed=True
        self.assertFalse(p._start_refresh())
        self.assertEqual(shared.starts,0)

    def test_14_passive_input_and_original_cadence_unmodified(self):
        src=(ROOT/"src/farm_train_composition.py").read_text("utf-8")
        for forbidden in ("SendInput(", "PostMessage(", "ReadProcessMemory(",
                          "CreateProcess(", "VerifiedClaims(", "ProxyTab(",
                          "click_at(", "RequestSellItem("):
            self.assertNotIn(forbidden,src)
        self.assertIn("TRAIN_ACCOUNT_REFRESH_MS",src)
        self.assertIn("self.accounts._start_refresh()",src)
        self.assertIn("self.accounts._stop_refresh()",src)

if __name__=="__main__":
    unittest.main()
