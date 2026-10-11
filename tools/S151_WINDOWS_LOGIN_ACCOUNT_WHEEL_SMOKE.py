"""S151 native Win64 actual Tk account grid wheel, test-owned no game."""
from __future__ import annotations
import json,os,sys,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from login_account_rows import TLMAccountRows

def run():
    if os.name!="nt":
        raise OSError("WIN64_REQUIRED")
    import tkinter as tk
    with tempfile.TemporaryDirectory() as folder:
        settings=Path(folder)/"settings.ini"
        baseline=b"[Settings]\r\naccounts = X|dummy|secret|Kh\xc3\xb4ng|\r\n"
        settings.write_bytes(baseline)
        root=tk.Tk()
        root.title("S151 TEST OWNED LOGIN 100 ROW SCROLL")
        root.geometry("485x1110+50+50")
        try:
            rows=TLMAccountRows(root)
            root.update_idletasks()
            root.update()
            canvas=rows.canvas
            checks={}
            checks["real_native_100_row_widgets"]=len(rows.row_selectors)==100
            checks["canvas_scrollregion_extends_past_view"]=(
                canvas.bbox("all")[3]>canvas.winfo_height())
            checks["new_blank_grid_native_wheel_binding"]=bool(rows.rows_inner.bind("<MouseWheel>"))
            checks["header_button_native_wheel_binding"]=bool(rows.header_selector.bind("<MouseWheel>"))
            headers=[
                w for w in rows.rows_inner.winfo_children()
                if isinstance(w,tk.Label) and w.cget("text") in
                   ("Tài khoản","Mật khẩu","Ẩn captcha","Login","Proxy")
            ]
            checks["all_five_header_labels_native_wheel_bound"]=(
                len(headers)==5 and all(w.bind("<MouseWheel>") for w in headers))
            def scroll_on(widget):
                canvas.yview_moveto(0)
                root.update_idletasks()
                before=canvas.yview()[0]
                widget.event_generate("<MouseWheel>",delta=-120)
                root.update_idletasks()
                return canvas.yview()[0]>before
            checks["wheel_over_real_blank_row_area_scrolls"]=scroll_on(rows.rows_inner)
            checks["wheel_over_real_header_label_scrolls"]=scroll_on(headers[0])
            checks["wheel_over_header_check_button_scrolls"]=scroll_on(rows.header_selector)
            checks["wheel_over_actual_username_entry_scrolls"]=scroll_on(rows.entry_user[0])
            # Events on external widgets must not reach account Canvas:
            outside=tk.Button(root,text="OUTSIDE WHEEL IS UNRELATED")
            outside.place(x=430,y=30,width=50,height=20)
            root.update_idletasks()
            before=canvas.yview()
            outside.event_generate("<MouseWheel>",delta=-120)
            root.update_idletasks()
            checks["wheel_outside_account_canvas_no_global_interception"]=(
                canvas.yview()==before and not root.bind_all("<MouseWheel>"))
            checks["legacy_account_ini_bytes_untouched"]=settings.read_bytes()==baseline
            rows.shutdown()
            checks["shutdown_preserves_account_ini_bytes"]=settings.read_bytes()==baseline
            return checks
        finally:
            root.destroy()

def main():
    try:
        checks=run()
        output={"status":("PASS_NATIVE_S151_REAL_F01_ACCOUNT_CANVAS_WHEEL_TEST_OWNED_NO_GAME"
                          if all(checks.values()) else "FAIL_S151_ACCOUNT_SCROLL"),
                "checks":checks,"original_game_used":False,
                "product_exe_verified":False}
    except Exception as exc:
        output={"status":"FAIL_S151_ACCOUNT_SCROLL","error_type":type(exc).__name__,
                "original_game_used":False}
    target=ROOT/"artifacts"/"s151"/"real_tk_account_wheel.json"
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(output,ensure_ascii=False))
    return 0 if output["status"].startswith("PASS_") else 1

if __name__=="__main__":raise SystemExit(main())
