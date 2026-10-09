"""S31 P02/P05 captured ADB transport & clone identity; no commands run."""
from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))

from adb_identity_evidence import (
    LOCAL_CAPTURE_TTL_SECONDS, GuestIdentityHint,
    inspect_captured_adb_devices, identify_possible_serial_rebinds,
)
from login_path import EXE_NAME, GameDirectoryResult
from login_launch_preflight import check_open_game_preflight
from permission_guard import PermissionSnapshot

HEADER="List of devices attached\n"


class S31Tests(unittest.TestCase):
    def parsed(self, lines="", *, at=100., hints=None):
        return inspect_captured_adb_devices(HEADER+lines,captured_at=at,
                                            hints_by_serial=hints)

    def test_no_capture_is_not_zero_devices(self):
        evidence=inspect_captured_adb_devices(None,captured_at=100.)
        self.assertEqual(evidence.status,"NO_CAPTURE")
        self.assertEqual(evidence.observed_online_serials,())
        self.assertIsNone(evidence.emulator_account_count)
        self.assertIsNone(evidence.combined_running_count)

    def test_empty_header_is_parsed_but_not_license_total(self):
        e=self.parsed()
        self.assertEqual(e.status,"PARSED")
        self.assertEqual(e.transports,())
        self.assertIsNone(e.combined_running_count)
        self.assertFalse(e.is_authoritative_account_total)

    def test_captured_two_active_serials(self):
        e=self.parsed("emulator-5554\tdevice\n127.0.0.1:5557 device product:ld\n")
        self.assertEqual(e.observed_online_serials,("127.0.0.1:5557","emulator-5554"))
        self.assertEqual(len(e.transports),2)
        self.assertIsNone(e.emulator_account_count)

    def test_offline_and_unauthorized_dont_show_as_online(self):
        e=self.parsed("emulator-5554 offline\nemulator-5556 unauthorized\n")
        self.assertEqual(e.observed_online_serials,())
        self.assertEqual(e.unknown_states,("offline","unauthorized"))
        self.assertEqual(len(e.transports),2)

    def test_duplicate_serial_records_not_silently_deduplicated(self):
        e=self.parsed("x device\nx device\n")
        self.assertEqual(e.status,"AMBIGUOUS_DUPLICATE_SERIAL")
        self.assertEqual(e.duplicate_serials,("x",))
        self.assertEqual(e.observed_online_serials,())
        self.assertIsNone(e.unique_serial_for("android_id","aid",101.))

    def test_clone_duplicate_android_id_and_hwid(self):
        h={"a":GuestIdentityHint(android_id="same",hwid="same-hw"),
           "b":GuestIdentityHint(android_id="same",hwid="same-hw")}
        e=self.parsed("a device\nb device\n",hints=h)
        self.assertEqual(e.duplicate_aids,("same",))
        self.assertEqual(e.duplicate_hwids,("same-hw",))
        self.assertIsNone(e.unique_serial_for("android_id","same",101.))
        self.assertIsNone(e.unique_serial_for("hwid","same-hw",101.))

    def test_unique_guest_ip_may_disambiguate_individual_serial(self):
        h={"a":GuestIdentityHint(android_id="same",guest_ipv4="10.0.0.2"),
           "b":GuestIdentityHint(android_id="same",guest_ipv4="10.0.0.3")}
        e=self.parsed("a device\nb device\n",hints=h)
        self.assertEqual(e.duplicate_aids,("same",))
        self.assertEqual(e.unique_serial_for("guest_ipv4","10.0.0.3",101.),"b")
        self.assertIsNone(e.unique_serial_for("android_id","same",101.))

    def test_duplicate_ip_cannot_select(self):
        h={"a":GuestIdentityHint(guest_ipv4="10.0.0.2"),
           "b":GuestIdentityHint(guest_ipv4="10.0.0.2")}
        e=self.parsed("a device\nb device\n",hints=h)
        self.assertEqual(e.duplicate_guest_ips,("10.0.0.2",))
        self.assertIsNone(e.unique_serial_for("guest_ipv4","10.0.0.2",101.))

    def test_offline_hinted_device_not_selected(self):
        h={"a":GuestIdentityHint(android_id="id-a",guest_ipv4="10.0.0.2")}
        e=self.parsed("a offline\n",hints=h)
        self.assertIsNone(e.unique_serial_for("guest_ipv4","10.0.0.2",101.))

    def test_capture_stale_after_local_ttl(self):
        e=self.parsed("a device\n")
        self.assertEqual(LOCAL_CAPTURE_TTL_SECONDS,30.)
        self.assertEqual(e.freshness(130.),"FRESH_CAPTURE_DIAGNOSTIC_ONLY")
        self.assertEqual(e.freshness(130.1),"STALE_CAPTURE")
        self.assertEqual(e.observed_online_serials,("a",))

    def test_stale_reverse_lookup_returns_none(self):
        e=self.parsed("a device\n",hints={"a":GuestIdentityHint(android_id="aid")})
        self.assertIsNone(e.unique_serial_for("android_id","aid",131.))

    def test_missing_header_and_malformed_row_fail_closed(self):
        for value in ("", "not adb output", "x device\n", HEADER+"bad\n",
                      HEADER+"x mystery\n"):
            with self.subTest(text=value):
                e=inspect_captured_adb_devices(value,captured_at=100.)
                self.assertEqual(e.status,"INVALID_CAPTURE")
                self.assertEqual(e.transports,())

    def test_daemon_starting_banner_not_parsed_as_devices(self):
        e=inspect_captured_adb_devices(
            "* daemon not running; starting now at tcp:5037\n"+HEADER+"a device\n",
            captured_at=100.)
        self.assertEqual(e.status,"INVALID_CAPTURE")

    def test_reject_unbound_hint(self):
        e=self.parsed("a device\n",hints={"not-observed":GuestIdentityHint()})
        self.assertEqual((e.status,e.error),("INVALID_CAPTURE","HINT_NOT_IN_CAPTURE"))

    def test_reject_malformed_hint_and_guest_pid(self):
        for hint in (GuestIdentityHint(android_id=""),
                     GuestIdentityHint(hwid=" h "),
                     GuestIdentityHint(guest_game_pid=0),
                     GuestIdentityHint(guest_game_pid=True)):
            with self.subTest(hint=hint):
                e=self.parsed("a device\n",hints={"a":hint})
                self.assertEqual(e.status,"INVALID_CAPTURE")

    def test_capture_monotonic_timestamp_required(self):
        for at in (True,float("nan"),float("inf"),"1",None):
            with self.assertRaises(ValueError):
                inspect_captured_adb_devices(HEADER,captured_at=at)

    def test_invalid_freshness_now_threshold(self):
        e=self.parsed("a device\n")
        for now,ttl in ((float("nan"),1),(101,-1),(True,1),(101,True)):
            with self.assertRaises(ValueError):
                e.freshness(now,max_age_seconds=ttl)
        self.assertEqual(e.freshness(99.),"CLOCK_INVALID_OR_REGRESSED")

    def test_possible_rebind_same_aid_new_serial_only(self):
        old=self.parsed("old device\n",at=100.,
                        hints={"old":GuestIdentityHint(android_id="stable")})
        new=self.parsed("new device\n",at=102.,
                        hints={"new":GuestIdentityHint(android_id="stable")})
        result=identify_possible_serial_rebinds(old,new,now=105.)
        self.assertEqual(len(result),1)
        self.assertEqual(result[0].previous_serial,"old")
        self.assertEqual(result[0].current_serial,"new")
        self.assertEqual(result[0].certainty,"POSSIBLE_ONLY_NOT_VERIFIED")

    def test_duplicate_aid_blocks_automatic_rebind_inference(self):
        old=self.parsed("a device\nb device\n",
                        hints={"a":GuestIdentityHint(android_id="shared"),
                               "b":GuestIdentityHint(android_id="shared")})
        new=self.parsed("c device\n",at=102.,
                        hints={"c":GuestIdentityHint(android_id="shared")})
        self.assertEqual(identify_possible_serial_rebinds(old,new,now=105.),())

    def test_stale_rebind_not_inferred(self):
        old=self.parsed("old device\n",
                        hints={"old":GuestIdentityHint(android_id="x")})
        new=self.parsed("new device\n",at=130.,
                        hints={"new":GuestIdentityHint(android_id="x")})
        self.assertEqual(identify_possible_serial_rebinds(old,new,now=135.),())

    def test_guest_pid_is_not_windows_process_pid_or_account_count(self):
        e=self.parsed("a device\n",hints={"a":GuestIdentityHint(guest_game_pid=999)})
        self.assertEqual(e.transports[0].hint.guest_game_pid,999)
        self.assertIsNone(e.emulator_account_count)

    def test_partial_identity_cannot_open_game_via_s26(self):
        e=self.parsed("a device\nb device\n")
        with tempfile.TemporaryDirectory() as td:
            d=Path(td);(d/EXE_NAME).write_bytes(b"S31 TEST OWNED NO GAME")
            snap=PermissionSnapshot(has_verified_payload=True,
                permissions=frozenset({"login_tab"}),max_windows=5,
                plan_status="TEST_ONLY")
            result=check_open_game_preflight(snap,GameDirectoryResult(d,""),
                running_windows=e.combined_running_count)
            self.assertFalse(result.allowed)
            self.assertEqual(result.reason,"RUNNING_WINDOW_COUNT_UNKNOWN")


if __name__ == "__main__":
    unittest.main()
