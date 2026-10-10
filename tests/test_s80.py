"""S80 C03: real native IsWindow/PID/IsHung + honest per-item red errors."""
from __future__ import annotations
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/"src"), str(ROOT/"tests")]
from dwm_preview import NativeDwmBackend, PreviewResult
from start_tab import TLMStartTab
from test_s15 import prepared, win


class DummyNative:
    """Invoke PRODUCTION native-only source_status with Win32 API fakes."""
    source_status = NativeDwmBackend.source_status
    def __init__(self):
        self.live = {51: 151}
        self.hung = set()
        self.calls = []
        self.w = SimpleNamespace(DWORD=lambda _:SimpleNamespace(value=0))
        self.ctypes = SimpleNamespace(byref=lambda x:x)
    def _is_window(self, hwnd):
        self.calls.append(("IsWindow", hwnd))
        return hwnd in self.live
    def _get_pid(self, hwnd, output):
        self.calls.append(("GetWindowThreadProcessId", hwnd))
        output.value = self.live[hwnd]
    def _hung(self, hwnd):
        self.calls.append(("IsHungAppWindow", hwnd))
        return hwnd in self.hung


class Label:
    def __init__(self):
        self.text=""
        self.visible=False
        self.options={}
    def configure(self, **kw):
        self.options.update(kw)
        self.text=kw.get("text",self.text)
    def place(self, **kw):
        self.visible=True
    def place_forget(self):
        self.visible=False

class Surface:
    def winfo_viewable(self):return True
    def winfo_width(self):return 197
    def winfo_height(self):return 110
    def winfo_rootx(self):return 30
    def winfo_rooty(self):return 35

class FakeSourceState:
    def __init__(self,values):
        self.states=values
    def source_status(self,hwnd,pid):
        return self.states.get((hwnd,pid),"LIVE")

class Controller:
    def __init__(self,states,errors=(),rendered=(1,2,3)):
        self.backend=FakeSourceState(states)
        self._errors=tuple(errors)
        self._rendered=tuple(rendered)
        self.calls=0
    def sync(self,placements):
        self.calls+=1
        return PreviewResult(self._rendered,self._errors)

def prepared_surface(states,errors=(),rendered=(1,2,3)):
    obj=prepared()
    obj.container.winfo_toplevel=lambda:SimpleNamespace(winfo_id=lambda:777)
    labels={}
    for item in obj._active_windows:
        label=Label()
        labels[item.hwnd]=label
        obj._tile_items[(item.hwnd,item.pid)]=(None,None,Surface(),None,None,label)
    obj._preview_controller=Controller(states,errors,rendered)
    return obj,labels


class S80OriginalC03ErrorTests(unittest.TestCase):
    def test_01_native_closed_never_claims_hung(self):
        backend=DummyNative()
        self.assertEqual(backend.source_status(51,151),"LIVE")
        backend.live.clear()
        backend.calls.clear()
        self.assertEqual(backend.source_status(51,151),"CLOSED")
        self.assertNotIn(("IsHungAppWindow",51),backend.calls)

    def test_02_native_hung_only_after_correct_PID(self):
        backend=DummyNative()
        backend.hung.add(51)
        self.assertEqual(backend.source_status(51,151),"HUNG")
        self.assertIn(("IsHungAppWindow",51),backend.calls)

    def test_03_reused_pid_never_falsely_claims_hung(self):
        backend=DummyNative()
        backend.hung.add(51)
        backend.calls.clear()
        self.assertEqual(backend.source_status(51,999),"STALE_PID")
        self.assertNotIn(("IsHungAppWindow",51),backend.calls)

    def test_04_invalid_ID_and_zero_PID_fail_closed(self):
        backend=DummyNative()
        self.assertEqual(backend.source_status(0,151),"CLOSED")
        self.assertEqual(backend.source_status(True,151),"CLOSED")
        self.assertEqual(backend.source_status(51,0),"STALE_PID")

    def test_05_true_hung_displays_original_text_only_on_bad_tile(self):
        obj,labels=prepared_surface({(2,1002):"HUNG"},
                         errors=((2,"STALE_CLOSED_OR_HUNG_SOURCE"),),rendered=(1,3))
        obj._refresh_dwm()
        self.assertTrue(labels[2].visible)
        self.assertEqual(labels[2].text,"Cửa sổ không phản hồi")
        self.assertFalse(labels[1].visible)
        self.assertFalse(labels[3].visible)

    def test_06_closed_displays_correct_original_prefix_not_hung(self):
        obj,labels=prepared_surface({(2,1002):"CLOSED"},
                         errors=((2,"STALE_CLOSED_OR_HUNG_SOURCE"),),rendered=(1,3))
        obj._refresh_dwm()
        self.assertTrue(labels[2].text.startswith("Đã đóng cửa sổ: "))
        self.assertNotIn("không phản hồi",labels[2].text)

    def test_07_recycled_pid_is_no_longer_old_source(self):
        obj,labels=prepared_surface({(2,1002):"STALE_PID"},
                         errors=((2,"STALE_CLOSED_OR_HUNG_SOURCE"),),rendered=(1,3))
        obj._refresh_dwm()
        self.assertTrue(labels[2].text.startswith("Đã đóng cửa sổ: "))

    def test_08_unclassified_native_DWM_error_not_mislabelled_hung(self):
        obj,labels=prepared_surface({(2,1002):"LIVE"},
                         errors=((2,"DWM_FAIL"),),rendered=(1,3))
        obj._refresh_dwm()
        self.assertEqual(labels[2].text,"Preview lỗi: DWM")

    def test_09_absent_classifier_is_generic_not_fabricated_hung(self):
        obj,labels=prepared_surface({},
                         errors=((2,"DWM_FAIL"),),rendered=(1,3))
        obj._preview_controller.backend=object()
        obj._refresh_dwm()
        self.assertEqual(labels[2].text,"Preview lỗi: DWM")

    def test_10_recovered_DWM_slot_hides_error_without_destroy(self):
        obj,labels=prepared_surface({(2,1002):"HUNG"},
                         errors=((2,"STALE_CLOSED_OR_HUNG_SOURCE"),),rendered=(1,3))
        obj._refresh_dwm()
        self.assertTrue(labels[2].visible)
        obj._preview_controller._errors=()
        obj._preview_controller._rendered=(1,2,3)
        obj._refresh_dwm()
        self.assertFalse(labels[2].visible)

    def test_11_more_than_one_bad_slot_each_has_independent_error(self):
        obj,labels=prepared_surface({(2,1002):"HUNG",(3,1003):"CLOSED"},
                         errors=((2,"HUNG"),(3,"CLOSED")),rendered=(1,))
        obj._refresh_dwm()
        self.assertEqual(labels[2].text,"Cửa sổ không phản hồi")
        self.assertTrue(labels[3].text.startswith("Đã đóng cửa sổ: "))
        self.assertFalse(labels[1].visible)

    def test_12_original_red_color_and_no_guessed_HP_or_role_reader(self):
        source=(ROOT/"src/start_tab.py").read_text("utf-8")
        self.assertIn('fg="#ff5555"',source)
        self.assertIn('"Cửa sổ không phản hồi"',source)
        self.assertIn('"Đã đóng cửa sổ: "',source)
        self.assertNotIn("ReadProcessMemory(",source)
        self.assertNotIn("CreateRemoteThread(",source)

    def test_13_destroyed_fixture_without_error_label_remains_compatible(self):
        obj=prepared()
        obj._set_preview_source_error((1,1001),"Cửa sổ không phản hồi")
        self.assertEqual(len(obj._tile_items),3)

    def test_14_no_background_native_wake_or_game_actions(self):
        source=(ROOT/"src/dwm_preview.py").read_text("utf-8")
        for token in ("SendInput(","PostMessage(","ReadProcessMemory(",
                      "CreateRemoteThread(", "proxy_tab"):
            self.assertNotIn(token,source)
        self.assertIn("def source_status(self, hwnd: int, pid: int)",source)

if __name__=="__main__":unittest.main()
