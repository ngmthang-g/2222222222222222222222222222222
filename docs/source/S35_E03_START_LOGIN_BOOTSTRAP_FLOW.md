# S35 — Only actual constructed feature tabs, gated by E03 Info authorization

```text
S21/S22/S23/S24 Tk bootstrap
   -> run_with_info_factory(real, caller-supplied Info constructor)
       -> source_backed_tab_builders(info_factory)
            info_tab = given Info constructor
            start_tab = lazy TLMStartTab (S08-S20 Win32/DWM)
            login_tab = lazy TLMLoginPathTab (S25 real Tk folder picker)
       -> TLMMainApp (E03 Notebook)
           initially visible/built: Info ONLY
           externally verified PermissionSnapshot
             -> show authorized implemented tabs only
             -> selected Login: create native widgets, browse real folder,
                resolve exact two-space Thần Long  Mobile.exe, save settings.ini
             -> selected Start: launch native Win32 discovery thread,
                update cache/preview on Tk, stop on leave/revoke
             -> revoked: force Info fallback; stop Start worker
           no builder for unimplemented tabs, no Proxy
   -> public src/TLMTool.py main() remains return code 2 (real
      signed Info service is MISSING; cannot start reconstructed product)
```

Real Windows native integration was run only with **TEST-only claims** and a dummy nonexecutable filename at test-owned location. This is source-backed functioning UI under test, NOT a licensed/production game product. Repo does not yet have a Stage-T packaging recipe or signed Info adapter.

[S35 Windows 533/533 unit + native PASS](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37918643711) · [evidence artifact 11609993006](https://github.com/ngmthang-g/2222222222222222222222222222222222222222222/actions/runs/37918643711/artifacts/11609993006).
