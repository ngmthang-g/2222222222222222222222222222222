"""S27 bounded/cancellable F05 PID->HWND handoff, including serial queue."""
from __future__ import annotations

from pathlib import Path
import sys
import threading
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"src"))
from login_window_handoff import (
    MAX_WAIT_SECONDS, DEFAULT_POLL_SECONDS, SerializedPidWindowHandoff,
    WindowHandoffResult, wait_for_pid_window,
)


class TickClock:
    def __init__(self):self.now=0.0;self.delays=[]
    def clock(self):return self.now
    def pause(self,s):
        self.delays.append(s)
        self.now+=s


class Backend:
    def __init__(self, *, pid=42, appearing_at=1, title="Thần Long"):
        self.pid=pid;self.reads=0;self.appearing_at=appearing_at
        self.title=title;self.active=True;self.visible=True
        self.changed_pid_at=0;self.after_title=None
        self.fail=False
    def enumerate_top_level(self):
        self.reads+=1
        if self.fail:raise OSError("TEST_ENUM_WINDOWS_FAILED")
        return (100,) if self.active and self.reads>=self.appearing_at else ()
    def is_window(self,h):return self.active and h==100
    def is_visible(self,h):return self.visible
    def process_id(self,h):return self.pid
    def window_class(self,h):return "TEST_OWNED"
    def title_with_timeout(self,h,timeout_ms):
        assert timeout_ms==150
        if self.after_title is not None:self.after_title()
        return self.title


class S27HandoffTests(unittest.TestCase):
    def run_fake(self,b,*,t=1,p=.1,cancel=None,tick=None):
        tk=tick or TickClock()
        return wait_for_pid_window(42,backend=b,cancel=cancel,
                                   timeout_seconds=t,poll_seconds=p,
                                   clock=tk.clock,pause=tk.pause),tk

    def test_original_ceiling_exact_25_seconds(self):
        self.assertEqual(MAX_WAIT_SECONDS,25.0)
        self.assertEqual(DEFAULT_POLL_SECONDS,.1)

    def test_invalid_pid_rejected_before_enumeration(self):
        for pid in (None,-1,0,True,"42"):
            b=Backend()
            r=wait_for_pid_window(pid,backend=b,timeout_seconds=0)
            self.assertEqual((r.code,r.hwnd,r.scans),("INVALID_PID",None,0))
            self.assertEqual(b.reads,0)

    def test_reject_unknown_overlong_or_bad_timing(self):
        for t in (25.01,-1,float("nan"),float("inf"),True,"25"):
            with self.assertRaises(ValueError):
                wait_for_pid_window(42,backend=Backend(),timeout_seconds=t)
        for p in (0,-1,float("inf"),True,"0.1"):
            with self.assertRaises(ValueError):
                wait_for_pid_window(42,backend=Backend(),poll_seconds=p)

    def test_immediate_present_hwnd(self):
        ans,tick=self.run_fake(Backend())
        self.assertEqual((ans.code,ans.hwnd,ans.scans),("FOUND",100,1))
        self.assertEqual(tick.delays,[])

    def test_late_pid_window_discovered_after_actual_waits(self):
        b=Backend(appearing_at=4)
        ans,tick=self.run_fake(b,t=.8,p=.1)
        self.assertEqual((ans.code,ans.hwnd,ans.scans),("FOUND",100,4))
        self.assertEqual(tick.delays,[.1,.1,.1])
        self.assertAlmostEqual(ans.elapsed_seconds,.3)

    def test_nonexistent_hwnd_timeout_exact_budget(self):
        ans,tick=self.run_fake(Backend(appearing_at=100),t=.35,p=.12)
        self.assertEqual((ans.code,ans.hwnd),("TIMEOUT",None))
        self.assertAlmostEqual(ans.elapsed_seconds,.35)
        self.assertLessEqual(max(tick.delays),.12)
        self.assertGreater(ans.scans,1)

    def test_zero_timeout_single_snapshot_only(self):
        b=Backend(appearing_at=10)
        ans,tick=self.run_fake(b,t=0)
        self.assertEqual((ans.code,ans.scans),("TIMEOUT",1))
        self.assertEqual(b.reads,1)
        self.assertEqual(tick.delays,[])

    def test_cancel_before_scan(self):
        event=threading.Event();event.set()
        b=Backend()
        ans,tick=self.run_fake(b,cancel=event)
        self.assertEqual((ans.code,ans.scans),("CANCELLED",0))
        self.assertEqual(b.reads,0)

    def test_cancel_during_polling(self):
        event=threading.Event();tick=TickClock()
        def pause(s):
            tick.pause(s)
            if len(tick.delays)==2:event.set()
        b=Backend(appearing_at=9)
        ans=wait_for_pid_window(42,backend=b,cancel=event,timeout_seconds=1,
                                clock=tick.clock,pause=pause)
        self.assertEqual((ans.code,ans.scans),("CANCELLED",2))
        self.assertEqual(tick.delays,[.1,.1])

    def test_cancel_race_after_hwnd_selected(self):
        event=threading.Event()
        b=Backend()
        b.after_title=event.set
        ans,tick=self.run_fake(b,cancel=event)
        self.assertEqual(ans.code,"CANCELLED")
        self.assertIsNone(ans.hwnd)

    def test_wrong_pid_cannot_match_title(self):
        ans,tick=self.run_fake(Backend(pid=99),t=.2)
        self.assertEqual(ans.code,"TIMEOUT")
        self.assertIsNone(ans.hwnd)

    def test_closed_hwnd_after_selection_rejected(self):
        b=Backend()
        b.after_title=lambda:setattr(b,"active",False)
        ans,tick=self.run_fake(b,t=.2)
        self.assertEqual(ans.code,"TIMEOUT")
        self.assertIsNone(ans.hwnd)

    def test_reused_pid_after_selection_rejected(self):
        b=Backend()
        b.after_title=lambda:setattr(b,"pid",99)
        ans,tick=self.run_fake(b,t=.2)
        self.assertEqual(ans.code,"TIMEOUT")
        self.assertIsNone(ans.hwnd)

    def test_top_level_enumeration_failure_reports_error(self):
        b=Backend();b.fail=True
        ans,tick=self.run_fake(b)
        self.assertEqual((ans.code,ans.scans),("ENUMERATION_FAILED",1))

    def test_clock_deadline_does_not_accept_late_window(self):
        tick=TickClock()
        b=Backend()
        b.after_title=lambda:setattr(tick,"now",1.01)
        ans=wait_for_pid_window(42,backend=b,timeout_seconds=1,
                                clock=tick.clock,pause=tick.pause)
        self.assertEqual(ans.code,"TIMEOUT")
        self.assertIsNone(ans.hwnd)

    def test_serial_coordinator_rejects_invalid_pid(self):
        coord=SerializedPidWindowHandoff()
        self.assertEqual(coord.wait(0,backend=Backend(),timeout_seconds=0).code,
                         "INVALID_PID")

    def test_serial_coordinator_free_lock_fast_handoff(self):
        coord=SerializedPidWindowHandoff()
        tick=TickClock()
        ans=coord.wait(42,backend=Backend(),timeout_seconds=.5,
                       clock=tick.clock,pause=tick.pause)
        self.assertEqual(ans.code,"FOUND")
        self.assertEqual(ans.hwnd,100)

    def test_serial_lock_contention_times_out_not_block_forever(self):
        coord=SerializedPidWindowHandoff()
        grabbed=threading.Event();release=threading.Event()
        def hold():
            with coord._lock:
                grabbed.set();release.wait(2)
        worker=threading.Thread(target=hold,daemon=True)
        worker.start();self.assertTrue(grabbed.wait(1))
        try:
            r=coord.wait(42,backend=Backend(),timeout_seconds=.06)
            self.assertEqual((r.code,r.scans),("TIMEOUT",0))
            self.assertGreaterEqual(r.elapsed_seconds,.04)
        finally:
            release.set();worker.join(1)

    def test_serial_lock_contention_cancelled_before_25s(self):
        coord=SerializedPidWindowHandoff()
        grabbed=threading.Event();release=threading.Event()
        def hold():
            with coord._lock:
                grabbed.set();release.wait(2)
        thread=threading.Thread(target=hold,daemon=True)
        thread.start();self.assertTrue(grabbed.wait(1))
        event=threading.Event()
        timer=threading.Timer(.06,event.set);timer.start()
        try:
            r=coord.wait(42,backend=Backend(),cancel=event,timeout_seconds=1)
            self.assertEqual((r.code,r.scans),("CANCELLED",0))
            self.assertLess(r.elapsed_seconds,.3)
        finally:
            release.set();thread.join(1);timer.join(1)

    def test_serial_held_lock_released_after_backend_error(self):
        coord=SerializedPidWindowHandoff()
        broken=Backend();broken.fail=True
        r=coord.wait(42,backend=broken,timeout_seconds=.2)
        self.assertEqual(r.code,"ENUMERATION_FAILED")
        ready=coord.wait(42,backend=Backend(),timeout_seconds=.2)
        self.assertEqual(ready.code,"FOUND")


if __name__=="__main__":
    unittest.main()
