"""S155 G02 original Party read-only ready list E03 lifecycle wiring tests.

Only explicit external G03 RoleName readings ever enable live ready rows.
Production defaults to proven S154 config-only and no guessed identities.
"""
from __future__ import annotations
import sys
from pathlib import Path
import unittest
from unittest.mock import patch
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import source_backed_tab_builders as factory
from auto_role_provenance import RoleReading
from party_ready_authorized_tab import AuthorizedPartyReadyTab
from party_settings_editor import PartySettingsEditor
from party_group_config import PartyConfigStore
from shell import INFO_KEY, TabLifecycle, ALL_KEYS, MissingFeatureError


class Start:
    def __init__(self):
        self.reads=0
    def read_snapshot(self):
        self.reads+=1
        return None


class S155ReadyBinding(unittest.TestCase):
    def test_01_no_live_game_reader_uses_previous_working_S154_editor(self):
        with patch.object(factory,"PartySettingsEditor") as ui, \
             patch.object(factory,"AuthorizedPartyReadyTab") as ready:
            builder=factory.source_backed_tab_builders(lambda _:None)
            builder["party_tab"](object())
            ui.assert_called_once()
            ready.assert_not_called()

    def test_02_explicit_external_reader_requires_shared_Start_cache(self):
        role=lambda h,p:RoleReading(h,p,"ROLE_ONLY_FROM_READER")
        for kwargs in ({"party_role_reader":role},
                       {"party_role_reader":role,"start_producer":object()},
                       {"party_role_reader":role,"start_producer":SimpleNamespace(read_snapshot=3)}):
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):
                factory.source_backed_tab_builders(lambda _:None,**kwargs)

    def test_03_reject_noncallable_reader_and_mixed_names_source(self):
        with self.assertRaises(ValueError):
            factory.source_backed_tab_builders(lambda _:None,start_producer=Start(),
                                               party_role_reader="INVALID")
        with self.assertRaises(ValueError):
            factory.source_backed_tab_builders(lambda _:None,start_producer=Start(),
                                               party_role_reader=lambda h,p:None,
                                               party_names_provider=lambda:("UNTRUSTED",))

    def test_04_genuine_roster_constructor_gets_same_S09_producer_and_G08_store(self):
        start=Start()
        role=lambda h,p:RoleReading(h,p,"TEST_EXTERNAL_ROLE")
        with patch.object(factory,"AuthorizedPartyReadyTab") as widget, \
             patch.object(factory,"PartySettingsEditor") as config:
            builders=factory.source_backed_tab_builders(
                lambda _:None,start_producer=start,
                party_role_reader=role,settings_file="test_owned.ini")
            tab=builders["party_tab"](object())
            self.assertIs(tab,widget.return_value)
            self.assertIs(widget.call_args.kwargs["start_producer"],start)
            self.assertIs(widget.call_args.kwargs["read_role"],role)
            self.assertIsInstance(widget.call_args.kwargs["store"],PartyConfigStore)
            config.assert_not_called()

    def test_05_unauthorized_Party_will_never_construct_ready_widget(self):
        start=Start()
        with patch.object(factory,"AuthorizedPartyReadyTab") as widget:
            builders=factory.source_backed_tab_builders(
                lambda _:None,start_producer=start,
                party_role_reader=lambda h,p:None)
            life=TabLifecycle(builders,{key:object() for key in ALL_KEYS})
            with self.assertRaises(MissingFeatureError):
                life.ensure_built("party_tab")
            self.assertNotIn("party_tab",life.visible)
            widget.assert_not_called()

    def test_06_original_g02_lifecycle_stops_and_restarts_only_existing_reader(self):
        tab=object.__new__(AuthorizedPartyReadyTab)
        events=[]
        tab._closing_ready=False
        tab._roster_reader=SimpleNamespace(
            stop=lambda: events.append("stop"),
            start=lambda: events.append("start"))
        with patch.object(AuthorizedPartyReadyTab,"winfo_exists",return_value=1):
            tab._start_refresh()
            tab._stop_refresh()
            tab._start_refresh()
        self.assertEqual(events,["start","stop","start"])

    def test_07_shutdown_does_not_restart_closed_party_roster(self):
        tab=object.__new__(AuthorizedPartyReadyTab)
        events=[]
        tab._closing_ready=True
        tab._roster_reader=SimpleNamespace(
            stop=lambda:events.append("stop"),
            start=lambda:events.append("start"))
        tab._start_refresh()
        tab._stop_refresh()
        self.assertEqual(events,[])

    def test_08_no_party_game_input_or_new_timer_is_in_bridge(self):
        s=(ROOT/"src/party_ready_authorized_tab.py").read_text("utf-8")
        for forbidden in ("PostMessage(","ReadProcessMemory(","CreateRemoteThread(",
                          "taskkill","_toggle_run(","after(3000","sleep(","RoleID",
                          "SetWindowPos("):
            self.assertNotIn(forbidden,s)
        self.assertIn("self._roster_reader.stop()",s)

    def test_09_real_G02_provider_is_disabled_in_default_TLM_tool_bootstrap(self):
        src=(ROOT/"src/TLMTool.py").read_text("utf-8")
        self.assertNotIn("party_role_reader=",src)
        self.assertIn("return 2",src)

    def test_10_original_shared_3_second_party_refresh_constant_unmodified(self):
        from party_roster import PARTY_REFRESH_MS
        from party_ready_list import READY_COLUMNS
        self.assertEqual(PARTY_REFRESH_MS,3000)
        self.assertEqual(READY_COLUMNS,3)

    def test_11_no_party_input_field_or_Start_tab_refactor(self):
        s=(ROOT/"src/source_backed_tab_builders.py").read_text("utf-8")
        self.assertIn('"start_tab": build_start',s)
        self.assertIn('"login_tab": build_login',s)
        self.assertIn('"party_tab": build_party',s)
        self.assertNotIn('ProxyTab(',s)


if __name__=="__main__":unittest.main()
