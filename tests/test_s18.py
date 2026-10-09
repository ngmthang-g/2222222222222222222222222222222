"""S18 C05/C08 authentic master radio HWND identity and grid persistence tests."""
from __future__ import annotations
from pathlib import Path
import sys
import tempfile
import threading
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from grid_master import (
    GridSettings, GridSettingsStore, MasterSelection, update_dimension,
    valid_dimension, GRID_BOUNDS_ORIGINAL,
)
from start_windows import GameWindow
from start_tab import TLMStartTab


def row(hwnd,pid=None,title="TEST"):
    return GameWindow(hwnd,hwnd+1000 if pid is None else pid,title,"Test","NO_GAME.exe")


class GridModelTests(unittest.TestCase):
    def test_default_grid_original_evidence(self):
        self.assertEqual(GridSettings(),GridSettings(3,4))
        self.assertIn("UNKNOWN",GRID_BOUNDS_ORIGINAL)

    def test_local_positive_bounds_not_claimed_original(self):
        self.assertEqual(update_dimension(3,-1),2)
        self.assertEqual(update_dimension(3,1),4)
        self.assertEqual(update_dimension(1,-1),1)
        self.assertEqual(update_dimension(12,1),12)
        self.assertTrue(valid_dimension(3))
        self.assertFalse(valid_dimension(0))
        self.assertFalse(valid_dimension(13))
        self.assertFalse(valid_dimension(True))

    def test_bad_delta_fails_closed(self):
        for delta in (0,2,None,"-1"):
            with self.assertRaises(ValueError):
                update_dimension(3,delta)

    def test_non_integer_value_fails_closed(self):
        for value in (0,13,-1,"3",None,3.0,True):
            with self.assertRaises(ValueError):
                update_dimension(value,1)

    def test_settings_read_missing_file_defaults(self):
        with tempfile.TemporaryDirectory() as d:
            store=GridSettingsStore(Path(d)/"TLMTool"/"settings.ini")
            self.assertEqual(store.load(),GridSettings())

    def test_settings_round_trip_exact_original_section_keys(self):
        with tempfile.TemporaryDirectory() as d:
            store=GridSettingsStore(Path(d)/"TLMTool"/"settings.ini")
            store.save(5,6)
            self.assertEqual(store.load(),GridSettings(5,6))
            content=store.path.read_text(encoding="utf-8")
            self.assertIn("[Settings]",content)
            self.assertIn("grid_cols = 5",content)
            self.assertIn("grid_rows = 6",content)

    def test_unrelated_config_keys_and_sections_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"TLMTool"/"settings.ini"
            path.parent.mkdir(parents=True)
            path.write_text("[Settings]\nother=untouched\n[User]\nname=preserve\n",
                            encoding="utf-8")
            store=GridSettingsStore(path)
            store.save(2,7)
            txt=path.read_text(encoding="utf-8")
            self.assertIn("other = untouched",txt)
            self.assertIn("name = preserve",txt)
            self.assertEqual(store.load(),GridSettings(2,7))

    def test_invalid_file_values_fall_back_per_field(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"settings.ini"
            path.write_text("[Settings]\ngrid_cols=not_number\ngrid_rows=8\n",encoding="utf-8")
            self.assertEqual(GridSettingsStore(path).load(),GridSettings())
            path.write_text("[Settings]\ngrid_cols=0\ngrid_rows=8\n",encoding="utf-8")
            self.assertEqual(GridSettingsStore(path).load(),GridSettings(3,8))

    def test_invalid_write_rejected_without_touching_file(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"settings.ini"
            store=GridSettingsStore(path)
            store.save(3,4)
            before=path.read_bytes()
            with self.assertRaises(ValueError):
                store.save(999,4)
            self.assertEqual(path.read_bytes(),before)

    def test_existing_E05_backup_on_subsequent_write(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"TLMTool"/"settings.ini"
            store=GridSettingsStore(path)
            store.save(3,4)
            store.save(4,4)
            self.assertEqual(store.load(),GridSettings(4,4))
            backups=list(path.parent.glob("settings.????????.ini"))
            self.assertEqual(len(backups),1)
            self.assertIn("grid_cols = 3",backups[0].read_text(encoding="utf-8"))

    def test_master_init_local_first_discovered_policy(self):
        m=MasterSelection()
        a,b=row(1),row(2)
        self.assertTrue(m.update((a,b)))
        self.assertEqual((m.hwnd,m.pid),(a.hwnd,a.pid))

    def test_manual_master_is_not_list_index_or_name(self):
        m=MasterSelection()
        a,b=row(1),row(2)
        m.update((a,b))
        self.assertTrue(m.choose(2,1002))
        self.assertEqual(m.selected,(2,1002))
        self.assertTrue(m.update((b,a)))
        # different order triggers radio redraw, but must preserve HWND.
        self.assertEqual(m.selected,(2,1002))

    def test_master_reuses_same_hwnd_changed_pid_as_new_source(self):
        m=MasterSelection()
        a,b=row(1),row(2)
        m.update((a,b))
        m.choose(2,1002)
        m.update((row(2,9999),a))
        self.assertEqual(m.selected,(2,9999)) # local first surviving after reuse
        self.assertFalse(m.choose(2,1002))

    def test_disappeared_master_falls_back_to_first_live_hwnd(self):
        m=MasterSelection()
        m.update((row(1),row(2),row(3)))
        m.choose(3,1003)
        m.update((row(2),row(1)))
        self.assertEqual(m.selected,(2,1002))

    def test_invalid_identity_does_not_update_state(self):
        m=MasterSelection()
        m.update((row(1),))
        old=m.selected
        with self.assertRaises(ValueError):
            m.update((row(2),row(2,999)))
        self.assertEqual(m.selected,old)

    def test_no_master_persisted_and_empty_collection_resets(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"settings.ini"
            store=GridSettingsStore(p)
            m=MasterSelection()
            m.update((row(8),))
            store.save(5,3)
            m.update(())
            self.assertIsNone(m.hwnd)
            self.assertNotIn("master",p.read_text(encoding="utf-8").lower())


class Obj:
    def __init__(self):
        self.props=[]
        self.destroyed=False
    def configure(self,**k):
        self.props.append(k)
    def destroy(self):
        self.destroyed=True
    def winfo_viewable(self):
        return True

class Val:
    def __init__(self):
        self.x=""
    def set(self,x):
        self.x=x
    def get(self):
        return self.x

class GridUI(unittest.TestCase):
    def make(self):
        obj=object.__new__(TLMStartTab)
        obj._closed=False
        obj.grid_cols=3
        obj.grid_rows=4
        obj._grid_settings=type("Store",(),{"saved":[],"save":lambda self,c,r:self.saved.append((c,r))})()
        obj.layout_active=False
        obj.sync_loop_id=0
        obj._layout_allow=threading.Event()
        obj.grid_cols_label=Obj()
        obj.grid_rows_label=Obj()
        obj.layout_status=Obj()
        obj.master_selection=MasterSelection()
        obj._master_var=Val()
        obj._master_radio_buttons=[]
        obj._master_hwnd_cache=()
        obj._hwnd_by_name={}
        obj.container=Obj()
        obj.poller=type("P",(),{"active":True})()
        return obj

    def test_actual_buttons_adjust_state_and_persist(self):
        o=self.make()
        self.assertTrue(o._increase_cols())
        self.assertTrue(o._decrease_rows())
        self.assertEqual((o.grid_cols,o.grid_rows),(4,3))
        self.assertEqual(o._grid_settings.saved,[(4,4),(4,3)])
        self.assertIn("Cột: 4",str(o.grid_cols_label.props))
        self.assertIn("Hàng: 3",str(o.grid_rows_label.props))

    def test_grid_change_restarts_running_layout_generation(self):
        o=self.make()
        o.layout_active=True
        old=o._layout_allow
        old.set()
        self.assertTrue(o._increase_rows())
        self.assertFalse(old.is_set())
        self.assertTrue(o._layout_allow.is_set())
        self.assertEqual(o.sync_loop_id,1)
        self.assertTrue(o.layout_active)

    def test_grid_bound_prevents_mutation(self):
        o=self.make()
        o.grid_cols=12
        self.assertFalse(o._increase_cols())
        self.assertEqual(o._grid_settings.saved,[])

    def test_closed_view_does_not_mutate_grid(self):
        o=self.make()
        o._closed=True
        self.assertFalse(o._decrease_cols())
        self.assertEqual(o.grid_cols,3)

    def test_user_master_choice_uses_hwnd_pid_guard(self):
        o=self.make()
        o.master_selection.update((row(1),row(2)))
        self.assertTrue(o._on_master_change(2,1002))
        self.assertEqual(o.layout_master_hwnd,2)
        self.assertEqual(o._master_var.get(),"2:1002")
        self.assertFalse(o._on_master_change(2,9999))
        self.assertFalse(o._on_master_change(3,1003))

    def test_master_selection_restarts_enabled_layout_not_input_sync(self):
        o=self.make()
        o.master_selection.update((row(1),row(2)))
        o.layout_active=True
        o._layout_allow.set()
        previous=o._layout_allow
        self.assertTrue(o._on_master_change(2,1002))
        self.assertFalse(previous.is_set())
        self.assertTrue(o.layout_active)
        self.assertEqual(o.sync_loop_id,1)

    def test_inactive_or_hidden_start_refuses_master_change(self):
        o=self.make()
        o.master_selection.update((row(1),))
        o.poller.active=False
        self.assertFalse(o._on_master_change(1,1001))
        o.poller.active=True
        o.container.winfo_viewable=lambda:False
        self.assertFalse(o._on_master_change(1,1001))


if __name__=="__main__":
    unittest.main()
