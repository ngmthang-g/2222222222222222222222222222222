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
    """Passive Tk labels only; missing original action handlers are not faked.

    The real original view has interactive Copy, Nhập, updates and log upload;
    those controls are withheld until their original behavior is implemented.
    """

    def __init__(self, parent: Any, info_state: Any = None, *, ttk_module: Any = None):
        if ttk_module is None:
            from tkinter import ttk as ttk_module
        self.parent = parent
        self.info_state = info_state
        self._ttk = ttk_module
        self.container = ttk_module.Frame(parent)
        self.container.pack(fill='both', expand=True)
        ttk_module.Label(self.container, text='TLMTool - Thông tin').pack(anchor='w', padx=10, pady=(10, 6))
        self._status = ttk_module.Label(self.container, text='')
        self._status.pack(fill='x', padx=10, pady=(0, 8))
        self._values = {}
        for label, key in (
            ('Phiên bản', 'version'), ('Mã ứng dụng', 'device_code'),
            ('Key', 'license_key'), ('Loại bản quyền', 'license_type'),
            ('Cửa sổ', 'windows'), ('Hiệu lực', 'validity'),
        ):
            row = ttk_module.Frame(self.container)
            row.pack(fill='x', padx=10, pady=2)
            ttk_module.Label(row, text=label, width=17).pack(side='left')
            value = ttk_module.Label(row, text='')
            value.pack(side='left')
            self._values[key] = value
        ttk_module.Label(self.container, text='Lịch sử cập nhật:').pack(anchor='w', padx=10, pady=(10, 0))
        self._changelog = ttk_module.Label(self.container, text='', justify='left')
        self._changelog.pack(anchor='w', padx=10, pady=2)
        self.refresh_readonly()

    def refresh_readonly(self) -> InfoDisplay:
        display = display_from_info_state(self.info_state)
        self._status.configure(text=display.status)
        for key, widget in self._values.items():
            widget.configure(text=getattr(display, key))
        self._changelog.configure(text=display.changelog)
        return display
