"""S54 stop timeout status must preserve one-way shutdown latch.

Deterministic concurrency for lifecycle mutex, joined worker and independent
clock cleanup lock; no game, account, OS, or Proxy operations.
"""
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
from login_schedule_worker import F09ScheduleEvaluationWorker

class S54PermanentCloseDuringTimeoutTests(unittest.TestCase):
    def setUp(self):
        self.when = datetime(2026, 10, 9, 3, 59, 50)
        self.cfg = ReadOnlyScheduleSettings(
            "READ_ONLY_VALIDATED", "04:00", "04:20",
            "OPAQUE_SCHEDULE_FLAG", "OPAQUE_POWER_FLAG")
        self.worker = F09ScheduleEvaluationWorker(self.cfg, now=lambda: self.when)
        self.releases = []
        self.threads = []

    def tearDown(self):
        for release in self.releases:
            release.set()
        for thread in self.threads:
            thread.join(2)
            self.assertFalse(thread.is_alive(), "S54_TEST_THREAD_LEAK")
        self.assertTrue(self.worker.shutdown(2))
        self.assertFalse(self.worker.thread_alive)

    def _hold_independent_poll(self, worker):
        entered, release = threading.Event(), threading.Event()
        self.releases.append(release)
        def paused_clock():
            entered.set()
            if not release.wait(3):
                raise TimeoutError("S54_INJECTED_POLL_TIMEOUT")
            return self.when
        worker._now = paused_clock
        results = []
        thread = threading.Thread(
            target=lambda: results.append(worker.poll_once()),
            name="S54-external-poll", daemon=True)
        self.threads.append(thread)
        thread.start()
        self.assertTrue(entered.wait(1))
        return thread, results, release

    def _hold_running_worker_clock(self):
        entered, release = threading.Event(), threading.Event()
        self.releases.append(release)
        real_wait = self.worker._cancel.wait
        def accelerated_wait(_seconds):
            return real_wait(0.01)
        def paused_clock():
            entered.set()
            if not release.wait(3):
                raise TimeoutError("S54_INJECTED_WORKER_TIMEOUT")
            return self.when
        self.worker._cancel.wait = accelerated_wait
        self.assertTrue(self.worker.start())
        self.worker._now = paused_clock
        self.assertTrue(entered.wait(1))
        self.assertTrue(self.worker.thread_alive)
        return release

    def test_closed_latch_outweighs_lifecycle_mutex_timeout(self):
        self.assertTrue(self.worker.start())
        self.worker._lifecycle_lock.acquire()
        try:
            self.worker.request_shutdown()
            start = time.monotonic()
            self.assertFalse(self.worker.stop(.02))
            self.assertLess(time.monotonic()-start, .25)
            self.assertEqual(self.worker.status, "CLOSED")
            self.assertTrue(self.worker._stop_requested.is_set())
            self.assertEqual(self.worker._pending_stop_callers, 0)
        finally:
            self.worker._lifecycle_lock.release()
        self.assertTrue(self.worker.stop(2))
        self.assertFalse(self.worker.start())

    def test_nonclosed_mutex_timeout_retains_stopping(self):
        self.assertTrue(self.worker.start())
        self.worker._lifecycle_lock.acquire()
        try:
            self.assertFalse(self.worker.stop(0))
            self.assertEqual(self.worker.status, "STOPPING")
        finally:
            self.worker._lifecycle_lock.release()
        self.assertTrue(self.worker.stop(2))
        self.assertEqual(self.worker.status, "STOPPED")

    def test_closed_latch_outweighs_worker_join_timeout(self):
        release = self._hold_running_worker_clock()
        self.worker.request_shutdown()
        before = time.monotonic()
        self.assertFalse(self.worker.stop(.025))
        self.assertLess(time.monotonic()-before, .3)
        self.assertEqual(self.worker.status, "CLOSED")
        self.assertTrue(self.worker.thread_alive)
        self.assertTrue(self.worker._stop_requested.is_set())
        release.set()
        self.assertTrue(self.worker.stop(2))
        self.assertFalse(self.worker.start())

    def test_nonclosed_worker_join_timeout_retains_stopping(self):
        release = self._hold_running_worker_clock()
        self.assertFalse(self.worker.stop(.025))
        self.assertEqual(self.worker.status, "STOPPING")
        release.set()
        self.assertTrue(self.worker.stop(2))
        self.assertTrue(self.worker.start())
        self.assertTrue(self.worker.stop(2))

    def test_closed_latch_outweighs_last_clock_cleanup_lock_timeout(self):
        self.assertTrue(self.worker.start())
        thread, events, release = self._hold_independent_poll(self.worker)
        self.worker.request_shutdown()
        before = time.monotonic()
        self.assertFalse(self.worker.stop(.03))
        self.assertLess(time.monotonic()-before, .3)
        self.assertEqual(self.worker.status, "CLOSED")
        self.assertTrue(self.worker._stop_requested.is_set())
        self.assertTrue(self.worker._cancel.is_set())
        release.set()
        thread.join(2)
        self.assertEqual(events, [()])
        self.assertTrue(self.worker.stop(2))
        self.assertFalse(self.worker.start())

    def test_nonclosed_last_lock_timeout_retains_stopping(self):
        self.assertTrue(self.worker.start())
        thread, events, release = self._hold_independent_poll(self.worker)
        self.assertFalse(self.worker.stop(.03))
        self.assertEqual(self.worker.status, "STOPPING")
        self.assertTrue(self.worker._stop_requested.is_set())
        release.set()
        thread.join(2)
        self.assertEqual(events, [()])
        self.assertTrue(self.worker.stop(2))
        self.assertTrue(self.worker.start())
        self.assertTrue(self.worker.stop(2))

    def test_fake_tk_destroy_with_contended_mutex_does_not_misreport_worker(self):
        label = FakeLabel()
        with patch("tkinter.Label", FakeLabel):
            life = F09ReadOnlyTabLifetime(
                label, self.cfg, now=lambda: self.when)
        self.assertTrue(life.start_preview_and_evaluation())
        life.worker._lifecycle_lock.acquire()
        try:
            began = time.monotonic()
            label.exists = False
            for callback in label._bindings["<Destroy>"]:
                callback(SimpleNamespace(widget=label))
            self.assertLess(time.monotonic()-began, .25)
            self.assertTrue(life.closed)
            self.assertFalse(life.finish_close(0))
            self.assertEqual(life.worker.status, "CLOSED")
            self.assertTrue(life.worker._stop_requested.is_set())
        finally:
            life.worker._lifecycle_lock.release()
        self.assertTrue(life.finish_close(2))
        self.assertFalse(life.worker.start())

    def test_normal_successful_shutdown_remains_closed_and_idempotent(self):
        self.assertTrue(self.worker.start())
        self.assertTrue(self.worker.shutdown(2))
        self.assertEqual(self.worker.status, "CLOSED")
        self.assertTrue(self.worker.shutdown(2))
        self.assertFalse(self.worker.start())

    def test_scope_excludes_game_proxy_os_and_account_writes(self):
        code = (ROOT / "src/login_schedule_worker.py").read_text("utf-8")
        for forbidden in ("write_settings(", "_open_game_batch(",
                          "CreateProcessW(", "PostMessage(",
                          "subprocess.Popen(", "shutdown /s /t 0"):
            self.assertNotIn(forbidden, code)

if __name__ == "__main__":
    unittest.main()
