"""S28: F05/D06 launch *inputs* read-only preflight, not a launcher.

No process creation, injection, loader operation or Proxy development.
F05's exact original Windows-essential environment allowlist is UNKNOWN:
a caller MUST explicitly supply its audited names, never a guessed default.
F05's _make_safe_env documented 'Windows essentials + TLM_PROFILE only'.
D06: only ./data/resources.dat is the current x64 PE DLL payload name.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Mapping, Sequence

from login_launch_preflight import LaunchPreflight

PAYLOAD_RELATIVE = Path("data") / "resources.dat"
MACHINE_AMD64 = 0x8664
PE32_PLUS_MAGIC = 0x20B
IMAGE_FILE_EXECUTABLE_IMAGE = 0x0002
IMAGE_FILE_DLL = 0x2000
MAX_PE_OFFSET = 1024 * 1024
MAX_SECTIONS = 96
FORBIDDEN_PREFIXES = ("PYTHON", "VIRTUAL_ENV", "CONDA", "PIP_", "TLM_PROXY",
                      "PROXY_", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY",
                      "NO_PROXY")


@dataclass(frozen=True)
class PeStructure:
    valid: bool
    reason: str
    machine: int | None = None
    dll: bool = False


def inspect_x64_pe(path: str | Path, *, dll_required: bool) -> PeStructure:
    """Read-only minimal structural PE32+ AMD64 check; NOT loadability/signature.

    Synthetic TEST-only PE headers used by S28 can pass but are not executable
    binaries. Never claim Windows loader compatibility or payload safety.
    """
    if type(dll_required) is not bool:
        return PeStructure(False, "INVALID_EXPECTED_KIND")
    try:
        target = Path(path)
        if not target.is_file():
            return PeStructure(False, "FILE_MISSING")
        with target.open("rb") as stream:
            stream.seek(0, os.SEEK_END)
            length = stream.tell()
            if length < 64:
                return PeStructure(False, "DOS_HEADER_SHORT")
            stream.seek(0)
            dos = stream.read(64)
            if dos[:2] != b"MZ":
                return PeStructure(False, "NOT_MZ")
            offset = int.from_bytes(dos[0x3c:0x40], "little")
            if not 64 <= offset <= MAX_PE_OFFSET or offset + 24 > length:
                return PeStructure(False, "INVALID_PE_OFFSET")
            stream.seek(offset)
            coff = stream.read(24)
            if len(coff) != 24 or coff[:4] != b"PE\0\0":
                return PeStructure(False, "NOT_PE_SIGNATURE")
            machine = int.from_bytes(coff[4:6], "little")
            if machine != MACHINE_AMD64:
                return PeStructure(False, "NOT_AMD64", machine)
            count = int.from_bytes(coff[6:8], "little")
            opt_size = int.from_bytes(coff[20:22], "little")
            chars = int.from_bytes(coff[22:24], "little")
            dll = bool(chars & IMAGE_FILE_DLL)
            if dll != dll_required:
                return PeStructure(False, "PE_KIND_MISMATCH", machine, dll)
            if not chars & IMAGE_FILE_EXECUTABLE_IMAGE:
                return PeStructure(False, "NOT_EXECUTABLE_IMAGE", machine, dll)
            if not 1 <= count <= MAX_SECTIONS or opt_size < 112:
                return PeStructure(False, "INVALID_HEADER_SIZES", machine, dll)
            if offset + 24 + opt_size + count * 40 > length:
                return PeStructure(False, "SECTION_HEADERS_TRUNCATED", machine, dll)
            optional = stream.read(opt_size)
            if (len(optional) != opt_size or
                    int.from_bytes(optional[:2], "little") != PE32_PLUS_MAGIC):
                return PeStructure(False, "NOT_PE32_PLUS", machine, dll)
            image_size = int.from_bytes(optional[56:60], "little")
            header_size = int.from_bytes(optional[60:64], "little")
            if image_size == 0 or header_size == 0 or header_size > length:
                return PeStructure(False, "INVALID_IMAGE_SIZES", machine, dll)
            sections = stream.read(count * 40)
            if len(sections) != count * 40:
                return PeStructure(False, "SECTION_HEADERS_TRUNCATED", machine, dll)
            for i in range(count):
                section = sections[i*40:(i+1)*40]
                raw_size = int.from_bytes(section[16:20], "little")
                raw_off = int.from_bytes(section[20:24], "little")
                if raw_size and (raw_off < header_size or raw_off + raw_size > length):
                    return PeStructure(False, "SECTION_RAW_TRUNCATED", machine, dll)
            return PeStructure(True, "STRUCTURAL_PE32_PLUS_AMD64_ONLY", machine, dll)
    except (OSError, ValueError, TypeError):
        return PeStructure(False, "FILE_UNREADABLE")


def build_audited_windows_env(
    *, profile_index: int,
    source_env: Mapping[str, str],
    essential_keys: Sequence[str],
) -> dict[str, str]:
    """Original F05 shape without guessing the original essential-key list.

    An explicitly supplied allowlist is obligatory (caller's audit decision).
    Key match is case-insensitive as on Windows; collision is fail-closed.
    Every Python/virtualenv and Proxy key is excluded even if requested.
    S28 local guard requires SystemRoot. NOT evidence original used this list.
    """
    if type(profile_index) is not int or not 1 <= profile_index <= 5:
        raise ValueError("Explicit F05 profile index must be 1..5")
    if not isinstance(source_env, Mapping) or isinstance(source_env, (str, bytes)):
        raise ValueError("Source environment must be a mapping")
    if not isinstance(essential_keys, (tuple, list)) or not essential_keys:
        raise ValueError("Explicit audited essential keys are required")
    entries: dict[str, tuple[str, str]] = {}
    for key, value in source_env.items():
        if (type(key) is not str or not key or "=" in key or "\0" in key
                or type(value) is not str or "\0" in value):
            raise ValueError("Malformed environment entry")
        folded = key.casefold()
        if folded in entries:
            raise ValueError("Case-colliding Windows environment keys")
        entries[folded] = (key, value)
    allowed: dict[str, str] = {}
    seen: set[str] = set()
    for key in essential_keys:
        if type(key) is not str or not key or "=" in key or "\0" in key:
            raise ValueError("Invalid essential environment key")
        folded = key.casefold()
        if folded in seen or folded == "tlm_profile":
            raise ValueError("Duplicate/reserved essential environment key")
        seen.add(folded)
        if folded.startswith(tuple(x.casefold() for x in FORBIDDEN_PREFIXES)):
            raise ValueError("Python/Proxy variables cannot be essentials")
        if folded not in entries:
            raise ValueError("Missing explicitly named Windows essential variable")
        native_key, value = entries[folded]
        allowed[native_key] = value
    if "systemroot" not in seen:
        raise ValueError("S28 local Windows safety policy requires SystemRoot")
    allowed["TLM_PROFILE"] = str(profile_index)
    return allowed


@dataclass(frozen=True)
class LaunchInputResult:
    prepared: bool
    reason: str
    executable: Path | None = None
    payload: Path | None = None
    environment: dict[str, str] | None = None
    game_pe: PeStructure | None = None
    payload_pe: PeStructure | None = None


def prepare_launch_inputs(
    preflight: LaunchPreflight,
    *,
    package_root: str | Path,
    profile_index: int,
    source_env: Mapping[str, str],
    essential_keys: Sequence[str],
) -> LaunchInputResult:
    """An offline input validator only; cannot authorize or perform launch.

    Caller must re-run live F05 permission/limit guard at actual spawn time.
    The actual frozen location and cwd expression are not known; package_root
    is supplied explicitly, and no cwd is returned or invented.
    """
    if (type(preflight) is not LaunchPreflight or not preflight.allowed
            or preflight.reason != "PREFLIGHT_ONLY_NOT_LAUNCHED"
            or preflight.executable is None):
        return LaunchInputResult(False, "LAUNCH_PREFLIGHT_DENIED")
    executable = Path(preflight.executable)
    game_pe = inspect_x64_pe(executable, dll_required=False)
    if not game_pe.valid:
        return LaunchInputResult(False, "GAME_" + game_pe.reason, game_pe=game_pe)
    root = Path(package_root)
    if not root.is_dir():
        return LaunchInputResult(False, "PACKAGE_ROOT_MISSING", game_pe=game_pe)
    payload = root / PAYLOAD_RELATIVE
    dll_pe = inspect_x64_pe(payload, dll_required=True)
    if not dll_pe.valid:
        return LaunchInputResult(False, "PAYLOAD_" + dll_pe.reason,
                                 game_pe=game_pe, payload_pe=dll_pe)
    try:
        env = build_audited_windows_env(
            profile_index=profile_index, source_env=source_env,
            essential_keys=essential_keys)
    except ValueError:
        return LaunchInputResult(False, "ESSENTIAL_ENVIRONMENT_UNVERIFIED",
                                 game_pe=game_pe, payload_pe=dll_pe)
    return LaunchInputResult(True, "STRUCTURAL_INPUTS_ONLY_NOT_LAUNCHED",
                             executable, payload, env, game_pe, dll_pe)
