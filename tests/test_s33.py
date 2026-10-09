"""S33: epoch-based invalidation of old ADB hints across reconnect/reboot."""
from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"src"))

from adb_identity_evidence import GuestIdentityHint, inspect_captured_adb_devices
from adb_hint_provenance import HintTimes, with_hint_times
from adb_serial_epochs import advance_serial_epochs
from login_path import EXE_NAME, GameDirectoryResult
from login_launch_preflight import check_open_game_preflight
from permission_guard import PermissionSnapshot

H = "List of devices attached\n"


def capture(rows: str, at: float, *, hints=None, times=None):
    c = inspect_captured_adb_devices(H+rows, captured_at=at,
                                     hints_by_serial=hints)
    return with_hint_times(c, times if times is not None else {})


def aid(serial: str, value: str, at: float):
    return ({serial: GuestIdentityHint(android_id=value)},
            {serial: HintTimes(android_id_at=at)})


class S33Tests(unittest.TestCase):
    def test_first_online_requires_hint_after_epoch_not_cache_replay(self):
        hints, times = aid("a", "same", 99.)
        a = advance_serial_epochs(None, capture("a device\n", 100.,
                                                 hints=hints, times=times))
        self.assertEqual(a.status, "BASELINE")
        self.assertEqual(a.boundary_by_serial["a"], 100.)
        self.assertEqual(a.generation_by_serial["a"], 1)
        self.assertEqual(a.assess("a","android_id",101.).code,
                         "HINT_NOT_AFTER_EPOCH")
        self.assertIsNone(a.unique_serial_for("android_id","same",101.))

    def test_equal_boundary_timestamp_is_untrusted(self):
        hints,times=aid("a","x",100.)
        a=advance_serial_epochs(None,capture("a device\n",100.,hints=hints,times=times))
        self.assertEqual(a.assess("a","android_id",101.).code,"HINT_NOT_AFTER_EPOCH")

    def test_subsequent_same_session_new_hint_becomes_eligible(self):
        a=advance_serial_epochs(None,capture("a device\n",100.))
        h,t=aid("a","x",101.)
        b=advance_serial_epochs(a,capture("a device\n",102.,hints=h,times=t))
        self.assertEqual(b.status,"CONSISTENT_HISTORY")
        self.assertEqual(b.boundary_by_serial["a"],100.)
        self.assertEqual(b.generation_by_serial["a"],1)
        self.assertTrue(b.assess("a","android_id",103.).is_fresh_diagnostic)
        self.assertEqual(b.unique_serial_for("android_id","x",103.),"a")

    def test_offline_disposes_epoch_and_old_aid(self):
        a=advance_serial_epochs(None,capture("a device\n",100.))
        b=advance_serial_epochs(a,capture("a offline\n",102.))
        self.assertIsNone(b.boundary_by_serial["a"])
        self.assertEqual([x.code for x in b.events],["EPOCH_ENDED_offline"])
        h,t=aid("a","old",101.)
        c=advance_serial_epochs(b,capture("a device\n",104.,hints=h,times=t))
        self.assertEqual(c.generation_by_serial["a"],2)
        self.assertEqual(c.boundary_by_serial["a"],104.)
        self.assertEqual(c.assess("a","android_id",105.).code,"HINT_NOT_AFTER_EPOCH")

    def test_reconnect_then_newly_observed_aid(self):
        a=advance_serial_epochs(None,capture("a device\n",100.))
        b=advance_serial_epochs(a,capture("a offline\n",102.))
        c=advance_serial_epochs(b,capture("a device\n",104.))
        h,t=aid("a","new",105.)
        d=advance_serial_epochs(c,capture("a device\n",106.,hints=h,times=t))
        self.assertTrue(d.assess("a","android_id",107.).is_fresh_diagnostic)
        self.assertEqual(d.generation_by_serial["a"],2)

    def test_disappear_reappear_starts_new_epoch(self):
        a=advance_serial_epochs(None,capture("a device\n",100.))
        b=advance_serial_epochs(a,capture("",102.))
        self.assertEqual(b.state_by_serial["a"],"ABSENT")
        c=advance_serial_epochs(b,capture("a device\n",105.))
        self.assertEqual(c.generation_by_serial["a"],2)
        self.assertEqual(c.boundary_by_serial["a"],105.)

    def test_unauthorized_and_recovery_starts_new_generation(self):
        a=advance_serial_epochs(None,capture("a device\n",100.))
        b=advance_serial_epochs(a,capture("a unauthorized\n",102.))
        self.assertIsNone(b.boundary_by_serial["a"])
        c=advance_serial_epochs(b,capture("a device\n",104.))
        self.assertEqual(c.generation_by_serial["a"],2)

    def test_explicit_observed_reboot_same_visible_serial_invalidates(self):
        a=advance_serial_epochs(None,capture("a device\n",100.))
        h,t=aid("a","old",101.)
        b=advance_serial_epochs(a,capture("a device\n",102.,hints=h,times=t))
        self.assertTrue(b.assess("a","android_id",103.).is_fresh_diagnostic)
        c=advance_serial_epochs(b,capture("a device\n",104.,hints=h,times=t),
                                observed_reboots=("a",))
        self.assertEqual(c.generation_by_serial["a"],2)
        self.assertEqual(c.assess("a","android_id",105.).code,"HINT_NOT_AFTER_EPOCH")
        self.assertIn("EXPLICIT_REBOOT_NEW_EPOCH",[e.code for e in c.events])

    def test_invalid_or_unknown_reboot_marker_blocks_capture(self):
        a=advance_serial_epochs(None,capture("a device\n",100.))
        for markers in (("missing",),("a","a"),(1,)):
            b=advance_serial_epochs(a,capture("a device\n",102.),
                                    observed_reboots=markers)
            self.assertEqual(b.status,"INVALID_CAPTURE_OR_EPOCH_MARKERS")
            self.assertIsNone(b.unique_serial_for("android_id","x",103.))

    def test_duplicate_serial_capture_invalid(self):
        a=advance_serial_epochs(None,capture("a device\na device\n",100.))
        self.assertEqual(a.status,"INVALID_CAPTURE_OR_EPOCH_MARKERS")
        self.assertFalse(a.is_authoritative_account_total)

    def test_invalid_hint_provenance_invalidates_epoch(self):
        c=capture("a device\n",100.,hints={"a":GuestIdentityHint(android_id="x")},
                  times={"a":HintTimes(android_id_at=101.)})
        self.assertEqual(advance_serial_epochs(None,c).status,
                         "INVALID_CAPTURE_OR_EPOCH_MARKERS")

    def test_nonincreasing_time_fails_closed(self):
        a=advance_serial_epochs(None,capture("a device\n",100.))
        for t in (100.,99.):
            b=advance_serial_epochs(a,capture("a device\n",t))
            self.assertEqual(b.status,"NON_INCREASING_CAPTURE_TIME")
            self.assertIsNone(b.combined_running_count)

    def test_history_gap_forces_new_boundary(self):
        a=advance_serial_epochs(None,capture("a device\n",100.))
        h,t=aid("a","aid",129.)
        b=advance_serial_epochs(a,capture("a device\n",140.,hints=h,times=t))
        self.assertEqual(b.status,"BASELINE")
        self.assertEqual(b.boundary_by_serial["a"],140.)
        self.assertEqual(b.assess("a","android_id",141.).code,"HINT_NOT_AFTER_EPOCH")
        self.assertIn("HISTORY_GAP_REBASELINE",[e.code for e in b.events])

    def test_recover_from_invalid_epoch_requires_new_baseline(self):
        a=advance_serial_epochs(None,capture("a device\n",100.))
        bad=advance_serial_epochs(a,capture("a device\n",102.),
                                  observed_reboots=("missing",))
        self.assertEqual(bad.status,"INVALID_CAPTURE_OR_EPOCH_MARKERS")
        good=advance_serial_epochs(bad,capture("a device\n",105.))
        self.assertEqual(good.status,"BASELINE")
        self.assertEqual(good.boundary_by_serial["a"],105.)

    def test_unknown_peer_hint_blocks_uniqueness_after_epoch(self):
        a=advance_serial_epochs(None,capture("a device\nb device\n",100.))
        h,t=aid("a","x",101.)
        b=advance_serial_epochs(a,capture("a device\nb device\n",102.,
                                            hints=h,times=t))
        self.assertIsNone(b.unique_serial_for("android_id","x",103.))

    def test_two_fresh_distinct_hints_unique_diagnostic(self):
        a=advance_serial_epochs(None,capture("a device\nb device\n",100.))
        h={"a":GuestIdentityHint(guest_ipv4="10.0.0.2"),
           "b":GuestIdentityHint(guest_ipv4="10.0.0.3")}
        t={"a":HintTimes(guest_ipv4_at=101.),
           "b":HintTimes(guest_ipv4_at=101.)}
        b=advance_serial_epochs(a,capture("a device\nb device\n",102.,hints=h,times=t))
        self.assertEqual(b.unique_serial_for("guest_ipv4","10.0.0.3",103.),"b")
        self.assertFalse(b.is_authoritative_account_total)

    def test_clone_duplicate_aid_still_rejected(self):
        a=advance_serial_epochs(None,capture("a device\nb device\n",100.))
        h={"a":GuestIdentityHint(android_id="CLONE"),
           "b":GuestIdentityHint(android_id="CLONE")}
        t={"a":HintTimes(android_id_at=101.),
           "b":HintTimes(android_id_at=101.)}
        b=advance_serial_epochs(a,capture("a device\nb device\n",102.,
                                           hints=h,times=t))
        self.assertIsNone(b.unique_serial_for("android_id","CLONE",103.))

    def test_peer_reconnected_old_ip_blocks_other_ip(self):
        a=advance_serial_epochs(None,capture("a device\nb device\n",100.))
        h={"a":GuestIdentityHint(guest_ipv4="10.0.0.2"),
           "b":GuestIdentityHint(guest_ipv4="10.0.0.3")}
        t={"a":HintTimes(guest_ipv4_at=101.),
           "b":HintTimes(guest_ipv4_at=101.)}
        b=advance_serial_epochs(a,capture("a device\nb device\n",102.,
                                           hints=h,times=t))
        self.assertEqual(b.unique_serial_for("guest_ipv4","10.0.0.2",103.),"a")
        c=advance_serial_epochs(b,capture("a offline\nb device\n",104.))
        d=advance_serial_epochs(c,capture("a device\nb device\n",106.,
                                           hints=h,times=t))
        self.assertIsNone(d.unique_serial_for("guest_ipv4","10.0.0.3",107.))

    def test_snapshot_mappings_are_immutable_copies(self):
        a=advance_serial_epochs(None,capture("a device\n",100.))
        with self.assertRaises(TypeError):
            a.state_by_serial["a"]="offline"
        with self.assertRaises(TypeError):
            a.boundary_by_serial["a"]=99.

    def test_offline_cannot_get_epoch_hints(self):
        a=advance_serial_epochs(None,capture("a offline\n",100.))
        self.assertIsNone(a.boundary_by_serial["a"])
        self.assertEqual(a.generation_by_serial["a"],0)

    def test_no_game_limit_grant_ever(self):
        a=advance_serial_epochs(None,capture("a device\n",100.))
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/EXE_NAME).write_bytes(b"S33 TEST ONLY")
            snap=PermissionSnapshot(has_verified_payload=True,
                                     permissions=frozenset({"login_tab"}),
                                     plan_status="TEST_ONLY",max_windows=4)
            denied=check_open_game_preflight(
                snap,GameDirectoryResult(root,""),
                running_windows=a.combined_running_count)
            self.assertFalse(denied.allowed)
            self.assertEqual(denied.reason,"RUNNING_WINDOW_COUNT_UNKNOWN")

    def test_no_serial_inference_from_same_aid(self):
        a=advance_serial_epochs(None,capture("old device\n",100.))
        h,t=aid("new","shared",104.)
        b=advance_serial_epochs(a,capture("new device\n",105.,
                                           hints=h,times=t))
        self.assertEqual(b.generation_by_serial["new"],1)
        self.assertEqual(b.state_by_serial["old"],"ABSENT")
        self.assertEqual(b.assess("new","android_id",106.).code,
                         "HINT_NOT_AFTER_EPOCH")

if __name__=="__main__":
    unittest.main()
