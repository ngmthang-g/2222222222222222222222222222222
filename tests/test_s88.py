"""S88 C03/C15: automatic HWND disappearance must fence uncertain native DWM teardown.

This is a local safety guard, NOT proof of original Nuitka exception paths.
Source-backed automatic C04 updates and S76 full-refresh cleanup already exist.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tests")]
from test_s15 import prepared, win
from start_polling import WindowSnapshot, StartCacheEvent
from start_windows import WindowDelta
from start_tab import TLMStartTab


class ClearFailure:
    def __init__(self, events, *, shutdown_fails=False):
        self.events = events
        self.clear_calls = 0
        self.shutdown_calls = 0
        self.shutdown_fails = shutdown_fails

    def clear(self):
        self.clear_calls += 1
        self.events.append(("automatic_native_clear_failed", None))
        raise OSError("TEST_NATIVE_DWM_UNREGISTER_FAILED")

    def shutdown(self):
        self.shutdown_calls += 1
        self.events.append(("native_final_shutdown_attempt", None))
        if self.shutdown_fails:
            raise OSError("TEST_SECOND_NATIVE_RELEASE_FAILED")


def fixture(*, final_shutdown_fails=False):
    obj = prepared()
    obj._preview_controller = ClearFailure(
        obj.events, shutdown_fails=final_shutdown_fails)
    obj._update_master_combobox = lambda windows: None
    obj._preview_cleanup_faulted = False
    obj._schedule_preview = lambda: TLMStartTab._schedule_preview(obj)
    return obj


class S88AutoSourceLossSafety(unittest.TestCase):
    def test_01_original_source_loss_clear_error_is_caught_in_ui_callback(self):
        obj = fixture()
        old_frames = [v[0] for v in obj._tile_items.values()]
        obj._sync_tiles((win(2), win(3)))
        self.assertTrue(obj._preview_cleanup_faulted)
        self.assertEqual(obj._tile_items, {})
        self.assertTrue(all(w.destroyed for w in old_frames))
        self.assertEqual(obj._observed_windows, ())
        self.assertEqual(obj._active_windows, ())

    def test_02_native_release_attempt_precedes_every_tk_frame_destroy(self):
        obj = fixture()
        obj._sync_tiles((win(2), win(3)))
        clear_at = obj.events.index(("automatic_native_clear_failed", None))
        shutdown_at = obj.events.index(("native_final_shutdown_attempt", None))
        first_destroy = min(i for i, e in enumerate(obj.events)
                            if e[0] == "destroy_widget")
        self.assertLess(clear_at, shutdown_at)
        self.assertLess(shutdown_at, first_destroy)

    def test_03_second_native_error_still_releases_all_tk_frames(self):
        obj = fixture(final_shutdown_fails=True)
        old = [v[0] for v in obj._tile_items.values()]
        obj._sync_tiles((win(1), win(3)))
        self.assertTrue(all(v.destroyed for v in old))
        self.assertTrue(obj._preview_cleanup_faulted)
        self.assertIsNone(obj._preview_controller)
        self.assertIn("DWM", obj.preview_status.value)

    def test_04_no_second_dwm_after_fault_or_late_snapshot(self):
        obj = fixture()
        native = obj._preview_controller
        obj._sync_tiles((win(2), win(3)))
        obj._present_cached_snapshot(WindowSnapshot(
            revision=88, windows=(win(2), win(3), win(4)), valid=True))
        self.assertEqual(native.clear_calls, 1)
        self.assertEqual(native.shutdown_calls, 1)
        self.assertEqual(obj._tile_items, {})
        self.assertEqual(obj._active_windows, ())
        self.assertIsNone(obj._preview_controller)

    def test_05_real_preview_scheduler_rejects_faulted_owner(self):
        obj = fixture()
        obj._sync_tiles((win(1), win(2)))
        self.assertIsNone(obj._preview_after)
        self.assertFalse(TLMStartTab._schedule_preview(obj))
        self.assertIsNone(obj._preview_after)

    def test_06_c04_event_does_not_throw_or_recreate_native_on_fault(self):
        obj = fixture()
        obj._on_cache_event(StartCacheEvent(
            snapshot=WindowSnapshot(
                revision=88, windows=(win(2), win(3)), valid=True),
            delta=WindowDelta()))
        self.assertTrue(obj._preview_cleanup_faulted)
        self.assertIsNone(obj._preview_controller)
        self.assertEqual(obj._tile_items, {})
        self.assertIn("DWM", obj.preview_status.value)

    def test_07_manual_refresh_must_not_report_success_after_late_fault(self):
        obj = prepared()
        obj._preview_cleanup_faulted = False
        # Model a post-teardown native failure surfaced without an exception
        # by a cache re-presentation; never claim C15 success.
        def fault_during_presentation(_snapshot):
            obj._preview_cleanup_faulted = True
        obj._present_cached_snapshot = fault_during_presentation
        self.assertFalse(obj.refresh_window_preview_list())
        self.assertEqual(obj._state.code, "ERROR")
        self.assertIn("DWM", obj.preview_status.value)

    def test_08_original_good_explicit_refresh_still_works(self):
        obj = prepared()
        self.assertTrue(obj.refresh_window_preview_list())
        self.assertFalse(getattr(obj, "_preview_cleanup_faulted", False))
        self.assertEqual(len(obj._tile_items), 3)

    def test_09_old_same_set_refresh_has_no_source_loss_clear(self):
        obj = fixture()
        native = obj._preview_controller
        # Fake no Tk layout or new tiles; validate the change predicate
        # by exercising an unchanged set through read-only callback.
        obj._observed_windows = (win(1), win(2), win(3))
        obj._present_cached_snapshot(WindowSnapshot(
            revision=89, windows=(win(1), win(2), win(3)), valid=True))
        self.assertEqual(native.clear_calls, 0)
        self.assertFalse(obj._preview_cleanup_faulted)

    def test_10_no_original_auth_game_input_proxy_or_new_control(self):
        source = (ROOT / "src/start_tab.py").read_text(encoding="utf-8")
        self.assertIn("S88 C03/C15", source)
        self.assertIn("self._clear_window_preview_list()", source)
        for disallowed in ("CreateRemoteThread(", "ReadProcessMemory(",
                           "TOKEN_HMAC_SECRET", "proxy_network_send("):
            self.assertNotIn(disallowed, source)


if __name__ == "__main__":
    unittest.main()
