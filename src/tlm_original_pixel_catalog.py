"""S204 original TLMTool 2.1.2 full seven-section compiled PIXEL_DATA catalog.

Source: owner-uploaded exact original TLMTool.dist/TLMTool.exe,
SHA256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22.
Nuitka e.pixel_data nested dictionary D7 at original file 0x2B97B3E,
complete through 0x2B98EC5, source-only decoded (NEVER executed).
This is original DATA, not a live game match, valid automation target,
mouse click permission, packet, login or authenticated party member.

Preserve malformed/NULL color values EXACTLY as recovered, including
original donVang.loiXDongKhoDo_multi.color=[1156,107] and common
dungAuto.color=[254,0,null]. DO NOT silently fix source evidence.
Some region fields contain 4/6 values (rect/multi) rather than single
point coordinates; a point comparator must NEVER treat them as point.
"""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
import json
import math

PIXEL_DATA_EVIDENCE = "TLM2.1.2_NUITKA_PIXELS_0x2B97B3E_0x2B98EC5"
_PIXEL_CATALOG_JSON = r'''
{"login":{"login1":{"region":[614,173],"color":[81,28,12],"timeout":100,"tolerance":10},"login2":{"region":[741,186],"color":[109,32,7],"timeout":100,"tolerance":10},"update":{"region":[646,457],"color":[123,142,63],"timeout":100,"tolerance":10},"vaoTroChoi":{"region":[1285,609],"color":[226,52,56],"timeout":60,"tolerance":20},"quayLaibtn":{"region":[75,83],"color":[66,49,22],"timeout":5,"tolerance":1},"ngatKetNoi1":{"region":[640,244],"color":[160,145,52],"timeout":5,"tolerance":null},"ngatKetNoi2":{"region":[702,453],"color":[212,28,34],"timeout":5,"tolerance":null},"dichChuyen1":{"region":[405,421],"color":[235,177,76],"timeout":5,"tolerance":10},"dichChuyen2":{"region":[658,429],"color":[228,152,66],"timeout":5,"tolerance":10}},
"common":{"active":{"region":[1330,33],"color":[34,8,11],"timeout":100,"tolerance":5},"dungAuto":{"region":[1074,125],"color":[254,0,null],"timeout":1,"tolerance":10},"fullBag":{"region":[971,408],"color":[208,186,133],"timeout":100,"tolerance":20},"nguaActive":{"region":[903,683],"color":[193,162,96],"timeout":1,"tolerance":10},"canhBaoPK":{"region":[769,453],"color":[223,44,47],"timeout":300,"tolerance":15},"canhBaoPK1":{"region":[680,241],"color":[226,215,74],"timeout":300,"tolerance":15},"hp_adfbar":{"region":[97,28,305,28],"color":[255,90,60],"timeout":0.5,"tolerance":30},"dichChuyen1":{"region":[405,421],"color":[235,177,76],"timeout":5,"tolerance":10},"dichChuyen2":{"region":[658,429],"color":[228,152,66],"timeout":5,"tolerance":10},"tickNhatVatPham":{"region":[221,173],"color":[151,204,68],"timeout":1,"tolerance":10},"nhattoanbo":{"region":[630,469],"color":[220,31,38],"timeout":1,"tolerance":10},"nguoiChoiGan":{"region":[17,215],"color":[255,245,85],"timeout":1,"tolerance":10}},
"shop":{"loiXDongVatPham_multi":{"region":[799,232,894,321,0,30],"color":[230,195,68],"offset":[85,61,42],"timeout":4,"tolerance":5},"tuiDoTrong":{"region":[730,190],"color":[209,196,173],"timeout":1,"tolerance":null},"tuiDoTrong1":{"region":[795,190],"color":[209,196,173],"timeout":1,"tolerance":null},"tuiDoTrong2":{"region":[860,190],"color":[209,196,173],"timeout":1,"tolerance":null},"tuiDoTrong3":{"region":[925,190],"color":[209,196,173],"timeout":1,"tolerance":null},"tuiDoTrong4":{"region":[980,190],"color":[209,196,173],"timeout":1,"tolerance":null},"tuiDoTrong5":{"region":[1040,190],"color":[209,196,173],"timeout":1,"tolerance":null},"tuiDoTrong6":{"region":[1100,190],"color":[209,196,173],"timeout":1,"tolerance":null},"tickBanNhanh":{"region":[215,648],"color":[150,202,68],"timeout":1,"tolerance":null},"nguaActive":{"region":[903,683],"color":[193,162,96],"timeout":1,"tolerance":10}},
"tuido":{"active":{"region":[1123,631],"color":[150,166,78],"timeout":5,"tolerance":10},"slottui98":{"region":[1108,431],"color":[185,159,126],"timeout":5,"tolerance":15},"slottui98_1":{"region":[1088,429],"color":[185,159,126],"timeout":5,"tolerance":15},"slottui99":{"region":[729,496],"color":[181,156,125],"timeout":5,"tolerance":15},"slottui100":{"region":[789,496],"color":[183,158,124],"timeout":5,"tolerance":15},"slottui100_1":{"region":[777,495],"color":[164,138,110],"timeout":5,"tolerance":15},"slottui101":{"region":[853,496],"color":[209,196,173],"timeout":5,"tolerance":1},"tangBaoDo":{"region":[702,163,1132,517],"color":[255,90,60],"timeout":0.5,"tolerance":30},"tangBaoDo_multi_old":{"region":[702,163,1132,517,0,20],"color":[189,174,117],"offset":[216,182,109],"timeout":10,"tolerance":7},"tangBaoDo_multi":{"region":[702,163,1132,517,20,30],"color":[2,30,35],"offset":[228,215,170],"timeout":5,"tolerance":1}},
"trungAc":{"trungAcLenhFail":{"region":[940,169,983,175],"color":[83,127,215],"timeout":1,"tolerance":10},"trungAcLenhFull":{"region":[636,184,643,199],"color":[253,251,113],"timeout":1,"tolerance":3},"tangBaoDo":{"region":[702,163,1132,517],"color":[255,90,60],"timeout":0.5,"tolerance":30},"tangBaoDo_multi_old":{"region":[702,163,1132,517,0,20],"color":[189,174,117],"offset":[216,182,109],"timeout":10,"tolerance":7},"tangBaoDo_multi":{"region":[702,163,1132,517,20,30],"color":[2,30,35],"offset":[228,215,170],"timeout":5,"tolerance":1}},
"phoBan":{"lapLai":{"region":[244,220],"color":[159,218,54],"timeout":1,"tolerance":10},"tuLamNhiemVu":{"region":[606,480,732,493],"color":[23,210,32],"timeout":1,"tolerance":5},"loiDangTrieuHoi":{"region":[593,620],"color":[176,78,0],"timeout":1,"tolerance":10},"trungAcLenhFull":{"region":[539,184,643,199],"color":[253,251,113],"timeout":1,"tolerance":3},"diTheoDoiTruong":{"region":[409,221],"color":[151,210,54],"timeout":1,"tolerance":3},"hoiSinh":{"region":[245,313],"color":[151,210,54],"timeout":1,"tolerance":3}},
"donVang":{"nguoiChoiGan":{"region":[17,215],"color":[255,245,85],"timeout":1,"tolerance":10},"muiTenAnNhiemVu":{"region":[34,462],"color":[232,222,121],"timeout":1,"tolerance":10},"giaoDich":{"region":[627,245,645,263],"color":[137,126,113],"timeout":1,"tolerance":10},"datLen":{"region":[1200,350,1200,650],"color":[141,156,72],"timeout":1,"tolerance":4},"o9TrongGiaoDich":{"region":[675,370],"color":[158,132,105],"timeout":1,"tolerance":4},"banVatPhamTab":{"region":[139,305],"color":[143,58,21],"timeout":1,"tolerance":10},"trangBiTab":{"region":[867,141],"color":[255,191,10],"timeout":1,"tolerance":10},"loiGiaoXong":{"region":[1168,112],"color":[96,52,27],"timeout":1,"tolerance":10},"loiMoTranThu":{"region":[1120,647],"color":[132,75,42],"timeout":1,"tolerance":10},"loiXDongVatPham_multi":{"region":[682,51,1185,350,0,30],"color":[230,195,68],"offset":[56,50,28],"timeout":4,"tolerance":5},"loiXDongKhoDo":{"region":[1164,107],"color":[100,56,31],"timeout":1,"tolerance":10},"loiXDongKhoDo_multi":{"region":[1140,90,1173,165,0,30],"color":[1156,107],"offset":[209,196,173],"timeout":4,"tolerance":1},"loiKhongPhanHoi":{"region":[641,453],"color":[137,150,70],"timeout":1,"tolerance":15}}
}
'''


@dataclass(frozen=True)
class OriginalPixelSpec:
    section: str
    key: str
    region: tuple[int, ...]
    color: tuple[int | None, ...]
    tolerance: float | None
    timeout: float
    offset: tuple[int, ...] | None = None

    @property
    def reader_kind(self) -> str:
        # These are SOURCE-SAFETY validators, not an original semantic
        # confirmation of image state or action readiness.
        if (len(self.color) != 3 or
                not all(type(x) is int and 0 <= x <= 255 for x in self.color)):
            return "UNSUPPORTED_INVALID_OR_INCOMPLETE_RGB"
        if (not isinstance(self.tolerance, (float, int))
                or not math.isfinite(self.tolerance)
                or not 0 <= self.tolerance <= 100):
            return "UNSUPPORTED_UNKNOWN_OR_INVALID_TOLERANCE"
        if len(self.region) == 2 and self.offset is None:
            return "SINGLE_CLIENT_PIXEL_READONLY"
        if len(self.region) == 4 and self.offset is None:
            return "RECTANGLE_SCAN_SEPARATE_EVIDENCE_REQUIRED"
        if len(self.region) == 6 and self.offset is not None:
            return "MULTI_PIXEL_SCAN_SEPARATE_EVIDENCE_REQUIRED"
        return "UNSUPPORTED_ORIGINAL_REGION_SHAPE"


def _all_specs():
    original = json.loads(_PIXEL_CATALOG_JSON)
    if type(original) is not dict or set(original) != {
            "login", "common", "shop", "tuido", "trungAc", "phoBan", "donVang"}:
        raise ValueError("ORIGINAL_FROZEN_PIXEL_SECTIONS_MISMATCH")
    result = {}
    for section, members in original.items():
        if type(members) is not dict:
            raise ValueError("ORIGINAL_FROZEN_PIXEL_NESTING_INVALID")
        result[section] = MappingProxyType({
            key: OriginalPixelSpec(
                section, key,
                tuple(spec["region"]), tuple(spec["color"]),
                spec["tolerance"], spec["timeout"],
                tuple(spec["offset"]) if "offset" in spec else None,
            ) for key, spec in members.items()
        })
    return MappingProxyType(result)


FROZEN_PIXEL_CATALOG = _all_specs()


def original_pixel_spec(section: str, key: str) -> OriginalPixelSpec | None:
    if not isinstance(section, str) or not isinstance(key, str):
        return None
    return FROZEN_PIXEL_CATALOG.get(section, {}).get(key)
