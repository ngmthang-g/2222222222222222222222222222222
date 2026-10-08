# O03 — Memory Items: `read_bag`/`get_bag` (Site 10), dictionary and trade Site 200 boundary

## 1. Authority, task and test boundary
- GitHub HEAD `98678985ca5c857e3dc57d98c5dee34232b2983f` checked with PLAN.md/STATE.md first: O01/O02 completed and O03 not yet present. All earlier research preserved.
- Frozen original ZIP SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd` (1,050 entries, CRC-clean previously verified), original inner TLMTool.dist/TLMTool.exe SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, 47,450,112 bytes. The EXE was read as bytes from the ZIP; it was never executed.
- Original compiled `memory_items` block `.memory_items` at `0x2b69c5f` (47,850 serialized bytes, 895 constants), rather than source Python. This stage isolates genuine bag read/data schema and does not implement trade, inventory use/drop or DLL injection.
- The O02 `memory_reader.Reader` process/GameAssembly validation model remains the attachment authority. Do not use another game repo for addresses. A string/number in the compiled constants is **not** a decompiled Python statement.

## 2. Reader attachment and three distinct bag states
Original `memory_items` imports `memory_reader.Reader`; `get_reader` uses HWND/PID, `_reader_cache`, timestamps and lock, and probes `Reader.read_all()/start()` with `target_pid`. Its embedded documentation says attached Reader or `None`. This creates an important error boundary: a missing Reader is not an empty bag.
Original `read_bag` serialized block has the three distinct diagnostics:
1. `Reader chua attach` — no validated process reader.
2. `Items null (nhan vat chua load?)` — character's Items pointer is missing; potentially not loaded yet.
3. `Tui rong (count=0)` — actual dictionary count zero after a valid read attempt.
Other statuses include `OK (... dict count=...)`, `KNOWN_SITES` and the literal return documentation `(rows, info). rows: [{dbID, itemID, site, pos, qty}]. Giu ten cu cho tuong thich.`
The original package therefore distinguishes **read failure/unready**, **valid empty**, and **nonempty** data. The exact tuple returned by every exceptional branch requires source-level or live testing; don't map `None`, an error dict and `[]` to the same success. Cached Readers must be revalidated after PID changes as already established by O02.

## 3. Dictionary traversal — evidenced structure, not invented offset table
Near `read_bag` the compiled constants include `_r64`, `rd`, `0xC8`, `_r32`, `0x18`, `0x20`, `entries`, `KNOWN_SITES`, and several tagged size/capacity-looking integers (`10000`, `65536`, `1000000`). These are **exact observed adjacent serialized constants** but not proof of the Python expression or correct assignment for every field.
O02 independently recovered an embedded Reader doc: `RoleData.Items (rd+0xC8)` is `Dictionary<int, DBItemData>`, in the mounted-item read section. This corroborates the Items pointer origin, **not** a complete bag-entry memory layout.
**Only schema fields proven by the read_bag embedded doc should be frozen as return columns**: `dbID` (live DBItemData instance identity), `itemID` (item template/type identity), `site` (container), `pos` (container slot/index, **not a mouse pixel coordinate**) and `qty` (quantity/stack).
The module's `KNOWN_SITES` set exists but its full membership and filtering conditions are not bound to source statements. Do not infer the exact dictionary capacity, `entries` stride, `count` field offset or all site membership from the ordering of tagged integers in this block.
The game may mutate Items, count, entries and per-item DBIDs during reading. The existence and ordering of an atomic snapshot/retry on the original is **unknown**; future implementation should validate owner PID/readability and not use a stale dbID for any destructive packet.

## 4. `get_bag`: Site 10 enriched summary
An exact embedded `get_bag` document states: **`Tong hop tui Site 10 + enrich ten. Tra dict hoac None.`** This is a bag **Site 10** view built from the reader results, not an alternate trade query.
The compiled output field surface contains `name`, `icon`, `src`, `type`/`etype` and summaries `slots`, `distinct`, `total_qty`, `non_bag`, `info`. It also contains `sorted`, a `get_bag.<locals>.<lambda>` and generator. A plausible derived meaning of these names is occupied slots/distinct templates/stack total and skipped other sites, but the precise expression, return nesting and ordering are **not fully reconstructed** from constants.
Metadata is from `item_meta_data.META` when bundled, with source/dev CSV fallback; O04 owns exact metadata/weapon set content. The existence of no external CSV must not turn valid unrecognized itemID into a fake “missing bag”.
**Do not derive full capacity or free slots from `slots` without confirming original semantics**; a separate original Lua query `Game.GetFreeBagSpace()` exists. A valid itemID can appear in multiple DBItemData instances or slots; `dbID` remains the per-instance identity.

## 5. Trade Site 200 is a separate, Lua-backed interface
The original `get_trade_items` block contains `TRADE_SITE`, a Lua expression `Game.GetItemsAtSite(%d)` enumerated with `pairs(t)`, reading `v.ItemID` and `v.Quantity`. Its embedded document explicitly says **Site 200** and states:
- Result `list[{dbID,itemID,qty}]` means trade table entries.
- Result `[]` means no item has been placed.
- Result `None` means query/read failure.
An independent `count_trade_items` document says **`-1` when unable to read**. Do not reinterpret `None` or `-1` as empty trade or as a valid zero count.
Trade placement helpers use `GUI.FindUI('Trade')`, `Game.GetItemData(dbID)` and `PutItemTrade`, with a documented fire-and-forget result: `True` means the Lua command was sent, not that an item was placed. Confirmation requires a **separate `get_trade_items` or `count_trade_items` query** after processing.
`get_bag_items_by_type` is another **distinct in-game Lua query**, normally Site 10 with `Game.GetItemType()`; it returns `list[{dbID,itemID,qty,pos}]` or `None` on error and explicitly does NOT depend on local item_meta.csv / weapon_ids. It is not the same mechanism as direct memory `read_bag` plus embedded metadata.

## 6. Non-goals and no destructive side effects
The same module contains `send_item_action_command` with documented use=3, drop=4, destroy=9 using dbID through packet 100005. Their presence is recorded as **boundary evidence only**. O03 did not perform any item action, packet send or trade placement, and does not claim any original action succeeded.
O01 filter protections remain frozen: no discard by default, empty rule/preset -> no packet, dry_run, weapons protected unless expressly included. Those policies will be audited separately in O05. No version-unverified offsets, fabricated bag rows, UI click coordinates or inventory mutations were introduced.

## 7. Acceptance matrix — all future reconstructed-app tests NOT_RUN
| ID | Requirement | Verification |
|---|---|---|
| O03-01 | Frozen original module and `read_bag/get_bag` markers match | STATIC |
| O03-02 | HWND reader cache and expected PID are revalidated | WINDOWS |
| O03-03 | Reader missing is distinct from valid empty inventory | WINDOWS |
| O03-04 | Items pointer null/unloaded is distinct from count=0 | WINDOWS |
| O03-05 | Dictionary entry traversal and cap/stride match original | RESEARCH/WINDOWS |
| O03-06 | Result `(rows,info)` contains dbID/itemID/site/pos/qty with correct types | WINDOWS |
| O03-07 | Broken/read-denied count/entry returns errors rather than synthetic `[]` | WINDOWS |
| O03-08 | Bag Site 10 filters correctly while other sites remain distinguishable | WINDOWS |
| O03-09 | get_bag enriches metadata and handles unknown item templates safely | WINDOWS |
| O03-10 | Summary slots/distinct/total_qty/non_bag exact semantics | RESEARCH/WINDOWS |
| O03-11 | Full/free slots do not conflate get_bag.slots and Game.GetFreeBagSpace | WINDOWS |
| O03-12 | Changing inventory during read avoids torn/stale snapshot misuse | WINDOWS/STRESS |
| O03-13 | Instance dbID vs itemID and pos semantics remain separate | STATIC/WINDOWS |
| O03-14 | Trade Site200 list/[]/None error semantics preserved | WINDOWS |
| O03-15 | count_trade_items -1 read error does not imply zero | WINDOWS |
| O03-16 | Lua GetItemType Site10 query is independent of local META | WINDOWS |
| O03-17 | Trade PutItemTrade True is send-only, success requires later read | WINDOWS |
| O03-18 | Game version/PID/GA pointer changes fail closed before item action | WINDOWS |
| O03-19 | No unapproved drop/use/trade packet during bag inspection | WINDOWS/SAFETY |
| O03-20 | Final Windows executable with original-vs-new bag UI/data parity | STAGE_S/T/V/W/X |

All 20 cases are **NOT_RUN** on a reconstructed application. Offline EXE marker/hash checks are research results, not tests of a working new game tool.

## 8. Result and NEXT_ACTION
**O03 = STATIC_BAG_SITE10_SCHEMA_AND_TRADE_SITE200_BOUNDARY_AUDITED / LIVE_MEMORY_PARITY_DEFERRED**.
**NEXT_ACTION O04 — `item_meta_data.META` and `weapon_ids` embedded datasets, record schema, ItemID coverage, classifier, fallback and metadata confidence audit.** Use the original frozen EXE first, sample/measure only if serialized data can be parsed without inventing entries. O05 follows with bag_filter rules and destructive-action safety. Preserve O01–O03 and all Stage N; Proxy remains excluded.
