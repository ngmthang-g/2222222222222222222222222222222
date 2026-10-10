"""S72: 12 C14 HWND/PID observer regressions; original cadence is UNKNOWN."""
from __future__ import annotations

import sys
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from detached_list_observer import C14DetachedListObserver
from start_polling import WindowSnapshot
from start_windows import GameWindow, GAME_TITLE, GAME_PROCESS, UNITY_WINDOW_CLASS
from test_s17 import row


def snapshot(revision, *windows, valid=True):
    return WindowSnapshot(revision, tuple(windows), valid)


class S72C14Observer(unittest.TestCase):
    def setUp(self):
        self.events = []
        self.observer = C14DetachedListObserver(lambda: self.events.append("clear"))
        self.a, self.b = row(41), row(42)

    def observe(self, revision, *windows, allowed=lambda: True, limit=3, valid=True):
        return self.observer.observe(
            snapshot(revision, *windows, valid=valid),
            max_windows=limit, allowed=allowed,
        )

    def test_01_first_verified_list_invalidates_prior_renderer(self):
        r = self.observe(1, self.a, self.b)
        self.assertEqual(r.code, "LIST_CHANGED")
        self.assertTrue(r.changed)
        self.assertEqual(r.current, ((41, self.a.pid), (42, self.b.pid)))
        self.assertEqual(self.events, ["clear"])

    def test_02_revision_or_title_only_change_never_rebuilds(self):
        self.observe(1, self.a)
        same = GameWindow(41, self.a.pid, "different visible label",
                          self.a.class_name, self.a.process_name)
        # A game-qualified class permits another title; title isn't identity.
        result = self.observe(2, same)
        self.assertEqual(result.code, "UNCHANGED")
        self.assertFalse(result.changed)
        self.assertEqual(len(self.events), 1)

    def test_03_added_and_removed_hwnds_each_invalidate(self):
        self.observe(1, self.a)
        self.assertEqual(self.observe(2, self.a, self.b).code, "LIST_CHANGED")
        result = self.observe(3, self.b)
        self.assertEqual(result.previous,
                         ((41, self.a.pid), (42, self.b.pid)))
        self.assertEqual(self.observer.identities, ((42, self.b.pid),))
        self.assertEqual(len(self.events), 3)

    def test_04_reused_hwnd_different_pid_never_keeps_old_renderer(self):
        self.observe(1, self.a)
        changed = row(41, 900002)
        result = self.observe(2, changed)
        self.assertEqual(result.code, "LIST_CHANGED")
        self.assertEqual(result.current, ((41, 900002),))
        self.assertEqual(len(self.events), 2)

    def test_05_same_revision_changed_identity_fails_closed(self):
        self.observe(8, self.a)
        result = self.observe(8, self.b)
        self.assertEqual(result.code, "REVISION_IDENTITY_CONFLICT")
        self.assertEqual(self.observer.identities, ())
        self.assertEqual(len(self.events), 2)

    def test_06_stale_revision_revokes_untrusted_handles(self):
        self.observe(5, self.a)
        result = self.observe(4, self.a)
        self.assertEqual(result.code, "STALE_REVISION")
        self.assertEqual(self.observer.identities, ())
        self.assertEqual(len(self.events), 2)

    def test_07_failed_enumeration_revokes_existing_and_does_not_keep_old(self):
        self.observe(1, self.a)
        result = self.observe(2, self.a, valid=False)
        self.assertEqual(result.code, "INVALID_CACHE")
        self.assertEqual(self.observer.identities, ())
        self.assertEqual(len(self.events), 2)

    def test_08_permission_revoke_and_unverified_permission(self):
        self.observe(1, self.a)
        self.assertEqual(self.observe(2, self.a, allowed=lambda: False).code,
                         "PERMISSION_REVOKED")
        self.assertEqual(self.observer.identities, ())
        self.assertEqual(self.observe(3, self.a, allowed=lambda: 1/0).code,
                         "PERMISSION_NOT_VERIFIED")

    def test_09_max_windows_missing_overlimit_and_bool_rejected(self):
        self.assertEqual(self.observe(1, self.a, limit=True).code,
                         "NO_VERIFIED_WINDOW_LIMIT")
        self.assertEqual(self.observe(2, self.a, self.b, limit=1).code,
                         "OVER_VERIFIED_LIMIT")
        self.assertEqual(self.observer.identities, ())

    def test_10_duplicate_untrusted_process_or_invalid_pid_rejected(self):
        self.assertEqual(self.observe(1, self.a, self.a).code,
                         "INVALID_OR_AMBIGUOUS_CACHE")
        bad = GameWindow(19, 999, GAME_TITLE, UNITY_WINDOW_CLASS, "other.exe")
        self.assertEqual(self.observe(2, bad).code,
                         "INVALID_OR_AMBIGUOUS_CACHE")
        bad_pid = row(19, 0)
        self.assertEqual(self.observe(3, bad_pid).code,
                         "INVALID_OR_AMBIGUOUS_CACHE")

    def test_11_cleanup_native_failure_not_reported_as_success(self):
        class Failed:
            code = "HOST_CLOSED_NATIVE_CLEANUP_FAILED"
        service = C14DetachedListObserver(lambda: Failed())
        result = service.observe(snapshot(1, self.a),
                                 max_windows=2, allowed=lambda: True)
        self.assertEqual(result.code, "RENDERER_CLEANUP_FAILED")
        self.assertEqual(service.identities, ())
        exploding = C14DetachedListObserver(lambda: (_ for _ in ()).throw(OSError()))
        self.assertEqual(exploding.observe(snapshot(1, self.a),
                  max_windows=2, allowed=lambda: True).code,
                  "RENDERER_CLEANUP_FAILED")

    def test_12_wrong_thread_reset_shutdown_and_no_fake_auto_open(self):
        self.observe(5, self.a)
        out = []
        t = threading.Thread(target=lambda: out.append(
            self.observer.observe(snapshot(6, self.b),
                       max_windows=3, allowed=lambda: True).code))
        t.start()
        t.join(5)
        self.assertEqual(out, ["WRONG_TK_THREAD"])
        self.assertEqual(self.observer.identities, ((41, self.a.pid),))
        self.assertEqual(self.observer.reset().code, "RESET")
        self.assertEqual(self.observe(1, self.b).code, "LIST_CHANGED")
        self.assertEqual(self.observer.shutdown().code, "CLOSED")
        self.assertEqual(self.observe(2, self.a).code, "CLOSED")
        self.assertEqual(self.events.count("clear"), 4)
        source = (ROOT / "src/detached_list_observer.py").read_text("utf-8")
        for forbidden in ("tk.Button(", "tk.Toplevel(", "PostMessage(",
                          "CreateRemoteThread(", "ReadProcessMemory(",
                          "after(1000", "proxy_tab"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
