"""S53 F09 total stop deadline also bounds the final _lock cleanup.

Regression for an INDEPENDENT poll_once holding _lock after the worker itself
has already exited. No original game actions, credentials or Proxy runtime.
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


class S53StopFinalLockDeadlineTests(unittest.TestCase):
    def setUp(self):
        self.when = datetime(2026, 10, 9, 3, 59, 50)
        self.cfg = ReadOnlyScheduleSettings(
            "READ_ONLY_VALIDATED", "04:00", "04:20",
            "OPAQUE_SCHEDULE_FLAG", "OPAQUE_PC_FLAG")
        self.worker = F09ScheduleEvaluationWorker(self.cfg, now=lambda: self.when)
        self.releases = []
        self.threads = []

    def tearDown(self):
        for event in self.releases:
            event.set()
        for thread in self.threads:
            thread.join(2)
            self.assertFalse(thread.is_alive(), "S53 test thread leaked")
        self.assertTrue(self.worker.shutdown(2))
        self.assertFalse(self.worker.thread_alive)

    def _hold_external_poll_clock(self, worker):
        entered, release = threading.Event(), threading.Event()
        self.releases.append(release)
        def blocking_clock():
            entered.set()
            if not release.wait(3):
                raise TimeoutError("S53_TEST_POLL_TIMEOUT")
            return self.when
        worker._now = blocking_clock
        results = []
        problems = []
        def poll():
            try:
                results.append(worker.poll_once())
            except Exception:
                problems.append("POLL_FAILED")
        t = threading.Thread(target=poll, name="S53-held-poll", daemon=True)
        self.threads.append(t)
        t.start()
        self.assertTrue(entered.wait(1), "independent poll did not take _lock")
        return t, results, problems, release

    def _bounded_call(self, method, expected_timeout=0.035):
        # A thread is used to avoid hanging the entire unit suite when this
        # red test runs on the pre-fix source.
        ended = threading.Event()
        outcomes = []
        def call():
            try:
                begin = time.monotonic()
                response = method(expected_timeout)
                outcomes.append((response, time.monotonic() - begin))
            except Exception as exc:
                outcomes.append((type(exc).__name__, -1))
            finally:
                ended.set()
        t = threading.Thread(target=call, name="S53-stopper", daemon=True)
        self.threads.append(t)
        t.start()
        return t, ended, outcomes

    def test_external_poll_lock_does_not_overrun_stop_deadline(self):
        self.assertTrue(self.worker.start())
        poll, records, problems, release = self._hold_external_poll_clock(self.worker)
        stopper, ended, outcomes = self._bounded_call(self.worker.stop)
        bounded = ended.wait(.28)
        # Always release even on intentionally red old source: no leaked test.
        release.set()
        stopper.join(2)
        poll.join(2)
        self.assertTrue(bounded, "S52 unbounded with self._lock after join")
        self.assertEqual(len(outcomes), 1)
        self.assertEqual(outcomes[0][0], False)
        self.assertLess(outcomes[0][1], .25)
        self.assertFalse(problems)
        self.assertEqual(records, [()])
        self.assertTrue(self.worker._cancel.is_set())
        self.assertTrue(self.worker._stop_requested.is_set())
        self.assertTrue(self.worker.stop(2))
        self.assertFalse(self.worker._stop_requested.is_set())

    def test_lifetime_finish_close_does_not_overrun_final_lock_deadline(self):
        label = FakeLabel()
        with patch("tkinter.Label", FakeLabel):
            life = F09ReadOnlyTabLifetime(label, self.cfg, now=lambda: self.when)
        self.assertTrue(life.start_preview_and_evaluation())
        poll, records, problems, release = self._hold_external_poll_clock(life.worker)
        began = time.monotonic()
        label.exists = False
        for callback in label._bindings["<Destroy>"]:
            callback(SimpleNamespace(widget=label))
        self.assertLess(time.monotonic() - began, .25)
        self.assertTrue(life.closed)
        stopper, ended, outcomes = self._bounded_call(life.finish_close)
        bounded = ended.wait(.28)
        release.set()
        stopper.join(2)
        poll.join(2)
        self.assertTrue(bounded, "finish_close hung in worker final _lock cleanup")
        self.assertEqual(outcomes[0][0], False)
        self.assertLess(outcomes[0][1], .25)
        self.assertTrue(life.worker._closed)
        self.assertTrue(life.worker._cancel.is_set())
        self.assertFalse(problems)
        self.assertEqual(records, [()])
        self.assertTrue(life.finish_close(2))
        self.assertEqual(life.status, "CLOSED")
        self.assertFalse(life.worker.start())

    def test_shutdown_bounded_even_if_worker_is_already_joined(self):
        self.assertTrue(self.worker.start())
        poll, records, problems, release = self._hold_external_poll_clock(self.worker)
        stopper, ended, outcomes = self._bounded_call(self.worker.shutdown)
        bounded = ended.wait(.28)
        release.set()
        stopper.join(2)
        poll.join(2)
        self.assertTrue(bounded)
        self.assertEqual(outcomes[0][0], False)
        self.assertLess(outcomes[0][1], .25)
        self.assertTrue(self.worker._closed)
        self.assertTrue(self.worker._stop_requested.is_set())
        self.assertTrue(self.worker.shutdown(2))
        self.assertFalse(self.worker.start())

    def test_cleanup_budget_exhaustion_preserves_restart_fence(self):
        self.assertTrue(self.worker.start())
        poll, records, problems, release = self._hold_external_poll_clock(self.worker)
        stopper, ended, outcomes = self._bounded_call(self.worker.stop)
        bounded = ended.wait(.28)
        self.assertTrue(self.worker._cancel.is_set())
        self.assertTrue(self.worker._stop_requested.is_set())
        self.assertFalse(self.worker.start())
        release.set()
        stopper.join(2)
        poll.join(2)
        self.assertTrue(bounded)
        self.assertEqual(outcomes[0][0], False)
        self.assertTrue(self.worker.stop(2))
        self.assertTrue(self.worker.start())
        self.assertTrue(self.worker.stop(2))

    def test_normal_stop_uses_uncontended_final_lock(self):
        self.assertTrue(self.worker.start())
        self.assertTrue(self.worker.stop(2))
        self.assertEqual(self.worker.status, "STOPPED")
        self.assertFalse(self.worker._stop_requested.is_set())
        self.assertTrue(self.worker.start())
        self.assertTrue(self.worker.stop(2))

    def test_idle_zero_budget_stop_remains_successful(self):
        self.assertTrue(self.worker.stop(0))
        self.assertEqual(self.worker.status, "STOPPED")
        self.assertTrue(self.worker.start())
        self.assertTrue(self.worker.stop(2))

    def test_due_audit_stays_blocked_action_only(self):
        self.assertTrue(self.worker.start())
        self.when = datetime(2026, 10, 9, 4, 21)
        events = self.worker.poll_once()
        self.assertEqual([e.kind for e in events], ["close", "open"])
        self.assertTrue(all(e.status == BLOCKED_ACTION for e in events))
        self.assertTrue(self.worker.stop(2))

    def test_invalid_deadlines_do_not_register_stop_callers(self):
        for value in (-1, 31, "1", True, None, float("nan"), float("inf")):
            with self.subTest(value=str(value)), self.assertRaises(ValueError):
                self.worker.stop(value)
        self.assertEqual(self.worker._pending_stop_callers, 0)
        self.assertFalse(self.worker._stop_requested.is_set())

    def test_scope_excludes_actions_proxy_and_ini_write(self):
        source = (ROOT / "src/login_schedule_worker.py").read_text("utf-8")
        for forbidden in ("write_settings(", "subprocess.Popen(",
                          "CreateProcessW(", "shutdown /s /t 0",
                          "_open_game_batch(", "PostMessage("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
