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

## B02 — Tab bar + style chung — VERIFIED

### Tab order
`▶ | Login | Party | Train | Train LSV | Phó Bản | Daily | Đồn | Rao | Tối ưu | i`

**11 tabs total.**

### Shared notebook geometry
- frame left/right: `x=6..443`
- tab strip top: `y=36`
- inactive-tab bottom separator: `y=56`
- notebook bottom: `y=1024`
- visible frame width: **438 px**
- client margins: left **5 px**, right **7 px**, top-to-tab **5 px**, bottom **6 px**

### Nominal inactive tab separator X coordinates
`6, 29, 67, 102, 136, 192, 244, 278, 308, 336, 377, 401`

Nominal separator spans:
- ▶ 23
- Login 38
- Party 35
- Train 34
- Train LSV 56
- Phó Bản 52
- Daily 34
- Đồn 30
- Rao 28
- Tối ưu 41
- i 24

These are raster separator spans, not source widget width units.

### Shared raster style
- client/inactive tab: `#F0F0F0`
- active tab: `#FFFFFF`
- tab/frame separator: `#D9D9D9`
- tab text/glyph: black
- title: `TLMTool`
- standard Windows-style title chrome is visible in all supplied captures

### Selected tab evidence
Direct selected captures exist for:
`▶, Login, Train, Train LSV, Phó Bản, Daily, Đồn, Rao, Tối ưu`.

Captured selected tabs expand into neighboring separator space, merge through the lower separator into the page, and show a dotted focus rectangle around the label/glyph.

Direct active-state pixel evidence for **Party** and **i** is **UNVERIFIED**.

The dotted rectangle is recorded only as a capture-state fact; B02 does not assert it must remain visible after focus changes.

### Deferred to B13
Exact font family/point size, font weight, button palette/borders and deeper anti-aliasing/color metrics.

---

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
