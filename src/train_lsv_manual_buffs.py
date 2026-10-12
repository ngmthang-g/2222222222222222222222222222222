"""S171 safely append original I05 TrainLSV manual buff config; no game send.

Original buff_<n> key/persistence is verified but fixed Dạ Minh Châu
numeric index is UNKNOWN. This store NEVER edits or deletes preexisting
buff_* records; only a NEW, strictly collision-free append is permitted.
The optional exact delete API only accepts a record created during the
current live UI session and its expected full value/bytes; no assumptions
about legacy ownership survive app restarts.
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

BUFF_KEYS = tuple(f"F{i}" for i in range(1, 11)) + ("1","2","3")
BUFF_DEFAULT = (False, "1", "0", "5")
_BUFF_PREFIX = re.compile(r"^[ \t]*buff_", re.I)
_BUFF_LINE = re.compile(r"^([ \t]*)(buff_(\d+))([ \t]*[=:][ \t]*)(.*?)(\r?\n)?$", re.I)
_DECIMAL = re.compile(r"^[0-9]{1,9}$")


class TrainLsvBuffError(ValueError):
    """Fail safely instead of overwriting unknown fixed Dạ Minh Châu key."""


@dataclass(frozen=True)
class LsvBuffRecord:
    number: int
    enabled: bool
    key: str
    minutes: str
    seconds: str
    raw: str


@dataclass(frozen=True)
class LsvBuffSnapshot:
    rows: tuple[LsvBuffRecord, ...]
    file_bytes: bytes


def validate_manual_buff(enabled: bool, key: str, minutes: str, seconds: str):
    if (type(enabled) is not bool or type(key) is not str
            or key not in BUFF_KEYS or type(minutes) is not str
            or type(seconds) is not str
            or _DECIMAL.fullmatch(minutes) is None
            or _DECIMAL.fullmatch(seconds) is None):
        raise TrainLsvBuffError("INVALID_OR_UNKNOWN_MANUAL_BUFF")
    # Original zero interval policy UNKNOWN. Never send game keys here;
    # accepting 0/0 as inert *data* is not claiming working schedule.
    return enabled,key,minutes,seconds


class TrainLsvBuffStore:
    def __init__(self,path: str | Path):
        self.path=Path(path)
        self._section=TrainLsvTopStore(self.path)

    @staticmethod
    def _rows(lines,begin,end):
        found=[]
        used=set()
        if begin is None:
            return found
        for pos in range(begin+1,end):
            line=lines[pos]
            if not _BUFF_PREFIX.match(line):
                continue
            m=_BUFF_LINE.fullmatch(line)
            if m is None:
                raise TrainLsvBuffError("MALFORMED_BUFF_KEY")
            num=int(m.group(3))
            if num in used:
                raise TrainLsvBuffError("DUPLICATE_BUFF_KEY")
            if pos+1<end and lines[pos+1][:1] in (" ","\t"):
                raise TrainLsvBuffError("AMBIGUOUS_BUFF_CONTINUATION")
            used.add(num)
            value=m.group(5)
            fields=value.split("|")
            # Imported original rows may have unsupported/uncertain values:
            # reserve their index and keep untouched, report raw readonly.
            valid=None
            if len(fields)==4:
                v=fields[0].strip().lower()
                if v in ("true","false"):
                    try:
                        valid=validate_manual_buff(
                            v=="true",fields[1],fields[2],fields[3])
                    except TrainLsvBuffError:
                        pass
            found.append((pos,num,valid,value))
        return sorted(found,key=lambda item:item[1])

    def load(self):
        with _settings_lock:
            try:
                raw,lines,_,begin,end=self._section._read()
            except TrainLsvSettingsError as exc:
                raise TrainLsvBuffError("UNSAFE_BUFF_SETTINGS") from exc
            rows=self._rows(lines,begin,end)
            return LsvBuffSnapshot(tuple(
                LsvBuffRecord(n, v[0],v[1],v[2],v[3],text)
                if v is not None else LsvBuffRecord(n,False,"","","",text)
                for _,n,v,text in rows
            ),raw)

    def append(self,*,expected_bytes: bytes,enabled: bool=False,
               key: str="1",minutes: str="0",seconds: str="5"):
        if type(expected_bytes) is not bytes:
            raise TrainLsvBuffError("EXPECTED_SNAPSHOT_REQUIRED")
        validate_manual_buff(enabled,key,minutes,seconds)
        with _settings_lock:
            try:
                raw,lines,nl,begin,end=self._section._read()
            except TrainLsvSettingsError as exc:
                raise TrainLsvBuffError("UNSAFE_BUFF_SETTINGS") from exc
            if raw!=expected_bytes:
                raise TrainLsvBuffError("STALE_BUFF_SETTINGS")
            rows=self._rows(lines,begin,end)
            # Independent-only monotonic append. Historical fixed index
            # remains reserved with all other existing indexed rows.
            number=max((n for _,n,_,_ in rows),default=0)+1
            value=f"{enabled}|{key}|{minutes}|{seconds}"
            record=f"buff_{number} = {value}{nl}"
            changed=list(lines)
            if begin is None:
                prefix="" if not changed or changed[-1].endswith(("\r","\n")) else nl
                changed.append(prefix+"[TrainLSV]"+nl+record)
            else:
                if end>0 and not changed[end-1].endswith(("\r","\n")):
                    raise TrainLsvBuffError("UNTERMINATED_TRAINLSV")
                changed.insert(end,record)
            self._write(raw,"".join(changed).encode("utf-8"))
            new=self.load()
            return number,new

    def update_session_row(self, number: int, *, expected_bytes: bytes,
                           expected_raw: str, enabled: bool, key: str,
                           minutes: str, seconds: str):
        """S173 modify only an exact row the Tk caller just created.

        The caller's in-memory session ownership gate is required; this
        store additionally enforces the full stale-file snapshot AND the
        old exact buff value to prevent accidental overwrites. Never infer
        the legacy fixed Dạ Minh Châu numeric key.
        """
        if (type(number) is not int or number < 0
                or type(expected_bytes) is not bytes
                or type(expected_raw) is not str):
            raise TrainLsvBuffError("INVALID_BUFF_EDIT_CAPABILITY")
        validate_manual_buff(enabled, key, minutes, seconds)
        with _settings_lock:
            try:
                raw, lines, _, begin, end = self._section._read()
            except TrainLsvSettingsError as exc:
                raise TrainLsvBuffError("UNSAFE_BUFF_SETTINGS") from exc
            if raw != expected_bytes:
                raise TrainLsvBuffError("STALE_BUFF_SETTINGS")
            matches = [(pos, val) for pos, n, _, val in
                       self._rows(lines, begin, end) if n == number]
            if len(matches) != 1 or matches[0][1] != expected_raw:
                raise TrainLsvBuffError("BUFF_SESSION_ROW_CHANGED")
            pos, _ = matches[0]
            match = _BUFF_LINE.fullmatch(lines[pos])
            if match is None:
                raise TrainLsvBuffError("MALFORMED_BUFF_ROW")
            value = f"{enabled}|{key}|{minutes}|{seconds}"
            # Preserve key spelling, spacing, colon/equal and newline.
            lines[pos] = (match.group(1) + match.group(2)
                          + match.group(4) + value + (match.group(6) or ""))
            new = "".join(lines).encode("utf-8")
            self._write(raw, new)
            return self.load()

    def delete_session_row(self,number: int,*,expected_bytes: bytes,
                           expected_raw: str):
        """Only a newly appended UI-owned row (session-only capability).

        Caller must remember exact freshly created (index, serialized value)
        in memory; no persisted ownership claim, never expose old rows.
        """
        if (type(number) is not int or number<0
                or type(expected_bytes) is not bytes or type(expected_raw) is not str):
            raise TrainLsvBuffError("INVALID_DELETE_CAPABILITY")
        with _settings_lock:
            try:
                raw,lines,_,begin,end=self._section._read()
            except TrainLsvSettingsError as exc:
                raise TrainLsvBuffError("UNSAFE_BUFF_SETTINGS") from exc
            if raw!=expected_bytes:
                raise TrainLsvBuffError("STALE_BUFF_SETTINGS")
            rows=self._rows(lines,begin,end)
            matches=[(pos,val) for pos,n,_,val in rows if n==number]
            if len(matches)!=1 or matches[0][1]!=expected_raw:
                raise TrainLsvBuffError("BUFF_SESSION_ROW_CHANGED")
            del lines[matches[0][0]]
            self._write(raw,"".join(lines).encode("utf-8"))
            return self.load()

    def _write(self,raw: bytes,new: bytes):
        if len(new)>MAX_SETTINGS_BYTES:
            raise TrainLsvBuffError("BUFF_SETTINGS_TOO_LARGE")
        if new==raw:return
        self.path.parent.mkdir(parents=True,exist_ok=True)
        fd,tmp=tempfile.mkstemp(prefix="settings.",suffix=".tmp",
                                dir=str(self.path.parent))
        try:
            with os.fdopen(fd,"wb") as h:
                h.write(new)
                h.flush()
                os.fsync(h.fileno())
            current=self.path.read_bytes() if self.path.exists() else b""
            if current!=raw:
                raise TrainLsvBuffError("BUFF_SETTINGS_CHANGED_CONCURRENTLY")
            if self.path.exists():
                backup=self.path.with_name(
                    "settings."+datetime.now().strftime("%Y%m%d")+".ini")
                if not backup.exists():
                    shutil.copy2(self.path,backup)
            os.replace(tmp,self.path)
        except OSError as exc:
            raise TrainLsvBuffError("BUFF_SETTINGS_WRITE_FAILED") from exc
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
