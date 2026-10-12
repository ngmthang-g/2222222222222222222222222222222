"""Stage M05: exact four-slot Rao assignment INI backend (NOT live account UI).

Source: docs/rao/M05_ACCOUNT_ASSIGNMENT_FLOW.md.
Only acc_<real sanitized RoleName> = JSON list of four names is supported.
No HWND/PID fallback may become a persistent key, and this module is NOT
wired into an account-row UI until a genuine game RoleName reader exists.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re

from settings_store import _settings_lock
from rao_definition_config import (
    RaoConfigError, RaoDefinitionStore, _VALID_NAME,
)

_TAGS = re.compile(r"<[^>]+>")
_ACC_START = re.compile(r"^[ \t]*acc_", re.I)
_ACC_LINE = re.compile(
    r"^([ \t]*)(acc_([^=:\r\n]*?))([ \t]*[=:][ \t]*)([^\r\n]*)(\r?\n)?$",
    re.I,
)
RAO_SLOTS = 4


class RaoAssignmentError(RaoConfigError):
    """Reject ambiguous identity, malformed account JSON and stale writes."""


def real_character_key(role_name: str) -> str:
    """M05 persisted key is RoleName only, never Window/HWND/PID fallback.

    Caller must obtain its source via a genuine independently attested
    game-character adapter. The string itself does NOT authenticate a player.
    """
    if type(role_name) is not str:
        raise RaoAssignmentError("VERIFIED_ROLE_NAME_REQUIRED")
    cleaned = _TAGS.sub("", role_name).strip()
    if (not cleaned or cleaned.startswith("Window ")
            or _VALID_NAME.fullmatch(cleaned) is None
            or cleaned.startswith(("#", ";"))):
        raise RaoAssignmentError("INVALID_OR_TEMPORARY_ROLE_NAME")
    return cleaned


@dataclass(frozen=True)
class RaoAssignmentSnapshot:
    role_name: str
    selected: tuple[str, str, str, str]
    file_bytes: bytes
    has_saved_record: bool


class RaoAccountAssignmentStore:
    """M05 safe inactive persistence capability for later REAL role reader.

    Never persist from an HWND title or from a test-owned synthetic RoleName.
    Current production UI has no caller and cannot create assignments.
    """

    def __init__(self, path: str | Path):
        self.store = RaoDefinitionStore(path)
        self.path = self.store.path

    @staticmethod
    def _entries(lines, begin, end):
        found = []
        if begin is None:
            return tuple(found)
        seen = set()
        for pos in range(begin + 1, end):
            line = lines[pos]
            if not _ACC_START.match(line):
                continue
            match = _ACC_LINE.fullmatch(line)
            if match is None:
                raise RaoAssignmentError("INVALID_RAO_ACCOUNT_LINE")
            if pos + 1 < end and lines[pos + 1][:1] in (" ", "\t"):
                raise RaoAssignmentError("AMBIGUOUS_RAO_ACCOUNT_CONTINUATION")
            name = match.group(3).strip()
            if not name or name.casefold() in seen:
                raise RaoAssignmentError("DUPLICATE_RAO_ACCOUNT_KEY")
            seen.add(name.casefold())
            found.append((pos, name, match.group(5), match))
        return tuple(found)

    def load(self, verified_role_name: str) -> RaoAssignmentSnapshot:
        # The adjective in this interface describes a responsibility of its
        # future game-side caller; the name string alone is not proof.
        name = real_character_key(verified_role_name)
        with _settings_lock:
            file_bytes, lines, _, begin, end = self.store._read()
            records = self._entries(lines, begin, end)
            matches = [r for r in records if r[1] == name]
            if len(matches) > 1:
                raise RaoAssignmentError("AMBIGUOUS_RAO_CHARACTER")
            definitions = self.store._definitions(lines, begin, end)
            available = {r.name for _, r in definitions}
            if not matches:
                return RaoAssignmentSnapshot(name, ("", "", "", ""),
                                             file_bytes, False)
            try:
                value = json.loads(matches[0][2])
            except (json.JSONDecodeError, ValueError) as exc:
                raise RaoAssignmentError("INVALID_RAO_ACCOUNT_JSON") from exc
            if (type(value) is not list or len(value) != RAO_SLOTS
                    or any(type(item) is not str for item in value)):
                raise RaoAssignmentError("RAO_ACCOUNT_EXPECTS_FOUR_NAMES")
            # M05: stale/renamed/deleted definitions are not restored active.
            selected = tuple(item if item in available else "" for item in value)
            return RaoAssignmentSnapshot(name, selected, file_bytes, True)

    def save(self, verified_role_name: str, selected: tuple[str, str, str, str],
             *, expected_bytes: bytes) -> RaoAssignmentSnapshot:
        name = real_character_key(verified_role_name)
        if (type(selected) not in (list, tuple) or len(selected) != RAO_SLOTS
                or any(type(item) is not str for item in selected)
                or type(expected_bytes) is not bytes):
            raise RaoAssignmentError("INVALID_FOUR_SLOT_RAO_ASSIGNMENT")
        slots = tuple(selected)
        with _settings_lock:
            raw, lines, nl, begin, end = self.store._read()
            if raw != expected_bytes:
                raise RaoAssignmentError("STALE_RAO_ACCOUNT_SETTINGS")
            definitions = self.store._definitions(lines, begin, end)
            names = {row.name for _, row in definitions}
            if any(value and value not in names for value in slots):
                raise RaoAssignmentError("MISSING_REFERENCED_RAO_DEFINITION")
            old = self._entries(lines, begin, end)
            matches = [(pos, match) for pos, record_name, _value, match in old
                       if record_name == name]
            if len(matches) > 1:
                raise RaoAssignmentError("AMBIGUOUS_RAO_CHARACTER")
            encoded_slots = json.dumps(list(slots), ensure_ascii=False)
            if matches:
                position, match = matches[0]
                # Preserve the preexisting acc_<RoleName> spelling/separator.
                lines[position] = (match.group(1) + match.group(2)
                                   + match.group(4) + encoded_slots
                                   + (match.group(6) or ""))
            else:
                record = f"acc_{name} = {encoded_slots}{nl}"
                if begin is None:
                    prefix = ("" if not lines or lines[-1].endswith(("\r", "\n"))
                              else nl)
                    lines.append(prefix + "[Rao]" + nl + record)
                else:
                    if end and not lines[end-1].endswith(("\r", "\n")):
                        raise RaoAssignmentError("UNTERMINATED_RAO_SECTION")
                    lines.insert(end, record)
            output = "".join(lines).encode("utf-8")
            self.store._atomic_write(raw, output)
            return RaoAssignmentSnapshot(name, slots, output, True)
