"""S48 F09 multiple concurrent stop callers cannot erase pending cancellation.

S48 repairs a real S47 source race; no real Login or game scheduler is wired.
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
from login_schedule_worker import F09ScheduleEvaluationWorker, BLOCKED_ACTION


class S48ConcurrentStopTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 9, 3, 59, 50)
        self.cfg = ReadOnlyScheduleSettings(
            "READ_ONLY_VALIDATED", "04:00", "04:20",
            "OPAQUE_SCHEDULE_ON", "OPAQUE_SHUTDOWN")
        self.worker = F09ScheduleEvaluationWorker(self.cfg, now=lambda: self.now)
        self.to_release = []
        self.threads = []

    def tearDown(self):
        for event in self.to_release:
            event.set()
        for thread in self.threads:
            thread.join(2)
            self.assertFalse(thread.is_alive(), "S48 thread leaked")
        self.worker.shutdown(2)
        self.assertFalse(self.worker.thread_alive)

    def _wait_pending(self, wanted, seconds=1.5):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            with self.worker._stop_request_lock:
                if self.worker._pending_stop_callers == wanted:
                    return True
            time.sleep(.002)
        return False

    def test_two_stop_callers_first_cleanup_does_not_erase_second_fence(self):
        self.assertTrue(self.worker.start())
        real_join = self.worker._thread.join
        in_join, release_join = threading.Event(), threading.Event()
        after_first, release_first = threading.Event(), threading.Event()
        self.to_release.extend((release_join, release_first))
        def held_join(timeout=None):
            real_join(timeout)
            in_join.set()
            if not release_join.wait(2):
                raise RuntimeError("S48_TEST_JOIN_TIMEOUT")
        self.worker._thread.join = held_join

        # Examine the true interleaving exactly after stopper A completes
        # cleanup but BEFORE its lifecycle lock is handed to stopper B.
        old_end = self.worker._end_stop_request
        def observe_end(cleaned):
            old_end(cleaned)
            if threading.current_thread().name == "S48-first" and cleaned:
                after_first.set()
                if not release_first.wait(2):
                    raise RuntimeError("S48_TEST_CLEANUP_TIMEOUT")
        self.worker._end_stop_request = observe_end
        results = []
        first = threading.Thread(name="S48-first",
                                 target=lambda: results.append(("A", self.worker.stop(2))),
                                 daemon=True)
        second = threading.Thread(name="S48-second",
                                  target=lambda: results.append(("B", self.worker.stop(2))),
                                  daemon=True)
        self.threads.extend((first, second))
        first.start()
        self.assertTrue(in_join.wait(1))
        second.start()
        self.assertTrue(self._wait_pending(2))
        release_join.set()
        self.assertTrue(after_first.wait(1))
        self.assertTrue(self.worker._stop_requested.is_set(),
                        "S47 bug: A cleared B's unfulfilled cancellation")
        self.assertTrue(self.worker._cancel.is_set())
        self.assertEqual(self.worker._pending_stop_callers, 1)
        self.assertFalse(self.worker.start())
        release_first.set()
        first.join(2)
        second.join(2)
        self.assertCountEqual(results, [("A", True), ("B", True)])
        self.assertEqual(self.worker._pending_stop_callers, 0)
        self.assertFalse(self.worker._stop_requested.is_set())
        self.assertFalse(self.worker.thread_alive)
        self.assertTrue(self.worker.start())
        self.assertTrue(self.worker.stop(2))

    def test_two_mutex_timeouts_retain_fence_until_explicit_cleanup(self):
        self.assertTrue(self.worker.start())
        self.worker._lifecycle_lock.acquire()
        try:
            for _ in range(2):
                began = time.monotonic()
                self.assertFalse(self.worker.stop(0.01))
                self.assertLess(time.monotonic()-began, 0.25)
            self.assertEqual(self.worker._pending_stop_callers, 0)
            self.assertTrue(self.worker._stop_requested.is_set())
            self.assertTrue(self.worker._cancel.is_set())
        finally:
            self.worker._lifecycle_lock.release()
        self.assertFalse(self.worker.start())
        self.assertTrue(self.worker.stop(2))
        self.assertFalse(self.worker._stop_requested.is_set())

    def test_failed_timeout_then_different_successful_stopper_can_clean(self):
        self.assertTrue(self.worker.start())
        self.worker._lifecycle_lock.acquire()
        try:
            self.assertFalse(self.worker.stop(0))
            self.assertFalse(self.worker.stop(.001))
        finally:
            self.worker._lifecycle_lock.release()
        self.assertFalse(self.worker.start())
        self.assertTrue(self.worker.stop(2))
        self.assertTrue(self.worker.start())
        self.assertTrue(self.worker.stop(2))

    def test_stop_validation_does_not_change_pending_request_count(self):
        for value in (None, True, -1, 31, "0", float("nan")):
            with self.subTest(value=str(value)), self.assertRaises(ValueError):
                self.worker.stop(value)
        self.assertEqual(self.worker._pending_stop_callers, 0)
        self.assertFalse(self.worker._stop_requested.is_set())

    def test_shutdown_while_stop_waiting_cannot_clear_permanent_fence(self):
        self.assertTrue(self.worker.start())
        self.worker._lifecycle_lock.acquire()
        try:
            self.assertFalse(self.worker.stop(.001))
            self.worker.request_shutdown()
        finally:
            self.worker._lifecycle_lock.release()
        self.assertTrue(self.worker.shutdown(2))
        self.assertTrue(self.worker._closed)
        self.assertTrue(self.worker._stop_requested.is_set())
        self.assertFalse(self.worker.start())

    def test_idle_and_repeated_stop_have_balanced_registration(self):
        self.assertTrue(self.worker.stop(0))
        self.assertTrue(self.worker.stop(0))
        self.assertEqual(self.worker._pending_stop_callers, 0)
        self.assertFalse(self.worker._stop_requested.is_set())
        self.assertTrue(self.worker.start())
        self.assertTrue(self.worker.stop(2))

    def test_blocked_only_events_still_never_dispatch_real_actions(self):
        self.assertTrue(self.worker.start())
        self.now = datetime(2026, 10, 9, 4, 21)
        events = self.worker.poll_once()
        self.assertEqual([e.kind for e in events], ["close", "open"])
        self.assertTrue(all(e.status == BLOCKED_ACTION for e in events))
        self.assertTrue(self.worker.stop(2))
        self.assertFalse(self.worker.start() is False)
        self.assertEqual(self.worker.blocked_occurrences(), ())
        self.worker.stop(2)

    def test_lifetime_destroy_two_worker_stop_requests_stays_closed(self):
        label = FakeLabel()
        with patch("tkinter.Label", FakeLabel):
            life = F09ReadOnlyTabLifetime(label, self.cfg, now=lambda: self.now)
        self.assertTrue(life.start_preview_and_evaluation())
        life.worker._lifecycle_lock.acquire()
        try:
            self.assertFalse(life.worker.stop(0))
            label.exists = False
            for cb in label._bindings["<Destroy>"]:
                cb(SimpleNamespace(widget=label))
            self.assertTrue(life.closed)
            self.assertTrue(life.worker._cancel.is_set())
            self.assertFalse(life.start_preview_and_evaluation())
        finally:
            life.worker._lifecycle_lock.release()
        self.assertTrue(life.finish_close(2))
        self.assertTrue(life.worker._stop_requested.is_set())
        self.assertFalse(life.worker.thread_alive)

    def test_no_credentials_writes_fake_actions_or_proxy(self):
        source = (ROOT/"src/login_schedule_worker.py").read_text(encoding="utf-8")
        for banned in ("write_settings(", "_open_game_batch(", "CreateProcessW(",
                       "subprocess.Popen(", "shutdown /s /t 0", "PostMessage("):
            self.assertNotIn(banned, source)


if __name__ == "__main__":
    unittest.main()
