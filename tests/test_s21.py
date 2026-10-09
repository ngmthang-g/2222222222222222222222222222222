"""S21 E01 Windows single-instance mutex: platform-neutral fail-closed unit cases.

No production mutex name is ever acquired by tests. Win32 real process
competition is covered in S21_WINDOWS_MUTEX_SMOKE.py with isolated names.
"""
from __future__ import annotations

import contextlib
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from single_instance import (
    SingleInstanceMutex, InstanceAlreadyRunning, MutexUnavailable,
    ORIGINAL_MUTEX_NAME, ERROR_ALREADY_EXISTS,
    ORIGINAL_COLLISION_MESSAGE, ORIGINAL_COMPARISON_NUMBER,
)
import TLMTool


class FakeBackend:
    def __init__(self, values=((101, 0),), closed=True):
        self.values = list(values)
        self.created = []
        self.closed = []
        self.close_ok = closed
        self.fail_create = False
        self.fail_close = False

    def create(self, name):
        self.created.append(name)
        if self.fail_create:
            raise OSError("TEST_ONLY_CREATE_FAIL")
        return self.values.pop(0)

    def close(self, handle):
        self.closed.append(handle)
        if self.fail_close:
            raise OSError("TEST_ONLY_CLOSE_FAIL")
        return self.close_ok


class S21MutexTests(unittest.TestCase):
    def test_exact_original_name_and_unknowns_not_guessed(self):
        self.assertEqual(ORIGINAL_MUTEX_NAME, "TLMTool_SingleInstance")
        self.assertEqual(ERROR_ALREADY_EXISTS, 183)
        self.assertIn("UNKNOWN", ORIGINAL_COLLISION_MESSAGE)
        self.assertIn("UNKNOWN", ORIGINAL_COMPARISON_NUMBER)

    def test_acquire_and_release_exactly_once(self):
        b = FakeBackend()
        g = SingleInstanceMutex("S21_TEST_ONLY_mock_name", b)
        self.assertTrue(g.acquire())
        self.assertTrue(g.acquired)
        self.assertEqual(b.created, ["S21_TEST_ONLY_mock_name"])
        g.close()
        self.assertFalse(g.acquired)
        self.assertEqual(b.closed, [101])

    def test_repeated_acquire_is_idempotent(self):
        b=FakeBackend()
        g=SingleInstanceMutex("S21_TEST_ONLY_idempotent",b)
        self.assertTrue(g.acquire())
        self.assertTrue(g.acquire())
        self.assertEqual(len(b.created),1)
        g.close()
        g.close()
        self.assertEqual(b.closed,[101])

    def test_existing_mutex_releases_new_duplicate_handle_immediately(self):
        b=FakeBackend(((202,ERROR_ALREADY_EXISTS),))
        g=SingleInstanceMutex("S21_TEST_ONLY_duplicate",b)
        with self.assertRaises(InstanceAlreadyRunning):
            g.acquire()
        self.assertEqual(b.closed,[202])
        self.assertFalse(g.acquired)

    def test_null_handle_never_acquires(self):
        b=FakeBackend(((0,0),))
        g=SingleInstanceMutex("S21_TEST_ONLY_null",b)
        with self.assertRaises(MutexUnavailable):
            g.acquire()
        self.assertEqual(b.closed,[])
        self.assertFalse(g.acquired)

    def test_unexpected_win32_error_closes_created_handle(self):
        b=FakeBackend(((104,5),))
        g=SingleInstanceMutex("S21_TEST_ONLY_win32_error",b)
        with self.assertRaises(MutexUnavailable):
            g.acquire()
        self.assertEqual(b.closed,[104])
        self.assertFalse(g.acquired)

    def test_backend_creation_error_fails_closed(self):
        b=FakeBackend()
        b.fail_create=True
        with self.assertRaises(MutexUnavailable):
            SingleInstanceMutex("S21_TEST_ONLY_raise",b).acquire()

    def test_duplicate_handle_close_failure_fails_closed(self):
        b=FakeBackend(((505,ERROR_ALREADY_EXISTS),),closed=False)
        with self.assertRaises(MutexUnavailable):
            SingleInstanceMutex("S21_TEST_ONLY_closeerror",b).acquire()
        self.assertEqual(b.closed,[505])

    def test_acquired_handle_close_failure_stays_tracked_for_retry(self):
        b=FakeBackend(closed=False)
        g=SingleInstanceMutex("S21_TEST_ONLY_closefail",b)
        g.acquire()
        with self.assertRaises(MutexUnavailable):
            g.close()
        self.assertTrue(g.acquired)
        b.close_ok=True
        g.close()
        self.assertFalse(g.acquired)
        self.assertEqual(b.closed,[101,101])

    def test_context_manager_frees_handle_when_body_raises(self):
        b=FakeBackend()
        g=SingleInstanceMutex("S21_TEST_ONLY_ctx",b)
        with self.assertRaisesRegex(RuntimeError,"EXCEPTION_IN_BODY"):
            with g:
                self.assertTrue(g.acquired)
                raise RuntimeError("EXCEPTION_IN_BODY")
        self.assertFalse(g.acquired)
        self.assertEqual(b.closed,[101])

    def test_invalid_name_rejected_before_platform_ops(self):
        for name in ("","   ","n\x00bad",None):
            with self.subTest(name=name),self.assertRaises(ValueError):
                SingleInstanceMutex(name,FakeBackend())

    def test_bootstrap_still_denies_unverified_server(self):
        # No Tk GUI, mutex, or local fake Info service is instantiated.
        self.assertEqual(TLMTool.main(),2)

    def test_bootstrap_duplicate_is_detected_before_creating_tk(self):
        timeline=[]
        @contextlib.contextmanager
        def duplicate():
            timeline.append("mutex_duplicate")
            raise InstanceAlreadyRunning("TEST_ALREADY_EXISTS")
            yield

        mocktk=types.SimpleNamespace(
            Tk=lambda: timeline.append("Tk_CREATED"),TclError=Exception)
        with patch.object(TLMTool,"StartupDiagnostics",return_value=contextlib.nullcontext()), \
             patch.object(TLMTool,"SingleInstanceMutex",return_value=duplicate()), \
             patch.dict(sys.modules,{"tkinter":mocktk}):
            with self.assertRaises(InstanceAlreadyRunning):
                TLMTool.run_with_info_factory(lambda _:None)
        self.assertEqual(timeline,["mutex_duplicate"])

    def test_bootstrap_normal_gui_exit_closes_mutex_last(self):
        timeline=[]
        class Guard:
            def __enter__(self):
                timeline.append("acquired")
            def __exit__(self,*_):
                timeline.append("released")
        class Root:
            def mainloop(self): timeline.append("mainloop")
            def destroy(self): timeline.append("root_destroy")
        class App:
            def __init__(self,*_): timeline.append("app_construct")
            def position_window_top_right(self): timeline.append("position")
            def shutdown(self): timeline.append("app_shutdown")
        mocktk=types.SimpleNamespace(Tk=lambda: (timeline.append("Tk"),Root())[1],
                                     TclError=Exception)
        with patch.object(TLMTool,"StartupDiagnostics",return_value=contextlib.nullcontext()), \
             patch.object(TLMTool,"SingleInstanceMutex",return_value=Guard()), \
             patch.object(TLMTool,"TLMMainApp",App), \
             patch.dict(sys.modules,{"tkinter":mocktk}):
            TLMTool.run_with_info_factory(lambda _:None)
        self.assertEqual(timeline,[
            "acquired","Tk","app_construct","position","mainloop",
            "app_shutdown","root_destroy","released",
        ])

    def test_bootstrap_startup_constructor_exception_still_releases_mutex(self):
        timeline=[]
        class Guard:
            def __enter__(self): timeline.append("acquired")
            def __exit__(self,*_): timeline.append("released")
        class Root:
            def destroy(self): timeline.append("root_destroy")
        class BrokenApp:
            def __init__(self,*_):
                timeline.append("app_fail")
                raise RuntimeError("no actual Info auth")
        mocktk=types.SimpleNamespace(Tk=lambda:Root(),TclError=Exception)
        with patch.object(TLMTool,"StartupDiagnostics",return_value=contextlib.nullcontext()), \
             patch.object(TLMTool,"SingleInstanceMutex",return_value=Guard()), \
             patch.object(TLMTool,"TLMMainApp",BrokenApp), \
             patch.dict(sys.modules,{"tkinter":mocktk}):
            with self.assertRaisesRegex(RuntimeError,"no actual Info auth"):
                TLMTool.run_with_info_factory(lambda _:None)
        self.assertEqual(timeline,[
            "acquired","app_fail","root_destroy","released",
        ])


if __name__ == "__main__":
    unittest.main()
