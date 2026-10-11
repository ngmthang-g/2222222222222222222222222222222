# STATE — TLMTool 2.1.2 reconstruction

_Last checkpoint: 2026-10-11. Source of truth for scope: PLAN.md and SCOPE_LOCK.md. Full earlier checkpoints: PROJECT_STATUS.md._

## Latest milestone — S137 VERIFIED (OFFLINE ORIGINAL ITEM CATALOG)
- **Real frozen original item metadata, not test-game data.** Exact original 2.1.2 `META`: **29,983 ItemIDs**; original `WEAPON_ITEM_IDS`: **5,477 IDs** and 12 weapon types, exact reverse equivalence with allowed EquipType set. Independently verified original ZIP SHA c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd and inner EXE SHA 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22, unchanged.
- **[S137 native Windows CI 38150945315](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38150945315) COMPLETED SUCCESS**: **2,127/2,127** full Python tests; **351** AST/compiled files, **92** production modules. Exact metadata/weapon identity/immutability and deterministic JSON.gz exporter tests PASS; inherited native Win64 test-owned S135/S134/S133 + Train S132–S119 + Party S118/S89/S91/S93 + Login S117/S116 PASS. Genuine signed Info product gate still **`EXPLICITLY_BLOCKED_NO_GUI_NOT_PRODUCT`**.
- **[Independent S36 Windows packaged diagnostic CI 38150945277](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38150945277) COMPLETED SUCCESS** (PyInstaller executable still **DIAGNOSTIC ONLY — NOT PRODUCT**); [Stage S source regression 38150945306](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38150945306) SUCCESS.
- Full original catalog independently exported as local gzipped JSON (29,983 rows, 5,477 weapons, 193,833 bytes). SHA256 e9322e4c6e5f0a832ae76316ad9be5fc9dc0fd2ebd0043f02bef0da360fb220a. Offline developer exporter in repo regenerates it from user-supplied original ZIP.
- **Prior S136** remains VERIFIED STATIC ONLY (2,095 Windows units, 348 compiled); S119–S136 production source preserved.

## S137 files created
- `src/original_item_catalog.py` — actual original offline ItemID lookup and weapon set, exact ZIP/EXE sha, frozen mapping, no missing ID guessing, no game reader
- `tools/S137_EXPORT_ORIGINAL_CATALOG.py` — separate opt-in complete sorted/deterministic catalog exporter and metadata digests
- `tests/test_s137.py` — 32 tests
- `.github/workflows/s137-original-item-catalog.yml`
- `docs/memory/S137_ORIGINAL_CATALOG_EVIDENCE.json`
- `docs/tasks/S137.md`
- `STATE.md` and `PROJECT_STATUS.md` milestone records
- Original frozen ZIP/PLAN/B04/S59, DATA-2222 repo and all previously verified modules **UNMODIFIED**.

## What's complete / actively blocked
- **COMPLETE S137:** truthful reusable FULL original catalog and weapon classification by template ItemID. Unknown/invalid IDs remain unknown; `get_bag` behavior and live ItemData are not fabricated.
- **BLOCKED:** legitimate original signed Info/server/heartbeat; current game build attestation; real RoleData / Items and dictionary layout; actual `read_bag/get_bag` exception/tuple and sort semantics; live Farm FSM actions/party/shop, original UI/EXE functional parity. Actual game memory was never read; test-owned Win64 native tests do not attest game compatibility. No independent signed Info issuer was supplied.
- **Do not modify:** PLAN.md, original ZIP and original binary evidence, B04/S59, previously VERIFIED S119–S136, no Proxy runtime, DATA-2222 is strictly READ ONLY. No fake role names, bag contents, game packets, signed tokens or live game buttons.

## NEXT_ACTION S138
1. Read LIVE `PLAN.md`, `STATE.md`, `PROJECT_STATUS.md`, `docs/tasks/S137.md`, O03/O04 and authentic original source/build evidence. Work toward evidence-backed *functional* capability: retain the original verified static metadata catalog and determine if an independent offline deployment resource can be safely used, or pursue legitimate signed Info + current game build validation rather than repeated artificial bag-memory demos.
2. Keep original TLM as absolute functional/UI reference, all prior S119–S137 code stable, no Proxy, DATA-2222 READ ONLY; **do not wire unverified memory offsets to the real-game adapter**, invent gameplay actions or bypass entitlement.
3. If code changes, require >= **2,127 Windows full tests**, >= **351 compiled**, inherited S137–S116 relevant real Win64 native regression and independent S36 packaged diagnostic fail-closed. Append exact tests, modified files, blockers and **NEXT_ACTION S139** to STATE and PROJECT_STATUS.
