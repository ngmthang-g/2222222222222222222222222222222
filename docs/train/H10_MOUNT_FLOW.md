# H10 — Train mount / horse flow

## Home priority

UI priority list:
→ Phù 1
→ Phù 2
→ Phù 3
→ Ngựa

_get_nav_priority
→ passes ordered list into move_character

move_character home-return stage:
→ try phù-style methods/hotkeys in order
→ Ngựa is the boundary/sentinel to stop further phù attempts
→ fall through to normal mounted/autopath movement

No dedicated horse hotkey/click is recovered in this priority block.

Exact source syntax around the internal Stop sentinel remains UNKNOWN.

## Mount state model

HasMount
→ equipped mount exists
→ Site 2 / RoleData.Items
→ cached through read_mount_cached
→ MOUNT_CACHE_TTL = 30.0s
→ values 1 / 0 / None

IsRiding
→ live current riding state
→ independent of HasMount

Never collapse HasMount and IsRiding.

## ensure_mounted

ensure_mounted(hwnd, stop_check, stop_auto_first)

if stop requested:
→ fail/exit

fresh IsRiding == 1?
→ return True immediately

if stop_auto_first:
→ set game auto mode None
→ stop-auto failure is logged
→ still continue mount attempt

ensure block contains exact 1.5 constant
→ exact source binding UNKNOWN

consult mount availability/action surface

send internal mount command:
→ memory_items.toggle_mount
→ Game.SendToggleRideState(Game.CurrentMountSlot)

wait exactly 3s

fresh-read IsRiding after cache invalidation

IsRiding == 1?
→ True

otherwise:
→ False

Current path is memory+packet only
→ no pixel/click mount sequence.

## Mid-route remount

move_character polling
→ HasMount available
→ riding lost?
→ _remount_requeue

_remount_requeue:
1. stop_autopath
2. ensure_mounted
3. queue_autopath with same target
4. continue outer poll unless stop requested

Current helper replaces old pixel-click/manual-Reader remount code.

move_character tracks:
→ remount_count
→ max_remount

Exact max_remount numeric:
→ UNKNOWN.

## Dismount

No active Train/shared movement dismount helper recovered.

Teleport/game state may clear IsRiding naturally.
Movement reacts by remounting if needed.

## NPC / route interaction

same map + NPC position known
→ move_to_npc
→ move_character
→ mounted approach
→ arrival poll
→ click NPC

different map OR NPC not spawned
→ game-native fallback
→ exact doc: no horse

mount-before-goto failure
→ log and ignore
→ higher-level fallback can continue

## H05 interaction

FarmTab Truyền route remains owner.

move / move_target legs
→ shared move_character
→ mount/remount can apply

after teleport
→ callers may pass stop_auto_first=False
→ avoid redundant auto-stop

return shortcut failure/walking fallback remains H05 behavior.

Horse is an optimization layer under movement, not a replacement for route state.
