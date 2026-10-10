"""S91: G02 3-column Party ready-account UI and S89/S90 wiring tests.

Tk rendering is exercised natively in the S91 real Windows smoke. These
unit tests validate deterministic layout, selected-name filtering and
generation-fenced visibility without pretending to read a game RoleName.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from auto_role_provenance import RoleReading
from start_windows import GameWindow
from start_polling import WindowSnapshot
from party_roster import PartyRoster, prepare_roster
from party_group_config import PartyGroup, PartySettings
from party_ready_list import PartyReadyList, PartyReadyConfigEditor, READY_COLUMNS


def window(h,p):
    return GameWindow(h,p,"WINDOW_TITLE_NOT_ROLE","TEST","TEST.exe")


def snapshot(revision,*items):
    return WindowSnapshot(revision=revision,windows=tuple(items),valid=True)


def build_roster(*names):
    windows=tuple(window(i+100,i+900) for i in range(len(names)))
    snap=snapshot(1,*windows)
    registry=dict((w.hwnd,n) for w,n in zip(windows,names))
    roster=PartyRoster()
    result=prepare_roster(snap,lambda h,p:RoleReading(h,p,registry[h]))
    assert roster.apply(result,snap)
    return roster


class FakeLabel:
    def __init__(self, parent, *, text):
        self.parent=parent
        self.text=text
        self.row=self.column=None
        self.destroyed=False
        parent.children.append(self)

    def grid(self, *, row, column, sticky, padx, pady):
        self.row=row
        self.column=column
        self.sticky=sticky
        self.padx=padx
        self.pady=pady

    def destroy(self):
        self.destroyed=True
        self.parent.children.remove(self)


class FakeBody:
    def __init__(self):
        self.children=[]

    def winfo_children(self):
        return list(self.children)


def fake_view():
    obj=object.__new__(PartyReadyList)
    obj.body=FakeBody()
    obj.labels=[]
    obj.names=()
    return obj


class Combo:
    def __init__(self,name):
        self.name=name
        self.values=()

    def get(self):
        return self.name

    def configure(self,**kwargs):
        self.values=kwargs["values"]


class S91ReadyListTests(unittest.TestCase):
    def setUp(self):
        self.patcher=patch("party_ready_list.ttk.Label",FakeLabel)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def test_01_original_three_per_row_constant(self):
        self.assertEqual(READY_COLUMNS,3)

    def test_02_five_ready_names_grid_coordinates(self):
        view=fake_view()
        PartyReadyList.show(view,build_roster("A","B","C","D","E"))
        self.assertEqual(view.names,("A","B","C","D","E"))
        self.assertEqual([(l.row,l.column) for l in view.labels],
                         [(0,0),(0,1),(0,2),(1,0),(1,1)])

    def test_03_nine_members_form_three_rows(self):
        view=fake_view()
        PartyReadyList.show(view,build_roster(*list("ABCDEFGHI")))
        self.assertEqual([(x.row,x.column) for x in view.labels[6:]],[(2,0),(2,1),(2,2)])

    def test_04_selected_names_hidden_and_remaining_compacted(self):
        view=fake_view()
        PartyReadyList.show(view,build_roster("A","B","C","D"),("A","C"))
        self.assertEqual(view.names,("B","D"))
        self.assertEqual([(x.row,x.column) for x in view.labels],[(0,0),(0,1)])

    def test_05_same_names_does_not_recreate_widgets(self):
        view=fake_view()
        roster=build_roster("A","B")
        PartyReadyList.show(view,roster)
        refs=tuple(view.labels)
        PartyReadyList.show(view,roster)
        self.assertEqual(tuple(view.labels),refs)

    def test_06_new_snapshot_removes_old_widgets(self):
        view=fake_view()
        PartyReadyList.show(view,build_roster("One","Two"))
        old=tuple(view.labels)
        PartyReadyList.show(view,build_roster("New"))
        self.assertTrue(all(x.destroyed for x in old))
        self.assertEqual(view.names,("New",))

    def test_07_absent_role_reader_does_not_render_window_title(self):
        view=fake_view()
        snap=snapshot(1,window(55,6))
        roster=PartyRoster()
        self.assertTrue(roster.apply(prepare_roster(snap),snap))
        PartyReadyList.show(view,roster)
        self.assertEqual(view.names,())
        self.assertEqual(view.labels,[])

    def test_08_reused_pid_generation_removes_stale_name(self):
        view=fake_view()
        old=snapshot(1,window(55,1))
        new=snapshot(2,window(55,2))
        roster=PartyRoster()
        result=prepare_roster(old,lambda h,p:RoleReading(h,p,"old acc"))
        self.assertTrue(roster.apply(result,old))
        PartyReadyList.show(view,roster)
        self.assertFalse(roster.apply(result,new))
        PartyReadyList.show(view,roster)
        self.assertEqual(view.names,())

    def test_09_stopped_party_roster_releases_labels(self):
        view=fake_view()
        roster=build_roster("A")
        PartyReadyList.show(view,roster)
        roster.clear("STOPPED")
        PartyReadyList.show(view,roster)
        self.assertEqual(view.body.winfo_children(),[])

    def test_10_reject_nonroster_untrusted_name_list(self):
        view=fake_view()
        with self.assertRaises(TypeError):
            PartyReadyList.show(view,["untrusted"])

    def test_11_duplicate_names_disallowed_at_ready_layer(self):
        view=fake_view()
        PartyReadyList.show(view,build_roster("Same","Same"))
        self.assertEqual(view.names,())

    def test_12_group_selector_keeps_saved_offline_values(self):
        editor=object.__new__(PartyReadyConfigEditor)
        editor._roster=build_roster("Online", "Busy")
        editor.state=PartySettings(groups=(
            PartyGroup(1,("Busy",)),PartyGroup(2,("Offline",""))))
        one=Combo("Busy")
        two=Combo("Offline")
        editor.group_inputs=[[one],[two]]
        PartyReadyConfigEditor._refresh_dropdown_values(editor)
        self.assertIn("Online",one.values)
        self.assertNotIn("Busy",two.values)
        self.assertIn("Offline",two.values)

    def test_13_selected_across_two_clusters_hidden(self):
        editor=object.__new__(PartyReadyConfigEditor)
        editor.state=PartySettings(groups=(PartyGroup(1,("A",)),PartyGroup(2,("B",))))
        self.assertEqual(PartyReadyConfigEditor._selected_names(editor),("A","B"))

    def test_14_source_never_creates_game_commands_or_claims(self):
        code=(ROOT/"src/party_ready_list.py").read_text(encoding="utf-8")
        for marker in ("ReadProcessMemory(", "PostMessage(", "200051",
                       "200057", "has_permission_with_limit(", "TOKEN_HMAC_SECRET"):
            self.assertNotIn(marker,code)


if __name__=="__main__":
    unittest.main()
