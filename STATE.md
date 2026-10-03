# STATE — TLMTool 2.1.2

## STATUS
IN_PROGRESS

## GATE A
**COMPLETE / VERIFIED**

## GATE B
IN_PROGRESS

## COMPLETED
- A01 VERIFIED
- A02 VERIFIED
- A03 VERIFIED
- A04 VERIFIED_WITH_EXPLICIT_UNKNOWN
- A05 VERIFIED
- A06 VERIFIED
- A07 VERIFIED
- A08 VERIFIED
- B01 VERIFIED
- B02 VERIFIED
- B03 VERIFIED

## B03 VERIFIED RESULTS
- Login baseline source: `TLMTool_4dw2sgi7mQ(2).png`, SHA-256 `a555bce4054a0d32d19c2377a726c7fa2e6b78c03ce80e8291affb6185f04461`.
- Three group boxes measured:
  - Cấu hình game: x=11..438, y=69..133
  - Cấu hình lịch trình: x=11..438, y=147..283
  - Cấu hình tài khoản: x=11..438, y=297..1013
- Game controls measured; selected-path text is visibly clipped and hidden suffix remains UNKNOWN.
- Schedule visible defaults recorded: unchecked enable, 04:00 shutdown, shutdown-PC unchecked, 04:20 startup, Chờ selected after login.
- Account header columns locked: selector / Tài khoản / Mật khẩu / Ẩn captcha / Login / Proxy.
- Header selector appears checked; first account selector appears unchecked.
- First account visible as `ngmthang1`; password is masked; first captcha `Tool`.
- Account rows use 35 px pitch; 17 complete rows plus partial 18th are visible.
- First Login button is green play; first Proxy button is blue arrows; following proxy cells are gray/disabled-looking.
- Bottom `Bắt đầu` measured at x=20..429, y=978..1007 (410 × 30).
- No behavior semantics were inferred from the screenshot.

## B03 FILES
- `docs/tasks/B03.md`
- `docs/UI_BASELINE_TLM.md`
- `docs/ui/B03_LOGIN_GEOMETRY.tsv`
- `docs/ui/B03_LOGIN_DEFAULTS.json`
- `docs/ui/B03_SCREENSHOT_EVIDENCE.tsv`

## CURRENT_TASK
B04 — Baseline Party.

## BLOCKERS
None for B04.

## DO_NOT_TOUCH
- Preserve Gate A forensic baseline unchanged.
- Do not implement behavior while Gate B is measuring UI.
- Do not infer hidden selected-game path suffix.
- Do not infer login/scheduler/captcha/proxy semantics from B03 screenshot state.
- Keep font/button metric finalization deferred to B13.

## NEXT_ACTION
On CONTINUE:
1. Read `PLAN.md`.
2. Read `STATE.md`.
3. Execute **B04 only**.
4. Measure the Party tab baseline from supplied screenshot evidence: mode controls, grid controls, main-window selection, sync buttons, preview area, zoom controls and license block.
5. Record only screenshot-supported states/geometry; behavior belongs to later stages.
6. Update `docs/UI_BASELINE_TLM.md` and persist B04 evidence/report to GitHub.
7. Advance to B05 only after B04 is verified.
