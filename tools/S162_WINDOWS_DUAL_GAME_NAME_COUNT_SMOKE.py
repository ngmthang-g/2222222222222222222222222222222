"""S162 genuine Win64: one AND two space original game image names counted.

Create two TEST-OWNED copies of system cmd.exe with exactly the two source-
verified names, run bounded harmless ping commands, read actual Toolhelp32
Unicode process image names, and test S26 extra=1 capacity before/after
terminating only owned PIDs. Does NOT launch actual Thần Long or connect ADB.
"""
from __future__ import annotations
import json,os,sys,subprocess,tempfile,shutil,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
DEST=ROOT/"artifacts"/"s162"
DEST.mkdir(parents=True,exist_ok=True)
ONE="Thần Long Mobile.exe"
TWO="Thần Long  Mobile.exe"


def run():
    report={
        "task":"S162","status":"NOT_RUN",
        "original_process_names":[ONE,TWO],
        "real_native_windows":os.name=="nt",
        "real_game_executed":False,"test_owned_cmd_copies":True,
        "real_signed_Info":False,"real_emulator_provider":False,
        "real_game_launch":False,"product_exe_built":False,
        "original_count_API_exact_parity":"UNKNOWN_LOCAL_TOOLHELP32",
    }
    children=[]
    try:
        if os.name!="nt" or sys.maxsize<=2**32:
            raise OSError("WIN64_REQUIRED")
        from login_path import EXE_NAME,GameDirectoryResult
        from permission_guard import PermissionSnapshot
        from login_running_process_capacity import (
            NativeWindowsProcessImages,count_current_game_processes,
            check_native_open_game_capacity,RUNNING_GAME_PROCESS_IMAGE_NAMES,
        )
        reader=NativeWindowsProcessImages()
        checks={}
        original=reader.process_images()
        already={pid for pid,name in original
                 if name.casefold() in RUNNING_GAME_PROCESS_IMAGE_NAMES}
        checks["no_preexisting_both_image_variants"]=len(already)==0
        if already:
            report["status"]="REFUSED_PREEXISTING_NAMESAKE_IMAGE"
            raise OSError("PREEXISTING_GAME_OR_UNRELATED_PROCESS")
        assert EXE_NAME==TWO
        cmd=Path(os.environ.get("COMSPEC",r"C:\Windows\System32\cmd.exe"))
        if cmd.name.casefold()!="cmd.exe" or not cmd.is_file():
            raise OSError("ORIGINAL_WINDOWS_CMD_NOT_FOUND")
        with tempfile.TemporaryDirectory(prefix="S162-OWNED-PROCESSES-") as root:
            root=Path(root)
            dirs=[root/"single",root/"double"]
            for folder in dirs:
                folder.mkdir()
            for folder,name in zip(dirs,(ONE,TWO)):
                file=folder/name
                shutil.copy2(cmd,file)
                proc=subprocess.Popen(
                    [str(file),"/c","ping -n 120 127.0.0.1 >nul"],
                    stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                children.append(proc)
            own_pids={p.pid for p in children}
            deadline=time.monotonic()+8
            rows=()
            observed=None
            while time.monotonic()<deadline:
                rows=reader.process_images()
                observed=count_current_game_processes(reader)
                matching={(pid,name.casefold()) for pid,name in rows
                          if pid in own_pids}
                if (observed.running_exe==2 and
                    {(pid,name) for pid,name in matching}==
                    {(children[0].pid,ONE.casefold()),
                     (children[1].pid,TWO.casefold())} and
                    all(p.poll() is None for p in children)):
                    break
                time.sleep(.12)
            checks["two_real_owned_PIDs_with_different_unicode_image_names"]=(
                matching=={(children[0].pid,ONE.casefold()),
                           (children[1].pid,TWO.casefold())}
                and all(p.poll() is None for p in children))
            checks["actual_Win32_count_includes_both_original_variants"]=(
                observed is not None and observed.code=="PROCESS_SNAPSHOT_OK"
                and observed.running_exe==2)
            checks["each_variant_has_a_distinct_running_PID"]=(
                children[0].pid!=children[1].pid and
                own_pids=={pid for pid,name in rows
                           if name.casefold() in RUNNING_GAME_PROCESS_IMAGE_NAMES})
            test_claim=PermissionSnapshot(
                has_verified_payload=True,permissions=frozenset({"login_tab"}),
                plan_status="active",max_windows=2)
            # The canonical two-space F04 file remains the ONLY acceptable
            # launch preflight path. The one-space copy is COUNT ONLY.
            game=GameDirectoryResult(dirs[1],"")
            denied,n=check_native_open_game_capacity(
                test_claim,game,verified_emulator_sessions=0,backend=reader)
            checks["original_F05_extra_one_denies_when_both_running"]=(
                denied.reason=="ACCOUNT_LIMIT_EXTRA_ONE"
                and n.running_exe==2 and n.combined==2)
            checks["canonical_F04_exe_still_double_space_only"]=(
                game.executable is not None and
                game.executable.name==TWO and
                not (dirs[0]/TWO).exists())
            no_info,_=check_native_open_game_capacity(
                PermissionSnapshot(),game,verified_emulator_sessions=0,
                backend=reader)
            checks["missing_signed_Info_never_allows_unsafe_launch"]=(
                not no_info.allowed and no_info.reason=="UNVERIFIED_INFO")
            missing_emulator,_=check_native_open_game_capacity(
                test_claim,game,verified_emulator_sessions=None,backend=reader)
            checks["unknown_emulator_population_never_assumed_zero"]=(
                missing_emulator.reason=="RUNNING_WINDOW_COUNT_UNKNOWN")
            # Stop ONLY the owned one-space image, proving genuine real-time
            # PID lifetime reflects game count, then re-evaluate S26.
            one=children[0]
            one.terminate()
            one.wait(timeout=6)
            deadline=time.monotonic()+6
            after=None
            while time.monotonic()<deadline:
                after=count_current_game_processes(reader)
                if after.running_exe==1:
                    break
                time.sleep(.12)
            allowed,n2=check_native_open_game_capacity(
                test_claim,game,verified_emulator_sessions=0,backend=reader)
            checks["ending_single_space_owned_PID_reduces_real_count_to_one"]=(
                after is not None and after.running_exe==1
                and children[1].poll() is None)
            checks["original_extra_one_now_preflight_only_allows"]=(
                allowed.reason=="PREFLIGHT_ONLY_NOT_LAUNCHED"
                and n2.combined==1 and allowed.allowed)
            checks["no_original_game_DLL_Proxy_or_real_Info"]=all(
                not report[key] for key in (
                    "real_game_executed","real_signed_Info",
                    "real_emulator_provider","real_game_launch",
                    "product_exe_built"))
            # Win64 temporary directory deletion requires child shutdown.
            for proc in children:
                if proc.poll() is None:
                    proc.kill()
                    proc.wait(timeout=5)
        report["checks"]=checks
        report["status"]=(
            "PASS_NATIVE_S162_WIN64_BOTH_GAME_IMAGE_SPACING_PIDS_TEST_OWNED"
            if all(checks.values()) else "FAIL_NATIVE_S162_GAME_IMAGE_COUNT")
    except Exception as exc:
        if report["status"]=="NOT_RUN":
            report["status"]="FAIL_NATIVE_S162_GAME_IMAGE_COUNT"
        report["error_type"]=type(exc).__name__
        report["error_message"]=str(exc)[:180]
    finally:
        for proc in children:
            if proc.poll() is None:
                try:proc.kill();proc.wait(timeout=5)
                except Exception:pass
        (DEST/"win64_one_two_space_process_count.json").write_text(
            json.dumps(report,ensure_ascii=False,indent=2)+"\n",
            encoding="utf-8")
        print(json.dumps(report,ensure_ascii=True))
    return 0 if report["status"].startswith("PASS_") else 1

if __name__=="__main__":
    raise SystemExit(run())
