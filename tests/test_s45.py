"""S45 test-owned lifecycle coordinates S44 Tk and S43 worker safely."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
import sys
import threading
import time
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"tests"))
from test_s41 import FakeLabel
from login_schedule_lifetime import F09ReadOnlyTabLifetime
from login_schedule_settings import ReadOnlyScheduleSettings
from login_schedule_worker import BLOCKED_ACTION


class S45TabLifetimeTests(unittest.TestCase):
    def setUp(self):
        self.label=FakeLabel()
        self.t=[datetime(2026,10,9,3,59,50)]
        self.config=ReadOnlyScheduleSettings(
            "READ_ONLY_VALIDATED","04:00","04:20","UNKNOWN_ON","UNKNOWN_PC")
        with patch("tkinter.Label",FakeLabel):
            self.life=F09ReadOnlyTabLifetime(
                self.label,self.config,now=lambda:self.t[0])
        self.release=None

    def tearDown(self):
        if self.release is not None:
            self.release.set()
        self.life.close()
        self.assertTrue(self.life.finish_close(2))
        self.assertFalse(self.life.worker.thread_alive)

    def _destroy(self,widget=None):
        event=SimpleNamespace(widget=widget if widget is not None else self.label)
        for callback in self.label._bindings["<Destroy>"]:
            callback(event)

    def test_initial_idle_does_not_auto_arm_opaque_saved_boolean(self):
        self.assertEqual(self.life.status,"IDLE")
        self.assertFalse(self.life.preview.active)
        self.assertFalse(self.life.worker.active)
        self.assertFalse(self.life.closed)

    def test_both_destroy_handlers_are_installed_without_clobbering(self):
        self.assertEqual(len(self.label._bindings["<Destroy>"]),2)
        self.assertEqual(self.life._destroy_binding,"S41_FAKE_TK_BINDING")

    def test_explicit_start_has_real_tk_timer_and_real_event_worker(self):
        self.assertTrue(self.life.start_preview_and_evaluation())
        self.assertEqual(self.life.status,"READONLY_PREVIEW_AND_BLOCKED_EVALUATION")
        self.assertTrue(self.life.preview.active)
        self.assertTrue(self.life.preview.has_pending_refresh)
        self.assertTrue(self.life.worker.thread_alive)
        self.assertEqual(len(self.label.callbacks),1)

    def test_destroy_own_label_closes_both_without_game_actions(self):
        self.life.start_preview_and_evaluation()
        callback_id=next(iter(self.label.callbacks))
        self.label.exists=False
        self._destroy()
        self.assertTrue(self.life.closed)
        self.assertEqual(self.life.preview.status,"CLOSED")
        self.assertIn(callback_id,self.label.cancelled)
        self.assertFalse(self.life.worker.active)
        self.assertFalse(self.life.start_preview_and_evaluation())

    def test_destroy_other_widget_does_not_stop_worker_or_preview(self):
        self.life.start_preview_and_evaluation()
        self._destroy(widget=object())
        self.assertFalse(self.life.closed)
        self.assertTrue(self.life.worker.active)
        self.assertTrue(self.life.preview.active)

    def test_close_is_idempotent_and_does_not_launch_game(self):
        self.life.start_preview_and_evaluation()
        self.life.close()
        self.life.close()
        self.assertTrue(self.life.closed)
        self.assertFalse(self.life.worker.active)
        self.assertFalse(self.life.preview.active)

    def test_pending_old_tk_callback_does_not_restart_after_destroy(self):
        self.life.start_preview_and_evaluation()
        old=self.label.callbacks[next(iter(self.label.callbacks))]
        self.label.exists=False
        self._destroy()
        old()
        self.assertEqual(self.label.callbacks,{})
        self.assertFalse(self.life.worker.active)

    def test_bad_schedule_blocks_both_without_threads(self):
        self.life.close()
        self.life.finish_close()
        with patch("tkinter.Label",FakeLabel):
            self.life=F09ReadOnlyTabLifetime(
                FakeLabel(),ReadOnlyScheduleSettings("BLOCKED_TIME_FORMAT"))
        self.assertFalse(self.life.start_preview_and_evaluation())
        self.assertEqual(self.life.status,"BLOCKED_SETTINGS")
        self.assertFalse(self.life.worker.thread_alive)

    def test_second_start_never_duplicates_worker_or_timer(self):
        self.life.start_preview_and_evaluation()
        self.assertFalse(self.life.start_preview_and_evaluation())
        self.assertEqual(len(self.label.callbacks),1)
        self.assertTrue(self.life.worker.active)

    def test_failed_worker_start_rolls_back_preview(self):
        self.life.worker.start=lambda:False
        self.assertFalse(self.life.start_preview_and_evaluation())
        self.assertEqual(self.life.status,"BLOCKED_WORKER")
        self.assertFalse(self.life.preview.active)
        self.assertEqual(self.label.callbacks,{})

    def test_failed_preview_start_never_launches_worker(self):
        self.label.exists=False
        self.assertFalse(self.life.start_preview_and_evaluation())
        self.assertEqual(self.life.status,"BLOCKED_PREVIEW")
        self.assertFalse(self.life.worker.thread_alive)

    def test_reentrant_destroy_during_initial_time_provider_preserves_closed(self):
        def callback():
            self.label.exists=False
            self._destroy()
            return self.t[0]
        self.life.preview._now=callback
        self.assertFalse(self.life.start_preview_and_evaluation())
        self.assertTrue(self.life.closed)
        self.assertEqual(self.life.status,"CLOSED")
        self.assertFalse(self.life.worker.thread_alive)

    def test_reentrant_destroy_during_worker_start_cancels_worker(self):
        original=self.life.worker.start
        def callback():
            started=original()
            self.label.exists=False
            self._destroy()
            return started
        self.life.worker.start=callback
        self.assertFalse(self.life.start_preview_and_evaluation())
        self.assertTrue(self.life.closed)
        self.assertFalse(self.life.worker.active)

    def test_finish_close_before_request_is_denied(self):
        with self.assertRaises(RuntimeError):
            self.life.finish_close()

    def test_wrong_thread_tk_close_denied(self):
        self.life.start_preview_and_evaluation()
        errors=[]
        def fn():
            try:
                self.life.close()
            except Exception as exc:
                errors.append(type(exc).__name__)
        t=threading.Thread(target=fn)
        t.start();t.join(2)
        self.assertEqual(errors,["RuntimeError"])
        self.assertFalse(self.life.closed)

    def test_worker_clock_stall_never_blocks_tk_close(self):
        release=threading.Event()
        entered=threading.Event()
        self.release=release
        first=[True]
        def slow_clock():
            if first[0]:
                first[0]=False
                return self.t[0]
            entered.set()
            release.wait(3)
            return datetime(2026,10,9,4,21)
        self.life.worker._now=slow_clock
        real_wait=self.life.worker._cancel.wait
        self.life.worker._cancel.wait=lambda delay:real_wait(0.01)
        self.assertTrue(self.life.start_preview_and_evaluation())
        self.assertTrue(entered.wait(2))
        start=time.monotonic()
        self.label.exists=False
        self._destroy()
        self.assertLess(time.monotonic()-start,0.35)
        self.assertTrue(self.life.closed)
        self.assertEqual(self.life.status,"CLOSING_WORKER")
        self.assertTrue(self.life.worker._cancel.is_set())
        release.set()
        self.assertTrue(self.life.finish_close(2))
        self.assertFalse(self.life.worker.thread_alive)
        self.assertEqual(self.life.worker.blocked_occurrences(),())

    def test_close_before_start_disarms_all_and_forbids_future_start(self):
        self.assertTrue(self.life.close())
        self.assertTrue(self.life.closed)
        self.assertFalse(self.life.start_preview_and_evaluation())
        self.assertEqual(self.life.status,"CLOSED")

    def test_clock_due_events_are_always_blocked_only(self):
        self.life.start_preview_and_evaluation()
        self.t[0]=datetime(2026,10,9,4,21)
        events=self.life.worker.poll_once()
        self.assertEqual([i.kind for i in events],["close","open"])
        self.assertTrue(all(i.status==BLOCKED_ACTION for i in events))

    def test_source_no_game_dispatch_no_ini_writes(self):
        source=Path(sys.modules["login_schedule_lifetime"].__file__).read_text(encoding="utf-8")
        for token in ("write_settings(", "subprocess.Popen(", "_open_game_batch(",
                      "shutdown /s /t 0", "CreateProcessW(", "PostMessage("):
            self.assertNotIn(token,source)


if __name__=="__main__":
    unittest.main()
