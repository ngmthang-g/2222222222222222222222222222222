# G02 — Party HWND / ready-list refresh flow

## Upstream discovery ownership

Start subsystem background producer
→ EnumWindows / visible-game filtering
→ safe title + process/class checks
→ cached list of game `(hwnd, title)`
→ producer cadence about 3s (C01)

Party does **not** duplicate EnumWindows.

## Party refresh lifecycle

Party constructor
→ `_start_refresh`
→ Party refresh lifecycle active

Recurring Party tick
→ `_refresh_acc_list`
→ daemon background `_worker`
→ `start_tab.get_windows()` reads shared cached list
→ for each active HWND:
   → resolve PID / read `utils.get_character_info(hwnd)`
   → collect worker `infos`
→ Tk `after` handoff
→ main-thread `_apply`
   → `_add_or_update_member(hwnd, ci)`
   → `_remove_stale_members(active_hwnds)`
   → `_apply_group_permission`
   → `_schedule_refresh`

Party recurring schedule:
→ encoded interval = 3000 ms
→ next Party refresh in 3s

Exact first-tick timing after initial `_start_refresh`: UNKNOWN.
Exact delay on worker→Tk `after` handoff: UNKNOWN.

## Member identity

New/current HWND
→ `_pid_of(hwnd)`
→ PID generation snapshot
→ `bind_window_identity(hwnd, pid)`
→ Party member row keyed by HWND
→ shared character info
→ sanitized RoleName when available

Temporary no-name case
→ `Window ...` placeholder
→ exact suffix UNKNOWN
→ later real RoleName updates display name

Same HWND + same PID
→ retain row
→ update name/info as current data becomes available

Same HWND + different PID
→ direct Party log: HWND đổi process
→ old numeric handle belongs to a new process generation
→ unbind old HWND/PID identity
→ destroy old member row/widget
→ refresh group choices
→ create/bind fresh member generation

HWND absent from current active set
→ `_remove_stale_members(active_hwnds)`
→ unbind stale identity
→ destroy row
→ live ready/group choices no longer contain that member

## Ready list and groups

Live Party members
→ `_ready_names`
→ ready-list relayout
   → 3 acc per row
   → hide acc already chosen by a group

Group combobox refresh
→ start from live ready names
→ keep each current selected value where possible
→ selections used by earlier cluster are unavailable to later cluster
→ update all leader labels

## Safety meaning

The shared identity layer makes the action target:
`HWND + PID generation`, not numeric HWND alone.

If Windows reuses a handle value for a different process, the stale Party row is replaced and later actions cannot safely inherit the old target binding.
