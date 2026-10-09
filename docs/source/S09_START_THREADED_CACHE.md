# S09 — Threaded Start Win32 producer and 2s Tk cache consumer

## Starting position and original evidence

User requested CONTINUE. Read the current GitHub `PLAN.md`, `STATE.md`, `PROJECT_STATUS.md`, `src/start_windows.py`, `src/shell.py`, `tests/test_s08.py`, and original static-analysis handoff `docs/tasks/C01.md`, `C02.md`, `C04.md`, `E03.md`. Confirmed `docs/tasks/S09.md` absent. S08 is real, completed Win32 read-only enumeration with 55/55 prior tests; did not rewrite that working source.

Original `C01` explicitly distinguishes:
- Background window enumeration + character info approximately **3 seconds**;
- Start UI cache polling **2 seconds**, stopped when tab not selected and restarted upon return;
- Heavier game-memory reading approximately **8 seconds** (NOT part of S09);
- DWM preview maintenance **800/2000 ms** (separate from the Start list cache; NOT part of S09).

Original `C02` tracks **HWND+PID**, invalidates stale rows on HWND reused by a different PID and removes closed window rows. Original `E03` uses lazy construction, per-tab `_start_refresh/_stop_refresh` hooks and Info fallback on unverified rights. S09 implements an evidence-backed concurrency *adaptation*, not a decompiled copy of original threading expressions.

## Actual production source

Created **`src/start_polling.py`**:

`StartWindowProducer`
- Default interval **3.0 seconds**, independent from Tk; constructs S08 `NativeWin32Backend` inside its daemon worker thread; calls real read-only `discover_game_windows()`.
- Thread-safe atomic `WindowSnapshot` with revision, immutable tuple of actual `GameWindow` records, validity, monotonic capture time, bounded error information. `read_snapshot()` reads cache only; **never scans windows on Tk**.
- On Win32 enumeration failure publishes **invalid EMPTY** snapshot: no stale HWND/PID identities reused. On backend initialization error publishes invalid error and permits future retry.
- Epoch+stop-event guard prevents late results from a stopped worker overwriting cache. `stop()` immediately invalidates cache and signals cancel, waiting at most **0.2s** for in-flight native enumeration to finish. A new session does not overlap a worker still exiting; start retries after old worker exits.
- No process memory, DLL, injection, click, window movement, game command, HTTP, Proxy or synthetic account handles. Worker cancellation cannot forcibly abort an in-flight Win32 call; its late snapshot is ignored. This is explicitly bounded, not instant thread kill.

`TkStartCachePoller`
- Default Tk callback interval **2000 ms**. Uses `root.after`, reads producer cache, and sends only changed snapshot revisions through `StartCacheEvent` to a user-facing callback on the Tk thread.
- Reconciles rows with S08 `WindowRegistry`, including `WindowDelta.added/removed/reused`, checked against HWND+PID generation, and wipes stale rows on invalid cache.
- Implements `_start_refresh` / `_stop_refresh` for existing S01 `TabLifecycle` integration. Stops/cancels Tk timers on leaving Start; generation guard discards callback already queued after cancellation; restarts as new session when returning; `shutdown` idempotent.
- **No Start UI/control widgets or entitlement bypass**. Production `src/TLMTool.py` still returns exit code 2 while genuine server authorization and functional tabs remain unimplemented. The S09 service can be integrated only via a legitimate future Start factory/permissions; tests use fake entitlement callbacks only in test code.

## New tests and real Windows execution

Created `tests/test_s09.py` with **12 new cases**:
- Exact separate original 3s/2s cadence constants;
- Real threaded snapshot publication from fake test backend;
- Stop during blocked enumeration (bounded latency) and late-result suppression;
- Backend failure and recovery; invalidation on enumeration error;
- Nonblocking Tk cache consumer, revision-driven update;
- HWND changed PID/reused, stale removal, invalid snapshot;
- Queued callback after cancellation rejected;
- Restart after selecting Start, and original S01 TabLifecycle _start/_stop_refresh compatibility;
- No overlapping in-flight worker.

Created `tools/S09_WINDOWS_START_POLLING_SMOKE.py` that creates a **real Tk window** on Windows, runs the actual S08 `NativeWin32Backend` via a separate Start producer at **3s** default cadence, and consumes the cache on the Tk thread at **2000ms**. No fake game handles, no game installed, no action request. Reports thread identities, Win32 enum count, timer duration, cache validity and cleanup to JSON.

Created `.github/workflows/s09-windows-start-polling.yml` (Windows latest, Python 3.10), compileall + ALL Stage S unit tests + actual Win32/Tk worker smoke + artifact.

**Verified live GitHub Actions run [37873565602](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37873565602)**, head SHA `10aa388164c71e9c75b607e4e05235107192596f`, job `113636843382`, **COMPLETED SUCCESS**. Examined actual job logs:
- `compileall -q src tests tools/S09_WINDOWS_START_POLLING_SMOKE.py`: PASS.
- Combined `unittest` tests **67/67 PASS** (`Ran 67 tests in 0.211s`); S01 7, S02 8, S03 6, S04 10, S06 6, S07 6, S08 12, S09 12.
- Native Win32/Tk smoke **PASS_NATIVE_WINDOWS_THREADED_START_CACHE**; measured 2.562 seconds; worker thread NOT main; **one** real scan returned **68** top-level HWNDs; consumer callback on main Tk thread TRUE.
- Captured two real cache events: initial revision 1 INVALID/unknown; revision 2 VALID and 0 matching game HWND. The GitHub Windows runner did **not** have Thần Long installed; therefore positive game-specific recognition remains **NOT_RUN**, not fail.
- `stop_revoked_cache=true`, `stopped_producer=true`, `poller_closed=true`. Actual callback cancellation race and HWND PID reuse positive game transition are **unit tested**, not demonstrated with the game.
- GitHub artifact `s09-windows-start-cache` ID **11591396593**, machine JSON `win32_start_cache.json`.

## Limits and next milestone

**Status `S09_NATIVE_WINDOWS_WORKER_TK_67_TESTS_PASS_NO_GAME_RUNTIME`.** This is working infrastructure but NOT a fully rendered StartTab or a usable TLM replacement: no production auth, no real-game-positive smoke, no character memory, preview/DWM, account control, game launch, auto train, game login or standalone Nuitka EXE. Exact original game filter Boolean grouping remains unknown from C01. No Proxy Phase Q development, no fake server license, no rewriting prior S01–S08 source.

**NEXT_ACTION S10:** Read latest `PLAN.md`/`STATE.md` and original B04 Start/Xếp-lưới screenshot plus C03/C05/C06/C08 and E03. Implement smallest legitimate **read-only Start tab view** consuming S09 real cache, displaying only actual HWND/PID/title and lifecycle change; retain Info-only authorization default and do not add nonfunctional preview/layout or game-control buttons. Test Tk real Windows and 3s+2s lifecycle; keep original game-positive test as explicit blocker. Do not restart Info cosmetics or Proxy.
