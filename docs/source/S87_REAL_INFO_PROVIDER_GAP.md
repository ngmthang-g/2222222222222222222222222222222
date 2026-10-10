# S87 — Info signed trust and transport evidence versus missing real provider

**Scope:** read-only original-data verification to guide safe reconstruction. This file does not encode an authorization bypass, server credentials, API client or manufactured grant.

The newly uploaded archive's **SHA256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd** is identical to the prior frozen original. The embedded application has **SHA256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22**. The package CRC check passed with 1,050 ZIP entries. Only the inner main EXE was used for S87 byte scanning; personal `data/` state was not inspected.

## Observed original surfaces
- Compiled module markers for `info_tab` and `permission_guard`.
- Original startup API helper `call_server_api_at_startup`, generic `_post_rpc`, and `/rest/v1/rpc/` route fragment. An embedded Supabase HTTPS origin occurs at original EXE byte offset 0x2970d92; SHA256(origin string) = `74d7a744041b016cc2e5c60572174289b33c8ba2534f6d4bcce4d706ad4b1fc1` (host intentionally omitted from public repository).
- Original `app_heartbeat_v2`, `send_heartbeat`, `decode_token`, `_verify_token_signature`, public-key/HMAC/config string markers, grace and failure fields.
- Existing S03 already knew the generic RPC+token+heartbeat architecture. S87 independently checks its source-of-truth hashes/offsets from the new archive and confirms the dedicated literal HTTPS origin; **S87 does not claim to reverse engineer unseen source instructions**.
- Existing `InfoState` and `PermissionGuard` have type-checked claims and fail-closed behavior; these are **interfaces**, not functioning licensed access.

## The trust chain that is not yet proven

```text
Legitimate server / issuer (NOT YET ATTESTED)
  -> startup RPC request/response schema (UNKNOWN)
  -> authenticated token (UNKNOWN valid sample)
  -> exact trusted key, algorithm, canonical signing input (UNKNOWN)
  -> enforceable expiry/device/session/plan checks (INCOMPLETE)
  -> VerifiedClaims from genuine verifier (NO PRODUCTION PRODUCER)
  -> PermissionGuard/InfoState existing interfaces (PARTIAL, SAFE)
  -> Tk tab visibility and game runtime (PARTIAL, BLOCKED)
  -> real heartbeat, revocation and grace (UNKNOWN)
```

A server-origin string, a function called `_verify_token_signature`, or an example FREE screenshot **does not verify any link in this chain**. The binary may contain more than one code path; mode-selection and key provenance were not established. No secret or session payload has been copied to the repo.

## To unblock without guessing
Require a legitimate specification or owner-approved trace with sanitized startup request/response field names, authenticated verifier configuration/public key and signature acceptance vectors, documented heartbeat cadence/failure behavior, and controlled Windows+game observations under actual authorized access. Verify that real mode/code path independently before enabling production startup. Continue separately implementing source-backed, non-auth-sensitive user-visible controls; do not mislabel test-only native action as game parity.

## Existing baseline
S86 source audit: 1174 Windows unit PASS + test-owned Win32/Tk/DWM regressions; 222 Python files parse/compile. The standalone diagnostic still explicitly refuses the user-facing application. These are prior results, not new S87 Windows execution.
