# I05 — Train LSV timed-key schedule flow

## Configuration layer

TrainLSV tab
→ _buff_rows
→ fixed _da_minh_chau_row
→ dynamic user-added rows

row model:
→ enabled_var
→ key_var
→ min_var
→ sec_var
→ fixed

allowed keys:
→ F1-F10
→ 1,2,3

clean _add_buff_row defaults:
→ enabled=False
→ key='1'
→ minutes='0'
→ seconds='5'
→ fixed=False

fixed Dạ Minh Châu:
→ _add_buff_row(fixed=True)
→ enabled_var=True
→ no checkbox
→ no delete
→ key 1 / 0m5s clean defaults.

## Farm session immediate Dạ Minh Châu

Farm cycle starts account
→ _start_extra_track
→ _trigger_da_minh_chau(... wait mode used by Farm cycle)

_trigger_da_minh_chau
→ read fixed Dạ Minh row/key
→ get_character_info(hwnd)
→ read IsRiding

if IsRiding == 0:
→ no dismount

if IsRiding == 1:
→ check common.nguaActive
→ if nguaActive=False:
   → click (1306,340)
→ click (906,688), delay=0 path
→ do NOT use removed clicks (1131,121)/(1073,123)

then:
→ keyboard.press_single_key_dll
→ target = account HWND
→ key = fixed row key
→ delay=0
→ sync=True.

Result:
→ immediate activation once at Farm start.

## Hidden key transport

press_single_key_dll
→ exact target HWND/title resolver
→ resolve key to VK
→ PostMessage
→ WM_MY_SYNC_KEY
→ packed DOWN/UP
→ version.dll hook/intercept
→ real game input in target process

No physical/global keyboard is required.

## Repeating worker

Farm cycle
→ create buff_stop Event
→ create buff_thread for that account
→ _buff_loop(hwnd, buff_stop, row, gen)

_buff_loop:
→ generation/account-running guard
→ iterate configured buff rows
→ inspect enabled/key/minutes/seconds
→ compute interval
→ track deadline
→ when due, call press_single_key_dll for this HWND
→ catch/log per-key send error
→ continue until stop/generation invalidation.

Exact multi-row deadline scheduling:
→ UNKNOWN

Exact zero-interval handling:
→ UNKNOWN

Exact repeating call delay/sync/retry overrides:
→ UNKNOWN.

## Session cancellation

if account stops Farm
OR generation changes:
→ old _buff_loop exits
→ prevents stale-session key sends.

buff_stop/buff_thread are session-owned.

Exact daemon/join ordering:
→ UNKNOWN.

## Persistence

save:
→ buff_<n>
→ enabled|key|minutes|seconds

load:
→ select/sort buff_* keys
→ split('|')
→ recreate row with enabled/key/minutes/seconds

fixed-row exact config index:
→ UNKNOWN.

## Runtime evidence

packaged automove_log:
→ no Dạ Minh / [Buff] / press_single_key_dll / WM_MY_SYNC_KEY correlated lines

classification:
→ STATIC_VERIFIED.

## Next

I06:
→ Train LSV item pickup/filter execution.
