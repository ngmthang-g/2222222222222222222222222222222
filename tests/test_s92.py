"""S92 G03 RoleName evidence blocker + G09 real Python Event/thread lifecycle.

All action executors and authorizers below are TEST-OWNED injected
callbacks. No real TLM/game data, packet, entitlement or window interaction.
"""
from __future__ import annotations
from pathlib import Path
import sys
import threading
import time
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from party_action_coordinator import PartyJob, PartyRunCoordinator


def job(n,*names):
    return PartyJob(n,tuple(names))


class Captured:
    def __init__(self):
        self.started=[]
        self.release=threading.Event()
        self.ready=threading.Event()
        self.guard=threading.Lock()
        self.calls=0

    def execute(self,j,cancel):
        with self.guard:
            self.started.append(j.number)
            self.calls+=1
            self.ready.set()
        while not cancel.is_set() and not self.release.wait(.01):
            pass
        return self.release.is_set() and not cancel.is_set()

    def allow(self,operation,count):
        return operation=="party" and count>=2

    def wait_count(self,count=1):
        deadline=time.monotonic()+2
        while time.monotonic()<deadline:
            with self.guard:
                if len(self.started)>=count:
                    return True
            time.sleep(.005)
        return False


class S92CoordinatorTests(unittest.TestCase):
    def test_01_natural_missing_protocol_is_blocked(self):
        c=PartyRunCoordinator(permission=lambda op,n:True)
        self.assertEqual(c.start_single(job(1,"A","B")),"TEAM_PROTOCOL_UNAVAILABLE")
        self.assertEqual(c.snapshot().running_single,())

    def test_02_missing_signed_permission_is_blocked(self):
        c=PartyRunCoordinator(execute=lambda j,e:True)
        self.assertEqual(c.start_global((job(1,"A","B"),)),"SIGNED_PERMISSION_UNAVAILABLE")
        self.assertEqual(c.snapshot().global_state,"IDLE")

    def test_03_explicit_denial_fails_closed(self):
        c=PartyRunCoordinator(execute=lambda j,e:True,permission=lambda op,n:False)
        self.assertEqual(c.start_single(job(1,"A","B")),"PERMISSION_DENIED")

    def test_04_non_boolean_trust_result_does_not_grant(self):
        c=PartyRunCoordinator(execute=lambda j,e:True,permission=lambda op,n:"allowed")
        self.assertEqual(c.start_single(job(1,"A","B")),"PERMISSION_DENIED")

    def test_05_permission_exception_fails_closed(self):
        def bad(op,n):raise OSError("no signed issuer")
        c=PartyRunCoordinator(execute=lambda j,e:True,permission=bad)
        self.assertEqual(c.start_single(job(1,"A","B")),"PERMISSION_ERROR")

    def test_06_no_global_selected_groups_stays_idle(self):
        c=PartyRunCoordinator(execute=lambda j,e:True,permission=lambda op,n:True)
        self.assertEqual(c.start_global(()),"NO_GROUPS_SELECTED")
        self.assertEqual(c.snapshot().global_state,"IDLE")

    def test_07_no_duplicate_group_id_and_no_double_run(self):
        c=PartyRunCoordinator(execute=lambda j,e:True,permission=lambda op,n:True)
        self.assertEqual(c.start_global((job(1,"A"),job(1,"B"))),"DUPLICATE_GROUP")

    def test_08_single_requires_two_members(self):
        c=PartyRunCoordinator(execute=lambda j,e:True,permission=lambda op,n:True)
        self.assertEqual(c.start_single(job(1,"A")),"AT_LEAST_TWO_MEMBERS")
        self.assertEqual(c.snapshot().running_single,())

    def test_09_global_parallel_clusters_and_post_action_exactly_once(self):
        fixture=Captured()
        post=[]
        c=PartyRunCoordinator(
            execute=fixture.execute,permission=fixture.allow,
            after_party=lambda:post.append(tuple(fixture.started)))
        self.assertEqual(c.start_global((job(1,"A","B"),job(2,"C","D"))),"STARTED")
        self.assertTrue(fixture.wait_count(2))
        self.assertEqual(set(c.snapshot().active_groups),{1,2})
        self.assertEqual(post,[])
        fixture.release.set()
        self.assertTrue(c.wait_idle())
        self.assertEqual(len(post),1)
        self.assertEqual(set(post[0]),{1,2})
        self.assertEqual(c.snapshot().completed_global,1)
        self.assertEqual(c.snapshot().post_calls,1)

    def test_10_global_stop_cancels_each_child_without_post_action(self):
        fixture=Captured()
        post=[]
        c=PartyRunCoordinator(execute=fixture.execute,permission=fixture.allow,
                              after_party=lambda:post.append(True))
        self.assertEqual(c.start_global((job(1,"A","B"),job(2,"C","D"))),"STARTED")
        self.assertTrue(fixture.wait_count(2))
        self.assertEqual(c.stop_global(),"STOPPING")
        self.assertTrue(c.wait_idle())
        self.assertEqual(post,[])
        self.assertEqual(c.snapshot().post_calls,0)
        self.assertEqual(c.snapshot().global_state,"IDLE")

    def test_11_duplicate_single_guard(self):
        f=Captured()
        c=PartyRunCoordinator(execute=f.execute,permission=f.allow)
        self.assertEqual(c.start_single(job(1,"A","B")),"STARTED")
        self.assertTrue(f.wait_count(1))
        self.assertEqual(c.start_single(job(1,"A","B")),"ALREADY_RUNNING")
        c.stop_single(1)
        self.assertTrue(c.wait_idle())

    def test_12_independent_distinct_single_clusters(self):
        f=Captured()
        c=PartyRunCoordinator(execute=f.execute,permission=f.allow)
        self.assertEqual(c.start_single(job(1,"A","B")),"STARTED")
        self.assertEqual(c.start_single(job(2,"C","D")),"STARTED")
        self.assertTrue(f.wait_count(2))
        self.assertEqual(set(c.snapshot().running_single),{1,2})
        c.stop_single(1)
        c.stop_single(2)
        self.assertTrue(c.wait_idle())

    def test_13_same_group_overlap_single_then_global_blocked(self):
        f=Captured()
        c=PartyRunCoordinator(execute=f.execute,permission=f.allow)
        self.assertEqual(c.start_single(job(1,"A","B")),"STARTED")
        self.assertTrue(f.wait_count())
        self.assertEqual(c.start_global((job(1,"A","B"),)),
                         "SAME_GROUP_COLLISION_BLOCKED")
        c.stop_single(1)
        self.assertTrue(c.wait_idle())

    def test_14_same_group_overlap_global_then_single_blocked(self):
        f=Captured()
        c=PartyRunCoordinator(execute=f.execute,permission=f.allow)
        self.assertEqual(c.start_global((job(1,"A","B"),)),"STARTED")
        self.assertTrue(f.wait_count())
        self.assertEqual(c.start_single(job(1,"A","B")),
                         "SAME_GROUP_COLLISION_BLOCKED")
        c.stop_global()
        self.assertTrue(c.wait_idle())

    def test_15_stop_twice_or_not_running_never_issues_game_command(self):
        f=Captured()
        c=PartyRunCoordinator(execute=f.execute,permission=f.allow)
        self.assertEqual(c.stop_global(),"NOT_RUNNING")
        self.assertEqual(c.stop_single(1),"NOT_RUNNING")
        c.start_global((job(1,"A","B"),))
        self.assertTrue(f.wait_count())
        self.assertEqual(c.stop_global(),"STOPPING")
        self.assertIn(c.stop_global(),("ALREADY_STOPPING","NOT_RUNNING"))
        self.assertTrue(c.wait_idle())

    def test_16_close_revokes_all_and_new_runs_fail(self):
        f=Captured()
        c=PartyRunCoordinator(execute=f.execute,permission=f.allow)
        self.assertEqual(c.start_global((job(1,"A","B"),)),"STARTED")
        self.assertTrue(f.wait_count())
        c.close()
        self.assertTrue(c.wait_idle())
        self.assertEqual(c.start_single(job(2,"C","D")),"CLOSED")
        self.assertEqual(c.start_global((job(3,"E","F"),)),"CLOSED")

    def test_17_exception_in_executor_releases_group(self):
        c=PartyRunCoordinator(
            execute=lambda job,e: (_ for _ in ()).throw(RuntimeError("GAME_UNAVAILABLE")),
            permission=lambda op,n:True)
        self.assertEqual(c.start_global((job(1,"A","B"),)),"STARTED")
        self.assertTrue(c.wait_idle())
        self.assertEqual(c.snapshot().errors,(1,))

    def test_18_negative_timeout_invalid(self):
        c=PartyRunCoordinator()
        with self.assertRaises(ValueError):
            c.wait_idle(-.1)

    def test_19_job_rejects_duplicate_names_and_nonstring(self):
        with self.assertRaises(ValueError):job(1,"A","A")
        with self.assertRaises(ValueError):job(1,"")
        with self.assertRaises(ValueError):PartyJob(1,("A",17))
        with self.assertRaises(ValueError):PartyJob(0,("A",))

    def test_20_callback_receives_immutable_snapshots(self):
        f=Captured()
        states=[]
        c=PartyRunCoordinator(execute=f.execute,permission=f.allow,
                              on_change=lambda s:states.append(s))
        c.start_single(job(1,"A","B"))
        self.assertTrue(f.wait_count())
        c.stop_single(1)
        self.assertTrue(c.wait_idle())
        self.assertTrue(any(1 in s.running_single for s in states))
        self.assertEqual(c.snapshot().running_single,())

    def test_21_g03_reader_data_offset_not_fabricated(self):
        source=(ROOT/"src/party_action_coordinator.py").read_text("utf-8")
        for forbidden in ("ReadProcessMemory(", "WriteProcessMemory(",
                          "PostMessage(", "0x355B208", "0xB8", "200057",
                          "ROLEID_FAKE", "RoleName ="):
            self.assertNotIn(forbidden,source)

    def test_22_source_never_exposes_live_tk_action_controls(self):
        source=(ROOT/"src/party_action_coordinator.py").read_text("utf-8")
        self.assertNotIn("tk.Button(",source)
        self.assertNotIn("ttk.Button(",source)
        self.assertNotIn("socket.",source)


if __name__=="__main__":
    unittest.main()
