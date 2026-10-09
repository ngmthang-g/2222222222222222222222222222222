"""S42 F09 genuine background evaluation + strict NEVER dispatch game actions."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys
import threading
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from login_schedule_clock import EVENT_CLOSE, EVENT_OPEN, WORKER_CHECK_SECONDS
from login_schedule_settings import ReadOnlyScheduleSettings
from login_schedule_worker import (
    AUDIT_CAP, BLOCKED_ACTION, BlockedScheduleOccurrence,
    F09ScheduleEvaluationWorker,
)


class S42BackgroundWorkerTests(unittest.TestCase):
    def setUp(self):
        self.current = [datetime(2026, 10, 9, 3, 59, 50)]
        self.settings = ReadOnlyScheduleSettings(
            "READ_ONLY_VALIDATED", "04:00", "04:20", "UNVERIFIED_TRUE", "UNVERIFIED_SHUTDOWN")
        self.worker = F09ScheduleEvaluationWorker(
            self.settings, now=lambda: self.current[0])

    def tearDown(self):
        self.worker.shutdown()
        self.assertFalse(self.worker.thread_alive)

    def test_exact_original_20_second_wait_and_no_real_actions(self):
        self.assertEqual(WORKER_CHECK_SECONDS, 20)
        self.assertEqual(AUDIT_CAP, 64)
        self.assertEqual(BLOCKED_ACTION, "BLOCKED_ACTION_UNAVAILABLE")

    def test_constructor_never_auto_starts_on_raw_truthy_flag(self):
        self.assertFalse(self.worker.active)
        self.assertFalse(self.worker.thread_alive)
        self.assertEqual(self.worker.status, "IDLE")

    def test_constructor_rejects_unvalidated_input(self):
        with self.assertRaises(TypeError):
            F09ScheduleEvaluationWorker(object())
        with self.assertRaises(TypeError):
            F09ScheduleEvaluationWorker(self.settings, now="not_callable")

    def test_explicit_start_real_daemon_thread_waiting_on_20s(self):
        self.assertTrue(self.worker.start())
        self.assertTrue(self.worker.thread_alive)
        self.assertTrue(self.worker.active)
        self.assertEqual(self.worker.status, "EVALUATING_ONLY_NO_ACTIONS")
        self.assertEqual(self.worker.ticks, 0)

    def test_enabling_after_time_passed_does_not_catchup(self):
        self.current[0] = datetime(2026, 10, 9, 15, 0)
        self.assertTrue(self.worker.start())
        self.assertEqual(self.worker.poll_once(), ())
        self.assertEqual(self.worker.blocked_occurrences(), ())

    def test_no_immediate_event_on_start(self):
        self.assertTrue(self.worker.start())
        self.assertEqual(self.worker.blocked_occurrences(), ())
        self.assertEqual(self.worker.ticks, 0)

    def test_manual_evaluation_emits_close_blocked_but_doesnt_close_game(self):
        self.worker.start()
        self.current[0] = datetime(2026, 10, 9, 4, 0, 10)
        result = self.worker.poll_once()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].kind, EVENT_CLOSE)
        self.assertEqual(result[0].planned_time, datetime(2026, 10, 9, 4))
        self.assertEqual(result[0].status, BLOCKED_ACTION)

    def test_open_occurrence_is_blocked_too(self):
        self.worker.start()
        self.current[0] = datetime(2026, 10, 9, 4, 20, 10)
        result = self.worker.poll_once()
        self.assertEqual([item.kind for item in result], [EVENT_CLOSE, EVENT_OPEN])
        self.assertTrue(all(item.status == BLOCKED_ACTION for item in result))

    def test_due_event_not_reported_twice(self):
        self.worker.start()
        self.current[0] = datetime(2026, 10, 9, 4, 20, 10)
        one = self.worker.poll_once()
        two = self.worker.poll_once()
        self.assertEqual(len(one), 2)
        self.assertEqual(two, ())
        self.assertEqual(len(self.worker.blocked_occurrences()), 2)

    def test_events_recur_on_next_calendar_day(self):
        self.worker.start()
        self.current[0] = datetime(2026, 10, 9, 4, 21)
        self.assertEqual(len(self.worker.poll_once()), 2)
        self.current[0] = datetime(2026, 10, 10, 4, 21)
        self.assertEqual(len(self.worker.poll_once()), 2)
        self.assertEqual(len(self.worker.blocked_occurrences()), 4)

    def test_event_order_follows_wall_clock_inverted_schedule(self):
        custom = ReadOnlyScheduleSettings(
            "READ_ONLY_VALIDATED", "04:20", "04:00")
        self.worker.shutdown()
        self.worker = F09ScheduleEvaluationWorker(custom, now=lambda: self.current[0])
        self.worker.start()
        self.current[0] = datetime(2026, 10, 9, 4, 21)
        self.assertEqual([item.kind for item in self.worker.poll_once()],
                         [EVENT_OPEN, EVENT_CLOSE])

    def test_worker_without_callbacks_never_executes_os_game_shutdown(self):
        self.worker.start()
        self.current[0] = datetime(2026, 10, 9, 4, 21)
        self.assertEqual(len(self.worker.poll_once()), 2)
        self.assertEqual(self.worker.status, "EVALUATING_ONLY_NO_ACTIONS")

    def test_worker_is_independent_from_persisted_shutdown_toggle(self):
        custom = ReadOnlyScheduleSettings(
            "READ_ONLY_VALIDATED", "04:00", "04:20", "1", "True")
        self.worker.shutdown()
        self.worker = F09ScheduleEvaluationWorker(custom, now=lambda: self.current[0])
        self.assertFalse(self.worker.active)
        self.worker.start()
        self.current[0] = datetime(2026, 10, 9, 4, 21)
        self.assertTrue(all(i.status == BLOCKED_ACTION for i in self.worker.poll_once()))

    def test_bad_schedule_blocks_thread_start(self):
        self.worker.shutdown()
        self.worker = F09ScheduleEvaluationWorker(ReadOnlyScheduleSettings("BLOCKED_TIME_FORMAT"))
        self.assertFalse(self.worker.start())
        self.assertFalse(self.worker.thread_alive)
        self.assertEqual(self.worker.status, "BLOCKED_SETTINGS")

    def test_bad_time_source_during_start_doesnt_spawn(self):
        self.worker.shutdown()
        self.worker = F09ScheduleEvaluationWorker(self.settings, now=lambda: "SECRET")
        self.assertFalse(self.worker.start())
        self.assertEqual(self.worker.status, "BLOCKED_CLOCK")
        self.assertFalse(self.worker.thread_alive)

    def test_corrupt_clock_during_poll_fails_closed(self):
        self.worker.start()
        self.current[0] = "BAD_CLOCK"
        self.assertEqual(self.worker.poll_once(), ())
        self.assertEqual(self.worker.status, "BLOCKED_CLOCK")
        self.assertFalse(self.worker.active)

    def test_wall_clock_rollback_fails_closed(self):
        self.worker.start()
        self.current[0] = datetime(2026, 10, 9, 3, 58)
        self.assertEqual(self.worker.poll_once(), ())
        self.assertEqual(self.worker.status, "BLOCKED_CLOCK")
        self.assertFalse(self.worker.active)

    def test_stop_interrupts_actual_long_wait_without_twenty_second_delay(self):
        self.worker.start()
        started = time.monotonic()
        self.assertTrue(self.worker.stop())
        self.assertLess(time.monotonic() - started, 2)
        self.assertFalse(self.worker.thread_alive)
        self.assertEqual(self.worker.status, "STOPPED")

    def test_stop_then_poll_does_not_emit(self):
        self.worker.start()
        self.assertTrue(self.worker.stop())
        self.current[0] = datetime(2026, 10, 9, 4, 21)
        self.assertEqual(self.worker.poll_once(), ())
        self.assertEqual(self.worker.blocked_occurrences(), ())

    def test_stop_twice_and_shutdown_twice(self):
        self.worker.start()
        self.assertTrue(self.worker.stop())
        self.assertTrue(self.worker.stop())
        self.assertTrue(self.worker.shutdown())
        self.assertTrue(self.worker.shutdown())
        self.assertEqual(self.worker.status, "CLOSED")

    def test_restart_only_after_worker_has_stopped(self):
        self.assertTrue(self.worker.start())
        self.assertFalse(self.worker.start())
        self.assertTrue(self.worker.stop())
        self.current[0] = datetime(2026, 10, 9, 15, 0)
        self.assertTrue(self.worker.start())
        self.assertEqual(self.worker.poll_once(), ())
        self.assertEqual(self.worker.blocked_occurrences(), ())

    def test_shutdown_permanently_denies_restart(self):
        self.worker.start()
        self.assertTrue(self.worker.shutdown())
        self.assertFalse(self.worker.start())
        self.assertFalse(self.worker.thread_alive)

    def test_invalid_stop_timeout_rejected(self):
        for value in (-1, 31, "2", None, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.worker.stop(timeout=value)

    def test_worker_passes_exact_20_to_event_wait(self):
        args = []
        triggered = threading.Event()
        actual = self.worker._cancel.wait

        def accelerated_wait(timeout):
            args.append(timeout)
            triggered.set()
            return actual(0.01)

        self.worker._cancel.wait = accelerated_wait
        self.assertTrue(self.worker.start())
        self.assertTrue(triggered.wait(2))
        self.assertTrue(self.worker.stop())
        self.assertGreaterEqual(len(args), 1)
        self.assertTrue(all(x == 20 for x in args))
        self.assertGreaterEqual(self.worker.ticks, 0)

    def test_worker_real_thread_updates_blocked_audit_without_actions(self):
        # The test accelerates real wait but does not alter production logic.
        original = self.worker._cancel.wait
        observed = threading.Event()
        self.current[0] = datetime(2026, 10, 9, 3, 59, 50)

        def accelerated_wait(timeout):
            result = original(0.02)
            observed.set()
            return result

        self.worker._cancel.wait = accelerated_wait
        self.assertTrue(self.worker.start())
        self.current[0] = datetime(2026, 10, 9, 4, 20, 10)
        deadline = time.monotonic() + 2
        while self.worker.ticks == 0 and time.monotonic() < deadline:
            time.sleep(0.005)
        events = self.worker.blocked_occurrences()
        self.assertEqual(len(events), 2)
        self.assertEqual([e.kind for e in events], [EVENT_CLOSE, EVENT_OPEN])
        self.assertTrue(self.worker.stop())

    def test_audit_cap_prevents_unbounded_growth(self):
        self.worker.start()
        for day in range(1, 49):
            self.current[0] = datetime(2026, 10, 9, 4, 21) + __import__("datetime").timedelta(days=day)
            self.worker.poll_once()
        self.assertEqual(len(self.worker.blocked_occurrences()), AUDIT_CAP)
        self.assertTrue(all(e.status == BLOCKED_ACTION for e in self.worker.blocked_occurrences()))

    def test_event_snapshot_is_tuple_with_immutable_records(self):
        self.worker.start()
        self.current[0] = datetime(2026, 10, 9, 4, 21)
        self.worker.poll_once()
        events = self.worker.blocked_occurrences()
        self.assertIsInstance(events, tuple)
        with self.assertRaises(Exception):
            events[0].kind = "open"

    def test_no_usernames_or_settings_values_appear_in_audit(self):
        self.worker.start()
        self.current[0] = datetime(2026, 10, 9, 4, 21)
        a = repr(self.worker.poll_once())
        self.assertNotIn("UNVERIFIED_TRUE", a)
        self.assertNotIn("UNVERIFIED_SHUTDOWN", a)

    def test_source_has_no_execution_or_config_write(self):
        src = Path(sys.modules["login_schedule_worker"].__file__).read_text(encoding="utf-8")
        for item in ("write_settings(", "subprocess.Popen(", "subprocess.run(",
                     "os.system(", "CreateProcessW(", "PostMessage(",
                     "spawn_and_inject(", "_open_game_batch(",
                     "_force_close_window(", "shutdown /s /t 0", "Tk("):
            self.assertNotIn(item, src)


if __name__ == "__main__":
    unittest.main()
