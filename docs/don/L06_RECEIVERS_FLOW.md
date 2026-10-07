# L06 — Dồn receiver accounts / readiness / selection / locking flow

## Authority
L06 was performed against the exact frozen specimen before screenshot/runtime use:

- ZIP SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`
- ZIP size **93,715,901 bytes**
- **1,050** entries, CRC clean
- inner `TLMTool.dist/TLMTool.exe` SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`
- inner EXE size **47,450,112 bytes**
- active Dồn authority: `donvang_tab.py / DonVangTab`
- direct transaction/receiver registry authority: `don_logic.py`

## 1. Receiver row lifecycle

`_add_receiver_row`
→ account combobox
→ delete button
→ row label `Acc nhận N`
→ coordinate variable is **not owned by the row**; all rows reference L05's shared `_recv_coord_var`.

`_renumber_receiver_rows`
→ after deletion, relabel rows `Acc nhận 1, 2, 3...`.

`_remove_receiver_row`
→ delete selected receiver row
→ never remove the final remaining row
→ shared Dồn coordinate survives because it is outside `_recv_rows`.

`_sync_recv_aliases`
→ keeps old singular APIs compatible:
- singular receiver selection aliases resolve through the first receiver row;
- receiver coordinate alias remains the shared Dồn coordinate used by every row.

Config load creates **one receiver row** when no receiver config exists.

## 2. Receiver account candidate list

`_refresh_receiver_combo`
→ scan current `_acc_rows`
→ read displayed character names
→ rebuild values for every receiver combobox
→ preserve current selection while the account still exists.

The function owns:
`names, hwnd_map, nm, label, dup, base, rd, any_valid, cur`
and the serialized label fragments include `" ("` plus HWND.

This fixes the duplicate-name policy at the static level:
- unique character name → plain character-name label;
- duplicate character names → disambiguated display label with parenthesized HWND;
- `_receiver_hwnd_map` maps the UI display label back to the real HWND.

Every receiver combobox receives the same candidate surface. No cross-row "already selected elsewhere" exclusion surface is recovered.

Therefore selecting the same account in two receiver rows is not modeled as two separate runtime receivers:
`_all_receiver_hwnds`
→ returns a **set** of selected HWNDs
→ duplicates collapse for downstream membership.

## 3. Receiver identity helpers

`_is_receiver_hwnd(hwnd)`
→ true if HWND is selected in **any** receiver row.

`_selected_receiver_hwnd()`
→ first selected receiver row HWND
→ legacy/single helper only.

`_all_receiver_hwnds()`
→ set of all selected receiver HWNDs.

`_find_recv_row_for_hwnd(hwnd)`
→ receiver configuration row corresponding to that HWND, or None.

Changing receiver selection:
`_on_receiver_selected`
→ update receiver/nonreceiver style
→ move selected receiver account row to top.

The GUI buttons do not become a different button set. Receiver distinction is presentation + runtime role.

## 4. Receiver state ownership is in don_logic

The real ready/busy transaction state is not inferred from label text.

`don_logic` owns:

`_recv_registry[receiver_hwnd]`
with independent:
- `ready` Event
- `donated` Event
- `aborted` Event
- `donor_hwnd`.

Registry access is protected by `_recv_reg_lock`.

`_register_receiver`
→ idempotently creates state.

`_unregister_receiver`
→ removes it when the receiver cycle ends.

`ready_receiver_hwnds()`
→ receiver HWND set whose ready Event is currently set.

This is the authoritative ready source used by automatic Dồn.

## 5. Receiver FSM

`recv_cycle(receiver)`

1. register receiver;
2. sell using receiver's selected sell destination;
3. move receiver back to the receive/Dồn point;
4. mark `ready`;
5. donor may claim it;
6. wait for one of:
   - `donated` → successful receive completed;
   - `aborted` → donor stopped/disconnected/aborted;
   - claimed donor window dies → reset immediately;
7. repeat with next sell/return cycle;
8. unregister on receiver loop exit.

Exact embedded summary:

`sell -> move back -> set ready -> wait donated -> repeat`.

A failed move to the receive point does not set ready; the receiver retries on a later cycle.

## 6. GUI phases

Current receiver-phase UI uses:

- **Sẵn sàng nhận** → green `#2e7d32`
- **Chuẩn bị nhận** → blue `#1565c0`
- **Đang nhận** → blue `#1565c0`.

`prep_cb`
→ used once after a donor has the receiver locked and is moving toward the Dồn point
→ receiver UI becomes **Chuẩn bị nhận**.

`_on_recv_phase(receiver, "start")`
→ **Đang nhận**.

`_on_recv_phase(receiver, "done")`
→ if the receiver still says **Đang nhận**, return to **Sẵn sàng nhận**.
The receiver's next sell stage will later change its state again.

## 7. Receiver priority

`_receiver_speed(receiver)`
→ current receiver gold/hour
→ tracker formula:
`_extra_donated / elapsed_hours`.

`_pick_ready_receiver(donor, ready_hwnds)`
→ candidate must:
- be a selected receiver;
- differ from donor HWND;
- be ready;
- have valid coordinate resolution.

Then:
1. compute speed for each candidate;
2. find the **minimum** gold/hour;
3. collect all candidates tied at that minimum;
4. `random.choice` among ties;
5. return `(receiver_hwnd, coords)`.

So the policy is intentionally:
**feed the currently lowest-gold/hour ready receiver first**.

This is recalculated for every donor selection event rather than fixed at startup.

## 8. Ready wait and busy re-check

Automatic Dồn uses `don_move_and_execute`.

Before selecting:
`don_wait_recv_ready`
→ wait for at least one ready receiver.

The frozen log text explicitly contains:
`ready=[] trong 5s`
and:
`Chưa có acc nhận nào sẵn sàng — bỏ qua, farm tiếp`.

After choosing, the receiver's own lock is acquired and readiness is checked again.

This closes the race:
- candidate can be ready when listed;
- another donor may claim it first;
- after lock, if it is no longer ready, the stale candidate is rejected.

If a receiver lock is busy, that receiver is skipped.
If all receiver locks are busy:
→ skip this Dồn cycle
→ farm continues.

There is no global queue waiting behind one busy receiver.

## 9. Per-receiver locking / parallelism

`_don_lock_for(receiver_hwnd)`
→ creates/returns an idempotent lock dedicated to that receiver.

Consequences:

- donor A → receiver 1 and donor B → receiver 2 can execute concurrently;
- two donors cannot simultaneously Dồn into the same receiver;
- manual `don_single` and automatic `don_move_and_execute` use the same per-receiver lock policy.

After a receiver is claimed:
`set_receiver_donor(receiver, donor)`
records `donor_hwnd`.

A fresh attempt clears an old abort only after the receiver lock is held.

This is the serialization boundary; there is no single global Dồn lock.

## 10. Fault isolation

If donor stops/disconnects/aborts after claiming:
`mark_receiver_aborted(receiver)`
→ only that receiver resets its receive cycle.

If the donor process/window dies while receiver waits:
→ receiver detects the claimed donor is gone
→ clean stale trade UI
→ restart its cycle immediately.

It does not wait forever for a `donated` signal that can never arrive.

Other receiver registry entries are unaffected.

## 11. Background trade watcher

Each selected/used receiver is ensured to have one background watcher.

`_ensure_trade_watch(receiver)`
→ if an existing thread is alive, do nothing
→ otherwise `_start_trade_watch`.

Watcher lifetime:
→ until that receiver game window closes.

The watcher is deliberately active even while no Dồn operation is occurring.

Allowed inviter set:
`_managed_account_names()`
→ **all character names currently managed by the tool**, donor and receiver rows alike.

Name matching uses `don_logic.normalize_name`, whose static contract normalizes case/diacritics and server suffix formatting.

Watcher behavior:
- allowed managed account inviter → accept;
- unknown/wrong inviter → press cancel, continue watching;
- unreadable/non-invite MessageBox → ignore;
- receiver currently claimed by donor → watcher **yields**.

The last rule is important: during real Dồn, the transaction flow itself must press the invitation confirmation. Letting the watcher press the same MessageBox would create a two-thread race.

## 12. Manual movement fallback is not automatic-ready fallback

`_fallback_receiver`
→ first receiver with a valid coordinate.

Its only direct Dồn-tab use is next to `_pick_ready_receiver` in the manual/move-only **Tới nơi nhận** path.

That gives a usable movement destination even if no receiver is currently ready.

Automatic Dồn does **not** convert "no ready receiver" into this fallback. Automatic behavior remains:
no ready / all busy → skip cycle and farm.

## 13. Persistence / migration boundary

Current save/load surface under `[DonVang]` includes:

- `recv_count`
- `recv_<n>_acc`
- `recv_<n>_coord`
- legacy `receiver`
- legacy `recv_coord`.

Because current rows all point at the shared L05 coordinate variable, per-row coordinate fields are compatibility data rather than independent live coordinates.

`_load_receiver_rows` locals expose:
`entries, count, acc, coord, shared, _acc, _c, _coord`.

This proves a migration path exists, but the exact precedence for a deliberately conflicting config such as:
- legacy `recv_coord=A`
- `recv_1_coord=B`
- `recv_2_coord=C`

is not source-visible enough from the recovered constant surface.

L06 leaves that one conflict case **EXPLICIT_UNKNOWN** rather than inventing a winner.

## 14. Screenshot cross-check

Only after static extraction, Dồn screenshot SHA-256
`dffb4da895d21dea87dd72a6601c29104f519dca89c2f716f5a7445bcbe4421a`
was checked.

It visibly shows:
- one shared **Tọa độ dồn** selector;
- **Acc nhận 1**;
- **Acc nhận 2**;
- delete buttons per receiver row;
- **+ Thêm acc nhận**.

This matches the dynamic multi-receiver row model.

## 15. Runtime evidence

Frozen packaged `automove_log.txt`:
- SHA-256 `17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`
- **387,238 lines**.

Counts recovered for correlated receiver lifecycle markers:
- `[RECV]`: 0
- `[RECV-DBG]`: 0
- `[DON]`: 0
- `Sẵn sàng nhận`: 0
- `Chuẩn bị nhận`: 0
- `Đang nhận`: 0
- `DON-WATCH`: 0
- receiver-claim/busy logs: 0.

Therefore L06 is **STATIC_VERIFIED / LIVE_RUNTIME_PARITY_REQUIRED**.

## L06 boundary

Resolved:
- receiver-row lifecycle;
- duplicate-name HWND disambiguation;
- effective duplicate-row membership behavior;
- receiver identity helpers;
- registry/event ownership;
- receiver FSM;
- ready/prep/receiving UI phases;
- lowest-gold/hour selection;
- random tie behavior;
- ready recheck after lock;
- per-receiver serialization and multi-receiver parallelism;
- abort/dead-donor fault isolation;
- one-watcher-per-receiver trade invitation policy;
- manual fallback vs automatic-ready behavior.

Deferred:
- conflicting legacy/per-row coordinate migration winner;
- live thread timing/races;
- broader Train/Dồn lifecycle integration → L07.
