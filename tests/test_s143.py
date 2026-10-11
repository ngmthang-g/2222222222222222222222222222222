"""S143 original C19 native master screen -> client geometry + safe planner.

Unit fixtures never load or signal game; Win64 OS read integration separate.
"""
from __future__ import annotations
import ast
from dataclasses import FrozenInstanceError
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from input_sync_core import InputSyncModel,ClientSize
from input_sync_screen_coords import (
    NativeC19MasterPointReader,VerifiedMasterClientPoint,
    queue_verified_screen_mouse,
)
from start_polling import WindowSnapshot
from start_windows import GameWindow,GAME_TITLE,UNITY_WINDOW_CLASS,GAME_PROCESS

MASTER=(101,1001)
A=(202,1002)
B=(303,1003)
def ready():
    rows=tuple(GameWindow(h,p,GAME_TITLE,UNITY_WINDOW_CLASS,GAME_PROCESS)
               for h,p in (MASTER,A,B))
    m=InputSyncModel()
    assert m.start(WindowSnapshot(1,rows,True),MASTER,max_windows=3)
    return m
class PointFixture:
    def __init__(self,p=None):
        self.point=p or VerifiedMasterClientPoint(*MASTER,40,60,200,150)
        self.calls=[]
    def capture(self,*args):
        self.calls.append(args)
        return self.point
class SizeFixture:
    def __init__(self):
        self.sizes={A:ClientSize(100,75),B:ClientSize(400,300)}
        self.calls=[]
    def size(self,*args):
        self.calls.append(args)
        return self.sizes[args]

def queue(m,**overrides):
    args=dict(
        button="left",pressed=True,now=1.0,
        allowed=lambda:True,
        live_identity=lambda h,p:True,
        point_reader=PointFixture(),size_reader=SizeFixture())
    args.update(overrides)
    return queue_verified_screen_mouse(m,321,234,**args)

class S143OriginalC19MasterClientTests(unittest.TestCase):
    def test_01_screen_capture_to_two_slave_fifo(self):
        model=ready()
        self.assertEqual(queue(model),2)
        self.assertEqual(model.pending,2)
        events=[]
        for _ in range(2):
            events.append(model.dispatch_one(
                sink=lambda e:None, identity_ok=lambda *_:True,
                permission_ok=lambda:True))
        self.assertEqual([(e.target,e.x,e.y) for e in events],
                         [(A,20,30),(B,80,120)])
    def test_02_capture_uses_actual_screen_point_and_master(self):
        point=PointFixture()
        model=ready()
        self.assertEqual(queue(model,point_reader=point),2)
        self.assertEqual(point.calls,[(101,1001,321,234)])
    def test_03_slave_client_dimensions_read_per_current_hwnd_pid(self):
        size=SizeFixture()
        self.assertEqual(queue(ready(),size_reader=size),2)
        self.assertEqual(size.calls,[A,B])
    def test_04_permission_deny_prevents_any_capture(self):
        model=ready()
        point=PointFixture()
        self.assertEqual(queue(model,allowed=lambda:False,point_reader=point),0)
        self.assertEqual(point.calls,[])
        self.assertEqual(model.pending,0)
    def test_05_stale_master_cannot_enqueue(self):
        model=ready()
        self.assertEqual(queue(model,live_identity=lambda h,p:h!=MASTER[0]),0)
        self.assertEqual(model.pending,0)
    def test_06_stale_slave_cannot_enqueue_partial_batch(self):
        model=ready()
        self.assertEqual(queue(model,live_identity=lambda h,p:h!=B[0]),0)
        self.assertEqual(model.pending,0)
    def test_07_changed_master_point_identity_refused(self):
        model=ready()
        wrong=PointFixture(VerifiedMasterClientPoint(*A,40,60,200,150))
        self.assertEqual(queue(model,point_reader=wrong),0)
        self.assertEqual(model.pending,0)
    def test_08_incomplete_native_slave_size_refuses_all(self):
        size=SizeFixture()
        del size.sizes[B]
        model=ready()
        # production must fail closed if a geometry source is gone
        self.assertEqual(queue(model,size_reader=size),0)
        self.assertEqual(model.pending,0)
    def test_09_permission_revoked_after_read_refuses_all(self):
        checks=iter((True,False))
        model=ready()
        self.assertEqual(queue(model,allowed=lambda:next(checks)),0)
        self.assertEqual(model.pending,0)
    def test_10_slave_recycled_after_geometry_refused(self):
        counter=[0]
        def current(h,p):
            if h==B[0]:
                counter[0]+=1
                return counter[0]==1
            return True
        model=ready()
        self.assertEqual(queue(model,live_identity=current),0)
        self.assertEqual(model.pending,0)
    def test_11_inactive_mode_disallows_capture(self):
        model=ready()
        model.stop("MODE_LEFT")
        self.assertEqual(queue(model),0)
        self.assertEqual(model.pending,0)
    def test_12_incompatible_type_and_missing_authority(self):
        self.assertEqual(queue_verified_screen_mouse(None,1,2,
           button="left",pressed=True,now=1.0,
           allowed=lambda:True,live_identity=lambda *_:True),0)
        self.assertEqual(queue(ready(),allowed=None),0)
    def test_13_master_point_is_frozen(self):
        p=VerifiedMasterClientPoint(*MASTER,2,3,100,80)
        with self.assertRaises(FrozenInstanceError):
            p.x=900
    def test_14_legacy_C19_unknown_input_message_not_claimed(self):
        s=(ROOT/"src/input_sync_screen_coords.py").read_text(encoding="utf8")
        for bad in ("PostMessageW(", "SendMessageW(", "SendInput(",
                    "keybd_event(", "mouse_event(", "WM_MY_SYNC_KEY =",
                    "WriteProcessMemory(", "requests.post("):
            self.assertNotIn(bad,s)
    def test_15_genuine_winapi_original_names_used(self):
        s=(ROOT/"src/input_sync_screen_coords.py").read_text(encoding="utf8")
        for name in ("WindowFromPoint","GetAncestor","ScreenToClient",
                     "NativeClientRectReader","queue_mouse"):
            self.assertIn(name,s)
    def test_16_compile_all_task_files(self):
        for p in ("src/input_sync_screen_coords.py","tests/test_s143.py",
                  "tools/S143_WINDOWS_C19_SCREEN_TO_CLIENT_SMOKE.py"):
            ast.parse((ROOT/p).read_text(encoding="utf8"))

if __name__=="__main__":
    unittest.main()
