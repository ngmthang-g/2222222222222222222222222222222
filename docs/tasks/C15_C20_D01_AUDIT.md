# AUDIT — C15–C20 + D01

## STATUS
**AUDITED / CORRECTIVE PATCHES REQUIRED AND APPLIED**

This audit was run against the exact user-provided archive in the current conversation, not only against prior notes.

Verified specimen hashes:
- archive `TLMTool_2.1.2(3).zip`: `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`
- inner `TLMTool.dist/TLMTool.exe`: `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`

The hashes match the frozen Gate-A specimen.

## C15 audit — Làm mới

Semantic result: **PASS**.

Direct binary re-check confirmed:
- `btn_refresh_preview`
- `_clear_window_preview_list`
- `_destroy_window_preview_item`
- `DwmUnregisterThumbnail`
- `_destroy_dwm_dst_hwnd`
- `DwmRegisterThumbnail`
- exact doc `Làm mới toàn bộ danh sách preview DWM.`
- detached refresh doc `Đóng rồi mở lại preview — tải lại danh sách cửa sổ mới.`

The behavior model remains correct: full DWM preview teardown/rebuild, current preview-column reuse, HWND-backed preview-order preservation, plus a separate detached close+reopen refresh path.

### C15 correction
Several rows in `C15_REFRESH_STATIC_EVIDENCE.tsv` used block-start/nearby offsets instead of the exact first byte of the cited literal/symbol. They are normalized by this audit to exact literal/symbol offsets. No behavior conclusion changes.

## C16 audit — Đóng hết

Semantic result: **PASS**.

Direct binary re-check confirmed:
- `_close_all_preview_windows`
- shared `close_all_game_windows`
- `get_game_windows`
- `IsWindow`
- `PostMessage`
- `WM_CLOSE`
- exact close-all documentation
- separate `UnityCrashHandler64.exe` cleanup path.

The behavior model remains correct:
- game client windows receive normal window-close requests;
- crash-handler cleanup is separate;
- no master-first close ordering evidence;
- immediate explicit preview refresh after click remains UNKNOWN.

### C16 correction
Several evidence-table offsets were off by one byte because earlier rows pointed at a preceding serialized/tag byte. The audit normalizes them to the actual first byte of the cited ASCII/UTF-8 string.

## C17 audit — preview left/right

Result: **PASS / NO SEMANTIC CHANGE**.

Direct binary re-check confirmed:
- `_move_preview_item`
- `_preview_order`
- exact doc mapping `delta=-1` to earlier and `delta=1` to later
- exact doc that refresh preserves order by HWND.

Boundary behavior and detached-order propagation remain explicit UNKNOWN. No additional evidence justifies inventing wrap-around/clamping.

## C18 audit — layout synchronization

Result: **PASS / NO SEMANTIC CHANGE**.

Recovered state and methods remain internally consistent:
- `layout_active`
- `sync_layout_running`
- `_sync_windows_loop`
- `_layout_worker`
- `_arrange_grid`
- worker-backed cache
- max-window guard / `_auto_stop_sync`.

Important preserved boundary:
- **1.5 seconds does not belong to layout worker cadence**.
- exact layout-worker cadence remains UNKNOWN.

## C19 audit — input synchronization

Result: **PASS WITH METADATA FIX**.

Direct binary re-check confirmed the exact docs:
- `Re-block slaves mỗi 1.5s — cửa sổ mới được block, phòng bị unblock.`
- `Mở khóa slave block quá 10s (mất release — master đóng/đổi/thoát).`
- `Chuyển client coord của master sang slave theo tỷ lệ kích thước cửa sổ.`

The detailed task report and STATE use status:
`VERIFIED_WITH_EXPLICIT_PAYLOAD_AND_STARTUP_TIMING_UNKNOWNS`.

The JSON model had the shorter stale status `VERIFIED_WITH_EXPLICIT_UNKNOWNS`; this audit aligns the JSON model with the authoritative task status.

## C20 audit — three-HWND combined scenario

Result: **PASS WITH WORDING FIX**.

The screenshot + static EXE evidence supports the combined three-HWND model:
- 3 visible tracked identities
- selected master independent from preview ordering
- preview grid 2x independent from physical grid 3x4
- one master + two input-sync targets.

However, wording `original-runtime evidence` can be read as if a new live runtime trace was performed during C20. C20 actually combines static EXE evidence with a locked screenshot captured from the original application.

The audit therefore standardizes Gate-C wording to:
**STATIC + VISUAL ORIGINAL EVIDENCE; RECONSTRUCTED WINDOWS RUNTIME PARITY DEFERRED**.

No original runtime behavior claim is expanded beyond the evidence.

## D01 audit — module inventory

Result: **PASS WITH REPRODUCIBILITY FIX**.

Re-running the committed extraction logic on the exact frozen inner EXE produced:
- valid exact module markers: **244**
- rejected exact marker string: **1**
- raw module-like `.py` filename candidates: **541**
- physical `.pyd` modules: **32**.

The D01 report previously stated **538** unique `.py` filename references without explaining the normalization step.

The difference is reproducible:
- raw filename candidates: **541**
- three raw leading-`u` duplicate-tag forms have exact unprefixed counterparts:
  - `ucertifi` ↔ `certifi`
  - `udll_injector` ↔ `dll_injector`
  - `ufarm_tab` ↔ `farm_tab`
- collapsing only those exact duplicate pairs gives **538 normalized filename references**.

This audit updates the extractor/report to expose both numbers:
- raw = 541
- normalized = 538.

The canonical accepted inventory remains unchanged:
- 570 accepted unique names
- 3 rejected artifacts
- 42 TLM internal
- 225 third-party Python
- 265 stdlib references
- 32 native extensions
- 6 Nuitka hooks.

D02 is unaffected because it uses the committed canonical accepted-name set, not the ambiguous raw filename-candidate count.

## FINAL DECISION

- C15: audited closed
- C16: audited closed
- C17: audited closed
- C18: audited closed
- C19: audited closed
- C20: audited closed with wording correction
- D01: audited closed with reproducibility correction

No task from C15–C20 requires redoing from scratch.

The authoritative continuation point remains **D03 — third-party dependencies** after the corrective commits are applied.
