"""S03 original-backed, read-only Info tab presentation slice.

B12 proves the section labels and version. The real server RPC, device ID,
license activation, update actions and changelog are NOT reconstructed.
The entrypoint remains blocked; this widget is not a released product.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

UNKNOWN = 'Chưa xác minh'  # Deliberate safe developer placeholder, NOT original text.
CURRENT_VERSION = '2.1.2'


@dataclass(frozen=True)
class InfoDisplay:
    version: str = CURRENT_VERSION
    device_code: str = UNKNOWN
    license_key: str = UNKNOWN
    license_type: str = UNKNOWN
    windows: str = UNKNOWN
    validity: str = UNKNOWN
    status: str = 'Chưa xác minh dữ liệu máy chủ'
    changelog: str = UNKNOWN


def display_from_info_state(info: Any) -> InfoDisplay:
    """Present only already verified state; NEVER infer features or license keys.

    The S02 InfoState does not contain independently verified device id,
    license key, expiry, changelog or price; therefore these stay UNKNOWN.
    """
    if info is None:
        return InfoDisplay()
    guard = getattr(info, 'permission_guard', None)
    snap = getattr(guard, 'snapshot', None)
    if snap is None or not getattr(snap, 'has_verified_payload', False) or getattr(snap, 'blocked', True):
        return InfoDisplay()
    # The plan status is not necessarily a server-facing license name.
    # This view deliberately does not claim FREE, VIP or the license expiry.
    return InfoDisplay(status='Đã có trạng thái quyền được xác minh')



class TLMInfoTab:
    """B12-measured read-only Info layout, without invented feature handlers.

    Coordinate anchors are relative to the real Info tab content frame
    (B12 top at screenshot y≈59). This is a Windows/Tk geometry match attempt,
    not a claim of pixel-identical original content, font or client DPI.
    """

    STATUS_B12 = (3, 51, 416, 44)
    VALUE_START_Y = 105
    VALUE_STEP_Y = 25
    CHANGELOG_B12 = (3, 295, 416, 109)

    def __init__(self, parent: Any, info_state: Any = None, *, ttk_module: Any = None):
        self._native = ttk_module is None
        if ttk_module is None:
            from tkinter import ttk as ttk_module
        self.parent = parent
        self.info_state = info_state
        self._ttk = ttk_module
        self.container = ttk_module.Frame(parent)
        self.container.pack(fill='both', expand=True)
        self._values = {}
        self._changelog_scrollbar = None

        title = ttk_module.Label(self.container, text='TLMTool - Thông tin')
        self._place(title, 7, 12, 320, 20)
        self._separator(37)

        # Unverified Info state uses the original blue "checking" palette
        # (#D1ECF1/#0C5460). It does NOT impersonate a validated 2.1.2 status.
        if self._native:
            import tkinter as tk
            self._status_border = tk.Frame(self.container, background='#000000',
                                           width=416, height=44)
            self._status = tk.Label(self._status_border, text='', anchor='w',
                                    padx=6, background='#D1ECF1', foreground='#0C5460')
            self._place(self._status_border, *self.STATUS_B12)
            self._status.place(x=1, y=1, width=414, height=42)
        else:
            self._status_border = ttk_module.Frame(self.container)
            self._status = ttk_module.Label(self._status_border, text='')
            self._place(self._status_border, *self.STATUS_B12)
            self._place(self._status, 1, 1, 414, 42)

        for index, (label, key) in enumerate((
            ('Phiên bản', 'version'), ('Mã ứng dụng', 'device_code'),
            ('Key', 'license_key'), ('Loại bản quyền', 'license_type'),
            ('Cửa sổ', 'windows'), ('Hiệu lực', 'validity'),
        )):
            y = self.VALUE_START_Y + self.VALUE_STEP_Y * index
            caption = ttk_module.Label(self.container, text=label)
            self._place(caption, 7, y, 96, 19)
            # The original has shorter surfaces for Key and device code to
            # accommodate actual actions. Their button slots stay BLANK.
            value_w = 256 if key in ('device_code', 'license_key') else 312
            if self._native:
                import tkinter as tk
                value = tk.Label(self.container, text='', background='#FFFFFF',
                                 anchor='w', padx=4)
            else:
                value = ttk_module.Label(self.container, text='')
            self._place(value, 107, y, value_w, 19)
            self._values[key] = value

        self._separator(259)
        label = ttk_module.Label(self.container, text='Lịch sử cập nhật:')
        self._place(label, 7, 274, 300, 19)

        if self._native:
            import tkinter as tk
            self._changelog_frame = tk.Frame(self.container, background='#FFFFFF',
                                             highlightthickness=0)
            self._place(self._changelog_frame, *self.CHANGELOG_B12)
            self._changelog = tk.Text(self._changelog_frame, wrap='word',
                                      relief='sunken', borderwidth=1, state='disabled',
                                      font=('Segoe UI', 9))
            self._changelog_scrollbar = ttk_module.Scrollbar(
                self._changelog_frame, orient='vertical',
                command=self._changelog.yview
            )
            self._changelog.configure(yscrollcommand=self._changelog_scrollbar.set)
            self._changelog.place(x=0, y=0, width=400, height=109)
            self._changelog_scrollbar.place(x=400, y=0, width=16, height=109)
        else:
            self._changelog_frame = ttk_module.Frame(self.container)
            self._place(self._changelog_frame, *self.CHANGELOG_B12)
            self._changelog = ttk_module.Label(self._changelog_frame, text='')
            self._place(self._changelog, 0, 0, 400, 109)

        self._separator(412)
        self.refresh_readonly()

    def _place(self, widget: Any, x: int, y: int, w: int, h: int) -> None:
        if self._native:
            widget.place(x=x, y=y, width=w, height=h)
        else:
            # Existing S03/S04 test adapters provide pack rather than place.
            widget.pack(anchor='w')

    def _separator(self, y: int) -> None:
        if self._native:
            separator = self._ttk.Separator(self.container, orient='horizontal')
        else:
            separator = self._ttk.Frame(self.container)
        self._place(separator, 3, y, 416, 1)

    def refresh_readonly(self) -> InfoDisplay:
        display = display_from_info_state(self.info_state)
        self._status.configure(text=display.status)
        for key, widget in self._values.items():
            widget.configure(text=getattr(display, key))
        if self._native:
            self._changelog.configure(state='normal')
            self._changelog.delete('1.0', 'end')
            self._changelog.insert('1.0', display.changelog)
            self._changelog.configure(state='disabled')
        else:
            self._changelog.configure(text=display.changelog)
        return display
