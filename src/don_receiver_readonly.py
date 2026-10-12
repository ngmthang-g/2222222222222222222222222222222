"""S183 L05/L06 receiver configuration *inspection only*.

The original has exactly one shared Dồn coordinate and 1..N receiver rows.
Historic recv_coord and per-row recv_<n>_coord migration precedence remains
UNKNOWN. Read/surface conflicts; NEVER write, auto-reconcile or treat saved
character names as currently authenticated in-game roles.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from pathlib import Path

from don_preset_store import DonPresetStore, resolve_don_target
from don_return_settings import DonReturnSettingsStore, DonReturnSettingsError
from farm_town_config import _KEYLINE
from settings_store import _settings_lock

_RECV_KEYS = re.compile(
    r"^(?:recv_count|recv_coord|receiver|recv_([0-9]+)_(?:acc|coord))$", re.I)
_RECV_START = re.compile(r"^[ \t]*(recv_|receiver\b)", re.I)


class DonReceiverConfigError(ValueError):
    pass


@dataclass(frozen=True)
class DonReceiverConfig:
    # These strings come from prior settings.ini, not live RoleName identity.
    saved_receiver_labels: tuple[str, ...]
    candidate_shared_coord: str | None
    migration_conflict: bool
    has_legacy_options: bool
    file_bytes: bytes

    @property
    def resolved_shared_coordinate(self):
        return self.candidate_shared_coord if not self.migration_conflict else None


class DonReceiverConfigReader:
    """Parse known receiver keys without new keys, game actions or mutation."""

    def __init__(self, path: str | Path):
        self.section = DonReturnSettingsStore(path)
        self.presets = DonPresetStore(path)

    def load(self) -> DonReceiverConfig:
        with _settings_lock:
            try:
                raw, lines, _nl, begin, end = self.section._read()
            except DonReturnSettingsError as exc:
                raise DonReceiverConfigError("UNSAFE_RECEIVER_SETTINGS") from exc
            values = {}
            if begin is not None:
                for i in range(begin + 1, end):
                    line = lines[i]
                    if not _RECV_START.match(line):
                        continue
                    hit = _KEYLINE.fullmatch(line)
                    if hit is None:
                        raise DonReceiverConfigError("MALFORMED_RECEIVER_OPTION")
                    key = hit.group(2).casefold()
                    if not _RECV_KEYS.fullmatch(key):
                        continue
                    if key in values:
                        raise DonReceiverConfigError("DUPLICATE_RECEIVER_OPTION")
                    if i + 1 < end and lines[i + 1][:1] in (" ", "\t"):
                        raise DonReceiverConfigError("RECEIVER_OPTION_CONTINUATION")
                    values[key] = hit.group(4).strip()
            count_raw = values.get("recv_count", "")
            if count_raw:
                if not count_raw.isascii() or not count_raw.isdecimal():
                    raise DonReceiverConfigError("INVALID_RECEIVER_COUNT")
                count = int(count_raw)
                if not 1 <= count <= 64:
                    raise DonReceiverConfigError("RECEIVER_COUNT_OUT_OF_BOUNDS")
            else:
                indices = [
                    int(match.group(1))
                    for key in values
                    if (match := re.fullmatch(r"recv_([0-9]+)_acc", key))
                ]
                count = max(indices, default=1)
                if count > 64:
                    raise DonReceiverConfigError("RECEIVER_COUNT_OUT_OF_BOUNDS")
            if any(
                (match := re.fullmatch(r"recv_([0-9]+)_(?:acc|coord)", key))
                and not (1 <= int(match.group(1)) <= count)
                for key in values):
                raise DonReceiverConfigError("RECEIVER_ROW_INDEX_OUT_OF_BOUNDS")
            labels = [values.get(f"recv_{i}_acc", "")
                      for i in range(1, count + 1)]
            if not any(labels) and "receiver" in values:
                labels[0] = values["receiver"]
            candidates = [
                values.get(k, "") for k in ("recv_coord",)
            ]
            candidates.extend(values.get(f"recv_{i}_coord", "")
                              for i in range(1, count + 1))
            names = {x for x in candidates if x}
            conflict = len(names) > 1
            coord = next(iter(names)) if len(names) == 1 else None
            if coord:
                snapshot = self.presets.load()
                # Do not select stale or retired preset name, and do not
                # convert an unknown old location into arbitrary coordinates.
                if resolve_don_target(coord, snapshot.rows) is None:
                    coord = None
            return DonReceiverConfig(
                tuple(labels), coord, conflict,
                any(k in values for k in ("receiver", "recv_coord")),
                raw)
