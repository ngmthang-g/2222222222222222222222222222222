"""S89 original G08 Party configuration persistence and UI-bound model tests."""
from __future__ import annotations
import configparser
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from party_group_config import (
    AFTER_VALUES, DORMANT_KEYS, MAX_GROUP_MEMBERS,
    PartyConfigStore, PartyGroup, PartySettings,
)
from settings_store import read_settings


class S89PartyConfigTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "settings.ini"
        self.store = PartyConfigStore(self.path)

    def seed(self, settings):
        self.path.write_text(settings, encoding="utf-8")

    def test_01_empty_load_never_writes_or_creates_settings_ini(self):
        value = self.store.load()
        self.assertEqual(value.after, "wait")
        self.assertEqual(value.groups, (PartyGroup(1, ()),))
        self.assertFalse(self.path.exists())

    def test_02_all_original_party_after_choices(self):
        for mode in AFTER_VALUES:
            self.store.save(PartySettings().change_after(mode))
            self.assertEqual(self.store.load().after, mode)

    def test_03_unicode_roundtrip_and_not_ascii_escape(self):
        state = PartySettings().select_member(1, 0, "Thiên Địa")
        state = state.select_member(1, 4, "Bạch Vân")
        self.store.save(state)
        raw = self.path.read_text("utf-8")
        self.assertIn("Thiên Địa", raw)
        self.assertNotIn(r"\\u00", raw)
        self.assertEqual(self.store.load().groups[0].members[4], "Bạch Vân")

    def test_04_current_json_is_numbered_multi_group_six_slots(self):
        value = PartySettings().add_group().select_member(2, 5, "Đội viên")
        self.store.save(value)
        parser = read_settings(self.path)
        groups = json.loads(parser.get("Settings", "party_groups"))
        self.assertEqual(groups[1]["num"], 2)
        self.assertEqual(groups[1]["members"][5], "Đội viên")
        self.assertEqual(len(groups[1]["members"]), MAX_GROUP_MEMBERS)
        self.assertEqual(len(self.store.load().groups), 2)

    def test_05_legacy_group_one_mirror_filters_empty_duplicate(self):
        value = PartySettings(groups=(PartyGroup(1, ("A", "", "A", "B")),))
        self.store.save(value)
        parsed = read_settings(self.path)
        self.assertEqual(json.loads(parsed.get("Settings", "party_group1")), ["A", "B"])

    def test_06_legacy_only_load_uses_group_one_names(self):
        self.seed("[Settings]\nparty_group1 = [\"An\", \"Bình\"]\n")
        value = self.store.load()
        self.assertEqual(value.groups[0].members, ("An", "Bình"))

    def test_07_bad_current_schema_falls_back_to_legacy(self):
        self.seed("[Settings]\nparty_groups = {\"fake\": 1}\nparty_group1 = [\"old\"]\n")
        self.assertEqual(self.store.load().groups[0].members, ("old",))

    def test_08_invalid_after_returns_wait_without_rewriting_file(self):
        raw = "[Settings]\nparty_after = zzz_invalid\nparty_groups = broken\n"
        self.seed(raw)
        self.assertEqual(self.store.load().after, "wait")
        self.assertEqual(self.path.read_text("utf-8"), raw)

    def test_09_remove_middle_group_renumbers_and_leaves_one(self):
        state = PartySettings().add_group().add_group()
        state = state.select_member(3, 0, "third").remove_group(2)
        self.assertEqual(tuple(g.num for g in state.groups), (1, 2))
        self.assertEqual(state.groups[1].members[0], "third")
        self.assertEqual(state.remove_group(2).remove_group(1).groups, (PartyGroup(1, ()),))

    def test_10_reject_invalid_member_type_or_slot_without_disk_change(self):
        self.store.save(PartySettings())
        original = self.path.read_bytes()
        with self.assertRaises(ValueError):
            PartySettings(groups=(PartyGroup(1, ("A", 123)),))
        with self.assertRaises(ValueError):
            PartySettings().select_member(1, 6, "foo")
        with self.assertRaises(ValueError):
            self.store.save("fake JSON payload")
        self.assertEqual(self.path.read_bytes(), original)

    def test_11_preserve_other_tab_options_and_sections(self):
        self.seed("[Settings]\ngame_dir = Z:\\Games\ngrid_cols = 3\n[Other]\nstate = kept\n")
        self.store.save(PartySettings().change_after("phoban"))
        parser = read_settings(self.path)
        self.assertEqual(parser.get("Settings", "game_dir"), r"Z:\Games")
        self.assertEqual(parser.get("Settings", "grid_cols"), "3")
        self.assertEqual(parser.get("Other", "state"), "kept")

    def test_12_remove_only_original_dormant_party_keys(self):
        keys = "\n".join(key + " = stale" for key in DORMANT_KEYS)
        self.seed("[Settings]\n" + keys + "\nnot_party = keep\n")
        self.store.save(PartySettings())
        p = read_settings(self.path)
        self.assertTrue(all(not p.has_option("Settings", k) for k in DORMANT_KEYS))
        self.assertEqual(p.get("Settings", "not_party"), "keep")

    def test_13_saved_config_does_not_include_runtime_ids(self):
        state = PartySettings().select_member(1, 0, "Test")
        self.store.save(state)
        d = json.loads(read_settings(self.path).get("Settings", "party_groups"))
        self.assertEqual(sorted(d[0].keys()), ["members", "num"])
        for forbidden in ("hwnd", "pid", "RoleID", "TeamID", "running"):
            self.assertNotIn(forbidden, json.dumps(d))

    def test_14_reject_unknown_after_or_bad_group_number(self):
        with self.assertRaises(ValueError):
            PartySettings("any")
        with self.assertRaises(ValueError):
            PartySettings(groups=(PartyGroup(2, ("A",)),))
        with self.assertRaises(ValueError):
            PartySettings().remove_group(10)

    def test_15_source_does_not_create_fake_party_or_auth_actions(self):
        source = (ROOT / "src/party_group_config.py").read_text("utf-8")
        widget = (ROOT / "src/party_settings_editor.py").read_text("utf-8")
        self.assertIn("write_settings", source)
        self.assertIn('text="+ Thêm nhóm"', widget)
        for term in ("CreateRemoteThread(", "ReadProcessMemory(",
                     "PostMessage(", "TOKEN_HMAC_SECRET", "200051",
                     "bind_window_identity(", "_run_one_group("):
            self.assertNotIn(term, source + widget)


if __name__ == "__main__":
    unittest.main()
