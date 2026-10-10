"""S63 real Windows Tk.after 1000ms Auto cadence, NO game/geometry/EXE."""
from __future__ import annotations
import json,os,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s63"
OUT.mkdir(parents=True,exist_ok=True)
def run():
    result={"task":"S63","status":"NOT_RUN","real_game":"NOT_RUN",
            "real_game_tiling":"NOT_IMPLEMENTED","product_exe":"NOT_PRODUCT",
            "proxy_runtime":"EXCLUDED"}
    root=None
    try:
        if os.name!="nt":raise RuntimeError("WINDOWS_REQUIRED")
        import tkinter as tk
        from auto_tile_clock import C07AutoTileClock,AUTO_TILE_LOOP_INTERVAL_MS
        root=tk.Tk()
        root.withdraw()
        permit=[True]
        ticks=[]
        start=time.monotonic()
        scheduler=C07AutoTileClock(root,on_tick=lambda:ticks.append(time.monotonic()),
                                  allowed=lambda:permit[0])
        result["starts_when_test_gate_allows"]=scheduler.start()
        def pump_until(condition,deadline):
            while not condition() and time.monotonic()<deadline:
                root.update()
                time.sleep(.01)
            return condition()
        result["actual_two_tk_after_callbacks"]=pump_until(
            lambda:len(ticks)==2,start+3.1)
        result["original_cadence_constant_ms"]=AUTO_TILE_LOOP_INTERVAL_MS
        result["first_tick_delay_seconds"]=round(ticks[0]-start,3) if ticks else None
        result["second_tick_spacing_seconds"]=round(ticks[1]-ticks[0],3) if len(ticks)>1 else None
        result["real_windows_tk_approximately_1000ms"]=(
            len(ticks)==2 and .85<=ticks[0]-start<=1.55
            and .85<=ticks[1]-ticks[0]<=1.55)
        permit[0]=False
        count=len(ticks)
        end=time.monotonic()+1.2
        while time.monotonic()<end:
            root.update()
            time.sleep(.01)
        result["revocation_prevents_third_tick_and_stops"]=(
            len(ticks)==count and not scheduler.auto_tile_active
            and scheduler._auto_tile_id is None)
        scheduler.shutdown()
        result["close_prevents_restart"]=not scheduler.start()
        result["no_game_windows_changed"]=True
        root.destroy();root=None
        check=("starts_when_test_gate_allows",
               "actual_two_tk_after_callbacks",
               "real_windows_tk_approximately_1000ms",
               "revocation_prevents_third_tick_and_stops",
               "close_prevents_restart",
               "no_game_windows_changed")
        assert all(result.get(k) is True for k in check),result
        result["status"]="PASS_NATIVE_S63_REAL_TK_1000MS_REVOKED_NO_GAME"
    except Exception as exc:
        result["status"]="FAIL_NATIVE_S63"
        result["error_type"]=type(exc).__name__
        result["error_text"]=str(exc)[:220]
    finally:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        (OUT/"s63_real_windows_tk_timer.json").write_text(
            json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
        for key,value in result.items():
            print("S63_"+key.upper()+"="+json.dumps(value,ensure_ascii=True))
    return int(result["status"]!="PASS_NATIVE_S63_REAL_TK_1000MS_REVOKED_NO_GAME")
if __name__=="__main__":raise SystemExit(run())
