# O05 — Bag filter: presets, rule matching and destructive-discard safety

## Original authority and limits
GitHub parent HEAD 76a1d9a47830ccbde501b2e41302eaf0cab01e38; PLAN.md and STATE.md confirm O01–O04 complete and O05 absent. SHA-pinned ZIP c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd (1050 CRC-clean entries), original EXE 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22 (47450112 bytes), original bag_filter serialized header 0x28d5db3 (5162 bytes, 145 top-level constants). Original executable/game never run. Compiled constants/docstrings != recovered Python AST.

## No-rule safety, schema and precedence
Original exact module doc: empty rules **return zero, no bag scan, no packet**. `discard_for_activity` None/[] selected keys also documented as no-discard, though extra_rules parameter interactions must be traced before implementation. Default Site={10} only. Fields within one rule AND; multiple rules/presets OR, dedupe by live instance dbID.
Rule fields: sites, item_ids, equip_types, src, name_contains, match_weapons, allow_weapons, protect_ids, protect_names. Original documents `allow_weapons=False` by default, `match_weapons=True` as intentional weapon exception, `protect_ids` and `protect_names` highest priority. Actual case normalizer and combined exception/protection if-branch order remain UNKNOWN; do not infer permissive behavior.
`itemID` names a template; `dbID` is a live instance, and `pos` is a bag slot not a screen click. O04 proves display Names are not unique across 29983 template IDs.

## Preview and possible irreversible action
`plan_discard` yields only preview `{dbID,itemID,pos,qty,name,preset_keys}`, empty rules returns []; it does not send. `discard_items` returns `{total,ok,fail,skipped,stopped,targets}`, has dry_run, stop_check, on_progress, delay/time.sleep, `_send_lock_for(hwnd)` and `_SEND_LOCKS_GUARD`. Exact cancellation/lock order and sender acknowledgment are not Python AST-recovered.
**Original drop packet is 100005, action 4:dbID; dropping may remove an entire stack.** Original module puts GUI confirmation/dry-run responsibility on UI caller; mere doc is NOT evidence every caller prompts. O05 sends no packet. Wrong owner PID, stale item DBID, unreadable bag, unknown metadata, absent approval or concurrent worker must fail closed.

## Original encoded preset sets, complete offline validation
At 0x28d69e7 a tagged P/ULEB count of **204** unique ItemIDs ends at `_PHOBAN_DISCARD_ITEM_IDS` marker 0x28d6de6. All 204 match O04 metadata `Source=Items` and none is weapon. At 0x28d6e00 P/ULEB count of **10** unique IDs ends at `_PHOBAN_DISCARD_MED_IDS` 0x28d6e34. All 10 match `Source=Medicines`, none weapon. Combined 214 distinct templates, NOT 214 live bag items.
Phó bản names `discard_equip`, `discard_items`, `discard_meds` and labels Vứt trang bị/vật phẩm/thuốc. Train has `discard_nonweapon`, `discard_weapons`; Daily has `discard_equip`. Dynamic exact Python rule constructor branches not recovered.

## Keep-mode UI — key distinction
| Radio Nhặt đồ | Mode | discard preset keys | Semantic |
|---|---|---|---|
| Không | `none` | `discard_weapons`, `discard_nonweapon` | Keep nothing; can discard eligible items |
| Chỉ vũ khí | `weapons` | `discard_nonweapon` | Keep weapons |
| Tất cả | `all` | `[]` | Keep all; no discard |

Decoded original `KEEP_PRESET_KEYS` at 0x28d6fa5 and default `KEEP_MODE_DEFAULT=all` at 0x28d6ffd. **Radio keep-mode `none` is potentially destructive; no selected rules/presets is the opposite (safe no-op).** Do not conflate them.

## Cross-tab working interfaces (not live test)
`farm_tab` and `donvang_tab` invoke train/radio filtering; `slots_after=None` can mean no filter or read error. `phoban_tab` worker calls chosen presets in order equipment→items→meds **sequentially within each account** but runs multiple active accounts in parallel, skipping an account while prior discard unfinished. `daily_tab` runs parallel account worker with busy skip. `train_lsv_tab` doc polls bag slots about every 10 sec and only discards if full. `debug_tab` has an expressly **read-only, no-packet** diagnostic. Call references and embedded docs do not prove all live actions work.

## Phase O research handoff and blockers
O01 (module authority), O02 (memory_reader/GameAssembly/process), O03 (bag Site10 vs trade Site200), O04 (29983 metadata and 5477 weapon ItemIDs), O05 (presets and item safety) collectively cover Phase O **STATIC** requirements. Unknown: name case/protect precedence, UI confirm at every caller, native/packet result, cancellation/races/PID reuse and live game behavior. Stage S reconstructed application source and Stage T build workflow NOT_STARTED.

## Future tests — all NOT_RUN on reconstructed app
| ID | Case |
|---|---|
| O05-01 | Empty rules no memory scan/no packet |
| O05-02 | Default bag site 10 prevents trade-site accidental selection |
| O05-03 | Rule fields AND; rule list OR |
| O05-04 | item_ids compared to template ItemID not dbID |
| O05-05 | Metadata name_contains case/Unicode tested |
| O05-06 | src/equip_types and missing META safe |
| O05-07 | match_weapons explicitly opted in |
| O05-08 | allow_weapons default false |
| O05-09 | protect_ids and protect_names highest priority |
| O05-10 | dedupe item-instance dbID across presets |
| O05-11 | plan_discard returns target preview and sends nothing |
| O05-12 | dry_run never calls abandon_item |
| O05-13 | per HWND _send_lock_for prevents concurrent double send |
| O05-14 | stop_check and stopped/skipped counters correct |
| O05-15 | on_progress/delay keeps Tk responsive |
| O05-16 | all result counters accurate and failure not success |
| O05-17 | Packet 100005 4:dbID only after informed approval |
| O05-18 | whole-stack warning for every destructive caller |
| O05-19 | Phoban 204 Items + 10 Medicines templates validated |
| O05-20 | keep none is discard presets while no-rules is no-op |
| O05-21 | keep weapons excludes weapon IDs |
| O05-22 | keep all default never drops |
| O05-23 | Phoban per-account parallel and sequential preset/busy skip |
| O05-24 | Daily parallel busy skip |
| O05-25 | Train LSV requires full bag |
| O05-26 | PID reuse/stale dbID fails closed |
| O05-27 | full rebuilt EXE runtime and UI parity |

Static ZIP+hash+CRC and P sets full META joins were independently verified as research, not product test PASS.

## Result and NEXT_ACTION
O05: STATIC_BAG_FILTER_RULE_PRESET_AND_DESTRUCTIVE_SAFETY_AUDITED / LIVE_DISCARD_PARITY_DEFERRED. Phase O: STATIC_MEMORY_ITEM_RESEARCH_HANDOFF_COMPLETE / LIVE_PARITY_DEFERRED.
NEXT_ACTION **P01 — emulator original module authority and dormancy** (`emu_input`, `emu_reader`, `emu_remote`, `emu_setup`, `emu_chat`, `emu_farm_tab`, `debug_android_tab`). Verify actual active UI wiring before claiming emulator controls. Phase Q Proxy/no-development lock stays in effect.
