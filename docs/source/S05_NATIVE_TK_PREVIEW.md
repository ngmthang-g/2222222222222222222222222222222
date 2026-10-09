# S05 — Native Windows Tk Info-only preview, B12 geometry and shutdown verification

## 1. Resume scope
Followed current `STATE.md` NEXT_ACTION S05 after reading `PLAN.md`, `PROJECT_STATUS.md`, `docs/tasks/S04.md`, original Gate-B `docs/tasks/B12.md`, `docs/ui/B12_INFO_GEOMETRY.tsv`, `docs/ui/B12_SCREENSHOT_EVIDENCE.tsv`, the original-wide UI baseline and current `src/info_binding.py`, `src/info_tab.py`, `src/shell.py`. Verified `docs/tasks/S05.md` absent. No earlier source files, previous task documentation, frozen TLMTool archive, original license controls, or Proxy-related code modified.

### New implementation/test infrastructure
- `tools/S05_WINDOWS_TK_SMOKE.py`: isolated script uses **native** `tkinter.Tk`, actual `ttk.Notebook`, actual `TLMInfoTab` and `create_info_only_shell` (S04); calls `position_window_top_right`, pumps Tk update events, records window/widget geometry, verifies Info-only visibility and no fabricated license grants, screenshots the client region where the Windows display permits, and destroys the root, validating callback cleanup.
- `.github/workflows/s05-native-info-preview.yml`: Windows GitHub Actions Python 3.10, Pillow 11.3.0 only for optional screenshot, compileall, all S01–S04 unittests, native real Tk smoke, and artifact upload of JSON+PNG.
- This is **internal and read-only** test infrastructure; `src/TLMTool.py` remains intentionally fail closed with exit code 2. Not an original TLM executable or a published user feature.

## 2. Grounded Windows Actions evidence
**Completed [S05 Actions run 37868251319](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37868251319)**, head `88d99b18a7e6a21e49b8fe23dea2c41d20b5f9c0`, job `113620048879`, overall **SUCCESS**. Actual job logs inspected:

- `python -m compileall -q src tests tools/S05_WINDOWS_TK_SMOKE.py`: **PASS**.
- `python -m unittest discover -s tests -p "test_s*.py" -v`: **31/31 PASS** (`Ran 31 tests in 0.017s`) on Windows, Python 3.10.
- `python tools/S05_WINDOWS_TK_SMOKE.py`: `S05_NATIVE_TK_STATUS=PASS_NATIVE_TK_INFO_ONLY_SMOKE`, no native Tk initialization problem, no blocked popup.
- Real Windows **desktop = 1024×768 px**. Root/Tk geometry = `450x688+564+0`, client **450×688 px**, matching the high-confidence E02 geometry model (`screenheight − 80` = 688), not the original B12 reference screenshot environment (`450×1000` client, `452×1032` full raster).
- Real ttk.Notebook: **15 potential slots**, only **`info_tab` visible**, `info_tab` is the selected key, exactly as the reconstructed fail-closed state requires. Original B12 captured **11 visible tabs** with Info at the right end (that requires legitimate permissions and real tab factories); S05 does **NOT** reproduce that screenshot state.
- Real notebook widget screen bounds: x=577, y=36, 440×678. Real selected Info content frame: x=578, y=59, 436×652. Version field actual screen bounds: x=694, y=123, 28×19. Other field values y=146/169/192/215/238. Status label x=588,y=94,416×19. These are **desktop coordinates**, not directly B12 screenshot-local pixels.
- Status text is `Chưa xác minh dữ liệu máy chủ`; license type displays `Chưa xác minh`. No other functionality or dev tab exposed. Tk root destroyed with S04 close handler, no callback resurrection and binding marked closed.
- Pillow `ImageGrab` captured actual **450×688 client-region PNG**, NOT original full-window raster. GitHub Action `s05-native-tk-preview` artifact **ID 11589735180**, contains **two files** (PNG and `windows_tk_report.json`) and is linked from the run. Screenshot capture success does **not** prove screenshot parity.

## 3. B12 original geometry versus actual current S05

| Criterion | Original locked B12 | Native Windows S05 | Verdict |
|---|---|---|---|
| Client width | 450 px | 450 px | **MATCH** |
| Client height | 1000 px in 1080-screen baseline | 688 px on 768-screen runner | **DIFFERENT ENVIRONMENT** (E02 screen-height model PASS) |
| Outer decorated raster | 452×1032 in B12 environment | Not measured on S05 | **NOT_VERIFIED** |
| Tab strip | 11 visible original tabs; Info at right | 1 Info visible; 15 potential slots | **EXPECTED PARITY GAP** (auth + feature factories absent) |
| Notebook top | y≈36 | y=36 absolute desktop | Similar number; reference coordinate systems differ, do not infer pixel exact |
| Info status panel | Original colored 416×44 box and 5 version modes | Current read-only text label 416×19 | **MISSING PANEL STYLING** |
| Six info value surfaces | White boxes at 25px vertical spacing | Passive ttk.Label rows at ≈23px spacing | **PARTIAL / NOT RASTER PARITY** |
| Changelog | Scrollable text+scrollbar, server data | Passive label, unknown text | **MISSING SCROLLABLE VIEW** |
| Copy/Enter/support log buttons | Present and functional in original | Withheld, no verified action implementation | **UNIMPLEMENTED BY DESIGN**, never fake |
| Token/server values | Dynamic authenticated values or B12 captured snapshot | Explicit `Chưa xác minh` | **CORRECT FAIL-CLOSED STATE**, not B12 static-copy parity |

The original screenshot **PNG bytes have not been loaded in this task**. The original B12 geometry and SHA are documented on GitHub, but no side-by-side full pixel difference image or SSIM/MAE check ran. **Do not call the GUI pixel-parity PASS.**

## 4. Scope and remaining blockers
- Static/GUI integration **proven on Windows** for native tkinter, actual widgets, 450 px width, fail-closed Info and clean close; headless regressions 31/31 also verified on that runner.
- No production auth verifier, real TLM Info server RPC, server-fed changelog/prices, heartbeat grace or default FREE policy, Windows app feature controllers, device/game handling, full 11-tab rendered state, DLL integration, Stage-T Nuitka EXE build or original-vs-rebuild pixel parity.
- All previously correct modules remain untouched. Proxy Phase Q stays NO DEVELOPMENT. Client DATA 222222 can be read only for later **game-client-specific** gaps, not used to invent licensing details.
- **Status: `S05_NATIVE_WINDOWS_INFO_TK_PASS_B12_PIXEL_PARITY_NOT_YET_VERIFIED`**. A real Windows Tk test and image exist; a distributable product does not.

## 5. Handoff
**NEXT_ACTION S06:** Do not re-run S05 research from scratch. Compare the captured S05 preview with B12 reference **as geometry evidence**, then incrementally implement **only verified passive Info status panel/row/changelog layout** (not inactive Copy, Enter, log upload or unverified server values). Add native Tk geometry tests on Windows, reuse S05 workflow and artifact collection. Keep exact authentication and tab-gate unknowns explicit, and the normal program entrypoint blocked until genuine service and real feature logic exists.
