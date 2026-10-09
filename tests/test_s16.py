"""S16 C16 native WM_CLOSE is a destructive action: fail-closed unit checks.

All rows here are synthetic test-only GameWindow data and a fake backend;
never send a WM_CLOSE to a real user/game window during unit tests.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from close_windows import C16CloseAll, CloseResult, WM_CLOSE
from start_polling import WindowSnapshot
from start_windows import GAME_PROCESS, GAME_TITLE, GameWindow, UNITY_WINDOW_CLASS
from start_tab import TLMStartTab


def game(hwnd, pid=None):
    return GameWindow(hwnd, pid or (10000 + hwnd), GAME_TITLE,
                      UNITY_WINDOW_CLASS, GAME_PROCESS)


class Backend:
    def __init__(self, rows):
        self.actual = {item.hwnd: item for item in rows}
        self.top_level = [item.hwnd for item in rows]
        self.vis = {}
        self.names = {}
        self.classes = {}
        self.titles = {}
        self.processes = {}
        self.bump_before_post = set()
        self.enumerations = 0
        self.fail_enum = False
    def enumerate_top_level(self):
        self.enumerations += 1
        if self.fail_enum:
            raise OSError("TEST_ONLY EnumWindows failure")
        return tuple(self.top_level)
    def is_window(self, hwnd):
        return hwnd in self.actual
    def is_visible(self, hwnd):
        return self.vis.get(hwnd, True)
    def process_id(self, hwnd):
        return self.actual[hwnd].pid if hwnd in self.actual else 0
    def process_executable(self, pid):
        return self.processes.get(pid, GAME_PROCESS)
    def window_class(self, hwnd):
        return self.classes.get(hwnd, UNITY_WINDOW_CLASS)
    def title_with_timeout(self, hwnd, timeout_ms):
        assert timeout_ms == 150
        return self.titles.get(hwnd, GAME_TITLE)


class Poster:
    def __init__(self, backend=None):
        self.sent = []
        self.fail = set()
        self.backend = backend
    def post_close(self, hwnd):
        self.sent.append((hwnd, WM_CLOSE, 0, 0))
        return hwnd not in self.fail


def ready(rows):
    backend = Backend(rows)
    poster = Poster(backend)
    return C16CloseAll(backend, poster), backend, poster


def snap(*rows, valid=True):
    return WindowSnapshot(3, tuple(rows), valid)


class S16NativeCloseTests(unittest.TestCase):
    def test_windows_message_original_constant(self):
        self.assertEqual(WM_CLOSE, 0x0010)

    def test_all_three_valid_game_windows_receive_real_close_requests(self):
        rows = [game(51), game(52), game(53)]
        svc, backend, poster = ready(rows)
        result = svc.close_all_game_windows(snap(*rows))
        self.assertEqual(result, CloseResult("WM_CLOSE_POSTED", 3, (51, 52, 53)))
        self.assertEqual(poster.sent, [(h, 16, 0, 0) for h in (51, 52, 53)])
        self.assertEqual(backend.enumerations, 1)

    def test_invalid_cache_makes_no_call(self):
        rows = [game(50)]
        svc, backend, poster = ready(rows)
        r = svc.close_all_game_windows(snap(*rows, valid=False))
        self.assertEqual(r.code, "INVALID_CACHE")
        self.assertFalse(poster.sent)
        self.assertEqual(backend.enumerations, 0)

    def test_non_snapshot_object_fails_closed(self):
        svc, backend, poster = ready([game(10)])
        self.assertEqual(svc.close_all_game_windows(None).code, "INVALID_CACHE")
        self.assertFalse(poster.sent)

    def test_cache_does_not_trust_fake_arbitrary_window(self):
        legitimate = game(11)
        accidental = GameWindow(44, 10044, "Other Window", "TkTop", "python.exe")
        svc, _, poster = ready([legitimate, accidental])
        result = svc.close_all_game_windows(snap(legitimate, accidental))
        self.assertEqual(result.posted, (11,))
        self.assertEqual(result.skipped, ((44, "UNVERIFIED_CACHE_GAME_IDENTITY"),))
        self.assertEqual([x[0] for x in poster.sent], [11])

    def test_live_wrong_exe_rejects_even_if_cached_is_game(self):
        row = game(101)
        svc, backend, poster = ready([row])
        backend.processes[row.pid] = "not-the-game.exe"
        result = svc.close_all_game_windows(snap(row))
        self.assertEqual(result.skipped, ((101, "LIVE_GAME_IDENTITY_MISMATCH"),))
        self.assertEqual(poster.sent, [])

    def test_live_class_and_title_both_changed_reject(self):
        row = game(10)
        svc, backend, poster = ready([row])
        backend.classes[10] = "TkTop"
        backend.titles[10] = "Random other window"
        self.assertEqual(
            svc.close_all_game_windows(snap(row)).skipped,
            ((10, "LIVE_GAME_IDENTITY_MISMATCH"),))
        self.assertEqual(poster.sent, [])

    def test_pid_reused_rejected_not_reassigned(self):
        row = game(10)
        svc, backend, poster = ready([row])
        backend.actual[10] = game(10, 55555)
        result = svc.close_all_game_windows(snap(row))
        self.assertEqual(result.skipped, ((10, "PID_REUSED"),))
        self.assertFalse(poster.sent)

    def test_closed_source_not_posted_even_when_still_in_cache(self):
        row = game(10)
        svc, backend, poster = ready([row])
        backend.actual.pop(10)
        r = svc.close_all_game_windows(snap(row))
        self.assertEqual(r.skipped, ((10, "CLOSED_OR_HIDDEN"),))
        self.assertFalse(poster.sent)

    def test_child_hwnd_not_in_enumwindows_rejected(self):
        row = game(10)
        svc, backend, poster = ready([row])
        backend.top_level = []
        r = svc.close_all_game_windows(snap(row))
        self.assertEqual(r.skipped, ((10, "NOT_LIVE_TOP_LEVEL"),))
        self.assertFalse(poster.sent)

    def test_hidden_window_not_posted(self):
        row = game(10)
        svc, backend, poster = ready([row])
        backend.vis[10] = False
        self.assertEqual(
            svc.close_all_game_windows(snap(row)).skipped,
            ((10, "CLOSED_OR_HIDDEN"),))
        self.assertFalse(poster.sent)

    def test_duplicate_hwnd_rejected_before_any_post(self):
        row = game(10)
        svc, backend, poster = ready([row])
        r = svc.close_all_game_windows(snap(row, row))
        self.assertEqual(r.code, "AMBIGUOUS_HWND")
        self.assertEqual(r.posted, ())
        self.assertFalse(poster.sent)
        self.assertEqual(backend.enumerations, 0)

    def test_failed_enumeration_blocks_entire_close(self):
        row = game(10)
        svc, backend, poster = ready([row])
        backend.fail_enum = True
        r = svc.close_all_game_windows(snap(row))
        self.assertEqual(r.code, "ENUMERATION_FAILED")
        self.assertFalse(poster.sent)

    def test_mixed_live_and_stale_only_posts_valid_subset(self):
        rows = [game(1), game(2), game(3)]
        svc, backend, poster = ready(rows)
        backend.actual.pop(2)
        r = svc.close_all_game_windows(snap(*rows))
        self.assertEqual(r.code, "PARTIAL_WM_CLOSE_POSTED")
        self.assertEqual(r.posted, (1, 3))
        self.assertEqual(r.skipped, ((2, "CLOSED_OR_HIDDEN"),))
        self.assertEqual([s[0] for s in poster.sent], [1, 3])

    def test_win32_postmessage_failure_is_not_reported_as_closed(self):
        row = game(1)
        svc, _, poster = ready([row])
        poster.fail.add(1)
        r = svc.close_all_game_windows(snap(row))
        self.assertEqual(r.posted, ())
        self.assertEqual(r.skipped, ((1, "POSTMESSAGE_FAILED"),))
        self.assertEqual(r.code, "NO_VALID_TARGETS")

    def test_empty_snapshot_never_posts(self):
        svc, backend, poster = ready([game(1)])
        r = svc.close_all_game_windows(snap())
        self.assertEqual(r.code, "NO_GAME_WINDOWS")
        self.assertEqual(backend.enumerations, 0)
        self.assertFalse(poster.sent)

    def test_invalid_row_never_posts(self):
        svc, backend, poster = ready([game(1)])
        r = svc.close_all_game_windows(WindowSnapshot(1, ("invalid",), True))
        self.assertEqual(r.code, "INVALID_ROW")
        self.assertEqual(backend.enumerations, 0)

    def test_start_wrapper_keeps_selected_tab_guard_before_cache_access(self):
        obj = object.__new__(TLMStartTab)
        obj._closed = False
        obj.poller = type("P", (), {"active": False})()
        obj._close_service_factory = lambda: (_ for _ in ()).throw(
            AssertionError("not allowed"))
        self.assertIsNone(obj._close_all())
        self.assertIsNone(obj._close_all_preview_windows())

    def test_start_button_uses_single_current_snapshot_no_restart_and_status_posted(self):
        obj = object.__new__(TLMStartTab)
        obj._closed = False
        obj.container = type("C", (), {"winfo_viewable": lambda _s: True})()
        row = game(1)
        class Producer:
            reads = 0
            def read_snapshot(self):
                self.reads += 1
                return snap(row)
        obj.poller = type("P", (), {"active": True, "producer": Producer()})()
        messages = []
        obj.preview_status = type("L", (), {"configure": lambda _s, **kw:
                                           messages.append(kw["text"])})()
        obj._close_service_factory = lambda: ready([row])[0]
        r = obj._close_all_preview_windows()
        self.assertEqual(r.posted, (1,))
        self.assertEqual(obj.poller.producer.reads, 1)
        self.assertEqual(obj.last_close_result, r)
        self.assertIn("đã gửi WM_CLOSE 1/1", messages[-1])

    def test_start_hidden_refuses_without_service_or_cache_access(self):
        obj = object.__new__(TLMStartTab)
        obj._closed = False
        obj.container = type("C", (), {"winfo_viewable": lambda _s: False})()
        obj.poller = type("P", (), {"active": True})()
        self.assertIsNone(obj._close_all_preview_windows())

    def test_start_closed_refuses_without_service(self):
        obj = object.__new__(TLMStartTab)
        obj._closed = True
        obj.poller = type("P", (), {"active": True})()
        self.assertIsNone(obj._close_all_preview_windows())


if __name__ == "__main__":
    unittest.main()
