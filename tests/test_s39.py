"""S39 deterministic F09 clock from original compiled scheduler evidence."""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from login_schedule_clock import (
    DEFAULT_CLOSE, DEFAULT_OPEN, EVENT_CLOSE, EVENT_OPEN,
    WORKER_CHECK_SECONDS, COUNTDOWN_REFRESH_SECONDS,
    LoginScheduleClock, next_occurrence, parse_hhmm, format_remaining,
)


class S39SchedulerTests(unittest.TestCase):
    def t(self, day, hour, minute, second=0):
        return datetime(2026, 10, day, hour, minute, second)

    def test_original_locked_defaults(self):
        self.assertEqual((DEFAULT_CLOSE, DEFAULT_OPEN), ("04:00", "04:20"))
        self.assertEqual(WORKER_CHECK_SECONDS, 20)
        self.assertEqual(COUNTDOWN_REFRESH_SECONDS, 1)

    def test_hhmm_24_hour_boundary(self):
        self.assertEqual(parse_hhmm("00:00"), (0, 0))
        self.assertEqual(parse_hhmm("23:59"), (23, 59))

    def test_invalid_hhmm_rejected_not_silently_fixed(self):
        for v in ("24:00", "04:60", "4:00", "4:0", "04:0", "04:00 ",
                  " 04:00", "04-00", "a4:00", "04:०0", "", None, 420):
            with self.subTest(v=v), self.assertRaises(ValueError):
                parse_hhmm(v)

    def test_future_same_day(self):
        self.assertEqual(next_occurrence(self.t(9, 3, 0), "04:20"), self.t(9, 4, 20))

    def test_time_already_passed_waits_tomorrow(self):
        self.assertEqual(next_occurrence(self.t(9, 15, 0), "04:20"),
                         self.t(10, 4, 20))

    def test_equality_does_not_catch_up(self):
        self.assertEqual(next_occurrence(self.t(9, 4, 20), "04:20"),
                         self.t(10, 4, 20))

    def test_midnight_rollover(self):
        self.assertEqual(next_occurrence(self.t(9, 23, 59, 59), "00:00"),
                         self.t(10, 0, 0))

    def test_wrong_now_refused(self):
        with self.assertRaises(TypeError):
            next_occurrence("2026-10-09", "04:00")

    def test_initially_disabled_has_no_events(self):
        c = LoginScheduleClock()
        self.assertFalse(c.enabled)
        self.assertEqual(c.upcoming(), ())
        self.assertEqual(c.poll(self.t(9, 4, 22)), ())
        self.assertEqual(c.countdown(self.t(9, 4, 22)), "")

    def test_arm_after_old_schedule_no_instant_fire(self):
        c = LoginScheduleClock()
        c.enable(self.t(9, 15, 0))
        self.assertTrue(c.enabled)
        self.assertEqual(c.poll(self.t(9, 15, 0)), ())
        self.assertEqual([e.planned_time for e in c.upcoming()],
                         [self.t(10, 4, 0), self.t(10, 4, 20)])

    def test_worker_20s_poll_emits_close_only(self):
        c = LoginScheduleClock()
        c.enable(self.t(9, 3, 59, 50))
        self.assertEqual(c.poll(self.t(9, 4, 0, 10))[0].kind, EVENT_CLOSE)
        self.assertEqual(c.upcoming()[0].kind, EVENT_OPEN)

    def test_both_due_in_order_even_with_inverted_wall_times(self):
        c = LoginScheduleClock(close_hhmm="04:20", open_hhmm="04:00")
        c.enable(self.t(9, 3, 59, 50))
        due = c.poll(self.t(9, 4, 21))
        self.assertEqual([e.kind for e in due], [EVENT_OPEN, EVENT_CLOSE])

    def test_events_advance_one_day_and_do_not_repeat(self):
        c = LoginScheduleClock()
        c.enable(self.t(9, 3, 59))
        due = c.poll(self.t(9, 4, 21))
        self.assertEqual([x.kind for x in due], [EVENT_CLOSE, EVENT_OPEN])
        self.assertEqual(c.poll(self.t(9, 4, 21)), ())
        self.assertEqual({e.planned_time.date() for e in c.upcoming()},
                         {self.t(10, 4, 0).date()})

    def test_same_time_closing_order_is_documented_local_choice(self):
        c = LoginScheduleClock(close_hhmm="04:00", open_hhmm="04:00")
        c.enable(self.t(9, 3, 59))
        self.assertEqual([x.kind for x in c.poll(self.t(9, 4, 0))],
                         [EVENT_CLOSE, EVENT_OPEN])

    def test_disable_does_not_run_any_action(self):
        c = LoginScheduleClock()
        c.enable(self.t(9, 3, 0))
        c.disable()
        self.assertEqual(c.poll(self.t(9, 5, 0)), ())
        self.assertEqual(c.upcoming(), ())
        self.assertEqual(c.countdown(self.t(9, 5, 0)), "")

    def test_re_enable_rearms_for_future_and_no_catchup(self):
        c = LoginScheduleClock()
        c.enable(self.t(9, 3, 0))
        c.disable()
        c.enable(self.t(9, 15, 0))
        self.assertEqual(c.poll(self.t(9, 15, 0)), ())
        self.assertTrue(all(e.planned_time.day == 10 for e in c.upcoming()))

    def test_countdown_matches_f09_examples(self):
        expected = {45: "45s", 930: "15p30s", 7500: "2h05p", 93600: "1d2h00p"}
        for n, label in expected.items():
            self.assertEqual(format_remaining(n), label)
        self.assertEqual(format_remaining(93700), "1d2h01p")

    def test_negative_duration_refused(self):
        for value in (-1, -30, 1.5, None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                format_remaining(value)

    def test_f09_countdown_contains_both_absolute_dates(self):
        c = LoginScheduleClock()
        now = self.t(9, 3, 59)
        c.enable(now)
        s = c.countdown(now)
        self.assertIn("Tắt 04:00 09/10 còn", s)
        self.assertIn(" | Mở 04:20 09/10 còn", s)

    def test_no_duplicate_catchup_after_multi_day_sleep(self):
        c = LoginScheduleClock()
        c.enable(self.t(9, 3, 59))
        later = datetime(2026, 10, 15, 4, 21)
        x = c.poll(later)
        self.assertEqual(len(x), 2)
        self.assertEqual(c.poll(later), ())
        self.assertTrue(all(event.planned_time > later for event in c.upcoming()))

    def test_clock_rollback_fails_closed(self):
        c = LoginScheduleClock()
        c.enable(self.t(9, 3, 59))
        with self.assertRaisesRegex(ValueError, "BACKWARD"):
            c.poll(self.t(9, 3, 58))
        self.assertFalse(c.enabled)

    def test_no_executable_actions_or_fake_scheduler_ui(self):
        text = Path(sys.modules["login_schedule_clock"].__file__).read_text(encoding="utf-8")
        for forbidden in ("subprocess", "os.system", "shutdown /s", "write_settings(",
                          "SendMessage", "PostMessage", "after(", "tkinter",
                          "_open_game_batch("):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
