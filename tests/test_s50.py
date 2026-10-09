"""S50 F09 worker start OSError failure mode + Tk lifecycle regression.

Only pure/test-owned scheduler evaluation. No real game or Proxy actions.
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


class S50WorkerStartFailureTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 9, 3, 59, 50)
        self.settings = ReadOnlyScheduleSettings(
            "READ_ONLY_VALIDATED", "04:00", "04:20",
            "UNKNOWN_SCHEDULE_FLAG", "UNKNOWN_POWER_FLAG")
        self.worker = F09ScheduleEvaluationWorker(
            self.settings, now=lambda: self.now)

    def tearDown(self):
        self.worker.shutdown(2)
        self.assertFalse(self.worker.thread_alive)

    def _check_failed_start_clean(self, worker):
        self.assertTrue(worker._cancel.is_set())
        self.assertIsNone(worker._thread)
        self.assertIsNone(worker._clock)
        self.assertFalse(worker.active)
        self.assertFalse(worker.thread_alive)
        self.assertEqual(worker.blocked_occurrences(), ())
        self.assertEqual(worker._pending_stop_callers, 0)

    def test_oserror_during_native_thread_start_is_fail_closed(self):
        with patch("login_schedule_worker.threading.Thread.start",
                   side_effect=OSError(11, "S50_FAKE_NATIVE_THREAD_RESOURCE")):
            self.assertFalse(self.worker.start())
        self.assertEqual(self.worker.status, "BLOCKED_THREAD")
        self._check_failed_start_clean(self.worker)

    def test_permissionerror_during_native_thread_start_is_fail_closed(self):
        with patch("login_schedule_worker.threading.Thread.start",
                   side_effect=PermissionError(13, "S50_FAKE_START_DENIED")):
            self.assertFalse(self.worker.start())
        self.assertEqual(self.worker.status, "BLOCKED_THREAD")
        self._check_failed_start_clean(self.worker)

    def test_existing_runtimeerror_branch_still_fails_closed(self):
        with patch("login_schedule_worker.threading.Thread.start",
                   side_effect=RuntimeError("S50_FAKE_START_RUNTIME")):
            self.assertFalse(self.worker.start())
        self.assertEqual(self.worker.status, "BLOCKED_THREAD")
        self._check_failed_start_clean(self.worker)

    def test_explicit_retry_after_native_oserror_really_starts_worker(self):
        with patch("login_schedule_worker.threading.Thread.start",
                   side_effect=OSError("S50_TEST_RESOURCE_ERROR")):
            self.assertFalse(self.worker.start())
        self._check_failed_start_clean(self.worker)
        self.assertTrue(self.worker.start())
        self.assertTrue(self.worker.thread_alive)
        self.assertTrue(self.worker.stop(2))
        self.assertFalse(self.worker._stop_requested.is_set())

    def test_real_worker_still_uses_twenty_second_wait(self):
        self.assertTrue(self.worker.start())
        t0 = time.monotonic()
        self.assertTrue(self.worker.stop(2))
        self.assertLess(time.monotonic()-t0, 0.5)

    def test_clock_failure_branch_preserves_existing_behavior(self):
        def bad_time():
            raise ValueError("S50_CLOCK_ERROR")
        self.worker._now = bad_time
        self.assertFalse(self.worker.start())
        self.assertEqual(self.worker.status, "BLOCKED_CLOCK")
        self.assertFalse(self.worker.thread_alive)
        self.assertTrue(self.worker._cancel.is_set())

    def test_tk_preview_rolls_back_on_oserror_without_fake_activation(self):
        label = FakeLabel()
        with patch("tkinter.Label", FakeLabel):
            life = F09ReadOnlyTabLifetime(
                label, self.settings, now=lambda: self.now)
        with patch("login_schedule_worker.threading.Thread.start",
                   side_effect=OSError("S50_TEST_THREAD_UNAVAILABLE")):
            self.assertFalse(life.start_preview_and_evaluation())
        self.assertEqual(life.status, "BLOCKED_WORKER")
        self.assertFalse(life.preview.active)
        self.assertFalse(life.worker.active)
        self.assertEqual(life.worker.status, "BLOCKED_THREAD")
        self._check_failed_start_clean(life.worker)
        self.assertTrue(life.close())
        self.assertTrue(life.finish_close(2))

    def test_permanent_shutdown_during_start_oserror_preserves_closed(self):
        def shutdown_then_fail():
            self.worker.request_shutdown()
            raise OSError("S50_NATIVE_START_FAILURE_AFTER_CLOSE")
        with patch("login_schedule_worker.threading.Thread.start",
                   side_effect=shutdown_then_fail):
            self.assertFalse(self.worker.start())
        self.assertTrue(self.worker._closed)
        self.assertEqual(self.worker.status, "CLOSED")
        self.assertTrue(self.worker._stop_requested.is_set())
        self._check_failed_start_clean(self.worker)
        self.assertFalse(self.worker.start())

    def test_no_due_event_after_failed_native_start(self):
        with patch("login_schedule_worker.threading.Thread.start",
                   side_effect=OSError("S50_NO_THREAD")):
            self.assertFalse(self.worker.start())
        self.now = datetime(2026, 10, 9, 4, 21)
        self.assertEqual(self.worker.poll_once(), ())
        self.assertEqual(self.worker.blocked_occurrences(), ())

    def test_tk_label_destroy_after_failed_native_start_is_nonblocking(self):
        label = FakeLabel()
        with patch("tkinter.Label", FakeLabel):
            life = F09ReadOnlyTabLifetime(
                label, self.settings, now=lambda: self.now)
        with patch("login_schedule_worker.threading.Thread.start",
                   side_effect=OSError("S50_TEST_UNAVAILABLE")):
            self.assertFalse(life.start_preview_and_evaluation())
        label.exists = False
        began = time.monotonic()
        for callback in label._bindings["<Destroy>"]:
            callback(SimpleNamespace(widget=label))
        self.assertLess(time.monotonic()-began, .25)
        self.assertTrue(life.closed)
        self.assertTrue(life.finish_close(2))

    def test_native_start_exception_does_not_modify_readonly_inputs(self):
        original = (
            self.settings.status, self.settings.close_hhmm,
            self.settings.open_hhmm, self.settings.schedule_on_raw,
            self.settings.shutdown_after_close_raw)
        with patch("login_schedule_worker.threading.Thread.start",
                   side_effect=OSError("S50_TEST_NO_IO")):
            self.assertFalse(self.worker.start())
        self.assertEqual(original, (
            self.settings.status, self.settings.close_hhmm,
            self.settings.open_hhmm, self.settings.schedule_on_raw,
            self.settings.shutdown_after_close_raw))

    def test_no_proxy_real_game_or_poweroff_dispatch(self):
        source = (ROOT/"src/login_schedule_worker.py").read_text("utf-8")
        for banned in ("write_settings(", "_open_game_batch(", "CreateProcessW(",
                       "subprocess.Popen(", "shutdown /s /t 0", "PostMessage("):
            self.assertNotIn(banned, source)


if __name__ == "__main__":
    unittest.main()
