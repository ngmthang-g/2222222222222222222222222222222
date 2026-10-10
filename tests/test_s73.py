"""S73 twelve scoped tests: independent one-shot read-only C14 worker."""
from __future__ import annotations

import sys
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from detached_one_shot_scanner import C14DetachedOneShotScanner
from test_s17 import Backend, row


class S73OneShotScanner(unittest.TestCase):
    def setUp(self):
        self.a, self.b = row(31), row(32)
        self.rows = [self.a, self.b]
        self.calls = []
        self.maker_thread_ids = []

        def make():
            self.calls.append("new_backend")
            self.maker_thread_ids.append(threading.get_ident())
            return Backend(self.rows)
        self.scanner = C14DetachedOneShotScanner(make, clock=lambda: 77.0)

    def start_and_join(self, max_windows=3):
        status = self.scanner.request(max_windows=max_windows,
                                      allowed=lambda: True)
        if status == "SCAN_STARTED":
            self.scanner._thread.join(4)
            self.assertFalse(self.scanner._thread.is_alive())
        return status

    def test_01_no_implicit_timer_or_background_scan_on_init(self):
        self.assertEqual(self.scanner.read().code, "IDLE")
        self.assertEqual(self.calls, [])
        self.assertIsNone(self.scanner._thread)

    def test_02_one_scan_publishes_immutable_s09_snapshot(self):
        self.assertEqual(self.start_and_join(), "SCAN_STARTED")
        state = self.scanner.read()
        self.assertEqual(state.code, "READY")
        self.assertTrue(state.snapshot.valid)
        self.assertEqual(tuple(w.hwnd for w in state.snapshot.windows),
                         (31, 32))
        self.assertEqual(state.snapshot.captured_at, 77.0)

    def test_03_no_second_scan_without_an_explicit_request(self):
        self.start_and_join()
        self.assertEqual(self.calls, ["new_backend"])
        self.assertEqual(self.scanner.read().code, "READY")
        self.assertEqual(self.calls, ["new_backend"])
        self.start_and_join()
        self.assertEqual(len(self.calls), 2)

    def test_04_backend_creation_only_inside_worker(self):
        owner_tid = threading.get_ident()
        self.start_and_join()
        self.assertNotEqual(self.maker_thread_ids[0], owner_tid)

    def test_05_new_scan_clears_previous_snapshot_before_native_work(self):
        self.start_and_join()
        entered = threading.Event()
        release = threading.Event()
        original = self.scanner._backend_factory

        def paused():
            entered.set()
            release.wait(3)
            return original()
        self.scanner._backend_factory = paused
        self.assertEqual(self.scanner.request(max_windows=3,
                           allowed=lambda: True), "SCAN_STARTED")
        self.assertTrue(entered.wait(2))
        self.assertFalse(self.scanner.read().snapshot.valid)
        release.set()
        self.scanner._thread.join(3)
        self.assertEqual(self.scanner.read().code, "READY")

    def test_06_live_scan_is_not_started_twice(self):
        entered, release = threading.Event(), threading.Event()
        def blocked():
            entered.set()
            release.wait(3)
            return Backend(self.rows)
        self.scanner._backend_factory = blocked
        self.assertEqual(self.scanner.request(max_windows=3,
                          allowed=lambda: True), "SCAN_STARTED")
        self.assertTrue(entered.wait(2))
        self.assertEqual(self.scanner.request(max_windows=3,
                         allowed=lambda: True), "SCAN_BUSY")
        release.set()
        self.scanner._thread.join(4)

    def test_07_revocation_drops_older_late_scan(self):
        entered, release = threading.Event(), threading.Event()
        def blocked():
            entered.set()
            release.wait(3)
            return Backend(self.rows)
        self.scanner._backend_factory = blocked
        self.assertEqual(self.scanner.request(max_windows=3,
                          allowed=lambda: True), "SCAN_STARTED")
        self.assertTrue(entered.wait(2))
        self.scanner.revoke()
        release.set()
        self.scanner._thread.join(4)
        self.assertEqual(self.scanner.read().code, "REVOKED")
        self.assertFalse(self.scanner.read().snapshot.valid)

    def test_08_shutdown_during_scan_never_republishes(self):
        entered, release = threading.Event(), threading.Event()
        def blocked():
            entered.set()
            release.wait(3)
            return Backend(self.rows)
        self.scanner._backend_factory = blocked
        self.scanner.request(max_windows=3, allowed=lambda: True)
        self.assertTrue(entered.wait(2))
        self.scanner.shutdown()
        release.set()
        self.scanner._thread.join(4)
        self.assertEqual(self.scanner.read().code, "CLOSED")
        self.assertFalse(self.scanner.read().snapshot.valid)
        self.assertEqual(self.start_and_join(), "CLOSED")

    def test_09_permissions_and_window_limit_fail_before_worker(self):
        for limit in (None, True, -2, 0, "2"):
            self.assertEqual(self.scanner.request(
                max_windows=limit, allowed=lambda: True),
                "NO_VERIFIED_WINDOW_LIMIT")
        self.assertEqual(self.scanner.request(max_windows=3,
                         allowed=lambda: False), "PERMISSION_REVOKED")
        self.assertEqual(self.scanner.request(max_windows=3,
                         allowed=lambda: 1/0), "PERMISSION_NOT_VERIFIED")
        self.assertEqual(self.calls, [])

    def test_10_backend_exception_invalidates_instead_of_reusing_data(self):
        self.start_and_join()
        def bad_backend():
            raise OSError("native failed")
        self.scanner._backend_factory = bad_backend
        self.start_and_join()
        result = self.scanner.read()
        self.assertEqual(result.code, "SCAN_ERROR_OSError")
        self.assertFalse(result.snapshot.valid)
        self.assertEqual(result.snapshot.windows, ())

    def test_11_hwnd_reuse_w_new_pid_fresh_scan_is_visible_to_s72(self):
        self.start_and_join()
        earlier = self.scanner.read().snapshot
        self.rows[0] = row(31, 888111)
        self.start_and_join()
        latest = self.scanner.read().snapshot
        self.assertEqual(earlier.windows[0].hwnd, latest.windows[0].hwnd)
        self.assertNotEqual(earlier.windows[0].pid, latest.windows[0].pid)
        self.assertGreater(latest.revision, earlier.revision)

    def test_12_overlimit_and_no_fake_detached_clock_or_ui(self):
        self.start_and_join(max_windows=1)
        self.assertEqual(self.scanner.read().code, "OVER_VERIFIED_LIMIT")
        self.assertEqual(self.scanner.read().snapshot.windows, ())
        self.assertFalse(self.scanner.read().snapshot.valid)
        source = (ROOT / "src/detached_one_shot_scanner.py").read_text("utf-8")
        for forbidden in ("tk.Button(", "tk.Toplevel(", ".after(",
                          "PostMessage(", "CreateRemoteThread(",
                          "ReadProcessMemory(", "proxy_tab"):
            self.assertNotIn(forbidden, source)
        self.scanner.shutdown()


if __name__ == "__main__":
    unittest.main()
