# S07 — B12 read-only price, contact and system catalog, native Windows validation

## Scope / exact resume
Resumed from the latest GitHub `STATE.md` `NEXT_ACTION=S07` after reading `PLAN.md`, `PROJECT_STATUS.md`, `docs/tasks/B12.md`, B12 screenshot/geometry evidence, existing S01–S06 source and S06 test/workflow. `docs/tasks/S07.md` was absent on arrival.

Reused the already-passing S06 Info frame, status border, six value surfaces, read-only changelog and lifecycle. No old research, compiled EXE, user ZIP, game-client DATA 222222, PLAN, Proxy logic or corrected **Dồn** text changed.

## What was reconstructed
Updated **only existing `src/info_tab.py`**. Original `InfoDisplay` gains default `price_text` and `catalog_text` fields set to `Chưa xác minh`, with no server adapter provided. Its existing status/license/view logic is preserved. `TLMInfoTab` now exposes B12-grounded passive content:

| B12 region | S07 Info-frame-relative anchor | Actual native Tk result |
|---|---|---|
| Price text block | `[6,427,416,88]` | **MATCH** |
| Separator after pricing | y=526 | **MATCH** |
| Support contact heading | `[7,539,300,19]` | **MATCH** |
| Facebook static label | `[27,566,126,19]` | **MATCH**, blue, not clickable |
| Zalo static label | `[155,566,110,19]` | **MATCH**, blue, not clickable |
| Separator after support | y=616 | **MATCH** |
| System catalog header | `[7,630,320,19]` | **MATCH** |
| System catalog area | `[30,656,340,58]` | **MATCH placement**, **CLIPPED on small runner** |

The B12 screenshot supports the *labels and approximate regions*, but its price figures, license content and catalog/product names are **server-fed snapshot content**, not client source defaults. S07 **does not hardcode** `200k` prices, `Lineage`/other product list, FREE plan, heartbeat, license keys or copied device identifiers. The original static strings `● Facebook` and `● Zalo` are represented only as ordinary colored **nonclickable labels**; original click destinations/activation behavior and log upload are NOT implemented. No fake `Copy`, `Nhập`, `Gửi log hỗ trợ`, update or proxy buttons.

Prior S06 status border `[3,51,416,44]`, changelog `[3,295,416,109]`, six 25-px row pitches and scroll behavior remain untouched. **This is not pixel-accurate or functional original TLM parity**.

## Newly created tests/CI
- `tests/test_s07.py`: **6** headless cases for B12 anchors, original static contact/catalog labels, blue styling and no button widgets, server-dependent values remaining unknown, revocation and safe view state.
- `tools/S07_WINDOWS_INFO_SECTIONS.py`: opens real native Windows `Tk` + `ttk` with the existing original-backed Info-only shell; checks all new `place_info` anchors and separators, `Scrollbar` remains read-only, no `tk.Button` or `ttk.Button`, no click bindings on support labels, trusted Info-only tab gating, shutdown callback, clipping detection and PNG+JSON capture. **Not a production entrypoint.**
- `.github/workflows/s07-info-sections.yml`: runs Windows Python 3.10 `compileall`, all S01–S07 unit tests, S06 existing native original-anchor regression and S07 native smoke; uploads reports/screenshots. No external licensing/game/API request.

## Verified GitHub Actions (not inferred)
Run **[37869958702](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37869958702)** at HEAD `77af1943f9cea686efebfdb8c56a3324bb87c7b0`, Windows job `113625514299`, **COMPLETED / SUCCESS**. Read the actual GitHub job logs:

- Source/test compilation **PASS**.
- Full combined S01–S07 unittest suite **43/43 PASS**, log line `Ran 43 tests in 0.017s` (S01=7, S02=8, S03=6, S04=10, S06=6, S07=6).
- S06 real Windows prior anchor regression **PASS_NATIVE_READONLY_LAYOUT_ANCHORS** (no S06 regression).
- S07 real Windows smoke: **PASS_NATIVE_PASSIVE_SECTIONS**. Rectangles exactly match the table, separators are `[37,259,412,526,616]`, `info_tab` only visible, **0 action buttons**, screenshot `CAPTURED_CLIENT_ONLY`, binding `closed=true`.
- Native test machine 1024×768, Tk client 450×688 (S05/S06 baseline). Catalog `[30,656,340,58]` extends below the Info frame height: `catalog_fully_within_frame=false`. **Placement matches**, but catalog is **NOT fully visible on short desktops**. Do not silently call this visual parity PASS.
- Artifact `s07-info-passive-sections` ID **11589688653**, with current PNG+JSON and S06 regression capture. Link: https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37869958702/artifacts/11589688653

## Remaining deviations and blockers
- Original B12 full screenshot is **452×1032** from a **450×1000 client**, with **11 visible tabs** and authenticated/server-fed UI. Reconstructed preview is unlicensed Info-only on a 1024×768 runner (450×688) and lacks functional server-fed price/catalog/support controls; native image != original screenshot and pixel diff/SSIM **NOT_RUN**.
- Original app authentication, heartbeat, production FREE/plan rules, full Start/Login/game modules, PC + emulator account count, client resource parity and Windows standalone Nuitka product **NOT IMPLEMENTED**. `src/TLMTool.py` deliberately returns code 2.
- No original package binaries/third-party game processes executed, no Proxy Phase Q development; existing S01–S06 functionality and B12 reference untouched.

**S07 STATUS:** `S07_WINDOWS_NATIVE_PASSIVE_SECTIONS_43_TESTS_PASS_CATALOG_CLIPPED_ON_768P`.

## NEXT_ACTION = S08 — start actual Start-tab functional source
Do not reimplement Info source or invent server permissions. Read original `start_tab` static evidence (B02 screenshot, E01/E03 shell, relevant original Start/UI/Win32 HWND window-discovery/task docs), check GitHub `docs/tasks/S08.md` absent, and implement the **smallest real, testable Start-tab non-Proxy function** (e.g., native Win32 game window discovery with safe read-only enumeration if original contracts justify it), preserving selection/auth gates. Then run real Windows tests and checkpoint. Avoid more decorative Info work unless needed to unblock genuine functionality. Catalog clipped on low screens remains a separately tracked visual gap, NOT a basis to change earlier passing high-resolution B12 coordinate locks without evidence.
