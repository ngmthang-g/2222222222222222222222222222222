# S207 — Owner-requested Windows DEV TEST EXE artifact (not gameplay-complete)

**Build/CI verified on real GitHub Actions Windows x64, owner live-game tests still NOT RUN.** On 2026-10-13, owner explicitly requested a usable tool folder/EXE to start Windows testing even though core gameplay code is not 100% ready. This specific DEV TEST packaging/smoke request supersedes the earlier *defer all intermediate tests* preference ONLY for this owner-requested isolated test artifact; the production final combined gameplay acceptance remains outstanding.

## Artifact and provenance

- Current source branch: `plan-source-first-defer-final-test`; frozen `PLAN.md`, `SCOPE_LOCK.md`, original TLM 2.1.2 ZIP/EXE, reference DATA-2222 all left unchanged.
- New workflow: `.github/workflows/s207-dev-test-build.yml`, Windows-latest x64 / Python 3.10.11 / PyInstaller `--onedir --console --noupx`, bundled entrypoint `src/TLMToolIndependent.py` (NEW independent tool, no original signed Info license / heartbeat / Proxy).
- **Windows GitHub Actions run:** https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38331640985 — **SUCCESS**.
- **Built exact branch commit:** `394d89976cf03d26843dc06f95f9cf40fe04c26e`.
- Artifact: `TLMTool_DEV_TEST_WIN64_PARTIAL_S207`, GitHub artifact ID **11782593428**. A downloaded portable package is also supplied to user in conversation: `TLMTool_DEV_TEST_WIN64_S207.zip`.
- ZIP directory includes `TLMTool_DEV_TEST.exe`, the full accompanying `_internal` PyInstaller dependencies folder, `START_DEV_TEST.cmd` (launch from same folder), `README_DEV_TEST.txt`, `SELF_CHECK_RESULT.txt`, `SOURCE_COMMIT.txt`.
- Windows source syntax compilation: PASS. Direct source `--self-check`: PASS. PyInstaller Windows x64 folder build: PASS. Packaged actual EXE `--self-check`: PASS. **Actual native GUI window startup / responsive HWND+PID / singleton duplicate protection / WM_CLOSE teardown / reopen** via existing `tools/S174_WINDOWS_PACKAGED_GUI_SMOKE.py`: **PASS**. These are actual packaged Windows process checks on a CI-owned desktop; **NOT** an actual game/login/workflow verification.

## What owner can test safely now

- Native Windows GUI startup/close, 11 independent tab navigation, saved local settings.
- Real OS HWND/PID discovery and recognition of user-existing game windows, click-to-activate the real window when applicable.
- Login F04 selected game directory and F05 NORMAL Windows Popen game launcher (original hooked/suspended DLL bootstrap is NOT included).
- Read-only original compiled TLM memory RoleData diagnostic; Party/Train numeric/name/HP/MapID are explicitly **candidate/unverified** and may fail on user client. No fake logged-in status or authentic team proof.
- Original 65-key original pixel catalog; user-triggered PrintWindow RGB/ROI read-only diagnostics in Login / Phó Bản / Dồn Vàng; may fail due native client rendering mismatch.
- Host CPU/GPU status and real local configuration editors for Train/TrainLSV/Daily/Dồn/Rao/Phó Bản.

## Core NOT COMPLETE / do not call 100%

- F05 original client DLL-assisted bootstrap; F06 actual credential entry, captcha and server-login confirmation; Party actual invite/join/formation; Train auto-path/auto-attack/revive; Phó Bản/Donation/Shop/Bag actual actions. Old `mouse.click_at` relies on a version-proxy hook and dangerous `pack(100)` real-mouse lock with `pack(99)` restore, which the independent tool intentionally does not inject. No verified sender; no click or credentials sent by the new read-only diagnostic panels.
- No real user game runtime test completed in GitHub CI; cannot certify original-game role name/% health or functionality parity from self-check/native Tk alone.
- User should EXTRACT ZIP to NEW directory, keep `_internal` next to the EXE, double click `START_DEV_TEST.cmd`, perform safe read-only tab/Window/ROI tests and send screenshots/console log for failures. DO NOT overwrite original TLM install or count read-only pixel matches as game automation.

## NEXT_ACTION — S208

Owner live Windows DEV TEST: obtain actual screenshots and failure codes of the current independent GUI and Start/Login/Party/Train/FuBen/Dồn read-only observations. Repair concrete runtime issues in staging branch, rebuild test ZIP, then proceed to game action sender only when recipient/protocol/abort/restore source evidence is complete. Preserve original read-only assets, do not claim 100% gameplay parity. Main STATE should distinguish verified GitHub Windows packaged GUI startup versus still-untested real game behavior.
