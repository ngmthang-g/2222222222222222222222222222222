"""S17 bounded C18 layout sync tests (all synthetic; never touch real windows)."""
from __future__ import annotations

import sys
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from layout_windows import (
    C18LayoutSync, LayoutResult, GRID_COLS_DEFAULT, GRID_ROWS_DEFAULT,
    ORIGINAL_GRID_FORMULA, ORIGINAL_LAYOUT_CADENCE,
)
from start_windows import GameWindow, GAME_PROCESS, GAME_TITLE, UNITY_WINDOW_CLASS
from start_polling import WindowSnapshot
from start_tab import TLMStartTab


def row(hwnd, pid=None):
    return GameWindow(hwnd, pid if pid is not None else 5000 + hwnd,
                      GAME_TITLE, UNITY_WINDOW_CLASS, GAME_PROCESS)


class Backend:
    def __init__(self, rows):
        self.rows = {r.hwnd: r for r in rows}
        self.positions = {r.hwnd: (30+i*48, 70+i*25, 150+i*48, 160+i*25)
                          for i, r in enumerate(rows)}
        self.moves = []
        self.desktop = (1800, 900)
        self.live_class = {}
        self.live_process = {}
        self.bumped_pid = {}
    def enumerate_top_level(self):
        return tuple(self.rows)
    def is_window(self, hwnd):
        return hwnd in self.rows
    def is_visible(self, hwnd):
        return True
    def process_id(self, hwnd):
        return self.bumped_pid.get(hwnd, self.rows[hwnd].pid)
    def process_executable(self, pid):
        return self.live_process.get(pid, GAME_PROCESS)
    def window_class(self, hwnd):
        return self.live_class.get(hwnd, UNITY_WINDOW_CLASS)
    def title_with_timeout(self, hwnd, ms):
        assert ms == 150
        return GAME_TITLE
    def window_rect(self, hwnd):
        return self.positions[hwnd]
    def screen_size(self):
        return self.desktop
    def move_no_resize(self, hwnd, x, y):
        old = self.positions[hwnd]
        w, h = old[2]-old[0], old[3]-old[1]
        self.positions[hwnd] = (x, y, x+w, y+h)
        self.moves.append((hwnd, x, y))
        return True


def snap(*rows, valid=True):
    return WindowSnapshot(7, tuple(rows), valid)


class S17PureLayout(unittest.TestCase):
    def test_original_defaults_but_unknown_geometry_are_explicit(self):
        self.assertEqual((GRID_COLS_DEFAULT, GRID_ROWS_DEFAULT), (3, 4))
        self.assertIn("UNKNOWN", ORIGINAL_GRID_FORMULA)
        self.assertIn("UNKNOWN", ORIGINAL_LAYOUT_CADENCE)

    def test_three_windows_arranged_in_default_grid_real_move_only(self):
        a = [row(10), row(20), row(30)]
        b = Backend(a)
        r = C18LayoutSync(b).arrange(snap(*a), max_windows=3)
        self.assertEqual(r.code, "GRID_APPLIED")
        self.assertEqual(b.moves, [(10, 0, 0), (20, 128, 0), (30, 256, 0)])
        self.assertEqual({h:(v[2]-v[0],v[3]-v[1]) for h,v in b.positions.items()},
                         {10:(120,90),20:(120,90),30:(120,90)})

    def test_master_first_even_when_input_order_different(self):
        rows = [row(1),row(2),row(3),row(4)]
        b = Backend(rows)
        r = C18LayoutSync(b).arrange(snap(*rows), max_windows=4,
                                     cols=2,rows=2,master_hwnd=3)
        self.assertEqual(r.code, "GRID_APPLIED")
        self.assertEqual(b.positions[3][:2],(0,0))
        self.assertEqual(b.positions[1][:2],(128,0))
        self.assertEqual(b.positions[2][:2],(0,98))
        self.assertEqual(b.positions[4][:2],(128,98))

    def test_next_identical_sync_does_not_repeat_move(self):
        rows = [row(1),row(2)]
        b = Backend(rows)
        engine = C18LayoutSync(b)
        engine.arrange(snap(*rows), max_windows=2)
        b.moves.clear()
        r = engine.arrange(snap(*rows), max_windows=2)
        self.assertEqual(r.moved, ())
        self.assertEqual(r.unchanged, (1,2))
        self.assertEqual(b.moves, [])

    def test_external_window_move_is_recovered_on_next_pass(self):
        rows = [row(1),row(2)]
        b = Backend(rows)
        engine = C18LayoutSync(b)
        engine.arrange(snap(*rows), max_windows=2)
        b.positions[2] = (460,370,580,460)
        b.moves.clear()
        engine.arrange(snap(*rows), max_windows=2)
        self.assertEqual(b.moves, [(2,128,0)])

    def test_missing_limit_rejects_all_moves(self):
        rows=[row(1)]
        b=Backend(rows)
        for limit in (0,-1,True,None,"999"):
            with self.subTest(limit=limit):
                self.assertEqual(C18LayoutSync(b).arrange(
                    snap(*rows),max_windows=limit).code,"NO_VERIFIED_WINDOW_LIMIT")
        self.assertEqual(b.moves, [])

    def test_over_verified_limit_rejects_before_native_actions(self):
        rows=[row(1),row(2),row(3)]
        b=Backend(rows)
        self.assertEqual(C18LayoutSync(b).arrange(
            snap(*rows),max_windows=2).code,"OVER_VERIFIED_LIMIT")
        self.assertEqual(b.moves, [])

    def test_grid_capacity_fails_closed(self):
        rows=[row(i) for i in range(1,5)]
        b=Backend(rows)
        self.assertEqual(C18LayoutSync(b).arrange(
            snap(*rows),max_windows=4,cols=1,rows=3).code,
            "GRID_CAPACITY_EXCEEDED")
        self.assertEqual(b.moves, [])

    def test_invalid_cache_is_rejected(self):
        rows=[row(1)]
        b=Backend(rows)
        self.assertEqual(C18LayoutSync(b).arrange(
            snap(*rows,valid=False),max_windows=2).code,"INVALID_CACHE")
        self.assertEqual(b.moves, [])

    def test_cache_duplicate_fails_before_mutation(self):
        rows=[row(1)]
        b=Backend(rows)
        self.assertEqual(C18LayoutSync(b).arrange(
            snap(rows[0],rows[0]),max_windows=2).code,
            "INVALID_OR_AMBIGUOUS_CACHE")
        self.assertEqual(b.moves, [])

    def test_wrong_exe_cache_rejected(self):
        fake=GameWindow(1,5001,GAME_TITLE,UNITY_WINDOW_CLASS,"not-game.exe")
        b=Backend([fake])
        self.assertEqual(C18LayoutSync(b).arrange(
            snap(fake),max_windows=1).code,"INVALID_OR_AMBIGUOUS_CACHE")
        self.assertEqual(b.moves, [])

    def test_pid_change_any_source_rejects_whole_batch(self):
        rows=[row(1),row(2)]
        b=Backend(rows)
        b.bumped_pid[2]=90000
        self.assertEqual(C18LayoutSync(b).arrange(
            snap(*rows),max_windows=2).code,"STALE_OR_REUSED_PID")
        self.assertEqual(b.moves, [])

    def test_changed_live_exe_rejects(self):
        rows=[row(1)]
        b=Backend(rows)
        b.live_process[5001]="other.exe"
        self.assertEqual(C18LayoutSync(b).arrange(
            snap(*rows),max_windows=1).code,"LIVE_NOT_GAME")
        self.assertEqual(b.moves, [])

    def test_unlisted_hwnd_never_moves(self):
        rows=[row(1),row(2)]
        b=Backend(rows)
        del b.rows[2]
        self.assertEqual(C18LayoutSync(b).arrange(
            snap(*rows),max_windows=2).code,"STALE_NOT_TOP_LEVEL")
        self.assertEqual(b.moves, [])

    def test_screen_too_small_fails_all_before_move(self):
        rows=[row(1),row(2),row(3)]
        b=Backend(rows)
        b.desktop=(200,100)
        self.assertEqual(C18LayoutSync(b).arrange(
            snap(*rows),max_windows=3).code,"LOCAL_GRID_DOES_NOT_FIT_SCREEN")
        self.assertEqual(b.moves, [])

    def test_cancelled_before_work_never_moves(self):
        rows=[row(1)]
        b=Backend(rows)
        self.assertEqual(C18LayoutSync(b).arrange(
            snap(*rows),max_windows=1,allowed=lambda:False).code,"CANCELLED")
        self.assertEqual(b.moves, [])

    def test_revoke_after_one_move_stops_remaining(self):
        rows=[row(1),row(2),row(3)]
        b=Backend(rows)
        original=b.move_no_resize
        permit=[True]
        def move(hwnd,x,y):
            ok=original(hwnd,x,y)
            permit[0]=False
            return ok
        b.move_no_resize=move
        out=C18LayoutSync(b).arrange(
            snap(*rows),max_windows=3,allowed=lambda:permit[0])
        self.assertEqual(out.code,"CANCELLED")
        self.assertEqual(len(b.moves),1)

    def test_master_must_be_discovered(self):
        a=[row(1),row(2)]
        b=Backend(a)
        self.assertEqual(C18LayoutSync(b).arrange(
            snap(*a),max_windows=3,master_hwnd=999).code,"MASTER_NOT_IN_CACHE")

    def test_empty_and_invalid_grid(self):
        b=Backend([])
        self.assertEqual(C18LayoutSync(b).arrange(
            snap(),max_windows=3).code,"NO_WINDOWS")
        self.assertEqual(C18LayoutSync(b).arrange(
            snap(row(1)),max_windows=3,cols=0).code,"INVALID_GRID")


class S17StartWorker(unittest.TestCase):
    def bare(self,active=True,visible=True,limit=3):
        obj=object.__new__(TLMStartTab)
        obj._closed=False
        obj.layout_max_windows=limit
        obj.layout_active=False
        obj.sync_layout_running=False
        obj.sync_loop_id=0
        obj.layout_master_hwnd=None
        obj.grid_cols=3
        obj.grid_rows=4
        obj._layout_last_result=None
        obj._layout_thread=None
        obj._layout_service_factory=lambda:C18LayoutSync(Backend([row(1)]))
        import threading
        obj._layout_allow=threading.Event()
        obj.btn_layout=type("B",(),{"configure":lambda s,**kw:None})()
        obj.layout_status=type("L",(),{"configure":lambda s,**kw:None})()
        obj.container=type("V",(),{"winfo_viewable":lambda s:visible})()
        class Producer:
            def read_snapshot(self):return snap(row(1))
        obj.poller=type("P",(),{"active":active,"producer":Producer()})()
        return obj

    def test_missing_limit_prevents_toggle(self):
        obj=self.bare(limit=0)
        self.assertFalse(obj._toggle_layout())
        self.assertFalse(obj.layout_active)

    def test_hidden_start_prevents_toggle(self):
        obj=self.bare(visible=False)
        self.assertFalse(obj._toggle_layout())
        self.assertFalse(obj.layout_active)

    def test_switch_on_uses_background_thread_and_off_cancels(self):
        obj=self.bare()
        self.assertTrue(obj._toggle_layout())
        worker=obj._layout_thread
        self.assertTrue(worker is not None)
        worker.join(2)
        self.assertEqual(obj._layout_last_result.code,"GRID_APPLIED")
        self.assertFalse(obj._toggle_layout())
        self.assertFalse(obj._layout_allow.is_set())

    def test_revocation_zeroes_limit_and_stops_worker(self):
        obj=self.bare()
        obj._toggle_layout()
        obj.set_layout_max_windows(0)
        self.assertFalse(obj.layout_active)
        self.assertFalse(obj._layout_allow.is_set())
        self.assertEqual(obj.layout_max_windows,0)

    def test_existing_layout_turn_off_without_new_cache(self):
        obj=self.bare()
        obj.layout_active=True
        obj._layout_allow.set()
        self.assertFalse(obj._toggle_layout())
        self.assertFalse(obj._layout_allow.is_set())


if __name__=="__main__":
    unittest.main()
