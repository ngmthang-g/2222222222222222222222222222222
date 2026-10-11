# STATE — TLMTool 2.1.2 reconstruction

_Last checkpoint: 2026-10-11. Absolute scope authority: PLAN.md + SCOPE_LOCK.md. Historical task ledger: PROJECT_STATUS.md._

## Latest completed task — S138 VERIFIED (OFFLINE ORIGINAL METADATA RESOURCE)
- Original `item_meta_data.META` **29,983** ItemIDs + original `weapon_ids` **5,477** IDs from frozen, SHA-pinned `TLMTool 2.1.2` EXE. Never executed original game/client. S137 independently decoded original ZIP; S138 supplies an **explicitly invoked, immutable 193,833-byte JSON.gz resource loader and offline diagnostic lookup without the 90 MB original ZIP**.
- SHA256 original gzip `e9322e4c6e5f0a832ae76316ad9be5fc9dc0fd2ebd0043f02bef0da360fb220a`; original underlying ZIP `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, original EXE `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Locally produced user-downloadable **`S138_TLMTool_Original_Item_Catalog_Offline.zip`**, **171,308 bytes**, SHA256 `e6bb745c035d3cbc41f3523ec7375c15d1052ae5605cb4b3daa0efb1c8ae5c00`. This local utility has a **self-contained** Python lookup whereas the GitHub packager recipe uses source modules; both are diagnostic only, NOT byte-identical source package layouts. Tested extraction + `ItemID 10100000` => `Thanh Đồng Đao`, absent ItemID -123 => UNKNOWN, corrupted gzip => BLOCKED; no actual game interaction.
- **[FINAL S138 Windows 38151954344](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38151954344) COMPLETED SUCCESS**: **2,153/2,153** Python full Windows tests, **355** compiled, **93** source modules; S138 no-resource failure returns fail closed; inherited native Win64 S135/S134/S133 plus Train S132–S119, Party S118/S89/S91/S93, Login S117/S116 all PASS; real signed Info product gate `EXPLICITLY_BLOCKED_NO_GUI_NOT_PRODUCT`; artifact `11706931686` TEST ONLY.
- Independent **[S36 Windows diagnostic 38151664684](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38151664684) COMPLETED SUCCESS**, [Stage S regression 38151664694](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38151664694) COMPLETED SUCCESS. S36 PyInstaller EXE is still a diagnostic and **NOT** functional original TLMTool.
- Earlier S138 CI runs failed exclusively for new PowerShell logging directory and expected-exit-code handling; the last workflow corrects both. See docs/tasks/S138.md.

## Files changed in S138
- NEW `src/original_item_catalog_resource.py` — exact SHA-pinned immutable offline resource loader
- NEW `tools/S138_CATALOG_LOOKUP.py` — CLI ItemID lookup, status 0 found / 3 unknown / 2 invalid
- NEW `tools/S138_PACKAGE_OFFLINE_CATALOG.py` — deterministic offline portable ZIP recipe
- NEW `tests/test_s138.py` — 26 Python unit tests
- NEW `.github/workflows/s138-offline-catalog-bundle.yml` — full Windows source/native regressions; PowerShell output issue corrected
- NEW `docs/memory/S138_BUNDLE_EVIDENCE.json` and `docs/tasks/S138.md`
- Updated `STATE.md` and append-only `PROJECT_STATUS.md`
- Existing S119–S137 code, frozen `PLAN.md`, original ZIP/manifest, B04/S59, user game DATA reference **UNCHANGED**, Proxy not developed.

## Current state and blockers
- **S138 DONE FOR OFFLINE CATALOG ONLY.** Neither the standalone offline ZIP nor the GitHub resource loader is the 1:1 TLMTool product. No game HWND/memory access, real Bag Site10 read, live Farm/Train actions, web account data, GUI product unlock or Info bypass.
- **BLOCKED:** original genuine signed Info issuer/token/heartbeat; current legitimate game build and validated RoleData/Items dictionary field offsets/count/entry stride; real `memory_items.read_bag/get_bag` error/tuple semantics; original gameplay FSM/shop/autopath and full UI/EXE parity. Do not claim a test-owned Win64 fixture is genuine game proof.

## NEXT_ACTION S139
1. Re-read LIVE `PLAN.md`, `STATE.md`, `PROJECT_STATUS.md`, `docs/tasks/S138.md` and original O01/O02/E01 Info and Train source evidence. Prioritize substantive original-backed **genuine runtime permission/build discovery and an independently verifiable remaining functionality**, not more synthetic bag reader loops.
2. Do not invent game offsets, signed Info providers, packets, UI buttons, training actions or version compatibility. Preserve S119–S138 verified source and original ZIP/PLAN/B04/S59; DATA-2222 STRICTLY READ ONLY; Proxy excluded.
3. For source edits require >=**2,153** full Windows unit tests, >=**355** compiled, relevant native inherited S138–S116, and independent S36 diagnostic fail-closed. Record completed, in-progress, errors, file list and **NEXT_ACTION S140** to both state files.
