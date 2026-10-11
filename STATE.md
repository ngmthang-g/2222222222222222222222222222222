# STATE — TLMTool 2.1.2 reconstruction

_Last reviewed: 2026-10-12 Asia/Bangkok. PLAN.md + SCOPE_LOCK.md authoritative; PROJECT_STATUS.md append-only history._

## LAST VERIFIED CODE MILESTONE: S163 — genuine F06 selected Tk Login account inputs (PARTIAL)
- [PR #17](https://github.com/ngmthang-g/2222222222222222222222222222222/pull/17) merged `ba87ac9a10034eaa14c30b4a137c1a478b1e4e94`; actual Win64 **2507/2507** tests, **412 compiled files / 104 source modules**, S163 **18/18 real test-owned Tk** checks, independent inherited S151, S36 DIAGNOSTIC and Stage S green.
- Login rows produce selected checked credentials from real Tk Widgets, **NOT an authorized or completed Thần Long game Login**. Signed Info issuer, F05 real x64 injected launcher and F06 runtime input remain unresolved. Preserve S163/S162/S161/S160 and all other passing sources.

## S164 INVESTIGATED — ORIGINAL INFO RPC STATIC ANCHORS VERIFIED; REAL AUTH BLOCKED

### Evidence and actual work completed
- Read LIVE PLAN/STATE S163 NEXT_ACTION S164/SCOPE_LOCK/S163/PROJECT_STATUS/E04 plus existing S02/S03/S04 `src/TLMTool.py`, `src/info_tab.py`, `src/info_state.py`, `src/permission_guard.py`, existing S03 source evidence. No verified code redone or source changed.
- Inspected the **frozen ORIGINAL inner EXE read-only** from the supplied user ZIP. ZIP CRC PASS; ZIP size **93,715,901**, SHA256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; original `TLMTool.dist/TLMTool.exe` size **47,450,112**, SHA256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`. Neither executed or altered. Static **12/12 module offsets verified**.
- In original `.info_tab`, verified `/rest/v1/rpc/` POST headers `apikey`, `Authorization: Bearer`, JSON; **`app_sync_v2`** startup with device/session/hash/hostname/IP/license/window-count symbols and explicit token rejection, **`app_heartbeat_v2`** with session/active tab, token re-verification, success/failure, over-limit autoclose and scheduling. Original static doc expressly says **one v2 RPC / NO v1 fallback**.
- Token code references `decode_token`, `_verify_token_signature`, a base64(JSON)+hex signature form and RSA PKCS1v15/SHA256 + HMAC SHA256 branches; `LTOOL_TOKEN_VERIFY_MODE`, `LTOOL_TOKEN_PUBLIC_KEY_PEM` and HMAC config symbols are present. RSA vs HMAC active mode, actual server-issued signatures, cryptographic trust anchor, verification byte sequence, token schema, heartbeat grace, expiry, original public key or legitimate HMAC secret remain **UNVERIFIED**. There is no literal RSA PUBLIC KEY PEM BEGIN sentinel in scanned inner EXE (external keys still possible).
- NEW **`docs/tasks/S164.md`** formal original evidence and explicit missing items; NEW `docs/memory/S164_INFO_RPC_SIGNING_BLOCKER_EVIDENCE.json` contains only non-secret offsets/status. No user license, secret, JWT/API key value, device identifiers, account credentials or token written to GitHub.
- **CODE CHANGES: NONE. NEW WIN64 CI: NONE (no executable code changed).** Existing S163 Windows PASS is retained, not misattributed to S164. No original server RPC request, token activation, or game process executed. Original S01 product entrypoint remains **exit=2 / BLOCKED**, S36 EXE DIAGNOSTIC ONLY, not finished TLMTool.
- Frozen original ZIP/EXE/PLAN/SCOPE_LOCK/B04/S59 unchanged; `ngmthang-g/clinent-game-than-long-DATA-2222` READ ONLY; Proxy excluded.

### Actual end-to-end blockers (do NOT hide or fabricate)
1. Need a legitimate **service-issued test response**, original trusted signature-verification material (public key or operator-controlled verifier — never hardcode private/HMAC secrets), authorized test session and sanitized schema/error/revocation/heartbeat evidence.
2. Original live F05 game process version and supported injected payload plus permission to observe its real Win32 HWND/F06 readiness; none currently available.
3. Signed Info authorization cannot be inferred from a static Supabase URL, public-style key, Python environment variable names, plain JSON, placeholder secret, screenshot or user-declared `VerifiedClaims`. Do NOT add another test-only mock task or fake license-granting UI.

### S164 supplemental FULL original-package read-only scan (no source milestone)
- Following repeated CONTINUE, read LIVE STATE/PLAN/S164/E04 and checked all **1,002 regular members / 1,050 ZIP entries** of the unchanged original TLM ZIP in memory. **No public RSA/SPKI PEM** `BEGIN PUBLIC KEY` / `BEGIN RSA PUBLIC KEY` in any member. No literal PEM private-key sentinel. Generic certificate marker in certifi CA bundle, Frida extension and original EXE is **not** an application token verification key.
- Packaged `data/auth_token.dat`, `data/config.dat`, `data/license.dat`, `data/sec_key.dat` are opaque/high-entropy bytes without literal PEM key markers; actual contents/trust/format UNKNOWN. No contents/secrets/tokens exposed, unpacked or used. Search cannot exclude DER, key obfuscation or runtime-provided issuer trust. New findings appended to `docs/tasks/S164.md` and sanitized `docs/memory/S164_INFO_RPC_SIGNING_BLOCKER_EVIDENCE.json`.
- **Code change: NONE. CI run: NONE. Last VERIFIED production source remains S163, 2507 Win64 tests. Info/game dependency remains BLOCKED; do NOT advance S165, fabricate issuer/keys, or bypass signed Info.**

## NEXT_ACTION S164 — BLOCKED_AUTH_TRUST_AND_REAL_GAME (DO NOT AUTO-ADVANCE TO S165)
- S163 remains last verified production-code milestone; S164's **static investigation is complete** but **external issuer/game evidence is missing**.
- On `CONTINUE` re-read this exact blocker first. **Do not reimplement S02/S03/S163, manufacture issuer keys, invent a free entitlement, call activation RPC with fake data, or create endless unrelated S-test tasks.**
- If genuine authorized Info test access (non-secret verifiable trust root and redacted live signed-response evidence) or authorized matching original game runtime is provided, resume S164 to design the **smallest source-backed real connector**. Any executable source changes need PR actual Windows **>=2507** tests, **>=412** compiled, S163 and inherited native, independent S36 packaged DIAGNOSTIC and Stage S, signed Info fail-closed until legitimate verification. Preserve DATA and all locked assets. Advance NEXT_ACTION S165 **only on new meaningful, verified implementation**, not on this blocked research report.
