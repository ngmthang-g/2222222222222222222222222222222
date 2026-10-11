"""S150: read-only manual ORIGINAL C12 hide/show coordinate observation.

This is an evidence collector, NOT a reconstructed TLM UI feature. It never
moves, hides, foregrounds, or sends input to any HWND, and does not run TLM.
The user manually clicks the ORIGINAL TLM's Ẩn hết / Hiện hết buttons.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from start_windows import NativeWin32Backend, discover_game_windows
from layout_windows import NativeLayoutBackend

ORIGINAL_EXE_SHA256 = "15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22"
HIDE_ORIGIN = (-2200, -2200)
MAX_OBSERVED = 25


@dataclass(frozen=True)
class RectSample:
    hwnd: int
    pid: int
    left: int
    top: int
    right: int
    bottom: int

    @property
    def size(self) -> tuple[int, int]:
        return self.right - self.left, self.bottom - self.top

    @property
    def origin(self) -> tuple[int, int]:
        return self.left, self.top


def verify_frozen_original(path: Path) -> bool:
    """Hash FILE supplied by user; this alone does not attest a live process."""
    if not path.is_file():
        return False
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    except OSError:
        return False
    return digest.hexdigest() == ORIGINAL_EXE_SHA256


def capture_game_rects(window_backend, rect_backend) -> tuple[RectSample, ...]:
    """Read verified game HWND+PID identities; no WM_CLOSE / SetWindowPos.

    Read before and after GetWindowRect; any stale/recycled HWND or malformed
    rectangle makes the phase fail closed. No title, credentials or role names
    are copied into the diagnostic report.
    """
    windows = discover_game_windows(window_backend)
    if not 1 <= len(windows) <= MAX_OBSERVED:
        raise ValueError("NO_UNAMBIGUOUS_GAME_WINDOW_SET")
    samples = []
    for game in windows:
        if (not window_backend.is_window(game.hwnd)
                or not window_backend.is_visible(game.hwnd)
                or window_backend.process_id(game.hwnd) != game.pid):
            raise ValueError("STALE_WINDOW_BEFORE_RECT")
        rect = tuple(rect_backend.window_rect(game.hwnd))
        if len(rect) != 4 or any(type(v) is not int for v in rect):
            raise ValueError("MALFORMED_NATIVE_RECT")
        sample = RectSample(game.hwnd, game.pid, *rect)
        if min(sample.size) <= 0:
            raise ValueError("INVALID_WINDOW_SIZE")
        if (not window_backend.is_window(game.hwnd)
                or window_backend.process_id(game.hwnd) != game.pid
                or not window_backend.is_visible(game.hwnd)):
            raise ValueError("STALE_WINDOW_AFTER_RECT")
        samples.append(sample)
    if len({(s.hwnd, s.pid) for s in samples}) != len(samples):
        raise ValueError("REPEATED_WINDOW_IDENTITY")
    return tuple(sorted(samples, key=lambda x: (x.hwnd, x.pid)))


def classify_c12(before: tuple[RectSample, ...],
                 hidden: tuple[RectSample, ...],
                 shown: tuple[RectSample, ...]) -> str:
    """Classify OBSERVED coordinates, never assert original source branch.

    If every original window was already at (0,0), restoring old coordinates
    and moving to origin are observationally indistinguishable.
    """
    if not before or not hidden or not shown:
        return "INCONCLUSIVE_EMPTY_PHASE"
    identities = [tuple((r.hwnd, r.pid) for r in group)
                  for group in (before, hidden, shown)]
    if any(len(set(keys)) != len(keys) for keys in identities):
        return "INCONCLUSIVE_DUPLICATE_IDENTITY"
    if identities[0] != identities[1] or identities[0] != identities[2]:
        return "INCONCLUSIVE_WINDOW_SET_CHANGED"
    if any(x.size != y.size or x.size != z.size
           for x, y, z in zip(before, hidden, shown)):
        return "INCONCLUSIVE_SIZE_CHANGED"
    if not all(item.origin == HIDE_ORIGIN for item in hidden):
        return "INCONCLUSIVE_HIDE_NOT_OBSERVED"
    if all(item.origin == (0, 0) for item in shown):
        if all(item.origin == (0, 0) for item in before):
            return "INCONCLUSIVE_ZERO_EQUALS_OLD_POSITION"
        return "OBSERVED_SHOW_DOCUMENTED_ZERO_ORIGIN"
    if all(a.origin == c.origin for a, c in zip(before, shown)):
        return "OBSERVED_RESTORE_OLD_POSITION"
    return "OBSERVED_MIXED_OR_OTHER_POSITION"


def safe_report(before, hidden, shown) -> dict:
    return {
        "source": "S150_MANUAL_THREE_PHASE_WINDOWS_C12_OBSERVATION",
        "original_binary_hash_proven": True,
        "original_running_process_identity_proven": False,
        "user_manual_actions_required": True,
        "game_memory_accessed": False,
        "game_input_sent": False,
        "coordinates_classification": classify_c12(before, hidden, shown),
        "phases": {
            "before": [asdict(s) for s in before],
            "hidden": [asdict(s) for s in hidden],
            "shown": [asdict(s) for s in shown],
        },
        "not_source_level_control_flow_proof": True,
        "not_game_product_verification": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only original TLM C12 observer; manual clicks only")
    parser.add_argument("--original-exe", type=Path, required=True,
                        help="Path to the hash-locked ORIGINAL TLMTool.dist/TLMTool.exe")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "artifacts" / "s150" / "c12_observation.json")
    args = parser.parse_args()
    if sys.platform != "win32" or not verify_frozen_original(args.original_exe):
        print("BLOCKED_NOT_WINDOWS_OR_FROZEN_EXE_NOT_VERIFIED")
        return 2
    try:
        backend = NativeWin32Backend()
        rectangles = NativeLayoutBackend()
        input("Open original TLM + games, arrange them at NONZERO positions; Enter to capture BEFORE: ")
        before = capture_game_rects(backend, rectangles)
        if all(item.origin == (0, 0) for item in before):
            print("BLOCKED_ALL_INITIAL_POSITIONS_ZERO_AMBIGUOUS")
            return 2
        input("Click ORIGINAL 'Ẩn hết', then Enter to capture HIDDEN: ")
        hidden = capture_game_rects(backend, rectangles)
        input("Click ORIGINAL 'Hiện hết', then Enter to capture SHOWN: ")
        shown = capture_game_rects(backend, rectangles)
        result = safe_report(before, hidden, shown)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(result["coordinates_classification"])
        print("Observation JSON:", args.output)
        print("Manually observed geometry; full original source branch still requires corroboration.")
        return 0 if result["coordinates_classification"].startswith("OBSERVED_") else 2
    except (OSError, ValueError, EOFError) as exc:
        # Sanitized only; never emit window titles, account fields or paths.
        print("INCONCLUSIVE_OR_CANCELLED:", type(exc).__name__)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
