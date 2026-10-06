# J01 — Phó Bản party-formation flow

## Ready-account pool

start_tab.get_windows
→ background character-info reads
→ main-thread UI apply
→ refresh every 5 seconds
→ HWND + current PID identity

closed/reused HWND
→ remove stale ready member

selected into any group
→ hide from ready grid
→ remove from later-group dropdown choices.

## One group

_add_group_cluster
→ leader label
→ six account comboboxes
→ B07: 2 rows × 3
→ first combobox = nominal leader
→ delete-group button
→ schedule body (deferred)

empty first slot
→ leader label "(chưa chọn)".

selection
→ _on_group_selected
→ refresh all group combo values
→ update leader labels
→ save.

## Recreate-team option

Tạo lại đội
→ recreate_team_var
→ config phoban_recreate_team
→ clean default OFF.

OFF
→ tool group definition does not recreate game party.

ON at group-run start
→ _pb_ensure_party
→ must finish before schedule setup.

## Formation targets

_group_targets
→ selected + currently online [(name, hwnd)]

_pb_resolve_targets
→ read_own_ids + hwnd_of_pid
→ exact-name lookup
→ case-insensitive fallback
→ output [(name, hwnd, RoleID)]

one unresolved RoleID
→ skip that member + log

zero resolved RoleIDs
→ abort group.

## Leader choice for recreation

nominal leader
→ first combobox

nominal leader offline
→ first online target becomes effective recreate-team leader

one online member only
→ no team creation
→ allow group to continue.

## TeamID validity

no-team integers
→ 0
→ -1
→ 4294967295

text no-team forms
→ "0"
→ "false"
→ ""

read failure None
→ never counts as successful state.

## B0 — auto accept

attempt/verify
→ UTILITIES.AutoAcceptInviteTeam=True

possible logs
→ confirmed ON
→ warning manual acceptance
→ unreadable readback
→ write error.

exact low-level writer
→ UNKNOWN.

## B1 — leave old teams

each target:
→ already outside team: skip leave
→ otherwise leave_team

then:
→ _pb_wait_team_state(expect_zero)
→ wait all outside team

timeout incomplete:
→ warning
→ STILL CONTINUE.

## B2 — leader creates team via UI

resize effective leader
→ 1366×768

if donVang.nguoiChoiGan pixel present
→ click (391,683)
else
→ skip that click

if donVang.muiTenAnNhiemVu pixel present
→ click (34,462)
else
→ skip that click

tail clicks:
→ (27,467)
→ (154,214)
→ (127,336)

exact documentation:
→ every click 1 second apart.

_pb_invite_create
→ repeat up to PB_PARTY_CREATE_RETRY
→ after each create attempt wait for a real TeamID
→ exhausted retries abort group.

numeric retry/timeout constants:
→ UNKNOWN.

## B3 — burst invite

others
→ resolved non-leader members

initial burst
→ invite all
→ spacing PB_PARTY_BURST_DELAY

wait
→ all others same real TeamID as leader
→ max PB_PARTY_JOIN_TIMEOUT

still missing
→ resend only missing members once
→ wait one additional time

still missing after second wait
→ log missing members + team snapshot
→ helper still succeeds unless cancelled.

## Cancellation

_pb_party_cancelled
→ group cancel OR global cancel

_pb_party_sleep
→ interruptible sleep

cancel during formation
→ abort group formation path.

## Runtime evidence

packaged automove_log
→ no correlated recreate-team trace

RoleID literal lines
→ unrelated private-chat scripts

classification
→ STATIC_VERIFIED / RUNTIME_ENV_REQUIRED.

## Next

J02
→ deeper leader semantics/responsibility only.
