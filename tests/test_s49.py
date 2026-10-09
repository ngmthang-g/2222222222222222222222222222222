"""S49 reproduce/fix S48 cleanup clear versus permanent lock-free shutdown."""
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


class S49PermanentShutdownFenceTests(unittest.TestCase):
    def setUp(self):
        self.when = datetime(2026, 10, 9, 3, 59, 50)
        self.settings = ReadOnlyScheduleSettings(
            "READ_ONLY_VALIDATED", "04:00", "04:20",
            "OPAQUE_SCHEDULE_ON", "OPAQUE_SHUTDOWN")
        self.worker = F09ScheduleEvaluationWorker(
            self.settings, now=lambda: self.when)
        self.to_release = []
        self.threads = []

    def tearDown(self):
        for item in self.to_release:
            item.set()
        for thread in self.threads:
            thread.join(2)
            self.assertFalse(thread.is_alive(), "S49 test thread leak")
        self.worker.shutdown(2)
        self.assertFalse(self.worker.thread_alive)

    def _hold_fence_clear(self, worker):
        entered, release = threading.Event(), threading.Event()
        self.to_release.append(release)
        real_clear = worker._stop_requested.clear
        def paused_clear():
            entered.set()
            if not release.wait(2):
                raise RuntimeError("S49_TEST_CLEAR_WAIT_TIMEOUT")
            real_clear()
        worker._stop_requested.clear = paused_clear
        return entered, release

    def test_lock_free_shutdown_during_clear_keeps_one_way_fence(self):
        self.assertTrue(self.worker.start())
        entered, release = self._hold_fence_clear(self.worker)
        results = []
        thread = threading.Thread(
            target=lambda: results.append(self.worker.stop(2)), daemon=True)
        self.threads.append(thread)
        thread.start()
        self.assertTrue(entered.wait(1), "stop never reached S48 clear")
        t0 = time.monotonic()
        self.worker.request_shutdown()
        self.assertLess(time.monotonic() - t0, .25)
        self.assertTrue(self.worker._closed)
        self.assertTrue(self.worker._cancel.is_set())
        release.set()
        thread.join(2)
        self.assertEqual(results, [True])
        self.assertEqual(self.worker._pending_stop_callers, 0)
        self.assertTrue(self.worker._stop_requested.is_set(),
                        "S48 incorrectly cleared the permanent shutdown fence")
        self.assertEqual(self.worker.status, "STOPPED")
        # S49 only concerns fence correctness; a pre-shutdown stop may
        # legitimately have written STOPPED before lock-free close arrived.
        self.assertFalse(self.worker.start())
        self.assertTrue(self.worker.shutdown(2))
        self.assertEqual(self.worker.status, "CLOSED")

    def test_closed_before_successful_cleanup_never_calls_clear(self):
        self.assertTrue(self.worker.start())
        self.worker.request_shutdown()
        with patch.object(self.worker._stop_requested, "clear",
                          side_effect=AssertionError("S49_CLEAR_AFTER_CLOSED")):
            self.assertTrue(self.worker.stop(2))
        self.assertTrue(self.worker._stop_requested.is_set())

    def test_normal_stop_still_clears_fence_to_allow_explicit_restart(self):
        self.assertTrue(self.worker.start())
        self.assertTrue(self.worker.stop(2))
        self.assertFalse(self.worker._stop_requested.is_set())
        self.assertTrue(self.worker.start())
        self.assertTrue(self.worker.stop(2))

    def test_shutdown_after_successful_clear_sets_fence(self):
        self.assertTrue(self.worker.start())
        self.assertTrue(self.worker.stop(2))
        self.assertFalse(self.worker._stop_requested.is_set())
        self.worker.request_shutdown()
        self.assertTrue(self.worker._stop_requested.is_set())
        self.assertFalse(self.worker.start())

    def test_two_stop_callers_and_shutdown_cannot_reenable(self):
        self.assertTrue(self.worker.start())
        self.worker._lifecycle_lock.acquire()
        try:
            self.assertFalse(self.worker.stop(0))
            self.worker.request_shutdown()
        finally:
            self.worker._lifecycle_lock.release()
        self.assertTrue(self.worker.stop(2))
        self.assertEqual(self.worker._pending_stop_callers, 0)
        self.assertTrue(self.worker._stop_requested.is_set())
        self.assertFalse(self.worker.start())

    def test_fake_tk_label_destroy_during_stop_clear_never_hangs(self):
        label = FakeLabel()
        with patch("tkinter.Label", FakeLabel):
            life = F09ReadOnlyTabLifetime(
                label, self.settings, now=lambda: self.when)
        self.assertTrue(life.start_preview_and_evaluation())
        entered, release = self._hold_fence_clear(life.worker)
        result = []
        thread = threading.Thread(
            target=lambda: result.append(life.worker.stop(2)), daemon=True)
        self.threads.append(thread)
        thread.start()
        self.assertTrue(entered.wait(1))
        began = time.monotonic()
        label.exists = False
        for callback in label._bindings["<Destroy>"]:
            callback(SimpleNamespace(widget=label))
        self.assertLess(time.monotonic()-began, .25)
        self.assertTrue(life.closed)
        self.assertTrue(life.worker._cancel.is_set())
        release.set()
        thread.join(2)
        self.assertEqual(result, [True])
        self.assertTrue(life.worker._stop_requested.is_set())
        self.assertFalse(life.start_preview_and_evaluation())
        self.assertTrue(life.finish_close(2))
        self.assertFalse(life.worker.thread_alive)

    def test_no_game_action_even_after_due_and_shutdown(self):
        self.assertTrue(self.worker.start())
        self.when = datetime(2026, 10, 9, 4, 21)
        events = self.worker.poll_once()
        self.assertEqual([e.kind for e in events], ["close", "open"])
        self.assertTrue(all(e.status == "BLOCKED_ACTION_UNAVAILABLE"
                            for e in events))
        self.worker.request_shutdown()
        self.assertEqual(self.worker.poll_once(), ())
        self.assertTrue(self.worker.stop(2))
        self.assertFalse(self.worker.start())

    def test_invalid_stop_timeouts_never_change_fence(self):
        for invalid in (-1, 31, None, True, "0"):
            with self.subTest(value=str(invalid)), self.assertRaises(ValueError):
                self.worker.stop(invalid)
        self.assertFalse(self.worker._stop_requested.is_set())
        self.assertEqual(self.worker._pending_stop_callers, 0)

    def test_scope_excludes_credentials_proxy_and_poweroff(self):
        source = (ROOT / "src/login_schedule_worker.py").read_text("utf-8")
        for forbidden in ("write_settings(", "_open_game_batch(",
                          "CreateProcessW(", "subprocess.Popen(",
                          "shutdown /s /t 0", "PostMessage("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
