"""S156 F05 — find the launched game's main HWND by the *actual* PID.

Frozen TLM 2.1.2 F05 find_main_window_by_pid explicitly uses Win32:
EnumWindows, GetWindowThreadProcessId, IsWindowVisible, GetClassNameW,
GetWindowTextW; prefers UnityWndClass or title containing 'Thần Long',
otherwise the first visible top-level HWND belonging to that PID.

Reuse the already real S08 Windows ctypes provider, not a new WinAPI hook.
F05 does not prove a class-vs-title priority when both candidates exist,
or a precise hung-title exception policy. This conservative reconstruction
uses class first, then title; it refuses HWND/PID generations that changed
during inspection, and bounds title messages via the existing S08 provider.

THIS IS READ-ONLY ONE-SCAN SELECTION, NOT game launch/inject, F06 Login,
the F05 25-second stabilization loop, a signed-Info grant or a TLM product.
Never infer an account/RoleName from the HWND title.
"""
from __future__ import annotations

from start_windows import (
    NativeWin32Backend, WindowBackend, UNITY_WINDOW_CLASS, TITLE_TIMEOUT_MS,
)

ORIGINAL_GAME_TITLE_TOKEN = "Thần Long"


def find_main_window_by_pid(
    pid: int, backend: WindowBackend | None = None,
) -> int | None:
    """Select a live visible PID-owned top-level HWND; never an arbitrary one.

    Prefer UnityWndClass or a title containing the original game name.
    Only *after* all preferred candidates are tested does the first verified
    visible fallback window qualify. Caller must independently establish
    that pid belongs to an authorized newly launched game instance.
    """
    if type(pid) is not int or pid <= 0 or pid > 0xFFFFFFFF:
        return None
    if backend is None:
        backend = NativeWin32Backend()
    try:
        hwnds = tuple(backend.enumerate_top_level())
    except (OSError, ValueError, RuntimeError, TypeError):
        return None
    class_preferred: list[int] = []
    title_preferred: list[int] = []
    fallback: list[int] = []
    seen: set[int] = set()
    for candidate in hwnds:
        if type(candidate) is not int or candidate <= 0 or candidate in seen:
            continue
        seen.add(candidate)
        try:
            if (not backend.is_window(candidate)
                    or not backend.is_visible(candidate)
                    or backend.process_id(candidate) != pid):
                continue
            class_name = backend.window_class(candidate)
            # The original F05 uses GetWindowTextW; this safer existing
            # shared S08 adapter bounds potentially unresponsive messages.
            title = backend.title_with_timeout(candidate, TITLE_TIMEOUT_MS)
            if not backend.is_window(candidate) or backend.process_id(candidate) != pid:
                continue  # HWND disappeared / reused while reading the title
            fallback.append(candidate)
            if class_name == UNITY_WINDOW_CLASS:
                class_preferred.append(candidate)
            elif isinstance(title, str) and ORIGINAL_GAME_TITLE_TOKEN.casefold() in title.casefold():
                title_preferred.append(candidate)
        except (OSError, ValueError, RuntimeError, TypeError):
            # Unknown, hung or stale HWND is not an authorized alternative.
            continue

    # Final *live* generation check after full enumeration. A stale
    # preferred HWND must never override a current fallback or title.
    for group in (class_preferred, title_preferred, fallback):
        for hwnd in group:
            try:
                if (backend.is_window(hwnd) and backend.is_visible(hwnd)
                        and backend.process_id(hwnd) == pid):
                    return hwnd
            except (OSError, RuntimeError, ValueError, TypeError):
                continue
    return None

def find_verified_game_window_by_pid(
    pid: int, expected_executable: str,
    backend: WindowBackend | None = None,
) -> int | None:
    """S209 production F05: find actual game window, NEVER PID-owned popup.

    S156's original-compatible finder has a first-visible fallback. That
    works for original inspection, but waiting for a launched Unity game
    must NOT repeatedly try the same unrelated popup until 25s timeout.

    Enumerate ALL actual top-level windows in ONE pass, require exact PID
    and selected game executable, then original S08 game class/title
    predicate. Prefer a unique UnityWndClass, otherwise a unique exact
    original game-title window. Multiple equally credible HWNDs remain
    ambiguous (no invented master window). No mouse, DLL or game commands.
    """
    from pathlib import Path
    import os
    from start_windows import is_game_candidate, GAME_TITLE, _compact

    if (type(pid) is not int or not 0 < pid <= 0xFFFFFFFF
            or not isinstance(expected_executable, (str, Path))
            or not str(expected_executable)):
        return None
    reader = backend if backend is not None else NativeWin32Backend()
    expected = os.path.normcase(os.path.normpath(str(expected_executable)))
    try:
        candidates = tuple(reader.enumerate_top_level())
    except (OSError, RuntimeError, TypeError, ValueError, AttributeError):
        return None
    unity = []
    title_matches = []
    seen = set()
    for hwnd in candidates:
        if type(hwnd) is not int or hwnd <= 0 or hwnd in seen:
            continue
        seen.add(hwnd)
        try:
            if (not reader.is_window(hwnd)
                    or not reader.is_visible(hwnd)
                    or reader.process_id(hwnd) != pid):
                continue
            exe = reader.process_executable(pid)
            if (not isinstance(exe, str) or
                    os.path.normcase(os.path.normpath(exe)) != expected):
                continue
            cls = reader.window_class(hwnd)
            title = reader.title_with_timeout(hwnd, TITLE_TIMEOUT_MS)
            if not is_game_candidate(exe, cls, title):
                continue
            if (not reader.is_window(hwnd)
                    or not reader.is_visible(hwnd)
                    or reader.process_id(hwnd) != pid
                    or os.path.normcase(os.path.normpath(
                        reader.process_executable(pid))) != expected):
                continue
            if cls == UNITY_WINDOW_CLASS:
                unity.append(hwnd)
            elif _compact(title) == _compact(GAME_TITLE):
                title_matches.append(hwnd)
        except (OSError, RuntimeError, TypeError, ValueError, AttributeError):
            continue
    for group in (unity, title_matches):
        if len(group) > 1:
            return None
        if len(group) == 1:
            hwnd = group[0]
            try:
                if (reader.is_window(hwnd)
                        and reader.is_visible(hwnd)
                        and reader.process_id(hwnd) == pid
                        and os.path.normcase(os.path.normpath(
                            reader.process_executable(pid))) == expected):
                    return hwnd
            except (OSError, RuntimeError, TypeError, ValueError, AttributeError):
                return None
            return None
    return None
