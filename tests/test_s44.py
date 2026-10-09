"""S44 F09 real Tk Label Destroy + callback re-entrancy fixes, no game actions."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
import sys
import threading
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"tests"))
from test_s41 import FakeLabel
from login_schedule_countdown import TkScheduleCountdownPreview, REFRESH_MS
from login_schedule_settings import ReadOnlyScheduleSettings


class S44TkDestroyLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.label=FakeLabel()
        self.current=[datetime(2026,10,9,3,59,50)]
        with patch("tkinter.Label",FakeLabel):
            self.preview=TkScheduleCountdownPreview(
                self.label,now=lambda:self.current[0])
        self.settings=ReadOnlyScheduleSettings(
            "READ_ONLY_VALIDATED","04:00","04:20","UNKNOWN_ON","UNKNOWN_PC")

    def tearDown(self):
        self.preview.shutdown()
        self.assertFalse(self.preview.has_pending_refresh)

    def emit_destroy(self,widget=None):
        event=SimpleNamespace(widget=self.label if widget is None else widget)
        for cb in self.label._bindings["<Destroy>"]:
            cb(event)

    def test_original_label_destroy_handler_is_installed_with_add(self):
        self.assertIn("<Destroy>",self.label._bindings)
        self.assertEqual(len(self.label._bindings["<Destroy>"]),1)
        self.assertEqual(self.preview._destroy_binding,"S41_FAKE_TK_BINDING")

    def test_unrelated_destroy_event_does_not_close_preview(self):
        self.assertTrue(self.preview.preview_start(self.settings))
        self.emit_destroy(widget=object())
        self.assertTrue(self.preview.active)
        self.assertEqual(len(self.label.callbacks),1)

    def test_own_label_destroy_automatically_cancels_pending_after(self):
        self.assertTrue(self.preview.preview_start(self.settings))
        ident=next(iter(self.label.callbacks))
        self.label.exists=False
        self.emit_destroy()
        self.assertEqual(self.preview.status,"CLOSED")
        self.assertFalse(self.preview.active)
        self.assertFalse(self.preview.has_pending_refresh)
        self.assertIn(ident,self.label.cancelled)
        self.assertEqual(self.label.callbacks,{})

    def test_after_callback_already_queued_cannot_rearm_after_destroy(self):
        self.assertTrue(self.preview.preview_start(self.settings))
        ident=next(iter(self.label.callbacks))
        old=self.label.callbacks[ident]
        self.label.exists=False
        self.emit_destroy()
        old()
        self.assertEqual(self.label.callbacks,{})
        self.assertEqual(self.preview.status,"CLOSED")

    def test_double_destroy_is_idempotent(self):
        self.preview.preview_start(self.settings)
        self.label.exists=False
        self.emit_destroy()
        self.emit_destroy()
        self.assertEqual(self.preview.status,"CLOSED")
        self.assertFalse(self.preview.preview_start(self.settings))

    def test_destroy_without_active_preview_is_also_terminal(self):
        self.label.exists=False
        self.emit_destroy()
        self.assertEqual(self.preview.status,"CLOSED")
        self.assertFalse(self.preview.preview_start(self.settings))

    def test_reentrant_stop_inside_label_configure_never_rearms(self):
        original=self.label.configure
        first=[True]
        def reentrant_configure(**kw):
            original(**kw)
            if first[0]:
                first[0]=False
                self.preview.stop()
        self.label.configure=reentrant_configure
        self.assertFalse(self.preview.preview_start(self.settings))
        self.assertEqual(self.preview.status,"STOPPED")
        self.assertEqual(self.label.text,"")
        self.assertEqual(self.label.callbacks,{})

    def test_reentrant_shutdown_inside_label_configure_preserves_closed(self):
        original=self.label.configure
        first=[True]
        def reentrant_configure(**kw):
            original(**kw)
            if first[0]:
                first[0]=False
                self.preview.shutdown()
        self.label.configure=reentrant_configure
        self.assertFalse(self.preview.preview_start(self.settings))
        self.assertEqual(self.preview.status,"CLOSED")
        self.assertEqual(self.label.callbacks,{})

    def test_reentrant_stop_inside_initial_clock_source_never_arms(self):
        def callback():
            self.preview.stop()
            return self.current[0]
        self.preview._now=callback
        self.assertFalse(self.preview.preview_start(self.settings))
        self.assertEqual(self.preview.status,"STOPPED")
        self.assertEqual(self.label.callbacks,{})

    def test_reentrant_shutdown_inside_initial_clock_source_never_arms(self):
        def callback():
            self.preview.shutdown()
            return self.current[0]
        self.preview._now=callback
        self.assertFalse(self.preview.preview_start(self.settings))
        self.assertEqual(self.preview.status,"CLOSED")
        self.assertEqual(self.label.callbacks,{})

    def test_reentrant_stop_in_scheduled_refresh_clock_source(self):
        self.assertTrue(self.preview.preview_start(self.settings))
        callback_id=next(iter(self.label.callbacks))
        def callback():
            self.preview.stop()
            return self.current[0]
        self.preview._now=callback
        self.label.fire(callback_id)
        self.assertEqual(self.preview.status,"STOPPED")
        self.assertEqual(self.label.text,"")
        self.assertEqual(self.label.callbacks,{})

    def test_reentrant_shutdown_in_scheduled_refresh_clock_source(self):
        self.preview.preview_start(self.settings)
        callback_id=next(iter(self.label.callbacks))
        def callback():
            self.preview.shutdown()
            return self.current[0]
        self.preview._now=callback
        self.label.fire(callback_id)
        self.assertEqual(self.preview.status,"CLOSED")
        self.assertEqual(self.label.callbacks,{})

    def test_reentrant_stop_during_after_creation_cancels_orphan_id(self):
        original=self.label.after
        ident_box=[]
        def callback(delay,fn):
            ident=original(delay,fn)
            ident_box.append(ident)
            self.preview.stop()
            return ident
        self.label.after=callback
        self.assertFalse(self.preview.preview_start(self.settings))
        self.assertEqual(self.label.callbacks,{})
        self.assertEqual(self.label.cancelled,ident_box)
        self.assertFalse(self.preview.has_pending_refresh)
        self.assertEqual(self.preview.status,"STOPPED")

    def test_reentrant_shutdown_during_after_creation_cancels_orphan_id(self):
        original=self.label.after
        ids=[]
        def callback(delay,fn):
            ident=original(delay,fn)
            ids.append(ident)
            self.preview.shutdown()
            return ident
        self.label.after=callback
        self.assertFalse(self.preview.preview_start(self.settings))
        self.assertEqual(self.label.callbacks,{})
        self.assertEqual(self.label.cancelled,ids)
        self.assertEqual(self.preview.status,"CLOSED")

    def test_existing_normal_1000ms_preview_kept_working(self):
        self.assertTrue(self.preview.preview_start(self.settings))
        self.assertEqual(self.label.last_delay,REFRESH_MS)
        self.assertEqual(len(self.label.callbacks),1)
        old=next(iter(self.label.callbacks))
        self.current[0]=datetime(2026,10,9,4,0,2)
        self.label.fire(old)
        self.assertIn("Tắt 04:00 10/10 còn",self.label.text)
        self.assertEqual(len(self.label.callbacks),1)

    def test_existing_explicit_stop_cancels_after_destroy_not_required(self):
        self.preview.preview_start(self.settings)
        old=next(iter(self.label.callbacks))
        self.preview.stop()
        self.assertIn(old,self.label.cancelled)
        self.assertEqual(self.label.text,"")
        self.assertEqual(self.preview.status,"STOPPED")

    def test_wrong_thread_shutdown_denied_no_tk_calls(self):
        self.preview.preview_start(self.settings)
        errors=[]
        def do_shutdown():
            try:
                self.preview.shutdown()
            except Exception as exc:
                errors.append(type(exc).__name__)
        t=threading.Thread(target=do_shutdown);t.start();t.join(2)
        self.assertEqual(errors,["RuntimeError"])
        self.assertTrue(self.preview.active)

    def test_no_original_f09_actions_or_config_writes(self):
        source=Path(sys.modules["login_schedule_countdown"].__file__).read_text(encoding="utf-8")
        for forbidden in ("write_settings(", "subprocess.Popen(", "shutdown /s /t 0",
                          "_open_game_batch(", "CreateProcessW(", "spawn_and_inject(",
                          "PostMessage("):
            self.assertNotIn(forbidden,source)


if __name__=="__main__":
    unittest.main()
