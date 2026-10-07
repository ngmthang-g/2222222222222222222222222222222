# L04 — Dồn inventory / full-bag / filter interaction flow

## Authority
Re-inspected exact `TLMTool_2.1.2(8).zip` before screenshot use: SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, 93,715,901 bytes, 1,050 entries, CRC clean. Inner `TLMTool.exe`: SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`. Active authority remains `donvang_tab.py / DonVangTab`.

## Bag metric
`_get_bag_slots(hwnd)` reads occupied **Site-10 slots** and returns `None` on read failure. It is not total item quantity or free-slot count; unreadable memory must not become zero.

## Dồn keep policy
Exact serialized Dồn constants:
- modes `("all","weapons")`
- labels `all -> Tất cả`, `weapons -> Chỉ vũ khí`
- presets `all -> []`, `weapons -> ["discard_nonweapon"]`
- default `all`

Dồn has only these two keep radios. There is no Dồn **Không** mode and Dồn never opts into `discard_weapons`.

## Hidden pickup
`pickup_no_cankhon_var -> _pickup_no_cankhon`. The helper has exact default delay `(5,)`, then calls `memory_items.set_auto_fields` with `PICKITEM.IsOn=True` (bool). Compiled documentation states the old manual UI click sequence was removed. No recurring 5-second poll was recovered.

`pickup_no_cankhon` enables hidden pickup; `pickup_mode` controls what the later pre-Dồn filter may discard. They are independent.

## Full-bag threshold
The exact full-bag region contains `full_bag_timer/full_bag`, nested `stop_bag_check`, one default tuple `(3,)`, then constants **98** and **100**. Farm-cycle locals contain both `no_cankhon/threshold` and post-filter `_nc/_th/_after`.

Strong static binding fixes:
- hidden pickup ON -> **98 occupied slots**
- hidden pickup OFF -> **100 occupied slots**

The nearby **3** is not a slot threshold. It is the exact default attached to nested `stop_bag_check`. Constants do not safely expose its parameter name or debounce/confirmation micro-order, so L04 does not invent “3 samples” as proven behavior.

## Full-bag path
For `full_bag_timer` (legacy alias `full_bag`):
1. resolve current hidden-pickup state and threshold 98/100;
2. evaluate occupied Site-10 slots;
3. on full, call `_filter_before_don`;
4. re-read occupied slots against the current threshold;
5. below threshold -> stay at farm and wait a later cycle;
6. still at/above threshold -> continue into the already-proven L02 Dồn/return boundary;
7. `None` from filter/no-filter/error cannot fabricate free space and therefore cannot cancel an already-detected full-bag transition.

Exact post-filter logs include:
- `đầy túi nhưng lọc còn chỗ (...) ô) → ở lại, chờ vòng sau`
- `lọc xong vẫn đầy (...)`

## Pre-Dồn filter
`get_pickup_preset_keys()` maps the current Dồn mode to the exact Dồn preset list.

`_filter_before_don(hwnd, stop_check)` temporarily sets **Đang lọc đồ** and calls:
```
bag_filter.discard_for_activity(
    hwnd,
    activity="train",
    keys=<Dồn preset keys>,
    stop_check=<farm cancel predicate>
)
```

Only `keys` and `stop_check` are supplied, so shared defaults remain active:
- delay **1.0s**
- empty keys/rules -> no scan/no packet/no discard
- selected rules OR-combined
- targets de-duplicated by `dbID`
- action **4**, opcode **100005**, payload `4:<dbID>`, whole stack
- cooperative cancellation through `stop_check`.

After filtering, Dồn re-reads Site-10 occupied slots and returns integer when usable or `None` for Tất cả/no-filter/error/unusable read. The prior row state is restored only if another actor has not changed it. **Đang lọc đồ** style is `#8e24aa`.

## Effective matrix
| Hidden pickup | Keep mode | Threshold | Pre-Dồn discard |
|---|---|---:|---|
| OFF | Tất cả | 100 | none |
| OFF | Chỉ vũ khí | 100 | discard non-weapon equipment |
| ON | Tất cả | 98 | none |
| ON | Chỉ vũ khí | 98 | discard non-weapon equipment |

## Screenshot cross-check
Only after static extraction, screenshot SHA-256 `dffb4da895d21dea87dd72a6601c29104f519dca89c2f716f5a7445bcbe4421a` was checked. It shows hidden pickup unchecked, **Tất cả** selected, and only **Tất cả/Chỉ vũ khí** radios. Captured state therefore resolves to threshold **100** and no pre-Dồn discard preset.

## Runtime boundary
Frozen `automove_log.txt`: SHA-256 `17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`, 387,238 lines. Correlated Dồn/full-bag/filter/PICKITEM markers are 0. Raw `action=4` appears **22,734** times but is primitive-only evidence, not attributable to Dồn.

Classification: **STATIC_VERIFIED / LIVE_RUNTIME_PARITY_REQUIRED**.

## Deferred
- exact callback parameter meaning/micro-order behind default 3
- live memory propagation after discard
- L05 coordinates
- later receiver selection/transaction logic
