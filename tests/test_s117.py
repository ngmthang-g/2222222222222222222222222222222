"""S117 original F02 saved/error display comes ONLY from actual S116 disk outcome."""
from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from login_existing_autosave import TLMExistingAccountAutosave
from login_account_legacy import LegacyAccountRecord
from login_existing_account_edits import ExistingAccountEditError


class FakeVar:
    def __init__(self, value):
        self.value = value
        self._traces = {}
    def get(self):
        return self.value
    def trace_add(self, mode, callback):
        token = str(len(self._traces))
        self._traces[token] = callback
        return token
    def trace_remove(self, mode, token):
        del self._traces[token]
    def set(self, value):
        self.value = value
        for callback in tuple(self._traces.values()):
            callback("fake", "fake", "write")


class FakeOwner:
    def __init__(self):
        self.events = {}
        self.next = 0
        self.cancelled = []
    def after(self, milliseconds, callback):
        self.next += 1
        self.events[self.next] = (milliseconds, callback)
        return self.next
    def after_cancel(self, event_id):
        self.cancelled.append(event_id)
        self.events.pop(event_id, None)


class FakeRows:
    def __init__(self):
        self.group_accounts = FakeOwner()
        self.username_vars = [FakeVar("S117_FAKE_USERNAME")]
        self.password_vars = [FakeVar("S117_FAKE_PASSWORD")]


class S117FeedbackTests(unittest.TestCase):
    def setup(self, callback=None, show_error=None):
        rows = FakeRows()
        statuses = []
        cb = callback if callback is not None else statuses.append
        record = LegacyAccountRecord("UNKNOWN", "S117_FAKE_USERNAME",
                                     "S117_FAKE_PASSWORD", "Có", "opaque")
        worker = TLMExistingAccountAutosave(rows, [record],
                settings_file=Path("TEST_ONLY_SHOULD_NEVER_WRITE"),
                show_error=show_error, on_save_result=cb)
        return worker, rows, statuses

    def test_01_no_success_when_no_edits(self):
        worker, _, status = self.setup()
        self.assertTrue(worker.flush())
        self.assertEqual(status, [])
        worker.shutdown()

    def test_02_300ms_is_actual_pending_event(self):
        worker, rows, status = self.setup()
        rows.username_vars[0].set("S117_CHANGED_USERNAME")
        self.assertEqual([ms for ms, cb in rows.group_accounts.events.values()], [300])
        self.assertEqual(status, [])
        with patch("login_existing_autosave.update_existing_accounts",
                   return_value="UPDATED_EXISTING_ACCOUNT_FIELDS_ONLY"):
            self.assertTrue(worker.flush())
        self.assertEqual(status, ["SAVE_CONFIRMED"])
        worker.shutdown()

    def test_03_disk_failure_emits_only_failure_and_no_success(self):
        err = []
        worker, rows, status = self.setup(show_error=lambda title, body: err.append((title, body)))
        rows.password_vars[0].set("S117_CHANGED_PASSWORD")
        with patch("login_existing_autosave.update_existing_accounts",
                   side_effect=ExistingAccountEditError("ACCOUNT_EDIT_STALE_DATA")):
            self.assertFalse(worker.flush())
        self.assertEqual(status, ["SAVE_FAILED"])
        self.assertEqual(worker.last_status, "BLOCKED_ACCOUNT_SAVE")
        self.assertEqual(len(err), 1)
        self.assertNotIn("S117_CHANGED_PASSWORD", str(err))
        # No pending saved state; do not allow accidental claim of success.
        self.assertEqual(worker._stored[0][1], "S117_FAKE_PASSWORD")
        worker._closed = True

    def test_04_unchanged_backend_never_reports_success(self):
        worker, rows, status = self.setup()
        rows.username_vars[0].set("S117_CHANGED_USERNAME")
        with patch("login_existing_autosave.update_existing_accounts",
                   return_value="UNCHANGED"):
            self.assertTrue(worker.flush())
        self.assertEqual(status, [])
        worker.shutdown()

    def test_05_malfunctioning_feedback_callback_cannot_negate_disk_result(self):
        worker, rows, _ = self.setup(callback=lambda code: (_ for _ in ()).throw(RuntimeError("test")))
        rows.username_vars[0].set("S117_CHANGED_USERNAME")
        with patch("login_existing_autosave.update_existing_accounts",
                   return_value="UPDATED_EXISTING_ACCOUNT_FIELDS_ONLY"):
            self.assertTrue(worker.flush())
        self.assertEqual(worker.last_status, "UPDATED_EXISTING_ACCOUNT_FIELDS_ONLY")
        worker.shutdown()

    def test_06_missing_feedback_callback_keeps_original_working(self):
        worker, rows, _ = self.setup(callback="NOT_CALLABLE")
        rows.username_vars[0].set("S117_CHANGED_USERNAME")
        with patch("login_existing_autosave.update_existing_accounts",
                   return_value="UPDATED_EXISTING_ACCOUNT_FIELDS_ONLY"):
            self.assertTrue(worker.flush())
        worker.shutdown()

    def test_07_close_flushes_before_detaching_traces(self):
        worker, rows, status = self.setup()
        rows.password_vars[0].set("S117_UPDATED")
        with patch("login_existing_autosave.update_existing_accounts",
                   return_value="UPDATED_EXISTING_ACCOUNT_FIELDS_ONLY"):
            self.assertTrue(worker.shutdown())
        self.assertEqual(status, ["SAVE_CONFIRMED"])
        self.assertTrue(worker._closed)
        self.assertFalse(rows.password_vars[0]._traces)

    def test_08_closed_worker_never_calls_backend(self):
        worker, rows, status = self.setup()
        worker.shutdown()
        rows.username_vars[0].set("AFTER_SHUTDOWN")
        with patch("login_existing_autosave.update_existing_accounts") as p:
            self.assertFalse(worker.flush())
            p.assert_not_called()
        self.assertFalse(status)

    def test_09_pending_multiple_edits_coalesce_single_300ms_event(self):
        worker, rows, status = self.setup()
        rows.username_vars[0].set("A")
        rows.password_vars[0].set("B")
        self.assertEqual(len(rows.group_accounts.events), 1)
        self.assertEqual(rows.group_accounts.cancelled, [1])
        worker._closed = True

    def test_10_no_interaction_with_check_captcha_or_proxy(self):
        worker, rows, _ = self.setup()
        rows.username_vars[0].set("ONLY_USERNAME")
        with patch("login_existing_autosave.update_existing_accounts",
                   return_value="UPDATED_EXISTING_ACCOUNT_FIELDS_ONLY") as p:
            self.assertTrue(worker.flush())
        (changes, path), _ = p.call_args
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0].username, "ONLY_USERNAME")
        self.assertEqual(changes[0].password, "S117_FAKE_PASSWORD")
        self.assertEqual(changes[0].expected_username, "S117_FAKE_USERNAME")
        self.assertEqual(path, Path("TEST_ONLY_SHOULD_NEVER_WRITE"))
        worker.shutdown()


if __name__ == "__main__":
    unittest.main()
