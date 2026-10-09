"""S11 read-only DWM controller tests: test HWNDs never shipped as game."""
from __future__ import annotations

import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dwm_preview import (
    ITEM_WIDTH, ITEM_HEIGHT, THUMB_WIDTH, THUMB_HEIGHT, NativeDwmBackend,
    PreviewPlacement, ReadOnlyDwmPreviews,
)


def place(hwnd=41, pid=1001, owner=500, x=3, y=5, w=197, h=110):
    return PreviewPlacement(hwnd, pid, owner, x, y, w, h)


class FakeDwmBackend:
    def __init__(self):
        self.live = {41: 1001, 42: 1002}
        self.next_dest = 300
        self.events = []
        self.fail_step = None

    def source_matches(self, hwnd, pid):
        self.events.append(("matches", hwnd, pid))
        return self.live.get(hwnd) == pid

    def create_destination(self, owner, x, y, width, height):
        self.events.append(("create", owner, x, y, width, height))
        if self.fail_step == "create":
            raise OSError("create failed")
        self.next_dest += 1
        return self.next_dest

    def register(self, destination, source):
        self.events.append(("register", destination, source))
        if self.fail_step == "register":
            raise OSError("register failed")
        return destination + 1000

    def reposition(self, destination, thumbnail, x, y, width, height):
        self.events.append(("reposition", destination, thumbnail, x, y, width, height))
        if self.fail_step == "reposition":
            raise OSError("update failed")

    def unregister(self, thumbnail):
        self.events.append(("unregister", thumbnail))

    def destroy_destination(self, destination):
        self.events.append(("destroy", destination))


class DwmS11Tests(unittest.TestCase):
    def test_exact_original_measured_thumb_and_item_metrics(self):
        self.assertEqual((THUMB_WIDTH, THUMB_HEIGHT), (197, 110))
        self.assertEqual((ITEM_WIDTH, ITEM_HEIGHT), (205, 137))

    def test_register_update_real_sourced_placement(self):
        b = FakeDwmBackend()
        ctl = ReadOnlyDwmPreviews(b)
        self.assertEqual(ctl.sync([place()]).rendered, (41,))
        self.assertEqual(ctl.active_hwnds, (41,))
        self.assertIn(("register", 301, 41), b.events)
        self.assertIn(("reposition", 301, 1301, 3, 5, 197, 110), b.events)

    def test_same_hwnd_pid_repositions_without_reregister(self):
        b = FakeDwmBackend()
        ctl = ReadOnlyDwmPreviews(b)
        ctl.sync([place()])
        ctl.sync([place(x=44, y=57)])
        self.assertEqual(sum(e[0] == "register" for e in b.events), 1)
        self.assertIn(("reposition", 301, 1301, 44, 57, 197, 110), b.events)

    def test_invalid_or_unknown_pid_does_not_register(self):
        b = FakeDwmBackend()
        ctl = ReadOnlyDwmPreviews(b)
        result = ctl.sync([place(pid=987)])
        self.assertEqual(result.rendered, ())
        self.assertEqual(result.errors[0][1], "STALE_CLOSED_OR_HUNG_SOURCE")
        self.assertFalse(any(e[0] == "create" for e in b.events))

    def test_pid_reuse_unregistered_before_second_register(self):
        b = FakeDwmBackend()
        ctl = ReadOnlyDwmPreviews(b)
        ctl.sync([place()])
        b.live[41] = 1009
        result = ctl.sync([place(pid=1009)])
        self.assertEqual(result.rendered, (41,))
        labels = [e[0] for e in b.events]
        first_remove = labels.index("unregister")
        last_register = len(labels) - 1 - labels[::-1].index("register")
        self.assertLess(first_remove, last_register)
        self.assertEqual(ctl.active_hwnds, (41,))

    def test_removed_hwnd_unregisters_and_destroys(self):
        b = FakeDwmBackend()
        ctl = ReadOnlyDwmPreviews(b)
        ctl.sync([place()])
        ctl.sync([])
        self.assertEqual(ctl.active_hwnds, ())
        self.assertEqual(b.events[-2:], [("unregister", 1301), ("destroy", 301)])

    def test_register_failure_destroys_partial_destination(self):
        b = FakeDwmBackend()
        b.fail_step = "register"
        ctl = ReadOnlyDwmPreviews(b)
        result = ctl.sync([place()])
        self.assertEqual(result.rendered, ())
        self.assertEqual(ctl.active_hwnds, ())
        self.assertEqual(b.events[-1], ("destroy", 301))

    def test_update_failure_unregisters_thumbnail_before_destroy(self):
        b = FakeDwmBackend()
        b.fail_step = "reposition"
        ctl = ReadOnlyDwmPreviews(b)
        result = ctl.sync([place()])
        self.assertEqual(result.rendered, ())
        self.assertEqual(b.events[-2:], [("unregister", 1301), ("destroy", 301)])

    def test_new_owner_forces_recreation(self):
        b = FakeDwmBackend()
        ctl = ReadOnlyDwmPreviews(b)
        ctl.sync([place()])
        ctl.sync([place(owner=999)])
        self.assertEqual([e[0] for e in b.events].count("register"), 2)
        self.assertEqual([e[0] for e in b.events].count("unregister"), 1)

    def test_invalid_dimensions_drop_stale_slot(self):
        b = FakeDwmBackend()
        ctl = ReadOnlyDwmPreviews(b)
        ctl.sync([place()])
        result = ctl.sync([place(w=0)])
        self.assertEqual(ctl.active_hwnds, ())
        self.assertEqual(result.errors[0][1], "INVALID_RECT_OR_ID")

    def test_close_rejects_all_further_work_and_is_idempotent(self):
        b = FakeDwmBackend()
        ctl = ReadOnlyDwmPreviews(b)
        ctl.sync([place()])
        ctl.shutdown()
        ctl.shutdown()
        self.assertEqual(ctl.active_hwnds, ())
        self.assertEqual(ctl.sync([place()]).errors, ((41, "CLOSED"),))
        self.assertEqual([e[0] for e in b.events].count("unregister"), 1)

    def test_conflicting_same_hwnd_input_fails_without_mutating_existing_slot(self):
        b = FakeDwmBackend()
        ctl = ReadOnlyDwmPreviews(b)
        ctl.sync([place()])
        with self.assertRaises(ValueError):
            ctl.sync([place(), place(pid=1002)])
        self.assertEqual(ctl.active_hwnds, (41,))

    def test_native_backend_requires_actual_windows(self):
        if os.name != "nt":
            with self.assertRaises(OSError):
                NativeDwmBackend()


if __name__ == "__main__":
    unittest.main()
