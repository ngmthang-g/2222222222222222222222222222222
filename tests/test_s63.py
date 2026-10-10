"""S63 original-backed 1000ms C07 tiler cadence, no invented placement."""
from __future__ import annotations
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from auto_tile_clock import C07AutoTileClock,AUTO_TILE_LOOP_INTERVAL_MS

class FakeTk:
    def __init__(self):
        self.pending={};self.history={};self.next_id=0;self.cancelled=[]
    def after(self,ms,cb):
        self.next_id+=1
        self.pending[self.next_id]=(ms,cb)
        self.history[self.next_id]=(ms,cb)
        return self.next_id
    def after_cancel(self,id):
        self.cancelled.append(id);self.pending.pop(id,None)
    def fire(self,id):
        ms,cb=self.pending.pop(id)
        cb()

class S63AutoTileClock(unittest.TestCase):
    def setUp(self):
        self.tk=FakeTk();self.allowed=[True];self.seen=[]
        self.clock=C07AutoTileClock(self.tk,on_tick=lambda:self.seen.append("tick"),
                      allowed=lambda:self.allowed[0])
    def test_original_one_second_not_input_keepalive_1500ms(self):
        self.assertEqual(AUTO_TILE_LOOP_INTERVAL_MS,1000)
        self.assertTrue(self.clock.start())
        self.assertEqual(self.tk.pending[self.clock._auto_tile_id][0],1000)
        self.assertEqual(self.seen,[])
    def test_one_callback_reschedules_exactly_one_1000ms_interval(self):
        self.clock.start()
        ident=self.clock._auto_tile_id
        self.tk.fire(ident)
        self.assertEqual(self.seen,["tick"])
        self.assertEqual(self.clock.tick_count,1)
        self.assertEqual(len(self.tk.pending),1)
        self.assertEqual(self.tk.pending[self.clock._auto_tile_id][0],1000)
    def test_duplicate_start_never_creates_second_after(self):
        self.assertTrue(self.clock.start())
        first=self.clock._auto_tile_id
        self.assertFalse(self.clock.start())
        self.assertEqual(list(self.tk.pending),[first])
    def test_stop_cancels_pending_and_inactive_tick_cannot_run(self):
        self.clock.start()
        old=self.clock._auto_tile_id
        oldcb=self.tk.history[old][1]
        self.assertTrue(self.clock.stop())
        self.assertEqual(self.tk.pending,{})
        oldcb()
        self.assertEqual(self.seen,[])
        self.assertFalse(self.clock.auto_tile_active)
    def test_restart_old_stale_callback_does_not_affect_new_session(self):
        self.clock.start();one=self.tk.history[self.clock._auto_tile_id][1]
        self.clock.stop()
        self.assertTrue(self.clock.start())
        current=self.clock._auto_tile_id
        one()
        self.assertEqual(self.clock._auto_tile_id,current)
        self.assertEqual(self.seen,[])
        self.tk.fire(current)
        self.assertEqual(self.seen,["tick"])
    def test_revoked_before_start_prevents_timer(self):
        self.allowed[0]=False
        self.assertFalse(self.clock.start())
        self.assertEqual(self.tk.pending,{})
    def test_revoked_between_ticks_prevents_callback(self):
        self.clock.start()
        self.allowed[0]=False
        self.tk.fire(self.clock._auto_tile_id)
        self.assertEqual(self.seen,[])
        self.assertFalse(self.clock.auto_tile_active)
        self.assertEqual(self.tk.pending,{})
    def test_revoke_inside_real_callback_does_not_rearm(self):
        def revoke():
            self.seen.append("tick");self.allowed[0]=False
        self.clock.on_tick=revoke
        self.clock.start();self.tk.fire(self.clock._auto_tile_id)
        self.assertEqual(self.seen,["tick"])
        self.assertFalse(self.clock.auto_tile_active)
        self.assertEqual(self.tk.pending,{})
    def test_callback_stop_prevents_late_reschedule(self):
        def stop():
            self.seen.append("tick");self.clock.stop()
        self.clock.on_tick=stop
        self.clock.start();self.tk.fire(self.clock._auto_tile_id)
        self.assertEqual(self.tk.pending,{})
        self.assertEqual(self.clock.tick_count,1)
    def test_failing_callback_stops_instead_of_claiming_tile_success(self):
        def fail():raise ValueError("TEST_ONLY_BAD_TILER")
        self.clock.on_tick=fail
        self.clock.start();self.tk.fire(self.clock._auto_tile_id)
        self.assertEqual(self.clock.last_error,"ValueError")
        self.assertFalse(self.clock.auto_tile_active)
        self.assertEqual(self.clock.tick_count,0)
    def test_shutdown_cancels_and_refuses_restart(self):
        self.clock.start();self.clock.shutdown();self.clock.shutdown()
        self.assertFalse(self.clock.start())
        self.assertEqual(self.tk.pending,{})
        self.assertTrue(self.clock._closed)
    def test_missing_callable_and_no_proxy_or_tile_geometry(self):
        for kw in ({"on_tick":None,"allowed":lambda:True},
                   {"on_tick":lambda:None,"allowed":None}):
            with self.assertRaises(TypeError):C07AutoTileClock(self.tk,**kw)
        source=(ROOT/"src/auto_tile_clock.py").read_text("utf-8")
        for txt in ("SetWindowPos","proxy_tab","tk.Radiobutton(",
                    "shutdown /s","PostMessage(","TileWidth","TileHeight"):
            self.assertNotIn(txt,source)
if __name__=="__main__":unittest.main()
