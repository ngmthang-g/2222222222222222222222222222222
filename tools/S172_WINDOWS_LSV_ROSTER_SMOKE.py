"""S172 true Win64 Tk LSV account roster native HWND/PID lifecycle smoke.

Strictly test-owned physical Tk HWND/PID; fake process/title CLASSIFICATION
is fixture-only in the producer adapter, NOT a discovered real game.
The production adapter is the existing native S09 Win32 worker, unchanged.
No RoleName, game process, memory reads or unauthorized original token.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s172"
OUT.mkdir(parents=True,exist_ok=True)


def main():
    proof={"status":"NOT_RUN","real_game":False,"original_license":False,
           "read_real_character_name":False,"gameplay_command":False,
           "test_only_game_process_name_fixture":True}
    root=None
    producer=None
    try:
        if os.name!="nt":
            raise RuntimeError("S172_REQUIRES_REAL_WIN64")
        import tkinter as tk
        from start_windows import GameWindow,NativeWin32Backend
        from start_polling import StartWindowProducer,WindowSnapshot
        from TLMToolIndependent import make_independent_builders
        from shell import TLMMainApp,INFO_KEY
        from train_lsv_top_tab import TkTrainLsvTopTab
        from train_lsv_passive_accounts import (
            TkTrainLsvPassiveAccounts,LSV_ACCOUNT_REFRESH_MS)
        from permission_guard import PermissionSnapshot

        with tempfile.TemporaryDirectory(prefix="S172_NATIVE_LSV_") as tmp:
            path=Path(tmp)/"settings.ini"
            raw=(b"[Login]\r\npassword = KEEP_SECRET\r\n"
                 b"[TrainLSV]\r\nrespawn = False\r\n"
                 b"coord_1 = TestLSV|10014|2|3\r\n"
                 b"buff_0 = True|1|0|5\r\n"
                 b"[Farm]\r\ncoord_1 = Farm|2|8|9\r\n"
                 b"[Party]\r\nmode = wait\r\n")
            path.write_bytes(raw)
            root=tk.Tk()
            root.geometry("1200x900+0+0")
            root.update()
            native=NativeWin32Backend()
            hwnd=int(root.winfo_id())
            pid=os.getpid()
            proof["actual_test_owned_tk_hwnd_pid"]=(
                hwnd>0 and native.is_window(hwnd) and native.process_id(hwnd)==pid)
            # SOURCE FIXTURE ONLY: real HWND/PID owned by this test Python
            # process. Never pretend Windows actually launched the game.
            class TestOwnedWindowBackend:
                def enumerate_top_level(self):return (hwnd,)
                def is_visible(self,h):return native.is_visible(h)
                def is_window(self,h):return native.is_window(h)
                def process_id(self,h):return native.process_id(h)
                def process_executable(self,p):return "thần long mobile.exe"
                def window_class(self,h):return "UnityWndClass"
                def title_with_timeout(self,h,t):return "Thần Long  Mobile"
            producer=StartWindowProducer(
                backend_factory=TestOwnedWindowBackend,
                interval_seconds=0.05,join_timeout=0.25)
            app=TLMMainApp(
                root,make_independent_builders(path,producer),
                independent_mode=True,local_window_count=lambda:0)
            app.position_window_top_right()
            root.update()
            proof["lsv_tab_shown_not_eager_with_zero_info"]=(
                "trainlsv_tab" in app.lifecycle.visible
                and "trainlsv_tab" not in app.lifecycle._instances
                and "proxy_tab" not in app.lifecycle.visible)
            app.notebook.select(app._tab_frames["trainlsv_tab"])
            root.update()
            tab=app.lifecycle._instances.get("trainlsv_tab")
            roster=tab.account_roster
            proof["real_lsv_tk_roster_shared_s09_owned_lifecycle"]=(
                isinstance(tab,TkTrainLsvTopTab)
                and isinstance(roster,TkTrainLsvPassiveAccounts)
                and roster.producer is producer
                and roster._active
                and producer.active
                and roster._owns_producer
                and LSV_ACCOUNT_REFRESH_MS==5000)
            # Worker asynchronous, no Tk calls from worker; poll boundedly.
            valid=False
            for _ in range(30):
                snapshot=producer.read_snapshot()
                if snapshot.valid:
                    valid=True
                    break
                time.sleep(0.03)
            if valid:
                # Test-only callback simulates subsequent I01 Tk tick, after
                # genuine background producer has populated the cache.
                roster.apply_snapshot(snapshot)
            root.update()
            proof["test_fixture_window_shows_only_hwnd_pid_no_fake_role"]=(
                valid and len(roster.rows)==1 and hwnd in roster.rows
                and roster.rows[hwnd]["pid"]==pid
                and f"HWND {hwnd} / PID {pid}" in roster.rows[hwnd]["label"].cget("text")
                and "Nhân vật: ?" in roster.rows[hwnd]["label"].cget("text"))
            # Fake recycled identity to prove Win32 rejects stale PID
            # regardless of the still cached synthetic game metadata.
            invalid=WindowSnapshot(
                revision=snapshot.revision+1,valid=True,
                windows=(GameWindow(hwnd,pid+1,"Thần Long  Mobile",
                                    "UnityWndClass","thần long mobile.exe"),))
            rejected=roster.apply_snapshot(invalid)
            proof["recycled_hwnd_wrong_pid_removed"]=(
                rejected and len(roster.rows)==0)
            roster.apply_snapshot(producer.read_snapshot())
            root.update()
            proof["same_physically_valid_hwnd_is_restored"]=(
                hwnd in roster.rows and roster.rows[hwnd]["pid"]==pid)
            app.apply_info_snapshot(PermissionSnapshot())
            app.apply_verified_permissions(set(),blocked=True)
            root.update()
            proof["old_original_license_revocation_does_not_hide_local_roster"]=(
                "trainlsv_tab" in app.lifecycle.visible
                and app.lifecycle.current=="trainlsv_tab"
                and roster._active)
            app.notebook.select(app._tab_frames[INFO_KEY])
            root.update()
            proof["deselect_stops_only_owned_worker_and_clears_rows"]=(
                app.lifecycle.current==INFO_KEY
                and not roster._active and not roster.rows
                and not producer.active and not roster._owns_producer)
            proof["unrelated_shared_settings_bytes_unchanged"]=(path.read_bytes()==raw)
            # External S09 worker lease must not be closed by LSV.
            external=producer.start()
            app.notebook.select(app._tab_frames["trainlsv_tab"])
            root.update()
            proof["external_worker_lease_is_not_owned"]=(
                external and producer.active and roster._active
                and not roster._owns_producer)
            app.notebook.select(app._tab_frames[INFO_KEY])
            root.update()
            proof["external_worker_survives_lsv_deselect"]=(
                producer.active and not roster._active)
            producer.stop()
            app.shutdown()
            root.destroy();root=None
        checks={k:v for k,v in proof.items() if type(v) is bool and k not in (
            "real_game","original_license","read_real_character_name",
            "gameplay_command","test_only_game_process_name_fixture")}
        if not all(checks.values()):
            raise RuntimeError("S172_NATIVE_FAILED:"+",".join(
                k for k,v in checks.items() if not v))
        proof["status"]="PASS_NATIVE_S172_LSV_SHARED_S09_TEST_OWNED_TK_HWND_ROSTER_NOT_GAME"
    except Exception as exc:
        proof["status"]="FAILED_S172"
        proof["error_type"]=type(exc).__name__
        proof["error_detail"]=str(exc)[:700]
    finally:
        if producer is not None:
            try:producer.stop()
            except Exception:pass
        if root is not None:
            try:root.destroy()
            except Exception:pass
        (OUT/"native_lsv_roster.json").write_text(
            json.dumps(proof,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        for k,v in proof.items():
            print("S172_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if proof["status"].startswith("PASS_NATIVE_") else 1


if __name__=="__main__":
    raise SystemExit(main())
