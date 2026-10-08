# L10 — Dồn reconstruction contract

## Gate purpose

L10 does not redo L01-L09. It consolidates their frozen findings into one implementation contract for the future Stage-S reconstruction.

Authority remains:

- original archive SHA-256: `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`
- inner EXE SHA-256: `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`
- active Dồn module: `donvang_tab.py / DonVangTab`
- direct receiver/transaction engine: `don_logic.py`
- L01-L09 evidence is normative unless a later exact contradiction is discovered.

## 1. Visible UI contract

Dedicated Dồn tab must preserve the current visible surface:

- Về thành condition:
  - Khi đầy túi
  - Theo chu kỳ (phút)
- four readonly priority selectors using:
  - blank
  - Phù 1
  - Phù 2
  - Phù 3
  - Ngựa
- Train options:
  - Quay lại train khi chết
  - Dừng khi mất kết nối mạng
  - Tự gỡ kẹt
  - Nhặt đồ không dùng hồ lô
  - Lọc đồ with exactly Tất cả / Chỉ vũ khí
  - Trị liệu sau khi chết
  - Tọa độ trị liệu
- saved-coordinate editor:
  - Tên / Map / X / Y
  - Train apply
  - delete
  - + Thêm tọa độ
- one shared **Tọa độ dồn** selector
- dynamic **Acc nhận N** rows with account selector + delete
- dynamic account list with role-dependent coordinate label:
  - donor -> Tọa độ train
  - receiver -> Tọa độ bán
- bottom **Điều khiển tất cả**:
  - Tới nơi nhận
  - Tới chỗ bán
  - Tới nơi train
- large bottom **Bắt đầu** lifecycle button.

Do not add visible Dừng tất cả / Farm tất cả / Bán tất cả buttons merely because legacy helpers remain in the class.

StartTab Dồn surface must remain:
- Dồn vàng
- Tới nơi nhận
- Tới chỗ bán
- Tới nơi train
- Cấu hình.

## 2. Persistence contract

Section: `[DonVang]`.

Frozen key families:

- return/priority:
  - town condition value family with internal values `cycle` and `full_bag_timer`
  - cycle minutes, default 30
  - `nav_priority_1..4`
- inventory:
  - `pickup_no_cankhon`
  - `pickup_mode`
- saved coordinates:
  - `coord_<n>=preset_name|map_id|x|y`
  - `acc_<character>_farm`
- receiver compatibility:
  - `recv_count`
  - `recv_<n>_acc`
  - `recv_<n>_coord`
  - legacy `receiver`
  - legacy `recv_coord`
- recovery:
  - `respawn`
  - legacy-named `auto_reconnect` whose current meaning is **stop on disconnect**
  - `trist`
  - `heal_map`.

Exact migration winner when legacy `recv_coord` conflicts with different `recv_<n>_coord` values remains EXPLICIT_UNKNOWN.

Unknown/stale map records must be skipped, not fuzzy-remapped.

## 3. Return trigger and movement contract

Two production return conditions:

### cycle
- internal value `cycle`
- default 30 minutes
- donor callback substitutes Dồn for the normal return-town leg.

### full bag
- internal value `full_bag_timer` / legacy `full_bag`
- occupied Site-10 slot count is authoritative
- hidden pickup OFF -> full threshold 100
- hidden pickup ON -> full threshold 98
- pre-Dồn filter runs before final return
- if filtering frees enough space -> remain at farm
- if still full -> continue Dồn.

Return shortcut:
- resolve current MapID first
- use map-specific `TRUYEN_DAI_LY_ROUTES` back path when present
- invalidate Reader cache
- verify exit fresh
- if shortcut fails and stop was not requested -> walk fallback
- final Dồn/receiver leg is normal horse movement, explicitly no Phù.

Standard sell movement is different:
- may use back shortcut
- then `move_character(home_priority=_get_nav_priority())`
- one explicit normal-move retry.

## 4. Navigation priority contract

Exact options:
`["", "Phù 1", "Phù 2", "Phù 3", "Ngựa"]`.

Default:
`Phù 1 -> Phù 2 -> Phù 3 -> Ngựa`.

Normal readonly UI prevents selecting a new duplicate nonblank priority by recomputing each slot's available options.

Only the sell movement path consumes `home_priority`.
Do not apply this priority chain to:
- Dồn/receiver final leg
- Truyền back executor
- ordinary Train-target movement.

## 5. Inventory / pre-Dồn filter contract

Bag count = occupied Site-10 slots.

Read failure = `None`, never synthesize zero.

Dồn filter modes are exactly:

- `Tất cả` -> no discard preset
- `Chỉ vũ khí` -> `discard_nonweapon`.

There is no Dồn `Không` mode and Dồn does not select `discard_weapons`.

Hidden pickup:
- independent from filter mode
- after exact 5-second helper delay, write `PICKITEM.IsOn=True`
- no recurring 5-second loop recovered
- no old manual-click pickup sequence.

Pre-Dồn discard:
- `bag_filter.discard_for_activity(activity="train")`
- default delay 1.0s
- OR-combined rules
- dbID dedupe
- action 4 / opcode 100005 / payload `4:<dbID>`
- cooperative stop.

The nested `stop_bag_check` default value 3 is real but its exact semantic must remain UNKNOWN.

## 6. Coordinate contract

Saved preset identity is its display name.

Rename:
- refresh account selector values
- rewrite active old-name selections to the new name.

Resolver accepts:
- built-in sell names
- built-in Dồn/receive names
- manual saved preset names
and returns `(map_id,x,y)` or `None`.

Exact Dồn built-ins:

| Name | MapID | X | Y |
|---|---:|---:|---:|
| Dồn Lạc Dương | 3 | 247 | 93 |
| Dồn Đại Lý | 2 | 258 | 124 |
| Dồn Tô Châu | 4 | 416 | 239 |
| Dồn Lâu Lan | 5 | 249 | 275 |

Exact sell built-ins:

| Name | MapID | X | Y |
|---|---:|---:|---:|
| Đại Lý | 2 | 103 | 188 |
| Lạc Dương | 3 | 231 | 219 |
| Tô Châu | 4 | 191 | 257 |
| Lâu Lan | 5 | 37 | 126 |

Current runtime owns exactly one shared `_recv_coord_var`.
Every receiver row aliases that variable.
Do not reconstruct one independent receive coordinate per receiver.

Current account coordinate selector is one role-switched surface:
- donor -> manual Train preset choices
- receiver -> sell built-ins + manual presets.

Saved-row Train apply propagates the preset **name** to Train selectors; it does not freeze copied coordinates.

## 7. Receiver architecture contract

Receiver rows:
- dynamic account selector + delete
- at least one row retained
- duplicate character names disambiguated by HWND in display label
- same account may appear in multiple rows at UI level; runtime receiver membership collapses through HWND set semantics.

Authoritative state lives in `don_logic._recv_registry` per receiver:
- ready Event
- donated Event
- aborted Event
- donor_hwnd.

Receiver FSM:
`sell -> return to receive point -> ready -> wait donated/abort/dead donor -> repeat`.

Selection:
- only selected receiver HWNDs
- exclude donor itself
- require ready
- require valid coordinate
- choose minimum current donated-gold/hour
- random choice among equal minima.

After receiver lock acquisition:
- recheck readiness
- skip stale/non-ready candidate.

Locks:
- one lock per receiver
- same receiver serialized to one donor
- different receivers may serve donors in parallel
- no one global Dồn lock.

Automatic no-ready/all-busy:
- skip Dồn cycle
- continue farm.

Manual **Tới nơi nhận** may use first-valid-receiver fallback when no ready receiver can be selected.
Do not import that manual fallback into automatic Dồn.

Trade watcher:
- one background watcher per receiver
- whitelist = all managed account names
- known inviter accept
- unknown inviter cancel
- unreadable/non-invite ignore
- watcher yields while a real donor claim owns the receiver.

## 8. Full-session lifecycle contract

Shared ownership:
- `_farming`
- `_farming_acc`
- `_farm_threads`
- `_stopping_play`
- row `_gen`.

Role is selected when the session starts:

- receiver -> `_run_receiver -> recv_cycle`
- donor -> `_farm_cycle(don_callback=_don_cb)`.

`_farm_acc` is only the internal StartAutoFight Train primitive and must not replace the full lifecycle.

Receiver selection changes while running:
- restyle/reorder only
- no hot worker migration
- newly selected role takes full-worker effect only after stop/start.

Stop:
- cooperative
- no force thread kill
- generation guards stale workers
- partial stop leaves other accounts running
- final account stop drains and resets the global control.

State writes must marshal to Tk main thread rather than mutate widgets directly from workers.

## 9. State table contract

Exact state/color map:

| State | Color |
|---|---|
| Đã dừng | #555555 |
| Sẵn sàng nhận | #2e7d32 |
| Chuẩn bị nhận | #1565c0 |
| Đang nhận | #1565c0 |
| Chờ giao | #2e7d32 |
| Chờ dồn | #2e7d32 |
| Về dồn | #1565c0 |
| Đang dồn | #1565c0 |
| Về địa phủ | #c62828 |
| Bán đồ | #555555 |
| Tới nơi nhận | #555555 |
| Trị liệu | #555555 |
| Đi train | #555555 |
| Đang train | #555555 |
| Đang lọc đồ | #8e24aa |
| Gỡ kẹt | #ef6c00 |

Default/unknown -> `#555555`.

Receiver transaction:
- start -> Đang nhận
- done -> Sẵn sàng nhận only if current state is still Đang nhận.

Donor:
- Về dồn
- Đang dồn
- on Dồn failure after receive point -> return toward Train.

Global full-start donor path additionally exposes:
- Chờ dồn at shared Dồn point before ready selection.

## 10. Death / treatment contract

Both roles run the Dồn death monitor.

Cadence: 4 seconds.

Map signal:
- MapID 87 -> set `respawn_event` once per continuous map-87 episode
- rearm after leaving map 87.

HP signal:
- real numeric `HpPercent == 0`
- one client click at `(792,441)`
- latch until HP becomes nonzero
- unreadable HP is not zero.

Receiver recovery stays receiver-role.
Do not redirect receiver to Train target.

Optional treatment:
- built-in or manual saved coordinate
- move with shared movement engine
- then click `(892,474)`
- click `(514,424)`
- repeat pair ×4.

Treatment built-ins:

| Name | MapID | X | Y |
|---|---:|---:|---:|
| Trị liệu Đại Lý | 2 | 43 | 178 |
| Trị liệu Lạc Dương | 3 | 255 | 126 |
| Trị liệu Tô Châu | 4 | 155 | 252 |
| Trị liệu Lâu Lan | 5 | 294 | 170 |

`Quay lại train khi chết` is post-death relocation policy.
It does not gate the HP0 respawn click.

## 11. Disconnect contract

Critical current semantics:

`auto_reconnect_var / [DonVang] auto_reconnect`
is a legacy name for the visible control:
**Dừng khi mất kết nối mạng**.

Dồn does not auto reconnect.

Watchdog:
- cadence 2s
- `Connected == True` vetoes/reset false-positive chain
- otherwise both pixels required:
  - (640,244), RGB (160,145,52), tolerance 5
  - (702,453), RGB (212,28,34), tolerance 5
- require 3 consecutive matching ticks, approximately 6s
- then set halt / stop account.

Receiver result:
- stop receiver session.

Donor result:
- stop donor session.

User must press Start again.

Do not implement:
- reconnect_ok
- click (616,455)
- common.active reconnect wait
- five-attempt batch
- 30-second reconnect retry
- infinite reconnect loop.

## 12. All-account action contract

Current dedicated-tab quick controls:

- Tới nơi nhận -> `_move_all_recv`
- Tới chỗ bán -> `_move_sell_acc`
- Tới nơi train -> `_move_all`.

These are asynchronous standalone movement commands.

Current ordinary bulk helper universe:
all listed accounts excluding receiver accounts.

`_move_all`:
- nonreceiver/donor only
- configured Train target
- parallel.

`_move_sell_acc`:
- receiver only
- each receiver's selected sell target
- movement only, no item selling.

`_move_all_recv`:
- donor -> manual current receiver choice/fallback
- receiver -> current shared Dồn point via its receiver-row alias.

Legacy methods remain:
- `_stop_all`
- `_farm_all`
- `_sell_all`.

They are real but no current visible Dồn/StartTab binding was recovered.
Do not expose them as new UI controls.

Large **Bắt đầu**:
- authoritative lifecycle = `_toggle_farm`
- not `_farm_all`.

## 13. StartTab parity contract

StartTab must delegate to Dồn rather than duplicate logic:

- Dồn vàng -> `_toggle_farm`
- Tới nơi nhận -> `_move_all_recv`
- Tới chỗ bán -> `_move_sell_acc`
- Tới nơi train -> `_move_all`
- Cấu hình -> navigate to Dồn tab.

StartTab and Dồn-tab run-state text/state must stay synchronized.

## 14. Explicit UNKNOWN / runtime-required edges

These must not be silently guessed during Stage S:

- exact polling micro-order for 30-minute cycle trigger
- exact semantic of `stop_bag_check` default 3
- live discard-memory propagation timing
- legacy duplicated nav-priority migration behavior
- exact fresh saved-coordinate defaults independent of captured config
- conflicting legacy/per-row receiver-coordinate migration winner
- stable candidate order before random equal-speed choice
- exact `_gen` mutation statement/order
- exact assignment site for every intermediate receiver UI state
- exact worker join timeout/drain timing
- donor continuation when Quay lại train khi chết is unchecked
- treatment-failure next branch
- first death-monitor tick timing
- exact `is_trade_active` branch in disconnect monitor
- same-window death/disconnect ordering
- exact quick-move internal join/order
- quick-move overlap/cancellation versus Farm start/stop
- live StartTab synchronization timing
- captured permission state that made Dồn tab visible.

These become runtime parity fixtures, not design choices.

## 15. Negative reconstruction requirements

A parity implementation must **not**:

- add Dồn `Không` filter mode
- add `discard_weapons` to Dồn keep policy
- add independent receive coordinate per receiver
- use one global receiver lock
- auto-reconnect Dồn
- hot-switch an already-running donor/receiver worker when the receiver combobox changes
- apply sell-home Phù priority to the final Dồn/receiver leg
- use `_farm_all` as the big Bắt đầu lifecycle
- make Tới chỗ bán actually sell inventory
- expose visible legacy Dừng/Farm/Bán-all buttons
- use manual receiver fallback in automatic no-ready Dồn
- fuzzy-remap stale/unknown coordinate maps
- mutate Tk state widgets directly from worker threads.

## 16. Phase-L gate

L01-L09 contain enough static evidence to freeze the Dồn reconstruction contract.

No app source is written in Phase L.

Phase-L result:

**STATIC_RESEARCH_CLOSED / LIVE_RUNTIME_PARITY_DEFERRED**

Live parity is deferred until a Stage-S reconstructed implementation and Windows + Thần Long runtime are available.
