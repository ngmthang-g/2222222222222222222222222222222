"""S184 original J04/J05/J06/J11 local Phó Bản groups/schedule settings.

Original section/key: [Settings]/phoban_groups JSON groups with num,
members (up to six), schedule [{enabled, activity, name, times}].
Preserves old phoban_group1/phoban_schedule byte-for-byte. Their migration
precedence is not instruction-recovered; refuse unsafe legacy-only writes.
Does NOT claim genuine character, dungeon execution or leader identity.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

from farm_town_config import _KEYLINE
from settings_store import _settings_lock, settings_path
from train_saved_coordinates import FarmCoordinatesStore, FarmCoordinateError, MAX_SETTINGS_BYTES, _HEADER

PHOBAN_NAMES = (
    "Tô Châu  - Thủy Lao",
    "Tô Châu 1 - Tống Liêu",
    "Tô Châu 2 - Trúc Lâm",
    "Tô Châu 3 - Dã Ngoại",
    "Lâu Lan 1 - Hoàng Kim",
    "Lâu Lan 2 - Huyền Phật Châu",
    "Lâu Lan 3 - Dung Nham",
    "Sát Tinh - Thử nghiệm",
)
TRAIN_NAMES = ("Về train theo thiết lập sẵn",)
ACTIVITIES = ("Phó bản", "Train")
CFG_SECTION = "Settings"
CFG_KEY = "phoban_groups"
LEGACY_KEYS = ("phoban_group1", "phoban_schedule")
_KEYPREFIX = re.compile(
    r"^[ \t]*(phoban_groups|phoban_group1|phoban_schedule)\b", re.I)


class PhoBanConfigError(ValueError):
    """Refuse uncertain original data/migrations instead of discarding it."""


@dataclass(frozen=True)
class PhoBanSchedule:
    enabled: bool = True
    activity: str | None = None
    name: str | None = None
    times: int | str = 1

    def validated(self):
        if type(self.enabled) is not bool:
            raise PhoBanConfigError("INVALID_SCHEDULE_ENABLED")
        if self.activity is not None and self.activity not in ACTIVITIES:
            raise PhoBanConfigError("UNKNOWN_SCHEDULE_ACTIVITY")
        if self.name is not None and type(self.name) is not str:
            raise PhoBanConfigError("INVALID_SCHEDULE_NAME")
        if self.activity is None and self.name:
            raise PhoBanConfigError("SCHEDULE_NAME_WITHOUT_ACTIVITY")
        if self.activity == "Phó bản" and self.name is not None and self.name not in PHOBAN_NAMES:
            raise PhoBanConfigError("UNKNOWN_DUNGEON_NAME")
        if self.activity == "Train" and self.name is not None and self.name not in TRAIN_NAMES:
            raise PhoBanConfigError("UNKNOWN_TRAIN_NAME")
        raw = self.times
        if (type(raw) not in (str, int) or type(raw) is bool
                or not str(raw).isascii() or not str(raw).isdecimal()
                or not 1 <= len(str(raw)) <= 9 or int(raw) < 1):
            raise PhoBanConfigError("INVALID_SCHEDULE_TIMES")
        return self

    def change(self, *, field: str, value):
        if field not in ("enabled", "activity", "name", "times"):
            raise PhoBanConfigError("UNSUPPORTED_SCHEDULE_FIELD")
        if field == "activity":
            if value not in ACTIVITIES and value is not None:
                raise PhoBanConfigError("INVALID_NEW_SCHEDULE_ACTIVITY")
            valid_names = PHOBAN_NAMES if value == "Phó bản" else (
                TRAIN_NAMES if value == "Train" else ())
            return replace(self, activity=value,
                           name=self.name if self.name in valid_names else None).validated()
        return replace(self, **{field: value}).validated()


@dataclass(frozen=True)
class PhoBanGroup:
    num: int
    members: tuple[str, ...] = ()
    schedule: tuple[PhoBanSchedule, ...] = ()

    def validated(self):
        if (type(self.num) is not int or self.num < 1
                or type(self.members) is not tuple or len(self.members) > 6
                or any(type(v) is not str for v in self.members)
                or type(self.schedule) is not tuple):
            raise PhoBanConfigError("INVALID_DUNGEON_GROUP")
        for row in self.schedule:
            if type(row) is not PhoBanSchedule:
                raise PhoBanConfigError("INVALID_DUNGEON_SCHEDULE")
            row.validated()
        return self


@dataclass(frozen=True)
class PhoBanConfig:
    groups: tuple[PhoBanGroup, ...] = (PhoBanGroup(1, ("",)*6),)

    def validated(self):
        if type(self.groups) is not tuple:
            raise PhoBanConfigError("INVALID_DUNGEON_GROUP_COLLECTION")
        for i, g in enumerate(self.groups, 1):
            if type(g) is not PhoBanGroup or g.num != i:
                raise PhoBanConfigError("INVALID_DUNGEON_GROUP_ORDER")
            g.validated()
        return self

    def add_group(self):
        return PhoBanConfig(self.groups + (
            PhoBanGroup(len(self.groups)+1, ("",)*6),)).validated()

    def delete_group(self, idx: int):
        if type(idx) is not int or not 0 <= idx < len(self.groups):
            raise PhoBanConfigError("UNKNOWN_DUNGEON_GROUP")
        return PhoBanConfig(tuple(replace(g, num=i) for i,g in enumerate(
            (g for j,g in enumerate(self.groups) if j != idx), 1))).validated()

    def add_schedule(self, group: int):
        if type(group) is not int or not 0 <= group < len(self.groups):
            raise PhoBanConfigError("UNKNOWN_DUNGEON_GROUP")
        updated = list(self.groups)
        old = updated[group]
        updated[group] = replace(old, schedule=old.schedule + (PhoBanSchedule(),))
        return PhoBanConfig(tuple(updated)).validated()

    def delete_schedule(self, group: int, row: int):
        if (type(group) is not int or not 0 <= group < len(self.groups)
                or type(row) is not int or not 0 <= row < len(self.groups[group].schedule)):
            raise PhoBanConfigError("UNKNOWN_SCHEDULE_ROW")
        updated = list(self.groups)
        g = updated[group]
        updated[group] = replace(g, schedule=g.schedule[:row]+g.schedule[row+1:])
        return PhoBanConfig(tuple(updated)).validated()

    def edit_schedule(self, group: int, row: int, field: str, value):
        if (type(group) is not int or not 0 <= group < len(self.groups)
                or type(row) is not int or not 0 <= row < len(self.groups[group].schedule)):
            raise PhoBanConfigError("UNKNOWN_SCHEDULE_ROW")
        new = list(self.groups)
        g = new[group]
        sched = list(g.schedule)
        sched[row] = sched[row].change(field=field, value=value)
        new[group] = replace(g, schedule=tuple(sched))
        return PhoBanConfig(tuple(new)).validated()

    def json_payload(self):
        self.validated()
        return [
            {"num": g.num, "members": list(g.members),
             "schedule": [
                {"enabled": r.enabled, "activity": r.activity, "name": r.name,
                 "times": r.times} for r in g.schedule
             ]}
            for g in self.groups
        ]


@dataclass(frozen=True)
class PhoBanConfigSnapshot:
    config: PhoBanConfig
    file_bytes: bytes
    legacy_only: bool = False


class PhoBanConfigStore:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path is not None else settings_path()

    def _read(self):
        try:
            raw, lines, nl = FarmCoordinatesStore(self.path)._lines()
        except (FarmCoordinateError, OSError) as exc:
            raise PhoBanConfigError("UNSAFE_PHOBAN_SETTINGS") from exc
        headings = []
        for i, line in enumerate(lines):
            m = _HEADER.fullmatch(line.rstrip("\r\n"))
            if m:
                headings.append((i, m.group(1).strip().casefold()))
        settings = [i for i, n in headings if n=="settings"]
        if len(settings) > 1:
            raise PhoBanConfigError("DUPLICATE_SETTINGS_SECTION")
        begin = settings[0] if settings else None
        end = (next((i for i,_ in headings if i>begin),len(lines))
               if begin is not None else len(lines))
        found = {}
        if begin is not None:
            for i in range(begin+1,end):
                if not _KEYPREFIX.match(lines[i]):
                    continue
                m = _KEYLINE.fullmatch(lines[i])
                if m is None:
                    raise PhoBanConfigError("MALFORMED_PHOBAN_KEY")
                key = m.group(2).casefold()
                if key not in (CFG_KEY, *LEGACY_KEYS) or key in found:
                    raise PhoBanConfigError("DUPLICATE_OR_UNKNOWN_PHOBAN_KEY")
                if i+1<end and lines[i+1][:1] in (" ","\t"):
                    raise PhoBanConfigError("AMBIGUOUS_PHOBAN_CONTINUATION")
                found[key]=(i,m.group(4).strip())
        return raw,lines,nl,begin,end,found

    @staticmethod
    def _decode(groups_json):
        try:
            arr=json.loads(groups_json)
        except (ValueError, TypeError) as exc:
            raise PhoBanConfigError("MALFORMED_PHOBAN_GROUPS_JSON") from exc
        if type(arr) is not list:
            raise PhoBanConfigError("INVALID_GROUPS_JSON_SHAPE")
        groups=[]
        for n,item in enumerate(arr,1):
            if (type(item) is not dict or type(item.get("members")) is not list
                    or type(item.get("schedule")) is not list):
                raise PhoBanConfigError("INVALID_PHOBAN_GROUP_PAYLOAD")
            members=tuple(item["members"])
            rows=[]
            for row in item["schedule"]:
                if type(row) is not dict:
                    raise PhoBanConfigError("INVALID_PHOBAN_SCHEDULE_PAYLOAD")
                rows.append(PhoBanSchedule(
                    enabled=row.get("enabled",True),
                    activity=row.get("activity"),
                    name=row.get("name"),
                    times=row.get("times",1)))
            groups.append(PhoBanGroup(n,members,tuple(rows)))
        return PhoBanConfig(tuple(groups)).validated()

    def load(self):
        with _settings_lock:
            raw,_lines,_nl,_begin,_end,found=self._read()
            legacy_only=(CFG_KEY not in found and
                         any(k in found for k in LEGACY_KEYS))
            config=(self._decode(found[CFG_KEY][1]) if CFG_KEY in found
                    else PhoBanConfig())
            return PhoBanConfigSnapshot(config,raw,legacy_only)

    def save(self, config: PhoBanConfig, *, expected_bytes: bytes):
        if type(config) is not PhoBanConfig or type(expected_bytes) is not bytes:
            raise PhoBanConfigError("INVALID_PHOBAN_SAVE_REQUEST")
        config.validated()
        with _settings_lock:
            raw, lines, nl, begin, end, found=self._read()
            if raw != expected_bytes:
                raise PhoBanConfigError("STALE_PHOBAN_SETTINGS")
            if CFG_KEY not in found and any(k in found for k in LEGACY_KEYS):
                raise PhoBanConfigError("LEGACY_ONLY_PHOBAN_MIGRATION_UNKNOWN")
            # Reject malformed current file before any rewrite.
            if CFG_KEY in found:
                self._decode(found[CFG_KEY][1])
            data=json.dumps(config.json_payload(),ensure_ascii=False)
            updated=list(lines)
            if CFG_KEY in found:
                pos,_=found[CFG_KEY]
                match=_KEYLINE.fullmatch(lines[pos])
                updated[pos]=(match.group(1)+match.group(2)
                              +match.group(3)+data+(match.group(5) or ""))
            elif begin is None:
                prefix="" if not updated or updated[-1].endswith(("\r","\n")) else nl
                updated.append(prefix+"[Settings]"+nl+CFG_KEY+" = "+data+nl)
            else:
                if end>0 and not updated[end-1].endswith(("\r","\n")):
                    raise PhoBanConfigError("UNTERMINATED_SETTINGS_SECTION")
                updated.insert(end, CFG_KEY+" = "+data+nl)
            encoded="".join(updated).encode("utf-8")
            if encoded == raw:
                return PhoBanConfigSnapshot(config,raw,False)
            if len(encoded)>MAX_SETTINGS_BYTES:
                raise PhoBanConfigError("PHOBAN_SETTINGS_TOO_LARGE")
            self.path.parent.mkdir(parents=True,exist_ok=True)
            fd,temp=tempfile.mkstemp(prefix="settings.",suffix=".tmp",dir=str(self.path.parent))
            try:
                with os.fdopen(fd,"wb") as stream:
                    stream.write(encoded)
                    stream.flush()
                    os.fsync(stream.fileno())
                actual=self.path.read_bytes() if self.path.exists() else b""
                if actual != raw:
                    raise PhoBanConfigError("PHOBAN_SETTINGS_CHANGED")
                if self.path.exists():
                    backup=self.path.with_name(
                        "settings."+datetime.now().strftime("%Y%m%d")+".ini")
                    if not backup.exists():
                        shutil.copy2(self.path,backup)
                os.replace(temp,self.path)
            except OSError as exc:
                raise PhoBanConfigError("PHOBAN_SETTINGS_WRITE_FAILED") from exc
            finally:
                if os.path.exists(temp):
                    os.unlink(temp)
            return PhoBanConfigSnapshot(config,encoded,False)
