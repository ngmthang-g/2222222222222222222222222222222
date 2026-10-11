"""S138: standalone developer-only, read-only lookup against exact original data.

Can run from the S138 offline diagnostic ZIP; never attaches to a game.
Examples: py -3 tools/S138_CATALOG_LOOKUP.py --item-id 10100000
          python tools/S138_CATALOG_LOOKUP.py --item-id 10100000 --catalog assets/original_item_catalog.json.gz
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from original_item_catalog_resource import load_verified_export


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="OFFLINE original item metadata lookup (NOT TLMTool)")
    ap.add_argument("--item-id",required=True,type=int,help="Original item template ItemID")
    ap.add_argument("--catalog",type=Path,
                    default=ROOT/"assets"/"original_item_catalog.json.gz")
    args = ap.parse_args(argv)
    try:
        catalog = load_verified_export(args.catalog)
    except (ValueError, OSError) as exc:
        print(json.dumps({"status":"BLOCKED_CATALOG_NOT_VERIFIED",
                          "reason":str(exc),
                          "game_attached":False,"game_actions_sent":False},
                         ensure_ascii=False),file=sys.stderr)
        return 2
    item = catalog.lookup(args.item_id)
    if item is None:
        print(json.dumps({"status":"UNKNOWN_ITEMID_IN_ORIGINAL_2_1_2",
                          "itemID":args.item_id,
                          "game_attached":False,"game_actions_sent":False},
                         ensure_ascii=False))
        return 3
    print(json.dumps({
        "status":"PASS_OFFLINE_ORIGINAL_2_1_2_ITEMID_METADATA",
        "itemID":item.item_id,"name":item.name,"icon":item.icon,
        "src":item.src,"type":item.equip_type,
        "is_weapon":catalog.weapon_membership(item.item_id),
        "game_attached":False,"runtime_bag_read_verified":False,
        "game_actions_sent":False,
    },ensure_ascii=False))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
