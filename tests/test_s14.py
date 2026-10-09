"""S14 C09/C17 original-evidenced grid/order; only test-owned window models."""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from preview_layout import (
    DEFAULT_PREVIEW_GRID, EDGE_POLICY, NEW_SOURCE_POLICY, PREVIEW_GRID_CHOICES,
    REUSED_HWND_POLICY, PreviewOrder, preview_columns, preview_position,
)
from start_windows import GameWindow


def window(hwnd, pid=None, title=None):
    return GameWindow(hwnd, hwnd + 1000 if pid is None else pid,
                      f"TEST WINDOW {hwnd}" if title is None else title,
                      "TEST_C09_C17", "NOT_GAME.exe")


class S14GridAndOrderTests(unittest.TestCase):
    def test_original_default_and_exact_five_column_choices(self):
        self.assertEqual(DEFAULT_PREVIEW_GRID, "2x")
        self.assertEqual(PREVIEW_GRID_CHOICES, ("1x", "2x", "3x", "4x", "5x"))
        self.assertEqual([preview_columns(v) for v in PREVIEW_GRID_CHOICES],
                         [1, 2, 3, 4, 5])

    def test_rejects_unsupported_preview_column_values(self):
        for value in ("0x", "6x", "2", "auto", "2X", 2, None, ""):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    preview_columns(value)

    def test_row_col_mapping_changes_exactly_with_column_selection(self):
        self.assertEqual([preview_position(i, 2) for i in range(5)],
                         [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)])
        self.assertEqual([preview_position(i, 1) for i in range(4)],
                         [(0, 0), (1, 0), (2, 0), (3, 0)])
        self.assertEqual([preview_position(i, 5) for i in range(6)],
                         [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 0)])

    def test_invalid_row_col_input_fails_closed(self):
        for idx, count in ((-1, 2), (0, 0), (0, 6), ("1", 2), (0, 2.0)):
            with self.subTest(idx=idx, count=count):
                with self.assertRaises(ValueError):
                    preview_position(idx, count)

    def test_initial_discovered_source_order_retained(self):
        ordering = PreviewOrder()
        input_rows = [window(90), window(10), window(40)]
        self.assertEqual(ordering.update(input_rows), tuple(input_rows))
        self.assertEqual(ordering.hwnds, (90, 10, 40))

    def test_arrow_delta_moves_only_one_neighbour(self):
        ordering = PreviewOrder()
        rows = [window(10), window(20), window(30)]
        ordering.update(rows)
        self.assertTrue(ordering.move(30, 1030, -1))
        self.assertEqual(ordering.hwnds, (10, 30, 20))
        self.assertTrue(ordering.move(10, 1010, 1))
        self.assertEqual(ordering.hwnds, (30, 10, 20))
        self.assertEqual(tuple(w.hwnd for w in ordering.ordered(rows)),
                         (30, 10, 20))

    def test_edge_arrows_no_wrap_are_documented_local_policy(self):
        self.assertIn("UNKNOWN_ORIGINAL", EDGE_POLICY)
        ordering = PreviewOrder()
        ordering.update([window(1), window(2)])
        self.assertFalse(ordering.move(1, 1001, -1))
        self.assertFalse(ordering.move(2, 1002, 1))
        self.assertEqual(ordering.hwnds, (1, 2))

    def test_mismatched_pid_or_missing_hwnd_cannot_reorder(self):
        ordering = PreviewOrder()
        ordering.update([window(11), window(22)])
        self.assertFalse(ordering.move(11, 1012, 1))
        self.assertFalse(ordering.move(99, 1099, 1))
        self.assertFalse(ordering.move(11, 1011, 5))
        self.assertEqual(ordering.hwnds, (11, 22))

    def test_reordered_survivors_preserve_position_across_cache_refresh(self):
        ordering = PreviewOrder()
        rows = [window(1), window(2), window(3)]
        ordering.update(rows)
        self.assertTrue(ordering.move(3, 1003, -1))
        same = [window(3, title="new title"), window(1), window(2)]
        self.assertEqual(tuple(w.hwnd for w in ordering.update(same)),
                         (1, 3, 2))
        self.assertEqual(ordering.hwnds, (1, 3, 2))

    def test_new_windows_append_but_source_insertion_policy_unknown_original(self):
        self.assertIn("UNKNOWN_ORIGINAL", NEW_SOURCE_POLICY)
        ordering = PreviewOrder()
        ordering.update([window(1), window(2)])
        ordering.move(2, 1002, -1)
        self.assertEqual(tuple(w.hwnd for w in
                               ordering.update([window(3), window(2), window(1)])),
                         (2, 1, 3))

    def test_deleted_source_is_removed_without_moving_other_source(self):
        ordering = PreviewOrder()
        ordering.update([window(1), window(2), window(3)])
        ordering.move(3, 1003, -1)
        self.assertEqual(tuple(w.hwnd for w in ordering.update([window(1), window(3)])),
                         (1, 3))
        self.assertEqual(ordering.hwnds, (1, 3))

    def test_pid_reuse_does_not_inherit_old_window_position(self):
        self.assertIn("PID_SAFETY", REUSED_HWND_POLICY)
        ordering = PreviewOrder()
        ordering.update([window(1), window(2), window(3)])
        ordering.move(3, 1003, -1)
        new_rows = [window(3, pid=98765), window(1), window(2)]
        self.assertEqual(tuple(w.hwnd for w in ordering.update(new_rows)),
                         (1, 2, 3))
        self.assertFalse(ordering.move(3, 1003, -1))
        self.assertTrue(ordering.move(3, 98765, -1))

    def test_zero_sources_resets_no_hidden_buttons(self):
        ordering = PreviewOrder()
        ordering.update([window(1), window(2)])
        self.assertEqual(ordering.update(()), ())
        self.assertEqual(ordering.hwnds, ())
        self.assertFalse(ordering.move(1, 1001, 1))

    def test_duplicates_and_unverified_ids_fail_closed(self):
        ordering = PreviewOrder()
        ordering.update([window(1), window(2)])
        with self.assertRaises(ValueError):
            ordering.update([window(1), window(1, pid=999)])
        self.assertEqual(ordering.hwnds, (1, 2))
        with self.assertRaises(ValueError):
            ordering.update([window(0)])

    def test_permutation_reordering_never_mutates_original_game_objects(self):
        ordering = PreviewOrder()
        one, two = window(100), window(200)
        ordering.update([one, two])
        ordering.move(200, 1200, -1)
        result = ordering.ordered([one, two])
        self.assertIs(result[0], two)
        self.assertIs(result[1], one)
        self.assertEqual(one.hwnd, 100)
        self.assertEqual(two.hwnd, 200)
        self.assertFalse(hasattr(ordering, "activate_game_window"))

    def test_clear_drops_only_logical_preview_order(self):
        ordering = PreviewOrder()
        ordering.update([window(1), window(2)])
        ordering.clear()
        self.assertEqual(ordering.hwnds, ())
        self.assertEqual(ordering.update([window(2)]), (window(2),))


if __name__ == "__main__":
    unittest.main()
