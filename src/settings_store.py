"""Real minimal shared settings.ini persistence, from E05 verified contract.

Backup retention/sanitization micro-rules are UNKNOWN in original source.
S01 deliberately does not prune existing backup files.
"""
from __future__ import annotations

import configparser
import os
import shutil
import tempfile
from datetime import datetime
import threading
from pathlib import Path

_settings_lock = threading.RLock()  # compatibility choice, not original lock-type proof


def settings_path(appdata: str | None = None) -> Path:
    base = appdata if appdata is not None else os.environ.get('APPDATA')
    if not base:
        raise RuntimeError('APPDATA unavailable; original Windows settings path cannot be resolved')
    return Path(base) / 'TLMTool' / 'settings.ini'


def new_parser() -> configparser.RawConfigParser:
    return configparser.RawConfigParser(strict=False)


def read_settings(path: str | Path | None = None) -> configparser.RawConfigParser:
    target = Path(path) if path is not None else settings_path()
    parser = new_parser()
    with _settings_lock:
        if target.is_file():
            with target.open('r', encoding='utf-8') as stream:
                parser.read_file(stream)
    return parser


def write_settings(parser: configparser.RawConfigParser, path: str | Path | None = None) -> None:
    """E05 dated prior-settings backup + atomic replace; retention deferred."""
    target = Path(path) if path is not None else settings_path()
    with _settings_lock:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_file():
            # E05 proves settings.YYYYMMDD.ini backups, but numeric retention
            # is unknown. Never delete historical backups in S01.
            dated = target.with_name('settings.' + datetime.now().strftime('%Y%m%d') + '.ini')
            if not dated.exists():
                shutil.copy2(target, dated)
        fd, name = tempfile.mkstemp(prefix='settings.', suffix='.tmp', dir=str(target.parent))
        try:
            with os.fdopen(fd,'w',encoding='utf-8') as out:
                parser.write(out)
                out.flush()
                os.fsync(out.fileno())
            os.replace(name, target)
        finally:
            if os.path.exists(name):
                os.unlink(name)
