"""S78 original C03 DWM click-to-activate, destination HWND+source PID guarded."""
from __future__ import annotations
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"tests")]
from test_s11 import FakeDwmBackend,place
from dwm_preview import (ReadOnlyDwmPreviews,_DWM_CLICK_TARGETS,
                         _DWM_LEFT_MESSAGES,_dispatch_dwm_click)

class ClickBackend(FakeDwmBackend):
    def __init__(self):
        super().__init__()
        self.activations=[]
        self.fail_bind=False
    def bind_click_target(self,dst,hwnd,pid):
        self.events.append(("bind",dst,hwnd,pid))
        if self.fail_bind:
            raise OSError("TEST_BIND_FAILED")
        _DWM_CLICK_TARGETS[dst]=(self,hwnd,pid)
    def activate_source(self,hwnd):
        self.activations.append(hwnd)
        self.events.append(("activate",hwnd))
        return True
    def destroy_destination(self,dst):
        _DWM_CLICK_TARGETS.pop(dst,None)
        super().destroy_destination(dst)


class S78C03ActivationTests(unittest.TestCase):
    def tearDown(self):
        _DWM_CLICK_TARGETS.clear()

    def make(self):
        b=ClickBackend()
        s=ReadOnlyDwmPreviews(b)
        self.addCleanup(s.shutdown)
        self.assertEqual(s.sync([place()]).rendered,(41,))
        return b,s

    def test_01_original_exact_C03_left_mouse_message_tuple(self):
        self.assertEqual(_DWM_LEFT_MESSAGES,(513,514,515))

    def test_02_bind_after_native_register_not_before(self):
        b,s=self.make()
        names=[e[0] for e in b.events]
        self.assertLess(names.index("register"),names.index("bind"))
        self.assertIn((301,41,1001),
                      [(dst,hwnd,pid) for dst,(_b,hwnd,pid)
                       in _DWM_CLICK_TARGETS.items()])

    def test_03_left_down_up_double_click_dispatch_to_same_source(self):
        b,s=self.make()
        for msg in (513,514,515):
            self.assertTrue(_dispatch_dwm_click(301,msg))
        self.assertEqual(b.activations,[41,41,41])

    def test_04_keyboard_right_button_and_unmapped_destination_ignored(self):
        b,s=self.make()
        for msg in (0x0100,0x0204,0x0205):
            self.assertFalse(_dispatch_dwm_click(301,msg))
        self.assertFalse(_dispatch_dwm_click(99999,513))
        self.assertEqual(b.activations,[])

    def test_05_stale_source_reused_pid_never_activates_old_account(self):
        b,s=self.make()
        b.live[41]=7777
        self.assertTrue(_dispatch_dwm_click(301,513))
        self.assertEqual(b.activations,[])
        self.assertIn(("matches",41,1001),b.events)

    def test_06_vanished_source_ignores_click_even_if_target_still_mapped(self):
        b,s=self.make()
        del b.live[41]
        self.assertTrue(_dispatch_dwm_click(301,515))
        self.assertFalse(b.activations)

    def test_07_removed_destination_unmaps_before_repeat_click(self):
        b,s=self.make()
        s.clear()
        self.assertNotIn(301,_DWM_CLICK_TARGETS)
        self.assertFalse(_dispatch_dwm_click(301,513))

    def test_08_unchanged_native_slot_never_rebinds_or_reactivates(self):
        b,s=self.make()
        s.sync([place(x=20)])
        self.assertEqual(sum(e[0]=="bind" for e in b.events),1)
        self.assertEqual(b.activations,[])

    def test_09_owner_change_clears_old_mapping_and_binds_new(self):
        b,s=self.make()
        s.sync([place(owner=999)])
        self.assertFalse(_dispatch_dwm_click(301,513))
        self.assertIn(302,_DWM_CLICK_TARGETS)
        self.assertEqual(_DWM_CLICK_TARGETS[302][1:],(41,1001))

    def test_10_failed_click_binding_drops_partially_created_DWM(self):
        b=ClickBackend()
        b.fail_bind=True
        s=ReadOnlyDwmPreviews(b)
        self.addCleanup(s.shutdown)
        result=s.sync([place()])
        self.assertEqual(result.rendered,())
        self.assertEqual(s.active_hwnds,())
        self.assertNotIn(301,_DWM_CLICK_TARGETS)
        self.assertIn(("unregister",1301),b.events)
        self.assertIn(("destroy",301),b.events)

    def test_11_reused_HWND_new_PID_only_bound_after_old_release(self):
        b,s=self.make()
        b.live[41]=9999
        res=s.sync([place(pid=9999)])
        self.assertEqual(res.rendered,(41,))
        self.assertNotIn(301,_DWM_CLICK_TARGETS)
        self.assertEqual(_DWM_CLICK_TARGETS[302][1:],(41,9999))
        self.assertFalse(_dispatch_dwm_click(301,513))

    def test_12_no_game_input_injection_unverified_magic_button(self):
        text=(ROOT/"src/dwm_preview.py").read_text("utf-8")
        for bad in ("PostMessage(","CreateRemoteThread(","ReadProcessMemory(",
                    "SendInput(", "tk.Button(", "proxy_tab"):
            self.assertNotIn(bad,text)
        self.assertIn("SetForegroundWindow",text)
        self.assertIn("SW_RESTORE",text)


if __name__=="__main__":
    unittest.main()
