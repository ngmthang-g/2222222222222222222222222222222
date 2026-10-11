"""S146 C12 explicitly documented native show (0,0), TEST-OWNED HWND only.

Original C12 specific method docs+log show both windows at (0,0) with
original size; generic doc mentions old rectangles. Isolated proof of
(0,0) branch, no Start two-way toggle, no real game/license.
"""
from __future__ import annotations
import json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s146"
OUT.mkdir(parents=True,exist_ok=True)

def main():
    if os.name!="nt" or sys.maxsize<=2**32:
        print("S146_REQUIRES_NATIVE_WIN64")
        return 2
    import ctypes
    import tkinter as tk
    from layout_windows import NativeLayoutBackend
    from window_hide import C12HideAll
    from start_windows import GameWindow,GAME_PROCESS,GAME_TITLE,UNITY_WINDOW_CLASS
    from start_polling import WindowSnapshot

    root=None
    checks={}
    try:
        root=tk.Tk()
        root.title("S146 TEST OWNED WINDOW, NOT GAME")
        root.geometry("250x165+125+110")
        second=tk.Toplevel(root)
        second.title("S146 TEST ONLY SECOND")
        second.geometry("275x170+475+245")
        root.update_idletasks()
        root.update()
        u=ctypes.WinDLL("user32",use_last_error=True)
        ancestor=u.GetAncestor
        ancestor.argtypes=[ctypes.c_void_p,ctypes.c_uint]
        ancestor.restype=ctypes.c_void_p
        handles=tuple(int(ancestor(w.winfo_id(),2) or 0) for w in (root,second))
        win=NativeLayoutBackend()
        pid=os.getpid()
        old={h:win.window_rect(h) for h in handles}
        size=lambda r:(r[2]-r[0],r[3]-r[1])
        checks["true_two_owned_native_top_level_windows"]=(
            len(set(handles))==2 and all(
                win.is_window(h) and win.is_visible(h)
                and win.process_id(h)==pid
                and h in win.enumerate_top_level() for h in handles))
        class OnlyTestOwned:
            """All real native Win32 calls but isolated TEST local identity."""
            def enumerate_top_level(self):
                return tuple(h for h in win.enumerate_top_level() if h in handles)
            def is_window(self,h):
                return h in handles and win.is_window(h)
            def is_visible(self,h):
                return h in handles and win.is_visible(h)
            def process_id(self,h):
                return win.process_id(h) if h in handles else -1
            def process_executable(self,p):
                return GAME_PROCESS if p==pid else "UNRELATED_TEST_ONLY"
            def window_class(self,h):
                return UNITY_WINDOW_CLASS if h in handles else "UNRELATED"
            def title_with_timeout(self,h,ms):
                return GAME_TITLE if h in handles and ms==150 else "UNRELATED"
            def window_rect(self,h):
                return win.window_rect(h)
            def move_no_resize(self,h,x,y):
                return win.move_no_resize(h,x,y) if h in handles else False

        rows=tuple(GameWindow(h,pid,GAME_TITLE,UNITY_WINDOW_CLASS,GAME_PROCESS)
                   for h in handles)
        snap=WindowSnapshot(7,rows,True)
        handler=C12HideAll(OnlyTestOwned())
        hidden=handler.hide(snap,max_windows=2)
        off={h:win.window_rect(h) for h in handles}
        checks["actual_C12_hide_at_negative_2200_preserves_sizes"]=(
            hidden.code=="HIDDEN" and handler.hidden and
            all(off[h][:2]==(-2200,-2200)
                and size(off[h])==size(old[h]) for h in handles))
        # Unauthorized show MUST NOT change the two Win32 HWND coordinates.
        forbidden=handler.show_documented_origin(
            snap,max_windows=2,allowed=lambda:False)
        checks["no_authorization_no_native_show"]=(
            forbidden.code=="CANCELLED" and
            all(win.window_rect(h)==off[h] for h in handles))
        missing=handler.show_documented_origin(
            snap,max_windows=0,allowed=lambda:True)
        checks["unverified_limit_refuses_show"]=(
            missing.code=="NO_VERIFIED_WINDOW_LIMIT" and
            all(win.window_rect(h)==off[h] for h in handles))
        restored=handler.show_documented_origin(
            snap,max_windows=2,allowed=lambda:True)
        actual={h:win.window_rect(h) for h in handles}
        checks["real_Win64_SetWindowPos_shows_both_at_0_0"]=(
            restored.code=="DOCUMENTED_ORIGIN_ZERO_ZERO_VERIFIED_NOT_FULL_PARITY"
            and restored.moved==handles
            and all(actual[h][:2]==(0,0) for h in handles))
        checks["GetWindowRect_sizes_unchanged_after_show"]=all(
            size(actual[h])==size(old[h]) for h in handles)
        checks["still_IsWindowVisible_no_SW_HIDE"]=all(
            win.is_visible(h) for h in handles)
        checks["state_reset_only_after_actual_rect_readback"]=(
            not handler.hidden and not handler.partial
            and handler.saved_window_rects==())
        repeat=handler.show_documented_origin(
            snap,max_windows=2,allowed=lambda:True)
        checks["idempotent_no_false_second_show"]=(
            repeat.code=="NOT_HIDDEN"
            and all(win.window_rect(h)==actual[h] for h in handles))
        checks["original_doc_conflict_not_wired_as_UI_toggle"]=(
            not hasattr(handler,"show") and not hasattr(handler,"restore"))
        checks["default_original_game_win32_identity_rejects_test_Tk"]=(
            not all(
                win.process_executable(pid).lower()==GAME_PROCESS.lower()
                for _ in handles))
        root.destroy()
        root=None
        out={
            "status":"PASS_S146_REAL_WIN64_C12_DOCUMENTED_ZERO_ORIGIN_TEST_OWNED_NO_GAME"
                if all(checks.values()) else "FAIL_S146_NATIVE_DOCUMENTED_ZERO",
            "checks":checks,
            "actual_windows_moved_count":2,
            "original_full_show_branch_proven":False,
            "actual_game_windows_used":False,
            "signed_Info_authentication":False,
            "Proxy_developed":False
        }
    except Exception as exc:
        out={"status":"FAIL_S146_NATIVE_DOCUMENTED_ZERO",
             "error_type":type(exc).__name__,
             "details":str(exc)[:120],
             "checks":checks,"actual_game_windows_used":False}
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
    (OUT/"c12_documented_show_0_0.json").write_text(
        json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(out,ensure_ascii=False))
    return 0 if out["status"].startswith("PASS_S146_") else 1

if __name__=="__main__":
    raise SystemExit(main())
