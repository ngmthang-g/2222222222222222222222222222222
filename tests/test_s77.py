"""S77 E08 Start native-DWM failure may not strand other cleanup owners."""
from __future__ import annotations
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"), str(ROOT/"tests")]
from test_s15 import prepared
from test_s76 import NativeErrorCtrl
from start_tab import TLMStartTab

def ready(fail=True):
    obj=prepared()
    e=obj.events
    obj._cancel_auto_reset_worker=lambda:e.append(("cancel_auto_reset",None))
    obj._cancel_stack_worker=lambda:e.append(("cancel_stack",None))
    obj._stop_sync_loop=lambda:e.append(("stop_sync",None))
    obj.maintenance=SimpleNamespace(
        stop=lambda:e.append(("maintenance_stop",None)),
        shutdown=lambda:e.append(("maintenance_shutdown",None)))
    obj.poller._stop_refresh=lambda:e.append(("poller_stop",None))
    obj.poller.shutdown=lambda:e.append(("poller_shutdown",None))
    class Host:
        def unbind(self,key,handle):e.append(("unbind",key,handle))
    obj._top=Host()
    obj._top_handlers=[("<Map>","s77-1"),("<Unmap>","s77-2")]
    if fail:
        obj._preview_controller=NativeErrorCtrl(e)
    return obj

class S77StartExitSafety(unittest.TestCase):
    def test_01_stop_after_native_error_still_finishes_tab_exit(self):
        x=ready()
        x._stop_refresh()
        self.assertIn(("poller_stop",None),x.events)
        self.assertEqual(x._state.code,"STOPPED")
        self.assertTrue(x._preview_cleanup_faulted)

    def test_02_error_stop_reports_unverified_release(self):
        x=ready()
        x._stop_refresh()
        self.assertIn("DWM",x.preview_status.value)
        self.assertIn(("rebuild",()),x.events)

    def test_03_stop_native_failure_cannot_rearm_preview_callback(self):
        x=ready()
        x._stop_refresh()
        TLMStartTab._schedule_preview(x)
        self.assertFalse(any(e[0]=="schedule_60ms" for e in x.events))
        self.assertIsNone(x._preview_controller)

    def test_04_stop_with_normal_DWM_release_remains_unchanged(self):
        x=ready(False)
        x._stop_refresh()
        self.assertEqual(x._state.code,"STOPPED")
        self.assertFalse(getattr(x,"_preview_cleanup_faulted",False))
        self.assertIn(("unregister_and_destroy_native_DWM",None),x.events)

    def test_05_closed_child_stops_without_touching_destroyed_widgets(self):
        x=ready()
        x._closed=True
        x._stop_refresh()
        self.assertNotIn(("rebuild",()),x.events)
        self.assertTrue(x._preview_cleanup_faulted)
        self.assertIn(("poller_stop",None),x.events)

    def test_06_shutdown_failure_still_unbinds_and_closes_poller(self):
        x=ready()
        with self.assertRaisesRegex(OSError,"TEST_NATIVE_UNREGISTER_FAILURE"):
            x.shutdown()
        self.assertIn(("unbind","<Map>","s77-1"),x.events)
        self.assertIn(("unbind","<Unmap>","s77-2"),x.events)
        self.assertIn(("poller_shutdown",None),x.events)
        self.assertEqual(x._top_handlers,[])

    def test_07_shutdown_first_error_reports_native_instead_of_success(self):
        x=ready()
        with self.assertRaises(OSError):
            x.shutdown()
        self.assertTrue(x._closed)
        self.assertTrue(x._preview_cleanup_faulted)
        self.assertEqual(x._preview_controller,None)

    def test_08_other_workers_cancel_before_DWM_then_poller_shutdown(self):
        x=ready()
        with self.assertRaises(OSError):
            x.shutdown()
        names=[e[0] for e in x.events]
        for name in ("cancel_auto_reset","cancel_stack","stop_sync",
                     "maintenance_shutdown","poller_shutdown"):
            self.assertIn(name,names)
        self.assertLess(names.index("maintenance_shutdown"),
                        names.index("native_shutdown_fails_after_attempt"))
        self.assertLess(names.index("native_shutdown_fails_after_attempt"),
                        names.index("poller_shutdown"))

    def test_09_late_repeat_shutdown_never_closes_twice(self):
        x=ready()
        with self.assertRaises(OSError):
            x.shutdown()
        count=len(x.events)
        x.shutdown()
        self.assertEqual(len(x.events),count)

    def test_10_first_failure_priority_does_not_skip_other_owners(self):
        x=ready()
        def fails():
            x.events.append(("maintenance_failed",None))
            raise ValueError("FIRST_MAINTENANCE_ERROR")
        x.maintenance.shutdown=fails
        with self.assertRaisesRegex(ValueError,"FIRST_MAINTENANCE_ERROR"):
            x.shutdown()
        self.assertIn(("poller_shutdown",None),x.events)
        self.assertIn(("native_shutdown_fails_after_attempt",None),x.events)

    def test_11_last_poller_failure_still_shows_exception(self):
        x=ready(False)
        def fails():
            x.events.append(("poller_shutdown_error",None))
            raise OSError("POLL_SHUTDOWN_FAILED")
        x.poller.shutdown=fails
        with self.assertRaisesRegex(OSError,"POLL_SHUTDOWN_FAILED"):
            x.shutdown()
        self.assertIn(("unbind","<Map>","s77-1"),x.events)

    def test_12_no_game_kill_fake_input_or_hidden_control_added(self):
        source=(ROOT/"src/start_tab.py").read_text("utf-8")
        for t in ("CreateRemoteThread(","ReadProcessMemory(",
                  "os.kill(", "WM_CLOSE_ALL_UNVERIFIED", "proxy_network_send("):
            self.assertNotIn(t,source)

if __name__=="__main__":unittest.main()
