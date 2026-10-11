# STATE — TLMTool 2.1.2 reconstruction

_Last VERIFIED checkpoint 2026-10-12 Asia/Bangkok. PLAN.md / SCOPE_LOCK.md authoritative; PROJECT_STATUS.md append-only history._

## S162 VERIFIED — FIXED ORIGINAL F05 PC PROCESS QUOTA UNDERCOUNT, BOTH EXE SPACING VARIANTS, REAL WIN64

### Live restart / true original evidence
- Read LIVE PLAN/STATE S161 NEXT_ACTION S162, S161 report, PROJECT_STATUS, SCOPE_LOCK and genuine existing S26/S160/S161 code. **Verified original frozen 47,450,112-byte inner EXE READ ONLY** from the user ZIP, SHA256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`. Original `permission_guard._is_game_process_name` documentation near raw offset **0x02b83815–0x02b83ab1** explicitly says running image names **`Thần Long Mobile.exe` (ONE space) and `Thần Long  Mobile.exe` (TWO spaces)** BOTH count toward game account limit. Existing S160 mistakenly counted only double-space → actual account-limit undercount. Original psutil/tasklist implementation/cache detail still UNKNOWN; this task only repairs the source-proven name predicate.

### Scoped correction, no unnecessary rewrites
- **MODIFY only `src/login_running_process_capacity.py`**: frozen source-grounded `RUNNING_GAME_PROCESS_IMAGE_NAMES` accepts precisely the original ONE/TWO space names using Unicode casefold. Reuses existing S160 Toolhelp Win64 Process32FirstW/NextW enumerator and distinct PID validation/unknown-count denial unchanged.
- **MODIFY only `tests/test_s160.py`**: one obsolete prior assertion expected 2 of 3 variants, now correctly expects 3. Preserves all other tests.
- NEW `tests/test_s162.py`: **12** cases, two original image names plus near misses, process dedupe/Unicode, S26 capacity with existing S161 emulator integer, signed Info denial, and F04 canonical double-space executable still strict.
- NEW `tools/S162_WINDOWS_DUAL_GAME_NAME_COUNT_SMOKE.py`: creates **two ACTUAL TEST-OWNED Windows subprocesses** (copies of system cmd.exe) with original Unicode ONE- and TWO-space image names after refusing if preexisting namesake process; native Toolhelp32 snapshots prove **two distinct live PIDs** count, original F05 cap 2 + extra-one **DENIES**, stopping only the one-space owned PID causes count=1 and preflight-only capacity allowed; no game/Info/inject/Proxy. **11/11** true native conditions PASS.
- NEW `.github/workflows/s162-f05-dual-game-name-count.yml`: PR full unit/S86/native S162 + inherited S161/S160/S26/S159..S146 and strict signed Info product negative gate.
- **IMPORTANT SEPARATION:** `src/login_path.py` F04 canonical selected launch EXE **still `Thần Long  Mobile.exe` with TWO spaces**; `src/start_windows.py` Start/HWND predicate unchanged. The **running PROCESS COUNT** alone accepts both original variants; it does NOT authorize starting arbitrary files.
- Frozen original ZIP/EXE, PLAN/SCOPE_LOCK, screenshots B04/S59 and reference `ngmthang-g/clinent-game-than-long-DATA-2222` **STRICTLY READ ONLY**; Proxy excluded. No user-visible fake control, no game memory, no full product built.

### Verified real Windows CI, head b9cbedacc3ce7973d862f4cd8345da28324aca2b
- [S162 Win64 native **38178958805**](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38178958805), job **114587230859 COMPLETED SUCCESS**: **2491/2491** Windows Python units, S86 **410 compiled files / 104 src modules**, marker `PASS_NATIVE_S162_WIN64_BOTH_GAME_IMAGE_SPACING_PIDS_TEST_OWNED` **11/11** checks; S161 ADB protocol test-only, S160 actual Win32 process counting, S26 and prior S159..S146 all native PASS. Signed Info `S162_PRODUCT=EXPLICITLY_BLOCKED_NO_GUI_NOT_PRODUCT`. Native artifact **11716977829** TEST ONLY.
- [Inherited S160 Win64 **38178958738**](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38178958738), job **114587230434 SUCCESS**: **2491/2491** and genuine S160 Toolhelp native, artifact **11717077600**.
- [Independent S36 Windows packaged DIAGNOSTIC **38178958783**](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38178958783), job **114587230499 COMPLETED SUCCESS**: **2491/2491**, Windows PyInstaller one-dir **DIAGNOSTIC ONLY** built and launched, `PASS_NATIVE_S36_PACKAGED_DIAGNOSTIC_FAIL_CLOSED_NOT_PRODUCT`, `S36_PRODUCT_EXE=NOT_BUILT`, test-only artifact **11716782180**. **NOT** the user product.
- [Stage S **38178958725**](https://github.com/ngmthang-g/2222222222222222222222222222222222222/actions/runs/38178958725), job **114587230412 SUCCESS**: **2491/2491** tests.
- Reviewed [PR #16](https://github.com/ngmthang-g/2222222222222222222222222222222222222/pull/16), exactly five changed source/test/native/workflow files. Marked ready, squash-merged main at **`af4514c8d395e5d5202093a7a605cec546a38bf2`** only after all four workflows green. NEW `docs/tasks/S162.md`, `docs/memory/S162_DUAL_WINDOWS_GAME_EXE_NAMES_NATIVE_EVIDENCE.json`, appended PROJECT_STATUS.

### Remaining actual product blockers
- Signed Info original issuer/heartbeat/token is NOT verified, real LDPlayer/Android game running ADB not tested, original game executable and suspended x64 DLL injection/F06 Login not built, external G03 RoleName/team, C12/C14 original geometry/behavior and C19 input remain incomplete. The Windows Toolhelp image name is not cryptographic game identity; actual CI used renamed cmd.exe deliberately. S36 EXE remains diagnostic only.

## NEXT_ACTION S163
1. Read LIVE PLAN/STATE/S162 and newest PROJECT_STATUS, preserve S160/S161/S162 native code and existing verified controls. Do not invent a new independent test-only helper as progress.
2. Prioritize a **distinct original-backed substantial user-facing Login/Start behavior** with actual native user effect. Inspect original F06 Login and existing sources for a usable verified action, or original signed Info issuer/heartbeat/blocker. If needed external game/account/issuer not available, record exact blocker rather than fake a Login button, bypass Info, inject unknown x64 DLL or claim product parity.
3. If source changes: PR-real Win64 >=2491 Python unit, >=410 compiled files, S162 true dual-name Win32 native and S161/S160/S159..S146 regressions, independent S36 packaged DIAGNOSTIC and Stage S, signed Info negative gate. Original ZIP/PLAN/SCOPE_LOCK/B04/S59 and DATA-2222 read-only; Proxy excluded. Log real code/CI errors and NEXT_ACTION S164 only after a verified meaningful milestone.
