# K15 — Tàng Bảo Đồ integrated lifecycle / failure matrix / static handoff

## 1. Scope

K15 is the Treasure closure task. It integrates K10–K14 into one reconstruction handoff and checks the complete top-level Treasure callable inventory from K01.

It does not re-open already-verified microdetails unless an actual contradiction appears.

## 2. Frozen authority

Exact original authority:
- `TLMTool_2.1.2(7).zip` SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`;
- archive size `93,715,901` bytes;
- inner `TLMTool.dist/TLMTool.exe` SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`;
- inner EXE size `47,450,112` bytes;
- `.daily_tab` frozen decode = `35,163 bytes / 1,186 top-level constants`.

## 3. Complete Treasure top-level callable coverage

K01's exact top-level Treasure-related inventory is fully accounted for:

- `_build_ui` -> K10 Treasure visible/config surface;
- `_apply_treasure_all` -> K10 selection-only behavior;
- `_treasure_start_worker` -> K10 inject-first activity wrapper;
- `_treasure_single_worker` -> K10 ownership + K13 recovery + K14 stop lifecycle;
- `_wait_movement_stopped` -> K11 exact Treasure call-site semantics;
- `_treasure_map_toggle` -> K10/K14 activity ownership and UI state;
- `_treasure_map_run_worker` -> K10/K14 batch selection/PID/open-loop/still-active behavior;
- `_treasure_map_disconnect_monitor` -> K13 event-adapter recovery surface;
- `_treasure_map_exec_sequence` -> K11-K14 activation/map96/heal/failure lifecycle;
- `_treasure_heal` -> K13 selected-map treatment;
- `_treasure_map_reset_ui` -> K10/K14 UI reset handoff.

No top-level Treasure callable from K01 remains uncovered.

## 4. Two orchestration models remain separate

### Activity-wide Treasure

`_treasure_start_worker`
-> inject/preparation
-> `_treasure_map_toggle`
-> `_treasure_map_run_worker`.

The batch snapshots:
- selected rows;
- selected PIDs;
- configured `tomb_dur`.

It then loops with `loop_idx`, recalculating `alive` / `still_active`, and can run eligible accounts in parallel.

### Per-row / bottom coordinator

`_toggle_single_acc` or `_start_all_accs`
-> `_treasure_single_worker`
-> `_treasure_map_exec_sequence`.

This path owns row/session identity through:
- HWND + PID;
- real row `_stop_event`;
- row generation snapshot;
- halt / respawn / monitor state;
- reconnect cache/memory recovery.

These two ownership models must not be collapsed in reconstruction.

## 5. Configuration handoff

Treasure user/config surface:
- tomb combat duration;
- low-HP treatment toggle;
- treatment map selector;
- reconnect toggle;
- respawn toggle;
- Apply-all.

Exact normal duration layer:
- UI seed = `30` seconds;
- missing-key config fallback = `30` seconds.

Exact helper fallback layer:
- direct `_treasure_map_exec_sequence` fallback `tomb_dur=5`.

Normal workers pass configured `tomb_dur`, so 30 versus 5 is layering, not contradiction.

Apply-all only sets current row activity selection to `Tàng bảo đồ`; it does not start execution.

## 6. Integrated Treasure cycle

Stable high-level order:

1. session/stop guard;
2. if `respawn_event` is set, clear it;
3. if Treasure heal is enabled and HP<30, call `_treasure_heal`;
4. prepare mount if needed;
5. open/verify bag;
6. find `tuido.tangBaoDo_multi`;
7. first map-item activation/use;
8. wait for movement stop through `_wait_movement_stopped(stop_check, skip_set)`;
9. second `tuido.tangBaoDo_multi` checkpoint/use;
10. enter post-activation MapID/tomb outcome region;
11. optional final HP<30 treatment;
12. cycle tail;
13. return to owning Treasure worker/session.

## 7. Mount and bag preparation

Mount preparation:
- read `IsRiding`;
- already riding -> skip mount-open work;
- use `common.nguaActive` readiness;
- exact fallback click `(1306,340)` if not active.

Bag preparation:
- use `tuido.active` readiness;
- preserve the exact bag/open/drag surfaces recovered in K11.

Unlabeled fixed coordinates remain unlabeled. K15 does not promote unresolved K11 click surfaces into invented button names.

## 8. Current Treasure item recognizer

Current call is exactly:
`find_multipixel('tuido','tangBaoDo_multi')`.

Current frozen pattern:
- region `(702,163)` to `(1132,517)`;
- offset `(20,30)`;
- base RGB `(2,30,35)`;
- offset RGB `(228,215,170)`;
- timeout `5`;
- tolerance `1`.

Legacy `tangBaoDo` / `tangBaoDo_multi_old` definitions are not the current Daily call.

Successful item activation uses the shared HWND background-click stack, not physical cursor movement.

## 9. Two-stage item use and terminal account exclusion

First item not found:
`dừng tàng bảo đồ cho acc này`.

Second item not found:
`not found (lần 2) → dừng tàng bảo đồ cho acc này`.

Both are:
`TERMINAL_CURRENT_TREASURE_ACCOUNT`.

`_treasure_map_skipped`, Treasure `skip_set`, and batch `still_active` filtering together provide strong static evidence that a terminally skipped account is excluded from later work during the active batch.

Exact `_treasure_map_skipped.add/discard/clear` statement placement remains UNKNOWN.

## 10. Movement-stop boundary

The exact Treasure call uses:
`_wait_movement_stopped(stop_check=..., skip_set=...)`

with no `by_memory` override.

Therefore this call uses the default:
`by_memory=False`

and the `MovementDetector / is_moving` 10-pixel branch.

It does not use the Direction+Pos memory branch.

## 11. Post-activation map96/tomb region

Exact surfaces include:
- `MapID=96 (huyệt mộ) → đánh <tomb_dur>`;
- state `Đánh trong mộ`;
- fixed click coordinates `(1135,124)` and `(955,123)`;
- move-to-map96 tile `(50,16)` through movement values `(1600,512)`;
- `common.active` wait;
- post-wait MapID outcome.

`tomb_dur` is seconds for the current tomb combat stage, not number of Treasure runs.

Exact timer primitive is still UNKNOWN; K15 does not copy Trừng Ác's monotonic timer.

The exact micro-order/meaning of fixed tomb clicks versus duration/movement/MapID read remains UNKNOWN.

## 12. Non-96 outcome

Exact text:
`không phải huyệt mộ, bỏ qua`.

Classification:
`SKIP_TOMB_OUTCOME / NOT_ACCOUNT_TERMINAL`.

This is intentionally distinct from terminal item-not-found.

## 13. Treasure treatment

Selected-map coordinates:
- Đại Lý `(43,178)`;
- Lạc Dương `(255,126)`;
- Tô Châu `(155,252)`;
- Lâu Lan `(27,183)`.

`_treasure_heal` resolves the selected map name through `MAP_LIST`, then moves to the selected Treasure coordinate.

No Treasure-specific tolerance override is present in the compact helper, so shared `move_character` default tolerance `48` remains the applicable default.

No Treasure-specific fixed treatment click or `_punish_heal`-style reinjection behavior is recovered.

Start-heal failure:
`SKIP_CURRENT_CYCLE`.

Final-heal failure:
`FAIL_SOFT / LOG_ONLY`.

## 14. Disconnect recovery

`_treasure_map_disconnect_monitor` has a thin event-adapter shape rather than a second independent full detector.

The shared Daily detector layer remains:
- 2-second cadence;
- memory-connected True veto;
- both disconnect pixels for 3 consecutive ticks;
- halt;
- reconnect click `(616,455)`.

Treasure activity-wide recovery is bounded:
- detected -> wait;
- reconnect OK -> continue;
- timeout -> stop.

Treasure-specific timeout numeric remains UNKNOWN.

The per-row worker owns Reader-cache invalidation and `wait_memory_ready` recovery surfaces.

No unconditional forced post-reconnect DLL reinjection is proven.

## 15. Death / Địa-phủ recovery

Shared Daily death monitor:
- cadence 4 seconds;
- HP0 -> click `(792,441)`;
- MapID87 -> `respawn_event.set()`.

Treasure workers own `respawn_event` and the next Treasure execution explicitly clears it before HP/heal/movement.

Therefore death/Map87 is:
`RECOVERABLE_INTERRUPT`

not an account-completion condition.

Exact simultaneous disconnect/death priority remains UNKNOWN.

## 16. Integrated failure matrix

| Condition | Class | Outcome |
| --- | --- | --- |
| No Treasure rows selected | BATCH NO-OP | No Treasure work starts |
| No selected row remains live | BATCH TERMINAL | Stop activity worker |
| All selected rows stopped/skipped/ineligible | BATCH TERMINAL | Auto-stop activity worker |
| First item recognition missing | TERMINAL CURRENT TREASURE ACCOUNT | Exclude affected account |
| Second item recognition missing | TERMINAL CURRENT TREASURE ACCOUNT | Exclude affected account |
| Start heal fails | SKIP CURRENT CYCLE | Account can try a later cycle |
| MapID != 96 | SKIP TOMB OUTCOME | Continue cycle tail |
| Final heal fails | FAIL-SOFT / LOG-ONLY | Finish cycle tail |
| Reconnect succeeds | RECOVERABLE INTERRUPT | Continue Treasure |
| Reconnect recovery times out | TERMINAL AFFECTED RECOVERY PATH | Stop affected path |
| Death / Map87 | RECOVERABLE INTERRUPT | respawn_event recovery |
| User cancels Treasure batch | CONTROL STOP | `cancel(batch-tàng-bảo-đồ)` |
| Row stop Event | CONTROL STOP | `stop_event(dừng)` |
| Row generation changes | CONTROL STOP | `gen(phiên-mới)` |
| Window/PID becomes invalid | CONTROL STOP | `window-chết/đổi-process` |

## 17. Stop and UI reset handoff

Treasure activity UI:
- running: `Dừng lại / FireBrick`;
- stopping: `Đang dừng... / disabled`;
- idle: `Tàng bảo đồ / RoyalBlue / normal`.

Bottom all-account stop:
- set row `_farming_acc=False`;
- signal row `_stop_event`;
- row workers unwind cooperatively.

Singleton `_daily_all_monitor`:
- wait until every Daily row session has stopped;
- call `_punish_reset_ui`;
- call `_treasure_map_reset_ui`;
- log automatic reset.

`_sync_start_tab_btns` handles external StartTab synchronization.

Exact teardown statement ordering remains UNKNOWN.

## 18. Contradiction audit

No blocking contradiction exists across K10-K14.

Resolved layering:
- production Treasure duration = 30 by default;
- direct exec helper fallback = 5.

Preserved UNKNOWNs include:
- Treasure reconnect timeout numeric;
- effective explicit `common.active` timeout numeric;
- exact Treasure skipped-set mutation/clear order;
- tomb timing primitive;
- meanings/order of unresolved fixed clicks;
- Treasure heal post-arrival microaction;
- adapter native call edge/event propagation;
- simultaneous death/disconnect priority;
- final UI teardown order.

No K10-K14 artifact requires corrective rewriting.

## 19. Runtime/B08 boundary

The packaged runtime log still contains no correlated end-to-end Treasure lifecycle trace.

B08 remains an idle configuration cross-check only.

K15 classification:
`STATIC_VERIFIED / END_TO_END_RUNTIME_ENV_REQUIRED`.

## 20. Static handoff status

From the Tàng Bảo Đồ perspective:
- all top-level callables are covered;
- configuration, orchestration, activation, movement, map96/tomb, heal, recovery, skip/stop and UI reset contracts are internally consistent;
- no blocking static contradiction remains.

Therefore:
`TREASURE STATIC HANDOFF COMPLETE`.

This does not mean the overall project is ready for Stage S. Phase K shared/runtime work and later PLAN phases remain.

Next: K16 — Daily shared cross-activity lifecycle / persistence / UI-coordinator integration audit.