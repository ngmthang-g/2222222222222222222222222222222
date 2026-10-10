"""S61: actual Windows Tk test-only native SetWindowPos C07 exact size+origin."""
from __future__ import annotations
import json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s61"
OUT.mkdir(parents=True,exist_ok=True)
def run():
    out={"task":"S61","status":"NOT_RUN","game":"NOT_RUN",
         "product_exe":"NOT_PRODUCT","proxy":"EXCLUDED"}
    root=None
    try:
        if os.name!="nt":raise RuntimeError("Windows required")
        import ctypes,tkinter as tk
        from window_auto_reset import NativeC07Backend,C07AutoReset
        from start_windows import GameWindow,GAME_PROCESS,GAME_TITLE,UNITY_WINDOW_CLASS
        from start_polling import WindowSnapshot
        root=tk.Tk()
        root.title("S61 TEST OWNED")
        root.geometry("320x210+180+190")
        second=tk.Toplevel(root)
        second.title("S61 SECOND TEST OWNED")
        second.geometry("340x220+520+270")
        root.update_idletasks();root.update()
        user32=ctypes.WinDLL("user32",use_last_error=True)
        ancestor=user32.GetAncestor
        ancestor.argtypes=[ctypes.c_void_p,ctypes.c_uint]
        ancestor.restype=ctypes.c_void_p
        handles=tuple(int(ancestor(w.winfo_id(),2)) for w in (root,second))
        native=NativeC07Backend()
        pid=os.getpid()
        out["real_native_process_is_python"]=native.process_executable(pid).lower().endswith(("python.exe","pythonw.exe","python3.exe"))
        out["two_distinct_owned_hwnds"]=len(set(handles))==2
        before={h:native.window_rect(h) for h in handles}
        class TestOnly:
            def enumerate_top_level(self):return tuple(h for h in native.enumerate_top_level() if h in handles)
            def is_window(self,h):return h in handles and native.is_window(h)
            def is_visible(self,h):return h in handles and native.is_visible(h)
            def process_id(self,h):return native.process_id(h) if h in handles else 0
            def process_executable(self,p):return GAME_PROCESS if p==pid else ""
            def window_class(self,h):return UNITY_WINDOW_CLASS if h in handles else ""
            def title_with_timeout(self,h,ms):return GAME_TITLE if h in handles else ""
            def window_rect(self,h):return native.window_rect(h)
            def resize_no_move(self,h,w,ht):return native.resize_no_move(h,w,ht) if h in handles else False
            def move_no_resize(self,h,x,y):return native.move_no_resize(h,x,y) if h in handles else False
        rows=tuple(GameWindow(h,pid,GAME_TITLE,UNITY_WINDOW_CLASS,GAME_PROCESS) for h in handles)
        svc=C07AutoReset(TestOnly())
        s=WindowSnapshot(17,rows,True)
        no=svc.apply(s,max_windows=0)
        out["no_limit_denied"]=no.code=="NO_VERIFIED_WINDOW_LIMIT" and all(native.window_rect(h)==before[h] for h in handles)
        result=svc.apply(s,max_windows=2,master_hwnd=handles[1])
        after={h:native.window_rect(h) for h in handles}
        out["native_reset_result_code"]=result.code
        out["native_reset_requested"]=result.requested
        out["native_reset_resized"]=[int(h) for h in result.resized]
        out["native_reset_moved"]=[int(h) for h in result.moved]
        out["native_reset_unchanged"]=[int(h) for h in result.unchanged]
        out["native_rectangles_before"]={str(h):list(rect) for h,rect in before.items()}
        out["native_rectangles_after"]={str(h):list(rect) for h,rect in after.items()}
        out["native_target_rectangles"]={str(h):[0,0,1366,768] for h in handles}
        out["real_setwindowpos_final_geometry"]=result.code=="AUTO_RESET_APPLIED" and all(after[h]==(0,0,1366,768) for h in handles)
        out["master_first_order"]=result.resized==(handles[1],handles[0])
        out["native_hwnd_pid_unchanged"]=all(native.is_window(h) and native.process_id(h)==pid for h in handles)
        again=svc.apply(s,max_windows=2)
        out["second_pass_no_mutation"]=again.code=="AUTO_RESET_APPLIED" and again.unchanged==handles and not again.moved and not again.resized
        root.destroy();root=None
        assert all(v is True for k,v in out.items() if k in (
            "real_native_process_is_python","two_distinct_owned_hwnds",
            "no_limit_denied","real_setwindowpos_final_geometry",
            "master_first_order","native_hwnd_pid_unchanged",
            "second_pass_no_mutation")),out
        out["status"]="PASS_NATIVE_S61_C07_TEST_OWNED_RESIZE_RESET"
    except Exception as exc:
        out["status"]="FAIL_NATIVE_S61"
        out["error_type"]=type(exc).__name__
        out["error_text"]=str(exc)[:250]
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        (OUT/"native_test_only_auto_reset.json").write_text(
            json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")
        for k,v in out.items():print("S61_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if out["status"]=="PASS_NATIVE_S61_C07_TEST_OWNED_RESIZE_RESET" else 1
if __name__=="__main__":raise SystemExit(run())
