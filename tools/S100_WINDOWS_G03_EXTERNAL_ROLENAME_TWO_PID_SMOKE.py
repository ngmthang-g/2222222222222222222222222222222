"""S100 G03 RoleName EXTERNAL source on TWO REAL TEST-owned Win32 PIDs.

Native HWNDs are physically present in two distinct Python Tk processes.
All RoleName dictionaries are synthetic callback values, NOT original game
memory, original utils or signed Info. No clicks/packets/process writes.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import traceback

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s100"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"s100_native_party_rolename_two_pid.json"

CHILD_CODE=r"""
import ctypes,os,tkinter as tk
root=tk.Tk()
root.title("S100 TEST CHILD NOT GAME")
root.geometry("240x120+700+90")
root.update_idletasks()
root.update()
get_ancestor=ctypes.windll.user32.GetAncestor
get_ancestor.argtypes=[ctypes.c_void_p,ctypes.c_uint]
get_ancestor.restype=ctypes.c_void_p
hwnd=int(get_ancestor(int(root.winfo_id()),2))
print(str(hwnd)+","+str(os.getpid()),flush=True)
root.after(25000,root.destroy)
root.mainloop()
"""


def main():
    info={"task":"S100","status":"NOT_RUN",
          "native_windows":"TWO_DISTINCT_TEST_OWNED_PYTHON_PIDS",
          "rolename_source":"SYNTHETIC_EXTERNAL_TEST_CALLBACK_NOT_GAME",
          "signed_Info":"NOT_AVAILABLE","game_process":"NEVER_USED"}
    root=None
    child=None
    try:
        if os.name!="nt":
            raise RuntimeError("WINDOWS_REQUIRED")
        import ctypes
        import tkinter as tk
        from start_polling import WindowSnapshot
        from start_windows import NativeWin32Backend, GameWindow
        from party_rolename_source import PartyRoleNameExternalSource
        from party_roster import PartyRoster, prepare_roster

        root=tk.Tk()
        root.title("S100 TEST PARENT NOT GAME")
        root.geometry("260x125+125+95")
        root.update_idletasks()
        root.update()
        get_ancestor=ctypes.windll.user32.GetAncestor
        get_ancestor.argtypes=[ctypes.c_void_p,ctypes.c_uint]
        get_ancestor.restype=ctypes.c_void_p
        hwnd_a=int(get_ancestor(int(root.winfo_id()),2))
        pid_a=os.getpid()
        child=subprocess.Popen(
            [sys.executable,"-u","-c",CHILD_CODE],stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        lines=[]
        t=threading.Thread(target=lambda:lines.append(child.stdout.readline()),daemon=True)
        t.start()
        t.join(timeout=9)
        if t.is_alive() or not lines or "," not in lines[0]:
            raise RuntimeError("CHILD_TEST_NATIVE_HWND_TIMEOUT")
        hwnd_b,pid_b=map(int,lines[0].strip().split(","))
        backend=NativeWin32Backend()
        assert hwnd_a!=hwnd_b and pid_a!=pid_b
        assert backend.is_window(hwnd_a) and backend.process_id(hwnd_a)==pid_a
        assert backend.is_window(hwnd_b) and backend.process_id(hwnd_b)==pid_b
        info["two_real_native_hwnd_different_pids"]=True

        class Cache:
            def __init__(self):
                self.value=WindowSnapshot(1,(
                    GameWindow(hwnd_a,pid_a,"NOT ROLE NAME","TEST","python.exe"),
                    GameWindow(hwnd_b,pid_b,"NOT ROLE NAME","TEST","python.exe")),True)
            def read_snapshot(self):
                return self.value
        cache=Cache()
        role_data={hwnd_a:{"RoleName":"<b>S100 Đội</b> Trưởng"},
                   hwnd_b:{"RoleName":"Hòa✨"}}
        source=PartyRoleNameExternalSource(
            start_producer=cache,backend=backend,
            get_character_info=lambda hwnd:role_data[hwnd])
        report=prepare_roster(cache.read_snapshot(),source.read_role)
        assert report.code=="ROLE_NAMES_READ",report
        roster=PartyRoster()
        assert roster.apply(report,cache.read_snapshot())
        assert roster.ready_names()==("S100 Đội Trưởng","Hòa✨"),roster.ready_names()
        probe=source.inspect(hwnd_b,pid_b)
        assert probe.reading.role_name=="Hòa✨"
        assert probe.source_provenance=="EXTERNAL_UNVERIFIED_NOT_GAME"
        assert probe.action_authorized is False
        info["original_tag_regex_and_s90_roster_reuse"]=True

        absent=PartyRoleNameExternalSource(
            start_producer=cache,backend=backend,get_character_info=None)
        r=absent.inspect(hwnd_a,pid_a)
        assert r.code=="ORIGINAL_CHARACTER_READER_UNAVAILABLE"
        assert r.reading is None and r.fallback_prefix=="Window "
        assert r.fallback_suffix_known is False
        unverified=prepare_roster(cache.read_snapshot(),absent.read_role)
        assert all(x.role_name is None for x in unverified.members)
        info["no_fabricated_role_when_original_reader_missing"]=True

        # Start revision mutation DURING the external reader must fail closed.
        def stale_reader(hwnd):
            cache.value=WindowSnapshot(2,cache.value.windows,True)
            return role_data[hwnd]
        stale_source=PartyRoleNameExternalSource(
            start_producer=cache,backend=backend,
            get_character_info=stale_reader)
        stale=stale_source.inspect(hwnd_a,pid_a)
        assert stale.code=="STALE_START_REVISION_OR_GENERATION",stale
        assert stale.reading is None
        info["start_revision_race_blocks"]=True

        # Actual child death INVALIDATES physical PID/HWND, regardless of
        # synthetic role callback values and cached old Start snapshot.
        child.terminate()
        child.wait(timeout=8)
        deadline=time.monotonic()+4
        while backend.is_window(hwnd_b) and time.monotonic()<deadline:
            root.update()
            time.sleep(.015)
        assert not backend.is_window(hwnd_b)
        closed=source.inspect(hwnd_b,pid_b)
        assert closed.code=="STALE_OR_REUSED_NATIVE_HWND_PID",closed
        assert closed.reading is None
        info["actual_destroyed_pid_hwnd_blocks"]=True
        info["status"]="PASS_NATIVE_S100_G03_EXTERNAL_ROLENAME_TWO_WIN32_PIDS_NO_GAME"
    except Exception as exc:
        info["status"]="FAIL_NATIVE_S100"
        info["error"]=str(exc)[:400]
        info["traceback"]=traceback.format_exc(limit=12)
        print(info["traceback"])
    finally:
        if child is not None:
            try:
                if child.poll() is None:
                    child.terminate()
                child.wait(timeout=4)
            except Exception:
                try:child.kill()
                except Exception:pass
            try:
                if child.stdout:child.stdout.close()
                if child.stderr:child.stderr.close()
            except Exception:pass
        if root is not None:
            try:root.destroy()
            except Exception:pass
        REPORT.write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding="utf-8")
        for k,v in info.items():
            if k!="traceback":
                print("S100_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if info["status"]=="PASS_NATIVE_S100_G03_EXTERNAL_ROLENAME_TWO_WIN32_PIDS_NO_GAME" else 1


if __name__=="__main__":
    raise SystemExit(main())
