"""S202 original F06 PrintWindow reference-file boundary for independent Login.

F06 original executable proves pixel labels login.login1/login.login2,
login.vaoTroChoi, common.active and optional login.update, plus background
PrintWindow check. It does NOT provide actual RGB/coordinate samples in
source-backed current repo. Never guess samples, infer login readiness
from HWND title, or send credentials/clicks on an incomplete template.

This imports real S145 native PrintWindow+single-frame comparison. The
user/operator must supply a strict, explicit, version-bound reference
file during final Windows acceptance. Merely loading this file or matching
a screen does not authorize sending a password or mark a character online.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path

from login_frozen_client_fingerprint import (
    FROZEN_GAMEASSEMBLY_SHA256, FROZEN_METADATA_SHA256,
    inspect_installed_frozen_client,
)
from login_printwindow_pixels import (
    RgbSample, LoginPixelResult, MAX_POINTS_PER_REFERENCE,
    observe_login_screen,
)
from start_windows import GameWindow, NativeWin32Backend
from start_polling import WindowSnapshot

F06_REFERENCE_SCHEMA = "TLM_F06_CLIENT_PIXELS_V1"
ORIGINAL_WINDOW_WIDTH = 1366
ORIGINAL_WINDOW_HEIGHT = 768
MAX_REFERENCE_JSON_BYTES = 65536
REQUIRED_F06_REFERENCES = (
    "login.login1", "login.login2",
    "login.vaoTroChoi", "common.active",
)
OPTIONAL_F06_REFERENCES = ("login.update",)
ALL_F06_REFERENCES = frozenset(
    REQUIRED_F06_REFERENCES + OPTIONAL_F06_REFERENCES)


@dataclass(frozen=True)
class OriginalF06PixelReferences:
    status: str
    selected_executable: Path | None = None
    samples: tuple[tuple[str, tuple[RgbSample, ...]], ...] = ()
    login_credentials_authorized: bool = False
    original_game_login_confirmed: bool = False

    def reference(self, name: str) -> tuple[RgbSample, ...]:
        return next((points for key, points in self.samples if key == name), ())

    @property
    def complete_readonly_evidence(self) -> bool:
        return (self.status == "F06_EXPLICIT_4_STAGE_REFERENCE_LOADED"
                and all(self.reference(key) for key in REQUIRED_F06_REFERENCES))


@dataclass(frozen=True)
class OriginalF06FormPreflight:
    code: str
    hwnd: int | None = None
    pid: int | None = None
    read_only_form_observed: bool = False
    login_credentials_sent: bool = False
    account_online: bool = False


def _reject_duplicate_json_keys(pairs):
    out = {}
    for k, value in pairs:
        if k in out:
            raise ValueError("F06_DUPLICATE_REFERENCE_JSON_KEY")
        out[k] = value
    return out


def _reference_points(items) -> tuple[RgbSample, ...]:
    if (type(items) is not list
            or not 1 <= len(items) <= MAX_POINTS_PER_REFERENCE):
        raise ValueError("F06_REFERENCE_POINT_COUNT_INVALID")
    points = []
    coordinates = set()
    for item in items:
        if type(item) is not dict or set(item) != {"x", "y", "r", "g", "b"}:
            raise ValueError("F06_REFERENCE_POINT_FIELDS_INVALID")
        x, y = item["x"], item["y"]
        channels = (item["r"], item["g"], item["b"])
        if (type(x) is not int or type(y) is not int
                or not 0 <= x < ORIGINAL_WINDOW_WIDTH
                or not 0 <= y < ORIGINAL_WINDOW_HEIGHT
                or any(type(value) is not int or not 0 <= value <= 255
                       for value in channels)
                or (x, y) in coordinates):
            raise ValueError("F06_REFERENCE_POINT_INVALID")
        coordinates.add((x, y))
        points.append(RgbSample(x, y, *channels))
    return tuple(points)


def load_f06_pixel_references(
    file: str | Path, selected_executable: str | Path,
) -> OriginalF06PixelReferences:
    """File/2-SHA256 work MUST run off Tk; no login/browser/game actions."""
    error = lambda code: OriginalF06PixelReferences(code)
    if not isinstance(file, (str, Path)) or not isinstance(
            selected_executable, (str, Path)):
        return error("F06_EXPLICIT_FILE_AND_CLIENT_REQUIRED")
    path, exe = Path(file), Path(selected_executable)
    if (not path.is_file() or path.is_symlink()
            or path.stat().st_size > MAX_REFERENCE_JSON_BYTES):
        return error("F06_REFERENCE_FILE_UNAVAILABLE_OR_UNSAFE")
    try:
        with path.open("rb") as stream:
            data = stream.read(MAX_REFERENCE_JSON_BYTES + 1)
        if not data or len(data) > MAX_REFERENCE_JSON_BYTES:
            return error("F06_REFERENCE_FILE_SIZE_INVALID")
        item = json.loads(
            data.decode("utf-8"), object_pairs_hook=_reject_duplicate_json_keys)
        if type(item) is not dict or set(item) != {
                "format", "gameassembly_sha256", "metadata_sha256",
                "capture_size", "references"}:
            return error("F06_REFERENCE_SCHEMA_INVALID")
        if (item["format"] != F06_REFERENCE_SCHEMA
                or item["gameassembly_sha256"] != FROZEN_GAMEASSEMBLY_SHA256
                or item["metadata_sha256"] != FROZEN_METADATA_SHA256
                or type(item["capture_size"]) is not list
                or item["capture_size"] != [
                    ORIGINAL_WINDOW_WIDTH, ORIGINAL_WINDOW_HEIGHT]):
            return error("F06_REFERENCE_CLIENT_VERSION_OR_GEOMETRY_MISMATCH")
        entries = item["references"]
        if (type(entries) is not dict
                or not set(REQUIRED_F06_REFERENCES).issubset(entries)
                or set(entries) - ALL_F06_REFERENCES):
            return error("F06_MISSING_OR_UNKNOWN_ORIGINAL_REFERENCE")
        samples = tuple(
            (key, _reference_points(entries[key]))
            for key in REQUIRED_F06_REFERENCES + OPTIONAL_F06_REFERENCES
            if key in entries)
        # Verify installed F04 client *after* validating file structure,
        # never attach a running game based on self-asserted JSON hashes.
        if not inspect_installed_frozen_client(exe).known_static_files:
            return error("F06_SELECTED_GAME_NOT_FROZEN_CLIENT")
        return OriginalF06PixelReferences(
            "F06_EXPLICIT_4_STAGE_REFERENCE_LOADED", exe, samples)
    except (OSError, UnicodeError, ValueError, TypeError, KeyError):
        return error("F06_REFERENCE_FILE_UNREADABLE_OR_INVALID")


def observe_f06_original_login_form(
    window: GameWindow,
    snapshot: WindowSnapshot,
    bundle: OriginalF06PixelReferences,
    *,
    backend=None, provider=None, allowed=lambda: False,
) -> OriginalF06FormPreflight:
    """One READ-ONLY full-frame capture of both original login form refs.

    Critical: even a positive match is a SCREEN OBSERVATION, not license to
    type credentials. F06 native click point transform and actual login
    success must be independently verified in final owner acceptance.
    """
    if type(window) is not GameWindow:
        return OriginalF06FormPreflight("F06_INVALID_TARGET_WINDOW")
    def result(code, matched=False):
        return OriginalF06FormPreflight(
            code, window.hwnd, window.pid, matched)
    if (type(bundle) is not OriginalF06PixelReferences
            or not bundle.complete_readonly_evidence
            or bundle.selected_executable is None):
        return result("F06_EXPLICIT_ORIGINAL_REFERENCES_REQUIRED")
    if (type(snapshot) is not WindowSnapshot or not snapshot.valid
            or window not in snapshot.windows
            or not snapshot.windows):
        return result("F06_CURRENT_NATIVE_START_CACHE_REQUIRED")
    if not callable(allowed):
        return result("F06_CANCELLATION_BOUNDARY_REQUIRED")
    try:
        reader = backend if backend is not None else NativeWin32Backend()
        def exact_exe():
            return (reader.is_window(window.hwnd)
                    and reader.process_id(window.hwnd) == window.pid
                    and os.path.normcase(os.path.normpath(
                        reader.process_executable(window.pid))) ==
                    os.path.normcase(os.path.normpath(
                        str(bundle.selected_executable))))
        if not exact_exe():
            return result("F06_GAME_EXE_NOT_SELECTED_FROZEN_CLIENT")
        observed: LoginPixelResult = observe_login_screen(
            window, snapshot=snapshot,
            # Exactly CURRENT real window count, NOT an invented
            # original licensing MAX_LOGIN_WINDOWS.
            max_windows=len(snapshot.windows),
            allowed=lambda: (allowed() is True and exact_exe()),
            references={
                "login.login1": bundle.reference("login.login1"),
                "login.login2": bundle.reference("login.login2"),
            }, backend=reader, provider=provider)
        if not exact_exe() or allowed() is not True:
            return result("F06_TARGET_CHANGED_DURING_CAPTURE")
        return result(
            observed.code,
            observed.code == "BOTH_EXPLICIT_REFERENCES_MATCH_TEST_ONLY")
    except (OSError, TypeError, RuntimeError, ValueError, AttributeError):
        return result("F06_NATIVE_READONLY_FORM_PREFLIGHT_FAILED")
