"""S23 E06 central session stdout/stderr tee / fail-closed tests.

Never touch original app logfile. Every log path is isolated under a
test-owned TemporaryDirectory; no live server or original mutex opened.
"""
from __future__ import annotations

import atexit
import contextlib
import io
from pathlib import Path
import sys
import tempfile
import threading
import types
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from session_logger import (
    SessionTee, SessionLogError, central_log_path, trim_if_needed,
    LOG_BASENAME, LOG_SUBDIR, SESSION_SEPARATOR, TRIM_NOTICE,
    ORIGINAL_MAX_SIZE, ORIGINAL_KEEP_SIZE, ORIGINAL_PARTIAL_LINE_TIMESTAMP,
    ORIGINAL_WRITER_SERIALIZATION, _TeeWriter,
)
import TLMTool


class S23LoggerTests(unittest.TestCase):
    def test_recovered_filename_subdir_and_explicit_unknowns(self):
        self.assertEqual((LOG_SUBDIR,LOG_BASENAME),("log","tlmtool.log"))
        self.assertEqual(len(SESSION_SEPARATOR),60)
        for value in (ORIGINAL_MAX_SIZE,ORIGINAL_KEEP_SIZE,
                      ORIGINAL_PARTIAL_LINE_TIMESTAMP,
                      ORIGINAL_WRITER_SERIALIZATION):
            self.assertIn("UNKNOWN",value)

    def test_test_folder_isolated_path(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(central_log_path(d),Path(d)/"log"/"tlmtool.log")

    def test_original_frozen_executable_directory(self):
        p=central_log_path(executable=r"C:\Test\TLMTool.exe",frozen=True)
        # On non-Windows unittest process, Windows-style separators need not
        # be parsed by pathlib; test only with native Path segments.
        p2=central_log_path(executable=Path("root")/"TLMTool.exe",frozen=True)
        self.assertEqual(p2,Path("root")/"log"/"tlmtool.log")
        self.assertTrue(str(p).endswith("tlmtool.log"))

    def test_constructor_no_global_stream_effect(self):
        with tempfile.TemporaryDirectory() as d:
            before=(sys.stdout,sys.stderr)
            obj=SessionTee(central_log_path(d))
            self.assertFalse(obj.active)
            self.assertEqual((sys.stdout,sys.stderr),before)
            self.assertFalse(obj.path.exists())

    def test_tee_writes_console_and_log_without_changing_text(self):
        with tempfile.TemporaryDirectory() as d:
            out,err=io.StringIO(),io.StringIO()
            filename=central_log_path(d)
            with patch.object(sys,"stdout",out),patch.object(sys,"stderr",err):
                with SessionTee(filename) as tee:
                    self.assertTrue(tee.active)
                    print("[PARTY] stdout example")
                    print("[SYNC] stderr example",file=sys.stderr)
                self.assertIs(sys.stdout,out)
                self.assertIs(sys.stderr,err)
            s=filename.read_text(encoding="utf-8")
            self.assertIn("[PARTY] stdout example",s)
            self.assertIn("[SYNC] stderr example",s)
            self.assertIn("[PARTY] stdout example",out.getvalue())
            self.assertIn("[SYNC] stderr example",err.getvalue())

    def test_session_markers_exe_python_and_end(self):
        with tempfile.TemporaryDirectory() as d:
            path=central_log_path(d)
            with SessionTee(path):
                pass
            txt=path.read_text(encoding="utf-8")
            self.assertIn("=== Start ",txt)
            self.assertIn("=== End ",txt)
            self.assertIn("exe: ",txt)
            self.assertIn("python: ",txt)
            self.assertGreaterEqual(txt.count(SESSION_SEPARATOR),2)

    def test_two_sessions_append_without_truncating_previous(self):
        with tempfile.TemporaryDirectory() as d:
            path=central_log_path(d)
            with SessionTee(path):
                print("S23_FIRST_SESSION")
            with SessionTee(path):
                print("S23_SECOND_SESSION")
            txt=path.read_text(encoding="utf-8")
            self.assertEqual(txt.count("=== Start "),2)
            self.assertEqual(txt.count("=== End "),2)
            self.assertIn("S23_FIRST_SESSION",txt)
            self.assertIn("S23_SECOND_SESSION",txt)

    def test_idempotent_close_and_repeated_start(self):
        with tempfile.TemporaryDirectory() as d:
            with SessionTee(central_log_path(d)) as tee:
                self.assertIs(tee.start(),tee)
                self.assertIs(sys.stdout,tee._out)
            self.assertFalse(tee.active)
            tee.close()

    def test_sys_fl_backups_restored_exactly(self):
        with tempfile.TemporaryDirectory() as d:
            old1=object()
            old2=object()
            with patch.object(sys,"_fl_tee_out",old1,create=True), \
                 patch.object(sys,"_fl_tee_err",old2,create=True):
                with SessionTee(central_log_path(d)):
                    self.assertIs(sys._fl_tee_out,sys.stdout.original)
                    self.assertIs(sys._fl_tee_err,sys.stderr.original)
                self.assertIs(sys._fl_tee_out,old1)
                self.assertIs(sys._fl_tee_err,old2)

    def test_stdout_and_stderr_restored_if_context_raises(self):
        with tempfile.TemporaryDirectory() as d:
            before=(sys.stdout,sys.stderr)
            with self.assertRaisesRegex(RuntimeError,"S23_TEST"):
                with SessionTee(central_log_path(d)):
                    raise RuntimeError("S23_TEST")
            self.assertEqual((sys.stdout,sys.stderr),before)
            self.assertIn("=== End ",central_log_path(d).read_text())

    def test_unwritable_path_fails_before_stream_install(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"folder_not_file"
            path.mkdir()
            before=(sys.stdout,sys.stderr)
            with self.assertRaises(SessionLogError):
                SessionTee(path).start()
            self.assertEqual((sys.stdout,sys.stderr),before)

    def test_double_logger_global_install_refused_without_stream_damage(self):
        with tempfile.TemporaryDirectory() as d:
            with SessionTee(central_log_path(Path(d)/"a")) as owner:
                captured=(sys.stdout,sys.stderr)
                with self.assertRaises(SessionLogError):
                    SessionTee(central_log_path(Path(d)/"b")).start()
                self.assertEqual((sys.stdout,sys.stderr),captured)
                self.assertTrue(owner.active)

    def test_no_magic_trimming_without_verified_sizes(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"log"
            p.write_text("x"*5000,encoding="utf-8")
            self.assertFalse(trim_if_needed(p))
            self.assertEqual(p.stat().st_size,5000)

    def test_explicit_test_only_trim_keeps_newest_full_lines(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"log"
            p.write_text("one\n"+"two\n"+"three\n"+"four\n"+"five\n",
                         encoding="utf-8")
            self.assertTrue(trim_if_needed(p,max_size=20,keep_size=15))
            result=p.read_text()
            self.assertIn(TRIM_NOTICE,result)
            self.assertIn("four",result)
            self.assertIn("five",result)
            self.assertNotIn("one\n",result)

    def test_invalid_custom_trim_bounds_never_mutate_file(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"log"
            p.write_text("keep")
            for lo,hi in [(0,1),(5,5),(5,7),(5,None),(True,2)]:
                with self.subTest(lo=lo,hi=hi), \
                     self.assertRaises(ValueError):
                    trim_if_needed(p,max_size=lo,keep_size=hi)
            self.assertEqual(p.read_text(),"keep")

    def test_all_text_records_keep_module_prefix(self):
        with tempfile.TemporaryDirectory() as d:
            with SessionTee(central_log_path(d)):
                print("[CONFIG] hello")
                print("[DAILY] hello")
                print("[LAYOUT] hello")
            txt=central_log_path(d).read_text()
            for prefix in ("[CONFIG]","[DAILY]","[LAYOUT]"):
                self.assertIn(prefix,txt)

    def test_multiple_worker_threads_writer_outputs_all_lines(self):
        with tempfile.TemporaryDirectory() as d:
            path=central_log_path(d)
            with SessionTee(path):
                def worker(index):
                    for n in range(20):
                        print(f"S23_T{index}_{n}")
                threads=[threading.Thread(target=worker,args=(i,))
                         for i in range(3)]
                for t in threads:t.start()
                for t in threads:t.join(timeout=4)
            txt=path.read_text()
            for i in range(3):
                for n in range(20):
                    self.assertIn(f"S23_T{i}_{n}",txt)

    def test_failing_atexit_registration_prevents_partial_stdout_replacement(self):
        with tempfile.TemporaryDirectory() as d:
            prev=(sys.stdout,sys.stderr)
            with patch.object(atexit,"register",side_effect=RuntimeError("test")):
                with self.assertRaises(SessionLogError):
                    SessionTee(central_log_path(d)).start()
            self.assertEqual((sys.stdout,sys.stderr),prev)

    def test_bootstrap_main_still_blocked(self):
        self.assertEqual(TLMTool.main(),2)

    def test_bootstrap_full_logger_diagnostics_mutex_order_and_close(self):
        order=[]
        class Guard:
            def __init__(self,label): self.label=label
            def __enter__(self):order.append(self.label)
            def __exit__(self,*args):order.append(self.label+"_exit")
        class Root:
            def mainloop(self):order.append("mainloop")
            def destroy(self):order.append("root_destroy")
        class App:
            def __init__(self,*_):order.append("app")
            def position_window_top_right(self):pass
            def shutdown(self):order.append("app_shutdown")
        tk=types.SimpleNamespace(Tk=lambda:(order.append("tk"),Root())[1],
                                 TclError=Exception)
        with patch.object(TLMTool,"SingleInstanceMutex",return_value=Guard("mutex")), \
             patch.object(TLMTool,"SessionTee",return_value=Guard("logger")), \
             patch.object(TLMTool,"StartupDiagnostics",return_value=Guard("diag")), \
             patch.object(TLMTool,"TLMMainApp",App), \
             patch.dict(sys.modules,{"tkinter":tk}):
            TLMTool.run_with_info_factory(lambda _:None)
        self.assertEqual(order,[
            "mutex","logger","diag","tk","app","mainloop",
            "app_shutdown","root_destroy","diag_exit","logger_exit","mutex_exit"])

    def test_bootstrap_logger_failure_prevents_diag_tk_and_releases_mutex(self):
        order=[]
        class Mutex:
            def __enter__(self):order.append("mutex")
            def __exit__(self,*_):order.append("mutex_exit")
        class FailedLogger:
            def __enter__(self):
                order.append("log_fail")
                raise SessionLogError("S23_TEST_NO_LOG")
            def __exit__(self,*_):
                raise AssertionError("Failed __enter__ must never reach __exit__")
        with patch.object(TLMTool,"SingleInstanceMutex",return_value=Mutex()), \
             patch.object(TLMTool,"SessionTee",return_value=FailedLogger()), \
             patch.object(TLMTool,"StartupDiagnostics",
                          side_effect=AssertionError("diag must not construct")):
            with self.assertRaises(SessionLogError):
                TLMTool.run_with_info_factory(lambda _:None)
        self.assertEqual(order,["mutex","log_fail","mutex_exit"])


if __name__=="__main__":
    unittest.main()
