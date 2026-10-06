# J03 — Phó Bản follower / “Theo sau đội trưởng” flow

## Config / toggle

follow_var
→ visible “Theo sau đội trưởng”
→ config key phoban_follow
→ clean default OFF.

toggle ON:
→ if any group currently running:
   → start follow worker now
→ else:
   → keep mode ON
   → log waiting for a schedule run

toggle OFF:
→ stop worker immediately

every worker cycle:
→ re-check tick state.

## Worker lifecycle

constructor:
→ _follow_stop
→ _follow_thread
→ _follow_gen

_start_follow:
→ existing is_alive guard
→ generation/session protection
→ Thread(target=_follow_worker, args=(gen,), daemon=<exact value not instruction-bound>)

_follow_worker(gen):
→ exits if tick OFF
→ exits if generation stale
→ exits if no group remains running
→ later run start may create a new worker

saved checkbox remains ON unless user unticks it.

## Group filter

_group_is_running(gd):
→ True only if group run cancel exists and is not set

_idle configured group:
→ no position reads
→ no follow movement.

## Group members

leader source:
→ first combobox

followers:
→ remaining member slots
→ frozen slice(1,None,None)

blank/offline follower:
→ no usable HWND/position
→ no command.

## Position source

nested _pos(hwnd):
→ get_character_info(hwnd)
→ read MapID
→ read PosX
→ read PosY

all follow decisions are memory-position based.

Frozen 32.0 and 0.5 constants occur in position/distance logic.
Exact native arithmetic expression:
→ UNKNOWN.

## Allowed maps

dungeon_maps:
→ derived from DUNGEON_MAP_IDS

leader outside allowed dungeon maps:
→ do not follow this group
→ clear stale position/command cache

leader re-enters:
→ follow may resume cleanly.

special exclusion:
→ Sát Tinh / map 111
→ NEVER follow
→ frozen reason: accounts anchor at 65,85 and auto-fight.

## Same-map gate

for each follower:
→ read current follower position
→ require follower MapID == leader MapID
→ otherwise skip.

## Distance gate

compute leader/follower separation in tile semantics

if distance <= PB_FOLLOW_DIST_TILES:
→ no move

if distance > PB_FOLLOW_DIST_TILES:
→ evaluate command-clash guards.

Numeric PB_FOLLOW_DIST_TILES:
→ UNKNOWN.

## Command-clash guard A — foreign movement delta

cache:
→ last_pos
→ commanded
→ commanded_now

if follower moved > PB_FOLLOW_MOVE_TILES since prior poll
AND follower was not follow-commanded on prior poll:
→ treat as another subsystem moving/combat-driving the account
→ skip this poll.

prior follow command:
→ exempts its own movement from being called “foreign”.

Numeric PB_FOLLOW_MOVE_TILES:
→ UNKNOWN.

## Command-clash guard B — shared move poll

call:
→ is_move_poll_active(follower_hwnd)

shared exact semantics:
→ True while a move_character wait_for_arrival controller is still actively steering that HWND

shared exact TTL:
→ 0.5 seconds

if active:
→ do not queue follow
→ avoid stealing the movement command.

## Follow movement

shared helper:
→ move_character

explicit call keyword surface:
→ wait_for_arrival
→ stop_check
→ follow_mode

effective frozen behavior:
→ wait_for_arrival=False
→ follow_mode=True
→ stop_check belongs to this follow worker/session

follow_mode semantics:
→ queue AutoPath only
→ no Phù
→ no stop game auto
→ no mount toggle
→ keep auto FuBen active.

successful command:
→ add follower to commanded_now
→ log follower bám theo leader with distance.

Exact cache mutation statement order:
→ UNKNOWN.

## Periodic loop

repeat every PB_FOLLOW_POLL seconds:
→ tick state
→ generation/session
→ any running group
→ each running group
→ leader position
→ dungeon-map gate
→ each follower
→ same-map gate
→ distance
→ conflict guards
→ queue move if safe

Numeric PB_FOLLOW_POLL:
→ UNKNOWN.

## Error handling

per follower:
→ “bám lỗi”

outer loop:
→ “[Phó bản] follow lỗi”

No frozen contract says a follow exception aborts the whole schedule.

## Runtime evidence

packaged automove_log:
→ 0 correlated follow markers

generic movement primitives exist:
→ AutoMove queued 16040 lines
→ StartAutoPath called 15993
→ StopAutoPath called 2027

scope:
→ primitive only
→ not proof of PhoBanTab follow.

classification:
→ STATIC_VERIFIED / RUNTIME_ENV_REQUIRED.

## Next

J04:
→ Phó Bản schedule model / schedule-row execution audit.
