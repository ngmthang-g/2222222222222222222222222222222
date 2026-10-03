# C02 — HWND ↔ character identity flow

## Runtime identity layers

```text
HWND
↓
_get_pid_from_hwnd(HWND)
↓
PID snapshot
↓
bind_window_identity(HWND, PID)
↓
get_character_info(HWND)
↓
shared Reader cache[PID]
↓
Reader.read_all()
↓
_format_char_info
↓
RoleName / HpPercent / Level / MapID / PosX / PosY / ...
```

## Key ownership

| Purpose | Stable/keyed by |
|---|---|
| Current GUI/account row | HWND |
| Anti-HWND-reuse generation | PID snapshot |
| Memory Reader cache | PID |
| Logical character label | sanitized RoleName |
| Persistent per-character config | RoleName/character name |
| Start preview physical source | src HWND |
| Start preview character data | worker info cache |

## Lifecycle

```text
new HWND
→ PID snapshot
→ bind HWND→PID
→ read memory
→ create row

real RoleName unavailable
→ temporary Window... label

later RoleName available
→ update same HWND row label

same HWND + same PID
→ keep/update row

same numeric HWND + different PID
→ treat as reused HWND
→ remove old row
→ unbind old PID snapshot
→ destroy old widgets/state
→ create fresh row for new process

window closed
→ remove stale row

successful reconnect
→ invalidate Reader cache(PID)
→ fresh pointer-chain resolution on next read
```

## Action safety

`mouse._identity_matches` protects background actions from an HWND that has been reused by another process.

The strict action resolver refuses to click when:
- HWND no longer exists; or
- current PID does not match the stored snapshot.

## Persistence

HWND is intentionally not used as a persistent account key.

Original Tối ưu code states that HWND changes each time the game is opened, therefore settings are restored by character name. Rao and farm-family tabs use the same character-name persistence pattern.
