# O02 — memory_reader: process discovery, GameAssembly attach, pointer chains and read validation

## Authority and scope
- GitHub main HEAD before edits: `ccb9def1b1cdd2db2e1e4f95995632bab308fa04`. PLAN.md and STATE.md reread. O01 existed/verified, O02 absent; all Phase N docs preserved. Scope is exact frozen TLM 2.1.2, NOT external Thần Long source.
- Frozen ZIP SHA256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, 1050 entries, ZIP CRC clean. Original inner TLMTool.dist/TLMTool.exe SHA256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, 47,450,112 bytes. Read-only ZIP extraction of bytes, not execution.
- Active compiled `.memory_reader` module at `0x2b7575a`; payload begins `0x2b7576f`, 11,804 bytes, 494 serialized constants. Reader class and methods are evidenced. Recoverable constants/docstrings are not Python source AST.
- O02 is **read/validation analysis only**. The compiled Reader also contains memory-write/remote-DLL functions; no memory write, injection, remote process access, packet or original EXE execution occurred. Numeric documentation is version-specific, not safe to transplant to other game builds.

## 1. Process selection and OpenProcess privileges
`memory_reader` references `psutil.process_iter`, Unicode NFD/ascii/strip normalization, and names `than`, `long`, `mobile`, plus `Game không chạy`. This supports process discovery with name normalization, but the complete predicate, exact prioritization when multiple instances exist, PID matching order, search cadence and process-selection fallbacks remain UNKNOWN.
An explicit `OpenProcess` path uses `PROCESS_RIGHTS`, `GetLastError`, `CloseHandle` and logs `OpenProcess(pid=..., rights=...) FAILED err=...` and `OpenProcess OK pid=... handle=...`.
On failure, original compiled symbols include `OpenProcessToken`, `GetCurrentProcess`, `TokenIsElevated`, `advapi32.GetTokenInformation` and diagnostic `Cần Run as Administrator!`. This is conditional guidance, **not proof every installation requires administrator privileges**. The exact PROCESS_RIGHTS numerical mask is not safely assigned from nearby tagged constants.

## 2. Module enumeration / version and cache invalidation
`Reader._enum_modules` is supported by `EnumProcessModulesEx`, `EnumProcessModules`, `GetModuleBaseNameW` and `GetLastError`. Its embedded documentation explicitly says `EnumProcessModulesEx(LIST_MODULES_ALL)` retries because it can be flaky on certain Windows builds (e.g. 1909). The number of retries, `delay` value, exact list/filter flags and error paths are not fully decompiled.
`Reader.start` probes `gameassembly` and `unityplayer`. GameAssembly base is saved for relative RVA reads and UnityPlayer base is tracked separately; a found module name alone does not prove an attached, valid RoleData object.
Cache `_ga_cache` is guarded by `_ga_cache_lock` and TTL. Exact source log surfaces: `cache HIT pid=... GA=... rd=...`, `cache stale rd invalid ... rescan`, `cache stale ga_base unmapped ... rescan`. Cache invalidation also responds to garbage RoleName read by `read_all`.
Do NOT hardcode a supposedly verified `GA_CACHE_TTL` numeric seconds; it is present as a symbol with unbound numeric constants. `MOUNT_CACHE_TTL` is a **different** read cache: the original read_mount docs explicitly state roughly 30s, and a nearby encoded double is 30.0.

## 3. Memory read primitives and invalid-region diagnostics
`ReadProcessMemory` and `_r32`/`_r64`/`_r8` read accessors are exact class symbols. Encoded `<I` and `<Q` unpack formats indicate little-endian 32-/64-bit reads; `utf-16-le` is present for game strings.
`VirtualQueryEx` and `_region_info` identify memory states from a target address: `unmapped`, `committed protect=0x..`, or `query-fail`. On a storage read failure, original logs include `Storage null`, `RPM err=`, `@ GA+...`; pointer-chain failures log `Chain break at +...` with region details.
Class has `read_all` and outputs RoleName, RoleID, Faction, MapID, position, HP/MP and other fields. If RoleName is nonsensical, original log mentions evicting GA cache. **An integer 0, a broken chain, a rejected session anchor and an unreadable process must not be treated as one successful empty character.**

## 4. Pointer chains: exact embedded docs vs uncertain assignment
Reader v10 original embedded text, verified at offset `0x2b773a0`: `Pointer: GA+355B208 → +B8 → +88 → RoleData`; `Coord UI: tile = pixel >> 5`.
`Reader._resolve_chain` exact doc: traverse from `GA+rva` by dereferencing `chain[:-1]`, return final **object address before the last field offset**, return `0` if broken. Hence an adapter must not mistake the chain result for the ultimate DWORD value or add the final offset twice.
The serialized block contains encoded `0x355B208` (`0x2b77568`), `0xB8` (`0x2b7756d`), and several other tagged values. **Doc-confirmed chain is exact intended original-version guidance, but the Python variable construction `STORAGE_RVA`/`CHAIN` was not decompiled.** We cannot label each adjacent integer an assigned member solely by table order.
The `read_auto_flags` exact doc describes two pointer chains: `GA+0x356ED08` and `GA+0x356E288`, terminal DWORD `+0x2C`. It returns `AutoFlag`, `AutoFlag2` and uses **-1 for broken chain or read failure**. That is **not** the same failure value as `_resolve_chain`'s `0`.
The read-auto-state doc also exposes `AutoPathManager.Instance.autoPathType @0x38` (0 idle, 1/2 pathing) and `PlayZone.Instance.EnableAutoF1 @0x20`, but values outside the valid range return **None** (possible stale static/base game version). These offsets are illustrative original-specific symbols, not license to enable AutoPath features in O02.

## 5. Anchored SessionData: avoid false static-getter matches
Original embedded static-backing doc: scan up to 64 bytes of `get_Instance`/getter code for the first `mov rax,[rip+disp32]`, sometimes behind lazy-init prologue. **The first matching instruction can be wrong** (e.g. point to a string literal), so only trust getters after range validation or the anchored `session_block()` method.
`SessionData.RoleData @0x88` must equal known live `self.rd`. The original describes scanning `get_RoleData` at `GA+0x6F4030`; for the matching QWORD target, block=`target-0x88`. This comparison is the essential validation anchor; without it, a guessed backing-field address is unsafe.
Once anchored, the original doc lists `Monsters@0x20`, `NPCs@0x50`, `ItemPacks@0x18` relative to SessionData block. These **are original embedded documentation**, not reconstructed confirmation that a current game process has valid dictionaries there. Numeric `SESSION_ROLE_DATA_RVA` and many `SESS_*_OFF` symbols appear in module serialization; adjacency is not sufficient to prove the exact assignment of every remaining offset.
Another original doc says `RoleData.Items (rd+0xC8)` is a `Dictionary<int,DBItemData>` used to read mounted equipment (Site 2); do not confuse this with bag Site 10 (O03) or infer item count from mounted-item retrieval.

## 6. Validation hierarchy for future implementation
**SOURCE STATIC**: verify exact module/method markers, offset docs, result variants `0`, `-1`, `None`, error logs and numeric tags. These are verified descriptions of the original executable.
**FUTURE WINDOWS**: each candidate PID must first satisfy process ownership/rights and module discovery, then a readable GameAssembly region, guarded pointer traversals, plausible/consistent RoleData fields and SessionData.RoleData anchor where needed.
**FAIL CLOSED**: wrong process, insufficient rights, missing GameAssembly, reused PID, expired cache, unmapped base, broken chain, implausible RoleName or mismatched session anchor => no valid inventory read and no destructive item operations. Do not assign a safe-looking item count of zero to unknown read failures.
`memory_reader` includes `WriteProcessMemory`, `Reader.inject_dll` and AutoPath helpers. These are out-of-scope read-adjacent symbols, **not** implemented, tested, or endorsed as prerequisites for memory reading in O02.

## 7. Acceptance tests (specifications, all rebuilt-app NOT_RUN)
| ID | Criterion | Gate |
|---|---|---|
| O02-01 | Frozen binary/module header+CRC/hash and Reader markers match | STATIC |
| O02-02 | Process name normalization and exact matching reconstructed from original | RESEARCH/WINDOWS |
| O02-03 | Multiple game instances and disappearing PID selected safely | WINDOWS |
| O02-04 | OpenProcess required rights and elevation fallback match real original | RESEARCH/WINDOWS |
| O02-05 | Module enumeration retries/fallback on flaky Windows variants | WINDOWS |
| O02-06 | Real GameAssembly/UnityPlayer addresses resolve for the exact target build | WINDOWS |
| O02-07 | GA cache hit is validated; stale ga_base/rd evicted on PID/game changes | WINDOWS |
| O02-08 | VirtualQueryEx distinguishes unreadable/unmapped committed ranges | WINDOWS |
| O02-09 | ReadProcessMemory 8/32/64-bit and UTF-16 read respect failure/size | WINDOWS |
| O02-10 | Original documented GA+355B208 -> B8 -> 88 resolves plausible RoleData | WINDOWS |
| O02-11 | Generic chain result is pre-final-offset object and fails with 0 | STATIC/WINDOWS |
| O02-12 | Two AutoFlag paths return -1 on broken chain/read error | WINDOWS |
| O02-13 | Out-of-range AutoPath/PlayZone state returns None, not false success | WINDOWS |
| O02-14 | SessionData get_RoleData 6F4030, RoleData+88 anchor yields valid block | WINDOWS |
| O02-15 | Anchored SessionData ItemPacks/Monsters/NPCs fields validate | WINDOWS |
| O02-16 | Static getter wrong match is rejected; RoleName garbage evicts cache | WINDOWS |
| O02-17 | GA_CACHE_TTL and module retry counts determined without guessing | RESEARCH |
| O02-18 | Different game versions/changed RVAs fail closed, no blind game writes | WINDOWS |
| O02-19 | Actual game source/bag reader integrated after O03 with same PID validation | STAGE_S/WINDOWS |
| O02-20 | Rebuilt Windows app launches and matches original behavior | STAGE_T/WINDOWS |

**All 20 tests NOT_RUN on reconstructed code**. Static read-back of original bytes is a research check, not an executable-function PASS. O02 did not run any memory reads against a live game or write/inject.

## 8. Result and NEXT_ACTION
**O02 = STATIC_MEMORY_READER_PROCESS_GA_RVA_CHAIN_AND_VALIDATION_AUDITED / WINDOWS_PARITY_DEFERRED**.
NEXT_ACTION: **O03 — memory_items live inventory reader, role/session dictionary layout, get_bag Site 10, entry fields, error/null/race, trade Site 200 separation audit**. Use original frozen `memory_items` EXE block and O02 Reader anchors; do NOT test/drop/use actual game items until live compatibility can be safely verified. O04 metadata/weapon records and O05 bag_filter policy remain separate. Keep Phase N, O01/O02 and Proxy exclusion untouched.
