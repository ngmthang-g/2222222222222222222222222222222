"""S82 C05 original only-rebuild-on-HWND-set-change + C09/C15 parity."""
from __future__ import annotations
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"tests")]
from test_s81 import FakeRadio, prepared, window
from start_tab import TLMStartTab

class S82MasterRadioIdentityTests(unittest.TestCase):
    def setUp(self):
        self.patch=patch("tkinter.ttk.Radiobutton",FakeRadio)
        self.patch.start()
        self.addCleanup(self.patch.stop)
    def three(self):
        o=prepared()
        rows=(window(1,title="one"),window(2,title="two"),window(3,title="three"))
        o._update_master_combobox(rows)
        return o,rows

    def test_01_initial_creates_three_identity_backed_radio_widgets(self):
        o,rows=self.three()
        self.assertEqual(len(o._master_radio_buttons),3)
        self.assertEqual(o._master_radio_identities,((1,1001),(2,1002),(3,1003)))
        self.assertEqual([x.kwargs["value"] for x in o._master_radio_buttons],
                         ["1:1001","2:1002","3:1003"])

    def test_02_permutation_does_not_destroy_or_recreate_radio_widgets(self):
        o,rows=self.three()
        first=tuple(o._master_radio_buttons)
        o._update_master_combobox((rows[2],rows[0],rows[1]))
        self.assertEqual(tuple(o._master_radio_buttons),first)
        self.assertFalse(any(x.destroyed for x in first))

    def test_03_permuted_and_renamed_same_hwnds_get_correct_keyed_label(self):
        o,rows=self.three()
        first=tuple(o._master_radio_buttons)
        o._update_master_combobox((
            window(3,title="new THREE"),window(1,title="new ONE"),window(2,title="new TWO")))
        self.assertEqual(tuple(o._master_radio_buttons),first)
        self.assertEqual([x.label for x in first],
                         ["new ONE [HWND 1]","new TWO [HWND 2]","new THREE [HWND 3]"])

    def test_04_manual_selected_hwnd_survives_oscillating_discovery_order(self):
        o,rows=self.three()
        o.master_selection.choose(2,1002)
        first=tuple(o._master_radio_buttons)
        for permutation in ((rows[1],rows[2],rows[0]),rows,(rows[2],rows[0],rows[1])):
            o._update_master_combobox(permutation)
        self.assertEqual(tuple(o._master_radio_buttons),first)
        self.assertEqual(o.master_selection.selected,(2,1002))
        self.assertEqual(o._master_var.value,"2:1002")

    def test_05_permutation_does_not_cancel_in_flight_native_stack(self):
        o,rows=self.three()
        o._stack_allow.set()
        old=o._stack_allow
        generation=o._stack_generation
        o._update_master_combobox((rows[1],rows[0],rows[2]))
        self.assertTrue(old.is_set())
        self.assertEqual(o._stack_generation,generation)

    def test_06_existing_master_title_change_only_updates_caption(self):
        o,rows=self.three()
        first=tuple(o._master_radio_buttons)
        o._update_master_combobox((window(1,title="ACTUAL RENAMED"),rows[1],rows[2]))
        self.assertEqual(tuple(o._master_radio_buttons),first)
        self.assertEqual(first[0].label,"ACTUAL RENAMED [HWND 1]")

    def test_07_closed_hwnd_rebuilds_only_new_source_set(self):
        o,rows=self.three()
        first=tuple(o._master_radio_buttons)
        o._update_master_combobox(rows[1:])
        self.assertTrue(all(x.destroyed for x in first))
        self.assertEqual(o._master_radio_identities,((2,1002),(3,1003)))
        self.assertEqual(len(o._master_radio_buttons),2)

    def test_08_reused_hwnd_new_pid_rebuilds_and_does_not_inherit_selection(self):
        o,rows=self.three()
        old=tuple(o._master_radio_buttons)
        o._update_master_combobox((window(1,pid=9999),rows[1],rows[2]))
        self.assertTrue(all(x.destroyed for x in old))
        self.assertEqual(o._master_radio_identities,((1,9999),(2,1002),(3,1003)))
        self.assertEqual(o.master_selection.selected,(1,9999))

    def test_09_added_source_rebuilds_one_time_only(self):
        o,rows=self.three()
        o._update_master_combobox((*rows,window(4)))
        refs=tuple(o._master_radio_buttons)
        o._update_master_combobox((window(4),rows[2],rows[1],rows[0]))
        self.assertEqual(tuple(o._master_radio_buttons),refs)

    def test_10_empty_list_removes_all_radio_widgets(self):
        o,rows=self.three()
        o._update_master_combobox(())
        self.assertEqual(o._master_radio_buttons,[])
        self.assertEqual(o._master_radio_identities,())
        self.assertIsNone(o.layout_master_hwnd)

    def test_11_invalid_duplicate_hwnd_snapshot_keeps_original_widgets(self):
        o,rows=self.three()
        refs=tuple(o._master_radio_buttons)
        o._update_master_combobox((rows[0],rows[0]))
        self.assertEqual(tuple(o._master_radio_buttons),refs)
        self.assertEqual(o._master_radio_identities,((1,1001),(2,1002),(3,1003)))

    def test_12_no_fake_role_reader_input_injection_or_proxy(self):
        s=(ROOT/"src/start_tab.py").read_text("utf-8")
        part=s[s.index("def _update_master_combobox"):s.index("def _on_master_change")]
        self.assertIn("self._master_radio_identities = identities",part)
        self.assertIn("by_identity[identity_key]",part)
        for term in ("ReadProcessMemory(","SendInput(","proxy_tab","CreateRemoteThread("):
            self.assertNotIn(term,part)

if __name__ == "__main__":
    unittest.main()
