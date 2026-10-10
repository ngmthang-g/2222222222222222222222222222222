"""S109 genuine Windows Tk F01 plan-limited 100-row Login visibility.

Uses real S25/S37 Tk UI, synthetic credentials and a TEST-ONLY caller
authorizing a 1..100 presentation cap. No signed Info issuer is fabricated;
NO actual login, game process, proxy or disk account migration.
"""
from __future__ import annotations

import json,os,sys,tempfile,traceback,threading
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s109"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"s109_real_tk_login_limit.json"


def main():
    info=dict(task="S109",status="NOT_RUN",
        real_tk=True,real_game=False,real_info_issuer=False,
        external_cap="TEST_ONLY",credentials_real=False,
        actions_sent=0,accounts_file_modified=False)
    root=None
    try:
        if os.name!="nt":raise RuntimeError("S109 requires Windows Tk")
        import tkinter as tk
        from login_tab import TLMLoginPathTab
        from settings_store import read_settings

        with tempfile.TemporaryDirectory(prefix="s109_login_test_") as td:
            cfg=Path(td)/"TLMTool"/"settings.ini"
            cfg.parent.mkdir(parents=True,exist_ok=True)
            cfg.write_text(
                "[Settings]\naccounts = CHECK_UNKNOWN|test_user|test_secret|Có|test_proxy\n"
                "grid_rows = 4\n[Other]\nunchanged = yes\n",
                encoding="utf-8")
            original_bytes=cfg.read_bytes()
            original_accounts=read_settings(cfg).get("Settings","accounts")
            root=tk.Tk();root.title("S109 TEST ONLY NOT PRODUCT")
            root.geometry("650x1060+10+10")
            tab=TLMLoginPathTab(root,settings_file=cfg,
                                choose_directory=lambda **_: "",
                                show_error=lambda *_:None)
            root.update()
            rows=tab.account_rows
            assert len(rows.entry_user)==len(rows.entry_pass)==100
            rows.entry_user[1].insert(0,"synthetic_low")
            rows.entry_pass[1].insert(0,"test_pw_1")
            rows.entry_user[5].insert(0,"synthetic_high")
            rows.entry_pass[5].insert(0,"test_pw_5")
            rows.entry_user[99].insert(0,"synthetic_last")
            rows.entry_pass[99].insert(0,"test_pw_99")
            rows.row_selectors[99].invoke()
            assert rows.snapshot(99).selected
            original_entry_ids=(id(rows.entry_user[5]),id(rows.entry_pass[99]))
            before=rows.rows_inner.winfo_reqheight()
            assert rows.entry_user[99].winfo_manager()=="grid"

            denied=rows.apply_account_row_limit(3)
            assert denied.status=="PERMISSION_NOT_VERIFIED" and rows.visible_row_count==100
            malformed=rows.apply_account_row_limit(1000,allowed=lambda:True)
            assert malformed.status=="INVALID_LIMIT_NOT_ORIGINAL_TIER_PROOF"
            first=rows.apply_account_row_limit(3,allowed=lambda:True)
            root.update()
            assert first.status=="ROW_VISIBILITY_CHANGED_TEST_EXTERNAL_PLAN",first
            assert first.hidden_count==97
            assert rows.entry_user[2].winfo_manager()=="grid"
            assert rows.entry_user[3].winfo_manager()==""
            assert rows.entry_pass[99].winfo_manager()==""
            assert rows.hidden_row_indices[:5]==(3,4,5,6,7)
            after=rows.rows_inner.winfo_reqheight()
            assert after<before,(before,after)
            assert rows.snapshot(99).selected  # no destructive migration
            assert rows.snapshot(99).password=="test_pw_99"
            info["actual_tk_hide_97_preserves_test_credentials"]=True

            middle=rows.apply_account_row_limit(6,allowed=lambda:True)
            root.update()
            assert middle.visible_count==6 and middle.hidden_count==94
            assert rows.entry_user[5].winfo_manager()=="grid"
            assert rows.entry_user[6].winfo_manager()==""
            assert rows.snapshot(5).username=="synthetic_high"
            assert rows.entry_pass[5].cget("show")=="*"
            assert id(rows.entry_user[5])==original_entry_ids[0]
            info["fifo_restore_hidden_row_3_to_5_same_widgets"]=True

            # F03 original checkbox applies even to plan-hidden rows.
            rows.show_password_toggle.invoke()
            assert all(w.cget("show")=="" for w in rows.entry_pass)
            rows.show_password_toggle.invoke()
            assert all(w.cget("show")=="*" for w in rows.entry_pass)
            info["F03_mask_on_visible_and_hidden_widgets"]=True

            last=rows.apply_account_row_limit(100,allowed=lambda:True)
            root.update()
            assert last.visible_count==100 and last.hidden_count==0
            assert rows.entry_user[99].winfo_manager()=="grid"
            assert rows.entry_pass[99].get()=="test_pw_99"
            assert rows.snapshot(99).selected
            assert id(rows.entry_pass[99])==original_entry_ids[1]
            assert rows.rows_inner.winfo_reqheight()>after
            info["all_100_restored_exact_same_live_widgets"]=True

            outcome=[]
            th=threading.Thread(target=lambda:outcome.append(
                rows.apply_account_row_limit(8,allowed=lambda:True)))
            th.start();th.join(timeout=4)
            assert not th.is_alive()
            assert outcome[0].status=="WRONG_TK_THREAD"
            assert rows.visible_row_count==100
            info["non_owner_thread_does_not_mutate_widgets"]=True
            tab.shutdown()
            root.destroy();root=None
            assert cfg.read_bytes()==original_bytes
            assert read_settings(cfg).get("Settings","accounts")==original_accounts
            info["legacy_settings_exact_bytes_preserved"]=True
        info["status"]="PASS_NATIVE_S109_REAL_TK_LOGIN_100_ROWS_FIFO_VISIBILITY_NO_GAME"
    except Exception as exc:
        info["status"]="FAIL_NATIVE_S109"
        info["error"]=type(exc).__name__
        info["traceback"]=traceback.format_exc(limit=8)
        print(info["traceback"])
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        REPORT.write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding="utf-8")
        for k,v in info.items():
            if k!="traceback":
                print("S109_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if info["status"]=="PASS_NATIVE_S109_REAL_TK_LOGIN_100_ROWS_FIFO_VISIBILITY_NO_GAME" else 1


if __name__=="__main__":
    raise SystemExit(main())
