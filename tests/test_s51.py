"""S51 F09 cancellation during due-event materialization must not publish late audits.

Test-owned pure scheduler; unknown flags do not arm real game actions.
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
from login_schedule_worker import (
    F09ScheduleEvaluationWorker, BlockedScheduleOccurrence, BLOCKED_ACTION,
)


class S51PostClockCancelTests(unittest.TestCase):
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
        for event in self.releases:
            event.set()
        for thread in self.threads:
            thread.join(2)
            self.assertFalse(thread.is_alive(), "S51 test poll leaked")
        self.worker.shutdown(2)
        self.assertFalse(self.worker.thread_alive)

    def _pause_materialization(self):
        entered, release = threading.Event(), threading.Event()
        self.releases.append(release)
        def callback(*args, **kwargs):
            entered.set()
            if not release.wait(2):
                raise RuntimeError("S51_TEST_MATERIALIZER_PAUSE")
            return BlockedScheduleOccurrence(*args, **kwargs)
        return entered, release, callback

    def _begin_due_poll(self, worker):
        results, problems = [], []
        thread = threading.Thread(
            target=lambda: (
                results.append(worker.poll_once())
            ), daemon=True, name="S51-poll")
        self.threads.append(thread)
        thread.start()
        return thread, results, problems

    def test_shutdown_mid_occurrence_materialization_discards_late_audit(self):
        self.assertTrue(self.worker.start())
        self.when = datetime(2026, 10, 9, 4, 21)
        entered, release, callback = self._pause_materialization()
        with patch("login_schedule_worker.BlockedScheduleOccurrence",
                   side_effect=callback):
            thread, results, _ = self._begin_due_poll(self.worker)
            self.assertTrue(entered.wait(1))
            started = time.monotonic()
            self.worker.request_shutdown()
            self.assertLess(time.monotonic()-started, .25)
            self.assertTrue(self.worker._cancel.is_set())
            release.set()
            thread.join(2)
        self.assertEqual(results, [()])
        self.assertEqual(self.worker.blocked_occurrences(), ())
        self.assertTrue(self.worker.stop(2))
        self.assertFalse(self.worker.start())

    def test_stop_during_occurrence_materialization_discards_late_audit(self):
        self.assertTrue(self.worker.start())
        self.when = datetime(2026, 10, 9, 4, 21)
        entered, release, callback = self._pause_materialization()
        with patch("login_schedule_worker.BlockedScheduleOccurrence",
                   side_effect=callback):
            thread, results, _ = self._begin_due_poll(self.worker)
            self.assertTrue(entered.wait(1))
            # Force stop(0) to fail before join/_lock (the poll thread
            # deliberately holds _lock until the test releases it).
            self.worker._lifecycle_lock.acquire()
            try:
                self.assertFalse(self.worker.stop(0))
            finally:
                self.worker._lifecycle_lock.release()
            self.assertTrue(self.worker._cancel.is_set())
            release.set()
            thread.join(2)
        self.assertEqual(results, [()])
        self.assertEqual(self.worker.blocked_occurrences(), ())
        self.assertTrue(self.worker.stop(2))

    def test_no_cancel_still_publishes_original_blocked_only_occurrences(self):
        self.assertTrue(self.worker.start())
        self.when = datetime(2026, 10, 9, 4, 21)
        events = self.worker.poll_once()
        self.assertEqual([x.kind for x in events], ["close", "open"])
        self.assertTrue(all(x.status == BLOCKED_ACTION for x in events))
        self.assertEqual(self.worker.blocked_occurrences(), events)
        self.assertEqual(self.worker.poll_once(), ())

    def test_no_stale_audit_during_fake_tk_destroy(self):
        label = FakeLabel()
        with patch("tkinter.Label", FakeLabel):
            life = F09ReadOnlyTabLifetime(
                label, self.cfg, now=lambda: self.when)
        self.assertTrue(life.start_preview_and_evaluation())
        self.when = datetime(2026, 10, 9, 4, 21)
        entered, release, callback = self._pause_materialization()
        with patch("login_schedule_worker.BlockedScheduleOccurrence",
                   side_effect=callback):
            thread, results, _ = self._begin_due_poll(life.worker)
            self.assertTrue(entered.wait(1))
            started = time.monotonic()
            label.exists = False
            for fn in label._bindings["<Destroy>"]:
                fn(SimpleNamespace(widget=label))
            self.assertLess(time.monotonic()-started, .25)
            self.assertTrue(life.closed)
            release.set()
            thread.join(2)
        self.assertEqual(results, [()])
        self.assertEqual(life.worker.blocked_occurrences(), ())
        self.assertTrue(life.finish_close(2))
        self.assertFalse(life.start_preview_and_evaluation())

    def test_cancelled_worker_poll_now_returns_no_events(self):
        self.assertTrue(self.worker.start())
        self.worker.request_shutdown()
        self.when = datetime(2026, 10, 9, 4, 21)
        self.assertEqual(self.worker.poll_once(), ())
        self.assertEqual(self.worker.blocked_occurrences(), ())

    def test_readonly_disabled_settings_never_spawn_worker(self):
        bad = ReadOnlyScheduleSettings("BLOCKED_TIME_FORMAT")
        worker = F09ScheduleEvaluationWorker(bad, now=lambda: self.when)
        self.assertFalse(worker.start())
        self.assertEqual(worker.status, "BLOCKED_SETTINGS")
        self.assertFalse(worker.thread_alive)
        self.assertTrue(worker.shutdown(2))

    def test_explicit_restart_after_normal_stop_remains_available(self):
        self.assertTrue(self.worker.start())
        self.assertTrue(self.worker.stop(2))
        self.assertFalse(self.worker._stop_requested.is_set())
        self.assertTrue(self.worker.start())
        self.assertTrue(self.worker.stop(2))

    def test_due_audit_cap_and_existing_blocked_only_semantics(self):
        self.assertTrue(self.worker.start())
        self.when = datetime(2026, 10, 9, 4, 21)
        self.assertEqual(
            [x.kind for x in self.worker.poll_once()], ["close", "open"])
        self.assertTrue(all(x.status == BLOCKED_ACTION
                            for x in self.worker.blocked_occurrences()))
        self.assertEqual(len(self.worker.blocked_occurrences()), 2)

    def test_scope_excludes_game_proxy_and_persistence(self):
        source = (ROOT/"src/login_schedule_worker.py").read_text("utf-8")
        for prohibited in (
            "write_settings(", "_open_game_batch(", "CreateProcessW(",
            "subprocess.Popen(", "shutdown /s /t 0", "PostMessage("):
            self.assertNotIn(prohibited, source)


if __name__ == "__main__":
    unittest.main()
