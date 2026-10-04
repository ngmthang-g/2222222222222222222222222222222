# G10 — Party B0→B3 team protocol

## Inputs

configured member names
→ _resolve_targets
→ live read_own_ids()
→ hwnd_of_pid(pid)
→ targets = (name, hwnd, RoleID)
→ offline/missing-window selections skipped

Runtime identity remains HWND + PID generation from G02.

## B0 — auto accept

for each live target:
→ memory_items.set_auto_fields
   → UTILITIES
   → AutoAcceptInviteTeam
   → bool True
   → live AutoFightSettings + SaveSetting
→ interruptible AUTOSET_DELAY
→ _is_autoset_on / get_auto_settings
   → True: confirmed ON
   → False: warning; manual acceptance may be needed
   → None: readback unavailable

B0 does not fabricate a successful readback.

## B1 — leave current team

for each target:
→ read TeamID
→ 0 / 0xFFFFFFFF?
   → already outside → skip leave
→ otherwise
   → memory_items.leave_team(hwnd)
      → packet 200057
      → TeamAction LeaveTeam=4
      → payload 4:<ownRid>
   → interruptible LEAVE_DELAY

after commands:
→ _wait_team_state(targets, expect_zero=True, WAIT_LEFT_TIMEOUT)
→ TeamID None never counts as success
→ timeout:
   → log snapshot
   → continue protocol anyway

## B2 — leader create team

leader
→ memory_items.create_team(leader_hwnd)
   → packet 200057
   → TeamAction CreateTeam=0
   → payload "0"
→ _wait_team_state(real-team, CREATE_PACKET_TIMEOUT)

real leader TeamID appears?
→ YES: B2 success
→ NO:
   → click fallback, up to symbolic CREATE_RETRY

click fallback:
→ resize leader HWND 1366×768
→ if nguoiChoiGan pixel present:
   → click (391,683)
→ if muiTenAnNhiemVu pixel present:
   → click (34,462)
→ tail:
   → (27,467)
   → (154,214)
   → (127,336)
→ every click separated by 1s
→ cancellation-aware

after fallback attempt:
→ wait real TeamID with WAIT_TEAM_TIMEOUT
→ success: continue
→ no team: log/retry with symbolic INVITE_DELAY
→ exhausted: TẠO THẤT BẠI → skip cluster

## B3 — burst invite

others = every resolved target except leader

initial round:
for each other:
→ memory_items.invite(leader_hwnd, target RoleID, kind='team')
   → packet 200051
   → team prefix 5:
   → payload 5:<targetRoleID>
→ spacing BURST_INVITE_DELAY
   → original doc says ~0.5s

one shared wait:
→ _wait_group_same_team
→ poll GROUP_JOIN_POLL
→ max GROUP_JOIN_TIMEOUT
→ leader must have real TeamID
→ each other must equal leader TeamID
→ returns missing target list
→ cancel returns None

missing empty?
→ YES: complete

missing remains?
→ resend exactly one round to missing only
→ second shared wait

after second wait:
→ all joined: success log
→ still missing:
   → log names + _team_snapshot
   → tell user to check auto-accept/manual popup
   → method still finishes True unless canceled

## Legacy helper

_invite_join
→ send one invite
→ fixed JOIN_WAIT
→ no TeamID verification
→ original docs describe old strategy as 2s per account
→ retained compatibility/retry helper
→ not main B3 path

## Direct Rời nhóm button

Rời nhóm
→ _leave_group_worker
→ resolve live targets
→ skip offline / already outside
→ leave_team per target
→ LEAVE_DELAY
→ log XONG

No final aggregate _wait_team_state is present in this button worker.

## Static numeric boundary

Exact from docs:
- create fallback click gap = 1s
- old sequential invite behavior = 2s/member
- burst spacing documented ~0.5s
- burst rounds = initial + one resend

Exact Party module float pool also contains:
0.3, 0.8, 2.0, 12.0, 0.5, 15.0, 6.0

But exact source assignment of each pooled float to every symbolic timing name is not safely recoverable from the deduplicated Nuitka static blob, so those bindings remain UNKNOWN.
