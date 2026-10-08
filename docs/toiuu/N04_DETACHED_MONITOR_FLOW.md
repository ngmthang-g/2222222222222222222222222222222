# N04 — Tối ưu detached CPU/GPU monitor lifecycle, geometry, persistence

## Authority and continuity
N04 was selected from `STATE.md` after confirming that GitHub `main` HEAD was `0d18f577b3be9d23893595d8e88c69570642c832` and no N04 artifacts existed. PLAN stage N requests detached monitor research. N01–N03 and B11 were retained as frozen evidence rather than rerun or modified.

Frozen authority: uploaded `TLMTool_2.1.2(9).zip` SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, 1,050 ZIP entries, CRC check clean. Original inner `TLMTool.dist/TLMTool.exe` SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, 47,450,112 bytes. Static read-only EXE analysis only; neither the EXE, the game nor its payload is executed.

Active original class: `toiuu_tab.ToiuuTab`; compiled module marker `.toiuu_tab` at `0x2c01fb5`. The findings below use exact recovered symbols, encoded constants, method-local metadata and original embedded Vietnamese documentation; they are **not** recovered Python AST/source statements.

## 1. Real feature and distinct ownership
The `Giám sát CPU/GPU` group contains a real clickable `Tách theo dõi` button bound to `_toggle_monitor_view`. These **six distinct methods** have original exact class-method markers:

| Method | Role established by original module symbols |
|---|---|
| `_toggle_monitor_view` | toggle current detached view via `winfo_exists` / close/open actions |
| `_open_monitor_view` | create/configure a separate Tk window |
| `_close_monitor_view` | close the detached view |
| `_update_monitor_view` | update detached-panel presentation from the Tối ưu redraw service |
| `_restore_monitor_view` | restore previous open state after startup |
| `_save_monitor_state` | save open/closed state in settings |

The exact toggle documentation says:

> Mở/đóng view bar CPU/GPU tách rời (sát cạnh trái GUI chính, cao 768).

This supports intended placement relative to the main GUI (near its left edge) and a **documented nominal height of 768**, but no full screen-position formula has been decompiled. The words “view bar” do not imply an additional independent CPU/GPU sampling worker.

The main chart collection remains N02/N03. `_update_monitor_view` occurs within the shared graph-redraw method region. Reuse of existing chart state is a strong component-level inference; the exact GUI update frequency and whether every redraw forces detached updates require runtime evidence.

## 2. Startup/restore lifecycle
The `ToiuuTab.__init__` compiled constant region contains in order:
- `_build_ui`, `_load_config`, `<Destroy>` / `_save_on_destroy`;
- `_start_refresh`, `_start_watch`, `_start_graphs`;
- `after`, `_restore_monitor_view`.

A separate exact embedded document states:

> Tự mở lại panel theo dõi nếu lần trước thoát app khi đang mở.

Therefore the original has a real delayed/restoration entry point after startup, rather than only a manual pop-out button. The precise `after` delay, all construction-time thread states, and what happens if there is no parent HWND at restoration remain unknown.

Constructor has `_monitor_open_saved` and `_closing` fields. These establish monitor/open and widget-destruction state; exact boolean mutation and error order are **not** reconstructed.

## 3. Real Tk detached-window structure
The compiled `_open_monitor_view` constant region contains:
- `winfo_toplevel`, `winfo_rootx`, `winfo_rooty` to anchor the detached view to the main Tk UI;
- `tk.Toplevel`, `title("CPU / GPU")`;
- `overrideredirect`, `geometry`, `minsize`, `maxsize`;
- `attributes` with `-topmost`;
- `protocol` with `WM_DELETE_WINDOW`;
- log strings showing monitor-open geometry diagnostics and `geometry loi:` error handling.

This is **a genuine separate Tk Toplevel**, not a screenshot embedded into the original tab. It includes border-override/topmost configuration surfaces; the exact Boolean arguments are not safely readable from constant proximity alone.

The local-variable region independently contains `root, rx, ry, width, height, win, geo, body, col_cpu, col_gpu`. This strongly supports calculating location and dimensions from a root-window anchor and creating internal CPU/GPU columns.

**Geometry rule:** Keep the original 768-height/left-of-parent intent, but mark actual width, offsets, clipping on screen edges, monitor DPI and `minsize/maxsize` arguments as UNKNOWN. Do not hardcode unexplained numbers or invent a detached-window pixel baseline.

## 4. Visible detached content
The Toplevel build region includes:
- `_make_bar_col` called with labels `CPU` and `GPU`;
- an explicit button/action surface `Đóng theo dõi`;
- Canvas drawing primitives `create_rectangle`, `create_text`, `coords`;
- fallback `--%`, `Segoe UI` bold, text fill black, background/outline light gray `#e0e0e0`;
- a second `Tách theo dõi` string in the auxiliary drawing area.

The original **bar-column design is different from assuming two full 414×66 line charts are cloned pixel-for-pixel**. It has per-column bar/text widgets. `_update_monitor_view` can refresh the auxiliary representation. Exact bar width, percentage text geometry, fill formula and gradient are not source-proven and need later Windows evidence.

The tab `CPU: 15%` / `GPU: N/A` screenshot does not show the detached panel, so it cannot prove the auxiliary panel's layout or bar-state rendering.

## 5. Persistence and close behavior
The original configuration region contains:
- `CONFIG_DIR`, `makedirs`, `_settings_lock`, `read_settings`, `write_settings`;
- section `Settings`;
- key `toiuu_monitor_open`;
- encoded `1`/`0` candidates around the save key;
- exact docs describing saving the monitor-open button state in `settings.ini` for next startup;
- error string `[TOIUU] Save monitor state error:`.

The load-config region also contains `toiuu_monitor_open`, `strip` and case/boolean-looking tokens `true`, `yes`, `on`. This supports loading a persisted truth-like state (not simply an in-memory toggle), with the exact parsing expression left UNKNOWN.

The open window defines `WM_DELETE_WINDOW` and offers a `Đóng theo dõi` action; the toggle method references `_close_monitor_view` and `_open_monitor_view`. The method-local region for save includes `is_open` and `cfg`. These are **separate** responsibilities from `_save_running_set` and saved per-character TLMP modes.

Open/close state is expected to persist, but original exact ordering of save → destroy → update StartTab shortcuts, behavior when close fails, crash without normal Destroy, and callback cancellation is unproven. Never claim all those races handled just because `<Destroy>` exists.

## 6. CPU/GPU synchronization and thread safety
The original `_redraw_graphs` method region directly references `_update_monitor_view`. N02 established worker sampling + Tk-main-thread redraw, and the module's `_ui` documentation says Tk must not be touched from a worker thread.

This gives a high-confidence architectural contract: **do not start a second GPU/CPU sample stream just to feed the detached view** without proof of original behavior. Use the existing sampled histories/availability as the authority and deliver UI drawing through Tk-compatible scheduling.

The exact `_update_monitor_view` tick policy, widget existence checks under rapidly repeated open/close, chart rate limiting, and close while GPU subprocess is outstanding remain runtime-required.

## 7. Screenshot cross-check (done AFTER binary extraction)
B11 verified screenshot: selected tab `Tối ưu`, top group `Giám sát CPU/GPU`, real `Tách theo dõi` button, CPU 15% and blue line, GPU N/A and empty line. **No detached Toplevel was visible in that capture.**

The screenshot confirms placement and label of the *button in the main tab*, not the bar-panel width, topmost policy, pop-out location or dynamic percentage bars. No new screenshot geometry was fabricated.

## 8. Future acceptance cases (planned; NOT_RUN)
| ID | Original parity requirement | Gate |
|---|---|---|
| N04-01 | `Tách theo dõi` toggles real Toplevel rather than placeholder | Stage-S + Windows |
| N04-02 | Title CPU / GPU, two CPU/GPU bar columns and close control | Stage-S + visual |
| N04-03 | Placement anchored left of parent with documented 768 height | Windows multi-display |
| N04-04 | Compare exact width, offsets, DPI, clamp/min/max and edge behavior | Original Windows trace |
| N04-05 | Test `overrideredirect` and `-topmost` effective flags | Original Windows trace |
| N04-06 | WM_DELETE_WINDOW/window X and `Đóng theo dõi` close same correct state | Windows |
| N04-07 | Rapid button toggling does not leak multiple Toplevels or crash | Windows stress |
| N04-08 | `[Settings] toiuu_monitor_open` save/reload round-trip | Config round-trip |
| N04-09 | Restore old-open window only when persisted state and current UI permit | Windows restart |
| N04-10 | Handling when save fails or config value is malformed | Windows fault injection |
| N04-11 | CPU/GPU bar values stay synchronized with main graph histories | Windows live |
| N04-12 | GPU None/unavailable displays correct auxiliary state (not fake 0%) | Windows live |
| N04-13 | Update/destroy callbacks remain on Tk thread | Windows thread instrumentation |
| N04-14 | Closing main TLMTool leaves no orphan panel or callback to dead widgets | Windows teardown |
| N04-15 | Hidden/off-screen/minimized main GUI and multiple monitors place panel acceptably | Windows layout |
| N04-16 | Original-vs-reconstructed auxiliary screenshot and functional parity | Stages V/W/X |

All 16 cases are **NOT_RUN**. Static analysis does not mean a working clone or a passing Windows test.

## 9. Result, non-goals and next work
**N04: STATIC_DETACHED_MONITOR_LIFECYCLE_AND_UI_AUDITED / LIVE_PARITY_DEFERRED.**

Do not modify N01–N03, PLAN, B11, the original EXE, other tabs or Proxy feature code. No source/build placeholders or imaginary working buttons were created.

**NEXT_ACTION:** **N05 — Tối ưu graphics-mode mapping, account configuration and selection-versus-application audit**. Start from the exact original `ToiuuTab` binary mode/combobox/config bindings, compare B11 only afterward. Native `send_perf_command` payload/handshake should be audited as a later separate N06, not guessed in N05.
