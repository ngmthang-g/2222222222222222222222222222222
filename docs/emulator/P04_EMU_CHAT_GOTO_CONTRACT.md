# P04 — Original EmuChat chat-link navigation, calibrated UI clicks, memory arrival proof

## 0. Authority and task boundaries
- **Starting point**: user asked CONTINUE. Read current GitHub `PLAN.md`, `STATE.md`, `PROJECT_STATUS.md`, P03/P02/P01 and D07. `docs/tasks/P04.md` was **404/absent**, so do not repeat P01–P03.
- **Locked original**: user-supplied `TLMTool_2.1.2(10).zip`, SHA256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, 1050 entries and CRC PASS. Inner `TLMTool.dist/TLMTool.exe` is 47450112 bytes, SHA256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`. Shipped `emu_client.js` SHA256 `384ccee9a2ddf236db377fca3abd36cbc17df81a94a286551a749a3132d02db1`.
- **Evidence**: directly inspected compiled Nuitka EXE byte strings and offsets, unpacked original Frida JS, plus preexisting GitHub reports. No TLM.exe/game/ADB/Frida/live Windows executed.
- **Module marker direction**: exact `<module emu_chat>` begins at **0x293100c** (prefix `u` at 0x293100b); preceding `0x2930abd..0x293100b` contains EmuChat module constants/docs, and after the marker are function-local variable/closure names until the adjacent farm tab begins `0x293110b`. Serialized constants cannot be treated as original Python AST or exact run order.

## 1. Two paths: high-level goto versus primitive UI clicks

### EmuChat public behavior (exact embedded original description, 0x2930d43–0x2930f23)
- Move the selected emulator serial's game character to a target **(map, tile_x, tile_y)** by clicking the game's *own chat coordinate link*, not writing memory or injecting a game command from EmuChat.
- **Early arrival**: when character already at destination within **2 tiles**, success immediately and *do not spam chat*. Literal `ARRIVE_TILES` is present at 0x2930fe4; exact distance formula (`L∞`, Euclidean, Manhattan, x/y separately) is **UNKNOWN**.
- Primitive sequence (literal EXE documentation): **open chat panel → focus input → clear existing text → enter `@GOTO_m_x_y` (tile coords) → dismiss Android keyboard → send → tap own newly sent chat link (newest row) → verify with character memory**. Presence of `AdbInput.tap`, `AdbInput.key`, `AdbInput.text` is static proof of intended inputs, *not proof that these commands all succeed*.
- `goto()` documented result `(ok: bool, msg: str)`. Original description says verify through memory while moving/changing maps (glide/đổi map), **stuck after 30 seconds → fail**, plus timeout error path. Actual default total timeout parameter/loop interval/poll count and exact definition of movement are not source-recovered. Unknown whether the 30s stuck clock starts immediately after link tap, first successful position read, or last actual movement.
- Original strings include `tuda o dich` (already there), `tap loi:` (tap error), `toi (...)` (arrived), `stuck tai (...)` and `timeout tai`. These are branch-report strings, *not* runtime logs from a successful run.

### Compiled callable clues
- `goto` original callable label appears near 0x2930ff7; `emu_chat.py` 0x2930ffe.
- `_pos_of` method at 0x2930bda, with `emu_reader.emu_manager.poll_rows` and keys `MapID`, `PosX`, `PosY` (0x2930b6d–0x2930bda). Source AST is unavailable: do not invent branch sequencing or a new memory-reader mechanism.
- `_chat_xy` 0x2930bf5 for calibrated screen locations. Private argument names `serial`, `map_id`, `tx`, `ty`, `timeout`, `adb`, `last_move`, `start_map`, `last` follow at 0x293104f–0x29310ec and support a stateful polling model. They do **not** tell us the actual clock arithmetic.

## 2. Exact UI coordinate calibration contract

The EmuChat constants read the **`settings.ini` `[EmuChat]`** section (0x2930acd–0x2930b2b; 0x2930edb). The debug Android tab is the user-facing calibration workbench and documents the same section at 0x290d7f4.

| Action | Explicit setting names | Compiled fallback label | Evidence |
|---|---|---|---|
| Open chat panel | `chat_open_x`, `chat_open_y` | `CHAT_PREVIEW` | 0x2930bff–0x2930c27 |
| Focus input | `input_x`, `input_y` | `INPUT_ROW` | 0x2930c27–0x2930c44 |
| Dismiss keyboard / OK | `kb_ok_x`, `kb_ok_y` | `KB_OK` | 0x2930c44–0x2930c5d |
| Send message | `send_x`, `send_y` | `SEND_BTN` | 0x2930c5d–0x2930c77 |
| Tap newly sent link | `link_x`, `link_y` | `LINK_X`, `LINK_Y` | 0x2930c77–0x2930c97 |

- The original doc states defaults are based on the developer's manually mapped PC diagram. **No numeric default values were proven from the compiled string evidence**; do not invent them or treat any screenshot coordinate as universally valid.
- `DebugAndroidTab._save_cfg` and compiled `_settings_lock`, `read_settings`, `write_settings` appear at 0x290d889–0x290db27. Debug UI variable labels include `chat_open_x/y`, `input_x/y`, `send_x/y`, `kb_ok_x/y`, `link_x/y`, `goto_map/x/y` at 0x290d932–0x290d9a2. Calibration is explicit; neither global *nor per-device* persistence semantics of every EmuChat setting are demonstrated.
- P03 established a separate `from_pc` PC-reference-to-ADB-device conversion and Debug Android's Windows `GetCursorPos`/`ScreenToClient` viewport conversion. **Do not mix saved device tap positions with map tile positions or Windows client pixels.** Correctness under changed resolution, keyboard state, chat scrolling and screen rotation is a future live test.

## 3. Coordinate-unit boundary: tile target versus memory data

- EmuChat goto declares input as **`tile_x`, `tile_y`** and emits `@GOTO_m_x_y` for the game's clickable chat-link system.
- `emu_reader` via Frida script `emu_client.js` supplies live `MapID`, `PosX`, `PosY` and independently `X_UI = String(PosX >> 5)`, `Y_UI = String(PosY >> 5)` (JS source line 56 in original shipped asset).
- `emu_chat._pos_of` directly names `PosX`, `PosY`, `MapID`. The **exact conversion between raw memory units, shifted UI coordinates and tile coordinates inside compiled EmuChat** is **not proven** by strings. Do not assume that EmuChat compares raw `PosX` against a tile `tx` without first recovering the actual transformation; this would manufacture a bug that hasn't been demonstrated.
- The success condition needs **map ID match and near-destination tile position** to avoid accepting the same x/y on a different map. The original doc says verify by memory/glide/map change, but whether it combines map and near-tile checks in exactly that way remains **not source-proven**. Document a parity requirement, not an observed Python `if`.
- Frida's `readAll()`/RPC validation and cache recency from P02 are prerequisites. `MapID/PosX/PosY` missing must not be silently reported as arrival.

## 4. Actual compiled Train LD integration and known incomplete farm path

At 0x2932300–0x2932312 the **`emu_farm_tab` compiled module references `emu_chat` and `goto`**; `EmuFarmTab._goto_acc` method is at 0x29328db. The surrounding module doc at 0x2932411–0x293262d explicitly states:
- LD/MEmu-oriented minimal configuration, device/group row presets, **per-emulator [EmuCoords:serial]** stored separately, plus `[EmuFarm]` with fallback `[TrainLD]` for settings migration.
- Its movement uses **chat-link goto + memory verification**.
- Row keys are based on `android_id` because ADB serial can change on reboot. P02 warns clones can share android_id — uniqueness of UI/account mapping is a future acceptance test.
- **The same compiled region explicitly says `farm cycle: phase sau` (0x29320a3)**. Therefore do **not** call the entire automatic farm cycle fully implemented based on a goto reference. It may offer partial Train LD controls, with full automation deferred in the original EXE. Original `/emu_farm_toggle` was separately ACK-only per D07.

## 5. Debug Android step-wise protocol

Original debug Android constants at 0x290d2b5–0x290d394 show staged steps:
1. Open chat panel.
2. Enter `@GOTO_` text.
3. Send and check the chat panel/link.
4. Tap chat link, then observe `MapID/PosX/PosY` and track movement.
There are separate `_do_mem`, `_do_tap`, `_do_cap`, `_do_rgb`, `_save_cfg` compiled callable names. This is a *developer-only test workbench* from P01, not evidence that the tab must be displayed for all users.

**Important distinction:** Debug's one-step `tap` command may succeed while higher-level `goto` fails; `goto` is successful only on verified game state rather than success of the ADB shell or HTTP transport.

## 6. Failure and fallback matrix (verified evidence versus planned parity)

| Case | Evidence | Do not overclaim |
|---|---|---|
| Already at destination | Literal 2-tile early exit | Exact distance function unknown |
| No saved/valid UI points | `_chat_xy` and fallbacks | Numeric fallback values and missing-value behavior unknown |
| Wrong live ADB serial/Android ID collision | P02 identity documentation | No silent target guessing |
| Chat focus loses keyboard | Multi-step UI sequencing | ADB tap ACK not proof of text entry |
| Old text not cleared | clear-step documented | Clear method/hotkey unknown |
| Keyboard still overlays send/link | keyboard dismissal documented | Need screenshot/live UI confirmation |
| Link row moved or scrolled | newest own chat row documented | Exact link-picking algorithm unproven |
| Tap/send fails | `tap loi` string | Retry/backoff unknown |
| No fresh valid memory | `poll_rows` and P02 Frida availability | Do not mark success without reading player state |
| Same coordinates different map | `start_map`, `MapID` | Cross-map arrival gating exact branch unknown |
| Char moves but stalls | `last_move`, literal 30s stuck | Clock-reset calculation unknown |
| Global timeout | `timeout tai` | Value/default/schedule unknown |
| Stop/cancel during goto | Farm setup/busy framework references | Cancellation semantics not recovered |
| Raw memory versus tile conversion | `X_UI/Y_UI` JS shifts, EmuChat `PosX/Y` | Do not assert hidden scaling logic without decompile/live trace |

## 7. Static verification and boundaries
**PASS static**: original ZIP SHA+CRC, inner EXE fingerprint, EmuChat methods/docs/coordinate keys and integration offsets, `emu_client.js` role coordinate representation source read-only. **NOT RUN**: LDPlayer, Windows native runtime, ADB tap/keyboard/link, Frida attach, actual character movement, reboots/multi-device, changing game UI scale, full reconstructed application.

No source rewrite, no EXE generated, no Proxy development, no hidden/dev tab exposed. Existing Stage-S product app source and Stage-T Actions Windows build pipeline remain absent in repository's prior full code audit: **BUILD_BLOCKED_SOURCE_MISSING**, not a compiled PASS/FAIL.

**Status**: `STATIC_EMU_CHAT_GOTO_COORDINATE_AND_MEMORY_VERIFICATION_AUDITED / LIVE_PARITY_DEFERRED`.

**NEXT_ACTION**: **P05 — `emu_farm_tab` active/partial Train LD controls, per-account device/preset mapping, permission gates, goto integration, and `farm cycle: phase sau` limitations**; original EXE first. Do not mark farm engine running from GUI alone.
