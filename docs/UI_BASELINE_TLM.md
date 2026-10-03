# UI_BASELINE_TLM — TLMTool 2.1.2

This document is the authoritative screenshot-derived UI baseline. It is built incrementally through Gate B.

Do not treat screenshot parity as functional parity. Behavior remains a separate verification track.

---

## B01 — Main window dimensions — VERIFIED

### Locked reconstruction target
- **Client/content area:** `450 × 1000 px`
- **Observed full window raster:** `452 × 1032 px`

### Observed non-client boundary in supplied screenshots
- left frame: 1 px
- right frame: 1 px
- top/titlebar through row 30
- client starts at row 31
- bottom frame: final row 1031

All **12/12** supplied screenshots agree on these dimensions.

### Confidence
**HIGH / VERIFIED from raster evidence.**

### Explicit UNKNOWN
- DPI/scaling percentage
- exact geometry-setting API/source code
- resizable/min/max policy
- initial screen coordinates
- decoration metrics under other OS themes/DPI settings

### Implementation parity rule
Target the **450 × 1000 client area**. Use the observed **452 × 1032 outer raster** only as the screenshot-environment parity reference; do not hard-code Windows decoration assumptions unless later evidence requires it.

---

## B02 — Tab bar + style chung
TODO

## B03 — Login
TODO

## B04 — Party
TODO

## B05 — Train
TODO

## B06 — Train LSV
TODO

## B07 — Phó Bản
TODO

## B08 — Daily
TODO

## B09 — Đồn
TODO

## B10 — Rao
TODO

## B11 — Tối ưu
TODO

## B12 — i
TODO

## B13 — Màu/font/button metrics
TODO

## B14 — Pixel comparison checklist
TODO
