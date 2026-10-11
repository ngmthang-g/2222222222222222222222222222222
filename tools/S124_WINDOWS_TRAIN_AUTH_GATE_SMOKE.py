"""S124 Windows native HWND/PID + Info snapshot gating of real Tk Train combos.

The HWND belongs to this CI's own Tk window, NOT a running game.
The token verifier below is a TEST STUB: no real signed Info or server grant.
"""
from __future__ import annotations
import os,sys,json,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s124";OUT.mkdir(parents=True,exist_ok=True)

def run():
    checks={"status":"NOT_RUN","is_real_game":False,"signed_info_verified":False,"proxy":"EXCLUDED"}
    root=None
    try:
        if os.name!="nt":raise RuntimeError("WINDOWS_REQUIRED")
        import tkinter as tk
        from permission_guard import PermissionGuard,VerifiedClaims
        from farm_saved_editor import FarmSavedCoordinatesEditor
        from train_saved_coordinates import FarmCoordinate,FarmCoordinatesStore
        from train_account_rows import TkTrainAccountRows
        from start_polling import WindowSnapshot
        from start_windows import NativeWin32Backend,GameWindow
        with tempfile.TemporaryDirectory(prefix="S124_INFO_H12_TK_") as td:
            ini=Path(td)/"settings.ini"
            ini.write_bytes(b"[Settings]\r\naccounts = unchanged\r\n[Farm]\r\nkeep = yes\r\n")
            store=FarmCoordinatesStore(ini)
            store.save([FarmCoordinate("A",26,"11","22")])
            root=tk.Tk();root.geometry("740x420+0+0")
            editor=FarmSavedCoordinatesEditor(root,store=store);editor.pack()
            root.update()
            backend=NativeWin32Backend()
            hwnd=root.winfo_id();pid=backend.process_id(hwnd)
            fixture=GameWindow(hwnd,pid,"Tk test fixture","TkTopLevel","NOT_GAME.exe")
            checks["native_win32_identity_real"]=(
                backend.is_window(hwnd) and backend.is_visible(hwnd)
                and pid==os.getpid())
            info=PermissionGuard()
            running=[1]
            denied=TkTrainAccountRows(root,editor,allow_account=lambda _:True)
            denied.apply_snapshot(WindowSnapshot(revision=1,windows=(fixture,),valid=True))
            checks["caller_true_without_info_never_grants"]=(
                denied._rows[hwnd]["sell"].instate(["disabled"])
                and editor.row_widgets[0]["apply_sell"].instate(["disabled"]))
            denied.shutdown();denied.container.destroy()
            owner=TkTrainAccountRows(
                root,editor,allow_account=lambda _:True,
                permission_guard=info,running_count=lambda:running[0])
            owner.apply_snapshot(WindowSnapshot(revision=1,windows=(fixture,),valid=True))
            checks["no_signed_token_keeps_all_disabled"]=(
                owner._rows[hwnd]["sell"].instate(["disabled"])
                and editor.row_widgets[0]["apply_train"].instate(["disabled"]))
            # STUB is used only to exercise runtime guards in isolated Windows CI.
            accepted=info.receive_token("TEST_ONLY_NOT_SIGNED", lambda _:
                VerifiedClaims(frozenset({"farm_tab"}),"active",2))
            owner.reapply_permissions()
            checks["test_fixture_can_exercise_all_3_guards"]=(
                accepted and not owner._rows[hwnd]["sell"].instate(["disabled"])
                and not editor.row_widgets[0]["apply_sell"].instate(["disabled"]))
            running[0]=3
            owner.reapply_permissions()
            checks["running_limit_reapplied_revoke"]=(
                owner._rows[hwnd]["farm"].instate(["disabled"])
                and editor.row_widgets[0]["apply_sell"].instate(["disabled"]))
            running[0]=1
            owner.reapply_permissions()
            checks["running_limit_recovery_requires_same_identity"]=(
                not owner._rows[hwnd]["farm"].instate(["disabled"]))
            # Cached HWND but a different PID must never grant editing.
            fake_reuse=GameWindow(hwnd,pid+1,"reused-number fixture","TkTopLevel","NOT_GAME.exe")
            owner.apply_snapshot(WindowSnapshot(revision=2,windows=(fake_reuse,),valid=True))
            checks["recycled_hwnd_wrong_real_pid_fails_closed"]=(
                owner._rows[hwnd]["sell"].instate(["disabled"])
                and editor.row_widgets[0]["apply_train"].instate(["disabled"]))
            owner.apply_snapshot(WindowSnapshot(revision=3,windows=(fixture,),valid=True))
            owner.reapply_permissions()
            checks["real_pid_restored_requires_new_bound_row"]=(
                not owner._rows[hwnd]["sell"].instate(["disabled"]))
            info.clear()
            owner.reapply_permissions()
            checks["info_heartbeat_revoke_without_window_revision"]=(
                owner._rows[hwnd]["sell"].instate(["disabled"])
                and editor.row_widgets[0]["apply_sell"].instate(["disabled"]))
            checks["revoked_apply_button_cannot_change_account_value"]=True
            sel=owner._rows[hwnd]["sell"]
            sel.set("SENTINEL")
            editor.row_widgets[0]["apply_sell"].invoke()
            checks["revoked_apply_button_cannot_change_account_value"]=sel.get()=="SENTINEL"
            owner.shutdown();owner.container.destroy()
            checks["shutdown_unbinds_all_account_combos"]=editor.account_bindings.active_count()==0
            editor.destroy();root.destroy();root=None
            checks["unrelated_settings_byte_preservation"]=(
                b"accounts = unchanged\r\n" in ini.read_bytes()
                and b"keep = yes\r\n" in ini.read_bytes())
        if not all(v for k,v in checks.items() if type(v) is bool and k not in ("is_real_game","signed_info_verified")):
            raise RuntimeError("S124_WINDOWS_AUTH_IDENTITY_NEGATIVE_GATE_FAILED")
        checks["status"]="PASS_NATIVE_S124_REAL_WIN32_PID_INFO_GATES_TK_NO_GAME"
    except Exception as exc:
        checks["status"]="FAIL_NATIVE_S124"
        checks["error_type"]=type(exc).__name__
        checks["error_detail"]=str(exc)[:150]
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        (OUT/"windows_h12_permission_gate.json").write_text(
            json.dumps(checks,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        for k,v in checks.items():print("S124_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if checks["status"].startswith("PASS_NATIVE_S124_") else 1
if __name__=="__main__":raise SystemExit(run())
