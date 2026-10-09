"""S22 real Windows diagnostic + S21 mutex failure-path proof.

Run only TEST-OWNED child processes, TEST-OWNED uniquely named mutex and
temp crash_fault.log files. No actual game, license server or production
TLMTool_SingleInstance mutex is touched by this smoke.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import traceback
import uuid

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/"src"))
OUT=BASE/"artifacts"/"s22"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"native_startup_diagnostics.json"


def probe(name):
    from single_instance import SingleInstanceMutex
    if not name.startswith("S22_TEST_ONLY_"):
        return 31
    with SingleInstanceMutex(name):
        print("MUTEX_RECOVERED",flush=True)
    return 0


def child_thread_log(log,name):
    import faulthandler
    from single_instance import SingleInstanceMutex
    from startup_diagnostics import StartupDiagnostics
    if not name.startswith("S22_TEST_ONLY_"):
        return 32
    previous=threading.excepthook
    initial_fault=faulthandler.is_enabled()
    with SingleInstanceMutex(name):
        with StartupDiagnostics(log) as diag:
            assert diag.active
            assert threading.excepthook is not previous
            assert faulthandler.is_enabled()
            print("DIAGNOSTICS_ENABLED",flush=True)

            def deliberately_bad_test_thread():
                raise RuntimeError("S22_TEST_ONLY_THREAD_CRASH")

            t=threading.Thread(target=deliberately_bad_test_thread,
                               name="S22_TEST_ONLY_WORKER")
            t.start()
            t.join(timeout=5)
            assert not t.is_alive()
            # Genuine built-in CPython traceback writer while log is live.
            faulthandler.dump_traceback(file=diag._file,all_threads=True)
            diag._file.flush()
    assert threading.excepthook is previous
    if not initial_fault:
        assert not faulthandler.is_enabled()
    contents=Path(log).read_text(encoding="utf-8")
    assert "S22 THREAD_EXCEPTION" in contents
    assert "RuntimeError: S22_TEST_ONLY_THREAD_CRASH" in contents
    assert "Current thread" in contents
    print("THREAD_AND_FAULTHANDLER_WRITTEN",flush=True)
    return 0


def child_startup_failure(log,name):
    from unittest.mock import patch
    import types
    from single_instance import SingleInstanceMutex
    from startup_diagnostics import StartupDiagnostics
    import TLMTool

    if not name.startswith("S22_TEST_ONLY_"):
        return 33

    destroyed=[]
    class Root:
        def destroy(self): destroyed.append("root_destroy")
    class BrokenApp:
        def __init__(self,*args):
            raise RuntimeError("S22_TEST_ONLY_INFO_CONSTRUCTOR_FAILURE")
    stubtk=types.SimpleNamespace(Tk=Root,TclError=Exception)
    with patch.object(TLMTool,"SingleInstanceMutex",
                      side_effect=lambda:SingleInstanceMutex(name)), \
         patch.object(TLMTool,"StartupDiagnostics",
                      side_effect=lambda:StartupDiagnostics(log)), \
         patch.object(TLMTool,"TLMMainApp",BrokenApp), \
         patch.dict(sys.modules,{"tkinter":stubtk}):
        try:
            TLMTool.run_with_info_factory(lambda _:"TEST_ONLY_NOT_AUTH")
        except RuntimeError as exc:
            assert "S22_TEST_ONLY_INFO_CONSTRUCTOR_FAILURE" in str(exc)
        else:
            raise AssertionError("FAILED_STARTUP_MUST_RAISE")

    assert destroyed==["root_destroy"]
    contents=Path(log).read_text(encoding="utf-8")
    assert "S22 STARTUP_EXCEPTION" in contents
    assert "S22_TEST_ONLY_INFO_CONSTRUCTOR_FAILURE" in contents
    with SingleInstanceMutex(name):
        print("MUTEX_REACQUIRED_AFTER_FAILED_START",flush=True)
    assert TLMTool.main()==2
    return 0


def child_diagnostics_setup_error(bad_path,name):
    from single_instance import SingleInstanceMutex
    from startup_diagnostics import StartupDiagnostics,DiagnosticSetupError
    if not name.startswith("S22_TEST_ONLY_"):
        return 34
    Path(bad_path).mkdir(parents=True,exist_ok=True)
    try:
        with SingleInstanceMutex(name):
            # Deliberate failure: a directory cannot be opened as an
            # append-only text file. Must NOT enter Tk.
            with StartupDiagnostics(bad_path):
                raise AssertionError("SHOULD_NOT_START_GUI")
    except DiagnosticSetupError:
        pass
    else:
        raise AssertionError("DIAGNOSTIC_FAILURE_NOT_PROPAGATED")
    with SingleInstanceMutex(name):
        print("MUTEX_REACQUIRED_AFTER_DIAGNOSTIC_SETUP_FAILURE",flush=True)
    return 0


def run():
    result={
        "task":"S22","status":"NOT_RUN",
        "original_diagnostic_fingerprints":[
            "debug_logger.setup","faulthandler.enable",
            "crash_fault.log","threading.excepthook"],
        "original_format_directory_order":"UNKNOWN",
        "mutex_original_name_ever_opened":False,
        "all_test_mutex_names_isolated":True,
        "real_info_auth":"NOT_IMPLEMENTED",
        "production_main":"BLOCKED",
        "actual_game":"NOT_RUN",
        "exe":"NOT_BUILT","proxy":"NOT_DEVELOPED",
    }
    try:
        if os.name!="nt":
            raise RuntimeError("S22 actual native smoke requires Windows")
        from TLMTool import main
        assert main()==2
        token=uuid.uuid4().hex
        with tempfile.TemporaryDirectory(prefix="s22_native_test_") as temp:
            root=Path(temp)
            run_cases=[
                ("thread",root/"thread"/"crash_fault.log",
                 "S22_TEST_ONLY_THREAD_"+token),
                ("startup",root/"startup"/"crash_fault.log",
                 "S22_TEST_ONLY_STARTUP_"+token),
                ("badlog",root/"folder_as_log",
                 "S22_TEST_ONLY_NOLOG_"+token),
            ]
            for mode,path,name in run_cases:
                path.parent.mkdir(parents=True,exist_ok=True)
                args=[sys.executable,str(Path(__file__).resolve()),
                      mode,str(path),name]
                case=subprocess.run(
                    args, capture_output=True,text=True,timeout=20)
                result[mode+"_exit"]=case.returncode
                result[mode+"_stdout"]=case.stdout.strip()[-900:]
                result[mode+"_stderr_summary"]=(
                    "RuntimeError: S22_TEST_ONLY_THREAD_CRASH" in case.stderr
                    if mode=="thread" else case.stderr.strip()[-350:])
                assert case.returncode==0,(
                    mode,case.stdout,case.stderr[-2400:])

                # Independent OTHER PROCESS reclaims the same mutex name.
                probe_result=subprocess.run(
                    [sys.executable,str(Path(__file__).resolve()),
                     "probe",name],capture_output=True,text=True,timeout=10)
                result[mode+"_new_process_can_acquire"]=(
                    probe_result.returncode==0
                    and "MUTEX_RECOVERED" in probe_result.stdout)
                assert result[mode+"_new_process_can_acquire"]

                if mode in ("thread","startup"):
                    contents=path.read_text(encoding="utf-8")
                    assert len(contents)>0
                    assert "S22 " in contents
                    saved=OUT/("TEST_ONLY_"+mode+"_crash_fault.log")
                    shutil.copyfile(path,saved)
                    result[mode+"_log_written"]=True
                else:
                    result["diagnostic_setup_denied_gui"]=True
        result["native_thread_log_and_hook_restore"]=True
        result["native_startup_failure_mutex_recovered"]=True
        result["native_diagnostic_open_failure_mutex_recovered"]=True
        result["status"]="PASS_NATIVE_S22_DIAGNOSTICS_THREAD_FAULT_MUTEX_RECOVERY"
    except Exception as exc:
        result["status"]="FAIL_NATIVE_S22_STARTUP_DIAGNOSTICS"
        result["error"]=f"{type(exc).__name__}: {exc}"
        result["traceback"]=traceback.format_exc(limit=20)
    finally:
        REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2),
                          encoding="utf-8")
        for k,v in result.items():
            if k!="traceback":
                print("S22_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if result["status"]==(
        "PASS_NATIVE_S22_DIAGNOSTICS_THREAD_FAULT_MUTEX_RECOVERY") else 1


if __name__=="__main__":
    if len(sys.argv)==4:
        if sys.argv[1]=="probe":
            raise SystemExit(probe(sys.argv[2]))
        modes={"thread":child_thread_log,
               "startup":child_startup_failure,
               "badlog":child_diagnostics_setup_error}
        if sys.argv[1] in modes:
            raise SystemExit(modes[sys.argv[1]](sys.argv[2],sys.argv[3]))
    if len(sys.argv)==3 and sys.argv[1]=="probe":
        raise SystemExit(probe(sys.argv[2]))
    raise SystemExit(run())
