"""S35 E03 source-backed Start/Login lazy factory + real bootstrap protection."""
from __future__ import annotations

import contextlib
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import TLMTool
import source_backed_tab_builders as available
from shell import INFO_KEY, TAB_SPECS


class S35Tests(unittest.TestCase):
    def test_exact_three_previously_implemented_tabs_only(self):
        b=available.source_backed_tab_builders(lambda frame:frame)
        self.assertEqual(frozenset(b),available.SOURCE_BACKED_KEYS)
        self.assertEqual(frozenset(b),frozenset({INFO_KEY,"start_tab","login_tab"}))
        self.assertNotIn("proxy_tab",b)
        self.assertNotIn("party_tab",b)
        self.assertEqual(len(TAB_SPECS),15)

    def test_factories_do_not_instantiate_tabs_eagerly(self):
        with patch.object(available,"TLMStartTab") as start, \
             patch.object(available,"TLMLoginPathTab") as login:
            available.source_backed_tab_builders(lambda p:p)
            start.assert_not_called()
            login.assert_not_called()

    def test_info_factory_is_exact_caller_provided(self):
        marker=object()
        def info(parent):
            return marker
        builders=available.source_backed_tab_builders(info)
        self.assertIs(builders["info_tab"],info)
        self.assertIs(builders["info_tab"](object()),marker)

    def test_start_uses_already_verified_native_producer_and_shared_path(self):
        parent=object(); producer=object()
        with patch.object(available,"TLMStartTab",return_value="START") as start:
            builders=available.source_backed_tab_builders(
                lambda f:None,settings_file=Path("ci")/"settings.ini",
                start_producer=producer)
            self.assertEqual(builders["start_tab"](parent),"START")
            start.assert_called_once()
            self.assertIs(start.call_args.args[0],parent)
            self.assertIs(start.call_args.kwargs["producer"],producer)
            self.assertEqual(start.call_args.kwargs["grid_settings_store"].path,
                             Path("ci")/"settings.ini")

    def test_login_forwards_real_widget_kwargs_without_game_spawn(self):
        parent=object()
        choose=lambda **_: ""
        error=lambda *_:None
        with patch.object(available,"TLMLoginPathTab",return_value="LOGIN") as tab:
            builders=available.source_backed_tab_builders(
                lambda f:None, settings_file="a.ini",
                choose_directory=choose,show_error=error)
            self.assertEqual(builders["login_tab"](parent),"LOGIN")
            tab.assert_called_once_with(parent,settings_file="a.ini",
                                        choose_directory=choose,show_error=error)

    def test_invalid_info_factory_cannot_create_shell_builder(self):
        for value in (None,"INFO",object(),True):
            with self.subTest(value=value),self.assertRaises(ValueError):
                available.source_backed_tab_builders(value)

    def test_invalid_picker_or_error_handler_rejected(self):
        for arg in ("choose_directory","show_error"):
            with self.subTest(name=arg),self.assertRaises(ValueError):
                available.source_backed_tab_builders(lambda _:None,**{arg:3})

    def test_bootstrap_registers_start_login_only_under_real_info_factory(self):
        captured={}
        class TkRoot:
            def mainloop(self):
                captured["mainloop"]=True
            def destroy(self):
                captured["destroy"]=True
        class App:
            def __init__(self,root,builders):
                captured["keys"]=frozenset(builders)
                captured["root"]=root
            def position_window_top_right(self):
                captured["position"]=True
            def shutdown(self):
                captured["shutdown"]=True
        fake_tk=types.SimpleNamespace(Tk=TkRoot,TclError=Exception)
        with patch.object(TLMTool,"SingleInstanceMutex",
                          return_value=contextlib.nullcontext()),\
             patch.object(TLMTool,"SessionTee",
                          return_value=contextlib.nullcontext()),\
             patch.object(TLMTool,"StartupDiagnostics",
                          return_value=contextlib.nullcontext()),\
             patch.object(TLMTool,"TLMMainApp",App),\
             patch.dict(sys.modules,{"tkinter":fake_tk}):
            TLMTool.run_with_info_factory(lambda frame:"REAL_INFO_CALLER")
        self.assertEqual(captured["keys"],available.SOURCE_BACKED_KEYS)
        self.assertTrue(all(captured[k] for k in
                            ("mainloop","position","shutdown","destroy")))

    def test_production_entrypoint_still_explicitly_denies_without_auth(self):
        with patch.object(TLMTool,"run_with_info_factory",
                          side_effect=AssertionError("SHOULD_NOT_START")):
            self.assertEqual(TLMTool.main(),2)

    def test_no_account_login_or_proxy_implementation_added(self):
        source=Path(available.__file__).read_text(encoding="utf-8")
        self.assertNotIn("Popen(",source)
        self.assertNotIn("CreateProcess",source)
        self.assertNotIn("receive_token(",source)
        self.assertNotIn("ProxyTab(",source)


if __name__=="__main__":
    unittest.main()
