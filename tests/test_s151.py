"""S151 original F01 account Canvas mousewheel - blank/header parity gap."""
from __future__ import annotations
import ast
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from login_account_rows import TLMAccountRows, MAX_ACCOUNT_ROWS


class CanvasStub:
    def __init__(self): self.calls=[]
    def yview_scroll(self, steps, units): self.calls.append((steps, units))


class S151ScopedAccountWheel(unittest.TestCase):
    @staticmethod
    def source():
        return (ROOT/"src"/"login_account_rows.py").read_text(encoding="utf-8")

    def test_01_actual_original_100_row_canvas_capacity_unchanged(self):
        self.assertEqual(MAX_ACCOUNT_ROWS,100)

    def test_02_empty_canvas_inner_frame_has_real_wheel_binding(self):
        self.assertIn('self.rows_inner.bind("<MouseWheel>", self._scroll_wheel, add="+")',self.source())

    def test_03_header_selector_has_real_wheel_binding(self):
        self.assertIn('self.header_selector.bind("<MouseWheel>", self._scroll_wheel, add="+")',self.source())

    def test_04_all_five_actual_labels_get_scoped_wheel_handler(self):
        s=self.source()
        self.assertIn('heading.bind("<MouseWheel>", self._scroll_wheel, add="+")',s)
        for label in ("Tài khoản","Mật khẩu","Ẩn captcha","Login","Proxy"):
            self.assertIn('"'+label+'"',s)

    def test_05_no_global_mouse_hook_for_other_tabs(self):
        s=self.source()
        self.assertNotIn("bind_all(",s)
        self.assertNotIn("unbind_all(",s)
        self.assertNotIn("mouse.Listener(",s)
        self.assertNotIn("pyautogui.",s)

    def test_06_negative_native_wheel_scrolls_down_exactly_one_unit(self):
        x=TLMAccountRows.__new__(TLMAccountRows)
        x._closed=False
        x.canvas=CanvasStub()
        self.assertEqual(x._scroll_wheel(SimpleNamespace(delta=-120)),"break")
        self.assertEqual(x.canvas.calls,[(1,"units")])

    def test_07_positive_native_wheel_scrolls_up_exactly_one_unit(self):
        x=TLMAccountRows.__new__(TLMAccountRows)
        x._closed=False
        x.canvas=CanvasStub()
        self.assertEqual(x._scroll_wheel(SimpleNamespace(delta=120)),"break")
        self.assertEqual(x.canvas.calls,[(-1,"units")])

    def test_08_zero_native_delta_does_not_move_canvas(self):
        x=TLMAccountRows.__new__(TLMAccountRows)
        x._closed=False
        x.canvas=CanvasStub()
        self.assertEqual(x._scroll_wheel(SimpleNamespace(delta=0)),"break")
        self.assertEqual(x.canvas.calls,[])

    def test_09_closed_account_tab_never_scrolls(self):
        x=TLMAccountRows.__new__(TLMAccountRows)
        x._closed=True
        x.canvas=CanvasStub()
        self.assertEqual(x._scroll_wheel(SimpleNamespace(delta=-120)),"break")
        self.assertEqual(x.canvas.calls,[])

    def test_10_no_configuration_password_or_proxy_new_write(self):
        s=self.source()
        for forbidden in ('write_settings(', 'save_accounts(', 'CreateProcessW(', 'ProxyTab('):
            self.assertNotIn(forbidden,s)

    def test_11_source_remains_python_compilable(self):
        ast.parse(self.source())

    def test_12_original_entry_widgets_still_have_same_wheel_handler(self):
        self.assertIn('widget.bind("<MouseWheel>",self._scroll_wheel,add="+")',
                      self.source())


if __name__=="__main__":unittest.main()
