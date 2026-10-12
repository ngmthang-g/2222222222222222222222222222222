"""S176: real Party candidate visibility from the shared S09 HWND/PID cache.

These tests explicitly DO NOT attest an in-game RoleName or HP reader.
No private game credentials, original license or automated game action.
"""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import source_backed_tab_builders as factory
from party_ready_list import PartyReadyConfigEditor
from party_roster import PartyMember, PartyRoster


class S176IndependentPartyReadOnlyTests(unittest.TestCase):
    def setUp(self):
        self.cache = SimpleNamespace(read_snapshot=lambda: None)

    def test_01_explicit_opt_in_uses_preexisting_party_roster_without_role_reader(self):
        with patch.object(factory, "AuthorizedPartyReadyTab") as ready, \
             patch.object(factory, "PartySettingsEditor") as config:
            b = factory.source_backed_tab_builders(
                lambda _: None, start_producer=self.cache,
                party_observe_windows=True, settings_file="test.ini")
            frame = object()
            self.assertIs(b["party_tab"](frame), ready.return_value)
            self.assertIs(ready.call_args.kwargs["start_producer"], self.cache)
            self.assertIsNone(ready.call_args.kwargs["read_role"])
            config.assert_not_called()

    def test_02_historic_default_behavior_does_not_change(self):
        with patch.object(factory, "AuthorizedPartyReadyTab") as ready, \
             patch.object(factory, "PartySettingsEditor") as config:
            b = factory.source_backed_tab_builders(
                lambda _: None, start_producer=self.cache)
            b["party_tab"](object())
            ready.assert_not_called()
            config.assert_called_once()

    def test_03_observer_refuses_missing_or_invalid_shared_cache(self):
        for p in (None, object(), SimpleNamespace(read_snapshot=42)):
            with self.subTest(producer=p), self.assertRaisesRegex(
                    ValueError, "S176_PARTY_OBSERVE_REQUIRES_SHARED_START_CACHE"):
                factory.source_backed_tab_builders(
                    lambda _: None, start_producer=p,
                    party_observe_windows=True)

    def test_04_observer_refuses_fake_external_names_and_invalid_flag(self):
        with self.assertRaisesRegex(ValueError, "S176_PARTY_OBSERVE_CANNOT"):
            factory.source_backed_tab_builders(
                lambda _:None, start_producer=self.cache,
                party_observe_windows=True,
                party_names_provider=lambda: ("FAKE",))
        with self.assertRaisesRegex(ValueError, "S176_PARTY_OBSERVE_FLAG"):
            factory.source_backed_tab_builders(
                lambda _:None, party_observe_windows=1)

    def test_05_true_candidate_count_visible_but_never_a_character_name(self):
        roster = PartyRoster()
        roster.code = "ROLE_READER_UNAVAILABLE"
        roster.members = (PartyMember(101, 1001, None),
                          PartyMember(102, 1002, None))
        self.assertEqual(roster.ready_names(), ())
        view = SimpleNamespace(
            _closing_ready=False, _roster=None,
            _refresh_ready=Mock(), _refresh_dropdown_values=Mock(),
            status=Mock())
        PartyReadyConfigEditor._on_roster(view, roster)
        view._refresh_ready.assert_called_once()
        view._refresh_dropdown_values.assert_called_once()
        caption = view.status.configure.call_args.kwargs["text"]
        self.assertIn("2 cửa sổ game", caption)
        self.assertIn("chưa xác minh", caption)
        self.assertNotIn("1001", caption)
        self.assertNotIn("1002", caption)

    def test_06_stale_and_stopped_candidates_never_remain_claimed_live(self):
        view = SimpleNamespace(
            _closing_ready=False, _roster=None,
            _refresh_ready=Mock(), _refresh_dropdown_values=Mock(),
            status=Mock())
        roster=PartyRoster()
        for code in ("INVALID_START_CACHE", "STALE_WORKER_RESULT", "STOPPED"):
            roster.code=code
            PartyReadyConfigEditor._on_roster(view, roster)
            self.assertEqual(view.status.configure.call_args.kwargs["text"],
                             "Chưa có dữ liệu nhân vật đã xác minh")

    def test_07_independent_app_enables_same_shared_cache_not_a_new_scanner(self):
        import TLMToolIndependent as independent
        class TestProducer: pass
        shared = TestProducer()
        with patch.object(independent, "StartWindowProducer", TestProducer), \
             patch.object(independent, "source_backed_tab_builders",
                          return_value={}) as builders:
            built=independent.make_independent_builders("test.ini", shared)
        self.assertTrue(builders.call_args.kwargs["party_observe_windows"])
        self.assertIs(builders.call_args.kwargs["start_producer"], shared)
        self.assertIn("party_tab", factory.SOURCE_BACKED_KEYS)
        self.assertIn("trainlsv_tab", built)

    def test_08_no_game_reader_is_created_by_s176_change(self):
        a=(ROOT/"src"/"source_backed_tab_builders.py").read_text("utf-8")
        b=(ROOT/"src"/"TLMToolIndependent.py").read_text("utf-8")
        self.assertIn("party_observe_windows=True", b)
        self.assertNotIn("party_role_reader=", b)
        self.assertIn("read_role=party_role_reader", a)
        self.assertNotIn("ReadProcessMemory(", b)


if __name__ == "__main__":
    unittest.main()
