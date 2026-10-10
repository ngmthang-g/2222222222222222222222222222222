"""S90 G02/G03: cached HWND/PID generation, genuine RoleName provenance boundaries."""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from start_windows import GameWindow
from start_polling import WindowSnapshot
from auto_role_provenance import RoleReading
from party_roster import (
    PARTY_REFRESH_MS, PartyMember, PartyRoster, PartyRosterResult,
    TkPartyRosterRefresh, prepare_roster,
)


def window(hwnd=101, pid=1001):
    return GameWindow(hwnd, pid, "TEST-OWNED TITLE - NOT ROLE", "TEST_ONLY", "not-game.exe")


def snap(rev=1, *windows, valid=True):
    return WindowSnapshot(revision=rev, windows=tuple(windows), valid=valid)


class Producer:
    def __init__(self, snapshot):
        self.snapshot = snapshot
        self.reads = 0
        self.starts = 0

    def read_snapshot(self):
        self.reads += 1
        return self.snapshot


class ClockRoot:
    def __init__(self):
        self.calls = []
        self.jobs = {}
        self.index = 0

    def after(self, delay, callback):
        self.index += 1
        self.calls.append(delay)
        self.jobs[self.index] = (delay, callback)
        return self.index

    def after_cancel(self, token):
        self.jobs.pop(token, None)

    def fire(self, delay):
        token = next(k for k, (ms, _) in self.jobs.items() if ms == delay)
        _, callback = self.jobs.pop(token)
        callback()


class S90RosterTests(unittest.TestCase):
    def test_01_original_party_refresh_interval(self):
        self.assertEqual(PARTY_REFRESH_MS, 3000)

    def test_02_invalid_start_cache_cannot_prove_game_members(self):
        self.assertEqual(prepare_roster(WindowSnapshot()).code, "INVALID_START_CACHE")

    def test_03_without_role_reader_keep_hwnd_but_no_guessed_name(self):
        out = prepare_roster(snap(1, window()))
        self.assertEqual(out.code, "ROLE_READER_UNAVAILABLE")
        self.assertEqual(out.members, (PartyMember(101, 1001, None),))
        self.assertNotIn("TEST-OWNED TITLE", str(out.members))

    def test_04_correct_reader_supplies_sanitized_role_name_only(self):
        result = prepare_roster(
            snap(1, window()),
            lambda hwnd, pid: RoleReading(hwnd, pid, " <font color=red>Thiên Địa</font> "))
        self.assertEqual(result.code, "ROLE_NAMES_READ")
        self.assertEqual(result.members[0].role_name, "Thiên Địa")

    def test_05_bad_identity_never_uses_wrong_role_name(self):
        out = prepare_roster(snap(1, window()), lambda h, p: RoleReading(h, p + 1, "Wrong"))
        self.assertEqual(out.code, "ROLE_READ_PARTIAL")
        self.assertIsNone(out.members[0].role_name)

    def test_06_reader_throw_does_not_guess_title_or_fabricate(self):
        def fail(_h, _p):
            raise OSError("NO_AUTHENTIC_GAME_READER")
        out = prepare_roster(snap(1, window()), fail)
        self.assertEqual(out.code, "ROLE_READ_PARTIAL")
        self.assertIsNone(out.members[0].role_name)

    def test_07_numeric_hwnd_pid_reuse_strips_old_name(self):
        roster = PartyRoster()
        a = snap(1, window(101, 1001))
        r = prepare_roster(a, lambda h, p: RoleReading(h, p, "Old Character"))
        self.assertTrue(roster.apply(r, a))
        self.assertEqual(roster.ready_names(), ("Old Character",))
        b = snap(2, window(101, 2002))
        self.assertFalse(roster.apply(r, b))
        self.assertEqual(roster.ready_names(), ())
        self.assertEqual(roster.code, "STALE_WORKER_RESULT")

    def test_08_same_generation_updated_name_not_pid_rename(self):
        roster = PartyRoster()
        a = snap(1, window())
        roster.apply(prepare_roster(a), a)
        b = snap(2, window())
        roster.apply(prepare_roster(b, lambda h, p: RoleReading(h, p, "Live")), b)
        self.assertEqual(roster.members[0].pid, 1001)
        self.assertEqual(roster.ready_names(), ("Live",))

    def test_09_closed_hwnd_no_old_members(self):
        roster = PartyRoster()
        a = snap(1, window())
        roster.apply(prepare_roster(a, lambda h,p:RoleReading(h,p,"Character")),a)
        b = snap(2)
        self.assertFalse(roster.apply(prepare_roster(a), b))
        self.assertEqual(roster.members, ())

    def test_10_invalid_revision_rejects_old_worker_even_same_hwnd_pid(self):
        a = snap(1, window())
        b = snap(2, window())
        roster = PartyRoster()
        self.assertFalse(roster.apply(prepare_roster(a), b))

    def test_11_duplicate_hwnd_cache_is_not_accepted(self):
        result = prepare_roster(snap(1, window(), window(101, 9000)))
        self.assertEqual(result.code, "INVALID_START_CACHE")

    def test_12_ready_list_omits_selected(self):
        a = snap(1, window(1, 10), window(2, 20))
        result = prepare_roster(
            a, lambda h,p:RoleReading(h,p,"Acc "+str(h)))
        roster = PartyRoster()
        self.assertTrue(roster.apply(result, a))
        self.assertEqual(roster.ready_names(("Acc 1",)), ("Acc 2",))

    def test_13_ambiguous_duplicate_character_names_hidden(self):
        a = snap(1, window(1, 10), window(2, 20))
        roster = PartyRoster()
        roster.apply(prepare_roster(a, lambda h,p:RoleReading(h,p,"Same")),a)
        self.assertEqual(roster.ready_names(), ())

    def test_14_no_read_allows_only_real_role_readings(self):
        a = snap(1, window(1, 10), window(2, 20))
        roster = PartyRoster()
        roster.apply(prepare_roster(a),a)
        self.assertEqual(roster.ready_names(), ())
        self.assertEqual(len(roster.members), 2)

    def test_15_poller_only_uses_existing_start_cache_no_new_scan(self):
        root=ClockRoot()
        producer=Producer(snap(1, window()))
        changes=[]
        controller=TkPartyRosterRefresh(root, producer, changes.append)
        controller.start()
        self.assertEqual(root.calls, [PARTY_REFRESH_MS])
        self.assertEqual(producer.reads, 0)
        self.assertEqual(producer.starts, 0)
        controller.shutdown()

    def test_16_worker_result_handoff_remains_tk_owner_only(self):
        root=ClockRoot()
        producer=Producer(snap(1, window()))
        changes=[]
        controller=TkPartyRosterRefresh(root, producer, changes.append)
        controller.start()
        # Exercise the immutable worker result/queue while Tk fake stays idle.
        controller._read_worker(controller._generation, producer.snapshot)
        self.assertEqual(changes, [])
        controller._working=True
        controller._handoff(controller._generation)
        self.assertEqual(changes[-1].code, "ROLE_READER_UNAVAILABLE")
        self.assertEqual(changes[-1].ready_names(), ())
        controller.shutdown()

    def test_17_stale_worker_after_stop_cannot_publish(self):
        root=ClockRoot()
        producer=Producer(snap(1, window()))
        states=[]
        ctl=TkPartyRosterRefresh(root,producer,lambda r:states.append(r.code))
        ctl.start()
        old=ctl._generation
        ctl.stop()
        ctl._read_worker(old, producer.snapshot)
        ctl._handoff(old)
        self.assertEqual(states, ["STOPPED"])
        self.assertEqual(ctl.roster.members, ())

    def test_18_permission_or_server_revocation_lifecycle_shutdown_idempotent(self):
        root=ClockRoot()
        ctl=TkPartyRosterRefresh(root, Producer(snap(1,window())),lambda r:None)
        ctl.start()
        self.assertTrue(ctl.active)
        ctl.shutdown()
        ctl.shutdown()
        self.assertFalse(ctl.active)
        self.assertEqual(root.jobs, {})
        ctl.start()
        self.assertEqual(root.jobs, {})

    def test_19_worker_late_result_with_updated_pid_discards(self):
        a = snap(1, window(1, 10))
        b = snap(2, window(1, 11))
        root=ClockRoot()
        producer=Producer(a)
        ctl=TkPartyRosterRefresh(root, producer, lambda r:None,
                                 read_role=lambda h,p:RoleReading(h,p,"Old"))
        ctl.start()
        ctl._read_worker(ctl._generation, a)
        producer.snapshot=b
        ctl._handoff(ctl._generation)
        self.assertEqual(ctl.roster.code, "STALE_WORKER_RESULT")
        self.assertEqual(ctl.roster.ready_names(), ())
        ctl.shutdown()

    def test_20_no_additional_local_enumeration_or_game_packet(self):
        code=(ROOT/"src/party_roster.py").read_text("utf-8")
        for forbidden in ("EnumWindows(", "CreateRemoteThread(", "ReadProcessMemory(",
                          "PostMessage(", "TOKEN_HMAC_SECRET", "200051",
                          "AutoAcceptInviteTeam", "read_team_id("):
            self.assertNotIn(forbidden,code)


if __name__=="__main__":
    unittest.main()
