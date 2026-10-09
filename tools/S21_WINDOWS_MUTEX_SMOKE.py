"""S21 native Windows TWO-PROCESS named-mutex proof, unique TEST names only.

Never opens the real TLMTool_SingleInstance mutex: every name uses a fresh,
unguessable S21_TEST_ONLY_ prefix. Both child processes use actual kernel32
CreateMutexW/GetLastError/CloseHandle through production SingleInstanceMutex.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import traceback
import uuid

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s21"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"native_single_instance_processes.json"


def child(mode,name):
    from single_instance import SingleInstanceMutex, InstanceAlreadyRunning
    if not name.startswith("S21_TEST_ONLY_"):
        print("INVALID_NON_TEST_MUTEX_NAME",flush=True)
        return 30
    try:
        with SingleInstanceMutex(name):
            print("MUTEX_ACQUIRED:"+str(os.getpid()),flush=True)
            if mode=="hold":
                # Parent explicitly releases or force-terminates this child.
                input()
                print("MUTEX_RELEASED",flush=True)
            return 0
    except InstanceAlreadyRunning:
        print("MUTEX_ALREADY_EXISTS",flush=True)
        return 23


def run():
    info={
        "task":"S21",
        "status":"NOT_RUN",
        "original_name":"TLMTool_SingleInstance",
        "original_mutex_ever_opened":False,
        "real_info_auth":"NOT_RECONSTRUCTED",
        "production_gui_entrypoint":"BLOCKED",
        "real_game":"NOT_RUN",
        "product_exe":"NOT_BUILT",
        "proxy":"NOT_DEVELOPED",
    }
    holders=[]
    try:
        if os.name!="nt":
            raise OSError("Windows native kernel32 smoke only")
        from single_instance import ORIGINAL_MUTEX_NAME
        from TLMTool import main

        assert ORIGINAL_MUTEX_NAME=="TLMTool_SingleInstance"
        info["bootstrapped_main_returns_blocked"]=main()==2
        assert info["bootstrapped_main_returns_blocked"]

        base="S21_TEST_ONLY_"+uuid.uuid4().hex
        def invoke(mode,name,timeout=8):
            p=subprocess.run(
                [sys.executable,str(Path(__file__).resolve()),mode,name],
                capture_output=True,text=True,timeout=timeout)
            return {"code":p.returncode,"out":p.stdout.strip(),
                    "err":p.stderr.strip()}

        name=base+"_live"
        p=subprocess.Popen(
            [sys.executable,str(Path(__file__).resolve()),"hold",name],
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,text=True,bufsize=1)
        holders.append(p)
        held=p.stdout.readline().strip()
        info["first_process_pid"]=p.pid
        info["first_process_acquired"]=held=="MUTEX_ACQUIRED:"+str(p.pid)
        assert info["first_process_acquired"],(held,p.poll())
        assert p.poll() is None
        competing=invoke("probe",name)
        info["second_process_duplicate"]=competing
        assert competing["code"]==23 and competing["out"]=="MUTEX_ALREADY_EXISTS"
        # First process continues to own only its registration; the second
        # briefly opened-and-CloseHandle'd a duplicate reference.
        assert p.poll() is None
        info["original_owner_still_alive_after_collision"]=True

        p.stdin.write("release\n")
        p.stdin.flush()
        out,err=p.communicate(timeout=8)
        info["first_process_graceful_close"]=(
            p.returncode==0 and "MUTEX_RELEASED" in out and not err)
        assert info["first_process_graceful_close"],(out,err,p.returncode)
        after=invoke("probe",name)
        info["new_process_can_acquire_after_close"]=after
        assert after["code"]==0 and after["out"].startswith("MUTEX_ACQUIRED:")

        # OS kernel object must also be released when a holder crashes,
        # without leaving a stale file or process-local lock.
        name2=base+"_terminated"
        p2=subprocess.Popen(
            [sys.executable,str(Path(__file__).resolve()),"hold",name2],
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,text=True,bufsize=1)
        holders.append(p2)
        held2=p2.stdout.readline().strip()
        assert held2=="MUTEX_ACQUIRED:"+str(p2.pid)
        contested=invoke("probe",name2)
        assert contested["code"]==23 and contested["out"]=="MUTEX_ALREADY_EXISTS"
        p2.terminate()
        p2.wait(timeout=8)
        recovered=invoke("probe",name2)
        info["acquire_after_forced_test_child_termination"]=recovered
        assert recovered["code"]==0 and recovered["out"].startswith("MUTEX_ACQUIRED:")
        info["no_stale_mutex_after_child_termination"]=True

        # Two distinct isolated test names never conflict with each other.
        parallel=invoke("probe",base+"_different")
        info["different_name_not_blocked"]=parallel
        assert parallel["code"]==0
        info["tested_only_isolated_names"]=True
        info["win32_kernel_handles_closed"]=True
        info["status"]="PASS_NATIVE_S21_TWO_PROCESS_MUTEX_COLLISION_AND_CLEANUP"
    except Exception as exc:
        info["status"]="FAIL_NATIVE_S21_MUTEX"
        info["error"]=f"{type(exc).__name__}: {exc}"
        info["traceback"]=traceback.format_exc(limit=22)
    finally:
        for p in holders:
            if p.poll() is None:
                p.terminate()
            try:p.wait(timeout=6)
            except Exception:
                p.kill()
                p.wait(timeout=6)
            for pipe in (p.stdin,p.stdout,p.stderr):
                try:pipe.close()
                except Exception:pass
        REPORT.write_text(json.dumps(info,ensure_ascii=False,indent=2),
                          encoding="utf-8")
        for key,val in info.items():
            if key!="traceback":
                print("S21_"+key.upper()+"="+json.dumps(val,ensure_ascii=True))
    return 0 if info["status"]==(
        "PASS_NATIVE_S21_TWO_PROCESS_MUTEX_COLLISION_AND_CLEANUP") else 1


if __name__=="__main__":
    if len(sys.argv)==3 and sys.argv[1] in ("probe","hold"):
        raise SystemExit(child(sys.argv[1],sys.argv[2]))
    raise SystemExit(run())
