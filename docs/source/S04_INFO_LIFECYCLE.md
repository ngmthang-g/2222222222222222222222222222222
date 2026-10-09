# S04 — Info state → Tk lifecycle integration, stale authorization race guard, Windows CI

## 0. CONTINUE authority and scope
S04 resumed from latest GitHub `STATE.md` (`NEXT_ACTION S04`) after rereading `PLAN.md`, `PROJECT_STATUS.md`, `docs/tasks/S03.md` and all existing S01–S03 source/test files. `docs/tasks/S04.md` did **not** exist before this work. Reused original E01/E03/E04/E07/E08 + B12 contracts already audited; did **not** reimplement completed S01/S02/S03 functionality or touch original ZIP/client DATA repo.

The TLM original uses InfoTab for server/permission ownership, `permission_guard` for decisions and `TLMMainApp` for Tk widget visibility. E04 explicitly identifies `root.after` as the worker-to-Tk bridge and E07/E08 establish per-tab cleanup. This small slice bridges **the previously reconstructed state and view**; it does not rebuild original server verification.

## 1. Source delivered (not stub buttons)
Added `src/info_binding.py` with:
- `create_info_only_shell(root, notebook_factory, frame_factory, ttk_module)`: uses actual reconstructed `InfoState`, `TLMMainApp`, `TLMInfoTab`; passes **only** the original Info tab's real passive factory. All other 14 Notebook slots exist but remain hidden because no real feature constructor/verified auth is supplied. No fabricated FREE/dev grants or fake login buttons.
- `InfoShellBinding.on_snapshot`: enqueues updates using `root.after(0, ...)`, checks the exact immutable `PermissionSnapshot` class, and calls the already-implemented `app.apply_verified_permissions` plus `view.refresh_readonly` on Tk event callback.
- **Stale permission update defense** (important S04 correction): sequence number AND current-snapshot identity checks discard older queued grants if a newer revocation arrived. This is a reconstruction **safety guard**, not proof of identical private-original Python implementation. No unexpected tab can become public.
- `on_destroy` only closes when the root widget is destroyed, not when a child is destroyed; `close()` is idempotent, stops the Info heartbeat placeholder and the selected-tab refresh lifecycle, and makes queued callbacks no-ops. Destroyed Tk interpreter callback scheduling errors (`tk.TclError`, `RuntimeError`) cause cleanup, not resurrection.
- Normal `src/TLMTool.py` remains unchanged and intentionally prints the missing-authentication blocker/returns exit code 2. The new constructor is a bounded internal integration seam, **not a runnable clone**; authenticated server startup, real feature tabs and Windows standalone distribution remain unimplemented.

Added `tests/test_s04.py` with 10 new unittest cases for: original 15 potential tab slots/Info-only visibility, no inactive action buttons, delayed root.after update, queued grant followed by revocation in reversed callback order, revocation after an applied grant, root-close and child-destroy behavior, discarded pending callbacks, Tk scheduling failure, strict snapshot type, shared exact InfoState/view instance. Test-only forged `VerifiedClaims` are never used by production startup.

## 2. Actual Windows GitHub Actions test — completed and independently confirmed
Added `.github/workflows/s04-source-tests.yml`: Windows GitHub Actions, Python **3.10**, `compileall -q src tests`, `python -m unittest discover -s tests -p "test_s*.py" -v`. Workflow is test-only, not a Nuitka build/release; read-only checkout permissions.

**GitHub Actions run [37867454367](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37867454367), commit `dcb154fc00846c382f7bec571a6da6c61d171a66`**:
- Workflow job `source-regression` completed **success**.
- Python 3.10 setup **success**.
- Compile all source/tests **success**.
- Full combined S01–S04 unittest **31 tests / OK**, exact log line `Ran 31 tests in 0.035s`.
- Coverage: S01=7, S02=8, S03=6, S04=10, all included at the tested HEAD.
- GitHub job log was fetched and inspected directly. This is **not** a guessed sum of historical milestones; the combined suite **actually ran** on Windows, resolving the S03 `NOT_RUN` blocker.

## 3. What is still unverified
- Tests use **fake Tk adapters** rather than a physical Windows window/raster/DPI context. They verify Python lifecycle and widget invocation, **not UI pixel parity** with the original B01/B12 screenshot.
- The S02 verifier callback in unit tests is explicitly artificial/test-only. **NO** authentic Supabase call, signed token validation, public-key policy, heartbeat grace, default FREE entitlement list, session accounting or real login has been implemented.
- The new `create_info_only_shell` is internal and does not authorize launching the production GUI. The public `src/TLMTool.py` continues fail closed. Original feature tab logic, DLL/Frida resources and Nuitka Windows EXE build/publish pipeline remain incomplete.
- No Proxy Phase Q development; no original binary/ZIP or prior A–R, S01–S03 source modified.

**S04 STATUS:** `S04_INFO_TK_BINDING_AND_WINDOWS_31_TESTS_PASS / REAL_APP_RUNTIME_BLOCKED_AUTH_AND_FEATURES`.

## 4. Artifact and next-action handoff
New files:
- `src/info_binding.py`
- `tests/test_s04.py`
- `.github/workflows/s04-source-tests.yml`
- `docs/source/S04_INFO_LIFECYCLE.md`, `docs/source/S04_MODEL.json`, `docs/source/S04_STATIC_EVIDENCE.tsv`, `docs/tasks/S04.md`
- append-only `STATE.md` and `PROJECT_STATUS.md`

**NEXT_ACTION = S05 — perform an actual Windows Tk Info-only preview/raster and safe shutdown smoke test using the isolated `create_info_only_shell` path, without unblocking the production entrypoint; compare against the frozen B12 screenshot.** If only CI/headless runtime is available, preserve `WINDOWS_GUI_NOT_RUN` and instead implement/test the minimal genuine original application startup/permission service contracts for which evidence exists; do not invent server endpoints/keys or falsely enable action tabs. Also record the Stage-T Nuitka blockers separately.
