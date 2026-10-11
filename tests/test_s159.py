"""S159 F05 original 1s Login-owned 1366×768 normalize, no jitter."""
from __future__ import annotations
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from login_resize_monitor import (
    F05LoginResizeMonitor,F05_LOGIN_RESIZE_INTERVAL_SECONDS,
    F05_LOGIN_TARGET_WIDTH,F05_LOGIN_TARGET_HEIGHT,
    F05_RESIZE_FLAGS_PARITY,
)
from start_polling import WindowSnapshot
from start_windows import GameWindow,GAME_PROCESS,GAME_TITLE,UNITY_WINDOW_CLASS


def win(hwnd=55,pid=981):
    return GameWindow(hwnd,pid,GAME_TITLE,UNITY_WINDOW_CLASS,GAME_PROCESS)

def snap(*rows,valid=True):
    return WindowSnapshot(5,tuple(rows),valid)

class Backend:
    def __init__(self,rows):
        self.rows={row.hwnd:row for row in rows}
        self.rects={row.hwnd:(45+i*230,62,45+i*230+700,62+420)
                    for i,row in enumerate(rows)}
        self.moves=[]
        self.override_exe={}
        self.override_title={}
        self.override_pid={}
        self.invisible=set()
        self.revoke_at_resize=None
    def enumerate_top_level(self):return tuple(self.rows)
    def is_window(self,h):return h in self.rows
    def is_visible(self,h):return h in self.rows and h not in self.invisible
    def process_id(self,h):return self.override_pid.get(h,self.rows[h].pid)
    def process_executable(self,p):return self.override_exe.get(p,GAME_PROCESS)
    def window_class(self,h):return self.rows[h].class_name
    def title_with_timeout(self,h,ms):
        self.test_last_title_timeout=ms
        return self.override_title.get(h,GAME_TITLE)
    def window_rect(self,h):return self.rects[h]
    def resize_no_move(self,h,w,he):
        if self.revoke_at_resize:self.revoke_at_resize()
        a,b,_,_=self.rects[h]
        self.rects[h]=(a,b,a+w,b+he)
        self.moves.append((h,w,he))
        return True

class S159F05SizeMonitor(unittest.TestCase):
    def make(self,rows):
        b=Backend(rows)
        return F05LoginResizeMonitor(b),b

    def test_01_exact_original_interval_and_dimensions(self):
        self.assertEqual((F05_LOGIN_RESIZE_INTERVAL_SECONDS,
                          F05_LOGIN_TARGET_WIDTH,F05_LOGIN_TARGET_HEIGHT),
                         (1.0,1366,768))

    def test_02_one_authentic_size_change_preserves_position(self):
        row=win()
        monitor,b=self.make([row])
        before=b.rects[row.hwnd][:2]
        r=monitor.normalize(snap(row),allowed=lambda:True,login_owned=lambda w:True)
        self.assertEqual((r.code,r.resized),("PASS",(row.hwnd,)))
        self.assertEqual(b.rects[row.hwnd],(*before,before[0]+1366,before[1]+768))
        self.assertEqual(b.moves,[(row.hwnd,1366,768)])

    def test_03_identical_size_never_calls_SetWindowPos_again(self):
        row=win()
        monitor,b=self.make([row])
        b.rects[row.hwnd]=(0,0,1366,768)
        for _ in range(3):
            x=monitor.normalize(snap(row),allowed=lambda:True,login_owned=lambda w:True)
            self.assertEqual(x.unchanged,(row.hwnd,))
        self.assertEqual(b.moves,[])

    def test_04_resize_once_then_no_jitter_on_next_1sec_tick(self):
        row=win()
        monitor,b=self.make([row])
        r1=monitor.normalize(snap(row),allowed=lambda:True,login_owned=lambda w:True)
        r2=monitor.normalize(snap(row),allowed=lambda:True,login_owned=lambda w:True)
        self.assertEqual(r1.resized,(55,))
        self.assertEqual(r2.unchanged,(55,))
        self.assertEqual(len(b.moves),1)

    def test_05_unverified_info_prevents_mutation(self):
        row=win()
        monitor,b=self.make([row])
        for permission in (None,lambda:False,lambda:1,
                           lambda:(_ for _ in ()).throw(AssertionError())):
            x=monitor.normalize(snap(row),allowed=permission,login_owned=lambda w:True)
            self.assertEqual(x.code,"NOT_AUTHORIZED")
        self.assertEqual(b.moves,[])

    def test_06_absent_Login_ownership_never_resizes(self):
        row=win()
        monitor,b=self.make([row])
        for owner in (None,lambda w:None,lambda w:False,
                      lambda w:(_ for _ in ()).throw(OSError())):
            x=monitor.normalize(snap(row),allowed=lambda:True,login_owned=owner)
            self.assertNotIn(row.hwnd,x.resized)
        self.assertEqual(b.moves,[])

    def test_07_only_verified_Login_owned_rows_changed(self):
        a,b=win(55),win(77,999)
        monitor,backend=self.make([a,b])
        x=monitor.normalize(snap(a,b),allowed=lambda:True,
                            login_owned=lambda w:w.hwnd==a.hwnd)
        self.assertEqual(x.resized,(a.hwnd,))
        self.assertEqual(x.skipped,(b.hwnd,))
        self.assertEqual(len(backend.moves),1)

    def test_08_wrong_actual_game_exe_title_and_PID_rejected(self):
        row=win()
        for mutate in ("exe","title","pid"):
            with self.subTest(mutate=mutate):
                monitor,b=self.make([row])
                if mutate=="exe":b.override_exe[row.pid]="python.exe"
                elif mutate=="title":
                    b.override_title[row.hwnd]="OTHER"
                    b.rows[row.hwnd]=GameWindow(row.hwnd,row.pid,"OTHER","OtherClass",GAME_PROCESS)
                else:b.override_pid[row.hwnd]=900
                x=monitor.normalize(snap(row),allowed=lambda:True,
                                    login_owned=lambda w:True)
                self.assertEqual(x.skipped,(row.hwnd,))
                self.assertEqual(b.moves,[])

    def test_09_reused_hidden_or_not_top_level_never_resized(self):
        row=win()
        for reason in ("hidden","removed"):
            monitor,b=self.make([row])
            if reason=="hidden":b.invisible.add(row.hwnd)
            else:b.rows.pop(row.hwnd)
            x=monitor.normalize(snap(row),allowed=lambda:True,
                                login_owned=lambda w:True)
            self.assertEqual(x.skipped,(row.hwnd,))
            self.assertEqual(b.moves,[])

    def test_10_bad_snapshot_and_duplicate_hwnds_fails_closed(self):
        a=win()
        monitor,b=self.make([a])
        self.assertEqual(monitor.normalize(snap(a,valid=False),
                         allowed=lambda:True,login_owned=lambda w:True).code,
                         "INVALID_CACHE")
        self.assertEqual(monitor.normalize(snap(a,a),
                         allowed=lambda:True,login_owned=lambda w:True).code,
                         "AMBIGUOUS_CACHE")
        self.assertEqual(b.moves,[])

    def test_11_revoke_permission_just_before_next_mutation(self):
        a,b=win(),win(77)
        mon,backend=self.make([a,b])
        calls=[0]
        def allow():
            calls[0]+=1
            return calls[0]<=4
        x=mon.normalize(snap(a,b),allowed=allow,login_owned=lambda w:True)
        self.assertIn(x.code,("AUTH_REVOKED","PASS"))
        self.assertLess(len(backend.moves),2)

    def test_12_live_PID_changes_after_rect_read_are_rejected(self):
        row=win()
        monitor,b=self.make([row])
        def rect(h):
            b.override_pid[h]=123456
            return (50,60,340,240)
        b.window_rect=rect
        x=monitor.normalize(snap(row),allowed=lambda:True,login_owned=lambda w:True)
        self.assertEqual(x.skipped,(row.hwnd,))
        self.assertFalse(b.moves)

    def test_13_original_flags_remain_explicit_UNKNOWN(self):
        self.assertIn("UNKNOWN",F05_RESIZE_FLAGS_PARITY)

    def test_14_worker_waits_exact_1s_and_stops_when_Info_lost(self):
        row=win()
        mon,b=self.make([row])
        class Stop:
            def __init__(self):self.wait_calls=[]
            def wait(self,seconds):
                self.wait_calls.append(seconds)
                return len(self.wait_calls)>1
        stop=Stop()
        calls=[0]
        def allowed():
            calls[0]+=1
            return calls[0]<=4
        mon.run_until_stopped(lambda:snap(row),allowed=allowed,
                              login_owned=lambda _:True,stop_event=stop)
        self.assertEqual(stop.wait_calls,[1.0,1.0])
        self.assertEqual(len(b.moves),1)

    def test_15_worker_missing_snapshot_callable_does_nothing(self):
        mon,b=self.make([win()])
        class Stop:
            def wait(self,s):raise AssertionError("unexpected timer")
        mon.run_until_stopped(None,allowed=lambda:True,login_owned=lambda _:True,
                              stop_event=Stop())
        self.assertEqual(b.moves,[])

    def test_16_no_game_input_injection_login_bypass_or_proxy(self):
        text=(ROOT/"src/login_resize_monitor.py").read_text("utf-8")
        for forbidden in ("CreateRemoteThread(","ReadProcessMemory(",
                          "SendInput(","subprocess.Popen(","TLM_PROXY_",
                          "has_permission = True","os.kill("):
            self.assertNotIn(forbidden,text)
        self.assertIn("SWP_NOMOVE",text)
        self.assertIn("backend.process_id(hwnd) != window.pid",text)

if __name__=="__main__":unittest.main()
