# S03 — TLMInfoTab original token/RPC/heartbeat audit and real read-only view

## Verified prior state, guardrails and source inputs
- Resumed **S03** from latest `STATE.md`/`PROJECT_STATUS.md`; `docs/tasks/S03.md` was not present before work. Read `PLAN.md`, original S01–S02 source/tests, `B12` screenshot-locked Info tab, `E04` permission ownership, `E07` thread lifecycle and `E08` shutdown.
- Direct read-only static scan of user-supplied original `TLMTool_2.1.2(10).zip`; inner frozen `TLMTool.dist/TLMTool.exe` SHA256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`; ZIP CRC PASS.
- No original EXE execution, no game/ADB/Frida, no HTTP request to the licensing service, no authentication key extraction or deployment.
- GitHub client DATA 222222 is an **optional read-only source for game-client behavior**. This task is solely TLM Info licensing/network, not client Lua/UI; no new DATA lookup needed and no client KB written.

## Original EXE: what is directly established

### InfoTab (`<module info_tab>` at 0x2975ca9)
- `call_server_api_at_startup` at 0x2970924, `_post_rpc` and `/rest/v1/rpc/` at 0x2970b25, Supabase URL reference, request keys for device/window information and `token`. The source contains an explicit startup RPC path; exact method argument schema, server acceptance and all retry rules are **not source-recovered**.
- `send_heartbeat` and `app_heartbeat_v2` at 0x2971118; `record_heartbeat_success`, `record_heartbeat_failure`, `start_heartbeat`, `stop_heartbeat`, and Tk `after` scheduling. There is an over-limit autoclose path with separate forced quit (see E07/E08). **Heartbeat interval and the exact grace/strike temporal ordering remain UNKNOWN.**
- `decode_token` at 0x2970f66, `_verify_token_signature` at 0x2971ba3, `base64` and `urlsafe_b64decode`; original doc references a Base64(JSON) signed token and alternate RSA/HMAC verification branches. Symbols `TOKEN_VERIFY_MODE`, `TOKEN_PUBLIC_KEY_PEM`, `TOKEN_HMAC_SECRET`, `LTOOL_TOKEN_VERIFY_MODE`, `LTOOL_TOKEN_PUBLIC_KEY_PEM` are present. **Do not infer the active cryptographic mode, production public key, signature parameters or token trust from compiled symbol presence.** Do not copy the embedded key material or manufacture signed licenses.
- Original Info exposes `update_fields_with_server_response` (0x29754e5) and `update_permissions_from_payload`; version constant **2.1.2** (B12), whereas price/changelog/product list depend on server data. The screenshot's device code, FREE plan and price rows are observed *runtime state*, not safe defaults for unverified runs.

### Permission guard (`<module permission_guard>` at 0x2b84c35)
- `_DEFAULT_FREE_PERMISSIONS` at 0x2b828b3 and `_extract_free_permissions` at 0x2b831c5 demonstrate a FREE feature path. But the **exact granted features and server override/merge logic are not recoverable from these static markers**, so S02's conservative Info-only default is retained with an explicit parity gap.
- `token_expiry_ts` (0x2b82cb1), `heartbeat_failures` (0x2b82cc4), `heartbeat_grace_seconds` (0x2b82d0d), `server_max_windows` (0x2b83375), `server_locked` (0x2b83389) are direct constants. **The presence of a grace variable does not prove its numeric default or all failure-branch semantics.** S02 revokes on server errors, which may be stricter than the original; this remains an explicitly tracked parity difference.
- Original maximum windows is obtained from server/token, and PC+emulator running accounts share a limit (E04/S02). No number is inferred from plan-name text.

## Actual S03 source: passive information only
Created `src/info_tab.py`:
- `InfoDisplay` is a dataclass with original **2.1.2** and explicit safe `Chưa xác minh` for device code, key, license name, window count, expiry and changelog without trusted server fields.
- `display_from_info_state` reads the S02 Info state and checks that a verified payload is present and unblocked; even then it does NOT treat plan_status as license name, or max_windows as a proven display limit.
- `TLMInfoTab` creates real Tk ttk Frames and Labels for the B12-proven headings and six information-row labels. `refresh_readonly` repaints safely from the state and revokes display on later invalidation. The text `Chưa xác minh` and the verification-status phrase are **explicit developer-safe placeholders, NOT exact original TLM strings**.
- Deliberately **no fake Copy, Nhập key, update, upload log, clickable support links, license activation or restart actions**. Their original behaviors are unfinished, and buttons must not be rendered as functional impostors.
- `src/TLMTool.py` is **not modified** and intentionally exits code 2 while a genuine signed token verifier and feature modules are missing. The new passive widget is **not** claimed to be the startup's complete real InfoTab or a visually identical screenshot.

New `tests/test_s03.py` has six independent stdlib headless tests for original version/labels, no invented license values, unverified/blocked view, absence of fake buttons, and repaint after revocation.

## Verification and limitations
- Original binary evidence: **18/18** selected exact-offset anchor strings PASS (two marker and several RPC/token/heartbeat/guard refs), ZIP CRC PASS.
- Local `python -m compileall` on S03 source/tests PASS, and `python -m unittest discover` for **S03 alone: 6/6 PASS**. Earlier S01–S02 had 15/15 PASS from their previous milestone; **the combined 21-test suite was NOT RUN together in S03**, so do not misstate it.
- New GitHub `src/info_tab.py` and `tests/test_s03.py` re-fetched, required source/test symbols verified (6 tests).
- No Windows Tk visual test, live Info RPC/license server, authentic token verification, heartbeat, expiry/grace, full MainApp launch or Nuitka Windows build: all **NOT_RUN**.
- Existing S01/S02 source and settings logic, all prior research, frozen originals and Proxy scope lock unchanged.
- **STATUS = S03_READONLY_INFO_VIEW_6_TESTS_PASS_AUTH_RPC_RUNTIME_UNVERIFIED**. Rebuilt source is real but partial; startup remains deliberately blocked, no full functional parity, no usable EXE.

## NEXT_ACTION: S04
- Reread `PLAN.md`, `STATE.md` and all new source; **do not recreate Info view**.
- Audit original startup RPC token fields and signature trust boundary **without copying secrets or manufacturing license tokens**. Where exact secure server contract cannot be reconstructed, preserve a clear blocker.
- Then implement a small **real, read-only Info display binding/lifecycle** through the existing shell (using a verified/authenticated data adapter only), run combined regressions, and verify Tk when a Windows or compatible display runtime exists. Do not add inactive feature buttons, auto-grant FREE, reveal dev tabs or develop Proxy.
