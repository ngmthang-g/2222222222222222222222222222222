"""S154: native-capable G08 Party config-only integration with E03 authorization.

The original Party game-action controls are intentionally NOT present until
G03 RoleName/G10 team adapter and signed Info are independently verified.
"""
from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import source_backed_tab_builders as factory
from party_group_config import PartyConfigStore
from shell import ALL_KEYS, INFO_KEY, MissingFeatureError, TabLifecycle


class S154AuthorizedPartyConfig(unittest.TestCase):
    def test_01_party_is_now_registered_only_as_existing_original_tab(self):
        self.assertEqual(factory.SOURCE_BACKED_KEYS,
                         frozenset({INFO_KEY,"start_tab","login_tab","party_tab"}))
        self.assertNotIn("proxy_tab",factory.SOURCE_BACKED_KEYS)

    def test_02_builder_never_eagerly_creates_party_frame(self):
        with patch.object(factory,"PartySettingsEditor") as editor:
            builders=factory.source_backed_tab_builders(lambda p: "TEST_INFO_ONLY")
            editor.assert_not_called()
            self.assertTrue(callable(builders["party_tab"]))

    def test_03_without_signed_info_grant_party_is_never_constructed(self):
        built=[]
        builders={INFO_KEY:lambda _: "TEST_INFO_ONLY",
                  "party_tab":lambda _:built.append("PARTY")}
        tabs=TabLifecycle(builders,{key:object() for key in ALL_KEYS})
        with self.assertRaises(MissingFeatureError):
            tabs.ensure_built("party_tab")
        self.assertEqual(tabs.apply_authorized_keys(set()),frozenset({INFO_KEY}))
        self.assertEqual(built,[])

    def test_04_explicit_mock_grant_only_then_construction(self):
        called=[]
        tabs=TabLifecycle({INFO_KEY:lambda _: "TEST_INFO_ONLY",
                           "party_tab":lambda _:called.append(1) or "PARTY"},
                          {key:object() for key in ALL_KEYS})
        tabs.apply_authorized_keys({"party_tab"})
        self.assertEqual(tabs.select("party_tab"),"PARTY")
        self.assertEqual(tabs.select("party_tab"),"PARTY")
        self.assertEqual(called,[1])

    def test_05_blocked_plan_can_never_materialize_party(self):
        calls=[]
        tabs=TabLifecycle({INFO_KEY:lambda _: "TEST_INFO_ONLY",
                           "party_tab":lambda _:calls.append(1)},
                          {key:object() for key in ALL_KEYS})
        self.assertEqual(tabs.apply_authorized_keys({"party_tab"},blocked=True),
                         frozenset({INFO_KEY}))
        self.assertEqual(calls,[])

    def test_06_constructor_receives_real_store_and_explicit_role_provider(self):
        with tempfile.TemporaryDirectory() as td:
            saved=Path(td)/"settings.ini"
            names=lambda:("TEST_ACCOUNT",)
            with patch.object(factory,"PartySettingsEditor") as ui:
                builders=factory.source_backed_tab_builders(
                    lambda _:None,settings_file=saved,
                    party_names_provider=names)
                frame=object()
                panel=builders["party_tab"](frame)
                self.assertIs(panel,ui.return_value)
                ui.assert_called_once()
                args,kwargs=ui.call_args
                self.assertIs(args[0],frame)
                self.assertIsInstance(kwargs["store"],PartyConfigStore)
                self.assertEqual(kwargs["store"].settings_file,saved)
                self.assertIs(kwargs["available_names"],names)
                ui.return_value.pack.assert_called_once_with(
                    fill="both",expand=True)

    def test_07_no_reader_never_invents_role_names(self):
        with patch.object(factory,"PartySettingsEditor") as ui:
            panel=factory.source_backed_tab_builders(
                lambda _:None)["party_tab"](object())
            self.assertIs(panel,ui.return_value)
            self.assertEqual(ui.call_args.kwargs["available_names"](),())

    def test_08_invalid_reader_refused_before_any_ui(self):
        with self.assertRaises(ValueError):
            factory.source_backed_tab_builders(
                lambda _:None,party_names_provider="FAKE_NAMES")

    def test_09_no_party_game_launch_hooks(self):
        source=(ROOT/"src/source_backed_tab_builders.py").read_text("utf-8")
        for token in ("create_team(", "invite(", "send_packet(", "RoleID=",
                      "Popen(", "CreateProcess", "ProxyTab(", "input_sync"):
            self.assertNotIn(token,source)

    def test_10_original_party_config_editor_is_real_widgets_not_fake_run(self):
        source=(ROOT/"src/party_settings_editor.py").read_text("utf-8")
        self.assertIn('text="+ Thêm nhóm"',source)
        self.assertIn('command=self.add_group',source)
        self.assertIn('command=lambda num=group.num: self.remove_group(num)',source)
        self.assertNotIn('command=self._toggle_run',source)

    def test_11_party_config_g08_keys_are_exact_original(self):
        from party_group_config import AFTER_KEY,GROUPS_KEY,LEGACY_KEY
        self.assertEqual((AFTER_KEY,GROUPS_KEY,LEGACY_KEY),
                         ("party_after","party_groups","party_group1"))

    def test_12_all_other_original_tab_labels_and_order_unchanged(self):
        from shell import TAB_SPECS
        self.assertEqual([x.label for x in TAB_SPECS[:4]],
                         ["▶","Login","Party","Train"])
        self.assertEqual(len(TAB_SPECS),15)


if __name__=="__main__":
    unittest.main()
