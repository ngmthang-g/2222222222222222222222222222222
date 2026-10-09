"""S06 read-only geometry and safe-field regression checks (Tk adapter tests)."""
import pathlib
import sys
import unittest
from types import SimpleNamespace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'src'))
from info_tab import CURRENT_VERSION, UNKNOWN, TLMInfoTab, display_from_info_state
from info_state import InfoState


class Element:
    registry = []
    def __init__(self, parent=None, **kwargs):
        self.parent = parent
        self.props = dict(kwargs)
        self.registry.append(self)
    def pack(self, **kwargs):
        self.props['pack'] = kwargs
    def configure(self, **kwargs):
        self.props.update(kwargs)


class HeadlessTtk:
    Frame = Element
    Label = Element


class S06ReadOnlyLayoutTests(unittest.TestCase):
    def make_view(self, state=None):
        Element.registry.clear()
        return TLMInfoTab(Element(), info_state=state, ttk_module=HeadlessTtk)

    def test_fixed_b12_status_and_changelog_geometry_contract(self):
        self.assertEqual(TLMInfoTab.STATUS_B12, (3, 51, 416, 44))
        self.assertEqual(TLMInfoTab.CHANGELOG_B12, (3, 295, 416, 109))
        self.assertEqual(TLMInfoTab.VALUE_START_Y, 105)
        self.assertEqual(TLMInfoTab.VALUE_STEP_Y, 25)

    def test_all_six_surfaces_show_verifiably_safe_values(self):
        view = self.make_view()
        self.assertEqual(len(view._values), 6)
        self.assertEqual(view._values['version'].props['text'], CURRENT_VERSION)
        for key in ('device_code', 'license_key', 'license_type', 'windows', 'validity'):
            self.assertEqual(view._values[key].props['text'], UNKNOWN)

    def test_scroll_region_is_prepared_without_functional_actions(self):
        view = self.make_view()
        self.assertIsNotNone(view._changelog_frame)
        self.assertIsNone(view._changelog_scrollbar)  # Headless-only fallback
        self.assertEqual(view._changelog.props['text'], UNKNOWN)
        self.assertNotIn('Copy', [v.props.get('text') for v in Element.registry])
        self.assertNotIn('Nhập', [v.props.get('text') for v in Element.registry])

    def test_verified_claim_does_not_fake_license_values(self):
        state = InfoState()
        from permission_guard import VerifiedClaims
        state.receive_server_token('FAKE_TEST_ONLY',
                                   lambda _: VerifiedClaims(frozenset({'info_tab'}), 'vip', 16))
        view = self.make_view(state)
        view.refresh_readonly()
        self.assertEqual(view._values['license_type'].props['text'], UNKNOWN)
        self.assertEqual(view._values['windows'].props['text'], UNKNOWN)

    def test_revocation_zeros_status_after_a_temporary_test_claim(self):
        state = InfoState()
        from permission_guard import VerifiedClaims
        view = self.make_view(state)
        state.receive_server_token('FAKE_TEST_ONLY',
                                   lambda _: VerifiedClaims(frozenset({'info_tab'}), 'vip', 4))
        self.assertIn('xác minh', view.refresh_readonly().status)
        state.on_server_error()
        self.assertEqual(view.refresh_readonly().status, 'Chưa xác minh dữ liệu máy chủ')
        self.assertEqual(view._status.props['text'], 'Chưa xác minh dữ liệu máy chủ')

    def test_textual_snapshot_cannot_force_price_or_changelog(self):
        raw = SimpleNamespace(permission_guard=SimpleNamespace(
            snapshot=SimpleNamespace(has_verified_payload=False, blocked=False, price="999",
                                     changelog="INVENTED", plan_status="VIP")))
        d = display_from_info_state(raw)
        self.assertEqual(d.changelog, UNKNOWN)
        self.assertEqual(d.license_type, UNKNOWN)


if __name__ == '__main__':
    unittest.main()
