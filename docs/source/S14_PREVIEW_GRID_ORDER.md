# S14 — Live DWM preview layout and ordering

Original references: `docs/tasks/C09.md`, `C17.md`, `C03.md`.

The Start read-only widget now has **functional Cột: [1x–5x]** (default 2x) and **◀ / ▶** buttons on every preview header. The displayed surfaces are still live `DwmRegisterThumbnail` previews attached to separate HWND destination overlays (not BitBlt/static images). The controls only rearrange Tk frames and DWM destination geometry. No process focus, game keyboard/mouse, or activation.

Each `PreviewOrder` updates from genuine S09 `GameWindow(hwnd,pid,...)` rows. It keeps surviving HWNDs in their saved logical order even if their cache enumeration order changes. To guard against numeric HWND reuse by a different process, a changed PID is treated as a new source. Edges are **no-op**; new HWNDs **append**. Both are safety choices because the original edge/insertion branch is UNKNOWN.

The native C14 layout proof uses four real Windows *test-owned Tk* source HWNDs, and actually invokes the ttk Combobox and ttk ◀/▶ buttons. All five grid column modes reposition real preview tile widgets; the unchanged original DWM handle pair remains bound to its source HWND across all modes. Old PID is rejected; permission revoke clears all DWM resources and returns to Info. Runs: [S14 37881002761](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37881002761) **SUCCESS**, **128/128** unit PASS. S10–S13 and source regression CI also succeed on same code.

Unknowns: raster geometry parity for 1x/3x/4x/5x with original TLM screenshot; original arrow edge/wrap; new-HWND placement; user-grid persistence; real Thần Long positive; signed license and final EXE. Original 2x screenshot geometry 205×137 item and 197×110 surface retained; other modes use same per-tile geometry as bounded reconstruction, not proven original screenshots.
