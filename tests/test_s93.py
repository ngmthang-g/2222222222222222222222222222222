"""S93 G09 Tk owner view-mode, fail-closed G10 and immutable state tests."""
from __future__ import annotations

from pathlib import Path
from queue import SimpleQueue
import sys
import threading
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from party_action_coordinator import PartyRunStatus
from party_tk_run_status import (
    PartyDisplay, TkPartyRunStatus, S93_TK_DRAIN_MS,
    RUNNING_COLOR, STOPPING_COLOR, UNVERIFIED_IDLE_COLOR, render_party_state,
)


def state(phase="IDLE", active=(), single=()):
    return PartyRunStatus(global_state=phase,active_groups=active,running_single=single)


class S93PureStateTests(unittest.TestCase):
    def test_01_exact_g09_running_state(self):
        a=render_party_state(state("RUNNING"),(1,),backend_diagnostic=True)
        self.assertEqual((a.code,a.global_text,a.global_color),
                         ("RUNNING","Dừng lại","#f44336"))

    def test_02_exact_g09_stopping_state(self):
        a=render_party_state(state("STOPPING"),(1,),backend_diagnostic=True)
        self.assertEqual((a.global_text,a.global_color),("Đang dừng...","#ef6c00"))

    def test_03_original_idle_color_token_unknown(self):
        a=render_party_state(state("IDLE"),(1,),backend_diagnostic=True)
        self.assertEqual(a.global_text,"Bắt đầu")
        self.assertIsNone(a.global_color)
        self.assertIsNone(UNVERIFIED_IDLE_COLOR)

    def test_04_absent_backend_explicit_unavailable(self):
        a=render_party_state(state("RUNNING",(1,)),(1,),backend_diagnostic=False)
        self.assertEqual(a.code,"UNAVAILABLE")
        self.assertIn("thiếu backend đội hoặc xác thực Info",a.global_text)
        self.assertEqual(a.groups,((1,"Không khả dụng"),))

    def test_05_default_diagnostic_not_live_game(self):
        self.assertEqual(
            render_party_state(state(),(1,2)).code,"UNAVAILABLE")

    def test_06_closed_clears_groups_and_old_running_state(self):
        a=render_party_state(
            state("RUNNING",(1,)),(1,2),backend_diagnostic=True,closed=True)
        self.assertEqual(a,PartyDisplay("CLOSED","Party đã đóng",None,()))

    def test_07_original_single_group_progress_label(self):
        a=render_party_state(state(single=(2,)),(1,2),backend_diagnostic=True)
        self.assertEqual(a.groups[0][1],"▶ Tạo nhóm 1 (chỉ xem)")
        self.assertEqual(a.groups[1][1],"⏳ Đang vào... (2)")

    def test_08_global_active_group_status_shown(self):
        a=render_party_state(
            state("RUNNING",active=(1,3)),(1,2,3),
            backend_diagnostic=True)
        self.assertEqual(tuple(n for n,t in a.groups if "⏳" in t),(1,3))

    def test_09_active_state_uses_real_membership(self):
        a=render_party_state(
            state("STOPPING",active=(4,),single=(3,)),
            (1,3,4),backend_diagnostic=True)
        self.assertEqual(tuple(n for n,t in a.groups if "⏳" in t),(3,4))

    def test_10_unknown_state_does_not_claim_success(self):
        a=render_party_state(state("CRASH"),(1,),backend_diagnostic=True)
        self.assertEqual(a.code,"UNKNOWN_STATE")

    def test_11_invalid_status_type_rejected(self):
        with self.assertRaises(ValueError):
            render_party_state({"global_state":"RUNNING"},(1,),backend_diagnostic=True)

    def test_12_group_numbers_cannot_be_duplicated(self):
        with self.assertRaises(ValueError):
            render_party_state(state(),(1,1),backend_diagnostic=True)

    def test_13_group_number_reject_bool_or_negative(self):
        for nums in ((True,),(0,),(-2,),("1",),[1]):
            with self.subTest(nums=nums),self.assertRaises(ValueError):
                render_party_state(state(),nums,backend_diagnostic=True)

    def test_14_original_state_color_constants_exact(self):
        self.assertEqual(RUNNING_COLOR,"#f44336")
        self.assertEqual(STOPPING_COLOR,"#ef6c00")

    def test_15_local_queue_timer_not_claimed_original(self):
        self.assertEqual(S93_TK_DRAIN_MS,50)
        source=(ROOT/"src/party_tk_run_status.py").read_text("utf-8")
        self.assertIn("NOT a verified original",source)

    def test_16_unavailable_even_with_multiple_unverified_window_rows(self):
        a=render_party_state(
            state("RUNNING",active=(1,2,3)),(1,2,3),
            backend_diagnostic=False)
        self.assertEqual(tuple(t for _,t in a.groups),
                         ("Không khả dụng",)*3)


class S93BridgeBoundaries(unittest.TestCase):
    def _uninitialized(self):
        obj=object.__new__(TkPartyRunStatus)
        obj._owner=threading.get_ident()
        obj._closed=False
        obj._epoch=7
        obj._queue=SimpleQueue()
        return obj

    def test_17_worker_callback_may_run_offthread_without_touching_tk(self):
        obj=self._uninitialized()
        error=[]
        def background():
            try:
                TkPartyRunStatus._worker_changed(obj,state("RUNNING"))
            except Exception as exc:
                error.append(exc)
        t=threading.Thread(target=background)
        t.start();t.join()
        self.assertEqual(error,[])
        self.assertEqual(obj._queue.get_nowait(),7)

    def test_18_late_notification_after_shutdown_does_not_enqueue(self):
        obj=self._uninitialized()
        obj._closed=True
        TkPartyRunStatus._worker_changed(obj,state("RUNNING"))
        self.assertTrue(obj._queue.empty())

    def test_19_direct_widget_mutation_from_worker_rejected(self):
        obj=self._uninitialized()
        errors=[]
        def background():
            try:TkPartyRunStatus._check_owner(obj)
            except Exception as exc:errors.append(exc)
        t=threading.Thread(target=background)
        t.start();t.join()
        self.assertEqual(len(errors),1)
        self.assertIsInstance(errors[0],RuntimeError)

    def test_20_do_not_expose_fake_party_buttons(self):
        source=(ROOT/"src/party_tk_run_status.py").read_text("utf-8")
        self.assertNotIn("ttk.Button(",source)
        self.assertNotIn("tk.Button(",source)

    def test_21_no_game_packet_memory_or_signed_issuer(self):
        source=(ROOT/"src/party_tk_run_status.py").read_text("utf-8")
        for forbidden in ("ReadProcessMemory(", "WriteProcessMemory(",
                          "PostMessage(", "CreateTeam(", "TOKEN_HMAC_SECRET",
                          "200057", "200051", "RoleID=1"):
            self.assertNotIn(forbidden,source)

    def test_22_status_not_mutated_to_authorize_game_actions(self):
        view=render_party_state(state("RUNNING"),(1,),backend_diagnostic=True)
        with self.assertRaises(Exception):
            view.code="AUTHORIZED"

if __name__=="__main__":
    unittest.main()
