# S08 — Genuine read-only Win32 Start discovery / HWND+PID identity

## 1. Authorized resume and boundaries
User approved S08 after S07. Re-read live GitHub `PLAN.md`, `STATE.md`, `PROJECT_STATUS.md`, `E01`, `E03`, `B02`, `B03`, `F01`, `D08`; checked `docs/tasks/S08.md` absent. Read original **`docs/tasks/C01.md`** (window discovery) and **`docs/tasks/C02.md`** (HWND/PID identity) in full. Prior S01–S07 actual source/tests and B12 Info screen left unchanged, as were original frozen EXE, data repo, PLAN, Proxy lock and user spelling Dồn.

**Original frozen binary authority:** `TLMTool.dist/TLMTool.exe` SHA256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`. Original compilation markers were previously verified in C01/C02; this S08 milestone did **not** run or decompile the original EXE again. Do not misrepresent source-level expression recovery.

## 2. Verified original Start contract and implementation choices

| Area | Evidence from original C01/C02 | S08 implementation | Confidence |
|---|---|---|---|
| Top-level discovery | EnumWindows + visible only | ctypes `user32.EnumWindows`, `IsWindow`, `IsWindowVisible` | Real Win32 API tested |
| Safe title | SendMessageTimeoutW 150 ms avoids indefinite hang | WM_GETTEXTLENGTH + WM_GETTEXT; both capped at 150 ms | Native test of ordinary Tk title, **hung game window NOT_RUN** |
| Process identity | GetWindowThreadProcessId + original psutil.Process | GetWindowThreadProcessId, `OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION)`, `QueryFullProcessImageNameW` | Compatible read-only adaptation; not original psutil code |
| Game name | normalized target `thần long mobile.exe` (whitespace variants) | Unicode casefold + whitespace compaction | Original exact normalizer unproven |
| Unity class | `UnityWndClass` and title predicate | require exact game process AND (UnityWndClass OR compacted exact `Thần Long  Mobile` title) | **Conservative S08 choice, original Boolean grouping UNKNOWN** |
| Debug fake accounts | `FAKE_ACCOUNTS` exists separately in original | No synthetic handles accepted; Windows EnumWindows only | S08 deliberate strict physical-mode exclusion |
| Anti-wrong-account | C02 HWND+PID generation snapshot; reuse removes old row | `WindowRegistry.update` with `added/removed/reused`; `identity_matches` | Test-supported C02 reconciliation |
| Cadence | background discovery ~3 s, UI poll 2 s on Start, memory ~8 s | Only synchronous one-snapshot backend, **NO timers, NO memory**, no Tk binding | Explicit future Stage S09 |
| Game action | separate strict window title resolver, memory reading and click layer | **No clicking, no memory, no injection, no window move, no game process launch** | Deliberately out of scope |

**Important:** `discover_game_windows` is a bounded *single read-only snapshot* and **must not be called from Tk's UI thread as if the ~3s Start background worker were already reconstructed**. `SendMessageTimeoutW` limits individual cross-process message waits, but many candidates could still incur cumulative latency. The later asynchronous producer and Tk 2s consumer belong to S09.

**Native API details:** `src/start_windows.py` lazily loads Win32 ctypes only on Windows, uses Unicode and strongly typed signatures, limits title buffers to 512 characters and message timeouts to 150 ms each, filters windows on process first and checks the HWND/PID again after timed title reads. `OpenProcess` requests query-only rights; no VM_READ, VM_WRITE, code execution or helper DLL.

## 3. Created source and tests

New `src/start_windows.py`:
- `GameWindow` immutable model with true HWND, PID, title, class, process name;
- `NativeWin32Backend` calling actual user32/kernel32 APIs;
- `is_game_candidate` explicit conservative filter;
- `discover_game_windows` read-only, visible top-level, no fake/hung/unreadable windows;
- `WindowRegistry` HWND+PID association, added/removed/reused deltas and anti-stale identity check.

New `tests/test_s08.py` **12** stdlib tests using a fake adapter (only in test code): normalized executable/class/title, reject unrelated Unity windows and "Lineage W", ignore invisible/stale/duplicate/fake HWND, bounded 150 ms timer contract, hung title exception, HWND changed PID mid-read, PID missing/process unreadable, HWND reuse and deletion, multi-HWND row identity, conflicting observations and Windows platform guard.

New `tools/S08_WINDOWS_DISCOVERY_SMOKE.py`: Creates **real Tk window belonging to Python on Windows**, then `EnumWindows` finds its real HWND/PID; retrieves its exact title with 150 ms `SendMessageTimeoutW`, verifies class+own executable with `GetClassNameW` / `QueryFullProcessImageNameW`, and verifies the non-game Tk HWND was **not** matched as Thần Long. Runs real game discovery without requiring game presence and does not forge account handles.

New `.github/workflows/s08-windows-start-discovery.yml`: Windows/Python 3.10, syntax compilation, all Stage S01–S08 unittest regressions and live Win32 API smoke; artifact JSON. No GitHub EXE release is built.

## 4. ACTUAL Windows CI results
**Run [37872770792](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37872770792)**, head commit `dd63c3b5b14b756e8cb389ae9fac7d08a734ad95`, job `113634367516`.

Actual GitHub Actions log:
- source and tests `compileall`: **PASS**
- full combined S01–S08 `unittest`: **55/55 PASS**, log `Ran 55 tests in 0.044s` (S01 7 + S02 8 + S03 6 + S04 10 + S06 6 + S07 6 + S08 12)
- real Windows smoke: `PASS_READONLY_NATIVE_WIN32_ENUMERATION`
- `EnumWindows` saw **63** top-level HWNDs; **11** were visible.
- The test Python process had **one** own visible HWND; read the exact expected Tk window title via `SendMessageTimeoutW` and verified the process path/class with real Win32 APIs.
- `game_candidates_found = 0`, `real_game_present = false`; **this runner had no Thần Long Mobile game process**, therefore the test does **NOT** validate game-specific positive matching, game title/class variation or game memory.
- `faked_game_hwnds = 0`. Artifact `s08-start-window-discovery`, ID **11591140628**, contains `win32_discovery.json`. Full genuine game or real Windows production behavior **NOT_RUN**.

## 5. Honest status and blockers
**STATUS = `S08_REAL_WIN32_DISCOVERY_55_TESTS_PASS_GAME_RUNTIME_NOT_PRESENT`**.
This is the **first working read-only operational Start subsystem source slice**, not a complete Start GUI, multi-preview, tile, login, character identification, startup license, or a usable TLM replacement EXE. It does not register a fake working Start tab or grant user access. Existing `src/TLMTool.py` still deliberately exits with code 2 and no authentication bypass. Exact compiled C01 filtering boolean remains UNKNOWN; current AND+(OR) choice must be tested on a real game installation before making parity claims. C01 3s discovery producer / 2s UI consumer are **NOT IMPLEMENTED**; real game scan and negative/hung title tests remain unverified by native game runtime.

## NEXT_ACTION S09
Read current PLAN/STATE and existing S08 code, plus C01/C02/C04 and E03 Start lifecycle. Implement **a bounded threaded Start window-snapshot producer with cancellation, stale HWND/PID invalidation, and a 2s UI cache consumer**; ensure Start tab leaving stops polling, background producer does not block Tk/UI. Use real Windows tests and no fake game controls; preserve license gating and Proxy exclusion. Verify actual game-positive recognition only on a real Windows machine with game, not fabricated CI data. Do not redo S08 or cosmetic InfoTab work.
