"""S24 E08: owner-scoped normal Tk destroy and no late authority resurrection."""
from __future__ import annotations

from pathlib import Path
import sys
import threading
import unittest
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from shell import ALL_KEYS, INFO_KEY, MissingFeatureError, TabLifecycle, TLMMainApp
from start_tab import TLMStartTab


class Owner:
    def __init__(self, name, calls, failure=None):
        self.name, self.calls, self.failure = name, calls, failure
    def _start_refresh(self):
        self.calls.append("start:" + self.name)
    def _stop_refresh(self):
        self.calls.append("stop:" + self.name)
    def shutdown(self):
        self.calls.append("close:" + self.name)
        if self.failure:
            raise RuntimeError(self.failure)


class Root:
    def __init__(self):
        self.events, self.pending = [], []
    def __getattr__(self, name):
        if name in {"title", "geometry", "withdraw", "option_add", "attributes"}:
            return lambda *a, **kw: None
        raise AttributeError(name)
    def bind(self, key, callback, add=None):
        self.events.append((key, callback, add))
        return str(len(self.events))
    def after(self, delay, callback):
        self.pending.append(callback)
        return len(self.pending)
    def emit(self, target):
        for key, callback, _ in self.events:
            if key == "<Destroy>":
                callback(SimpleNamespace(widget=target))


class Frame:
    next_id = 0
    def __init__(self, parent):
        Frame.next_id += 1
        self.ident = f"frame_{Frame.next_id}"
    def __str__(self):
        return self.ident


class Notebook:
    def __init__(self, parent):
        self.frames, self.states, self.selected = [], {}, None
    def pack(self, **_):
        pass
    def add(self, frame, **_):
        self.frames.append(frame)
    def tab(self, frame, **kwargs):
        self.states[frame] = kwargs["state"]
    def select(self, frame=None):
        if frame is not None:
            self.selected = frame
        return str(self.selected)
    def bind(self, *_):
        pass


class S24LifecycleTests(unittest.TestCase):
    def make_lifecycle(self, calls=None):
        calls = [] if calls is None else calls
        owners = {key: Owner(key, calls) for key in (INFO_KEY, "start_tab", "login_tab")}
        lifecycle = TabLifecycle(
            {key: (lambda _frame, obj=obj: obj) for key, obj in owners.items()},
            {key: object() for key in ALL_KEYS})
        lifecycle.select(INFO_KEY)
        lifecycle.apply_authorized_keys({"start_tab", "login_tab"})
        lifecycle.select("start_tab")
        lifecycle.ensure_built("login_tab")
        return lifecycle, calls

    def test_active_refresh_stopped_before_each_owner_closed(self):
        lifecycle, calls = self.make_lifecycle()
        lifecycle.shutdown()
        self.assertEqual(calls, [
            "start:start_tab", "stop:start_tab",
            "close:login_tab", "close:start_tab", "close:info_tab"])
        self.assertTrue(lifecycle._closed)
        self.assertIsNone(lifecycle._active_refresh)

    def test_idempotent_repeat_and_late_grant_never_reopens(self):
        lifecycle, calls = self.make_lifecycle()
        lifecycle.shutdown()
        previous = list(calls)
        lifecycle.shutdown()
        self.assertEqual(calls, previous)
        self.assertEqual(lifecycle.apply_authorized_keys({"start_tab"}), frozenset({INFO_KEY}))
        with self.assertRaises(MissingFeatureError):
            lifecycle.select("start_tab")
        with self.assertRaises(MissingFeatureError):
            lifecycle.ensure_built(INFO_KEY)

    def test_faulted_owner_does_not_leave_other_owner_running(self):
        calls=[]
        lifecycle = TabLifecycle(
            {INFO_KEY: lambda _: Owner("info", calls),
             "start_tab": lambda _: Owner("start", calls, "TEST_OWNER_CLOSE_FAIL"),
             "login_tab": lambda _: Owner("login", calls)},
            {key: object() for key in ALL_KEYS})
        lifecycle.select(INFO_KEY)
        lifecycle.apply_authorized_keys({"start_tab", "login_tab"})
        lifecycle.select("start_tab")
        lifecycle.ensure_built("login_tab")
        with self.assertRaisesRegex(RuntimeError, "TEST_OWNER_CLOSE_FAIL"):
            lifecycle.shutdown()
        self.assertIn("close:info", calls)
        self.assertIn("close:login", calls)
        lifecycle.shutdown()
        self.assertEqual(calls.count("close:start"), 1)

    def test_failed_stop_still_closes_all(self):
        calls=[]
        class Broken(Owner):
            def _stop_refresh(self):
                calls.append("fail_stop")
                raise RuntimeError("TEST_STOP_FAIL")
        obj=Broken("start",calls)
        lifecycle=TabLifecycle(
            {INFO_KEY:lambda _:Owner("info",calls),"start_tab":lambda _:obj},
            {key:object() for key in ALL_KEYS})
        lifecycle.select(INFO_KEY)
        lifecycle.apply_authorized_keys({"start_tab"})
        lifecycle.select("start_tab")
        with self.assertRaisesRegex(RuntimeError,"TEST_STOP_FAIL"):
            lifecycle.shutdown()
        self.assertIn("close:start",calls)
        self.assertIn("close:info",calls)

    def make_app(self):
        root=Root()
        calls=[]
        owners={"info_tab": Owner("info", calls),
                "start_tab": Owner("start", calls)}
        app=TLMMainApp(
            root,{key:(lambda _frame,obj=obj:obj) for key,obj in owners.items()},
            notebook_factory=Notebook, frame_factory=Frame)
        return root, app, calls

    def test_root_destroy_ignores_descendant_events(self):
        root, app, calls=self.make_app()
        self.assertEqual(root.events[0][0],"<Destroy>")
        root.emit(Frame(None))
        self.assertFalse(app._closed)
        self.assertEqual(calls,[])
        root.emit(root)
        self.assertTrue(app._closed)
        self.assertEqual(calls,["close:info"])

    def test_active_tab_stopped_on_root_destroy_and_not_twice(self):
        root, app, calls=self.make_app()
        app.apply_verified_permissions({"start_tab"})  # TEST-ONLY grants
        app.notebook.select(app._tab_frames["start_tab"])
        app._on_tab_changed()
        self.assertEqual(calls,["start:start"])
        root.emit(root)
        root.emit(root)
        app.shutdown()
        self.assertEqual(calls,[
            "start:start", "stop:start", "close:start", "close:info"])
        self.assertEqual(app.lifecycle.visible,{INFO_KEY})
        app.apply_verified_permissions({"start_tab"})
        self.assertEqual(app.lifecycle.visible,{INFO_KEY})

    def test_queued_permission_callback_cannot_reopen_after_destroy(self):
        from permission_guard import PermissionSnapshot
        root, app, calls=self.make_app()
        app.apply_info_snapshot(PermissionSnapshot())
        self.assertEqual(len(root.pending),1)
        root.emit(root)
        root.pending.pop(0)()
        self.assertEqual(app.lifecycle.visible,{INFO_KEY})
        self.assertEqual(calls,["close:info"])

    def test_start_stop_after_widget_destroy_skips_render_and_tile_calls(self):
        tab=TLMStartTab.__new__(TLMStartTab)
        calls=[]
        tab._closed=True
        tab._stop_sync_loop=lambda: calls.append("sync")
        tab.maintenance=SimpleNamespace(stop=lambda:calls.append("maintenance"))
        tab.poller=SimpleNamespace(_stop_refresh=lambda:calls.append("poller"))
        tab._drop_previews=lambda:calls.append("dwm")
        tab._sync_tiles=lambda *_: self.fail("Destroyed widgets MUST NOT be touched")
        tab._render=lambda *_: self.fail("Destroyed labels MUST NOT be touched")
        tab._stop_refresh()
        self.assertEqual(calls,["sync","maintenance","poller","dwm"])

    def test_start_shutdown_fences_destroyed_layout_button(self):
        tab=TLMStartTab.__new__(TLMStartTab)
        tab._closed=False
        tab._layout_allow=threading.Event()
        tab.layout_active=True
        tab.sync_layout_running=True
        tab.sync_loop_id=0
        tab.btn_layout=SimpleNamespace(
            configure=lambda **_: self.fail("Layout button already destroyed"))
        done=[]
        tab.maintenance=SimpleNamespace(shutdown=lambda:done.append("maintenance"))
        tab._drop_previews=lambda:done.append("dwm")
        tab._top_handlers=[]
        tab.poller=SimpleNamespace(shutdown=lambda:done.append("poller"))
        tab.shutdown()
        tab.shutdown()
        self.assertTrue(tab._closed)
        self.assertFalse(tab.layout_active)
        self.assertEqual(done,["maintenance","dwm","poller"])


if __name__ == "__main__":
    unittest.main()
