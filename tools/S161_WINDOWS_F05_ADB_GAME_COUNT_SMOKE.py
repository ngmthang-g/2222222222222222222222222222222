"""S161 true Win64 subprocess CLI integration for original per-serial pidof.

Calls real Windows Python child processes that mimic ONLY the ADB output
protocol; they are NOT real Android devices or genuine adb.exe. A separate
test confirms AdbCommandRunner invokes the installed Windows Python.exe
as a real subprocess. No genuine Thần Long/LDPlayer/Info is exercised.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s161"
OUT.mkdir(parents=True,exist_ok=True)


def main() -> int:
    report={
        "task":"S161","status":"NOT_RUN","real_native_process_launch":True,
        "protocol_fixture":"TEST_OWNED_PYTHON_SUBPROCESS_ADB_OUTPUT_NOT_REAL_ADB",
        "real_adb_executable_tested":False,"real_emulator_tested":False,
        "game_client_launched":False,"signed_Info_authenticated":False,
        "proxy_controlled":False,"product_exe_built":False,
        "original_pidof_transport_microorder":"UNKNOWN",
    }
    try:
        if os.name!="nt":
            raise OSError("WINDOWS_REQUIRED")
        from login_emulator_game_capacity import (
            AdbCommandRunner,ORIGINAL_ANDROID_GAME_PACKAGE,
            count_adb_emulator_games,check_open_game_with_adb_process_count)
        from login_path import EXE_NAME, GameDirectoryResult
        from permission_guard import PermissionSnapshot

        checks={}
        # Real Windows executable/subprocess invocation, no ADB network or game.
        real_exe=AdbCommandRunner(sys.executable)
        exitcode,out,err=real_exe(("--version",))
        checks["actual_windows_executable_invoked_without_shell"]=(
            exitcode==0 and "Python" in (out+err))

        with tempfile.TemporaryDirectory(prefix="S161-ADB-PIDOF-TEST-") as temp:
            root=Path(temp)
            state=root/"game_serials.json"
            log=root/"command_log.jsonl"
            script=root/"stub_adb_protocol.py"
            script.write_text(
                """import json,sys
from pathlib import Path
state=Path(sys.argv[1]);log=Path(sys.argv[2]);a=sys.argv[3:]
with log.open('a',encoding='utf-8') as f:
 f.write(json.dumps(a,ensure_ascii=True)+'\\n')
values=json.loads(state.read_text(encoding='utf-8'))
if a==['devices','-l']:
 print('List of devices attached')
 for k in ('emulator-5554','emulator-5556'):
  print(k+'\\tdevice product:TEST ONLY')
 sys.exit(0)
if (len(a)==5 and a[:1]==['-s'] and a[2:4]==['shell','pidof']
    and a[4]=='com.fgstudio.thanlongmobile'):
 value=values.get(a[1])
 if value is None:sys.exit(1)
 print(value)
 sys.exit(0)
print('unknown test command',file=sys.stderr)
sys.exit(7)
""",encoding="utf-8")
            state.write_text(json.dumps({"emulator-5554":"301 302","emulator-5556":None}))
            calls=[]
            def run(args):
                # True Windows child Python process for EACH ADB command.
                # Deliberate fixture, not a real Android adb instance.
                cmd=[sys.executable,str(script),str(state),str(log),*args]
                completed=subprocess.run(cmd,shell=False,capture_output=True,
                    text=True,errors="replace",timeout=5,check=False,
                    creationflags=subprocess.CREATE_NO_WINDOW)
                calls.append(tuple(args))
                return completed.returncode,completed.stdout,completed.stderr

            got=count_adb_emulator_games(run)
            checks["native_4_subprocess_protocol_calls_for_2_serials"]=(
                got.code=="ADB_GAME_PIDOF_CONFIRMED" and len(calls)==4)
            checks["per_serial_two_game_PIDs_still_count_one_VM"]=(
                got.count==1 and got.game_serials==("emulator-5554",))
            checks["native_commands_include_exact_original_PIDOF_package"]=(
                calls[1]==("-s","emulator-5554","shell","pidof",
                           ORIGINAL_ANDROID_GAME_PACKAGE)
                and calls[2]==("-s","emulator-5556","shell","pidof",
                               ORIGINAL_ANDROID_GAME_PACKAGE))
            checks["devices_list_verified_before_and_after_pidof"]=(
                calls[0]==("devices","-l") and calls[-1]==("devices","-l"))
            state.write_text(json.dumps({"emulator-5554":"301 302","emulator-5556":"444"}))
            both=count_adb_emulator_games(run)
            checks["live_test_protocol_game_count_changes_one_to_two"]=(
                both.count==2 and len(both.game_serials)==2)
            class OwnNativeWindowsImages:
                def process_images(self):
                    return ((9876, EXE_NAME),)
            placeholder=root/EXE_NAME
            placeholder.write_bytes(b"S161_NOT_A_REAL_GAME")
            game=GameDirectoryResult(root,"")
            info=PermissionSnapshot(True,frozenset({"login_tab"}),"active",3)
            pre,measure=check_open_game_with_adb_process_count(
                info,game,adb_run=run,windows_backend=OwnNativeWindowsImages())
            checks["original_S26_combined_one_PC_two_EMU_plus_one_DENIED"]=(
                pre.reason=="ACCOUNT_LIMIT_EXTRA_ONE" and measure.count==2)
            before=len(calls)
            denied,reason=check_open_game_with_adb_process_count(
                PermissionSnapshot(),game,adb_run=run,
                windows_backend=OwnNativeWindowsImages())
            checks["no_Info_grant_never_invokes_any_ADB_process"]=(
                denied.reason=="UNVERIFIED_INFO" and reason.code=="INFO_OR_PLAN_DENIED"
                and len(calls)==before)
            records=[json.loads(x) for x in log.read_text("utf-8").splitlines()]
            checks["all_native_subprocess_invocations_are_readonly_query_shape"]=all(
                r==["devices","-l"] or
                (len(r)==5 and r[:1]==["-s"] and r[2:4]==["shell","pidof"]
                    and r[4]==ORIGINAL_ANDROID_GAME_PACKAGE) for r in records)
            checks["no_actual_Android_Info_game_product"]=all(
                report[x] is False for x in (
                    "real_adb_executable_tested","real_emulator_tested",
                    "game_client_launched","signed_Info_authenticated",
                    "proxy_controlled","product_exe_built"))
            report["checks"]=checks
            report["status"]=(
                "PASS_NATIVE_S161_F05_REAL_WINDOWS_CLI_EMU_PIDOF_TEST_ONLY_NOT_ANDROID"
                if all(checks.values()) else "FAIL_NATIVE_S161_ADB_PROTOCOL")
    except Exception as exc:
        report["status"]="FAIL_NATIVE_S161_ADB_PROTOCOL"
        report["error_type"]=type(exc).__name__
        report["error_detail"]=str(exc)[:180]
    finally:
        (OUT/"native_win64_adb_pidof_protocol_subprocess.json").write_text(
            json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        print(json.dumps(report,ensure_ascii=True))
    return 0 if report["status"].startswith("PASS_") else 1


if __name__=="__main__":
    raise SystemExit(main())
