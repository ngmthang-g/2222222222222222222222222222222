# I12 — Train LSV Runtime Parity Report

## Executive result

Gate I result:

**CLOSED_FOR_STATIC_VISUAL_RESEARCH_HANDOFF / END_TO_END_RUNTIME_PARITY_DEFERRED**

The frozen Train LSV module has been researched deeply enough for downstream reconstruction handoff without inventing missing behavior.

End-to-end parity is still intentionally deferred to a Windows + live-game environment.

## Evidence set

Authoritative frozen inputs:
- original archive SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`
- inner EXE SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`
- TrainLSV Nuitka constant chunk at `0x2c07798`
- B06 screenshot SHA-256 `9e3b57671a2ff165ea31264a1c2fb19493f861a7bdadc4dc993a55bd130f5d29`
- packaged runtime helper log SHA-256 `17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`.

All 44 I01-I11 artifacts were re-inspected before final classification.

## Matrix summary

The final matrix contains **80 rows**:

| Classification | Count | Meaning |
|---|---:|---|
| STATIC_VERIFIED | 24 | Frozen EXE/config/UI evidence is sufficient to lock the contract without live execution. |
| RUNTIME_VERIFIED_FROM_EXISTING_EVIDENCE | 3 | Packaged real-session log directly records the low-level primitive. |
| RUNTIME_ENV_REQUIRED | 53 | Exact behavior needs Windows/live-game execution or stronger native instrumentation. |
| BLOCKED | 0 | No unresolved static blocker prevents Phase-J research or future reconstruction handoff. |

## Existing runtime evidence that is safe to reuse

The packaged helper log directly proves execution of shared primitives:

- movement:
  - AutoMove queued: 16,040
  - StartAutoPath called: 15,993
  - StopAutoPath called: 2,027
- fight:
  - AutoFight_Main: 8,511
- discard:
  - ItemAction spts sent action=4: 22,732
  - raw action=4: 22,734.

These are primitive-level facts only.

They do not prove that a specific TrainLSV UI button, account row, Farm generation or recovery branch caused the recorded primitive.

## I01 — Module/UI/config

Static contract is closed:
- dedicated `TrainLsvTab`
- [TrainLSV] config section
- 5-second incremental account refresh
- 30-second config autosave
- dynamic saved coordinates
- fixed Dạ Minh Châu schedule row
- four bulk controls
- StartTab forwarding/mirroring.

B06 remains visually consistent with these frozen contracts.

No live runtime behavior is claimed from B06 alone.

## I02 — LSV entry/navigation

Static contract is closed for:
- normal Lạc Dương MapID 3 gate route
- exact entry clicks
- LSV hub MapID 10000
- recognized LSV map set
- exact floor order/waypoints
- flat-map waypoints
- portal click data
- common.active readiness helper.

Live tests remain required for:
- real map transition success
- exact click pacing
- PK-warning timing
- wait_pixel interval/debug
- portal/stuck behavior under actual game latency.

## I03 — Final train point

Static contract is closed for:
- saved-preset resolution
- I02 premove then direct final move
- tile X/Y x32 conversion
- `wait_for_arrival=True`
- caller stop_check
- no LSV-specific 8-tile pre-skip
- no extra common.active/MapID post-check.

Live tests remain required for:
- actual shared arrival timeout
- cancellation timing
- nonfatal timeout continuation.

## I04 — Leave LSV

Static contract is closed for:
- only MapID 10000 proceeds
- floor/flat maps skip
- gate tile 236,190
- clicks 887,475 then 478,427
- no direct stop_check
- no explicit post-exit MapID/common.active verification.

Runtime is required to bind:
- explicit wait_for_arrival boolean value
- exact click pacing
- actual destination after sequence.

## I05 — Dạ Minh Châu / timed keys

Static contract is closed for:
- fixed always-active row
- key1 / 0m5s clean defaults
- dynamic row defaults and key list
- exact dismount decision/click points
- one-shot `press_single_key_dll(... delay=0,sync=True)`
- hidden HWND/DLL sync transport
- one schedule worker per farming account
- generation guard
- `buff_<n>=enabled|key|minutes|seconds`.

Runtime remains required for:
- multi-row deadline order
- zero/invalid interval policy
- repeating-call kwargs
- worker join/daemon timing
- fixed-row migration/index details.

## I06 — Keep/discard

Static contract is closed for:
- Nhặt đồ = keep/discard policy, not auto-pick enable
- exact modes/mappings/default
- occupied Site-10 slot metric
- 10-second polling
- temporary purple `Đang lọc đồ`
- shared `discard_for_activity`
- absence of TrainLSV PICKITEM enable.

Existing runtime log directly proves action-4 item primitive execution.

Runtime remains required for:
- exact numeric FULL_BAG_THRESHOLD
- top-level TrainLSV trigger
- cancellation/state-restoration timing.

## I07 — Treatment

Static contract is closed for:
- `trist=False`
- fixed MapID10000 tile163,237
- legacy heal_map ignored
- 50% HP gate
- unreadable HP still heals
- exact treatment points and x4 behavior
- no post-heal HP verification/common.active gate.

Runtime remains required for:
- effective click pacing
- exact x4 call shape
- cancellation checkpoints
- movement/click sequencing under game latency.

## I08 — Reconnect

Static contract is closed for:
- opt-in default false
- 2-second watchdog
- TCPGame memory veto
- exact two disconnect pixels with tolerance 5
- 3 consecutive strikes
- click616,455
- 5 attempts per batch
- 30-second common.active window
- 30-second failed-batch delay
- infinite retry while session valid
- cache invalidation
- reconnect_ok cycle reset
- exact 5-second Event wait
- memory-ready 45s / 3 reads / 1s sample / fail-open.

Runtime remains required for:
- real false-positive rejection
- live batch timing
- exact wait_pixel args
- whether any post-reconnect reinjection occurs.

## I09 — Death/recovery

Static contract is closed for:
- `respawn=False`
- 4-second monitor from Farm start
- real HP0 one-shot respawn click792,441
- death counter ownership
- MapID10000 recovery event
- detected/hp latches
- common.active recovery wait
- `Về Lạc Dương LSV` state
- reuse of I07 treatment and I02/I03 return target.

Runtime remains required for:
- latch reset points
- death active-wait timeout
- exact `respawn=False` continuation
- treatment/return ordering
- death/reconnect race.

## I10 — Coordinate persistence

Static contract is closed for:
- Train-only coordinate rows
- [TrainLSV] `coord_*`
- `preset_name|map_id|x|y`
- map-name <-> MapID normalization
- stale-map skip
- name-based identity
- rename propagation
- `acc_<character>_train`
- tile-unit persistence.

Runtime remains required for:
- first coord index
- duplicate-name winner
- selected-preset deletion behavior
- exact edit-save debounce/scheduler.

## I11 — Bulk commands/FSM

Static contract is closed for:
- `_checked_rows` = all account rows
- four visible bulk commands
- outer daemon UI dispatch
- per-account parallel workers
- manual bulk Fight separated from full Farm FSM
- manual Fight skip when full Farm active
- `_farming_acc/_farm_threads/_gen`
- row states ▶ / II / …
- global START inactive-only / STOP active-only
- cooperative stop/drain
- partial/full stop behavior
- no-window cleanup special state
- StartTab mirror
- full cycle excludes ordinary Train sell/buy/town logic.

Runtime remains required for:
- inner child thread lifecycle
- exact join timeout/order
- global permission wrapper
- bulk move/leave conflicts during Farm
- rapid generation race
- ordinary user-stop transient UI
- aggregate failure behavior.

## Runtime test plan

The 53-scenario Windows/live-game plan is the authority for future parity completion.

A test is not PASS merely because static evidence predicts its result.

Each scenario must be marked:
- `PASS_ORIGINAL_CONTRACT`
- `FAIL_CONTRADICTS_STATIC_CONTRACT`
- `UNVERIFIED_ENV_NOT_AVAILABLE`.

Any contradiction must update the narrow contract that failed and preserve unrelated locked evidence.

## Gate conclusion

There are **0 static blockers**.

Phase I can therefore hand off to later reconstruction and move research attention to Phase J.

End-to-end runtime parity remains deferred and must be completed before the rebuilt product can claim full Train LSV functional parity.
