"""S20 C20 combined *three-source* invariants; no game input or UI shims.

These tests connect existing C05/C08/C09/C17/C18/C19 models only.
Native real Win32 DWM/SetWindowPos validation lives in S20 smoke.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from grid_master import MasterSelection, GridSettings
from preview_layout import PreviewOrder, preview_position, preview_columns
from input_sync_core import InputSyncModel, ClientSize, scale_client_point
from start_polling import WindowSnapshot
from start_windows import GameWindow, GAME_PROCESS, GAME_TITLE, UNITY_WINDOW_CLASS


def row(hwnd, pid=None):
    return GameWindow(hwnd, pid or (1000 + hwnd), GAME_TITLE,
                      UNITY_WINDOW_CLASS, GAME_PROCESS)


ROWS = (row(11), row(22), row(33))


def snapshot(*rows, valid=True):
    return WindowSnapshot(4, tuple(rows), valid)


class S20CombinedThreeSource(unittest.TestCase):
    def setUp(self):
        self.preview = PreviewOrder()
        self.master = MasterSelection()
        self.preview.update(ROWS)
        self.master.update(ROWS)

    def test_original_physical_grid_defaults_independent_of_preview_two_x(self):
        grid = GridSettings()
        self.assertEqual((grid.cols, grid.rows), (3, 4))
        self.assertEqual(preview_columns("2x"), 2)
        self.assertEqual([preview_position(i, 2) for i in range(3)],
                         [(0, 0), (0, 1), (1, 0)])

    def test_second_preview_card_can_be_master_for_physical_grid(self):
        self.assertTrue(self.master.choose(22, 1022))
        self.assertEqual(self.master.selected, (22, 1022))
        self.assertEqual([w.hwnd for w in self.preview.ordered(ROWS)],
                         [11, 22, 33])
        self.assertNotEqual(self.preview.hwnds[0], self.master.hwnd)

    def test_preview_reorder_does_not_change_master_identity(self):
        self.master.choose(22, 1022)
        self.assertTrue(self.preview.move(33, 1033, -1))
        self.assertEqual([w.hwnd for w in self.preview.ordered(ROWS)],
                         [11, 33, 22])
        self.assertEqual(self.master.selected, (22, 1022))

    def test_preview_reorder_does_not_change_s19_slave_membership(self):
        self.master.choose(22, 1022)
        self.preview.move(33, 1033, -1)
        model = InputSyncModel()
        self.assertTrue(model.start(snapshot(*ROWS), self.master.selected,
                                    max_windows=3))
        self.assertEqual(model.master, (22, 1022))
        self.assertEqual(model.slaves, ((11, 1011), (33, 1033)))

    def test_two_slaves_have_independent_client_coordinate_scaling(self):
        model = InputSyncModel()
        self.master.choose(22, 1022)
        self.assertTrue(model.start(snapshot(*ROWS), self.master.selected,
                                    max_windows=3))
        sizes = {(11, 1011): ClientSize(300, 180),
                 (22, 1022): ClientSize(450, 300),
                 (33, 1033): ClientSize(600, 480)}
        self.assertEqual(model.queue_mouse(225, 150, button="left",
                                            pressed=True, sizes=sizes,
                                            now=2.0), 2)
        dispatched = []
        while model.pending:
            model.dispatch_one(sink=dispatched.append,
                               identity_ok=lambda h, p: True,
                               permission_ok=lambda: True)
        self.assertEqual([e.target for e in dispatched],
                         [(11, 1011), (33, 1033)])
        self.assertEqual([(e.x, e.y) for e in dispatched],
                         [(150, 90), (300, 240)])

    def test_shrink_three_to_two_prunes_only_removed_preview_card(self):
        self.master.choose(22, 1022)
        self.preview.move(33, 1033, -1)
        two = ROWS[:2]
        self.preview.update(two)
        self.master.update(two)
        self.assertEqual([w.hwnd for w in self.preview.ordered(two)], [11, 22])
        self.assertEqual(self.master.selected, (22, 1022))

    def test_removed_master_fallback_is_explicitly_local_not_original(self):
        self.master.choose(22, 1022)
        self.master.update((ROWS[0], ROWS[2]))
        self.assertEqual(self.master.selected, (11, 1011))

    def test_recycled_hwnd_pid_cannot_keep_old_master_selection(self):
        self.master.choose(22, 1022)
        fresh = row(22, 9022)
        self.master.update((ROWS[0], fresh, ROWS[2]))
        self.assertNotEqual(self.master.selected, (22, 1022))
        self.assertFalse(self.master.choose(22, 1022))

    def test_preview_pid_reuse_does_not_preserve_stale_manual_order(self):
        self.preview.move(33, 1033, -1)
        changed = (ROWS[0], row(33, 9033), ROWS[1])
        self.preview.update(changed)
        self.assertEqual([w.hwnd for w in self.preview.ordered(changed)],
                         [11, 22, 33])
        self.assertFalse(self.preview.move(33, 1033, -1))

    def test_master_change_requires_input_model_stop_not_auto_restart(self):
        self.master.choose(22, 1022)
        model = InputSyncModel()
        self.assertTrue(model.start(snapshot(*ROWS), self.master.selected,
                                    max_windows=3))
        model.master_changed((11, 1011))
        self.assertFalse(model.active)
        self.assertEqual(model.pending, 0)

    def test_revoke_cancels_queued_model_input(self):
        self.master.choose(22, 1022)
        model = InputSyncModel()
        model.start(snapshot(*ROWS), self.master.selected, max_windows=3)
        sizes = {(11, 1011): ClientSize(200, 100),
                 (22, 1022): ClientSize(400, 200),
                 (33, 1033): ClientSize(600, 300)}
        model.queue_mouse(20, 30, button="left", pressed=True,
                          sizes=sizes, now=1.0)
        sent = []
        self.assertIsNone(model.dispatch_one(
            sink=sent.append, identity_ok=lambda h, p: True,
            permission_ok=lambda: False))
        self.assertEqual(sent, [])
        self.assertFalse(model.active)

    def test_no_fake_roles_or_hp_in_current_source_schema(self):
        self.assertFalse(hasattr(ROWS[0], "RoleName"))
        self.assertFalse(hasattr(ROWS[0], "HP"))

    def test_preview_grid_and_layout_grid_do_not_share_state(self):
        settings = GridSettings(3, 4)
        self.assertEqual(preview_columns("3x"), 3)
        self.assertEqual(settings, GridSettings(3, 4))
        self.assertEqual(preview_columns("2x"), 2)
        self.assertEqual(settings.cols, 3)


if __name__ == "__main__":
    unittest.main()
