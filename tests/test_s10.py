"""S10 pure read-only view state + shell authorization boundaries."""
from __future__ import annotations
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from start_polling import StartCacheEvent, WindowSnapshot
from start_windows import GameWindow, WindowDelta
from start_tab import StartReadOnlyState, StartWindowRow, readonly_state, TLMStartTab
from shell import TabLifecycle, TAB_SPECS


def game(hwnd=301, pid=901, title="Tài khoản thực (test only)"):
    return GameWindow(hwnd, pid, title, "UnityWndClass", "thần long mobile.exe")


class S10ReadOnlyStateTests(unittest.TestCase):
    def test_pending_is_not_fabricated_as_empty(self):
        state = readonly_state(WindowSnapshot())
        self.assertEqual(state.code, "PENDING")
        self.assertEqual(state.rows, ())

    def test_empty_only_after_valid_enumeration(self):
        state = readonly_state(WindowSnapshot(2, (), True))
        self.assertEqual(state.code, "EMPTY")
        self.assertEqual(state.rows, ())

    def test_error_never_leaks_old_handle(self):
        state = readonly_state(WindowSnapshot(3, (game(),), False,
                                              error="ENUMERATION_ERROR"))
        self.assertEqual(state.code, "ERROR")
        self.assertEqual(state.rows, ())

    def test_real_cache_values_are_preserved_not_character_names(self):
        state = readonly_state(WindowSnapshot(5, (game(title="Custom game title"),), True))
        self.assertEqual(state.code, "LIVE")
        self.assertEqual(state.rows, (StartWindowRow(301, 901, "Custom game title"),))
        self.assertNotIn("HP", state.caption)

    def test_two_hwnds_and_same_process_are_distinct(self):
        state = readonly_state(WindowSnapshot(
            4, (game(100, 99), game(101, 99)), True))
        self.assertEqual([(r.hwnd, r.pid) for r in state.rows],
                         [(100, 99), (101, 99)])

    def test_pid_reuse_is_not_substituted_with_previous_identity(self):
        old = readonly_state(WindowSnapshot(1, (game(10, 20),), True))
        new = readonly_state(WindowSnapshot(2, (game(10, 30),), True))
        self.assertNotEqual(old.rows, new.rows)
        self.assertEqual(new.rows[0].pid, 30)

    def test_no_default_start_grant_even_with_real_factory(self):
        frames = {spec.key: object() for spec in TAB_SPECS}
        class Info: pass
        factory_called = []
        def start_factory(frame):
            factory_called.append(frame)
            return object()
        lifecycle = TabLifecycle(
            {"info_tab": lambda frame: Info(), "start_tab": start_factory}, frames)
        self.assertEqual(lifecycle.visible, {"info_tab"})
        lifecycle.select("start_tab")
        self.assertFalse(factory_called)
        lifecycle.shutdown()

    def test_deny_after_grant_falls_back_to_info(self):
        frames = {spec.key: object() for spec in TAB_SPECS}
        class Info: pass
        class Start:
            def __init__(self): self.starts = 0; self.stops = 0
            def _start_refresh(self): self.starts += 1
            def _stop_refresh(self): self.stops += 1
        item = Start()
        lifecycle = TabLifecycle(
            {"info_tab": lambda frame: Info(), "start_tab": lambda frame: item}, frames)
        lifecycle.apply_authorized_keys({"start_tab"})  # test-only trusted adapter
        lifecycle.select("start_tab")
        self.assertEqual(item.starts, 1)
        lifecycle.apply_authorized_keys(set(), blocked=True)
        self.assertEqual(lifecycle.current, "info_tab")
        self.assertEqual(item.stops, 1)
        lifecycle.shutdown()

    def test_view_exposes_no_click_action_methods(self):
        forbidden = (
            "_activate_game_window", "_toggle_input", "_toggle_layout",
            "_arrange_grid", "_register_dwm_thumbnail", "_on_master_change",
        )
        for name in forbidden:
            self.assertFalse(hasattr(TLMStartTab, name), name)

    def test_cache_event_presentation_is_noninteractive(self):
        event = StartCacheEvent(
            WindowSnapshot(7, (game(16, 29),), True),
            WindowDelta((game(16, 29),), (), ()),
        )
        self.assertEqual(readonly_state(event.snapshot).rows[0].hwnd, 16)


if __name__ == "__main__":
    unittest.main()
