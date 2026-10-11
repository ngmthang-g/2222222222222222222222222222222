"""S153 original C16 UnityCrashHandler taskkill image cleanup safety tests.

Original frozen EXE offset 0x2c51eb7 proves EXACT taskkill /f /t /im
UnityCrashHandler64.exe in shared close_all_game_windows. Actual process kill
is exercised ONLY on a test-owned Windows runner process (separate smoke).
"""
from __future__ import annotations
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase, mock

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"tests")]
from test_s16 import Backend, Poster, game, snap
from close_windows import (
    C16CloseAll,NativeCrashHandlerCleaner,CRASH_HANDLER_TASKKILL_ARGS,
    CRASH_HANDLER_TIMEOUT_SECONDS,CRASH_HANDLER_EXE,CloseResult
)


class Clean:
    def __init__(self,result="TASKKILL_SENT",error=False):
        self.calls=0
        self.result=result
        self.error=error
    def run(self):
        self.calls+=1
        if self.error:raise AssertionError("TEST_CALLBACK_EXCEPTION")
        return self.result


class S153OriginalCrashHandler(TestCase):
    def make(self,rows,cleaner=None):
        b=Backend(rows)
        p=Poster(b)
        c=cleaner if cleaner is not None else Clean()
        s=C16CloseAll(b,p,crash_cleanup=c)
        return s,b,p,c

    def test_01_exact_original_C16_command_and_name(self):
        self.assertEqual(CRASH_HANDLER_TASKKILL_ARGS,
                         ("taskkill","/f","/t","/im","UnityCrashHandler64.exe"))
        self.assertEqual(CRASH_HANDLER_EXE,"UnityCrashHandler64.exe")

    def test_02_three_real_validated_wmclose_posts_then_one_cleanup(self):
        rows=(game(41),game(42),game(43))
        svc,backend,poster,cleanup=self.make(rows)
        result=svc.close_all_game_windows(snap(*rows))
        self.assertEqual(result.code,"WM_CLOSE_POSTED")
        self.assertEqual(result.posted,(41,42,43))
        self.assertEqual(cleanup.calls,1)
        self.assertEqual(svc.last_crash_cleanup,"TASKKILL_SENT")

    def test_03_partial_valid_native_close_still_original_cleanup_once(self):
        rows=(game(41),game(42),game(43))
        svc,backend,poster,cleanup=self.make(rows)
        backend.actual.pop(42)
        result=svc.close_all_game_windows(snap(*rows))
        self.assertEqual(result.code,"PARTIAL_WM_CLOSE_POSTED")
        self.assertEqual(result.posted,(41,43))
        self.assertEqual(cleanup.calls,1)

    def test_04_empty_or_unverified_cache_does_not_kill(self):
        row=game(41)
        svc,_,poster,cleanup=self.make((row,))
        for snapshot in (snap(),snap(row,valid=False),None):
            self.assertEqual(svc.close_all_game_windows(snapshot).posted,())
        self.assertEqual(cleanup.calls,0)
        self.assertEqual(poster.sent,[])

    def test_05_reused_PIDs_and_fake_window_do_not_invoke_taskkill(self):
        a=game(41)
        svc,b,p,c=self.make((a,))
        b.actual[41]=game(41,98765)
        self.assertEqual(svc.close_all_game_windows(snap(a)).code,"NO_VALID_TARGETS")
        self.assertEqual(c.calls,0)

    def test_06_duplicate_cache_no_kill(self):
        a=game(41)
        svc,_,poster,cleanup=self.make((a,))
        self.assertEqual(svc.close_all_game_windows(snap(a,a)).code,"AMBIGUOUS_HWND")
        self.assertEqual(cleanup.calls,0)

    def test_07_WM_CLOSE_post_fail_no_taskkill(self):
        a=game(41)
        svc,_,poster,cleanup=self.make((a,))
        poster.fail.add(a.hwnd)
        r=svc.close_all_game_windows(snap(a))
        self.assertEqual(r.code,"NO_VALID_TARGETS")
        self.assertEqual(cleanup.calls,0)

    def test_08_taskkill_failure_does_not_claim_game_exit(self):
        a=game(41)
        svc,_,poster,cleanup=self.make((a,),Clean("TASKKILL_FAILED_OR_NO_MATCH"))
        r=svc.close_all_game_windows(snap(a))
        self.assertEqual(r,CloseResult("WM_CLOSE_POSTED",1,(41,)))
        self.assertEqual(svc.last_crash_cleanup,"TASKKILL_FAILED_OR_NO_MATCH")

    def test_09_callback_exception_does_not_abort_WM_CLOSE_report(self):
        a=game(41)
        svc,_,poster,cleanup=self.make((a,),Clean(error=True))
        r=svc.close_all_game_windows(snap(a))
        self.assertEqual(r.code,"WM_CLOSE_POSTED")
        self.assertEqual(svc.last_crash_cleanup,"TASKKILL_FAILED")
        self.assertEqual(cleanup.calls,1)

    def test_10_cleanup_status_resets_before_rejected_second_invocation(self):
        a=game(41)
        svc,_,poster,cleanup=self.make((a,))
        svc.close_all_game_windows(snap(a))
        self.assertEqual(svc.last_crash_cleanup,"TASKKILL_SENT")
        self.assertEqual(svc.close_all_game_windows(None).code,"INVALID_CACHE")
        self.assertEqual(svc.last_crash_cleanup,"NOT_RUN")
        self.assertEqual(cleanup.calls,1)

    def test_11_native_runner_uses_exact_argv_no_shell_and_bounded_timeout(self):
        proc=SimpleNamespace(returncode=0)
        with mock.patch("close_windows.os",SimpleNamespace(name="nt")), \
             mock.patch("close_windows.subprocess.run",return_value=proc) as run:
            self.assertEqual(NativeCrashHandlerCleaner().run(),"TASKKILL_SENT")
        args,kwargs=run.call_args
        self.assertEqual(args[0],list(CRASH_HANDLER_TASKKILL_ARGS))
        self.assertIs(kwargs["shell"],False)
        self.assertEqual(kwargs["timeout"],CRASH_HANDLER_TIMEOUT_SECONDS)
        self.assertFalse(kwargs["check"])

    def test_12_native_timeout_fail_closed_no_success(self):
        import subprocess
        with mock.patch("close_windows.os",SimpleNamespace(name="nt")), \
             mock.patch("close_windows.subprocess.run",
                        side_effect=subprocess.TimeoutExpired(["taskkill"],1)):
            self.assertEqual(NativeCrashHandlerCleaner().run(),"TASKKILL_FAILED")

    def test_13_no_arbitrary_game_process_terminate_or_WM_CLOSE_to_helper(self):
        text=(ROOT/"src/close_windows.py").read_text("utf-8")
        for bad in ("TerminateProcess(", "os.kill(", "shell=True",
                    "subprocess.Popen(", "ReadProcessMemory("):
            self.assertNotIn(bad,text)
        self.assertIn("if posted and self.crash_cleanup is not None",text)

if __name__=="__main__":
    import unittest
    unittest.main()
