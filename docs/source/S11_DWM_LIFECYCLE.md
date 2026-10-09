# S11 — Real DWM thumbnail HWND/PID lifecycle

## Evidence boundary
Original C03 proves live DWM thumbnail rather than BitBlt, overlay destination class, Win32 hwnd owner, register/update/unregister, geometry reposition, and original opacity 255. It DOES NOT prove exact `fVisible`/`fSourceClientAreaOnly` assignments. S11 chooses both `True` for its own adapter, without inventing original source equivalence.

## Pipeline
```text
S08 real EnumWindows candidate (HWND, PID, title)
  -> S09 background 3-second native scanner / immutable snapshot
  -> selected Tk Start tab root.after cache poll (2 s)
  -> S10 readonly table + S11 2-column DWM item frames 205×137
  -> 197×110 child Tk region (geometry anchor, NOT DWM destination)
  -> C02-safe source HWND+PID check
  -> NativeDwmBackend creates separate owned top-level overlay HWND
     ThlDwmThumbDst; WS_EX_LAYERED | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE
  -> DwmRegisterThumbnail(dest, src) [actual native HRESULT checked]
  -> SetWindowPos to Tk anchor screen x/y/w/h
  -> DwmUpdateThumbnailProperties (rect, opacity 255, visible, client-only)
  -> DWM live composition; not capture-based FPS
```

## Safety/teardown
Window close, HWND PID change, owner change, invalid geometry, DWM native error or tab leave cause `DwmUnregisterThumbnail` then `DestroyWindow`. Refresh/reposition stays on Tk main thread. No mouse handler, keyboard handling, game injection or process memory in S11. 80ms debounce is a reconstruction detail, not a recovered original value.

## Win32 test insight
Tk `Toplevel.winfo_id()` may identify an inner drawable child HWND, invalid for DWM source registration. The native test fixture resolves its real top-level `GetAncestor(hwnd, GA_ROOT=2)`; backend normalizes Tk destination owner. First-run `E_INVALIDARG` became native PASS after correcting the HWND level. This distinction is mandatory when diagnosing real DWM display.

## Verified
- S01–S11 combined 90 unit tests PASS on Windows Python 3.10.
- Win32 real test-owned HWND/PID matched.
- DwmRegisterThumbnail and DwmUpdateThumbnailProperties PASS.
- Reposition PASS, stale PID refused and existing overlay removed.
- DwmUnregisterThumbnail + DestroyWindow PASS.
- GitHub Actions 37878364061 (SUCCESS), source regression 37878364020 (SUCCESS).

## Deferred
- Pixel-by-pixel comparison against original Start screenshot.
- 2–3 concurrent native HWND thumbnail stress with move/resize/occlusion and native overlays.
- Real Thần Long game process, character cache/HP, cross-account input, original auto/grid functions.
- Server token/heartbeat, production entry and Windows EXE.
