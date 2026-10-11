"""S127 original H12 passive Farm state source/colors, no mock game runner."""
from __future__ import annotations
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from train_state_labels import (
    PassiveTrainState, STATE_COLORS, DEFAULT_COLOR, DEFAULT_STATE, color_for_state
)

EXPECTED = {
    "Đã dừng": "#555555", "Về bán đồ": "#1565c0",
    "Bán đồ": "#1565c0", "Mua thuốc": "#555555",
    "Trị liệu": "#555555", "Tới bãi train": "#1565c0",
    "Đang train": "#2e7d32", "Về địa phủ": "#c62828",
    "Đang hồi sinh": "#e65100", "Đang lọc đồ": "#8e24aa",
    "Mất kết nối": "#b71c1c",
}


class S127Tests(unittest.TestCase):
    def test_01_exact_original_state_style_11(self):
        self.assertEqual(dict(STATE_COLORS), EXPECTED)

    def test_02_default_original_initial_state(self):
        s = PassiveTrainState()
        self.assertEqual((s.text, s.color, s.generation),
                         ("Đã dừng", "#555555", -1))

    def test_03_original_unknown_dynamic_state_gray(self):
        self.assertEqual(color_for_state("Đang chờ kết nối"), "#555555")

    def test_04_wrong_type_state_gray_safe(self):
        self.assertEqual(color_for_state(None), DEFAULT_COLOR)

    def test_05_exact_colors_for_all_known_states(self):
        for state, color in EXPECTED.items():
            self.assertEqual(color_for_state(state), color)

    def test_06_stale_generation_rejected_without_ui_change(self):
        s = PassiveTrainState()
        self.assertTrue(s.accept_confirmed("Đang train", 3))
        self.assertFalse(s.accept_confirmed("Về bán đồ", 2))
        self.assertEqual((s.text, s.generation), ("Đang train", 3))

    def test_07_same_generation_ordered_state_transition(self):
        s = PassiveTrainState()
        self.assertTrue(s.accept_confirmed("Về bán đồ", 8))
        self.assertTrue(s.accept_confirmed("Bán đồ", 8))
        self.assertEqual((s.text, s.color), ("Bán đồ", "#1565c0"))

    def test_08_next_generation_accepts_original_state(self):
        s = PassiveTrainState()
        self.assertTrue(s.accept_confirmed("Đang train", 3))
        self.assertTrue(s.accept_confirmed("Đang hồi sinh", 4))
        self.assertEqual(s.color, "#e65100")

    def test_09_boolean_generation_not_a_session(self):
        s = PassiveTrainState()
        self.assertFalse(s.accept_confirmed("Đang train", True))
        self.assertEqual(s.text, DEFAULT_STATE)

    def test_10_negative_generation_rejected(self):
        s = PassiveTrainState()
        self.assertFalse(s.accept_confirmed("Đang train", -1))

    def test_11_missing_generation_rejected(self):
        self.assertFalse(PassiveTrainState().accept_confirmed("Đang train", None))

    def test_12_empty_or_non_string_rejected(self):
        s = PassiveTrainState()
        self.assertFalse(s.accept_confirmed("", 1))
        self.assertFalse(s.accept_confirmed(123, 1))
        self.assertEqual(s.text, DEFAULT_STATE)

    def test_13_extreme_unverified_text_rejected(self):
        self.assertFalse(PassiveTrainState().accept_confirmed("X" * 161, 2))

    def test_14_unknown_verified_text_can_fallback_gray(self):
        s = PassiveTrainState()
        self.assertTrue(s.accept_confirmed("Đang chờ kết nối", 4))
        self.assertEqual(s.color, "#555555")

    def test_15_reset_drops_stale_state_and_generation(self):
        s = PassiveTrainState()
        s.accept_confirmed("Đang train", 25)
        s.reset()
        self.assertEqual((s.text, s.generation, s.color),
                         (DEFAULT_STATE, -1, DEFAULT_COLOR))

    def test_16_style_mapping_frozen(self):
        with self.assertRaises(TypeError):
            STATE_COLORS["Đang train"] = "red"

    def test_17_original_tk_row_widgets_source_only(self):
        text = (ROOT/"src/train_account_rows.py").read_text(encoding="utf-8")
        for item in ('"state_dot": dot', '"state_label": lbl_state',
                     '"passive_state": passive_state', "def apply_confirmed_state(",
                     "self._render_passive_state(row)",
                     "threading.get_ident() != self._owner_thread"):
            self.assertIn(item, text)

    def test_18_no_unverified_native_game_or_proxy_source(self):
        data = (ROOT/"src/train_state_labels.py").read_text(encoding="utf-8")
        for item in ("ReadProcessMemory(", "PostMessage(", "WriteProcessMemory(",
                     "proxy_tab", "farm_click", "create_game_account(", "SendInput("):
            self.assertNotIn(item, data)


if __name__ == "__main__":
    unittest.main()
