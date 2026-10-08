# O04 — Embedded Item Metadata and Weapon ItemID full binary audit

## Authority
- GitHub HEAD before work: 38e7629d9110c73aa237c13b9a45bc372b4d626d; PLAN.md and STATE.md specify O04. O01–O03 completed and kept unchanged.
- Frozen archive SHA-256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd (1050 entries, CRC clean), original inner EXE SHA-256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22 (47450112 bytes). EXE/game were never executed.
- Complete Nuitka serialized item_meta_data (0x2977206, 1989514 bytes) and weapon_ids (0x2c54798, 27719 bytes) decoded read-only, not estimated from module top-level constant counts.

## Full metadata result
- At 0x29772d3, tagged D 9f ea 01 yields 29983 entries. Exactly 29983 unique u-tagged UTF8 decimal key strings precede 29983 T4 record tuples (Name,Icon,Source,EquipType). End marker aMETA appears at 0x2b5cd71.
- Five Source counts: Equips=22776; Items=5289; Gems=1154; Medicines=694; PetEquips=70. All 29983 records have nonblank Name and Icon, but only 12835 distinct Names and 4082 distinct Icons. Names and icons are **not unique item identifiers**.
- 7207 non-Equips entries use EquipType None; all 22776 Equips records have a type. Serialized META keys are numeric text; audit normalization to integer for joins does not prove original Python load_meta conversion.

## Full weapon-set result
- WEAPON_TYPES at 0x2c54890: 0, 1, 2, 3, 4, 5, 6, 7, 8, 16, 17, 100. Set marker S e5 2a at 0x2c548b8 decodes 5477 unique l-tagged numeric ItemIDs, followed exactly by ais_weapon at 0x2c5b3b4.
- Exhaustive cross-join: all 5477 weapon IDs appear in META, all Source Equips, all use the twelve weapon types. In reverse, every META Equips entry with one of those types is present in WEAPON_ITEM_IDS. Zero missing on either side **for this pinned EXE**, not a claim about all live game versions.
- The other 17299 Equips records are non-weapons by this set. Do not infer a weapon from Source Equips alone or from duplicated translated display names.

## Weapon type counts
| EquipType | ItemIDs |
|---|---:|
| 0 | 600 |
| 1 | 736 |
| 2 | 1056 |
| 3 | 601 |
| 4 | 618 |
| 5 | 627 |
| 6 | 213 |
| 7 | 213 |
| 8 | 208 |
| 16 | 218 |
| 17 | 202 |
| 100 | 185 |

## Consumers, fallback and safety
- memory_items imports embedded item_meta_data.META and weapon_ids.is_weapon. Original constants also contain item_meta.csv/item_icon_list.csv for source/dev fallback; the frozen ZIP lacks these separately named CSV/XML files but includes embedded metadata.
- Exact original Python conversion of META key type, missing/invalid ItemID behavior, fallback order and live weapon classification remain UNKNOWN. This task proves static embedded data, not live bag ItemID coverage.
- O01/O03 bag_filter constraints remain: weapon protection default, empty rules mean no discard, and no item action is authorized by metadata lookup. O05 will audit precise filter rules, user selection and destructive packet safeguards.

## Reproducibility and gates
- Data was decoded using a hash-pinned, read-only Python auditor (available as a separate file). Format: D unsigned-varint count, u/NUL keys, T4 tuples with a/u/w/n fields; weapon L 12-type list and S unsigned-varint item set. Both exact end markers verified.
- docs/memory/O04_DATA_METRICS.json stores counts and original offsets; docs/memory/O04_STATIC_EVIDENCE.tsv stores evidence and uncertainty. No rewritten fake item catalog was generated.

## Future acceptance — ALL NOT_RUN ON REBUILT APP
| Test | Requirement |
|---|---|
| O04-01 | Match pinned original ZIP/EXE SHA and CRC |
| O04-02 | Decode full 29983-key metadata map and tuple shape |
| O04-03 | Verify all five category counts and None EquipTypes |
| O04-04 | Preserve unique ItemID instead of duplicate Name/Icon |
| O04-05 | Decode exactly 12 weapon EquipTypes |
| O04-06 | Decode 5477 unique integer weapon IDs |
| O04-07 | Verify every weapon ID belongs to META |
| O04-08 | Verify Source Equips and weapon EquipType for all weapon IDs |
| O04-09 | Verify reverse Equips+type set equals weapons for this binary |
| O04-10 | Ensure metadata key string/int normalization matches original runtime |
| O04-11 | Handle unknown/malformed ItemID without false match |
| O04-12 | Render live bag Site10 Name/Icon/Source/Type correctly |
| O04-13 | Verify dev-mode CSV fallback if embedded module absent |
| O04-14 | Use embedded META with no separately packaged CSV |
| O04-15 | Ensure runtime is_weapon classifies by template ItemID |
| O04-16 | Do not treat all 22776 Equips items as weapons |
| O04-17 | Preserve weapon protection when lookup errors occur |
| O04-18 | Diagnose changed game/catalog version conservatively |
| O04-19 | Verify audit causes no use/drop/destroy item action |
| O04-20 | Verify rebuilt Windows EXE metadata and functional parity |

All 20 are planned tests, not PASS results for a reconstructed application.

## Status and NEXT_ACTION
**O04 = EMBEDDED_META_AND_WEAPON_DATA_FULLY_DECODED_STATIC_AUDIT / LIVE_CLASSIFIER_AND_BAG_PARITY_DEFERRED**.
**NEXT_ACTION: O05 — bag_filter activity presets, _match_rule fields, protect_ids/protect_names and weapon opt-in precedence, plan_discard dry_run, discard_items stop_check and packet 100005 safety.** Original EXE first; never actually drop/use/destroy an item. Keep N/O01–O04 and Proxy scope lock.
