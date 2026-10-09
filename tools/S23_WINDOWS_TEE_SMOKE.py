"""S23 E06 real Windows subprocess stdout/stderr tee + mutex/diagnostics.

Only S23_TEST_ONLY_<UUID> Win32 mutex names and TemporaryDirectory logs.
Never launch real GUI or game. Each subprocess has its own sys.stdout.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import traceback
import uuid

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s23"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"native_tee_sessions.json"


def child(mode, folder, name):
    if not name.startswith("S23_TEST_ONLY_"):
        return 35
    from single_instance import SingleInstanceMutex
    from session_logger import SessionTee, central_log_path, SessionLogError
    from startup_diagnostics import StartupDiagnostics
    folder=Path(folder)
    path=central_log_path(folder)
    crash=folder/"crash_fault.log"
    if mode=="probe":
        with SingleInstanceMutex(name):
            print("S23_MUTEX_NEW_PROCESS_ACQUIRED",flush=True)
        return 0
    if mode=="normal":
        previous=(sys.stdout,sys.stderr)
        with SingleInstanceMutex(name):
            for session_id in (1,2):
                with SessionTee(path):
                    print(f"S23_SESSION_{session_id}_STDOUT",flush=True)
                    print(f"S23_SESSION_{session_id}_STDERR",
                          file=sys.stderr,flush=True)
                    if session_id==1:
                        def worker():
                            print("S23_WORKER_THREAD_STDOUT",flush=True)
                            print("S23_WORKER_THREAD_STDERR",
                                  file=sys.stderr,flush=True)
                        t=threading.Thread(target=worker)
                        t.start()
                        t.join(5)
                        assert not t.is_alive()
                assert (sys.stdout,sys.stderr)==previous
        log=path.read_text(encoding="utf-8")
        assert log.count("=== Start ")==2 and log.count("=== End ")==2
        for token in ("S23_SESSION_1_STDOUT","S23_SESSION_1_STDERR",
                      "S23_SESSION_2_STDOUT","S23_SESSION_2_STDERR",
                      "S23_WORKER_THREAD_STDOUT","S23_WORKER_THREAD_STDERR"):
            assert token in log
        print("S23_TWO_SESSIONS_RESTORED",flush=True)
        return 0
    if mode=="bootfail":
        from unittest.mock import patch
        import types
        import TLMTool
        destroyed=[]
        class Root:
            def destroy(self):destroyed.append("root_destroy")
        class FailInfo:
            def __init__(self,*_):
                raise RuntimeError("S23_TEST_ONLY_INFO_CONSTRUCTOR_ERROR")
        mocktk=types.SimpleNamespace(Tk=Root,TclError=Exception)
        with patch.object(TLMTool,"SingleInstanceMutex",
                          side_effect=lambda:SingleInstanceMutex(name)), \
             patch.object(TLMTool,"SessionTee",
                          side_effect=lambda:SessionTee(path)), \
             patch.object(TLMTool,"StartupDiagnostics",
                          side_effect=lambda:StartupDiagnostics(crash)), \
             patch.object(TLMTool,"TLMMainApp",FailInfo), \
             patch.dict(sys.modules,{"tkinter":mocktk}):
            try:
                TLMTool.run_with_info_factory(lambda _:"TEST_ONLY_NOT_AUTH")
            except RuntimeError as exc:
                assert "S23_TEST_ONLY_INFO_CONSTRUCTOR_ERROR" in str(exc)
            else:
                raise AssertionError("BOOTSTRAP_MUST_FAIL")
        assert destroyed==["root_destroy"]
        content=path.read_text(encoding="utf-8")
        assert "=== Start " in content and "=== End " in content
        assert "S23 TEST BOOT FAILURE" not in content # never fabricated
        assert "S22 STARTUP_EXCEPTION" in crash.read_text(encoding="utf-8")
        assert TLMTool.main()==2
        print("S23_BOOT_FAILED_LOG_CLOSED_MUTEX_RELEASED",flush=True)
        return 0
    if mode=="badlog":
        path.mkdir(parents=True,exist_ok=True)
        with SingleInstanceMutex(name):
            try:
                with SessionTee(path):
                    raise AssertionError("GUI_CANNOT_START")
            except SessionLogError:
                pass
            else:
                raise AssertionError("BAD_LOG_MUST_DENY")
        print("S23_BAD_LOG_DENIED_TK_MUTEX_RELEASED",flush=True)
        return 0
    raise AssertionError("UNKNOWN_MODE")


def run():
    report={
        "task":"S23","status":"NOT_RUN",
        "original_log_relpath":"log/tlmtool.log",
        "original_MAX_SIZE_KEEP_SIZE":"UNKNOWN_NOT_GUESSED",
        "production_auth":"BLOCKED",
        "real_game":"NOT_RUN","production_exe":"NOT_BUILT",
        "production_mutex_ever_opened":False,"proxy":"NOT_DEVELOPED"
    }
    try:
        if os.name!="nt":raise RuntimeError("Windows only")
        from TLMTool import main
        assert main()==2
        with tempfile.TemporaryDirectory(prefix="s23_testonly_logs_") as td:
            base=Path(td)
            uuid_part=uuid.uuid4().hex
            for mode in ("normal","bootfail","badlog"):
                folder=base/mode
                folder.mkdir()
                name="S23_TEST_ONLY_"+mode+"_"+uuid_part
                command=[sys.executable,str(Path(__file__).resolve()),
                         mode,str(folder),name]
                result=subprocess.run(command,capture_output=True,text=True,timeout=20)
                report[mode+"_exit"]=result.returncode
                report[mode+"_console_stdout"]=result.stdout.strip()[-850:]
                report[mode+"_console_stderr"]=result.stderr.strip()[-650:]
                assert result.returncode==0,(
                    mode,result.stdout[-1300:],result.stderr[-2000:])
                if mode=="normal":
                    for token in ("S23_SESSION_1_STDOUT","S23_SESSION_1_STDERR",
                                  "S23_SESSION_2_STDOUT","S23_SESSION_2_STDERR"):
                        assert token in result.stdout+result.stderr
                    report["console_tee_verified"]=True
                    log=folder/"log"/"tlmtool.log"
                    report["two_appended_sessions"]=(
                        log.read_text(encoding="utf-8").count("=== Start ")==2
                        and log.read_text(encoding="utf-8").count("=== End ")==2)
                    assert report["two_appended_sessions"]
                    (OUT/"TEST_ONLY_normal_tlmtool.log").write_text(
                        log.read_text(encoding="utf-8"),encoding="utf-8")
                if mode=="bootfail":
                    log=folder/"log"/"tlmtool.log"
                    report["bootstrap_log_closed"]=(
                        "=== End " in log.read_text(encoding="utf-8"))
                    assert report["bootstrap_log_closed"]
                    report["separate_crash_file"]=(
                        "S22 STARTUP_EXCEPTION" in
                        (folder/"crash_fault.log").read_text(encoding="utf-8"))
                    assert report["separate_crash_file"]
                    (OUT/"TEST_ONLY_bootstrap_tlmtool.log").write_text(
                        log.read_text(encoding="utf-8"),encoding="utf-8")
                if mode=="badlog":
                    report["bad_log_fails_closed"]=True
                recheck=subprocess.run(
                    [sys.executable,str(Path(__file__).resolve()),
                     "probe",str(folder),name],
                    capture_output=True,text=True,timeout=10)
                report[mode+"_new_process_reacquires_mutex"]=(
                    recheck.returncode==0
                    and "S23_MUTEX_NEW_PROCESS_ACQUIRED" in recheck.stdout)
                assert report[mode+"_new_process_reacquires_mutex"]
        report["all_test_owned_log_paths_only"]=True
        report["status"]="PASS_NATIVE_S23_TWO_SESSION_STDOUT_STDERR_TEE_AND_FAILURE_CLEANUP"
    except Exception as exc:
        report["status"]="FAIL_NATIVE_S23_LOGGER"
        report["error"]=f"{type(exc).__name__}: {exc}"
        report["traceback"]=traceback.format_exc(limit=18)
    finally:
        REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),
                          encoding="utf-8")
        for k,v in report.items():
            if k!="traceback":
                print("S23_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if report["status"]==(
        "PASS_NATIVE_S23_TWO_SESSION_STDOUT_STDERR_TEE_AND_FAILURE_CLEANUP") else 1


if __name__=="__main__":
    if len(sys.argv)==4:
        raise SystemExit(child(*sys.argv[1:]))
    raise SystemExit(run())
