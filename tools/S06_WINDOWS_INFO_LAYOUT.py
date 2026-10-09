"""S06 native Windows Tk geometry check against B12 Info reference.

No real token/network/game/activation or normal product entrypoint.
The screenshot contains only safe read-only unverified values.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import time
import traceback

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / 'src'))

OUTPUT = BASE / 'artifacts' / 's06'
REPORT = OUTPUT / 'native_info_layout.json'
PREVIEW = OUTPUT / 'native_info_layout.png'
B12_CLIENT = [450, 1000]
B12_FULL = [452, 1032]


def bounds_relative(widget, parent):
    return [
        int(widget.winfo_rootx() - parent.winfo_rootx()),
        int(widget.winfo_rooty() - parent.winfo_rooty()),
        int(widget.winfo_width()),
        int(widget.winfo_height()),
    ]


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    record = {
        'task': 'S06',
        'status': 'NOT_RUN',
        'platform': os.name,
        'b12_client': B12_CLIENT,
        'b12_full_raster': B12_FULL,
        'b12_raster_loaded': False,
        'pixel_diff_performed': False,
        'production_auth': 'NOT_RUN',
        'release_exe': 'NOT_BUILT',
        'screenshot': 'NOT_RUN',
    }
    root = None
    binding = None
    try:
        import tkinter as tk
        from info_binding import create_info_only_shell
        from shell import INFO_KEY

        root = tk.Tk()
        binding = create_info_only_shell(root)
        binding.app.position_window_top_right()
        root.update_idletasks()
        root.update()

        view = binding.view
        frame = binding.app._tab_frames[INFO_KEY]
        status = bounds_relative(view._status_border, frame)
        values = {key: bounds_relative(widget, frame) for key, widget in view._values.items()}
        changelog = bounds_relative(view._changelog_frame, frame)
        native_scroller = view._changelog_scrollbar
        record.update({
            'desktop': [root.winfo_screenwidth(), root.winfo_screenheight()],
            'client': [root.winfo_width(), root.winfo_height()],
            'info_content_frame': [frame.winfo_width(), frame.winfo_height()],
            'b12_reference_layout_in_info_coordinates': {
                'status': [3, 51, 416, 44],
                'first_value': [107, 105, 312, 19],
                'changelog': [3, 295, 416, 109],
            },
            'status_rect': status,
            'value_rects': values,
            'changelog_rect': changelog,
            'changelog_scrollbar_present': native_scroller is not None,
            'changelog_readonly': view._changelog.cget('state') == 'disabled',
            'status_text': view._status.cget('text'),
            'license_type': view._values['license_type'].cget('text'),
            'visible': [key for key, obj in binding.app._tab_frames.items()
                        if binding.app.notebook.tab(obj, 'state') == 'normal'],
        })
        if status != [3, 51, 416, 44]:
            raise AssertionError('S06 status geometry differs from B12 frame-relative anchor: ' + repr(status))
        if values['version'] != [107, 105, 312, 19]:
            raise AssertionError('S06 version surface geometry differs: ' + repr(values['version']))
        if changelog != [3, 295, 416, 109]:
            raise AssertionError('S06 changelog geometry differs: ' + repr(changelog))
        if [values[k][1] for k in (
            'version','device_code','license_key','license_type','windows','validity')] != [
            105,130,155,180,205,230]:
            raise AssertionError('Six value rows do not have 25px pitch')
        if not native_scroller or view._changelog.cget('state') != 'disabled':
            raise AssertionError('Missing native read-only Text/Scrollbar')
        if record['visible'] != ['info_tab'] or record['license_type'] != 'Chưa xác minh':
            raise AssertionError('Unverified license or unsupported tab was exposed')
        if record['client'][0] != 450:
            raise AssertionError('Expected original 450px client width')

        record['b12_relation'] = {
            'anchor_match': True,
            'full_raster_pixel_parity': 'NOT_RUN',
            'height_matches_b12': record['client'][1] == 1000,
            'tab_visibility_matches_B12': False,
            'server_content_matches_B12': False,
            'note': 'Coordinates are Info-frame relative; titlebar, DPI and environment differ.',
        }

        try:
            from PIL import ImageGrab
            root.update()
            time.sleep(0.15)
            img = ImageGrab.grab(bbox=(
                root.winfo_rootx(), root.winfo_rooty(),
                root.winfo_rootx() + root.winfo_width(),
                root.winfo_rooty() + root.winfo_height(),
            ))
            img.save(PREVIEW)
            record['screenshot'] = 'CAPTURED_CLIENT_REGION'
            record['screenshot_size'] = list(img.size)
        except Exception as exc:
            record['screenshot'] = 'UNAVAILABLE'
            record['screenshot_error'] = str(exc)[:250]

        record['status'] = 'PASS_NATIVE_READONLY_LAYOUT_ANCHORS'
    except Exception as exc:
        record['status'] = 'FAIL_NATIVE_LAYOUT'
        record['failure'] = type(exc).__name__ + ': ' + str(exc)
        record['traceback'] = traceback.format_exc(limit=8)
    finally:
        if root is not None:
            try:
                root.destroy()
            except Exception as exc:
                record['status'] = 'FAIL_DESTROY'
                record['destroy_error'] = str(exc)
        if binding is not None:
            record['binding_closed'] = binding._closed
            if not binding._closed:
                record['status'] = 'FAIL_CLEANUP'
        REPORT.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
        print('S06_LAYOUT_REPORT=' + str(REPORT))
        print('S06_LAYOUT_STATUS=' + record['status'])
        for key in ('desktop','client','status_rect','value_rects','changelog_rect',
                    'changelog_scrollbar_present','screenshot','b12_relation','binding_closed'):
            if key in record:
                print('S06_' + key.upper() + '=' + json.dumps(record[key], ensure_ascii=False))
        if 'failure' in record:
            print('S06_ERROR=' + record['failure'])
    return 0 if record['status'] == 'PASS_NATIVE_READONLY_LAYOUT_ANCHORS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
