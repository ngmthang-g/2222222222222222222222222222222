"""S66 native Windows C06 horizontal/vertical move-only proof, TEST-OWNED HWNDs."""
from __future__ import annotations
import ctypes,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s66"
OUT.mkdir(parents=True,exist_ok=True)
def run():
    o={"task":"S66","status":"NOT_RUN","real_game":"NOT_RUN",
       "real_license":"NOT_CONNECTED","product_exe":"NOT_PRODUCT",
       "proxy_runtime":"EXCLUDED","real_game_commands":0}
    root=None
    try:
        if os.name!="nt":raise RuntimeError("S66_WINDOWS_REQUIRED")
        import tkinter as tk
        from layout_windows import NativeLayoutBackend
        from window_stacking import C10C11WindowStacker
        from start_polling import WindowSnapshot
        from start_windows import GameWindow,GAME_PROCESS,GAME_TITLE,UNITY_WINDOW_CLASS
        root=tk.Tk()
        root.title("S66 TEST ROOT")
        root.geometry("400x260+220+140")
        owned=[]
        for i in range(3):
            w=tk.Toplevel(root)
            w.title("S66 TEST OWNED "+str(i))
            w.geometry(f"220x160+{250+i*250}+400")
            owned.append(w)
        root.update_idletasks();root.update()
        get_ancestor=ctypes.WinDLL("user32",use_last_error=True).GetAncestor
        get_ancestor.argtypes=[ctypes.c_void_p,ctypes.c_uint]
        get_ancestor.restype=ctypes.c_void_p
        ids=tuple(int(get_ancestor(w.winfo_id(),2)) for w in owned)
        real=NativeLayoutBackend()
        pid=os.getpid()
        o["native_hwnd_test_python_owned"]=(
            len(set(ids))==3
            and real.process_executable(pid).lower().endswith(
                ("python.exe","pythonw.exe","python3.exe"))
            and all(real.is_window(h) and real.process_id(h)==pid for h in ids))
        before={h:real.window_rect(h) for h in ids}
        dimensions=lambda r:(r[2]-r[0],r[3]-r[1])
        class OwnedOnly:
            def enumerate_top_level(self):
                return tuple(h for h in real.enumerate_top_level() if h in ids)
            def is_window(self,h):
                return h in ids and real.is_window(h)
            def is_visible(self,h):
                return h in ids and real.is_visible(h)
            def process_id(self,h):
                return real.process_id(h) if h in ids else 0
            def process_executable(self,p):
                return GAME_PROCESS if p==pid else ""
            def window_class(self,h):
                return UNITY_WINDOW_CLASS if h in ids else ""
            def title_with_timeout(self,h,ms):
                return GAME_TITLE if h in ids else ""
            def window_rect(self,h):
                return real.window_rect(h)
            def move_no_resize(self,h,x,y):
                return h in ids and real.move_no_resize(h,x,y)
        svc=C10C11WindowStacker(OwnedOnly())
        rows=tuple(GameWindow(h,pid,GAME_TITLE,UNITY_WINDOW_CLASS,GAME_PROCESS) for h in ids)
        snap=WindowSnapshot(66,rows,True)
        no=svc.apply(snap,mode="horizontal",max_windows=0)
        o["no_verified_limit_denies_all"]=(
            no.code=="NO_VERIFIED_WINDOW_LIMIT"
            and all(real.window_rect(h)==before[h] for h in ids))
        horizontal=svc.apply(snap,mode="horizontal",max_windows=3,master_hwnd=ids[2])
        after_h={h:real.window_rect(h) for h in ids}
        o["horizontal_master_first_50px_x"]=(
            horizontal.code=="STACK_HORIZONTAL_APPLIED" and
            all(after_h[h][:2]==target for h,target in
                ((ids[2],(0,0)),(ids[0],(50,0)),(ids[1],(100,0)))))
        vertical=svc.apply(snap,mode="vertical",max_windows=3,master_hwnd=ids[1])
        after_v={h:real.window_rect(h) for h in ids}
        o["vertical_master_first_50px_y"]=(
            vertical.code=="STACK_VERTICAL_APPLIED" and
            all(after_v[h][:2]==target for h,target in
                ((ids[1],(0,0)),(ids[0],(0,50)),(ids[2],(0,100)))))
        o["real_hwnd_original_sizes_preserved"]=all(
            dimensions(before[h])==dimensions(after_h[h])==dimensions(after_v[h])
            for h in ids)
        o["same_original_hwnd_pid"]=all(real.is_window(h) and real.process_id(h)==pid for h in ids)
        repeated=svc.apply(snap,mode="vertical",max_windows=3,master_hwnd=ids[1])
        o["repeat_no_unneeded_move"]=(
            repeated.code=="STACK_VERTICAL_APPLIED"
            and repeated.moved==()
            and repeated.unchanged==(ids[1],ids[0],ids[2]))
        root.destroy();root=None
        keys=("native_hwnd_test_python_owned","no_verified_limit_denies_all",
              "horizontal_master_first_50px_x","vertical_master_first_50px_y",
              "real_hwnd_original_sizes_preserved","same_original_hwnd_pid",
              "repeat_no_unneeded_move")
        assert all(o[k] is True for k in keys),o
        o["status"]="PASS_NATIVE_S66_C06_HV_STACK_TEST_OWNED"
    except Exception as exc:
        o["status"]="FAIL_NATIVE_S66"
        o["error_type"]=type(exc).__name__
        o["error_text"]=str(exc)[:260]
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        (OUT/"native_horizontal_vertical_owned.json").write_text(
            json.dumps(o,ensure_ascii=False,indent=2),encoding="utf-8")
        for k,v in o.items():
            print("S66_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return int(o["status"]!="PASS_NATIVE_S66_C06_HV_STACK_TEST_OWNED")
if __name__=="__main__":raise SystemExit(run())
