"""S32 per-hint provenance and offline reconnect/clone lifecycle tests."""
from __future__ import annotations
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))

from adb_identity_evidence import GuestIdentityHint,inspect_captured_adb_devices
from adb_hint_provenance import (
    HINT_LOCAL_TTL_SECONDS,HintTimes,with_hint_times,compare_adb_lifecycle,
)
from login_launch_preflight import check_open_game_preflight
from login_path import EXE_NAME,GameDirectoryResult
from permission_guard import PermissionSnapshot

HEADER="List of devices attached\n"


def view(rows, *, captured=100., hints=None, times=None):
    e=inspect_captured_adb_devices(HEADER+rows,captured_at=captured,
                                   hints_by_serial=hints)
    return with_hint_times(e,{} if times is None else times)


class S32Tests(unittest.TestCase):
    def test_independent_field_timestamps_per_serial(self):
        v=view("a device\n",hints={"a":GuestIdentityHint(
            android_id="id",guest_ipv4="10.0.0.2",hwid="hw",guest_game_pid=42)},
            times={"a":HintTimes(android_id_at=50.,guest_ipv4_at=98.,
                                 hwid_at=98.,guest_game_pid_at=99.)})
        self.assertEqual(v.assess("a","android_id",101.).code,"STALE_HINT")
        for field in ("guest_ipv4","hwid","guest_game_pid"):
            self.assertEqual(v.assess("a",field,101.).code,"FRESH_HINT_DIAGNOSTIC_ONLY")
        self.assertIsNone(v.unique_serial_for("android_id","id",101.))
        self.assertEqual(v.unique_serial_for("guest_ipv4","10.0.0.2",101.),"a")

    def test_no_timestamp_never_assumes_capture_timestamp(self):
        v=view("a device\n",hints={"a":GuestIdentityHint(android_id="id")})
        self.assertEqual(v.assess("a","android_id",101.).code,"TIMESTAMP_UNKNOWN")
        self.assertIsNone(v.unique_serial_for("android_id","id",101.))

    def test_stale_peer_blocks_unique_reverse_mapping(self):
        v=view("a device\nb device\n",hints={
            "a":GuestIdentityHint(guest_ipv4="10.0.0.2"),
            "b":GuestIdentityHint(guest_ipv4="10.0.0.3")},
            times={"a":HintTimes(guest_ipv4_at=99.),
                   "b":HintTimes(guest_ipv4_at=40.)})
        self.assertIsNone(v.unique_serial_for("guest_ipv4","10.0.0.2",101.))

    def test_peer_with_unknown_value_blocks_reverse_mapping(self):
        v=view("a device\nb device\n",hints={
            "a":GuestIdentityHint(android_id="aid")},
            times={"a":HintTimes(android_id_at=99.)})
        self.assertIsNone(v.unique_serial_for("android_id","aid",101.))

    def test_all_fresh_and_unique_allows_diagnostic_lookup_only(self):
        v=view("a device\nb device\n",hints={
            "a":GuestIdentityHint(guest_ipv4="10.0.0.2"),
            "b":GuestIdentityHint(guest_ipv4="10.0.0.3")},
            times={"a":HintTimes(guest_ipv4_at=99.),
                   "b":HintTimes(guest_ipv4_at=99.)})
        self.assertEqual(v.unique_serial_for("guest_ipv4","10.0.0.3",101.),"b")
        self.assertFalse(v.is_authoritative_account_total)

    def test_clone_same_fresh_aid_never_maps(self):
        v=view("a device\nb device\n",hints={
            "a":GuestIdentityHint(android_id="clone"),
            "b":GuestIdentityHint(android_id="clone")},
            times={"a":HintTimes(android_id_at=99.),
                   "b":HintTimes(android_id_at=99.)})
        self.assertIsNone(v.unique_serial_for("android_id","clone",101.))

    def test_offline_device_does_not_contribute_fresh_identity(self):
        v=view("a offline\n",hints={"a":GuestIdentityHint(android_id="aid")},
               times={"a":HintTimes(android_id_at=99.)})
        self.assertEqual(v.assess("a","android_id",101.).code,"TRANSPORT_NOT_ONLINE")
        self.assertIsNone(v.unique_serial_for("android_id","aid",101.))

    def test_capture_stale_overrides_recent_hint(self):
        v=view("a device\n",captured=100.,
               hints={"a":GuestIdentityHint(android_id="id")},
               times={"a":HintTimes(android_id_at=100.)})
        self.assertEqual(v.assess("a","android_id",131.).code,"CAPTURE_NOT_FRESH")
        self.assertIsNone(v.unique_serial_for("android_id","id",131.))

    def test_stale_hint_at_local_threshold(self):
        v=view("a device\n",captured=200.,
               hints={"a":GuestIdentityHint(android_id="aid")},
               times={"a":HintTimes(android_id_at=170.)})
        self.assertEqual(HINT_LOCAL_TTL_SECONDS,30.)
        self.assertTrue(v.assess("a","android_id",200.).is_fresh_diagnostic)
        self.assertEqual(v.assess("a","android_id",200.01).code,"STALE_HINT")

    def test_invalid_timestamps_fail_closed(self):
        for stamp in (True,float("nan"),float("inf"),"99",101.):
            v=view("a device\n",hints={"a":GuestIdentityHint(android_id="x")},
                   times={"a":HintTimes(android_id_at=stamp)})
            self.assertEqual(v.provenance_error,"INVALID_HINT_TIMESTAMP")
            self.assertEqual(v.assess("a","android_id",101.).code,"PROVENANCE_INVALID")

    def test_stamp_without_a_value_fails_closed(self):
        v=view("a device\n",times={"a":HintTimes(guest_ipv4_at=99.)})
        self.assertEqual(v.provenance_error,"TIMESTAMP_WITHOUT_HINT")
        self.assertIsNone(v.unique_serial_for("guest_ipv4","10.0.0.2",101.))

    def test_unknown_serial_times_not_accepted(self):
        v=view("a device\n",times={"b":HintTimes(android_id_at=99.)})
        self.assertEqual(v.provenance_error,"INVALID_SERIAL_OR_TIMES")

    def test_invalid_mapping_not_a_crash_or_grant(self):
        v=with_hint_times(inspect_captured_adb_devices(HEADER+"a device\n",
                            captured_at=100.),None)
        self.assertEqual(v.provenance_error,"INVALID_TIMESTAMP_MAPPING")
        self.assertIsNone(v.combined_running_count)

    def test_pure_time_map_is_immutable_snapshot(self):
        times={"a":HintTimes(android_id_at=99.)}
        v=view("a device\n",hints={"a":GuestIdentityHint(android_id="x")},
               times=times)
        times.clear()
        self.assertTrue(v.assess("a","android_id",101.).is_fresh_diagnostic)
        with self.assertRaises(TypeError):
            v.times_by_serial["b"]=HintTimes()

    def test_unknown_serial_or_field_never_invents_identity(self):
        v=view("a device\n",hints={"a":GuestIdentityHint(android_id="x")},
               times={"a":HintTimes(android_id_at=99.)})
        self.assertEqual(v.assess("missing","android_id",101.).code,"SERIAL_NOT_PRESENT")
        with self.assertRaises(ValueError):
            v.assess("a","wrong",101.)
        self.assertIsNone(v.unique_serial_for("guest_game_pid","123",101.))

    def test_invalid_now_age_input(self):
        v=view("a device\n")
        for now,age in ((True,1),(float("nan"),1),(101,-1),(101,True)):
            with self.assertRaises(ValueError):
                v.assess("a","android_id",now,max_age_seconds=age)

    def test_offline_to_online_transition_not_a_rebind(self):
        a=view("x offline\n",captured=100.)
        b=view("x device\n",captured=102.)
        delta=compare_adb_lifecycle(a,b,now=105.)
        self.assertEqual(delta.status,"DIAGNOSTIC_ONLY")
        self.assertEqual([t.code for t in delta.transitions],["OFFLINE_TO_ONLINE"])
        self.assertEqual(delta.possible_rebinds,())
        self.assertFalse(delta.is_authoritative_rebinding)

    def test_online_to_offline_and_disappeared_separate(self):
        a=view("x device\ny device\n",captured=100.)
        b=view("x offline\n",captured=102.)
        changes=compare_adb_lifecycle(a,b,now=105.)
        self.assertEqual({t.serial:t.code for t in changes.transitions},
                         {"x":"ONLINE_TO_UNAVAILABLE","y":"SERIAL_DISAPPEARED"})

    def test_same_aid_new_serial_possible_not_verified(self):
        a=view("old device\n",captured=100.,
               hints={"old":GuestIdentityHint(android_id="aid")},
               times={"old":HintTimes(android_id_at=99.)})
        b=view("new device\n",captured=103.,
               hints={"new":GuestIdentityHint(android_id="aid")},
               times={"new":HintTimes(android_id_at=102.)})
        result=compare_adb_lifecycle(a,b,now=105.)
        self.assertEqual(len(result.possible_rebinds),1)
        self.assertEqual(result.possible_rebinds[0].certainty,"POSSIBLE_ONLY_NOT_VERIFIED")
        self.assertEqual((result.possible_rebinds[0].previous_serial,
                          result.possible_rebinds[0].current_serial),("old","new"))

    def test_stale_old_aid_suppresses_possible_rebind(self):
        a=view("old device\n",captured=100.,
               hints={"old":GuestIdentityHint(android_id="aid")},
               times={"old":HintTimes(android_id_at=50.)})
        b=view("new device\n",captured=103.,
               hints={"new":GuestIdentityHint(android_id="aid")},
               times={"new":HintTimes(android_id_at=102.)})
        self.assertEqual(compare_adb_lifecycle(a,b,now=105.).possible_rebinds,())

    def test_clone_aid_duplicate_suppresses_possible_rebind(self):
        a=view("a device\nb device\n",captured=100.,
               hints={"a":GuestIdentityHint(android_id="same"),
                      "b":GuestIdentityHint(android_id="same")},
               times={"a":HintTimes(android_id_at=99.),
                      "b":HintTimes(android_id_at=99.)})
        c=view("c device\n",captured=102.,
               hints={"c":GuestIdentityHint(android_id="same")},
               times={"c":HintTimes(android_id_at=101.)})
        self.assertEqual(compare_adb_lifecycle(a,c,now=103.).possible_rebinds,())

    def test_both_old_and_new_serials_still_online_is_not_rebind(self):
        a=view("a device\n",captured=100.,
               hints={"a":GuestIdentityHint(android_id="id")},
               times={"a":HintTimes(android_id_at=99.)})
        b=view("a device\nb device\n",captured=103.,
               hints={"a":GuestIdentityHint(android_id="other"),
                      "b":GuestIdentityHint(android_id="id")},
               times={"a":HintTimes(android_id_at=102.),
                      "b":HintTimes(android_id_at=102.)})
        self.assertEqual(compare_adb_lifecycle(a,b,now=105.).possible_rebinds,())

    def test_stale_or_invalid_captures_suppress_transitions(self):
        a=view("a device\n",captured=100.)
        b=view("b device\n",captured=150.)
        self.assertEqual(compare_adb_lifecycle(a,b,now=155.).status,
                         "INCOMPLETE_OR_STALE")
        self.assertEqual(compare_adb_lifecycle(a,b,now=155.).transitions,())

    def test_chronology_regression_rejected(self):
        a=view("a device\n",captured=105.)
        b=view("b device\n",captured=103.)
        self.assertEqual(compare_adb_lifecycle(a,b,now=106.).status,
                         "CHRONOLOGY_INVALID")

    def test_adb_evidence_never_grants_s26_account_limits(self):
        v=view("a device\n",hints={"a":GuestIdentityHint(android_id="aid")},
               times={"a":HintTimes(android_id_at=99.)})
        with tempfile.TemporaryDirectory() as td:
            d=Path(td);(d/EXE_NAME).write_bytes(b"S32 TEST NOT GAME")
            snap=PermissionSnapshot(has_verified_payload=True,
                                    permissions=frozenset({"login_tab"}),
                                    plan_status="TEST_ONLY",max_windows=10)
            res=check_open_game_preflight(snap,GameDirectoryResult(d,""),
                                          running_windows=v.combined_running_count)
            self.assertEqual(res.reason,"RUNNING_WINDOW_COUNT_UNKNOWN")
            self.assertFalse(res.allowed)

if __name__=="__main__":
    unittest.main()
