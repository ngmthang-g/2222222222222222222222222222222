"""S34 offline S31 -> S32 -> S33 strict intake facade; no emulator control."""
from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from adb_identity_evidence import GuestIdentityHint
from adb_hint_provenance import HintTimes
from adb_offline_intake import CapturedAdbFrame, OfflineAdbIntake
from login_path import EXE_NAME, GameDirectoryResult
from login_launch_preflight import check_open_game_preflight
from permission_guard import PermissionSnapshot

H = "List of devices attached\n"

def frame(rows="a device\n", at=100., *, hints=None, stamps=None, reboot=()):
    return CapturedAdbFrame(H+rows, at, hints, stamps, reboot)

def hint(serial="a", value="aid", at=101.):
    return ({serial: GuestIdentityHint(android_id=value)},
            {serial: HintTimes(android_id_at=at)})


class S34Tests(unittest.TestCase):
    def test_first_online_snapshot_must_not_trust_cached_identity(self):
        h,t=hint(at=99.)
        f=OfflineAdbIntake()
        r=f.ingest(frame(at=100.,hints=h,stamps=t),now=102.)
        self.assertEqual((r.status,r.epoch_status),
                         ("ACCEPTED_DIAGNOSTIC_ONLY","BASELINE"))
        self.assertEqual(f.lookup("android_id","aid",now=102.).code,
                         "AMBIGUOUS_OR_UNVERIFIED")
        self.assertFalse(r.is_authoritative_account_total)

    def test_second_capture_after_epoch_enables_only_diagnostic(self):
        f=OfflineAdbIntake()
        f.ingest(frame(at=100.),now=103.)
        h,t=hint(at=101.)
        r=f.ingest(frame(at=102.,hints=h,stamps=t),now=103.)
        result=f.lookup("android_id","aid",now=103.)
        self.assertEqual(r.epoch_status,"CONSISTENT_HISTORY")
        self.assertEqual((result.code,result.serial),
                         ("UNIQUE_DIAGNOSTIC_ONLY","a"))
        self.assertFalse(result.may_control_device)

    def test_s32_stale_hint_cannot_pass_facade(self):
        f=OfflineAdbIntake()
        f.ingest(frame(at=100.),now=105.)
        h,t=hint(at=40.)
        f.ingest(frame(at=102.,hints=h,stamps=t),now=105.)
        self.assertIsNone(f.lookup("android_id","aid",now=105.).serial)

    def test_transport_fresh_but_missing_hint_timestamp_not_trusted(self):
        f=OfflineAdbIntake()
        f.ingest(frame(at=100.),now=105.)
        h,_=hint(at=101.)
        f.ingest(frame(at=102.,hints=h),now=105.)
        self.assertIsNone(f.lookup("android_id","aid",now=105.).serial)

    def test_clone_two_same_android_ids_are_ambiguous(self):
        f=OfflineAdbIntake()
        f.ingest(frame("a device\nb device\n",100.),now=103.)
        h={"a":GuestIdentityHint(android_id="clone"),
           "b":GuestIdentityHint(android_id="clone")}
        t={"a":HintTimes(android_id_at=101.),
           "b":HintTimes(android_id_at=101.)}
        f.ingest(frame("a device\nb device\n",102.,hints=h,stamps=t),now=103.)
        self.assertEqual(f.lookup("android_id","clone",now=103.).code,
                         "AMBIGUOUS_OR_UNVERIFIED")

    def test_other_peer_without_new_aid_blocks_claim(self):
        f=OfflineAdbIntake()
        f.ingest(frame("a device\nb device\n",100.),now=103.)
        h,t=hint(at=101.)
        f.ingest(frame("a device\nb device\n",102.,hints=h,stamps=t),now=103.)
        self.assertIsNone(f.lookup("android_id","aid",now=103.).serial)

    def test_offline_then_online_requires_new_post_epoch_hint(self):
        f=OfflineAdbIntake()
        f.ingest(frame(at=100.),now=107.)
        h,t=hint(at=101.)
        f.ingest(frame(at=102.,hints=h,stamps=t),now=107.)
        self.assertEqual(f.lookup("android_id","aid",now=107.).serial,"a")
        end=f.ingest(frame("a offline\n",104.),now=107.)
        self.assertIn("EPOCH_ENDED_offline",end.epoch_events)
        rejoin=f.ingest(frame(at=106.,hints=h,stamps=t),now=107.)
        self.assertIn("ONLINE_AFTER_UNAVAILABLE",rejoin.epoch_events)
        self.assertIsNone(f.lookup("android_id","aid",now=107.).serial)

    def test_reconnect_then_refreshed_hint_restores_diagnostic(self):
        f=OfflineAdbIntake()
        f.ingest(frame(at=100.),now=108.)
        f.ingest(frame("a offline\n",102.),now=108.)
        f.ingest(frame(at=104.),now=108.)
        h,t=hint(at=105.)
        f.ingest(frame(at=106.,hints=h,stamps=t),now=108.)
        self.assertEqual(f.lookup("android_id","aid",now=108.).serial,"a")

    def test_caller_observed_reboot_invalidates_cached_hint(self):
        f=OfflineAdbIntake()
        f.ingest(frame(at=100.),now=107.)
        h,t=hint(at=101.)
        f.ingest(frame(at=102.,hints=h,stamps=t),now=107.)
        receipt=f.ingest(frame(at=104.,hints=h,stamps=t,
                               reboot=("a",)),now=107.)
        self.assertIn("EXPLICIT_REBOOT_NEW_EPOCH",receipt.epoch_events)
        self.assertIsNone(f.lookup("android_id","aid",now=107.).serial)

    def test_missing_capture_resets_history_not_just_hides_row(self):
        f=OfflineAdbIntake()
        f.ingest(frame(at=100.),now=107.)
        h,t=hint(at=101.)
        f.ingest(frame(at=102.,hints=h,stamps=t),now=107.)
        self.assertIsNotNone(f.lookup("android_id","aid",now=107.).serial)
        missing=f.ingest(CapturedAdbFrame(None,104.),now=107.)
        self.assertEqual(missing.status,"REJECTED")
        self.assertEqual(missing.detail,"S31_NO_CAPTURE")
        self.assertEqual(f.lookup("android_id","aid",now=107.).code,
                         "NO_ACCEPTED_EPOCH")
        # Next online capture cannot trust old cached hint.
        f.ingest(frame(at=106.,hints=h,stamps=t),now=107.)
        self.assertIsNone(f.lookup("android_id","aid",now=107.).serial)

    def test_malformed_transport_reset_discards_history(self):
        f=OfflineAdbIntake()
        f.ingest(frame(at=100.),now=103.)
        receipt=f.ingest(CapturedAdbFrame("bad header",102.),now=103.)
        self.assertEqual(receipt.detail,"S31_INVALID_CAPTURE")
        self.assertEqual(f.last_receipt,receipt)

    def test_duplicate_serial_fails_and_clears_history(self):
        f=OfflineAdbIntake()
        f.ingest(frame(at=100.),now=104.)
        bad=f.ingest(frame("a device\na device\n",at=102.),now=104.)
        self.assertEqual(bad.detail,"S31_AMBIGUOUS_DUPLICATE_SERIAL")
        self.assertIsNone(f.lookup("android_id","aid",now=104.).serial)

    def test_invalid_s32_timestamp_rejected_before_epoch(self):
        f=OfflineAdbIntake()
        h,t=hint(at=999.)
        r=f.ingest(frame(at=100.,hints=h,stamps=t),now=103.)
        self.assertEqual(r.detail,"S32_INVALID_HINT_TIMESTAMP")

    def test_nonmonotonic_replayed_frame_fails_closed(self):
        f=OfflineAdbIntake()
        f.ingest(frame(at=100.),now=105.)
        r=f.ingest(frame(at=100.),now=105.)
        self.assertEqual(r.detail,"S33_NON_INCREASING_CAPTURE_TIME")
        self.assertEqual(f.lookup("android_id","aid",now=105.).code,
                         "NO_ACCEPTED_EPOCH")

    def test_post_replay_capture_starts_new_boundary(self):
        f=OfflineAdbIntake()
        f.ingest(frame(at=100.),now=105.)
        f.ingest(frame(at=100.),now=105.)
        h,t=hint(at=101.)
        f.ingest(frame(at=102.,hints=h,stamps=t),now=105.)
        self.assertIsNone(f.lookup("android_id","aid",now=105.).serial)

    def test_future_capture_clock_refused(self):
        f=OfflineAdbIntake()
        r=f.ingest(frame(at=110.),now=105.)
        self.assertEqual(r.detail,"CAPTURE_OUTSIDE_LOCAL_WINDOW")

    def test_stale_capture_clock_refused(self):
        f=OfflineAdbIntake()
        r=f.ingest(frame(at=100.),now=131.)
        self.assertEqual(r.detail,"CAPTURE_OUTSIDE_LOCAL_WINDOW")

    def test_unknown_host_clock_refused(self):
        f=OfflineAdbIntake()
        for value in (None,True,float("nan"),float("inf")):
            self.assertEqual(f.ingest(frame(at=100.),now=value).status,
                             "REJECTED")

    def test_invalid_external_reboot_marker_rejected(self):
        f=OfflineAdbIntake()
        f.ingest(frame(at=100.),now=105.)
        r=f.ingest(frame(at=102.,reboot=("unknown",)),now=105.)
        self.assertEqual(r.detail,"S33_INVALID_CAPTURE_OR_EPOCH_MARKERS")

    def test_invalid_hint_mapping_rejected(self):
        f=OfflineAdbIntake()
        r=f.ingest(frame(at=100.,stamps={"unknown":HintTimes()}),now=101.)
        self.assertEqual(r.detail,"S32_INVALID_SERIAL_OR_TIMES")

    def test_only_strict_lookup_api_is_exported(self):
        f=OfflineAdbIntake()
        self.assertFalse(hasattr(f,"capture"))
        self.assertFalse(hasattr(f,"timed"))
        self.assertFalse(hasattr(f,"serial_for_aid"))
        self.assertFalse(hasattr(f.last_receipt,"capture"))
        self.assertFalse(hasattr(f.last_receipt,"view"))

    def test_batch_replay_does_not_sort_or_skip_bad_frame(self):
        f=OfflineAdbIntake()
        h,t=hint(at=101.)
        receipts=f.replay((frame(at=100.),
                           frame(at=102.,hints=h,stamps=t),
                           frame(at=102.,hints=h,stamps=t),
                           frame(at=104.,hints=h,stamps=t)),now=105.)
        self.assertEqual(len(receipts),4)
        self.assertEqual(receipts[0].epoch_status,"BASELINE")
        self.assertEqual(receipts[1].epoch_status,"CONSISTENT_HISTORY")
        self.assertEqual(receipts[2].detail,"S33_NON_INCREASING_CAPTURE_TIME")
        self.assertEqual(receipts[3].epoch_status,"BASELINE")
        self.assertIsNone(f.lookup("android_id","aid",now=105.).serial)

    def test_empty_batch_preserves_history_without_making_new_proof(self):
        f=OfflineAdbIntake()
        self.assertEqual(f.replay((),now=103.),())
        self.assertEqual(f.last_receipt.status,"NO_CAPTURE")

    def test_invalid_batch_not_a_success(self):
        f=OfflineAdbIntake()
        self.assertEqual(f.replay(None,now=103.)[0].status,"REJECTED")

    def test_account_limits_can_never_be_inferred_from_intake(self):
        f=OfflineAdbIntake()
        r=f.ingest(frame(at=100.),now=103.)
        with tempfile.TemporaryDirectory() as td:
            d=Path(td);(d/EXE_NAME).write_bytes(b"S34 TEST OWNED NO GAME")
            snapshot=PermissionSnapshot(
                has_verified_payload=True,
                permissions=frozenset({"login_tab"}),
                plan_status="TEST_ONLY", max_windows=4)
            p=check_open_game_preflight(
                snapshot, GameDirectoryResult(d,""),
                running_windows=r.combined_running_count)
            self.assertFalse(p.allowed)
            self.assertEqual(p.reason,"RUNNING_WINDOW_COUNT_UNKNOWN")
            self.assertIsNone(r.emulator_account_count)

    def test_no_control_authority_from_valid_lookup(self):
        f=OfflineAdbIntake()
        f.ingest(frame(at=100.),now=103.)
        h,t=hint(at=101.)
        f.ingest(frame(at=102.,hints=h,stamps=t),now=103.)
        lookup=f.lookup("android_id","aid",now=103.)
        self.assertEqual(lookup.code,"UNIQUE_DIAGNOSTIC_ONLY")
        self.assertFalse(lookup.may_control_device)
        self.assertFalse(lookup.is_authoritative_account_total)


if __name__=="__main__":
    unittest.main()
