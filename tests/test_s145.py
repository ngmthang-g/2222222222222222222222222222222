"""S145 original F06 single PrintWindow frame and explicit-only pixel refs.

TEST-OWNED RGB fixtures, never original Thần Long login RGB or pixels.
"""
from __future__ import annotations
import ast
from dataclasses import FrozenInstanceError
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from login_printwindow_pixels import (
    CapturedBgra, RgbSample, LoginPixelResult,
    LOGIN_REFERENCES, _valid_reference, compare_reference,
    observe_login_screen, MAX_CAPTURE_WIDTH,
)
from start_polling import WindowSnapshot
from start_windows import GameWindow, GAME_TITLE,UNITY_WINDOW_CLASS,GAME_PROCESS

ROW=GameWindow(101,201,GAME_TITLE,UNITY_WINDOW_CLASS,GAME_PROCESS)
SNAP=WindowSnapshot(1,(ROW,),True)
FRAME=CapturedBgra(2,2,bytes([
    3,2,1,255, 6,5,4,255,
    9,8,7,255, 12,11,10,255,
]))
REF={
    "login.login1":(RgbSample(0,0,1,2,3),RgbSample(1,0,4,5,6)),
    "login.login2":(RgbSample(0,1,7,8,9),RgbSample(1,1,10,11,12)),
}
class FakeBackend:
    def __init__(self):
        self.hwnds=(101,)
        self.pid=201
        self.exe=GAME_PROCESS
        self.cls=UNITY_WINDOW_CLASS
        self.title=GAME_TITLE
        self.visible=True
        self.alive=True
    def enumerate_top_level(self):return self.hwnds
    def is_window(self,hwnd):return self.alive and hwnd==101
    def is_visible(self,hwnd):return self.visible and hwnd==101
    def process_id(self,hwnd):return self.pid
    def process_executable(self,pid):return self.exe
    def window_class(self,hwnd):return self.cls
    def title_with_timeout(self,hwnd,ms):return self.title

class FakeProvider:
    def __init__(self,frame=FRAME,after=None):
        self.calls=[]
        self.frame=frame
        self.after=after
    def capture(self,hwnd):
        self.calls.append(hwnd)
        if self.after:self.after()
        return self.frame

def observe(refs=REF,*,backend=None,provider=None,allowed=lambda:True,snapshot=SNAP,limit=1):
    return observe_login_screen(ROW,snapshot=snapshot,
         max_windows=limit,allowed=allowed,references=refs,
         backend=backend if backend is not None else FakeBackend(),
         provider=provider if provider is not None else FakeProvider())

class S145F06PrintWindowReadOnlyTests(unittest.TestCase):
    def test_01_proven_original_labels_only(self):
        self.assertEqual(LOGIN_REFERENCES,("login.login1","login.login2"))
    def test_02_pixel_B_G_R_to_RGB(self):
        self.assertEqual(FRAME.rgb_at(0,0),(1,2,3))
        self.assertEqual(FRAME.rgb_at(1,1),(10,11,12))
    def test_03_both_explicit_refs_one_capture(self):
        p=FakeProvider()
        result=observe(provider=p)
        self.assertEqual(result.code,"BOTH_EXPLICIT_REFERENCES_MATCH_TEST_ONLY")
        self.assertEqual(result.matched,LOGIN_REFERENCES)
        self.assertTrue(result.observed_one_full_frame)
        self.assertEqual(p.calls,[101])
    def test_04_mismatch_ref_no_login_ready(self):
        refs={**REF,"login.login2":(RgbSample(1,1,0,0,0),)}
        result=observe(refs)
        self.assertEqual(result.code,"LOGIN_REFERENCE_MISMATCH")
        self.assertEqual(result.matched,("login.login1",))
    def test_05_missing_original_data_no_capture_or_ready(self):
        p=FakeProvider()
        for refs in (None,{},{"login.login1":REF["login.login1"]}):
            with self.subTest(refs=refs):
                result=observe(refs,provider=p)
                self.assertEqual(result.code,"NO_VERIFIED_ORIGINAL_PIXEL_REFERENCE")
                self.assertEqual(result.matched,())
        self.assertEqual(p.calls,[])
    def test_06_unsourced_extra_keys_refused(self):
        self.assertEqual(observe({**REF,"login.update":(RgbSample(0,0,1,2,3),)}).code,
                         "NO_VERIFIED_ORIGINAL_PIXEL_REFERENCE")
    def test_07_invalid_coordinate_and_rgb_refused(self):
        for v in (RgbSample(-1,0,1,2,3),RgbSample(0,0,256,2,3),
                  RgbSample(0,0,True,2,3),RgbSample(1.0,0,1,2,3)):
            with self.subTest(v=v):
                self.assertFalse(_valid_reference((v,)))
    def test_08_wrong_pixel_bounds_cannot_match(self):
        bad=(RgbSample(3,0,1,2,3),)
        self.assertFalse(compare_reference(FRAME,bad))
    def test_09_wrong_FRAME_length_denied(self):
        bad=CapturedBgra(2,2,b"\x01\x02\x03\x04")
        self.assertFalse(compare_reference(bad,REF["login.login1"]))
        self.assertEqual(observe(provider=FakeProvider(bad)).code,"INVALID_CAPTURE")
    def test_10_oversize_frame_refused(self):
        bad=CapturedBgra(MAX_CAPTURE_WIDTH+1,2,b"")
        self.assertEqual(observe(provider=FakeProvider(bad)).code,"INVALID_CAPTURE")
    def test_11_permission_revoked_before_capture(self):
        p=FakeProvider()
        result=observe(provider=p,allowed=lambda:False)
        self.assertEqual(result.code,"STALE_OR_UNAUTHORIZED_TARGET")
        self.assertEqual(p.calls,[])
    def test_12_permission_revoked_after_capture_denies_match(self):
        active=[True]
        p=FakeProvider(after=lambda:active.__setitem__(0,False))
        result=observe(provider=p,allowed=lambda:active[0])
        self.assertEqual(result.code,"STALE_OR_UNAUTHORIZED_AFTER_CAPTURE")
        self.assertEqual(result.matched,())
    def test_13_recycled_game_pid_denied(self):
        b=FakeBackend();b.pid=999
        self.assertEqual(observe(backend=b).code,"STALE_OR_UNAUTHORIZED_TARGET")
    def test_14_executable_mismatch_denied(self):
        b=FakeBackend();b.exe="not-game.exe"
        self.assertEqual(observe(backend=b).code,"STALE_OR_UNAUTHORIZED_TARGET")
    def test_15_unverified_cache_denied(self):
        self.assertEqual(observe(snapshot=WindowSnapshot(1,(ROW,),False)).code,
                         "UNVERIFIED_TARGET")
    def test_16_window_limit_not_verified(self):
        self.assertEqual(observe(limit=0).code,"UNVERIFIED_TARGET")
    def test_17_mismatched_reference_invalid_does_not_invoke_GDI(self):
        p=FakeProvider()
        refs={**REF,"login.login2":()}
        self.assertEqual(observe(refs,provider=p).code,
                         "NO_VERIFIED_ORIGINAL_PIXEL_REFERENCE")
        self.assertEqual(p.calls,[])
    def test_18_capture_fails_no_false_ready(self):
        class Bad:
            def capture(self,hwnd):raise OSError("native failure")
        self.assertEqual(observe(provider=Bad()).code,"PRINTWINDOW_CAPTURE_FAILED")
    def test_19_snapshot_member_required(self):
        other=GameWindow(202,333,GAME_TITLE,UNITY_WINDOW_CLASS,GAME_PROCESS)
        s=WindowSnapshot(1,(other,),True)
        self.assertEqual(observe(snapshot=s).code,"UNVERIFIED_TARGET")
    def test_20_immutable_pixel_template(self):
        p=RgbSample(0,0,1,2,3)
        with self.assertRaises(FrozenInstanceError):p.red=42
    def test_21_no_game_auth_credentials_mouse_or_hooks(self):
        s=(ROOT/"src/login_printwindow_pixels.py").read_text(encoding="utf8")
        for bad in ("SendInput(", "mouse_event(", "PostMessageW(",
                    "WriteProcessMemory(", "CreateRemoteThread(",
                    "TOKEN_PUBLIC_KEY_PEM", "login.login1 = RgbSample("):
            self.assertNotIn(bad,s)
    def test_22_true_PrintWindow_and_one_capture_source(self):
        s=(ROOT/"src/login_printwindow_pixels.py").read_text(encoding="utf8")
        for word in ("PrintWindow","GetWindowRect","GetDIBits",
                     "GetWindowDC","compare_reference","provider.capture(window.hwnd)"):
            self.assertIn(word,s)
    def test_23_hwnd_destroyed_during_native_printwindow_rejects_pixels(self):
        backend=FakeBackend()
        provider=FakeProvider(after=lambda:setattr(backend,"alive",False))
        result=observe(backend=backend,provider=provider)
        self.assertEqual(result.code,"STALE_OR_UNAUTHORIZED_AFTER_CAPTURE")
        self.assertEqual(result.matched,())
        self.assertEqual(provider.calls,[101])

    def test_24_oversize_unknown_reference_refuses_native_capture(self):
        provider=FakeProvider()
        large={**REF,"login.login2":tuple(
            RgbSample(0,0,1,2,3) for _ in range(33))}
        self.assertEqual(observe(large,provider=provider).code,
                         "NO_VERIFIED_ORIGINAL_PIXEL_REFERENCE")
        self.assertEqual(provider.calls,[])

    def test_25_ast_all_new_S145_files(self):
        for p in ("src/login_printwindow_pixels.py","tests/test_s145.py",
                  "tools/S145_WINDOWS_PRINTWINDOW_NATIVE_SMOKE.py"):
            ast.parse((ROOT/p).read_text(encoding="utf8"))

if __name__=="__main__":
    unittest.main()
