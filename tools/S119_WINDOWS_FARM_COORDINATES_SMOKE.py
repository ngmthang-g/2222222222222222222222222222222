"""S119 real Windows filesystem test for verified H11 Farm coord INI writer."""
import json
import os
from pathlib import Path
import sys
import tempfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
OUT=ROOT/"artifacts"/"s119"
OUT.mkdir(parents=True,exist_ok=True)

def run():
    result={"task":"S119","status":"NOT_RUN","game_run":False,
            "real_info":"NOT_AVAILABLE","proxy":"EXCLUDED",
            "map_registry":"TEST_FIXTURE_NOT_CLIENT"}
    try:
        if os.name!="nt":
            raise RuntimeError("WINDOWS_REQUIRED")
        from train_saved_coordinates import FarmCoordinate,FarmCoordinatesStore
        with tempfile.TemporaryDirectory(prefix="S119_FARM_TEST_") as td:
            path=Path(td)/"settings.ini"
            before=("[Settings]\r\naccounts = KEEP_RAW_TOKEN|DUMMY|No|Proxy|x\r\n"
                    "[Farm]\r\ncoord_7 = O|101|0|0\r\nfarm_stop = do-not-touch\r\n"
                    "[Other]\r\nkeep = yes\r\n").encode()
            path.write_bytes(before)
            store=FarmCoordinatesStore(path,known_map_ids={101:"TestA",202:"TestB"})
            result["source_rows_read_from_disk"]=(len(store.load().rows)==1)
            changed=store.save((FarmCoordinate("Điểm Train",202,"15","33"),))
            after=path.read_bytes()
            result["real_file_changed"]=(changed=="SAVED_FARM_COORDINATES" and
                                         b"coord_1 = " in after and
                                         b"coord_7" not in after)
            result["all_unrelated_bytes_preserved"]=(after==before.replace(
                b"coord_7 = O|101|0|0", "coord_1 = Điểm Train|202|15|33".encode()))
            result["reload_actual_coordinates"]=(store.load().rows==
                (FarmCoordinate("Điểm Train",202,"15","33"),))
            result["repeat_saves_do_not_rewrite"]=(store.save(store.load().rows)=="UNCHANGED" and path.read_bytes()==after)
            result["dated_original_backup_created"]=(len(list(Path(td).glob("settings.????????.ini")))==1)
        required=[k for k,v in result.items() if type(v) is bool and k!="game_run"]
        if not all(result[k] for k in required):
            raise RuntimeError("S119_FILE_ASSERTIONS_FAILED")
        result["status"]="PASS_NATIVE_S119_FARM_COORDINATES_REAL_DISK_ONLY_NOT_TRAIN"
    except Exception as exc:
        result["status"]="FAIL_NATIVE_S119"
        result["error_type"]=type(exc).__name__
    (OUT/"farm_coordinates_native.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    for k,v in result.items():
        print("S119_"+k.upper()+"="+json.dumps(v,ensure_ascii=True))
    return 0 if result["status"].startswith("PASS_NATIVE_S119_") else 1

if __name__=="__main__":
    raise SystemExit(run())
