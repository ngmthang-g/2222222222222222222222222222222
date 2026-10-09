"""S15: C15 full DWM preview rebuild from immutable S09 cache only."""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from preview_layout import PreviewOrder
from start_polling import WindowSnapshot
from start_tab import TLMStartTab, StartReadOnlyState, readonly_state
from start_windows import GameWindow


def win(hwnd, pid=None):
    return GameWindow(hwnd, pid or (1000 + hwnd),
                      f"TEST WINDOW {hwnd}", "ONLY_TEST", "NO_GAME.exe")


class Element:
    def __init__(self, events=None, name="frame"):
        self.events = events if events is not None else []
        self.name = name
        self.destroyed = False
        self.value = ""
    def destroy(self):
        self.events.append(("destroy_widget", self.name))
        self.destroyed = True
    def configure(self, **kwargs):
        self.value = kwargs.get("text", self.value)
    def winfo_viewable(self):
        return True
    def after_cancel(self, job):
        self.events.append(("after_cancel", job))


class Ctrl:
    def __init__(self, events):
        self.events = events
        self.shutdown_count = 0
    def shutdown(self):
        self.events.append(("unregister_and_destroy_native_DWM", None))
        self.shutdown_count += 1


class Producer:
    def __init__(self, snap):
        self.snap = snap
        self.reads = 0
        self.starts = 0
        self.scans = 0
    def read_snapshot(self):
        self.reads += 1
        if isinstance(self.snap, Exception):
            raise self.snap
        return self.snap


def prepared(rows=(win(1), win(2), win(3)), *, active=True, visible=True):
    obj = object.__new__(TLMStartTab)
    obj._closed = False
    obj.events = []
    obj.container = Element(obj.events, "container")
    obj.container.winfo_viewable = lambda: visible
    obj.preview_status = Element(obj.events, "preview_status")
    obj.preview_order = PreviewOrder()
    obj.preview_order.update(rows)
    obj._active_windows = tuple(rows)
    obj._observed_windows = tuple(rows)
    obj._tile_items = {
        (w.hwnd, w.pid): (Element(obj.events, f"tile-{w.hwnd}"), None, None)
        for w in rows
    }
    obj._preview_controller = Ctrl(obj.events)
    obj._preview_after = "pending-60ms"
    obj._state = readonly_state(WindowSnapshot(1, tuple(rows), True))
    obj.poller = type("Poller", (), {})()
    obj.poller.active = active
    obj.poller.producer = Producer(WindowSnapshot(2, tuple(rows), True))
    obj._render = lambda state: setattr(obj, "_state", state)
    def sync(snap_rows):
        obj.events.append(("rebuild", tuple((w.hwnd, w.pid) for w in snap_rows)))
        obj._observed_windows = tuple(snap_rows)
        obj._active_windows = obj.preview_order.update(tuple(snap_rows))
        obj._tile_items = {
            (w.hwnd, w.pid): (Element(obj.events, f"new-tile-{w.hwnd}"), None, None)
            for w in obj._active_windows
        }
    obj._sync_tiles = sync
    obj._schedule_preview = lambda: obj.events.append(("schedule_60ms", None))
    return obj


class S15ManualRefreshTests(unittest.TestCase):
    def test_original_button_is_full_list_not_label_only(self):
        self.assertTrue(callable(TLMStartTab.refresh_window_preview_list))
        self.assertTrue(callable(TLMStartTab._clear_window_preview_list))

    def test_cleanup_unregisters_native_before_destroying_old_frames(self):
        obj = prepared()
        c = obj._preview_controller
        self.assertTrue(obj.refresh_window_preview_list())
        self.assertEqual(c.shutdown_count, 1)
        evt = obj.events
        reg_idx = next(i for i, v in enumerate(evt) if v[0] == "unregister_and_destroy_native_DWM")
        frame_idx = next(i for i, v in enumerate(evt) if v[0] == "destroy_widget")
        self.assertLess(reg_idx, frame_idx)
        self.assertIn(("after_cancel", "pending-60ms"), evt)
        self.assertIn(("schedule_60ms", None), evt)

    def test_refresh_has_exactly_one_cache_read_and_no_scan(self):
        obj = prepared()
        self.assertTrue(obj.refresh_window_preview_list())
        self.assertEqual(obj.poller.producer.reads, 1)
        self.assertEqual(obj.poller.producer.starts, 0)
        self.assertEqual(obj.poller.producer.scans, 0)

    def test_manual_order_survives_reversed_cache_enumeration(self):
        rows = [win(1), win(2), win(3)]
        obj = prepared(tuple(rows))
        obj.preview_order.move(3, 1003, -1)
        obj._active_windows = obj.preview_order.ordered(rows)
        obj.poller.producer.snap = WindowSnapshot(3, tuple(reversed(rows)), True)
        self.assertTrue(obj.refresh_window_preview_list())
        self.assertEqual([w.hwnd for w in obj._active_windows], [1, 3, 2])

    def test_same_hwnd_new_pid_does_not_inherit_stale_slot(self):
        obj = prepared()
        obj.preview_order.move(3, 1003, -1)
        rows = (win(3, 9999), win(1), win(2))
        obj.poller.producer.snap = WindowSnapshot(3, rows, True)
        self.assertTrue(obj.refresh_window_preview_list())
        self.assertEqual(tuple(w.hwnd for w in obj._active_windows), (1, 2, 3))
        self.assertFalse(obj.preview_order.move(3, 1003, -1))

    def test_inactive_start_refuses_without_read_or_teardown(self):
        obj = prepared(active=False)
        previous = obj._preview_controller
        self.assertFalse(obj.refresh_window_preview_list())
        self.assertIs(obj._preview_controller, previous)
        self.assertEqual(obj.poller.producer.reads, 0)

    def test_hidden_root_refuses_without_read_or_teardown(self):
        obj = prepared(visible=False)
        self.assertFalse(obj.refresh_window_preview_list())
        self.assertEqual(obj.poller.producer.reads, 0)
        self.assertEqual(len(obj._tile_items), 3)

    def test_shutdown_refuses_even_if_stale_gui_button_is_invoked(self):
        obj = prepared()
        obj._closed = True
        self.assertFalse(obj.refresh_window_preview_list())
        self.assertEqual(obj.poller.producer.reads, 0)

    def test_empty_cache_hides_native_and_shows_original_no_game_message(self):
        obj = prepared()
        obj.poller.producer.snap = WindowSnapshot(3, (), True)
        self.assertTrue(obj.refresh_window_preview_list())
        self.assertEqual(obj._tile_items, {})
        self.assertEqual(obj.preview_status.value,
                         "Không tìm thấy cửa sổ game, hãy mở game trước.")
        self.assertIsNone(obj._preview_controller)

    def test_invalid_cache_clears_native_and_marks_error(self):
        obj = prepared()
        obj.poller.producer.snap = WindowSnapshot(
            3, (win(1),), False, error="ENUMERATION_ERROR")
        self.assertTrue(obj.refresh_window_preview_list())
        self.assertEqual(obj._state.code, "ERROR")
        self.assertEqual(obj._tile_items, {})
        self.assertIsNone(obj._preview_controller)

    def test_unexpected_cache_object_fails_closed_not_rendered(self):
        obj = prepared()
        obj.poller.producer.snap = {"fake": "not immutable snapshot"}
        self.assertFalse(obj.refresh_window_preview_list())
        self.assertEqual(obj._state.code, "ERROR")
        self.assertEqual(obj._tile_items, {})

    def test_cache_exception_fails_closed_and_removes_stale_dwm(self):
        obj = prepared()
        obj.poller.producer.snap = RuntimeError("broken")
        self.assertFalse(obj.refresh_window_preview_list())
        self.assertIsNone(obj._preview_controller)
        self.assertEqual(obj._tile_items, {})
        self.assertEqual(obj._state.code, "ERROR")

    def test_invalid_duplicate_live_hwnds_does_not_leave_ghosts(self):
        obj = prepared()
        obj.poller.producer.snap = WindowSnapshot(4, (win(1), win(1)), True)
        self.assertFalse(obj.refresh_window_preview_list())
        self.assertEqual(obj._tile_items, {})
        self.assertEqual(obj._state.code, "ERROR")

    def test_repeated_full_refresh_destroys_all_prior_frames(self):
        obj = prepared()
        self.assertTrue(obj.refresh_window_preview_list())
        self.assertTrue(obj.refresh_window_preview_list())
        self.assertEqual(sum(e[0] == "destroy_widget" for e in obj.events), 6)
        self.assertEqual(sum(e[0] == "rebuild" for e in obj.events), 2)
        self.assertEqual(obj.poller.producer.reads, 2)


if __name__ == "__main__":
    unittest.main()
