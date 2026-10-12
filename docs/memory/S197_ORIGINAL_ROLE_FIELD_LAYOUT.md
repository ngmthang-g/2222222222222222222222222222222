# S197 — Original TLMTool 2.1.2: proven 42-field RoleData layout

**Authority:** user's immutable `TLMTool_2.1.2(20261012-115511).zip`, inner `TLMTool.dist/TLMTool.exe`, SHA256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`. Same frozen binary as O01/O02. **Read-only static bytes**, no EXE, DLL, game or native Windows execution.

## What was actually recovered

- Original compiled Nuitka `.memory_reader` serialized constants module begins at absolute file offset `0x2B7576F`, length `11,804` bytes (O02).
- At payload `+0x1F2B` (EXE `0x2B7769A`), encoded `D*` contains exactly **42 named RoleData fields**; ordered names finish at payload `+0x20CE`.
- Immediately afterward **42 values** are encoded as `T\x02 l<varint byte offset> w<type letter>`; `I` is 32-bit unsigned, `Q` is 64-bit unsigned, and `P` pointer width for this Win64 client. The values finish at payload `+0x21E6`. **Every field below is bound to its corresponding tuple by ordered dictionary serialization**, NOT adjacency speculation.
- A separate original `D1` dictionary at payload `+0x2280` (EXE `0x2B779EF`) contains **49 `read_all` output keys**. These include the original field names and derived `FactionName`, `HasMount`, `MountItemID`, `X_UI/Y_UI`, `AutoFlag/AutoFlag2`. Derived outputs are NOT automatically assigned new `RoleData` memory offsets.

| Original RoleData field | Offset | Original format |
|---|---:|---|
| RoleID | 0x010 | I |
| RoleName | 0x018 | P |
| Sex | 0x020 | I |
| FactionID | 0x024 | I |
| Level | 0x028 | I |
| MapID | 0x050 | I |
| PosX | 0x054 | I |
| PosY | 0x058 | I |
| Exp | 0x060 | Q |
| MaxExp | 0x068 | Q |
| Direction | 0x0A0 | I |
| CurrentHP | 0x0A4 | I |
| MaxHP | 0x0A8 | I |
| CurrentMP | 0x0AC | I |
| MaxMP | 0x0B0 | I |
| CurrentRage | 0x0B4 | I |
| MaxRage | 0x0B8 | I |
| CurrentStrike | 0x0BC | I |
| Money | 0x078 | I |
| BoundMoney | 0x07C | I |
| Token | 0x080 | I |
| BoundToken | 0x084 | I |
| BankMoney | 0x088 | I |
| PKMode | 0x070 | I |
| PKValue | 0x074 | I |
| GuildID | 0x09C | I |
| GuildRank | 0x170 | I |
| TeamID | 0x0E8 | I |
| ServerID | 0x0F8 | I |
| Strength | 0x12C | I |
| Energy | 0x130 | I |
| Stamina | 0x134 | I |
| Intelligence | 0x138 | I |
| Dexterity | 0x13C | I |
| MoveSpeed | 0x100 | I |
| CurrentPetID | 0x140 | I |
| IsRiding | 0x108 | I |
| IsGM | 0x0FC | I |
| CombatRelationship | 0x104 | I |
| QuickSkills | 0x150 | P |
| AutoSettings | 0x158 | P |
| SystemSettings | 0x160 | P |

## What source implements

- **NEW `src/tlm_original_role_fields.py`**: read-only immutable 42-field original dictionary (never editable by runtime callers), widths and exact offsets, `read_original_role_numeric_candidate`, one bounded read per original field, unsigned little-endian shape checks. Reads `RoleID`, `CurrentHP`, `MaxHP`, `MapID`, `TeamID`, `Level`, `RoleName` **pointer only**. Plausibility/identity checks: nonzero role/level/map/maxHP, HP ≤ maxHP, valid canonical aligned role-name pointer, repeated RoleID/MapID/TeamID/name-pointer must match before accepting numeric candidate. A candidate does not produce RoleName text or authorize game control.
- **UPDATED `src/tlm_original_memory_reader_native.py`**: S196 Win64 read-only original role pointer+anchored SessionData diagnostic now calls this S197 decoder after client SHA256, native HWND/PID, GameAssembly/UnityPlayer PE and pointer/SessionData checks. Rechecks RoleData pointer+SessionData anchor+selected process image after numeric reading. Returns candidate data **only as nested diagnostic**, with all root `role_name_read/hp_read/map_id_read/gameplay_authorized` fields still FALSE — no accidental promotion to Party/Train or UI. This remains `SOURCE_IMPLEMENTED_UNTESTED`.

## IMPORTANT boundary

- The 42 field offsets are original TLM EXE **static, exactly source-bound**. Their actual compatibility with a running game/client process is STILL **NOT VERIFIED**. Actual `RoleData` pointer traversal, Lua/IL2CPP object lifetime, fields changing during combat, and Win32 reads require final owner game acceptance. Static offsets are **not** automatic proof the game logged in.
- Original `_rstr` references UTF-16-LE; the pointer at `RoleData+0x18` is now exactly identified, but this task does **not** invent or assert the unverified string object header/length/character offsets. RoleName string decoding remains the next source task, fail-closed.
- The original 49 `read_all` fields include derived or additional reads, so do not confuse its count with 42 memory field offsets.
- No intermediate unit/CI/native Windows/live game/EXE tests; no `PLAN.md`, `SCOPE_LOCK.md`, original ZIP/EXE, DATA-2222 edits. Historical S176 last verified Win64 artifact, staged S177–S197 `SOURCE_IMPLEMENTED_UNTESTED`.
