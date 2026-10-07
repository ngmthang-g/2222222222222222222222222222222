# K06 — Trừng Ác combat / movement-stop / auto-train flow

## 1. Successful summon enters the combat segment

K05 ends only after the `Triệu hồi` stage succeeds. The next compact block inside `DailyTab._punish_exec_sequence` is the Trừng Ác fight phase.

```text
successful summon
      ↓
state/log = "Đánh ác tặc"
      ↓
start_auto_train(...)
      ↓
configured punish_duration fight window
      ↓
post-fight position/drift check
      ↓
final-HP/heal edge       [heal internals deferred K07]
      ↓
"Kết thúc ==="
      ↓
return to K03 outer Trừng Ác loop
```

The function-local mapping contains `punish_duration`, `_fight_pos`, `_t_end`, final character-info locals and `_drift`. The fight block explicitly references `monotonic`, so the configured duration is a deadline-style elapsed-time window, not a loop-count.

## 2. Auto-train is enabled through the shared helper

Daily calls `start_auto_train` with keyword-name tuple:

```text
stop_check
verify
```

The exact Boolean value passed for Daily's explicit `verify` keyword is not instruction-bound by the serialized constant stream, so K06 does not guess it.

The shared `utils.start_auto_train` contract is independently exact:

```text
start_auto_train(
    hwnd,
    stop_check=None,
    verify=True,
    samples=3,
    interval=1.0,
    retries=2
)
```

Its behavior is:

```text
send StartAutoFight(Train / mode 1)
      ↓
when verify enabled:
  sample Direction 3 times, 1.0s apart
  ├─ any valid Direction changes → success
  ├─ all valid samples identical → verification failure
  └─ insufficient valid samples → None / fail-open
      ↓
verification/send failure → retry up to 2 times
maximum send attempts = 3
```

The shared mode contract is `0=stop`, `1=train`, `2=pk`, `3=quest`, `6=fuben`.

## 3. Auto-train failure is fail-soft

Daily has an exact failure line:

```text
"gửi bật auto train thất bại → vẫn đánh tiếp"
```

Therefore failure to prove/start auto-train does **not** hard-stop the account and does **not** itself skip the fight window. The combat sequence continues.

This is an important parity behavior: do not convert it to a hard error merely because a reconstructed implementation could be stricter.

## 4. No Daily combat-end auto-off call is recovered

A bounded Daily-payload scan contains:

- `start_auto_train`;
- no `stop_game_auto`;
- no `set_game_auto`;
- no `AUTO_MODE_NONE`;
- no `stop_auto_train`.

The shared `utils` module does have `stop_game_auto`, and movement code can stop game auto later as a side effect of moving. But the Daily combat tail itself has no recovered explicit auto-off surface.

```text
combat ends
   ↓
NO invented Daily stop_game_auto() here
   ↓
next outer-cycle actions/movement may later change auto state through their own helper contracts
```

## 5. Combat timing and stop/death behavior

The exact combat block owns `_t_end` and references `monotonic`. This binds `punish_duration` to elapsed seconds.

The block also contains:

```text
"chết giữa lúc đánh → dừng đánh sớm"
```

so the fight window can end before its deadline when the already-owned death/respawn signal becomes active. K03/K07 own the broader stop/respawn lifecycle; K06 does not rewrite that Boolean composition.

The exact internal sleep/wait quantum of the fight loop is **UNKNOWN** from current static evidence. Do not infer `0.5s`, `1s`, etc. merely because those constants exist elsewhere in the module.

## 6. Fight anchor and drift detector

Before/during the fight, the block captures a fight-position state using character info including `PosX/PosY` (and the later comparison logs both source and destination map). The fallback tuple is `(None, 0, 0)`.

After the fight it computes displacement through `math.hypot` and contains the exact integer threshold:

```text
160 pixels
```

When the character has moved too far, the exact log is:

```text
LỆCH KHỎI BÃI ĐÁNH (... px) — nghi bị follow party lôi đi / PK đẩy
```

No direct Daily relocation helper or auto-off symbol is recovered in the combat-tail block. The exact Python return effect of this branch is not instruction-bound, so K06 freezes the detector/log and leaves the return micro-effect UNKNOWN rather than inventing a corrective move.

## 7. Final heal is only a boundary in K06

The combat tail has an exact final HP-check surface and a failure line:

```text
"% — kiểm tra trị liệu cuối vòng"
"[TRỪNG ÁC]   Heal cuối vòng thất bại"
```

K06 records only that this edge exists. The actual heal route/retry/reconnect/death behavior belongs to K07.

Normal tail text is:

```text
"— Kết thúc ==="
```

After this, control returns to the already-proven K03 open-ended Trừng Ác worker. If the account/session remains active, a later outer iteration starts a new cycle. The exact Python success return scalar (`True` versus `None`, etc.) is not instruction-bound and remains UNKNOWN.

## 8. `_wait_movement_stopped` is not to be inserted into Trừng Ác combat by assumption

K06 audited `DailyTab._wait_movement_stopped` because it was named in the K06 continuation contract. Its recovered signature-local mapping is:

```text
self, hwnd, cancel_event, tag, stop_check, skip_set, by_memory,
_stopped, ok, hung_deadline, recovered, md
```

The immediately associated defaults are:

```text
(None, None, False)
```

so the recovered `by_memory` default is **False**.

### Memory branch

When `by_memory=True`, Daily calls `utils.wait_stopped_by_direction` with an explicit 300-second timeout. The shared helper defaults are exact:

```text
stop_check=None
timeout=300
stable_needed=6
interval=0.5
move_eps=16
```

Its frozen documentation says:

```text
Phase A:
  wait for common.active + valid/stable MapID

Phase B every 0.5s:
  read PosX, PosY, MapID
  movement >16px or MapID change → reset stable count
  stable 6 consecutive polls (~3s) → stopped=True
  stop or 300s timeout → False
```

It retains the older detector side effect of closing PK-warning UI during polling.

### Non-memory branch

The Daily helper also exposes the older `MovementDetector` / `is_moving` path, described in its own frozen text as the **10-pixel** detector branch.

### Hung-window check

After movement reports stopped, the helper probes `is_window_hung`. It exposes `HUNG_TIMEOUT` and custom `DailyTab.WindowHungError`. The `HUNG_TIMEOUT` symbol is exact, but its numeric value is not safely bound by K06.

### Current Daily call-site boundary

The explicit `_wait_movement_stopped` call recovered in the compact Daily constants is in the **Tàng Bảo Đồ** block, with keyword names `stop_check/skip_set` and no visible `by_memory` override. No direct call edge is recovered from the Trừng Ác combat compact block.

Therefore a future clone must **not** inject `_wait_movement_stopped` into the Trừng Ác fight merely because this helper was audited in K06.

## 9. Runtime and screenshot cross-checks

Static extraction was completed first.

The re-supplied Daily screenshots exactly match the previously frozen B08 hashes:

```text
217178561894a4205c7b5835ed33c050b384c8f60359f6894165e3400d514834
3939691e166fa67d9c50069119e4e3904496cd6769b04cf0d3199c6b3e0f866b
```

They confirm the clean visible `Thời gian đánh ác tặc (giây): 15` baseline, but they show no running combat state and are not used to infer hidden behavior.

The exact packaged `automove_log.txt` has SHA-256:

```text
17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500
```

It contains **0** correlated Daily/K06 markers for `[TRỪNG ÁC]`, `Đánh ác tặc`, `start_auto_train`, `verify hướng`, or `LỆCH KHỎI BÃI ĐÁNH`.

It does contain **8,511** generic `AutoFight_Main` lines, including **6,102** `:Start` lines. Those are useful evidence that the packaged environment exercised the underlying auto-fight primitive, but they are not correlated to Daily and therefore are **not** end-to-end K06 proof.
