# N02 — Tối ưu CPU sampler, bounded history and graph redraw audit

## Scope, provenance and continuity
- N02 executed after checking GitHub main `bddfbcb8a20641b3b53c1abee45a4273552f24d6` and rereading `PLAN.md`, `STATE.md`, `PROJECT_STATUS.md`. No pre-existing N02 artifacts existed. N01 and the verified B11 visual baseline were reused, **not rebuilt**.
- Frozen archive: `TLMTool_2.1.2(9).zip`, SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, 1,050 ZIP members, valid CRC.
- Frozen inner source of evidence: `TLMTool.dist/TLMTool.exe`, 47,450,112 bytes, SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Static inspection read only the EXE bytes. No Windows binary, DLL, injection, GPU helper, or game process was executed. EXE constants/string groups are **not** decompiled Python statements.
- N02 owns the **CPU chart sample/history/render path only**. GPU subprocess details are deferred to N03, detached monitor lifecycle to N04, native TLMP graphics controls to N05+.

## 1. Distinguish two similarly named CPU systems
**Current Tối ưu graph authority:** `toiuu_tab.ToiuuTab`, original `.toiuu_tab` serialized block at `0x2c01fb5`, 22,485 bytes / 940 constants.

**Separate warning service:** `cpu_monitor.CPUMonitor` under `.cpu_monitor` block at `0x28d82e9`, 2,019 bytes / 127 constants, with `psutil.cpu_percent` and high-CPU warning UI. This warning is **not** the Tối ưu tab's blue graph and must not be mistakenly substituted for it during reconstruction.

## 2. Data acquisition / sampler initialization
Within the active `ToiuuTab`:
- Constructor/bootstrap references `_start_graphs` after starting refresh/watch services. This is a current live-start path in the original static evidence, not merely a visual control.
- The CPU sampling setup contains `HAS_PSUTIL_TOIUU` and `cpu_percent`, immediately followed by a serialized `None` tuple and keyword `interval`. **Strong static signature:** `psutil.cpu_percent(interval=None)` (non-blocking mode); exact Python conditional/exception structure remains unknown.
- Original embedded method doc: **“Sample 1s/lần (thread phụ) + vẽ lại (main thread).”** Thus source-intended sampling is off the Tk UI thread, followed by a main-thread draw schedule. Do **not** make Canvas updates directly from the worker.
- Method surfaces: `_start_graphs`, `_sample_loop`, `_schedule_redraw`, `_redraw_graphs`, `_fmt_pct`, `_draw_one`. The original uses more than a `CPU: xx%` label or a static image.

### Important timing-evidence discrepancy
The EXE also contains:
- `GRAPH_TICK_MS` in the sample-loop surface next to `sleep`;
- a tagged double **1000.0**, consistent with converting milliseconds to seconds;
- module-level tagged integer values **750** (`l EE 05` at `0x2c0612d`) and **64** (`l 40` at `0x2c06130`).

These are **exact recovered numeric bytes**, but this constant-table scan does **not** prove which Python variable each numeric object initializes. The doc says “1s/lần” while 750 may be a configured millisecond tick; 64 may be plot height/history length. Accordingly:
- **Confirmed:** original documented approximately one-second sampling intention; `GRAPH_TICK_MS`/sleep/millisecond-conversion constant-family exists.
- **Not confirmed:** exact steady-state tick is 1000ms or 750ms; exact history maximum is 64, 200 or another value.
- A future source-level/Windows trace must bind symbols and measure the actual cadence. Do not silently resolve this ambiguity by inventing source assignments.

## 3. Bounded chart history
The original graph UI construction stores:
```text
deque
GRAPH_HIST
maxlen
_cpu_hist
_gpu_hist
_gpu_avail
```
This is strong evidence for **bounded, appendable CPU history** held in `_cpu_hist` and a distinct GPU series in `_gpu_hist`; not a constantly growing unbounded list, and not a one-shot render.
- The exact `GRAPH_HIST` numeric binding remains **UNKNOWN**; a nearby `64` numeric object is not sufficient to prove `GRAPH_HIST=64`.
- The exact handling of absent/failing CPU readings (append None, omit sample, synthetic 0, etc.) is **UNKNOWN**; the original has an unavailable `--%` display marker, but a marker alone does not prove all failure branches.
- Sampling and plotting are separated from the standalone `CPUMonitor` warning threshold/interval.

## 4. Main-thread scheduling and drawing
Original surfaces establish:
```text
background sample -> bounded _cpu_hist
 -> _schedule_redraw -> Tk/main-thread _redraw_graphs
 -> _fmt_pct + _draw_one(Canvas, history, color)
```
This is a **functional interaction model**. It is supported by the original doc and symbols, not an exact decompilation of each call statement.

Render-specific evidence:
- CPU initialization `CPU: --%`, active label prefix `CPU: `, and formatter `_fmt_pct` beside `--%` and `.0f` formatting.
- Canvas `delete` before drawing, `create_line` for graph lines, grid color **`#e0e0e0`**, CPU color **`#1565c0`**, canvas outline **`#bbbbbb`**.
- Nearby drawing constants **0.25 / 0.5 / 0.75** and **100.0** support horizontal percentage guide/normalization logic; exact pixel-to-value formula, rounding/clamping operator order and every canvas coordinate are not reconstructed.
- A tagged **200** also occurs in this drawing block. Its role (e.g. min width/plot scale/other geometry) is unproven, and N02 must **not** label it `GRAPH_HIST` by guessing.
- `_graph_id`, `_closing`, `after_cancel`, and general Tk main-thread `_ui` marshaling exist. Graph-specific `after_cancel` wiring, a guaranteed cancellation token, deduplication of queued redraws and thread-join order **remain unknown**. Do not claim all graph shutdown races solved.

## 5. Baseline screenshot verification AFTER static extraction
Reused `docs/tasks/B11.md`, `docs/ui/B11_TOIUU_VISIBLE_STATE.json`, and supplied original Tối ưu image:
- 452×1032 external screenshot / 450×1000 client; selected `Tối ưu`.
- Current label `CPU: 15%` in blue with a **real-looking changing** time-history line (single screenshot itself cannot prove live updates). Inner graph has light-gray guides on a white canvas.
- GPU label `GPU: N/A (không có nvidia-smi)` and empty GPU graph in the captured environment. GPU error behavior is N03.
- Screenshot is consistent with string/Canvas model but **does not measure sample cadence, deque length, CPU accuracy, or callback cancellation.**

## 6. Future Stage-S implementation contract, NOT product source
1. Use the original CPU **host utilization** path via `psutil.cpu_percent` with a guarded availability policy; preserve its non-blocking `interval=None` signature unless stronger source/runtime evidence contradicts it.
2. Keep a bounded CPU history, with its own capacity constant; do not hardcode guessed buffer size or timer during final parity certification.
3. Sample on a worker, schedule GUI redraw on the Tk thread; do not mutate Tk widgets from background threads.
4. Redraw the actual Canvas content/labels rather than substituting static images; preserve chart palette and fallback glyphs.
5. Handle destruction/tab visibility so stale redraws cannot touch dead widgets; exact original graph cancellation order is still an evidence gap to close during reconstruction tests.
6. Distinguish `_cpu_hist` graph from `CPUMonitor` high-CPU warning and `_gpu_hist` deep reader.
7. Verify live original-vs-new timing, history length, CPU accuracy, thread safety and shutdown on Windows with an instrumented test environment before functional PASS.

## 7. Acceptance matrix (planned, not executed)
| ID | Requirement | Current evidence | Required next verification |
|---|---|---|---|
| N02-01 | Correct active chart authority | Exact module marker + GUI symbols | Static source parity after Stage-S |
| N02-02 | psutil non-blocking CPU read | Strong static local signature | Runtime sample tracing |
| N02-03 | Worker updates history, not direct Tk mutation | Exact original embedded doc | Thread-safe instrumented Windows run |
| N02-04 | Bounded deque history | Exact deque/maxlen/GRAPH_HIST symbols | Numeric capacity binding/live trace |
| N02-05 | Schedule redraw on main Tk thread | Exact doc + method pair | Live thread-ID checks |
| N02-06 | CPU label and graph colors/guide lines | Exact strings + B11 pixel baseline | Screenshot pixel parity |
| N02-07 | Dynamic actual plotting | Canvas/delete/create_line string family | Live changing CPU load |
| N02-08 | Exact tick `GRAPH_TICK_MS` | Integer 750/64 + doc 1s conflict | Source assignment/traced timing |
| N02-09 | Fallback for unavailable CPU source | Placeholder `--%`; branch unclear | psutil missing/failure test |
| N02-10 | Stop/rebuild without Tk callbacks after destroy | Lifecycle symbols; order unclear | Repeated tab/destroy stress |
| N02-11 | Separate CPUMonitor warning | Distinct compiled module / doc | Cross-module integration test |
| N02-12 | Separate GPU reader and history | Distinct `_gpu_hist` / `_read_gpu` | N03 scope; do not test in N02 |

All 12 future acceptance cases are **NOT_RUN**. Static evidence recovered is not an application test PASS.

## 8. Gate, preserved scope and next action
**N02 status:** `STATIC_CPU_SAMPLE_HISTORY_REDRAW_AUDITED_WITH_EXPLICIT_TIMER_UNCERTAINTY / LIVE_RUNTIME_DEFERRED`.

Do not alter existing `PLAN.md`, Gate B11 or N01; do not implement Proxy, app source placeholders, new UI controls, or guessed perf command handlers. **NEXT_ACTION: N03 — GPU collection / nvidia-smi failure and chart integration audit**. Start with the exact frozen `toiuu_tab` EXE block and only then compare B11 screenshot.
