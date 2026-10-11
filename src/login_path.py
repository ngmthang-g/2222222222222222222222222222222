"""S25: F04 game folder recognition and E05 settings persistence only.

The original executable name contains TWO spaces between Long and Mobile.
The exact F04 path revalidation micro-order and save timing are UNKNOWN.
No game launch, login, captcha, injection, Proxy or entitlement logic here.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import re
import shutil
import tempfile
from datetime import datetime

from settings_store import read_settings, settings_path, _settings_lock

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



# S141: F04-owned write must not normalize F02 legacy Accounts values.
# E05 confirms atomic settings.ini replacement and dated backup. The exact
# original ConfigParser formatting microsequence is UNKNOWN, so preserve
# all non-target bytes and fail closed rather than rewrite unknown tokens.
_MAX_SETTINGS_BYTES = 2 * 1024 * 1024
_SECTION_LINE = re.compile(r"^\\[([^\\]\\r\\n]+)\\][ \\t]*$")
_GAME_KEY_LINE = re.compile(r"^(game_dir)([ \\t]*[=:][ \\t]*)([^\\r\\n]*)$", re.IGNORECASE)


def _updated_game_dir_bytes(raw: bytes, value: str) -> bytes:
    """Edit ONLY an unambiguous [Settings].game_dir line or add that key.

    This is an S141 byte-preservation safety refinement, not a claim that
    the compiled original preserves identical spacing on every write.
    Never deserialize/re-emit check/captcha/Proxy/password account tokens.
    """
    if (type(value) is not str or not value or
            any(c in value for c in ("\\r", "\\n", "\\x00"))):
        raise ValueError("INVALID_GAME_DIR_VALUE")
    if len(raw) > _MAX_SETTINGS_BYTES or b"\\x00" in raw:
        raise ValueError("AMBIGUOUS_GAME_DIR_SETTINGS")
    try:
        body = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise ValueError("UNREADABLE_GAME_DIR_SETTINGS") from None
    if body.startswith("\\ufeff") or ("\\r" in body.replace("\\r\\n", "")):
        raise ValueError("AMBIGUOUS_GAME_DIR_SETTINGS")
    newline = "\\r\\n" if "\\r\\n" in body else "\\n"
    lines = body.splitlines(keepends=True)
    sections = []
    for index, line in enumerate(lines):
        clean = line.rstrip("\\r\\n")
        found = _SECTION_LINE.fullmatch(clean)
        if found:
            sections.append((index, found.group(1).strip().casefold()))
        elif clean.lstrip().startswith("[") and "]" in clean:
            # Accepting an unknown section delimiter can insert a key
            # into the wrong original section: never risk user credentials.
            raise ValueError("AMBIGUOUS_GAME_DIR_SETTINGS")
    targets = [index for index, name in sections if name == "settings"]
    if len(targets) != 1:
        if targets or body.strip():
            raise ValueError("AMBIGUOUS_GAME_DIR_SETTINGS")
        return ("[Settings]" + newline + "game_dir = " + value + newline).encode("utf-8")
    start = targets[0]
    end = next((i for i, _name in sections if i > start), len(lines))
    key_lines = []
    for index in range(start + 1, end):
        line = lines[index].rstrip("\\r\\n")
        # Indented key-looking lines may be legacy Accounts continuations.
        if re.match(r"^[ \\t]+game_dir\\b", line, re.IGNORECASE):
            raise ValueError("AMBIGUOUS_GAME_DIR_SETTINGS")
        if re.match(r"^game_dir\\b", line, re.IGNORECASE):
            match = _GAME_KEY_LINE.fullmatch(line)
            if match is None:
                raise ValueError("AMBIGUOUS_GAME_DIR_SETTINGS")
            key_lines.append((index, match))
    if len(key_lines) > 1:
        raise ValueError("AMBIGUOUS_GAME_DIR_SETTINGS")
    if key_lines:
        index, match = key_lines[0]
        old_line = lines[index]
        terminator = ("\\r\\n" if old_line.endswith("\\r\\n")
                      else "\\n" if old_line.endswith("\\n") else "")
        lines[index] = match.group(1) + match.group(2) + value + terminator
    else:
        if end and not lines[end - 1].endswith(("\\r", "\\n")):
            lines[end - 1] += newline
        lines.insert(end, "game_dir = " + value + newline)
    return "".join(lines).encode("utf-8")


def _save_only_game_dir(path: Path, value: str) -> str:
    """E05 shared lock + dated backup + atomic bytes; no account rewrite."""
    with _settings_lock:
        try:
            existing = path.is_file()
            before = path.read_bytes() if existing else b""
            original_stat = path.stat() if existing else None
        except OSError:
            raise ValueError("UNREADABLE_GAME_DIR_SETTINGS") from None
        rewritten = _updated_game_dir_bytes(before, value)
        if rewritten == before:
            return "UNCHANGED"
        if len(rewritten) > _MAX_SETTINGS_BYTES:
            raise ValueError("AMBIGUOUS_GAME_DIR_SETTINGS")
        fd = None
        temp_name = None
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            fd, temp_name = tempfile.mkstemp(prefix="settings.", suffix=".tmp",
                                             dir=str(path.parent))
            with os.fdopen(fd, "wb") as out:
                fd = None
                out.write(rewritten)
                out.flush()
                os.fsync(out.fileno())
            # Refuse a concurrent external file mutation instead of
            # overwriting unrelated persisted Login/Farm edits.
            current = path.stat() if path.is_file() else None
            if (current is None) != (original_stat is None) or (
                current is not None and original_stat is not None and
                (current.st_size, current.st_mtime_ns, current.st_ino) !=
                (original_stat.st_size, original_stat.st_mtime_ns, original_stat.st_ino)
            ):
                raise ValueError("STALE_GAME_DIR_SETTINGS")
            if original_stat is not None:
                backup = path.with_name("settings."+
                    datetime.now().strftime("%Y%m%d")+".ini")
                if not backup.exists():
                    shutil.copy2(path, backup)
            os.replace(temp_name, path)
            temp_name = None
        except OSError:
            raise ValueError("GAME_DIR_WRITE_FAILED") from None
        finally:
            if fd is not None:
                os.close(fd)
            if temp_name is not None and os.path.exists(temp_name):
                os.unlink(temp_name)
        return "UPDATED_ONLY_GAME_DIR"

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
        # F04 save instant UNKNOWN: S25 local policy saves on successful choice.
        # S141 keeps the original other INI bytes EXACTLY, including legacy
        # F02 account continuation lines with unknown checkbox/captcha tokens.
        target = self.settings_file if self.settings_file is not None else settings_path()
        _save_only_game_dir(target, str(result.directory))

    @staticmethod
    def get_exe_path(result: GameDirectoryResult) -> Path | None:
        """Do not return stale executables after files are removed."""
        return result.executable if isinstance(result, GameDirectoryResult) else None
