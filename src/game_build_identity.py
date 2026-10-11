"""S139: explicit, read-only identity record for user-supplied game build files.

Original O02 uses GameAssembly.dll to find RoleData; original PE data alone
does not establish which current client build has the same offsets. This
module checks a candidate x64 DLL using the already-tested S28 structural
inspector, optionally fingerprints explicitly supplied Unity metadata,
and reports SHA-256 evidence WITHOUT marking build compatibility.

NEVER opens a game process, loads/executes a DLL, emits tokens, phones home,
chooses a game folder, rewrites binaries or grants any permission.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import hashlib
from pathlib import Path
import sys
from typing import Optional

from login_launch_inputs import inspect_x64_pe

EXPECTED_DLL = "gameassembly.dll"
EXPECTED_METADATA = "global-metadata.dat"
CHUNK_BYTES = 1024 * 1024

@dataclass(frozen=True)
class CandidateFileIdentity:
    name: str
    size: int
    sha256: str

@dataclass(frozen=True)
class GameBuildIdentity:
    status: str
    candidate_dll: Optional[CandidateFileIdentity] = None
    candidate_metadata: Optional[CandidateFileIdentity] = None
    dll_x64_pe_structure: bool = False
    is_authoritatively_known_game_build: bool = False
    signed_info_verified: bool = False
    game_process_attached: bool = False
    original_tlm_pointer_offsets_compatible: bool = False
    real_roledata_read: bool = False
    ready_for_game_actions: bool = False
    confidence: str = "UNATTESTED_CANDIDATE_ONLY"
    # No full filesystem path, PID, token, account or license in output.


def _fingerprint(path: Path, expected_name: str) -> CandidateFileIdentity:
    if not path.is_file() or path.name.casefold() != expected_name:
        raise ValueError("INVALID_CANDIDATE_FILENAME_OR_FILE")
    before = path.stat()
    if before.st_size <= 0:
        raise ValueError("CANDIDATE_FILE_EMPTY")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(CHUNK_BYTES), b""):
            digest.update(block)
    after = path.stat()
    if (before.st_size != after.st_size or
            before.st_mtime_ns != after.st_mtime_ns or
            before.st_ino != after.st_ino):
        raise ValueError("CANDIDATE_CHANGED_DURING_READ")
    return CandidateFileIdentity(expected_name,after.st_size,digest.hexdigest())


def inspect_explicit_game_build(
    gameassembly: str | Path,
    metadata: str | Path | None = None,
) -> GameBuildIdentity:
    """Evidence only; positive structure NEVER authorizes real game offsets.

    The original game version + signed Info + live RoleData remain
    unverified even when the candidate DLL is a syntactically valid x64 PE.
    """
    try:
        dllpath = Path(gameassembly)
        if dllpath.name.casefold() != EXPECTED_DLL:
            return GameBuildIdentity("NOT_EXPLICIT_GAMEASSEMBLY_DLL")
        if not dllpath.is_file():
            return GameBuildIdentity("GAMEASSEMBLY_FILE_UNAVAILABLE")
        candidate = _fingerprint(dllpath, EXPECTED_DLL)
        pe = inspect_x64_pe(dllpath, dll_required=True)
        if not pe.valid:
            return GameBuildIdentity(
                "CANDIDATE_DLL_NOT_VALID_X64_PE_" + pe.reason,
                candidate_dll=candidate)
        if metadata is None:
            return GameBuildIdentity(
                "UNATTESTED_X64_GAMEASSEMBLY_CANDIDATE_METADATA_NOT_SUPPLIED",
                candidate_dll=candidate, dll_x64_pe_structure=True)
        metapath = Path(metadata)
        if metapath.name.casefold() != EXPECTED_METADATA:
            return GameBuildIdentity(
                "METADATA_BASENAME_NOT_VERIFIED",
                candidate_dll=candidate,dll_x64_pe_structure=True)
        if not metapath.is_file():
            return GameBuildIdentity(
                "METADATA_FILE_UNAVAILABLE",
                candidate_dll=candidate,dll_x64_pe_structure=True)
        companion = _fingerprint(metapath,EXPECTED_METADATA)
        # No ungrounded assumption that same folder, exact game version,
        # IL2CPP metadata layout or correct pairing has been established.
        return GameBuildIdentity(
            "UNATTESTED_DLL_AND_METADATA_FINGERPRINTS_ONLY",
            candidate_dll=candidate,candidate_metadata=companion,
            dll_x64_pe_structure=True)
    except (OSError, ValueError, TypeError, OverflowError):
        return GameBuildIdentity("CANDIDATE_FILES_UNREADABLE_OR_CHANGED")


def public_report(result: GameBuildIdentity) -> dict:
    """Structured limited metadata, no paths/process, never auth flags."""
    if type(result) is not GameBuildIdentity:
        raise TypeError("GAME_BUILD_IDENTITY_REQUIRED")
    return asdict(result)
