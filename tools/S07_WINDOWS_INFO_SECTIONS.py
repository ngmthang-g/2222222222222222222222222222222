"""S07 native Windows Tk measurement of B12 passive lower Info sections.

This is NOT the production launcher; no server, license signing, game,
clickable support control or original EXE is invoked.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
OUT = ROOT / 'artifacts' / 's07'
OUT.mkdir(parents=True, exist_ok=True)


def placed(widget):
    value = widget.place_info()
    return [int(value[k]) for k in ('x','y','width','height')]


def main():
    record = dict(task='S07', status='NOT_RUN', b12_pixel_parity='NOT_RUN',
                  real_license_server='NOT_RUN', windows_exe='NOT_BUILT')
    root = None
    binding = None
    try:
        import tkinter as tk
        from tkinter import ttk
        from info_binding import create_info_only_shell
        from info_tab import UNKNOWN

        root = tk.Tk()
        binding = create_info_only_shell(root)
        binding.app.position_window_top_right()
        root.update_idletasks()
        root.update()
        ui = binding.view

        rects = {
            'status': placed(ui._status_border),
            'changelog': placed(ui._changelog_frame),
            'price': placed(ui._price),
            'contact': placed(ui._contact_label),
            'facebook': placed(ui._facebook_label),
            'zalo': placed(ui._zalo_label),
            'catalog_header': placed(ui._catalog_heading),
            'catalog': placed(ui._catalog),
        }
        expected = {
            'status': [3,51,416,44],
            'changelog': [3,295,416,109],
            'price': [6,427,416,88],
            'contact': [7,539,300,19],
            'facebook': [27,566,126,19],
            'zalo': [155,566,110,19],
            'catalog_header': [7,630,320,19],
            'catalog': [30,656,340,58],
        }
        for key in expected:
            assert rects[key] == expected[key], (key,rects[key],expected[key])
        separators = sorted(int(w.place_info()['y']) for w in ui.container.winfo_children()
                            if isinstance(w, ttk.Separator))
        assert separators == [37,259,412,526,616], separators
        assert ui._price.cget('text') == UNKNOWN
        assert ui._catalog.cget('text') == UNKNOWN
        assert ui._facebook_label.cget('text') == '● Facebook'
        assert ui._zalo_label.cget('text') == '● Zalo'
        assert ui._facebook_label.bind('<Button-1>') == ''
        assert ui._zalo_label.bind('<Button-1>') == ''
        assert ui._changelog.cget('state') == 'disabled'
        assert len(binding.app.notebook.tabs()) == 15
        visible = [key for key, frame in binding.app._tab_frames.items()
                   if binding.app.notebook.tab(frame, 'state') == 'normal']
        assert visible == ['info_tab'], visible

        def descendants(w):
            for child in w.winfo_children():
                yield child
                yield from descendants(child)
        buttons = [w for w in descendants(ui.container) if isinstance(w, (tk.Button,ttk.Button))]
        assert not buttons, ['fake action controls',str(buttons)]

        frame_height = int(binding.app._tab_frames['info_tab'].winfo_height())
        record.update(
            client=[root.winfo_width(),root.winfo_height()],
            desktop=[root.winfo_screenwidth(),root.winfo_screenheight()],
            b12_client=[450,1000],
            rectangles=rects, separators=separators,
            visible_tabs=visible,
            price_text=ui._price.cget('text'),
            catalog_text=ui._catalog.cget('text'),
            action_button_count=len(buttons),
            contact_clickable=False,
            info_frame_height=frame_height,
            catalog_fully_within_frame=(656+58 <= frame_height),
            noted_small_runner_clipping=(656+58 > frame_height),
            exact_original_png_loaded=False,
            b12_status_panel_color_mode='SAFE_UNVERIFIED_CHECKING',
        )
        try:
            from PIL import ImageGrab
            root.update()
            time.sleep(0.1)
            png=ImageGrab.grab(bbox=(root.winfo_rootx(),root.winfo_rooty(),
                                   root.winfo_rootx()+root.winfo_width(),
                                   root.winfo_rooty()+root.winfo_height()))
            png.save(OUT / 'native_info_lower_sections.png')
            record['screenshot']='CAPTURED_CLIENT_ONLY'
        except Exception as e:
            record['screenshot']='UNAVAILABLE'
            record['capture_error']=str(e)[:220]
        record['status']='PASS_NATIVE_PASSIVE_SECTIONS'
    except Exception as e:
        record['status']='FAIL_NATIVE_SECTIONS'
        record['failure']=str(e)
        record['traceback']=traceback.format_exc(limit=8)
    finally:
        if root is not None:
            try:
                root.destroy()
            except Exception as e:
                record['status']='FAIL_SHUTDOWN'
                record['close_error']=str(e)
        if binding is not None:
            record['closed']=binding._closed
            if not binding._closed:
                record['status']='FAIL_CLEANUP'
        (OUT / 'native_sections.json').write_text(
            json.dumps(record, ensure_ascii=False, indent=2),encoding='utf-8')
        for key in ['status','client','desktop','rectangles','separators','visible_tabs',
                    'action_button_count','catalog_fully_within_frame','screenshot','closed','failure']:
            if key in record:
                print('S07_'+key.upper()+'='+json.dumps(record[key],ensure_ascii=False))
    return 0 if record['status']=='PASS_NATIVE_PASSIVE_SECTIONS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
