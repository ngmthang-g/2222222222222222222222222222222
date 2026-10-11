"""S158 F05 original 25s serialized launch and same-PID HWND arrival tests."""
from __future__ import annotations
from pathlib import Path
import sys
import threading
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from login_pid_handoff import (
    F05SerializedHandoff,F05_HWND_TIMEOUT_SECONDS,F05_LOCAL_POLL_SECONDS,
)


class Clock:
    def __init__(self):self.now=0.0;self.waits=[]
    def time(self):return self.now
    def sleep(self,seconds):self.waits.append(seconds);self.now+=seconds


class S158LaunchPidArrival(unittest.TestCase):
    def make(self,fn,clock=None):
        c=clock or Clock()
        return F05SerializedHandoff(find_hwnd=fn,monotonic=c.time,wait=c.sleep),c

    def test_01_exact_original_timeout(self):
        self.assertEqual(F05_HWND_TIMEOUT_SECONDS,25)

    def test_02_launch_then_two_reads_then_actual_hwnd(self):
        events=[];reads=[None,888]
        w,c=self.make(lambda pid:(events.append(("read",pid)) or reads.pop(0)))
        result=w.launch_and_wait(lambda:events.append("spawn") or 321,allowed=lambda:True)
        self.assertEqual((result.code,result.pid,result.hwnd,result.polls),
                         ("PID_HWND_FOUND",321,888,2))
        self.assertEqual(events,["spawn",("read",321),("read",321)])
        self.assertEqual(c.waits,[F05_LOCAL_POLL_SECONDS])

    def test_03_window_never_arrives_hard_timeout_at_25s(self):
        w,c=self.make(lambda pid:None)
        r=w.launch_and_wait(lambda:44,allowed=lambda:True)
        self.assertEqual(r.code,"TIMEOUT_NO_PID_WINDOW")
        self.assertEqual(r.pid,44)
        self.assertLessEqual(c.now,25.0)
        self.assertGreaterEqual(c.now,24.999)
        self.assertEqual(r.polls,100)

    def test_04_unverified_info_refuses_to_run_spawn(self):
        called=[]
        w,_=self.make(lambda p:888)
        r=w.launch_and_wait(lambda:called.append(1) or 4,allowed=lambda:False)
        self.assertEqual(r.code,"NOT_AUTHORIZED")
        self.assertEqual(called,[])

    def test_05_missing_or_throwing_auth_refuses_spawn(self):
        w,_=self.make(lambda p:1)
        for a in (None,lambda:1,lambda:(_ for _ in ()).throw(OSError())):
            r=w.launch_and_wait(lambda:9,allowed=a)
            self.assertEqual(r.code,"NOT_AUTHORIZED")

    def test_06_revoked_after_launch_never_returns_hwnd(self):
        count=[0]
        def auth():
            count[0]+=1
            return count[0]<=3
        w,_=self.make(lambda p:99)
        r=w.launch_and_wait(lambda:4,allowed=auth)
        self.assertEqual(r.code,"AUTH_REVOKED")
        self.assertIsNone(r.hwnd)

    def test_07_cancel_before_launch_and_after_one_failed_lookup(self):
        w,_=self.make(lambda p:None)
        self.assertEqual(w.launch_and_wait(lambda:4,allowed=lambda:True,
                         cancelled=lambda:True).code,"CANCELLED")
        n=[0]
        def check():n[0]+=1;return n[0]>3
        r=w.launch_and_wait(lambda:4,allowed=lambda:True,cancelled=check)
        self.assertEqual(r.code,"CANCELLED")
        self.assertIsNone(r.hwnd)

    def test_08_invalid_spawn_result_fail_closed(self):
        w,_=self.make(lambda p:123)
        for pid in (None,0,-1,True,1.0,"42",0x100000000):
            with self.subTest(pid=pid):
                self.assertEqual(w.launch_and_wait(lambda:pid,allowed=lambda:True).code,
                                 "INVALID_SPAWN_PID")

    def test_09_launch_error_not_reinterpreted_as_success(self):
        w,_=self.make(lambda p:999)
        r=w.launch_and_wait(lambda:(_ for _ in ()).throw(OSError()),
                            allowed=lambda:True)
        self.assertEqual(r.code,"LAUNCH_CALLBACK_FAILED")

    def test_10_transient_window_lookup_error_can_recover(self):
        calls=[0]
        def probe(pid):
            calls[0]+=1
            if calls[0]==1:raise OSError("S158_TEST_WINDOW_NOT_YET_READY")
            return 900
        w,_=self.make(probe)
        self.assertEqual(w.launch_and_wait(lambda:4,allowed=lambda:True).hwnd,900)

    def test_11_wait_interrupt_returns_explicit_failure(self):
        c=Clock()
        def fail(secs):raise RuntimeError("TEST_ONLY_WAIT_CANCEL")
        w=F05SerializedHandoff(find_hwnd=lambda p:None,monotonic=c.time,wait=fail)
        self.assertEqual(w.launch_and_wait(lambda:4,allowed=lambda:True).code,
                         "WAIT_INTERRUPTED")

    def test_12_nonpositive_or_boolean_hwnd_never_valid(self):
        calls=[0]
        def probe(pid):
            calls[0]+=1
            return [True,-2,None,700][min(3,calls[0]-1)]
        w,_=self.make(probe)
        r=w.launch_and_wait(lambda:9,allowed=lambda:True)
        self.assertEqual((r.hwnd,r.polls),(700,4))

    def test_13_one_shared_lock_guards_entire_spawn_and_poll(self):
        # Lock is actually held through the first worker's first blocked
        # lookup, not just while invoking the caller-supplied spawn.
        lock=threading.Lock()
        in_poll=threading.Event();resume=threading.Event()
        order=[];out=[]
        def slow(pid):
            in_poll.set()
            if not resume.wait(2):raise TimeoutError()
            return 100+pid
        first=F05SerializedHandoff(launch_lock=lock,find_hwnd=slow)
        second=F05SerializedHandoff(launch_lock=lock,find_hwnd=lambda p:100+p)
        def work(obj,pid):
            r=obj.launch_and_wait(lambda:order.append(pid) or pid,allowed=lambda:True)
            out.append(r.code)
        a=threading.Thread(target=work,args=(first,11),daemon=True)
        bb=threading.Thread(target=work,args=(second,12),daemon=True)
        a.start()
        self.assertTrue(in_poll.wait(3))
        bb.start()
        # Verify the second spawn cannot start while first lookup is held.
        self.assertFalse(resume.is_set())
        self.assertEqual(order,[11])
        resume.set()
        a.join(3);bb.join(3)
        self.assertFalse(a.is_alive() or bb.is_alive())
        self.assertEqual(order,[11,12])
        self.assertEqual(sorted(out),["PID_HWND_FOUND","PID_HWND_FOUND"])

    def test_14_original_post_hwnd_stabilization_is_explicitly_unknown(self):
        src=(ROOT/"src/login_pid_handoff.py").read_text("utf-8")
        self.assertIn("stabilization",src)
        self.assertIn("UNKNOWN",src)
        self.assertNotIn("stabilization_seconds =",src)

    def test_15_no_original_game_inject_mouse_proxy_or_product_bypass(self):
        src=(ROOT/"src/login_pid_handoff.py").read_text("utf-8")
        for unsafe in ("subprocess.Popen(","CreateRemoteThread(","NtResumeProcess(",
                       "ReadProcessMemory(","SetWindowPos(","SendInput(",
                       "TLM_PROXY_ENABLE", "has_permission = True"):
            self.assertNotIn(unsafe,src)

if __name__=="__main__":unittest.main()
