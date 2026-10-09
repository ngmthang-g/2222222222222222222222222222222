"""S03 headless tests for read-only original-backed Info presentation."""
import pathlib
import sys
import unittest
from types import SimpleNamespace
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]/'src'))
from info_tab import CURRENT_VERSION, UNKNOWN, InfoDisplay, TLMInfoTab, display_from_info_state


class FakeWidget:
    instances = []
    def __init__(self, parent=None, **kwargs):
        self.parent, self.settings, self.kwargs = parent, {}, kwargs
        self.settings.update(kwargs)
        self.instances.append(self)
    def pack(self, **kwargs): return None
    def configure(self, **kwargs): self.settings.update(kwargs)


class FakeTtk:
    Frame = FakeWidget
    Label = FakeWidget


class S03Tests(unittest.TestCase):
    def test_original_version_and_unverified_values(self):
        self.assertEqual(CURRENT_VERSION, '2.1.2')
        d = display_from_info_state(None)
        self.assertEqual(d.version, CURRENT_VERSION)
        self.assertEqual((d.license_type, d.device_code, d.license_key), (UNKNOWN, UNKNOWN, UNKNOWN))

    def test_never_display_unverified_raw_payload(self):
        fake = SimpleNamespace(permission_guard=SimpleNamespace(snapshot=SimpleNamespace(
            has_verified_payload=False, blocked=False, max_windows=500, plan_status='VIP')))
        d = display_from_info_state(fake)
        self.assertEqual(d.windows, UNKNOWN)
        self.assertEqual(d.license_type, UNKNOWN)

    def test_verified_snapshot_does_not_invent_license_or_expiry(self):
        fake = SimpleNamespace(permission_guard=SimpleNamespace(snapshot=SimpleNamespace(
            has_verified_payload=True, blocked=False, max_windows=3, plan_status='vip')))
        d = display_from_info_state(fake)
        self.assertEqual(d.license_type, UNKNOWN)
        self.assertEqual(d.windows, UNKNOWN)
        self.assertIn('xác minh', d.status)

    def test_blocked_snapshot_returns_unverified(self):
        fake = SimpleNamespace(permission_guard=SimpleNamespace(snapshot=SimpleNamespace(
            has_verified_payload=True, blocked=True, plan_status='ban')))
        self.assertEqual(display_from_info_state(fake), InfoDisplay())

    def test_real_readonly_widgets_without_dummy_action_buttons(self):
        FakeWidget.instances.clear()
        ui = TLMInfoTab(FakeWidget(), ttk_module=FakeTtk)
        labels=[x.settings.get('text') for x in FakeWidget.instances]
        for text in ('TLMTool - Thông tin', 'Phiên bản', 'Mã ứng dụng', 'Key',
                     'Loại bản quyền', 'Cửa sổ', 'Hiệu lực', 'Lịch sử cập nhật:'):
            self.assertIn(text, labels)
        self.assertEqual(set(ui._values), {'version', 'device_code', 'license_key',
                                            'license_type', 'windows', 'validity'})
        self.assertNotIn('Nhập', labels)
        self.assertNotIn('Copy', labels)
        self.assertEqual(ui.refresh_readonly().license_type, UNKNOWN)

    def test_revoke_repaints_without_credentials(self):
        snap=SimpleNamespace(has_verified_payload=True, blocked=False)
        state=SimpleNamespace(permission_guard=SimpleNamespace(snapshot=snap))
        ui=TLMInfoTab(FakeWidget(),state,ttk_module=FakeTtk)
        self.assertIn('xác minh',ui.refresh_readonly().status)
        state.permission_guard.snapshot=SimpleNamespace(has_verified_payload=False, blocked=True)
        self.assertEqual(ui.refresh_readonly(),InfoDisplay())
        self.assertEqual(ui._status.settings['text'],InfoDisplay().status)


if __name__ == '__main__': unittest.main()
