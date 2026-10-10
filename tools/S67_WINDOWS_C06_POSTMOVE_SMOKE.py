"""S67 real Win32 SetWindowPos/GetWindowRect readback and false-success guard.

Uses TEST-OWNED local Python Tk windows, never actual game/client accounts.
"""
from __future__ import annotations
import ctypes,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s67"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"s67_owned_native_after_move.json"

def run():
    evidence={"task":"S67","status":"NOT_RUN","actual_game":"NOT_RUN",
              "actual_license":"NOT_CONNECTED","product_exe":"NOT_PRODUCT",
              "proxy_runtime":"EXCLUDED"}
    root=None
    try:
        if os.name!="nt":raise RuntimeError("WINDOWS_REQUIRED")
        import tkinter as tk
        from layout_windows import NativeLayoutBackend
        from window_stacking import C10C11WindowStacker
        from start_polling import WindowSnapshot
        from start_windows import (
            GameWindow,GAME_PROCESS,GAME_TITLE,UNITY_WINDOW_CLASS)
        root=tk.Tk()
        root.title("S67 TEST ROOT")
        root.geometry("420x280+200+120")
        owned=[]
        for i in range(3):
            w=tk.Toplevel(root)
            w.title("S67 TEST OWNED HWND "+str(i))
            w.geometry(f"220x160+{260+i*230}+370")
            owned.append(w)
        root.update_idletasks()
        root.update()
        u32=ctypes.WinDLL("user32",use_last_error=True)
        ancestor=u32.GetAncestor
        ancestor.argtypes=[ctypes.c_void_p,ctypes.c_uint]
        ancestor.restype=ctypes.c_void_p
        ids=tuple(int(ancestor(w.winfo_id(),2)) for w in owned)
        native=NativeLayoutBackend()
        pid=os.getpid()
        evidence["actual_test_owned_hwnd_pid"]=(
            len(set(ids))==3
            and native.process_executable(pid).lower().endswith(
                ("python.exe","pythonw.exe","python3.exe"))
            and all(native.is_window(h) and native.process_id(h)==pid for h in ids))
        original={h:native.window_rect(h) for h in ids}
        size=lambda rect:(rect[2]-rect[0],rect[3]-rect[1])

        class LocalNative:
            def enumerate_top_level(self):
                return tuple(h for h in native.enumerate_top_level() if h in ids)
            def is_window(self,h):
                return h in ids and native.is_window(h)
            def is_visible(self,h):
                return h in ids and native.is_visible(h)
            def process_id(self,h):
                return native.process_id(h) if h in ids else 0
            def process_executable(self,p):
                return GAME_PROCESS if p==pid else ""
            def window_class(self,h):
                return UNITY_WINDOW_CLASS if h in ids else ""
            def title_with_timeout(self,h,ms):
                assert ms==150
                return GAME_TITLE if h in ids else ""
            def window_rect(self,h):
                return native.window_rect(h)
            def move_no_resize(self,h,x,y):
                return h in ids and native.move_no_resize(h,x,y)

        rows=tuple(GameWindow(h,pid,GAME_TITLE,UNITY_WINDOW_CLASS,GAME_PROCESS)
                   for h in ids)
        snap=WindowSnapshot(67,rows,True)
        owner=LocalNative()
        service=C10C11WindowStacker(owner)
        positions={
            "tight":((0,0),(0,0),(0,0)),
            "diagonal":((0,0),(50,50),(100,100)),
            "horizontal":((0,0),(50,0),(100,0)),
            "vertical":((0,0),(0,50),(0,100)),
        }
        observed={}
        for mode,locs in positions.items():
            outcome=service.apply(snap,mode=mode,max_windows=3,
                                  master_hwnd=ids[0])
            after={h:native.window_rect(h) for h in ids}
            observed[mode]=(outcome.code=="STACK_"+mode.upper()+"_APPLIED"
                and tuple(after[h][:2] for h in ids)==locs
                and all(size(after[h])==size(original[h]) for h in ids))
        evidence["four_real_win32_modes_verified"]=all(observed.values())
        evidence["verified_modes"]=observed

        # A malicious/buggy backend claims a successful last SetWindowPos
        # while making no native call; all other HWNDs use real Win32.
        class LieAboutLast(LocalNative):
            def move_no_resize(self,h,x,y):
                if h==ids[-1]:return True
                return super().move_no_resize(h,x,y)
        old_last=native.window_rect(ids[-1])
        failed=C10C11WindowStacker(LieAboutLast()).apply(
            snap,mode="diagonal",max_windows=3,master_hwnd=ids[0])
        evidence["last_false_native_success_detected"]=(
            failed.code=="MOVE_UNVERIFIED_PARTIAL"
            and ids[-1] in failed.moved
            and native.window_rect(ids[-1])==old_last
            and old_last[:2]!=(100,100))
        # Stale post-move PID simulated ONLY in the test adapter; production
        # still uses true kernel PID and refuses replacement.
        class LieAboutPidAfterMove(LocalNative):
            def __init__(self):
                self.changed=False
            def process_id(self,h):
                if self.changed and h==ids[1]:return pid+11
                return super().process_id(h)
            def move_no_resize(self,h,x,y):
                value=super().move_no_resize(h,x,y)
                if h==ids[1]:self.changed=True
                return value
        stale=C10C11WindowStacker(LieAboutPidAfterMove()).apply(
            snap,mode="horizontal",max_windows=3,master_hwnd=ids[0])
        evidence["post_move_pid_mismatch_detected"]=(
            stale.code=="STALE_AFTER_MOVE_PARTIAL"
            and stale.moved==(ids[1],))
        evidence["real_windows_remain_same_pid"]=all(
            native.is_window(h) and native.process_id(h)==pid for h in ids)
        root.destroy();root=None
        checks=("actual_test_owned_hwnd_pid",
                "four_real_win32_modes_verified",
                "last_false_native_success_detected",
                "post_move_pid_mismatch_detected",
                "real_windows_remain_same_pid")
        assert all(evidence[k] is True for k in checks),evidence
        evidence["status"]="PASS_NATIVE_S67_C06_POSTMOVE_REAL_RECT_AND_PID"
    except Exception as ex:
        evidence["status"]="FAIL_NATIVE_S67"
        evidence["error_type"]=type(ex).__name__
        evidence["error_text"]=str(ex)[:250]
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        REPORT.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),
                          encoding="utf-8")
        for k,v in evidence.items():
            print("S67_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if evidence["status"]=="PASS_NATIVE_S67_C06_POSTMOVE_REAL_RECT_AND_PID" else 1
if __name__=="__main__":raise SystemExit(run())
