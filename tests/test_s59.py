"""S59 measured original Auto controls dispatch the existing S56 workers.

The test adapter records Tk widget construction; real Tk geometry, button
invoke and real SetWindowPos are checked by the Windows S59 smoke.
"""
from pathlib import Path
import hashlib
import sys
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from start_tab import TLMStartTab


class Widget:
    def __init__(self, parent, **kwargs):
        self.parent, self.options = parent, kwargs
        self.placement = {}
    def pack(self, **kwargs):
        self.packing = kwargs
    def place(self, **kwargs):
        self.placement = kwargs
    def invoke(self):
        return self.options['command']()


class S59MeasuredQuickControls(unittest.TestCase):
    def build(self):
        view = object.__new__(TLMStartTab)
        view.container = object()
        calls = []
        view._stack_tight_cmd = lambda: calls.append('tight') or True
        view._stack_diagonal_cmd = lambda: calls.append('diagonal') or False
        self.assertTrue(hasattr(view, '_build_verified_auto_controls'),
                        'S59 measured Auto controls not built')
        with patch.dict(sys.modules, {
            'tkinter': SimpleNamespace(Frame=Widget, Button=Widget,
                ttk=SimpleNamespace(LabelFrame=Widget, Style=lambda _:
                    SimpleNamespace(configure=lambda *a, **k: None))),
        }):
            view._build_verified_auto_controls()
        return view, calls

    def test_reference_bytes_are_the_frozen_b14_original(self):
        data = (ROOT / 'docs/ui/original/START_AUTO.png').read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(),
                         '4f1b126ea4ba0034889545653046f552a226d5f0033d2329a8693342184c28cd')

    def test_buttons_invoke_existing_callbacks_and_preserve_rejection(self):
        view, calls = self.build()
        self.assertTrue(view.btn_stack_tight.invoke())
        self.assertFalse(view.btn_stack_diagonal.invoke())
        self.assertEqual(calls, ['tight', 'diagonal'])

    def test_measured_rectangles_and_original_style(self):
        view, _ = self.build()
        self.assertEqual(view.auto_frame.placement,
                         dict(x=4, y=56, width=428, height=188))
        for button, x, label in (
            (view.btn_stack_tight, 165, 'Xếp gọn'),
            (view.btn_stack_diagonal, 245, 'Xếp chéo'),
        ):
            self.assertEqual(button.placement,
                             dict(x=x, y=22, width=78, height=21,
                                  bordermode='outside'))
            self.assertEqual(button.options['text'], label)
            self.assertEqual(button.options['bg'], '#4169e1')
            self.assertEqual(button.options['fg'], 'white')
            self.assertEqual(button.options['font'], ('Segoe UI', 8, 'bold'))
            self.assertEqual(button.options['relief'], 'raised')
            self.assertEqual(button.options['bd'], 1)

    def test_no_toggle_or_game_action_is_fabricated(self):
        view, _ = self.build()
        self.assertFalse(hasattr(view, 'btn_hide_windows'))
        self.assertFalse(hasattr(view, 'mode_var'))
        self.assertFalse(hasattr(view, 'btn_login'))


class S59MoverExclusion(unittest.TestCase):
    def test_stack_then_grid_cannot_start_a_second_native_mover(self):
        import test_s56
        fixture = test_s56.S56StartDispatch()
        fixture.setUp()
        view = fixture.obj
        entered, release = threading.Event(), threading.Event()
        started_grid = []
        view._stack_service_factory = lambda: test_s56.FakeService(
            fixture.seen, entered, release)
        view.grid_cols, view.grid_rows = 2, 2
        view.btn_layout = view.layout_status = SimpleNamespace(configure=lambda **_: None)
        view._layout_worker = lambda _: started_grid.append(True)
        try:
            self.assertTrue(view._stack_tight_cmd())
            self.assertTrue(entered.wait(1))
            self.assertFalse(view._toggle_layout(), 'grid must wait for native stack exit')
            self.assertFalse(view.layout_active)
            self.assertEqual(started_grid, [])
        finally:
            release.set()
            fixture.tearDown()

    def test_stopped_grid_still_in_native_call_blocks_stack_until_exit(self):
        import test_s56
        fixture = test_s56.S56StartDispatch()
        fixture.setUp()
        view = fixture.obj
        release = threading.Event()
        view._layout_thread = threading.Thread(target=lambda: release.wait(2))
        view._layout_thread.start()
        try:
            self.assertFalse(view.layout_active)  # cancellation requested already
            self.assertFalse(view._stack_diagonal_cmd(), 'native grid has not exited yet')
            self.assertIsNone(view._stack_thread)
            release.set()
            view._layout_thread.join(1)
            self.assertTrue(view._stack_diagonal_cmd())
        finally:
            release.set()
            view._layout_thread.join(1)
            fixture.tearDown()


if __name__ == '__main__':
    unittest.main()
