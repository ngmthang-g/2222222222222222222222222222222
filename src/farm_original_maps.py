"""S120: EXACT original TLM 2.1.2 Farm map name/ID choices, in original UI order.

Original frozen inner EXE SHA256: 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22
Serialized farm_data.FARM_MAP_LIST bytes at 0x293975c..0x2939dc6:
SHA256 f5e9504230d6d5feeb2a33386c0e07c1e8f89005af2a645d92fce7af6ff8e917.
72 original pairs = 67 unique MapIDs + 5 visual separators.
Client database/MAPS.csv has DIFFERENT UI labels/IDs; do not substitute it.
Pure frozen data only. NO real game process, Proxy or Info authorization.
"""
from __future__ import annotations

from types import MappingProxyType

SEPARATOR = "==================="
FARM_MAP_LIST: tuple[tuple[str, int | None], ...] = (
    ("Đại Lý", 2),
    ("Lạc Dương", 3),
    ("Tô Châu", 4),
    ("Lâu Lan", 5),
    ("===================", None),
    ("Phó Bản-Thiên Sơn", 1300),
    ("Phó Bản-Núi Võ Đang", 1400),
    ("Phó Bản-Đường Môn", 1700),
    ("===================", None),
    ("Vô Lượng Sơn", 19),
    ("Nhĩ Hải", 20),
    ("Kiếm Các", 21),
    ("Đôn Hoàng", 22),
    ("Tung Sơn", 23),
    ("Nhạn Nam", 24),
    ("Thái Hồ", 25),
    ("Tây Hồ", 26),
    ("Long Tuyền", 27),
    ("Kiếm Gia", 28),
    ("Thanh Nguyên", 29),
    ("Kính Hồ", 30),
    ("Nhạn Bắc", 31),
    ("Thảo Liệu Trường", 32),
    ("===================", None),
    ("Yến Vương Cổ Mộ 1", 33),
    ("Yến Vương Cổ Mộ 2", 34),
    ("Yến Vương Cổ Mộ 3", 35),
    ("Yến Vương Cổ Mộ 4", 36),
    ("Yến Vương Cổ Mộ 5", 37),
    ("Yến Vương Cổ Mộ 6", 38),
    ("Yến Vương Cổ Mộ 7", 39),
    ("Yến Vương Cổ Mộ 8", 40),
    ("Yến Vương Cổ Mộ 9", 41),
    ("Ma Nhai Động", 42),
    ("Thảo Nguyên", 43),
    ("Thủy Kính Hồ", 44),
    ("Liêu Tây", 45),
    ("Tiên Vương Thần", 46),
    ("Ngân Nhai Tuyết Nguyên", 47),
    ("Trường Bạch Sơn", 48),
    ("Hoàng Long Phủ", 49),
    ("===================", None),
    ("Bảo Tàng Động 1", 50),
    ("Bảo Tàng Động 2", 51),
    ("Bảo Tàng Động 3", 52),
    ("Bảo Tàng Động 4", 53),
    ("Bảo Tàng Động 5", 54),
    ("Hỏa Diệm Sơn", 55),
    ("Ôn Tuyền Động", 56),
    ("Thương Sơn", 57),
    ("Dã Nhân Cốc", 59),
    ("Thạch Lâm", 60),
    ("Ngọc Khê", 61),
    ("Đào Hoa Nguyên", 62),
    ("Nam Chiêu", 63),
    ("Miêu Cương", 64),
    ("Diêm Hồ", 65),
    ("===================", None),
    ("Bạch Sa Diêm Khanh", 66),
    ("Thiên Khanh Thụ Động", 67),
    ("Cao Xương", 68),
    ("Cao Xương Mê Cung", 69),
    ("Hỏa Diệm Cốc", 70),
    ("Đại Uyển", 71),
    ("Hãn Huyết Lĩnh", 72),
    ("Tháp Lý Mộc", 73),
    ("Tháp Khắc Lạp Mã Can", 74),
    ("Côn Lôn Sơn", 75),
    ("Côn Lôn Phúc Địa", 76),
    ("Võ Di", 83),
    ("Nam Hải", 85),
    ("Quỳnh Châu", 86),
)

FARM_MAP_ID_TO_NAME = MappingProxyType(
    {mid: name for name, mid in FARM_MAP_LIST if mid is not None})
FARM_MAP_NAME_TO_ID = MappingProxyType(
    {name: mid for name, mid in FARM_MAP_LIST if mid is not None})

if (len(FARM_MAP_LIST) != 72 or len(FARM_MAP_ID_TO_NAME) != 67
        or len(FARM_MAP_NAME_TO_ID) != 67
        or sum(mid is None for _, mid in FARM_MAP_LIST) != 5):
    raise RuntimeError("TLM_ORIGINAL_MAP_CATALOG_INTEGRITY_ERROR")


def coord_id_for_name(display_name: str) -> int | None:
    """Original visible name to unique map ID; no aliases/fuzzy matches."""
    return (FARM_MAP_NAME_TO_ID.get(display_name)
            if isinstance(display_name, str) else None)


def coord_name_for_id(map_id: int) -> str | None:
    """Original map ID to visible name; reject invalid/retired ids."""
    return FARM_MAP_ID_TO_NAME.get(map_id) if type(map_id) is int else None
