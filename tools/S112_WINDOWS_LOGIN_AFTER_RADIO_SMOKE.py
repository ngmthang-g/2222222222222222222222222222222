"""S112 native Windows Tk F01/F10 post-login radio settings only (no game)."""
from __future__ import annotations
import json,os,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s112"
OUT.mkdir(parents=True,exist_ok=True)

def main():
    if os.name!="nt":raise RuntimeError("S112 Windows Tk smoke only")
    import tkinter as tk
    from login_tab import TLMLoginPathTab
    from login_after_login_choice import AFTER_CHOICES,read_after_login_choice
    from settings_store import read_settings
    status=dict(task="S112",real_tk=True,real_game=False,real_license=False,
                routed_game_actions=0,ini_other_bytes_preserved=False,status="NOT_RUN")
    root=None
    try:
        with tempfile.TemporaryDirectory(prefix="s112_radio_") as td:
            p=Path(td)/"TLMTool"/"settings.ini"
            p.parent.mkdir(parents=True,exist_ok=True)
            original=("[Settings]\r\n"
                      "accounts = ?|alice|pw1|Co|opaque\r\n"
                      " ?|bob|pw2|Tool|opaque\r\n"
                      "schedule_on = UNKNOWN\r\nschedule_close = 04:00\r\n"
                      "schedule_open = 04:20\r\nshutdown_after_close = UNKNOWN\r\n"
                      "after_login = wait\r\n[Keep]\r\nkey = intact\r\n").encode("utf-8")
            p.write_bytes(original)
            accounts_before=read_settings(p).get("Settings","accounts")
            root=tk.Tk();root.title("S112 TEST ONLY - no Thần Long launch")
            root.geometry("650x1060+12+12")
            tab=TLMLoginPathTab(root,settings_file=p,
                                choose_directory=lambda **_:"",
                                show_error=lambda *_:None)
            root.update()
            selector=tab.after_login_choice
            assert selector.label.cget("text")=="Sau khi login:"
            assert selector.label.winfo_manager()=="place"
            assert selector.selection_var.get()=="wait"
            assert len(selector.radios)==len(AFTER_CHOICES)==5
            assert [r.cget("text") for r in selector.radios]==[x[0] for x in AFTER_CHOICES]
            assert selector.radios[4].cget("text")=="Dồn vàng"
            assert tab.schedule_times.group.winfo_y()==88
            assert tab.account_rows.group_accounts.winfo_y()==238
            for radio,(_,value) in zip(selector.radios,AFTER_CHOICES):
                assert str(radio.cget("state"))=="normal"
                radio.invoke();root.update()
                assert selector.selection_var.get()==value
                assert read_after_login_choice(p)==(value,"READ_ONLY_VERIFIED_CHOICE")
            expected=original.replace(b"after_login = wait",b"after_login = don")
            assert p.read_bytes()==expected
            assert read_settings(p).get("Settings","accounts")==accounts_before
            status["ini_other_bytes_preserved"]=True
            tab.shutdown();root.destroy();root=None
            status["status"]="PASS_NATIVE_S112_REAL_F01_F10_RADIOS_ONLY_NO_POST_LOGIN_DISPATCH"
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        (OUT/"s112.json").write_text(json.dumps(status,ensure_ascii=False,indent=2),
                                     encoding="utf-8")
    print(status["status"])

if __name__=="__main__":main()
