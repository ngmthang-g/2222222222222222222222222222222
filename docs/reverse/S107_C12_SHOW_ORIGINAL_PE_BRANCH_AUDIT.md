# S107 — Original TLMTool 2.1.2 C12 Hiện hết: independently rechecked PE evidence

## Verdict

**`ORIGINAL_SHOW_BRANCH_UNRESOLVED` — DO NOT IMPLEMENT THE C12 SHOW HALF BY GUESS.**

This task scanned the exact user-supplied frozen release archive from the active session instead of relying only on inherited C12 documentation. Both contradictory statements remain physically present in the original Nuitka binary. The strings establish documentation/log tokens, **not** proof of which executable control-flow branch runs or whether `_saved_window_rects` is used during `_show_all_game_windows`.

## Original files independently verified, 2026-10-10

| Original specimen | Exact result |
| --- | --- |
| User-uploaded `TLMTool_2.1.2(20261010-133331).zip` | **93,715,901** bytes; SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd` |
| ZIP entries, expanded size | **1,050** entries; **260,061,035** total uncompressed bytes |
| `TLMTool_2.1.2/TLMTool.dist/TLMTool.exe` | **47,450,112** bytes; SHA-256 `15c8044f215680d6851c8f901a8938f2a628077cf21a2df22` |
| PE format | PE32+ Windows x86-64, native **Nuitka-compiled**, no readable original Python module implementation |
| Windows execution of original released binary | **NOT RUN** (not asserted, and there is no authenticated live-game runtime trace) |
| Original files changed | **None**; EXE extracted only into ephemeral analysis workspace |

## Exact UTF-8 file offsets in the original inner EXE

All offsets are **zero-based binary file offsets**, NOT runtime program counters or a decompiled Python function body:

| String/token | File offset(s) | Evidence |
| --- | --- | --- |
| `_show_all_game_windows` | `0x02bfb168`, `0x02bffe28` | Method name encoded in compiled constants |
| `_hide_all_game_windows` | `0x02bfb180`, `0x02bffe04` | Paired method name |
| `_saved_window_rects` | `0x02bfb21e` | Saved rectangle state exists |
| `GetWindowRect` near C12 | `0x02bfb233` | Rectangle acquisition is named |
| Generic C12 toggle doc: `Toggle: đẩy toàn bộ cửa sổ game ra ngoài màn hình / trả về vị trí cũ.` | `0x02bfb198` | Generic statement suggests restoring old position |
| `Hiện hết` | `0x02bfb255` (also `0x02bff70d`) | Visible label of the original toggle |
| Original show log prefix `[Ẩn] Đã hiện lại` | `0x02bfb39e` | Log string exists |
| Explicit show doc `Đưa các cửa sổ về góc trên trái (0,0), GIỮ NGUYÊN kích thước.` | `0x02bfb3d6` | Describes (0,0), preserving size |
| `_hide_windows_cmd` | `0x02bfa076`, `0x02bffde5` | Toggle callback marker |

The binary text also contains the show-log continuation `cửa sổ game về (0,0)` next to the `Đã hiện lại` prefix. Neither an emitted log nor a docstring is executed evidence by itself.

### Reproduction

On the original ZIP bytes, verify SHA-256 and extract `TLMTool_2.1.2/TLMTool.dist/TLMTool.exe` without altering it. A binary UTF-8 literal search for the strings above yields the offsets listed. The existing repository documents `docs/tasks/C12.md`, `docs/window/C12_HIDE_SHOW_FLOW.md`, `docs/window/C12_HIDE_SHOW_MODEL.json` and `docs/tasks/S57.md`/`S58.md` are consistent with the observed binary text, but their ambiguity is now independently reconfirmed against this exact specimen. Also searched the release ZIP's directly readable `.md/.txt/.json/.ini/.log/.lua/.py/.csv/.cfg/.xml` entries (under 25 MB each) for the restore identifiers and messages; **no additional text file resolved the C12 show branch**.

### Why this is not enough to implement Hiện hết

- `_saved_window_rects` may be used solely for hide-time bookkeeping or for one show branch. Mere co-location in a Nuitka constants table does not prove its use by a released execution path.
- A `(0,0)` show doc/log may be a faithful description, may cover one branch, or may be stale text. The generic older-position doc may likewise be stale. **The actual conditional branch and rectangle selection remain unknown.**
- The original executable's PE debug information / recoverable Python source is absent; the binary constant pool does not by itself recover the method's instruction-level data flow. A direct RIP-relative reference to the raw string would not establish semantics either.
- The verified C12 **hide-only** behavior and C10/C11 verified re-layout reset already have complete native tests and must remain untouched. Do not choose the specific doc just because it seems stronger.

## Specific original evidence needed to unblock

1. **Preferred:** authenticated original source of `TLMStartTab._show_all_game_windows` and `_hide_windows_cmd` including saved-rect reads, fallback, branch conditions and how hidden state is cleared.
2. **Alternative:** instrumented **authorized original EXE** running on a Windows desktop with two dedicated test game HWNDs. Record each HWND/PID/rect, invoke *Ẩn hết*, then *Hiện hết*, and capture the real rectangles before/after with GetWindowRect. Repeat with different initial positions, changing window count/PID, and C10/C11 between hide/show. Record signed Info state; do not infer availability from simulated authorization.
3. **Static executable reverse-analysis:** establish an instruction-level, independently reproducible control-flow/data-flow mapping between `_show_all_game_windows`, the Win32 SetWindowPos call sites, and conditional reads of `_saved_window_rects` in the exact PE hash. Raw string hits, Nuitka name markers or adjacent values are insufficient.

## Source/CI scope

**S107 is original-binary research only.** No `src/`, `tests/`, `.github/workflows/`, game/Info, original ZIP, locked `PLAN.md`, B04/S59 images or Proxy source modified. There is **no new S107 Windows CI claim**. Prior [S106 native Windows workflow 38065057307](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38065057307) COMPLETED SUCCESS: **1,564/1,564 tests**, **269** compiled files and selected genuine TEST-owned native Win32/DWM smokes. Original game not tested. The last S36 packaged executable remains DIAGNOSTIC `EXPLICITLY_BLOCKED_NO_GUI`, NOT PRODUCT.

## NEXT_ACTION S108

Investigate a different substantial missing original-backed behavior with obtainable proof, prioritizing C14 detached preview lifecycle/geometry before adding a visual-only button. Re-read LIVE PLAN/STATE, S107 and C14/S75/S85; only implement if actual arithmetic and embedded visibility control-flow can be verified. Otherwise preserve the exact blocker and document the next genuine runtime evidence required. Do NOT repeat passing C10/C11/C12 hide/C13 native implementations or create another synthetic Party adapter.
