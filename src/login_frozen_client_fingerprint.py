"""S193: compare a user-installed game client to frozen DATA-2222 evidence.

READ-ONLY: no process attach, no GameAssembly load, no DLL injection,
original TLM license, IPC command, or game automation. Source of these
two hashes: immutable client DATA-2222 CLIENT_MANIFEST.md (GameVersion 126,
Unity metadata v39, Windows x64), not a guessed role memory offset.

Matching file content confirms ONLY the two frozen files, not game-running
version, launcher compatibility, correct game UI, reader/sender protocol,
RoleName, HP, map/party data or gameplay success.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import threading
from queue import Empty, Queue

from game_build_identity import inspect_explicit_game_build
from login_path import EXE_NAME


FROZEN_GAMEASSEMBLY_SHA256 = (
    "4c98c9934bc4260efa64f5492c58e0c5104c89359f0126e7cd402feb381fe3c7"
)
FROZEN_METADATA_SHA256 = (
    "d199498dad7d3139e4c09f6742f4645bfc2a33c465e3d259196931199f6ee6a8"
)
FROZEN_CLIENT_DATA_REF = (
    "ngmthang-g/clinent-game-than-long-DATA-2222/CLIENT_MANIFEST.md"
)


@dataclass(frozen=True)
class FrozenClientMatch:
    code: str
    gameassembly_match: bool = False
    metadata_match: bool = False
    source: str = FROZEN_CLIENT_DATA_REF

    @property
    def compatible_for_runtime_reader(self) -> bool:
        # File-identical does not prove a live game process and its ABI.
        return False

    @property
    def known_static_files(self) -> bool:
        return self.code == "FROZEN_TWO_FILE_SHA256_MATCH"


def inspect_installed_frozen_client(exe_path: str | Path) -> FrozenClientMatch:
    """Fingerprint only local files selected by the user via F04 game dir.

    No recursive search, network, arbitrary DLL loading or memory reads.
    Unlike ordinary version strings, a 2-file SHA256 comparison can
    distinguish the exact frozen research client from unknown builds.
    """
    if not isinstance(exe_path, (str, Path)):
        return FrozenClientMatch("INVALID_SELECTED_EXE")
    exe = Path(exe_path)
    if exe.name != EXE_NAME or exe.is_symlink() or not exe.is_file():
        return FrozenClientMatch("INVALID_SELECTED_EXE")
    base = exe.parent
    dll = base / "GameAssembly.dll"
    metadata = (
        base / (exe.stem + "_Data") / "il2cpp_data"
        / "Metadata" / "global-metadata.dat"
    )
    if not dll.is_file():
        return FrozenClientMatch("INSTALLED_GAMEASSEMBLY_MISSING")
    if not metadata.is_file():
        return FrozenClientMatch("INSTALLED_GLOBAL_METADATA_MISSING")
    if dll.is_symlink() or metadata.is_symlink():
        return FrozenClientMatch("FINGERPRINT_SYMLINK_NOT_ALLOWED")
    result = inspect_explicit_game_build(dll, metadata)
    # Reuse existing S139 change-detection and x64 PE inspection, never
    # untrusted arbitrary external process and never emit real paths.
    if (not result.dll_x64_pe_structure
            or result.candidate_dll is None
            or result.candidate_metadata is None):
        return FrozenClientMatch(
            "INSTALLED_BUILD_UNREADABLE_OR_NOT_X64_" + result.status)
    a = result.candidate_dll.sha256.lower() == FROZEN_GAMEASSEMBLY_SHA256
    b = result.candidate_metadata.sha256.lower() == FROZEN_METADATA_SHA256
    return FrozenClientMatch(
        "FROZEN_TWO_FILE_SHA256_MATCH" if a and b
        else "INSTALLED_CLIENT_DIFFERS_FROM_FROZEN_SNAPSHOT", a, b)


class FrozenClientFingerprintWorker:
    """One read-only hashing worker; notify Tk through bounded mailbox.

    A new request invalidates a prior in-flight result rather than
    mislabelling a changed game folder as an approved known build.
    There is deliberately NO game reader enable/permission side effect.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self._closed = False
        self._serial = 0
        self._worker: threading.Thread | None = None
        self._events: Queue[tuple[int, FrozenClientMatch]] = Queue(maxsize=4)

    @property
    def busy(self) -> bool:
        with self._lock:
            return bool(self._worker is not None
                        and self._worker.is_alive())

    def request(self, exe_path: str | Path) -> bool:
        if not isinstance(exe_path, (str, Path)):
            return False
        with self._lock:
            if (self._closed or
                    (self._worker is not None and self._worker.is_alive())):
                return False
            self._serial += 1
            serial = self._serial
            self._worker = threading.Thread(
                name="TLM-ReadOnly-Frozen-Client-Fingerprint",
                target=self._run, args=(serial, exe_path),
                daemon=True)
            try:
                self._worker.start()
            except RuntimeError:
                self._worker = None
                return False
            return True

    def _run(self, serial, exe):
        try:
            result = inspect_installed_frozen_client(exe)
        except (OSError, ValueError, RuntimeError):
            result = FrozenClientMatch("INSTALLED_CLIENT_FINGERPRINT_FAILED")
        with self._lock:
            if self._closed or serial != self._serial:
                return
            try:
                self._events.put_nowait((serial, result))
            except Exception:
                try:
                    self._events.get_nowait()
                    self._events.put_nowait((serial, result))
                except Empty:
                    pass

    def drain(self) -> tuple[FrozenClientMatch, ...]:
        rows = []
        try:
            while True:
                serial, result = self._events.get_nowait()
                with self._lock:
                    if not self._closed and serial == self._serial:
                        rows.append(result)
        except Empty:
            pass
        return tuple(rows)

    def invalidate(self):
        with self._lock:
            self._serial += 1
        self.drain()

    def shutdown(self):
        with self._lock:
            self._closed = True
            self._serial += 1
