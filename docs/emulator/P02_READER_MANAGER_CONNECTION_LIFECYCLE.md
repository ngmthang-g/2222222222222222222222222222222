# P02 — AndroidReader / EmuManager: ADB–Frida connection and identity lifecycle

## Scope and authority
Task P02 continues the verified P01 handoff; **no UI rebuild, no Proxy, no emulator control or game process execution**. Authority is frozen user-supplied `TLMTool_2.1.2(10).zip` (ZIP SHA256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, 1,050 ZIP entries, CRC PASS), its inner `TLMTool.dist/TLMTool.exe` (47,450,112 bytes; SHA256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`) and shipped `emu_client.js` (5,368 bytes; SHA256 `384ccee9a2ddf236db377fca3abd36cbc17df81a94a286551a749a3132d02db1`). These match Gate A/P01 and do not require re-auditing those completed tasks.

**Important Nuitka-constant provenance:** the relevant `AndroidReader`/`EmuManager` strings and method markers lie **before** the `<module emu_reader>` terminator at binary offset `0x29361cc`, predominantly `0x29333d9e..0x29361a6`. Do not wrongly attribute the strings after that marker to `emu_reader`. Static strings prove embedded contracts and identifiers, **not** decompiled Python condition order or a successful game interaction.

## 1. Read-only architecture and connection sequence
```text
TLM UI / EmuFarmTab (permission emu_tab, initially hidden)
    -> EmuManager.devices() / poll_rows() [cached quick UI poll]
       -> ADB serial enumeration / game PID check (app com.fgstudio.thanlongmobile)
       -> per-serial background _worker / _kick (expensive discovery)
       -> AndroidReader(serial, adb)
          -> resolve adb.exe; ensure /data/local/tmp/frida-server per VM
          -> guest root frida-server startup/health
          -> frida device/session attach game and resident JS create/load
          -> RPC ping == "emu-ok"; ensure_loaded can reload on stale session/export
          -> cached RoleID: scanRoleId; else scanShape
          -> pick_validated verifies live name to reject stale same-pattern candidate
          -> setBase -> validate(expected RoleID) / readAll / bagSlots
       -> EmuManager reports (serial, row-or-None, status, aid) / error
       -> EmuFarmTab row mapping, not proof of active automation
```
This is a **static interface model**, not a verified total call graph. Explicit method markers: `AndroidReader.ensure_server` 0x2935b8e, `connect` 0x2935bab, `close` 0x2935bc2, `ensure_loaded` 0x2935bd7, `discover` 0x2935bf6, `pick_validated` 0x2935c2a, `validate` 0x2935c5b, `bag_slots` 0x2935c73, `read_all` 0x2935c8c.

ADB resolution references common LDPlayer paths, dnconsole/ldconsole, local frida-server or .xz and guest `/data/local/tmp/frida-server`. Original bundled documentation states each VM filesystem is separate; `ensure_binary` pushes/chmods if missing and `ensure_server` can launch a root frida-server. Those operations were **not executed** for this task. The original error text includes missing Frida Python package, missing frida-server binary, failed connection and zero candidates.

Resident JS is Frida 17-oriented, not a Python source recovery. Seven exact exports: `ping`, `setBase`, `readAll`, `validate`, `scanRoleId`, `scanShape`, `bagSlots`. The original ensure_loaded doc says stale JS (e.g. missing bagSlots after updates) triggers reloading and ping checks distinguish dead session after game close; precise retry/timing/cleanup ordering remains **UNKNOWN**.

## 2. Identity: three identifiers are not interchangeable
| Identity | Original static contract | Use / safety boundary |
|---|---|---|
| ADB `serial` | ADB device/transport target; may change with reboot or port | Attach/input commands must target current live serial |
| `aid` / Android ID | `aid_of` cached for ~5 min; used as a stable UI row/config key | Clone VMs may share Android ID; do not silently assume global uniqueness |
| Guest IPv4 | `ip_of` + `serial_for_ip`; originals say clones sharing serialno and android_id are differentiated by IP | Reverse lookup must be unique; ambiguity => no guessed target |
| `hwid` / ro.serialno | `hwid_of` + `serial_for_hwid` | May collide between clones |
| RoleID/RoleName | Cached RoleID drives targeted memory discovery; readable live name is required by validated pick | Do not reuse stale role memory after relogin |

Source docs at 0x2934a43, 0x2934b9f, 0x2934d7a, 0x2934cf5 and 0x293351e8 explicitly distinguish these purposes. In particular **UI key by aid** coexists with **clone collision risk**; whether running clones are uniquely keyed everywhere is *not proved* by static strings. Diagnose rather than normalize silently.

`EmuManager` exposes `devices`, `status_all` (dictionary with state/error/aid/role/vm), `_server_pidof`, `_server_alive`, `_server_start`, `_worker`, `poll_rows`, `active_serials`, `force_discover`, `get_bag_slots`. `active_serials` means current game-running ADB serials, not proven logged-in characters. Embedded documentation says `poll_rows` is a lightweight refresh while expensive per-serial discovery runs in background; `force_discover` clears status cache but preserves RoleID hint. Exact scheduler cadence, retry ceiling and the `_VM_NAMES_TTL` numeric value are UNKNOWN.

## 3. Candidate selection, validation and reader output
Original AndroidReader docs at 0x29341a3–0x2934476:
- Known RoleID: targeted `scanRoleId`, preferred exact RoleID; “newest” candidate may be high-address and **must** be checked live.
- No RoleID: blind `scanShape` based on invariant MaxRage pattern.
- `pick_validated`: actually read candidate data/name and reject stale pattern matching a “dead” character after relogin; if unsuccessful, move to another candidate.
- `read_all` exposes PC-style keys `RoleName`, `RoleID`, `Level`, `MapID`, `PosX`, `PosY`, `X_UI`, `Y_UI`, HP/MP/money etc. JS sets X_UI/Y_UI to shifted integer coordinates; it does not establish game-visible parity on a live VM.

Shipped JS `verifyBase` explicitly constrains RoleID >100000, Level 1..120, MaxRage 1000, Rage 0..1000, MapID 0..20000, X/Y 0..30000, FactionID 0..20; readability failures return null/false rather than a trustworthy row. `readAll` returns null if BASE unset. `validate(expectedRid)` requires current RoleID and readable RoleName, but does not independently prove it is the correct clone if the same character is active twice.

## 4. Bag slots and failure semantics
The JS `bagSlots` method counts plausible entries with Site==10, returning null when BASE/dictionary/read fails, 0 for missing entries or nonpositive count and N for counted occupied entries. Source comments state dictionary ptr player+0xC8; entries +0x18; count +0x20; entry stride 24; item pointer +16; template ID +0x14; site +0x1C. It caps scanning at 10000. The original compiled doc says `AndroidReader.bag_slots` / `EmuManager.get_bag_slots`: **None when read error / short cache**, not “empty bag”.

**Risk:** the actual JS returns 0 for a null entries pointer or count<=0, which cannot on its own distinguish genuine empty inventory from a malformed/unloaded dictionary; preserve this observed behavior as a parity risk, not an asserted live game bug. Do not trigger auto-sell/drop on 0 unless a separately validated state is established.

## 5. Failure and recovery state matrix
| Condition | Original evidence and expected conservative classification |
|---|---|
| ADB executable or device missing | cannot connect; report diagnostics, no invented row |
| Game PID absent | VM may be alive but character row not proof; no action |
| Frida server binary absent | setup failure with explicit diagnostic |
| Frida connection/attach failure | connection FAIL, do not treat stale cached row as fresh |
| Script stale / missing RPC export | ensure_loaded reload path documented; success unproven |
| Session dies after logout/game restart | ping/liveness and reconnect path documented; retry ordering UNKNOWN |
| RoleID cached but no live valid candidate | targeted search zero => candidate recovery should be explicit; exact fallback order UNKNOWN |
| Blind scan finds stale garbage candidates | reject via live readable-name check; no fake success |
| IP/aid/hwid collision among clones | do not guess a serial; uniqueness must be tested |
| `bagSlots` returns None | read failure, **not** true empty bag |
| `bagSlots` returns 0 | potentially empty **or** dictionary-not-ready; distinguish on live test |
| Manual force discovery | purge status cache, keep RoleID hint (original doc) |

Known diagnostic strings include “đang kết nối”, “đang quét”, “re-scan”, “scan 0 instance”, “connect frida fail”, and the row contract `[(serial, ci|None, status, aid)]` (0x29335026..0x29335274). These do not verify retries ran successfully.

## 6. Tests and unresolved items
Static PASS: exact original hashes, ZIP CRC, compiled method markers, seven RPC exports, and Node grammar check of **Frida JS only**. 0 live LDPlayer/ADB/Frida tests performed; 0 reconstructed-app tests performed.

UNKNOWN: ADB device selection under reconnect, process-PID race, exact manager worker backoff and cache expiry except documented aid 5min/coords 30sec, Frida script unload/dispose ownership, per-clone collision handling across *all* UI/storage paths, root availability, permission changes during worker execution, whether memory offsets fit user's current APK, and all real read/refresh timings.

**Keep original UI constraints:** Train LD hidden until `emu_tab` entitlement; Debug Android dev-only; do not invent always-visible tabs; do not develop Proxy. Existing P01/D07 docs remain authoritative; P02 adds only connection/identity specifics.

## Gate/status
**P02 = STATIC_ADB_FRIDA_IDENTITY_CONNECTION_LIFECYCLE_AUDITED / LIVE_EMULATOR_PARITY_DEFERRED.** 25 acceptance tests listed in `P02_MODEL.json`, 0 runtime executed.

**Build audit:** Gate S application source and Gate T Windows build workflow remain missing as of current GitHub review, so no rebuilt EXE or UI/runtime PASS is claimed.

**NEXT_ACTION:** P03 — original `emu_input` ADB event/capture and per-device coordinate/action/timeout contract audit. Compare original EXE and shipped scripts before writing code. Respect original permission gates and Proxy exclusion.
