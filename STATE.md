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

## B02 VERIFIED RESULTS
- Tab order locked: `▶ | Login | Party | Train | Train LSV | Phó Bản | Daily | Đồn | Rao | Tối ưu | i`.
- 11 tabs total.
- Notebook/frame: x=6..443; tab strip top y=36; inactive-tab bottom y=56; bottom y=1024.
- Nominal inactive separators X: 6, 29, 67, 102, 136, 192, 244, 278, 308, 336, 377, 401.
- Nominal separator spans: 23, 38, 35, 34, 56, 52, 34, 30, 28, 41, 24 px.
- Shared raster colors: inactive/client `#F0F0F0`, selected `#FFFFFF`, separator `#D9D9D9`, text/glyph black.
- Captured selected-state evidence exists for 9/11 labels: ▶, Login, Train, Train LSV, Phó Bản, Daily, Đồn, Rao, Tối ưu.
- Party and i selected states are not directly captured and remain UNVERIFIED at exact-pixel level.
- All captured selected tabs show the same selected-surface expansion/merge pattern and a dotted focus rectangle around the selected label/glyph.
- Exact font metrics and broader button metrics remain deferred to B13.

## B02 FILES
- `docs/tasks/B02.md`
- `docs/UI_BASELINE_TLM.md`
- `docs/ui/B02_TAB_GEOMETRY.tsv`
- `docs/ui/B02_COMMON_STYLE.json`
- `docs/ui/B02_SCREENSHOT_ACTIVE_TAB.tsv`

## CURRENT_TASK
B03 — Baseline Login.

## BLOCKERS
None for B03.

## DO_NOT_TOUCH
- Preserve Gate A forensic baseline unchanged.
- Do not implement behavior while Gate B is measuring UI.
- Do not invent selected-state details for Party or i.
- Keep font/button metrics provisional until B13.

## NEXT_ACTION
On CONTINUE:
1. Read `PLAN.md`.
2. Read `STATE.md`.
3. Execute **B03 only**.
4. Measure the Login tab screenshot: group boxes, controls, account table, scroll region, bottom Start button, labels and visible default states.
5. Record only screenshot-supported properties; mark behavior/config semantics separately for later stages.
6. Update `docs/UI_BASELINE_TLM.md` and persist B03 report/evidence to GitHub.
7. Advance to B04 only after B03 is verified.
