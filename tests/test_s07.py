"""S07: original B12 passive price, contacts and system catalog tests."""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'src'))
from info_tab import InfoDisplay, TLMInfoTab, UNKNOWN
from info_state import InfoState
from permission_guard import VerifiedClaims


class MockWidget:
    instances = []
    def __init__(self, parent=None, **kwargs):
        self.parent = parent
        self.settings = dict(kwargs)
        self.instances.append(self)
    def pack(self, **kwargs):
        pass
    def configure(self, **kwargs):
        self.settings.update(kwargs)


class MockTtk:
    Frame = MockWidget
    Label = MockWidget


class S07ReadOnlySectionsTests(unittest.TestCase):
    def view(self, state=None):
        MockWidget.instances.clear()
        return TLMInfoTab(MockWidget(), state, ttk_module=MockTtk)

    def test_b12_original_section_anchor_contracts(self):
        self.assertEqual(TLMInfoTab.PRICE_B12, (6, 427, 416, 88))
        self.assertEqual(TLMInfoTab.CONTACT_B12, (7, 539, 300, 19))
        self.assertEqual(TLMInfoTab.CATALOG_B12, (30, 656, 340, 58))
        self.assertEqual(TLMInfoTab.STATUS_B12, (3, 51, 416, 44))
        self.assertEqual(TLMInfoTab.CHANGELOG_B12, (3, 295, 416, 109))

    def test_original_static_support_headings_without_fake_links(self):
        view = self.view()
        self.assertEqual(view._contact_label.settings['text'], 'Liên hệ hỗ trợ, yêu cầu tính năng:')
        self.assertEqual(view._facebook_label.settings['text'], '● Facebook')
        self.assertEqual(view._zalo_label.settings['text'], '● Zalo')
        self.assertEqual(view._catalog_heading.settings['text'], 'Auto trong hệ thống')
        self.assertEqual(view._facebook_label.settings['foreground'], '#0000FF')
        self.assertEqual(view._zalo_label.settings['foreground'], '#0000FF')
        self.assertFalse(hasattr(MockTtk, 'Button'))

    def test_no_server_prices_or_catalog_are_hardcoded(self):
        view = self.view()
        self.assertEqual(view._price.settings['text'], UNKNOWN)
        self.assertEqual(view._catalog.settings['text'], UNKNOWN)
        self.assertEqual(InfoDisplay().price_text, UNKNOWN)
        self.assertEqual(InfoDisplay().catalog_text, UNKNOWN)
        self.assertNotIn('200k/1', repr(view._price.settings))
        self.assertNotIn('Lineage W', repr(view._catalog.settings))

    def test_test_only_verified_claim_cannot_fabricate_server_fields(self):
        state = InfoState()
        state.receive_server_token(
            'TEST_ONLY', lambda _: VerifiedClaims(
                frozenset({'info_tab'}), 'vip', 20,
            ),
        )
        view = self.view(state)
        self.assertEqual(view.refresh_readonly().price_text, UNKNOWN)
        self.assertEqual(view._price.settings['text'], UNKNOWN)
        self.assertEqual(view._catalog.settings['text'], UNKNOWN)
        self.assertEqual(view._values['license_type'].settings['text'], UNKNOWN)

    def test_revocation_clears_view_and_preserves_passive_sections(self):
        state = InfoState()
        view = self.view(state)
        state.receive_server_token(
            'TEST_ONLY', lambda _: VerifiedClaims(frozenset({'info_tab'}), 'vip', 1))
        view.refresh_readonly()
        state.on_server_error()
        self.assertEqual(view.refresh_readonly(), InfoDisplay())
        self.assertEqual(view._price.settings['text'], UNKNOWN)
        self.assertEqual(view._catalog.settings['text'], UNKNOWN)
        self.assertEqual(view._contact_label.settings['text'], 'Liên hệ hỗ trợ, yêu cầu tính năng:')

    def test_no_missing_action_buttons_materialize_from_labels(self):
        self.view()
        texts=[w.settings.get('text') for w in MockWidget.instances]
        self.assertNotIn('Gửi log hỗ trợ',texts)
        self.assertNotIn('Nhập', texts)
        self.assertNotIn('Copy', texts)
        self.assertNotIn('Cập nhật tự động', texts)


if __name__ == '__main__':
    unittest.main()
