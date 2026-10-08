# L07 — Dồn train-state / receiver-donor lifecycle integration flow

## Frozen authority first

L07 was performed against the exact frozen specimen before using screenshot/runtime evidence:

- archive `TLMTool_2.1.2(8).zip` SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`
- archive size **93,715,901 bytes**
- ZIP entries **1,050**
- CRC clean
- inner `TLMTool.dist/TLMTool.exe` SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`
- inner EXE size **47,450,112 bytes**
- active Dồn authority `donvang_tab.py / DonVangTab`
- receiver transaction engine `don_logic.py`

L01-L06 contracts remain unchanged.

## Session ownership

Dồn uses one shared full-session ownership model for both account roles:

- `_farming` = global large-button/running projection;
- `_farming_acc` = authoritative per-account full-session membership;
- `_farm_threads` = full-session worker collection;
- `_stopping_play` = account requested to stop but old worker not fully drained yet;
- `row["_gen"]` = generation barrier against stale worker/monitor callbacks.

The receiver registry from L06 is additional transaction state. It does not replace `_farming_acc`.

This distinction matters: an account can be in a Dồn full session while its internal worker is either the receiver engine or the donor Train engine.

## Start-time role split

The full-session decision happens when the session is started.

`_toggle_single_farm(hwnd)`
contains both role surfaces:

```text
receiver role
  -> _run_receiver
  -> don_logic.recv_cycle

normal/donor role
  -> _farm_cycle(..., don_callback=_don_cb)
  -> _don_cb uses don_logic.don_move_and_execute
```

The global `_toggle_farm` has the same two role-specific engine families.

Therefore receiver vs donor is not a different play button or separate top-level Farm membership. It is a branch choosing the worker that the account will run for that session.

## _farm_acc is not the Farm FSM

`_farm_acc` is only the internal fight primitive:

```text
start_auto_train(hwnd)
-> StartAutoFight Train through memory
-> no game-UI click
```

It accepts `stop_check` for the full Farm cycle but does not own:

- `_farming_acc`;
- receiver selection;
- receiver registry;
- generation;
- full start/stop;
- sell/return sequencing.

Do not reconstruct the Dồn play button as a direct call to `_farm_acc`.

## Receiver start path

When the account is selected as receiver at session start:

1. the account joins the shared full-session membership;
2. receiver donated-gold/time tracking is started by `_start_extra_track`;
3. receiver-specific row3 tracking is visible;
4. session `gen_snap` is captured;
5. receiver death/respawn and disconnect/halt guards are started;
6. `_run_receiver` enters `don_logic.recv_cycle`.

The receiver engine is:

```text
sell receiver inventory
   ↓
move back to receive/Dồn point
   ↓
mark receiver ready
   ↓
wait for donor claim / donated / abort / donor death
   ↓
sell again
   ↓
repeat
```

If movement back to the receive point fails, `recv_cycle` does not set ready and retries in a later cycle.

## Receiver state projection

The exact Dồn state table contains:

```text
Đã dừng
Sẵn sàng nhận
Chuẩn bị nhận
Đang nhận
Chờ giao
Chờ dồn
Về dồn
Đang dồn
Về địa phủ
Bán đồ
Tới nơi nhận
Trị liệu
Đi train
Đang train
Đang lọc đồ
Gỡ kẹt
```

Exact state colors:

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

Unknown states fall back to `#555555`.

Receiver flow order fixes the semantic projection:

```text
Bán đồ
→ Tới nơi nhận
→ Sẵn sàng nhận
→ donor claim: Chuẩn bị nhận
→ transaction start: Đang nhận
→ transaction done: Sẵn sàng nhận
→ next receiver sell cycle
```

The transaction pair is exact:

- `_on_recv_phase(receiver, "start")` → **Đang nhận**
- `_on_recv_phase(receiver, "done")` → **Sẵn sàng nhận**, but only if the row still says **Đang nhận**

The sell→move→ready engine order is exact from `recv_cycle`. The exact source instruction that assigns every first-cycle intermediate GUI label is not fully recovered, so that micro-order remains an explicit implementation checkpoint rather than being invented.

## Donor start path

A normal account starts:

`_farm_cycle(row, don_callback=_don_cb)`.

The frozen `_farm_cycle` documentation says:

> Per-account Farm loop: sell/medicine/move/farm → wait cycle. For a donor, don_callback replaces the return-town step with Dồn.

So Dồn does not replace the whole Train cycle. It replaces the return/sell leg at the configured trigger.

Normal training work still owns:
- move toward Train target;
- internal auto-fight;
- full-bag/cycle waiting;
- L04 filtering;
- return to Train after the Dồn callback.

## Donor Dồn states

The per-row donor callback has exact state constants:

```text
Về dồn
Đang dồn
```

It also contains:

```text
Dồn fail sau khi về điểm nhận — đưa acc giao về farm
Đi train
```

Therefore a failed donor transaction is not left parked permanently at the receiver point. It is returned toward the normal Train leg.

The current global **Bắt đầu** path has an additional explicit pre-stage surface:

```text
_don_point_coords
→ donor reaches shared Dồn point
→ don_mark_waiting
→ Chờ dồn
→ _any_ready_receiver
→ don_move_and_execute
```

The single-account start path instead exposes direct ready-pick/move callbacks around `don_move_and_execute` with **Về dồn / Đang dồn**.

This single-vs-global static distinction is preserved for parity. Do not “simplify” the two callback paths into one guessed behavior before runtime parity.

## No-ready / failed Dồn

Already-frozen L06 receiver selection stays authoritative.

If no receiver is valid/ready:
→ Dồn for that cycle is skipped;
→ normal Farm loop continues.

If Dồn fails after movement:
→ donor is directed back toward Train.

If a receiver becomes busy between candidate listing and locking:
→ L06 post-lock readiness logic rejects that candidate.

These failures do not tear down the full donor session unless a separate stop/halt condition is raised.

## Cooperative stop

Dồn does not force-kill its session threads.

`_stop_acc` has the exact semantic:

> Dừng nhân vật + tắt flag farm cá nhân.

Full-session subflows also use:

- `_check_stop`;
- `_is_acc_farming`;
- stop events;
- generation checks;
- HWND/PID ownership;
- receiver registry abort/reset;
- halt/hard_stop for their relevant monitor paths.

Once a row is requested to stop, `_stopping_play` blocks normal play-button refresh/restart until the old worker exits.

`_wait_farm_stop` calls `join` on requested Farm workers.

If other accounts remain:
→ cleanup only stopped account workers;
→ global Dồn Farm remains running.

If no account remains:
→ wait for drain;
→ reset large button to **Bắt đầu**;
→ StartTab stopped projection remains **Dồn vàng**.

The exact join timeout/drain timing remains unknown.

## Generation barrier

Each running session captures `gen_snap`.

Frozen worker documentation says old workers exit when:
- account no longer Farm;
- generation changes after user stop/start.

`_restore_play_button` has an additional exact guard:

> restore the ▶ button only if generation still matches, so an old worker cannot overwrite a new run that the user already started.

Inactive play projection is role-sensitive:
- receiver → **▶** with gold/brown `#B48608`;
- normal donor → **▶** with green `#388e3c`;
- active → **II** with red `#f44336`.

The exact statement that increments/assigns `_gen`, and its exact ordering versus membership/thread insertion/removal, is still not source-visible enough to freeze.

## Role changes while a session is already running

This is a critical parity detail.

`_on_receiver_selected` has exact compiled documentation:

> Changing receiver account updates style + moves the receiver row to the top. GUI buttons remain the same for every account; only color/reorder changes.

No stop/restart or worker replacement surface is present in that handler.

Meanwhile the full worker was already chosen at start:

- receiver session → `recv_cycle`;
- donor session → `_farm_cycle(don_callback=...)`.

Therefore changing the combobox selection does **not** dynamically morph the current worker.

### Receiver removed while its receiver worker is alive

The existing `recv_cycle` is not replaced by a donor Farm cycle.

Its receiver callback contains an explicit failure:

`[Nhận đồ] hwnd=... không nằm trong danh sách acc nhận`

So removing receiver role mid-run can make a subsequent receiver callback fail/retry. It does not silently turn that session into a donor.

### Running donor selected as receiver

Selecting an already-running donor as a receiver changes role presentation/current receiver mapping, but it does not create a new `recv_cycle` or register that donor as ready.

Its current donor Farm worker remains the worker created for that generation.

The safe parity interpretation is:

```text
role change in UI
→ presentation / candidate mapping changes
→ current full worker remains
→ stop + start creates a worker for the newly selected role
```

L07 does not invent automatic hot role migration.

## State ownership / threading

Canonical state:
→ `row["_state"]`.

`_state_of(hwnd)`
→ current state string or `None`.

All worker/monitor state changes must be marshaled:

```text
_set_state
→ _schedule_state_label
→ Tk after(0)
→ _apply_state_label
```

The compiled documentation explicitly warns that direct Tk widget mutation from worker threads can terminate the process silently.

## Receiver tracker ownership

`_start_extra_track` is explicitly receiver-oriented:

> start tracking when receiver is started; elapsed time + BoundMoney baseline, with baseline taken on first normal refresh rather than main-thread memory read.

Receiver row3 shows:
- elapsed time;
- donated gold;
- average donated gold/hour.

A normal donor row keeps row3 hidden.

This tracker feeds L06's lowest-gold/hour receiver selection policy.

## Disconnect/death boundary for L08

L07 only freezes lifecycle ownership:

- receiver runner contains death/respawn and disconnect monitor surfaces;
- donor Farm cycle also owns its session monitors;
- `halt` / `hard_stop` can terminate current subflows;
- generation/membership/window checks cancel stale work.

The exact death healing, checkbox semantics, and disconnect/reconnect behavior are intentionally deferred to **L08**.

## Screenshot cross-check

Only after the EXE-first analysis, the supplied Dồn screenshot was checked:

- SHA-256 `dffb4da895d21dea87dd72a6601c29104f519dca89c2f716f5a7445bcbe4421a`.

It agrees with the lifecycle structure:
- one common play/control surface for accounts;
- role comes from receiver selection rather than a separate receiver-only button set;
- shared Dồn coordinate and receiver rows remain as frozen by L05/L06.

## Runtime evidence

Frozen packaged `automove_log.txt`:

- SHA-256 `17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`
- **387,238 lines**

Correlated lifecycle marker counts:
- `[RECV]`: 0
- `[RECV-DBG]`: 0
- `[DON]`: 0
- `[DON-DBG]`: 0
- `[DonVang]`: 0
- `[Donvang]`: 0
- `Sẵn sàng nhận`: 0
- `Chuẩn bị nhận`: 0
- `Đang nhận`: 0
- `Chờ dồn`: 0
- `Về dồn`: 0
- `Đang dồn`: 0
- per-row Dồn Farm start/stop markers: 0

Therefore L07 is **STATIC_VERIFIED / LIVE_RUNTIME_PARITY_REQUIRED**.

## L07 boundary

Resolved:
- shared session state ownership;
- start-time receiver-vs-donor worker split;
- `_farm_acc` primitive vs full Farm FSM;
- receiver worker integration;
- donor Farm callback integration;
- exact state vocabulary/colors;
- transaction start/done receiver states;
- donor Dồn state surfaces;
- cooperative stop/drain;
- generation stale-worker barrier;
- current role-change behavior boundary;
- receiver tracker lifecycle.

Deferred:
- exact generation assignment statement/order;
- exact first-cycle assignment statement for every intermediate receiver state label;
- exact join timeout/drain timing;
- live role-change/thread race parity;
- death/heal/disconnect/reconnect internals → L08.
