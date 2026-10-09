"""S12 multi-HWND DWM lifecycle regressions; all HWNDs in this file are test-only."""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dwm_preview import PreviewPlacement, ReadOnlyDwmPreviews


class CountingBackend:
    def __init__(self):
        self.pid = {h: 7100 + h for h in (71, 72, 73)}
        self.serial = 1000
        self.created = []
        self.registered = []
        self.updated = []
        self.unregistered = []
        self.destroyed = []
        self.fail_on = set()
        self.thumbs = {}

    def source_matches(self, hwnd, pid):
        return self.pid.get(hwnd) == pid

    def create_destination(self, owner, x, y, width, height):
        self.serial += 1
        self.created.append(self.serial)
        return self.serial

    def register(self, destination, source):
        if source in self.fail_on:
            raise OSError("S12 TEST-ONLY forced native register failure")
        h = destination + 2000
        self.registered.append((h, source))
        self.thumbs[h] = destination
        return h

    def reposition(self, destination, thumbnail, x, y, width, height):
        self.updated.append((destination, thumbnail, x, y, width, height))

    def unregister(self, thumbnail):
        self.unregistered.append(thumbnail)
        self.thumbs.pop(thumbnail, None)

    def destroy_destination(self, destination):
        self.destroyed.append(destination)


def items(count=3, shift=0, owner=200):
    return [
        PreviewPlacement(
            hwnd=h, pid=7100 + h, owner_hwnd=owner,
            x=20 + i * 210 + shift, y=35 + (i // 2) * 145 + shift,
            width=197, height=110)
        for i, h in enumerate((71, 72, 73)[:count])
    ]


class S12MultiDwmTests(unittest.TestCase):
    def test_three_genuine_ids_have_three_independent_resources(self):
        b = CountingBackend()
        c = ReadOnlyDwmPreviews(b)
        result = c.sync(items())
        self.assertEqual(result.rendered, (71, 72, 73))
        self.assertEqual(len(b.created), 3)
        self.assertEqual(len(b.registered), 3)
        self.assertEqual(len(set(h for h, _ in b.registered)), 3)
        self.assertEqual(len(b.updated), 3)
        c.shutdown()
        self.assertEqual(len(b.unregistered), 3)
        self.assertEqual(set(b.created), set(b.destroyed))

    def test_root_move_resize_only_updates_existing_destinations(self):
        b = CountingBackend()
        c = ReadOnlyDwmPreviews(b)
        c.sync(items())
        c.sync(items(shift=55))
        self.assertEqual(len(b.registered), 3)
        self.assertEqual(len(b.updated), 6)
        self.assertEqual(set(row[2] for row in b.updated[-3:]), {75, 285, 495})
        c.shutdown()

    def test_removed_one_does_not_replace_other_two(self):
        b = CountingBackend()
        c = ReadOnlyDwmPreviews(b)
        c.sync(items())
        result = c.sync([items()[0], items()[2]])
        self.assertEqual(result.rendered, (71, 73))
        self.assertEqual(c.active_hwnds, (71, 73))
        self.assertEqual(len(b.registered), 3)
        self.assertEqual(len(b.unregistered), 1)
        c.shutdown()
        self.assertEqual(len(b.destroyed), 3)

    def test_closed_source_drops_only_its_thumbnail(self):
        b = CountingBackend()
        c = ReadOnlyDwmPreviews(b)
        c.sync(items())
        del b.pid[72]
        result = c.sync(items())
        self.assertEqual(result.rendered, (71, 73))
        self.assertEqual(result.errors, ((72, "STALE_CLOSED_OR_HUNG_SOURCE"),))
        self.assertEqual(c.active_hwnds, (71, 73))
        c.shutdown()
        self.assertEqual(len(b.created), len(b.destroyed))

    def test_pid_reuse_one_does_not_corrupt_siblings(self):
        b = CountingBackend()
        c = ReadOnlyDwmPreviews(b)
        c.sync(items())
        b.pid[72] += 1
        moved = items()
        moved[1] = PreviewPlacement(72, b.pid[72], 200, 230, 35, 197, 110)
        result = c.sync(moved)
        self.assertEqual(result.rendered, (71, 72, 73))
        self.assertEqual(len(b.registered), 4)
        self.assertEqual(len(b.unregistered), 1)
        c.shutdown()
        self.assertEqual(len(b.created), len(b.destroyed))

    def test_one_failed_new_source_does_not_poison_survivors(self):
        b = CountingBackend()
        b.fail_on.add(72)
        c = ReadOnlyDwmPreviews(b)
        result = c.sync(items())
        self.assertEqual(result.rendered, (71, 73))
        self.assertEqual(tuple(h for h, _ in result.errors), (72,))
        self.assertEqual(c.active_hwnds, (71, 73))
        c.shutdown()
        self.assertEqual(len(b.created), len(b.destroyed))

    def test_repeated_refresh_and_hide_restoration_has_no_leaks(self):
        b = CountingBackend()
        c = ReadOnlyDwmPreviews(b)
        for cycle in range(15):
            self.assertEqual(c.sync(items(shift=cycle * 3)).rendered, (71, 72, 73))
            self.assertEqual(c.sync(items(shift=cycle * 3 + 1)).rendered, (71, 72, 73))
            c.clear()
            self.assertEqual(c.active_hwnds, ())
        c.shutdown()
        self.assertEqual(len(b.registered), 45)
        self.assertEqual(len(b.registered), len(b.unregistered))
        self.assertEqual(len(b.created), len(b.destroyed))
        self.assertEqual(b.thumbs, {})

    def test_revoked_session_never_resurrects_old_items(self):
        b = CountingBackend()
        c = ReadOnlyDwmPreviews(b)
        c.sync(items())
        c.shutdown()
        self.assertEqual(c.sync(items()).rendered, ())
        self.assertEqual(len(c.sync(items()).errors), 3)
        self.assertEqual(len(b.created), len(b.destroyed))
        self.assertEqual(b.thumbs, {})


if __name__ == "__main__":
    unittest.main()
