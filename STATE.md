# STATE — TLMTool 2.1.2 reconstruction

Last verified checkpoint 2026-10-12 Asia/Bangkok. PLAN.md and SCOPE_LOCK.md remain authority; PROJECT_STATUS.md is append-only.

## S152 VERIFIED — Existing C14 detached Win64 DWM permission-callback exception fail-closed; FULL ORIGINAL UI NOT PROVEN

### Recovered real scope without restarting PLAN
- Read LIVE PLAN.md, STATE S151 NEXT_ACTION S152, PROJECT_STATUS, SCOPE_LOCK, C13/C14 and source. Existing S68 C14DetachedDwmSession, S69 settings, S70 TOPMOST Tk host, S71 cleanup, S73/S74 independent scan, S84 actual Đóng xem and S85 close-then-reopen DWM refresh are already implemented/Windows-tested. Do NOT remake them.
- Original C14 thumbnail grid x/y and tile arithmetic, automatic open timing, Hủy tách vs Đóng xem embedded-preview visibility/restore and complete end-user Tách rời wiring remain UNKNOWN; no made-up user toggle. Frozen original ZIP SHA256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd, 93,715,901 bytes / 1,050 entries; original EXE SHA256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22, all UNMODIFIED.

### S152 actual changes
- Found reconstructed C14DetachedHost direct allowed() calls in open/render/refresh: unexpected external provider Exception after live HWND/DWM activation escaped C13 close boundary and could leave detached preview visible despite revocation. A native teardown failure returned an error but had not latched future open. NOT proof of an original TLM bug.
- EDIT ONLY src/detached_host.py: strict literal True / Exception-denied authorization helper at each existing open/render/refresh checkpoint; broader normal Exception handling on native owner/render path invokes existing C13 detached cleanup, preserving original game HWNDs; native teardown error permanently latches _refresh_cleanup_faulted for that owner lifetime. C14 region (0,768), TOPMOST, prior working DWM tile placement and existing buttons remain unchanged.
- NEW tests/test_s152.py: 12 regressions. NEW tools/S152_WINDOWS_C14_AUTH_EXCEPTION_SMOKE.py: 3 genuine test-owned Win64 Tk source HWNDs, true TOPMOST host/3 DWM registrations, throw provider AssertionError, verify all DWM unregister/destination destruction BEFORE Tk host cleanup and source HWNDs still alive, with still-denied callback no new HWND. GitHub hosted physical desktop 1024x768 cannot fit original C14; positive test uses explicitly TEST-ONLY Tk-reported 1600x1000 dimensions (real Win32 HWND and DWM, not real display proof).
- NEW .github/workflows/s152-c14-auth-exception.yml: full Windows unit/source and inherited S85/S70/S71 C14, S151 Login, S150 observer, S146/C12, original signed Info negative product gate.
- Reviewed [PR #6](https://github.com/ngmthang-g/2222222222222222222222222222222/pull/6) exact four-file diff; merge after all three Windows workflows SUCCESS, main squash commit 773e90ed470abad1b0088b573fea2f4b146b3ca7. New docs/tasks/S152.md and docs/memory/S152_C14_NATIVE_PROVIDER_FAILURE_EVIDENCE.json. No edits other product source, original PNG/PLAN/SCOPE_LOCK/ZIP/EXE, client DATA-2222 STRICTLY READ ONLY; Proxy excluded.

### Real Windows CI on PR head d044e12e665e01577201145417f5213d0422d2da
- [S152 native Windows run 38169442333](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38169442333), job 114558751215 COMPLETED SUCCESS: 2350/2350 Python unit tests; S86 383 compiled files / 97 source modules; real TEST-owned HWND and DWM S152 callback failure/cleanup PASS, inherited S85 genuine native refresh, S70 TOPMOST, S71 DWM failure, S151 native Login wheel, S150 observer and C12 native all PASS. Signed Info still S152_PRODUCT=EXPLICITLY_BLOCKED_NO_GUI_NOT_PRODUCT. Native test artifact 11713266985.
- [Independent S36 packaged DIAGNOSTIC run 38169442340](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38169442340), job 114558751353 COMPLETED SUCCESS: 2350/2350 units, actual PyInstaller one-dir DIAGNOSTIC EXE launch PASS_NATIVE_S36_PACKAGED_DIAGNOSTIC_FAIL_CLOSED_NOT_PRODUCT; S36_PRODUCT_EXE=NOT_BUILT, artifact 11713406214; NOT a user TLM product.
- [Stage S source regression 38169442328](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38169442328), job 114558751173 COMPLETED SUCCESS: 2350/2350 units.
- All tests on test-owned native Windows HWNDs; no real Thần Long, original Info verifier, native game action, Proxy, or original EXE runtime.

### Remaining original parity blockers
Real original signed Info server/heartbeat unavailable, F05/F06 login reference RGB/coordinates and real game build/RoleData/Bag memory unresolved; original C12 Hiện hết position conflict; C14 original detached per-tile geometry/embedded restoration and end-user Tách rời opener unknown; C19 native input payload, original full tabs/UI, finished user TLMTool EXE not completed. S36 EXE is test-only diagnostic.

## NEXT_ACTION S153
1. Read LIVE PLAN.md / STATE.md / docs/tasks/S152.md / PROJECT_STATUS.md. Do NOT redo existing S68/S70/S84/S85 C14 functional native stack nor S152 exception guard, or earlier S151/S150/C12 proof.
2. Find another substantial original-evidence-backed actually working user-facing Start/Login/Windows gap that can be implemented without fake buttons, guessed C14 tile spacing/restore, original Info grant, game memory or Proxy; if genuine C14 pixel/algorithm trace appears, verify before connecting the Start Tách rời button.
3. If changing code require PR-based real Windows >=2350 unit tests, >=383 compiled, new S152 C14 native and inherited S85/S70/S71, S151/S150/C12, separate S36 packaged diagnostic and Stage S, original Info fail-closed. Preserve DATA reference repo read-only; update verified files/error blockers and NEXT_ACTION S154 after a real milestone.
