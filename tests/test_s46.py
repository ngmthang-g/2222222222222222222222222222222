"""S46 independently reproduce lock-contention Tk freeze and teardown failure."""
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
from login_schedule_worker import F09ScheduleEvaluationWorker


class S46ShutdownContentionTests(unittest.TestCase):
    def setUp(self):
        self.label=FakeLabel()
        self.current=datetime(2026,10,9,3,59,50)
        self.config=ReadOnlyScheduleSettings(
            "READ_ONLY_VALIDATED","04:00","04:20",
            "UNKNOWN_PERSISTED_ON","UNKNOWN_PERSISTED_SHUTDOWN")
        with patch("tkinter.Label",FakeLabel):
            self.life=F09ReadOnlyTabLifetime(
                self.label,self.config,now=lambda:self.current)
        self.to_release=[]

    def tearDown(self):
        for event in self.to_release:
            event.set()
        self.life.close()
        self.life.worker.shutdown(timeout=2)
        self.assertFalse(self.life.worker.thread_alive)

    def _destroy(self):
        self.label.exists=False
        for callback in self.label._bindings["<Destroy>"]:
            callback(SimpleNamespace(widget=self.label))

    def test_request_shutdown_is_idempotent_and_never_starts_thread(self):
        self.life.worker.request_shutdown()
        self.life.worker.request_shutdown()
        self.assertTrue(self.life.worker._closed)
        self.assertTrue(self.life.worker._cancel.is_set())
        self.assertFalse(self.life.worker.start())
        self.assertFalse(self.life.worker.thread_alive)

    def test_gui_close_while_worker_lifecycle_lock_held_does_not_block(self):
        self.assertTrue(self.life.start_preview_and_evaluation())
        self.assertTrue(self.life.worker._lifecycle_lock.acquire(blocking=False))
        try:
            start=time.monotonic()
            self._destroy()
            elapsed=time.monotonic()-start
            self.assertLess(elapsed,0.30)
            self.assertTrue(self.life.closed)
            self.assertTrue(self.life.worker._cancel.is_set())
            self.assertFalse(self.life.worker.active)
            self.assertFalse(self.life.start_preview_and_evaluation())
        finally:
            self.life.worker._lifecycle_lock.release()
        self.assertTrue(self.life.finish_close(2))
        self.assertEqual(self.life.status,"CLOSED")

    def test_real_concurrent_stop_join_interleaving_never_blocks_tk(self):
        self.assertTrue(self.life.start_preview_and_evaluation())
        target=self.life.worker._thread
        real_join=target.join
        joined=threading.Event()
        resume=threading.Event()
        self.to_release.append(resume)
        finished=[]
        def delayed_join(timeout=None):
            real_join(timeout)
            joined.set()
            resume.wait(2)
        target.join=delayed_join
        def stopping():
            finished.append(self.life.worker.stop(timeout=2))
        bg=threading.Thread(target=stopping,daemon=True)
        bg.start()
        try:
            self.assertTrue(joined.wait(1))
            start=time.monotonic()
            self._destroy()
            self.assertLess(time.monotonic()-start,0.3)
            self.assertTrue(self.life.closed)
            self.assertTrue(self.life.worker._cancel.is_set())
        finally:
            resume.set()
            bg.join(2)
        self.assertFalse(bg.is_alive())
        self.assertEqual(finished,[True])
        self.assertTrue(self.life.finish_close(2))

    def test_gui_close_during_blocked_time_provider_and_contended_lifecycle(self):
        first=[True]
        entered=threading.Event()
        unblock=threading.Event()
        self.to_release.append(unblock)
        def source():
            if first[0]:
                first[0]=False
                return self.current
            entered.set()
            unblock.wait(3)
            return datetime(2026,10,9,4,21)
        self.life.worker._now=source
        actual=self.life.worker._cancel.wait
        self.life.worker._cancel.wait=lambda timeout: actual(0.01)
        self.assertTrue(self.life.start_preview_and_evaluation())
        self.assertTrue(entered.wait(1))
        # Another thread owns lifecycle lock during its *bounded* stop.
        stopping=threading.Thread(
            target=lambda:self.life.worker.stop(timeout=0.35),daemon=True)
        stopping.start()
        start=time.monotonic()
        self._destroy()
        self.assertLess(time.monotonic()-start,0.30)
        self.assertTrue(self.life.closed)
        self.assertTrue(self.life.worker._cancel.is_set())
        unblock.set()
        stopping.join(2)
        self.assertTrue(self.life.finish_close(2))
        self.assertEqual(self.life.worker.blocked_occurrences(),())

    def test_tk_shutdown_exception_still_cancels_worker(self):
        self.life.start_preview_and_evaluation()
        original=self.life.preview.shutdown
        def failing_tk():
            original()
            raise RuntimeError("S46_TEST_TK_SHUTDOWN_FAILURE")
        self.life.preview.shutdown=failing_tk
        self.assertFalse(self.life.close())
        self.assertTrue(self.life.closed)
        self.assertTrue(self.life.worker._cancel.is_set())
        self.assertEqual(self.life.status,"BLOCKED_PREVIEW_TEARDOWN")
        self.assertFalse(self.life.finish_close(2))
        self.assertFalse(self.life.worker.thread_alive)

    def test_tk_exception_before_preview_cleanup_still_signals_worker(self):
        self.life.start_preview_and_evaluation()
        old=self.life.preview.shutdown
        self.life.preview.shutdown=lambda: (_ for _ in ()).throw(
            RuntimeError("S46_TEST_TK_ERROR"))
        self.assertFalse(self.life.close())
        self.assertTrue(self.life.worker._cancel.is_set())
        self.assertEqual(self.life.status,"BLOCKED_PREVIEW_TEARDOWN")
        self.assertFalse(self.life.worker.active)
        self.life.preview.shutdown=old
        self.life.preview.shutdown()

    def test_unrelated_destroy_does_not_cancel_worker(self):
        self.life.start_preview_and_evaluation()
        for callback in self.label._bindings["<Destroy>"]:
            callback(SimpleNamespace(widget=object()))
        self.assertTrue(self.life.worker.active)
        self.assertTrue(self.life.preview.active)

    def test_destroyed_label_cannot_restart_even_after_other_stop_join(self):
        self.life.start_preview_and_evaluation()
        self._destroy()
        self.life.finish_close(2)
        self.assertFalse(self.life.start_preview_and_evaluation())
        self.assertFalse(self.life.worker.start())

    def test_one_way_shutdown_latch_preempts_reentrant_worker_now(self):
        self.life.worker.shutdown()
        self.life.worker=F09ScheduleEvaluationWorker(
            self.config,now=lambda:None)
        def side_effect():
            self.life.worker.request_shutdown()
            return datetime(2026,10,9,3,59,50)
        self.life.worker._now=side_effect
        self.assertFalse(self.life.worker.start())
        self.assertTrue(self.life.worker._closed)
        self.assertTrue(self.life.worker._cancel.is_set())
        self.assertFalse(self.life.worker.thread_alive)

    def test_preemptive_request_prevents_duplicate_start(self):
        self.life.worker.request_shutdown()
        self.assertFalse(self.life.worker.start())
        self.assertFalse(self.life.worker.start())

    def test_normal_20s_worker_and_preview_remain_readonly(self):
        self.assertTrue(self.life.start_preview_and_evaluation())
        self.assertEqual(len(self.label.callbacks),1)
        self.assertTrue(self.life.worker.thread_alive)
        self.current=datetime(2026,10,9,4,21)
        observed=self.life.worker.poll_once()
        self.assertEqual([x.kind for x in observed],["close","open"])
        self.assertTrue(all(x.status=="BLOCKED_ACTION_UNAVAILABLE" for x in observed))

    def test_no_legacy_token_interpretation_or_game_action(self):
        self.assertFalse(self.life.closed)
        self.assertFalse(self.life.worker.thread_alive)
        for path in ("src/login_schedule_lifetime.py","src/login_schedule_worker.py"):
            s=(ROOT/path).read_text(encoding="utf-8")
            for token in ("write_settings(", "_open_game_batch(", "subprocess.Popen(",
                          "CreateProcessW(", "shutdown /s /t 0"):
                self.assertNotIn(token,s)

    def test_finish_close_cannot_join_before_close(self):
        with self.assertRaises(RuntimeError):
            self.life.finish_close(timeout=0)

    def test_finish_close_after_success_is_idempotent(self):
        self.life.start_preview_and_evaluation()
        self.life.close()
        self.assertTrue(self.life.finish_close(2))
        self.assertTrue(self.life.finish_close(2))
        self.assertEqual(self.life.status,"CLOSED")

    def test_request_shutdown_preserves_no_file_write_no_preview_auto_start(self):
        self.life.worker.request_shutdown()
        self.assertFalse(self.life.preview.active)
        self.assertEqual(self.life.status,"IDLE")
        self.assertFalse(self.life.start_preview_and_evaluation())


if __name__=="__main__":
    unittest.main()
