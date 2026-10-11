"""S144 guarded F06 WM_CHAR sender, no product game integration."""
from __future__ import annotations
import ast
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from login_native_text import (
    guarded_send_login_text, _safe_printable, NativeCharPoster,
    WM_CHAR, SMTO_ABORTIFHUNG, TextDeliveryResult,
)
from start_windows import GAME_TITLE,UNITY_WINDOW_CLASS,GAME_PROCESS,GameWindow
from start_polling import WindowSnapshot

ROW=GameWindow(101,1001,GAME_TITLE,UNITY_WINDOW_CLASS,GAME_PROCESS)
SNAP=WindowSnapshot(1,(ROW,),True)


class Backend:
    def __init__(self):
        self.active=True
        self.pid=1001
        self.title=GAME_TITLE
        self.cls=UNITY_WINDOW_CLASS
        self.exe=GAME_PROCESS
        self.tops=(101,)
    def enumerate_top_level(self):return self.tops
    def is_window(self,h):return self.active and h==101
    def is_visible(self,h):return self.active and h==101
    def process_id(self,h):return self.pid
    def process_executable(self,p):return self.exe
    def window_class(self,h):return self.cls
    def title_with_timeout(self,h,timeout_ms):
        assert timeout_ms==150
        return self.title

class Poster:
    def __init__(self):
        self.chars=[]
        self.fail_on=None
        self.after=None
    def send_bmp_char(self,h,scalar):
        if self.fail_on==len(self.chars):
            return False
        self.chars.append((h,scalar))
        if self.after:
            self.after(len(self.chars))
        return True


def deliver(text="ABC",*,backend=None,poster=None,allowed=lambda:True,
            snapshot=SNAP,window=ROW,limit=1):
    return guarded_send_login_text(
        window,text,snapshot=snapshot,max_windows=limit,
        allowed=allowed,backend=backend if backend is not None else Backend(),
        poster=poster if poster is not None else Poster())


class S144OriginalBackgroundCharTests(unittest.TestCase):
    def test_01_real_f06_WM_CHAR_numeric(self):
        self.assertEqual(WM_CHAR,0x0102)
        self.assertEqual(SMTO_ABORTIFHUNG,2)
    def test_02_bmp_character_sequence_order(self):
        poster=Poster()
        result=deliver("User ABC123",poster=poster)
        self.assertEqual(result,TextDeliveryResult(
            "WIN32_WM_CHAR_SENT_NOT_GAME_LOGIN",11,11))
        self.assertEqual("".join(chr(x[1]) for x in poster.chars),"User ABC123")
    def test_03_unicode_bmp_Vietnamese(self):
        poster=Poster()
        text="Việt"
        self.assertEqual(deliver(text,poster=poster).sent,len(text))
        self.assertEqual([s for h,s in poster.chars],[ord(c) for c in text])
    def test_04_special_key_and_CR_enter_not_inferred(self):
        for text in ("\n","abc\rdef","\t","A\x00B",""):
            with self.subTest(text=repr(text)):
                self.assertEqual(deliver(text).code,"UNSUPPORTED_OR_EMPTY_TEXT")
    def test_05_non_bmp_units_not_guessed(self):
        self.assertFalse(_safe_printable("🐱"))
        self.assertEqual(deliver("🐱").sent,0)
    def test_06_over_length_denied(self):
        self.assertEqual(deliver("X"*257).code,"UNSUPPORTED_OR_EMPTY_TEXT")
    def test_07_missing_explicit_auth_denied(self):
        poster=Poster()
        result=deliver(poster=poster,allowed=lambda:False)
        self.assertEqual(result.code,"PERMISSION_DENIED")
        self.assertEqual(poster.chars,[])
    def test_08_permission_exception_denies(self):
        def boom():raise RuntimeError("not authorized")
        self.assertEqual(deliver(allowed=boom).code,"PERMISSION_DENIED")
    def test_09_foreign_unverified_non_game_candidate_refused(self):
        altered=GameWindow(101,1001,"NOT_GAME","TkTopLevel","python.exe")
        self.assertEqual(deliver(window=altered).code,"UNVERIFIED_TARGET")
    def test_10_unverified_snapshot_denied(self):
        self.assertEqual(deliver(snapshot=WindowSnapshot(1,(ROW,),False)).code,
                         "UNVERIFIED_TARGET")
    def test_11_missing_max_windows_denied(self):
        self.assertEqual(deliver(limit=0).code,"UNVERIFIED_TARGET")
        self.assertEqual(deliver(limit=True).code,"UNVERIFIED_TARGET")
    def test_12_target_not_from_snapshot_denied(self):
        other=GameWindow(102,1002,GAME_TITLE,UNITY_WINDOW_CLASS,GAME_PROCESS)
        self.assertEqual(deliver(window=other).code,"UNVERIFIED_TARGET")
    def test_13_recycled_pid_denied_before_native_send(self):
        b=Backend();b.pid=9999
        poster=Poster()
        self.assertEqual(deliver(backend=b,poster=poster).sent,0)
        self.assertEqual(poster.chars,[])
    def test_14_original_S08_exe_and_class_OR_title_guard(self):
        # S08 is deliberately GAME_PROCESS AND (UNITY_CLASS OR EXACT_TITLE);
        # a single nonmatching class/title does NOT invalidate the other
        # independently authenticated live game identity signal.
        b=Backend();b.cls="Edit"
        self.assertEqual(deliver(backend=b).sent,3)
        b=Backend();b.title="unrelated"
        self.assertEqual(deliver(backend=b).sent,3)
        b=Backend();b.cls="Edit";b.title="unrelated"
        self.assertEqual(deliver(backend=b).sent,0)
        b=Backend();b.exe="not-game.exe"
        self.assertEqual(deliver(backend=b).sent,0)
    def test_15_not_current_top_level_denied(self):
        b=Backend();b.tops=(999,)
        self.assertEqual(deliver(backend=b).sent,0)
    def test_16_duplicate_top_level_identity_denied(self):
        b=Backend();b.tops=(101,101)
        self.assertEqual(deliver(backend=b).sent,0)
    def test_17_revoke_after_first_character_cancels_remainder(self):
        backend=Backend()
        poster=Poster()
        state={"allow":True}
        poster.after=lambda _:state.update(allow=False)
        result=deliver("ABC",backend=backend,poster=poster,
                       allowed=lambda:state["allow"])
        self.assertEqual(result.code,"PARTIAL_STALE_OR_PERMISSION_REVOKED")
        self.assertEqual(result.sent,1)
        self.assertEqual(len(poster.chars),1)
    def test_18_hwnd_destroy_after_first_character_cancels_remainder(self):
        backend=Backend()
        poster=Poster()
        poster.after=lambda _:setattr(backend,"active",False)
        result=deliver("ABC",backend=backend,poster=poster)
        self.assertEqual(result.code,"PARTIAL_STALE_OR_PERMISSION_REVOKED")
        self.assertEqual(result.sent,1)
    def test_19_native_send_returns_failure_no_retry(self):
        poster=Poster()
        poster.fail_on=1
        result=deliver("ABC",poster=poster)
        self.assertEqual(result.code,"PARTIAL_NATIVE_WM_CHAR_FAILED")
        self.assertEqual(result.sent,1)
        self.assertEqual(len(poster.chars),1)
    def test_20_native_post_exception_caught_and_does_not_replay(self):
        class Failed:
            def send_bmp_char(self,*_):raise OSError("NATIVE_TIMEOUT")
        self.assertEqual(deliver(poster=Failed()).code,"NATIVE_WM_CHAR_FAILED")
    def test_21_no_mouse_global_input_or_original_C19_DLL_sender(self):
        source=(ROOT/"src/login_native_text.py").read_text(encoding="utf8")
        for banned in ("SetCursorPos(","mouse_event(","SendInput(",
                "PostMessageW(","WM_MY_SYNC_KEY","_pack(99)",
                "CreateRemoteThread(","pynput","TOKEN_HMAC_SECRET"):
            self.assertNotIn(banned,source)
    def test_22_new_python_parses(self):
        for p in ("src/login_native_text.py","tests/test_s144.py",
                  "tools/S144_WINDOWS_F06_NATIVE_WM_CHAR_SMOKE.py"):
            ast.parse((ROOT/p).read_text(encoding="utf8"))


if __name__=="__main__":
    unittest.main()
