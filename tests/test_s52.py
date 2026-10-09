"""S52 F09 exception-completion must not overwrite permanent shutdown/stop state.

Deterministic original-free testing. No game actions or persistent writes.
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


class S52ExceptionAfterCancellationTests(unittest.TestCase):
    def setUp(self):
        self.when = datetime(2026, 10, 9, 3, 59, 50)
        self.cfg = ReadOnlyScheduleSettings(
            "READ_ONLY_VALIDATED", "04:00", "04:20",
            "OPAQUE_SCHEDULE_ON", "OPAQUE_POWER")
        self.worker = F09ScheduleEvaluationWorker(
            self.cfg, now=lambda: self.when)
        self.threads = []
        self.releases = []

    def tearDown(self):
        for release in self.releases:
            release.set()
        for thread in self.threads:
            thread.join(2)
            self.assertFalse(thread.is_alive(), "S52 test thread leaked")
        self.worker.shutdown(2)
        self.assertFalse(self.worker.thread_alive)

    def _time_source_that_fails_after_release(self):
        entered, release = threading.Event(), threading.Event()
        self.releases.append(release)
        def clock():
            entered.set()
            if not release.wait(2):
                raise TimeoutError("S52_TEST_TIME_SOURCE_TIMEOUT")
            raise ValueError("S52_TEST_INJECTED_BAD_CLOCK")
        return entered, release, clock

    def _spawn(self, fn):
        results = []
        thread = threading.Thread(
            target=lambda: results.append(fn()),
            name="S52-fault-worker", daemon=True)
        self.threads.append(thread)
        thread.start()
        return thread, results

    def test_start_clock_fault_after_lockfree_shutdown_reports_closed(self):
        entered, release, clock = self._time_source_that_fails_after_release()
        self.worker._now = clock
        thread, result = self._spawn(self.worker.start)
        self.assertTrue(entered.wait(1))
        before = time.monotonic()
        self.worker.request_shutdown()
        self.assertLess(time.monotonic()-before, .25)
        release.set()
        thread.join(2)
        self.assertEqual(result, [False])
        self.assertEqual(self.worker.status, "CLOSED")
        self.assertTrue(self.worker._closed)
        self.assertTrue(self.worker._cancel.is_set())
        self.assertTrue(self.worker._stop_requested.is_set())
        self.assertFalse(self.worker.thread_alive)
        self.assertFalse(self.worker.start())

    def test_start_clock_fault_after_timed_out_stop_reports_stopping(self):
        entered, release, clock = self._time_source_that_fails_after_release()
        self.worker._now = clock
        thread, result = self._spawn(self.worker.start)
        self.assertTrue(entered.wait(1))
        self.assertFalse(self.worker.stop(0))
        self.assertTrue(self.worker._stop_requested.is_set())
        release.set()
        thread.join(2)
        self.assertEqual(result, [False])
        self.assertEqual(self.worker.status, "STOPPING")
        self.assertTrue(self.worker.stop(2))
        self.assertFalse(self.worker._stop_requested.is_set())
        self.worker._now = lambda: self.when
        self.assertTrue(self.worker.start())
        self.assertTrue(self.worker.stop(2))

    def test_start_clock_fault_without_cancellation_is_blocked_clock(self):
        def fail():
            raise OSError("S52_TEST_CLOCK_PROVIDER_FAIL")
        self.worker._now = fail
        self.assertFalse(self.worker.start())
        self.assertEqual(self.worker.status, "BLOCKED_CLOCK")
        self.assertFalse(self.worker.thread_alive)

    def test_poll_clock_fault_after_lockfree_shutdown_reports_closed(self):
        self.assertTrue(self.worker.start())
        entered, release, clock = self._time_source_that_fails_after_release()
        self.worker._now = clock
        thread, results = self._spawn(self.worker.poll_once)
        self.assertTrue(entered.wait(1))
        started = time.monotonic()
        self.worker.request_shutdown()
        self.assertLess(time.monotonic() - started, .25)
        release.set()
        thread.join(2)
        self.assertEqual(results, [()])
        self.assertEqual(self.worker.status, "CLOSED")
        self.assertTrue(self.worker._cancel.is_set())
        self.assertEqual(self.worker.blocked_occurrences(), ())
        self.assertTrue(self.worker.stop(2))

    def test_poll_clock_fault_after_timeout_stop_reports_stopping(self):
        self.assertTrue(self.worker.start())
        entered, release, clock = self._time_source_that_fails_after_release()
        self.worker._now = clock
        thread, results = self._spawn(self.worker.poll_once)
        self.assertTrue(entered.wait(1))
        self.worker._lifecycle_lock.acquire()
        try:
            self.assertFalse(self.worker.stop(0))
        finally:
            self.worker._lifecycle_lock.release()
        release.set()
        thread.join(2)
        self.assertEqual(results, [()])
        self.assertEqual(self.worker.status, "STOPPING")
        self.assertTrue(self.worker.stop(2))
        self.assertFalse(self.worker._stop_requested.is_set())

    def test_poll_clock_fault_without_cancel_is_blocked_clock(self):
        self.assertTrue(self.worker.start())
        self.worker._now = lambda: (_ for _ in ()).throw(
            OSError("S52_TEST_POLL_FAILURE"))
        self.assertEqual(self.worker.poll_once(), ())
        self.assertEqual(self.worker.status, "BLOCKED_CLOCK")
        self.assertTrue(self.worker._cancel.is_set())
        self.assertTrue(self.worker.stop(2))

    def test_run_wait_exception_after_shutdown_reports_closed(self):
        entered, release = threading.Event(), threading.Event()
        self.releases.append(release)
        def failed_wait(_seconds):
            entered.set()
            if not release.wait(2):
                raise TimeoutError("S52_TEST_RUN_WAIT_TIMEOUT")
            raise RuntimeError("S52_TEST_WORKER_WAIT_FAULT")
        with patch.object(self.worker._cancel, "wait", side_effect=failed_wait):
            self.assertTrue(self.worker.start())
            self.assertTrue(entered.wait(1))
            self.worker.request_shutdown()
            release.set()
            self.assertTrue(self.worker.stop(2))
        self.assertEqual(self.worker.status, "CLOSED")
        self.assertFalse(self.worker.thread_alive)

    def test_run_wait_exception_without_shutdown_is_blocked_worker(self):
        entered, release = threading.Event(), threading.Event()
        self.releases.append(release)
        def failed_wait(_seconds):
            entered.set()
            if not release.wait(2):
                raise TimeoutError("S52_TEST_RUN_WAIT_TIMEOUT")
            raise RuntimeError("S52_TEST_RUN_FAILED")
        with patch.object(self.worker._cancel, "wait", side_effect=failed_wait):
            self.assertTrue(self.worker.start())
            self.assertTrue(entered.wait(1))
            release.set()
            self.worker._thread.join(2)
        self.assertEqual(self.worker.status, "BLOCKED_WORKER")
        self.assertTrue(self.worker._cancel.is_set())
        self.assertTrue(self.worker.stop(2))

    def test_fake_tk_destroy_while_poll_clock_fault_held_is_nonblocking(self):
        label = FakeLabel()
        with patch("tkinter.Label", FakeLabel):
            life = F09ReadOnlyTabLifetime(
                label, self.cfg, now=lambda: self.when)
        self.assertTrue(life.start_preview_and_evaluation())
        entered, release, clock = self._time_source_that_fails_after_release()
        life.worker._now = clock
        thread, result = self._spawn(life.worker.poll_once)
        self.assertTrue(entered.wait(1))
        began = time.monotonic()
        label.exists = False
        for callback in label._bindings["<Destroy>"]:
            callback(SimpleNamespace(widget=label))
        self.assertLess(time.monotonic() - began, .25)
        self.assertTrue(life.closed)
        release.set()
        thread.join(2)
        self.assertEqual(result, [()])
        self.assertEqual(life.worker.status, "CLOSED")
        self.assertTrue(life.finish_close(2))
        self.assertFalse(life.worker.thread_alive)

    def test_normal_due_schedule_still_blocked_only(self):
        self.assertTrue(self.worker.start())
        self.when = datetime(2026, 10, 9, 4, 21)
        events = self.worker.poll_once()
        self.assertEqual([x.kind for x in events], ["close", "open"])
        self.assertTrue(all(x.status == BLOCKED_ACTION for x in events))
        self.assertTrue(self.worker.stop(2))

    def test_no_credentials_proxy_real_game_or_os_action(self):
        code = (ROOT / "src/login_schedule_worker.py").read_text("utf-8")
        for bad in ("write_settings(", "_open_game_batch(", "CreateProcessW(",
                    "subprocess.Popen(", "shutdown /s /t 0", "PostMessage("):
            self.assertNotIn(bad, code)


if __name__ == "__main__":
    unittest.main()
