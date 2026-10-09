"""S08 actual Windows-only Win32 enumeration smoke: no game launch/injection.

Creates a local Tk test window for a known *real* HWND/PID/title read.
Discovery is read-only and does NOT accept that Python test window as game.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import traceback

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / 'src'))
OUT = BASE / 'artifacts' / 's08'
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT / 'win32_discovery.json'
TEST_TITLE = 'S08 Read-only Win32 Probe'


def run() -> int:
    data = {
        'task': 'S08',
        'status': 'NOT_RUN',
        'platform': os.name,
        'title_timeout_ms': 150,
        'game_exe_executed': False,
        'memory_read': False,
        'game_control': False,
        'proxy': False,
        'production_auth': 'NOT_RUN',
        'exe_build': 'NOT_BUILT',
    }
    root = None
    try:
        if os.name != 'nt':
            data['status'] = 'NOT_RUN_NON_WINDOWS'
            return 1
        import tkinter as tk
        from start_windows import (
            NativeWin32Backend, discover_game_windows, WindowRegistry,
            TITLE_TIMEOUT_MS, GAME_PROCESS,
        )
        root = tk.Tk()
        root.title(TEST_TITLE)
        root.geometry('330x130+30+30')
        root.update_idletasks()
        root.update()

        api = NativeWin32Backend()
        handles = api.enumerate_top_level()
        assert len(handles) > 0, 'EnumWindows returned no real top-level windows'
        visible = [h for h in handles if api.is_window(h) and api.is_visible(h)]
        own = [h for h in visible if api.process_id(h) == os.getpid()]
        assert own, 'No visible real HWND belonging to the test process'
        titled = [h for h in own
                  if api.title_with_timeout(h, TITLE_TIMEOUT_MS) == TEST_TITLE]
        assert titled, 'SendMessageTimeoutW 150ms did not recover the real Tk title'
        hwnd = titled[0]
        own_exe = api.process_executable(os.getpid())
        assert own_exe and own_exe.lower().endswith('.exe'), 'QueryFullProcessImageNameW failed'
        assert api.window_class(hwnd), 'GetClassNameW failed'
        assert not api.window_class(hwnd) == 'UnityWndClass', 'Test Tk window spoofed Unity class'
        windows = discover_game_windows(api)
        registry = WindowRegistry()
        delta = registry.update(windows)
        assert len(delta.added) == len(windows)
        assert all(row.hwnd != hwnd for row in windows), 'Non-game Tk window accepted as game'
        assert all(row.process_name.casefold().endswith(GAME_PROCESS.casefold().replace('  ', ' '))
                   or ''.join(row.process_name.casefold().split()).endswith(
                       ''.join(GAME_PROCESS.casefold().split())) for row in windows)
        for row in windows:
            assert registry.identity_matches(row.hwnd, row.pid)
            assert api.is_window(row.hwnd), 'Lost HWND while smoke was running'
        data.update({
            'status':'PASS_READONLY_NATIVE_WIN32_ENUMERATION',
            'top_level_hwnd_count':len(handles),
            'visible_hwnd_count':len(visible),
            'own_process_visible_hwnd_count':len(own),
            'own_title_verified_by_SendMessageTimeoutW':True,
            'own_process_image_api':'QueryFullProcessImageNameW',
            'own_window_class_verified':True,
            'game_candidates_found':len(windows),
            'candidate_pid_guarded':True,
            'real_game_present':len(windows) > 0,
            'faked_game_hwnds':0,
        })
    except Exception as exc:
        data['status'] = 'FAIL_NATIVE_WIN32_DISCOVERY'
        data['error'] = type(exc).__name__ + ': ' + str(exc)
        data['traceback'] = traceback.format_exc(limit=8)
    finally:
        if root is not None:
            try:
                root.destroy()
            except Exception as exc:
                data['status']='FAIL_TK_CLEANUP'
                data['close_error']=str(exc)
        REPORT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        for key in data:
            if key not in {'traceback'}:
                print('S08_'+key.upper()+'='+json.dumps(data[key],ensure_ascii=False))
        print('S08_REPORT='+str(REPORT))
    return 0 if data['status']=='PASS_READONLY_NATIVE_WIN32_ENUMERATION' else 1


if __name__=='__main__':
    raise SystemExit(run())
