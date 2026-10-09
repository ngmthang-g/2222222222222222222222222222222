"""S43 reproduce and fix S42 scheduler lifecycle races, no game actions."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys
import threading
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from login_schedule_settings import ReadOnlyScheduleSettings
from login_schedule_worker import (
    BLOCKED_ACTION, F09ScheduleEvaluationWorker,
)


class S43WorkerConcurrencyTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 9, 3, 59, 50)
        self.settings = ReadOnlyScheduleSettings(
            "READ_ONLY_VALIDATED", "04:00", "04:20", "UNVERIFIED", "UNKNOWN_PC")
        self.worker = F09ScheduleEvaluationWorker(self.settings, now=lambda: self.now)
        self.release: threading.Event | None = None

    def tearDown(self):
        if self.release is not None:
            self.release.set()
        self.assertTrue(self.worker.shutdown(timeout=2))
        self.assertFalse(self.worker.thread_alive)

    def _pause_stop_after_join(self):
        """Deterministic interleaving: stop joined OLD thread, not cleaned yet."""
        self.assertTrue(self.worker.start())
        thread = self.worker._thread
        joined = threading.Event()
        resume = threading.Event()
        real_join = thread.join

        def paused_join(timeout=None):
            real_join(timeout)
            joined.set()
            if not resume.wait(3):
                raise RuntimeError("TEST_STOP_PAUSE_TIMED_OUT")

        thread.join = paused_join
        stopped: list[object] = []

        def do_stop():
            try:
                stopped.append(self.worker.stop())
            except BaseException as exc:
                stopped.append(type(exc).__name__)

        caller = threading.Thread(target=do_stop, daemon=True)
        caller.start()
        self.assertTrue(joined.wait(2), "real worker did not join")
        return caller, joined, resume, stopped

    def test_old_thread_join_cleanup_prevents_new_start(self):
        caller, joined, resume, result = self._pause_stop_after_join()
        try:
            self.assertFalse(self.worker.start())
            self.assertFalse(self.worker.active)
        finally:
            resume.set()
            caller.join(2)
        self.assertFalse(caller.is_alive())
        self.assertEqual(result, [True])
        self.assertFalse(self.worker.thread_alive)
        self.assertEqual(self.worker.status, "STOPPED")

    def test_restart_after_complete_stop_is_still_allowed(self):
        caller, _, resume, result = self._pause_stop_after_join()
        resume.set()
        caller.join(2)
        self.assertEqual(result, [True])
        self.assertTrue(self.worker.start())
        self.assertEqual(self.worker.status, "EVALUATING_ONLY_NO_ACTIONS")
        self.assertTrue(self.worker.stop())

    def test_no_worker_actions_were_dispatched_during_overlap(self):
        caller, _, resume, result = self._pause_stop_after_join()
        try:
            self.assertFalse(self.worker.start())
            self.assertEqual(self.worker.blocked_occurrences(), ())
        finally:
            resume.set()
            caller.join(2)
        self.assertEqual(result, [True])

    def _block_in_clock(self):
        """The real worker holds _lock inside poll_once while now() stalls."""
        release = threading.Event()
        entered = threading.Event()
        self.release = release
        first = [True]

        def blocking_now():
            if first[0]:
                first[0] = False
                return datetime(2026, 10, 9, 3, 59, 50)
            entered.set()
            if not release.wait(3):
                raise RuntimeError("TEST_CLOCK_BLOCK_TIMEOUT")
            return datetime(2026, 10, 9, 4, 20, 10)

        self.worker = F09ScheduleEvaluationWorker(self.settings, now=blocking_now)
        real_wait = self.worker._cancel.wait

        def accelerated_wait(timeout):
            return real_wait(0.01)
        self.worker._cancel.wait = accelerated_wait
        self.assertTrue(self.worker.start())
        self.assertTrue(entered.wait(2), "clock callback was not entered")
        return release

    def test_hung_clock_does_not_make_stop_timeout_unbounded(self):
        release = self._block_in_clock()
        start = time.monotonic()
        result = self.worker.stop(timeout=0.02)
        elapsed = time.monotonic() - start
        self.assertFalse(result)
        self.assertLess(elapsed, 0.4)
        self.assertEqual(self.worker._status, "STOPPING")
        self.assertTrue(self.worker.thread_alive)
        release.set()
        self.assertTrue(self.worker.stop(timeout=2))

    def test_while_clock_hung_restart_is_refused(self):
        release = self._block_in_clock()
        self.assertFalse(self.worker.stop(timeout=0.01))
        self.assertFalse(self.worker.start())
        release.set()
        self.assertTrue(self.worker.stop())
        self.assertTrue(self.worker.start())
        self.assertTrue(self.worker.stop())

    def test_pending_stop_keeps_events_blocked_even_after_clock_unblocks(self):
        release = self._block_in_clock()
        self.assertFalse(self.worker.stop(timeout=0.01))
        release.set()
        self.assertTrue(self.worker.stop())
        self.assertEqual(self.worker.blocked_occurrences(), ())
        self.assertFalse(self.worker.active)

    def test_bad_clock_does_not_leak_opaque_flag_values(self):
        release = self._block_in_clock()
        self.assertFalse(self.worker.stop(timeout=0.01))
        release.set()
        self.assertTrue(self.worker.stop())
        self.assertNotIn("UNVERIFIED", str(self.worker.blocked_occurrences()))

    def test_shutdown_during_stalled_clock_is_permanent(self):
        release = self._block_in_clock()
        start = time.monotonic()
        self.assertFalse(self.worker.shutdown(timeout=0.02))
        self.assertLess(time.monotonic() - start, 0.4)
        self.assertFalse(self.worker.start())
        release.set()
        self.assertTrue(self.worker.shutdown())
        self.assertFalse(self.worker.start())
        self.assertEqual(self.worker.status, "CLOSED")

    def test_stop_request_is_visible_without_clock_lock(self):
        release = self._block_in_clock()
        self.assertFalse(self.worker._cancel.is_set())
        self.assertFalse(self.worker.stop(timeout=0.01))
        self.assertTrue(self.worker._cancel.is_set())
        release.set()
        self.assertTrue(self.worker.stop())

    def test_stop_invalid_timeout_does_not_cancel(self):
        self.assertTrue(self.worker.start())
        with self.assertRaises(ValueError):
            self.worker.stop(-2)
        self.assertFalse(self.worker._cancel.is_set())
        self.assertTrue(self.worker.stop())

    def test_shutdown_then_restart_is_denied(self):
        self.assertTrue(self.worker.start())
        self.assertTrue(self.worker.shutdown())
        self.assertFalse(self.worker.start())
        self.assertEqual(self.worker.status, "CLOSED")

    def test_new_preview_boolean_still_never_auto_arms(self):
        self.assertFalse(self.worker.active)
        self.assertFalse(self.worker.thread_alive)
        self.assertEqual(self.worker.status, "IDLE")

    def test_previous_blocked_due_event_behavior_preserved(self):
        self.assertTrue(self.worker.start())
        self.now = datetime(2026, 10, 9, 4, 21)
        events = self.worker.poll_once()
        self.assertEqual([e.kind for e in events], ["close", "open"])
        self.assertTrue(all(e.status == BLOCKED_ACTION for e in events))
        self.assertEqual(self.worker.poll_once(), ())

    def test_no_execution_or_credentials_written_in_source(self):
        src = Path(sys.modules["login_schedule_worker"].__file__).read_text(encoding="utf-8")
        for forbidden in ("write_settings(", "subprocess.Popen(", "subprocess.run(",
                          "CreateProcessW(", "spawn_and_inject(",
                          "_open_game_batch(", "shutdown /s /t 0"):
            self.assertNotIn(forbidden, src)


if __name__=="__main__":
    unittest.main()
