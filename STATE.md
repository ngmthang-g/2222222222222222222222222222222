# STATE — TLMTool 2.1.2

## STATUS
IN_PROGRESS

## GATE A
**COMPLETE / VERIFIED**

## GATE B
**COMPLETE / VERIFIED**

## GATE C
IN_PROGRESS

## COMPLETED
- A01 VERIFIED
- A02 VERIFIED
- A03 VERIFIED
- A04 VERIFIED_WITH_EXPLICIT_UNKNOWN
- A05 VERIFIED
- A06 VERIFIED
- A07 VERIFIED
- A08 VERIFIED
- B01 VERIFIED
- B02 VERIFIED
- B03 VERIFIED
- B04 VERIFIED
- B05 VERIFIED
- B06 VERIFIED
- B07 VERIFIED
- B08 VERIFIED
- B09 VERIFIED
- B10 VERIFIED
- B11 VERIFIED
- B12 VERIFIED
- B13 VERIFIED_WITH_EXPLICIT_UNKNOWN_FONT_POINT_SIZE
- B14 VERIFIED
- C01 VERIFIED_WITH_EXPLICIT_UNKNOWN_BOOLEAN_FORMULA
- C02 VERIFIED_WITH_EXPLICIT_UNKNOWN_FALLBACK_FORMAT
- C03 VERIFIED_WITH_EXPLICIT_UNKNOWN_PROPERTY_BOOLEANS

## C03 VERIFIED RESULTS
- Verified Start preview backend is live Windows DWM Thumbnail, not BitBlt/PrintWindow polling.
- Source window is the discovered game `src_hwnd`.
- TLM creates a separate destination overlay HWND:
  - registered class `ThlDwmThumbDst`
  - CreateWindowExW
  - WS_EX_LAYERED
  - WS_EX_TOOLWINDOW
  - WS_EX_NOACTIVATE
  - WS_POPUP
  - WS_VISIBLE
- Preview Tk child supplies screen geometry through `winfo_rootx/y/width/height`.
- Destination owner comes from Tk toplevel `winfo_id`.
- Registration chain:
  - create destination HWND
  - DwmRegisterThumbnail(dst, src)
  - DwmUpdateThumbnailProperties
- Verified property flags/fields:
  - RECTDESTINATION
  - OPACITY
  - VISIBLE
  - SOURCECLIENTAREAONLY
  - serialized opacity constant = 255
- Exact source-level boolean assignment for fVisible/fSourceClientAreaOnly remains explicit UNKNOWN.
- Destination overlay follows Tk preview geometry through debounced reposition logic.
- Verified custom WndProc click messages:
  - 0x201 WM_LBUTTONDOWN
  - 0x202 WM_LBUTTONUP
  - 0x203 WM_LBUTTONDBLCLK
- Overlay click target map resolves destination HWND back to source game HWND.
- Source activation path uses IsWindow / IsIconic / SW_RESTORE or SW_SHOW / SetForegroundWindow.
- Hung handling:
  - IsHungAppWindow
  - nonblocking check
  - visible error path `Cửa sổ không phản hồi`
- Teardown:
  - DwmUnregisterThumbnail
  - remove click-target mapping
  - DestroyWindow destination
  - destroy Tk frame
- Screenshot corroboration recorded for three visible preview items:
  - outer frame 205×137
  - visible black preview surface 197×110

## C03 FILES
- `docs/tasks/C03.md`
- `docs/window/C03_PREVIEW_STATIC_EVIDENCE.tsv`
- `docs/window/C03_PREVIEW_FLOW.md`
- `docs/window/C03_PREVIEW_SCREENSHOT_GEOMETRY.tsv`
- `WINDOW_BEHAVIOR_MATRIX.md`

## CURRENT_TASK
C04 — update preview và FPS.

## BLOCKERS
None known for C04.

## DO_NOT_TOUCH
- Preserve Gate A forensic baseline unchanged.
- Preserve Gate B visual contract unchanged.
- Preserve C01/C02 explicit unknowns.
- Do not assume the two C03 DWM boolean field assignments.
- Do not begin C05 before C04 is verified.

## NEXT_ACTION
On CONTINUE:
1. Read `PLAN.md`.
2. Read `STATE.md`.
3. Execute **C04 only**.
4. Recover preview-loop scheduling, 800/2000 ms policy, rebuild conditions, label/HP refresh, reposition debounce and detached-loop separation from original evidence.
5. Distinguish DWM compositor rendering from TLM's metadata/update polling; do not call DWM thumbnail repaint an app FPS unless evidence supports that wording.
6. Update `WINDOW_BEHAVIOR_MATRIX.md` and persist C04 evidence/report.
7. Advance to C05 only after C04 is verified.
