"""S126 H12 Farm session earn/rate formatting from validated read-only samples."""
from __future__ import annotations
from decimal import Decimal
from pathlib import Path
import sys
import unittest

R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"src"))
from train_character_samples import TrainCharacterSample
from train_extra_tracking import TrainSessionTracker, vn_money_2, vn_integer

def sample(*, bag=None, gold=None, exp=None):
    return TrainCharacterSample(101,201,bag_slots=bag,bound_money=gold,exp=exp)


class S126Tests(unittest.TestCase):
    def test_01_initial_original_line(self):
        self.assertEqual(TrainSessionTracker(clock=lambda:100).text(),
                         "0h:00p | Túi: ? | Chết: 0 | Vàng: 0,00 | 0,00 vàng/h | 0 exp/h")

    def test_02_sanitized_only_known_bag_before_session(self):
        t=TrainSessionTracker(clock=lambda:100)
        self.assertTrue(t.accept(sample(bag=98,gold=100,exp=100)))
        self.assertEqual(t.bag_slots,98)
        self.assertEqual(t.earned_bound_money_raw,0)
        self.assertEqual(t.earned_exp,0)
        self.assertFalse(t.active)

    def test_03_start_zeroes_earnings_and_death(self):
        t=TrainSessionTracker(clock=lambda:100)
        t.start_confirmed_session()
        self.assertTrue(t.record_confirmed_death())
        t.start_confirmed_session(now=200)
        self.assertEqual((t.deaths,t.earned_exp,t.bag_slots),(0,0,None))

    def test_04_first_refresh_is_baseline_not_wages(self):
        t=TrainSessionTracker(clock=lambda:200)
        t.start_confirmed_session(now=100)
        t.accept(sample(bag=2,gold=10000,exp=6000))
        self.assertEqual((t.earned_bound_money_raw,t.earned_exp),(0,0))

    def test_05_positive_gold_and_exp_only(self):
        t=TrainSessionTracker(clock=lambda:300)
        t.start_confirmed_session(now=100)
        t.accept(sample(gold=10000,exp=100))
        t.accept(sample(gold=23000,exp=400))
        self.assertEqual((t.earned_bound_money_raw,t.earned_exp),(13000,300))

    def test_06_decrease_never_subtracts_earned(self):
        t=TrainSessionTracker(clock=lambda:300)
        t.start_confirmed_session(now=100)
        t.accept(sample(gold=10000,exp=300))
        t.accept(sample(gold=12000,exp=400))
        t.accept(sample(gold=1000,exp=10))
        self.assertEqual((t.earned_bound_money_raw,t.earned_exp),(2000,100))

    def test_07_recovery_after_lower_current_counts_deltas_from_last(self):
        t=TrainSessionTracker(clock=lambda:300)
        t.start_confirmed_session(now=100)
        for g,e in [(10000,300),(12000,400),(1000,10),(3000,20)]:
            t.accept(sample(gold=g,exp=e))
        self.assertEqual((t.earned_bound_money_raw,t.earned_exp),(4000,110))

    def test_08_failed_bag_none_preserves_last_count(self):
        t=TrainSessionTracker(clock=lambda:100)
        t.accept(sample(bag=89))
        t.accept(sample(bag=None))
        self.assertEqual(t.bag_slots,89)

    def test_09_unknown_first_gold_is_not_guessed_as_zero(self):
        t=TrainSessionTracker(clock=lambda:300)
        t.start_confirmed_session(now=100)
        t.accept(sample(exp=100))
        t.accept(sample(gold=10000,exp=200))
        self.assertEqual((t.earned_bound_money_raw,t.earned_exp),(0,100))

    def test_10_1h30_elapsed_original_time_format(self):
        t=TrainSessionTracker(clock=lambda:5500)
        t.start_confirmed_session(now=100)
        self.assertTrue(t.text().startswith("1h:30p |"))

    def test_11_gold_raw_10000_per_unit_whole_session_rate(self):
        t=TrainSessionTracker(clock=lambda:3700)
        t.start_confirmed_session(now=100)
        t.accept(sample(gold=10000,exp=100))
        t.accept(sample(gold=50000,exp=150))
        data=t.stats()
        self.assertEqual(data.money_per_hour,Decimal(4))
        self.assertEqual(data.exp_per_hour,50)
        self.assertIn("Vàng: 4,00 | 4,00 vàng/h | 50 exp/h",t.text())

    def test_12_zero_elapsed_rates_safe(self):
        t=TrainSessionTracker(clock=lambda:100)
        t.start_confirmed_session(now=100)
        t.accept(sample(gold=100))
        t.accept(sample(gold=200))
        self.assertEqual((t.stats().money_per_hour,t.stats().exp_per_hour),(Decimal(0),0))

    def test_13_vietnamese_grouping(self):
        self.assertEqual(vn_integer(12345678),"12.345.678")
        self.assertEqual(vn_money_2(Decimal("3333.335")),"3.333,34")

    def test_14_no_death_without_active_session(self):
        t=TrainSessionTracker(clock=lambda:100)
        self.assertFalse(t.record_confirmed_death())
        self.assertEqual(t.deaths,0)

    def test_15_verified_death_increments_only_on_explicit_event(self):
        t=TrainSessionTracker(clock=lambda:100)
        t.start_confirmed_session()
        self.assertTrue(t.record_confirmed_death())
        self.assertEqual(t.deaths,1)

    def test_16_stop_resets_and_prevents_phantom_accumulation(self):
        t=TrainSessionTracker(clock=lambda:3700)
        t.start_confirmed_session(now=100)
        t.accept(sample(gold=1000,exp=100))
        t.accept(sample(gold=2000,exp=200))
        t.stop()
        t.accept(sample(gold=5000))
        self.assertEqual((t.active,t.earned_exp,t.earned_bound_money_raw),(False,0,0))
        self.assertIn("Vàng: 0,00",t.text())

    def test_17_invalid_bool_and_negative_values_are_not_samples(self):
        t=TrainSessionTracker(clock=lambda:100)
        self.assertFalse(t.accept(sample(bag=True)))
        self.assertFalse(t.accept(sample(exp=-1)))
        self.assertEqual(t.bag_slots,None)

    def test_18_elapsed_backwards_safely_clamped(self):
        t=TrainSessionTracker(clock=lambda:0)
        t.start_confirmed_session(now=500)
        self.assertEqual(t.stats().elapsed_seconds,0)

    def test_19_no_live_game_memory_or_unsigned_token(self):
        s=(R/"src/train_extra_tracking.py").read_text(encoding="utf-8")
        for fragment in ("ReadProcessMemory(", "PostMessage(", "WriteProcessMemory(",
                         "create_game_account(", "proxy_tab"):
            self.assertNotIn(fragment,s)

    def test_20_original_Tk_hooks_without_fake_Farm_start(self):
        s=(R/"src/train_account_rows.py").read_text(encoding="utf-8")
        for token in ('"label_extra": extra','"tracker": tracker',
                      'row["tracker"].accept(sample)',"start_confirmed_tracking(",
                      "record_confirmed_death("):
            self.assertIn(token,s)
        for invalid in ('text="Bắt đầu"', 'text="Đánh"', 'text="Bán đồ"'):
            self.assertNotIn(invalid,s)

if __name__=="__main__":
    unittest.main()
