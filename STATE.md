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
- B04 VERIFIED

## B04 VERIFIED RESULTS
- New Party-selected screenshot: `image(5).png`.
- Screenshot SHA-256: `b04e9a73887bb8093bba8bfcd8a77a4dc57c5838ca11370c85def0f8adeb9590`.
- Raw raster: **451 × 1035**. It has different right/bottom edge-shadow framing from the original 452 × 1032 set; B01 is not changed.
- Party selected white bridge at y=56: `x=65..101`.
- `Sau khi party`: x=11..434, y=69..130; `Chờ` selected.
- `Cấu hình tổ đội`: x=11..434, y=144..181; no ready-account entry visible in this state.
- `Cấu hình nhóm`: x=11..434, y=195..611.
- Three group frames measured:
  - Nhóm 1: x=16..429, y=215..326
  - Nhóm 2: x=16..429, y=340..451
  - Nhóm 3: x=16..429, y=465..576
- Each group visibly confirms 6 account slots arranged 2 rows × 3 comboboxes.
- Nhóm 1 leader: `ThápCa`; first row `ThápCa | 75C.S6 | TổngTài.S6`; second row blank; status `Đang vào...`.
- Nhóm 2/3 leaders: `(chưa chọn)`; six blank slots; action bars `Tạo nhóm 2` / `Tạo nhóm 3`.
- `+ Thêm nhóm`: x=18..151, y=586..607.
- bottom `Bắt đầu`: x=16..429, y=988..1017.
- Static-only `Theo sau đội trưởng` / `Tự nhặt đồ` are not visible in this capture; no pixel coordinates were invented.
- B02 tab evidence updated: Party is now directly observed selected; only `i` still lacks a direct selected screenshot.

## B04 FILES
- `docs/tasks/B04.md`
- `docs/ui/B04_PARTY_GEOMETRY.tsv`
- `docs/ui/B04_PARTY_DEFAULTS.json`
- `docs/ui/B04_SCREENSHOT_EVIDENCE.tsv`
- `docs/ui/B04_PARTY_STATIC_EVIDENCE.tsv`
- `docs/ui/B04_PARTY_STATIC_STRUCTURE.json`
- `docs/UI_BASELINE_TLM.md`

## CURRENT_TASK
B05 — Baseline Train.

## BLOCKERS
None for B05. A Train-selected screenshot is already present in the supplied baseline set.

## DO_NOT_TOUCH
- Preserve Gate A forensic baseline unchanged.
- Do not infer Party runtime behavior from screenshot state.
- Do not force the differently framed Party screenshot into the B01 raster baseline.
- Do not invent coordinates for static-only Party controls not visible in the screenshot.
- Continue Gate B as UI measurement only.

## NEXT_ACTION
On CONTINUE:
1. Read `PLAN.md`.
2. Read `STATE.md`.
3. Execute **B05 only**.
4. Measure the Train tab from the supplied Train-selected screenshot.
5. Record visible sections, controls, default states, coordinate table/list, account list and bottom all-account controls.
6. Persist B05 evidence/report to GitHub and update `docs/UI_BASELINE_TLM.md`.
7. Advance to B06 only after B05 is verified.

## WORKFLOW_CORRECTION
- Before measuring each remaining Gate B tab, first inspect the corresponding compiled module/static UI evidence from the original TLM binary, then use screenshots to lock pixel geometry/state. Screenshots are for visual parity; the binary is authoritative for recoverable labels, defaults, hidden controls and UI structure.
- Do not ask for a screenshot merely to learn text/structure that is already recoverable from the original binary.
- Newly supplied `i`-tab screenshot is staged for B12: `TLMTool_f8iidp8FS8.png`, SHA-256 `e536e081c653c72991344bfe505dd79cbcbf5fa52c9befa63214eb9d1516e4bc`.
