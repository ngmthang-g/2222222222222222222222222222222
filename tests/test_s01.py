"""S01 functional unit tests; no DISPLAY/game/network dependencies."""
import configparser
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'src'))
from shell import (ALL_KEYS, DEV_KEYS, INFO_KEY, TAB_SPECS,
                   MissingFeatureError, TabLifecycle, TLMMainApp)
from settings_store import settings_path, read_settings, write_settings
from TLMTool import main


class StubTab:
    def __init__(self):
        self.started = self.stopped = 0
    def _start_refresh(self): self.started += 1
    def _stop_refresh(self): self.stopped += 1


class FakeRoot:
    def __init__(self): self.calls=[]
    def __getattr__(self,name):
        if name in {'title','geometry','withdraw','option_add','attributes','update_idletasks','deiconify'}:
            return lambda *args,**kw:self.calls.append((name,args,kw))
        raise AttributeError(name)
    def winfo_screenheight(self): return 1080
    def winfo_screenwidth(self): return 1920


class FakeFrame:
    _i=0
    def __init__(self,nb): FakeFrame._i+=1;self.id='frame'+str(FakeFrame._i)
    def __str__(self): return self.id


class FakeNotebook:
    def __init__(self,root): self.tabs=[];self.states={};self.sel=None;self.calls=[]
    def pack(self,**kw): self.calls.append(('pack',kw))
    def add(self,frame,**kw): self.tabs.append((frame,kw['text']));self.states[frame]='normal'
    def tab(self,frame,**kw): self.states[frame]=kw['state']
    def select(self,frame=None):
        if frame is not None: self.sel=frame
        return str(self.sel)
    def bind(self,*a): self.calls.append(('bind',a))


class S01Tests(unittest.TestCase):
    def frames(self):return {key:object() for key in ALL_KEYS}

    def test_original_tab_order_and_default_info_only(self):
        names=[t.label for t in TAB_SPECS]
        self.assertEqual(len(names),15)
        self.assertEqual([names[i] for i in (0,1,2,3,4,6,7,8,9,10,11)],
                         ['▶','Login','Party','Train','Train LSV','Phó Bản','Daily','Dồn','Rao','Tối ưu','ℹ'])
        model=TabLifecycle({INFO_KEY:lambda _:StubTab()},self.frames())
        self.assertEqual(model.visible,{INFO_KEY})
        self.assertFalse(DEV_KEYS & model.visible)

    def test_never_build_without_verified_factory_and_server_authority(self):
        with self.assertRaises(MissingFeatureError): TabLifecycle({},self.frames())
        m=TabLifecycle({INFO_KEY:lambda _:StubTab()},self.frames())
        m.apply_authorized_keys({'login_tab','emu_farm_tab'},dev_allowed=False)
        self.assertEqual(m.visible,{INFO_KEY})
        with self.assertRaises(MissingFeatureError):m.ensure_built('login_tab')

    def test_lazy_single_build_stop_refresh_and_fallback(self):
        count={'info':0,'login':0}; instances={}
        def factory(k):
            def make(_):
                count[k]+=1;instances[k]=StubTab();return instances[k]
            return make
        m=TabLifecycle({INFO_KEY:factory('info'),'login_tab':factory('login')},self.frames())
        m.ensure_built(INFO_KEY)
        m.select(INFO_KEY)
        m.apply_authorized_keys({'login_tab'})
        m.select('login_tab');m.select('login_tab')
        self.assertEqual(count,{'info':1,'login':1})
        self.assertEqual(instances['login'].started,1)
        m.apply_authorized_keys(set(),blocked=True)
        self.assertEqual(m.current,INFO_KEY)
        self.assertEqual(instances['login'].stopped,1)
        self.assertEqual(m.visible,{INFO_KEY})

    def test_dev_not_exposed_without_explicit_server_dev_authority(self):
        builders={INFO_KEY:lambda _:StubTab(),'debug_tab':lambda _:StubTab()}
        m=TabLifecycle(builders,self.frames())
        self.assertNotIn('debug_tab',m.apply_authorized_keys({'debug_tab'},dev_allowed=False))
        self.assertIn('debug_tab',m.apply_authorized_keys({'debug_tab'},dev_allowed=True))
        self.assertNotIn('debug_tab',m.apply_authorized_keys({'debug_tab'},dev_allowed=True,blocked=True))

    def test_notebook_shell_is_real_hidden_tabs_not_fake_widgets(self):
        root=FakeRoot()
        app=TLMMainApp(root,{INFO_KEY:lambda f:StubTab()},notebook_factory=FakeNotebook,frame_factory=FakeFrame)
        self.assertEqual(len(app.notebook.tabs),15)
        self.assertEqual(sum(x=='normal' for x in app.notebook.states.values()),1)
        self.assertEqual(app.notebook.states[app._tab_frames[INFO_KEY]],'normal')
        app.position_window_top_right()
        self.assertIn(('geometry',('450x1000+1460+0',),{}),root.calls)
        app.shutdown()

    def test_duplicate_last_wins_atomic_round_trip(self):
        with tempfile.TemporaryDirectory() as td:
            p=pathlib.Path(td)/'TLMTool'/'settings.ini';p.parent.mkdir()
            p.write_text('[Settings]\ngrid_rows = 1\ngrid_rows = 4\n',encoding='utf-8')
            cfg=read_settings(p)
            self.assertEqual(cfg.getint('Settings','grid_rows'),4)
            cfg.set('Settings','grid_cols','3')
            write_settings(cfg,p)
            reread=read_settings(p)
            self.assertEqual(reread.getint('Settings','grid_cols'),3)
            self.assertEqual(reread.getint('Settings','grid_rows'),4)
            self.assertEqual(list(p.parent.glob('*.tmp')),[])
            self.assertEqual(settings_path(td),p)

    def test_bootstrap_refuses_unverified_fake_info_without_gui(self):
        self.assertEqual(main(),2)


if __name__=='__main__': unittest.main()
