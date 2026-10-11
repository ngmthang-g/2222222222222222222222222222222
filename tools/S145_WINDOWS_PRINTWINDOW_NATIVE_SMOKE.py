"""S145 real Windows PrintWindow+GetDIBits against own WM_PRINT painted HWND.

The known RGB (28,78,135) belongs ONLY to this self-owned test class.
Original Thần Long login1/login2 pixel colors are UNKNOWN and never filled.
No game, credentials, input, focus stealing, injection or Proxy.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s145"
OUT.mkdir(parents=True,exist_ok=True)

def main():
    if os.name!="nt" or sys.maxsize<=2**32:
        print("S145_WIN64_REQUIRED")
        return 2
    import ctypes as ct
    from ctypes import wintypes as w
    from login_printwindow_pixels import (
        NativePrintWindowFrame, RgbSample, observe_login_screen)
    from start_windows import (
        GameWindow, NativeWin32Backend, GAME_TITLE,
        UNITY_WINDOW_CLASS, GAME_PROCESS)
    from start_polling import WindowSnapshot

    user32=ct.WinDLL("user32",use_last_error=True)
    gdi32=ct.WinDLL("gdi32",use_last_error=True)
    kernel32=ct.WinDLL("kernel32",use_last_error=True)
    original_color=(28,78,135)  # TEST-OWNED; NOT original game
    hwnd=0
    blocker=0
    atom=0
    checks={}
    callback=None
    brush=0
    try:
        class WNDCLASSW(ct.Structure):
            _fields_=[
                ("style",w.UINT),("lpfnWndProc",ct.c_void_p),
                ("cbClsExtra",ct.c_int),("cbWndExtra",ct.c_int),
                ("hInstance",w.HINSTANCE),("hIcon",w.HICON),
                ("hCursor",w.HANDLE),("hbrBackground",w.HBRUSH),
                ("lpszMenuName",w.LPCWSTR),("lpszClassName",w.LPCWSTR)]
        classname="S145TestOwnedBackgroundPrintWindow"
        wproc=ct.WINFUNCTYPE(ct.c_ssize_t,w.HWND,w.UINT,w.WPARAM,w.LPARAM)
        getrect=user32.GetWindowRect
        getrect.argtypes=[w.HWND,ct.POINTER(w.RECT)]
        getrect.restype=w.BOOL
        fill=user32.FillRect
        fill.argtypes=[w.HDC,ct.POINTER(w.RECT),w.HBRUSH]
        fill.restype=ct.c_int
        makebrush=gdi32.CreateSolidBrush
        makebrush.argtypes=[w.COLORREF]
        makebrush.restype=w.HBRUSH
        colorref=original_color[0]|(original_color[1]<<8)|(original_color[2]<<16)
        brush=makebrush(colorref)
        assert brush
        default=user32.DefWindowProcW
        default.argtypes=[w.HWND,w.UINT,w.WPARAM,w.LPARAM]
        default.restype=ct.c_ssize_t
        @wproc
        def wndproc(win,msg,wparam,lparam):
            # PrintWindow sends WM_PRINT / WM_PRINTCLIENT to target.
            # Painting ONLY our own HDC means no desktop/window injection.
            if msg in (0x0317,0x0318):
                rect=w.RECT()
                if getrect(win,ct.byref(rect)):
                    paintrect=w.RECT(0,0,rect.right-rect.left,
                                   rect.bottom-rect.top)
                    fill(wparam,ct.byref(paintrect),brush)
                    return 1
            return default(win,msg,wparam,lparam)
        callback=wndproc
        kernel32.GetModuleHandleW.argtypes=[w.LPCWSTR]
        kernel32.GetModuleHandleW.restype=w.HMODULE
        inst=kernel32.GetModuleHandleW(None)
        if not inst:
            raise OSError("S145_MODULE_HANDLE_FAILED")
        user32.DestroyWindow.argtypes=[w.HWND]
        user32.DestroyWindow.restype=w.BOOL
        user32.UpdateWindow.argtypes=[w.HWND]
        user32.UpdateWindow.restype=w.BOOL
        user32.UnregisterClassW.argtypes=[w.LPCWSTR,w.HINSTANCE]
        user32.UnregisterClassW.restype=w.BOOL
        gdi32.DeleteObject.argtypes=[w.HGDIOBJ]
        gdi32.DeleteObject.restype=w.BOOL
        wc=WNDCLASSW()
        wc.lpfnWndProc=ct.cast(callback,ct.c_void_p)
        wc.hInstance=inst
        wc.lpszClassName=classname
        register=user32.RegisterClassW
        register.argtypes=[ct.POINTER(WNDCLASSW)]
        register.restype=w.ATOM
        atom=register(ct.byref(wc))
        if not atom:
            raise OSError("S145_TEST_WINDOW_CLASS_REGISTER_FAILED")
        create=user32.CreateWindowExW
        create.argtypes=[
            w.DWORD,w.LPCWSTR,w.LPCWSTR,w.DWORD,
            ct.c_int,ct.c_int,ct.c_int,ct.c_int,
            w.HWND,w.HMENU,w.HINSTANCE,w.LPVOID]
        create.restype=w.HWND
        hwnd=int(create(
            0,classname,"S145 SELF-OWNED WM_PRINT - NOT GAME",
            0x00CF0000|0x10000000,85,100,340,260,
            0,0,inst,None) or 0)
        if not hwnd:
            raise OSError("S145_TEST_WINDOW_CREATION_FAILED")
        user32.UpdateWindow(hwnd)
        native=NativeWin32Backend()
        pid=os.getpid()
        checks["real_native_top_level_hwnd_pid"]=(
            native.is_window(hwnd) and native.is_visible(hwnd)
            and native.process_id(hwnd)==pid
            and hwnd in native.enumerate_top_level())
        capture=NativePrintWindowFrame()
        frame=capture.capture(hwnd)
        checks["real_printwindow_full_window_bgra"]=(
            frame.width==340 and frame.height==260
            and len(frame.bgra)==340*260*4)
        checks["native_WM_PRINT_background_RGB_exact"]=(
            frame.rgb_at(45,40)==original_color
            and frame.rgb_at(170,150)==original_color)
        # An unrelated overlay can obscure the OS window on the desktop.
        blocker=int(create(
            0,"STATIC","S145 DIFFERENT WINDOW",
            0x80000000|0x10000000|6,
            105,140,230,175,0,0,inst,None) or 0)
        if not blocker:
            raise OSError("S145_TEST_OVERLAY_CREATION_FAILED")
        user32.UpdateWindow(blocker)
        covered=capture.capture(hwnd)
        checks["printwindow_source_still_readable_when_covered"]=(
            covered.rgb_at(170,150)==original_color)
        class TestOnlyIdentityBackend:
            def enumerate_top_level(self):return (hwnd,)
            def is_window(self,h):return native.is_window(h)
            def is_visible(self,h):return native.is_visible(h)
            def process_id(self,h):return native.process_id(h)
            def process_executable(self,p):
                return GAME_PROCESS if p==pid else "OTHER"
            def window_class(self,h):
                return UNITY_WINDOW_CLASS if h==hwnd else "OTHER"
            def title_with_timeout(self,h,timeout_ms):
                return GAME_TITLE if h==hwnd else "OTHER"
        class CountingNative:
            def __init__(self):self.calls=0
            def capture(self,h):
                self.calls+=1
                return capture.capture(h)
        source=GameWindow(hwnd,pid,GAME_TITLE,UNITY_WINDOW_CLASS,GAME_PROCESS)
        snap=WindowSnapshot(1,(source,),True)
        samples={
            "login.login1":(RgbSample(45,40,*original_color),),
            "login.login2":(RgbSample(170,150,*original_color),),
        }
        provider=CountingNative()
        observed=observe_login_screen(source,snapshot=snap,
            max_windows=1,allowed=lambda:True,
            references=samples,backend=TestOnlyIdentityBackend(),
            provider=provider)
        checks["both_explicit_test_rgb_from_one_real_frame"]=(
            observed.code=="BOTH_EXPLICIT_REFERENCES_MATCH_TEST_ONLY"
            and len(observed.matched)==2 and provider.calls==1)
        checks["real_native_game_identity_denies_our_TEST_owned_class"]=(
            observe_login_screen(source,snapshot=snap,max_windows=1,
                allowed=lambda:True,references=samples,
                backend=native,provider=provider).code==
                "STALE_OR_UNAUTHORIZED_TARGET" and provider.calls==1)
        checks["no_original_rgb_means_no_capture_or_ready"]=(
            observe_login_screen(source,snapshot=snap,max_windows=1,
                allowed=lambda:True,references=None,
                backend=TestOnlyIdentityBackend(),provider=provider).code==
                "NO_VERIFIED_ORIGINAL_PIXEL_REFERENCE"
            and provider.calls==1)
        deny=observe_login_screen(source,snapshot=snap,max_windows=1,
              allowed=lambda:False,references=samples,
              backend=TestOnlyIdentityBackend(),provider=provider)
        checks["no_permission_denies_before_real_PrintWindow"]=(
            deny.code=="STALE_OR_UNAUTHORIZED_TARGET"
            and provider.calls==1)
        user32.DestroyWindow(hwnd)
        hwnd=0
        stale=observe_login_screen(source,snapshot=snap,max_windows=1,
              allowed=lambda:True,references=samples,
              backend=TestOnlyIdentityBackend(),provider=provider)
        checks["destroyed_hwnd_fails_closed"]=(
            stale.code=="STALE_OR_UNAUTHORIZED_TARGET"
            and provider.calls==1)
        checks["no_native_input_and_no_real_game"]=True
        result={
            "status":"PASS_S145_WIN64_REAL_PRINTWINDOW_ONE_FRAME_NO_GAME"
                    if all(checks.values()) else "FAIL_S145_PRINTWINDOW",
            "native_checks":checks,
            "test_owned_color_only":True,
            "original_game_login_pixels_available":False,
            "actual_game_executed":False,
            "signed_info_authenticated":False,
            "background_only_read":True,
        }
    except Exception as e:
        result={
            "status":"FAIL_S145_PRINTWINDOW",
            "error_type":type(e).__name__,
            "error_detail":str(e)[:180],"native_checks":checks,
            "actual_game_executed":False,
        }
    finally:
        if blocker:
            user32.DestroyWindow(blocker)
        if hwnd:
            user32.DestroyWindow(hwnd)
        if atom:
            user32.UnregisterClassW(classname,inst)
        if brush:
            gdi32.DeleteObject(brush)
        callback=None
    (OUT/"native_printwindow.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(result,ensure_ascii=False))
    return 0 if result["status"].startswith("PASS_S145_") else 1

if __name__=="__main__":
    raise SystemExit(main())
