# P07 — Original `emu_remote` HTTP listener, emulator identity, endpoints and ACK truth

## Starting state and frozen authority
- Re-read GitHub `PLAN.md`, `STATE.md`, `PROJECT_STATUS.md`, P06 and D07. `docs/tasks/P07.md` was absent. NEXT_ACTION is P07, not a new plan.
- Direct read-only audit of the user-supplied frozen ZIP `TLMTool_2.1.2(10).zip`, SHA256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, 1050 CRC-clean entries. Original inner EXE `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`; original AutoX script `ld_remote.js` raw bytes SHA256 `3bd84a2b433ee679b7a049f5aa5cba2e8725d1e09b14d5deb3f42b6bf919edfb` (has UTF-8 BOM). No binary, server, emulator, ADB or game executed.
- EXE Nuitka serialized module terminator `<module emu_remote>` at `0x2938352`; direct constants/method evidence before that marker, predominantly `0x29369f6..0x2938352`. The exact Python AST/call order is **not** recovered.
- Static verifier: **34/34** selected original EXE tokens at documented offsets PASS; **10/10** AutoX JS source tokens PASS. Two initial checks were corrected to true text beginnings (0x29373c1, 0x29374ae) before final verification; no product code was changed.

## 1. Listener contract, lifecycle and security boundary
Original compiled docs at `0x2937dd8..0x293806a` identify a background JSON HTTP service, `ThreadingHTTPServer`, default bind `0.0.0.0`, default port `8765` and token `tlm` from `[Emu] remote_port/remote_token`. `start` described as **idempotent** and returns `(ok, port|msg)`; `stop` uses `shutdown` and `server_close`. `_Handler.do_GET`, `do_POST`, `_send`, `_body`, `_auth` are present, as are JSON/Content-Length/URL parser references. Exact request size caps, server timeouts, cancellation, thread join, and GET authentication coverage are **UNKNOWN**.

**Security finding/constraint:** binding all interfaces with a static default token is a potential unauthenticated/weakly-authenticated LAN exposure when started. Do not launch this service on the user's machine or assume `/ping` proves authorization to game actions. No proxy/network Phase Q development was performed. A future parity build should retain documented behavior under test, while any hardening/new authentication must be an explicitly authorized separate change. **Do not claim GET routes are authenticated without method-level proof**; GET method literals and `_auth` method presence do not prove call sequence.

## 2. Target identity — socket IP versus aid
- The shipped AutoX `ld_remote.js` sets `AID` to a guest IPv4 from Java NetworkInterface (fallback `device.getIpAddress`) and sends `aid`, `token` in every `post()`. **This AID is an IP string in this script**, unlike the historical Android-ID identity key of some PC-side Train LD rows.
- The original PC compiled `_peer_ip` reads the socket `client_address`, and `serial_for_ip` is documented at `0x293746e..0x293758f`: prioritize actual peer socket IP, match to known VM IPs, **do not fall back to guessing if multiple clones share serialno/android_id**. It returns empty if no reliable match.
- `_serial_for_aid` method also exists but its exact fallback/precedence and how a caller-supplied `aid` could influence a given endpoint are not reconstructable from serialized constants. **Never imply that sender-supplied aid alone authenticates/uniquely identifies a VM**.
- IP routing/NAT/reboot/cache and duplicate IP/serial edge behavior require live LDPlayer tests.

## 3. Route and result semantics

| Method | Route | Original static contract | What is NOT proven |
|---|---|---|---|
| GET | `/ping` | `{"ok":true}` health/reachability | Game connected, privilege or farm running |
| GET | `/maps` | map names/ids from data list | current map geometry |
| GET | `/emu_status?aid=` | role/map/tile/HP/bag snapshot via reader | fresh data without stale state |
| GET | `/emu_config` | current configurable values | guest cache synchronized |
| GET | `/emu_heal_presets` | heal preset names | actual healing |
| GET | `/emu_coords` | device presets | immutable serial/aid mapping |
| POST | `/emu_goto` | {aid,map,x,y,token}: background thread / `accepted` | arrived at coordinates |
| POST | `/emu_save_coord` | save named device coordinate | correct selected device/persistence on crash |
| POST | `/emu_del_coord` | delete named preset | correct selected device without collision |
| POST | `/emu_steps` | ordered tap/text/key/wait actions with gap | game accepted or finished actions |
| POST | `/emu_act` | `to_train` / `sell` / `heal` based on selected presets | completed movement, sale or healing |
| POST | `/emu_farm_toggle` | state ACK **original explicitly says farm engine not connected** | any background auto-train worker |
| POST | `/emu_config` | type/allowlist-validated key and value | applied to game runtime now |

Routes and semantics are from serialized compiled docs/method tokens (see `P07_STATIC_EVIDENCE.tsv`), corroborated where used by AutoX `ld_remote.js`. The exact content/HTTP status on every error path is not decompiled. `_CONFIG_BOOL`, `_CONFIG_INT`, `_CONFIG_TEXT` and error strings for malformed conditions/buffs/unsupported keys provide evidence of an allowlist but not a fully recovered schema implementation.

`_run_steps` supports `do= tap | text | key | wait`; `AdbInput` is the execution backend. Errors in selected steps can return error messages, but a returned `(ok,msg)` does not by itself mean a game UI state or tile arrival changed. The original `/emu_goto` runs a daemon worker and immediately returns `accepted`, so higher-level position verification is mandatory to establish actual arrival. `/emu_farm_toggle` explicitly records state only (original compiled doc at 0x2937426).

## 4. Confirmed client/server-result mismatch in shipped AutoX JS
**Source-level fact:**
```js
function post(path, obj) {
  try {
    obj = obj || {};
    obj.aid = AID;
    obj.token = TOKEN;
    var r = http.postJson(PC + path, obj, { timeout: 8000 });
    return { ok: true, body: r.body.string() };
  } catch (e) {
    return { ok: false, err: friendlyErr(e) };
  }
}
```
- The wrapper neither parses `body` as JSON nor checks an HTTP status code before returning its own `ok:true`. Therefore **any nonexceptional `http.postJson` and readable response** appears successful to the JS UI even when the response body describes a failed request. Exact behavior on HTTP 4xx/5xx depends on AutoX's HTTP library and is **NOT_RUN / UNKNOWN**.
- `runSteps()` (lines 1044–1054) updates “Di chuyển ... thành công” on the wrapper's local `r.ok`; no memory verification.
- `act()` (1058–1065) updates “Đã gửi lệnh” on local `r.ok`; sale/heal/game state not measured.
- `toggleFarm()` (1097–1105) flips local `farmOn` and displays “Đang chạy” after local `r.ok` without parsing server farm state; compiled server endpoint is a stub. This is an evidence-backed **false-success risk**, not a user-device reproduced bug.
- `getp()`, unlike `post()`, attempts `JSON.parse(r.body.string())` and returns null on exception; `pingOk()` checks parsed `j.ok` (lines 509–514). Do not conflate GET and POST result semantics.
- Source shows parallel probing of possible PC hosts after checking cached host (lines 516–545); risk of stale IP selection/rebinding remains untested.

## 5. Permission and configuration gates
EXE references `permission_guard.has_permission('emu_tab')`, `check_account_limit`, and `_guard_permission` with distinct reporting for missing permission, license server unverified and exceeding permitted accounts. P01/P05 already proved Train LD is conditional; Debug Android is developer-only. Whether **every GET and every POST** undergoes exactly the same permission check is **unknown** without original source/runtime. No bypass was implemented.

The `POST /emu_config` branch has an allowlist/validation contract. It supports town condition `never/full_bag`, town return method `phu1/phu2/phu3/horse`, boolean/integer/text fields and structured buff string forms. This **does not mean** the emulator auto-train engine applies all UI settings (P05 documented `farm cycle: phase sau`).

## 6. Limitations, tests and gates
- Static verdict: **34/34 compiled offset-token checks PASS; 10/10 AutoX tokens PASS; ZIP 1050 CRC PASS; frozen EXE and JS hashes verified.** `72` evidence records and `33` future runtime acceptance cases, all `NOT_RUN`.
- No PC listener started, no network exposed, no game/LDPlayer, ADB, Frida, item/merchant, Proxy or Windows rebuilt EXE ran.
- Important UNKNOWNs: per-route GET authentication, exact remote account-limit call placement, malformed/huge JSON handling, concurrent listener shutdown, real NAT/clone device IP, HTTP library 401/500 error semantics, action acknowledgements after game state transitions.
- The existing repository code/build audit found missing Stage-S reconstructed app and Stage-T Windows workflow; subsequent current-stage commits only add documentation/checkpoints. **BUILD_BLOCKED_SOURCE_MISSING** is accurate, **not** a compiler failure or build PASS.
- No forbidden public tab added and no source from earlier phases rewritten.

**P07 STATUS:** `STATIC_EMU_REMOTE_ENDPOINT_AUTH_IDENTITY_AND_ACK_AUDITED / LIVE_PARITY_DEFERRED`.

**NEXT_ACTION P08** — original `debug_android_tab` developer-only remote/capture/viewport/ADB/Frida workbench: actual visible controls, callback wiring and deferred test contract. Examine original EXE/JS first and preserve all prior work.
