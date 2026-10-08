# S02 — Info authorization-state reconstruction / no live license API

## Authority and scope

User requested CONTINUE and explicitly allowed supplemental research in GitHub client-DATA-222222 if original TLM documentation lacked required *game-client* facts. Started from current `PLAN.md`/`STATE.md` (`NEXT_ACTION = S02`), verified `docs/tasks/S02.md` absent, checked existing S01 source/tests first and preserved completed parts.

Original-TLM authority: `docs/tasks/E01.md`, `E04.md`, `E05.md`, `E07.md`, `E08.md`, `B12.md`, and direct read-only inspection of original `TLMTool_2.1.2(10).zip` / inner frozen `TLMTool.exe` (SHA256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`). Compiled markers: `permission_guard` at `0x2b84c35`, `info_tab` at `0x2975ca9`.

Read-only *client* reference: `ngmthang-g/clinent-game-than-long-DATA-2222` `README.md`, `AI_BOOTSTRAP.md`, `AI_ROUTER.md`. Its router is for client Lua/game state/UI, inventory, NPC/action and game runtime. **No client data was used to infer TLM's license server, signed token, subscription privileges or plan defaults**; these originate with TLM itself. No DATA repo modifications or full repository sweep.

Scope: implement the **smallest real in-memory Info/permission_guard service**, not a fabricated server or full InfoTab GUI. Absolutely no Proxy Phase Q development, no extra visible tabs or false license grants.

## Confirmed original contracts
- `permission_guard.py` compiled block exposes `update_permissions_from_payload`, `has_permission`, `has_permission_with_limit`, `check_account_limit`, `get_plan_status`, `get_permissions`, `is_version_locked`, `is_plan_banned`, `record_heartbeat_failure/success`, and `set_block_notifier`.
- State/input symbols include `permissions`, `plan_tabs`, `plan_status`, `plan_cfg`, `server_max_windows`, `version_lock`, `server_locked`, `token_expiry_ts`, `heartbeat_failures`, `has_payload`.
- Original permission helper documentation expressly says production **does not guess max-window limits from plan-name text**; server/token values (including online count) are authoritative. PC and emulator game sessions share a window/account limit. `check_account_limit` returns `(allowed,running,limit,msg)`.
- Original compiled module has a `_DEFAULT_FREE_PERMISSIONS` path and heartbeat failure/grace state; **exact list of free entitlements and original grace/retry decision rules are NOT recovered**. S02 therefore **conservatively grants no unverified feature** and revokes on rejected payload, rather than claiming exact original FREE offline parity. Revisit when the actual trusted server contract is recovered.
- `info_tab` contains `call_server_api_at_startup`, `_post_rpc`, `decode_token`, `_verify_token_signature`, `LTOOL_TOKEN_VERIFY_MODE`, `LTOOL_TOKEN_PUBLIC_KEY_PEM`, `update_permissions_from_payload`, `start_heartbeat`, `send_heartbeat`, `record_heartbeat_success/failure`, `plan_update_callback`.
- Original Info CURRENT_VERSION is `2.1.2`. Changelog/price/catalog are server-driven, not static. Info has real UI/network/activation/update paths, **not reconstructed in S02**.

## Actual source implementation

### src/permission_guard.py — state model, not cryptography
- `VerifiedClaims` immutable normalized data contract, `PermissionSnapshot` with explicit `has_verified_payload`, `PermissionGuard` manager.
- Without a verified token: `info_tab` is the only allowed tab; all feature actions and account-limit checks reject.
- `receive_token(token, verify_and_decode)` requires a nonempty token and **a separately supplied verifier adapter returning exact VerifiedClaims**. A raw JSON payload, `True` flag, plain dict, exception, malformed keys or invalid counts results in fail-closed reset. That callback has **NO real production implementation in S02**. Fake signature verifiers exist **only in tests**.
- Valid normalized claims are filtered against the original Notebook keys. Dev-only tabs require both a verified corresponding tab grant and a verified developer flag. Version lock, server lock, expired or banned/over-limit plan block actions.
- `check_account_limit(running)` accepts an explicitly provided nonnegative count and verified positive server-derived limit; rejects no count, invalid or nonpositive limit; does **not scan processes** or derive count from plan name.
- On new valid token, snapshot only changes once to avoid transient revoke/grant flicker; on invalid token, it clears. This is conservative gateway behavior, not a claim of exact TLM heartbeat semantics.
- **SECURITY LIMITATION:** the adapter interface is not cryptographic verification. A malicious replacement adapter could return invented claims. No actual license access is possible until an independently verified real token decoder/verifier is implemented, wired and tested. Never use the test adapter in shipped code.

### src/info_state.py — Info-owned session bridge
- Real `InfoState` owns `PermissionGuard`, original static current-version string 2.1.2, last server result, an optional on-change callback.
- Verified-token outcome and failure-state tracking are explicit. `on_server_error` clears permissions, conservative until original heartbeat grace is reproduced. `stop_heartbeat` currently clears a local flag only; **not a heartbeat scheduler**.
- Does not invent an RPC URL, token signature, auth bypass, server-provided prices, a startup device hash, CPU monitor, heartbeat interval, activation endpoint or InfoTab rendering.

### src/shell.py — minimal integration with Tk thread
- Preserved all existing S01 tab order/settings/lazy factory code and user-corrected label **Dồn**.
- Added `TLMMainApp.apply_info_snapshot(snapshot)` rejecting non-`PermissionSnapshot` values. It marshals `apply_verified_permissions` to the Tk loop via `root.after(0,...)` (E04 documented UI callback bridge).
- The normal `src/TLMTool.py` entrypoint **still deliberately returns exit code 2** because a genuine InfoTab/server signed-token verifier and live feature modules are absent. No fake GUI opened.

## Verification results
- `python -m compileall -q` on the combined S01+S02 source/test tree **PASS**.
- `python -m unittest discover -s ... -v` **15/15 PASS** (S01 prior 7 + S02 new 8). Test cases include denied unknown, rejected raw JSON/flag/dict, test-only verifier, dev gate, version/ban/expired, server-limit guard, invalid token revocation, server-down revocation, Tk thread dispatch and wrong snapshot rejection.
- GitHub after commits: re-fetched `src/permission_guard.py`, `src/info_state.py`, `src/shell.py`, `tests/test_s01.py` and `tests/test_s02.py`; required symbols verified, counts 7+8. **NOT_RUN**: real server transport and signature verification, Windows Tk event loop, heartbeat timing, full InfoTab GUI pixels, source-to-Windows Nuitka/EXE build, game or LDPlayer.

## Remaining gaps and status
- Signed token canonical format/verifier/public key policy and authentic RPC endpoint; do NOT invent from strings alone.
- Real `TLMInfoTab` view, licensing UI and API/heartbeat; original free-permissions list and token expiry/grace.
- Actual running-PC/LDPlayer count aggregation and window-limit persistence; Info source of truth on server refresh.
- S01 currently has no callable production authentication factory, no other functional game tab controllers and no Stage-T Windows build. A partial Python source exists; application remains **SOURCE_PARTIAL_AUTH_VERIFIER_INFO_UI_FEATURES_AND_WINDOWS_BUILD_MISSING** (not SOURCE_MISSING, not EXE build failure).
- Server failure immediately revokes in this conservative slice while original may permit heartbeat grace — deliberate parity deviation tracked, not a claim of exact behavior.

## NEXT_ACTION — S03
Research the original `info_tab` transport/token validation contract and permission_guard FREE/heartbeat grace boundaries with exact EXE evidence. Implement a **real but isolated InfoTab read-only UI/controller only after underlying data/state is legitimate**; use client-DATA-222222 only for game-client-specific unknowns, never invent license server. Extend tests, update STATE/PROJECT_STATUS. Keep entrypoint blocked until authenticated startup and real modules are available; no Proxy work.
