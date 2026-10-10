"""S91 native Windows/Tk Party G02 ready list, TEST-OWNED HWND/PID and RoleReading.

Actual ttk layout 3 per row, selected names leave the ready pool,
real Win32 HWND disappearance removes stale labels. Never runs the TLM
original EXE, sends game packets, reads game memory or fakes credentials.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUTPUT = ROOT/"artifacts"/"s91"
OUTPUT.mkdir(parents=True,exist_ok=True)
REPORT = OUTPUT/"native_party_ready_list.json"


def main():
    report={
        "task":"S91","status":"NOT_RUN",
        "windows":"ACTUAL_TEST_OWNED_WINDOWS_TK_HWND_PID",
        "RoleName":"INJECTED_TEST_ONLY_NOT_GAME_MEMORY",
        "Info":"NOT_AVAILABLE",
        "product":"NOT_BUILT_OR_RUN"
    }
    root=None
    panel=None
    temp=None
    try:
        if os.name!="nt":
            raise RuntimeError("NATIVE_WINDOWS_REQUIRED")
        import tkinter as tk
        from dwm_preview import NativeDwmBackend
        from auto_role_provenance import RoleReading
        from party_group_config import PartyConfigStore
        from party_ready_list import PartyReadyConfigEditor, READY_COLUMNS
        from start_windows import GameWindow
        from start_polling import WindowSnapshot

        native=NativeDwmBackend()
        root=tk.Tk()
        root.title("S91 TEST ONLY Party ready accounts")
        root.geometry("740x690+25+25")
        names=("Thiên Địa","Bạch Vân","Bình Minh","Hồng Hà","Phong Vân")
        windows=[]
        for idx,name in enumerate(names):
            top=tk.Toplevel(root)
            top.title("TEST WINDOW TITLE NOT "+name)
            top.geometry(f"180x135+{800+idx*22}+{45+idx*21}")
            tk.Label(top,text="TEST HWND - NOT GAME").pack()
            windows.append(top)
        root.update_idletasks()
        root.update()
        hwnds=tuple(int(native._ancestor(int(w.winfo_id()),2)) for w in windows)
        pid=os.getpid()
        assert len(set(hwnds))==5
        for hwnd in hwnds:
            assert native.source_matches(hwnd,pid)
        by_hwnd=dict(zip(hwnds,names))

        def make_window(h):
            return GameWindow(h,pid,"THIS TITLE IS NOT A CHARACTER NAME",
                              "TEST_TK","NOT_GAME.exe")
        class Producer:
            def __init__(self):
                self.snapshot=WindowSnapshot(1,tuple(make_window(h) for h in hwnds),True)
                self.reads=0
            def read_snapshot(self):
                self.reads+=1
                return self.snapshot
        start=Producer()
        def role_source(h,p):
            assert p==pid and h in by_hwnd and native.source_matches(h,p)
            return RoleReading(h,p,"<span>"+by_hwnd[h]+"</span>")

        temp=tempfile.TemporaryDirectory()
        path=Path(temp.name)/"settings.ini"
        panel=PartyReadyConfigEditor(
            root,store=PartyConfigStore(path),
            start_producer=start,read_role=role_source)
        panel.pack(fill="both",expand=True)
        root.update_idletasks()
        root.update()

        # With a real reader not yet called, an HWND title is NOT a ready name.
        assert panel.ready_list.names==()
        assert READY_COLUMNS==3

        def until(predicate,timeout=9.0):
            deadline=time.monotonic()+timeout
            while time.monotonic()<deadline:
                root.update()
                if predicate():
                    return True
                time.sleep(.016)
            return False
        assert until(lambda:panel.ready_list.names==names),(
            "First 3000ms Party refresh did not produce verified TEST names",
            panel.ready_list.names,panel._roster.code)
        def coords():
            return [(int(w.grid_info()["row"]),int(w.grid_info()["column"]))
                    for w in panel.ready_list.labels]
        assert coords()==[(0,0),(0,1),(0,2),(1,0),(1,1)],coords()
        report["native_tk_three_columns_five_accounts"]=True
        report["native_true_hwnd_pid_roster_from_start_cache"]=True
        report["title_not_used_as_rolename"]=True

        # Real ttk Combobox selection causes original G08 atomic disk save;
        # corresponding ready pool shrinks and re-packs without fake account.
        first=panel.group_inputs[0][0]
        first.set(names[0])
        first.event_generate("<<ComboboxSelected>>")
        root.update()
        assert panel.ready_list.names==names[1:],panel.ready_list.names
        assert coords()==[(0,0),(0,1),(0,2),(1,0)]

        panel.add_btn.invoke()
        root.update()
        second=panel.group_inputs[1][1]
        second.set(names[1])
        second.event_generate("<<ComboboxSelected>>")
        root.update()
        assert panel.ready_list.names==names[2:],panel.ready_list.names
        assert coords()==[(0,0),(0,1),(0,2)]
        assert panel.store.load().groups[1].members[1]==names[1]
        report["selected_groups_removed_from_ready_pool"]=True
        report["durable_unicode_group_selection"]=True

        # Real Win32 source destroyed; caller-owned S09 test cache publishes
        # removed HWND in next revision. Original Party never re-enumerates.
        doomed=windows[2]
        dead_handle=hwnds[2]
        doomed.destroy()
        root.update()
        assert not native._is_window(dead_handle)
        start.snapshot=WindowSnapshot(
            2,tuple(make_window(h) for h in hwnds if h!=dead_handle),True)
        assert until(lambda:names[2] not in panel.ready_list.names
                     and len(panel.ready_list.names)==2),panel.ready_list.names
        assert panel.ready_list.names==(names[3],names[4])
        assert coords()==[(0,0),(0,1)]
        report["closed_real_hwnd_purged_without_duplicate_win32_scan"]=True

        panel.shutdown()
        root.update()
        assert panel.ready_list.names==()
        assert not panel._roster_reader.active
        report["destroy_cleanup_releases_old_names"]=True
        report["status"]="PASS_NATIVE_S91_G02_PARTY_3_PER_ROW_READY_LIST"
    except Exception as exc:
        report["status"]="FAIL_NATIVE_S91"
        report["error_type"]=type(exc).__name__
        report["error_text"]=str(exc)[:500]
        report["traceback"]=traceback.format_exc(limit=18)
        print(report["traceback"])
    finally:
        if panel is not None:
            try:panel.shutdown()
            except Exception:pass
        if root is not None:
            try:root.destroy()
            except Exception:pass
        if temp is not None:
            temp.cleanup()
        REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
        for k,v in report.items():
            if k!="traceback":
                print("S91_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if report["status"]=="PASS_NATIVE_S91_G02_PARTY_3_PER_ROW_READY_LIST" else 1


if __name__=="__main__":
    raise SystemExit(main())
