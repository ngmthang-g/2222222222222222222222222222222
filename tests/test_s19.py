"""S19 pure C19 click order + scaled client geometry safety tests.

No sender or listener is constructed; sink is an explicitly test-owned spy.
"""
from __future__ import annotations
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from input_sync_core import (
    InputSyncModel, ClientSize, InputEvent, scale_client_point,
    WATCHDOG_UNLOCK_SECONDS, INPUT_KEEPALIVE_SECONDS,
    ORIGINAL_KEYBOARD_PAYLOAD, ORIGINAL_MOUSE_MOVE_THROTTLE,
    SCALING_ROUNDING, NativeClientRectReader,
)
from start_polling import WindowSnapshot
from start_windows import GameWindow, GAME_PROCESS,GAME_TITLE,UNITY_WINDOW_CLASS


def row(hwnd,pid=None):
    return GameWindow(hwnd,pid if pid is not None else 10000+hwnd,
                      GAME_TITLE,UNITY_WINDOW_CLASS,GAME_PROCESS)


def snap(*rows,valid=True):
    return WindowSnapshot(1,tuple(rows),valid)


ROWS=(row(11),row(22),row(33))
MASTER=(ROWS[0].hwnd,ROWS[0].pid)
SIZES={(w.hwnd,w.pid):ClientSize(400+(i*125),300+(i*100))
       for i,w in enumerate(ROWS)}


def activated(rows=ROWS,maximum=3,master=MASTER):
    p=InputSyncModel()
    assert p.start(snap(*rows),master,max_windows=maximum)
    return p


def flush(model,valid=lambda h,p: True,allowed=lambda:True):
    got=[]
    while True:
        event=model.dispatch_one(sink=got.append,identity_ok=valid,
                                 permission_ok=allowed)
        if event is None:
            break
    return got


class S19Geometry(unittest.TestCase):
    def test_verified_facts_are_not_mixed_with_unknown_payload(self):
        self.assertEqual(INPUT_KEEPALIVE_SECONDS,1.5)
        self.assertEqual(WATCHDOG_UNLOCK_SECONDS,10.0)
        self.assertIn("UNKNOWN",ORIGINAL_KEYBOARD_PAYLOAD)
        self.assertIn("UNKNOWN",ORIGINAL_MOUSE_MOVE_THROTTLE)
        self.assertIn("LOCAL",SCALING_ROUNDING)

    def test_exact_ratio_integer_sizes(self):
        self.assertEqual(scale_client_point(
            100,50,ClientSize(400,200),ClientSize(800,500)),(200,125))

    def test_non_uniform_client_sizes(self):
        self.assertEqual(scale_client_point(
            50,100,ClientSize(100,200),ClientSize(280,300)),(140,150))

    def test_local_floor_rule_distinguished_from_original(self):
        self.assertEqual(scale_client_point(
            1,1,ClientSize(3,3),ClientSize(5,5)),(1,1))

    def test_last_valid_master_point_clamped_inside_slave(self):
        self.assertEqual(scale_client_point(
            99,49,ClientSize(100,50),ClientSize(1,1)),(0,0))

    def test_negative_and_boundary_outside_master_fail(self):
        for x,y in [(-1,3),(1,-1),(100,0),(0,50)]:
            with self.subTest(x=x,y=y),self.assertRaises(ValueError):
                scale_client_point(x,y,ClientSize(100,50),ClientSize(200,100))

    def test_bad_client_rect_fail_closed(self):
        for w,h in [(0,1),(1,0),(-1,2),(3.2,5),(True,10)]:
            with self.subTest(w=w,h=h),self.assertRaises(ValueError):
                ClientSize(w,h)

    def test_invalid_coordinates_types_are_rejected(self):
        for x,y in [(1.2,1),(True,2),("2",4),(None,1)]:
            with self.subTest(x=x,y=y),self.assertRaises(ValueError):
                scale_client_point(x,y,ClientSize(5,5),ClientSize(8,8))


class S19Session(unittest.TestCase):
    def test_valid_three_window_snapshot_does_not_send_by_itself(self):
        s=activated()
        self.assertTrue(s.active)
        self.assertEqual(s.slaves,((22,10022),(33,10033)))
        self.assertEqual(s.pending,0)

    def test_cannot_enable_without_true_verified_limit(self):
        for limit in (0,-1,1,2,None,True,"3"):
            m=InputSyncModel()
            self.assertFalse(m.start(snap(*ROWS),MASTER,max_windows=limit))
            self.assertFalse(m.active)

    def test_invalid_empty_or_duplicate_snapshots_reject(self):
        for w in [snap(valid=False),snap(),snap(ROWS[0]),
                  snap(ROWS[0],ROWS[0]),
                  snap(ROWS[0],row(11,9999))]:
            with self.subTest(w=w):
                m=InputSyncModel()
                self.assertFalse(m.start(w,MASTER,max_windows=9))

    def test_unverified_other_app_cache_rejected(self):
        fake=GameWindow(44,10044,"random","TkTop","python.exe")
        m=InputSyncModel()
        self.assertFalse(m.start(snap(ROWS[0],fake),MASTER,max_windows=3))

    def test_master_hwnd_pid_must_be_current(self):
        for master in [(11,12345),(50,10050),(0,0),(22,0)]:
            with self.subTest(master=master):
                self.assertFalse(InputSyncModel().start(
                    snap(*ROWS),master,max_windows=3))

    def test_queue_does_not_dispatch_to_any_sink_on_enqueue(self):
        s=activated()
        self.assertEqual(s.queue_mouse(100,75,button="left",pressed=True,
                                     sizes=SIZES,now=1.0),2)
        self.assertEqual(s.pending,2)
        self.assertEqual(s.planned_buttons,frozenset({"left"}))

    def test_down_up_FIFO_across_two_slaves(self):
        s=activated()
        self.assertEqual(s.queue_mouse(100,75,button="left",pressed=True,
                                      sizes=SIZES,now=1),2)
        self.assertEqual(s.queue_mouse(100,75,button="left",pressed=False,
                                      sizes=SIZES,now=2),2)
        got=flush(s)
        self.assertEqual([(e.target[0],e.action) for e in got],
                         [(22,"down"),(33,"down"),(22,"up"),(33,"up")])
        self.assertEqual([e.sequence for e in got],[1,2,3,4])
        self.assertEqual([(e.x,e.y) for e in got[:2]],[(131,100),(162,125)])
        self.assertEqual(s.pending,0)
        self.assertFalse(s.planned_buttons)

    def test_repeated_down_and_orphan_up_are_ignored(self):
        s=activated()
        self.assertEqual(s.queue_mouse(0,0,button="left",pressed=False,
                                      sizes=SIZES,now=0),0)
        self.assertEqual(s.queue_mouse(0,0,button="left",pressed=True,
                                      sizes=SIZES,now=0),2)
        self.assertEqual(s.queue_mouse(0,0,button="left",pressed=True,
                                      sizes=SIZES,now=1),0)
        self.assertEqual(s.pending,2)

    def test_three_mouse_buttons_supported_unknown_one_rejected(self):
        s=activated()
        for b in ("left","middle","right"):
            self.assertEqual(s.queue_mouse(0,0,button=b,pressed=True,
                                          sizes=SIZES,now=1),2)
            self.assertEqual(s.queue_mouse(0,0,button=b,pressed=False,
                                          sizes=SIZES,now=2),2)
        self.assertEqual(s.queue_mouse(0,0,button="xbutton",pressed=True,
                                      sizes=SIZES,now=3),0)

    def test_missing_slave_dimensions_denies_whole_batch(self):
        s=activated()
        missing={MASTER:ClientSize(400,300),(22,10022):ClientSize(100,100)}
        self.assertEqual(s.queue_mouse(10,10,button="left",pressed=True,
                                      sizes=missing,now=1),0)
        self.assertEqual(s.pending,0)
        self.assertFalse(s.planned_buttons)

    def test_outside_master_denies_whole_batch(self):
        s=activated()
        self.assertEqual(s.queue_mouse(400,0,button="left",pressed=True,
                                      sizes=SIZES,now=1),0)
        self.assertEqual(s.pending,0)

    def test_dispatch_requires_three_explicit_callbacks(self):
        s=activated()
        with self.assertRaises(ValueError):
            s.dispatch_one(sink=None,identity_ok=lambda a,b:True,
                           permission_ok=lambda:True)

    def test_revoke_before_dispatch_clears_all_no_events(self):
        s=activated()
        s.queue_mouse(1,2,button="left",pressed=True,sizes=SIZES,now=1)
        observed=[]
        result=s.dispatch_one(sink=observed.append,identity_ok=lambda a,b:True,
                              permission_ok=lambda:False)
        self.assertIsNone(result)
        self.assertEqual(observed,[])
        self.assertEqual(s.pending,0)
        self.assertFalse(s.active)

    def test_pid_reuse_on_second_target_blocks_remaining(self):
        s=activated()
        s.queue_mouse(1,2,button="left",pressed=True,sizes=SIZES,now=1)
        got=[]
        s.dispatch_one(sink=got.append,identity_ok=lambda a,b:True,
                       permission_ok=lambda:True)
        result=s.dispatch_one(sink=got.append,
                              identity_ok=lambda h,p:h != 33,
                              permission_ok=lambda:True)
        self.assertIsNone(result)
        self.assertEqual([e.target[0] for e in got],[22])
        self.assertEqual(s.last_stop,"REVOKED_OR_STALE_HWND")

    def test_master_change_clears_press_state_and_pending_queue(self):
        s=activated()
        s.queue_mouse(5,5,button="left",pressed=True,sizes=SIZES,now=1)
        old=s.generation
        s.master_changed((22,10022))
        self.assertFalse(s.active)
        self.assertIsNone(s.master)
        self.assertEqual(s.pending,0)
        self.assertFalse(s.planned_buttons)
        self.assertGreater(s.generation,old)

    def test_session_restart_discards_old_generation(self):
        s=activated()
        s.queue_mouse(5,5,button="left",pressed=True,sizes=SIZES,now=1)
        old=s.generation
        self.assertTrue(s.start(snap(*ROWS),MASTER,max_windows=3))
        self.assertGreater(s.generation,old)
        self.assertEqual(s.pending,0)

    def test_watchdog_below_10s_no_action_then_release_at_10(self):
        s=activated()
        s.queue_mouse(5,5,button="left",pressed=True,sizes=SIZES,now=100)
        self.assertFalse(s.watchdog(109.99))
        self.assertTrue(s.watchdog(110.0))
        self.assertFalse(s.active)
        self.assertEqual(s.last_stop,"WATCHDOG_LOGICAL_RELEASE")
        self.assertEqual(s.pending,0)

    def test_down_followed_by_up_clears_watchdog(self):
        s=activated()
        s.queue_mouse(5,5,button="left",pressed=True,sizes=SIZES,now=100)
        s.queue_mouse(5,5,button="left",pressed=False,sizes=SIZES,now=101)
        self.assertFalse(s.watchdog(900))

    def test_test_sink_exception_revokes_session(self):
        s=activated()
        s.queue_mouse(5,5,button="left",pressed=True,sizes=SIZES,now=1)
        def fail(_):
            raise RuntimeError("test adapter broken")
        with self.assertRaises(RuntimeError):
            s.dispatch_one(sink=fail,identity_ok=lambda a,b:True,
                           permission_ok=lambda:True)
        self.assertFalse(s.active)
        self.assertEqual(s.pending,0)
        self.assertEqual(s.last_stop,"TEST_SINK_EXCEPTION")

    def test_shutdown_idempotent_and_no_post_stop_callbacks(self):
        s=activated()
        s.queue_mouse(5,5,button="left",pressed=True,sizes=SIZES,now=1)
        s.stop("QUIT")
        s.stop("QUIT")
        called=[]
        self.assertIsNone(s.dispatch_one(
            sink=called.append,identity_ok=lambda a,b:True,
            permission_ok=lambda:True))
        self.assertEqual(called,[])

    def test_no_win32_input_sender_or_keyboard_payload_implemented(self):
        # Read-only Win32 geometry exists, but no raw input sender, listener,
        # input-sync toggle, or invented WM_MY_SYNC_KEY encoding in S19.
        self.assertFalse(hasattr(NativeClientRectReader,"post_click"))
        self.assertFalse(hasattr(InputSyncModel,"_toggle_input"))
        self.assertFalse(hasattr(InputSyncModel,"send_key"))
        self.assertFalse(hasattr(InputSyncModel,"register_mouse_listener"))


if __name__=="__main__":
    unittest.main()
