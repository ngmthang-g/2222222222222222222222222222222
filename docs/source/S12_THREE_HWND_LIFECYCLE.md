# S12 — Native multi-source DWM geometry and cleanup

## Verified architecture
Win32 `DwmRegisterThumbnail` handles **three separate real test-owned top-level sources**. `DwmUpdateThumbnailProperties` moves existing destinations with native `SetWindowPos`; no new registration needed on root move/resize. Tk child `winfo_rootx/y/width/height` anchors define exact DWM destination bounds. On destroy/PID mismatch, old thumbnail unregisters and destination HWND is destroyed without corrupting survivors.

## Start widget integration
The original C03 describes overlay reposition on window resize. The S11 integration observed only child surface `<Configure>`; moving the parent without child-size changes could therefore leave overlays at stale screen positions. S12 adds root `<Configure>` observation and roots/container `<Map>/<Unmap>` handlers. It restores the 60ms C04-evidenced debounce (not a frame rate). Root handler identities are unbound during shutdown. No other source or permissions changed.

## Evidence
Windows 3.10 run: https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37878962348, **98/98 tests PASS, native DWM three-HWND/Tk lifecycle PASS**. Native 5 overlay windows created and all 5 destroyed. Three real test-owned source HWNDs [524308, 262264, 196736], one closed cleanly, mismatched PID denied, owner move/resize bounds matched GetWindowRect, hide/restore verified. Two test-owned HWND sources were then presented in a test-only authorized real Start tab; root move repositioned same thumbnail HWNDs and entitlement revoke removed overlays and returned to Info.

## NOT verified
Real game character windows, game visual pixels, GPU/compositor animation characteristics, exact original adaptive preview count boundary, real server token, product EXE. These are explicit separate gates rather than a false completed parity claim.
