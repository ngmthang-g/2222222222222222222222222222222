# K16 — Daily shared cross-activity lifecycle / persistence / UI-coordinator integration flow

## 1. Scope

K16 audits only Daily infrastructure shared by Trừng Ác and Tàng Bảo Đồ. K09 and K15 are treated as closed activity contracts.

Shared surfaces covered here:
- account discovery and HWND/PID identity;
- row/session lifecycle;
- shared injection;
- manual Tới bổ đầu / Trị liệu actions;
- per-row and all-row coordinator ownership;
- Tk-safe row state updates;
- global Daily monitor and StartTab synchronization;
- Daily config load/save/destroy persistence;
- cross-domain ownership/race boundaries.

## 2. Frozen original rechecked first

Exact specimen:
- `TLMTool_2.1.2(7).zip` SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`;
- size `93,715,901` bytes;
- ZIP CRC test clean;
- inner `TLMTool.exe` SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`;
- inner size `47,450,112` bytes.

## 3. Shared callable coverage

K02 already covered the shared roster/UI/session coordinator family. K16 closes the remaining shared top-level gaps:
- `_validate_repeat`;
- `_ensure_injected`;
- `_inject_all_windows`;
- `_move_bo_dau`;
- `_move_bo_dau_all`;
- `_heal_bo_dau`;
- `_heal_all`;
- `_save_on_destroy`;
- `_load_config`;
- `_save_config`.

After K16, no shared/cross-activity top-level Daily callable from K01 remains unaccounted for.

## 4. Account discovery and identity

Daily refresh remains incremental every 5 seconds.

Identity is not HWND-only:
`HWND + bound PID`.

If the same numeric HWND is reused by a different process, Daily treats the previous logical row as stale and recreates it.

Row runtime/session fields remain transient:
- `_farming_acc`;
- `_stop_event`;
- `_gen`;
- `_state`;
- bound PID.

They are not recovered as durable Daily settings.

## 5. Row activity selection

Each row dispatches exactly one selected activity through `_toggle_single_acc`:
- `Trừng ác` -> `_punish_single_worker`;
- `Tàng bảo đồ` -> `_treasure_single_worker`.

Activity selection belongs to row runtime/UI state and is not persisted.

The new-row static block strongly places `Trừng ác` before the readonly `Trừng ác / Tàng bảo đồ` values, consistent with Trừng Ác as the fresh-row selection surface. K16 does not use that as evidence of durable persistence.

## 6. Event + generation session protection

Each row has:
- a real `_stop_event`;
- `_gen` session generation.

`_GenStop` becomes set if:
- the real stop Event is set; or
- the row generation no longer equals the worker snapshot.

This is the exact stale-worker defense against rapid Stop -> Start.

Do not reconstruct the row lifecycle with a reusable Event alone.

## 7. Shared state-label marshalling

Shared state path:

`worker`
-> `_set_state`
-> `_schedule_state_label`
-> `Tk after(0)`
-> `_apply_state_label`.

This contract applies to both activity families.

Background worker threads must not directly mutate the row's Tk state widgets.

## 8. Shared injection layer

`_ensure_injected(hwnd)` uses:
- DLL injector;
- current HWND->PID resolution;
- default DLL path;
- `resources.dat` injection.

Its exact documentation says to inject only when not already injected.

`already loaded` is an accepted ready/success outcome.

This matters cross-activity because:
- activity-wide Trừng Ác start injects first;
- activity-wide Treasure start injects first;
- bottom all-account start also performs shared injection/preparation.

Repeated access to the helper is therefore designed around an already-loaded state rather than blindly duplicating injection.

`_inject_all_windows` applies this to currently-open game windows and reports the number successfully injected.

## 9. Manual Tới bổ đầu

One-account helper:
`_move_bo_dau`.

Exact target:
`Tô Châu, map 4, tile (224,285)`.

Exact shared behavior includes:
- window liveness check;
- Daily runtime permission surface;
- injection attempt;
- injection failure is fail-open: try direct movement anyway;
- shared `move_character`.

All-account helper:
`_move_bo_dau_all`.

It uses shared all-window injection/preparation and parallel child work, then joins and reports completion.

This manual action does not select a Trừng Ác/Treasure execution worker; it targets account HWNDs directly.

## 10. Manual Trị liệu

One-account helper:
`_heal_bo_dau`.

Exact destination:
`Tô Châu, map 4, tile (155,252)`.

It includes a HWND-targeted `click_at` treatment surface.

All-account helper:
`_heal_all`.

It runs the per-account treatment work in parallel.

Like Tới bổ đầu, this is a manual shared action rather than an activity dispatch.

The exact rule preventing or allowing these manual actions while the same HWND is owned by an active worker is not independently bound and remains a runtime boundary for K17.

## 11. Bottom all-account coordinator

Idle branch:

`Bắt đầu`
-> shared injection/preparation
-> inspect each non-running row
-> dispatch according to current activity selection
-> start one per-account worker per eligible row
-> switch bottom control to `Dừng lại / #f44336`
-> ensure singleton Daily monitor.

Running branch:

`Dừng lại`
-> each running row `_farming_acc=False`
-> set each row `_stop_event`
-> restore row play controls / bottom `Bắt đầu / #388e3c`
-> workers unwind cooperatively.

A Trừng Ác row in teleport mode without a configured hotkey can be rejected at this coordinator boundary without affecting Treasure rows.

## 12. Global Daily monitor

`_ensure_daily_monitor` guarantees only one `_daily_all_monitor`.

The monitor waits until all per-row Daily sessions are no longer running.

Then it resets both activity UIs:
- `_punish_reset_ui`;
- `_treasure_map_reset_ui`.

Exact completion text:
`[Bắt đầu] Tất cả acc đã dừng — tự động reset UI`.

This is a row-session monitor. It is not evidence of a force-kill mechanism.

## 13. Activity-wide ownership is a separate domain

Trừng Ác activity-wide state:
- `_punish_running`;
- `_punish_cancel`.

Treasure activity-wide state:
- `_treasure_map_running`;
- `_treasure_map_cancel`.

Per-row/bottom state:
- row `_farming_acc`;
- row `_stop_event`;
- row `_gen`.

These are separate ownership domains.

No unified `Daily owner token` or mutex was recovered.

Equally, K16 cannot instruction-bind a specific guard proving that an activity-wide worker and a row-level worker can never target the same HWND simultaneously.

Therefore:
- do not invent a new mutex during static reconstruction;
- do not assume overlap is safe;
- preserve both state domains;
- test the original overlap behavior in K17.

## 14. StartTab synchronization

`_sync_start_tab_btns` explicitly synchronizes external Trừng Ác/Tàng Bảo Đồ controls on StartTab.

This is UI synchronization across tabs.

It does not by itself prove worker mutual exclusion between activity-wide and row-level ownership domains.

## 15. Daily persistence

Shared settings infrastructure:
- `CONFIG_PATH`;
- `CONFIG_DIR`;
- `_settings_lock`;
- `read_settings`;
- `write_settings`;
- section `Settings`.

Exact load-side Daily config surface includes:
- `daily_punish_duration`;
- `daily_tele_use`;
- `daily_move_mode`;
- `daily_tele_hotkey`;
- `daily_treasure_map_tomb_dur`;
- `daily_treasure_heal`;
- `daily_treasure_heal_map`;
- `daily_punish_heal`;
- `daily_punish_discard_equip`;
- `daily_punish_dc_reconnect`;
- `daily_punish_respawn`;
- `daily_treasure_dc_reconnect`;
- `daily_treasure_respawn`.

The write region contains the visible Daily configuration keys and calls `write_settings`.

No durable keys were recovered for:
- per-row activity selection;
- bound PID;
- `_farming_acc`;
- `_stop_event`;
- `_gen`;
- current row state.

So those values are session state, not Daily persistence.

## 16. Teleport compatibility persistence boundary

`daily_move_mode` is exact on the load side together with `daily_tele_use` and `old_tele_use` compatibility logic from K03.

A second literal `daily_move_mode` is not visible in the save block, but Nuitka can reuse string constants through backreferences.

Therefore K16 does not claim that `daily_move_mode` is never saved.

Exact migration/write expression remains UNKNOWN.

## 17. Destroy/save boundary

Constructor state includes:
- `_closing`;
- `_saving_enabled`;
- refresh state.

`<Destroy>` is exactly bound to `_save_on_destroy`.

`_save_config` has the shared settings write surface and `[DAILY] Save error:` fallback.

However the exact `_save_on_destroy` cleanup sequence among:
- setting `_closing`;
- stopping refresh;
- stopping activity/discard/monitor work;
- saving config;
- final widget destruction

is not native-instruction-bound.

K16 keeps the save-on-destroy contract and leaves exact cleanup order UNKNOWN.

## 18. Numeric validator

`_validate_repeat` exposes an `isdigit` generator surface and is the shared numeric-entry validator.

Its historical method name must not be interpreted as evidence of a user run-count setting: K03 and K10 independently prove no Trừng Ác/Treasure repeat-count configuration.

Exact empty-string/cleanup behavior remains UNKNOWN.

## 19. Cross-activity contradiction audit

No blocking contradiction is found between:
- K02 shared row/session coordinator;
- K09 Trừng Ác handoff;
- K15 Treasure handoff.

Important preserved distinctions:
- activity-wide state is separate from row-session state;
- activity Apply-all selection remains transient;
- both activities share injection, Tk state marshalling, window identity and global reset infrastructure;
- manual shared actions are HWND/account actions, not activity workers;
- static evidence does not resolve all same-HWND overlap/race ordering.

## 20. Runtime/B08 cross-check

Only after static integration, the exact packaged runtime log was checked.

SHA-256:
`17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`.

Size:
`15,741,058 bytes / 387,238 lines`.

Correlated counts are zero for:
- `[Daily]`;
- `[Bắt đầu]`;
- `[Inject]`;
- `DailyTab`;
- `Tới bổ đầu`;
- `[Trị liệu]`;
- `Trừng ác`;
- `Tàng bảo đồ`.

B08 shows an idle Daily tab with an empty account list, so it cannot prove populated-row concurrency, owner collisions, or destroy-time ordering.

K16 classification:
`STATIC_VERIFIED / END_TO_END_RUNTIME_ENV_REQUIRED`.

## 21. K16 result

After closing the remaining shared helpers, no shared/cross-activity top-level Daily callable from K01 remains uncovered.

The static Daily architecture is internally consistent:
- K09 Trừng Ác handoff complete;
- K15 Treasure handoff complete;
- K16 shared integration complete.

Runtime concurrency/parity remains the remaining Phase-K closure boundary.

Next: K17 — Daily integrated runtime/parity closure matrix and Phase-K handoff.