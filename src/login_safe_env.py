"""S157 F05 — minimally inherited Windows environment, no game launch.

Direct frozen TLMTool.dist/TLMTool.exe evidence (sha256
15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22):
 dll_injector._make_safe_env(tlm_profile: str) -> dict, _SAFE_ENV_KEYS,
 os.environ, TLM_PROFILE; exact documentation:
 "Build minimal env: Windows essentials + TLM_PROFILE only.
  Prevents Python/VirtualEnv vars leaking into game (can break Unity TLS)."

Many essential Windows variable names are present in the same original
.dll_injector serialized-name region near raw offsets 0x291a6b0..0x291a87e.
The exact membership/order of _SAFE_ENV_KEYS is NOT recoverable merely from
that string pool. This code uses a *conservative documented subset of observed
Windows essentials*, not a claimed byte-identical original whitelist.

Proxy environment variables are explicitly OUT OF SCOPE. This function never
creates a process itself, never injects DLL, never grants Info, never reads game
memory or creates a real game launch profile. Windows env names are
case-insensitive, so conflicts fail closed rather than choose a surprising
case variant; the caller-provided profile value is preserved without guessing
the original 1..5 profile conversion rules.
"""
from __future__ import annotations

import os
from collections.abc import Mapping

# Every member appears literally near the original F05 dll_injector
# string/constant region; deliberately excludes TLM_PROXY_* and any
# PYTHON*/VIRTUAL_ENV/CONDA* names even if inherited.
# Membership in the frozen original _SAFE_ENV_KEYS = UNKNOWN.
WINDOWS_ESSENTIAL_CANDIDATES = frozenset({
    "SYSTEMROOT", "WINDIR", "SYSTEMDRIVE", "COMSPEC",
    "PATH", "PATHEXT", "TEMP", "TMP",
    "USERPROFILE", "APPDATA", "LOCALAPPDATA",
    "HOMEDRIVE", "HOMEPATH",
    "PROGRAMFILES", "PROGRAMFILES(X86)", "PROGRAMW6432",
    "COMMONPROGRAMFILES", "COMMONPROGRAMFILES(X86)", "COMMONPROGRAMW6432",
    "PROGRAMDATA", "ALLUSERSPROFILE", "PUBLIC",
    "PROCESSOR_ARCHITECTURE", "PROCESSOR_IDENTIFIER",
    "PROCESSOR_LEVEL", "PROCESSOR_REVISION", "NUMBER_OF_PROCESSORS",
    "COMPUTERNAME", "USERNAME", "USERDOMAIN", "USERDOMAIN_ROAMINGPROFILE",
    "LOGONSERVER", "SESSIONNAME", "PSMODULEPATH",
})
# Explicit block even if a future maintainer changes the candidate set.
BLOCKED_VARIABLE_PREFIXES = ("PYTHON", "VIRTUAL_ENV", "CONDA", "PIP_", "TLM_PROXY")
PROFILE_ENV_KEY = "TLM_PROFILE"


def make_safe_launch_env(
    tlm_profile: str, source_env: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Build F05-shaped Windows child env; does not spawn or authorize anything.

    A STRICTLY LOCAL safer reconstruction policy, not an instruction-exact
    decompile: profile must be a nonblank single-line string <=256 codepoints,
    and caller-supplied env must be unambiguous on case-insensitive Windows.
    """
    if (type(tlm_profile) is not str or not tlm_profile.strip()
            or len(tlm_profile) > 256
            or any(c in tlm_profile for c in ("\0", "\r", "\n", "="))):
        raise ValueError("F05_INVALID_TLM_PROFILE")
    if source_env is None:
        source_env = os.environ
    if not isinstance(source_env, Mapping):
        raise TypeError("F05_ENV_MAPPING_REQUIRED")
    result: dict[str, str] = {}
    seen: set[str] = set()
    for key, value in source_env.items():
        if (type(key) is not str or type(value) is not str
                or not key or "=" in key or "\0" in key or "\0" in value):
            raise ValueError("F05_UNSAFE_SOURCE_ENV")
        normalized = key.upper()
        if normalized in seen:
            raise ValueError("F05_AMBIGUOUS_CASE_INSENSITIVE_ENV")
        seen.add(normalized)
        if (normalized in WINDOWS_ESSENTIAL_CANDIDATES
                and not any(normalized.startswith(prefix)
                            for prefix in BLOCKED_VARIABLE_PREFIXES)):
            result[key] = value
    # Ignore inherited TLM_PROFILE, even when a caller provided a different
    # spelling, and overwrite with caller-selected live per-launch profile.
    result[PROFILE_ENV_KEY] = tlm_profile
    return result
