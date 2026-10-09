"""S13 C04 adaptive preview housekeeping: pure scheduler tests only."""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from preview_maintenance import (
    BOUNDARY_AT_SIX, SHORT_MAINTENANCE_MS, LONG_MAINTENANCE_MS,
    ORIGINAL_SWITCH_CONSTANT, TkPreviewMaintenance, maintenance_delay_ms,
)
from start_polling import WindowSnapshot
from start_windows import GameWindow


class ManualAfter:
    def __init__(self):
        self.jobs = {}
        self.seq = 0
        self.delays = []
        self.cancelled = []
    def after(self, delay, callback):
        self.seq += 1
        self.jobs[self.seq] = (delay, callback)
        self.delays.append(delay)
        return self.seq
    def after_cancel(self, token):
        self.cancelled.append(token)
        self.jobs.pop(token, None)
    def run_next(self):
        assert self.jobs
        key = sorted(self.jobs)[0]
        _, callback = self.jobs.pop(key)
        callback()


class Cache:
    def __init__(self, snapshot=WindowSnapshot()):
        self.snapshot = snapshot
        self.reads = 0
    def read_snapshot(self):
        self.reads += 1
        return self.snapshot


def snap(n):
    return WindowSnapshot(10, tuple(
        GameWindow(h, 1234 + h, f"S13 TEST WINDOW {h}", "FakeWindowClass", "NOTGAME.EXE")
        for h in range(100, 100 + n)), True)


class S13PreviewSchedulerTests(unittest.TestCase):
    def test_original_literals_and_conservative_boundary_are_explicit(self):
        self.assertEqual((SHORT_MAINTENANCE_MS, LONG_MAINTENANCE_MS), (800, 2000))
        self.assertEqual(ORIGINAL_SWITCH_CONSTANT, 6)
        self.assertIn("NOT_ORIGINAL_PROVEN", BOUNDARY_AT_SIX)

    def test_small_counts_eight_hundred(self):
        self.assertEqual([maintenance_delay_ms(i) for i in range(6)], [800] * 6)

    def test_six_uses_conservative_two_thousand_not_claimed_original(self):
        self.assertEqual(maintenance_delay_ms(6), 2000)

    def test_large_counts_two_thousand(self):
        self.assertEqual([maintenance_delay_ms(i) for i in (7, 10, 100)], [2000] * 3)

    def test_invalid_counts_are_rejected(self):
        for value in (-1, True, 1.5, None, "6"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    maintenance_delay_ms(value)

    def test_tk_after_loop_consumes_cache_only_not_scans(self):
        root = ManualAfter()
        cache = Cache(snap(2))
        seen = []
        loop = TkPreviewMaintenance(root, cache, seen.append)
        loop.start()
        self.assertEqual(root.delays, [800])
        root.run_next()
        self.assertEqual(cache.reads, 1)
        self.assertEqual(seen, [cache.snapshot])
        self.assertEqual(root.delays[-1], 800)
        self.assertEqual(loop.cycles, 1)

    def test_count_change_is_reflected_after_real_cached_tick(self):
        root = ManualAfter()
        cache = Cache(snap(2))
        loop = TkPreviewMaintenance(root, cache, lambda _: None)
        loop.start()
        root.run_next()
        cache.snapshot = snap(6)
        root.run_next()
        self.assertEqual(root.delays[-1], 2000)
        cache.snapshot = snap(1)
        root.run_next()
        self.assertEqual(root.delays[-1], 800)
        self.assertEqual(loop.cycles, 3)

    def test_invalid_snapshot_never_reuses_old_cached_window_count(self):
        root = ManualAfter()
        cache = Cache(snap(9))
        loop = TkPreviewMaintenance(root, cache, lambda _: None)
        loop.start()
        root.run_next()
        self.assertEqual(root.delays[-1], 2000)
        cache.snapshot = WindowSnapshot(12, snap(9).windows, False, error="SCAN_FAILED")
        root.run_next()
        self.assertEqual(root.delays[-1], 800)

    def test_stop_revocation_cancels_pending_and_late_callbacks(self):
        root = ManualAfter()
        cache = Cache(snap(2))
        emitted = []
        loop = TkPreviewMaintenance(root, cache, emitted.append)
        loop.start()
        token, (_, late) = next(iter(root.jobs.items()))
        loop.stop()
        self.assertIn(token, root.cancelled)
        self.assertEqual(root.jobs, {})
        late()
        self.assertEqual(emitted, [])
        self.assertEqual(cache.reads, 0)
        self.assertFalse(loop.active)

    def test_restart_generation_fences_stale_callback(self):
        root = ManualAfter()
        cache = Cache(snap(1))
        loop = TkPreviewMaintenance(root, cache, lambda _: None)
        loop.start()
        _, (_, old) = next(iter(root.jobs.items()))
        loop.stop()
        loop.start()
        old()
        self.assertEqual(cache.reads, 0)
        self.assertEqual(len(root.jobs), 1)
        root.run_next()
        self.assertEqual(cache.reads, 1)

    def test_double_start_and_shutdown_permanently_disable(self):
        root = ManualAfter()
        cache = Cache(snap(1))
        loop = TkPreviewMaintenance(root, cache, lambda _: None)
        loop.start()
        loop.start()
        self.assertEqual(len(root.jobs), 1)
        loop.shutdown()
        loop.start()
        self.assertEqual(root.jobs, {})
        self.assertFalse(loop.active)

    def test_unavailable_producer_fails_closed_not_tight_loop(self):
        class Broken:
            def read_snapshot(self):
                raise RuntimeError("broken producer")
        root = ManualAfter()
        loop = TkPreviewMaintenance(root, Broken(), lambda _: None)
        loop.start()
        root.run_next()
        self.assertFalse(loop.active)
        self.assertEqual(root.jobs, {})

    def test_callback_exception_fails_closed(self):
        root = ManualAfter()
        cache = Cache(snap(1))
        def fail(_):
            raise ValueError("test callback")
        loop = TkPreviewMaintenance(root, cache, fail)
        loop.start()
        root.run_next()
        self.assertFalse(loop.active)
        self.assertEqual(root.jobs, {})

    def test_closed_loop_has_no_resurrected_callbacks(self):
        root = ManualAfter()
        loop = TkPreviewMaintenance(root, Cache(snap(1)), lambda _: None)
        loop.start()
        _, (_, saved) = next(iter(root.jobs.items()))
        loop.shutdown()
        saved()
        self.assertEqual(root.jobs, {})
        self.assertEqual(loop.cycles, 0)


if __name__ == "__main__":
    unittest.main()
