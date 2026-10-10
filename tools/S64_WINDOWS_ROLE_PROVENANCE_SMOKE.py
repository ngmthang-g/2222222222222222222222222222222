"""S64 native Windows HWND/PID RoleName source gate, TEST-OWNED ONLY.

RoleName strings in this script are synthetic fixtures, NOT from a game
memory Reader. Test proves real Win32 HWND/PID fencing and exact master-first
ordering only with <=1 follower. No guess of original C07 _sort_key.
"""
from __future__ import annotations
import json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s64"
OUT.mkdir(parents=True,exist_ok=True)

def run():
    result={"task":"S64","status":"NOT_RUN","real_game":"NOT_RUN",
            "role_names":"SYNTHETIC_TEST_FIXTURE_NOT_GAME",
            "original_sort_key":"UNKNOWN","product_exe":"NOT_PRODUCT",
            "proxy_runtime":"EXCLUDED"}
    root=None
    try:
        if os.name!="nt":raise RuntimeError("S64_WINDOWS_REQUIRED")
        import ctypes,tkinter as tk
        from start_polling import WindowSnapshot
        from start_windows import GameWindow,GAME_PROCESS,GAME_TITLE,UNITY_WINDOW_CLASS
        from auto_role_provenance import C07RolePreflight,RoleReading
        from layout_windows import NativeLayoutBackend
        root=tk.Tk()
        root.title("S64 TEST ROOT")
        root.geometry("350x220+200+120")
        tops=[]
        for i in range(3):
            w=tk.Toplevel(root)
            w.title("S64 TEST HWND "+str(i))
            w.geometry(f"330x210+{220+300*i}+370")
            tops.append(w)
        root.update_idletasks();root.update()
        win32=ctypes.WinDLL("user32",use_last_error=True)
        ga=win32.GetAncestor
        ga.argtypes=[ctypes.c_void_p,ctypes.c_uint]
        ga.restype=ctypes.c_void_p
        handles=tuple(int(ga(w.winfo_id(),2)) for w in tops)
        backend=NativeLayoutBackend()
        pid=os.getpid()
        result["three_real_test_owned_python_hwnds"]=(
            len(set(handles))==3 and
            backend.process_executable(pid).lower().endswith(
                ("python.exe","pythonw.exe","python3.exe"))
            and all(backend.is_window(h) and backend.process_id(h)==pid for h in handles))
        before={h:backend.window_rect(h) for h in handles}

        class ReadOnlyOwned:
            def enumerate_top_level(self):
                return tuple(h for h in backend.enumerate_top_level() if h in handles)
            def is_window(self,h):
                return h in handles and backend.is_window(h)
            def is_visible(self,h):
                return h in handles and backend.is_visible(h)
            def process_id(self,h):
                return backend.process_id(h) if h in handles else 0
            def process_executable(self,p):
                return GAME_PROCESS if p==pid else ""
            def window_class(self,h):
                return UNITY_WINDOW_CLASS if h in handles else ""
            def title_with_timeout(self,h,ms):
                return GAME_TITLE if h in handles else ""
        rows=tuple(GameWindow(h,pid,GAME_TITLE,UNITY_WINDOW_CLASS,GAME_PROCESS)
                   for h in handles)
        fake_names=("Tên thử A","Tên thử B","Tên thử C")
        names=dict(zip(handles,fake_names))
        reader=lambda h,p:RoleReading(h,p,names[h])
        preflight=C07RolePreflight(ReadOnlyOwned())
        out3=preflight.prepare(WindowSnapshot(64,rows,True),max_windows=3,
                               master_hwnd=handles[2],read_role=reader)
        result["three_followers_rejected_without_original_comparator"]=(
            out3.code=="ORIGINAL_SORT_KEY_UNKNOWN" and
            len(out3.verified)==3 and out3.ordered==())
        out2=preflight.prepare(WindowSnapshot(65,rows[:2],True),max_windows=3,
                               master_hwnd=handles[1],read_role=reader)
        result["real_hwnd_pid_gate_master_first_two"]=(
            out2.code=="MASTER_FIRST_WITHOUT_SORT" and
            tuple(w.hwnd for w in out2.ordered)==(handles[1],handles[0]))
        absent=preflight.prepare(WindowSnapshot(66,rows,True),max_windows=3,
                                 master_hwnd=handles[1],read_role=None)
        result["no_game_role_reader_does_not_invent_names"]=(
            absent.code=="ROLE_READER_UNAVAILABLE")
        out_bad=preflight.prepare(WindowSnapshot(67,rows[:2],True),max_windows=3,
                                  master_hwnd=handles[1],
                                  read_role=lambda h,p:RoleReading(h,p+1,"WRONG"))
        result["stale_pid_bound_role_rejected"]=out_bad.code=="ROLE_IDENTITY_MISMATCH"
        after={h:backend.window_rect(h) for h in handles}
        result["native_window_coordinates_unchanged"]=after==before
        root.destroy();root=None
        checks=("three_real_test_owned_python_hwnds",
                "three_followers_rejected_without_original_comparator",
                "real_hwnd_pid_gate_master_first_two",
                "no_game_role_reader_does_not_invent_names",
                "stale_pid_bound_role_rejected",
                "native_window_coordinates_unchanged")
        assert all(result[k] is True for k in checks),result
        result["status"]="PASS_NATIVE_S64_ROLE_PROVENANCE_TEST_ONLY"
    except Exception as exc:
        result["status"]="FAIL_NATIVE_S64"
        result["error_type"]=type(exc).__name__
        result["error_text"]=str(exc)[:240]
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        (OUT/"native_test_owned_roles.json").write_text(
            json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
        for k,v in result.items():
            print("S64_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if result["status"]=="PASS_NATIVE_S64_ROLE_PROVENANCE_TEST_ONLY" else 1
if __name__=="__main__":raise SystemExit(run())
