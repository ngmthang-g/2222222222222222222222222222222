"""S76: C15 Start native-DWM failure must release all preview frame owners."""
from __future__ import annotations
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
sys.path.insert(0, str(ROOT/"tests"))
from test_s15 import prepared, win, Element
from start_polling import WindowSnapshot
from start_tab import TLMStartTab, StartReadOnlyState


class NativeErrorCtrl:
    def __init__(self, events):
        self.events = events
        self.calls = 0
    def shutdown(self):
        self.events.append(("native_shutdown_fails_after_attempt", None))
        self.calls += 1
        raise OSError("TEST_NATIVE_UNREGISTER_FAILURE")


class S76C15FailClosedTests(unittest.TestCase):
    def failing(self):
        obj = prepared()
        native = NativeErrorCtrl(obj.events)
        obj._preview_controller = native
        return obj, native

    def test_01_native_error_never_claims_refresh_success(self):
        obj, native = self.failing()
        self.assertFalse(obj.refresh_window_preview_list())
        self.assertEqual(native.calls, 1)
        self.assertTrue(obj._preview_cleanup_faulted)
        self.assertEqual(obj._state.code, "ERROR")

    def test_02_every_old_frame_still_destroyed_after_native_failure(self):
        obj, _ = self.failing()
        old = [item[0] for item in obj._tile_items.values()]
        obj.refresh_window_preview_list()
        self.assertTrue(all(item.destroyed for item in old))
        self.assertEqual(len([e for e in obj.events if e[0]=="destroy_widget"]), 3)
        self.assertEqual(obj._tile_items, {})

    def test_03_native_release_attempt_precedes_any_frame_destroy(self):
        obj, _ = self.failing()
        obj.refresh_window_preview_list()
        self.assertLess(obj.events.index(("native_shutdown_fails_after_attempt", None)),
                        obj.events.index(("destroy_widget", "tile-1")))

    def test_04_no_rebuild_or_new_DWM_schedule_on_unverified_cleanup(self):
        obj, _ = self.failing()
        obj.refresh_window_preview_list()
        self.assertFalse(any(e[0] == "rebuild" for e in obj.events))
        self.assertFalse(any(e[0] == "schedule_60ms" for e in obj.events))
        self.assertIsNone(obj._preview_controller)
        self.assertEqual(obj._active_windows, ())
        self.assertEqual(obj._observed_windows, ())

    def test_05_second_click_fails_without_second_scan_or_reopen(self):
        obj, native = self.failing()
        self.assertFalse(obj.refresh_window_preview_list())
        reads = obj.poller.producer.reads
        self.assertFalse(obj.refresh_window_preview_list())
        self.assertEqual(obj.poller.producer.reads, reads)
        self.assertEqual(native.calls, 1)
        self.assertIn("DWM", obj.preview_status.value)

    def test_06_invalid_cache_with_native_failure_still_clears_old_items(self):
        obj, native = self.failing()
        obj.poller.producer.snap = ValueError("CACHE_BROKEN_TEST")
        self.assertFalse(obj.refresh_window_preview_list())
        self.assertEqual(native.calls, 1)
        self.assertEqual(obj._tile_items, {})
        self.assertEqual(obj._state.code, "ERROR")

    def test_07_update_cache_does_not_resurrect_tiles_after_error(self):
        obj, _ = self.failing()
        obj.refresh_window_preview_list()
        obj._present_cached_snapshot(WindowSnapshot(17, (win(4),), True))
        self.assertEqual(obj._tile_items, {})
        self.assertEqual(obj._active_windows, ())
        self.assertEqual(obj._state.code, "LIVE")

    def test_08_delayed_dwm_callback_is_fenced_after_error(self):
        obj, _ = self.failing()
        obj.refresh_window_preview_list()
        obj._refresh_dwm()
        self.assertIsNone(obj._preview_controller)
        self.assertIsNone(obj._preview_after)
        obj._schedule_preview()
        self.assertFalse(any(e[0]=="schedule_60ms" for e in obj.events))

    def test_09_one_Tk_frame_destroy_failure_does_not_strand_siblings(self):
        obj = prepared()
        first = obj._tile_items[(1, 1001)][0]
        def broken():
            obj.events.append(("destroy_failure", "tile-1"))
            raise RuntimeError("TEST_WIDGET_DESTROY_ERROR")
        first.destroy = broken
        self.assertFalse(obj.refresh_window_preview_list())
        self.assertTrue(obj._preview_cleanup_faulted)
        self.assertEqual(obj._tile_items, {})
        self.assertIn(("destroy_widget", "tile-2"), obj.events)
        self.assertIn(("destroy_widget", "tile-3"), obj.events)

    def test_10_normal_C15_still_rebuilds_and_preserves_order(self):
        obj = prepared()
        obj.preview_order.move(3,1003,-1)
        self.assertTrue(obj.refresh_window_preview_list())
        self.assertEqual([w.hwnd for w in obj._active_windows], [1,3,2])
        self.assertFalse(getattr(obj,"_preview_cleanup_faulted",False))
        self.assertEqual(sum(e[0]=="rebuild" for e in obj.events),1)

    def test_11_invalid_duplicate_cache_is_original_failed_refresh_not_latch(self):
        obj = prepared()
        obj.poller.producer.snap = WindowSnapshot(14, (win(1),win(1)), True)
        self.assertFalse(obj.refresh_window_preview_list())
        self.assertEqual(obj._tile_items, {})
        self.assertFalse(getattr(obj, "_preview_cleanup_faulted", False))
        self.assertEqual(obj._state.code,"ERROR")

    def test_12_never_adds_fake_UI_license_or_auto_actions(self):
        source = (ROOT/"src/start_tab.py").read_text("utf-8")
        self.assertIn("def refresh_window_preview_list",source)
        self.assertIn("self._preview_cleanup_faulted",source)
        for term in ("CreateRemoteThread(", "ReadProcessMemory(",
                     "self._enable_detached_auto_open(", "proxy_network_send("):
            self.assertNotIn(term,source)


if __name__ == "__main__":
    unittest.main()
