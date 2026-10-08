# L09 — Dồn all-account action flow

## Authority

L09 was performed against the exact frozen specimen before screenshot/runtime use:

- archive SHA-256: c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd
- archive size: **93,715,901 bytes**
- ZIP entries: **1,050**
- CRC clean
- inner EXE SHA-256: 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22
- inner EXE size: **47,450,112 bytes**

L02-L08 contracts remain unchanged.

## Current Dồn “Điều khiển tất cả” surface

The exact Dồn UI constant block is:

- **Điều khiển tất cả:**
- **Tới nơi nhận**
- **Tới chỗ bán**
- **Tới nơi train**

The exact command surface immediately after those buttons contains:

- threading.Thread
- _move_all_recv
- target / daemon / start
- _move_sell_acc
- _move_all

So the current visible quick controls are mapped as:

```text
Tới nơi nhận -> _move_all_recv
Tới chỗ bán  -> _move_sell_acc
Tới nơi train-> _move_all
```

Each top-level quick command is moved off the Tk main thread.

The separate bottom **Bắt đầu** button is wired to `_toggle_farm`. It is not one of these three quick movement commands.

## Bulk row universe

The exact `_checked_rows` documentation says:

> Tất cả acc trong danh sách (thao tác hàng loạt áp dụng cho mọi acc).
>
> Loại trừ acc nhận đồ — acc này không đi farm, vận hành theo luồng riêng.

Therefore the current effective bulk universe for the ordinary donor helper family is:

```text
all managed account rows
minus
all selected receiver HWNDs
```

The name `_checked_rows` and the older “acc được tick” wording are legacy naming. The current function documentation says all listed nonreceiver accounts, not “only rows with an active checkbox”.

## Tới nơi train

`_move_all`

Exact documentation:

> Di chuyển các acc được tick tới tọa độ đã cấu hình — song song.

Combined with the current `_checked_rows` contract and button binding:

```text
all nonreceiver/donor rows
    ↓
each row's configured Train preset
    ↓
_move_acc / normal coordinate resolution
    ↓
parallel donor moves
```

Receivers are excluded because receiver movement belongs to its own flow.

This is a movement-only command. It does not start the full Dồn Farm session.

## Tới chỗ bán

`_move_sell_acc`

Exact documentation:

> Di chuyển mọi acc nhận đồ tới chỗ bán (tọa độ bán của từng acc).

So this action is receiver-only:

```text
selected receiver accounts
    ↓
resolve each receiver's current sell destination
    ↓
move to sell point
```

The function contains a nested `_run` worker surface and explicit logs for:

- no receiver selected;
- receiver with no valid sell coordinate.

Important distinction:

**Tới chỗ bán is not `_sell_all`.**

It only moves receiver accounts toward their sale destination. Actual item selling remains the `_sell_acc / _sell_all` family.

The exact nested worker join/order policy is not fully source-visible.

## Tới nơi nhận

`_move_all_recv`

Its exact documentation says:

> Di chuyển acc giao tới tọa độ nhận của acc nhận tốt nhất hiện tại
> (thấp vàng/h nhất trong các acc nhận đang sẵn sàng); acc nhận thì về
> ĐÚNG tọa độ nhận riêng của dòng combobox tương ứng với nó.

The current effective behavior must be read together with L05/L06:

### Donor accounts

Manual move-only receiver selection:

1. prefer a currently ready receiver;
2. among ready candidates, reuse L06's lowest-gold/hour ranking;
3. randomize equal-speed ties;
4. if the move-only action cannot pick a ready receiver, reuse the L06 manual fallback: first receiver with valid coordinates;
5. donor moves to that receiver's Dồn/receive target.

This fallback is allowed for the manual **Tới nơi nhận** movement action.

It must not be copied into automatic Dồn's no-ready behavior, which still skips the cycle and continues farming.

### Receiver accounts

The old documentation says the receiver uses the coordinate belonging to its receiver row.

In the current UI architecture from L05, every receiver row's compatibility `recv_coord_var` points to the same shared `_recv_coord_var`.

Therefore the current result is:

```text
each receiver account
    ↓
its receiver-row coordinate alias
    ↓
same shared Tọa độ dồn value
```

Do not reconstruct one independent coordinate field per receiver just because the compatibility wording says “riêng của dòng”.

The top-level quick action itself is run in a worker thread. Exact internal per-account ordering/parallelism inside `_move_all_recv` remains runtime/source-detail unknown.

## Real but currently unwired bulk helpers

The exact Dồn class also contains:

### _stop_all

> Dừng các acc được tick — song song.

Adjacent helper surface:
`_stop_acc`.

Effective current universe:
all nonreceiver rows from `_checked_rows`.

### _farm_all

> Farm các acc được tick — song song.

Adjacent helper surface:
`_farm_acc`.

But L07 already proved:

`_farm_acc`
= internal StartAutoFight Train memory primitive
≠ full Dồn Farm lifecycle.

So:

`_farm_all`
must not be substituted for the current big **Bắt đầu** button.

### _sell_all

> Bán đồ các acc được tick — song song.

This is the actual selling-flow helper family, not a movement button.

Current effective ordinary universe:
all nonreceiver rows from `_checked_rows`.

## Current UI wiring boundary

No current Dồn toolbar or StartTab button binding was recovered for:

- `_stop_all`
- `_farm_all`
- `_sell_all`.

They are real class methods and must not be deleted from a parity reconstruction merely because the visible UI no longer calls them.

But reconstruction must also **not invent new visible buttons** for them.

The current visible UI uses:

- three move-only quick commands;
- the full `_toggle_farm` lifecycle button.

## Authoritative Bắt đầu / stop behavior

Current big button:

`Bắt đầu -> _toggle_farm`.

L07 remains authoritative:

- when starting, only not-yet-farming rows are started;
- receiver/donor role is classified at session start;
- receiver starts `recv_cycle`;
- donor starts `_farm_cycle(don_callback=...)`;
- when stopping, only currently running rows are drained;
- stopping some rows leaves remaining Dồn sessions running;
- stopping the final row resets the global button after worker drain.

This is the all-account session control.

Do not replace it with `_farm_all` or `_stop_all`.

## StartTab parity

The StartTab Dồn section exposes:

- **Dồn vàng**
- **Tới nơi nhận**
- **Tới chỗ bán**
- **Tới nơi train**
- **Cấu hình**

Exact wrapper surfaces:

`_toggle_donvang_cmd`
→ toggles Dồn
→ synchronizes text/state between StartTab and DonVangTab.

`_donvang_action(method_name)`
→ invokes the delegated Dồn bulk action in a worker thread.

Current quick-action mapping is the same as the dedicated Dồn tab:

```text
StartTab Tới nơi nhận -> _move_all_recv
StartTab Tới chỗ bán  -> _move_sell_acc
StartTab Tới nơi train-> _move_all
```

`Cấu hình`
→ `_goto_donvang_tab`
→ navigate to the Dồn tab rather than performing an action.

This is functional parity, not a second independent implementation.

## Thread and cancellation boundary

The quick move buttons are standalone asynchronous commands.

No dedicated quick-action queue/cancel token was recovered.

They are not the same worker collection as the full `_toggle_farm` session.

Therefore L09 does not claim:

- big Farm Stop definitely cancels a quick move already in progress;
- a quick move is automatically serialized against a concurrently started Farm session;
- standalone quick move completion has a specific join barrier visible to the UI.

Those overlap cases require live runtime parity or stronger native-code recovery.

The separate `_stop_all` helper exists, but because no current button binding was recovered, it must not be silently repurposed as the quick-command cancellation mechanism.

## Screenshot cross-check

Only after static extraction, the supplied Dồn screenshot was checked.

SHA-256:
dffb4da895d21dea87dd72a6601c29104f519dca89c2f716f5a7445bcbe4421a

It visibly agrees with the exact surface:

```text
Điều khiển tất cả:
[Tới nơi nhận] [Tới chỗ bán] [Tới nơi train]

[Bắt đầu]
```

No visible **Dừng tất cả / Farm tất cả / Bán tất cả** buttons exist in the captured Dồn tab.

## Runtime evidence

Frozen `automove_log.txt`:

- SHA-256: 17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500
- **387,238 lines**

Correlated current bulk-action counts are 0 for:

- `[Tới chỗ bán]`
- `[Tới nơi nhận]`
- `[Farm] Bắt đầu farm`
- `[Farm] Dừng farm`
- `[Đánh]`
- `[Bán đồ]`
- `chưa chọn được acc nhận đồ hợp lệ`
- `Chờ dồn`
- `Về dồn`
- `Đang dồn`.

Therefore L09 is:

**STATIC_VERIFIED / LIVE_RUNTIME_PARITY_REQUIRED**.

## L09 boundary

Resolved:
- current visible Dồn all-account toolbar;
- exact quick-button backend mapping;
- nonreceiver bulk universe;
- Train quick move;
- receiver-to-sell move;
- role-aware move-to-receive action;
- current shared-coordinate reconciliation;
- legacy helper semantics;
- big Bắt đầu authority;
- StartTab parity;
- visible/unwired boundary.

Deferred:
- exact internal ordering/join policy inside `_move_all_recv`;
- exact `_move_sell_acc` worker join policy;
- standalone quick-command overlap/cancellation;
- hidden/plugin reachability of legacy helper methods;
- live StartTab synchronization timing.
