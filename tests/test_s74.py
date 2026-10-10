"""S74: 12 C14 verified native-host closing and scanner lifetime regressions."""
from __future__ import annotations
import sys
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from test_s17 import row, snap
from test_s70 import Root, SourceBackend, Widget, Session
from detached_host import C14DetachedHost
from detached_one_shot_scanner import C14DetachedOneShotScanner
from detached_lifecycle import C14DetachedLifecycle


class TestOnlySourceScanBackend:
    """Scanner view of S70 fake game rows; Tk detached owner 900 is NOT a game."""
    def __init__(self, source_backend):
        self.backend = source_backend
    def enumerate_top_level(self):
        return tuple(self.backend.rows)
    def is_window(self, hwnd):
        return self.backend.is_window(hwnd)
    def is_visible(self, hwnd):
        return self.backend.is_visible(hwnd)
    def process_id(self, hwnd):
        return self.backend.process_id(hwnd)
    def process_executable(self, pid):
        return self.backend.process_executable(pid)
    def window_class(self, hwnd):
        return self.backend.window_class(hwnd)
    def title_with_timeout(self, hwnd, timeout):
        return self.backend.title_with_timeout(hwnd, timeout)


class S74DetachmentLifecycle(unittest.TestCase):
    def setUp(self):
        self.rows = (row(1), row(2))
        self.events = []
        self.backend = SourceBackend(self.rows)
        self.root = Root()
        self.host = C14DetachedHost(
            self.root, windows_backend=self.backend,
            toplevel_factory=lambda _: Widget(self.events),
            resolve_root_hwnd=lambda h: h, is_topmost=lambda h: True,
            session_factory=lambda: Session(self.events))
        self.scanner = C14DetachedOneShotScanner(
            lambda: TestOnlySourceScanBackend(self.backend), clock=lambda: 87.0)
        self.ctrl = C14DetachedLifecycle(self.scanner, self.host)

    def scan(self, limit=2):
        self.assertEqual(self.ctrl.request_scan(max_windows=limit,
                         allowed=lambda: True).code, "SCAN_STARTED")
        self.scanner._thread.join(5)
        self.assertFalse(self.scanner._thread.is_alive())
        return self.ctrl.consume_scan(max_windows=limit, allowed=lambda: True)

    def show_host(self):
        state = self.scanner.read().snapshot
        self.assertTrue(state.valid)
        result = self.host.open(state, max_windows=2, allowed=lambda: True)
        self.assertEqual(result.code, "HOST_OPEN")
        self.assertEqual(self.host.owner_hwnd, 900)

    def test_01_constructing_controller_no_scan_tk_or_open(self):
        self.assertIsNone(self.scanner._thread)
        self.assertEqual(self.ctrl.identities, ())
        self.assertEqual(self.ctrl.consume_scan(max_windows=2,
                         allowed=lambda: True).code, "IDLE")
        self.assertEqual(self.events, [])

    def test_02_first_explicit_scan_accepts_verified_two_rows(self):
        result = self.scan()
        self.assertEqual(result.code, "LIST_CHANGED")
        self.assertEqual(result.identities, ((1, self.rows[0].pid),
                                             (2, self.rows[1].pid)))
        self.assertEqual(self.ctrl.consume_scan(max_windows=2,
                         allowed=lambda: True).code, "NO_NEW_SCAN")

    def test_03_same_list_second_scan_does_not_destroy_host(self):
        self.scan()
        self.show_host()
        self.assertEqual(self.scan().code, "UNCHANGED")
        self.assertEqual(self.host.owner_hwnd, 900)
        self.assertNotIn("host_destroy", self.events)

    def test_04_source_removed_closes_host_with_dwm_first(self):
        self.scan()
        self.show_host()
        self.backend.rows.pop(2)
        result = self.scan()
        self.assertEqual(result.code, "LIST_CHANGED")
        self.assertEqual(self.host.owner_hwnd, 0)
        self.assertLess(self.events.index("dwm_unregistered"),
                        self.events.index("host_destroy"))

    def test_05_hwnd_reused_with_new_pid_invalidates_host(self):
        self.scan()
        self.show_host()
        self.backend.rows[1] = row(1, 90011)
        result = self.scan()
        self.assertEqual(result.code, "LIST_CHANGED")
        self.assertEqual(self.host.owner_hwnd, 0)
        self.assertEqual(result.identities[0], (1, 90011))

    def test_06_revocation_closes_native_owner_and_cache(self):
        self.scan()
        self.show_host()
        self.assertEqual(self.ctrl.revoke().code, "REVOKED")
        self.assertEqual(self.ctrl.identities, ())
        self.assertEqual(self.host.owner_hwnd, 0)
        self.assertEqual(self.scanner.read().code, "REVOKED")

    def test_07_permission_denied_never_keeps_topmost_host(self):
        self.scan()
        self.show_host()
        response = self.ctrl.consume_scan(max_windows=2,
                        allowed=lambda: False)
        self.assertEqual(response.code, "PERMISSION_NOT_VERIFIED_OR_REVOKED")
        self.assertEqual(self.host.owner_hwnd, 0)
        self.assertEqual(self.scanner.read().code, "REVOKED")

    def test_08_overlimit_invalid_scan_cannot_keep_old_DWM(self):
        self.scan()
        self.show_host()
        self.assertEqual(self.ctrl.request_scan(max_windows=1,
                         allowed=lambda: True).code, "SCAN_STARTED")
        self.scanner._thread.join(4)
        self.assertEqual(self.scanner.read().code, "OVER_VERIFIED_LIMIT")
        self.assertEqual(self.ctrl.consume_scan(max_windows=1,
                         allowed=lambda: True).code,
                         "SCAN_INVALIDATED_OVER_VERIFIED_LIMIT")
        self.assertEqual(self.host.owner_hwnd, 0)

    def test_09_native_cleanup_error_latches_fail_closed(self):
        class ErrorSession(Session):
            def shutdown(obj):
                obj.events.append("dwm_error")
                raise OSError("test-only teardown failed")
        self.host._session_factory = lambda: ErrorSession(self.events)
        self.scan()
        self.show_host()
        self.backend.rows.pop(2)
        result = self.scan()
        self.assertEqual(result.code, "NATIVE_CLEANUP_FAILED_LOCKED")
        self.assertTrue(self.ctrl.faulted)
        self.assertEqual(self.ctrl.identities, ())
        self.assertEqual(self.host.owner_hwnd, 0)
        self.assertEqual(self.ctrl.request_scan(max_windows=2,
                         allowed=lambda: True).code,
                         "NATIVE_CLEANUP_FAILED_LOCKED")
        self.assertEqual(self.ctrl.shutdown().code,
                         "CLOSED_NATIVE_CLEANUP_FAILED")

    def test_10_background_cannot_consume_or_teardown_native_host(self):
        self.scan()
        self.show_host()
        replies = []
        t = threading.Thread(target=lambda: replies.append(
            self.ctrl.revoke().code))
        t.start()
        t.join(3)
        self.assertEqual(replies, ["WRONG_TK_THREAD"])
        self.assertEqual(self.host.owner_hwnd, 900)

    def test_11_shutdown_with_late_scan_cannot_republish(self):
        self.scan()
        self.show_host()
        gate, release = threading.Event(), threading.Event()
        def blocked_backend():
            gate.set()
            release.wait(3)
            return self.backend
        self.scanner._backend_factory = blocked_backend
        self.assertEqual(self.ctrl.request_scan(max_windows=2,
                           allowed=lambda: True).code, "SCAN_STARTED")
        self.assertTrue(gate.wait(2))
        self.assertEqual(self.ctrl.shutdown().code, "CLOSED")
        release.set()
        self.scanner._thread.join(4)
        self.assertEqual(self.scanner.read().code, "CLOSED")
        self.assertEqual(self.ctrl.identities, ())
        self.assertEqual(self.host.owner_hwnd, 0)

    def test_12_no_timer_injection_fake_button_or_auto_open(self):
        self.scan()
        self.assertEqual(self.ctrl.shutdown().code, "CLOSED")
        self.assertEqual(self.ctrl.shutdown().code, "CLOSED")
        source = (ROOT / "src/detached_lifecycle.py").read_text("utf-8")
        for token in ("tk.Button(", "tk.Toplevel(", ".after(",
                      "PostMessage(", "ReadProcessMemory(",
                      "CreateRemoteThread(", "proxy_tab", "host.open(",
                      "host.render("):
            self.assertNotIn(token, source)

    def test_13_lowered_cap_on_same_snapshot_closes_native_host(self):
        self.scan()
        self.show_host()
        # No second scan: entitlement limit has reduced from 2 to 1.
        response = self.ctrl.consume_scan(max_windows=1,
                                         allowed=lambda: True)
        self.assertEqual(response.code, "OVER_VERIFIED_LIMIT_OR_INVALID_CACHE")
        self.assertEqual(self.host.owner_hwnd, 0)
        self.assertEqual(self.ctrl.identities, ())
        self.assertEqual(self.scanner.read().code, "REVOKED")
        self.assertLess(self.events.index("dwm_unregistered"),
                        self.events.index("host_destroy"))


if __name__ == "__main__":
    unittest.main()
