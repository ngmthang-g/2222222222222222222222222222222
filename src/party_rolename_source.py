"""S100 G03 original Party display RoleName source boundary, READ-ONLY.

Verified original Party display path:
  utils.get_character_info(hwnd)["RoleName"] -> <[^>]+> tag removal
  -> human display/config name (separate from RoleID and TeamID).
Missing RoleName: original only proves fallback prefix "Window ", NOT suffix.
S90 already owns sanitation, Party roster and Tk rows; DO NOT duplicate them.

This module is a validation adapter for explicitly supplied EXTERNAL/TEST
get_character_info callbacks. It does NOT supply the original game reader,
legitimate signed Info, process-memory access, RoleID, action targets or UI.
No caller-provided synthetic RoleName is authenticated game identity.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from auto_role_provenance import RoleReading
from party_roster import _TAGS, _valid_snapshot, _identity_set
from start_polling import WindowSnapshot


@dataclass(frozen=True)
class PartyRoleNameProbeResult:
    code: str
    revision: int | None = None
    reading: RoleReading | None = None
    normalized_name: str | None = None
    fallback_prefix: str = "Window "
    fallback_suffix_known: bool = False
    source_provenance: str = "EXTERNAL_UNVERIFIED_NOT_GAME"
    action_authorized: bool = False
    # No RoleID/TeamID, no send/click target, no game action.


class PartyRoleNameExternalSource:
    """Fresh Start cache+native HWND/PID fence around external name callback.

    This is a read-only *source boundary*, not the actual original reader.
    Existing S90 roster is the only owner of Party display list and Tk UI.
    """

    def __init__(self, *, start_producer, backend,
                 get_character_info: Callable[[int], object] | None = None):
        self.start_producer = start_producer
        self.backend = backend
        self.get_character_info = get_character_info

    def _generation(self, hwnd: int, pid: int
                    ) -> tuple[str, WindowSnapshot | None]:
        try:
            snap = self.start_producer.read_snapshot()
        except Exception:
            return "START_CACHE_READ_ERROR",None
        if (not _valid_snapshot(snap)
                or type(snap.revision) is not int
                or snap.revision < 0):
            return "INVALID_START_CACHE",None
        if len({w.pid for w in snap.windows}) != len(snap.windows):
            return "DUPLICATE_PID_IN_START_CACHE",None
        if (hwnd,pid) not in _identity_set(snap):
            return "HWND_PID_NOT_IN_START_CACHE",None
        try:
            if (not self.backend.is_window(hwnd)
                    or self.backend.process_id(hwnd) != pid):
                return "STALE_OR_REUSED_NATIVE_HWND_PID",None
        except Exception:
            return "NATIVE_HWND_CHECK_FAILED",None
        return "VALID",snap

    def inspect(self, hwnd: int, pid: int) -> PartyRoleNameProbeResult:
        def blocked(code: str) -> PartyRoleNameProbeResult:
            return PartyRoleNameProbeResult(code)
        if (type(hwnd) is not int or type(pid) is not int
                or hwnd <= 0 or pid <= 0):
            return blocked("INVALID_HWND_PID")
        if (self.backend is None
                or not callable(getattr(self.backend,"is_window",None))
                or not callable(getattr(self.backend,"process_id",None))
                or not callable(getattr(self.start_producer,"read_snapshot",None))):
            return blocked("NATIVE_SOURCE_UNAVAILABLE")
        if not callable(self.get_character_info):
            return blocked("ORIGINAL_CHARACTER_READER_UNAVAILABLE")

        code,initial = self._generation(hwnd,pid)
        if code!="VALID":
            return blocked(code)
        try:
            # Explicitly provided callback, NEVER dynamically imported
            # from the original game or silently synthesized.
            info = self.get_character_info(hwnd)
        except Exception:
            return blocked("EXTERNAL_CHARACTER_READER_ERROR")
        # Re-check PHYSICAL HANDLE/PID + full cached generation, not just
        # the numeric HWND. Delayed workers cannot rename another process.
        code,latest=self._generation(hwnd,pid)
        if code!="VALID":
            return blocked("POST_READ_"+code)
        if (latest.revision != initial.revision
                or _identity_set(latest) != _identity_set(initial)):
            return blocked("STALE_START_REVISION_OR_GENERATION")
        if not isinstance(info, Mapping):
            return blocked("INVALID_CHARACTER_INFO")
        raw=info.get("RoleName")
        if type(raw) is not str:
            return blocked("ROLENAME_UNAVAILABLE")
        # This is the exact G03/S90 regex; S90 remains responsible for
        # consumer normalization and Party ready list behavior.
        normalized=_TAGS.sub("",raw).strip()
        if not normalized:
            return blocked("ROLENAME_EMPTY_AFTER_TAG_REMOVAL")
        return PartyRoleNameProbeResult(
            "EXTERNAL_DISPLAY_NAME_OBSERVED_NOT_GAME",
            revision=initial.revision,
            reading=RoleReading(hwnd,pid,raw),
            normalized_name=normalized)

    def read_role(self, hwnd: int, pid: int) -> RoleReading:
        """Existing S90 optional read_role protocol, no new Party widgets.

        Fail-closed by raising: S90 retains the HWND/PID as an unverified
        physical member but never offers an invented saved account name.
        """
        result=self.inspect(hwnd,pid)
        if result.reading is None:
            raise LookupError(result.code)
        return result.reading
