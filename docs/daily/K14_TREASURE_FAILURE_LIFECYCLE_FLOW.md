# K14 — Tàng Bảo Đồ skipped-account / stop-reset / failure lifecycle flow

## 1. Scope

K14 does not reopen K10-K13 internals. It audits how Treasure accounts are excluded/stopped/recovered, how the batch decides no work remains, and how the Daily UI resets after the workers actually unwind.

## 2. Treasure lifecycle state owned by DailyTab

Exact activity fields:
- `_treasure_map_running`;
- `_treasure_map_cancel`;
- `_treasure_map_btn`;
- `_treasure_map_skipped`.

The skipped-account set is distinct from the batch cancel Event and from each row's `_stop_event` / `_gen` session guard.

## 3. Terminal item-not-found versus ordinary skip

K11 proved two exact terminal messages:

`tuido.tangBaoDo_multi not found → dừng tàng bảo đồ cho acc này`

and

`tuido.tangBaoDo_multi not found (lần 2) → dừng tàng bảo đồ cho acc này`.

These are terminal for that Treasure account's current activity session.

By contrast:
- start-heal failure says `skip vòng này` and remains current-cycle only;
- `MapID != 96 — không phải huyệt mộ, bỏ qua` skips only the tomb outcome;
- final-heal failure is log-only at cycle tail.

Do not merge all uses of the word bỏ qua/skip into the same terminal class.

## 4. `_treasure_map_skipped` evidence boundary

`_treasure_map_skipped` is an exact DailyTab-owned state field.

The Treasure activation call to `_wait_movement_stopped` explicitly passes a keyword named `skip_set`.

The activity-wide worker owns:
- `selected`;
- `selected_pids`;
- `alive`;
- `still_active`.

Taken together with the two terminal account-stop branches, this is strong static evidence that terminally skipped Treasure HWNDs are kept out of later `still_active` work during the active batch.

The exact native source statements such as:
`self._treasure_map_skipped.add(hwnd)`

or the exact place where the set is cleared cannot be line-by-line recovered from the current Nuitka evidence.

K14 therefore preserves the lifecycle role but keeps add/discard/clear micro-order explicit UNKNOWN.

## 5. Activity-batch end conditions

Exact worker messages:
- no selected Treasure row → `Chưa acc nào chọn Tàng bảo đồ — bỏ qua`;
- no selected account still alive → `Không còn acc nào sống — dừng`;
- all selected accounts have ended/excluded work → `Tất cả <n> acc đã dừng — tự động dừng`.

`[TÀNG BẢO ĐỒ] Lần ...` and the `loop_idx` local keep the batch open-ended while eligible accounts remain.

Thus one terminally skipped account does not itself end a multi-account Treasure batch if other `still_active` accounts remain.

## 6. Exact stop-reason classes

The shared `_stop_reason` diagnostic exposes these exact strings:
- `cancel(batch-tàng-bảo-đồ)`;
- `halt(mất-kết-nối)`;
- `stop_event(dừng)`;
- `gen(phiên-mới)`;
- `window-chết/đổi-process`;
- `respawn(địa-phủ)`;
- `không-stop(?)`.

These reasons are not semantically identical.

### Activity user cancel

`_treasure_map_cancel` is the activity-wide batch cancel Event.

Classification:
`CONTROL_STOP / BATCH`.

### Row stop

K02's bottom/per-row contract uses the real row `_stop_event`.

Classification:
`CONTROL_STOP / ROW`.

### Generation change

`_GenStop` also reports set when the worker's generation snapshot no longer equals row `_gen`.

This is the protection against an old worker surviving a rapid Stop → Start.

Classification:
`CONTROL_STOP / STALE_WORKER`.

### Window/PID death

K02 binds HWND with PID and rejects a closed/reused process.

Classification:
`CONTROL_STOP / INVALID_WINDOW_IDENTITY`.

### Disconnect halt

`halt(mất-kết-nối)` is a recovery-interrupt reason, not ordinary user stop.

Successful reconnect can continue; reconnect timeout can terminate the affected recovery/account path.

### Respawn

`respawn(địa-phủ)` is also a recovery-interrupt reason. K13 proved Map87/death is recoverable through `respawn_event` and next-cycle clear.

## 7. Treasure failure/lifecycle matrix

| Condition | Class | Account remains eligible? | Outcome |
| --- | --- | --- | --- |
| No rows selected at activity start | BATCH NO-OP | n/a | Worker does no Treasure work |
| No selected row remains live | BATCH TERMINAL | No batch work remains | Activity ends |
| All selected rows stopped/skipped | BATCH TERMINAL | No batch work remains | Auto-stop |
| First treasure item not found | TERMINAL CURRENT TREASURE ACCOUNT | No, for current activity session | Exclude this account |
| Second treasure item not found | TERMINAL CURRENT TREASURE ACCOUNT | No, for current activity session | Exclude this account |
| Start heal fails | SKIP CURRENT CYCLE | Yes | Next Treasure cycle may run |
| Post-wait MapID != 96 | SKIP TOMB OUTCOME | Yes | Final-heal/cycle-tail path |
| Final heal fails | FAIL-SOFT / LOG-ONLY | Yes | Finish cycle tail |
| Disconnect recovered | RECOVERABLE INTERRUPT | Yes | Continue Treasure |
| Disconnect recovery timeout | TERMINAL AFFECTED RECOVERY PATH | No for that path | Stop affected activity/account path |
| Death / Map87 | RECOVERABLE INTERRUPT | Yes | respawn_event → next cycle recovery |
| User cancels activity batch | CONTROL STOP | No for current batch | Cancel batch |
| Row stop Event | CONTROL STOP | No for current row session | Worker unwinds |
| Generation changes | CONTROL STOP | Old worker no | Stale worker exits |
| Window/PID invalid | CONTROL STOP | No | Worker exits |

## 8. Bottom all-account stop

Exact shared Daily documentation:

while running:
- set each running row `_farming_acc=False`;
- signal each row `_stop_event`.

The bottom control immediately returns toward its idle visual:
- `▶`;
- `Bắt đầu`;
- green `#388e3c`.

The actual per-row workers then unwind cooperatively through their normal stop checks.

## 9. Singleton Daily monitor and final reset

`_daily_all_monitor` is explicitly singleton.

Its exact documentation:
`Monitor: chờ tất cả acc dừng, rồi reset UI.`

It owns both reset calls:
- `_punish_reset_ui`;
- `_treasure_map_reset_ui`.

Exact completion log:
`[Bắt đầu] Tất cả acc đã dừng — tự động reset UI`.

So visual reset is not evidence that a worker was force-killed; the monitor waits for row sessions to end.

## 10. Treasure activity button reset

Exact Treasure idle tuple:
- text `Tàng bảo đồ`;
- background `RoyalBlue`;
- state `normal`.

Shared active/stopping surfaces are:
- running: `Dừng lại / FireBrick`;
- stopping: `Đang dừng... / disabled`.

`_sync_start_tab_btns` separately synchronizes the external StartTab Treasure button.

The exact source-line order among cancel Event, running flag, monitor shutdown, child completion, reset helper and StartTab sync is still UNKNOWN.

## 11. Runtime/B08 boundary

After static extraction the packaged `automove_log.txt` was checked again.

There are zero correlated records for:
- Treasure activity lifecycle;
- either terminal treasure-map not-found;
- non96 Treasure skip;
- all-selected-stopped;
- `cancel(batch-tàng-bảo-đồ)`;
- `respawn(địa-phủ)`;
- Treasure reconnect timeout;
- global Daily auto-reset.

B08 shows only idle Daily/Treasure configuration and cannot prove worker teardown or skipped-account behavior.

K14 therefore remains:
`STATIC_VERIFIED / END_TO_END_RUNTIME_ENV_REQUIRED`.

## 12. K14 boundary

K14 freezes the failure/lifecycle classes but deliberately does not perform the final integrated Treasure handoff.

That final cross-check belongs to K15.

Next: K15 — Tàng Bảo Đồ integrated lifecycle / failure matrix / static handoff audit.