"""S170 independent TrainLSV coordinate records; B06/I10 original evidence.

Only [TrainLSV] coord_<n>=name|map_id|x|y is edited. Numeric key
allocation uses append max(existing)+1 as an explicitly LOCAL safe policy:
the original first-number/gap reuse and autosave debounce remain UNKNOWN.
No movement, Train apply, game packet or original TLM licensing.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import os
from pathlib import Path
import re
import shutil
import tempfile

from settings_store import _settings_lock
from train_saved_coordinates import MAX_SETTINGS_BYTES
from train_lsv_top_settings import TrainLsvTopStore, TrainLsvSettingsError

LSV_MAP_IDS = {
    10014: "Tần Hoàng Địa Cung Tầng 1",
    10015: "Tần Hoàng Địa Cung Tầng 2",
    10016: "Tần Hoàng Địa Cung Tầng 3",
    10017: "Tần Hoàng Địa Cung Tầng 4",
    10004: "Phàm Liên Trại",
    10005: "Thanh Liên Trại",
    10007: "Khô Vinh Đạo",
}
LSV_MAP_NAMES = {name: num for num, name in LSV_MAP_IDS.items()}
_COORD_PREFIX = re.compile(r"^[ \t]*coord_", re.I)
_COORD_VALUE = re.compile(r"^[ \t]*coord_(\d+)[ \t]*[=:][ \t]*(.*?)(\r?\n)?$", re.I)


class TrainLsvCoordinateError(ValueError):
    pass


@dataclass(frozen=True)
class LsvCoordinate:
    key_number: int
    name: str
    map_id: int
    x: str
    y: str


@dataclass(frozen=True)
class LsvCoordinatesSnapshot:
    rows: tuple[LsvCoordinate, ...]
    skipped_retired: tuple[int, ...]
    file_bytes: bytes


class TrainLsvCoordinatesStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._top = TrainLsvTopStore(self.path)

    @staticmethod
    def _value(number: int, text: str) -> LsvCoordinate:
        # Shared original parser splits at the LAST three pipe fields, so
        # preset names may contain a literal pipe.
        fields=text.split("|")
        if len(fields)<4:
            raise TrainLsvCoordinateError("INVALID_LSV_COORD_VALUE")
        name="|".join(fields[:-3])
        map_text,x,y=fields[-3:]
        if not map_text.isascii() or not map_text.isdecimal():
            raise TrainLsvCoordinateError("INVALID_LSV_COORD_MAP_ID")
        return LsvCoordinate(number,name,int(map_text),x,y)

    @staticmethod
    def _read_rows(lines, begin, end):
        if begin is None:
            return []
        rows=[]
        seen=set()
        for index in range(begin+1,end):
            value=lines[index]
            if not _COORD_PREFIX.match(value):
                continue
            match=_COORD_VALUE.fullmatch(value)
            if not match:
                raise TrainLsvCoordinateError("MALFORMED_LSV_COORD_RECORD")
            num=int(match.group(1))
            if num in seen:
                raise TrainLsvCoordinateError("DUPLICATE_LSV_COORD_INDEX")
            if index+1<end and lines[index+1][:1] in (" ","\t"):
                raise TrainLsvCoordinateError("AMBIGUOUS_LSV_COORD_CONTINUATION")
            seen.add(num)
            rows.append((index,TrainLsvCoordinatesStore._value(num,match.group(2))))
        rows.sort(key=lambda v:v[1].key_number)  # never lexical coord_10 vs coord_2
        return rows

    @staticmethod
    def _validated_edit(name: str, map_id: int, x: str, y: str):
        if (type(name) is not str or not name.strip()
                or len(name)>180 or any(c in name for c in "\r\n\x00")
                or type(map_id) is not int or map_id not in LSV_MAP_IDS
                or any(type(v) is not str or not v.strip() or len(v)>80
                       or any(c in v for c in "\r\n\x00|") for v in (x,y))):
            raise TrainLsvCoordinateError("INVALID_OR_UNVERIFIED_LSV_COORD")
        # Do not convert to pixels, infer map IDs, or silently change user text.
        return name,map_id,x,y

    def load(self) -> LsvCoordinatesSnapshot:
        with _settings_lock:
            try:
                raw,lines,_,start,end=self._top._read()
            except TrainLsvSettingsError as exc:
                raise TrainLsvCoordinateError("UNSAFE_LSV_COORD_SETTINGS") from exc
            parsed=self._read_rows(lines,start,end)
            good=tuple(v for _,v in parsed if v.map_id in LSV_MAP_IDS)
            skipped=tuple(v.map_id for _,v in parsed if v.map_id not in LSV_MAP_IDS)
            return LsvCoordinatesSnapshot(good,skipped,raw)

    def _commit(self, action: str, key_number: int | None, *,
                expected_bytes: bytes, name: str="", map_id: int=0,
                x: str="", y: str="") -> LsvCoordinatesSnapshot:
        if (type(expected_bytes) is not bytes or action not in ("save","delete")
                or (key_number is not None
                    and (type(key_number) is not int or key_number<0))):
            raise TrainLsvCoordinateError("INVALID_LSV_COORD_REQUEST")
        if action=="save":
            self._validated_edit(name,map_id,x,y)
        elif key_number is None:
            raise TrainLsvCoordinateError("MISSING_DELETE_TARGET")
        with _settings_lock:
            try:
                raw,lines,nl,start,end=self._top._read()
            except TrainLsvSettingsError as exc:
                raise TrainLsvCoordinateError("UNSAFE_LSV_COORD_SETTINGS") from exc
            if raw!=expected_bytes:
                raise TrainLsvCoordinateError("STALE_LSV_COORD_SETTINGS")
            entries=self._read_rows(lines,start,end)
            byid={v.key_number:(pos,v) for pos,v in entries}
            if key_number is not None and key_number not in byid:
                raise TrainLsvCoordinateError("MISSING_LSV_COORD_KEY")
            if action=="save":
                # In the independent app, name identity must be unambiguous:
                # original duplicate winner is UNKNOWN.
                if any(v.name==name and v.key_number!=key_number
                       for _,v in entries):
                    raise TrainLsvCoordinateError("AMBIGUOUS_LSV_PRESET_NAME")
                if key_number is None:
                    # LOCAL append policy, NOT an assertion about original
                    # first suffix or gaps; never renumber existing records.
                    key_number=max(byid,default=0)+1
                newrecord=f"coord_{key_number} = {name}|{map_id}|{x}|{y}{nl}"
            modified=list(lines)
            if action=="delete":
                pos,_=byid[key_number]
                del modified[pos]
            elif key_number in byid:
                pos,_=byid[key_number]
                old=_COORD_VALUE.fullmatch(modified[pos])
                if old is None:
                    raise TrainLsvCoordinateError("INVALID_COORD_ROW_FOR_EDIT")
                # Preserve original spacing, delimiter and original suffix.
                prefix=modified[pos][:modified[pos].find(old.group(2))]
                modified[pos]=prefix+f"{name}|{map_id}|{x}|{y}"+(old.group(3) or "")
            elif start is None:
                prefix=("" if not modified or modified[-1].endswith(("\n","\r"))
                        else nl)
                modified.append(prefix+"[TrainLSV]"+nl+newrecord)
            else:
                if end>0 and not modified[end-1].endswith(("\n","\r")):
                    raise TrainLsvCoordinateError("UNTERMINATED_LSV_SECTION")
                modified.insert(end,newrecord)
            encoded="".join(modified).encode("utf-8")
            if encoded==raw:
                return self.load()  # same re-entrant RLock
            if len(encoded)>MAX_SETTINGS_BYTES:
                raise TrainLsvCoordinateError("LSV_COORD_SETTINGS_TOO_LARGE")
            self.path.parent.mkdir(parents=True,exist_ok=True)
            fd,temp=tempfile.mkstemp(prefix="settings.",suffix=".tmp",
                                      dir=str(self.path.parent))
            try:
                with os.fdopen(fd,"wb") as out:
                    out.write(encoded)
                    out.flush()
                    os.fsync(out.fileno())
                current=self.path.read_bytes() if self.path.exists() else b""
                if current!=raw:
                    raise TrainLsvCoordinateError("LSV_COORD_CHANGED_CONCURRENTLY")
                if self.path.exists():
                    backup=self.path.with_name(
                        "settings."+datetime.now().strftime("%Y%m%d")+".ini")
                    if not backup.exists():
                        shutil.copy2(self.path,backup)
                os.replace(temp,self.path)
            except OSError as exc:
                raise TrainLsvCoordinateError("LSV_COORD_WRITE_FAILED") from exc
            finally:
                if os.path.exists(temp):
                    os.unlink(temp)
            # No nested lock assumptions: format rows from the local bytes
            # already validated by _read_rows.
            check=self._read_rows(modified,
                start if start is not None else len(lines)+
                    (1 if lines and not lines[-1].endswith(("\n","\r")) else 0),
                len(modified)) if start is not None else self._read_rows(
                    modified, len(lines), len(modified))
            valid=tuple(v for _,v in check if v.map_id in LSV_MAP_IDS)
            retired=tuple(v.map_id for _,v in check if v.map_id not in LSV_MAP_IDS)
            return LsvCoordinatesSnapshot(valid,retired,encoded)

    def save_row(self, *, expected_bytes: bytes, name: str, map_id: int,
                 x: str, y: str, key_number: int | None = None):
        return self._commit("save",key_number,expected_bytes=expected_bytes,
                            name=name,map_id=map_id,x=x,y=y)

    def delete_row(self, key_number: int, *, expected_bytes: bytes):
        return self._commit("delete",key_number,expected_bytes=expected_bytes)
