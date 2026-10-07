# K07 — Trừng Ác heal / reconnect / respawn recovery flow

## 1. Recovery components

The frozen Daily module owns three distinct Trừng Ác recovery surfaces:

```text
DailyTab._diaphu_monitor
DailyTab._punish_disconnect_monitor
DailyTab._punish_heal
```

and connects them to both the activity-wide Trừng Ác worker and the single-account worker.

They are not one generic recovery loop. Death/Địa-phủ, disconnect, and low-HP treatment have different signals and different retry/termination semantics.

---

## 2. Death / Địa-phủ monitor

Exact frozen documentation:

```text
Theo dõi mỗi 4s: MapID==87 → respawn_event;
HP==0% → click hồi sinh.
```

Recovered local state includes:

```text
detected
hp_latched
ci
hp_pct
```

Flow:

```text
every 4 seconds
    ↓
read character info
    ↓
HP == 0?
    ├─ yes
    │   → state surface "Về Địa phủ"
    │   → click client (792,441)
    │   → "HP 0% → click (792, 441) hồi sinh"
    │   → hp_latched prevents uncontrolled repeat clicking
    │
    └─ no
        → continue monitoring

MapID == 87?
    ├─ yes
    │   → respawn_event.set()
    │   → detected latch suppresses duplicate event work
    └─ no
        → continue monitoring
```

The exact source expressions that re-arm `hp_latched` and `detected` are not instruction-bound and remain UNKNOWN.

This monitor is a recovery signaler, not a terminal account-stop mechanism.

---

## 3. How a respawn event returns to Trừng Ác

The Trừng Ác cycle entry contains the exact branch:

```text
respawn_event đang set
→ clear
→ cho heal/move rời map 87
```

Therefore Map87 recovery is intentionally consumed by the next Trừng Ác cycle.

Combined with K06:

```text
death during combat
    ↓
combat can stop early
    ↓
_diaphu_monitor detects HP0 / Map87
    ↓
revive click + respawn_event
    ↓
next cycle starts
    ↓
respawn_event.clear()
    ↓
optional low-HP heal
    ↓
normal movement/quest path leaves map 87
```

Death is therefore recoverable and does not by itself permanently disable the account.

---

## 4. Low-HP treatment at cycle start

The execution sequence reads:

```text
HpPercent
→ "[TRỪNG ÁC]   HP=<...>% — kiểm tra trị liệu đầu vòng"
```

When Trừng Ác treatment is enabled and HP is below 30%:

```text
"[TRỪNG ÁC]   HP < 30% → trị liệu tại Tô Châu"
      ↓
DailyTab._punish_heal(hwnd, stop_check=...)
```

If that start-of-cycle treatment fails:

```text
"[TRỪNG ÁC]   Heal thất bại → skip vòng này"
```

So start-heal failure is **fail-soft to the session but skips the current cycle**. It is not a terminal current-account stop.

---

## 5. Trừng Ác treatment route

The exact Daily treatment-coordinate table contains:

```text
Tô Châu → (155,252)
```

Daily's treatment helper contract elsewhere identifies this as:

```text
map 4, tile 155,252
```

`DailyTab._punish_heal` has exact locals:

```text
coords
heal_tile_x
heal_tile_y
ok
```

and exact move keyword surface:

```text
wait_for_arrival
stop_check
tolerance
```

with exact tolerance:

```text
10
```

Before movement it attempts injection repair. Injection failure is explicitly fail-open:

```text
inject cho heal thất bại, thử di chuyển trực tiếp
```

Then:

```text
move to Tô Châu treatment destination
    ↓
move succeeds?
    ├─ yes → treatment helper succeeds
    └─ no  → "di chuyển đến Tô Châu trị liệu thất bại"
```

The manual Daily treatment helper has exact treatment clicks `(892,474)` and `(514,424)`, but readable static evidence does not independently bind those same two clicks inside `_punish_heal`. K07 therefore does not invent that microsequence for the automatic helper.

---

## 6. Low-HP treatment at cycle end

K06 already froze the final HP-check boundary.

K07 confirms the same Trừng Ác heal subsystem is used at the cycle tail when treatment is enabled and HP is low.

Exact failure text:

```text
[TRỪNG ÁC]   Heal cuối vòng thất bại
```

Unlike the start-heal branch, this is already at the end of the combat cycle. The frozen surface shows a failure log, not a separate terminal-account stop.

The outer K03 loop remains responsible for the next cycle.

---

## 7. Disconnect monitor — Daily-specific detector

Exact Daily documentation:

```text
Theo dõi mất kết nối mỗi 2s — per-acc.

Memory veto + pixel dialog 3-strike:
socket chắc chắn mở (memory True) thì không bao giờ halt nhầm;
dialog phải đủ 2 pixel 3 tick liên tiếp (~6s)
mới halt + click (616, 455).
```

This is intentionally a different recovery design from Train/TrainLSV's larger five-attempt reconnect loop.

### Memory probe

Daily calls:

```text
memory_items.is_connected
```

Shared exact contract:

```text
TCPGame.Instance.tcpClient.Connected
True  = đang nối
False = mất kết nối
None  = đọc lỗi
```

Daily uses memory True as a **false-positive veto/reset**.

A memory False result does not replace the dialog persistence requirement.

### Frozen dialog probes

```text
login.ngatKetNoi1
  point     = (640,244)
  RGB       = (160,145,52)
  timeout   = 5
  tolerance = 5

login.ngatKetNoi2
  point     = (702,453)
  RGB       = (212,28,34)
  timeout   = 5
  tolerance = 5
```

Both must remain positive for 3 consecutive 2-second ticks.

```text
both pixels positive
    ↓
dc_strikes += 1
    ↓
strike 3/3
    ↓
"MAT KET NOI (dialog 3/3) → halt"
    ↓
halt.set()
    ↓
click client (616,455)
```

The just-confirmed dialog itself is the evidence used before this click. No Daily `/5` retry counter is recovered.

If the HWND disappears or is reused by another process, the disconnect monitor exits instead of reconnecting the wrong window.

---

## 8. Activity-wide Trừng Ác reconnect path

The activity-wide worker has a nested recovery surface:

```text
_punish_monitor_stops
```

Exact sequence:

```text
halt / disconnect observed
    ↓
state = "Mất kết nối"
    ↓
"[TRỪNG ÁC] Phát hiện mất kết nối → chờ kết nối lại..."
    ↓
wait for reconnect / active state
    ↓
timeout = 60 seconds

success:
    → "[TRỪNG ÁC] Kết nối lại OK → tiếp tục"

timeout:
    → "[TRỪNG ÁC] Kết nối lại timeout → dừng"
```

This is a bounded Daily reconnect wait.

Do **not** replace it with Train/TrainLSV's five attempts + 30-second batches + infinite retry.

---

## 9. Single-account Trừng Ác reconnect path

The per-row/bottom-start single worker owns a separate recovery shell.

Exact state:

```text
Chờ kết nối lại
```

It directly calls:

```text
wait_pixel("common","active", ...)
```

with keyword surface:

```text
window_hwnd
timeout
interval
debug
```

and an exact serialized interval constant:

```text
0.5
```

The frozen `common.active` pixel is:

```text
point     = (1330,33)
RGB       = (34,8,11)
timeout   = 100 in PIXEL_DATA
tolerance = 5
```

The activity-wide path directly proves a 60-second Daily reconnect window. The single-worker call uses the same Daily active-wait surface and timeout keyword, but readable constant metadata does not independently instruction-bind the single-worker numeric timeout. K07 therefore records the single-worker numeric value as a strong 60-second inference, not as a source-line exact binding.

No `/5` counter, retry-batch loop, or infinite Daily retry surface is recovered.

---

## 10. Reader cache invalidation after single-account reconnect

The single worker's direct local surface includes:

```text
invalidate_character_cache
_get_pid_from_hwnd
wait_memory_ready
```

Shared exact cache documentation says:

```text
Xóa Reader cache của pid — gọi ngay khi reconnect thành công.
```

Reason:
- character structures can move after reconnect/reload;
- stale Reader pointer-chain cache can otherwise survive up to 10 seconds;
- invalidation forces a fresh memory resolve.

So the single-worker success path refreshes character-memory identity before trusting normal automation again.

---

## 11. Post-reconnect memory-ready gate

Daily serializes the exact call arguments:

```text
wait_memory_ready(
    timeout=45.0,
    need=3
)
```

The shared helper defaults are:

```text
timeout = 45.0
need = 3
interval = 1.0
```

Since Daily overrides only timeout and need, effective sampling interval is the shared **1.0 second** default.

A valid sample requires:
- a clear/non-placeholder RoleName;
- MapID not None.

Before each sample the Reader cache is invalidated so the read is fresh.

### Fail-open timeout

Exact shared documentation:

```text
Hết timeout → trả False để caller chạy tiếp như cũ + log
(fail-open, không bao giờ kẹt farm)
```

Daily therefore must not turn the 45-second memory-ready gate into an infinite hard block.

---

## 12. DLL reinjection boundary after reconnect

The single-worker reconnect-local surface proves:
- active-state wait;
- cache invalidation;
- memory-ready gate.

It does **not** directly prove an unconditional post-reconnect `_ensure_injected` call.

Therefore:

```text
forced DLL reinjection immediately after ordinary reconnect
= NOT PROVEN
```

This does not mean injection is ignored forever.

The next recovery movements have their own guarded repair behavior:
- `_punish_heal` tries reinjection before heal movement;
- `_punish_goto_bodau` tries reinjection before NPC movement.

Do not add a new unconditional reconnect injection step merely by analogy with other tools.

---

## 13. Daily reconnect is not Train reconnect

This distinction is important for reconstruction.

### Daily Trừng Ác

Recovered:
- 2s detector;
- memory True veto;
- both dialog pixels;
- 3 consecutive ticks;
- one confirmed reconnect click `(616,455)`;
- bounded reconnect waiting;
- activity-wide exact 60s timeout;
- single-account active wait + cache reset + 45s/3-read memory gate.

Not recovered:
- `/5` reconnect attempts;
- 30-second reconnect-attempt windows;
- 30-second failed-batch sleeps;
- infinite retry batches.

Those belong to Train/TrainLSV and must not be copied into Daily.

---

## 14. Runtime cross-check

Only after static extraction, the exact packaged log was checked:

```text
SHA-256:
17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500
```

Correlated K07 counts are zero for:
- `[TRỪNG ÁC]`;
- `MAT KET NOI`;
- `Chờ kết nối lại`;
- `MemReady`;
- `Địa phủ`;
- `HP 0%`;
- heal-failure text;
- reconnect OK/timeout text;
- the reconnect/revive click coordinate strings.

K07 is therefore static-verified but still requires a real Windows + live game environment for end-to-end runtime parity.
