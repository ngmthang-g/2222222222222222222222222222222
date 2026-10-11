"""S144 real Win64 WM_CHAR into one TEST-OWNED native EDIT child HWND.

This proves the F06 non-DLL printable background text stage without
launching Thần Long, sending credentials, moving mouse or enabling product.
A test-owned identity adapter is NEVER installed in production.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s144"
OUT.mkdir(parents=True,exist_ok=True)

def main()->int:
    if os.name!="nt" or sys.maxsize<=2**32:
        print("S144_NATIVE_WIN64_REQUIRED")
        return 2
    import ctypes
    from ctypes import wintypes
    import tkinter as tk
    from login_native_text import guarded_send_login_text, NativeCharPoster
    from start_windows import (
        GameWindow,NativeWin32Backend,GAME_TITLE,UNITY_WINDOW_CLASS,GAME_PROCESS,
    )
    from start_polling import WindowSnapshot
    root=None
    child=0
    checks={}
    try:
        root=tk.Tk()
        root.title("S144 SELF-OWNED WM_CHAR TARGET - NOT GAME")
        root.geometry("560x220+40+40")
        root.update()
        user32=ctypes.WinDLL("user32",use_last_error=True)
        create=user32.CreateWindowExW
        create.argtypes=[wintypes.DWORD,wintypes.LPCWSTR,wintypes.LPCWSTR,
            wintypes.DWORD,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,
            wintypes.HWND,wintypes.HMENU,wintypes.HINSTANCE,wintypes.LPVOID]
        create.restype=wintypes.HWND
        child=int(create(
            0,"EDIT","",0x40000000|0x10000000|0x00800000|0x80,
            25,35,450,35,root.winfo_id(),0,0,None) or 0)
        if not child:
            raise OSError("OWNED_NATIVE_EDIT_CREATION_FAILED")
        root.update()
        pid=os.getpid()
        native=NativeWin32Backend()
        checks["actual_native_EDIT_hwnd_pid"]=(
            native.is_window(child) and native.process_id(child)==pid
            and native.is_visible(child))
        checks["true_win32_child_not_discovered_as_game_top_level"]=(
            child not in native.enumerate_top_level())
        def read_text():
            get=user32.GetWindowTextW
            get.argtypes=[wintypes.HWND,wintypes.LPWSTR,ctypes.c_int]
            get.restype=ctypes.c_int
            buf=ctypes.create_unicode_buffer(256)
            get(child,buf,len(buf))
            return buf.value

        class TestOnlyIdentityBackend:
            """Win32 real IsWindow/PID; *synthetic game identity ONLY HERE*."""
            def enumerate_top_level(self):
                return (child,)
            def is_window(self,h):
                return native.is_window(h)
            def is_visible(self,h):
                return native.is_visible(h)
            def process_id(self,h):
                return native.process_id(h)
            def process_executable(self,p):
                return GAME_PROCESS if p==pid else "TEST_UNRELATED"
            def window_class(self,h):
                return UNITY_WINDOW_CLASS if h==child else "TEST_UNRELATED"
            def title_with_timeout(self,h,timeout_ms):
                return GAME_TITLE if h==child else "TEST_UNRELATED"

        record=GameWindow(child,pid,GAME_TITLE,UNITY_WINDOW_CLASS,GAME_PROCESS)
        snapshot=WindowSnapshot(1,(record,),True)
        backend=TestOnlyIdentityBackend()
        poster=NativeCharPoster()
        pt=wintypes.POINT()
        cursor=user32.GetCursorPos
        cursor.argtypes=[ctypes.POINTER(wintypes.POINT)]
        cursor.restype=wintypes.BOOL
        assert cursor(ctypes.byref(pt))
        before=(pt.x,pt.y)
        original="S144 Test 123"
        first=guarded_send_login_text(
            record,original,snapshot=snapshot,max_windows=1,
            allowed=lambda:True,backend=backend,poster=poster)
        checks["real_WM_CHAR_handled_by_actual_Windows_EDIT"]=(
            first.code=="WIN32_WM_CHAR_SENT_NOT_GAME_LOGIN"
            and first.sent==len(original) and read_text()==original)
        next_text=" Việt"
        second=guarded_send_login_text(
            record,next_text,snapshot=snapshot,max_windows=1,
            allowed=lambda:True,backend=backend,poster=poster)
        checks["real_native_BMP_unicode_input"]=(
            second.sent==len(next_text)
            and read_text()==original+next_text)
        assert cursor(ctypes.byref(pt))
        checks["physical_mouse_position_untouched"]=(pt.x,pt.y)==before

        denied=guarded_send_login_text(
            record,"ACCESS_DENIED",snapshot=snapshot,
            max_windows=1,allowed=lambda:False,
            backend=backend,poster=poster)
        checks["without_auth_no_native_input"]=(
            denied.code=="PERMISSION_DENIED"
            and read_text()==original+next_text)
        denied_foreign=guarded_send_login_text(
            record,"FOREIGN",snapshot=snapshot,max_windows=1,
            allowed=lambda:True,poster=poster)
        checks["default_win32_game_identity_denies_owned_EDIT"]=(
            denied_foreign.sent==0
            and read_text()==original+next_text)

        destroy=user32.DestroyWindow
        destroy.argtypes=[wintypes.HWND]
        destroy.restype=wintypes.BOOL
        checks["native_child_destroyed"]=bool(destroy(child))
        refused=guarded_send_login_text(
            record,"STALE",snapshot=snapshot,max_windows=1,
            allowed=lambda:True,backend=backend,poster=poster)
        checks["destroyed_hwnd_denied_no_redirect"]=(
            refused.sent==0 and refused.code=="STALE_OR_PERMISSION_REVOKED")
        child=0
        root.destroy()
        root=None
        result={
            "status":"PASS_S144_WIN64_REAL_F06_WM_CHAR_OWNED_EDIT_NO_GAME"
                     if all(checks.values()) else "FAIL_S144_WIN64_WM_CHAR",
            "checks":checks,"real_windows_WM_CHAR_sent":True,
            "recipient":"TEST_OWNED_EDIT_ONLY","real_game_launched":False,
            "signed_authentication":False,
            "original_DLL_sync_protocol_implemented":False,
            "real_credentials_used":False,"mouse_cursor_moved":False,
        }
    except Exception as exc:
        result={"status":"FAIL_S144_WIN64_WM_CHAR",
                "failure_type":type(exc).__name__,"checks":checks,
                "real_game_launched":False}
    finally:
        if child:
            try:ctypes.WinDLL("user32").DestroyWindow(child)
            except Exception:pass
        if root is not None:
            try:root.destroy()
            except Exception:pass
    (OUT/"native_f06_wmchar.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(result,ensure_ascii=False))
    return 0 if result["status"].startswith("PASS_S144") else 1


if __name__=="__main__":
    raise SystemExit(main())
