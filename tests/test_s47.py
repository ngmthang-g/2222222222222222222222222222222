"""S47 real worker total timeout budget and concurrent start/stop fence tests."""
from __future__ import annotations
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
import sys
import threading
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
from test_s41 import FakeLabel
from login_schedule_lifetime import F09ReadOnlyTabLifetime
from login_schedule_settings import ReadOnlyScheduleSettings
from login_schedule_worker import F09ScheduleEvaluationWorker, BLOCKED_ACTION


class S47DeadlineTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 9, 3, 59, 50)
        self.config = ReadOnlyScheduleSettings(
            "READ_ONLY_VALIDATED", "04:00", "04:20",
            "UNKNOWN_SCHEDULE_FLAG", "UNKNOWN_POWER_FLAG")
        self.worker = F09ScheduleEvaluationWorker(self.config, now=lambda: self.now)
        self.releases = []
        self.threads = []

    def tearDown(self):
        for event in self.releases:
            event.set()
        for thread in self.threads:
            thread.join(2)
        self.worker.shutdown(timeout=2)
        self.assertFalse(self.worker.thread_alive)

    def test_idle_stop_returns_stopped_and_restart_succeeds(self):
        self.assertTrue(self.worker.stop(timeout=0))
        self.assertEqual(self.worker.status, "STOPPED")
        self.assertTrue(self.worker.start())
        self.assertTrue(self.worker.stop(timeout=2))

    def test_contended_mutex_stop_zero_timeout_is_bounded(self):
        self.assertTrue(self.worker.start())
        self.assertTrue(self.worker._lifecycle_lock.acquire(blocking=False))
        try:
            began = time.monotonic()
            self.assertFalse(self.worker.stop(timeout=0))
            self.assertLess(time.monotonic()-began, 0.25)
            self.assertTrue(self.worker._cancel.is_set())
            self.assertTrue(self.worker._stop_requested.is_set())
            self.assertEqual(self.worker.status, "STOPPING")
        finally:
            self.worker._lifecycle_lock.release()
        self.assertTrue(self.worker.stop(timeout=2))
        self.assertFalse(self.worker._stop_requested.is_set())

    def test_contended_mutex_stop_positive_timeout_is_bounded(self):
        self.assertTrue(self.worker.start())
        self.worker._lifecycle_lock.acquire()
        try:
            t0 = time.monotonic()
            self.assertFalse(self.worker.stop(timeout=0.025))
            self.assertLess(time.monotonic()-t0, 0.25)
        finally:
            self.worker._lifecycle_lock.release()
        self.assertTrue(self.worker.stop(timeout=2))

    def test_still_pending_stop_denies_new_start_until_cleaned(self):
        self.assertTrue(self.worker.start())
        self.worker._lifecycle_lock.acquire()
        try:
            self.assertFalse(self.worker.stop(timeout=0))
            self.assertFalse(self.worker._cancel.is_set() is False)
        finally:
            self.worker._lifecycle_lock.release()
        self.assertFalse(self.worker.start())
        self.assertTrue(self.worker.stop(timeout=2))
        self.assertTrue(self.worker.start())
        self.assertTrue(self.worker.stop(timeout=2))

    def test_request_shutdown_is_immediate_even_when_lock_held(self):
        self.worker.start()
        self.worker._lifecycle_lock.acquire()
        try:
            began=time.monotonic()
            self.worker.request_shutdown()
            self.assertLess(time.monotonic()-began,0.25)
            self.assertTrue(self.worker._cancel.is_set())
            self.assertTrue(self.worker._stop_requested.is_set())
            self.assertFalse(self.worker.start())
        finally:
            self.worker._lifecycle_lock.release()
        self.assertTrue(self.worker.shutdown())

    def _slow_start(self, permanent: bool):
        entered=threading.Event()
        resume=threading.Event()
        self.releases.append(resume)
        def clock():
            entered.set()
            if not resume.wait(2):
                raise RuntimeError("TEST_CLOCK_WAIT_TIMEOUT")
            return self.now
        self.worker._now=clock
        results=[]
        thread=threading.Thread(target=lambda:results.append(self.worker.start()),daemon=True)
        self.threads.append(thread)
        thread.start()
        self.assertTrue(entered.wait(1))
        if permanent:
            self.worker.request_shutdown()
        else:
            self.assertFalse(self.worker.stop(timeout=0.015))
        resume.set()
        thread.join(2)
        self.assertFalse(thread.is_alive())
        self.assertEqual(results,[False])
        self.assertFalse(self.worker.thread_alive)
        self.assertTrue(self.worker._cancel.is_set())
        return permanent

    def test_cancel_while_start_time_provider_blocked(self):
        self._slow_start(permanent=False)
        self.assertTrue(self.worker.stop(timeout=2))
        self.assertTrue(self.worker.start())
        self.assertTrue(self.worker.stop(timeout=2))

    def test_permanent_close_while_start_time_provider_blocked(self):
        self._slow_start(permanent=True)
        self.assertFalse(self.worker.start())
        self.assertTrue(self.worker.shutdown(timeout=2))

    def test_stop_then_restart_preserves_blocked_event_only(self):
        self.worker.start()
        self.now=datetime(2026,10,9,4,21)
        events=self.worker.poll_once()
        self.assertEqual([e.kind for e in events],["close","open"])
        self.assertTrue(all(e.status==BLOCKED_ACTION for e in events))
        self.assertTrue(self.worker.stop())
        self.assertEqual(len(self.worker.blocked_occurrences()),2)
        self.assertTrue(self.worker.start())
        self.assertEqual(self.worker.blocked_occurrences(),())
        self.assertTrue(self.worker.stop())

    def test_timeout_rejects_invalid_values_before_cancellation(self):
        self.assertTrue(self.worker.start())
        for bad in (-1, 31, "1", True, None, float("nan"), float("inf")):
            with self.subTest(bad=str(bad)), self.assertRaises(ValueError):
                self.worker.stop(bad)
        self.assertFalse(self.worker._cancel.is_set())
        self.assertTrue(self.worker.stop())

    def test_real_thread_stop_still_interrupts_twenty_second_wait(self):
        self.assertTrue(self.worker.start())
        began=time.monotonic()
        self.assertTrue(self.worker.stop(timeout=2))
        self.assertLess(time.monotonic()-began,0.5)

    def test_shutdown_remains_idempotent(self):
        self.assertTrue(self.worker.start())
        self.assertTrue(self.worker.shutdown())
        self.assertTrue(self.worker.shutdown())
        self.assertFalse(self.worker.start())

    def test_initial_opaque_flag_never_automatically_arms(self):
        self.assertEqual(self.worker.status,"IDLE")
        self.assertFalse(self.worker.active)
        self.assertFalse(self.worker.thread_alive)

    def test_lifetime_finish_close_mutex_timeout_budget(self):
        label=FakeLabel()
        with patch("tkinter.Label",FakeLabel):
            life=F09ReadOnlyTabLifetime(label,self.config,now=lambda:self.now)
        self.assertTrue(life.start_preview_and_evaluation())
        life.close()
        self.assertTrue(life.closed)
        self.assertTrue(life.worker._cancel.is_set())
        life.worker._lifecycle_lock.acquire()
        try:
            began=time.monotonic()
            self.assertFalse(life.finish_close(timeout=0.02))
            self.assertLess(time.monotonic()-began,0.25)
            self.assertEqual(life.status,"CLOSING_WORKER")
        finally:
            life.worker._lifecycle_lock.release()
        self.assertTrue(life.finish_close(timeout=2))
        self.assertEqual(life.status,"CLOSED")

    def test_real_external_stop_holds_join_cleanup_and_finish_is_bounded(self):
        label=FakeLabel()
        with patch("tkinter.Label",FakeLabel):
            life=F09ReadOnlyTabLifetime(label,self.config,now=lambda:self.now)
        self.assertTrue(life.start_preview_and_evaluation())
        old=life.worker._thread
        real_join=old.join
        entered=threading.Event()
        resume=threading.Event()
        self.releases.append(resume)
        results=[]
        def paused_join(timeout=None):
            real_join(timeout)
            entered.set()
            if not resume.wait(2):
                raise RuntimeError("TEST_JOIN_PAUSE_TIMEOUT")
        old.join=paused_join
        def external_stop():
            results.append(life.worker.stop(timeout=2))
        background=threading.Thread(target=external_stop,daemon=True)
        self.threads.append(background)
        background.start()
        self.assertTrue(entered.wait(1))
        life.close()
        began=time.monotonic()
        self.assertFalse(life.finish_close(timeout=0.025))
        self.assertLess(time.monotonic()-began,0.25)
        resume.set()
        background.join(2)
        self.assertEqual(results,[True])
        self.assertTrue(life.finish_close(timeout=2))
        self.assertFalse(life.worker.thread_alive)

    def test_finish_close_before_lifetime_close_is_denied(self):
        label=FakeLabel()
        with patch("tkinter.Label",FakeLabel):
            life=F09ReadOnlyTabLifetime(label,self.config,now=lambda:self.now)
        with self.assertRaises(RuntimeError):
            life.finish_close(timeout=0)

    def test_no_launch_config_writes_or_proxy_in_changed_source(self):
        source=(ROOT/"src/login_schedule_worker.py").read_text(encoding="utf-8")
        for banned in ("write_settings(", "_open_game_batch(", "CreateProcessW(",
                       "subprocess.Popen(", "shutdown /s /t 0", "PostMessage("):
            self.assertNotIn(banned,source)


if __name__=="__main__":
    unittest.main()
