# M04 — Rao interval normalization / timing audit

## Authority

M04 re-inspected the exact frozen Rao block after reading PLAN.md / STATE.md and checking GitHub first.

- archive SHA-256: `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`
- inner EXE SHA-256: `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`
- module: `rao_tab.py / RaoTab`.

M01-M03 remain unchanged.

## 1. UI interval value

The visible column is:

**Lặp (s)**

Each Rao row owns `sec_var`.

The entry is validated through the nested `_only_digits` validator with Tk `%P`.

Recovered `isdigit` surface establishes the current edit rule:

- decimal digits are accepted;
- empty text is allowed while editing;
- arbitrary letters/signs/decimal punctuation are not normal UI input.

The screenshot's visible `30` is consistent with the statically recovered default below.

## 2. Default interval

The exact `_load_config` constant surface contains `"30"` both as the normal missing-value default and as the TypeError/ValueError fallback.

The row-construction/load boundary also passes `seconds` back into `_add_rao_row`.

Therefore the current Rao interval default/fallback is:

**30 seconds**.

Persistence keeps the row's `sec` value as the UI/config scalar; the worker converts it to numeric seconds when resolving a Rao definition.

## 3. Load normalization / clamp

The exact load block around the `sec` field contains:

- `min`
- integer constant **0**
- integer constant **60**
- the `sec` field
- `TypeError`
- `ValueError`
- fallback `"30"`.

Together with the reused module `max` builtin and the single `_sec` load local, this is strong static evidence that persisted numeric interval data is normalized to the bounded **0..60 second** domain before row reconstruction.

M04 freezes the semantic bounds as:

- stored/UI normalized minimum: **0**
- stored/UI normalized maximum: **60**
- malformed/non-numeric load fallback: **30**.

The exact syntactic nesting of `min/max/int` is not reconstructed because the constant stream is not Python source, but the resulting 0..60 clamp is the current static contract.

## 4. Runnable interval / zero handling

`_resolve_rao` has the exact failure text:

`'<Rao name>' chưa đặt thời gian lặp`.

The UI allows a temporarily blank interval, and load normalization can produce 0.

The slot worker uses a positive wait floor through the `max` wait surface.

The reconstruction contract is therefore:

- blank interval → Rao definition is not runnable;
- zero interval → not a valid repeating Rao interval;
- positive normalized values **1..60 seconds** are the current runnable interval domain.

Do not interpret 0 as “spam continuously”.

## 5. First-send timing

The exact `_slot_loop` documentation is:

> Vòng lặp rao độc lập của 1 slot: gửi nội dung slot đó, nghỉ đúng
> hẹn giờ của dòng rao rồi lặp. Tối đa 4 slot chạy song song / acc.

This fixes the loop order:

`resolve current Rao -> send -> wait interval -> resolve/send again`.

So a newly started valid slot performs its first send **before** waiting one interval.

There is no wait-one-full-period-before-first-send behavior.

## 6. Wait / cancellation boundary

The current slot loop contains:

- `_stop_event`
- `wait`
- `max`
- local `interval`.

Therefore the interval delay is an interruptible event wait, not an unconditional `time.sleep(interval)`.

This matters for stop behavior: a slot can be woken/stopped without waiting for the whole configured interval to expire.

The worker also guards:
- slot generation;
- per-slot running state;
- game-window validity.

Deep start/stop ownership remains M06.

## 7. Per-slot independence

The exact doc explicitly says each slot has an independent loop and up to **4 slots run in parallel per account**.

Each slot resolves its own selected Rao definition, including that definition's own interval.

Therefore one account may have four concurrent Rao timers with different intervals.

There is no recovered single global Rao timer shared by all four slots.

## 8. Live interval edits while running

`_slot_loop` owns locals:

- `want`
- `resolved`
- `content`
- `interval`
- `chan_id`
- `chan_name`.

The loop carries `_resolve_rao` inside the repeating slot surface rather than resolving once only at slot startup.

M02 also proved that edits to a Rao row are live StringVar writes and do not restart the worker.

Therefore:

- changing `Lặp (s)` while a slot is running does **not** retroactively shorten/extend the wait already in progress;
- after the current wait ends, the next loop re-resolves the Rao definition and observes the edited interval;
- no stop/start is required for the new interval to affect subsequent cycles.

## 9. Send success/failure timer behavior

The slot loop's static sequence contains:

- `send_chat`
- send-exception log surface
- timestamp/state update
- optional `verify_chat_echo`
- no-echo / send-error log surfaces
- then the common `_stop_event.wait(...interval...)` boundary.

No separate short retry/backoff interval constant or retry queue was recovered.

Thus a completed send attempt—whether send/echo result is successful or merely logged as failed/no-echo—returns to the normal configured interval before the next normal attempt.

This does not mean a hard exception/window death/invalid definition continues: those error/stop conditions can terminate the slot through the normal slot-stop path.

## 10. Definition invalidation between cycles

Because each loop resolves the currently selected Rao name again:

- deleted Rao definition;
- renamed old reference;
- blanked content;
- invalid channel;
- blank/zero interval

can make the next resolution fail.

The current worker owns the explicit `_stop_slot` surface and the exact doc:

> Dừng 1 slot (rao bị xóa/lỗi giữa chừng).

Therefore a definition that becomes unusable while running causes the affected slot to stop/fail closed rather than continuing forever with stale cached content/interval.

Exact per-account UI state after that stop is deferred to M06.

## 11. Storage type boundary

M02 established JSON payload field `sec`.

The UI source is a StringVar and the load fallback/default is textual `"30"`.

Therefore persistence is treated as a textual decimal interval value, while runtime `_resolve_rao` returns numeric `interval_giây`.

Do not store a hidden milliseconds value or convert the UI to minutes.

## 12. Screenshot/runtime cross-check

Only after static extraction, the Rao screenshot was cross-checked:

- visible interval: **30**
- current static default/fallback: **30 seconds**.

The frozen `automove_log.txt` has no correlated Rao send trace, so exact wall-clock scheduler jitter and live message echo timing remain runtime-required.

## M04 boundary

Verified:

- digits-only/blank-edit UI validation;
- default/fallback **30s**;
- normalized load domain **0..60**;
- runnable positive domain **1..60s**;
- first send occurs before interval wait;
- event-based interruptible interval wait;
- four independent per-account slot timers;
- live interval edit affects the next loop without restart;
- current in-progress wait is not dynamically rescheduled;
- normal send/no-echo failure returns to the normal interval rather than a recovered fast-retry path;
- unusable definition on a later loop stops/fails closed.

Runtime-required / explicit edges:

- exact Tk validation callback return expression;
- exact scheduler jitter under Windows load;
- exact UI state wording after a running slot becomes invalid;
- exact server echo latency/behavior.

Deferred:
- M05 account assignment/persistence;
- M06 full start/stop ownership;
- M07 parity/reconstruction gate.
