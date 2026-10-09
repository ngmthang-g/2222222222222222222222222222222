"""S09 worker and Tk cache tests: no game/exe process invoked."""
from __future__ import annotations
import pathlib
import sys
import threading
import time
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from start_polling import (
    DISCOVERY_INTERVAL_SECONDS, START_UI_POLL_MS, StartWindowProducer,
    TkStartCachePoller, WindowSnapshot,
)
from start_windows import GAME_PROCESS, GAME_TITLE, GameWindow
from shell import TabLifecycle, TAB_SPECS


def game(hwnd=19, pid=119):
    return GameWindow(hwnd, pid, GAME_TITLE, "UnityWndClass", GAME_PROCESS)


def until(predicate, seconds=1.0):
    stop = time.monotonic() + seconds
    while time.monotonic() < stop:
        if predicate():
            return
        time.sleep(.002)
    raise AssertionError("Timed out waiting for producer")


class FakeBackend:
    def __init__(self, block=None, failure=False):
        self.block = block
        self.failure = failure
        self.count = 0

    def enumerate_top_level(self):
        self.count += 1
        if self.block is not None:
            self.block.wait(timeout=.8)
        if self.failure:
            raise OSError("test enumeration failure")
        return [19]

    def is_visible(self, hwnd): return True
    def is_window(self, hwnd): return True
    def process_id(self, hwnd): return 119
    def process_executable(self, pid): return GAME_PROCESS
    def window_class(self, hwnd): return "UnityWndClass"
    def title_with_timeout(self, hwnd, ms): return GAME_TITLE


class FakeRoot:
    def __init__(self):
        self.pending = {}
        self.next_id = 0
        self.delays = []
        self.cancelled = []

    def after(self, delay, callback):
        self.next_id += 1
        self.pending[self.next_id] = callback
        self.delays.append(delay)
        return self.next_id

    def after_cancel(self, token):
        self.cancelled.append(token)
        self.pending.pop(token, None)

    def fire_next(self):
        key = next(iter(self.pending))
        callback = self.pending.pop(key)
        callback()


class FakeProducer:
    def __init__(self):
        self.snapshot = WindowSnapshot()
        self.active = False
        self.starts = 0
        self.stops = 0
        self.reads = 0

    def start(self):
        self.active = True
        self.starts += 1
        return True

    def stop(self):
        self.active = False
        self.stops += 1

    def read_snapshot(self):
        self.reads += 1
        return self.snapshot


class S09StartPollingTests(unittest.TestCase):
    def test_contracts_have_independent_original_cadences(self):
        self.assertEqual(DISCOVERY_INTERVAL_SECONDS, 3.0)
        self.assertEqual(START_UI_POLL_MS, 2000)

    def test_real_worker_publishes_immutable_snapshot_without_tk(self):
        backend = FakeBackend()
        producer = StartWindowProducer(lambda: backend, interval_seconds=.01)
        self.assertTrue(producer.start())
        try:
            until(lambda: producer.read_snapshot().valid)
            snap = producer.read_snapshot()
            self.assertEqual(snap.windows, (game(),))
            self.assertGreater(snap.revision, 0)
            self.assertIsInstance(snap.windows, tuple)
            self.assertEqual(backend.count >= 1, True)
            self.assertTrue(producer.start())  # no duplicate workers
        finally:
            producer.stop()
        self.assertFalse(producer.active)
        self.assertFalse(producer.read_snapshot().valid)
        self.assertEqual(producer.read_snapshot().windows, ())

    def test_stopped_during_slow_enumeration_rejects_late_publish(self):
        gate = threading.Event()
        backend = FakeBackend(block=gate)
        producer = StartWindowProducer(lambda: backend, interval_seconds=.01, join_timeout=.005)
        producer.start()
        until(lambda: backend.count >= 1)
        t0 = time.monotonic()
        producer.stop()
        self.assertLess(time.monotonic()-t0, .1)
        self.assertFalse(producer.read_snapshot().valid)
        self.assertFalse(producer.start(), "Must not start overlapping worker while old scan blocked")
        gate.set()
        until(lambda: producer._thread is not None and not producer._thread.is_alive())
        self.assertEqual(producer.read_snapshot().windows, ())
        self.assertTrue(producer.start())
        try:
            until(lambda: producer.read_snapshot().valid)
        finally:
            producer.stop()

    def test_enumeration_error_never_retains_stale_game_window(self):
        backend = FakeBackend()
        producer = StartWindowProducer(lambda: backend, interval_seconds=.02)
        producer.start()
        try:
            until(lambda: producer.read_snapshot().valid)
            backend.failure = True
            until(lambda: producer.read_snapshot().error is not None)
            snap = producer.read_snapshot()
            self.assertFalse(snap.valid)
            self.assertEqual(snap.windows, ())
            self.assertTrue(snap.error.startswith("ENUMERATION_ERROR"))
        finally:
            producer.stop()

    def test_initial_backend_error_fails_closed_and_can_restart(self):
        attempt = []
        def factory():
            attempt.append(1)
            if len(attempt) == 1:
                raise OSError("temporary")
            return FakeBackend()
        producer = StartWindowProducer(factory, interval_seconds=.01)
        self.assertTrue(producer.start())
        until(lambda: not producer.active)
        self.assertTrue(producer.read_snapshot().error.startswith("BACKEND_ERROR"))
        # Original worker is finished by the time the retry is attempted.
        until(lambda: producer._thread is not None and not producer._thread.is_alive())
        self.assertTrue(producer.start())
        try:
            until(lambda: producer.read_snapshot().valid)
            self.assertEqual(producer.read_snapshot().windows, (game(),))
        finally:
            producer.stop()

    def test_cache_poller_does_not_scan_or_read_hwnd_on_tk_thread(self):
        root, producer = FakeRoot(), FakeProducer()
        observed = []
        poll = TkStartCachePoller(root, producer, observed.append)
        poll._start_refresh()
        self.assertEqual(root.delays, [0])
        producer.snapshot = WindowSnapshot(2, (game(),), True)
        root.fire_next()
        self.assertEqual(producer.reads, 1)
        self.assertEqual(len(observed), 1)
        self.assertEqual(observed[0].delta.added, (game(),))
        self.assertEqual(root.delays, [0, 2000])
        root.fire_next()
        self.assertEqual(len(observed), 1)  # no new revision, no redraw
        poll._stop_refresh()
        self.assertFalse(root.pending)
        self.assertEqual(producer.stops, 1)

    def test_pid_reuse_is_reported_not_silently_reassigned(self):
        root, producer = FakeRoot(), FakeProducer()
        items = []
        poll = TkStartCachePoller(root, producer, items.append)
        poll._start_refresh()
        producer.snapshot = WindowSnapshot(1, (game(19,119),), True)
        root.fire_next()
        self.assertTrue(poll.registry.identity_matches(19,119))
        producer.snapshot = WindowSnapshot(2, (game(19,333),), True)
        root.fire_next()
        self.assertEqual(items[-1].delta.reused, ((game(19,119),game(19,333)),))
        self.assertFalse(poll.registry.identity_matches(19,119))
        self.assertTrue(poll.registry.identity_matches(19,333))
        poll._stop_refresh()

    def test_invalid_snapshot_removes_stale_rows_and_denies_old_pid(self):
        root, producer = FakeRoot(), FakeProducer()
        items=[]
        poll=TkStartCachePoller(root,producer,items.append)
        poll._start_refresh()
        producer.snapshot=WindowSnapshot(1,(game(),),True)
        root.fire_next()
        producer.snapshot=WindowSnapshot(2,(),False,error="ENUMERATION_ERROR")
        root.fire_next()
        self.assertEqual(items[-1].delta.removed,(game(),))
        self.assertFalse(poll.registry.identity_matches(19,119))
        poll.shutdown()

    def test_leaving_start_cancels_tk_loop_and_prevents_late_callback(self):
        root, producer=FakeRoot(),FakeProducer()
        observed=[]
        poll=TkStartCachePoller(root,producer,observed.append)
        poll._start_refresh()
        stale=next(iter(root.pending.values()))
        poll._stop_refresh()
        self.assertEqual(len(root.pending),0)
        stale()  # a queued callback that reached dispatcher despite cancellation
        self.assertEqual(observed,[])
        self.assertEqual(producer.reads,0)
        poll.shutdown()
        poll._start_refresh()
        self.assertFalse(poll.active)

    def test_switching_back_to_start_starts_new_cache_session(self):
        root, producer=FakeRoot(),FakeProducer()
        observed=[]
        poll=TkStartCachePoller(root,producer,observed.append)
        poll._start_refresh()
        producer.snapshot=WindowSnapshot(1,(game(),),True)
        root.fire_next()
        poll._stop_refresh()
        poll._start_refresh()
        producer.snapshot=WindowSnapshot(3,(game(19,222),),True)
        root.fire_next()
        self.assertEqual(observed[-1].delta.added,(game(19,222),))
        self.assertFalse(poll.registry.identity_matches(19,119))
        self.assertEqual(producer.starts,2)
        poll.shutdown()

    def test_shell_tab_lifecycle_calls_same_start_stop_without_auto_grant(self):
        root, producer=FakeRoot(),FakeProducer()
        poll=TkStartCachePoller(root,producer,lambda e: None)
        frames={x.key:object() for x in TAB_SPECS}
        class PassiveInfo: pass
        lifecycle=TabLifecycle(
            {'info_tab':lambda frame:PassiveInfo(), 'start_tab':lambda frame:poll},frames)
        self.assertEqual(lifecycle.visible,{'info_tab'})
        lifecycle.select('start_tab')  # denied, falls back to Info
        self.assertFalse(poll.active)
        # Only a test-supplied authorized key, not a runtime license bypass.
        lifecycle.apply_authorized_keys({'start_tab'})
        lifecycle.select('start_tab')
        self.assertTrue(poll.active)
        lifecycle.select('info_tab')
        self.assertFalse(poll.active)
        lifecycle.shutdown()
        self.assertEqual(producer.stops,1)

    def test_stop_and_restart_while_backend_is_exiting_never_block_tk(self):
        backend=FakeBackend()
        producer=StartWindowProducer(lambda:backend,interval_seconds=.03,join_timeout=0)
        producer.start()
        until(lambda:producer.read_snapshot().valid)
        producer.stop()
        self.assertFalse(producer.read_snapshot().valid)
        # Active worker may have exited already; retry if necessary.
        until(lambda:producer._thread is None or not producer._thread.is_alive())
        self.assertTrue(producer.start())
        try:
            until(lambda:producer.read_snapshot().valid)
        finally:
            producer.stop()


if __name__ == '__main__':
    unittest.main()
