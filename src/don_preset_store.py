"""S183 L05 original-backed [DonVang] saved coordinates, no game sender.

coord_<n> = preset_name|map_id|x|y; map IDs from the already frozen
Farm EXE map registry (never client guesses). Existing receiver/acc config
is preserved byte-for-byte. Rename/delete of a *referenced* preset refuses
rather than orphaning an account with no authenticated RoleName reader.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import os
import re
import shutil
import tempfile

from don_return_settings import DonReturnSettingsStore, DonReturnSettingsError
from farm_original_maps import FARM_MAP_ID_TO_NAME
from farm_town_config import _KEYLINE
from settings_store import _settings_lock
from train_saved_coordinates import FarmCoordinate, MAX_SETTINGS_BYTES

_COORD_KEY_PREFIX = re.compile(r"^[ \t]*coord_", re.I)
_COORD_KEY = re.compile(r"^coord_([0-9]+)$", re.I)
_REF_KEY = re.compile(r"^(?:acc_.+_farm|recv_coord|recv_[0-9]+_coord)$", re.I)


class DonPresetError(ValueError):
    """Never erase damaged/unknown/externally updated Dồn coordinates."""


@dataclass(frozen=True)
class DonPresetSnapshot:
    rows: tuple[FarmCoordinate, ...]
    file_bytes: bytes
    row_numbers: tuple[int, ...]
    referenced_names: frozenset[str]
    skipped_retired_map_ids: tuple[int, ...] = ()


def next_don_preset_name(rows) -> str:
    """Original L05 generated name uses smallest unused 'Tọa độ N'."""
    used = {r.name for r in rows}
    number = 1
    while f"Tọa độ {number}" in used:
        number += 1
    return f"Tọa độ {number}"


def resolve_don_target(name: str, presets):
    """Pure original L05 name -> (MapID, X, Y); NEVER move characters."""
    if type(name) is not str or not name:
        return None
    don_builtin = {
        "Dồn Lạc Dương": (3, 247, 93),
        "Dồn Đại Lý": (2, 258, 124),
        "Dồn Tô Châu": (4, 416, 239),
        "Dồn Lâu Lan": (5, 249, 275),
    }
    sell_builtin = {
        "Đại Lý": (2, 103, 188),
        "Lạc Dương": (3, 231, 219),
        "Tô Châu": (4, 191, 257),
        "Lâu Lan": (5, 37, 126),
    }
    if name in don_builtin:
        return don_builtin[name]
    if name.startswith("Bán ") and name[4:] in sell_builtin:
        name = name[4:]
    if name in sell_builtin:
        return sell_builtin[name]
    matches = [r for r in presets if r.name == name]
    if len(matches) != 1 or matches[0].map_id not in FARM_MAP_ID_TO_NAME:
        return None
    row = matches[0]
    try:
        return (row.map_id, int(row.x), int(row.y))
    except (ValueError, TypeError):
        return None


def _validate_rows(rows):
    if not isinstance(rows, (tuple, list)):
        raise DonPresetError("INVALID_PRESET_COLLECTION")
    names = set()
    for row in rows:
        if type(row) is not FarmCoordinate:
            raise DonPresetError("INVALID_DON_PRESET_ROW")
        if (type(row.name) is not str or not row.name
                or row.name != row.name.strip()
                or row.name.casefold() in names
                or row.name in ("Đại Lý", "Lạc Dương", "Tô Châu", "Lâu Lan")
                or row.name.startswith("Dồn ")
                or type(row.map_id) is not int
                or row.map_id not in FARM_MAP_ID_TO_NAME
                or any(type(z) is not str or not z
                       or "|" in z or "\r" in z or "\n" in z
                       for z in (row.name, row.x, row.y))):
            raise DonPresetError("INVALID_DON_PRESET_VALUE")
        names.add(row.name.casefold())
    return tuple(rows)


class DonPresetStore:
    """Safe isolated [DonVang] coordinate-family editor, never Farm coord_N."""

    def __init__(self, path: str | Path):
        self.section = DonReturnSettingsStore(path)
        self.path = self.section.path

    @staticmethod
    def _scan(lines, begin, end):
        saved = []
        reserved = set()
        refs = set()
        if begin is None:
            return saved, refs
        for i in range(begin + 1, end):
            line = lines[i]
            parsed = _KEYLINE.fullmatch(line)
            if _COORD_KEY_PREFIX.match(line):
                if parsed is None:
                    raise DonPresetError("MALFORMED_DON_PRESET_KEY")
                key = parsed.group(2)
                match = _COORD_KEY.fullmatch(key)
                if match is None or int(match.group(1)) < 1:
                    raise DonPresetError("INVALID_DON_PRESET_INDEX")
                index = int(match.group(1))
                if index in reserved:
                    raise DonPresetError("DUPLICATE_DON_PRESET_INDEX")
                if i + 1 < end and lines[i + 1][:1] in (" ", "\t"):
                    raise DonPresetError("AMBIGUOUS_DON_PRESET_CONTINUATION")
                reserved.add(index)
                fields = parsed.group(4).strip().split("|")
                if (len(fields) != 4 or not fields[1].isascii()
                        or not fields[1].isdecimal()):
                    raise DonPresetError("MALFORMED_DON_PRESET_VALUE")
                saved.append((i, index, FarmCoordinate(
                    fields[0], int(fields[1]), fields[2], fields[3])))
            elif parsed is not None and _REF_KEY.fullmatch(parsed.group(2)):
                if i + 1 < end and lines[i + 1][:1] in (" ", "\t"):
                    raise DonPresetError("AMBIGUOUS_DON_REFERENCE_CONTINUATION")
                ref = parsed.group(4).strip()
                if ref:
                    refs.add(ref)
        return sorted(saved, key=lambda t: t[1]), refs

    def _from_current(self):
        try:
            raw, lines, nl, begin, end = self.section._read()
        except DonReturnSettingsError as exc:
            raise DonPresetError("UNSAFE_DON_SETTINGS") from exc
        saved, refs = self._scan(lines, begin, end)
        rows = tuple(row for _, _, row in saved)
        # Unknown/retired MapIDs remain on disk but edit must fail closed.
        retired = tuple(row.map_id for row in rows
                        if row.map_id not in FARM_MAP_ID_TO_NAME)
        names = [x.name.casefold() for x in rows]
        if len(set(names)) != len(names):
            raise DonPresetError("DUPLICATE_DON_PRESET_NAME")
        for row in rows:
            if row.map_id in FARM_MAP_ID_TO_NAME:
                _validate_rows((row,))
        return (DonPresetSnapshot(rows, raw,
                                  tuple(num for _, num, _ in saved),
                                  frozenset(refs), retired),
                lines, nl, begin, end, saved)

    def load(self) -> DonPresetSnapshot:
        with _settings_lock:
            return self._from_current()[0]

    def save(self, rows, *, expected_bytes: bytes) -> DonPresetSnapshot:
        requested = _validate_rows(rows)
        if type(expected_bytes) is not bytes:
            raise DonPresetError("INVALID_EXPECTED_SETTINGS_BYTES")
        with _settings_lock:
            before, lines, nl, begin, end, saved = self._from_current()
            if before.file_bytes != expected_bytes:
                raise DonPresetError("STALE_DON_PRESET_SETTINGS")
            if before.skipped_retired_map_ids:
                raise DonPresetError("DON_PRESET_RETIRED_MAP_NOT_WRITABLE")
            existing = {r.name for r in before.rows}
            incoming = {r.name for r in requested}
            # Rename and delete of a referenced name cannot be silently
            # propagated to an unauthenticated account or legacy receiver.
            if any(n in before.referenced_names for n in existing - incoming):
                raise DonPresetError("REFERENCED_DON_PRESET_CANNOT_REMOVE")
            inserts = [
                f"coord_{i} = {r.name}|{r.map_id}|{r.x}|{r.y}{nl}"
                for i, r in enumerate(requested, 1)
            ]
            positions = {i for i, _, _ in saved}
            insertion = min(positions) if positions else end
            if begin is None:
                prefix = ("" if not lines or lines[-1].endswith(("\n", "\r"))
                          else nl)
                updated = "".join(lines) + prefix
                if requested:
                    updated += "[DonVang]" + nl + "".join(inserts)
            else:
                if (inserts and insertion > 0
                        and not lines[insertion - 1].endswith(("\r", "\n"))):
                    raise DonPresetError("UNTERMINATED_DON_SECTION")
                revised = []
                for i, line in enumerate(lines):
                    if i == insertion:
                        revised.extend(inserts)
                    if i not in positions:
                        revised.append(line)
                if insertion == len(lines):
                    revised.extend(inserts)
                updated = "".join(revised)
            encoded = updated.encode("utf-8")
            if encoded == before.file_bytes:
                return before
            if len(encoded) > MAX_SETTINGS_BYTES:
                raise DonPresetError("DON_SETTINGS_TOO_LARGE")
            self.path.parent.mkdir(parents=True, exist_ok=True)
            fd, temp = tempfile.mkstemp(
                prefix="settings.", suffix=".tmp", dir=str(self.path.parent))
            try:
                with os.fdopen(fd, "wb") as stream:
                    stream.write(encoded)
                    stream.flush()
                    os.fsync(stream.fileno())
                current = self.path.read_bytes() if self.path.exists() else b""
                if current != before.file_bytes:
                    raise DonPresetError("DON_PRESET_SETTINGS_CHANGED")
                if self.path.exists():
                    backup = self.path.with_name(
                        "settings." + datetime.now().strftime("%Y%m%d") + ".ini")
                    if not backup.exists():
                        shutil.copy2(self.path, backup)
                os.replace(temp, self.path)
            except OSError as exc:
                raise DonPresetError("DON_PRESET_WRITE_FAILED") from exc
            finally:
                if os.path.exists(temp):
                    os.unlink(temp)
            return self._from_current()[0]
