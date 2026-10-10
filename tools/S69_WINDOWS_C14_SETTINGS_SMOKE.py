"""S69 true Windows E05 settings.ini C14 preference persistence, NO auto-open.

Operates only under a temporary APPDATA dir. Proves native Win32 HWND list
does not change when detached_auto_open=True is saved/loaded: this is a
persisted option ONLY, not a fabricated auto-open feature or game action.
"""
from __future__ import annotations
import ctypes,json,os,sys,tempfile,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s69"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"s69_settings_windows_no_autoopen.json"

def run():
    result={"task":"S69","status":"NOT_RUN","real_game":"NOT_RUN",
            "signed_info":"NOT_CONNECTED","product_exe":"NOT_PRODUCT",
            "detached_autoopen_runtime":"NOT_WIRED",
            "real_DWM_maintained_by":"S68_NATIVE_TEST",
            "proxy_runtime":"EXCLUDED"}
    old=os.environ.get("APPDATA")
    root=None
    try:
        if os.name!="nt":raise RuntimeError("WINDOWS_REQUIRED")
        import tkinter as tk
        from ctypes import wintypes
        from detached_settings import DetachedSettingsStore,DetachedSettings
        from grid_master import GridSettingsStore
        from settings_store import settings_path

        u32=ctypes.WinDLL("user32",use_last_error=True)
        cb_type=ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)
        enum=u32.EnumWindows
        enum.argtypes=[cb_type,wintypes.LPARAM]
        enum.restype=wintypes.BOOL
        get_pid=u32.GetWindowThreadProcessId
        get_pid.argtypes=[wintypes.HWND,ctypes.POINTER(wintypes.DWORD)]
        get_pid.restype=wintypes.DWORD
        is_window=u32.IsWindow
        is_window.argtypes=[wintypes.HWND]
        is_window.restype=wintypes.BOOL
        def owned_hwnds():
            found=[]
            @cb_type
            def collect(h,_):
                out=wintypes.DWORD(0)
                get_pid(h,ctypes.byref(out))
                if out.value==os.getpid():found.append(int(h))
                return True
            assert enum(collect,0)
            return set(found)

        root=tk.Tk()
        root.title("S69 test-only settings owner")
        root.geometry("360x220+280+220")
        root.update_idletasks();root.update()
        baseline=owned_hwnds()
        assert baseline
        result["native_test_owned_hwnds_before"]=sorted(baseline)

        with tempfile.TemporaryDirectory(prefix="s69_original_E05_") as appdata:
            os.environ["APPDATA"]=appdata
            path=Path(appdata)/"TLMTool"/"settings.ini"
            result["E05_real_APPDATA_path"]=str(settings_path())
            result["native_temp_APPDATA_scoped"]=settings_path()==path
            preferences=DetachedSettingsStore()
            grid=GridSettingsStore()
            result["exact_original_C14_defaults"]=(
                preferences.load()==DetachedSettings(True,"3"))
            preferences.save(False,"4")
            grid.save(5,6)
            preferences.save(True,"3")
            result["E05_c14_persistence_across_grid_writer"]=(
                preferences.load()==DetachedSettings(True,"3")
                and grid.load().cols==5 and grid.load().rows==6
                and path.exists())
            raw=path.read_text(encoding="utf-8")
            result["actual_settings_ini_exact_keys"]=all(k in raw for k in
                ("[Settings]","detached_auto_open = True",
                 "detached_grid = 3","grid_cols = 5","grid_rows = 6"))
            result["E05_dated_backup_created"]=(len(list(
                path.parent.glob("settings.????????.ini")))==1)
            root.update_idletasks();root.update()
            after=owned_hwnds()
            result["no_preview_or_extra_native_HWND_created_by_true_setting"]=(
                after==baseline)
            result["Tk_root_remains_real_native_window"]=all(
                is_window(h) for h in baseline)
            # Verify invalid data can't update real existing file bytes.
            before_bytes=path.read_bytes()
            try:preferences.save("yes","3")
            except ValueError:pass
            else:raise AssertionError("INVALID_AUTO_OPEN_WRITTEN")
            result["invalid_setting_did_not_touch_ini"]=path.read_bytes()==before_bytes

        checks=("native_temp_APPDATA_scoped","exact_original_C14_defaults",
                "E05_c14_persistence_across_grid_writer",
                "actual_settings_ini_exact_keys","E05_dated_backup_created",
                "no_preview_or_extra_native_HWND_created_by_true_setting",
                "Tk_root_remains_real_native_window",
                "invalid_setting_did_not_touch_ini")
        assert all(result[k] is True for k in checks),result
        result["status"]="PASS_NATIVE_S69_C14_SETTINGS_ONLY_NO_FAKE_AUTOOPEN"
    except Exception as exc:
        result["status"]="FAIL_NATIVE_S69"
        result["error_type"]=type(exc).__name__
        result["error_text"]=str(exc)[:250]
        result["traceback"]=traceback.format_exc(limit=12)
    finally:
        if old is None:os.environ.pop("APPDATA",None)
        else:os.environ["APPDATA"]=old
        if root is not None:
            try:root.destroy()
            except Exception:pass
        REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2),
                          encoding="utf-8")
        for k,v in result.items():
            if k!="traceback":print("S69_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if result["status"]=="PASS_NATIVE_S69_C14_SETTINGS_ONLY_NO_FAKE_AUTOOPEN" else 1
if __name__=="__main__":raise SystemExit(run())
