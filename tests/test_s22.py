"""S22 E01 fail-safe early diagnostics without any fake authorization.

Tests use only temporary directories and mocked global fault/thread hooks.
A separate S22 native Windows child proves actual faulthandler logging and
real test-owned S21 mutex teardown.
"""
from __future__ import annotations

import contextlib
import faulthandler
from pathlib import Path
import sys
import tempfile
import threading
import types
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from startup_diagnostics import (
    StartupDiagnostics, DiagnosticSetupError, crash_log_path,
    ORIGINAL_CRASH_LOG_BASENAME, ORIGINAL_LOG_FORMAT,
    ORIGINAL_LOG_DIRECTORY, ORIGINAL_DEBUG_LOGGER_SETUP,
)
import TLMTool


class DiagnosticsS22Tests(unittest.TestCase):
    def test_original_log_name_and_unsolved_format_location_explicit(self):
        self.assertEqual(ORIGINAL_CRASH_LOG_BASENAME, "crash_fault.log")
        self.assertIn("UNKNOWN", ORIGINAL_LOG_DIRECTORY)
        self.assertIn("UNKNOWN", ORIGINAL_LOG_FORMAT)
        self.assertIn("NOT_REBUILT", ORIGINAL_DEBUG_LOGGER_SETUP)

    def test_explicit_temp_parent_path(self):
        with tempfile.TemporaryDirectory(prefix="s22_test_") as d:
            self.assertEqual(crash_log_path(d),Path(d)/"crash_fault.log")

    def test_localappdata_is_only_a_documented_policy(self):
        with patch.dict("os.environ",{"LOCALAPPDATA":"C:\\Temp\\S22_ONLY_TEST"}):
            self.assertEqual(crash_log_path(),
                 Path("C:\\Temp\\S22_ONLY_TEST")/"TLMTool"/"crash_fault.log")

    def test_constructor_has_no_global_hook_side_effect(self):
        with tempfile.TemporaryDirectory() as d:
            old=threading.excepthook
            diag=StartupDiagnostics(Path(d)/"crash_fault.log")
            self.assertFalse(diag.active)
            self.assertIs(threading.excepthook,old)
            self.assertFalse(diag.path.exists())

    def test_start_idempotent_close_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            filename=Path(d)/"crash_fault.log"
            diag=StartupDiagnostics(filename)
            with patch.object(faulthandler,"is_enabled",return_value=False), \
                 patch.object(faulthandler,"enable") as enable, \
                 patch.object(faulthandler,"disable") as disable:
                self.assertIs(diag.start(),diag)
                self.assertTrue(diag.active)
                self.assertIs(diag.start(),diag)
                enable.assert_called_once()
                diag.close()
                diag.close()
                disable.assert_called_once()
            self.assertFalse(diag.active)
            self.assertTrue(filename.exists())

    def test_threading_hook_restored_after_normal_exit(self):
        with tempfile.TemporaryDirectory() as d:
            original=threading.excepthook
            with patch.object(faulthandler,"is_enabled",return_value=True), \
                 StartupDiagnostics(Path(d)/"log.txt") as obj:
                self.assertTrue(obj.active)
                self.assertIsNot(threading.excepthook,original)
                self.assertFalse(obj._owns_fault_handler)
            self.assertIs(threading.excepthook,original)

    def test_preexisting_faulthandler_not_disabled(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.object(faulthandler,"is_enabled",return_value=True), \
                 patch.object(faulthandler,"enable") as enable, \
                 patch.object(faulthandler,"disable") as disable:
                with StartupDiagnostics(Path(d)/"log"):
                    pass
                enable.assert_not_called()
                disable.assert_not_called()

    def test_new_fault_handler_enabled_disabled_only_when_owned(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.object(faulthandler,"is_enabled",return_value=False), \
                 patch.object(faulthandler,"enable") as enable, \
                 patch.object(faulthandler,"disable") as disable:
                with StartupDiagnostics(Path(d)/"nested"/"log"):
                    self.assertTrue(enable.called)
                disable.assert_called_once()

    def test_startup_exception_is_logged_then_propagates(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"crash_fault.log"
            with patch.object(faulthandler,"is_enabled",return_value=True):
                with self.assertRaisesRegex(RuntimeError,"S22_FAKE_AUTH_FAILURE"):
                    with StartupDiagnostics(f):
                        raise RuntimeError("S22_FAKE_AUTH_FAILURE")
            txt=f.read_text(encoding="utf-8")
            self.assertIn("S22 STARTUP_EXCEPTION",txt)
            self.assertIn("RuntimeError: S22_FAKE_AUTH_FAILURE",txt)

    def test_manual_record_exception_when_active_only(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"log.txt"
            diag=StartupDiagnostics(f)
            try:
                raise ValueError("S22_EXPLICIT_TRACE")
            except ValueError as err:
                diag.record_exception(err) # inactive: no output
                with patch.object(faulthandler,"is_enabled",return_value=True):
                    with diag:
                        diag.record_exception(err)
            self.assertIn("ValueError: S22_EXPLICIT_TRACE",f.read_text())

    def test_thread_hook_calls_prior_hook_after_writing_trace(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"log.txt"
            previous=[]
            def old(args): previous.append(args.exc_value)
            with patch.object(threading,"excepthook",old), \
                 patch.object(faulthandler,"is_enabled",return_value=True):
                with StartupDiagnostics(f):
                    try:
                        raise RuntimeError("S22_CHILD_THREAD_EXCEPTION")
                    except RuntimeError as err:
                        args=types.SimpleNamespace(
                            exc_type=type(err),exc_value=err,
                            exc_traceback=err.__traceback__,
                            thread=threading.current_thread())
                        threading.excepthook(args)
            self.assertEqual(len(previous),1)
            self.assertIn("S22 THREAD_EXCEPTION",f.read_text(encoding="utf-8"))
            self.assertIn("S22_CHILD_THREAD_EXCEPTION",f.read_text(encoding="utf-8"))

    def test_partial_setup_file_directory_failure_restores_thread_hook(self):
        with tempfile.TemporaryDirectory() as d:
            filename=Path(d)/"folder_as_log"
            filename.mkdir()
            before=threading.excepthook
            with self.assertRaises(DiagnosticSetupError):
                StartupDiagnostics(filename).start()
            self.assertIs(threading.excepthook,before)

    def test_partial_setup_faulthandler_failure_closes_file(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"log.txt"
            before=threading.excepthook
            diag=StartupDiagnostics(f)
            with patch.object(faulthandler,"is_enabled",return_value=False), \
                 patch.object(faulthandler,"enable",side_effect=OSError("fake")):
                with self.assertRaises(DiagnosticSetupError):
                    diag.start()
            self.assertFalse(diag.active)
            self.assertIs(threading.excepthook,before)
            self.assertIsNone(diag._file)

    def test_later_global_hook_is_never_overwritten_during_cleanup(self):
        with tempfile.TemporaryDirectory() as d:
            later=lambda args: None
            original=threading.excepthook
            with patch.object(faulthandler,"is_enabled",return_value=True):
                x=StartupDiagnostics(Path(d)/"log")
                x.start()
                try:
                    threading.excepthook=later
                    x.close()
                    self.assertIs(threading.excepthook,later)
                finally:
                    threading.excepthook=original

    def test_no_running_thread_monitor_or_background_network(self):
        self.assertFalse(hasattr(StartupDiagnostics,"grant_license"))
        self.assertFalse(hasattr(StartupDiagnostics,"open_game"))
        self.assertFalse(hasattr(StartupDiagnostics,"os_exit"))

    def test_main_remains_return_2_no_real_info(self):
        self.assertEqual(TLMTool.main(),2)

    def test_gui_startup_order_and_final_mutex_release(self):
        observed=[]
        class Mutex:
            def __enter__(self):observed.append("mutex")
            def __exit__(self,*args):observed.append("mutex_exit")
        class Diagnostics:
            def __enter__(self):observed.append("diagnostics")
            def __exit__(self,*args):observed.append("diagnostics_exit")
        class Root:
            def mainloop(self):observed.append("mainloop")
            def destroy(self):observed.append("root_destroy")
        class App:
            def __init__(self,*_):observed.append("app")
            def position_window_top_right(self):observed.append("position")
            def shutdown(self):observed.append("app_shutdown")
        tk=types.SimpleNamespace(Tk=lambda:(observed.append("Tk"),Root())[1],
                                 TclError=Exception)
        with patch.object(TLMTool,"SingleInstanceMutex",return_value=Mutex()), \
             patch.object(TLMTool,"StartupDiagnostics",return_value=Diagnostics()), \
             patch.object(TLMTool,"TLMMainApp",App), \
             patch.dict(sys.modules,{"tkinter":tk}):
            TLMTool.run_with_info_factory(lambda _:None)
        self.assertEqual(observed,[
            "mutex","diagnostics","Tk","app","position","mainloop",
            "app_shutdown","root_destroy","diagnostics_exit","mutex_exit"])

    def test_gui_setup_failure_does_not_call_tk_and_still_closes_mutex(self):
        seen=[]
        class M:
            def __enter__(self):seen.append("mutex")
            def __exit__(self,*_):seen.append("mutex_exit")
        class D:
            def __enter__(self):
                seen.append("diag_fail")
                raise DiagnosticSetupError("NO_LOG")
            def __exit__(self,*_):seen.append("diag_exit")
        with patch.object(TLMTool,"SingleInstanceMutex",return_value=M()), \
             patch.object(TLMTool,"StartupDiagnostics",return_value=D()):
            with self.assertRaises(DiagnosticSetupError):
                TLMTool.run_with_info_factory(lambda _:None)
        self.assertEqual(seen,["mutex","diag_fail","mutex_exit"])


if __name__=="__main__":
    unittest.main()
