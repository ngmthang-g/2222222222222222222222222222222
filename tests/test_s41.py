"""S41 F09 cancellable main-thread Tk preview controller tests (no game)."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from login_schedule_countdown import REFRESH_MS, TkScheduleCountdownPreview
from login_schedule_settings import ReadOnlyScheduleSettings


class FakeLabel:
    def __init__(self):
        self.exists = True
        self.text = "OLDER"
        self.callbacks = {}
        self.cancelled = []
        self.index = 0
        self.last_delay = None
        self.fail_configure = False
        self.fail_after = False

    def configure(self, **kwargs):
        if not self.exists or self.fail_configure:
            raise RuntimeError("FAKE_TK_DESTROYED")
        self.text = kwargs["text"]

    def winfo_exists(self):
        return int(self.exists)

    def after(self, delay, callback):
        if not self.exists or self.fail_after:
            raise RuntimeError("FAKE_AFTER_BLOCKED")
        self.last_delay = delay
        self.index += 1
        ident = str(self.index)
        self.callbacks[ident] = callback
        return ident

    def after_cancel(self, ident):
        self.cancelled.append(ident)
        self.callbacks.pop(ident, None)

    def fire(self, ident):
        self.callbacks.pop(ident)()


class S41CountdownTests(unittest.TestCase):
    def setUp(self):
        self.label = FakeLabel()
        self.clock_time = datetime(2026, 10, 9, 3, 59, 50)
        with patch("tkinter.Label", FakeLabel):
            self.preview = TkScheduleCountdownPreview(
                self.label, now=lambda: self.clock_time)
        self.settings = ReadOnlyScheduleSettings(
            "READ_ONLY_VALIDATED", "04:00", "04:20",
            schedule_on_raw="ANY_OLD_TRUE_UNKNOWN",
            shutdown_after_close_raw="ANY_POWER_TOKEN_UNKNOWN")

    def tearDown(self):
        self.preview.shutdown()

    def test_f09_1000ms_main_thread_cadence(self):
        self.assertEqual(REFRESH_MS, 1000)
        self.assertTrue(self.preview.preview_start(self.settings))
        self.assertEqual(self.label.last_delay, 1000)
        self.assertTrue(self.preview.has_pending_refresh)

    def test_preview_is_inactive_until_explicit_call(self):
        self.assertFalse(self.preview.active)
        self.assertEqual(self.preview.status, "IDLE")
        self.assertEqual(self.label.text, "OLDER")

    def test_start_shows_both_actual_absolute_schedule_times(self):
        self.assertTrue(self.preview.preview_start(self.settings))
        self.assertIn("Tắt 04:00 09/10 còn", self.label.text)
        self.assertIn("Mở 04:20 09/10 còn", self.label.text)
        self.assertEqual(self.preview.last_text, self.label.text)

    def test_no_implicit_start_from_truthy_legacy_bool(self):
        self.assertFalse(self.preview.active)
        self.assertFalse(self.preview.has_pending_refresh)
        self.assertEqual(self.preview.status, "IDLE")

    def test_false_bool_also_never_automatically_starts(self):
        self.settings = ReadOnlyScheduleSettings(
            "READ_ONLY_VALIDATED", "04:00", "04:20", "False", "True")
        self.assertFalse(self.preview.active)

    def test_bad_settings_refuse_no_action(self):
        for status in ("BLOCKED_TIME_FORMAT", "BLOCKED_SETTINGS_READ",
                       "BLOCKED_OPAQUE_TOKEN"):
            with self.subTest(status=status):
                self.assertFalse(self.preview.preview_start(
                    ReadOnlyScheduleSettings(status)))
                self.assertFalse(self.preview.active)
                self.assertEqual(self.label.callbacks, {})

    def test_missing_settings_cannot_start(self):
        self.assertFalse(self.preview.preview_start(None))
        self.assertFalse(self.preview.active)

    def test_defaults_only_preview_is_disarmed_until_explicit_call(self):
        settings = ReadOnlyScheduleSettings("DEFAULTS_ONLY", "04:00", "04:20")
        self.assertFalse(self.preview.active)
        self.assertTrue(self.preview.preview_start(settings))
        self.assertEqual(self.preview.status, "PREVIEW_ONLY")

    def test_second_start_does_not_duplicate_timers(self):
        self.assertTrue(self.preview.preview_start(self.settings))
        before = self.label.index
        self.assertFalse(self.preview.preview_start(self.settings))
        self.assertEqual(self.label.index, before)
        self.assertEqual(len(self.label.callbacks), 1)

    def test_normal_refresh_updates_actual_label(self):
        self.preview.preview_start(self.settings)
        old_id = next(iter(self.label.callbacks))
        old_text = self.label.text
        self.clock_time = datetime(2026, 10, 9, 3, 59, 59)
        self.label.fire(old_id)
        self.assertNotEqual(self.label.text, old_text)
        self.assertEqual(len(self.label.callbacks), 1)

    def test_rollover_keeps_countdown_future_without_dispatch(self):
        self.preview.preview_start(self.settings)
        self.clock_time = datetime(2026, 10, 9, 4, 0, 1)
        old_id = next(iter(self.label.callbacks))
        self.label.fire(old_id)
        self.assertIn("Tắt 04:00 10/10 còn", self.label.text)
        self.assertIn("Mở 04:20 09/10 còn", self.label.text)

    def test_stop_cancels_actual_pending_after(self):
        self.preview.preview_start(self.settings)
        ident = next(iter(self.label.callbacks))
        self.preview.stop()
        self.assertIn(ident, self.label.cancelled)
        self.assertEqual(self.label.callbacks, {})
        self.assertEqual(self.label.text, "")
        self.assertFalse(self.preview.has_pending_refresh)
        self.assertFalse(self.preview.active)
        self.assertEqual(self.preview.status, "STOPPED")

    def test_stop_before_start_clears_stale_label_no_game_action(self):
        self.preview.stop()
        self.assertEqual(self.label.text, "")
        self.assertFalse(self.preview.active)

    def test_stop_twice_is_idempotent(self):
        self.preview.preview_start(self.settings)
        self.preview.stop()
        self.preview.stop()
        self.assertFalse(self.preview.active)
        self.assertEqual(self.label.callbacks, {})

    def test_start_again_after_stop_is_new_preview_epoch(self):
        self.preview.preview_start(self.settings)
        self.preview.stop()
        self.assertTrue(self.preview.preview_start(self.settings))
        self.assertEqual(len(self.label.callbacks), 1)

    def test_stale_cancelled_callback_cannot_refresh_or_rearm(self):
        self.preview.preview_start(self.settings)
        ident = next(iter(self.label.callbacks))
        obsolete_cb = self.label.callbacks[ident]
        self.preview.stop()
        self.assertTrue(self.preview.preview_start(self.settings))
        current_id = next(iter(self.label.callbacks))
        current_text = self.label.text
        obsolete_cb()  # simulate already-queued Tcl cancellation race
        self.assertEqual(next(iter(self.label.callbacks)), current_id)
        self.assertEqual(self.label.text, current_text)
        self.assertEqual(len(self.label.callbacks), 1)

    def test_destroyed_label_fails_closed(self):
        self.label.exists = False
        self.assertFalse(self.preview.preview_start(self.settings))
        self.assertEqual(self.preview.status, "BLOCKED_TK_LABEL")

    def test_label_destroyed_after_start_stops(self):
        self.preview.preview_start(self.settings)
        ident = next(iter(self.label.callbacks))
        self.label.exists = False
        self.label.fire(ident)
        self.assertFalse(self.preview.active)
        self.assertEqual(self.preview.status, "BLOCKED_PREVIEW")

    def test_after_schedule_failure_fails_closed(self):
        self.label.fail_after = True
        self.assertFalse(self.preview.preview_start(self.settings))
        self.assertEqual(self.label.callbacks, {})
        self.assertEqual(self.preview.status, "BLOCKED_PREVIEW")

    def test_render_failure_fails_closed(self):
        self.label.fail_configure = True
        self.assertFalse(self.preview.preview_start(self.settings))
        self.assertFalse(self.preview.active)

    def test_backwards_wall_clock_disarms_preview(self):
        self.preview.preview_start(self.settings)
        old_id = next(iter(self.label.callbacks))
        self.clock_time = datetime(2026, 10, 9, 3, 58)
        self.label.fire(old_id)
        self.assertEqual(self.preview.status, "BLOCKED_PREVIEW")
        self.assertFalse(self.preview.active)

    def test_bad_time_source_type_disarms(self):
        self.preview.preview_start(self.settings)
        ident = next(iter(self.label.callbacks))
        self.preview._now = lambda: "BAD_NOW"
        self.label.fire(ident)
        self.assertEqual(self.preview.status, "BLOCKED_PREVIEW")

    def test_main_thread_guard_on_start(self):
        errors = []
        def worker():
            try:
                self.preview.preview_start(self.settings)
            except Exception as e:
                errors.append(type(e).__name__)
        thread = threading.Thread(target=worker)
        thread.start()
        thread.join(timeout=3)
        self.assertEqual(errors, ["RuntimeError"])
        self.assertFalse(self.preview.active)

    def test_main_thread_guard_on_stop(self):
        self.preview.preview_start(self.settings)
        errors = []
        def worker():
            try:
                self.preview.stop()
            except Exception as e:
                errors.append(type(e).__name__)
        thread = threading.Thread(target=worker)
        thread.start()
        thread.join(timeout=3)
        self.assertEqual(errors, ["RuntimeError"])
        self.assertTrue(self.preview.active)

    def test_shutdown_cancels_and_refuses_restart(self):
        self.preview.preview_start(self.settings)
        self.preview.shutdown()
        self.assertFalse(self.preview.active)
        self.assertEqual(self.preview.status, "CLOSED")
        self.assertEqual(self.label.callbacks, {})
        self.assertFalse(self.preview.preview_start(self.settings))
        self.preview.shutdown()
        self.assertEqual(self.preview.status, "CLOSED")

    def test_source_never_dispatched_or_saved_accounts(self):
        src = Path(sys.modules["login_schedule_countdown"].__file__).read_text(encoding="utf-8")
        for forbidden in ("write_settings(", "os.system(", "subprocess.run(",
                          "subprocess.Popen(", "CreateProcessW(",
                          "PostMessage(", "SendMessage(", "spawn_and_inject(",
                          "_open_game_batch(", "shutdown /s /t 0"):
            self.assertNotIn(forbidden, src)


if __name__ == "__main__":
    unittest.main()
