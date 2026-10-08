# L08 — Dồn death / treatment / disconnect flow

## Authority

The exact frozen specimen was revalidated before screenshot/runtime use:

- archive SHA-256: c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd
- archive size: **93,715,901 bytes**
- ZIP entries: **1,050**
- CRC clean
- inner EXE SHA-256: 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22
- inner EXE size: **47,450,112 bytes**
- active Dồn authority: donvang_tab.py / DonVangTab

L02-L07 contracts remain unchanged.

## Visible controls and legacy config naming

Current Dồn UI exposes:
- Quay lại train khi chết
- Dừng khi mất kết nối mạng
- Trị liệu sau khi chết
- Tọa độ trị liệu

Internal/config mapping:
- respawn_var -> [DonVang] respawn
- auto_reconnect_var -> [DonVang] auto_reconnect
- trist_var -> [DonVang] trist
- heal_map_var -> [DonVang] heal_map

The compatibility trap is auto_reconnect. In the current Dồn build it does **not** mean auto reconnect. The visible behavior is stop when network disconnect is confirmed.

## Death monitor

Both receiver and donor full sessions start _diaphu_monitor.

Exact monitor contract:
- every 4 seconds, read character info;
- MapID == 87 sets respawn_event once per continuous map-87 episode and arms detected;
- leaving MapID 87 re-arms detected;
- a real numeric HpPercent == 0 triggers one client click at (792,441);
- hp_latched prevents repeated clicks while HP remains zero;
- readable nonzero HP re-arms hp_latched;
- unreadable HP is not reinterpreted as zero.

MapID 87 and HP 0 serve different purposes:
- MapID 87 raises recovery intent;
- HP 0 performs the actual one-shot respawn click.

The map latch remains armed until the character leaves map 87, preventing repeated recovery events while moving out of Địa phủ.

## Receiver death handling

Receiver session consumes respawn_event:
1. log “acc nhận đang ở Địa phủ → hồi sinh”;
2. optionally call _heal_at_death when treatment is enabled;
3. return to the receiver lifecycle unless stop/halt/other failure ends the worker.

The receiver runner has no Train-target movement surface. A receiver is not turned into a donor or sent to its Train preset by the death event.

## Donor death handling

Donor _farm_cycle consumes the same respawn_event and exposes “đang ở Địa phủ → hồi sinh”.

The checkbox Quay lại train khi chết is persisted as respawn.

Important parity boundary:
- the HP0 monitor click is not this checkbox's job;
- respawn is a post-death return/relocation policy;
- exact donor continuation when the option is unchecked is not source-visible enough to freeze and remains explicit UNKNOWN.

## Treatment routing

When Trị liệu sau khi chết is enabled, Dồn calls _heal_at_death(hwnd, stop_check).

Destination can be one of the shared built-ins or a manual saved-coordinate preset.

Exact shared built-ins:

| Destination | MapID | X | Y |
|---|---:|---:|---:|
| Trị liệu Đại Lý | 2 | 43 | 178 |
| Trị liệu Lạc Dương | 3 | 255 | 126 |
| Trị liệu Tô Châu | 4 | 155 | 252 |
| Trị liệu Lâu Lan | 5 | 294 | 170 |

Resolution failure cases:
- empty selection;
- invalid built-in MapID;
- missing built-in coordinate;
- unresolved manual preset;
- movement failure;
- stop/cancel.

Movement uses shared move_character.

## Treatment interaction

After reaching the destination, Dồn carries the same frozen treatment interaction contract:
- click (892,474);
- click (514,424);
- repeat the two-point sequence ×4.

The Dồn function's embedded documentation says:
“Trị liệu sau khi chết: di chuyển tới map trị liệu + click 2 điểm x4 lần.”

The same function exposes the common/active readiness pair. An exact 0.2 pacing constant belongs to this treatment interaction family, but its exact call-argument binding remains UNKNOWN.

Successful treatment returns success. Failure surfaces “trị liệu sau chết thất bại”; the exact caller branch after failure remains UNKNOWN.

## Disconnect watchdog

Both receiver and donor sessions start _disconnect_monitor.

Dồn's watchdog is intentionally **not** ordinary Train's auto-reconnect loop.

Every 2 seconds:
- if connection memory is definitely True, reset/veto the disconnect strike chain;
- otherwise require both disconnect pixels;
- require 3 consecutive matching ticks, approximately 6 seconds.

Exact shared probes:
- login.ngatKetNoi1: point (640,244), RGB (160,145,52), tolerance 5;
- login.ngatKetNoi2: point (702,453), RGB (212,28,34), tolerance 5.

Memory source is TCPGame.Instance.tcpClient.Connected. Memory False/None alone is not enough; persistent dual-pixel evidence is still required.

## 3/3 disconnect result

On the third consecutive dual-pixel hit:
- log MAT KET NOI (dialog 3/3);
- set halt / stop the character and hard-stop-aware subflows;
- receiver path says “mất kết nối → dừng acc nhận”;
- donor path says “mất kết nối → dừng acc”;
- the full account session finishes stopped.

If a donor drops during active Dồn, the L06 receiver abort/reset path prevents that receiver from waiting forever.

## No reconnect in Dồn

This is the most important L08 correction.

Dồn _disconnect_monitor contains halt, stop_character, is_connected, the two disconnect pixel keys and dc_strikes.

It does **not** contain:
- reconnect_ok;
- reconnect click (616,455);
- wait_pixel(common.active) reconnect attempts;
- 5-attempt reconnect batches;
- 30-second retry batches;
- an infinite reconnect loop.

The EXE's own embedded documentation states:
“KHÔNG tự kết nối lại — user bấm Start để chạy lại.”

Therefore reconstruction must preserve the legacy config key auto_reconnect while implementing the current **stop-on-disconnect** semantics. Do not import ordinary Train's reconnect loop into Dồn.

## Disconnect monitor exit boundary

The Dồn monitor documentation says it exits when:
- user/session stops;
- account leaves _farming_acc;
- generation changes;
- the real window/process dies;
- Dừng khi mất kết nối mạng is turned off.

No reconnect resume is performed.

A live re-enable after the monitor has already exited is not separately proven to recreate the monitor thread; no hot re-arm is assumed.

## Death + disconnect overlap

Death treatment/movement uses hard_stop. Confirmed disconnect asserts halt.

Once halt is visible, hard-stop-aware movement/treatment/Dồn subflows are interruptible and the account exits rather than completing recovery.

Exact ordering when death detection and the third disconnect strike occur in the same scheduling window remains runtime-required.

## Captured UI

Screenshot SHA-256:
dffb4da895d21dea87dd72a6601c29104f519dca89c2f716f5a7445bcbe4421a

After static extraction, the capture shows:
- Quay lại train khi chết: unchecked;
- Dừng khi mất kết nối mạng: unchecked;
- Trị liệu sau khi chết: unchecked;
- Tự gỡ kẹt: checked;
- treatment destination: Trị liệu Tô Châu.

These are captured config/runtime values, not asserted universal first-install defaults.

## Existing runtime log

Frozen automove_log.txt:
- SHA-256 17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500
- **387,238 lines**

Correlated L08 markers are all 0:
- [HP Monitor]
- MAT KET NOI
- [Donvang]
- Địa phủ
- trị liệu sau chết thất bại
- mất kết nối
- [Trị liệu]

Classification: **STATIC_VERIFIED / LIVE_RUNTIME_PARITY_REQUIRED**.

## L08 boundary

Resolved:
- 4s death monitor;
- MapID87 recovery event;
- HP0 one-click latch;
- receiver-vs-donor recovery integration;
- shared treatment route and interaction;
- current disconnect-control semantics;
- 2s memory-veto + dual-pixel 3-strike detection;
- stop-on-disconnect behavior;
- decisive no-auto-reconnect boundary.

Deferred:
- unchecked donor return-to-train continuation;
- treatment failure next branch;
- first monitor tick immediate-vs-after-4s;
- exact is_trade_active conditional role inside disconnect monitor;
- same-tick death/disconnect ordering;
- live timing/race parity.
