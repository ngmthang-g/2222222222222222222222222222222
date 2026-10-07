# K08 — Trừng Ác discard worker / equipment filtering flow

## 1. Separate background subsystem

Trừng Ác discard is not one step inside a single punish execution cycle.

Daily owns separate state:
punish_discard_equip_var, _punish_discard_stop, _punish_discard_thread, and _punish_discard_gen.

The worker lives at the Trừng Ác run/session level and periodically scans accounts that are currently running Trừng Ác. It can therefore span multiple ordinary quest/combat cycles.

## 2. Checkbox/config lifecycle

Visible control:
Lọc trang bị (vứt vũ khí, trang bị trong quá trình làm nhiệm vụ)

Persisted key:
daily_punish_discard_equip

Load fallback:
"0"

B08 captured state is OFF.

Exact frozen toggle documentation says:
- ON + a running Trừng Ác account → create the worker immediately.
- ON + nothing running → wait; a later account start creates the worker.
- OFF → stop the worker immediately.
- Worker rechecks the tick every cycle; untick during a run exits.
- Save config.

So the enabled setting may remain armed while no worker exists, then be reactivated by a later Trừng Ác start.

## 3. Account scope

Exact _punish_running_hwnds documentation says it returns HWNDs of accounts currently running Trừng Ác, excluding stopped/disconnected accounts.

Discard therefore does not scan every visible game window.

## 4. Periodic worker and parallel accounts

Exact worker documentation says every DAILY_DISCARD_POLL seconds it discards in parallel for all currently-running Trừng Ác accounts, with one thread per account. It explicitly states packet pacing is 1 second per account, because serializing all accounts would bottleneck.

The numeric value of DAILY_DISCARD_POLL is not safely bound by current static evidence and remains UNKNOWN.

Flow:

periodic worker tick
→ obtain current running Trừng Ác HWNDs
→ for each eligible HWND:
  - if its prior discard pass is still inflight, skip this account for this tick;
  - otherwise start one child thread calling _punish_discard_one.

Different accounts can therefore discard in parallel while one account remains sequential internally.

## 5. Inflight protection

Worker locals contain inflight and started.

Exact worker documentation says an account whose previous discard has not finished is skipped for the current tick, so passes do not overlap.

A slow account must not accumulate multiple simultaneous discard passes.

## 6. Generation/thread protection

Persistent state includes _punish_discard_gen, and the worker captures local gen.

This proves a generation-aware stale-worker boundary exists.

The exact source-level ordering of generation increment, stop Event replacement, thread replacement, and old-thread exit is not native-instruction-bound. K08 therefore preserves the generation concept without inventing statement order.

## 7. Exact shared helper call

Each account uses bag_filter.discard_for_activity with:
- activity = daily
- keys = [discard_equip]
- keyword surface = keys, delay, stop_check

Exact Daily worker documentation says:
Preset = daily discard_equip, all non-weapon equipment plus weapons, same equipment semantics as Phó Bản.

This is therefore not a keep-weapons mode.

## 8. Shared bag_filter contract

Exact bag_filter documentation says:
- default is discard nothing;
- empty rules return zero and send no packet;
- presets are opt-in by key;
- combining presets ORs the rules and deduplicates by dbID.

Rule semantics:
- Site 10 is the default bag site.
- Fields inside one rule are AND.
- Multiple rules are OR.
- Supported selectors include item_ids, name_contains, equip_types, src, match_weapons, allow_weapons, protect_ids, and protect_names.
- Weapons are protected by default unless an explicit weapon rule permits/matches them.
- Protected IDs/names have highest priority.

Daily discard_equip deliberately includes the explicit weapon behavior.

## 9. Metadata degradation

Exact bag_filter warning says that if embedded/item metadata is empty, non-weapon matching falls out and only weapon-ID discard remains.

Thus:
- non-weapon equipment depends on embedded metadata Source/EquipType;
- weapon matching has the weapon-ID / is_weapon path.

Parity work must not silently replace this behavior with a new heuristic.

## 10. Internal packet action

Shared discard ultimately calls memory_items.abandon_item(hwnd, dbID).

Frozen packet contract:
- command 100005
- action 4
- payload 4:<dbID>

Exact documentation states that discard removes the whole stack in that slot.

This is an internal dbID packet action, not visible bag GUI clicking.

## 11. Pacing and stop behavior

bag_filter.discard_items exact defaults:
- delay = 1.0
- stop_check = None
- on_progress = None
- dry_run = False

discard_for_activity also defaults to delay = 1.0.

Daily worker documentation independently states 1-second packet pacing.

Daily passes stop_check. Shared documentation says a true stop_check stops early, so turning the feature off or stopping its owner can interrupt a long pass between item actions.

## 12. Shared per-HWND send lock

bag_filter owns _SEND_LOCKS_GUARD, _SEND_LOCKS and _send_lock_for.

This is a per-HWND packet-serialization surface.

Daily also has its own inflight guard. Preserve both layers: one blocks repeated Daily passes for an account, the shared lock protects packet sending at the lower shared-filter layer.

## 13. Retry behavior

No dedicated retry or attempt counter is recovered for a failed action-4 target.

Strongest contract:
- one pass records total/ok/fail/skipped/stopped/targets;
- the pass returns;
- a later periodic Daily rescan can encounter remaining items again if they are still present.

Do not add an immediate hidden multi-retry loop.

## 14. Failure scope

_punish_discard_one logs either result counts or an account-local error.

Each eligible account runs in a separate child thread, so a failure in one child is fail-soft/account-local and does not require cancelling other account children.

The worker also has a top-level error text. Exact continue-vs-exit micro-order after an unexpected worker-level outer exception remains UNKNOWN.

## 15. Run-scoped, not cycle-scoped

Lifecycle:

Trừng Ác session starts
→ if discard setting is armed, create discard worker
→ worker continues while eligible Trừng Ác accounts exist
→ outer quest/combat cycles can repeat underneath it
→ when the last eligible account stops/disconnects, the discard worker no longer lives
→ the checkbox/config may remain enabled
→ a future Trừng Ác start can create a new worker

Do not place discard once at the end of every punish execution sequence.

## 16. Runtime evidence boundary

Packaged automove_log.txt contains:
- 22,734 generic action=4 records total;
- 22,732 ItemAction spts sent action=4;
- 2 plain ItemAction sent action=4.

It contains zero correlated markers for:
[Trừng ác], lọc trang bị, DAILY_DISCARD_POLL, discard_for_activity, or discard_equip.

So the low-level action-4 primitive has real packaged runtime evidence, but those lines cannot be attributed specifically to the Daily K08 worker.

K08 remains STATIC_VERIFIED / END_TO_END_RUNTIME_ENV_REQUIRED.
