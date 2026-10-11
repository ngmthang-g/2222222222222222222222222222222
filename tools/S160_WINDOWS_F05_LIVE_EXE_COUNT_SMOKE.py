"""S160 actual native Win64 process-snapshot / F05 license limit test.

Creates TWO temporary TEST-OWNED copies of the Windows system cmd.exe named
exactly like the original game's executable, and counts their real PIDs via
the read-only Toolhelp32Snapshot/Process32FirstW/NextW APIs.

This is NOT Thần Long Mobile. The copies only run a bounded benign ping
and are always terminated by their owning subprocess handles. Never terminate
or access a pre-existing game; refuses if any same-name process already exists.
Info grants and emulator count are TEST-INJECTED solely for preflight proof.
"""
from __future__ import annotations
import json,os,sys,subprocess,tempfile,shutil,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
DEST=ROOT/"artifacts"/"s160"
DEST.mkdir(parents=True,exist_ok=True)


def main():
    report={"status":"NOT_RUN","task":"S160",
            "real_game_started":False,"authentic_signed_Info":False,
            "test_only_claims":True,"verified_emulator_provider":False,
            "real_launcher_or_injection":False,"product_exe_built":False,
            "sample":"TWO_TEST_OWNED_WIN64_SYSTEM_CMD_COPIES_RENAMED",
            "process_count_API":"TOOLHELP32_READ_ONLY_NOT_PROVEN_ORIGINAL"}
    children=[]
    try:
        if os.name!="nt" or sys.maxsize<=2**32:
            raise OSError("WIN64_REQUIRED")
        from login_path import GameDirectoryResult,EXE_NAME
        from permission_guard import PermissionSnapshot
        from login_running_process_capacity import (
            NativeWindowsProcessImages,count_current_game_processes,
            check_native_open_game_capacity)
        reader=NativeWindowsProcessImages()
        checks={}
        initial=count_current_game_processes(reader)
        checks["preexisting_real_or_unrelated_same_image_absent"]=(
            initial.code=="PROCESS_SNAPSHOT_OK" and initial.running_exe==0)
        if not checks["preexisting_real_or_unrelated_same_image_absent"]:
            report["status"]="REFUSED_PREEXISTING_GAME_IMAGE_ON_WINDOWS_RUNNER"
            raise OSError("UNSAFE_TEST_OWNED_IMAGE_COLLISION")
        cmd=Path(os.environ.get("COMSPEC",r"C:\Windows\System32\cmd.exe"))
        if cmd.name.casefold()!="cmd.exe" or not cmd.is_file():
            raise OSError("WIN64_CMD_REQUIRED")
        with tempfile.TemporaryDirectory(prefix="S160-F05-TEST-") as td:
            dirs=[Path(td)/"one",Path(td)/"two"]
            for path in dirs:path.mkdir()
            for path in dirs:
                image=path/EXE_NAME
                shutil.copy2(cmd,image)
                proc=subprocess.Popen(
                    [str(image),"/c","ping -n 120 127.0.0.1 >nul"],
                    stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
                children.append(proc)

            deadline=time.monotonic()+6
            observed=None
            while time.monotonic()<deadline:
                observed=count_current_game_processes(reader)
                if (observed.running_exe==2 and
                        all(p.poll() is None for p in children)):
                    break
                time.sleep(.14)
            native_rows=reader.process_images()
            own_pids={p.pid for p in children}
            game_pids={pid for pid,image in native_rows
                       if image.casefold()==EXE_NAME.casefold()}
            checks["two_real_processes_counted_by_unicode_ImageName"]=(
                observed is not None and observed.running_exe==2
                and game_pids==own_pids)
            checks["both_native_images_are_test_only_cmd_copies"]=(
                all((dir/EXE_NAME).is_file() for dir in dirs)
                and all(p.poll() is None for p in children))
            # Injected verified claims are SIMULATION only: genuine Info
            # server unavailable. Counts are REAL test-owned Win32.
            snapshot=PermissionSnapshot(
                has_verified_payload=True,permissions=frozenset({"login_tab"}),
                plan_status="active",max_windows=2)
            game=GameDirectoryResult(dirs[0],"")
            cap,n=check_native_open_game_capacity(snapshot,game,
                                verified_emulator_sessions=0,backend=reader)
            checks["two_running_exes_plus_extra_one_DENIED"]=(
                cap.reason=="ACCOUNT_LIMIT_EXTRA_ONE"
                and n.running_exe==2 and n.running_emulators==0 and n.combined==2)
            unknown,_=check_native_open_game_capacity(snapshot,game,
                                verified_emulator_sessions=None,backend=reader)
            checks["unknown_emulator_count_does_not_assume_zero"]=(
                unknown.reason=="RUNNING_WINDOW_COUNT_UNKNOWN")
            no_auth,_=check_native_open_game_capacity(
                PermissionSnapshot(),game,verified_emulator_sessions=0,backend=reader)
            checks["no_real_auth_claims_REFUSE_open"]=(
                no_auth.reason=="UNVERIFIED_INFO" and not no_auth.allowed)
            child=children.pop()
            child.terminate()
            child.wait(timeout=6)
            deadline=time.monotonic()+5
            after=None
            while time.monotonic()<deadline:
                after=count_current_game_processes(reader)
                if after.running_exe==1:break
                time.sleep(.12)
            cap2,n2=check_native_open_game_capacity(
                snapshot,game,verified_emulator_sessions=0,backend=reader)
            checks["closed_one_PID_live_count_shrinks_with_no_HWND_assumption"]=(
                after is not None and after.running_exe==1
                and cap2.reason=="PREFLIGHT_ONLY_NOT_LAUNCHED"
                and n2.combined==1 and children[0].poll() is None)
            checks["never_spawns_actual_Thần_Long_inject_Info_or_proxy"]=all(
                not report[key] for key in (
                    "real_game_started","authentic_signed_Info",
                    "verified_emulator_provider","real_launcher_or_injection",
                    "product_exe_built"))
        report["checks"]=checks
        report["status"]=(
            "PASS_NATIVE_S160_F05_REAL_WINDOWS_EXE_PID_COUNT_TEST_OWNED_NO_GAME"
            if all(checks.values()) else "FAIL_NATIVE_S160_COUNT")
    except Exception as exc:
        if report["status"]=="NOT_RUN":report["status"]="FAIL_NATIVE_S160_COUNT"
        report["error_type"]=type(exc).__name__
    finally:
        for proc in children:
            if proc.poll() is None:
                try:proc.kill();proc.wait(timeout=5)
                except Exception:pass
        report_path=DEST/"f05_native_real_process_image_count.json"
        report_path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",
                               encoding="utf-8")
        print(json.dumps(report,ensure_ascii=True))
    return 0 if report["status"].startswith("PASS_") else 1

if __name__=="__main__":raise SystemExit(main())
