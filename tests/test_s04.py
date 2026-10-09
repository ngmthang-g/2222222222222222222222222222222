"""S04 regression tests: real S01–S04 classes, fake Tk and fake token ONLY in tests."""
import pathlib
import sys
import tkinter as tk
import unittest
from types import SimpleNamespace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from info_binding import InfoShellBinding, create_info_only_shell
from info_tab import InfoDisplay, UNKNOWN
from permission_guard import PermissionSnapshot, VerifiedClaims
from shell import INFO_KEY


class Root:
    def __init__(self):
        self.pending = []
        self.bindings = []
        self.root_calls = []
        self.reject_after = False

    def __getattr__(self, key):
        if key in {"title", "geometry", "withdraw", "option_add", "attributes",
                   "update_idletasks", "deiconify"}:
            return lambda *a, **kw: self.root_calls.append((key, a, kw))
        raise AttributeError(key)

    def after(self, delay, callback):
        if self.reject_after:
            raise tk.TclError("destroyed")
        self.pending.append((delay, callback))
        return len(self.pending)

    def bind(self, event, callback, add=None):
        self.bindings.append((event, callback, add))

    def run_pending(self, *, reversed_order=False):
        calls = self.pending[:]
        self.pending.clear()
        for _, callback in (reversed(calls) if reversed_order else calls):
            callback()


class Frame:
    next_id = 0
    def __init__(self, parent=None, **kw):
        Frame.next_id += 1
        self.ident = str(Frame.next_id)
        self.attrs = dict(kw)
    def __str__(self):
        return self.ident
    def pack(self, **kw):
        pass


class Label(Frame):
    def configure(self, **kw):
        self.attrs.update(kw)


class FakeTtk:
    Frame = Frame
    Label = Label


class Notebook(Frame):
    def __init__(self, root):
        super().__init__(root)
        self.tabs = []
        self.states = {}
        self.selected = None

    def add(self, frame, text):
        self.tabs.append((frame, text))
        self.states[frame] = "normal"

    def tab(self, frame, *, state):
        self.states[frame] = state

    def select(self, frame=None):
        if frame is not None:
            self.selected = frame
        return str(self.selected)

    def bind(self, *args):
        pass


def verified_test_claims():
    # Fake server decoder is scoped to tests, not a production entrypoint.
    return VerifiedClaims(
        frozenset({"info_tab", "login_tab", "debug_tab"}),
        "vip", 2, developer=True,
    )


class S04BindingTests(unittest.TestCase):
    def make_binding(self):
        root = Root()
        binding = create_info_only_shell(
            root,
            notebook_factory=Notebook,
            frame_factory=Frame,
            ttk_module=FakeTtk,
        )
        return root, binding

    def test_original_slots_only_info_is_visible(self):
        root, binding = self.make_binding()
        self.assertEqual(len(binding.app.notebook.tabs), 15)
        visible = [key for key, frame in binding.app._tab_frames.items()
                   if binding.app.notebook.states[frame] == "normal"]
        self.assertEqual(visible, [INFO_KEY])
        self.assertEqual(binding.info.server_last_result, "NOT_VERIFIED")
        self.assertEqual(binding.view.refresh_readonly(), InfoDisplay())
        self.assertEqual(root.bindings[0][0], "<Destroy>")

    def test_passive_view_does_not_add_action_buttons(self):
        _, binding = self.make_binding()
        self.assertEqual(binding.view._values["license_type"].attrs["text"], UNKNOWN)
        self.assertEqual(binding.view._values["license_key"].attrs["text"], UNKNOWN)
        self.assertFalse(hasattr(FakeTtk, "Button"))

    def test_verified_snapshot_reaches_view_only_after_tk_dispatch(self):
        root, binding = self.make_binding()
        self.assertTrue(binding.info.receive_server_token(
            "TEST_ONLY", lambda _: verified_test_claims()))
        self.assertEqual(binding.view._status.attrs["text"], InfoDisplay().status)
        self.assertEqual(len(root.pending), 1)
        self.assertEqual(root.pending[0][0], 0)
        root.run_pending()
        self.assertIn("xác minh", binding.view._status.attrs["text"])
        self.assertNotEqual(binding.view._status.attrs["text"], InfoDisplay().status)
        self.assertEqual(binding.view._values["license_type"].attrs["text"], UNKNOWN)
        # No missing factory becomes an enabled tab, even if test claims grant.
        self.assertEqual(binding.app.lifecycle.visible, {INFO_KEY})

    def test_newer_revocation_overrides_queued_verified_grant(self):
        root, binding = self.make_binding()
        binding.info.receive_server_token("TEST_ONLY", lambda _: verified_test_claims())
        binding.info.on_server_error()
        self.assertEqual(len(root.pending), 2)
        root.run_pending(reversed_order=True)
        self.assertEqual(binding.view.refresh_readonly(), InfoDisplay())
        self.assertEqual(binding.app.lifecycle.visible, {INFO_KEY})
        self.assertEqual(binding.view._status.attrs["text"], InfoDisplay().status)

    def test_revoked_permissions_after_applied_valid_claims(self):
        root, binding = self.make_binding()
        binding.info.receive_server_token("TEST_ONLY", lambda _: verified_test_claims())
        root.run_pending()
        binding.info.on_server_error()
        root.run_pending()
        self.assertEqual(binding.view._status.attrs["text"], InfoDisplay().status)
        self.assertEqual(binding.app.lifecycle.visible, {INFO_KEY})

    def test_close_drops_pending_callbacks(self):
        root, binding = self.make_binding()
        binding.info.receive_server_token("TEST_ONLY", lambda _: verified_test_claims())
        binding.close()
        self.assertTrue(binding._closed)
        root.run_pending()
        self.assertEqual(binding.view._status.attrs["text"], InfoDisplay().status)
        binding.close()  # idempotent

    def test_destroy_only_root_and_not_child(self):
        root, binding = self.make_binding()
        binding.on_destroy(SimpleNamespace(widget=Frame()))
        self.assertFalse(binding._closed)
        binding.on_destroy(SimpleNamespace(widget=root))
        self.assertTrue(binding._closed)

    def test_after_failure_closes_without_resurrecting_tk(self):
        root, binding = self.make_binding()
        root.reject_after = True
        binding.info.receive_server_token("TEST_ONLY", lambda _: verified_test_claims())
        self.assertTrue(binding._closed)
        self.assertEqual(root.pending, [])

    def test_rejects_untyped_unverified_snapshot(self):
        _, binding = self.make_binding()
        with self.assertRaises(TypeError):
            binding.on_snapshot({"permissions": ["debug_tab"]})
        self.assertEqual(binding.info.permission_guard.snapshot,
                         PermissionSnapshot())

    def test_info_state_and_view_are_same_instance(self):
        _, binding = self.make_binding()
        self.assertIs(binding.view.info_state, binding.info)
        self.assertIs(binding.app.lifecycle.ensure_built(INFO_KEY),
                      binding.view)


if __name__ == "__main__":
    unittest.main()
