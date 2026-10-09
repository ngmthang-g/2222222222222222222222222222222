"""S25: F04 game folder recognition and E05 settings persistence only.

The original executable name contains TWO spaces between Long and Mobile.
The exact F04 path revalidation micro-order and save timing are UNKNOWN.
No game launch, login, captcha, injection, Proxy or entitlement logic here.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Union

from settings_store import read_settings, write_settings

EXE_NAME = "Thần Long  Mobile.exe"
GAME_DIR_KEY = "game_dir"
SETTINGS_SECTION = "Settings"
PICKER_TITLE = "Chọn thư mục chứa Thần Long Mobile"
INVALID_TITLE = "Thư mục game không hợp lệ"
EXAMPLE_PATH = r"D:\ThanLongMobile_PC\Game"


@dataclass(frozen=True)
class GameDirectoryResult:
    directory: Path | None
    note: str

    @property
    def executable(self) -> Path | None:
        if self.directory is None:
            return None
        exe = self.directory / EXE_NAME
        return exe if exe.is_file() else None


def resolve_game_dir(selected: str | Path | None) -> GameDirectoryResult:
    """F04 bounded resolver. Never recursive-scan arbitrary parent trees.

    Deterministic 1-child scan is an explicit S25 local ordering choice:
    case-insensitive 'game' names first, then lexicographic names.
    """
    if selected is None:
        return GameDirectoryResult(None, "thư mục không tồn tại")
    raw = str(selected).strip()
    if not raw:
        return GameDirectoryResult(None, "thư mục không tồn tại")
    # F04 names rstrip('/\\'); preserve filesystem root correctly.
    path = Path(raw)
    if not path.is_dir():
        return GameDirectoryResult(None, "thư mục không tồn tại")
    if (path / EXE_NAME).is_file():
        return GameDirectoryResult(path, "")
    game = path / "Game"
    if (game / EXE_NAME).is_file():
        return GameDirectoryResult(game, "tự nhận diện thư mục Game bên trong")
    # F04: a selection like Game/<game>_Data should step UP to Game.
    # A parent containing the canonical exe is the only accepted match.
    parent = path.parent
    if parent != path and (parent / EXE_NAME).is_file():
        return GameDirectoryResult(parent, "tự lùi về thư mục cha chứa game")
    try:
        children = sorted(
            (child for child in path.iterdir() if child.is_dir()),
            key=lambda child: ("game" not in child.name.casefold(),
                               child.name.casefold(), child.name),
        )
        for child in children:
            if (child / EXE_NAME).is_file():
                return GameDirectoryResult(child, "tự nhận diện thư mục con " + child.name)
    except OSError:
        return GameDirectoryResult(None, "không thể đọc thư mục đã chọn")
    return GameDirectoryResult(None, "không tìm thấy " + EXE_NAME + " trong thư mục đã chọn")


class GameDirectoryStore:
    """Save only F04-owned Settings.game_dir, using existing E05 atomic writer."""

    def __init__(self, settings_file: str | Path | None = None):
        self.settings_file = Path(settings_file) if settings_file is not None else None

    def load(self) -> GameDirectoryResult:
        parser = read_settings(self.settings_file)
        stored = parser.get(SETTINGS_SECTION, GAME_DIR_KEY, fallback="").strip()
        return (resolve_game_dir(stored)
                if stored else GameDirectoryResult(None, ""))

    def save(self, result: GameDirectoryResult) -> None:
        if not isinstance(result, GameDirectoryResult) or result.executable is None:
            raise ValueError("Cannot persist unverified game executable")
        parser = read_settings(self.settings_file)
        if not parser.has_section(SETTINGS_SECTION):
            parser.add_section(SETTINGS_SECTION)
        parser.set(SETTINGS_SECTION, GAME_DIR_KEY, str(result.directory))
        # F04 save instant UNKNOWN: S25 local policy saves on successful choice.
        write_settings(parser, self.settings_file)

    @staticmethod
    def get_exe_path(result: GameDirectoryResult) -> Path | None:
        """Do not return stale executables after files are removed."""
        return result.executable if isinstance(result, GameDirectoryResult) else None
