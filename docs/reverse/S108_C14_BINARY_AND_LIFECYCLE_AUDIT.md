# S108 — C14 detached preview geometry and embedded-visibility original PE audit

## Status

**Evidence audit complete; exact C14 geometry, thumbnail ordering, and Start embedded-preview transitions remain BLOCKED.** No fake `Tách rời` button or production code edit was made.

This was a targeted reread of LIVE `PLAN.md`, latest oversized `STATE.md` at S107 `NEXT_ACTION S108`, C14/S75/S85 original evidence, and current `src/detached_host.py`, `src/detached_preview.py`, `src/detached_lifecycle.py` and `src/start_tab.py`. The original user-supplied released executable was inspected directly; it was NOT run.

## Independently confirmed original artifact

| Artifact | Verified bytes | SHA-256 |
| --- | ---: | --- |
| `TLMTool_2.1.2(20261010-133331).zip` | 93,715,901 | `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd` |
| Original inner `TLMTool.dist/TLMTool.exe` | 47,450,112 | `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22` |

- Original ZIP: **1050** entries. There are **no direct readable `.py`, `.pyc`, `.pdb`, `.map`, `.md`, or `.json` entries** with original implementation. The 11 image files comprise `splash.png` and Tk toolkit bitmaps/GIFs; none is a detached-preview screenshot establishing layout.
- Inner executable: **PE32+ / Nuitka x86-64**, with `.text` and `.rdata` sections. Standard PE symbol listing reports **no symbols**; no recovered original Python function body or source-level control-flow map.
- The examined text is a **Nuitka serialized-name/constant pool in `.rdata`**. Names and contiguous local-variable groups do not establish runtime arithmetic, execution order, origin of runtime data, or original branches.

## New primary evidence beyond S75

[Exact C14 binary-offset table](S108_C14_PE_LOCAL_NAME_OFFSETS.tsv) records matching literals and their precise ZERO-BASED FILE OFFSETS in the hash-pinned PE, not addresses of executable instructions.

**Observed method names** (in one qualified-name list):

- `TLMStartTab._set_window_previews_visible` at `0x02c008d0`
- `TLMStartTab._toggle_detached_preview` at `0x02c00972`
- `TLMStartTab._open_detached_preview` at `0x02c00aa7`
- `TLMStartTab._close_detached_preview` at `0x02c00acb`

**Observed adjacent detached-open locals** in a serialized function-local-name area:

- `SM_CXSCREEN` `0x02c015c5`; `SM_CYSCREEN` `0x02c015d2`
- `region_x` `0x02c015e7`, `region_y` `0x02c015f1`, `region_w` `0x02c015fb`, `region_h` `0x02c01605`
- `cols` `0x02c01611`, `rows` `0x02c01617`, `gap` `0x02c0161d`, `tile_w` `0x02c01622`, `tile_h` `0x02c0162a`
- `index` `0x02c0163c`, `row` `0x02c01650`, `col` `0x02c01655`, `tx` `0x02c0165a`, `ty` `0x02c0165e`, `dst_hwnd` `0x02c01662`, `new_thumb` `0x02c0166c`.

The exact byte sequence just before `cols` is `wnacols`, and **the literal UTF-8 string `ncols` is not present at that offset**. The `wn` prefix is a Nuitka serialization token; the number of columns and its source cannot be recovered by reading that token as a numeric grid size. This distinction prevents false source claims.

**What these data mean:** the released program has original terms for a screen/region, columns/rows, tile width and height, an indexed iteration and tile x/y placement. **What they DO NOT mean:** no formula for tile dimensions/spacing or row/column mapping has been recovered. The recorded arrangement of locals is not an execution trace and does not identify HWND ordering.

C14 previously verified documentation remains valid: detached region `x=0, y=768, width=screen_width-450, height=screen_height-768`, native topmost DWM destinations, close→reopen refresh and a separate detached-update loop. None of those facts establishes an exact per-HWND destination rectangle. The released method may use scaling, rounding, adjustment by number of windows and columns, or other conditions; **all are unknown and must not be guessed.**

## Embedded preview visibility — branch not recovered

The qualified method-name list physically contains `_set_window_previews_visible`, `_toggle_detached_preview`, `_open_detached_preview` and `_close_detached_preview`. The original also has `user_initiated=True` in the close doc at `0x02bff380`.

Those observations **do not establish**:

1. whether each original `Tách rời` click withdraws, hides, unregisters or merely masks embedded DWM thumbnails;
2. which event (`Hủy tách`, `Đóng xem`, failed open, auto-open, Start hide, shutdown) restores the embedded preview, and in what order;
3. whether saved detached settings or `user_initiated` modify auto-open or thumbnail lifetime;
4. whether detached tiles use cached order, selected master first, RoleName sorting or original visible sequence.

No verified branch graph or authorized released-app runtime trace of these operations was available. PE method-name co-occurrence is not a call graph.

## Prior implementation remains valid but partial

- S68 `C14DetachedDwmSession` performs real DWM registrations for a separately supplied **measured** `PreviewPlacement` set.
- S70 `C14DetachedHost` opens a real topmost owner at the known original detached region, and S84 adds a functioning `Đóng xem` button that closes native DWM resources and the host.
- S85 `C14DetachedHost.refresh` closes and reopens detached hosts with **TEST/caller-provided placements**, revalidating permission and native HWND/PID. It cannot derive the original tile arithmetic.
- The Start UI does **not** wire a fake `Tách rời` toggle or claim a real embedded-preview hide/restore state machine. This is correct fail-closed behavior under the PLAN.

## Precise missing evidence for unblocking C14

A functional, visually faithful `Tách rời` requires **one** of:

- authentic original `_open_detached_preview` and `_toggle_detached_preview` function implementations (including arithmetic, column selection, order, DPI and embedded visibility calls); or
- a repeatable **authorized** original TLMTool Windows UI trace with 1, 2, 3, 4, 6 and 10 existing genuine client HWNDs, different screen dimensions and detached-grid selections. Record each DWM destination HWND's Win32 rectangle, source HWND/PID, selected order, first-click/refresh/`Hủy tách`/`Đóng xem` before/after embedded visibility and settings changes. Genuine Info must remain verified; no bypass or fake client state; or
- an independently verified reverse-control-flow mapping of the exact Nuitka PE hash, linking original function body and concrete Win32/DWM placement call sites and branches. Constant-name matches alone are insufficient.

If none of these sources is available, original geometry and visibility remain explicitly **UNKNOWN**. Do not substitute the embedded 197×110 geometry or the arbitrary 210px spacing used by native S85's TEST-only smoke.

## Work scope and verification honesty

- NEW evidence files: `docs/reverse/S108_C14_PE_LOCAL_NAME_OFFSETS.tsv`, `docs/reverse/S108_C14_BINARY_AND_LIFECYCLE_AUDIT.md`, `docs/tasks/S108.md`, append-only `STATE.md`/`PROJECT_STATUS.md`.
- NO changes to `src/`, Python tests, CI workflows, bundled original ZIP/EXE, immutable `PLAN.md`, B04/S59 or frozen Proxy. **NO new Windows CI** because this is a static-source audit, not a new runtime feature. No original EXE was executed.
- The last actual Windows [S106 full/native workflow 38065057307](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38065057307) completed SUCCESS: **1564/1564** Python, **269** compiled, nine test-owned Win32/DWM regression smokes. S36 remains deliberately `EXPLICITLY_BLOCKED_NO_GUI` in normal unverified launch and is **not** a real 1:1 product.

## NEXT_ACTION S109 — Source-backed, functional priority

Read LIVE PLAN/STATE and this audit. Deprioritize repeated C12/C14 binary-string scans unless a genuinely new original executable body, authorized trace, or real function geometry is available. Identify a distinct original-backed functional gap that can be demonstrated with real Win32 TEST-owned handles or original config fixtures, but has not yet been implemented. Audit current code **before** proposing implementation; never repeat already passing modules or create a visual-only button. If the next candidate also lacks complete original behavior, document the blocker and choose the next available candidate. Run CI if source/test changes; append exact evidence, changed files and NEXT_ACTION S110. Keep frozen original, signed Info and no-Proxy boundaries.
