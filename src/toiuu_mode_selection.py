"""S186 N05: REAL source-backed Tối ưu selection-only session model.

Original N05: Không = skip, Thấp vừa = medium, Cực thấp = low,
Cực đại = max; 1/2/3 are native TLMP codes but SELECTION NEVER SENDS.
No INI writer is invented: original toiuu_cfg_<RoleName> section and
collision/late-name storage precedence are still UNKNOWN.

A roster must be provided by a future independently attested read-only
game character reader; HWND/window title or test-owned string is NOT a
substitute. Until then all account mode selections remain absent.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import re


MODE_NAMES = ("Không", "Thấp vừa", "Cực thấp", "Cực đại")
MODE_ORDER = ("medium", "low", "max")
KEY_TO_LABEL = {
    None: "Không",
    "medium": "Thấp vừa",
    "low": "Cực thấp",
    "max": "Cực đại",
}
LABEL_TO_KEY = {name: key for key, name in KEY_TO_LABEL.items()}
MODE_TO_TLMP = {"medium": 1, "low": 2, "max": 3}
_TAGS = re.compile(r"<[^>]+>")


class ToiuuSelectionError(ValueError):
    """Ambiguous runtime roles and invalid selections fail closed."""


def stable_role_name(name: str) -> str:
    """Original tag stripping; rejects HWND/window-title pseudo characters."""
    if type(name) is not str:
        raise ToiuuSelectionError("ROLE_NAME_READER_REQUIRED")
    cleaned = _TAGS.sub("", name).strip()
    if (not cleaned or len(cleaned) > 120
            or cleaned.startswith(("Window ", "HWND ", "PID "))
            or any(ch in cleaned for ch in ("\x00", "\n", "\r", "[", "]", "="))):
        raise ToiuuSelectionError("INVALID_OR_TEMPORARY_ROLE_NAME")
    return cleaned


@dataclass(frozen=True)
class AttestedGameRole:
    """Read-only game identity contract, NOT proof produced by this module.

    Only a future adapter whose source was verified by runtime/live-game
    checks may instantiate these records for a production account list.
    """
    name: str
    hwnd: int
    pid: int
    process_creation_id: int
    snapshot_revision: int

    def validated(self) -> "AttestedGameRole":
        stable_role_name(self.name)
        if any(type(x) is not int or x <= 0 for x in (
                self.hwnd, self.pid, self.process_creation_id,
                self.snapshot_revision)):
            raise ToiuuSelectionError("INVALID_GAME_PROCESS_PROVENANCE")
        return self

    @property
    def identity(self) -> tuple[str, int, int, int]:
        return (stable_role_name(self.name), self.hwnd, self.pid,
                self.process_creation_id)


@dataclass(frozen=True)
class ToiuuAccountSelection:
    role: AttestedGameRole
    mode: str | None = None
    touched: bool = False

    def validated(self):
        self.role.validated()
        if self.mode is not None and self.mode not in MODE_TO_TLMP:
            raise ToiuuSelectionError("UNKNOWN_TOIUU_MODE")
        if type(self.touched) is not bool:
            raise ToiuuSelectionError("INVALID_TOIUU_TOUCH_STATE")
        return self

    @property
    def display_mode(self) -> str:
        return KEY_TO_LABEL[self.mode]


@dataclass(frozen=True)
class ToiuuSelectionState:
    revision: int = 0
    accounts: tuple[ToiuuAccountSelection, ...] = ()

    def validated(self):
        if type(self.revision) is not int or self.revision < 0:
            raise ToiuuSelectionError("INVALID_TOIUU_ROSTER_REVISION")
        if type(self.accounts) is not tuple:
            raise ToiuuSelectionError("INVALID_TOIUU_ROSTER_SHAPE")
        role_names = set()
        live_hwnds = set()
        live_pids = set()
        for record in self.accounts:
            if type(record) is not ToiuuAccountSelection:
                raise ToiuuSelectionError("INVALID_TOIUU_ACCOUNT_RECORD")
            record.validated()
            if record.role.snapshot_revision != self.revision:
                raise ToiuuSelectionError("MISMATCHED_TOIUU_ROSTER_REVISION")
            name = stable_role_name(record.role.name).casefold()
            if (name in role_names or record.role.hwnd in live_hwnds
                    or record.role.pid in live_pids):
                raise ToiuuSelectionError("AMBIGUOUS_GAME_CHARACTER_IDENTITY")
            role_names.add(name)
            live_hwnds.add(record.role.hwnd)
            live_pids.add(record.role.pid)
        return self

    def with_roster(self, observations: tuple[AttestedGameRole, ...], *,
                    revision: int) -> "ToiuuSelectionState":
        """Swap only on newer genuine revision; no HWND reuse inheritance.

        Matching display name but a replaced PID/create-time/HWND starts with
        Không, not stale optimization intent or previous process state.
        """
        if (type(observations) is not tuple or type(revision) is not int
                or revision <= self.revision):
            raise ToiuuSelectionError("STALE_OR_INVALID_TOIUU_ROSTER")
        old = {r.role.identity: r for r in self.accounts}
        result = []
        for role in observations:
            if type(role) is not AttestedGameRole:
                raise ToiuuSelectionError("AUTHENTIC_GAME_ROLE_ADAPTER_REQUIRED")
            role.validated()
            if role.snapshot_revision != revision:
                raise ToiuuSelectionError("STALE_TOIUU_ROLE_OBSERVATION")
            prior = old.get(role.identity)
            result.append(ToiuuAccountSelection(
                role=role, mode=prior.mode if prior else None,
                touched=prior.touched if prior else False))
        return ToiuuSelectionState(revision, tuple(result)).validated()

    def select_all(self, mode: str) -> "ToiuuSelectionState":
        """Three original gray bulk buttons: selection only, NO native send."""
        if mode not in MODE_ORDER or not self.accounts:
            raise ToiuuSelectionError("TOIUU_BULK_MODE_OR_ACCOUNT_UNAVAILABLE")
        return ToiuuSelectionState(
            self.revision,
            tuple(replace(r, mode=mode, touched=True)
                  for r in self.accounts)).validated()

    def select_account(self, identity: tuple[str, int, int, int],
                       mode: str | None) -> "ToiuuSelectionState":
        """Original readonly combobox: Không means skip, NOT TLMP restore."""
        if mode is not None and mode not in MODE_TO_TLMP:
            raise ToiuuSelectionError("INVALID_TOIUU_MODE_SELECTION")
        if (type(identity) is not tuple or len(identity) != 4
                or not any(r.role.identity == identity for r in self.accounts)):
            raise ToiuuSelectionError("TOIUU_ACCOUNT_NOT_IN_CURRENT_ROSTER")
        return ToiuuSelectionState(
            self.revision, tuple(
                replace(r, mode=mode, touched=True)
                if r.role.identity == identity else r
                for r in self.accounts)).validated()

    def clear_roster(self) -> "ToiuuSelectionState":
        """On reader loss, drop all process-affined selection state."""
        return ToiuuSelectionState(self.revision, ())
