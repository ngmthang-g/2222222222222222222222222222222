"""S157 Win64 REAL CHILD PROCESS smoke for F05 minimal Windows environment.

ONLY launches the already-installed TEST-OWNED Python executable twice with a
filtered environment. Never launches Thần Long, never injects, never touches
system Proxy or user credentials, never enables licensed TLM UI.

A Win64 Python child actually inherits the env built by src/login_safe_env.py.
It reports BOOLEAN security properties, not environment values or secrets.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
ART=ROOT/"artifacts"/"s157"
ART.mkdir(parents=True,exist_ok=True)


def run():
    report={
        "task":"S157","status":"NOT_RUN",
        "original_exe_sha256":"15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22",
        "original_exact_SAFE_ENV_KEYS":"UNKNOWN",
        "actual_child_windows_exe":"TEST_OWNED_INSTALLED_PYTHON_ONLY",
        "original_game_launched":False,
        "DLL_injected":False,
        "real_signed_Info":False,
        "Proxy_touched":False,
        "product_exe_built":False,
    }
    try:
        if os.name!="nt":raise OSError("WINDOWS_REQUIRED")
        from login_safe_env import make_safe_launch_env,WINDOWS_ESSENTIAL_CANDIDATES
        parent=dict(os.environ)
        # These are deliberately TEST-ONLY strings; values are never written
        # to logs, artifacts or git.
        parent["PYTHONPATH"]=r"Z:\S157_TEST_UNTRUSTED_PYTHON"
        parent["VIRTUAL_ENV"]=r"Z:\S157_TEST_UNTRUSTED_VENV"
        parent["CONDA_PREFIX"]=r"Z:\S157_TEST_UNTRUSTED_CONDA"
        parent["S157_TEST_PRIVATE_ENV"]="S157_NOT_FOR_CHILD"
        parent["TLM_PROXY_HOST"]="s157.test.invalid"
        parent["TLM_PROFILE"]="STALE_PARENT_PROFILE"
        # The actual child tests two separate profile values under different
        # launches without modifying the live parent process environment.
        child_python=(
            "import json,os;"
            "e=os.environ;"
            "names={k.upper() for k in e};"
            "print(json.dumps({"
            "'profile':e.get('TLM_PROFILE'),"
            "'has_systemroot':'SYSTEMROOT' in names,"
            "'has_path':'PATH' in names,"
            "'has_comspec':'COMSPEC' in names,"
            "'has_python_leak':any(k.startswith('PYTHON') for k in names),"
            "'has_virtualenv_leak':'VIRTUAL_ENV' in names,"
            "'has_conda_leak':any(k.startswith('CONDA') for k in names),"
            "'has_proxy_leak':any(k.startswith('TLM_PROXY') for k in names),"
            "'has_private_test_leak':'S157_TEST_PRIVATE_ENV' in names,"
            "'unexpected_keys':len(names-set("+repr(sorted(WINDOWS_ESSENTIAL_CANDIDATES))+")-{'TLM_PROFILE'}),"
            "'count':len(names)"
            "},ensure_ascii=True))"
        )
        checks={}
        outcomes=[]
        for profile in ("1","5"):
            child_env=make_safe_launch_env(profile,parent)
            completed=subprocess.run(
                [sys.executable,"-c",child_python],
                cwd=str(ROOT),env=child_env,
                shell=False,stdin=subprocess.DEVNULL,
                capture_output=True,text=True,errors="replace",
                timeout=12,check=False,
                creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0),
            )
            if completed.returncode!=0:
                raise OSError("TEST_OWNED_WINDOWS_CHILD_DID_NOT_RUN")
            data=json.loads(completed.stdout.strip())
            checks[f"actual_windows_child_profile_{profile}_correct"]=(data["profile"]==profile)
            checks[f"actual_windows_child_profile_{profile}_has_essentials"]=(
                data["has_systemroot"] and data["has_path"] and data["has_comspec"])
            checks[f"actual_windows_child_profile_{profile}_no_Python_venv_conda_proxy_secret"]=(
                not any((data["has_python_leak"],data["has_virtualenv_leak"],
                         data["has_conda_leak"],data["has_proxy_leak"],
                         data["has_private_test_leak"])))
            checks[f"actual_windows_child_profile_{profile}_exact_filtered_key_domain"]=(
                data["unexpected_keys"]==0)
            outcomes.append((profile,completed.returncode))
        checks["independent_two_child_launches_no_profile_collision"]=(
            outcomes==[("1",0),("5",0)])
        checks["parent_source_mapping_did_not_mutate"]=(
            parent["TLM_PROFILE"]=="STALE_PARENT_PROFILE"
            and parent["S157_TEST_PRIVATE_ENV"]=="S157_NOT_FOR_CHILD")
        checks["no_real_game_injection_proxy_or_Info"]=all(
            not report[x] for x in (
                "original_game_launched","DLL_injected","real_signed_Info",
                "Proxy_touched","product_exe_built"))
        report["checks"]=checks
        report["status"]=(
            "PASS_NATIVE_S157_F05_MINIMAL_ENV_REAL_TEST_OWNED_WIN64_CHILD_NO_GAME"
            if all(checks.values()) else "FAIL_NATIVE_S157_MINIMAL_ENV")
    except Exception as exc:
        report["status"]="FAIL_NATIVE_S157_MINIMAL_ENV"
        report["error_type"]=type(exc).__name__
    finally:
        (ART/"real_test_owned_windows_children_env.json").write_text(
            json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(json.dumps(report,ensure_ascii=True))
    return 0 if report["status"].startswith("PASS_") else 1


if __name__=="__main__":
    raise SystemExit(run())
