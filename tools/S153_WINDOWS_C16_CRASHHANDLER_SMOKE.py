"""S153 C16 native Windows test-only original crash-handler taskkill.

Creates ONE temporary test-owned image named UnityCrashHandler64.exe by
copying cmd.exe, runs it in the isolated GitHub Windows runner, proves
the exact source-backed 'taskkill /f /t /im' stops that test process.
Refuses to run if ANY real preexisting process bears the same name.
This test does NOT start/close Thần Long and does NOT authorize product.
"""
from __future__ import annotations
import csv
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
REPORT=ROOT/"artifacts"/"s153"/"c16_real_taskkill_test_owned.json"


def tasklist_rows(image: str) -> list[list[str]]:
    result=subprocess.run(
        ["tasklist","/fi",f"IMAGENAME eq {image}","/fo","csv","/nh"],
        shell=False,capture_output=True,text=True,errors="replace",
        timeout=8,check=False,
        creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
    if result.returncode != 0:
        raise OSError("TEST_TASKLIST_FAILED")
    return [row for row in csv.reader(io.StringIO(result.stdout))
            if row and row[0].casefold()==image.casefold()]


def main() -> int:
    report={"status":"NOT_RUN","task":"S153",
            "test_kind":"ISOLATED_TEMP_COPY_OF_WINDOWS_CMD_AS_CRASH_HANDLER",
            "real_game_used":False,"original_tool_exe_used":False,
            "signed_info_verified":False,"product_exe_built":False}
    child=None
    try:
        if os.name!="nt" or sys.maxsize<=2**32:
            raise OSError("WINDOWS_X64_REQUIRED")
        from close_windows import NativeCrashHandlerCleaner,CRASH_HANDLER_EXE
        before=tasklist_rows(CRASH_HANDLER_EXE)
        report["preexisting_same_name_processes_absent"]=(len(before)==0)
        if before:
            report["status"]="REFUSED_PREEXISTING_PROCESS_UNSAFE_TO_TERMINATE"
            raise OSError("REFUSE_TO_KILL_NON_TEST_PROCESS")
        with tempfile.TemporaryDirectory(prefix="S153-C16-TASKKILL-") as temp:
            # Copy standard Windows cmd; it remains a fully native signed
            # system executable but with a TEST-ONLY image name for taskkill.
            system_cmd=Path(os.environ.get("COMSPEC",r"C:\Windows\System32\cmd.exe"))
            if not system_cmd.is_file() or system_cmd.name.casefold()!="cmd.exe":
                raise OSError("SYSTEM_CMD_NOT_VERIFIED")
            copy=Path(temp)/CRASH_HANDLER_EXE
            shutil.copy2(system_cmd,copy)
            child=subprocess.Popen(
                [str(copy),"/c","ping -n 120 127.0.0.1 >nul"],
                stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL, shell=False,
                creationflags=subprocess.CREATE_NO_WINDOW)
            time.sleep(0.65)
            matches=tasklist_rows(CRASH_HANDLER_EXE)
            row_pids={int(row[1].replace(",","").strip('"')) for row in matches
                      if len(row)>1 and row[1].replace(",","").strip('"').isdigit()}
            report["exactly_one_test_owned_native_handler_running"]=(
                child.poll() is None and len(matches)==1 and child.pid in row_pids)
            if not report["exactly_one_test_owned_native_handler_running"]:
                raise OSError("TEST_PROCESS_IDENTITY_NOT_PROVEN")
            result=NativeCrashHandlerCleaner().run()
            try:child.wait(timeout=8)
            except subprocess.TimeoutExpired:pass
            report["real_exact_original_taskkill_returned_success"]=(
                result=="TASKKILL_SENT")
            report["owned_native_handler_terminated"]=child.poll() is not None
            report["post_taskkill_same_name_absent"]=(
                len(tasklist_rows(CRASH_HANDLER_EXE))==0)
            if (report["real_exact_original_taskkill_returned_success"]
                    and report["owned_native_handler_terminated"]
                    and report["post_taskkill_same_name_absent"]):
                report["status"]="PASS_NATIVE_S153_C16_ORIGINAL_TASKKILL_TEST_OWNED_NOT_GAME"
            else:
                report["status"]="FAIL_NATIVE_S153_TEST_OWNED_TASKKILL"
    except Exception as exc:
        if report["status"]=="NOT_RUN":
            report["status"]="FAIL_NATIVE_S153"
        report["error_type"]=type(exc).__name__
    finally:
        if child is not None and child.poll() is None:
            try:
                child.kill()  # ONLY our own known Popen PID
                child.wait(timeout=5)
            except Exception:pass
        REPORT.parent.mkdir(parents=True,exist_ok=True)
        REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(json.dumps(report,ensure_ascii=False))
    return 0 if report["status"].startswith("PASS_") else 1


if __name__=="__main__":
    raise SystemExit(main())
