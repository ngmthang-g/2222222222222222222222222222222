# O01 — Memory/Item original module authority and active wiring audit

## Authority and continuity
- GitHub main parent HEAD `d45a0efb4c781f73e7f465e39dc98425fcda8b40` checked first; PLAN.md, STATE.md, PROJECT_STATUS.md reread. Stage N01–N10 documented; O01 absent. No previous report/source changed.
- Frozen user-uploaded `TLMTool_2.1.2(9).zip` SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, 93,715,901 bytes, 1050 entries with CRC clean. Authoritative inner `TLMTool.dist/TLMTool.exe` SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, 47,450,112 bytes.
- Read-only static parsing of original EXE Nuitka-style module headers, UTF-8 string/doc constants, class-method name tables, and caller module references. Did not execute original EXE, game, DLL, inject or packet. Module existence/byte count is not recovered original Python source or successful feature execution.
- PLAN Phase O explicitly names `memory_reader`, `memory_items`, `bag_filter`, `item_meta_data`, `weapon_ids`, and asks process selection, addresses/offsets, read strategy, validation, inventory structure, item classification, filter behavior. This task is O01 **authority + wiring only**; deeper numeric offsets are O02, schema O03, metadata O04, policy O05.

## 1. Five exact original modules
| Module | Original EXE header offset | Serialized bytes | Constants | Role |
|---|---|---:|---:|---|
| `memory_reader` | `0x2b7575a` | 11,804 | 494 | Windows process/memory reader and role/game-state APIs |
| `memory_items` | `0x2b69c5f` | 47,850 | 895 | Facade for Reader, live bag read, item/transaction/Lua operations |
| `bag_filter` | `0x28d5db3` | 5,162 | 145 | Shared filtering, presets, dry-run and discard command plan |
| `item_meta_data` | `0x2977206` | 1,989,514 | 7 | Large embedded item catalog `META`; 7 serialized top-level constants do not equal 7 items |
| `weapon_ids` | `0x2c54798` | 27,719 | 11 | Large weapon ItemID set and `is_weapon` classifier |

All five have associated original `.py` and `<module ...>` markers. `item_meta_data` and `weapon_ids` data are serialized objects, not plain source files; do not claim entry counts by treating constants count as number of items.

## 2. Process selection, attach, memory-read safety — `memory_reader`
- Original symbols show `psutil.process_iter`, process name filtering including `than`, `long`, `mobile`, Windows `OpenProcess`, `PROCESS_RIGHTS`, and related `OpenProcessToken`/privilege diagnostics. Exact process-match conditions, allowed-rights mask and privilege escalation policy are **UNKNOWN**; do not use substring-only matching as a verified process selector.
- The Reader attempts `EnumProcessModulesEx`/`EnumProcessModules` with retry, checks for `GameAssembly.dll` and `UnityPlayer`, obtains GameAssembly base, and traverses pointers from `STORAGE_RVA`/`CHAIN`/session offsets. It uses `_r32`, `_r64`, `_r8`, `ReadProcessMemory`, `VirtualQueryEx` and log diagnostics in `tlm_memory.log`.
- `_ga_cache` and TTL plus stale-reader verification exist: invalid/unmapped GA or garbage RoleName triggers cache eviction/re-resolution instead of assuming old handles are always valid.
- `ReadProcessMemory` can return errors and Reader.start can fail (e.g. privileges, missing game/DLL). An attached Reader is not proof the current bag schema is valid.
- Original Reader also has `WriteProcessMemory`, direct field-writing and auto-path methods; they are **not** permission to add memory-write/injection features to O01 or infer that reading the bag requires writing process memory.
- `STORAGE_RVA`, `SESSION_ROLE_DATA_RVA`, `SESS_ITEMPACKS_OFF` and pointer-chain symbols are present, but exact numerical binding and chain validation need O02 binary decoding and original Windows verification. Never invent absolute addresses or copy offsets from a different tool/game.

## 3. Inventory data interface — `memory_items`
- Direct import of `memory_reader.Reader`, HWND→PID get_reader, Reader cache/locks and failure returns `None` when not attached.
- `read_bag` original doc returns `(rows, info)` with each row `{dbID, itemID, site, pos, qty}`. `get_bag` focuses on **bag Site 10** and enriches rows with metadata; it can return `None` on read error. Distinguish empty bag rows from failed attach/read.
- `dbID` is live item-instance identity used by actions, while `itemID` is a template identity used to classify (weapon/equip/type). `site`, `pos`, `qty` describe location and stack; do not blindly treat `pos` as screen pixel coordinates.
- Existing command surfaces include `send_item_action_command` with packet `100005`: action 4 drop/abandon, action 9 destroy and action 3 use by `dbID`. This is an **original compiled behavior contract**, not a newly verified network protocol implementation; O01 sends nothing.
- Separate Lua game services such as `Game.GetFreeBagSpace()` and Site 200 trade table belong to the same large module. **Do not conflate** bag Site 10, trade Site 200, `get_trade_items` and free-slot query or declare all these functions powered by the same data-acquisition path.
- `get_bag_items_by_type` references in-game `Game.GetItemType()` independent of the offline CSV/weapon set. Exact subtype, item-classification fallback and numerical inventory offsets reserved O03/O04.

## 4. Embedded item metadata and weapon ID rules
- `memory_items.load_meta` explicitly prefers `item_meta_data.META` *embedded in binary*, and only then falls back to `out_icons/item_meta.csv`/`item_icon_list.csv` for source/dev. The packaged ZIP contains no separately named item/equip/weapon metadata CSV/XML matching those filenames, **but the embedded module exists**. Never infer `META` is empty simply because a CSV is absent.
- `item_meta_data` original doc describes generated records `META[id] = (Name, Icon, Source, EquipType)` from `out_icons/item_meta.csv` using `tools/gen_item_meta_data.py`; the source generator is mentioned in the original doc, not proven present as a runnable repo script.
- `weapon_ids` original doc describes Type 0–8, 16, 17 and 100 weapon templates from `Equips.xml` and `out_icons/weapon`, classified via ItemID int not display name. ItemID matching is important because translated/colored and duplicated display names can differ.
- Exact count and completeness of embedded metadata and weapon ID entries cannot be asserted from top-level Nuitka constant count; O04 must measure/validate data samples without changing data.

## 5. Filtering and discard safety — `bag_filter`
- `bag_filter` directly imports `memory_items` and uses `get_reader`, `read_bag`, metadata and item actions. `ACTIVITY_PRESETS` and `KEEP_PRESET_KEYS` provide opt-in activity modes. `farm_tab` original text: `Radio Nhặt đồ → preset keys bag_filter (train)`.
- Original `plan_discard` doc: dry-run produces a **preview of targets** `{dbID,itemID,pos,qty,name,preset_keys}` without sending. Empty rules -> `[]`.
- `discard_items` returns counters `{total,ok,fail,skipped,stopped,targets}`, handles stop_check callback, progress and delay; dry_run sends no item command.
- `discard_for_activity` doc says `keys None/[] -> KHÔNG vứt gì`; filter module doc reinforces **empty rules do not even scan memory or send a packet**. These are strict safety invariants, not optional defaults.
- Rule fields include `sites`, `item_ids`, `name_contains`, `equip_types`, `src`, `match_weapons`, `allow_weapons`, `protect_ids` and `protect_names`. Multiple rules are OR; declared fields of a rule are AND; target deduplicated by `dbID`.
- **Weapons protected by default** (`allow_weapons=False`); explicit weapon inclusion must be opt-in (match_weapons=True) and higher-priority protect_ids/protect_names must still be respected.
- **Drop can destroy a whole stack**: original doc packet `100005` and argument `4:dbID`; high-risk operation must require preview/user confirmation and runtime verification, never fire based solely on a guessed list. Original module calls out GUI confirmation/dry_run separately.
- If memory reader is None or embedded metadata load fails, do not synthesize empty inventory or false positive rules. Original warns missing item metadata can make non-weapon filter fail.

## 6. Direct cross-module wiring — what is active and what is not proved
Original EXE compiled byte strings show direct reference imports, independent of screenshots:
| Consumer module | `memory_items` direct symbol | `bag_filter` direct symbol | Distinction |
|---|---|---|---|
| `farm_tab` | YES (0x293ff59) | YES (0x2941412) | Farm tab has visible radio/preset hook and `discard_for_activity` |
| `phoban_tab` | YES (0x2b889d3) | YES (0x2b89be1) | Dungeon worker path references shared discard service |
| `daily_tab` | YES (0x29071d2) | YES (0x2905b15) | Daily worker wiring |
| `donvang_tab` | YES (0x292766e) | YES (0x2928936) | Dồn vàng/activity wiring |
| `debug_tab` | YES (0x2912ec4) | YES (0x2912ed2) | Developer/debug import surface |
| `train_lsv_tab` | YES (0x2c0be35) | YES (0x2c0e09f) | Cross-server training references |
| `party_tab`, `rao_tab`, `don_logic`, `utils` | YES | not recovered direct here | Other shared memory/item services |

**Conclusion:** these are not five arbitrary unreferenced modules. `memory_items`/`bag_filter` are imported into multiple current compiled tab modules; FarmTab's visible logic directly maps pickup selection into bag_filter presets. But **source imports are not runtime-call proof** and do not certify that every function or preset is used on every tab. Avoid adding invented standalone inventory/bag tabs: no `.bag_tab`/`.inventory_tab` module was found in this original module-surface scan.

## 7. Evidence/unknowns and future acceptance gates
| Check | Requirement | Status |
|---|---|---|
| O01-01 | All five compiled module headers and markers exist with correct sizes | STATIC VERIFIED |
| O01-02 | Reader process selection uses GameAssembly/WinAPI and guarded attach/cache | STATIC VERIFIED; exact values UNKNOWN |
| O01-03 | Item rows schema `{dbID,itemID,site,pos,qty}` and bag Site 10 | STATIC DOC VERIFIED |
| O01-04 | Embedded META preferred; fallback CSV is source/dev only | STATIC DOC VERIFIED |
| O01-05 | Weapon classifier uses ItemID, not name; defaults protected | STATIC DOC VERIFIED |
| O01-06 | Empty rule/preset never sends item commands | STATIC DOC VERIFIED |
| O01-07 | Dry-run and stop/progress counters exist | STATIC DOC VERIFIED |
| O01-08 | Live farm/daily/phoban/donvang/train reference filter | STATIC IMPORT VERIFIED |
| O01-09 | Exact attach rights, RVA, chain and memory layout valid on original Windows game | NOT_RUN — O02/O03 |
| O01-10 | Exact embedded metadata count, content and fallback correctness | NOT_RUN — O04 |
| O01-11 | Exact discard rule priority, safe opt-in and weapon exceptions | NOT_RUN — O05 |
| O01-12 | Original displayed inventory/GUI parity and per-tab discard execution | NOT_RUN — Windows |
| O01-13 | Item action 100005 actually acknowledged/effected by game (not only send) | NOT_RUN — Windows |
| O01-14 | Windows game attach failure / PID reuse / race / empty bag handling | NOT_RUN — Windows |
| O01-15 | Reconstructed app and EXE build/parity | NOT_APPLICABLE — Stage S/T not started |

Original ZIP/EXE checksum and the exact static symbols have been inspected, but these are **not** acceptance passes of a rebuilt application. Do not treat historical modules as product Python sources. Empty rules and default weapon protection must not be weakened.

## 8. Status and NEXT_ACTION
**O01 = STATIC_MEMORY_ITEM_MODULE_AUTHORITY_AND_CROSS_TAB_WIRING_AUDITED / DEEP_LAYOUT_AND_LIVE_PARITY_DEFERRED.**
**NEXT_ACTION: O02 — `memory_reader` process discovery, GameAssembly/UnityPlayer module base, pointer chains, ReadProcessMemory validation and cache/privilege error audit**. Inspect original `memory_reader` serialized constants, marker/offset and numeric bindings with read-only tools; do not run original EXE or write game memory. Later O03 is inventory read/schema, O04 embedded item/weapon metadata and O05 bag_filter match/safety. Reuse completed O01 and Stage-N, keep Proxy development excluded.
