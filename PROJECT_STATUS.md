# PROJECT_STATUS

Authoritative continuation state: [STATE.md](STATE.md)

## Gate A
A01–A08: **COMPLETE / VERIFIED**

## Gate B
B01–B14: **COMPLETE / VERIFIED**

## Gate C
- C01 — VERIFIED_WITH_EXPLICIT_UNKNOWN_BOOLEAN_FORMULA
- C02 — VERIFIED_WITH_EXPLICIT_UNKNOWN_FALLBACK_FORMAT
- C03 — VERIFIED_WITH_EXPLICIT_UNKNOWN_PROPERTY_BOOLEANS
- C04 — VERIFIED_WITH_EXPLICIT_UNKNOWN_BOUNDARY_AND_DETACHED_CADENCE
- C05 — VERIFIED_WITH_EXPLICIT_UNKNOWN_AUTO_SELECTION_RULE
- C06 — AUDITED_CLOSED_WITH_EXPLICIT_UNKNOWNS
- C07 — VERIFIED_WITH_EXPLICIT_UNKNOWNS
- C08 — VERIFIED_WITH_EXPLICIT_UNKNOWNS
- C09 — VERIFIED_WITH_EXPLICIT_UNKNOWNS
- C10 — VERIFIED_WITH_EXPLICIT_CONCURRENCY_UNKNOWN
- C11 — VERIFIED_WITH_EXPLICIT_CONCURRENCY_UNKNOWN
- C12 — VERIFIED_WITH_EXPLICIT_RESTORE_DOC_CONFLICT
- C13 — VERIFIED_WITH_EXPLICIT_POST_CLOSE_UI_UNKNOWN
- C14 — VERIFIED_WITH_EXPLICIT_EMBEDDED_VISIBILITY_UNKNOWN
- C15 — AUDITED_CLOSED_WITH_EXPLICIT_DIRECT_BUTTON_BINDING_UNKNOWN
- C16 — AUDITED_CLOSED_WITH_EXPLICIT_POST_CLOSE_REFRESH_UNKNOWN
- C17 — AUDITED_CLOSED_WITH_EXPLICIT_BOUNDARY_AND_DETACHED_ORDER_UNKNOWNS
- C18 — AUDITED_CLOSED_WITH_EXPLICIT_WORKER_CADENCE_AND_INITIAL_STATE_UNKNOWNS
- C19 — AUDITED_CLOSED_WITH_EXPLICIT_PAYLOAD_AND_STARTUP_TIMING_UNKNOWNS
- C20 — AUDITED_CLOSED_STATIC_VISUAL_WITH_RECONSTRUCTION_RUNTIME_PARITY_DEFERRED

Current task: **E04 — shared state**

C06 was re-audited and closed. C07 Auto and C08 Xếp-lưới are now verified from the original EXE. Auto resets to (0,0) 1366×768 and re-tiles every 1 second; Xếp-lưới auto-enables layout+input sync, uses 3×4 defaults, and input keepalive re-blocks slaves every 1.5 seconds. Exact grid arithmetic/bounds/layout cadence remain explicit UNKNOWN.

Preserve Gate A/B baselines unchanged.

C09 verified the main preview 1x–5x column selector: runtime default 2x, manual callback, numeric column resolver, row/column rebuild and separate persisted detached-grid state.

C10 verified Xếp gọn as a real move-only multi-HWND action to (0,0), preserving each window's current size and clearing hidden-state bookkeeping.

C11 verified Xếp chéo as a move-only diagonal stack: master at (0,0), then +50 X/+50 Y per window index, preserving each current size.

C12 verified the off-screen hide design: move to (-2200,-2200), preserve size, avoid SW_HIDE to keep Unity rendering. Restore docs conflict between old-position wording and a specific (0,0) path, so that branch remains explicitly unresolved.

C13 verified Đóng xem as detached-preview teardown, distinct from Hủy tách, refresh, and the later Đóng hết game-window action.

C14 verified the detached DWM-preview subsystem, its screen region, topmost lifecycle, persisted auto-open/grid settings and independent update loop.

C15 verified full DWM preview refresh/rebuild, preserved HWND preview order, automatic conditional refresh, and the detached close+reopen refresh path.

C16 verified the real game-window close path: the shared utility sends normal Windows close requests to the current game windows, while lingering Unity crash-handler cleanup is handled separately. Preview/master cleanup then follows the existing discovery/maintenance lifecycle.

C17 verified the embedded preview ordering controls: left moves one logical position earlier, right moves one position later, the order is keyed by source HWND, and refresh/rebuild preserves it. Edge behavior and detached-order propagation remain explicit unknowns.

C18 verified the layout synchronization subsystem: real toggle state, worker-maintained grid application from cached HWNDs, master-first placement, mode integration, and max-window stop policy. Worker cadence and exact stop ordering remain explicit unknowns.

C19 verified the input synchronization subsystem: master-originated mouse/keyboard events, size-aware coordinate scaling, ordered event handling, 1.5-second keepalive, stale-state watchdog, and master-change safety. Several low-level timing/payload details remain explicit unknowns.

## Gate C closure
C01–C20 are complete for the original executable/static/screenshot evidence. The locked three-HWND screenshot is coherent with the recovered discovery, master, preview-order, layout and synchronization models. Exact reconstructed-build Windows parity is explicitly deferred to the later implementation/parity stage.

## Gate D
- D01 — AUDITED_CLOSED_WITH_PROVENANCE_TIERS
- D02 — VERIFIED_STATIC_REFERENCE_GRAPH_WITH_EXPLICIT_IMPORT_SYNTAX_UNKNOWN
- D03 — VERIFIED_WITH_VERSION_EVIDENCE_TIERS
- D04 — VERIFIED_LAYERED_GRAPH_WITH_CONTEXTUAL_EDGE_TIERS
- D05 — VERIFIED_EXACT_MARKER_BLOCK_MAP_WITH_HEURISTIC_SIGNAL_CLASSIFICATION
- D06 — VERIFIED_WITH_OPAQUE_DATA_ROLES_EXPLICITLY_UNKNOWN
- D07 — VERIFIED_STATIC_HELPER_PROTOCOL_WITH_RUNTIME_EXECUTION_DEFERRED
- D08 — VERIFIED_ARCHITECTURE_HANDOFF_WITH_CONFIDENCE_BOUNDARIES

D01 completed the full original module-name inventory with provenance tiers: 570 accepted unique names across TLM internal, third-party, stdlib-reference, native-extension and Nuitka-hook categories, plus 3 rejected artifacts. The canonical row-level inventory is stored as a compressed TSV.

D02 recovered a conservative compiled-module relationship graph: 377 static references, including 132 TLM-internal edges. Relationship evidence is explicitly not promoted to literal Python import syntax where the Nuitka binary cannot prove it.

Audit C15–C20 + D01 completed against the exact user archive. C15/C16 evidence offsets were normalized, C19/C20 metadata wording was aligned, and D01 raw-vs-normalized source-reference counts were made reproducible (541 raw → 538 normalized). D03 then recovered third-party dependency versions, direct TLM references and native-extension structure.

D04 refined the 132-edge TLM internal reference graph with separate contextual evidence tiers and a layered architecture model, without promoting static references to exact Python import syntax.

D05 mapped printable strings/constants to all 37 exact-marker TLM module blocks with exact offsets, deterministic per-module counts and a separate high-signal classifier. Large compiled intervals are not misrepresented as original source-file ownership.

D06 separated immutable payload/templates, persistent PC settings/state, Android guest config, runtime logs and opaque packaged data. Active resources.dat and version.dat were confirmed as PE payload/proxy files rather than ordinary data.

D07 statically recovered the Frida resident RPC reader, AutoX remote overlay/HTTP protocol, emulator identity/config bridge, proxy forwarder helper, and updater/helper connections. No helper executable or script was executed.

## Gate D closure
D01–D08 are complete for static architecture evidence. The integrated diagram preserves evidence tiers and separates PC game integration, emulator protocol, proxy/update helpers and persistent data boundaries. Runtime/helper parity remains explicitly deferred.

## Gate E
- E01 — VERIFIED_WITH_EXPLICIT_NORMAL_CLOSE_ORDER_AND_SPLASH_ORDER_UNKNOWNS
- E02 — VERIFIED_WITH_HIGH_CONFIDENCE_POSITION_MODEL_AND_EXPLICIT_STYLE_UNKNOWNS
- E03 — VERIFIED_WITH_CONDITIONAL_VISIBILITY_AND_LAZY_BUILD_MODEL
- E04 — CURRENT
- E05 — TODO
- E06 — TODO
- E07 — TODO
- E08 — TODO
- E09 — TODO
- E10 — TODO

E01 recovered the main GUI lifecycle, special forwarder branch, diagnostic/single-instance setup, tab construction, Info startup/heartbeat service and distinct normal-vs-forced shutdown paths. Splash micro-order and normal destroy ordering remain explicit unknowns.

E02 recovered the Tk root construction: transient 250x20 startup geometry, topmost/withdraw/icon behavior, exact root default font Segoe UI 9, Notebook 5 px packing margin, and the top-right 450/80/10 positioning model. Gate-B B13 was corrected only for the root/global font; per-widget override sizes remain explicit unknowns.

E03 recovered the potential tab insertion order, Info fallback, conditional/dev visibility, lazy build/rebuild path, scroll wrapper and selected-tab refresh ownership while preserving the Gate-B 11-tab production order.
