"""S120 native actual Windows INI with exact original TLM Farm maps."""
import json
import os
from pathlib import Path
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
OUT=ROOT/"artifacts"/"s120"
OUT.mkdir(parents=True,exist_ok=True)
def run():
    result={"task":"S120","status":"NOT_RUN","game_run":False,
            "original_exe_executed":False,"proxy":"EXCLUDED",
            "info":"NOT_AVAILABLE"}
    try:
        if os.name!="nt":
            raise RuntimeError("WINDOWS_REQUIRED")
        from farm_original_maps import FARM_MAP_LIST,coord_id_for_name,coord_name_for_id
        from train_saved_coordinates import FarmCoordinate,FarmCoordinateError,FarmCoordinatesStore
        result["original_72_pairs"]=(len(FARM_MAP_LIST)==72)
        result["exact_west_lake_id"]=(coord_id_for_name("Tây Hồ")==26
                                        and coord_name_for_id(26)=="Tây Hồ")
        result["client_only_map_mismatch_blocked"]=(coord_name_for_id(2600) is None
             and coord_id_for_name("Dạ Tây Hồ") is None)
        with tempfile.TemporaryDirectory(prefix="S120_TLM_MAP_TEST_") as td:
            p=Path(td)/"settings.ini"
            before=b"[Settings]\r\naccounts = DEMO_ONLY\r\n[Farm]\r\nkeep = yes\r\n"
            p.write_bytes(before)
            store=FarmCoordinatesStore(p)
            rows=(FarmCoordinate("Train",26,"15","35"),
                  FarmCoordinate("Quỳnh",86,"44","55"))
            result["actual_disk_save"]=(store.save(rows)=="SAVED_FARM_COORDINATES")
            result["actual_disk_reload"]=(store.load().rows==rows)
            data=p.read_bytes()
            result["other_original_settings_bytes_preserved"]=(
                b"accounts = DEMO_ONLY\r\n" in data and b"keep = yes\r\n" in data)
            try:
                store.save([FarmCoordinate("Client Wrong",2600,"1","2")])
            except FarmCoordinateError:
                result["reject_client_only_id_without_rewrite"]=(p.read_bytes()==data)
            else:
                result["reject_client_only_id_without_rewrite"]=False
        checks=[key for key,val in result.items() if type(val) is bool
                and key not in ("game_run","original_exe_executed")]
        if not all(result[x] for x in checks):
            raise RuntimeError("S120_CHECK_FAILED")
        result["status"]="PASS_NATIVE_S120_TLM_ORIGINAL_67_MAPS_REAL_INI_NO_GAME"
    except Exception as exc:
        result["status"]="FAIL_NATIVE_S120"
        result["error_type"]=type(exc).__name__
    (OUT/"windows_maps.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    for k,v in result.items():
        print("S120_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if result["status"].startswith("PASS_NATIVE_S120_") else 1
if __name__=="__main__":
    raise SystemExit(run())
