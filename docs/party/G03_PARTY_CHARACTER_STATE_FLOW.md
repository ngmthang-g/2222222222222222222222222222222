# G03 — Party character-state flow

## Identity layers

Physical runtime identity
→ HWND + PID generation
→ G02 bind/unbind protection

Display/config identity
→ utils.get_character_info(hwnd)
→ RoleName
→ remove <...> tags
→ usable name
→ otherwise Window ... placeholder
→ ready list / group Combobox / saved group member names

Action identity
→ selected member name
→ memory_items.read_own_ids()
→ live records shaped as (pid, RoleID, Name, Lv)
→ build exact/lowercase name lookup
→ no matching live name: offline → skip
→ PID present but no current HWND: skip
→ hwnd_of_pid(pid)
→ resolved target = (name, hwnd, rid)

No numeric RoleID sentinel is invented.

## Team-state layer

resolved/current HWND
→ memory_items.read_team_id(hwnd)
→ TeamID

TeamID result:
- 0 = known outside team
- 0xFFFFFFFF = known outside team
- None = read failure / unknown
- otherwise = real team ID

Important:
None != outside-team success.

Wait for outside-team
→ every target must return one of the known no-team sentinels
→ None does not satisfy the wait

Wait for same-team
→ TeamID must be real/non-sentinel
→ compare equality between windows/leader and members

Diagnostic snapshot
→ name=TeamID
→ unreadable TeamID shown as ?

## Ownership boundary

Party direct get_character_info use
→ RoleName only

Party action-state sources
→ RoleID: memory_items.read_own_ids + hwnd_of_pid
→ TeamID: memory_items.read_team_id

Not evidenced as direct Party character-info consumers:
→ CurrentHP / MaxHP / HPPercent
→ Level
→ MapID
→ PosX / PosY

Those shared-reader fields must not be pulled into Party merely because they exist globally.
