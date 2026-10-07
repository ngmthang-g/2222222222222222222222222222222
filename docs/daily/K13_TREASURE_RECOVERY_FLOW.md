# K13 — Tàng Bảo Đồ heal / reconnect / respawn recovery flow

## 1. Scope

K13 continues from the K12 cycle-tail boundary and audits Treasure recovery only:
- selected-map low-HP treatment;
- start-heal versus final-heal failure behavior;
- Treasure disconnect adapter and activity-wide reconnect shell;
- per-row cache/memory recovery;
- shared death/Địa-phủ event integration.

K10-K12 ownership, activation and map96 contracts are preserved unchanged.

## 2. Recovery configuration

Exact missing-key fallbacks:
- `daily_treasure_heal = "0"`;
- `daily_treasure_heal_map = "Tô Châu"`;
- `daily_treasure_dc_reconnect = "1"`;
- `daily_treasure_respawn = "1"`.

B08 captured current state:
- heal OFF;
- heal location Tô Châu;
- reconnect ON;
- respawn ON.

Current screenshot state and missing-key fallback are separate layers.

## 3. Death/respawn cycle entry

Exact execution text:
`[Tàng bảo đồ]   respawn_event đang set → clear, cho heal/move rời map 87`.

So a prior death/Map87 signal is consumed at the next Treasure execution boundary rather than treated as completed/terminal work.

Immediately after that boundary the execution sequence reads HP.

## 4. Start-of-cycle heal

Exact surfaces:
- `[Tàng bảo đồ]   HP=<...>`;
- `[Tàng bảo đồ]   HP < 30% → trị liệu`;
- helper `_treasure_heal`;
- failure: `[Tàng bảo đồ]   Heal thất bại → skip vòng này`.

Therefore start-heal failure is:
`SKIP_CURRENT_CYCLE`

not a permanent stop of that Treasure account.

## 5. Exact selected-map treatment helper

`DailyTab._treasure_heal` exact locals:
`self, hwnd, stop_check, heal_map, coords, heal_tile_x, heal_tile_y, map_id, name, mid, e, ok`.

The static validation chain is:

selected heal_map?
-> no: `chưa chọn vị trí trị liệu`

coordinate table contains heal_map?
-> no: `không có tọa độ cho map <...>`

resolve selected name through `MAP_LIST`
-> invalid: `map_id không hợp lệ`

call movement subsystem
-> failure: `di chuyển đến vị trí trị liệu thất bại`

success
-> `trị liệu tại <heal_map> thành công`.

## 6. Exact selectable heal coordinates

`TREASURE_HEAL_COORDS`:
- Đại Lý `(43,178)`;
- Lạc Dương `(255,126)`;
- Tô Châu `(155,252)`;
- Lâu Lan `(27,183)`.

The helper resolves the selected map name to a map ID dynamically through `MAP_LIST`; K13 does not hardcode invented map IDs for names whose ID is not independently bound here.

## 7. Treasure heal movement boundary

Exact movement keyword surface:
`wait_for_arrival / stop_check`.

There is no `tolerance` keyword in the Treasure helper's compact move surface.

Shared `move_character` default tolerance is `48`, so that is the effective default unless later exact native evidence proves an internal override.

The exact Boolean passed to `wait_for_arrival` is not independently bound.

## 8. Do not import Trừng Ác treatment internals

`_punish_heal` has its own reinjection/tolerance behavior. Treasure does not expose the same compact constants.

K13 therefore does not copy:
- `_punish_heal` reinjection failure behavior;
- manual Tô Châu treatment click coordinates;
- any assumed fixed post-arrival treatment click.

No Treasure-specific fixed treatment-click coordinate is serialized in the `_treasure_heal` compact block.

The exact additional action after arrival, if any, remains UNKNOWN rather than invented.

## 9. Final-heal boundary

K12 already froze:
`[Tàng bảo đồ]   Heal cuối vòng thất bại`.

The same Treasure heal subsystem is used at the cycle tail when enabled and HP is low.

Unlike the start-heal branch, failure here is already at the cycle tail and has no separately recovered account-terminal stop.

Classification:
`FAIL_SOFT / LOG_ONLY`.

## 10. Treasure disconnect monitor is an adapter shape

Exact method:
`DailyTab._treasure_map_disconnect_monitor`.

Exact local model:
`self, hwnd, halt, respawn_event, stop_event, ev, real_set`.

Compare this with the full Daily detector `_punish_disconnect_monitor`, whose locals include:
`win32gui, check_pixel, dc_strikes, MI, conn, dc1, dc2`.

The Treasure method does not expose a second copy of those detector locals. Instead it owns an event-bridge shape through `ev` and `real_set`.

Strong static conclusion:
- Treasure reuses/delegates into the existing Daily disconnect detector layer rather than maintaining a second independent pixel/memory detector;
- exact native call edge and exact `ev/real_set` propagation ordering are not line-by-line proven.

## 11. Shared Daily detector contract

The already-verified Daily detector layer is:
- poll every 2 seconds;
- memory `Connected=True` vetoes a false positive;
- both disconnect pixels must persist for 3 consecutive ticks (~6s);
- confirmed disconnect signals halt;
- click `(616,455)`.

Exact pixels:
- `login.ngatKetNoi1`: `(640,244)`, RGB `(160,145,52)`;
- `login.ngatKetNoi2`: `(702,453)`, RGB `(212,28,34)`.

K13 preserves this as the shared detector contract while keeping Treasure's adapter propagation micro-order explicit UNKNOWN.

## 12. Activity-wide Treasure reconnect shell

Exact nested surface:
`_treasure_monitor_stops`.

Exact messages:
- `Phát hiện mất kết nối → chờ kết nối lại...`;
- `Kết nối lại OK → tiếp tục`;
- `Kết nối lại timeout → dừng`.

This proves a bounded reconnect shell.

The exact Treasure timeout number is not independently bound. K13 deliberately does not copy Trừng Ác's exact 60-second number by analogy.

Success returns the affected Treasure activity path to normal continuation. Timeout is terminal for the affected recovery/account path.

## 13. Per-row/single-account recovery

`_treasure_single_worker` exact locals include:
- `halt`;
- `respawn_event`;
- `monitor_stop`;
- `rm`;
- `invalidate_character_cache`;
- `_get_pid_from_hwnd`;
- `wait_memory_ready`;
- `_exit_why`.

This freezes a post-reconnect/session memory-refresh boundary.

Shared exact cache rule:
`invalidate_character_cache` is used after reconnect/reload because stale Reader pointer chains can otherwise survive.

Shared exact `wait_memory_ready` semantics:
- RoleName must be clear/non-placeholder;
- MapID must not be None;
- cache is invalidated for fresh samples;
- timeout returns False/logs and fails open.

Shared helper defaults are:
`timeout=45.0, need=3, interval=1.0`.

The exact Treasure call override values are not independently instruction-bound. K13 records the helper defaults separately instead of pretending the Treasure call explicitly passed 45/3.

## 14. No forced post-reconnect reinjection

No unconditional Treasure-specific post-reconnect DLL reinjection edge is independently recovered.

Do not add one merely because another activity has guarded injection around movement.

## 15. Shared death/Địa-phủ integration

The shared Daily `_diaphu_monitor` contract was already recovered exactly:
- cadence 4 seconds;
- HP 0 -> click `(792,441)` revive;
- MapID 87 -> `respawn_event.set()`.

Treasure activity and single-worker local models both own:
- `respawn_event`;
- `monitor_stop`;
- `rm` monitor handle.

Treasure execution then explicitly consumes/clears `respawn_event` at the next cycle entry.

Thus death/Map87 is a recoverable Treasure transition:

HP0 / Map87
-> shared death monitor signals recovery
-> current Treasure work unwinds/interruption boundary
-> next Treasure exec sees respawn_event
-> clear event
-> HP/start-heal boundary
-> normal Treasure movement/activation can leave map87.

Exact thread-launch statement ordering remains UNKNOWN.

## 16. Simultaneous disconnect/death

Both `halt` and `respawn_event` exist in the same Treasure session shell.

The exact precedence when both become set in the same scheduling window is not instruction-bound.

K13 keeps this explicit UNKNOWN instead of inventing priority.

## 17. Runtime/B08 cross-check

Only after static extraction, packaged `automove_log.txt` was searched.

Counts are zero for Treasure-correlated:
- heal failure/success;
- reconnect detected/OK/timeout;
- Treasure disconnect monitor;
- respawn_event/Địa-phủ;
- HP0 revive coordinate;
- reconnect coordinate;
- memory-ready/cache-ready markers.

Exact log SHA-256 remains:
`17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`.

B08 confirms only current control state, not live recovery behavior.

K13 remains:
`STATIC_VERIFIED / END_TO_END_RUNTIME_ENV_REQUIRED`.

## 18. Reconstruction boundary

Preserve:
1. respawn_event clear at Treasure cycle entry;
2. HP<30 start heal and start-heal current-cycle skip;
3. selected-map Treasure treatment coordinates;
4. dynamic map-name -> MAP_LIST map_id resolution;
5. Treasure movement failure as helper failure;
6. no invented Treasure treatment click/reinject logic;
7. final-heal fail-soft/log-only;
8. Treasure disconnect adapter/event-bridge shape;
9. shared Daily detector semantics as the detector layer;
10. Treasure bounded activity reconnect shell without invented timeout numeric;
11. per-row cache invalidation/memory-ready recovery boundary;
12. shared death/Map87 event model and Treasure cycle re-entry.

Keep UNKNOWN:
- exact config gate placement;
- wait_for_arrival Boolean;
- post-arrival treatment microaction;
- `ev/real_set` propagation order;
- native detector-delegation call edge;
- Treasure reconnect timeout numeric;
- Treasure memory-ready override args;
- single-worker reconnect pre-wait/unwind micro-order;
- forced post-reconnect reinjection;
- death-monitor thread-launch order;
- disconnect/death simultaneous-event precedence;
- live runtime parity.

Next: K14 — Tàng Bảo Đồ skipped-account / stop-reset / failure-lifecycle audit.