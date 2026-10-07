# K09 — Trừng Ác integrated lifecycle / failure matrix / static handoff

## 1. Scope

K09 does not re-open K03–K08 unless a contradiction appears. It integrates the already-verified Trừng Ác surfaces into one reconstruction handoff and checks whether any top-level Trừng Ác callable is still uncovered.

Exact frozen authority was re-inspected first:
- archive SHA-256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd;
- inner TLMTool.exe SHA-256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22;
- .daily_tab decoded as 35,163 bytes / 1,186 top-level constants.

## 2. Two entry architectures must remain separate

Activity-wide Trừng Ác:
_punish_start_worker -> _punish_toggle -> _punish_run_worker.

It snapshots rows selected as Trừng ác plus PID identity, owns _punish_cancel, iterates with loop_idx, filters live/still-active accounts every outer iteration, and stops when cancelled, no live account remains, or every selected account has stopped.

Per-row / bottom all-account Trừng Ác:
_toggle_single_acc or _start_all_accs -> _punish_single_worker.

Each row owns its own real stop Event plus generation snapshot through _GenStop. The single worker is itself iterative. The bottom coordinator may mix Trừng ác and Tàng bảo đồ rows and is not the same worker as the activity-wide batch.

## 3. Integrated normal cycle

One successful Trừng Ác cycle is:

1. Check stop/session/window state at cycle entry.
2. If respawn_event is set, clear it so heal/movement can leave map 87.
3. If enabled and HP < 30%, run start-of-cycle treatment.
4. If teleport mode is selected, run the teleport pre-step.
5. Move to bổ đầu in Tô Châu, map 4, tile (224,285).
6. Run fixed return-quest clicks.
7. Run fixed receive-quest clicks.
8. Check the Ngô Giới daily 30/30 GameDialog.
9. Use Trừng Ác Lệnh item 40004000 and acquire target coordinates.
10. Fast-travel to the target.
11. Use the same item again and activate Triệu hồi.
12. Enter Đánh ác tặc combat; call start_auto_train and run the monotonic punish_duration window.
13. Run the post-fight 160px drift check.
14. If enabled and HP < 30%, run final treatment.
15. Reach Kết thúc and return to the outer open-ended worker.

Discard is not step 16. It is a separate run-scoped background subsystem that can operate across many cycles.

## 4. Failure matrix

| Condition | Class | Recovered outcome |
| --- | --- | --- |
| Activity batch cancel | CONTROL STOP | Batch unwinds through cancel(batch-trừng-ác). |
| Row stop Event | CONTROL STOP | Current row worker unwinds. |
| Row generation changes | CONTROL STOP | Stale worker exits through gen(phiên-mới). |
| Window closes / PID changes | CONTROL STOP | Affected account becomes invalid. |
| Batch has no selected Trừng Ác rows | BATCH TERMINAL | No activity work starts. |
| Batch has no live rows | BATCH TERMINAL | Activity worker stops. |
| All selected rows have stopped | BATCH TERMINAL | Activity worker auto-stops. |
| Start heal fails | SKIP CURRENT CYCLE | Outer session remains alive and next cycle may retry. |
| Re-inject before NPC move fails | FAIL-SOFT | Direct movement is still attempted. |
| Move to bổ đầu fails / times out / ends on wrong map | SKIP CURRENT CYCLE | Avoid NPC clicks from wrong location; stop_character is used where recovered. |
| 30/30 daily-limit dialog confirmed and acknowledgement succeeds | TERMINAL CURRENT ACCOUNT | Stop Trừng Ác for that account. |
| 30/30 dialog missing/read error/ack failure | FAIL-OPEN | Treat as not-full and continue. |
| Trừng Ác Lệnh missing before target acquisition | TERMINAL CURRENT ACCOUNT | Account cannot progress and is stopped. |
| First-stage item use fails after two attempts | SKIP CURRENT CYCLE | Return to outer loop. |
| Target coordinates cannot be extracted | RECOVER NEXT CYCLE | Cancel current quest, then restart from next cycle. |
| Travel to target fails | SKIP CURRENT CYCLE | stop_character + target-failure tracking. |
| Same target repeatedly sticks beyond threshold | RECOVER NEXT CYCLE | Cancel quest/reset tracking; exact threshold remains UNKNOWN. |
| Trừng Ác Lệnh missing at summon stage | SKIP CURRENT CYCLE | Return to next outer cycle. |
| Summon use/dialog/button/click fails | SKIP CURRENT CYCLE | Return to next outer cycle. |
| start_auto_train fails | FAIL-SOFT | Combat time window still continues. |
| Character dies during combat | RECOVERABLE INTERRUPT | Combat ends early; death/Địa-phủ recovery takes over. |
| Post-fight drift exceeds 160px | DETECTED / EFFECT UNKNOWN | Exact log is proven; exact return effect remains UNKNOWN. |
| Final heal fails | FAIL-SOFT / LOG-ONLY | Cycle tail still completes. |
| Disconnect dual-pixel condition reaches 3/3 | RECOVERABLE INTERRUPT | halt + reconnect click (616,455). |
| Activity-wide reconnect succeeds within 60s | RECOVERED | Continue Trừng Ác. |
| Activity-wide reconnect times out | TERMINAL CURRENT RECOVERY PATH | Exact text says timeout -> dừng. |
| Single-worker reconnect succeeds | RECOVERED | Invalidate Reader cache, wait_memory_ready(45,3), then start a fresh outer cycle. |
| Single-worker common.active wait fails | UNKNOWN MICRO-ORDER | Exact unwind ordering is not independently bound. |
| Discard child fails on one account/item | FAIL-SOFT / ACCOUNT-LOCAL | Count/log; other account threads continue; later scan may see remaining item again. |
| Discard worker outer exception | EFFECT UNKNOWN | Error surface is proven; continue-vs-exit micro-order remains UNKNOWN. |

## 5. Death / Địa-phủ recovery is not a terminal stop

_diaphu_monitor runs every 4 seconds.

HP 0% -> click (792,441).
MapID 87 -> respawn_event.set().

K06 proves death may end combat early. At the next execution-cycle entry, respawn_event is cleared so the account can heal/move away from Địa phủ. This is a recoverable state transition, not an account-completion condition.

## 6. Disconnect recovery is Daily-specific

_punish_disconnect_monitor runs every 2 seconds.

Memory connected=True vetoes a false positive. Both exact disconnect pixels must match for 3 consecutive ticks, roughly 6 seconds. On 3/3 Daily signals halt and clicks (616,455).

Activity-wide recovery has an exact 60-second bounded wait:
- reconnect success -> continue;
- timeout -> dừng.

Single-row recovery has Chờ kết nối lại, common.active wait, Reader-cache invalidation, then wait_memory_ready(timeout=45, need=3). The exact single-worker common.active timeout numeric value is still not independently instruction-bound.

Do not import Train/TrainLSV five-attempt + infinite retry batches into Daily.

## 7. Discard runs beside the cycle

When the persisted discard option is armed and Trừng Ác accounts are active, the separate discard worker periodically gets only currently-running/non-disconnected Trừng Ác HWNDs.

It fans out one child thread per eligible account. Per-account inflight prevents overlapping passes. Shared bag_filter then serializes packet sends by HWND and paces actions at 1 second per account.

The preset is daily/discard_equip and intentionally includes non-weapon equipment plus weapons. Packet action is command 100005, action 4, payload 4:<dbID>, discarding the whole stack.

Do not place this logic at the end of each Trừng Ác cycle.

## 8. UI and stop handoff

Activity-wide Trừng Ác button:
- running: Dừng lại / FireBrick;
- stopping: Đang dừng... / disabled;
- idle/reset: Trừng ác / RoyalBlue / normal.

_punish_reset_ui owns the idle tuple.

Bottom Daily stop behaves differently: it sets each running row _farming_acc=False and row _stop_event, restores the bottom button to Bắt đầu/green, then workers unwind cooperatively. The singleton _daily_all_monitor waits until all row sessions have ended and then calls both activity reset helpers and logs the automatic UI reset.

_sync_start_tab_btns separately synchronizes StartTab controls.

The exact source-line ordering among clearing run flags, stopping child monitors, resetting the activity button, and StartTab synchronization remains UNKNOWN.

## 9. Callable coverage

Every top-level Trừng Ác handler in K01_HANDLER_INVENTORY.tsv is now accounted for:

- _punish_start_worker -> K03
- _punish_toggle -> K03
- _punish_run_worker -> K03/K07
- _punish_single_worker -> K03/K07
- _punish_running_hwnds -> K08
- _toggle_punish_discard -> K08
- _start_punish_discard -> K08
- _stop_punish_discard -> K08
- _punish_discard_worker -> K08
- _punish_discard_one -> K08
- _diaphu_monitor -> K07
- _punish_disconnect_monitor -> K07
- _punish_exec_sequence -> K04/K05/K06/K07
- _punish_cancel_quest -> K04
- _punish_check_full -> K04
- _punish_goto_target -> K05
- _punish_summon_target -> K05
- _punish_goto_bodau -> K04
- _punish_heal -> K07
- _punish_reset_ui -> K03/K09
- _wait_movement_stopped -> audited in K06, but its explicit recovered Daily call is in Tàng Bảo Đồ, not Trừng Ác.

_punish_target_fail is target-failure tracking state inside the goto-target path, not a top-level method. _punish_monitor_stops is a nested activity-wide recovery surface.

No unaccounted top-level Trừng Ác callable remains.

## 10. Cross-task contradiction audit

No blocking contradiction was found.

Two apparent conflicts are actually different layers:

1. Duration: UI construction seed is 15, while _load_config missing-key fallback is "5". Preserve both. Do not claim they are the same default layer.
2. Recovery checkboxes: B08 captures current/saved visible state, while config missing-key fallbacks are separate. Different values do not contradict each other.

Two scope differences must also remain explicit:

- Daily reconnect is not Train/TrainLSV reconnect.
- _wait_movement_stopped must not be inserted into Trừng Ác because its explicit recovered Daily call belongs to Tàng Bảo Đồ.

No K03–K08 artifact requires rewriting.

## 11. Static handoff status

From the Trừng Ác perspective, top-level static behavior coverage is complete enough for later Stage-S reconstruction.

This does not mean the whole project is ready for Stage S. Phase K still has Tàng Bảo Đồ, shared, and runtime-test work, and PLAN contains later phases before source reconstruction.

Runtime classification remains STATIC_VERIFIED / END_TO_END_RUNTIME_ENV_REQUIRED because the packaged automove log contains no correlated Trừng Ác lifecycle trace.

Next task: K10 — Tàng Bảo Đồ configuration / selection / top-level run-loop contract audit.