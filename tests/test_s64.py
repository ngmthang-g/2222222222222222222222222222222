"""S64 authentic HWND/PID RoleName preflight, NEVER guess C07 collation."""
from __future__ import annotations
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"tests"))
from test_s17 import Backend,row,snap
from auto_role_provenance import C07RolePreflight,RoleReading

class S64RoleProvenance(unittest.TestCase):
    def setUp(self):
        self.rows=[row(10),row(20),row(30)]
        self.backend=Backend(self.rows)
        self.svc=C07RolePreflight(self.backend)
        self.reads=[]
        self.names={w.hwnd: ("Ánh Dương" if w.hwnd==10
                       else "Bình Minh" if w.hwnd==20 else "Chiều Tím")
                    for w in self.rows}
    def reader(self,h,p):
        self.reads.append((h,p))
        return RoleReading(h,p,self.names[h])
    def prepare(self, rows=None, **kw):
        data=rows if rows is not None else self.rows
        return self.svc.prepare(snap(*data),max_windows=kw.get("max_windows",3),
                master_hwnd=kw.get("master_hwnd",20),
                read_role=kw.get("read_role",self.reader),
                allowed=kw.get("allowed",lambda:True))
    def test_no_real_reader_fails_closed_no_window_title_fallback(self):
        self.assertEqual(self.prepare(read_role=None).code,"ROLE_READER_UNAVAILABLE")
        self.assertEqual(self.reads,[])
    def test_master_required_no_guessed_first_selection(self):
        self.assertEqual(self.prepare(master_hwnd=None).code,"MASTER_NOT_VERIFIED")
        self.assertEqual(self.prepare(master_hwnd=99).code,"MASTER_NOT_VERIFIED")
    def test_two_windows_master_first_without_unknown_comparator(self):
        out=self.prepare(self.rows[:2])
        self.assertEqual(out.code,"MASTER_FIRST_WITHOUT_SORT")
        self.assertEqual(tuple(w.hwnd for w in out.ordered),(20,10))
        self.assertEqual(tuple(x.role_name for x in out.verified),
                         ("Ánh Dương","Bình Minh"))
    def test_three_windows_role_verified_but_no_misleading_sort(self):
        out=self.prepare()
        self.assertEqual(out.code,"ORIGINAL_SORT_KEY_UNKNOWN")
        self.assertEqual(out.requested,3)
        self.assertEqual(len(out.verified),3)
        self.assertEqual(out.ordered,())
    def test_duplicate_real_role_names_are_not_duplicate_hwnd(self):
        self.names[10]=self.names[20]
        out=self.prepare(self.rows[:2])
        self.assertEqual(out.code,"MASTER_FIRST_WITHOUT_SORT")
        self.assertEqual(len(out.verified),2)
    def test_missing_or_whitespace_only_role_is_rejected(self):
        self.names[10]=" "
        self.assertEqual(self.prepare().code,"ROLE_NAME_MISSING")
        self.assertEqual(self.reads,[(10,self.rows[0].pid)])
    def test_wrong_pid_or_hwnd_from_reader_not_accepted(self):
        self.assertEqual(self.prepare(read_role=lambda h,p:RoleReading(h,p+1,"REAL")).code,
                         "ROLE_IDENTITY_MISMATCH")
        self.assertEqual(self.prepare(read_role=lambda h,p:RoleReading(h+1,p,"REAL")).code,
                         "ROLE_IDENTITY_MISMATCH")
    def test_reused_hwnd_pid_before_call_blocks_role_reader(self):
        self.backend.bumped_pid[20]=111111
        self.assertEqual(self.prepare().code,"STALE_OR_REUSED_PID")
        self.assertEqual(self.reads,[])
    def test_pid_changes_while_reading_rejected(self):
        def reuse(h,p):
            self.backend.bumped_pid[h]=88888
            return RoleReading(h,p,"TEST")
        self.assertEqual(self.prepare(read_role=reuse).code,"STALE_AFTER_READ")
    def test_duplicate_or_fake_snapshot_blocked(self):
        self.assertEqual(self.prepare([self.rows[0],self.rows[0]]).code,
                         "INVALID_OR_AMBIGUOUS_CACHE")
        self.assertEqual(self.prepare(max_windows=2).code,"OVER_VERIFIED_LIMIT")
        self.assertEqual(self.reads,[])
    def test_cancellation_and_reader_error_do_not_return_partial_order(self):
        permit=[False]
        self.assertEqual(self.prepare(allowed=lambda:permit[0]).code,"CANCELLED")
        self.assertEqual(self.prepare(read_role=lambda h,p:1/0).code,"ROLE_READER_ERROR")
        self.assertEqual(self.reads,[])
    def test_no_guessed_sort_or_game_memory_or_executable_actions(self):
        code=(ROOT/"src/auto_role_provenance.py").read_text("utf-8")
        for absent in ("sorted(", ".casefold(", "SetWindowPos", "ReadProcessMemory",
                       "tk.Button(", "proxy_tab", "PostMessage(", "CreateRemoteThread"):
            self.assertNotIn(absent,code)
if __name__=="__main__":unittest.main()
