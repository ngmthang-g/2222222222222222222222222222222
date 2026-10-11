"""S161 E04/F05: count games active inside connected Android emulator VMs.

The frozen original TLM EXE permission_guard at 0x2B83B95–0x2B83CA2
calls emu_reader.emu_game_count(use_cache=...) and documents:
"1 VM co game = 1 cua so"; game process checked with "pidof tung serial".
The original emu_reader also contains the game Android package literal
"com.fgstudio.thanlongmobile" near 0x29359E6. The exact original
ADB/Frida transport, devices enumeration, TTL, timeout and exception branch
cannot be reconstructed from these strings. Not instruction-level parity.

This is an explicitly LOCAL conservative ADB transport: query connected
serials and pidof per serial, count one active game per serial (not per PID).
A missing/unauthorized device, timeout, parse ambiguity or failed command
returns UNKNOWN, never silently a zero usable for extra=1 authorization.
The ORIGINAL's lazy-import error -> 0 (fail-open) is intentionally not
replicated until exact behavior and real license source are proven.

Only query commands are executed: "devices -l" and
"-s SERIAL shell pidof PACKAGE". No tap, shell modification, frida,
inject, game automation, proxy, or license grant. ADB may itself start
its local daemon even on a devices query; this is not zero-side-effect
with respect to adb server state. The user must supply an EXISTING,
explicitly chosen adb executable. No global emulator discovery guessed.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
from typing import Callable, Sequence

from login_launch_preflight import LaunchPreflight
from login_path import GameDirectoryResult
from login_running_process_capacity import (
    ProcessSnapshotBackend, check_native_open_game_capacity,
)
from permission_guard import PermissionSnapshot

ORIGINAL_ANDROID_GAME_PACKAGE = "com.fgstudio.thanlongmobile"
ORIGINAL_EMU_COUNT_METHOD = "emu_reader.emu_game_count"
ORIGINAL_EMU_COUNT_RULE = "ONE_RUNNING_GAME_VM_COUNTS_AS_ONE_WINDOW"
ADB_TRANSPORT_PARITY = "UNKNOWN_ORIGINAL_TRANSPORT_LOCAL_READ_ONLY_ADB"
ADB_QUERY_TIMEOUT_SECONDS = 4
_SERIAL = re.compile(r"[A-Za-z0-9_.:-]{1,128}\Z")


@dataclass(frozen=True)
class EmulatorGameCount:
    code: str
    count: int | None = None
    connected_serials: tuple[str, ...] = ()
    game_serials: tuple[str, ...] = ()


class AdbCommandRunner:
    """CLI adapter; accepts only a real explicit executable path."""

    def __init__(self, adb: str | Path):
        candidate = Path(adb)
        if (not candidate.is_file() or not candidate.is_absolute()
                or candidate.suffix.casefold() != ".exe"):
            raise ValueError("ADB_EXECUTABLE_NOT_VERIFIED")
        self.executable = str(candidate.resolve())

    def __call__(self, args: Sequence[str]) -> tuple[int, str, str]:
        completed = subprocess.run(
            [self.executable, *args], shell=False,
            capture_output=True, text=True, errors="replace",
            stdin=subprocess.DEVNULL, timeout=ADB_QUERY_TIMEOUT_SECONDS,
            check=False, creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0),
        )
        return (completed.returncode, completed.stdout, completed.stderr)


def _device_serials(output: str) -> tuple[str, ...] | None:
    lines = output.replace("\r\n","\n").strip().split("\n")
    if not lines or lines[0].strip() != "List of devices attached":
        return None
    seen: set[str] = set()
    result: list[str] = []
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.strip().split()
        if len(parts) < 2 or _SERIAL.fullmatch(parts[0]) is None:
            return None
        serial, state = parts[0], parts[1]
        # Partial emulator fleets may hide a running game. Fail closed,
        # not count only the subset that happens to be online.
        if state != "device" or serial in seen:
            return None
        seen.add(serial)
        result.append(serial)
    return tuple(result)


def count_adb_emulator_games(
    run: Callable[[Sequence[str]], tuple[int, str, str]] | None,
) -> EmulatorGameCount:
    """Count unique connected Android serials with a running game PID.

    A valid devices listing containing zero devices is a grounded zero
    from a complete ADB response, NOT a guessed fallback after an error.
    """
    if not callable(run):
        return EmulatorGameCount("ADB_PROVIDER_NOT_CONFIGURED")
    try:
        initial = run(("devices","-l"))
        if (type(initial) is not tuple or len(initial)!=3
                or type(initial[0]) is not int or
                any(type(v) is not str for v in initial[1:]) or
                initial[0]!=0 or initial[2].strip()):
            return EmulatorGameCount("ADB_DEVICES_UNVERIFIED")
        serials = _device_serials(initial[1])
        if serials is None:
            return EmulatorGameCount("ADB_FLEET_UNVERIFIED")
        active: list[str] = []
        for serial in serials:
            result = run(("-s",serial,"shell","pidof",ORIGINAL_ANDROID_GAME_PACKAGE))
            if (type(result) is not tuple or len(result)!=3
                    or type(result[0]) is not int or
                    any(type(v) is not str for v in result[1:])):
                return EmulatorGameCount("ADB_PIDOF_UNVERIFIED")
            code, out, err = result
            if err.strip():
                return EmulatorGameCount("ADB_PIDOF_UNVERIFIED")
            values=out.strip().split()
            if code==0 and values and all(v.isdecimal() and int(v)>0 for v in values):
                active.append(serial)
            elif code==1 and not values:
                pass  # tested normal pidof no-match; not a guessed service fallback
            else:
                return EmulatorGameCount("ADB_PIDOF_UNVERIFIED")
        ending=run(("devices","-l"))
        if (type(ending) is not tuple or len(ending)!=3 or
                ending[0]!=0 or type(ending[1]) is not str or
                type(ending[2]) is not str or ending[2].strip() or
                _device_serials(ending[1]) != serials):
            return EmulatorGameCount("ADB_FLEET_CHANGED")
        return EmulatorGameCount("ADB_GAME_PIDOF_CONFIRMED",len(active),
                                 serials,tuple(active))
    except (OSError,ValueError,RuntimeError,TypeError,subprocess.TimeoutExpired):
        return EmulatorGameCount("ADB_READ_FAILED")


def check_open_game_with_adb_process_count(
    snapshot: PermissionSnapshot, game: GameDirectoryResult, *,
    adb_run: Callable[[Sequence[str]], tuple[int,str,str]] | None,
    windows_backend: ProcessSnapshotBackend | None = None,
) -> tuple[LaunchPreflight,EmulatorGameCount]:
    """Bridge to existing S160/S26, no second capacity algorithm.

    A fully authentic signed Info snapshot is STILL required by S26.
    This function does not certify that a returned pidof originates from
    the same original game client version, nor build its process launcher.
    """
    # Run original-verified Info gate BEFORE any ADB subprocess invocation.
    denied, _ = check_native_open_game_capacity(
        snapshot, game, verified_emulator_sessions=None,
        backend=windows_backend)
    if denied.reason != "RUNNING_WINDOW_COUNT_UNKNOWN":
        return denied,EmulatorGameCount("INFO_OR_PLAN_DENIED")
    measured=count_adb_emulator_games(adb_run)
    if measured.code!="ADB_GAME_PIDOF_CONFIRMED" or measured.count is None:
        return denied,measured
    preflight,_=check_native_open_game_capacity(
        snapshot,game,verified_emulator_sessions=measured.count,
        backend=windows_backend)
    return preflight,measured
