# STATE — TLMTool 2.1.2

## STATUS
IN_PROGRESS

## GATE A
**COMPLETE / VERIFIED**

## GATE B
**COMPLETE / VERIFIED**

## GATE C
**COMPLETE / STATIC+VISUAL VERIFIED; RECONSTRUCTED WINDOWS PARITY DEFERRED**

## GATE D
**COMPLETE / VERIFIED STATIC ARCHITECTURE EVIDENCE**

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
- B05 VERIFIED
- B06 VERIFIED
- B07 VERIFIED
- B08 VERIFIED
- B09 VERIFIED
- B10 VERIFIED
- B11 VERIFIED
- B12 VERIFIED
- B13 AUDITED_ROOT_DEFAULT_FONT_9_WITH_EXPLICIT_PER_WIDGET_POINT_SIZE_UNKNOWNS
- B14 VERIFIED
- C01 VERIFIED_WITH_EXPLICIT_UNKNOWN_BOOLEAN_FORMULA
- C02 VERIFIED_WITH_EXPLICIT_UNKNOWN_FALLBACK_FORMAT
- C03 VERIFIED_WITH_EXPLICIT_UNKNOWN_PROPERTY_BOOLEANS
- C04 VERIFIED_WITH_EXPLICIT_UNKNOWN_BOUNDARY_AND_DETACHED_CADENCE
- C05 VERIFIED_WITH_EXPLICIT_UNKNOWN_AUTO_SELECTION_RULE
- C06 AUDITED_CLOSED_WITH_EXPLICIT_UNKNOWNS
- C07 VERIFIED_WITH_EXPLICIT_UNKNOWNS
- C08 VERIFIED_WITH_EXPLICIT_UNKNOWNS
- C09 VERIFIED_WITH_EXPLICIT_UNKNOWNS
- C10 VERIFIED_WITH_EXPLICIT_CONCURRENCY_UNKNOWN
- C11 VERIFIED_WITH_EXPLICIT_CONCURRENCY_UNKNOWN
- C12 VERIFIED_WITH_EXPLICIT_RESTORE_DOC_CONFLICT
- C13 VERIFIED_WITH_EXPLICIT_POST_CLOSE_UI_UNKNOWN
- C14 VERIFIED_WITH_EXPLICIT_EMBEDDED_VISIBILITY_UNKNOWN
- C15 AUDITED_CLOSED_WITH_EXPLICIT_DIRECT_BUTTON_BINDING_UNKNOWN
- C16 AUDITED_CLOSED_WITH_EXPLICIT_POST_CLOSE_REFRESH_UNKNOWN
- C17 AUDITED_CLOSED_WITH_EXPLICIT_BOUNDARY_AND_DETACHED_ORDER_UNKNOWNS
- C18 AUDITED_CLOSED_WITH_EXPLICIT_WORKER_CADENCE_AND_INITIAL_STATE_UNKNOWNS
- C19 AUDITED_CLOSED_WITH_EXPLICIT_PAYLOAD_AND_STARTUP_TIMING_UNKNOWNS
- C20 AUDITED_CLOSED_STATIC_VISUAL_WITH_RECONSTRUCTION_RUNTIME_PARITY_DEFERRED
- D01 AUDITED_CLOSED_WITH_PROVENANCE_TIERS
- D02 VERIFIED_STATIC_REFERENCE_GRAPH_WITH_EXPLICIT_IMPORT_SYNTAX_UNKNOWN
- D03 VERIFIED_WITH_VERSION_EVIDENCE_TIERS
- D04 VERIFIED_LAYERED_GRAPH_WITH_CONTEXTUAL_EDGE_TIERS
- D05 VERIFIED_EXACT_MARKER_BLOCK_MAP_WITH_HEURISTIC_SIGNAL_CLASSIFICATION
- D06 VERIFIED_WITH_OPAQUE_DATA_ROLES_EXPLICITLY_UNKNOWN
- D07 VERIFIED_STATIC_HELPER_PROTOCOL_WITH_RUNTIME_EXECUTION_DEFERRED
- D08 VERIFIED_ARCHITECTURE_HANDOFF_WITH_CONFIDENCE_BOUNDARIES
- E01 VERIFIED_WITH_EXPLICIT_NORMAL_CLOSE_ORDER_AND_SPLASH_ORDER_UNKNOWNS
- E02 VERIFIED_WITH_HIGH_CONFIDENCE_POSITION_MODEL_AND_EXPLICIT_STYLE_UNKNOWNS
- E03 VERIFIED_WITH_CONDITIONAL_VISIBILITY_AND_LAZY_BUILD_MODEL

## C06 AUDITED / CLOSED RESULTS
- Rechecked the exact user-provided `TLMTool_2.1.2(3).zip`: SHA-256 matches the Gate-A frozen archive, so no forensic baseline was redone.
- Inner `TLMTool.dist/TLMTool.exe` hash matches the binary used by C01–C05.
- Current Xếp-lưới screenshot is byte-identical to the prior Gate-B baseline; UI baseline therefore remains valid.
- Recovered grid config from original binary:
  - `grid_cols` default = 3
  - `grid_rows` default = 4
  - persisted under Start settings.
- `_arrange_grid` recovered with:
  - `GetSystemMetrics`
  - exact literals 450 and 40
  - `min`, `sorted`, `new_slots`, `ww`, `wh`
  - master index 0 / top-left
  - remaining HWNDs sequential after master.
- Exact grid arithmetic formula remains explicit UNKNOWN; no meaning is invented for literals 450/40.
- `_move_windows_offset` is the shared move-only primitive:
  - `pos_fn(index) -> (x,y)`
  - keeps current size
  - master index 0.
- `SetWindowPos` family is recovered; no `MoveWindow` literal/import was recovered from the inner EXE.
- `resize_window` block contains:
  - `GetWindowPlacement`
  - `ShowWindow(SW_SHOWNORMAL)`
  - `SetWindowPos`
  - `SWP_NOZORDER`, `SWP_NOACTIVATE`, `SWP_NOMOVE`.
- Shared stack primitives recovered:
  - tight → (0,0)
  - diagonal → +50 x/+50 y
  - horizontal → +50 x
  - vertical → +50 y.
- Layout sync architecture recovered:
  - `_toggle_layout`
  - `_sync_windows_loop`
  - `_layout_worker`
  - `_arrange_grid`
  - cached HWND list via worker.
- Limit model recovered:
  - server source `new_version_info.max_windows`
  - fallback literal 999
  - worker-cached process count
  - over limit prevents sync
  - `_auto_stop_sync` stops both layout sync and input sync.
- Re-audit confirmed the earlier C06 evidence with no contradictions.
- Exact 1.5s cadence recovered in the same binary belongs to input-sync keepalive, NOT layout-worker cadence.
- Explicit unknowns preserved:
  - exact grid arithmetic / final tile-size expression
  - exact grid +/- bounds
  - exact max-window comparator operator
  - exact layout-worker cadence.
- C07 evidence was observed (Auto 1366x768 reset, RoleName auto-tile, 1-second loop) but deliberately not marked complete.

## C06 FILES
- `docs/tasks/C06.md`
- `docs/tasks/C06_AUDIT.md`
- `docs/window/C06_LAYOUT_STATIC_EVIDENCE.tsv`
- `docs/window/C06_LAYOUT_MODEL.md`
- `docs/window/C06_LAYOUT_MODEL.json`
- `WINDOW_BEHAVIOR_MATRIX.md`

## CURRENT_TASK
N01 — Tối ưu active module/UI authority audit (Phase M handoff complete).

## C07 VERIFIED RESULTS
- Auto is the default Start mode (mode_var = auto).
- _on_mode_change is the shared mode switch handler.
- Auto/manual disables both layout sync and input sync.
- Auto transition resets game windows to (0,0) 1366×768 before/around the Auto tile cycle.
- Auto tiling uses _auto_tile_windows + _auto_tile_loop.
- Original EXE documents a 1-second re-arrangement cadence while auto_tile_active=True.
- Auto tiling sorts using character-info RoleName and keeps master first.
- Auto tile toggle is wired to _get_max_windows / _count_game_processes.
- Switching to sync/Xếp-lưới stops active Train, Trừng ác and Tàng bảo đồ.
- Exact final Auto tile arithmetic and exact max-limit comparator remain explicit UNKNOWN.

## C07 FILES
- docs/tasks/C07.md
- docs/window/C07_AUTO_STATIC_EVIDENCE.tsv
- docs/window/C07_AUTO_FLOW.md
- docs/window/C07_AUTO_MODEL.json
- WINDOW_BEHAVIOR_MATRIX.md

## C08 VERIFIED RESULTS
- Xếp lưới is internal mode value sync and uses _on_mode_change.
- Entering sync automatically enables layout synchronization and mouse/keyboard synchronization.
- Active Train, Trừng ác and Tàng bảo đồ are stopped before entering sync.
- Grid defaults are 3 columns × 4 rows and match the screenshot.
- Dedicated +/- handlers exist for columns and rows; _on_grid_change updates labels and persists config.
- Layout path uses _sync_windows_loop / _layout_worker / worker cache / _arrange_grid with master first.
- Input sync keepalive is explicitly 1.5 seconds.
- Over-limit path disables both layout and input sync.
- Exact grid bounds, layout-worker cadence, grid arithmetic and limit comparator remain explicit UNKNOWN.

## C08 FILES
- docs/tasks/C08.md
- docs/window/C08_GRID_SYNC_STATIC_EVIDENCE.tsv
- docs/window/C08_GRID_SYNC_FLOW.md
- docs/window/C08_GRID_SYNC_MODEL.json
- WINDOW_BEHAVIOR_MATRIX.md

## C09 VERIFIED RESULTS
- Main preview exposes 1x–5x column choices.
- preview_grid_var default is 2x and matches the screenshot.
- _set_manual_preview_grid is the real manual-grid callback.
- _get_preview_columns parses the x-form selection into preview column count.
- refresh_window_preview_list consumes preview_cols/preview_rows and places items by row/column.
- Current 2x geometry remains 3 items in 2 columns, outer frame 205×137, visible surface 197×110.
- Preview order is separate from column count and is preserved by HWND across rebuild.
- Main preview remains live DWM thumbnails.
- Detached preview uses separate detached_grid state and persists it; no main preview_grid settings key was recovered.
- Exact preview_rows arithmetic/manual-flag timing remain explicit UNKNOWN; other column pixel geometries remain runtime-unverified.

## C09 FILES
- docs/tasks/C09.md
- docs/window/C09_PREVIEW_COLUMNS_STATIC_EVIDENCE.tsv
- docs/window/C09_PREVIEW_COLUMNS_FLOW.md
- docs/window/C09_PREVIEW_COLUMNS_MODEL.json
- WINDOW_BEHAVIOR_MATRIX.md

## C10 VERIFIED RESULTS
- Xếp gọn is wired to _stack_tight_cmd.
- Exact original behavior: all current game windows move to (0,0).
- Shared _move_windows_offset preserves current size and processes master first.
- Layout movement resets the hidden/off-screen bookkeeping state.
- Shared movement path is SetWindowPos-family, not a resize-to-default operation.
- Exact interaction if the Auto tile loop is already active remains explicit concurrency UNKNOWN.

## C10 FILES
- docs/tasks/C10.md
- docs/window/C10_STACK_TIGHT_STATIC_EVIDENCE.tsv
- docs/window/C10_STACK_TIGHT_FLOW.md
- docs/window/C10_STACK_TIGHT_MODEL.json
- WINDOW_BEHAVIOR_MATRIX.md

## C11 VERIFIED RESULTS
- Xếp chéo is wired to _stack_diagonal_cmd.
- Exact positioning rule is origin (0,0) with +50 X/+50 Y per ordered window index.
- Shared engine preserves current size and processes master first.
- Re-layout clears hidden/off-screen bookkeeping.
- Exact interaction if Auto tiling is already active remains explicit concurrency UNKNOWN.

## C11 FILES
- docs/tasks/C11.md
- docs/window/C11_STACK_DIAGONAL_STATIC_EVIDENCE.tsv
- docs/window/C11_STACK_DIAGONAL_FLOW.md
- docs/window/C11_STACK_DIAGONAL_MODEL.json
- WINDOW_BEHAVIOR_MATRIX.md

## C12 VERIFIED RESULTS
- Ẩn hết is a real hide/show toggle using _windows_hidden.
- Hide moves all game windows to (-2200,-2200) and preserves their current size.
- It deliberately avoids SW_HIDE so Unity keeps rendering and PrintWindow/PostMessage background operation remains usable.
- _saved_window_rects + GetWindowRect bookkeeping exists.
- Toggle changes to Hiện hết after hiding.
- Specific restore log/doc says (0,0), while generic toggle doc says old position; exact saved-rect restore use is preserved as a documentation conflict/UNKNOWN.
- Any visible re-layout can clear the hidden bookkeeping through _reset_hidden_state.

## C12 FILES
- docs/tasks/C12.md
- docs/window/C12_HIDE_SHOW_STATIC_EVIDENCE.tsv
- docs/window/C12_HIDE_SHOW_FLOW.md
- docs/window/C12_HIDE_SHOW_MODEL.json
- WINDOW_BEHAVIOR_MATRIX.md

## C13 VERIFIED RESULTS
- Đóng xem belongs to the detached-preview control bar and closes preview/view resources, not game windows.
- _close_detached_preview explicitly distinguishes user_initiated=True for the close button.
- Detached view uses real DWM overlay destination windows.
- Refresh is a separate close+reopen path.
- Hủy tách and Đóng xem are distinct visible actions.
- C16 remains the actual game-window Đóng hết task.
- Exact secondary user-initiated state changes and Hủy tách-vs-Đóng xem embedded restoration remain explicit UNKNOWN.

## C13 FILES
- docs/tasks/C13.md
- docs/window/C13_CLOSE_VIEW_STATIC_EVIDENCE.tsv
- docs/window/C13_CLOSE_VIEW_FLOW.md
- docs/window/C13_CLOSE_VIEW_MODEL.json
- WINDOW_BEHAVIOR_MATRIX.md

## C14 VERIFIED RESULTS
- Tách rời uses _toggle_detached_preview and a real DWM detached-overlay subsystem.
- Detached region is documented as x=0, y=768 to screen bottom, width screen_width-450.
- Detached overlays have topmost behavior.
- detached_auto_open is persisted with fallback True and uses silent no-window opening.
- detached_grid is persisted with recovered default-like value 3.
- Detached control bar includes Cột/Tên/HP/Lv/Map/refresh/Hủy tách/Đóng xem.
- _detached_update_loop rebuilds on game-list changes independently of Start-tab visibility.
- Exact embedded-preview visibility/restoration sequence remains explicit UNKNOWN.

## C14 FILES
- docs/tasks/C14.md
- docs/window/C14_DETACHED_PREVIEW_STATIC_EVIDENCE.tsv
- docs/window/C14_DETACHED_PREVIEW_FLOW.md
- docs/window/C14_DETACHED_PREVIEW_MODEL.json
- WINDOW_BEHAVIOR_MATRIX.md

## C15 VERIFIED RESULTS
- Main preview has a real `Làm mới` control and a dedicated full-list DWM rebuild method.
- Full rebuild clears old preview items, unregisters DWM thumbnails, destroys destination overlay HWNDs/frames, then recreates live DWM previews from the current game-window/cache set.
- Current 1x–5x preview-column selection is reused during rebuild.
- Manual preview ordering is preserved by HWND across refresh/rebuild.
- `_update_window_previews_loop` can also conditionally rebuild the list when `need_refresh` is true and separately refreshes labels/HP.
- Detached ↺ refresh uses `_refresh_detached_preview`: close then reopen to reload the current game-window list.
- Exact Tk command expression for `btn_refresh_preview`, exact `need_refresh` formula, and forced fresh-memory-read semantics remain explicit UNKNOWN.

## C15 FILES
- docs/tasks/C15.md
- docs/window/C15_REFRESH_STATIC_EVIDENCE.tsv
- docs/window/C15_REFRESH_FLOW.md
- docs/window/C15_REFRESH_MODEL.json
- WINDOW_BEHAVIOR_MATRIX.md

## C16 VERIFIED RESULTS
- Preview `Đóng hết` is wired to the original close-all callback and shared game-close utility.
- The original utility operates on the current game-window HWND list and sends each live game window a normal Windows close request.
- No force-termination path for the main game executable was recovered in the shared close utility.
- Lingering Unity crash-handler processes are handled by a separate cleanup path.
- This is distinct from `Đóng xem` (preview teardown) and `Làm mới` (preview rebuild).
- Existing discovery/preview maintenance eventually removes stale preview/master state after HWNDs disappear.
- Exact immediate post-click refresh timing remains explicit UNKNOWN; close-specific confirmation behavior was not recovered.

## C16 FILES
- docs/tasks/C16.md
- docs/window/C16_CLOSE_ALL_STATIC_EVIDENCE.tsv
- docs/window/C16_CLOSE_ALL_FLOW.md
- docs/window/C16_CLOSE_ALL_MODEL.json
- WINDOW_BEHAVIOR_MATRIX.md

## C17 VERIFIED RESULTS
- Preview arrows reorder the embedded preview list.
- Left uses delta -1; right uses delta +1.
- Order state is keyed by source HWND and survives refresh/rebuild.
- Boundary behavior and detached-order propagation remain explicit UNKNOWN.

## C18 VERIFIED RESULTS
- `Dồng bộ các cửa sổ` is a real toggle backed by `_toggle_layout`.
- Runtime state includes `layout_active`, `sync_layout_running`, `sync_loop_id`, and grid-slot state.
- The maintenance path uses `_sync_windows_loop` → `_layout_worker` → worker-cached HWNDs → `_arrange_grid`.
- Grid application is master-aware: current master is index 0/top-left.
- Xếp-lưới mode auto-enables layout synchronization; Auto/manual disables it.
- Runtime max-window policy is integrated; the over-limit path stops both synchronization subsystems.
- Manual master change auto-disabling layout sync is not proven.
- Exact worker cadence, initial layout-active value, and exact stop/cancel ordering remain explicit UNKNOWN.

## C18 FILES
- docs/tasks/C18.md
- docs/window/C18_LAYOUT_SYNC_STATIC_EVIDENCE.tsv
- docs/window/C18_LAYOUT_SYNC_FLOW.md
- docs/window/C18_LAYOUT_SYNC_MODEL.json
- WINDOW_BEHAVIOR_MATRIX.md

## C19 VERIFIED RESULTS
- `Dồng bộ phím chuột` is a real persistent input-synchronization subsystem.
- The selected master window is the event source; other game windows are targets.
- Mouse coordinates are converted to master-client coordinates and scaled to each target client size.
- Click processing is ordered; scroll and mouse-move have dedicated paths, with move throttling.
- Input-sync keepalive is exactly 1.5 seconds.
- Stale target state is released by a watchdog at about 10 seconds.
- Changing master while input sync is active turns input sync off and releases target state.
- Keyboard press/release uses a dedicated synchronization path.
- Exact key-message format, move-throttle interval, listener startup timing and retry delay remain explicit UNKNOWN.

## C19 FILES
- docs/tasks/C19.md
- docs/window/C19_INPUT_SYNC_STATIC_EVIDENCE.tsv
- docs/window/C19_INPUT_SYNC_FLOW.md
- docs/window/C19_INPUT_SYNC_MODEL.json
- WINDOW_BEHAVIOR_MATRIX.md

## C20 VERIFIED RESULTS
- The locked original screenshot shows three simultaneously tracked game identities: 75C.S6, TổngTài.S6, ThápCa.
- TổngTài.S6 is selected as master while the preview order starts with 75C.S6, proving master order and preview order are independent.
- Embedded preview uses 2 columns while physical game-window layout independently uses a 3×4 grid setting.
- With three live HWNDs, the combined model is one master source plus two follower targets.
- C01–C19 discovery, identity, DWM preview, ordering, layout, refresh, close, layout-sync and input-sync models are mutually coherent.
- Exact physical grid geometry/timing and a future reconstructed-build Windows three-HWND parity run remain deferred rather than falsely marked PASS.

## C20 FILES
- docs/tasks/C20.md
- docs/window/C20_THREE_HWND_EVIDENCE.tsv
- docs/window/C20_THREE_HWND_FLOW.md
- docs/window/C20_THREE_HWND_MODEL.json
- WINDOW_BEHAVIOR_MATRIX.md

## GATE C DECISION
- C01–C20 analysis is complete for original static + screenshot evidence.
- Remaining unknowns are explicit and localized.
- Reconstructed executable runtime parity is deferred to the later implementation/parity stage.

## D01 VERIFIED RESULTS
- Frozen inner EXE hash rechecked against Gate A.
- 244 valid exact module markers were recovered from the original EXE.
- 538 unique module-like `.py` filename references were recovered as supplemental provenance.
- 32 physical native `.pyd` modules were inventoried from the frozen distribution.
- Canonical D01 inventory contains 573 rows: 570 accepted unique names + 3 rejected string artifacts.
- Accepted categories: 42 TLM internal, 225 third-party Python, 265 stdlib references, 32 native extensions, 6 Nuitka hooks.
- Confidence is explicit: 276 HIGH, 294 MEDIUM; filename-only references are not overclaimed as executed modules.
- The full row-level inventory is committed as `D01_MODULE_INVENTORY.tsv.gz`; helper EXEs/DLLs/resources are inventoried separately.

## D01 FILES
- docs/tasks/D01.md
- docs/modules/D01_MODULE_INVENTORY.tsv.gz
- docs/modules/D01_MODULE_SUMMARY.json
- docs/modules/D01_TLM_INTERNAL.json
- docs/modules/D01_NATIVE_PYD.json
- docs/modules/D01_NUITKA_HOOKS.json
- docs/modules/D01_HELPER_FILES.tsv
- tools/D01_EXTRACT_MODULES.py

## D02 VERIFIED RESULTS
- 37 TLM internal modules with exact compiled module markers were eligible as relationship sources.
- 5 filename-only TLM names remain targets-only for this extraction method: TLMTool, bag_filter, emu_reader, pixel, proxy_refresh.
- 377 deduplicated static module-reference edges were recovered from compiled module blocks.
- Target categories: 132 TLM internal, 59 third-party Python, 153 stdlib references, 33 native-extension references.
- The 132 internal→internal edges span 31 sources and 36 distinct internal targets.
- `info_tab` and `utils` are the strongest internal reference hubs in this graph.
- Every edge is explicitly labeled `STATIC_REFERENCE_NOT_IMPORT_PROOF`; exact Python import syntax/order is not fabricated.
- The internal graph is persisted compressed; the full 377-row evidence table is reproducible with the committed extractor.

## D02 FILES
- docs/tasks/D02.md
- docs/modules/D02_RELATIONSHIP_SUMMARY.json
- docs/modules/D02_INTERNAL_RELATIONSHIPS.tsv.gz
- tools/D02_EXTRACT_RELATIONSHIPS.py

## C15–C20 + D01 AUDIT
- Exact user archive and inner EXE hashes rechecked against Gate A.
- C15/C16 semantics remain correct; evidence tables had several nearby/off-by-one offsets and were normalized to exact literal/symbol starts.
- C17/C18 semantic models remain correct with their existing explicit unknowns.
- C19 model status metadata was aligned with the detailed task status.
- C20 wording was tightened to static+visual original evidence; no new live runtime trace is claimed.
- D01 reproducibility was corrected: raw source-filename candidates = 541; normalized count = 538 after collapsing three exact leading-u duplicate-tag pairs.
- Canonical D01 accepted inventory remains 570 names; D02 is unaffected.
- Audit report: docs/tasks/C15_C20_D01_AUDIT.md

## D03 VERIFIED RESULTS
- Third-party presence, exact version evidence and direct TLM reference evidence are separated.
- Exact package versions recovered for requests 2.34.2, urllib3 2.7.0, Pillow 12.3.0, cryptography 49.0.0, idna 3.18, certifi 2026.06.17, PyAutoGUI 0.9.54, pyperclip 1.11.0, PyScreeze 1.0.1, PyTweening 1.2.0, PyMsgBox 1.0.9, PyGetWindow 0.0.9 and six 1.17.0.
- PyWin32 binaries expose File/ProductVersion 3.10.312.0.
- 32 PYD files split into 16 CPython/runtime extensions and 16 third-party native extensions.
- Direct internal reference mapping identifies major Windows/input/process families without overclaiming exact Python import syntax.
- Frida/psutil/pynput/keyboard/mouse/typing_extensions/Brotli/cffi package versions remain UNKNOWN where no strong version evidence was recovered.

## D03 FILES
- docs/tasks/D03.md
- docs/modules/D03_DEPENDENCY_MATRIX.tsv
- docs/modules/D03_DEPENDENCY_SUMMARY.json
- docs/modules/D03_DIRECT_USAGE.tsv
- tools/D03_EXTRACT_DEPENDENCIES.py

## D04 VERIFIED RESULTS
- D02 132-edge internal reference graph was reproduced and preserved as Tier-B static-reference evidence.
- Stronger Tier-A contextual edges were separated from simple compiled-name adjacency.
- Key contextual relationships include Start→Daily/Farm coordination, FarmData→Start/DLL injector, MemoryItems→MemoryReader/DLL injector, FastTravel→Forwarder, and emulator input→remote/farm/train/permission integration.
- Three contextual relationships stronger than the original D02 exact-name edge set are recorded separately rather than silently mutating D02.
- Internal modules were grouped into shell/orchestration, feature automation, low-level game integration, guard/metadata/support, and emulator layers.
- Five filename-only internal names remain unable to provide reliable outgoing exact-marker blocks: TLMTool, bag_filter, emu_reader, pixel, proxy_refresh.
- Exact original Python import syntax remains UNKNOWN.

## D04 FILES
- docs/tasks/D04.md
- docs/modules/D04_INTERNAL_DEPENDENCIES.tsv
- docs/modules/D04_CONTEXTUAL_EDGES.tsv
- docs/modules/D04_ARCHITECTURE.json
- tools/D04_BUILD_INTERNAL_GRAPH.py

## D05 VERIFIED RESULTS
- 37 exact-marker TLM compiled-module blocks were mapped from the frozen inner EXE.
- 273,502 raw printable strings fall inside those block intervals; a reproducible classifier selects 38,901 high-signal rows.
- High-signal categories include WinAPI/constants, logs/UI text, paths/files, URLs and meaningful symbols.
- Exact offsets and per-module counts are persisted; representative samples are committed.
- The unusually large info_tab marker interval is explicitly treated as compiled-block provenance, not literal source-file ownership.
- Five filename-only internal names remain unassigned because this method requires exact module markers.
- Full raw/high-signal tables can be reproduced by the committed extractor; original Python source-line ownership is not claimed.

## D05 FILES
- docs/tasks/D05.md
- docs/modules/D05_MODULE_STRING_SUMMARY.tsv
- docs/modules/D05_HIGH_SIGNAL_SAMPLES.tsv
- tools/D05_EXTRACT_MODULE_STRINGS.py

## D06 VERIFIED RESULTS
- Gate-A package DATA set was reconciled: 23 DATA files plus Default.ppx as an additional config resource.
- Fourteen high-entropy MZ/PE-like invalid .dat files remain opaque; semantic roles are not inferred from filenames.
- Active data/resources.dat is a valid x64 PE DLL-format injected payload; five old/backup copies are preserved separately.
- version.dat is a valid x64 version.dll-compatible proxy PE with Version API exports.
- automove_log.txt and proxy_working.txt are plain-text runtime data/log files with direct consumers.
- Default.ppx is the Proxifier XML template using local SOCKS5 127.0.0.1:10800 for the game rule.
- Persistent PC settings/config, login JSON state, forwarder/proxy coordination files, Android guest JSON, and logs are separated by lifecycle.
- emu_client.js and ld_remote.js are explicitly deferred to D07.

## D06 FILES
- docs/tasks/D06.md
- docs/data/D06_PACKAGE_DATA.tsv
- docs/data/D06_RUNTIME_CONFIG_REFERENCES.tsv
- docs/data/D06_DATA_SUMMARY.json
- tools/D06_INVENTORY_DATA.py

## D07 VERIFIED RESULTS
- emu_client.js is a 150-line Frida 17 resident RPC memory reader with 7 exported RPC methods.
- Player structure offsets/validation and bag Site==10 counting were recovered directly from the shipped JS.
- ld_remote.js is a 1297-line AutoX/Auto.js floating guest UI and HTTP client.
- PC listener contract includes 0.0.0.0, default port 8765, default token tlm, emulator identification by peer IPv4, maps/status/config/coords/action endpoints.
- Overlay uses local AutoX storage plus /sdcard/TLM/tlm_<aid8>.json as an ADB-readable bridge.
- forwarder.exe is a separate Nuitka SOCKS4/SOCKS5/HTTP CONNECT proxy helper with its own runtime state files.
- bootstrap/update/7z/Proxifier helper connections were recorded without reopening Gate-A scope.
- No helper, Frida script, emulator script or injected payload was executed during D07; live runtime parity remains deferred.

## D07 FILES
- docs/tasks/D07.md
- docs/helpers/D07_JS_RPC_CONTRACT.tsv
- docs/helpers/D07_HELPER_FILES.tsv
- docs/helpers/D07_EMULATOR_ARCHITECTURE.json
- tools/D07_ANALYZE_HELPERS.py

## D08 VERIFIED RESULTS
- D01–D07 were reconciled into one integrated architecture handoff.
- Main architecture is separated into shell/orchestration, feature automation, shared support/guards, low-level PC game integration, emulator path, proxy helpers, update helpers and persistent data stores.
- Diagram edge meanings explicitly separate contextual Tier-A evidence, static Tier-B references, protocol/helper boundaries and data associations.
- Key parity constraints are preserved: master vs preview order, physical vs preview grids, layout vs input sync, PC vs emulator paths, runtime config vs immutable payload, static reference vs exact import syntax.
- Gate D is complete for static architecture evidence; live helper/emulator/runtime parity remains deferred.

## D08 FILES
- docs/tasks/D08.md
- docs/architecture/D08_MODULE_ARCHITECTURE.mmd
- docs/architecture/D08_ARCHITECTURE_LEGEND.tsv
- docs/architecture/D08_ARCHITECTURE.json

## GATE D DECISION
- D01–D08 COMPLETE / VERIFIED for static architecture evidence.
- Remaining uncertainty is explicit and moves to later implementation/runtime gates.

## E01 VERIFIED RESULTS
- Main shell class is TLMMainApp with a normal GUI lifecycle plus a special --forwarder branch.
- Startup diagnostics include debug logger, faulthandler crash logging and a custom threading exception hook.
- A Windows named mutex TLMTool_SingleInstance enforces single-instance behavior.
- Tk root, TLMMainApp, splash close contract and mainloop are all recovered; exact micro-order of app/splash construction remains explicit UNKNOWN.
- TLMMainApp constructs the potential tab set, starts CPU monitoring, binds NotebookTabChanged and installs permission/plan/limit lifecycle hooks.
- TLMInfoTab participates in startup service behavior: startup server call, plan/license/permission update and heartbeat.
- Selected-tab refresh loops are coordinated centrally.
- Normal cleanup is driven through Tk/widget Destroy handlers; exact cross-tab destroy order remains UNKNOWN.
- Heartbeat-enforced forced quit destroys the GUI then uses os._exit to terminate despite non-daemon workers; that path intentionally leaves forwarder child process running.

## E01 FILES
- docs/tasks/E01.md
- docs/core/E01_LIFECYCLE_STATIC_EVIDENCE.tsv
- docs/core/E01_LIFECYCLE_FLOW.md
- docs/core/E01_LIFECYCLE_MODEL.json

## E02 VERIFIED RESULTS
- Root title is `TLMTool`; `250x20` is a transient startup geometry, not the final production size.
- Root startup attributes include `-topmost=True`, frozen `_MEIPASS` icon resolution for `icon.ico`, and `withdraw` during construction.
- Root/global default font is statically recovered as the exact tuple `("Segoe UI", 9)` applied via `option_add("*Font", ...)`.
- This corrects the earlier broad B13 font-size UNKNOWN: root/global size 9 is now verified; explicit per-widget overrides remain unknown where not separately evidenced.
- ttk.Notebook is packed with fill/expand behavior and exact 5 px outer packing margin; Gate-B raster geometry corroborates the 5 px margin.
- `TNotebook.Tab` padding and `TNotebook` tabmargins are configured, but exact source list values remain explicit UNKNOWN.
- `position_window_top_right` uses screen width/height plus exact literals 80, 450 and 10; high-confidence model is w=450, h=screen_height-80, x=max(0,screen_width-w-10), y=0.
- The exact arithmetic source expression remains not directly recovered; the production screenshot target remains 450×1000 client pixels.
- Literal `350x450+1621+0` is quarantined as stale/example/unknown-flow and is not allowed to override 12/12 screenshot evidence.
- No explicit resizable/minsize/maxsize policy was recovered in the main-shell block.

## E02 FILES
- docs/tasks/E02.md
- docs/core/E02_ROOT_STATIC_EVIDENCE.tsv
- docs/core/E02_ROOT_FLOW.md
- docs/core/E02_ROOT_MODEL.json
- docs/tasks/B13.md (corrected root/default font evidence)
- docs/UI_BASELINE_TLM.md (B13 correction)
- docs/ui/B13_STATIC_STYLE_EVIDENCE.tsv

## E03 VERIFIED RESULTS
- `create_tabs` uses local `_new_tab` plus `_tab_inner`, `_tab_frames`, `_tab_keys` maps.
- Potential insertion order contains Start/Login/Party/Train/Train LSV/Train LD/Phó Bản/Daily/Dồn/Rao/Tối ưu/Info/Proxy/Debug/Debug Android.
- Gate-B visible production order is the same sequence with Train LD, Proxy, Debug and Debug Android hidden.
- Info is the invariant always-visible fallback; if selected tab becomes hidden, selection moves to Info.
- Debug/Android/Proxy are dev-gated; Dồn/Rao/Tối ưu are permission-controlled.
- Tab content has a one-time lazy-build guard plus `_rebuild_tab` path.
- `_make_scrollable` provides Canvas+vertical Scrollbar+MouseWheel wrapper.
- Central refresh lifecycle stops old tab polling and starts selected tab polling; after build only selected refresh-capable tab polls.
- Permission/account-limit changes can disable child controls without destroying tab content.

## E03 FILES
- docs/tasks/E03.md
- docs/core/E03_TAB_STATIC_EVIDENCE.tsv
- docs/core/E03_TAB_ORDER.tsv
- docs/core/E03_TAB_LOADER_MODEL.json

## E04 AUDIT / COMPLETION
- Existing E04 report and state table were audited against prior Gate-D/E01-E03 evidence.
- No semantic contradiction was found; the ownership model is coherent.
- The declared JSON model artifact was missing and has now been created.

## E04 VERIFIED RESULTS
- TLMMainApp owns shell coordination state and tab instance refs.
- permission_guard owns normalized permission/plan/limit decisions and the block-notifier service API.
- TLMInfoTab owns server/license/session/heartbeat transport state.
- TLMStartTab owns multi-window HWND/preview/grid/sync runtime state.
- Feature FSM/account/schedule state remains tab-owned.
- Cross-thread block notifications marshal back to Tk with root.after.
- Persistent files remain separate from in-memory app state.
- Exact private permission_guard backing globals and heartbeat mutation order remain explicit UNKNOWN/PARTIAL.

## E04 FILES
- docs/tasks/E04.md
- docs/core/E04_SHARED_STATE.tsv
- docs/core/E04_SHARED_STATE_MODEL.json

## E05 VERIFIED RESULTS
- Shared config service exposes CONFIG_PATH/CONFIG_DIR/SETTINGS_PATH plus get/load/save/read/write helpers.
- Shared central config path is %APPDATA%/TLMTool/config.ini using RawConfigParser and UTF-8 section/key writes.
- settings.ini safe-read behavior explicitly tolerates duplicate keys with last-wins/no-error semantics.
- settings.ini writes use temp file + os.replace atomic replacement and dated backup/pruning behavior.
- _BACKUP_KEEP exists but its exact numeric value remains UNKNOWN.
- _settings_lock is shared across config-consuming tabs; exact lock class remains UNKNOWN.
- Feature tabs share the [Settings] section but own typed defaults/fallbacks and JSON-in-INI complex values.
- InfoTab has a separate config.ini simple-dict ConfigParser contract and is not silently merged with the central APPDATA config helper.
- Runtime JSON/text state files remain separate from the shared INI service.
- No global filesystem hot-reload watcher was recovered.

## E05 FILES
- docs/tasks/E05.md
- docs/core/E05_CONFIG_STATIC_EVIDENCE.tsv
- docs/core/E05_CONFIG_FLOW.md
- docs/core/E05_CONFIG_MODEL.json

## E06 VERIFIED RESULTS
- debug_logger.setup creates the central append-only session log under log/tlmtool.log and tees stdout/stderr to the original streams plus the file.
- Session Start/End markers, runtime/executable information and timestamp formatting are recovered.
- Central log trimming drops oldest content when MAX_SIZE is exceeded and keeps newest KEEP_SIZE content; exact numeric size values remain UNKNOWN.
- Main startup separately enables faulthandler against crash_fault.log.
- A custom threading.excepthook records [THREAD-EXC] metadata plus traceback through the central log path.
- memory diagnostics use separate tlm_memory.log with documented >1MB truncation behavior.
- data/automove_log.txt is monitored by Tối ưu watchdog for per-PID Perf: ping evidence and belongs to the injected/performance diagnostic boundary.
- No explicit central logging lock/queue was recovered; concurrent-write serialization remains NOT RECOVERED.

## E06 FILES
- docs/tasks/E06.md
- docs/core/E06_LOGGING_STATIC_EVIDENCE.tsv
- docs/core/E06_LOGGING_FLOW.md
- docs/core/E06_LOGGING_MODEL.json

## E07 VERIFIED RESULTS
- Concurrency is split across Tk after/after_cancel jobs, Python worker threads, listener/service threads, and external/native process boundaries.
- Background workers return Tk mutations through root.after rather than touching widgets directly.
- CPU monitor is a daemon worker with bounded join cleanup.
- Start input sync uses a Queue-backed serialized worker plus Locks and daemon listener threads.
- Start preview/cache worker performs window/basic-info refresh around 3s and heavier memory refresh around 8s without Tk calls.
- Login owns cancellation Events and a launch Lock; Party owns cancellation/locks and one-thread-per-group execution with join(timeout).
- Daily/Farm/Train families use per-account threads, stop Events/running-generation flags and main-thread UI apply.
- Emulator remote listener is a daemon ThreadingHTTPServer service with shutdown/server_close.
- Info heartbeat is centrally coordinated through Tk after-id state.
- CreateRemoteThread/helper processes are explicitly separated from Python threading.
- Exact daemon flag for every worker, every join timeout, and simultaneous global stop ordering remain explicit UNKNOWN.

## E07 FILES
- docs/tasks/E07.md
- docs/core/E07_THREAD_STATIC_EVIDENCE.tsv
- docs/core/E07_THREAD_FLOW.md
- docs/core/E07_THREAD_MODEL.json

## E08 VERIFIED RESULTS
- Normal close is driven by Tk/root/widget destruction plus tab-owned <Destroy> save/stop hooks; no main-shell WM_DELETE_WINDOW callback was recovered.
- Twelve tab/module Destroy hooks were enumerated; exact cross-tab destroy order remains UNKNOWN.
- Forced heartbeat shutdown uses a confirmation/strike model, waits about 5s on the second blocking state, destroys the GUI and uses os._exit.
- Forced heartbeat shutdown explicitly leaves the independent forwarder process running.
- TLMMainApp._rebuild_tab and preview refresh paths are in-process widget/view rebuilds, not process restarts.
- Start-page Reload is an unstick/input-window recovery command via _unstick_all_cmd / unstick_windows, not a TLMTool restart; exact helper micro-sequence remains UNKNOWN.
- Login row Reload advances that forwarder proxy, closes that account's tracked game window if present, then immediately logs the account in with the new proxy.
- Auto-update explicitly confirms, closes all game windows, stops all forwarders, resolves update link, finds/spawns update.exe; external updater replaces files and relaunches TLMTool.
- Normal user-close global forwarder cleanup remains NOT PROVEN/UNKNOWN.

## E08 FILES
- docs/tasks/E08.md
- docs/core/E08_SHUTDOWN_STATIC_EVIDENCE.tsv
- docs/core/E08_SHUTDOWN_FLOW.md
- docs/core/E08_SHUTDOWN_MODEL.json

## E09 VERIFIED RESULTS
- Process-level diagnostics use faulthandler plus a custom threading.excepthook with traceback logging.
- Feature workers commonly expose done/error callbacks and restore UI state on the Tk main thread.
- Config load/save/parse failures are locally caught/logged and do not terminate the main GUI; per-key fallback remains feature-owned.
- Server startup/heartbeat validates timeout/status/token/decode results, records failures and reschedules rather than crashing on the first failure.
- Runtime permission_guard is the logic boundary; UI disabled state is only cosmetic. Fail-closed behavior is explicitly documented for sensitive missing/invalid server states, with a special limit<=0 trial/unlimited semantic.
- Synchronous window messaging uses SendMessageTimeout/SMTO_ABORTIFHUNG; Start input retries a short path two times on transient Unity-busy failure then skips that slave/current action.
- Input stale-lock watchdog and idempotent unblock recover missing releases/master changes.
- Emulator remote validates token/action/identity/required fields/config value formats and returns structured ok/error results.
- Exact retry delay, exact HTTP status mapping for every emulator error, and exhaustive source-level try/except tables remain explicit UNKNOWN/NOT_RECOVERED.

## E09 FILES
- docs/tasks/E09.md
- docs/core/E09_ERROR_STATIC_EVIDENCE.tsv
- docs/core/E09_ERROR_FLOW.md
- docs/core/E09_ERROR_MODEL.json

## E10 VERIFIED RESULTS
- Start/stop coordination is distributed across TLMMainApp shell state, StartTab quick orchestration and feature-owned FSMs; no universal global feature FSM was recovered.
- Entering Xếp-lưới explicitly stops active Farm/Train plus Daily Trừng Ác and Tàng Bảo Đồ before enabling layout+input sync.
- Switching Auto/manual disables both synchronization systems.
- Start quick commands delegate to feature-tab methods in short threads; feature tabs remain authoritative owners of long-running FSM/workers.
- Farm/Train LSV/Dồn/Daily expose synchronization helpers that mirror authoritative feature state back to Start buttons.
- Farm/Train LSV/Dồn have per-account plus all-account start/stop surfaces; Daily keeps separate Trừng Ác/Tàng Bảo Đồ FSMs.
- Rao/Tối ưu expose _start_all_busy guards; Phó Bản exposes stop-all-run control.
- Runtime permission/account-limit checks remain authoritative at action time.
- Login owns post-login routing; Party waits all groups then executes its configured post-party action once.
- Selected-tab refresh start/stop is UI polling only and is separate from feature execution.
- Universal 'starting one feature stops all others' behavior was NOT recovered and must not be invented.

## E10 FILES
- docs/tasks/E10.md
- docs/core/E10_COORDINATOR_STATIC_EVIDENCE.tsv
- docs/core/E10_COORDINATOR_FLOW.md
- docs/core/E10_COORDINATOR_MODEL.json

## GATE E DECISION
- E01–E10 COMPLETE / VERIFIED for static core/lifecycle evidence.
- Explicit unknowns remain localized and move to later feature/runtime parity gates.

## F01 VERIFIED RESULTS
- Re-opened the exact user archive and inner TLMTool.exe before using Login screenshot evidence.
- Current Login screenshot hash matches the Gate-B B03 baseline exactly.
- Original EXE resolves all three Login group widgets as Tk LabelFrame using Bold.TLabelframe.
- Game group controls, conditional game-path/captcha-status labels, schedule Checkbutton/readonly Combobox/radio widgets, account Canvas+Scrollbar structure and bottom Bắt đầu button were recovered.
- Exact after-login source labels/internal values are Chờ/wait, Party/party, Train/train, Train LSV/train_lsv, Dồn vàng/don.
- B03 screenshot transcription `Dồn văn` was corrected: source label is `Dồn vàng`; right-edge raster clipping hid/misled the final glyph.
- Header selector is a custom check-glyph Button calling _toggle_all_checks, not an unknown native checkbox.
- Account rows use custom selector Button + account/password Entry + readonly captcha Combobox + Login Button + proxy/reload Button.
- Captcha modes are Không / Tool / Proxy; proxy action is Tool→⇄, Proxy→➜, Không→blank gray disabled.
- Logical account-row capacity is exactly 100. Plan updates may hide/restore rows through _hidden_rows/apply_account_row_limit.
- Locked screenshot geometry remains authoritative: 17 full rows + partial 18th visible in the viewport, row pitch 35 px, bottom Bắt đầu 410×30.
- Hidden/conditional lbl_dll_status, lbl_sched_countdown, lbl_proxifier_status and _profile_btns are not assigned invented pixels.

## F01 FILES
- docs/tasks/F01.md
- docs/login/F01_LOGIN_UI_STATIC_EVIDENCE.tsv
- docs/login/F01_LOGIN_UI_GEOMETRY.tsv
- docs/login/F01_LOGIN_UI_MODEL.json
- docs/tasks/B03.md (F01 supplement/correction)
- docs/ui/B03_LOGIN_DEFAULTS.json (resolved screenshot-only unknowns)
- docs/UI_BASELINE_TLM.md (F01 Login supplement)

## F02 VERIFIED RESULTS
- Login account rows persist in the shared settings.ini [Settings] / accounts entry.
- Rows are newline-delimited; row fields are pipe-delimited.
- Save-side field order is check, user, pass, captcha, proxy.
- Normalized cache fields are check, username, password, captcha_mode, proxy_env.
- _accounts_cache is the plain-dict persistence model synchronized from widgets before save.
- The model has 100 logical rows; plan-limited rows are preserved in _hidden_rows.
- Autosave is debounced by 300 ms; <Destroy> provides a separate final-save path.
- login_online.json is runtime live-window/session state, not the account list.
- last_login_times.json is separate login-history state.
- Exact serialized check token and exact legacy Có migration mapping remain UNKNOWN.

## F02 FILES
- docs/tasks/F02.md
- docs/login/F02_ACCOUNT_STORAGE_STATIC_EVIDENCE.tsv
- docs/login/F02_ACCOUNT_STORAGE_FLOW.md
- docs/login/F02_ACCOUNT_STORAGE_MODEL.json

## F03 VERIFIED RESULTS
- Login credential masking is display-only and uses the Entry show option with a one-character star mask.
- The show/hide toggle applies to visible rows and rows preserved in _hidden_rows without changing the underlying Entry text.
- Account cache and persistence carry the credential field directly; no credential encryption/base64/DPAPI/keyring transform was recovered in LoginTab.
- Selected login rows pass the credential forward as mk/mk_val into the original login sequence.
- Username normalization has strip evidence; no separate credential-strip evidence was recovered.
- No explicit credential clipboard path or explicit credential log format was recovered.
- Delimiter escaping for the pipe/newline account format was not recovered.

## F03 FILES
- docs/tasks/F03.md
- docs/login/F03_PASSWORD_STATIC_EVIDENCE.tsv
- docs/login/F03_PASSWORD_FLOW.md
- docs/login/F03_PASSWORD_MODEL.json

## F04 VERIFIED RESULTS
- Canonical Login game executable is exactly "Thần Long  Mobile.exe" with two spaces.
- Folder selection uses tkinter.filedialog.askdirectory; user selects a directory, not an EXE.
- _resolve_game_dir returns (resolved_dir | None, note) and documents four recognition cases: selected direct, selected/Game, selected child-inside-Game parent recovery, and one-level child scan prioritizing names containing game.
- Resolver strips trailing slash/backslash and reports nonexistent/not-found outcomes without requiring a hard-coded install root.
- Invalid selection uses messagebox.showerror with title "Thư mục game không hợp lệ" and example D:\ThanLongMobile_PC\Game.
- Success status begins "✅ Đã chọn game thành công:" and reuses/re-packs lbl_game_dir.
- Valid path recognition enables path-dependent _profile_btns.
- game_dir appears in both Login load-config and save-config blocks, so the resolved directory participates in persistent Login configuration.
- _get_exe_path is the launch-facing boundary; Open Game/login/profile paths reject missing directory or missing canonical executable.
- Profile launch receives a common exe_path plus profile_idx 1-5; no separate per-profile game-install directory contract was recovered.
- Exact _get_exe_path revalidation microsequence, immediate config-flush timing, and launcher cwd derivation remain UNKNOWN/deferred.

## F04 FILES
- docs/tasks/F04.md
- docs/login/F04_GAME_PATH_STATIC_EVIDENCE.tsv
- docs/login/F04_GAME_PATH_FLOW.md
- docs/login/F04_GAME_PATH_MODEL.json

## F05 VERIFIED RESULTS
- Generic Open Game is guarded by has_permission(login_tab), check_account_limit(login, extra=1), configured game_dir and _get_exe_path.
- _open_game dispatches launch work to daemon _launch_worker rather than blocking Tk.
- Generic launcher uses _make_safe_env, _apply_proxy_hook_env and spawn_and_inject with a recovered 15,000 ms timeout literal.
- _make_safe_env(tlm_profile:str)->dict keeps Windows essentials + TLM_PROFILE and excludes Python/VirtualEnv leakage.
- Login proxy overlay exposes TLM_PROXY_ENABLE/HOST/PORT/FAIL with host 127.0.0.1; exact enable encoding remains F08/UNKNOWN.
- Active launch payload is ./data/resources.dat.
- spawn_and_inject creates the game with CREATE_SUSPENDED, injects LoadLibraryW via VirtualAllocEx/WriteProcessMemory/CreateRemoteThread, waits, then NtResumeProcess, returning (success,pid,error_msg).
- inject_into_pid is a separate existing-process helper with double-inject guard.
- find_main_window_by_pid binds by returned PID, preferring UnityWndClass or title containing Thần Long, then first visible PID-owned window.
- _launch_one_window serializes game opens under _launch_lock, waits up to 25s for the PID-owned HWND and a stabilization phase, then hands off the HWND.
- Multi-account contract is LAUNCH TUẦN TỰ + LOGIN SONG SONG; only the launcher half is completed in F05.
- Forwarder readiness is a launch precondition when used; a dead required port prevents game launch into that network path.
- _login_resize_monitor checks game-window size every second and only resizes when not 1366x768.
- Profile-specific launch indices are 1-5 with busy/success/inject-failure/error states.
- Exact generic profile-iteration policy, cwd derivation, post-HWND stabilization duration, failure-cleanup micro-order and UnityCrashHandler cleanup timing remain explicit UNKNOWN.

## F05 FILES
- docs/tasks/F05.md
- docs/login/F05_LAUNCHER_STATIC_EVIDENCE.tsv
- docs/login/F05_LAUNCHER_FLOW.md
- docs/login/F05_LAUNCHER_MODEL.json

## F06 VERIFIED RESULTS
- Checked rows are parsed as (row_idx, tk, mk, captcha_mode, proxy); missing username/password is rejected before normal login.
- Row login is asynchronous through _single_login_worker and uses a retry loop bounded by MAX_LOGIN_RETRIES; exact numeric retry value remains UNKNOWN.
- Login mouse actions use background/window-relative click_at through the DLL sync/PostMessage path, so the physical cursor does not move.
- Username/password text uses press_at with WM_CHAR/Unity activation and does not require user physical keyboard focus.
- Readiness is detected with PrintWindow so covered game windows can still be checked.
- login.login1 + login.login2 must both match; login-form timeout is exactly 100s.
- login.update popup is detected and closed at exact coordinate (630,457).
- Exact credential sequence: username click (613,302) → type tk → password click (573,362) → type mk → Login click (684,506).
- login.vaoTroChoi wait has strong static evidence for a 150-check ceiling, followed by click at (684,450); exact poll delay remains UNKNOWN.
- Step 8 awaits common.active with exact timeout 30s and cancellation/window-validity guards.
- On success the worker calls _mark_row_online and _record_login_time; online runtime state and last-login history are updated through the already recovered stores.
- Failed retry attempts use _force_close_window before another launch/login attempt.
- Multi-account behavior keeps F05 launch serialization but allows login-click workers to run in parallel under Semaphore(MAX_PARALLEL_LOGIN); exact semaphore limit remains UNKNOWN.
- The monitor waits for all login threads before aggregating results and resetting overall Login UI.
- Captcha internals remain F07; proxy policy remains F08; post-login routing remains F10.

## F06 FILES
- docs/tasks/F06.md
- docs/login/F06_LOGIN_ACTION_STATIC_EVIDENCE.tsv
- docs/login/F06_LOGIN_ACTION_FLOW.md
- docs/login/F06_LOGIN_ACTION_MODEL.json

## F07 VERIFIED RESULTS
- Current per-row captcha modes are exactly Không / Tool / Proxy.
- Runtime mapping is explicit: Không→direct, Tool→ordinary/free-proxy path, Proxy→row-specific private proxy path.
- Tool path uses the proxy/forwarder helpers and exact runtime log DÙNG PROXY FREE; detailed allocation/rotation remains F08.
- Proxy path uses row private proxy and exact log DÙNG PROXY RIÊNG; missing private proxy is rejected/skipped rather than silently falling back to the free pool.
- _on_captcha_mode_change exact contract: Tool→⇄, Proxy→➜, Không→hidden/blank disabled; mode changes schedule account autosave.
- User-selecting Proxy may auto-open the private-proxy popup; loading saved config must not auto-open it.
- Private-proxy editor has a permission guard, 440x100 popup, accepted input-hint formats and parse_proxy validation surface.
- Login initialization calls _check_dll_status; readiness label has red "Vượt captcha chưa hoạt động" and green "Hệ thống vượt captcha sẵn sàng" states.
- _check_dll_hash_worker uses MD5/freshness logic and can show "Đã cập nhật cấu hình mới nhất" or "Cần cập nhật cấu hình".
- No hard readiness-status gate over the captcha Combobox/login worker was recovered; do not invent one.
- No Login-owned external captcha solver/OCR/2captcha/Selenium API surface was recovered.
- Legacy load surface contains proxy_mode none/free/private plus Không/Có/Tool/Proxy tokens. Exact Có migration and legacy proxy_mode mapping remain UNKNOWN.
- General proxy pool/forwarder rotation/pinning mechanics remain explicitly deferred to F08.

## F07 FILES
- docs/tasks/F07.md
- docs/login/F07_CAPTCHA_STATIC_EVIDENCE.tsv
- docs/login/F07_CAPTCHA_FLOW.md
- docs/login/F07_CAPTCHA_MODEL.json

## F08 VERIFIED RESULTS
- Packaged proxy_working.txt baseline is hash-locked: 131 entries (108 SOCKS5, 17 HTTP, 6 SOCKS4).
- Shared parser contract returns host/port/user/password/protocol and supports explicit SOCKS5/SOCKS4/HTTP plus multiple authenticated/unauthed text forms.
- Login treats proxy_working.txt older than 5 minutes as stale and refreshes it in a worker-thread path.
- proxy_refresh suppresses overlapping refreshes, has a <60s recent-refresh skip guard, downloads/deduplicates/checks proxies in parallel, and writes live proxies fastest-first.
- A real refresh resets every forwarder index to 0 and clears stale advance/allocation state so the new fastest list starts from the beginning.
- Runtime account proxy-advance threshold is 300 seconds / 5 minutes. This is supported by serialized _proxy_reload_threshold=300 and >5/<5-minute call-site logs.
- The original sentence claiming >=30 minutes is stale documentation and is explicitly not treated as runtime truth.
- Multi-account forwarder mapping is port=22200+profile_idx with iid=str(profile_idx); 22200 is reserved for the default instance.
- Multi instances use IID-suffixed mode/index/stats/pid/advance/pinned files.
- Healthy listeners are reused; stale/non-listening or zombie port owners are replaced before game launch; forwarder readiness is required before launch.
- Mode switching is file-driven and does not require restarting a healthy forwarder.
- Private proxy is pinned per IID; pinned failure is PINNED-ONLY with no fallback to the free pool.
- Tool/free mode uses cross-process allocation locking via proxy_alloc.lock/proxy_alloc.txt and a shared proxy_bad.txt failure list.
- Selective routing is critical: GAME SERVER 103.147.34.81 ports 3001/4001 is proxied while CDN/SDK 443 must remain direct.
- _advance_forwarder_proxy uses an advance-file signal plus idx-file confirmation.
- Row reload advances once, closes that row's tracked game session, and immediately re-logins without a second automatic advance.
- forwarder_stats[_IID].json is consumed asynchronously for UI status.
- Exact ALLOC_TTL, BAD_COOLDOWN/PROXY_COOLDOWN numeric values, forwarder ROTATE_INTERVAL and some low-level worker/socket timeouts remain explicit UNKNOWN.

## F08 FILES
- docs/tasks/F08.md
- docs/login/F08_PROXY_STATIC_EVIDENCE.tsv
- docs/login/F08_PROXY_FLOW.md
- docs/login/F08_PROXY_MODEL.json

## USER SCOPE LOCK — PROXY
- User explicitly requested on 2026-10-04: **không phát triển phần Proxy**.
- F08 remains retained as analysis/documentation evidence only.
- Do not implement/extend/fix runtime proxy/network features or create new proxy behavior unless the user explicitly reopens that scope.
- Do not delete existing F08 evidence; later tasks may reference it only to avoid breaking unrelated flows.
- Proxy-specific runtime work in future Gate Q is skipped/analysis-only.

## F09 VERIFIED RESULTS
- Manual Bắt đầu and the schedule checkbox are explicitly independent control paths.
- Schedule enable starts the worker/countdown without immediately opening games; disable stops the worker/clears countdown and leaves existing game windows untouched.
- _schedule_cancel Event and _schedule_active state own cooperative scheduler lifetime.
- Schedule worker checks due events every 20 seconds; countdown UI is updated on the Tk main thread about every second.
- _next_occurrence uses today if the configured HH:MM is still future, otherwise tomorrow.
- Original EXE contains an explicit fix for the old late-enable bug: missed times are not executed immediately; each event advances by +1 day after triggering.
- Scheduled close logs "Đến giờ tắt game (...) — đóng tất cả" and invokes Login close-all semantics; exact internal close/cancel/tracking micro-order remains UNKNOWN.
- Optional shutdown-after-close shows a topmost 340x150 popup with 60-second countdown; closing/Hủy cancels, confirm/timeout invokes shutdown /s /t 0.
- Scheduled open reuses _open_game_batch and therefore uses the currently checked Login accounts plus the F05/F06 launch/login pipeline.
- If a Login batch is already active when open time arrives, the scheduled open is skipped instead of starting a duplicate batch.
- Scheduler remains active after Login success/failure and continues waiting for the close event.
- schedule_on/schedule_close/schedule_open/shutdown_after_close are persisted Login config fields.
- Automatic worker resume on a completely fresh process solely because saved schedule_on=True remains EXPLICIT UNKNOWN.
- Proxy runtime development remains OUT OF SCOPE under the user scope lock recorded in PLAN.md and STATE.md.

## F09 FILES
- docs/tasks/F09.md
- docs/login/F09_SCHEDULER_STATIC_EVIDENCE.tsv
- docs/login/F09_SCHEDULER_FLOW.md
- docs/login/F09_SCHEDULER_MODEL.json

## F10 VERIFIED RESULTS
- Rechecked the current uploaded `TLMTool_2.1.2(4).zip`; its inner `TLMTool.dist/TLMTool.exe` is SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, matching the frozen EXE used by the existing forensic work. Gate A was not repeated.
- Cross-checked the supplied Login screenshot against the EXE before recording UI behavior.
- `Sau khi login` modes are persisted under `after_login`; default/fallback is `wait`.
- Internal mode mapping is: Chờ→wait, Party→party, Train→train, Train LSV→train_lsv, compiled EXE Dồn vàng→don.
- Canonical visible text is `Dồn vàng` / internal `don`. F01/B03 and the frozen EXE agree; the user explicitly reconfirmed `Dồn vàng` during F11.
- `LoginTab._auto_start_after_login` is the generic routing coordinator. Exact original documentation says it waits for the target tab to scan the just-logged windows and then activates that tab's real Bắt đầu path; Chờ does nothing.
- Party has a dedicated helper `_auto_start_party_after_login` using `party_tab_ref`, `_member_rows`, `_running`, and `_toggle_run`.
- Train / Train LSV / Dồn vàng use `farm_tab_ref` / `train_lsv_tab_ref` / `donvang_tab_ref`, scan `_acc_rows`, guard `_farming` / `_farming_acc`, and invoke the real `_toggle_farm`.
- Target tab selection happens before readiness waiting because hidden tabs may not scan while hidden.
- A separate original helper explicitly cross-references `login_tab._wait_and_activate`; F11 resolved the generic wait as 1.0s polling, at most 20 polls / 20s, with `want.issubset(have)` over target `_acc_rows.get("hwnd")` values.
- Generic and Party helpers contain nested main-thread/UI handoff surfaces; final tab/start mutation is not performed blindly from the background wait path.
- Missing tab refs produce warning/skip behavior.
- Already-running target automation is skipped so the toggle is not accidentally inverted/stopped.
- Routing errors are logged locally: tab-switch and auto-start failures do not redefine the completed credential-login result.
- F09 scheduled open and manual Login both reuse `_open_game_batch`; both therefore feed the same post-login routing layer after normal Login completion.
- F11 resolved the generic Login helper HWND readiness predicate/cadence. Exact mixed-success/zero-success routing guard remains runtime-only UNKNOWN.

## F10 FILES
- docs/tasks/F10.md
- docs/login/F10_POST_LOGIN_STATIC_EVIDENCE.tsv
- docs/login/F10_POST_LOGIN_FLOW.md
- docs/login/F10_POST_LOGIN_MODEL.json

## F11 VERIFIED RESULTS
- Re-read PLAN.md and STATE.md; F11 was the only current task and F01–F10 were not redone.
- Current uploaded `TLMTool_2.1.2(4).zip` SHA-256 is `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, byte-identical to the frozen archive already used by F01/Gate A.
- Inner `TLMTool.dist/TLMTool.exe` remains SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Current Login screenshot `TLMTool_4dw2sgi7mQ(4).png` is SHA-256 `a555bce4054a0d32d19c2377a726c7fa2e6b78c03ce80e8291affb6185f04461`, byte-identical to B03/F01; no UI remeasurement was needed.
- Final canonical label is **Dồn vàng** with internal mode `don`. PLAN.md was corrected from stale `Dồn vàng` occurrences to `Dồn vàng`.
- F11 audited F01–F10 as one Login handoff and found no contradiction requiring earlier task redo.
- New static evidence resolves the generic post-login readiness loop:
  - original same-as-`login_tab._wait_and_activate` helper serializes range constants 0/20/1;
  - `issubset` at frozen EXE file offset about `0x2b808ab`;
  - `sleep` at about `0x2b808b5`;
  - serialized float 1.0 immediately follows;
  - explicit documentation says hidden destination tab must be selected then waited on for at most 20s and reads target `_acc_rows.get("hwnd")`.
- Generic Train / Train LSV / Dồn vàng readiness contract is therefore: select tab → once per second build `have` HWND set → ready when `want.issubset(have)` → maximum 20 polls / 20 seconds → final dispatch on main Tk thread.
- Original login_tab metadata shows `_auto_start_after_login` has no explicit success/results parameter; the completion layer owns success/total aggregation and invokes the routing surface separately.
- Exact branch guard for mixed-success and zero-success batches cannot be proven from the static specimen. It remains a runtime-only parity case, not an invented rule.
- Party remains a dedicated `_member_rows` / `_running` / `_toggle_run` path; its exact instruction-level readiness-set construction remains explicit UNKNOWN.
- Proxy runtime development remains OUT OF SCOPE.
- Login research gate F01–F11 is now closed for research and ready for later Stage-S reconstruction; Stage S is not started early.

## F11 FILES
- docs/tasks/F11.md
- docs/login/F11_LOGIN_PARITY_MATRIX.tsv
- docs/login/F11_LOGIN_RECONSTRUCTION_HANDOFF.md
- docs/login/F11_LOGIN_MODEL.json
- docs/tasks/F10.md (F11 resolution note only)
- docs/login/F10_POST_LOGIN_STATIC_EVIDENCE.tsv (resolved readiness rows only)
- docs/login/F10_POST_LOGIN_MODEL.json (resolved handoff fields only)
- PLAN.md (canonical Dồn vàng wording correction)

## GATE F DECISION
- F01–F11 COMPLETE / VERIFIED for Login static+visual research handoff.
- Generic post-login HWND readiness is locked to 1.0s polling, max 20s, set-subset readiness.
- Mixed-success / zero-success route guard remains runtime-only and is explicitly reserved for later Windows original-vs-reconstruction parity testing.
- Proxy runtime implementation remains excluded by user scope lock.

## G01 VERIFIED RESULTS
- Re-read PLAN.md and STATE.md and executed G01 only; no previous Party geometry was remeasured.
- Re-opened the frozen `TLMTool_2.1.2(4).zip` / inner EXE first. Inner `TLMTool.exe` remains SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Party module markers are frozen around `.party_tab`, `party_tab.py`, `<module party_tab>`, and `PartyTab.__init__`.
- Party-owned constructor state surfaces recovered: `_running`, `_cancel`, `_run_lock`, `_run_cancels`, `_targets_lock`, `_refresh_id`, `_refreshing`, `_closing`, `_last_targets`, `_member_rows`, `_sections`, `_sec_team`, `_sec_corps`, plus refs to Phó Bản / Train / Train LSV / Dồn vàng.
- Constructor lifecycle is wired as build UI → load config → bind Destroy cleanup → start refresh.
- Bottom green `Bắt đầu` is a real Party action bound to `_toggle_run`.
- `Sau khi party` is backed by `_after_party` StringVar and exact values: Chờ/wait, Train/train, Train LSV/train_lsv, Dồn vàng/don, Phó bản/phoban. A write trace participates in config persistence.
- `Cấu hình tổ đội` owns the ready-account container `_team_body`.
- `Cấu hình nhóm` is dynamic and parameterized with active team keys `party_groups` / `party_group1`; `+ Thêm nhóm` binds `_add_group_cluster`.
- One group cluster wires: leader label, 6 readonly account Comboboxes (B04 locks 2×3), `Rời nhóm` → `_leave_group`, delete → `_remove_group`, Combobox open → `_open_dropdown`, selection → `_on_group_selected`, group action → `_run_single_cluster`, leader update → `_update_leader_label`, structural renumber → `_renumber_groups`.
- Party refresh consumes shared `start_tab.get_windows`, shared `utils.get_character_info` / `RoleName`, PID/window-identity bind/unbind helpers, and applies worker results back through Tk `after`.
- Party does NOT own DWM preview, layout sync or keyboard/mouse sync. Static scan of the Party module range found no DWM thumbnail, `_toggle_layout`, `_toggle_input`, PostMessage or SendInput ownership. Those remain Start/window-subsystem responsibilities.
- Permission UI wiring recovered through `permission_guard`, `has_permission`, `check_account_limit`, `has_permission_with_limit`, `set_children_state`, `refresh_permission_state`, and `_apply_group_permission`.
- Config uses shared `read_settings` / `write_settings` under `Settings`, with `party_after`, team group JSON, plus compatibility surfaces `party_corps_groups` / `party_corps_group1`.
- Important correction: the old Party module prose mentions `Theo sau đội trưởng` and `Tự nhặt đồ`, and compatibility keys `party_follow` / `party_pick` remain, but the active frozen PartyTab widget/method surface has no matching BooleanVar/widgets/toggle methods. The real matching controls/methods are in PhoBanTab. These two controls must NOT be added to reconstructed Party UI.
- B04 pixel geometry remains unchanged; only its stale static-only note was corrected.
- Detailed HWND enumeration, refresh cadence, stale HWND/process replacement and ready-account identity are deliberately deferred to G02.
- Character-state semantics beyond the shared RoleName surface remain deferred to G03.
- Actual create/invite/run behavior remains deferred to later G action tasks.

## G01 FILES
- docs/tasks/G01.md
- docs/party/G01_PARTY_UI_WIRING_STATIC_EVIDENCE.tsv
- docs/party/G01_PARTY_UI_WIRING_FLOW.md
- docs/party/G01_PARTY_UI_WIRING_MODEL.json
- docs/tasks/B04.md (targeted stale-note correction only)
- docs/ui/B04_PARTY_DEFAULTS.json (targeted G01 resolution note)
- docs/ui/B04_PARTY_STATIC_STRUCTURE.json (targeted G01 resolution note)
- docs/UI_BASELINE_TLM.md (targeted Party baseline correction only)

## G02 VERIFIED RESULTS
- G02 used the frozen original EXE first; B04 geometry was not re-measured.
- Party consumes `start_tab.get_windows()`; no Party-local EnumWindows/IsWindowVisible discovery path was recovered.
- Party refresh uses a daemon worker for cached-window/character reads and a Tk-after apply path for UI/member updates.
- Party recurring refresh is exactly **3000 ms**. Frozen constant bytes `6c b8 17` decode to 3000 with the same small-int encoding already validated in F11.
- Exact first refresh tick timing and exact Tk-after handoff delay remain UNKNOWN.
- Party runtime identity is HWND + PID generation through `_pid_of`, `bind_window_identity`, row `pid`, and `unbind_window_identity`.
- Direct Party log proves same numeric HWND with a new PID is treated as a replaced process generation: old member is removed, identity unbound, widget destroyed, then refreshed.
- `_remove_stale_members(active_hwnds)` removes members whose HWND disappears from the current shared active set.
- Party display name uses shared character info → `RoleName` → `<[^>]+>` sanitization; a `Window ` fallback prefix exists, exact suffix UNKNOWN.
- Ready list relayout is 3 accounts per row and hides members already chosen into groups.
- Group dropdown refresh removes earlier-group selections from later choices while preserving the current value when possible.
- Party owns refresh stop/cancel/destroy surfaces; exact destroy micro-order remains UNKNOWN.
- Character state beyond name/identity is deferred to G03; team action behavior remains later G scope.

## G02 FILES
- docs/tasks/G02.md
- docs/party/G02_PARTY_HWND_STATIC_EVIDENCE.tsv
- docs/party/G02_PARTY_HWND_FLOW.md
- docs/party/G02_PARTY_HWND_MODEL.json

## G03 VERIFIED RESULTS
- Re-read PLAN.md and STATE.md and executed G03 only. G02 HWND discovery/identity was reused, not redone.
- Re-materialized and inspected the exact user archive/EXE first. Archive SHA-256 remains `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; inner EXE remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Party has three separate identity/state layers: physical HWND+PID generation, display/config RoleName, and live RoleID/TeamID action state.
- In the frozen Party module, direct `utils.get_character_info` consumption is limited to `RoleName` for the ready/member name layer. No direct Party constants for CurrentHP/MaxHP/HPPercent/Level/MapID/PosX/PosY were recovered.
- RoleName is sanitized through the `<[^>]+>` path; a temporary `Window ` fallback exists. Exact fallback suffix remains UNKNOWN.
- RoleID is NOT taken from get_character_info. Party resolves it live through `memory_items.read_own_ids` plus `hwnd_of_pid`.
- The shared own-ID path exposes records shaped as `(pid, RoleID, Name, Lv)`. Party resolves selected names to `(name, hwnd, rid)`.
- Name resolution has direct `strip`, exact-name map and lowercase fallback-map surfaces. An absent live name logs `không online — bỏ qua`; a PID without current HWND logs `không tìm thấy cửa sổ — bỏ qua`.
- Party contains direct diagnostic `[Party] Không đọc được RoleID: ...`. No Party numeric invalid-RoleID sentinel contract was recovered; G03 explicitly does NOT invent `RoleID=0` or another value as invalid.
- TeamID is read separately via `memory_items.read_team_id(hwnd)`, not from get_character_info.
- TeamID semantic states are locked:
  - `0` = known outside/no team;
  - `0xFFFFFFFF` = known outside/no team;
  - `None` = read failure / unknown;
  - other accepted ID = real team.
- Party explicitly says `None (đọc lỗi) không được coi là đạt`; therefore read failure must never be merged into the successful outside-team state.
- Same-team verification only accepts equal real TeamIDs after excluding 0 / 0xFFFFFFFF / None.
- `_team_snapshot` preserves unreadable TeamID as `?` for diagnostics rather than formatting it as 0.
- Party summary documents `read_team_id` at `RoleData+0xE8`. A separate shared `read_team_leader` helper documents leader RoleID at `RoleData+0xEC`, but Party does not use that helper as its member RoleID source.
- Party persists member names/config, not live RoleID or TeamID. RoleID and TeamID must be re-resolved/polled live.
- B04 was cross-checked only after EXE extraction and remains unchanged: it visibly shows names in Comboboxes, not RoleID/TeamID numbers.
- Team create/invite/action sequencing remains deferred; G03 records state semantics only.

## G03 FILES
- docs/tasks/G03.md
- docs/party/G03_PARTY_CHARACTER_STATE_STATIC_EVIDENCE.tsv
- docs/party/G03_PARTY_CHARACTER_STATE_FLOW.md
- docs/party/G03_PARTY_CHARACTER_STATE_MODEL.json

## G04 VERIFIED RESULTS
- Before doing new work, GitHub was checked exactly as requested. G01–G03 artifacts and completion commits are present and STATE.md already marked them complete; no G04 files existed, so completed work was not repeated.
- Frozen archive and inner EXE were rechecked first: archive SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; inner EXE SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Party does NOT own or invoke a second physical game-window grid engine. No Party references were recovered for `_arrange_grid`, `_move_windows_offset`, `_auto_tile_windows`, `_layout_worker`, `_sync_windows_loop`, `grid_cols` or `grid_rows`.
- Party's shared Start call remains `start_tab.get_windows()` for ready/member discovery. No direct Party edge to Start arrange/tile entry points was recovered.
- Party `grid` / `grid_remove` and `_relayout_ready_list` are Tk UI geometry only. The exact Party doc says ready accounts are laid out 3 per UI row and selected accounts are hidden.
- The six group slots / 2×3 Combobox arrangement is Party UI/member grouping, not physical desktop window positions.
- No evidence maps Party logical group order to C06 grid slots, Auto RoleName sort or Xếp-lưới row/column order.
- No evidence equates a Party group leader with the Start subsystem's master HWND. These concepts remain independent.
- One direct physical-window geometry operation exists: `PartyTab._click_create_team` contains leader HWND local `lhwnd`, shared `resize_window`, and exact encoded integers 1366 and 768.
- Raw EXE bytes immediately after `resize_window` are `6c d6 0a` (1366) and `6c 80 06` (768), and the exact Party method doc says the leader creates the team by UI click with game at 1366x768.
- This resize applies to the leader/create-team HWND, not all Party members. No Party loop resizing every member/window was recovered.
- C06's already-verified shared `resize_window` semantics apply: normalize window state, resize with SetWindowPos, preserve x/y through SWP_NOMOVE, do not activate, and do not alter z-order through the resize helper itself.
- Therefore the 1366×768 resize is a coordinate-system precondition for later fixed Party create-team clicks, not Party grid/tile arrangement.
- B04 was cross-checked only after EXE extraction and requires no change; it shows Party UI grouping, not physical desktop game-window layout.
- Full create-team click sequencing remains deferred to the later Party action-button task.

## G04 FILES
- docs/tasks/G04.md
- docs/party/G04_PARTY_LAYOUT_STATIC_EVIDENCE.tsv
- docs/party/G04_PARTY_LAYOUT_FLOW.md
- docs/party/G04_PARTY_LAYOUT_MODEL.json

## G05 VERIFIED RESULTS
- Followed PLAN.md/STATE.md exactly. GitHub was checked first; G01–G04 were already complete and no G05 artifact/commit existed, so completed work was not repeated.
- Rechecked the exact frozen specimen first: archive SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; inner EXE SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Inspected the Party implementation/code-object range from `.party_tab` near `0x2b7d066` through PartyTab methods and `<module party_tab>` at `0x2b81b28`.
- PartyTab has **no owned preview subsystem**. Static Party-range scan found zero occurrences of preview/thumbnail/DWM registration/update/unregister, `src_hwnd`, `dst_hwnd`, `window_preview_items`, preview-list refresh, preview visibility control or detached-preview state.
- Party has no direct preview-click activation path: no `_activate_game_window`, `SetForegroundWindow`, DWM destination WndProc/click-target map, or Start preview activation helper reference.
- The direct shared Start dependency remains `start_tab.get_windows()` around `0x2b7dc49`–`0x2b7dc63`, already used by G02 for Party member discovery. No Party direct call to Start preview-control methods was recovered.
- C03/C09/C14 therefore remain authoritative for embedded DWM preview, 1x–5x preview layout and detached preview. G05 does not duplicate those systems.
- The same underlying game HWND may independently appear in Start preview state and Party member state, but that does not create shared preview ownership.
- Party contains no preview-order or preview-column state; Party group order must not depend on Start preview order/columns.
- Party contains no detached-preview dependency; Party member/action state should not be coupled to whether Start embedded/detached preview is shown, beyond the underlying game HWND remaining valid.
- Party direct game-action helpers such as `click_at` / `resize_window` target game HWNDs directly and are not preview activation.
- B04 was cross-checked only after EXE extraction; no Party preview geometry was added and the baseline is unchanged.
- G05 closes the preview item in the original Party PLAN with a negative ownership result: **Party does not own or directly control preview**.

## G05 FILES
- docs/tasks/G05.md
- docs/party/G05_PARTY_PREVIEW_STATIC_EVIDENCE.tsv
- docs/party/G05_PARTY_PREVIEW_FLOW.md
- docs/party/G05_PARTY_PREVIEW_MODEL.json

## G06 VERIFIED RESULTS
- Followed PLAN.md/STATE.md exactly. GitHub was checked first; G01–G05 were already complete and no G06 artifact existed, so completed work was not repeated.
- Rechecked the exact frozen archive/EXE first: archive SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; inner EXE SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Static scan of the frozen Party implementation range found zero Party keyboard-sync ownership surfaces: no `keyboard`, `pynput`, `keyboard.Listener`, `_on_master_key_press`, `_on_master_key_release`, `input_active`, `_toggle_input`, `_sync_keepalive`, `_sync_locked`, `WM_MY_SYNC_KEY`, `GetForegroundWindow` or keyboard `vk` forwarding state.
- No Party call/reference to Start `_toggle_input` or Start `input_active` was recovered. Party start/stop/group-leader changes therefore do not directly control Start keyboard synchronization.
- C19 remains authoritative for shared keyboard sync: Start master HWND → `keyboard.Listener` → press/release handlers → virtual-key path → `WM_MY_SYNC_KEY` to Start-managed slaves.
- G04's boundary remains intact: Party leader is not Start master. G06 found no keyboard-side assignment that changes this.
- Party's direct input/action surface is separate: `mouse` is present for shared identity/action infrastructure; `click_at` is present around `0x2b7f0db` / `0x2b7f0e5`, plus check-pixel/resize helpers. These are direct Party target actions, not keyboard event synchronization.
- Party range contains no `press_at`, `send_key`, `send_keyboard`, `PostMessage`, `SendMessage` or `SendInput` Party-owned keyboard-send path.
- No Party edge passes a group member HWND list into Start keyboard-sync slave selection. Party group membership must not be treated as the Start keyboard slave set.
- Start mode/master/max-window input-sync rules from C19/C08 remain unchanged and are not overridden by Party.
- B04 contains no Party keyboard-sync control; no Party UI baseline change was required.
- G06 closes the original PLAN's Party `sync keyboard` item with a negative ownership result: keyboard synchronization remains entirely in the shared Start/input subsystem.

## G06 FILES
- docs/tasks/G06.md
- docs/party/G06_PARTY_KEYBOARD_SYNC_STATIC_EVIDENCE.tsv
- docs/party/G06_PARTY_KEYBOARD_SYNC_FLOW.md
- docs/party/G06_PARTY_KEYBOARD_SYNC_MODEL.json

## G07 VERIFIED RESULTS
- Followed PLAN.md/STATE.md exactly. GitHub was checked first; G01–G06 were already complete and no G07 artifact existed, so completed work was not repeated.
- Rechecked the frozen Party implementation range first against the same locked inner EXE SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Static Party-range scan found no synchronized-mouse ownership: no `mouse.Listener`, `_on_master_click`, `_on_master_scroll`, `_on_master_move`, `_sync_worker`, `_do_down`, `_do_up`, `_slave_client`, `send_scroll`, `send_move_slave`, `WindowFromPoint`, `GetAncestor`, `ScreenToClient` or `GetClientRect`.
- Party also has no `_toggle_input`, `input_active`, `_sync_keepalive` or `_sync_locked` surface and no direct call edge into Start mouse-sync lifecycle.
- C19 remains authoritative for synchronized mouse input: selected Start master HWND → mouse.Listener → click/scroll/move handlers → client-coordinate conversion → size-aware master/slave scaling → Start-managed slaves.
- No Party edge maps a Party leader to Start mouse master, or Party group members to Start mouse slaves.
- Party does contain direct targeted input helpers. Frozen Party evidence contains `check_pixel` at about `0x2b7f0bf`, `click_at` at about `0x2b7f0db`, `resize_window`, and target `window_hwnd`.
- The create-team fallback uses fixed-coordinate UI actions on the intended leader/create-team HWND, including the recovered `(391,683)` and `(34,462)` clicks after the corresponding pixel checks.
- That Party fallback is not synchronized mouse replay. It is one-target automation after the leader window is normalized to 1366×768.
- Party's `mouse` symbol around `0x2b7daa3` is directly adjacent to `bind_window_identity` / `unbind_window_identity`; this is G02 HWND/PID-generation safety and must not be misread as mouse.Listener ownership.
- Party fixed-coordinate action has no C19 coordinate-scaling stage. No Party `ScreenToClient`, `GetClientRect` or `_slave_client` path was recovered.
- No Party mouse move or wheel broadcast path exists.
- B04 contains no Party mouse-sync control; no UI baseline change was required.
- G07 closes the original PLAN's Party `sync mouse` item: synchronized mouse ownership remains in Start/input; Party keeps only its separate direct targeted action path.

## G07 FILES
- docs/tasks/G07.md
- docs/party/G07_PARTY_MOUSE_SYNC_STATIC_EVIDENCE.tsv
- docs/party/G07_PARTY_MOUSE_SYNC_FLOW.md
- docs/party/G07_PARTY_MOUSE_SYNC_MODEL.json

## G08 VERIFIED RESULTS
- Followed PLAN.md/STATE.md exactly. GitHub was checked first; G01–G07 were already complete and no G08 artifact existed, so completed work was not repeated.
- Rechecked the frozen EXE first. Inner EXE SHA-256 remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Party configuration uses the shared settings backend: `CONFIG_PATH`, `CONFIG_DIR`, `_settings_lock`, `read_settings`, `write_settings`, section `Settings`, file `settings.ini`.
- Party owns a `_saving_enabled` persistence guard. It exists specifically around build/load/save lifecycle so initialization/restoration does not become an uncontrolled write loop. Exact flag-enable instruction timing remains UNKNOWN.
- `party_after` is active and defaults to `wait`. The exact allowed internal values recovered from the EXE are `wait / train / train_lsv / don / phoban`.
- `_after_party.trace_add("write", ...)` is a direct autosave trigger.
- Active team-section config keys are `party_groups` and `party_group1`; these are passed into the current `Cấu hình nhóm` section as `cfg_groups` / `cfg_group1`.
- `get_groups_data` exact original documentation defines the current multi-group schema as `[{'num': n, 'members': [...]}, ...]`.
- `party_groups` is therefore the current multi-group JSON representation.
- `party_group1` is a backward-compatibility mirror for Nhóm 1. Exact original documentation says it contains selected Group-1 names with blanks/duplicates removed.
- Load locals directly expose both current and legacy paths: `raw_groups`, `groups_data`, `parsed`, `legacy`, `g1`, `members`, `var`, `nm`. Exact source Boolean expression deciding precedence remains UNKNOWN.
- Save/load directly use `json.loads` / `json.dumps`; save has `ensure_ascii=False`, preserving Vietnamese/Unicode character names.
- Group restoration is name/StringVar based, not HWND/PID based. Exact malformed-JSON branch and exact treatment of saved `num` during visual renumbering remain UNKNOWN.
- Party config persists member names/group structure, not HWND, PID, RoleID or TeamID. G02/G03 identity separation remains intact.
- Runtime execution state such as `_running`, cancel events, refresh IDs, member-row live identity and per-cluster join-running state is not represented as Party config.
- Four literals appear together only in the save block and have no active Party build/load UI path: `party_corps_groups`, `party_corps_group1`, `party_follow`, `party_pick`.
- The `_save_config` code-object locals include iterator `_k`, consistent with processing that grouped legacy-key set. These are classified as dormant compatibility cleanup keys, not active features. Exact cleanup statement syntax (delete/pop/equivalent) remains UNKNOWN.
- `_sec_corps` still exists as dormant constructor state, but no active second corps section is built in the current Party UI.
- Save-side major surfaces are: ensure CONFIG_DIR → save party_after → serialize current/legacy group data → process dormant compatibility-key set → write_settings. Exact save error text is `[PARTY] Save error: `.
- B04 was cross-checked only after EXE extraction and requires no geometry change.
- Action semantics for create/invite/start buttons remain deferred to G09+.

## G08 FILES
- docs/tasks/G08.md
- docs/party/G08_PARTY_CONFIG_STATIC_EVIDENCE.tsv
- docs/party/G08_PARTY_CONFIG_FLOW.md
- docs/party/G08_PARTY_CONFIG_MODEL.json

## G09 VERIFIED RESULTS
- Followed PLAN.md/STATE.md exactly. GitHub was checked first; G01–G08 were already complete and no G09 artifact existed, so completed work was not repeated.
- Rechecked the frozen Party implementation first against the same locked inner EXE SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Bottom Party control is the real global toggle: idle `Bắt đầu` / `BTN_GREEN_PARTY` → `_toggle_run`.
- Global start validation uses `get_groups_data`; if no selected group has accounts, exact log is `[Party] Chưa có nhóm nào chọn acc`.
- Global start path contains log fragments `[Party] Bắt đầu N cụm — M acc`, clears the shared cancel Event, changes the bottom button to `Dừng lại` / red `#f44336`, and launches `_run_worker`.
- Global stop phase is a distinct UI state: `Đang dừng...` / orange `#ef6c00` / disabled. `PartyTab.stop` exact doc says it stops the process if running.
- Constructor owns `_running`, global `_cancel` Event, `_run_lock`, and `_run_cancels`. Exact `_run_lock` critical-section scope and exact Event-set/assignment micro-order remain explicit UNKNOWN.
- Party summary explicitly says global Bắt đầu runs groups in parallel with one thread and a separate cancel per cluster.
- `_run_worker` directly contains `own_cancels`, `threads`, `is_alive`, `join`, `timeout`, `_after_party_action`, and `_reset_run_button`.
- Exact `_run_worker` doc locks the aggregate lifecycle: one `_run_one_group` thread per cluster; after all settle, execute post-party action once and reset global UI once.
- `_sleep` exact doc says waits are interruptible: per-cluster cancel when provided, otherwise global cancel by default.
- Each group cluster action button is `▶ Tạo nhóm N` → `_run_single_cluster`, with state fields `join_btn`, `join_cancel`, `join_running`.
- Single-cluster launch is permission/account-limit guarded, refuses duplicate invocation when its `join_running` state is active, requires at least 2 selected accounts, then changes its button to `⏳ Đang vào...` / disabled and starts `_run_single_worker`.
- Exact original doc says the single-cluster action runs only that cluster, independently of the common Bắt đầu button, with its own thread/cancel, and multiple clusters may be launched in parallel.
- `_run_single_worker` reuses the same `_run_one_group` engine and has a dedicated `_reset_single_button` completion path. Adjacent `discard` evidence shows completed single-run cancel tracking is cleaned up, but exact lock/statement syntax is not claimed.
- Exact collision rule for running the **same cluster** simultaneously through global Bắt đầu and its single `▶ Tạo nhóm` button remains UNKNOWN from readable static evidence. Architectural independence and different-cluster single-run parallelism are verified.
- `Rời nhóm` → `_leave_group` → daemon `_leave_group_worker`; exact doc says it runs in background for all cluster members and skips already-outside/offline accounts.
- `+ Thêm nhóm` / `✕ Xóa N` remain structural/configuration controls, separate from Party run workers; delete keeps at least one cluster.
- Detailed B0→B3 create/invite/leave protocol was intentionally deferred to G10, per NEXT_ACTION.

## G09 FILES
- docs/tasks/G09.md
- docs/party/G09_PARTY_ACTION_LIFECYCLE_STATIC_EVIDENCE.tsv
- docs/party/G09_PARTY_ACTION_LIFECYCLE_FLOW.md
- docs/party/G09_PARTY_ACTION_LIFECYCLE_MODEL.json

## G10 VERIFIED RESULTS
- Followed PLAN.md/STATE.md exactly. GitHub was checked first; G01–G09 were already complete and no G10 artifact existed, so completed work was not repeated.
- Rechecked the exact frozen archive/EXE first: archive SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; inner EXE SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- `_run_one_group` exact documentation defines the active Party protocol as **B0 → B1 → B2 → B3**, independent per cluster.
- Target resolution remains name-based config → live `read_own_ids` → current `hwnd_of_pid` → `(name, hwnd, RoleID)`; offline/missing-window selections are skipped. An explicit `chỉ 1 acc online — ...` guard exists before create/burst; its final assembled suffix/source return expression remains UNKNOWN.
- **B0** writes live auto-accept through `set_auto_fields` with `UTILITIES / AutoAcceptInviteTeam / bool=True`, then reads back via `get_auto_settings` after symbolic `AUTOSET_DELAY`.
- B0 readback semantics are exact: True = confirmed ON; False = still OFF and logs manual-accept warning; None = unreadable. Write/readback failure never fabricates a positive state.
- **B1** skips targets already at TeamID 0/0xFFFFFFFF, calls `memory_items.leave_team` for in-team targets, uses interruptible `LEAVE_DELAY`, then waits all targets outside via `_wait_team_state(expect_zero=True)` with `WAIT_LEFT_TIMEOUT`.
- B1 verification timeout logs `chưa xác nhận thoát hết ... — vẫn tiếp tục`; it does not hard-abort the cluster.
- Shared TeamID semantics remain unchanged: 0/0xFFFFFFFF = outside team; None = read error and never counts as reached.
- Shared leave packet is verified from memory_items: channel **200057**, TeamAction **LeaveTeam=4**, payload **`4:<ownRid>`**.
- **B2** is packet-first and leader-only. `memory_items.create_team` uses channel **200057**, TeamAction **CreateTeam=0**, payload **`"0"`**, then Party waits for a real leader TeamID with symbolic `CREATE_PACKET_TIMEOUT`.
- If packet-first creation does not establish a real TeamID, Party falls back to `_click_create_team`: resize leader to 1366×768, conditional click (391,683) for `donVang.nguoiChoiGan`, conditional click (34,462) for `donVang.muiTenAnNhiemVu`, then exact tail clicks (27,467) → (154,214) → (127,336).
- Exact original fallback doc states **every click is 1 second apart** and the sequence is cancellation-aware.
- Fallback creation waits a real TeamID with symbolic `WAIT_TEAM_TIMEOUT`, retries up to symbolic `CREATE_RETRY`, and uses symbolic `INVITE_DELAY` between attempts. Exact numeric CREATE_RETRY is not safely recoverable and remains UNKNOWN.
- Exhausted create retries log `TẠO THẤT BẠI — bỏ qua cụm này`; normal B3 is skipped.
- **B3** uses `_invite_burst`, not the old one-member-at-a-time wait model.
- Party summary explicitly calls `invite kind='team'`. The shared memory_items invite map is serialized as trade/team/group → `7:1:` / `5:` / `10:`, and invite uses packet **200051**. Active Party team invite is therefore payload **`5:<targetRoleID>`**.
- B3 sends all `others` in a burst with symbolic `BURST_INVITE_DELAY`, then one shared `_wait_group_same_team` wait using symbolic `GROUP_JOIN_POLL` and `GROUP_JOIN_TIMEOUT`.
- `_wait_group_same_team` succeeds only when each other account's real TeamID equals the leader's real TeamID; timeout returns a missing-target list; cancellation returns None.
- Missing members after the first wait are resent **exactly one additional round**, followed by one final shared wait.
- If members still remain missing after the resend, Party logs names + `_team_snapshot` and advises checking auto-accept/manual popup; `_invite_burst` still finishes True unless canceled.
- Original B3 doc explicitly contrasts the old fixed **2s/member** strategy with burst spacing `BURST_INVITE_DELAY (~0.5s)`. G10 records ~0.5s as approximate documentation, not as an invented exact assignment.
- Legacy `_invite_join` remains one invite + fixed symbolic `JOIN_WAIT` without TeamID verification, but it is not the main B3 engine.
- The direct `Rời nhóm` worker is simpler than B1: resolve live targets → skip offline/already-outside → send leave_team → interruptible LEAVE_DELAY → log XONG. Its readable block has no final aggregate `_wait_team_state`; do not silently add B1's verification wait to that button.
- Frozen Party module float pool contains exact values `0.3, 0.8, 2.0, 12.0, 0.5, 15.0, 6.0`, but Nuitka's deduplicated blob does not safely bind every float to every symbolic timing name. Those mappings remain UNKNOWN except values tied directly by docs.
- G09 button/thread/cancel lifecycle was preserved unchanged.

## G10 FILES
- docs/tasks/G10.md
- docs/party/G10_PARTY_TEAM_PROTOCOL_STATIC_EVIDENCE.tsv
- docs/party/G10_PARTY_TEAM_PROTOCOL_FLOW.md
- docs/party/G10_PARTY_TEAM_PROTOCOL_MODEL.json

## G11 VERIFIED RESULTS
- Followed PLAN.md/STATE.md exactly. GitHub was checked first; G01–G10 were already complete and no G11 artifact existed, so completed work was not repeated.
- Rechecked the frozen Party implementation first against the locked inner EXE SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Exact `_after_party_action` documentation locks the mode behavior: `phoban` activates Phó Bản's own process; `train/train_lsv/don` starts per-account farm for the accounts that just partied; `wait` does nothing.
- Generic mapping is exact: `train → farm_tab_ref / Train`; `train_lsv → train_lsv_tab_ref / Train LSV`; `don → donvang_tab_ref / Dồn vàng`.
- Missing refs are logged and skipped. Generic dispatch also skips when there are no `acc nào vừa party`.
- Party owns aggregate target state `_last_targets` guarded by `_targets_lock`. Post-party readiness metadata exposes target iteration variables `nm, hwnd`; the handoff shape is name + Party-HWND, not RoleID/TeamID.
- Exact reset/merge statement order for `_last_targets` across parallel cluster workers remains UNKNOWN; synchronized aggregate storage is verified.
- `phoban` is a special whole-tab path, not per-account farm. It requires `phoban_tab_ref`, skips if Phó Bản is already running, and uses dedicated main-thread `_after_phoban_main`.
- `_after_phoban_main` exact doc says: switch to tab Phó Bản and start its process on the main thread. Notebook selection uses `_select_tab_by_text`, which finds a tab by visible label and selects it.
- Generic Train/Train LSV/Dồn vàng selects the destination tab first so hidden tabs can begin scanning, then runs `_wait_and_dispatch_after_party` in the background.
- Exact generic readiness loop is now locked directly in Party: `want.issubset(have)`, where want is the original Party target-HWND set and have is destination `_acc_rows` HWND set; poll every **1.0s**, max **20 polls / 20s**.
- Background readiness reads row HWND data only and does not mutate Tk widgets; actual dispatch is handed back to main thread through `_after_dispatch_main`.
- Destination tab must expose `_toggle_single_farm`; if not, Party logs and skips rather than substituting another engine.
- Matching is exact HWND first, then account-name fallback; direct metadata contains `by_hwnd`, `by_name`, `by_lower`. Original doc explicitly says HWND first, name second to survive stale/different HWND values.
- A further `_fresh_map` / `khớp sau resolve lại (hwnd mới=...)` fallback exists before final failure. Exact dictionary/source expression for the fresh map remains UNKNOWN.
- If a target still cannot be mapped, it is skipped individually. Empty destination rows get a hidden/permission diagnostic rather than an invented match.
- Local `used_hwnd` state proves destination rows are guarded against accidental repeated consumption.
- Matched rows are checked through `_farming_acc`; already-running accounts are skipped so the generic toggle cannot accidentally turn them off.
- Successful dispatch uses the **current HWND of the destination row found**, not the possibly stale Party HWND, then invokes the destination tab's real `_toggle_single_farm`.
- Post-party dispatch is a **global Bắt đầu aggregate** feature. G09's single-cluster `▶ Tạo nhóm N` worker resets its own button and has no independent post-party action.
- Global `_run_worker` has threads/cancels/join surfaces but no recovered per-cluster results/success aggregation. Static evidence therefore does **not** gate post-party dispatch on all clusters succeeding; ordinary cluster failure does not create an all-success barrier.
- Exact behavior after explicit global/manual cancellation remains UNKNOWN because a `self._cancel` branch could exist without a separate result local. This is reserved for runtime/stronger-decompile parity testing.
- Login F10/F11, G09 lifecycle and G10 B0→B3 protocol were not reopened or changed.

## G11 FILES
- docs/tasks/G11.md
- docs/party/G11_PARTY_POST_ACTION_STATIC_EVIDENCE.tsv
- docs/party/G11_PARTY_POST_ACTION_FLOW.md
- docs/party/G11_PARTY_POST_ACTION_MODEL.json

## G12 VERIFIED RESULTS
- Followed PLAN.md/STATE.md exactly. GitHub was checked first; G01–G11 were already complete and no G12 artifact existed, so completed Party work was not repeated.
- G12 integrated B04 + G01–G11 into one authoritative Party parity/reconstruction handoff without starting Stage S.
- Gate-G coverage now matches every Party category in PLAN.md: UI, HWND, character state, grid-layout boundary, preview boundary, keyboard-sync boundary, mouse-sync boundary, configuration, action lifecycle/protocol, and parity handoff.
- B04 remains the visual authority. Party visible structure, 2×3 group slots, dynamic clusters and exact after-party labels remain locked.
- Runtime identity remains HWND+PID generation; RoleName is display/config identity; RoleID and TeamID are live action state only.
- Party does not own physical window grid, preview/DWM, keyboard sync or mouse sync. These ownership boundaries remain Start/window responsibilities.
- Active Party persistence remains name/group based under `party_after`, `party_groups`, `party_group1`; no HWND/PID/RoleID/TeamID persistence is allowed.
- Global/per-group action lifecycle, B0→B3 packet-first team protocol, direct Rời nhóm behavior and post-party routing were consolidated without changing any verified G09–G11 behavior.
- Remaining UNKNOWNs were explicitly classified:
  - IMPLEMENTATION_SAFE: syntax/micro-order details where visible behavior is already bounded.
  - RUNTIME_ONLY: first refresh tick, same-cluster global+single collision, explicit global-cancel post-party behavior, one-live-account branch.
  - STRONGER_DECOMPILATION_REQUIRED: invalid RoleID sentinel if any, exact `_run_lock` critical section, exact `_last_targets` reset/merge sequence, numeric `CREATE_RETRY`, and exact numeric bindings for symbolic Party timing constants.
- No unknown was silently resolved or filled from the pooled float constants.
- A mandatory **33-case Windows original-vs-reconstruction Party parity matrix** is now defined, including same-HWND/new-PID, packet-create success/fallback, missing auto-accept, B3 resend/missing cases, hidden destination readiness, stale-HWND fallback, ordinary cluster failure and explicit global cancel.
- Proxy runtime development scope lock remains active.
- Stage S source reconstruction was **not** started.

## G12 FILES
- docs/tasks/G12.md
- docs/party/G12_PARTY_PARITY_MATRIX.tsv
- docs/party/G12_PARTY_RECONSTRUCTION_HANDOFF.md
- docs/party/G12_PARTY_MODEL.json

## GATE G DECISION
- G01–G12 COMPLETE / VERIFIED for Party static+visual research and reconstruction handoff.
- Party runtime parity is explicitly deferred to the mandatory Windows original-vs-reconstruction matrix.
- Runtime/decompilation reservations remain preserved and do not justify repeating G01–G11.
- The next PLAN phase is H — Train.

## H01 VERIFIED RESULTS
- Followed PLAN.md/STATE.md exactly. GitHub was checked first; Gate G was already closed, B05 was already verified, and no H01 artifact existed, so no completed work was repeated.
- Rechecked the exact frozen inner EXE first; SHA-256 remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- FarmTab static module boundary is now locked: `.farm_tab` near `0x293a91e`, `farm_tab.py` near `0x2943ecb`, `<module farm_tab>` near `0x2944146`, next module `<module fast_travel>` near `0x2947cb1`.
- `FarmTab.__init__` owns Train UI/config/account-row lifecycle. Direct early state includes `_farming`, `_acc_rows`, refresh/scroll/import/farm-thread/autosave state, map caches, `_coord_rows`, and `_saving_enabled`.
- Constructor lifecycle is directly ordered as `_build_ui → _load_config → <Destroy>/_save_on_destroy → _start_refresh → _autosave_loop`.
- Bottom B05 `Bắt đầu` is wired to `_toggle_farm`; H01 does not decode the full start/stop FSM yet.
- Town section ownership is locked: `_toggle_town_config`, default-hidden `_town_body`, `town_condition_var`, values `never/full_bag_timer/cycle`, `_on_town_condition_changed`, `loop_var`, nav-priority variables/comboboxes and `_on_nav_priority_changed`.
- Hidden town config variables directly include sell-equipment/map/tab, HP/MP purchase item/quantity and medicine-coordinate state. H01 records ownership only; routing/shop semantics are deferred.
- Train section owns `respawn_var`, `auto_reconnect_var`, `pickup_no_cankhon_var`, `trist_var`, `heal_map_var`, `pickup_mode_var`, manual buff rows and add/remove callbacks. Original buff-key doc remains `F1–F10 + 1,2,3`.
- Saved-coordinate section owns header/body/toolbar/rows, add-row and visibility-toggle callbacks, plus map select/apply-all/remove/save/refresh wiring. Coordinate behavior is deferred.
- Account list is a FarmTab Canvas + vertical Scrollbar. `_add_or_update_row` owns live rows; row action surfaces include `_toggle_single_farm`, `_goto_sell_acc`, `_toggle_sell`, `_move_acc`, and `_farm_acc`.
- B05 all-account buttons map to genuine background actions: `Tới bán đồ → _goto_sell_all`, `Bán đồ → _sell_all`, `Tới bãi train → _move_all`, `Đánh → _farm_all`; build wiring uses daemon Thread launches.
- FarmTab consumes shared Start discovery through `start_tab.get_windows()`; character/bag reads occur in the background refresh worker and row mutation is applied on the Tk/main thread.
- Row identity wiring directly includes `_pid_of`, `bind_window_identity`, `unbind_window_identity`, and stale-row removal.
- Exact incremental account refresh is **5000 ms**. Original doc says refresh every 5 seconds; frozen bytes `6c 88 27` decode to 5000.
- Exact periodic config autosave is **30000 ms**. Original doc says autosave every 30 seconds; frozen bytes `6c b0 ea 01` decode to 30000.
- FarmTab uses shared settings backend with section `Farm`. Active key surfaces include loop/town condition/nav priorities, sell/buy/meds, respawn/reconnect/trist/pickup/heal, `buff_*`, `coord_*`, and per-account `acc_*_sell/farm`.
- The load block also contains `full_bag`; its exact relationship to current town-condition semantics is deliberately deferred to H02/H03.
- Permission wiring uses the shared guard/account-limit layer with scope/action `farm_tab/farm`; enabled Combobox state is documented as `readonly`.
- FarmTab owns `_sync_start_tab_btn` through `start_tab_ref`, keeping Start-tab Farm UI synchronized with FarmTab run state.
- Only after static extraction, current `TLMTool_b2OvbUQCNB(4).png` was hashed; SHA-256 exactly matches B05 `17d98f6b6a263daa5857224d100355379672eae7bd7c72794323f31417d8bc53`. No Train geometry was remeasured.
- Return-town conditions, inventory-full, periodic-town, train coordinates, heal/death/reconnect, loot, mount, saved-coordinate semantics and Farm FSM remain later H tasks.

## H01 FILES
- docs/tasks/H01.md
- docs/train/H01_TRAIN_UI_WIRING_STATIC_EVIDENCE.tsv
- docs/train/H01_TRAIN_UI_WIRING_FLOW.md
- docs/train/H01_TRAIN_UI_WIRING_MODEL.json

## H02 VERIFIED RESULTS
- Followed PLAN.md/STATE.md exactly. GitHub was checked first; no H02 artifact existed, so no completed Train work was repeated.
- Inspected the frozen original EXE first; inner EXE SHA-256 remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Current return-town radio values are exactly `never / full_bag_timer / cycle`, mapped to `Không về / Khi đầy túi / Theo chu kỳ (phút)`.
- `town_condition_var` is initialized to `cycle`; `loop_var` is initialized to `30`. This matches the locked B05 screenshot.
- Exact `_on_town_condition_changed` documentation says only: `Khi chọn điều kiện về thành — lưu config.` No condition-owned town-body visibility transition is recovered.
- The cycle Spinbox lives in the always-visible condition row, outside the default-hidden lower town body. Switching mode does not clear the retained minute value.
- Current config persistence uses `town_condition`.
- H02 resolves H01's deferred `full_bag` surface: `full_bag` is a legacy condition value/compatibility alias, not a fourth active radio or an independent current return-town option.
- The farm runtime directly groups `full_bag_timer` and legacy `full_bag` in the same two-value bag-enabled condition tuple. The current UI value is `full_bag_timer`; exact source syntax of the load normalization remains an implementation-detail UNKNOWN.
- Mode boundary is now locked at high level:
  - `never`: no automatic town return; direct original logs show a full bag can be filtered and, if still full, stays in place because mode is Không về.
  - `full_bag_timer`: bag-enabled timed mode; bag-full participates in ending the common wait early.
  - `cycle`: periodic `loop_minutes` mode without the full-bag early-stop branch.
- Exact bag threshold/filter mechanics are intentionally deferred to H03; exact periodic timing execution remains H04.
- Exact `_toggle_town_config` documentation says the entire block below the condition row is hidden/shown and is **default hidden**. Button texts are `Hiện cấu hình` / `Ẩn cấu hình`. This visibility is independent of the selected return-town condition.
- Exact `_update_dungeon_town_lock` documentation says: if **any** account selects a route with `lock_town`, FarmTab forces `Không về thành` and disables the return-town radios.
- Direct lock-method surfaces include each row's `farm_var`, `_preset_to_vars`, `TRUYEN_DAI_LY_ROUTES`, `lock_town`, `has_dungeon`, `disabled/normal`, and forced `never`.
- When no selected route is locked, the return-town radios return to `normal`.
- No previous-condition memory surface was recovered. Therefore no automatic restoration of the pre-lock `cycle/full_bag_timer` selection is statically evidenced; do not invent one.
- Exact `_is_dungeon_farm` documentation says it is True when an account has selected an old-dungeon / route-`lock_town` Farm map. This is the per-account runtime safety predicate.
- The lock-town UI method explicitly gates return-town radios; no lock-owned disable edge for the navigation-priority comboboxes was recovered.
- Navigation priority has four readonly comboboxes. Available options are blank + `Phù 1 / Phù 2 / Phù 3 / Ngựa`; defaults are `Phù 1 / Phù 2 / Phù 3 / Ngựa`.
- Exact `_on_nav_priority_changed` documentation says each navigation value can be selected only once. Recovered locals `NAV_OPTIONS/idx/var/used/other_var/val/current/available` confirm dynamic exclusion of methods already used by other priority slots while retaining the current selection.
- B05 was cross-checked only after static extraction. Current screenshot hash still exactly matches `17d98f6b6a263daa5857224d100355379672eae7bd7c72794323f31417d8bc53`; no geometry was remeasured.

## H02 FILES
- docs/tasks/H02.md
- docs/train/H02_TOWN_CONDITION_STATIC_EVIDENCE.tsv
- docs/train/H02_TOWN_CONDITION_FLOW.md
- docs/train/H02_TOWN_CONDITION_MODEL.json

## H03 VERIFIED RESULTS
- Followed PLAN.md/STATE.md exactly. GitHub was checked first; no H03 artifact existed, so no completed Train work was repeated.
- Re-materialized and re-hashed the frozen specimen before analysis. Archive SHA-256 remains `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; inner EXE remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- `FarmTab._get_bag_slots` exact original doc says: `Số ô túi đồ đang dùng (Site 10) — None nếu đọc lỗi (giữ giá trị cũ).`
- Farm bag metric is therefore **occupied Site-10 slot count**, not free slots and not total item quantity.
- `_get_bag_slots` calls shared `memory_items.get_bag` and reads the returned `slots` field.
- Shared `get_bag` exact doc says it aggregates Site-10 bag data and returns a dict or None; dict surface contains `slots/distinct/total_qty/non_bag/info`.
- Read failure at the Farm row/display helper returns None and preserves the prior displayed bag value rather than synthesizing zero.
- Farm cycle directly contains `MI.is_full_bag`, a local `threshold`, `bag`, `slots`, and nested `stop_bag_check`, proving a dedicated fullness predicate exists.
- No current Farm UI/settings key for a bag threshold was recovered. The exact numeric FarmTab threshold cannot be safely bound from the readable Nuitka constant stream and remains explicit **STRONGER-DECOMPILATION/RUNTIME UNKNOWN**. No 95/98/100 guess was introduced.
- Exact `_filter_before_town` doc says it filters according to the Train `Nhặt đồ` radio/preset through shared `bag_filter`, is used for all town/full-bag paths, returns post-filter `slots_after` as int, or None when there is no filter (keep-all) / an error prevents a usable count.
- `_filter_before_town` temporarily shows `Đang lọc đồ`, calls `discard_for_activity(... activity='train' ...)`, passes the Farm stop predicate, and restores the prior row state only if nobody else changed it.
- The pre-town discard stage is driven by Train pickup presets and is separate from `sell_equip` / town shop selling.
- In `never / Không về`, exact logs prove the path: `túi đầy (N ô, Không về) → lọc` → filter → if a readable post-filter result is still full, `lọc xong vẫn đầy (N ô) → ở lại (Không về)`.
- Therefore a full bag never overrides the user's no-town policy. If filtering frees enough slots, normal farming may continue without a forced town trip; if filtering yields None, no fake post-filter count is invented and no-town still cannot authorize automatic return.
- H02's `full_bag_timer` + legacy `full_bag` family is used by nested `stop_bag_check`. When `MI.is_full_bag` becomes true, the common wait can end early and the exact runtime log transitions to `N ô) → về thành`.
- H03 preserves the exact H02 boundary that `cycle` does **not** use the bag-full early-stop branch. Periodic `loop_minutes` scheduling remains H04.
- Low-level read-error behavior internal to `MI.is_full_bag` itself is not exposed strongly enough by readable static evidence. Its read-failure mapping remains explicit UNKNOWN rather than assuming unreadable=full or unreadable=empty.
- B05 was cross-checked only after static extraction; no geometry or threshold was inferred from the screenshot.

## H03 FILES
- docs/tasks/H03.md
- docs/train/H03_INVENTORY_FULL_STATIC_EVIDENCE.tsv
- docs/train/H03_INVENTORY_FULL_FLOW.md
- docs/train/H03_INVENTORY_FULL_MODEL.json

## H04 VERIFIED RESULTS
- Followed PLAN.md/STATE.md exactly. GitHub was checked first; no H04 artifact existed, so no completed Train work was repeated.
- Rechecked the frozen original EXE first; inner EXE SHA-256 remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- `FarmTab._farm_cycle` exact documentation is `Vòng lặp farm cho 1 acc: bán đồ → mua thuốc → tới → farm → chờ chu kỳ.`
- Farm-cycle code-object locals directly include `cycle_start`, `condition`, `loop_minutes`, `elapsed`, and `sleep_time`.
- The periodic-wait constant surface contains exact integer **60** next to the sleep-time portion. Together with the `Theo chu kỳ (phút)` UI and those locals, the target cycle duration is locked as `loop_minutes × 60` seconds.
- Distinct `cycle_start` + `elapsed` + `sleep_time` surfaces prove Train uses a remaining-cycle wait after accounting for time already spent on the front-half cycle work, rather than intentionally adding a second full `loop_minutes` sleep after sell/buy/move/farm.
- Exact source-level clamp/floor expression for the remaining sleep is not safely recoverable and remains UNKNOWN.
- `cycle` uses the normal timer boundary without H03's bag-full early-stop predicate.
- `full_bag_timer` and legacy `full_bag` use the same timed cycle wait but overlay nested `stop_bag_check → MI.is_full_bag`; bag fullness can end the wait early and transition to the town path.
- H02/H03 `never` semantics are preserved: ordinary timer completion does not authorize automatic town return; lock_town routes force this no-town condition.
- Normal timer expiry is a cycle boundary, not a Farm worker terminal state. No dedicated “timer done” terminal log was recovered; the outer per-account Farm loop proceeds to its next iteration.
- User/per-account stop is cancellation-aware through `stop_check` / `hard_stop`, so Farm does not intentionally wait out the full periodic interval after a stop request.
- Death/respawn is an asynchronous interrupt/reset boundary. The exact death monitor doc says it checks every **4s** and sets `respawn_event`; `_farm_cycle` directly contains `respawn_event`, `Đang hồi sinh`, and `_heal_at_death`. Detailed recovery remains later H scope.
- Disconnect/reconnect is also asynchronous. Exact monitor doc locks: watchdog every **2s**, **3 consecutive ticks (~6s)** to confirm disconnect, set `halt` and stop the farm loop immediately, reconnect attempts with **30s common.active wait per attempt**, and successful reconnect sets `reconnect_ok` as a cycle reset.
- Farm-cycle constants directly bind post-reconnect memory stabilization to `wait_memory_ready(timeout=45.0, need=3)`.
- A literal **5** exists near the periodic constant surface, but it cannot safely be assigned as the scheduler sleep/check quantum because the same Farm module independently documents another feature with an exact 5-second pickup delay and Nuitka constants are module-deduplicated.
- Therefore exact periodic sleep/check quantum remains explicit UNKNOWN.
- Exact clock API for `cycle_start/elapsed` and exact invalid/min/max `loop_minutes` parsing/clamp remain UNKNOWN rather than guessed.
- H03 inventory/full-bag/filter semantics were preserved unchanged; movement/town-route execution was intentionally deferred to H05.
- B05 was cross-checked only after static extraction; no geometry work was performed.

## H04 FILES
- docs/tasks/H04.md
- docs/train/H04_PERIODIC_TOWN_STATIC_EVIDENCE.tsv
- docs/train/H04_PERIODIC_TOWN_FLOW.md
- docs/train/H04_PERIODIC_TOWN_MODEL.json

## H05 VERIFIED RESULTS
- Followed PLAN.md/STATE.md exactly. GitHub was checked first; no H05 artifact existed, so no completed Train work was repeated.
- Inspected the frozen inner EXE first; SHA-256 remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Per-account Train target is a **saved-coordinate preset name**. Exact `_preset_to_vars` doc says saved name → `(map_var, x_var, y_var)`; missing preset → `(None,None,None)`.
- Row `Tới bãi train` resolves the selected `farm_var` preset and calls `_move_acc`; all-account `_move_all` resolves each checked row and runs movement in parallel.
- Exact `_move_acc` doc confirms the same primitive supports an optional `stop_check` for Farm-cycle cancellation; manual button calls run to completion when no stop callback is supplied.
- Manual move is explicitly blocked while that HWND is already auto-farming: exact log says `đang farm tự động → bỏ qua thao tác thủ công (dừng farm acc trước)`.
- Saved Train X/Y are tile coordinates. Active route movement contains exact integer **32**, and near-target live-position conversion contains exact float **32.0**; the movement convention is therefore tile × 32 pixels.
- FarmTab module directly binds `FARM_NEAR_TILES = 8.0`. Exact near-target doc says accounts already near the Train target skip redundant movement and the `Tới bãi train` state; read error, different map, or unresolved target is fail-open so movement proceeds.
- Near helper locals expose `dx/dy`, but the exact final metric expression is not safely source-visible. Threshold = 8 tiles is exact; metric expression remains UNKNOWN.
- Active forward shortcut selection is inside FarmTab: `_move_acc` has `to`, `to_from`, and `_move_truyen_to` surfaces against `TRUYEN_DAI_LY_ROUTES`. Ordinary targets retain the normal `move_character` path.
- Exact `_move_truyen_to` doc says city→Farm route steps use `move_target` for the **user's selected final Train coordinate**, so shortcut data does not replace the account's saved final spot.
- Exact `_truyen_move_retry` doc says retry belongs at the route-executor layer above generic `move_character`; this prevents blind primitive requeue after teleport. It uses arrival waiting. Exact retry count remains UNKNOWN.
- Active route executor surfaces support move/click/drag/pixel-wait/npc_hub/wait/sleep/move_target. Exact local route-wait default is **30s**; interruptible sleep handling uses exact **0.5s** capped chunks.
- `npc_hub` resolves the current town/map's transmission NPC through `resolve_hub_npc`; if the town has no entry in `TRUYEN_NPC_BY_TOWN`, exact behavior is abort rather than blind click.
- Exact `_resolve_truyen_back` doc locks return-route identity: prefer **current live MapID**; only fall back to the selected Farm preset when memory read fails; normal map returns None and keeps ordinary movement.
- `_run_farm_exit` executes the route's `back` branch and verifies exit with `fast_travel.verify_exited_farm`; success requires a fresh current MapID different from the farm map.
- Live FarmTab return behavior is explicit: if shortcut exit fails and the operation is not canceled, it falls back to walking to the configured destination. Exact logs exist for sell and medicine: `teleport hụt, vẫn ở farm → đi bộ về điểm bán/điểm mua`.
- `_get_sell_coords` normalizes built-in `SELL_MAP_LIST + SELL_MAP_COORDS`, manual saved coordinates, and `meds_map_var` to `(map_id, tile_x, tile_y)`.
- Exact `_get_nav_priority` doc says UI order `Phù 1/2/3, Ngựa` is passed into `move_character` for the normal home-bound leg.
- Generic `fast_travel.py` is **not** the current FarmTab movement owner. Its own exact module status says `run_steps/goto_map DORMANT`; only `fast_hop_to_map` is LIVE through `move_to_npc`, while FarmTab also uses `verify_exited_farm`.
- Therefore Stage-S reconstruction must preserve FarmTab's local movement helpers rather than replacing them with dormant generic `goto_map`.
- Active FarmTab **forward** shortcut final failure behavior (plain-walk fallback vs abort) cannot be safely resolved from readable static control flow and remains explicit RUNTIME/STRONGER-DECOMPILE UNKNOWN. Do not import the dormant generic goto_map branch as proof.
- Ordinary final-move tolerance, long fallback-walk timeout, and exact route-leg retry count also remain UNKNOWN rather than guessed.
- B05 was cross-checked only after EXE extraction; no geometry was remeasured.

## H05 FILES
- docs/tasks/H05.md
- docs/train/H05_TRAIN_MOVEMENT_STATIC_EVIDENCE.tsv
- docs/train/H05_TRAIN_MOVEMENT_FLOW.md
- docs/train/H05_TRAIN_MOVEMENT_MODEL.json

## H06 VERIFIED RESULTS
- Followed PLAN.md/STATE.md exactly. GitHub was checked first; no H06 artifact existed, so no completed Train work was repeated.
- Inspected the exact frozen inner EXE first; SHA-256 remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Train treatment UI/config is locked: `trist_var` / key `trist` controls `Trị liệu sau khi chết`; B05/default load path is OFF. `heal_map_var` / key `heal_map` stores the selected destination; B05 default is `Trị liệu Tô Châu`.
- Treatment combobox contains built-in and manual sections with exact separators `======Có sẵn======` and `=====Thủ công=====`. Exact `_on_heal_sep_select` doc says selecting a separator jumps to the first real item below it.
- Frozen `TRAIN_HEAL_COORDS` mapping is now decoded exactly:
  - Trị liệu Đại Lý → tile (43,178)
  - Trị liệu Lạc Dương → tile (255,126)
  - Trị liệu Tô Châu → tile (155,252)
  - Trị liệu Lâu Lan → tile (294,170)
- Same farm-data map list binds those cities to MapIDs 2/3/4/5 respectively. Thus B05 default Tô Châu = MapID 4, tile (155,252).
- Exact `_heal_at_death` doc says: `Trị liệu sau khi chết: di chuyển tới map trị liệu + click 2 điểm x4 lần`, and supports both built-in `TRAIN_HEAL_COORDS` and manual saved coordinates.
- Built-in branch recognizes prefix `Trị liệu `; manual branch resolves the selected saved-coordinate preset.
- Explicit treatment failure/skip logs are recovered for: no destination selected, invalid MapID, missing built-in treatment coordinate, manual map/coordinate resolve failure, and movement failure.
- Treatment movement uses shared `move_character`; H05 tile × 32-pixel movement convention remains authoritative. No treatment-specific movement retry count is recovered.
- Exact two treatment client click points are **(892,474)** and **(514,424)**.
- Exact original doc locks the interaction repeat count as **x4**.
- Same heal constant block contains exact float **0.2**. Because readable Nuitka data does not safely expose whether this is specifically click delay vs pixel-poll pacing, H06 preserves the value but leaves the exact parameter binding UNKNOWN.
- Same heal block contains the exact `("common","active")` readiness/completion pair. The shared common-active pixel contract is therefore part of the treatment path, but exact placement/timeout and whether the 0.2 belongs to its interval remain UNKNOWN.
- Exact success log is `[Trị liệu] hwnd=... hoàn thành trị liệu tại <destination>`.
- Farm-cycle constants directly contain `_heal_at_death`, the composed `hard_stop` callback and exact failure surface `trị liệu sau chết thất bại`. This proves the treatment worker returns/communicates a success/failure result that the Farm recovery caller checks.
- The complete death-FSM consequence of treatment failure is intentionally deferred to H07; H06 does not invent abort/retry/continue behavior beyond the verified failure handoff.
- H06 finds no evidence of automatic failover to another treatment city when the selected target is invalid or movement fails.
- B05 was cross-checked only after static extraction; no geometry was remeasured.

## H06 FILES
- docs/tasks/H06.md
- docs/train/H06_TRAIN_HEAL_STATIC_EVIDENCE.tsv
- docs/train/H06_TRAIN_HEAL_FLOW.md
- docs/train/H06_TRAIN_HEAL_MODEL.json

## H07 VERIFIED RESULTS
- Followed PLAN.md/STATE.md exactly. GitHub was checked first; no H07 artifact existed, so no completed Train work was repeated.
- Inspected the exact frozen inner EXE first; SHA-256 remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Train return-to-train setting is `respawn_var` / config key `respawn`, visible label `Quay lại train khi chết`; B05/load fallback is OFF by default.
- Exact death monitor is `FarmTab._diaphu_monitor`; local surface is `self/hwnd/respawn_event/stop_event/detected/hp_latched/click_at/get_character_info/ci/hp_pct/row_d`.
- Exact original monitor doc locks cadence at **4 seconds** and says it runs `từ đầu khi start farm`, not only after reaching the Train spot.
- Two independent death signals are combined:
  - **MapID 87** → set `respawn_event` for recovery.
  - real numeric **HP 0%** → one respawn click.
- Exact HP-zero respawn click is client coordinate **(792,441)** and the doc says **1 lần**.
- `hp_latched` prevents repeated clicks while HP remains 0 and resets only when HP becomes nonzero. Unreadable HP is explicitly not equivalent to true zero.
- `detected` latches MapID-87 detection so the recovery event is set once per continuous stay in map 87 and re-arms/clears only after leaving map 87, preventing an endless recovery loop while moving out of Địa phủ.
- HP click and MapID-87 event are separate paths; recovery readiness is therefore state-based on observed MapID 87 rather than assuming the click succeeded.
- FarmTab's death monitor does **not** contain the Train-LSV-specific `common.active sau hồi sinh` wait. Do not import that behavior.
- H04's `wait_memory_ready(timeout=45.0, need=3)` remains bound to reconnect recovery; H07 does not reuse it as a death-respawn readiness wait.
- `_farm_cycle` directly owns `respawn_event`, state `Đang hồi sinh`, H06 `_heal_at_death`, `hard_stop`, and exact failure surface `trị liệu sau chết thất bại`. This verifies a real recovery branch and treatment result handoff.
- Exact FSM consequence after H06 treatment returns failure remains UNKNOWN; H07 does not invent abort/skip/continue semantics.
- `respawn` is the return-to-train enable setting. Verified intent: enabled allows recovery to return to the selected Train target; disabled must not fabricate an automatic return-to-train request.
- Exact worker continuation when `respawn=False` (stop vs remain alive/skip relocation) is not source-visible enough and remains explicit RUNTIME UNKNOWN.
- When return-to-train is enabled, reconstruction must reuse H05's current saved `farm_var` target and active movement path; no death-only hard-coded Train destination is recovered.
- New row tracker starts at `Chết: 0` and owns `_extra_deaths`. The HP-zero monitor branch directly references `_extra_deaths` beside the one-click recovery path, supporting one counter increment per latched HP-zero episode. No separate MapID-87-only increment is recovered.
- Exact death-counter reset behavior on stop/start of the same row remains RUNTIME UNKNOWN; row creation initial 0 is verified.
- Recovered state phases include monitor-side `Về địa phủ`, Farm-cycle `Đang hồi sinh`, and H06 `Trị liệu`.
- Farm-session safety layering is preserved: per-cycle `monitor_stop`, `gen_snap`, `hard_stop`, and `_hwnd_alive`. Exact `_hwnd_alive` doc rejects closed/invisible windows and same numeric HWND reused by a different PID.
- The death monitor itself receives the session stop event rather than a generation argument; generation/window safety is enforced by the surrounding Farm lifecycle. Exact monitor cleanup/finally ordering remains UNKNOWN.
- Death vs reconnect simultaneous arbitration is intentionally deferred to H08.
- B05 was cross-checked only after static extraction; no geometry was remeasured.

## H07 FILES
- docs/tasks/H07.md
- docs/train/H07_DEATH_RECOVERY_STATIC_EVIDENCE.tsv
- docs/train/H07_DEATH_RECOVERY_FLOW.md
- docs/train/H07_DEATH_RECOVERY_MODEL.json

## H08 VERIFIED RESULTS
- Followed PLAN.md/STATE.md exactly. GitHub was checked first; no H08 artifact existed, so no completed Train work was repeated.
- Inspected the exact frozen inner EXE first; SHA-256 remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Reconnect feature is `auto_reconnect_var` / config key `auto_reconnect`, visible label `Tự kết nối lại khi mất mạng`; B05/load fallback is OFF by default.
- Exact source-level placement of the auto-reconnect gate (caller launch vs monitor entry/loop) is not source-visible enough; semantic behavior remains opt-in.
- Exact reconnect watchdog is `FarmTab._disconnect_monitor`; locals include `stop_event/reconnect_ok/halt/hwnd/check_pixel/stop_character/wait_pixel/click_at/gen_snap/dc_strikes/conn/dc1/dc2/retry/invalidate_character_cache/_get_pid_from_hwnd`.
- Exact original watchdog doc locks cadence at **2 seconds** and says it runs in parallel with the Farm loop.
- Shared connection-memory semantics are exact: `True=connected`, `False=disconnected`, `None=read error`.
- The monitor uses memory as a **veto**: memory True resets disconnect strikes and prevents false halt; None is ignored and pixel detection decides. The persistent pixel pair is still required before halting.
- Frozen PIXEL_DATA was decoded directly:
  - `login.ngatKetNoi1`: point **(640,244)**, RGB **(160,145,52)**, config timeout 5, serialized tolerance False/0.
  - `login.ngatKetNoi2`: point **(702,453)**, RGB **(212,28,34)**, config timeout 5, serialized tolerance False/0.
- Exact watchdog doc requires **both** disconnect pixels for **3 consecutive ticks**; at 2s cadence this is ~6s. Transient UI color coincidences therefore do not halt the account.
- Exact confirmation log is `MAT KET NOI (dialog 3/3) -> dung farm loop, ket noi lai`. Confirmed disconnect sets `halt` and stops the Farm execution path immediately.
- `_disconnect_monitor` directly uses `stop_character`; the shared movement layer explicitly distinguishes this from `stop_game_auto` because `stop_character` only stops movement. No direct `stop_game_auto` call is recovered in the reconnect monitor.
- Exact watchdog doc says the disconnect dialog is rechecked before every reconnect click. If the dialog is gone, the click is skipped and the flow still observes active-state recovery.
- Exact reconnect client click is **(616,455)**.
- The reconnect block has local `retry` and exact attempt log denominator `/5`, locking **5 visible attempts per reconnect batch**.
- Each reconnect attempt waits for `common.active` up to **30 seconds**.
- Frozen `common.active` pixel is decoded as point **(1330,33)**, RGB **(34,8,11)**, default pixel timeout 100, tolerance 5; the reconnect path overrides the wait to its documented 30s/attempt.
- Exact `wait_pixel` interval/debug argument values for this call are not safely bound and remain UNKNOWN.
- Exact success log is `kết nối lại THANH CONG`; exact watchdog doc says success sets `reconnect_ok` and resets the Farm cycle.
- `_disconnect_monitor` locals directly contain `invalidate_character_cache` and current-PID lookup. Shared helper doc explicitly says Reader cache is cleared **immediately when reconnect succeeds**, preventing stale pointer-chain cache for up to 10s after character reload.
- Exact failed-batch log is `chưa kết nối lại được -> thử lại sau 30s`; exact integer 30 is stored in this branch.
- Exact watchdog doc says reconnect retries are **infinite**: after a failed 5-attempt batch, wait 30s and try again; never disable the account merely because reconnect has not succeeded.
- Watchdog only exits when user/session validity ends: stop event/account no longer farming/generation changed or the game window truly dies.
- Farm cycle has state `Chờ kết nối lại` and waits on `reconnect_ok`; exact Event-wait poll timeout/quantum is not safely bound and remains UNKNOWN.
- After reconnect success, Farm uses `wait_memory_ready(timeout=45.0, need=3)`.
- Shared exact memory-ready doc says `common.active` can appear before character memory is ready; valid recovery requires **3 consecutive fresh reads** with clear RoleName + MapID not None, invalidating Reader cache before each sample.
- `wait_memory_ready` timeout is explicit **fail-open**: after 45s it returns False/logs and the caller may continue; it must never wedge Farm indefinitely.
- FarmTab has verified guarded `_ensure_injected` for resources.dat, but H08 finds no direct readable proof of an **unconditional post-reconnect reinjection call** between reconnect success and memory-ready. Do not add forced reinjection merely because TCP reconnect occurred; keep this edge UNKNOWN until stronger decompilation/runtime parity.
- Reconnect-vs-death overlap is partially resolved: once `halt` is asserted, reconnect interrupts current H07/H06 actions through the Farm `hard_stop` boundary, then successful reconnect performs a cycle reset. Exact same-tick death-vs-third-strike ordering before halt remains RUNTIME UNKNOWN.
- B05 was cross-checked only after static extraction; no geometry was remeasured.

## H08 FILES
- docs/tasks/H08.md
- docs/train/H08_RECONNECT_STATIC_EVIDENCE.tsv
- docs/train/H08_RECONNECT_FLOW.md
- docs/train/H08_RECONNECT_MODEL.json

## H09 VERIFIED RESULTS
- Followed PLAN.md/STATE.md exactly. GitHub was checked first; no H09 artifact existed, so no completed Train work was repeated.
- Inspected the frozen original EXE first; inner EXE SHA-256 remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Exact shared keep modes are `none / weapons / all`, visible labels `Không / Chỉ vũ khí / Tất cả`, with exact default `KEEP_MODE_DEFAULT='all'`. B05's selected `Tất cả` matches the frozen default.
- Exact keep-mode→Train preset mapping is now locked:
  - `none → ['discard_weapons','discard_nonweapon']`
  - `weapons → ['discard_nonweapon']`
  - `all → []`
- The mode is a **keep/filter policy**, not the actual pickup enable switch. `none` must not be reconstructed as “delete every item category in the bag”; the Train mapping only activates its weapon/non-weapon-equipment discard presets.
- Weapon classification uses the shared `weapon_ids.is_weapon` layer. Shared bag-filter rule docs say weapons are protected by default and only explicit `match_weapons=True` / `discard_weapons` may target them.
- Non-weapon filtering depends on item metadata / `NON_WEAPON_EQUIP_TYPES`; the frozen warning explicitly says non-weapon filtering drops out if metadata is missing. Do not replace this with a naive “not weapon ID = discard everything” rule.
- `FarmTab.get_pickup_preset_keys` is the bridge from current `pickup_mode` to shared `keys_for_keep_mode('train', mode)`. Exact Farm wrapper doc says `[] = không vứt gì`.
- Shared `discard_for_activity` exact docs lock: keys None/[] = no discard; empty rules = zero result, no scan and no item packet; multiple active presets are OR-combined and targets deduplicated by dbID in one send pass.
- Shared discard primitive exact doc says whole stack is abandoned via packet **100005** payload **`4:<dbID>`**.
- Frozen shared defaults bind `discard_items` and `discard_for_activity` to **delay=1.0s** with stop/progress/dry-run defaults. Farm `_filter_before_town` passes activity `train`, keys and stop_check and has no recovered Farm-specific delay override, so the active pre-town filter uses the shared 1.0s discard pacing parameter.
- Shared discard is cancellation-aware through `stop_check` and returns structured `total/ok/fail/skipped/stopped/targets`.
- Normal FarmTab has **no continuous `_discard_loop` method**. Loot filtering is event-driven through `_filter_before_town`; do not copy the separate 10-second continuous discard watcher from another tab into FarmTab.
- Exact `_filter_before_town` doc says it uses Train's Nhặt đồ radio/preset for every town/full-bag path, returns post-filter `slots_after` int or None for `Tất cả`/error, shows `Đang lọc đồ`, then restores the prior state only if nobody changed it.
- Frozen `STATE_STYLE` binds `Đang lọc đồ` to foreground **#8e24aa**.
- H03's None/no-filter/error semantics and full-bag behavior are preserved unchanged; H09 does not reopen the numeric full threshold.
- Separate checkbox `Nhặt đồ không dùng hồ lô (càn khôn hồ)` is config `pickup_no_cankhon`, default False.
- Exact `_pickup_no_cankhon` doc says: **sleep 5s then write hidden `PICKITEM.IsOn=true`**, replacing the old visible UI click/tick/confirm sequence.
- Direct helper constants lock `memory_items.set_auto_fields`, section `PICKITEM`, key `IsOn`, type `bool`, value True.
- This no-Càn-Khôn feature is independent of `pickup_mode`: it enables game pickup; the keep-mode radio determines later discard behavior.
- No recurring 5-second pickup polling loop is recovered; the safe contract is one delayed enable write per helper invocation.
- No direct readback confirmation helper is recovered for `PICKITEM.IsOn`; unlike Party auto-accept, do not claim the original confirms the setting after writing.
- Exact pickup-helper threading/inline dispatch micro-order and setter-result handling remain implementation/runtime UNKNOWN.
- B05 was cross-checked only after static extraction; no geometry was remeasured.

## H09 FILES
- docs/tasks/H09.md
- docs/train/H09_LOOT_FILTER_STATIC_EVIDENCE.tsv
- docs/train/H09_LOOT_FILTER_FLOW.md
- docs/train/H09_LOOT_FILTER_MODEL.json

## H10 VERIFIED RESULTS
- Followed PLAN.md/STATE.md exactly. GitHub was checked first; no H10 artifact existed, so no completed Train work was repeated.
- Inspected the exact frozen inner EXE first; SHA-256 remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- H02/H05 home priority remains `Phù 1 / Phù 2 / Phù 3 / Ngựa`; `_get_nav_priority` passes that ordered list into shared `move_character`.
- Frozen `move_character` home-priority block directly contains `Ngựa`, an internal `Stop` sentinel surface, the `Về thành: thử ... → bấm phím ...` log, `press_single_key_dll`, and transfer-dialog probes. Static architecture supports `Ngựa` as the boundary/fallback to normal mounted/autopath movement rather than a fabricated horse hotkey. Exact source syntax around the Stop sentinel remains UNKNOWN.
- Current live mount helper is `ensure_mounted`. Exact original doc says it ensures riding **entirely by memory + packet, no pixel/click**.
- Exact riding fast path: read `IsRiding`; if `==1`, return True immediately.
- Equipped mount state is separate: shared `HasMount/MountItemID/read_mount_cached/has_mount`; exact doc says HasMount scans Site 2 equipment and returns 1/0/None, explicitly different from IsRiding.
- Frozen memory-reader constant binds **MOUNT_CACHE_TTL = 30.0 seconds** for equipped-mount caching.
- `ensure_mounted` optionally stops game auto first through `set_auto_mode(None)`; exact logs prove stop-auto failure/error does **not** hard-abort the mount attempt.
- Exact doc says callers may pass `stop_auto_first=False` after teleport because UI/game state reset makes an extra stop unnecessary.
- An exact **1.5** float is serialized in the ensure_mounted block between stop-auto diagnostics and mount-action surfaces. Its precise call/parameter binding is not instruction-visible enough and remains UNKNOWN.
- Active mount command is internal `memory_items.toggle_mount` with frozen expression **`Game.SendToggleRideState(Game.CurrentMountSlot)`**.
- Exact ensure_mounted doc locks: send mount action → **sleep 3 seconds** → fresh-memory/cache-invalidated `IsRiding` verification.
- Exact return contract: True if already riding or newly mounted; False if failed/stopped. No internal multi-send retry loop is recovered inside one ensure_mounted invocation.
- `has_mount` is consulted in the ensure block, but exact HasMount=0/None source branch/log wording is not safely visible; do not invent it.
- Exact `_remount_requeue` doc locks mid-route recovery: **stop_autopath → mount again via memory+packet → queue_autopath again**. It explicitly replaces the old pixel-click/manual-Reader remount cluster.
- `_remount_requeue` returns False only when stopped mid-way; otherwise it lets the outer movement poll continue, while stop/requeue/remount errors are logged.
- Live `move_character` directly owns `HasMount`, `remount_count`, `max_remount`, and calls `_remount_requeue`; exact numeric `max_remount` cannot be safely bound and remains STRONGER-DECOMPILATION/RUNTIME UNKNOWN.
- No active Train/shared-movement dismount routine or pixel/click dismount sequence is recovered. Teleport/game transitions may naturally clear IsRiding; the movement layer remounts when needed.
- Exact `move_to_npc` doc says same-map + known NPC position uses mounted `move_character` with arrival polling; different-map/NPC-not-spawn fallback uses game-native logic **without horse**.
- Exact `mount trước goto lỗi (bỏ qua)` log proves mount preparation error is non-fatal in the NPC helper and higher-level fallback may still continue.
- H05 Truyền routing remains authoritative. H10 only layers mounted ordinary movement/remount beneath route legs; active FarmTab movement was not replaced.
- H09 loot filtering was not reopened.
- B05 was cross-checked only after static extraction; no geometry was remeasured.

## H10 FILES
- docs/tasks/H10.md
- docs/train/H10_MOUNT_STATIC_EVIDENCE.tsv
- docs/train/H10_MOUNT_FLOW.md
- docs/train/H10_MOUNT_MODEL.json

## H11 VERIFIED RESULTS
- Followed PLAN.md/STATE.md exactly. GitHub was checked first; no H11 artifact existed, so no completed Train work was repeated.
- Re-hashed and inspected the exact frozen inner EXE first; SHA-256 remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- `FarmTab._add_coord_row` has four optional inputs `name/map_val/x_val/y_val` with four None defaults and owns row-local `name_var/map_var/x_var/y_var` plus `Bán/Train/✕` action buttons.
- B05 row schema remains `Tên | Map | X | Y | Áp dụng hết | Xóa`; no coordinate-row geometry was invented from the empty capture.
- Add-row constants directly contain prefix `Tọa độ `, local `existing`, and the initial positive index surface. Safe contract: absent explicit name → collision-aware numbered `Tọa độ N` generation beginning at 1.
- No fixed `MAX_COORDS`/hard saved-coordinate row cap is recovered; the row list is dynamic.
- Exact no-argument initial map/X/Y UI fallback cannot be safely bound from the readable constant stream and remains UNKNOWN.
- Unlike the immediately preceding buff-row builder, the coordinate-row builder has no recovered `_only_digits/vcmd` numeric-validation locals. Shared `parse_coord_value` explicitly normalizes `mid:int` but returns x/y as coordinate fields. H11 therefore does not invent a coordinate Entry clamp/range.
- `_on_map_select` exact doc says choosing a `=====` separator auto-jumps to the next real map entry, preventing separator text from becoming a final map selection.
- Save-side `coord_id_for_name` maps display map name → MapID. Exact Farm warning says an unknown map row is **skipped and not saved**, never assigned a guessed ID.
- Coordinate persistence uses shared settings section `Farm`, save prefix `coord_`, sequential index local `_n`, and current-row `name/mid/x_v/y_v` surfaces.
- Current config record contract is a sequential `coord_<n>` key family with a four-field pipe value: `preset_name|map_id|x|y`.
- Shared parser exact doc says `Parse 1 dòng coord config mới. Trả (preset, mid:int, x, y) hoặc None.`; direct constant surface contains `split('|')`.
- Exact `_load_coords` doc says saved coordinates are loaded from config and recreated as dynamic rows. Recovered locals include `coord_keys/parse_coord_value/coord_name_for_id/key/val/parsed/name/mid/x_v/y_v/map_v/parts`.
- Save-side sequential numbering and load-side ordered `coord_keys`/lambda surface preserve coordinate row ordering. Exact source expression of the sort lambda remains UNKNOWN; Stage-S must preserve numeric row order rather than unsafe lexical `coord_10 < coord_2` behavior.
- Retired/unknown MapID/display names are explicitly skipped on load; H11 does not fuzzy-remap stale maps.
- Exact rename doc says changing a preset name **immediately updates account comboboxes and any current selection using the old name**.
- Exact `_refresh_acc_combo_values` doc covers add/delete/rename and locks `rename_map={old:new}` selected-value migration.
- Exact immediate Tk-variable behavior when deleting the currently selected preset is not source-visible enough and remains RUNTIME/STRONGER-DECOMPILE UNKNOWN; do not auto-select an unrelated preset.
- Exact `_apply_coord_to_all` doc says coordinate application is **name-based**: target `sell` → all Sell comboboxes, target `farm` → all Train comboboxes.
- Per-account config save surface directly exposes `acc_`, `_sell`, `_farm`, and current character-name local `cname`; concrete key family is `acc_<character>_sell/farm`.
- Exact `load_acc_config` doc says saved coordinate choices are loaded by character name and applied **only if the preset name still exists**; stale saved selection is ignored instead of recreating a missing coordinate.
- Exact `_toggle_coord_list` doc says it hides/shows only coordinate header+body while toolbar always remains visible.
- No coordinate-list-visible/hidden config key is recovered in Farm save/load surfaces. Thus coordinate list visibility is **UI-only, not persisted**; B05 locks the fresh default as visible with button `Ẩn danh sách tọa độ`.
- Saved-coordinate edit hooks `_auto_save`, `_on_name_changed`, and `_schedule_save_all_coords` are verified.
- No coordinate-specific debounce/delay constant can be safely bound. The exact **30ms** debounce elsewhere in FarmTab belongs only to scrollregion geometry and must not be copied into coordinate persistence.
- H01's independent **30000ms** config autosave remains the safety net.
- Constructor/load surfaces `_importing` and `_saving_enabled` remain verified; exact guard-flip statement ordering during dynamic coordinate load is implementation-safe UNKNOWN, but config loading must not corrupt/rewrite itself mid-load.
- H05 live preset-name→map/x/y movement resolution and H10 mount behavior remain unchanged.

## H11 FILES
- docs/tasks/H11.md
- docs/train/H11_SAVED_COORD_STATIC_EVIDENCE.tsv
- docs/train/H11_SAVED_COORD_FLOW.md
- docs/train/H11_SAVED_COORD_MODEL.json

## H12 VERIFIED RESULTS
- Followed PLAN.md/STATE.md exactly. GitHub was checked first; no H12 artifact existed, so no completed Train work was repeated.
- Re-extracted/re-hashed the frozen specimen; inner EXE SHA-256 remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Farm account-row identity is **HWND + bound PID snapshot**, not HWND alone. `_add_or_update_row` uses `_pid_of`, `bind_window_identity`, `unbind_window_identity`.
- Exact PID-reuse log says the same HWND changing process means the old window is gone and a new row must be created. This prevents old runtime state from being inherited by a newly reused numeric HWND.
- Exact `_hwnd_alive` doc requires the HWND to exist, remain visible and still belong to the expected PID; PID mismatch means HWND reuse and returns False.
- Exact `_add_or_update_row` doc locks incremental behavior: create only when missing, otherwise update the existing row and **preserve map/x/y/preset selections**.
- Character info and Site-10 bag-slot count are normally pre-read in a background worker; `ci=None` is only a fallback-read path. Bag None means preserve the old row value.
- Active account refresh remains exact **5000ms**. Exact refresh doc says window list + character memory are read in BACKGROUND and only applied to UI on the Tk main thread.
- Refresh apply path is directly `_add_or_update_row → _remove_stale_rows(active_hwnds) → _reapply_permission_state → scroll update → schedule next refresh`.
- Exact state-label scheduler doc says every worker/monitor state update is marshaled back to Tk with **after(0)**; direct cross-thread Tk access can silently kill the process.
- Recovered visible populated-row model: `▶` play button, name, Sell/Train preset comboboxes, `⬤` state dot, state label, live MapID, row action buttons, and a combined third-line extra tracker.
- New-row state is exactly `Đã dừng`.
- Row internal runtime surfaces include `_bag_slots`, money/EXP baseline+delta fields, `_extra_deaths`, `_sell_active`, `_sell_stop_event`, `_state`, `_gen`, and control-combo fields.
- Character RoleName is sanitized by removing HTML tags with `<[^>]+>` before display. A Window fallback surface exists; its exact fallback text composition remains UNKNOWN.
- Live `MapID` is updated independently from H11's selected destination preset; do not confuse current map with target-map config.
- H03 Site-10 occupied-slot behavior is now placed into the row model: refresh None keeps the prior `_bag_slots`.
- Exact `_start_extra_track` doc says Farm starts with a time marker and money/EXP baseline is taken from the **first background refresh**, specifically to avoid memory reads on the Tk main thread.
- Exact tracker doc locks BoundMoney as **positive-delta accumulation**: selling adds earned gold; spending on medicine does not subtract from session earned-gold total.
- EXP is also accumulated only from positive deltas.
- New-row extra text surfaces are exactly `0h:00p | Túi: ? | Chết: 0 | Vàng: 0,00 | 0,00 vàng/h | 0 exp/h` as components joined by the tracker separator.
- Exact running tracker example is `1h:30p | Túi: 98 | Chết: 3 | Vàng: 5.000,01 | 3.333,33 vàng/h | 12.345.678 exp/h`; total EXP earned is internally tracked but currently hidden from this line.
- Exact rate denominator surface is **3600 seconds/hour**; money/h and EXP/h are whole-session averages, not rolling-window rates.
- Formatting helpers are locked: raw gold /10000 with Vietnamese separators, 4-decimal raw/scaled formatters, 2-decimal rounded money-rate formatter, and dot-thousands integer EXP formatter.
- Important frozen-binary correction: tracker prose still says bag updates every `refresh 3s`, but the same active FarmTab explicitly schedules the account refresh every **5 seconds**, and no separate Farm bag/extra poller is recovered. Therefore the current effective memory-sample cadence is **5s** and the embedded 3s sentence is stale documentation.
- Exact `STATE_STYLE` mapping is now locked:
  - Đã dừng #555555
  - Về bán đồ #1565c0
  - Bán đồ #1565c0
  - Mua thuốc #555555
  - Trị liệu #555555
  - Tới bãi train #1565c0
  - Đang train #2e7d32
  - Về địa phủ #c62828
  - Đang hồi sinh #e65100
  - Đang lọc đồ #8e24aa
  - Mất kết nối #b71c1c
  - unknown state fallback #555555.
- `_state` is the row's canonical runtime state; the Tk labels/dot are the main-thread UI projection.
- `_farming_acc` is the authoritative set of HWNDs with active Farm cycles. Exact play-button doc says rows in `_stopping_play` remain in orange `…` until the old cycle really exits, preventing early button flip/new overlapping cycle.
- `_gen` is a Farm-session generation guard. Exact buff/reconnect docs say old threads exit when account leaves Farm or generation changes after user stop/start. Exact source increment statements remain UNKNOWN.
- `_sell_active` and `_sell_stop_event` are separate row-local sell lifecycle state, not aliases of `_farming_acc`.
- There is **no per-row selection checkbox** in the Train account list. Exact `_checked_rows` doc says it returns **all accounts in the list**; all-account command execution itself remains H13.
- Permission/account-limit state is re-applied continuously. Exact heartbeat doc says double guard `has_permission + check_account_limit`; enabled Comboboxes use `readonly`, denied rows are disabled.
- Exact `_remove_stale_rows` doc says it removes rows for closed windows from the background-provided `active_hwnds`; locals also expose old/current PID and bind/unbind identity surfaces. Safe contract: closed/reused-PID rows are torn down incrementally, and active stale Farm work participates in stop/wait cleanup. Exact join/finally order remains UNKNOWN.
- Transient character/bag memory failures preserve row/session state rather than deleting/resetting the row.
- B05 was cross-checked only after static extraction; screenshot hash remains `17d98f6b6a263daa5857224d100355379672eae7bd7c72794323f31417d8bc53`; populated-row geometry was not invented from the empty capture.

## H12 FILES
- docs/tasks/H12.md
- docs/train/H12_ACCOUNT_ROW_STATIC_EVIDENCE.tsv
- docs/train/H12_ACCOUNT_ROW_FLOW.md
- docs/train/H12_ACCOUNT_ROW_MODEL.json

## H13 VERIFIED RESULTS
- Followed PLAN.md/STATE.md exactly. GitHub was checked first; no H13 artifact existed, so H01–H12 were not repeated.
- Re-extracted/re-hashed the uploaded frozen specimen before using the screenshots. Archive SHA-256 remains `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; inner `TLMTool.dist/TLMTool.exe` SHA-256 remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Exact `_checked_rows` documentation now locks the current all-account target set as **all accounts in the Train list**. There is no per-row selection checkbox; older all-command docstrings saying “acc được tick” are stale wording and must not recreate checkbox semantics.
- The visible Train all-account bar remains `Tới bán đồ | Bán đồ | Tới bãi train | Đánh`, mapped respectively to `_goto_sell_all / _sell_all / _move_all / _farm_all`.
- The frozen `_build_ui` surface binds these visible commands to `threading.Thread(target=..., daemon=True).start()`. Therefore the Tk click path launches an outer daemon worker and does not synchronously block the Tk thread until the whole multi-account operation completes.
- `_move_all` is explicitly parallel and owns a recovered per-row thread collection surface `rows/_threads/row`. The per-account movement guard exactly says an account already in automatic Farm is skipped for manual movement; H13 does not invent implicit stop-before-move.
- The visible `Đánh` command is the manual/one-shot Fight path: `_farm_acc` calls `start_auto_train` / StartAutoFight Train through memory/internal behavior with no game-UI click. It is **not** the large green `Bắt đầu` full Farm FSM.
- `_farm_all` is explicitly parallel. A row that is selling or still waiting for sell-stop is skipped with the frozen warning to stop selling first; H13 does not auto-cancel selling or race Fight against selling.
- `_sell_all` is explicitly parallel and must preserve H12's independent `_sell_active/_sell_stop_event` lifecycle. Exact child entry (`_sell_acc` versus `_toggle_sell`) is not safely source-visible and remains UNKNOWN.
- `_goto_sell_all` is explicitly a parallel **move-only test**: use the same route to the sell point (including the Truyền return branch where applicable), then stop; do **not** open the shop and do **not** sell.
- `_stop_all` is explicitly parallel, has a direct `_stop_acc` surface, and owns a recovered `rows/_threads/row` collection. H13 only locks this stop fan-out boundary; the complete global Bắt đầu/Dừng FSM is H14.
- Internal `_buy_meds_all` also uses the same parallel all-row pattern with a recovered `rows/_threads/row` collection and `_buy_meds_acc`; it is not added as a new visible Train button.
- Exact inner per-account daemon flags, child join/wait policy, join timeouts, and exact child-thread implementation for every all-command are not safely bound by the current static evidence and remain UNKNOWN. Do not invent a barrier or arbitrary timeout.
- H12 permission/account-limit gating remains authoritative for row UI. Whether each all-command performs an additional internal permission recheck is not proven and remains UNKNOWN.
- Command-specific safe skips are now locked: manual move while full Farm is active → skip; manual Fight while selling/stopping sell → skip. No aggregate transaction/rollback model was recovered; per-row failure must not be turned into an invented global rollback.
- Only after the frozen EXE audit, B05 was cross-checked. The supplied Train screenshot is byte-identical to the existing baseline, SHA-256 `17d98f6b6a263daa5857224d100355379672eae7bd7c72794323f31417d8bc53`; it confirms the four-button all-account bar, no account-selection checkbox, and the separate large green `Bắt đầu`. No geometry was remeasured.

## H13 FILES
- docs/tasks/H13.md
- docs/train/H13_ALL_ACCOUNT_COMMANDS_STATIC_EVIDENCE.tsv
- docs/train/H13_ALL_ACCOUNT_COMMANDS_FLOW.md
- docs/train/H13_ALL_ACCOUNT_COMMANDS_MODEL.json

## H14 VERIFIED RESULTS
- Followed PLAN.md/STATE.md exactly. GitHub was checked first; no H14 artifact existed, so H01–H13 were not repeated.
- Re-extracted and re-hashed the frozen uploaded specimen before using the screenshots. Archive SHA-256 remains `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; inner `TLMTool.dist/TLMTool.exe` SHA-256 remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Farm has three distinct lifecycle state surfaces: global `_farming`, per-account authoritative membership `_farming_acc`, and worker collection `_farm_threads`. Do not collapse them into one boolean; per-account membership can differ from old-thread liveness during cooperative stop/drain.
- Frozen FarmTab bottom-button construction is exactly `Bắt đầu` with background **#388e3c**, command `_toggle_farm`, matching B05.
- Exact `_toggle_farm` documentation locks global direction semantics: when stopped/start direction, only start accounts **not already Farm**; when running/stop direction, only stop accounts **currently Farm**. Already-correct rows are skipped.
- Active Farm projection is exactly `Dừng lại` with **#f44336**. The StartTab Farm wrapper independently contains the same active label/color.
- Exact `_toggle_single_farm` documentation locks per-row Farm start/stop and says stopping the **last** Farm account transitions into the same global all-stop workflow as the large Bắt đầu/Dừng button.
- Per-row start has a direct `has_permission_with_limit / farm_tab / farm` permission surface. The exact additional permission recheck/filter inside global `_toggle_farm` itself is not statically source-bound and remains UNKNOWN.
- `_stopping_play` is now locked as the anti-overlap stop sentinel. Its exact frozen UI is orange **#ef6c00** text `…`; normal play refresh deliberately skips those rows because the old cycle has not actually exited yet. This prevents a stopped/restarted row from launching an overlapping Farm session.
- Exact stable row play projection is now locked: row in `_farming_acc` → red **#f44336** text ASCII `II`; row not in `_farming_acc` → green **#388e3c** text `▶`; row in `_stopping_play` stays orange `…` until actual cycle exit.
- The source doc visually calls the active icon `||`, while the frozen serialized button constant is ASCII `II`. Stage-S must preserve the frozen constant unless later runtime evidence proves a font/icon substitution.
- Starting a full Farm account directly references `_farm_cycle`, `_resize_monitor`, and `_refresh_play_buttons`. This confirms the large/single Farm FSM starts the full automatic session, not H13's manual one-shot `Đánh/start_auto_train`.
- Exact `_resize_monitor` documentation locks a 1-second check cadence and only resizes game windows when not 1366×768; when associated with a row, it exits when that Farm account stops.
- Exact `_farm_cycle` documentation remains `bán đồ → mua thuốc → tới → farm → chờ chu kỳ`. Its current session surfaces include `monitor_stop/reconnect_ok/halt/respawn_event/gen_snap/hard_stop/buff_stop/cycle_start/buff_thread`, placing H07/H08 subworkers inside one Farm generation.
- Stop is cooperative, not forceful thread termination. Frozen `_check_stop` documentation says a stop request means the active operation must exit; `_is_acc_farming` checks specific account membership. H07/H08 guards remain authoritative for generation/HWND/hard-stop cancellation.
- `_wait_farm_stop` directly contains `join` and exact documentation that it waits for Farm thread exit. `has_remaining=True` cleans up stopped workers while keeping the global Farm/Dừng state; `has_remaining=False` performs the all-stopped reset.
- Exact final all-stopped FarmTab reset is `Bắt đầu` + **#388e3c** + `normal`, and it happens on the no-remaining wait/cleanup branch rather than being treated as complete at the initial stop request.
- Therefore partial row stop is locked: stop/drain that row, but if another Farm row remains the large button must remain in running/Dừng state. Last-row stop must flow into the global no-remaining reset.
- A real orange global drain UI surface exists in Farm cleanup: `Đang dừng...` + **#ef6c00** + `disabled` + `_sync_start_tab_btn` + `_wait_farm_stop`. It is directly bound to stale/closed-row cleanup. Static evidence does **not** safely prove that every ordinary user global-stop click always displays that exact intermediate caption, so ordinary-click coverage remains UNKNOWN.
- Exact buff documentation now binds generation changes to **user stop/start**: stale worker exits when account ends Farm or `gen` changes. Exact `_gen` increment/assignment statement placement and ordering versus membership/widget mutations remain UNKNOWN.
- Row button reset timing is exact enough to say `_stopping_play` preserves `…` until cycle exit and then normal refresh returns `▶`. Exact source ordering for the canonical row state label `Đã dừng` relative to cycle-finally/join remains UNKNOWN.
- `_sync_start_tab_btn` exact documentation says FarmTab synchronizes the StartTab Farm control whenever Farm state changes. Its frozen local surface contains `text/bg/state/st/_upd`, and StartTab's own `_toggle_farm_cmd` says it updates both StartTab and FarmTab controls.
- Important UI correction: synchronized Farm **state** does not mean identical stopped captions. Frozen StartTab builder stopped label is `Train`; FarmTab stopped label is `Bắt đầu`. The supplied screenshots show the same. Running state projects red `Dừng lại`.
- Exact daemon flags for each full-Farm worker, exact child join timeout/no-timeout policy, exact `_farming` assignment statements, exact membership/stopping/gen/widget mutation order, global-toggle internal permission recheck, ordinary-click use of `Đang dừng...`, and exact `Đã dừng` label-reset ordering remain explicit UNKNOWNs.
- Only after the EXE audit, B05 was re-hashed. The supplied Train screenshot remains byte-identical to the existing baseline, SHA-256 `17d98f6b6a263daa5857224d100355379672eae7bd7c72794323f31417d8bc53`; no geometry was remeasured.

## H14 FILES
- docs/tasks/H14.md
- docs/train/H14_FARM_FSM_STATIC_EVIDENCE.tsv
- docs/train/H14_FARM_FSM_FLOW.md
- docs/train/H14_FARM_FSM_MODEL.json

## H15 VERIFIED / CLASSIFIED RESULTS
- Followed PLAN.md/STATE.md exactly. GitHub was checked first; no H15 artifacts existed, so H01–H14 were not repeated.
- Re-extracted/re-hashed the exact supplied frozen specimen before classifying runtime evidence. Archive SHA-256 remains `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; inner `TLMTool.dist/TLMTool.exe` SHA-256 remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Re-hashed the supplied Train screenshot; it remains byte-identical to B05, SHA-256 `17d98f6b6a263daa5857224d100355379672eae7bd7c72794323f31417d8bc53`. This is valid live visual evidence only for the stopped/default Train UI.
- Audited the supplied package for pre-existing runtime evidence and discovered `TLMTool.dist/data/automove_log.txt`: SHA-256 `17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`, 15,741,058 bytes, 387,238 lines, extracted/archive mtime 2026-10-01 20:13:16 UTC.
- The packaged trace directly contains actual low-level helper execution: 16,040 `AutoMove queued`, 15,993 `StartAutoPath called`, 2,027 `StopAutoPath called`, 8,511 `AutoFight_Main` records, 1,579 `Game.SendToggleRideState(Game.CurrentMountSlot)`, 114 `Game.GoTo(...)`, 114 `GUI.FindUI('NPCShop')`, and 22,732 `ItemAction ... action=4 dbID=...` records.
- PID-tagged trace breadth is also material: AutoMove appears across 87 PID-tagged processes, StartAutoPath 85, AutoFight_Main 91, mount toggle 28, Game.GoTo 11, and action=4 item operations across 49 parseable PID-tagged processes.
- H15 explicitly limits what that trace proves. It verifies those **primitive executions**, not which top-level Train button/Farm generation triggered them, not successful arrival, not full sell completion, and not the complete H14 FSM.
- No literal `PICKITEM/IsOn=true`, `RequestSellItem/200036`, or direct Train reconnect-success labels were found in the packaged helper log. H15 does not treat absence from this log as proof that those features never executed.
- The Train runtime parity matrix now contains **45 cases**: 8 `RUNTIME_VERIFIED_FROM_EXISTING_EVIDENCE`, 34 `RUNTIME_ENV_REQUIRED`, and 3 `STATIC_VERIFIED`. No user-visible case is currently classified `BLOCKED`.
- Existing runtime evidence directly covers only limited scopes: stopped UI rendering; AutoMove/AutoPath primitive execution; AutoFight primitive execution; mount-toggle command execution; Game.GoTo; action=4 item primitive; and NPCShop probe execution.
- End-to-end Windows runtime verification remains required for global/single Farm start-stop transitions, partial/last-account stop, orange stopping states, active StartTab/FarmTab synchronization, all-account fan-out, full-bag threshold, periodic timing, movement arrival/Truyền fallback, treatment, death, reconnect, hidden pickup write, keep-mode filtering, remount verification, coordinate persistence, 5s row refresh, tracker arithmetic, HWND/PID reuse, permission denial, full Farm-cycle ordering, stale-generation cancellation, resize monitor and actual sale completion.
- H15 produced an exact Windows test plan with 35 runnable scenarios, specimen hash checks, PowerShell preparation commands, required per-test observations and no dependency on redesigning the test matrix later.
- Gate H is now **CLOSED FOR STATIC/VISUAL RESEARCH AND RECONSTRUCTION HANDOFF**, matching the Gate F/G project pattern. This does **not** mean end-to-end Train runtime parity has been achieved; Windows original-vs-reconstruction parity remains deferred and mandatory before a final Train runtime-parity claim.
- Stage S source reconstruction has not started and remains out of scope at this point.

## H15 FILES
- docs/tasks/H15.md
- docs/train/H15_EXISTING_RUNTIME_EVIDENCE.tsv
- docs/train/H15_RUNTIME_PARITY_MATRIX.tsv
- docs/train/H15_RUNTIME_PARITY_REPORT.md
- docs/train/H15_RUNTIME_TEST_PLAN.json
- docs/train/H15_GATE_H.md

## GATE H
**CLOSED_FOR_STATIC_VISUAL_RESEARCH_HANDOFF / END_TO_END_RUNTIME_PARITY_DEFERRED**

## I01 VERIFIED RESULTS
- Followed PLAN.md/STATE.md exactly. GitHub was checked first; no I01 artifacts existed, so completed Gate H work was not repeated.
- Inspected and re-hashed the frozen original EXE first. Inner `TLMTool.dist/TLMTool.exe` SHA-256 remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Active Train LSV implementation is a dedicated compiled `train_lsv_tab.py` module with class `TrainLsvTab`, not ordinary `farm_tab.py` under another caption. Exact embedded description: `Train LSV Tab - Cấu hình farm liên server (LSV) với danh sách acc.`
- Constructor/lifecycle surface is now locked: `_build_ui → _load_config → <Destroy>/_save_on_destroy → _start_refresh → _autosave_loop`.
- Top module state surfaces include `_farming, _acc_rows, _refresh_id, _region_child_count, _scroll_after, _rows_window, _importing, _farm_threads, _autosave_id, _map_lookup, _map_values, _map_names, _coord_rows, _saving_enabled`. Constructor also exposes `info_tab` and `notebook` references.
- Train LSV uses the shared settings backend with its own `[TrainLSV]` section in TLMTool `settings.ini`. Direct key families are `respawn, auto_reconnect, trist, heal_map, pickup_mode, buff_*, acc_*_train, coord_*`.
- Exact LSV autosave documentation is **30 seconds**: `Tự lưu config mỗi 30 giây — đảm bảo không mất dữ liệu dù quên thao tác.`
- Frozen top UI wiring is independently verified inside the LSV module: `Cấu hình Train LSV`; Quay lại train khi chết; Tự kết nối lại khi mất mạng; Trị liệu sau khi chết tại Lạc Dương LSV; Nhặt đồ; and `Dùng thủ công châu, đan dược (2x, 4x...)`.
- Direct Tk variable surfaces are `respawn_var, auto_reconnect_var, trist_var, heal_map_var, pickup_mode_var`. LSV directly references the shared pickup-mode constant family; deep discard execution remains deferred to I06 rather than copied from ordinary Train by assumption.
- The large bottom Train LSV control is its own green `Bắt đầu` button bound to `TrainLsvTab._toggle_farm`. Full LSV FSM semantics remain deferred to I11.
- Saved-coordinate wiring is now locked: dynamic `_coord_rows`; `+ Thêm tọa độ → _add_coord_row`; hide/show through `_toggle_coord_list`; helpers `_coord_name_list/_preset_to_vars/_apply_coord_to_all/_refresh_acc_combo_values/_remove_coord_row/_schedule_save_all_coords/_load_coords`; per-account selection persists under `acc_*_train`.
- The module's embedded LSV map label set is independently recovered as Tần Hoàng Địa Cung Tầng 1–4, Phàm Liên Trại, Thanh Liên Trại and Khô Vinh Đạo. MapID/coordinate execution semantics remain I10.
- Manual schedule wiring is now locked through `_buff_rows/_add_buff_row/_remove_buff_row/_get_buff_keys/_load_buffs`. The dedicated fixed `_da_minh_chau_row` is **Dạ Minh Châu**, has no delete button and is always active according to exact frozen documentation. Allowed key list is **F1–F10 + 1,2,3**.
- B06 visually shows Dạ Minh Châu key `1` and `0 phút 5 giây`, but I01 preserves B06's existing warning: those values may be persisted runtime config, not clean-package defaults. They were not promoted into hardcoded defaults.
- Train LSV account discovery directly consumes shared `start_tab.get_windows()`; it does not own a second HWND enumerator. Its own row projection uses PID identity binding, character/bag reads, `load_acc_config`, permission scope `trainlsv_tab`, and LSV-specific action callbacks.
- Exact refresh architecture is independently verified: window/character memory reads happen in a BACKGROUND worker, only apply to Tk on the main thread, and apply `_add_or_update_row → _remove_stale_rows(active_hwnds) → _reapply_permission_state → _request_scroll_update`.
- Exact LSV refresh cadence is **5 seconds incremental**, with dedicated `_start_refresh/_stop_refresh/_schedule_refresh/_refresh_acc_list` lifecycle. Frozen docs explicitly say start when the tab is selected and stop when switched away.
- Row action wiring directly references `_toggle_single_farm, _ensure_in_lsv, _move_acc, _move_lsv, _farm_acc, _leave_lsv`. I01 does not yet assign deep navigation semantics to those symbols.
- All-account visible bar is exactly `Tới LSV | Tới chỗ train | Đánh | Rời LSV`, mapped to `_move_lsv_all / _move_all / _farm_all / _leave_lsv_all`. The UI block directly binds these bulk actions through `threading.Thread(... daemon ...).start()`, keeping them off Tk. Target/conflict/wait semantics remain I11.
- StartTab integration is real and two-way. TrainLsvTab owns `start_tab_ref/_sync_start_tab_btn`; StartTab has Train LSV quick controls and exact docs that bulk LSV actions run in a worker thread and the Train LSV toggle updates both StartTab and TrainLsvTab. StartTab is a forwarding/mirror surface, not a separate LSV engine.
- Only after EXE extraction, B06 was cross-checked. The current supplied Train LSV image SHA-256 is `9e3b57671a2ff165ea31264a1c2fb19493f861a7bdadc4dc993a55bd130f5d29`, byte-identical to the locked B06 baseline. No geometry was remeasured and no behavior was inferred solely from the screenshot.

## I01 FILES
- docs/tasks/I01.md
- docs/train_lsv/I01_LSV_UI_WIRING_STATIC_EVIDENCE.tsv
- docs/train_lsv/I01_LSV_UI_WIRING_FLOW.md
- docs/train_lsv/I01_LSV_UI_WIRING_MODEL.json

## I01 CORRECTION / STRONGER STATIC RESOLUTION
- A stronger direct decode of the frozen `.train_lsv_tab` Nuitka constant chunk resolved I01's previous B06 reservation about the fixed Dạ Minh Châu row.
- `TrainLsvTab._add_buff_row` exact defaults are now statically decoded as `(enabled=False, key='1', minutes='0', seconds='5', fixed=False)`.
- `_build_ui` calls `_add_buff_row(fixed=True)` for `_da_minh_chau_row`.
- Therefore the fixed Dạ Minh Châu row's clean code defaults are now locked as **key 1, 0 minutes, 5 seconds**; `fixed=True` then forces its always-active/no-delete presentation.
- This is frozen-EXE evidence, not an inference from the screenshot. I01 task/model/evidence files were updated accordingly.

## I02 VERIFIED RESULTS
- Followed PLAN.md/STATE.md exactly and performed the user's requested GitHub-first continuity check. No I02 artifacts existed and the latest completed work was I01, so no completed work was redone.
- Inspected the frozen original EXE first. A direct decode of the well-formed Nuitka `.train_lsv_tab` constant chunk at file offset `0x2c07798` recovered **1201** top-level constants from a **37904-byte** encoded part.
- Authoritative Train LSV map labels/IDs are now locked: Tần Hoàng Địa Cung Tầng 1/2/3/4 = **10014/10015/10016/10017**; Phàm Liên Trại = **10004**; Thanh Liên Trại = **10005**; Khô Vinh Đạo = **10007**. Lạc Dương LSV/server hub is **10000**; normal-world Lạc Dương used for entry is MapID **3**.
- Exact full LSV-zone set used by `_ensure_in_lsv` is `{10000,10004,10005,10007,10014,10015,10016,10017}`.
- `_move_lsv` has a smaller special already-inside set `{10000,10014,10015,10016,10017}`. For those maps it calls shared `move_character` to MapID 10000, tile **(236,190)** / pixel **(7552,6080)** and skips normal-world gate clicks.
- Normal `Tới LSV` path calls shared `move_character` to normal Lạc Dương MapID **3**, tile **(232,190)** / pixel **(7424,6080)**, then uses exact entry clicks **(891,473)** and **(480,605)**. A **1-second** pacing constant is statically bound to this click block, but its exact statement placement between/after the clicks remains UNKNOWN.
- `_move_lsv` directly owns `stop_check`, current MapID and movement-result `ok`; movement failure is explicit. Its recovered local surface contains no `_wait_active` and no second post-click character-info sample, so I02 does **not** invent post-gate MapID/common.active verification inside `_move_lsv`.
- Both `_move_lsv` and `_ensure_in_lsv` directly reuse shared `move_character`. Therefore H10's shared memory/packet mount/remount primitive applies at that edge; no I02-specific horse hotkey/pixel mount helper was recovered. Ordinary Train return-town/Truyền logic is not imported.
- `_ensure_in_lsv` is now locked as a **premove/normalization** step before the caller's final saved-coordinate movement. `farm_map=None` compatibility targets **10014**. Final `Tới chỗ train` movement remains I03.
- Exact floor order is `[10000,10014,10015,10016,10017]`.
- Exact floor waypoint table is:
  - `(10000,10014,258,470,True)`
  - `(10014,10015,26,215,False)`
  - `(10015,10016,95,90,False)`
  - `(10016,10017,132,224,False)`.
- Floor climb is sequential. Exact 10000→10014 portal action is click **(609,450)** exactly **3 times**, **0.5s** apart. Higher-floor transitions require movement/map-change readiness but their table flag says no extra portal click.
- If a requested floor is not found in the floor order, the frozen path falls back to **10014**. If already at or above the requested floor index, the frozen branch says it is already high enough and does not replay lower-floor transitions.
- Exact flat-map waypoint table is: **10004→(37,264)**, **10005→(487,257)**, **10007→(256,36)**. If already on the selected flat map, no premove is required; otherwise the branch moves/observes MapID and requires the final MapID to equal the requested flat map.
- Flat-map entry directly checks shared pixel `common.canhBaoPK`; when shown it clicks exact point **(617,454)**. The branch contains exact numeric constants **0.3** and **0.5**, but their precise call/argument placement is not instruction-bound and remains UNKNOWN.
- When outside the full LSV set, exact frozen log semantics are “ngoài cụm LSV → Tới LSV”. The post-entry normalization block has a one-argument integer **3** constant, but its exact call binding remains STRONG_STATIC_BUT_NOT_INSTRUCTION_BOUND. An unrecognized map after normalization is explicitly reasoned as **10000**.
- `_wait_active` exact decoded defaults are now locked as `timeout=30, click_if_stuck=False`.
- `_wait_active` waits shared `common.active`. Reusing the already-frozen shared pixel definition: point **(1330,33)**, RGB **(34,8,11)**, tolerance **5**. TrainLsvTab exposes `window_hwnd/timeout/interval/debug` kwargs to `wait_pixel`; exact interval/debug values remain UNKNOWN.
- With `click_if_stuck=True`, exact frozen recovery is click **(609,450)** exactly **2 times**, **1 second** apart, then continue waiting for `common.active`.
- Important cancellation boundary: `_wait_active` has no `stop_check/stop_event` parameter in its decoded signature/local surface. Movement/premove are stop-check aware, but a bounded active wait itself is not directly passed the TrainLSV stop callback.
- No arbitrary I02-specific retry loop was recovered. The fixed 3-click portal burst and optional 2-click stuck recovery are the only exact retry-like entry behaviors here; any retry inside shared `move_character` remains owned by that shared helper.
- Only after static extraction, the packaged `automove_log.txt` was searched for correlated `Tới LSV`, entry-click, common.active, Địa Cung and PK-warning evidence. No top-level/correlated Train LSV entry trace was recovered. Generic AutoMove/AutoPath lines remain primitive-level evidence only; I02 is static-verified, not end-to-end runtime-verified.

## I02 FILES
- docs/tasks/I02.md
- docs/train_lsv/I02_LSV_ENTRY_STATIC_EVIDENCE.tsv
- docs/train_lsv/I02_LSV_ENTRY_FLOW.md
- docs/train_lsv/I02_LSV_ENTRY_MODEL.json

## I03 VERIFIED RESULTS
- Followed PLAN.md/STATE.md exactly and performed the GitHub-first continuity check. No I03 artifacts existed; the latest completed work was I02, so earlier I work was not redone.
- Re-materialized the exact supplied TLMTool_2.1.2 archive and re-hashed it before analysis. Archive SHA-256 remains c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd; inner TLMTool.exe SHA-256 remains 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22.
- The directly decoded .train_lsv_tab Nuitka chunk remains well-formed at offset 0x2c07798 with encoded part size 37904 bytes and 1201 top-level constants.
- Manual row Tới chỗ train starts from the selected farm_var saved-coordinate preset. The row callback directly references _preset_to_vars; an invalid/missing preset logs “chưa chọn tọa độ Farm hợp lệ” and does not enter the final movement path.
- The valid row callback surface is now locked as preset resolution -> _ensure_in_lsv(... farm_map=...) -> _move_acc(...). This preserves I02 as map/floor premove and I03 as the final saved-coordinate move.
- Exact _move_acc documentation says it moves directly to the selected coordinate with no intermediate station. It accepts a stop_check callback for Farm-cycle cancellation; manual None/no-stop semantics run the move fully.
- _move_acc first calls _ensure_injected. Exact failure text is “bỏ qua: chưa inject được DLL”; no alternate pixel movement path is recovered for that failure.
- The final movement helper directly imports/uses shared move_character. Its decoded local surface is self/hwnd/map_var/x_var/y_var/stop_check/_hp/move_character/map_sel/map_id/name/mid/tile_x/tile_y/pixel_x/pixel_y/ok.
- Map selection is resolved/validated into a numeric MapID before movement. Exact validation logs are “bỏ qua: ko có bản đồ” and “bỏ qua: map_id không hợp lệ”. Module-level lookup ownership remains _map_lookup backed by shared FARM_MAP_LIST plus local _MAP_LIST/_map_values/_map_names. The exact Python label-vs-ID expression remains UNKNOWN.
- Saved X/Y are tile coordinates. The final movement block has strip normalization, tile_x/tile_y and pixel_x/pixel_y locals plus exact integer 32, so final movement converts to pixels with x32. Invalid coordinates log “bỏ qua: tọa độ ko hợp lệ”.
- Exact move_character keyword tuple is (wait_for_arrival, stop_check). Therefore final LSV movement requests arrival waiting and directly propagates the caller cancellation callback. There is no TrainLSV-specific timeout argument; exact arrival timeout remains owned by shared move_character.
- I03 explicitly checked ordinary Train H05's 8-tile skip. TrainLsvTab contains no _is_near helper, no PosX/PosY constants, no distance/near-target documentation and no dx/dy/current-position locals in _move_acc. Therefore H05's explicit 8-tile pre-skip is NOT part of TrainLsvTab._move_acc and must not be copied into LSV reconstruction.
- This does not redefine shared move_character: that shared helper may still naturally recognize exact arrival. I03 only proves there is no separate TrainLSV 8-tile pre-check.
- After the final shared move, _move_acc has no _wait_active/wait_pixel/common.active/get_character_info or second MapID-read surface. Final point completion relies on move_character(wait_for_arrival=True); I02's common.active wait is limited to LSV map/floor transitions.
- Success log prefix is “[Tới] Hoàn thành hwnd=”. Timeout text is “chưa đến nơi sau timeout (...) — tiếp tục tác vụ”. Thus an arrival timeout at this TrainLSV layer is logged as continue-task behavior, not an unconditional fatal Farm-cycle abort. The exact Python return value remains UNKNOWN.
- Farm-cycle constants preserve state “Tới bãi LSV” and adjacent ensure keywords (stop_check, farm_map), consistent with the I02 premove -> I03 final move pipeline.
- All-account Tới chỗ train remains I11. I03 locks only the reusable per-account _move_acc primitive and does not invent _move_all target/thread/conflict/join behavior.
- Only after static extraction, packaged automove_log.txt was searched. Generic AutoMove/StartAutoPath/StopAutoPath primitives exist, but there are zero correlated lines for “[Tới] Bắt đầu”, “[Tới] hwnd=”, “[TrainLSV]” or “Tới chỗ train”. I03 is STATIC_VERIFIED, not end-to-end runtime-verified.

## I03 FILES
- docs/tasks/I03.md
- docs/train_lsv/I03_TRAIN_POINT_STATIC_EVIDENCE.tsv
- docs/train_lsv/I03_TRAIN_POINT_FLOW.md
- docs/train_lsv/I03_TRAIN_POINT_MODEL.json

## I04 VERIFIED RESULTS
- Followed PLAN.md/STATE.md exactly and performed the GitHub-first continuity check. No I04 artifacts existed; I01–I03 were already complete and were not repeated.
- Rechecked the frozen original first. Archive SHA-256 remains `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; inner `TLMTool.exe` SHA-256 remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- The decoded `.train_lsv_tab` chunk remains the authority at file offset `0x2c07798`, encoded size 37904 bytes, 1201 top-level constants.
- Exact `_leave_lsv` contract is now locked: it only proceeds when the character's current MapID is **10000**. Exact frozen text for every other map is `không phải 10000 → bỏ qua`.
- Therefore manual/per-account `Rời LSV` does **not** normalize characters from 10014–10017 or 10004/10005/10007 back to the hub before leaving. Floor/flat maps are skipped by this helper.
- Exact exit-gate destination is the LSV hub MapID **10000**, tile **(236,190)**, pixel **(7552,6080)**. This is the same serialized hub-gate target already locked in I02.
- `_leave_lsv` directly reuses shared `move_character`. Its strongly mapped local surface is `self, hwnd, _hp, move_character, click_at, time, ci, current_map, ok`.
- The movement result is checked through `ok`. Exact failure text is `di chuyển tới cổng thất bại`; the normal two-click exit sequence is not continued on that failure branch.
- Exact frozen keyword tuple `(wait_for_arrival,)` proves that `_leave_lsv` explicitly supplies/overrides the shared movement wait-for-arrival option. The constant-only decode does not safely bind the loaded boolean value, so **True vs False remains explicit UNKNOWN** rather than guessed.
- Exact exit-click order is locked as **(887,475)** then **(478,427)**.
- The leave locals include `time`, so pacing exists in the helper, but its constant block introduces no leave-specific numeric timing literal. Exact sleep interval(s) and exact before/between/after placement remain UNKNOWN. Do not copy the normal Tới-LSV 1-second timing merely by analogy.
- `_leave_lsv` has no `stop_check/stop_event` parameter in its decoded local/signature surface. Unlike I02/I03 movement helpers, no TrainLSV cancellation callback is directly passed into this leave helper.
- The leave block does not expose `_ensure_injected`; I04 therefore does not add an explicit pre-injection step. Any injection/resource behavior inside shared helpers remains shared-helper-owned.
- There is no post-exit verification inside `_leave_lsv`: no second `get_character_info`, no fresh MapID read, no `_wait_active`, no `wait_pixel`, and no `common.active`. Exact success log is `[Rời LSV] Hoàn thành hwnd=` after the move/click sequence.
- Three static outcomes are now locked: non-10000 → skip; 10000 + gate move failure → log failure/no normal exit clicks; 10000 + gate move success → click (887,475), then (478,427), then completion log. Exact Python return values remain UNKNOWN.
- `_leave_lsv` does not call `_ensure_in_lsv`, `TRAIN_FLOOR_ORDER`, or `TRAIN_FLAT_WAYPOINTS`. I02 entry/premove and I03 final train-point movement remain separate and unchanged.
- All-account `_leave_lsv_all` orchestration remains deferred to I11. I04 locks only the per-account primitive.
- Only after static extraction, packaged `automove_log.txt` was searched for `[Rời LSV]`, `Rời LSV`, and the two exit-click coordinates. No correlated top-level leave trace was recovered. Generic movement records remain primitive-level evidence only.
- I04 classification is **STATIC_VERIFIED**, not end-to-end runtime parity.

## I04 FILES
- docs/tasks/I04.md
- docs/train_lsv/I04_LEAVE_LSV_STATIC_EVIDENCE.tsv
- docs/train_lsv/I04_LEAVE_LSV_FLOW.md
- docs/train_lsv/I04_LEAVE_LSV_MODEL.json

## I05 VERIFIED RESULTS
- Followed PLAN.md/STATE.md exactly and checked GitHub first. No I05 artifacts existed; I01-I04 were already complete and were not repeated.
- Frozen TrainLSV authority remains `.train_lsv_tab` at offset `0x2c07798`, encoded size 37904 bytes, 1201 constants. The project's own `.keyboard` helper was independently decoded from the same frozen EXE.
- Schedule UI is shared TrainLSV configuration through `_buff_rows/_add_buff_row/_remove_buff_row/_get_buff_keys/_load_buffs`; allowed keys are exactly **F1-F10 + 1,2,3**.
- Exact clean `_add_buff_row` defaults are **enabled=False, key=1, minutes=0, seconds=5, fixed=False**. User-added rows therefore start disabled and are removable.
- The fixed Dạ Minh Châu row is created with `fixed=True`: always active, no delete button, clean key **1**, clean time **0 phút 5 giây**.
- Time fields are digit-constrained through `_only_digits`, `%P`, and `isdigit`. Exact blank-string handling remains UNKNOWN.
- `_trigger_da_minh_chau` sends Dạ Minh Châu once when Farm starts for an account. The frozen doc distinguishes asynchronous `wait=False` mode and synchronous Farm-cycle `wait=True` mode.
- One-shot Dạ Minh Châu reads `IsRiding`. If already not riding, no dismount is needed. If riding, the frozen path uses exact points **(1306,340)** when the horse-toggle surface is not active, then **(906,688)** to dismount. The old points **(1131,121)/(1073,123)** are explicitly absent from this frozen path.
- Exact one-shot key call is `press_single_key_dll(hwnd,key,delay=0,sync=True)`.
- The frozen keyboard helper proves this is targeted hidden-window key delivery through the project's DLL synchronization message path, not physical/global keyboard control.
- Repeating worker is `_buff_loop`; its exact local surface includes `hwnd, stop_event, row, gen, press_single_key_dll, rd, key, mins, secs, interval, deadline`.
- Architecture is one repeating schedule worker per farming account HWND, using the shared TrainLSV row configuration. The worker internally services configured rows; no separate timer thread per buff row is recovered.
- Farm-cycle owns dedicated `buff_stop` and `buff_thread`, separate from the discard worker.
- Exact generation guard is locked: old schedule worker exits when the account leaves Farm or the generation changes after stop/restart, preventing stale-session key sends.
- Repeating worker uses key/minute/second values and an `interval/deadline` model. Exact multi-row deadline/reset ordering remains UNKNOWN.
- Exact zero/empty/malformed interval policy remains UNKNOWN; it is not guessed.
- Repeating worker definitely uses `press_single_key_dll`, but TrainLsv evidence does not independently bind the one-shot's delay/sync options to that repeating call. Repeating call options remain UNKNOWN.
- Persistence is safely locked as `buff_<n>=enabled|key|minutes|seconds`; `_load_buffs` sorts `buff_*`, splits on `|`, and recreates rows with those four fields.
- Exact persisted index/migration rule for the fixed Dạ Minh Châu row remains UNKNOWN.
- Only after static extraction, packaged `automove_log.txt` was searched for Dạ Minh/[Buff]/keyboard schedule markers; no correlated schedule trace was found. I05 therefore remains **STATIC_VERIFIED**, not runtime-parity verified.

## I05 FILES
- docs/tasks/I05.md
- docs/train_lsv/I05_BUFF_SCHEDULE_STATIC_EVIDENCE.tsv
- docs/train_lsv/I05_BUFF_SCHEDULE_FLOW.md
- docs/train_lsv/I05_BUFF_SCHEDULE_MODEL.json

## I06 VERIFIED RESULTS
- Followed PLAN.md/STATE.md exactly and performed the GitHub-first continuity check. No I06 artifacts existed; I01-I05 were already complete and were not repeated.
- Rechecked the frozen original first. Archive SHA-256 remains `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; inner EXE SHA-256 remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- TrainLSV authority remains `.train_lsv_tab` at file offset `0x2c07798`, size 37904, 1201 constants. Shared filtering authority was independently decoded from `.bag_filter` at `0x28d5db3`, size 5162, 145 constants.
- The TrainLSV `Nhặt đồ` radio is a keep/discard policy. It is backed by `pickup_mode_var/PICKUP_MODE_DEFAULT/PICKUP_MODE_LABELS/PICKUP_MODES/PICKUP_PRESET_KEYS/get_pickup_preset_keys` and aliases the shared bag-filter keep-mode contract.
- Exact shared modes/labels/default are: `none=Không`, `weapons=Chỉ vũ khí`, `all=Tất cả`, default `all`.
- Exact preset-key mapping is locked: `none -> [discard_weapons, discard_nonweapon]`; `weapons -> [discard_nonweapon]`; `all -> []`.
- Therefore TrainLSV default `Tất cả` means **keep everything / discard nothing**, not “enable pickup of all items”.
- Shared `discard_for_activity` exact docs say `None/[] -> KHONG vut gi`; empty rules return zero without scanning/touching game or sending packets.
- Train activity provides `discard_nonweapon` plus explicit `discard_weapons` with `match_weapons=True`. Shared filter OR-merges selected rules, deduplicates by dbID and performs one discard pass.
- Low-level discard path is exact: shared `discard_items` uses `abandon_item`, action **4**, whole-stack packet `100005 "4:dbID"`, and returns `total/ok/fail/skipped/stopped/targets`.
- TrainLSV `_discard_loop` calls shared `discard_for_activity` with activity `train` and exact kwargs `keys, stop_check`. It does not override the shared delay/dry-run defaults.
- Shared `discard_for_activity` defaults decode as `keys=None, extra_rules=None, delay=1.0, stop_check=None, on_progress=None, dry_run=False`. Effective TrainLSV discard pacing therefore inherits **1.0s** and real destructive mode.
- TrainLSV bag metric is occupied Site-10 slots. `_get_bag_slots` calls `memory_items.get_bag` and reads `slots`; exact doc says “Số ô túi đồ đang dùng (Site 10)” and returns None on read failure.
- Exact discard watcher cadence is **10 seconds**. Frozen worker doc independently says “đọc slots mỗi 10s, chỉ vứt khi túi đầy.”
- `_discard_loop` directly references `FULL_BAG_THRESHOLD`, but the numeric threshold is **not safely bound** by current static evidence. Do not guess 98/100/etc and do not import ordinary H03's also-unresolved threshold.
- Safe full-bag boundary: live occupied `slots` are threshold-gated; only the “full” side runs a discard pass. Unreadable bag samples are not evidence of full and must not trigger destructive discard.
- Temporary state is exact: `Đang lọc đồ`, style `#8e24aa`. Worker locals contain `row, prev`; exact doc says show purple while discarding then restore the previous state.
- Serialized discard steady-state set is exactly `{'Đang train LSV'}`. Its exact native placement as eligibility gate vs restoration guard remains unbound; do not invent extra state branches.
- Worker error/result surfaces are exact: `[Nhặt đồ] hwnd=... vứt lỗi: ...`, slot-count “túi đầy (...)”, total discarded, and separate fail count.
- `_discard_loop` local surface is account-targeted: `self, hwnd, stop_event, stop_check, BF, MI, _bag, _slots, keys, row, prev, res, e`.
- Farm-cycle locals contain dedicated `discard_stop` alongside `gen_snap/buff_stop/buff_thread`; the discard watcher belongs to the per-account Farm session. Exact discard-thread handle retention, daemon/join micro-order and exact generation predicate inside the discard loop remain UNKNOWN.
- Full decoded TrainLsvTab constants contain **no** `PICKITEM`, `IsOn`, `set_auto_fields`, `PickRanger` or `IsFilterItem`. I06 therefore finds **no direct TrainLSV hidden auto-pick enable** analogous to ordinary Train H09. Do not import H09's `PICKITEM.IsOn=true` path into TrainLSV without later direct evidence.
- Only after static extraction, packaged automove_log was searched. Top-level `[Nhặt đồ]`, `Đang lọc đồ`, `discard_for_activity`, `PICKITEM` and `IsOn=true` markers were absent.
- Existing runtime log does contain action-4 item primitives: **22,734** raw `action=4` occurrences and **22,732** `ItemAction spts sent action=4` occurrences; prior H15 parsing found action-4 records across **49 PID-tagged processes**.
- Runtime classification remains scoped: action-4 primitive execution is runtime-evidenced, but there is no top-level correlation proving those records came from TrainLSV's bag-full watcher. TrainLSV I06 trigger remains STATIC_VERIFIED / runtime-environment-required.

## I06 FILES
- docs/tasks/I06.md
- docs/train_lsv/I06_PICKUP_FILTER_STATIC_EVIDENCE.tsv
- docs/train_lsv/I06_PICKUP_FILTER_FLOW.md
- docs/train_lsv/I06_PICKUP_FILTER_MODEL.json

## I07 VERIFIED RESULTS
- Followed PLAN.md/STATE.md exactly and performed the GitHub-first continuity check. No I07 artifacts existed; I01-I06 were already complete and were not repeated.
- Rechecked the frozen original first. Archive SHA-256 remains `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; inner EXE SHA-256 remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- TrainLSV treatment authority remains `.train_lsv_tab` at offset `0x2c07798`, size 37904, 1201 constants.
- Treatment is opt-in. UI/config variable is `trist_var`; exact config default is `trist=False`.
- `heal_map_var` and config key `heal_map` still exist for compatibility, with clean UI value `10000`, but the active frozen `_heal_at_death` doc explicitly says the treatment map is **fixed 10000** and does **not** depend on `heal_map_var`. Do not import ordinary Train H06's four-city treatment selector.
- Exact HP gate inside `_heal_at_death`: readable `HpPercent >= 50` → skip treatment; readable `HpPercent < 50` → run treatment; unreadable HP → still run treatment.
- This HP gate is owned by the helper itself, not only by callers. The Farm cycle also has explicit pre-train treatment log `% < 50% lúc bắt đầu → trị liệu trước` followed by `_heal_at_death`.
- Exact fixed treatment coordinates are `TRAIN_HEAL_COORDS = {'10000': (163,237)}`: MapID **10000**, tile **(163,237)**.
- Because the helper directly reuses the already-frozen shared `move_character` pixel contract, the derived shared movement target is **(5216,7584)** = tile ×32. The pixel pair is derived from the shared movement contract, not separately serialized.
- `_heal_at_death` local model is `self, hwnd, stop_check, ci, hp_pct, map_id, coords, heal_tile_x, heal_tile_y, move_character, click_at, ok`.
- The helper directly uses shared `move_character`; exact failure log is `di chuyển đến map trị liệu thất bại`. A failed move aborts the normal treatment-click completion path.
- `stop_check` is an explicit treatment argument/API surface, proving cooperative cancellation intent. Exact pass-through/checkpoint placement inside movement/click execution remains UNKNOWN rather than imported from ordinary Train.
- Active treatment state is exact `Trị liệu`; TrainLSV style table maps it to `#555555`. No `prev` state local is recovered, so no helper-owned previous-state restoration is proven.
- Exact treatment click coordinates are **(892,474)** and **(514,424)**. Exact frozen doc says the two points are used **x4 lần**.
- The treatment local tuple contains no explicit Python loop variable `_`, unlike I02's floor loop metadata. This strongly suggests the x4 behavior is delegated to the click helper's repeat/count mechanism, but exact source call shape is not byte-for-byte recovered and remains STRONG_STATIC/UNKNOWN.
- Shared frozen `mouse.click_at` default delay is 0.5s, but TrainLSV treatment does not independently bind whether it accepts that default or overrides pacing. Effective treatment click delay/order remains UNKNOWN.
- Ordinary Train H06's 0.2 pacing must **not** be imported: TrainLsvTab has no 0.2 float constant.
- No post-treatment HP verification is recovered: `_heal_at_death` has no second character-info/HP local and no wait-until-HP-target loop.
- No treatment-specific `_wait_active/wait_pixel/common.active` surface exists. Do not add a post-treatment active-screen wait.
- Completion log is `hoàn thành trị liệu tại map ...` after the successful movement/click sequence. Exact Python return values for skip/failure/success remain UNKNOWN.
- Death-trigger orchestration remains deferred to I09; I07 only locks the treatment primitive and the Farm-start pre-heal caller edge.
- Only after static extraction, packaged `automove_log.txt` was searched for treatment markers, tile and click coordinates; all returned zero correlated treatment lines. I07 is **STATIC_VERIFIED / RUNTIME_ENV_REQUIRED**.

## I07 FILES
- docs/tasks/I07.md
- docs/train_lsv/I07_TREATMENT_STATIC_EVIDENCE.tsv
- docs/train_lsv/I07_TREATMENT_FLOW.md
- docs/train_lsv/I07_TREATMENT_MODEL.json

## I08 VERIFIED RESULTS
- Followed PLAN.md/STATE.md exactly and performed the GitHub-first continuity check. No I08 artifacts existed; I01-I07 were already complete and were not repeated.
- Rechecked the frozen original first. Archive SHA-256 remains `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; inner EXE SHA-256 remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- TrainLSV reconnect authority remains `.train_lsv_tab` at offset `0x2c07798`, encoded size 37904, 1201 constants.
- Auto reconnect is opt-in and clean default is **False**: `auto_reconnect_var`, label `Tự kết nối lại khi mất mạng`, config key `auto_reconnect`, exact fallback `('auto_reconnect', False)`. Exact source placement of the gate remains UNKNOWN.
- Exact watchdog is `TrainLsvTab._disconnect_monitor`, running in parallel with Farm at **2-second cadence**.
- TrainLSV independently serializes the memory-veto design: shared TCPGame connected probe is tri-state; True resets disconnect strikes and vetoes false positives, None is unresolved/read-error and lets pixels decide, False still does not bypass the persistent pixel-dialog requirement.
- Exact disconnect probes from frozen `.pixel_data`:
  - `login.ngatKetNoi1`: point **(640,244)**, RGB **(160,145,52)**, timeout **5**, tolerance **5**.
  - `login.ngatKetNoi2`: point **(702,453)**, RGB **(212,28,34)**, timeout **5**, tolerance **5**.
- Both pixels must match for **3 consecutive 2-second ticks**, about 6 seconds, before halt. Positive memory-connected state resets the strike chain.
- Window/process identity is also a monitor exit guard: missing window or changed process identity stops the disconnect monitor rather than reconnecting the wrong HWND.
- Confirmed 3/3 disconnect signals `halt` and directly uses shared `stop_character`, which remains a movement-stop surface rather than a global stop-all-game-auto operation.
- Before every reconnect click, the monitor re-confirms the disconnect dialog. If the dialog has disappeared, it skips the click and still observes recovery.
- Exact reconnect click is **(616,455)**.
- Exact reconnect batch is **5 attempts**, independently serialized by `range(0,5,1)` and `/5` logging.
- Each attempt waits up to **30 seconds** for shared `common.active`.
- Frozen `common.active` is point **(1330,33)**, RGB **(34,8,11)**, tolerance **5**. Exact wait_pixel interval/debug kwargs remain UNKNOWN.
- On reconnect success, the monitor invalidates the character Reader cache for the current PID and sets `reconnect_ok`; exact docs define this as a Farm-cycle reset rather than continuation of the interrupted sub-action.
- TrainLSV has an exact stronger Farm-cycle event-wait contract than previously recovered ordinary Train: `reconnect_ok.wait(timeout=5)`, bound by adjacent `wait`, `(5,)`, and `('timeout',)` constants.
- If all 5 attempts fail, exact behavior is remain in `Chờ kết nối lại`, wait **30 seconds**, and retry another batch indefinitely while the Farm session/window remains valid. Failure does not disable the account.
- After `reconnect_ok`, TrainLSV calls shared `wait_memory_ready(timeout=45.0, need=3)`.
- Shared helper clean defaults are `(45.0,3,1.0)`; because TrainLSV overrides timeout/need only, effective memory-ready sample interval is **1.0 second**.
- Memory readiness requires **3 consecutive** fresh valid reads with clear RoleName and non-None MapID; each sample invalidates cache first. Timeout at 45s is explicitly fail-open so Farm is not permanently wedged.
- No direct unconditional post-reconnect `_ensure_injected` edge is proven in the readable TrainLSV reconnect path. Do not add forced reinjection solely because TCP reconnect occurred.
- TrainLSV state table contains `Mất kết nối → #b71c1c`; the Farm recovery branch explicitly uses `Chờ kết nối lại`. Exact setter ordering for `Mất kết nối` remains UNKNOWN.
- Exact monitor error prefix is `disconnect monitor lỗi: `; exception-to-next-iteration micro-order remains UNKNOWN.
- Only after static extraction, packaged `automove_log.txt` was searched for reconnect/common.active/MemReady markers and exact click coordinates; no correlated top-level reconnect trace was recovered. I08 is **STATIC_VERIFIED / RUNTIME_ENV_REQUIRED**.
- I08 also uncovered a direct frozen-data correction: both disconnect pixel tolerances are **5**, not 0. The earlier H08 task/model/static-evidence artifacts were minimally corrected for consistency; all other H08 reconnect contracts remain unchanged.

## I08 FILES
- docs/tasks/I08.md
- docs/train_lsv/I08_RECONNECT_STATIC_EVIDENCE.tsv
- docs/train_lsv/I08_RECONNECT_FLOW.md
- docs/train_lsv/I08_RECONNECT_MODEL.json

## I08 CROSS-PHASE CORRECTION
- Corrected ordinary Train H08 disconnect-probe tolerance from prior artifact value 0 to the directly decoded frozen value **5** for both `login.ngatKetNoi1` and `login.ngatKetNoi2`.
- Updated:
  - docs/tasks/H08.md
  - docs/train/H08_RECONNECT_MODEL.json
  - docs/train/H08_RECONNECT_STATIC_EVIDENCE.tsv
- This is a narrow evidence correction only; H08 cadence, coordinates, RGB, timeout, 3-strike logic, reconnect batching and recovery semantics were not reopened.

## I09 VERIFIED RESULTS
- Followed PLAN.md/STATE.md exactly and performed the GitHub-first continuity check. No I09 artifacts existed; I01-I08 were already complete and were not repeated.
- Re-materialized/re-hashed the frozen specimen before B06/runtime cross-check. Archive SHA-256 remains `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; inner EXE remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- TrainLSV death/recovery authority remains the decoded `.train_lsv_tab` chunk at file offset `0x2c07798`, encoded size 37904, 1201 constants.
- Return-to-train setting is `respawn_var` / config key `respawn` / label `Quay lại train khi chết`; exact clean config tuple is `('respawn', False)`. Automatic return is OFF by default.
- Exact monitor is `TrainLsvTab._diaphu_monitor`; strongly mapped locals are `self, hwnd, respawn_event, stop_event, detected, hp_latched, click_at, get_character_info, ci, hp_pct, row_d, wait_pixel`.
- Exact monitor documentation says it runs **every 4 seconds from the beginning of Farm**, combining MapID-10000 recovery detection and real HP-zero detection. It explicitly watches during movement/heal and is not armed only after reaching the train spot.
- Real numeric `HpPercent == 0` triggers exact client click **(792,441)** **one time** for that latched zero episode. Unreadable/None HP is not documented as zero.
- Dedicated `hp_latched` plus exact “hồi sinh 1 lần” behavior locks a one-shot zero-HP latch and forbids repeated click spam every 4 seconds. Exact latch-reset statement remains UNKNOWN.
- A new row starts with `Chết: 0` and owns `_extra_deaths`. Exact tuple `('_extra_deaths',0)` sits directly in the HP-zero branch beside the respawn click. Death-counter ownership therefore belongs to the latched HP-zero handling path; repeated zero samples must not continuously increment. Exact reset on Farm restart remains UNKNOWN.
- MapID **10000** is the TrainLSV recovery-hub signal, not ordinary Train MapID 87. Dedicated local `detected`, `respawn_event`, recovery log and event-clear surface establish a second latch around one continuous 10000 episode. Exact `detected` reset / `respawn_event.clear()` statement order remains UNKNOWN.
- TrainLSV's death monitor directly owns `wait_pixel` and exact success text `common.active sau hồi sinh OK`; monitor documentation explicitly says the MapID10000 recovery path waits for active. Shared `common.active` remains point **(1330,33)**, RGB **(34,8,11)**, tolerance **5**.
- Death-monitor-specific active-wait timeout/interval/debug are not independently bound. Do not copy I08's 30-second reconnect timeout or I02's active-wait timeout by analogy.
- Recovery state is exact `Về Lạc Dương LSV`, style `#1565c0`. The full TrainLsvTab constants contain **no** `Đang hồi sinh` and no `Về địa phủ`; ordinary Train H07 state names must not be imported.
- `_farm_cycle` owns `respawn_event` and exact log `đang ở map 10000 → xử lý hồi sinh`, proving the event changes Farm-cycle control rather than being diagnostic only.
- Farm-cycle locals retain selected target `fm/fx/fy`, normal `Tới bãi LSV` state and the already-frozen I02/I03 premove/final-move path. No death-only hard-coded Train LSV coordinate is recovered.
- `respawn_var` is therefore the automatic-return enable switch. When return is enabled, reconstruction must reuse the account's selected I02/I03 Train LSV target path. The exact Farm-worker behavior when `respawn=False` remains EXPLICIT UNKNOWN rather than guessed.
- Treatment remains independent through `trist_var` and the I07 `_heal_at_death` primitive. The same Farm cycle contains the recovery branch plus the exact pre-train marker `% < 50% lúc bắt đầu → trị liệu trước` before `Tới bãi LSV`. Recovery must not invent a separate treatment implementation. Exact inline-death-branch versus next-cycle-top treatment call order remains UNKNOWN.
- Safe recovery sequence is: HP0 one-shot respawn click → observe recovery hub MapID10000 → raise recovery event → wait common.active → Farm cycle leaves normal train work → honor optional I07 treatment → if auto return enabled reuse I02/I03 selected target → resume normal train loop. Exact statement-level ordering inside the recovery branch remains native-control-flow UNKNOWN.
- Monitor stop is controlled by `stop_event`; exact doc says stop does not depend on `respawn_event`, avoiding deadlock on that event.
- I08 arbitration remains separate: once reconnect `halt` is asserted, reconnect recovery takes over. Same-scheduling-window ordering before halt when death and disconnect become visible together remains UNKNOWN.
- Only after static extraction, B06 was re-hashed at `9e3b57671a2ff165ea31264a1c2fb19493f861a7bdadc4dc993a55bd130f5d29`; respawn and treatment checkboxes remain visibly unchecked. No geometry was remeasured.
- Only after static extraction, packaged `automove_log.txt` was searched for HP-monitor, 792/441, HP0, respawn_event, recovery-state and post-respawn-active markers; no correlated top-level death/recovery trace was recovered. I09 remains **STATIC_VERIFIED / RUNTIME_ENV_REQUIRED**.

## I09 FILES
- docs/tasks/I09.md
- docs/train_lsv/I09_DEATH_STATIC_EVIDENCE.tsv
- docs/train_lsv/I09_DEATH_FLOW.md
- docs/train_lsv/I09_DEATH_MODEL.json

## I10 VERIFIED RESULTS
- GitHub-first continuity check passed. I10 did not exist; I01-I09 were already complete and were not redone.
- Frozen archive/EXE hashes remain unchanged.
- TrainLSV uses dynamic coordinate rows with name/map/X/Y plus Train apply and delete. There is no coordinate Sell action.
- _add_coord_row has four None defaults. It contains generated-name prefix "Tọa độ " and current-name awareness; exact generated suffix/start remains UNKNOWN.
- Current TrainLSV map list remains the seven LSV maps already locked by I02.
- TrainLsvTab contains no FarmTab-style map separator handler or ===== literal.
- Coordinates persist in [TrainLSV] under coord_* keys. Save uses coord_id_for_name; unknown map rows are skipped.
- Shared parse_coord_value locks value schema preset_name|map_id|x|y and treats the last three pipe fields as map ID, X, Y. Map ID is normalized to int.
- _load_coords sorts coord keys, parses them, maps MapID back to a current display name and recreates dynamic rows. Retired numeric/legacy map values are skipped rather than guessed.
- Exact first coord numeric suffix and exact sort-lambda source remain UNKNOWN.
- Preset identity is the display name. Rename propagates immediately to all account Train comboboxes and current old-name selections.
- Add/delete also refresh account Train combobox options. Exact selected-value behavior after deleting the active preset remains UNKNOWN.
- No manual duplicate-name rejection surface is recovered; exact duplicate resolver winner remains UNKNOWN.
- _apply_coord_to_all applies the preset name to every account Train combobox.
- Per-account saved selection uses the acc_..._train key family. load_acc_config restores it only when the preset still exists.
- Coordinate edits are save-wired through _auto_save, _on_name_changed and _schedule_save_all_coords. Exact scheduler delay/thread/debounce mechanism remains UNKNOWN.
- _importing/_saving_enabled provide load/save guard surfaces; exact flip order remains UNKNOWN.
- I01 periodic config autosave remains exactly 30 seconds.
- I03 remains authoritative for execution: saved X/Y are tile coordinates and final movement converts by x32.
- B06 hash remains 9e3b57671a2ff165ea31264a1c2fb19493f861a7bdadc4dc993a55bd130f5d29. Coordinate area is visible and empty in that capture; no geometry was remeasured.
- Packaged automove_log contains no correlated coordinate-management trace. I10 is STATIC_VERIFIED / RUNTIME_ENV_REQUIRED for persistence microbehavior.

## I10 FILES
- docs/tasks/I10.md
- docs/train_lsv/I10_COORDS_STATIC_EVIDENCE.tsv
- docs/train_lsv/I10_COORDS_FLOW.md
- docs/train_lsv/I10_COORDS_MODEL.json

## I11 VERIFIED RESULTS
- GitHub-first continuity check passed. No I11 artifacts existed; I01-I10 were already complete and were not redone.
- Re-extracted/re-hashed the frozen specimen first. Archive SHA-256 remains c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd; inner EXE remains 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22.
- TrainLSV all-account/FSM authority remains the decoded .train_lsv_tab chunk at marker 0x2c07798, data 0x2c077ab, size 37904, 1201 constants.
- Exact _checked_rows doc says all accounts in the list; TrainLSV has no row-selection checkbox. Old "checked/tick" naming is stale. Bulk target set is all current account rows.
- Visible B06 bulk commands remain exactly Tới LSV / Tới chỗ train / Đánh / Rời LSV. Each outer UI command dispatches through threading.Thread(..., daemon=True).start().
- Frozen bulk docs independently lock per-account parallelism. _move_lsv_all and _leave_lsv_all explicitly say one account per thread; _move_all/_stop_all/_farm_all say parallel and recovered locals contain rows/_threads/row worker surfaces.
- _move_all has dedicated mv/xv/yv locals, binding per-account selected train preset rather than one global coordinate snapshot. It reuses the already-frozen I02/I03 movement boundary.
- Visible bulk Đánh is NOT full TrainLSV automation. _farm_all calls the per-account manual _farm_acc path; exact _farm_acc doc says StartAutoFight Train by memory/internal path, no click.
- _farm_acc directly guards against overlap with full automatic Farm: if _is_acc_farming(hwnd), it logs that the account is already farming automatically and skips the manual Fight action.
- No equivalent active-Farm skip rule is independently proven for bulk Tới LSV/Tới chỗ train/Rời LSV; keep those conflict rules UNKNOWN instead of importing ordinary Train H13.
- _stop_acc exact doc is "Dừng nhân vật + tắt flag farm cá nhân." It uses shared stop_character and cooperative Farm deactivation rather than asynchronous Python thread killing.
- _farming_acc is the per-account active authority. _farm_threads is the per-account worker registry. Each row owns _gen; _farm_cycle captures gen_snap.
- _check_stop is strongly mapped as self,row,halt,gen_snap,hwnd and exact doc says True means exit immediately. Other TrainLSV worker docs explicitly say generation changes on user stop/start invalidate stale workers.
- Exact row play states are: inactive ▶ / green #388e3c; active serialized ASCII II / red #f44336; stopping _stopping_play with … / orange #ef6c00. _refresh_play_buttons skips _stopping_play rows so refresh cannot prematurely restore ▶.
- _toggle_single_farm exact doc locks individual start/stop and says stopping the last active account transitions into the same global-stop workflow.
- Stop-side constants appear before the start permission guard. Start-side Farm creation is guarded by has_permission_with_limit with trainlsv_tab/trainlsv surfaces; denied start logs the license denial. A separate global-wrapper permission precheck remains UNKNOWN.
- Starting an account directly references _farm_cycle and _resize_monitor. The resize monitor independently polls each second and only resizes when the owned window differs from 1366x768.
- Global _toggle_farm exact doc is idempotent/incremental: START only accounts not already farming; STOP only accounts currently farming. Exact no-row/all-running/no-active/start/stop logs are recovered.
- Stable large-button states are stopped Bắt đầu / #388e3c / normal and running Dừng lại / #f44336.
- _wait_farm_stop directly owns join and locals self,threads,has_remaining,wt. Exact doc says it waits for worker exit after current sub-cycle: has_remaining=True removes stopped workers while others continue; has_remaining=False resets the large button to Bắt đầu.
- Exact partial-stop log is "Dừng xong phần acc được chọn — các acc còn lại tiếp tục"; full-stop log is "Đã dừng hoàn toàn".
- Exact join timeout/micro-order remains UNKNOWN.
- A separate no-window stale cleanup path is exact: if no game windows remain while Farm is active, TrainLSV auto-stops and sets large button Đang dừng... / #ef6c00 / disabled, syncs StartTab, then waits/drains workers. Do not generalize this orange state to every normal user stop.
- _sync_start_tab_btn exact doc says the local Bắt đầu caption maps to StartTab Train LSV and that Farm state changes keep both buttons synchronized. Frozen StartTab independently routes _toggle_train_lsv_cmd into the same TrainLsvTab engine.
- Exact _farm_cycle doc is move to Train LSV point -> farm -> repeat, keeping only map movement + fight and explicitly excluding ordinary Train sell/medicine/return-town cycle.
- Only after static extraction, B06 was re-hashed at 9e3b57671a2ff165ea31264a1c2fb19493f861a7bdadc4dc993a55bd130f5d29 and visually confirms the four bulk commands and bottom Bắt đầu.
- Packaged automove_log contains zero correlated top-level TrainLSV/FSM markers. Generic runtime primitives remain AutoFight_Main=8511, AutoMove queued=16040, StartAutoPath called=15993, StopAutoPath called=2027; these prove only shared primitive execution.
- I11 classification is STATIC_VERIFIED / RUNTIME_ENV_REQUIRED.

## I11 FILES
- docs/tasks/I11.md
- docs/train_lsv/I11_ALL_FSM_STATIC_EVIDENCE.tsv
- docs/train_lsv/I11_ALL_FSM_FLOW.md
- docs/train_lsv/I11_ALL_FSM_MODEL.json

## I12 VERIFIED RESULTS
- GitHub-first continuity check passed. No I12 artifacts existed; I01-I11 were already complete and were not redone.
- Re-materialized/re-hashed the frozen specimen before final parity classification. Archive SHA-256 remains `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; inner `TLMTool.dist/TLMTool.exe` remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, size 47,450,112 bytes.
- TrainLSV marker remains `.train_lsv_tab` at `0x2c07798`. B06 remains `9e3b57671a2ff165ea31264a1c2fb19493f861a7bdadc4dc993a55bd130f5d29`.
- Re-inspected all **44** existing Phase-I artifacts before matrix construction: 11 task docs, 11 flow docs, 11 model JSON files and 11 static-evidence TSV files. No contradiction required reopening I01-I11.
- Packaged runtime helper log remains exact SHA-256 `17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`, size 15,741,058 bytes, 387,238 lines.
- Existing runtime primitive counts were re-derived line-by-line from the exact frozen log: AutoMove queued **16,040** / 87 PID-tagged processes; StartAutoPath **15,993** / 85; StopAutoPath **2,027** / 12; AutoFight_Main **8,511** / 91; mount-toggle Lua primitive **1,579** / 28; ItemAction spts action=4 **22,732** / 49; raw action=4 **22,734**; action=3 **206** / 8.
- The packaged helper log contains **0 correlated top-level TrainLSV traces** for TrainLSV navigation/FSM, Dạ Minh/Buff, Nhặt đồ/filter state, treatment, reconnect, HP monitor/recovery and coordinate-management markers. Absence is not evidence the feature never ran.
- Runtime evidence scope remains strict: generic movement/fight/action4 records prove only the low-level primitive directly logged, never the top-level TrainLSV caller/button/Farm generation.
- Final parity matrix contains **80 rows**:
  - **24 STATIC_VERIFIED**
  - **3 RUNTIME_VERIFIED_FROM_EXISTING_EVIDENCE**
  - **53 RUNTIME_ENV_REQUIRED**
  - **0 BLOCKED**.
- The 3 existing-runtime rows are deliberately limited to shared movement/AutoPath primitive execution, action-4 discard primitive execution and AutoFight primitive execution.
- All unresolved I02-I11 micro-details were preserved as runtime-environment-required instead of guessed. Major deferred edges include LSV transition timing, leave wait flag/pacing, schedule deadline/zero interval behavior, numeric FULL_BAG_THRESHOLD, treatment pacing/cancel checkpoints, reconnect live timing/reinjection, death latch/reset/respawn-false behavior, coordinate duplicate/delete/save timing, and all-account thread/join/generation race details.
- Built an explicit Windows + live-game runtime test plan with **53 scenarios** covering I02-I11: entry/floors/flat maps, final point, leave, Dạ Minh schedule, bag threshold/keep modes, treatment, reconnect, death recovery, coordinate persistence, bulk commands, start/stop, generation safety, StartTab mirroring and 3+ account stress.
- Runtime verdict vocabulary is fixed as `PASS_ORIGINAL_CONTRACT`, `FAIL_CONTRADICTS_STATIC_CONTRACT`, or `UNVERIFIED_ENV_NOT_AVAILABLE`. An unexecuted scenario is never PASS.
- B06 was visually cross-checked only after static evidence and remains consistent with the locked stopped/default TrainLSV UI. No geometry was remeasured.
- Gate I decision is now **CLOSED_FOR_STATIC_VISUAL_RESEARCH_HANDOFF / END_TO_END_RUNTIME_PARITY_DEFERRED**.
- Gate I closure means the static/visual contracts are sufficient for later reconstruction handoff and Phase-J research may begin. It does **not** claim original Windows/live-game end-to-end TrainLSV parity has been executed.
- Any later original-runtime contradiction must update only the narrow affected contract with captured evidence; do not silently reopen or rewrite unrelated I01-I11 findings.

## I12 FILES
- docs/tasks/I12.md
- docs/train_lsv/I12_EXISTING_RUNTIME_EVIDENCE.tsv
- docs/train_lsv/I12_RUNTIME_PARITY_MATRIX.tsv
- docs/train_lsv/I12_RUNTIME_PARITY_REPORT.md
- docs/train_lsv/I12_RUNTIME_TEST_PLAN.json
- docs/train_lsv/I12_GATE_I.md

## GATE I
**CLOSED_FOR_STATIC_VISUAL_RESEARCH_HANDOFF / END_TO_END_RUNTIME_PARITY_DEFERRED**

## J01 VERIFIED RESULTS
- GitHub-first continuity check passed. No J01 artifacts existed; Gate I was already complete and was not reopened.
- Re-extracted/re-hashed the frozen original before using B07. Archive SHA-256 remains `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; inner EXE remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Active Phó Bản authority is frozen module `.phoban_tab` / `phoban_tab.py`, class `PhoBanTab`; marker offset `0x2b86f63`, encoded chunk size **52957**, **1508** top-level constants. Related dungeon-handler module `phoban_dungeons.py` is present but J01 did not audit dungeon handlers.
- Constructor/UI party-formation surfaces are native to `PhoBanTab`: `_member_rows`, `recreate_team_var`, `_group_vars`, `_pending_group`, `_groups`, `_group_counter`, run-lock/job surfaces.
- Ready accounts are refreshed incrementally every **5 seconds** from `start_tab.get_windows`; slow window/character reads happen in a background worker and UI apply happens on the main thread.
- Ready-member identity is HWND + current PID. Closed windows and HWND process reuse remove the old member row.
- Exact ready-list doc says selected accounts are hidden from the ready grid; ready grid layout is 3 accounts/row.
- Each group built by `_add_group_cluster` contains exactly **6 account comboboxes**. B07 confirms 2 rows × 3.
- Exact leader-label rule: the **first combobox is the nominal leader**; blank first slot displays `(chưa chọn)`.
- `_refresh_group_combo_values` enforces cross-group uniqueness in the normal UI: an account chosen by an earlier group disappears from later-group dropdown choices; a still-valid current selection is preserved; a dead/stale selection resets.
- `_on_group_selected` immediately refreshes other combobox values and enters the config-save path.
- Group combobox permission scope is `phoban_tab`; enabled state is `readonly`, denied state disabled.
- `Tạo lại đội` uses `recreate_team_var`; exact clean config fallback is `phoban_recreate_team=0`. B07 shows it unchecked. Party recreation is therefore opt-in.
- Exact `_run_one_group` doc places team recreation **before** schedule setup when enabled. If `_pb_ensure_party` fails, that group stops and its schedule does not proceed.
- Current formation targets are selected **and currently online** group members: `[(name, hwnd)]`.
- `_pb_resolve_targets` resolves RoleID using live `read_own_ids + hwnd_of_pid`, exact-name then case-insensitive matching. One unresolved member is skipped/logged; zero resolvable RoleIDs aborts the group.
- TeamID no-team integer sentinels are exactly `{0,-1,4294967295}`; textual no-team forms include `0/false/empty`. `None`/read failure is not accepted as successful team state.
- Party recreation effective leader rule is exact: first combobox account if online; if that nominal leader is offline, **first online target becomes the creation leader**. If only one online account remains, no team creation is needed and the group can continue.
- Recreate pipeline is exact at architecture level: **B0 auto-accept → B1 leave existing team → B2 leader UI create → B3 burst invite**.
- B0 targets `UTILITIES.AutoAcceptInviteTeam=True` and verifies readback where possible. Exact low-level writer and numeric `PB_PARTY_AUTOSET_DELAY` remain UNKNOWN.
- B1 skips `leave_team` for members already outside a team, sends leave for others, then waits for no-team state. If all-leave confirmation times out, exact behavior is warning + **still continue** rather than hard abort.
- B2 `_pb_click_create_team` has leader-window 1366×768 resize surface and exact UI click sequence:
  - pixel `donVang.nguoiChoiGan` present → click **(391,683)**; absent → skip/log.
  - pixel `donVang.muiTenAnNhiemVu` present → click **(34,462)**; absent → skip/log.
  - then tail clicks **(27,467) → (154,214) → (127,336)**.
  Exact documentation says **every click is 1 second apart**.
- B2 `_pb_invite_create` retries creation symbolically by `PB_PARTY_CREATE_RETRY`, waiting for a **real TeamID** each attempt. Exhausted creation retries hard-abort that group.
- B3 `_pb_invite_burst` sends a burst to all resolved non-leader members, waits once for same-TeamID, resends only missing members once, then waits one more time.
- Crucial frozen behavior: after the second wait, `_pb_invite_burst` returns success **even if some members are still missing**, unless cancelled; missing list/team snapshot are logged. Do not reconstruct an all-members-must-join hard abort at this layer.
- Party sleeps/waits are cooperative through `_pb_party_cancelled` + `_pb_party_sleep`; group or global cancel can interrupt formation.
- Symbolic PB_PARTY timing/retry globals are verified, but J01 does not safely bind their numeric values: TEAMID_POLL, CREATE_RETRY, WAIT_TEAM_TIMEOUT, INVITE_RETRY_GAP, JOIN_POLL, BURST_DELAY, JOIN_TIMEOUT, AUTOSET_DELAY, LEAVE_DELAY, WAIT_LEFT_TIMEOUT.
- Only after static extraction, B07 was re-hashed at `8b62070b04231f762dc080f4432cbc178f020ae0614540dc0e9c293d16987fb8`, 452×1032 RGBA. It confirms recreate unchecked, one visible group, leader `(chưa chọn)`, six blank slots and add/delete-group controls. No geometry was remeasured.
- Only after static extraction, packaged `automove_log.txt` was searched. No correlated team-recreation markers were found for AutoAcceptInviteTeam/CreateTeam/leave_team/invite/TeamID/C_TeamAction/Tạo đội/mời đội/Phó Bản. The 87 literal RoleID lines sampled are unrelated private-chat packet scripts. J01 is **STATIC_VERIFIED / RUNTIME_ENV_REQUIRED** for actual game-party recreation.

## J01 FILES
- docs/tasks/J01.md
- docs/phoban/J01_PARTY_FORMATION_STATIC_EVIDENCE.tsv
- docs/phoban/J01_PARTY_FORMATION_FLOW.md
- docs/phoban/J01_PARTY_FORMATION_MODEL.json

## J02 VERIFIED RESULTS
- GitHub-first continuity check passed. No J02 artifacts existed; J01 was already complete and was not redone.
- Re-materialized/re-hashed the frozen specimen before B07. Archive SHA-256 remains `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; inner EXE remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Re-parsed both active Phase-J constant chunks directly:
  - `.phoban_tab` marker `0x2b86f63`, size **52957**, **1508** constants.
  - `.phoban_dungeons` marker `0x2b8513b`, size **7700**, **249** constants.
- Visible/nominal leader identity remains exact: **first group combobox**. If it is blank the leader label is `(chưa chọn)`.
- The live group-combo refresh only retains still-valid selections; a stale/dead account selection resets. Therefore a stale first-slot leader is not preserved indefinitely as the UI leader.
- `_group_targets` is the current execution roster: selected + currently-online unique account names resolved to HWNDs in group-slot iteration order. Strong local model is `self/gd/hwnd_by_name/hwnd/entry/seen/out/var/nm`.
- `_run_one_group` owns explicit runtime locals `_leader_hw` and `_idx` in the per-account worker-construction region, plus current `targets`, `_nm`, `_hw`, `threads`.
- Exact Python source expression assigning `_leader_hw` is not stored in the Nuitka constants blob. The strongest static model is that one current online target is captured as the run leader and each current target is indexed for worker metadata. The literal `_leader_hw = ...` and exact Boolean expression for `is_leader` remain **STRONG_STATIC / EXPLICIT UNKNOWN**, not guessed source.
- `_acc_step_worker` directly carries `is_leader`, `member_index`, `total_members`; its local model includes all three.
- The worker's Phó Bản call surface to `_do_dungeon` has exact keyword tuple `stop_check, barrier, cancel, acc_name, is_leader, member_index, total_members`, proving that leader/member metadata is operational and not only UI text.
- Adjacent frozen default surface for `_do_dungeon` is `(None,None,None,'',False,0,1)`; adjacent worker defaults include `False,0,1`. Exact leader metadata defaults are therefore **is_leader=False / member_index=0 / total_members=1**.
- `_do_dungeon` strongly maps `is_leader/member_index/total_members` into `_ctx` / dungeon-handler execution.
- `DungeonCtx` exact field order is `tab, hwnd, acc_name, dungeon, is_leader, member_index, total_members, mid, post, stop_check, cancel, barrier, run_idx, times`.
- Exact `DungeonCtx` defaults are `(None,0,'','',False,0,1,None,None,None,None,None,0,1)`.
- Crucial architecture finding: **PhoBanTab does not read the in-game team leader**. The full `.phoban_tab` chunk has no `read_team_leader`, `TeamLeader`, `LeaderID`, `leader_id`, `is_team_leader`, `captain`; `.phoban_dungeons` has the same absence.
- The frozen EXE does contain a shared `memory_items.read_team_leader` elsewhere, but the active Phó Bản chunks do not reference it. `read_team_id` is present only for J01 party-state verification.
- Therefore Phó Bản's `is_leader` is a **tool-side group/run metadata concept**, not a live game-captain memory query.
- This remains true when `Tạo lại đội` is OFF: the J01 B0/B1/B2/B3 recreation stage is skipped, but `_run_one_group` / `_acc_step_worker` still carry leader/member metadata. Do not add a `read_team_leader` prerequisite.
- J01's team-creation leader and J02's run-local leader are separate concepts. J01 proves nominal first-slot leader with first-online fallback when recreating a team. J02 proves a run-local `_leader_hw` exists over the current online roster. Their normal alignment is strongly supported, but the exact native assignment/equivalence is not instruction-bound by constants alone.
- Common dungeon configuration is symmetric for participants: `SelectedFuBen`, `AutoRepeat=False`, `FollowLeader=True`, `AutoRevive=True`. `FUBEN.FollowLeader=True` is a game auto-FuBen setting and must not be conflated with PhoBanTab's Boolean `is_leader`.
- `BaseDungeon` hooks are pass-through/default; no leader-only behavior is recovered.
- The only custom current dungeon class recovered is `SatTinhDungeon`. Its exact docs state **"mọi acc giống nhau"** and explicitly say future versions can branch on `ctx.is_leader / ctx.member_index / ctx.acc_name`. Thus current Sát Tinh does **not** have a leader-specific branch.
- J02 records only the leader source boundary needed for J03: the follow-worker doc explicitly says it uses the **first combobox of the running group** as leader-position source. Follow polling/movement logic remains deferred.
- No recovered run path verifies that the worker marked `is_leader` is actually the current game captain immediately before dungeon hooks. Do not add such a gate without original-runtime evidence.
- Only after static extraction, B07 was re-hashed at `8b62070b04231f762dc080f4432cbc178f020ae0614540dc0e9c293d16987fb8`, 452×1032 RGBA. It remains consistent with blank first slot and leader `(chưa chọn)`; no geometry was remeasured.
- Only after static extraction, packaged `automove_log.txt` was checked. It contains 0 lines for `is_leader`, `member_index`, `Đội trưởng`, `leader`, `PhoBanTab`, `[Phó bản]`, and `Sát Tinh`. J02 is **STATIC_VERIFIED / RUNTIME_ENV_REQUIRED** for the exact run-local leader assignment/offline race behavior.

## J02 FILES
- docs/tasks/J02.md
- docs/phoban/J02_LEADER_STATIC_EVIDENCE.tsv
- docs/phoban/J02_LEADER_FLOW.md
- docs/phoban/J02_LEADER_MODEL.json

## J03 VERIFIED RESULTS
- GitHub-first continuity check passed. No J03 artifacts existed; J01-J02 were already complete and were not redone.
- Rechecked/re-hashed the frozen TLMTool 2.1.2 specimen before B07/runtime evidence. Archive SHA-256 remains `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; inner EXE remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Active follower authority remains frozen `.phoban_tab` at `0x2b86f63`, size **52957**, **1508** constants. Shared movement-clash helper authority was independently checked in frozen `.utils` at `0x2c4c962`, size **32300**, **862** constants.
- The actual constructor field is **`follow_var`** (not a separate `follow_leader_var` symbol), with `_follow_stop`, `_follow_thread`, `_follow_gen`.
- Visible option is exact `Theo sau đội trưởng`; callback `_toggle_follow`; config key `phoban_follow`; exact clean fallback is `('phoban_follow','0')`. Follow is opt-in and OFF by default.
- Exact toggle doc: ON + any group already running -> start follower worker immediately; ON + no run -> keep option ON and wait; later run start creates worker; OFF -> stop worker immediately; worker rechecks the tick each cycle; config is saved.
- Exact group filters: `_group_is_running(gd)` is true only when the group's run cancel exists and is not set; `_any_group_running()` is true while any group runs. Idle configured groups are skipped entirely by follow (no leader/member reads, no follow moves).
- Worker lifecycle is generation-safe: constructor owns `_follow_stop/_follow_thread/_follow_gen`; `_start_follow` references `_follow_worker`, existing-thread `is_alive` guard and Thread keyword surface `target/args/daemon`; worker receives `gen`. Exact doc says generation prevents two workers overlapping and worker exits when no groups remain running. Exact `_follow_gen` mutation statements and daemon Boolean remain UNKNOWN.
- Follow leader source is exact: **first combobox of each running group**. This matches J02 nominal leader source; no `read_team_leader` memory query is introduced.
- The follow block contains exact `slice(1,None,None)`, binding the normal follower slice to group member slots after the first/leader slot. Leader is not commanded to follow itself.
- Position reads are memory-based via exact imports `get_character_info` + `move_character`. Nested `_pos` reads exact fields `MapID`, `PosX`, `PosY`. Constants **32.0** and **0.5** are in the follow position/distance block, but the exact native arithmetic formula is not recoverable from constants alone and remains UNKNOWN.
- Exact map rule: follow works only inside `DUNGEON_MAP_IDS`. If the leader leaves the dungeon-map set, the group stops following and old position/command cache is cleared; when the leader comes back into a dungeon map, follow resumes without stale safety-cache blocking the first new tick.
- Exact exception: **Sát Tinh map 111 never follows**, even with checkbox enabled. Frozen doc says the accounts anchor at 65,85 and following would break that position.
- Same-map gate is exact: a follower is considered only when on the same MapID as the leader. Another-map members are not dragged by this worker.
- Two distinct symbolic thresholds are verified:
  - `PB_FOLLOW_DIST_TILES`: minimum leader/follower distance before queueing follow movement.
  - `PB_FOLLOW_MOVE_TILES`: safety threshold for detecting significant follower self/foreign movement between polls.
  - `PB_FOLLOW_POLL`: periodic worker interval.
  Their numeric values are **not safely bound** to names from the serialized constant table and remain explicit UNKNOWN.
- Command-clash safety rule is exact at semantic level: if a follower moves more than `PB_FOLLOW_MOVE_TILES` tiles in one poll and that movement was not caused by follow's previous poll, skip that follower for this poll. Frozen doc explicitly identifies run-move/combat as the competing-command case.
- Worker owns exact caches `last_pos`, `commanded`, `commanded_now`. Exact wording `không phải do follow ra lệnh poll trước` locks prior-follow-command exemption, so follow-caused movement is not misclassified as foreign movement on the next cycle. Exact set/dict mutation order remains UNKNOWN.
- Follow also directly calls shared `is_move_poll_active` before queueing movement. Frozen shared utils doc says it returns True while a `move_character` **wait_for_arrival** poll is actively steering the HWND, specifically so Follow does not steal that movement command.
- Shared `_MOVE_POLL_TTL` is exactly **0.5 seconds**.
- Follow movement uses shared `move_character` with explicit keyword surface `wait_for_arrival, stop_check, follow_mode`.
- Shared `move_character` defaults are directly frozen as `(False,None,None,False,48)` = wait_for_arrival=False, stop_check=None, home_priority=None, follow_mode=False, tolerance=48.
- Follow's exact documentation says `follow_mode` **only queues AutoPath**: no Phù, no stop game auto, no mount toggle, so current auto FuBen remains active. Combined with the explicit caller keywords, the effective follow semantics are **wait_for_arrival=False / follow_mode=True**. Exact Python callable supplied as `stop_check` remains UNKNOWN but belongs to the follow worker/session lifecycle.
- The follow worker is periodic, not one-shot: every `PB_FOLLOW_POLL` cycle it re-evaluates checkbox/generation, running groups, leader/follower positions, allowed maps, same-map, movement-distance/clash guards and current leader position before optionally queueing a new follow move.
- Group-run completion does **not** clear the saved follow checkbox. Worker exits when no group runs, while the persisted mode may remain ON; a later run can create it again.
- Exact per-member/outer error surfaces include `bám lỗi:` and `[Phó bản] follow lỗi:`. No frozen contract says one follow exception hard-aborts the whole schedule.
- Only after static extraction, B07 was re-hashed at `8b62070b04231f762dc080f4432cbc178f020ae0614540dc0e9c293d16987fb8`, 452×1032 RGBA. Existing B07 visible-state evidence records `follow_leader=false`; no geometry was remeasured.
- Only after static extraction, exact packaged `automove_log.txt` (SHA-256 `17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`) was searched. It contains 0 correlated lines for follow labels/actions/errors/`follow_mode`/`is_move_poll_active`. Generic primitive lines remain AutoMove queued **16040**, StartAutoPath **15993**, StopAutoPath **2027**, and are primitive-only evidence, not PhoBanTab-follow causation.
- J03 classification is **STATIC_VERIFIED / RUNTIME_ENV_REQUIRED** for numeric PB_FOLLOW values, exact cache/generation micro-order and live movement-command race behavior.

## J03 FILES
- docs/tasks/J03.md
- docs/phoban/J03_FOLLOWER_STATIC_EVIDENCE.tsv
- docs/phoban/J03_FOLLOWER_FLOW.md
- docs/phoban/J03_FOLLOWER_MODEL.json


## J04 VERIFIED RESULTS
- GitHub-first continuity check passed. No J04 artifacts existed before this turn; J01-J03 were already complete and were not redone.
- Re-inspected the exact user-supplied frozen TLMTool 2.1.2 specimen before using the screenshot. Archive SHA-256 remains `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; inner `TLMTool.dist/TLMTool.exe` remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, size 47,450,112 bytes.
- Active schedule authority remains frozen `.phoban_tab` at marker `0x2b86f63`, encoded chunk size **52,957** bytes, **1,508** top-level constants.
- The continuation-note names `_group_schedule` and `_set_schedule_progress` do **not** exist in the exact frozen EXE (0 raw hits each). The actual frozen surfaces are `_schedule_rows`, `_add_schedule_row`, `_remove_schedule_row`, `_all_schedule_rows`, `get_schedule_rows`, `get_groups_data`, `get_selected_schedule`, `set_progress`, `reset_all_progress`, `_reset_group_progress`, `_set_row_progress`, `_collect_group_job` and `_run_one_group`.
- Per-group schedule columns are exactly **Hoạt động / Tên Map / Lần / Status / Xóa**. Group controls include **+ Thêm Lịch trình / Tắt auto PB / Bắt đầu lịch trình**. The group header checkbox toggles only rows of that group; the old global `_toggle_all_schedule` surface is retained only for compatibility and is documented as no longer used.
- Exact serialized defaults for `_add_schedule_row` decode to `(True, None, None, 1, None)`; local argument order binds the reconstruction model to `_add_schedule_row(self, enabled=True, activity=None, name=None, times=1, rows=None)`. `rows=None` means the last/current target group.
- Supported activity types are exactly **Phó bản** and **Train**. `_map_names_for_activity` maps them to `PHOBAN_MAP_LIST` and `TRAIN_MAP_LIST`; the frozen Train display value includes **Về train theo thiết lập sẵn**. Activity changes replace the Tên Map choice list, reset an invalid current name and preserve the Lần value.
- Row business/persistence fields are exactly **enabled / activity / name / times**. Activity/name/times writes are wired into the row autosave path. Live rows additionally carry frame/widget/progress references.
- Canonical progress styles are exact: `chưa -> Chưa/#808080`, `đang -> Đang/#b8860b`, `xong -> Xong/#1b5e20`. `set_progress` accepts a row dict or a widget belonging to the row and matches the three states case-insensitively. `_set_row_progress` is the worker-to-main-thread UI bridge.
- Static nuance preserved: row construction contains an initial **Chưa/#555555**, while the canonical `chưa` style is **Chưa/#808080**. Whether the creation state is immediately normalized is not proven and remains explicit UNKNOWN.
- `get_schedule_rows` is the legacy flat all-groups compatibility surface. `get_groups_data` is the modern per-group config surface with exact documented shape `[{'num': n, 'members': [...], 'schedule': [...]}, ...]`. `get_selected_schedule` returns checked rows as `[{activity, name, times, row}]`, preserving current row/UI order.
- `_collect_group_job` returns `(num, targets, sched)` and returns None when there are no currently-online selected targets or no enabled schedule rows.
- Persistence is modern + legacy compatible. Modern key is `phoban_groups`; legacy keys are `phoban_group1` and `phoban_schedule`. Missing legacy `enabled` defaults True and missing `times` defaults 1. Old legacy activity **Bán đồ** is explicitly skipped because that activity was removed. The save path still references all three compatibility keys and uses JSON with `ensure_ascii=False`.
- Exact J04 execution architecture is now frozen: **groups run in parallel; rows inside one group run sequentially; accounts inside one row run in parallel**. In one group, optional J01 team recreation runs first, then target-account setup runs in parallel and joins, then each schedule row is marked `đang`, receives a per-step `Barrier`, launches one `_acc_step_worker` per target, joins that batch and on the normal path marks the row `xong` before advancing.
- `_acc_step_worker` executes exactly one schedule step for one account and dispatches by activity: **Phó bản -> `_do_dungeon`**, **Train -> `_do_train`**. Dungeon-list internals remain J05, exact `times`/run-count semantics remain J06, and deep cancel/abort/failure/status-machine behavior remains J07.
- Only after static extraction, the user-provided Phó Bản screenshot was cross-checked. It is byte-identical to locked B07: SHA-256 `8b62070b04231f762dc080f4432cbc178f020ae0614540dc0e9c293d16987fb8`, 452x1032 RGBA. It visually confirms the six member slots, schedule headers and group controls; no geometry was remeasured.
- Only after static extraction, packaged `data/automove_log.txt` was searched. No correlated top-level Phó Bản schedule/group-step/completion markers were recovered. J04 is therefore **STATIC_VERIFIED / RUNTIME_ENV_REQUIRED** for live ordering/cancel races.

## J04 FILES
- docs/tasks/J04.md
- docs/phoban/J04_SCHEDULE_FLOW.md
- docs/phoban/J04_SCHEDULE_MODEL.json
- docs/phoban/J04_SCHEDULE_STATIC_EVIDENCE.tsv


## J05 VERIFIED RESULTS
- GitHub-first continuity check passed. No J05 artifacts or completion commit existed before this turn; J01-J04 were already complete and were not redone.
- Re-inspected the exact uploaded TLMTool 2.1.2 archive first. Archive SHA-256 remains `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; inner `TLMTool.dist/TLMTool.exe` remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, size **47,450,112** bytes.
- Active frozen serialized module markers remain `.phoban_dungeons` at `0x2b8513b` and `.phoban_tab` at `0x2b86f63`.
- The exact visible `PHOBAN_MAP_LIST` is a length-8 list, in order: **Tô Châu  - Thủy Lao / Tô Châu 1 - Tống Liêu / Tô Châu 2 - Trúc Lâm / Tô Châu 3 - Dã Ngoại / Lâu Lan 1 - Hoàng Kim / Lâu Lan 2 - Huyền Phật Châu / Lâu Lan 3 - Dung Nham / Sát Tinh - Thử nghiệm**. The first name contains two spaces before the hyphen.
- Plain **Sát Tinh** is not a ninth visible dropdown item. It is a compatibility/alias key used in the frozen binding tables and handler registry.
- Exact `DUNGEON_FUBEN_CODE`: Thủy Lao→`ThuyLao`; Tô Châu 1/2/3→`Q1_ToChau/Q2_ToChau/Q3_ToChau`; Lâu Lan 1/2/3→`Q1_LauLan/Q2_LauLan/Q3_LauLan`; both Sát Tinh aliases→`SatTinh`.
- Exact `DUNGEON_MAP_IDS`: **92,93,94,95,108,109,110,111,111** for the same nine-key alias order. This independently agrees with J03's map-111 Sát Tinh follow exclusion.
- Exact support table `DUNGEON_CLICK_POS` was also decoded: (540,246), (515,273), (498,301), (493,328), (502,296), (488,323), (498,350), (0,0), (0,0) in that same nine-key order. This is preserved as cross-table canonical-name evidence; movement execution was not reopened.
- Frozen `.phoban_dungeons` contains `DungeonCtx`, `BaseDungeon`, `SatTinhDungeon`, `DUNGEON_HANDLERS`, `get_dungeon_handler` and `_call_hook`. No other custom `*Dungeon` class exists in that exact module.
- BaseDungeon exposes the common hook contract: `pre_config/post_config/pre_move/post_move/pre_start_fuben/post_start_fuben/on_entered/post_cycle`.
- Exact module documentation says an unregistered dungeon falls back to **BaseDungeon common flow**, and a new custom dungeon is added as a class plus one line in `DUNGEON_HANDLERS`.
- The only current custom handler is **SatTinhDungeon**. Exact recovered custom hook surfaces are `on_entered` and `post_cycle`, with helper/session methods `_stop_session/_run/_halted/_loop_revive/_move_to_center/_train_once`.
- Exact handler aliases immediately before `get_dungeon_handler` are **Sát Tinh - Thử nghiệm** and **Sát Tinh**. Combined with the single custom class and the matching FuBen/MapID aliases, the semantic binding is locked: both aliases resolve to **SatTinhDungeon**. Exact class-object-versus-instance storage form inside the registry remains a micro-detail UNKNOWN.
- J04 row binding is now explicit: `activity == "Phó bản"` passes `row.name` into `_do_dungeon`; the same canonical name feeds `get_dungeon_handler(dungeon)` and `DUNGEON_FUBEN_CODE[dungeon]`. Custom handlers decorate the shared flow rather than replacing the scheduler.
- Handler hook integration around the common flow is statically recovered as pre_config → common config → post_config → pre_move → common move/barrier → post_move → pre_start_fuben → common start-FuBen → post_start_fuben → common dungeon-cycle wait → post_cycle. J06/J07 boundaries remain deferred.
- Only after static extraction, the user Phó Bản screenshot was re-hashed at `8b62070b04231f762dc080f4432cbc178f020ae0614540dc0e9c293d16987fb8`, 452×1032 RGBA. It confirms the Tên Map column but has no expanded schedule-row dropdown; exact dungeon names therefore come from the frozen EXE, not the screenshot.
- Only after static extraction, packaged `data/automove_log.txt` was searched. No correlated Sát Tinh/SatTinh/SelectedFuBen/FuBen/ThuyLao/Q*_ToChau/Q*_LauLan/DUNGEON_HANDLERS traces were recovered. J05 is **STATIC_VERIFIED / RUNTIME_ENV_REQUIRED** for live dispatch/FuBen application.

## J05 FILES
- docs/tasks/J05.md
- docs/phoban/J05_DUNGEON_BINDING_FLOW.md
- docs/phoban/J05_DUNGEON_BINDING_MODEL.json
- docs/phoban/J05_DUNGEON_BINDING_STATIC_EVIDENCE.tsv


## J06 VERIFIED RESULTS
- GitHub-first continuity check passed. No J06 artifacts/completion commit existed before this turn; J01-J05 were already complete and were not redone.
- Re-inspected the exact uploaded TLMTool 2.1.2 archive first. Archive SHA-256 remains `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; inner `TLMTool.dist/TLMTool.exe` remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, size **47,450,112** bytes.
- The current schedule `Lần` control is a real **Entry**, not a fixed-choice Combobox. The old local remains named `cb_times`, but the exact widget class in the frozen EXE is `Entry`. No readonly values-list/Spinbox/validation surface is present for that field.
- Exact `_add_schedule_row` serialized defaults are `(True, None, None, 1, None)`, so a new row's `times` default is **1**. The row-construction block also carries literal fallback `"1"` plus `ValueError/TypeError`, giving strong static evidence that invalid seeded/load-time numeric conversion falls back to 1.
- Exact handling/clamping of a manually-entered **0**, negative value, or invalid nonnumeric text immediately before Start is not source-bound by the printable constants and remains explicit UNKNOWN rather than guessed.
- Legacy schedule load also defaults a missing `times` field to **1**.
- The frozen `TIMES_CLICK_POS` table was decoded exactly: `"1"→(337,241), "2"→(336,266), "3"→(341,291), "4"→(337,317), "5"→(337,340)`. This table does **not** make the current schedule Lần field a 1–5 dropdown: the current UI is a free Entry and the current dungeon path does not use game RepeatCount.
- Exact activity-change documentation says the Lần value is preserved when switching activity. That is a UI/config rule only.
- Critical execution asymmetry is now locked. A **Phó bản** row passes `times` into the dungeon execution path. A **Train** row calls `_do_train` with only its normal stop/control surface; the frozen Train doc says it switches to Train and activates that account once. Therefore the Lần field is **ignored by Train execution** and Train runs once regardless of the preserved displayed count.
- Dungeon repetition is tool-side/manual. `_config_dungeon_memory` sets `SelectedFuBen`, `AutoRepeat=False`, `FollowLeader=True`, `AutoRevive=True`, and explicitly says **do not modify RepeatCount**. The exact `_do_dungeon` doc says the Phó Bản activity repeats `times` times.
- Memory dungeon configuration is re-applied on **every requested repetition**, with no first-run/s later-run split. The memory write helper independently retries up to **5 times**, **2 seconds** apart; those are write retries, not schedule repetitions.
- The per-repetition common flow is statically locked as config/hooks → move to meeting/NPC point → shared barrier → FuBen-start retry → dungeon cycle → shared barrier before the next repetition. Move logging shows total attempt notation `/3`, matching initial movement plus up to two retries.
- J04 creates **one Barrier per schedule row**. J06 confirms `_do_dungeon` receives/reuses that same barrier across requested repetitions. It is not recreated per run. The barrier helper itself has no timeout; broken/aborted barrier outcomes remain J07.
- The FuBen-start retry is internal to one dungeon repetition, not the user's schedule count. Frozen docs bind the current fast retry model to **5 × 0.3s**, with MapID fast-pass from retry #2 onward if another account already pulled the party into the target map.
- One completed dungeon cycle is based on map transition: target `MapID` entered, then later a **non-None** different MapID observed. Temporary `None` during map loading is ignored and does not count as exit.
- `DungeonCtx` has exact fields `run_idx` and `times`. The `_do_dungeon` outer local model owns `run`, and its nested context builder takes `run_idx`, proving per-run context plus total-count context for custom handlers.
- Exact first `run_idx` value (0-based vs 1-based) is not observable in the current handler/runtime evidence and remains explicit UNKNOWN.
- The generic `_wait_dungeon_cycles` helper owns `times`, `done`, and `deadline`. Its doc says it counts MapID enter/exit cycles and ignores None.
- A real frozen-code/documentation conflict was found: the helper doc says waiting is “vô thời hạn”, but the exact compiled helper also contains local `deadline`, literal **480**, and the exact timeout-log fragment `theo dõi map timeout (...s) — hoàn thành ...`. Therefore a compiled **480-second watchdog branch exists** and reconstruction must not implement a truly infinite wait from the stale prose line alone. Deep timeout outcome/order is deferred to J07.
- Another boundary is preserved rather than guessed: `_do_dungeon` explicitly documents outer manual repetition and “1 cycle map” per repetition, while the generic helper itself still accepts a `times` argument. The exact literal native caller value passed into that helper is not recoverable from printable constants; overall requested-count completion is locked, but that call literal remains a micro-UNKNOWN for later Windows verification.
- Normal row completion remains consistent with J04: account workers return only after their normal activity completes; the row is marked `Xong` only after the current account-thread batch joins. For Phó Bản this means normal success only after the requested dungeon repetition sequence. Failure/cancel status behavior remains J07.
- Only after static extraction, B07 was re-hashed at `8b62070b04231f762dc080f4432cbc178f020ae0614540dc0e9c293d16987fb8`, 452×1032 RGBA. No schedule row is expanded in the screenshot, so Entry/count behavior comes from the EXE, not image inference.
- Only after static extraction, exact packaged `data/automove_log.txt` (SHA-256 `17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`, 15,741,058 bytes, 387,238 lines) was searched. It contains 0 correlated top-level J06 markers for Phó Bản start/completion/map-timeout/cycle failure/start retry/SelectedFuBen/RepeatCount. J06 is **STATIC_VERIFIED / RUNTIME_ENV_REQUIRED** for live count/index/timeout races.

## J06 FILES
- docs/tasks/J06.md
- docs/phoban/J06_TIMES_FLOW.md
- docs/phoban/J06_TIMES_MODEL.json
- docs/phoban/J06_TIMES_STATIC_EVIDENCE.tsv


## J07 VERIFIED RESULTS
- GitHub-first continuity check passed. No J07 artifacts/completion commit existed before this turn; J01-J06 were already complete and were not redone.
- Re-inspected the exact uploaded TLMTool 2.1.2 archive first. Archive SHA-256 remains `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; inner `TLMTool.dist/TLMTool.exe` remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, size **47,450,112** bytes.
- Frozen run-state ownership is two-layered: tab-global `_running/_cancel/_run_lock/_active_runs/_run_jobs` plus per-group `_run_cancel`. Exact `_group_is_running` semantics are cancel exists + not set. External `stop()` explicitly means global cancel + every group cancel.
- Exact command routing remains: bottom run button controls all groups; a group run button controls only that group; unrelated groups continue independently.
- Exact group button states are now frozen: running = **Dừng lịch trình / #f44336 / normal**; stopping = **Đang dừng lịch trình... / #ef6c00 / disabled**; idle = **Bắt đầu lịch trình** with green start styling. Bottom button is **Dừng lại / #f44336** while groups run, **Bắt đầu** when idle, and the bulk stop path has **Đang dừng... / #ef6c00 / disabled**.
- Cancellation is cooperative. No forced Python thread-kill mechanism was recovered. Group/global stop signals Events and the synchronization/failure shell lets workers unwind.
- Exact `_abort_cycle` contract: any account hard failure stops **that group only**, aborts/breaks the shared barrier so peers escape, sets the group cancel so workers cannot advance, and is idempotent.
- Exact `_barrier_wait` contract: no ordinary timeout; wait for the complete party. An aborted barrier caused by account failure or user stop returns False so the caller exits.
- Frozen `.phoban_dungeons._call_hook` contract is asymmetric and important: missing hook or hook exception is logged/fail-open True; only explicit hook False aborts the current group cycle through the tab abort shell.
- Hard-failure escalation after internal retries is group-local: exhausted memory config, movement, FuBen-start, or false cycle-wait result stops the current group, not every group.
- J06's compiled 480-second watcher was rechecked. `_wait_dungeon_cycles` has `deadline`, `done`, encoded integer **480** and exact timeout log `theo dõi map timeout (...s) — hoàn thành ...`. The exact native return expression of that timeout branch is **not instruction-bound by the static constant stream**. It remains explicit UNKNOWN rather than being guessed. If the helper returns False, the outer exact path logs `chờ cycle map FAIL → dừng chu trình`.
- Per-account worker and outer dungeon exception logs are exact: `worker lỗi:` and `lỗi chu trình:`. Their semantic boundary is current-group failure, but the precise source-level exception-handler micro-order relative to `_abort_cycle` is not reconstructable from printable constants and remains explicit UNKNOWN.
- Row-progress vocabulary remains only **Chưa / Đang / Xong**; no Error/Cancelled style exists. `Đang` is set before the worker batch and `Xong` is on the normal post-batch path. Exact late-cancel ordering against that final Xong write is not instruction-bound, so J07 does not invent whether every aborted current row visibly remains Đang.
- Exact `_finish_group_run` documentation locks one-group cleanup versus final global teardown. If other groups remain, only the completed/stopped group is cleaned and those groups continue. Only the last finishing group emits **[Phó bản] Hết nhóm chạy — teardown toàn cục** and resets the global flags/buttons/pickup lifecycle once.
- Critical recovery safety is exact: `_finish_group_run` removes cancel/job state only when it belongs to the **same run identity**. If the user starts a new session while the old worker is still winding down, stale cleanup must not clear the new cancel/job or trigger premature global teardown. No numeric group-run generation counter is recovered; this is an identity guard, not a guessed generation guard.
- Recovery is stage-local retry + safe/manual restart. Automatic retries remain config 5×2s, movement up to 3 total attempts, FuBen start 5×0.3s, plus the compiled cycle watcher. No automatic whole-group schedule restart after hard abort was recovered. A new/manual start resets group progress and gets a fresh run identity.
- Only after static extraction, B07 was re-hashed at `8b62070b04231f762dc080f4432cbc178f020ae0614540dc0e9c293d16987fb8`, 452×1032 RGBA. It shows only the normal idle state; red/orange stopping states come from the EXE, not screenshot inference.
- Only after static extraction, exact packaged `data/automove_log.txt` (SHA-256 `17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`, 15,741,058 bytes, 387,238 lines) was searched. It contains 0 correlated top-level J07 stop/abort/failure/teardown/completion markers. J07 is **STATIC_VERIFIED / RUNTIME_ENV_REQUIRED** for live cancellation/barrier/watchdog/rapid-restart races.

## J07 FILES
- docs/tasks/J07.md
- docs/phoban/J07_STATUS_FLOW.md
- docs/phoban/J07_STATUS_MODEL.json
- docs/phoban/J07_STATUS_STATIC_EVIDENCE.tsv


## J08 VERIFIED RESULTS
- GitHub-first continuity check passed. No J08 artifacts/completion commit existed before this turn; J01-J07 were already complete and were not redone.
- Re-inspected the exact uploaded TLMTool 2.1.2 archive and inner EXE first. Archive SHA-256 remains `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; inner EXE remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, size 47,450,112 bytes.
- Exact visible discard controls are **Vứt trang bị / Vứt vật phẩm / Vứt thuốc**, owned by `discard_equip_var/discard_items_var/discard_meds_var`, with shared callback `_toggle_discard`. B07 confirms all three clean/default visible states are OFF.
- Exact config mapping decodes to `discard_equip_var→phoban_discard_equip`, `discard_items_var→phoban_discard_items`, `discard_meds_var→phoban_discard_meds`.
- Exact runtime `DISCARD_TICK_KEYS` decodes as nested tuples: `(discard_equip_var,(discard_equip,))`, `(discard_items_var,(discard_items,))`, `(discard_meds_var,(discard_meds,))`. Current enabled preset order is therefore equipment → items → medicines.
- Discard mode is run-scoped and opt-in. Enabled ticks + an already-running group start the worker immediately; enabled ticks while idle wait for a later run; all ticks OFF stop the worker immediately; worker rechecks tick state every cycle and exits when no group runs.
- Worker lifecycle uses `_discard_stop/_discard_thread/_discard_gen`, an existing-thread `is_alive` guard and generation protection against overlapping worker sessions. Exact generation/thread teardown micro-order remains UNKNOWN.
- Scan cadence is exactly “every `PB_DISCARD_POLL` seconds”. The numeric value is not safely bindable from the serialized scalar pool and remains explicit UNKNOWN.
- Every poll processes all accounts belonging to currently-running groups. Accounts are processed in parallel; within each account the enabled presets are processed sequentially in exact `discard_equip → discard_items → discard_meds` order.
- The worker owns an `inflight` guard. Exact doc/log says an account whose previous discard thread is not finished is skipped for that poll, preventing overlapping per-account discard threads. Exact internal inflight identity key remains UNKNOWN.
- `_discard_one_acc` calls `bag_filter.discard_for_activity` once per enabled preset with activity `phoban`, one-second per-item pacing and a stop_check handoff. It does not merge all three tick presets into one PhoBanTab call.
- Shared `bag_filter` is opt-in: no keys/rules means no discard/no packet. The underlying abandon action is internal packet path `CMD_ITEM_ACTION=100005`, payload `4:<dbID>`; shared `memory_items` independently confirms action 4 = Abandon. No game-GUI “Vứt” click is required.
- Stop-check handoff is proven, but the exact Boolean formula of the worker-owned stop closure — especially whether an already-running per-account pass directly checks one individual group's cancel Event — is not source-bound and remains explicit UNKNOWN.
- The normal `_run_one_group` completion path contains a dedicated final-discard region after ordinary row completion and before `HOÀN THÀNH`: exact literals `vứt lượt cuối (`, `xong vứt lượt cuối`, `vứt lượt cuối lỗi:` plus locals `_fkeys/_ft/_t`. Strong static contract: re-read the current enabled discard keys, and when non-empty run one final account-thread batch for the finishing group's targets before completion.
- If all three ticks were unticked, current final keys are empty and no forced final discard is recovered. The all-off toggle has already stopped the periodic worker.
- No static evidence of a mandatory final flush after user stop/hard abort was recovered. The final-discard block is on the normal post-row path. A very late cancel at the exact final-pass boundary remains runtime-UNKNOWN.
- If another group is still running, periodic discard can continue for that group after the finishing group completes. When the last group is gone, the worker's no-running-groups condition makes it exit.
- Shared `bag_filter` owns `_SEND_LOCKS_GUARD/_SEND_LOCKS/_send_lock_for`, giving a lower-level send serialization boundary; exact periodic-vs-final-pass same-account interleaving still needs Windows/runtime parity.
- Only after static extraction, B07 was re-hashed at `8b62070b04231f762dc080f4432cbc178f020ae0614540dc0e9c293d16987fb8`, 452×1032 RGBA. It confirms all three controls unchecked; runtime behavior was not inferred from the screenshot.
- Only after static extraction, exact packaged `data/automove_log.txt` was checked. It contains 0 correlated PhoBanTab discard/final-pass markers. Generic action-4 evidence exists: 2 normal + 22,732 spts = **22,734** explicit Abandon sends. This proves the shared low-level primitive ran, not that PhoBanTab caused those sends.
- J08 classification: **STATIC_VERIFIED / RUNTIME_PRIMITIVE_ONLY / END_TO_END_RUNTIME_ENV_REQUIRED**.

## J08 FILES
- docs/tasks/J08.md
- docs/phoban/J08_DISCARD_FLOW.md
- docs/phoban/J08_DISCARD_MODEL.json
- docs/phoban/J08_DISCARD_STATIC_EVIDENCE.tsv


## J09 VERIFIED RESULTS
- GitHub-first continuity check passed. No J09 artifacts/completion commit existed before this turn; J01-J08 were already complete and were not redone.
- Re-inspected the exact mounted original archive `/mnt/data/TLMTool_2.1.2(6).zip` before any screenshot/log cross-check. Archive SHA-256 remains `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, size **93,715,901** bytes. Inner `TLMTool.dist/TLMTool.exe` remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, size **47,450,112** bytes.
- Exact visible control is **Nhặt không hồ lô**. Constructor state is `pickup_var/_pick_stop/_pick_thread`; callback is `_toggle_pickup`. Exact function inventory contains `_pickup_members/_toggle_pickup/_start_pickup/_stop_pickup/_pickup_worker`.
- Critical architecture difference: no `_pick_gen` or `_pickup_gen` exists in the exact PhoBanTab module. Pickup must not inherit the generation-counter design used by follow/discard/buff.
- Config key is exactly `phoban_pickup`; clean/load fallback is `"0"`; save path writes the same key. B07 independently confirms `pickup_no_gourd=false`.
- Exact toggle documentation says `Tự nhặt đồ` is a persisted mode and the IsOn keepalive only runs while a Phó Bản schedule is running. Tick during a run starts it immediately; untick stops it immediately. Run documentation independently says pickup runs in the background with the schedule.
- The pickup start shell exposes `is_alive` and stop-event `clear` immediately before `_pickup_worker`, proving duplicate-worker guard + stop-event reuse. Exact thread daemon/join/reference-clear ordering remains micro-UNKNOWN.
- Exact cadence is `PICK_POLL` seconds. Numeric value cannot be safely bound from the serialized scalar pool and remains explicit UNKNOWN.
- `_pickup_members` exact doc: **all selected accounts from all group clusters, unique, stable order**. It references `get_groups_data` and `members`; its local model includes output/seen/member-name state. This is intentionally broader than J08 discard's “currently-running groups only” scope.
- Therefore the static original model is: while at least one Phó Bản schedule is running, the pickup keepalive services all currently selected Phó Bản members that resolve to live HWNDs, even if one selected member belongs to another configured group that is not the group currently executing.
- Worker directly references `_pickup_members` + `_hwnd_by_name`; local model is `self,stop,GI,names,name_hw,nm,hwnd,data,val,on,ok,e`. It re-resolves current live HWNDs each poll rather than freezing one lifetime HWND roster.
- Internal implementation is exact: read `get_auto_settings(hwnd)` → inspect `PICKITEM.IsOn` → if not effectively ON, call `set_auto_fields` with `PICKITEM.IsOn=True`. The worker is a memory/internal auto-setting keepalive, not a drop scan/click engine.
- Exact worker documentation: every `PICK_POLL` seconds, any account whose auto-pick is off is turned back on and saved. The local `val/on/bool` model strongly supports Boolean normalization/readback before repair.
- Shared exact-memory documentation says `set_auto_fields đã SaveSetting`; this matches the pickup worker's “bật lại + lưu” contract. The write is therefore sent through the game's internal auto-setting/save path.
- Exact diagnostics include per-account `bật tự nhặt lỗi:`, result `tự nhặt đồ (OK/FAIL)`, and outer `[Phó bản] pick lỗi:`. No recovered contract says one pickup keepalive error hard-aborts the Phó Bản schedule.
- J09 contains no bag_filter preset, item-action packet, or screen-click pickup logic. The operational contract is specifically **keep `PICKITEM.IsOn=True`** while the run-scoped mode is active.
- Stop/untick cleanup was audited carefully. Inside the exact pickup subsystem there is only a recovered `PICKITEM.IsOn=True` write shape; no pickup-local `_sweep_off`, no recovered `PICKITEM.IsOn=False` write, and exact toggle wording is “bỏ tick -> dừng ngay”. The `_sweep_off` symbol present in PhoBanTab belongs to Nga My buff, not pickup. Reconstruction must therefore stop enforcing ON and must **not invent an OFF write**.
- J07 final-group documentation says global teardown resets flags/buttons/pickup once. Combined with the persisted pickup-mode contract, strongest static model is that final-group teardown stops/resets the pickup worker lifecycle; no evidence shows it clears `pickup_var/phoban_pickup` or writes `PICKITEM.IsOn=False`.
- Only after static extraction, B07 was re-hashed at `8b62070b04231f762dc080f4432cbc178f020ae0614540dc0e9c293d16987fb8`, 452×1032 RGBA. It confirms the visible checkbox and clean OFF state only.
- Only after static extraction, exact packaged `data/automove_log.txt` (SHA-256 `17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`, 15,741,058 bytes, 387,238 lines) was searched. It contains 0 correlated pickup markers for Phó Bản, PICKITEM, pick errors, set_auto_fields or SaveSetting. J09 is **STATIC_VERIFIED / END_TO_END_RUNTIME_ENV_REQUIRED**.

## J09 FILES
- docs/tasks/J09.md
- docs/phoban/J09_PICKUP_FLOW.md
- docs/phoban/J09_PICKUP_MODEL.json
- docs/phoban/J09_PICKUP_STATIC_EVIDENCE.tsv


## J10 VERIFIED RESULTS
- GitHub-first continuity check passed. No J10 artifacts/completion commit existed before this turn; J01-J09 were already complete and were not redone.
- Re-inspected the exact mounted original archive `/mnt/data/TLMTool_2.1.2(6).zip` before B07/runtime cross-check. Archive SHA-256 remains `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, size **93,715,901** bytes. Inner `TLMTool.dist/TLMTool.exe` remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, size **47,450,112** bytes.
- Exact visible control is **Nga My buff (Sát Tinh)**. Constructor state is `nga_my_buff_var/_buff_stop/_buff_thread/_buff_gen`; callback is `_toggle_buff`. Exact callable inventory includes `_start_buff/_stop_buff/_is_nga_my/_buff_ensure/_buff_worker`.
- Config key is exactly `phoban_nga_my_buff`; load fallback is `"0"`; B07 independently confirms clean/default OFF.
- Exact toggle documentation locks run-scoped persisted-mode behavior: ON+running starts worker immediately; ON+idle waits for later run start; OFF stops immediately and the worker performs a **final untick sweep** before exit.
- Worker lifecycle uses stop Event + thread + generation. Exact doc says `is_alive` prevents overlap and generation prevents two workers from overlapping. Exact generation/thread teardown micro-order remains UNKNOWN.
- Scan cadence is `PB_BUFF_POLL` seconds. Its numeric value is not safely bound from current static evidence and remains explicit UNKNOWN.
- Exact `PB_BUFF_MONSTER_LIST` value is **"910"**.
- Nga My detection is exact: primary `FactionID == 4`, fallback faction name **Nga My**. Exact fallback string-normalization expression remains a micro-UNKNOWN.
- Exact controlled auto fields are under `AUTOTRAIN`. ON = `IsAttackMonsterInList=True` + `AttackMonsterList="910"`. OFF = `IsAttackMonsterInList=False` + `AttackMonsterList=""`.
- `_buff_ensure` is a readback/repair helper: read current `AUTOTRAIN` fields, skip writing if already correct, otherwise write desired pair and re-read/retry up to `PB_BUFF_RETRY`. Failed attempts wait **1 second**. Exact numeric `PB_BUFF_RETRY` remains explicit UNKNOWN.
- Buff account scope is **members of currently-running groups**, unlike J09 pickup's all-selected-groups roster.
- Worker re-reads current character info and uses `FactionID/FactionName/MapID`. Exact snapshot log is `[Phó bản] Buff snapshot: ... F<FactionID>(FactionName)/map<MapID> ...`.
- Important parity finding: although the checkbox label says **(Sát Tinh)**, the exact worker documentation says **Nga My + trong map phó bản → ON; còn lại (không phải Nga My / đã ra ngoài) → OFF**. The worker has local `dungeon_maps`; no dedicated `MapID == 111` gate is recovered in the buff block. Reconstruction must not narrow the code to map 111 just from the label.
- Every regular poll computes the desired ON/OFF state and writes only when readback differs. This means non-NgaMy or accounts outside the dungeon-map set are actively restored to the OFF pair.
- Worker owns a `known` roster plus nested `_sweep_off`. Exact final cleanup log is **[Phó bản] Buff quét cuối untick <N> acc Nga My**. This binds the final untick sweep to Nga My accounts known during the worker session; exact container/key type remains UNKNOWN.
- Unlike J09 pickup, J10 has an explicit OFF cleanup on untick: final sweep forces `IsAttackMonsterInList=False` and empty `AttackMonsterList`.
- Worker doc separately says **hết nhóm chạy cũng thoát**, but the frozen prose explicitly names the final OFF sweep as **quét cuối untick**. No independently-recovered unconditional no-running-group/run-end OFF sweep exists. Normal polling already drives out-of-dungeon accounts OFF; an additional unconditional schedule-end sweep must not be invented without stronger evidence.
- Buff errors are logged/retried/contained: exact surfaces include `buff lỗi import:`, `ghi buff lỗi:`, `ghi buff FAIL ... retry sau 1s`, `[Phó bản] buff lỗi:`. No recovered contract routes a routine buff maintenance error into J07 `_abort_cycle`.
- Only after static extraction, B07 was re-hashed at `8b62070b04231f762dc080f4432cbc178f020ae0614540dc0e9c293d16987fb8`, 452×1032 RGBA. It confirms the visible label and clean OFF state only.
- Only after static extraction, exact packaged `data/automove_log.txt` (SHA-256 `17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`, 15,741,058 bytes, 387,238 lines) was searched. It contains 0 correlated PhoBanTab buff markers/field names. Raw `910` occurs 99 times but without buff/PhoBan correlation and is not J10 runtime proof.
- J10 classification: **STATIC_VERIFIED / END_TO_END_RUNTIME_ENV_REQUIRED**.

## J10 FILES
- docs/tasks/J10.md
- docs/phoban/J10_NGA_MY_BUFF_FLOW.md
- docs/phoban/J10_NGA_MY_BUFF_MODEL.json
- docs/phoban/J10_NGA_MY_BUFF_STATIC_EVIDENCE.tsv


## J11 VERIFIED RESULTS
- GitHub-first continuity check passed. No J11 artifacts/completion commit existed before this turn; J01-J10 were already complete and were not redone.
- Re-inspected the exact mounted original archive `/mnt/data/TLMTool_2.1.2(6).zip` before B07/runtime cross-check. Archive SHA-256 remains `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, size **93,715,901** bytes. Inner `TLMTool.dist/TLMTool.exe` remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, size **47,450,112** bytes.
- Exact multi-group constructor/runtime state includes `_groups/_group_counter/_run_lock/_active_runs/_run_jobs`. The UI has persistent **+ Thêm nhóm** → `_add_group_cluster`.
- Exact group-builder documentation: one new group contains leader row + per-group delete + **Nhóm n (6 combobox)** + activity table + add-schedule-row controls and returns a group dict.
- B07 reference idle baseline shows exactly one visible group. However exact removal documentation says **“Xóa 1 cụm ... cho phép xóa hết.”** Therefore one is not a minimum: the current UI permits deleting all groups and reaching zero.
- Current per-group delete is **✕ Xóa nhóm**. Frozen compatibility helpers `_remove_last_group` and `_update_del_group_state` remain, but their docs explicitly mark them as old compatibility; current architecture no longer has a shared/common delete button.
- The exact group builder has `MAX_GROUP_MEMBERS` and six account slots. No `MAX_GROUPS/MAX_PHOBAN_GROUPS/PB_MAX_GROUPS` symbol or Phó Bản max-group message is recovered. Therefore the exact member cap is **6 per group**, while no explicit hard group-count cap is recovered. Reconstruction must not invent an arbitrary maximum group count.
- The exact missing/empty-config bootstrap group-count branch is not instruction-bound by printable constants. Preserve the B07 one-group reference baseline and exact delete-all behavior; do not falsely claim a hidden mandatory one-group minimum.
- Cross-group account uniqueness is exact. `_refresh_group_combo_values` says an account chosen in an earlier group no longer appears in later-group dropdowns; current valid selections remain; dead/stale selections reset. The all-group helper is exactly “Tất cả acc được chọn (mọi cụm Nhóm), unique, giữ thứ tự.”
- Group order is semantically important: modern `get_groups_data` persists `[{num,members,schedule}, ...]` in UI order; J04 already froze row order within each group. No group drag/reorder control is recovered.
- Removal control region directly contains `_run_cancel`, `remove`, then `_renumber_groups` immediately before the exact removal doc. Strong static contract: deleting a group is run-aware, removes it from the group container and renumbers/relabels remaining groups. Exact `_group_counter` mutation/reset expression remains UNKNOWN.
- Each group owns its own six member vars, nominal leader, schedule rows, header checkbox, leader label, run button, `Tắt auto PB` button and current `_run_cancel`. Groups are self-contained configuration/run units, not member lists sharing one global schedule.
- Modern persistence key remains `phoban_groups`; legacy `phoban_group1/phoban_schedule` remain compatibility surfaces only. Do not reconstruct the current tool as single Group1 + global schedule.
- Exact `_collect_group_job`: one group becomes `(num,targets,sched)`; no online targets or no checked row → no job. Thus start-all skips non-runnable configured groups.
- Exact start-all contract: bottom Start runs **all runnable groups**, one thread per group, in parallel. Exact log is **[Phó bản] Bắt đầu song song <N> nhóm — <M> acc**; zero runnable jobs logs no-group-to-run.
- Run ownership is split between tab registry `_run_lock/_active_runs/_run_jobs` and group-local `_run_cancel`. Exact Python container/key types remain UNKNOWN and are not invented.
- Group execution is genuinely parallel/independent: rows are sequential only inside that group, accounts parallel inside its row, and stop/failure of Group A does not cancel Group B/C.
- Exact finish contract: one group cleanup leaves other runs untouched and can log **xong, còn <N> nhóm chạy tiếp**. Global teardown occurs only when the final active group finishes. J07 identity-safe cleanup remains authoritative so stale old-run cleanup cannot remove a newly-started session.
- Shared worker cross-group scopes are now frozen explicitly:
  - J03 Follow = each **running group** independently, first slot leader + remaining followers;
  - J08 Vứt đồ = accounts in **currently-running groups**;
  - J09 Nhặt không hồ lô = **all selected members across all groups**, unique/order-preserving, while pickup worker lifetime remains schedule-scoped;
  - J10 Nga My buff = accounts in **currently-running groups**.
- These four worker scopes are intentionally different. Reconstruction must not replace them with one universal group-members helper.
- Group removal during a live/winding-down run is architecturally protected by per-group cancel handling plus J07 run-identity cleanup, but exact live timing when deletion happens during barrier/memory work remains runtime-unverified.
- Only after static extraction, B07 was re-hashed at `8b62070b04231f762dc080f4432cbc178f020ae0614540dc0e9c293d16987fb8`, 452×1032 RGBA. It confirms one visible group, six slots, per-group delete and + Thêm nhóm; it is not used to infer hidden multi-group behavior.
- Only after static extraction, exact packaged `data/automove_log.txt` was checked: 0 correlated markers for `[Phó bản]`, `Bắt đầu song song`, `nhóm chạy tiếp`, `Hết nhóm chạy`, `Dừng Nhóm`, or `Dừng hết các nhóm`. J11 is **STATIC_VERIFIED / END_TO_END_MULTI_GROUP_RUNTIME_ENV_REQUIRED**.

## J11 FILES
- docs/tasks/J11.md
- docs/phoban/J11_MULTI_GROUP_FLOW.md
- docs/phoban/J11_MULTI_GROUP_MODEL.json
- docs/phoban/J11_MULTI_GROUP_STATIC_EVIDENCE.tsv


## J12 VERIFIED RESULTS
- GitHub-first continuity check passed. No J12 artifacts/completion commit existed before this turn; J01-J11 were already complete and were not redone.
- Re-inspected the exact mounted original archive `/mnt/data/TLMTool_2.1.2(6).zip` before B07/runtime cross-check. Archive SHA-256 remains `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, size **93,715,901** bytes. Inner `TLMTool.dist/TLMTool.exe` remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, size **47,450,112** bytes.
- Exact start/stop entry points are unified through `_toggle_run`: bottom button `gd=None` = stop all if anything is running, otherwise start all runnable groups; group button = stop/start only that group while other groups continue.
- Stop routing precedes new-start preflight. Group stop / all-stop branches are ahead of the permission/job-launch surfaces, so a stop request is not blocked by a start permission check.
- New-start permission gate is exact: `has_permission_with_limit` with `phoban_tab` / `phoban`; denial logs **[PhoBan] Khóa bản quyền - khong cho phep** before job/progress/cancel/thread creation.
- Start preflight also carries the `memory_items` dependency/error surface before current HWND/job collection. Exact source-level exception-return syntax is not recoverable, but reconstruction must not launch a broken job if the required memory plumbing is unavailable.
- Per-group start lifecycle is statically frozen as: collect runnable job first; invalid group logs “không có acc online + lịch trình” and does not start; valid group resets only its progress, receives a fresh `_run_cancel` identity, registers/launches its run and syncs buttons.
- Start-all independently filters every group. Non-runnable configured groups are skipped. Zero runnable jobs logs **[Phó bản] Không có nhóm nào để chạy**. A valid batch uses `reset_all_progress` and logs **[Phó bản] Bắt đầu song song <N> nhóm — <M> acc**.
- Exact machine-instruction order of `reset_all_progress()` versus construction/start of the first group thread is not printable-constant-bound; semantic contract is that reset belongs to the successful fresh start-all path, not stop/invalid-start.
- J07 identity-safe teardown plus the start-region `_run_cancel` surface proves each new group run needs a fresh cancel identity; an old set Event cannot be reused for a new run.
- Global `_cancel` is separate from group `_run_cancel`. Public `stop()` exact doc says **global cancel + every group cancel**. Fresh restart necessarily re-arms the global stop state; the exact `_cancel.clear()` source-line order remains an explicit micro-UNKNOWN.
- Shared background mode integration is now frozen semantically: Follow/Discard/Pickup/Buff all document that ON while idle waits and **run start will build/rebuild the worker**. Therefore a valid active run identity must be visible before these workers can successfully pass their run-scope guard.
- Exact native call order among `_run_one_group` Thread.start and `_start_pickup/_start_follow/_start_discard/_start_buff`, plus the inter-worker ordering, is not instruction-bound by the serialized printable constants. J12 keeps this explicit UNKNOWN instead of guessing from method-definition order.
- Starting an additional group must not duplicate tab-level background workers: Pickup has `is_alive`; Follow/Discard/Buff have `is_alive` + generation guards. Existing workers simply see their cross-group scope change on subsequent polls.
- Per-group stop sets that group's cancel, immediately making it logically non-running under the exact J07 definition, while its old worker may still wind down. Other groups continue.
- Stop-all exact shell: `_stop_all_runs`, all run buttons show **Đang dừng... / #ef6c00 / disabled**, exact log **[Phó bản] Dừng hết các nhóm**, then cooperative unwind and last-group teardown. No forced Python thread kill is recovered.
- Persisted run-mode selections are not cleared by stop/end: `phoban_pickup/phoban_follow/phoban_nga_my_buff/phoban_discard_equip/phoban_discard_items/phoban_discard_meds/phoban_recreate_team` remain configuration choices. Worker lifecycle stops; next run re-arms enabled modes.
- Cleanup asymmetries remain exactly preserved: no hard-stop final discard flush; pickup has no recovered IsOn=False sweep; Nga My buff's OFF sweep is explicitly tied to untick and not independently recovered as unconditional run-end cleanup; Follow simply exits its run-scoped worker.
- `_finish_group_run` remains the last-group lifecycle boundary: if another run remains, clean only the matching current group run; when the last run is gone, emit **[Phó bản] Hết nhóm chạy — teardown toàn cục** and reset flags/buttons/pickup lifecycle once.
- Exact final-teardown prose names pickup specifically. Follow/Discard/Buff are still run-scoped because their own exact worker docs say they exit when no group is running.
- Public `stop()` is confirmed as a tab-wide API, not focused-group stop.
- `_on_destroy` is definitely bound through `<Destroy>`; constructor owns `_refresh_id/_refreshing/_closing`; exact method symbol is present. No standalone readable `_on_destroy` doc/log contract is recovered, so its exact internal cleanup call order remains explicit UNKNOWN for stronger native/runtime proof.
- Only after static extraction, B07 was re-hashed at `8b62070b04231f762dc080f4432cbc178f020ae0614540dc0e9c293d16987fb8`, 452×1032 RGBA. It confirms the idle Start presentation only.
- Only after static extraction, exact packaged `data/automove_log.txt` was checked. It contains 0 correlated J12 start/stop/permission/shared-worker Phó Bản markers. J12 is **STATIC_VERIFIED / END_TO_END_START_STOP_RUNTIME_ENV_REQUIRED**.

## J12 FILES
- docs/tasks/J12.md
- docs/phoban/J12_START_STOP_FLOW.md
- docs/phoban/J12_START_STOP_MODEL.json
- docs/phoban/J12_START_STOP_STATIC_EVIDENCE.tsv


## J13 VERIFIED RESULTS
- GitHub-first continuity check passed. No J13 artifacts/completion commit existed before this turn; J01-J12 were already complete and were not redone.
- Re-inspected the exact mounted original archive `/mnt/data/TLMTool_2.1.2(6).zip` before B07/runtime cross-check. Archive SHA-256 remains `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, size **93,715,901** bytes. Inner `TLMTool.dist/TLMTool.exe` remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, size **47,450,112** bytes.
- Integrated failure classes are now locked as four distinct categories: pre-run reject; per-account degradation; current-group hard abort; fail-soft/log-only. Do not normalize all failures to one abort policy.
- Start-preflight failures (permission/dependency/no runnable job) create no new run; recovery is fixing the condition then manual Start.
- Party formation remains deliberately mixed: AutoAccept issues and leave timeout are fail-open; unresolved individual RoleID skips that member; zero RoleID targets or exhausted real-TeamID create retries stop the current group; burst invite still-missing after resend remains best-effort success unless cancelled.
- Account setup is per-account degradation. Exact `_run_one_group` local model owns `setup_threads/results/ready`; nested `_setup_one` owns `nm/hw/ok/cancel/self/lock/results`. Strong static contract: failed inject/common.active/setup accounts are omitted from the ready subset; ready accounts continue. Exact group log when none remain is **không acc nào online**, then no schedule executes.
- Setup's own recovery is local only: normal inject path + short `common.active` retry window documented around 2 seconds. No automatic whole-group rerun after setup exhaustion is recovered.
- Explicit dungeon hard-failure shell remains current-group-only: config memory 5×2s exhaustion, movement 3 total attempts exhaustion, explicit hook False, FuBen start 5×0.3s exhaustion, and false cycle-wait result all stop the current group through the existing abort/barrier shell.
- Barrier is propagation, not retry: no normal timeout; failure/user stop aborts it and peers exit.
- Cycle watcher tolerates temporary MapID None and has local repair/fail-open behavior such as `tuLamNhiemVu` read error → skip restart, False → attempt to re-enable auto FuBen. No immediate hard-abort surface is attached to those transient verification messages.
- The 480-second watcher was re-audited. The exact helper still contains `deadline`, `done`, integer **480**, and timeout log **theo dõi map timeout (...s) — hoàn thành ...**. A second static pass still cannot instruction-bind its exact native return expression. It remains **EXPLICIT UNKNOWN**; if the helper returns False, the outer exact path hard-aborts the current group.
- J13 found and corrected a real J07 overclaim for hooks. Exact `_call_hook` doc says missing/error → pass True and explicit False → abort, but the same exact helper block also contains exception text `) lỗi:` followed by **→ abort** plus `_abort_cycle`. Therefore hook exception behavior is now **STATIC_CONFLICT / RUNTIME_OR_NATIVE_INSTRUCTION_REQUIRED**. Explicit False remains a current-group abort.
- J13 found and corrected a second J07 overclaim for generic `_acc_step_worker` exceptions. The worker's own exact block calls `_do_dungeon/_do_train`, logs `worker lỗi:`, has no recovered worker-local `_abort_cycle` reference and no schedule-worker result aggregation. Generic worker exceptions are therefore fail-soft/log-only unless the called dungeon path already set group cancel itself.
- This correction does not weaken explicit dungeon failures: config/move/hook-False/start/cycle hard stages abort internally before returning to the generic worker shell.
- Train failure is now explicitly classified fail-soft at schedule-row level. `_do_train` has failure paths for unwired farm tab, account missing, dispatch/main-thread errors; its return is not aggregated by the worker/run shell. Therefore a normal-return Train failure can still allow the row worker batch to join and reach the normal `Xong` path. This bug-like behavior must be preserved for parity.
- Final-discard failure is also fail-open: exact `vứt lượt cuối lỗi:` is followed by `HOÀN THÀNH` in the normal completion region and no abort link is recovered.
- Periodic Follow/Discard/Pickup/Buff errors remain feature-local; no schedule `_abort_cycle` linkage is recovered. Buff has its own PB_BUFF_RETRY; other workers rely on their periodic/toggle/run lifecycle for later recovery.
- Ordinary hard failure blast radius remains only the current group. Other groups continue. Global blast radius requires explicit stop-all/public stop semantics.
- Progress still has only **Chưa/Đang/Xong**. Hard-abort current-row late-cancel label timing remains UNKNOWN; Train/generic fail-soft paths can reach `Xong`.
- Automatic recovery exists only inside individual stages. No whole-group automatic restart after hard abort is recovered. Manual fresh Start is the recovery mechanism: reset progress, fresh cancel/job identity, rerun setup/config, re-arm persisted modes.
- Targeted J07 artifacts were patched rather than silently leaving contradictions: hook exception was downgraded to STATIC_CONFLICT and generic worker exception was corrected to fail-soft/log-only unless an inner dungeon stage already aborted.
- Only after static extraction, B07 was re-hashed at `8b62070b04231f762dc080f4432cbc178f020ae0614540dc0e9c293d16987fb8`, 452×1032 RGBA. It contains no failure UI evidence.
- Only after static extraction, exact packaged `data/automove_log.txt` (SHA-256 `17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`, 15,741,058 bytes, 387,239 newline-counted lines) was searched. It contains 0 correlated J13 party/setup/worker/dungeon/final-discard/background/watchdog/Train markers.
- J13 classification: **STATIC_VERIFIED / END_TO_END_FAILURE_RECOVERY_RUNTIME_ENV_REQUIRED**.

## J13 FILES
- docs/tasks/J13.md
- docs/phoban/J13_FAILURE_RECOVERY_FLOW.md
- docs/phoban/J13_FAILURE_RECOVERY_MODEL.json
- docs/phoban/J13_FAILURE_RECOVERY_MATRIX.tsv
- docs/phoban/J13_FAILURE_RECOVERY_STATIC_EVIDENCE.tsv

## J13 TARGETED CORRECTION FILES
- docs/tasks/J07.md
- docs/phoban/J07_STATUS_FLOW.md
- docs/phoban/J07_STATUS_MODEL.json
- docs/phoban/J07_STATUS_STATIC_EVIDENCE.tsv


## J14 VERIFIED RESULTS / GATE-J CLOSURE
- GitHub-first continuity check passed. No J14 artifacts/completion commit existed before this turn; J01-J13 were already complete and were not redone.
- Runtime capability check was performed before claiming parity. Current execution environment is **Linux x86_64 / POSIX**; Python reports Linux, `wine` is not installed, and no TLMTool/Thần Long/Wine/LDPlayer Windows process is running. DISPLAY exists but this is not a Windows game runtime.
- Exact frozen original archive remains mounted at `/mnt/data/TLMTool_2.1.2(6).zip`, size **93,715,901** bytes, SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`. Inner EXE contract remains SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, size **47,450,112** bytes.
- Because no real Windows + live Thần Long runtime exists here, **0 live Phó Bản cases were executed and 0 live cases were marked PASS**. Mocks/Linux execution are not substituted for original runtime proof.
- Gate-J classification is **STATIC_RESEARCH_CLOSED / LIVE_RUNTIME_PARITY_DEFERRED**. This closes the static research handoff only.
- J13 conflict `_call_hook` exception behavior remains unresolved and classified `RUNTIME_OR_NATIVE_INSTRUCTION_REQUIRED`.
- J13 conflict for the compiled 480-second cycle-watchdog return remains unresolved and classified `RUNTIME_OR_NATIVE_INSTRUCTION_REQUIRED`.
- A Windows runtime harness specification is frozen: Windows 10/11 x64, exact original specimen, matching game client, at least 3 accounts (prefer 6), real HWND/memory/injection environment, timestamped video/log/config evidence and optional native debugger for unresolved conflicts.
- J14 runtime matrix contains 25 explicit cases covering normal run, rapid Start→Stop→Start, multi-group concurrency/independence, barrier abort, partial/all setup failure, Train fail-soft, final-discard fail-open, persisted-mode re-arm, Follow/Discard/Pickup/Buff scopes, stop-one/stop-all, teardown, delete-during-run, late-cancel progress, destroy cleanup, 480s watchdog and hook-exception behavior.
- Every unexecuted live test is explicitly `RUNTIME_ENV_REQUIRED` or `RUNTIME_OR_NATIVE_INSTRUCTION_REQUIRED`; no unrun case is counted as PASS.
- J14 closes Phase J at static research level and advances to Phase K. Stage S implementation remains locked by PLAN.

## J14 FILES
- docs/tasks/J14.md
- docs/phoban/J14_RUNTIME_ENVIRONMENT.md
- docs/phoban/J14_RUNTIME_HARNESS.md
- docs/phoban/J14_RUNTIME_TEST_MATRIX.tsv
- docs/phoban/J14_GATE_CLOSURE.md


## K01 VERIFIED RESULTS
- GitHub-first continuity check passed. No K01 artifact/completion commit existed before this turn; Phase J remained closed at **STATIC_RESEARCH_CLOSED / LIVE_RUNTIME_PARITY_DEFERRED** and was not reopened.
- Re-inspected the exact frozen original EXE first. Archive SHA-256 remains `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; inner `TLMTool.dist/TLMTool.exe` remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, size **47,450,112** bytes.
- Exact active Daily authority is now frozen: `.daily_tab` payload marker `0x2903223`; next serialized payload `.debug_android_tab` at `0x290bb8c`; bounded Daily serialized span **35,177 bytes / 0x8969**; `daily_tab.py` at `0x290aad1`; `<module daily_tab>` at `0x290abe0`; class `DailyTab`; embedded description **Daily Tab - Quản lý tác vụ hàng ngày.**
- Daily is active, not dormant. Main application tab construction contains visible `Daily`, module key `daily_tab`, class reference `DailyTab`, plus `daily_tab_ref` coordination.
- Constructor/runtime state visibly separates Trừng Ác and Tàng Bảo Đồ ownership: `_punish_running/_punish_cancel/_punish_btn` versus `_treasure_map_running/_treasure_map_cancel/_treasure_map_btn`, plus shared `_monitor_running/_acc_rows` and refresh/shutdown state.
- Exact visible Trừng Ác surface is frozen: duration field with UI seed **15**; move method `Ngựa / Định vị phù`; readonly teleport hotkey values **1/2/3**; heal option; visible Tô Châu heal location; equipment-discard option; reconnect; respawn/Địa phủ; apply-all control.
- Exact visible Tàng Bảo Đồ surface is frozen: tomb duration field with UI seed **30**; post-dig heal option; heal-location selector; reconnect; respawn; apply-all control.
- Shared account-list static row architecture is frozen: headers **Nhân vật / Hoạt động**, row `▶`, activity values exactly **Trừng ác / Tàng bảo đồ**, status dot `⬤`, initial state **Đã dừng**, per-row **Tới bổ đầu** and **Trị liệu**.
- Shared visible all-account controls are **Tới bổ đầu / Trị liệu / Bắt đầu**. Runtime string surface also contains **Dừng lại / Đang dừng...**.
- Exact top-level callable inventory contains **70 DailyTab methods/class members**. K01 categorizes them into shared UI/account discovery/config, runtime support, all-account/per-row orchestration, Trừng Ác support/execution and Tàng Bảo Đồ execution without deep-auditing those sequences.
- Top-level entry points are frozen: bottom all-account toggle `_start_all_accs`; per-row toggle `_toggle_single_acc`; activity start wrappers `_punish_start_worker/_treasure_start_worker`; activity run families `_punish_toggle/_punish_run_worker` and `_treasure_map_toggle/_treasure_map_run_worker`; config lifecycle `_load_config/_save_config/_save_on_destroy`.
- Exact internal module names directly exposed inside the bounded Daily payload include `utils`, `permission_guard`, `dll_injector`, `bag_filter`, `memory_items`, `fast_travel`, `pixel`, and `start_tab`. Module-level/external refs include `tkinter`, `tkinter.font`, `configparser`, `os`, `threading`, `win32gui`, and `keyboard`.
- Prior D04 B-level Daily→emulator edges remain only `STATIC_REFERENCE_NOT_IMPORT_PROOF`; K01 does **not** promote `emu_input/emu_reader/emu_remote/emu_setup` to active Daily imports because those exact module names are not direct refs in the bounded Daily payload.
- Only after static extraction, K01 cross-checked the frozen B08 evidence. Existing Daily screenshots remain hashes `217178561894a4205c7b5835ed33c050b384c8f60359f6894165e3400d514834` and `3939691e166fa67d9c50069119e4e3904496cd6769b04cf0d3199c6b3e0f866b`, same visible state with the already-frozen 265-pixel cursor-only difference. EXE-derived visible labels agree with B08; no hidden behavior was inferred from images.
- K01 establishes the Phase-K split consistent with PLAN's ~17 tasks: K01–K02 shared; K03–K09 seven Trừng Ác tasks; K10–K15 six Tàng Bảo Đồ tasks; K16–K17 runtime/parity closure.

## K01 FILES
- docs/tasks/K01.md
- docs/daily/K01_AUTHORITY_SURFACE.md
- docs/daily/K01_HANDLER_INVENTORY.tsv
- docs/daily/K01_DEPENDENCIES.tsv
- docs/daily/K01_STATIC_EVIDENCE.tsv
- docs/daily/K01_MODEL.json


## K02 VERIFIED RESULTS
- GitHub-first continuity check passed. No K02 artifact/completion commit existed before this turn; K01 was already complete and was not redone.
- Re-inspected the exact frozen original EXE first. Archive SHA-256 remains `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; inner EXE remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, size **47,450,112** bytes.
- Daily shared account refresh is incremental, not a full UI rebuild. Exact helpers are `_refresh_acc_lists/_start_refresh/_stop_refresh/_schedule_refresh`; the refresh worker gathers window/account data and uses Tk `after` for UI application.
- Exact refresh cadence is **5 seconds**. `_start_refresh` is documented for tab selection; `_stop_refresh` for switching away. Constructor lifecycle state includes `_refresh_id/_refreshing/_closing`.
- HWND identity is protected against handle reuse by PID binding. Exact `_is_window_alive` contract requires an HWND to remain open and still belong to the bound process; `bind_window_identity/unbind_window_identity` are explicit. If the HWND now points to another PID, Daily treats the old window as gone and recreates the row.
- `_add_or_update_row` exact doc says new rows are added, while existing valid rows update name/level/map in place. `_remove_stale_accs` removes rows whose window closed or whose HWND was reused by another process.
- Daily's account-list scrollregion has an exact **30 ms** time debounce. Frozen docs explicitly reject the older row-count-only optimization because it could lock an incorrect scrollregion before row geometry finished expanding.
- Shared row controls are locked: `▶`, character label, activity combobox `Trừng ác/Tàng bảo đồ`, status dot `⬤`, state label, MapID, `Tới bổ đầu`, `Trị liệu`. Initial state is **Đã dừng**.
- Row runtime/session state includes bound process identity plus `_farming_acc/_stop_event/_gen/_state`. These are runtime row/session surfaces, not recovered as durable Daily config keys.
- Row permission gating is exact: `permission_guard.has_permission("daily_tab")`. A newly-created row without permission disables the play button, activity combobox, `Tới bổ đầu`, and `Trị liệu`. The shared injection/runtime path separately exposes `has_permission_with_limit("daily_tab","daily")`; K02 keeps these two permission layers distinct.
- Exact shared state vocabulary/style mapping is frozen: `Đã dừng/Trị liệu` gray `#555555`; `Về bổ đầu/Đi huyệt mộ` blue `#1565c0`; `Làm nhiệm vụ/Đánh ác tặc/Đánh trong mộ` green `#2e7d32`; `Về Địa phủ` red `#c62828`; `Mất kết nối` dark red `#b71c1c`; unknown state falls back to gray.
- State UI mutation is strictly marshaled back to the Tk main thread. Exact `_schedule_state_label` docs say it invokes `_apply_state_label` via `after(0)`; frozen comments explicitly warn that touching Tk widgets from worker threads can terminate the process silently.
- Daily has a dedicated stale-worker race fix: module-level `_GenStop`. It wraps row `_stop_event` plus a captured `_gen`; `is_set()` also becomes true when the row generation changes. This prevents an old worker from surviving a rapid Stop→Start after the same Event is cleared for a new session.
- Exact `_stop_reason` vocabulary independently confirms shared stop causes: batch Trừng Ác/Tàng Bảo Đồ cancel, disconnect halt, stop_event, new generation, dead/reused window, and respawn/Địa-phủ.
- Per-row `▶/||` is owned by `_toggle_single_acc` and runs the row's **current activity only**, dispatching to `_punish_single_worker` or `_treasure_single_worker`. K02 does not deep-audit either activity worker.
- Bottom `_start_all_accs` is a true all-row toggle. Exact doc: while running it sets running rows `_farming_acc=False` and signals their stop Events; while idle it starts each eligible non-running row in a per-account thread according to that row's selected activity.
- Stop-all branch exact UI/log region restores row play presentation to `▶`, bottom button to **Bắt đầu / #388e3c**, syncs StartTab, and logs **[Bắt đầu] Đã dừng tất cả acc**. Worker unwind remains cooperative.
- Start-all branch skips a Trừng Ác row whose teleport mode lacks a configured hotkey, logs **Không acc nào cần chạy** if zero rows qualify, otherwise logs **Đã chạy ...**, switches bottom to **Dừng lại / #f44336**, and ensures the shared monitor exists.
- `_ensure_daily_monitor` exact doc says **Chỉ start 1 monitor instance**. `_daily_all_monitor` waits for all account sessions to stop, then resets UI using both activity reset helpers and logs **Tất cả acc đã dừng — tự động reset UI**.
- Shared `_resize_monitor(hwnd,is_running_fn)` checks every **1 second** and restores a valid/visible bound game window to **1366×768** through the shared StartTab resize helper when size differs.
- `_sync_start_tab_btns` explicitly synchronizes Trừng Ác/Tàng Bảo Đồ buttons on StartTab, confirming Daily has a shared external UI-state integration.
- Daily persistence is bounded to configuration modes through shared `read_settings/write_settings`. Exact `daily_*` keys cover activity options; no persistence key is recovered for row activity selection, bound PID, `_farming_acc`, `_stop_event`, `_gen`, or current row state. `<Destroy>` is bound to `_save_on_destroy`; its exact internal cleanup order remains UNKNOWN.
- Only after static extraction, K02 cross-checked B08 for shared controls only. The captured Daily state has an empty account list, shared headers, all-account `Tới bổ đầu/Trị liệu`, and bottom `Bắt đầu`; no populated-row behavior was inferred from the screenshot.
- Only after static extraction, exact packaged `automove_log.txt` was searched. It contains 0 correlated Daily/Bắt đầu/Inject/DailyTab/Trừng Ác/Tàng Bảo Đồ markers. K02 is **STATIC_VERIFIED / END_TO_END_RUNTIME_ENV_REQUIRED**.

## K02 FILES
- docs/tasks/K02.md
- docs/daily/K02_SHARED_FLOW.md
- docs/daily/K02_SHARED_MODEL.json
- docs/daily/K02_SHARED_STATIC_EVIDENCE.tsv


## K03 VERIFIED RESULTS
- GitHub-first continuity check passed. No K03 artifact/completion commit existed before this turn; K01-K02 were already complete and were not redone.
- Re-inspected the exact frozen original EXE first. Archive SHA-256 remains `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; inner EXE remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, size **47,450,112** bytes.
- Exact visible Trừng Ác configuration is frozen: duration field **15** seconds clean baseline; move mode labels **Ngựa / Định vị phù** with internal values `horse/teleport`; readonly teleport hotkeys exactly **1/2/3** with clean blank selection.
- B08 clean state independently confirms duration 15, Ngựa, blank hotkey, heal ON, discard OFF, reconnect ON, respawn ON. K03 records those neighboring defaults but defers their deep behavior.
- `punish_duration` is the combat-duration parameter passed to the execution sequence, not a user run-count. The outer worker owns `loop_idx` and logs **Lần ...**; no `daily_punish_repeat/punish_repeat/repeat_count/max_repeat` symbol exists in the bounded Daily payload. The outer loop is therefore open-ended until stop/live/activity termination.
- `_validate_repeat` exposes digit-oriented validation via `isdigit`; exact empty/min/max entry microbehavior remains UNKNOWN.
- Runtime move snapshot owns `move_mode/use_tele/tele_hotkey`. Strong static contract: canonical move values are horse/teleport and the session derives the Boolean-style teleport decision from the chosen mode.
- Config load exposes `daily_punish_duration/daily_tele_use/daily_move_mode/daily_tele_hotkey`; the load local model includes `old_tele_use`, strongly indicating backward-compatibility normalization between old Boolean teleport config and explicit move mode. Exact precedence/migration expression remains UNKNOWN.
- `_apply_punish_all` exact doc says it sets every current row's activity combobox to **Trừng ác**. It is a selection/configuration operation and does **not** itself start execution.
- Four distinct Trừng Ác ownership surfaces are frozen:
  - `_punish_start_worker`: inject-first activity wrapper;
  - `_punish_toggle`: activity-wide start/stop toggle;
  - `_punish_run_worker`: activity-wide batch worker;
  - `_punish_single_worker`: one-row iterative worker used by K02 row/all-account coordination.
- Exact activity-level button states are frozen: idle/reset = **Trừng ác / RoyalBlue / normal**; running = **Dừng lại / FireBrick**; stopping = **Đang dừng... / disabled**.
- Batch worker exact start-time structures include `selected` and `selected_pids`. Empty Trừng Ác selection logs **Chưa acc nào chọn Trừng ác — bỏ qua**. This is a start-time activity/process-identity snapshot rather than an unbounded rescan of arbitrary rows.
- Inside the outer loop the worker owns `alive` and `still_active` filters, with distinct terminal logs **Không còn acc nào sống — dừng** and **Tất cả <N> acc đã dừng — tự động dừng**. Thus current liveness/activity is re-evaluated on every loop even though the original selection is snapshotted.
- Batch loop is iteration-counted by `loop_idx`, logs **[TRỪNG ÁC] Lần ...**, and fans work out through a `threads` collection. No configured maximum iteration count is recovered.
- Batch and row cancellation are distinct. Activity-wide batch uses `_punish_cancel`; K02 row sessions use `row._stop_event + row._gen + _GenStop`. Exact `_stop_reason` vocabulary independently distinguishes `cancel(batch-trừng-ác)`, `stop_event(dừng)`, `gen(phiên-mới)`, and window/process death.
- Exact per-account batch stop-lambda Boolean composition—especially the exact instant an individually-stopped row interrupts an in-flight batch cycle—is not instruction-bound and remains explicit UNKNOWN.
- `_punish_single_worker` snapshots `row/gen_snap`, owns its own `loop_idx`, passes `punish_duration/use_tele`, and uses `_GenStop`. It is also an iterative session, not a one-shot call.
- Activity-wide Trừng Ác batch and Daily bottom Bắt đầu are intentionally different orchestration modes: the former is one batch worker over Trừng Ác-selected rows; the latter can mix Trừng Ác and Tàng Bảo Đồ and launches one single-account worker per eligible row.
- Bottom all-account path has exact missing-hotkey guard **[Bắt đầu] Thiếu phím tắt phù — bỏ qua trừng ác**. No equivalent dedicated missing-hotkey message is independently recovered from the activity-wide batch block; K03 does not assume identical validation placement.
- `_punish_reset_ui` restores the activity-level idle state. Exact final ordering among clearing `_punish_running`, button reset, StartTab sync and monitor teardown remains a runtime/lifecycle microdetail.
- Only after static extraction, B08 was cross-checked for the clean Trừng Ác config state. It provides no running/stopping evidence.
- Only after static extraction, exact packaged `automove_log.txt` was searched. It contains 0 correlated K03 Trừng Ác batch/single/start markers. K03 is **STATIC_VERIFIED / END_TO_END_RUNTIME_ENV_REQUIRED**.

## K03 FILES
- docs/tasks/K03.md
- docs/daily/K03_PUNISH_FLOW.md
- docs/daily/K03_PUNISH_MODEL.json
- docs/daily/K03_PUNISH_STATIC_EVIDENCE.tsv


## K04 VERIFIED RESULTS
- GitHub-first recovery check found K04 **partially completed but not closed**: commits already existed for `docs/tasks/K04.md`, `docs/daily/K04_PUNISH_QUEST_FLOW.md`, and `docs/daily/K04_PUNISH_QUEST_MODEL.json`, while `STATE.md/PROJECT_STATUS.md` still pointed to K04 and the static-evidence TSV was missing. Those completed K04 artifacts were **not redone**.
- Revalidated the already-written K04 claims against the exact frozen original EXE before closing the task. Archive SHA-256 remains `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; inner EXE remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, size **47,450,112** bytes.
- `_punish_goto_bodau` exact frozen documentation confirms normal NPC return target **Tô Châu map 4, tile (224,285)**, arrival tolerance **96**, and MapID==4 verification after movement.
- The NPC-return helper re-injects before movement because the hook may be lost after respawn/restart. Injection failure is explicitly **fail-open**: exact logs say “inject cho move thất bại, thử di chuyển trực tiếp” / “inject lỗi:”, after which direct movement is still attempted.
- NPC move stop/fail/wrong-map is a **current-cycle skip**, not terminal Trừng Ác completion. Exact failure text is “move về bổ đầu thất bại → skip vòng”; frozen doc says fail/timeout stops character and returns False so caller skips rather than clicking the NPC from a wrong location.
- Teleport mode has exact pre-step tuple **(490,429)** after the configured DLL hotkey, then converges on the same final `_punish_goto_bodau` path. Exact UI meaning of that fixed coordinate remains UNKNOWN.
- Normal quest interaction fixed-click groups were re-decoded directly from serialized integer tuples:
  - trả nhiệm vụ: **(890,471) → (884,423) → (481,423)**
  - nhận nhiệm vụ: **(891,467) → (484,424)**
  followed by `_punish_check_full`.
- 30/30 detection is memory/GameDialog-based, replacing the older unreliable pixel detector. The Daily helper directly reads `Title/CleanMsg/Buttons` through `memory_items.get_dialog_raw`.
- Exact full-dialog semantic markers are **Ngô Giới**, message signature **tối đa 30**, and button **Ta biết rồi**. Exact operator/string-normalization microexpressions are not invented from constant order.
- Full acknowledgement uses shared `memory_items.click_dialog_button`, whose exact frozen docs say it calls `GameDialog:FunctionButtonClicked`, lets the game send its normal dialog close/packet path, and returns True only after the dialog closes.
- Full-check read/no-match/click-failure paths are intentionally fail-open as **not full**. A verified full dialog + successful close returns True.
- Caller exact text says **NV đã đầy 30/30 → dừng trừng ác cho acc này**. Constructor owns `_punish_skipped`, and an `add` constant occurs immediately after this terminal branch, strongly binding 30/30 to terminal per-account Trừng Ác skip/stop tracking. Exact mutation order versus row stop Event remains UNKNOWN.
- Stuck/no-target cancellation is a separate recovery helper `_punish_cancel_quest`: close current panel at **(1072,130)**; `move_to_npc(map 4, npc 698)`; then click **(479,480) → (476,422)**. Exact success text says **đã gửi hủy nhiệm vụ → sang vòng mới**.
- Shared `memory_items.move_to_npc` exact docs confirm NPC position lookup, movement, `ClickNPC`, GameDialog verification, and fallback to game NPC navigation when cross-map/no live NPC position. K04 uses that shared evidence only because the cancellation helper directly calls it.
- No-target log is **không bóc được tọa độ mục tiêu → hủy NV rồi sang vòng mới**. Cancellation failure logs but has no terminal-account stop surface; strongest static contract is fail-soft/current-cycle skip and retry on the next outer Trừng Ác iteration.
- Repeated target failure can also trigger quest cancellation through `_punish_target_fail` and “kẹt ... vòng liên tiếp → hủy NV”. Exact threshold/accounting is deliberately deferred to K05.
- B08 was only cross-checked after static extraction and contains no quest-dialog runtime evidence.
- Packaged runtime log contains no correlated K04 quest/NPC/full/cancel markers. K04 remains **STATIC_VERIFIED / END_TO_END_RUNTIME_ENV_REQUIRED**.
- Missing K04 evidence artifact was added and K04 is now complete.

## K04 FILES
- docs/tasks/K04.md
- docs/daily/K04_PUNISH_QUEST_FLOW.md
- docs/daily/K04_PUNISH_QUEST_MODEL.json
- docs/daily/K04_PUNISH_QUEST_STATIC_EVIDENCE.tsv


## CURRENT REPOSITORY AUDIT — 2026-10-07
- A full GitHub-tree continuity audit was run because continuation appeared stalled.
- Current repository has **563 entries** and remains a research/reconstruction evidence repository, not yet the reconstructed application source tree.
- Authoritative continuity was consistent before K05: PLAN/STATE/PROJECT_STATUS showed K01-K04 complete and K05 as the first unfinished task. GitHub search found no pre-existing K05 artifact/commit, so no completed Daily work was redone.
- Current code-bearing research tools are the seven static forensic scripts under `tools/D01...D07`; they were not modified by this recovery.
- No reconstructed application build target currently exists: no `src/` app tree, no app `pyproject.toml/setup.py/requirements`, no reconstructed-app `.spec`, and no GitHub Actions build workflow were found.
- Therefore product build status at this phase is **NOT_APPLICABLE_YET / STAGE S NOT STARTED**, not “broken”. It would be incorrect to claim a successful reconstructed-app build before an app source/build system exists.
- This is consistent with PLAN/SCOPE_LOCK: Stage S implementation remains intentionally locked until later research gates.
- Recovery action was docs/evidence-only, so no product source/build pipeline could be regressed by K05.
- Persistent audit artifact: `docs/audits/CURRENT_REPO_AUDIT_2026-10-07.md`.

## K05 VERIFIED RESULTS
- GitHub-first check passed: no K05 artifacts existed before this work; K01-K04 were not rewritten.
- Exact frozen original archive/EXE were revalidated before analysis. Inner EXE SHA-256 remains `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, size **47,450,112** bytes.
- Exact Trừng Ác Lệnh item constant is **40004000**.
- `_punish_goto_target` reads the internal bag through `memory_items.get_bag`, finds the matching item row and uses its `dbID`; no screen/image bag search belongs to this path.
- Shared `memory_items.use_item` is the internal item-action path: command **100005**, action **3**, payload `3:<dbID>`; it does not click the visible bag GUI.
- Missing Trừng Ác Lệnh at the **target-acquisition** stage is terminal for that account's current Trừng Ác session. Exact frozen text is `túi không có Trừng Ác Lệnh → dừng acc`.
- First item use has exactly **2 total send attempts**. The block owns `_att/_used` and exact `... thất bại lần ... /2`; exhausting both attempts is fail-soft to the current cycle: `gửi lệnh dùng thất bại → skip vòng`.
- Target extraction priority is exact: `memory_items.get_dialog_target` first, then `memory_items.get_use_item_target` fallback. If neither yields a usable target, Daily calls K04 `_punish_cancel_quest` and proceeds to a later outer cycle.
- Shared GameDialog target parser uses the exact shape `- <TargetName> ở <MapName> (<PosX>, <PosY>)` and returns `MapID/PosX/PosY/TargetName/MapName/Title/Buttons`.
- UseItemData fallback queries current doing tasks and task-template `UseItemData`, matching `ItemID == requested item id`, and returns `MapID/PosX/PosY`. It is live task metadata, not a hard-coded Trừng Ác target table.
- Daily reads `MapID/PosX/PosY`, optional `TargetName`, and falls back to label `mục tiêu`. Exact coordinate-range predicate remains UNKNOWN.
- Target travel is owned by `fast_travel.goto_map`, with exact tag `TrừngÁc` and keyword surfaces `wait_for_arrival/stop_check/tag`.
- Shared fast_travel docs state its coordinate convention is pixels where pixel = tile×32. Daily logs target coordinates as `tile=(...)`, but the exact Daily source expression performing tile→pixel conversion is not instruction-bound, so K05 keeps that arithmetic expression UNKNOWN.
- Travel stopped by session cancellation logs `bay tới mục tiêu bị stop (...)` and returns/skips. Ordinary travel failure logs `bay tới mục tiêu thất bại → skip vòng`, invokes `stop_character`, updates target-failure tracking, and skips the cycle.
- Important correction: `_punish_target_fail` is **not** recovered as a qualified DailyTab method. It is the target-failure state/attribute used by `_punish_goto_target`.
- Exact target-failure locals are `_tkey/_d/_last/_streak`; default prior state is **(None, 0)**. Strong static contract is consecutive-failure tracking for the same target, with changed target resetting/rebasing the streak.
- Exact stuck log is `kẹt <...> vòng liên tiếp → hủy NV`; the recovery then uses K04 quest cancellation and a `pop` reset surface.
- The **numeric stuck threshold is not statically resolved** and is frozen as `EXPLICIT_UNKNOWN`; no 2/3/etc. value is guessed.
- Summon `_punish_summon_target` reads the bag again and reuses the same item 40004000.
- Important outcome difference: no item during target acquisition is terminal to the account, while no item during **summon** logs `túi không còn Trừng Ác Lệnh → skip vòng` and only skips the current cycle.
- Summon use failure/error is also current-cycle skip. Unlike target acquisition, no `/2` retry surface or `_att` local is recovered in summon, so K05 does not invent a two-attempt summon retry.
- Frozen summon documentation expects GameDialog title **Trừng Ác Lệnh** with buttons **[2] Triệu hồi / [3] Để sau**. The executable definitely scans button text **Triệu hồi**.
- Summon dialog missing/read error/button missing/click failure all skip the current cycle.
- `Triệu hồi` activation uses shared `memory_items.click_dialog_button`: exact internal `GameDialog:FunctionButtonClicked` path with verified dialog close, not a screen-coordinate click.
- B08 contains no target/summon runtime evidence. Packaged runtime log contains no correlated K05 markers, so K05 is **STATIC_VERIFIED / END_TO_END_RUNTIME_ENV_REQUIRED**.

## K05 FILES
- docs/tasks/K05.md
- docs/daily/K05_PUNISH_TARGET_FLOW.md
- docs/daily/K05_PUNISH_TARGET_MODEL.json
- docs/daily/K05_PUNISH_TARGET_STATIC_EVIDENCE.tsv


## K06 VERIFIED RESULTS
- GitHub-first continuity check passed: no K06 artifact/completion commit existed before this work; K01-K05 were already complete and were not redone.
- The exact frozen original archive was re-materialized from the user's Library and verified before any screenshot cross-check. Archive SHA-256 remains `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, size **93,715,901** bytes. Inner `TLMTool.dist/TLMTool.exe` remains SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, size **47,450,112** bytes.
- The successful K05 summon transitions into the combat segment of `DailyTab._punish_exec_sequence`. Exact combat state/text is **Đánh ác tặc**.
- `punish_duration` is bound to an elapsed-time fight window through local `_t_end` plus `monotonic`; it is not a run-count. Exact inner fight polling/sleep quantum remains **EXPLICIT_UNKNOWN**.
- Exact combat text **chết giữa lúc đánh → dừng đánh sớm** proves death/respawn state can terminate the fight window before its deadline.
- Daily directly calls shared `start_auto_train` with keyword-name surface `stop_check/verify`. Shared helper defaults are exactly `(None, True, 3, 1.0, 2)`: verify enabled by default, 3 Direction samples, 1.0-second interval, 2 retries = **3 total send attempts**.
- Shared Direction verification semantics are locked: any valid Direction change = True; all valid samples identical = False; insufficient valid samples = None/fail-open. The exact Boolean value explicitly supplied by the Daily combat call for `verify=` is not instruction-bound and remains **EXPLICIT_UNKNOWN**.
- Exact Daily failure behavior is **fail-soft**: `gửi bật auto train thất bại → vẫn đánh tiếp`. Do not turn this into a hard abort.
- The bounded Daily payload contains no recovered `stop_game_auto`, `set_game_auto`, `AUTO_MODE_NONE`, or `stop_auto_train` combat-tail surface. Shared movement code can stop auto later, but K06 recovers **no explicit Daily combat-end auto-off call**.
- Combat stores a fight-position anchor, compares later Map/X/Y state, uses `math.hypot`, and has an exact drift threshold of **160 pixels**. Exact log says the character has moved away from the fight area and suspects party-follow/PK displacement.
- No direct Daily relocation helper or combat-tail auto-off is recovered alongside the 160-pixel detector. The exact Python return-value effect of the >160px branch remains **EXPLICIT_UNKNOWN** instead of being guessed.
- The combat tail contains the final HP/heal boundary and exact failure surface `Heal cuối vòng thất bại`; heal/reconnect/respawn internals remain K07.
- Normal tail reaches exact **Kết thúc** text and returns control to the already-proven K03 open-ended Trừng Ác worker. Exact normal-success Python return scalar remains **EXPLICIT_UNKNOWN**.
- `DailyTab._wait_movement_stopped` was audited without inventing a Trừng Ác call edge. Its recovered trailing defaults are `(None, None, False)`, so `by_memory` defaults **False**.
- Its memory branch calls shared `wait_stopped_by_direction` with explicit 300-second timeout. Shared defaults are exactly: timeout **300s**, stable_needed **6**, interval **0.5s**, move_eps **16px**. Stable MapID/PosX/PosY for 6 polls (~3s) means stopped; movement/map change resets stability; stop/timeout returns False.
- The non-memory branch exposes the older **MovementDetector 10-pixel** path. Post-stop hung-window checking exposes `is_window_hung`, `HUNG_TIMEOUT`, and `DailyTab.WindowHungError`; numeric `HUNG_TIMEOUT` remains **EXPLICIT_UNKNOWN**.
- Important call-site boundary: the explicit `_wait_movement_stopped` call recovered from the compact Daily constants is in the **Tàng Bảo Đồ** block, with `stop_check/skip_set` keyword names and no visible `by_memory` override. A direct call from the Trừng Ác combat block was not recovered. Do not insert this helper into Trừng Ác combat merely because it exists.
- Only after static extraction, the user-re-supplied Daily screenshots were matched against the frozen B08 hashes `217178561894a4205c7b5835ed33c050b384c8f60359f6894165e3400d514834` and `3939691e166fa67d9c50069119e4e3904496cd6769b04cf0d3199c6b3e0f866b`. They confirm only the visible clean baseline **Thời gian đánh ác tặc (giây): 15** and provide no live combat evidence.
- Exact packaged `data/automove_log.txt` remains SHA-256 `17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`, 15,741,058 bytes. It contains **0 correlated Daily/K06 markers** for Trừng Ác combat. It does contain **8,511** generic `AutoFight_Main` records, including **6,102** `:Start` records; these prove only the lower-level primitive was exercised somewhere, not Daily/K06 end-to-end behavior.
- K06 classification is **STATIC_VERIFIED / END_TO_END_RUNTIME_ENV_REQUIRED**.
- Stage S application reconstruction has not started, so reconstructed-product build verification remains **NOT_APPLICABLE_YET**, not failed.

## K06 FILES
- docs/tasks/K06.md
- docs/daily/K06_PUNISH_COMBAT_FLOW.md
- docs/daily/K06_PUNISH_COMBAT_MODEL.json
- docs/daily/K06_PUNISH_COMBAT_STATIC_EVIDENCE.tsv

## BLOCKERS
- Phase J live runtime parity remains deferred by environment.
- K06 end-to-end Daily combat runtime parity still requires a real Windows + live Thần Long runtime; packaged generic AutoFight traffic is not correlated proof.
- Reconstructed application build verification is not applicable yet because Stage S/application source has not started and no product build target exists.
- No known static blocker for K07.

## DO_NOT_TOUCH
- Preserve K01-K06 Daily/Trừng Ác contracts unchanged.
- Preserve the K05 successful-summon → K06 combat transition.
- Preserve `punish_duration` as a monotonic elapsed-time combat window, not a configured run-count.
- Preserve auto-train enable failure as fail-soft: the fight window continues.
- Do not invent an explicit Daily combat-end auto-off call.
- Preserve the exact **160-pixel** drift detector, but do not invent a relocation action or exact branch return semantics.
- Do not insert `_wait_movement_stopped` into Trừng Ác combat merely because the helper exists; the explicit recovered Daily call belongs to the Tàng Bảo Đồ block.
- Keep Daily's explicit `verify=` value, fight-loop polling quantum, exact hard-stop Boolean composition, normal-success return scalar, drift-branch return effect, and numeric `HUNG_TIMEOUT` as explicit UNKNOWNs.
- TLMTool 2.1.2 remains sole authority; do not import recovery/combat logic from older Auto-BTD/Trừng Ác projects.
- Do not deep-audit K08 discard during K07 except for a dependency strictly required by recovery handoff.
- Do not start Stage S or create placeholder application/build files before PLAN reaches implementation.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md.
2. Read STATE.md.
3. Check GitHub first for any K07 artifacts/commits; if already complete and verified, do not redo them.
4. Execute **K07 — Trừng Ác heal / reconnect / respawn recovery audit** only.
5. Re-inspect the exact frozen original EXE first, primarily `_punish_heal`, `_punish_disconnect_monitor`, `_diaphu_monitor`, and only the `_punish_single_worker/_punish_run_worker` recovery edges directly needed to understand handoff/resumption.
6. Audit HP<30 start/end heal triggers, Tô Châu treatment routing, reconnect detection/wait/reinject/cache/memory-ready boundaries, HP0/Map87/Địa phủ respawn-event behavior, terminal versus fail-soft retry boundaries, and how successful recovery resumes the next Trừng Ác cycle.
7. Preserve K06 combat/movement-helper contracts unchanged; do not reopen auto-train or movement-stop research unless a direct recovery dependency requires it.
8. Do not deep-audit **K08 — Trừng Ác discard worker**.
9. Cross-check B08/screenshots only after EXE/static extraction; the screenshots show recovery configuration controls but no live recovery state.
10. Persist K07 artifacts, update STATE.md/PROJECT_STATUS.md, and advance only after K07 verification.

## K07 STATIC EXTRACTION MILESTONE — IN PROGRESS
- GitHub-first continuity check passed: no pre-existing K07 artifacts or K07 completion commit existed; K01-K06 were not redone.
- Re-inspected the newly supplied exact archive `TLMTool_2.1.2(7).zip` first. Archive SHA-256 is still `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, size **93,715,901** bytes. Inner `TLMTool.dist/TLMTool.exe` remains SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, size **47,450,112** bytes.
- The exact `.daily_tab` Nuitka constant blob was fully decoded: **35,163 bytes / 1,186 top-level constants**, ending exactly at the next blob boundary. K07 evidence was extracted from that blob plus directly-called shared `.utils`, `.memory_items`, and frozen `.pixel_data` constants.
- Recovery surfaces now statically frozen: `DailyTab._diaphu_monitor`, `DailyTab._punish_disconnect_monitor`, `DailyTab._punish_heal`, and the K07 edges in `_punish_single_worker/_punish_run_worker/_punish_exec_sequence`.
- Death monitor evidence is exact: 4-second cadence, HP0 revive click **(792,441)**, MapID **87** sets `respawn_event`, and the cycle-start recovery branch clears that event so heal/move can leave map 87.
- Disconnect detector evidence is exact: 2-second cadence, memory-connected True veto, both `login.ngatKetNoi1+2` pixels, 3 consecutive ticks (~6s), then `halt` + click **(616,455)**.
- Daily recovery is intentionally not being conflated with Train/TrainLSV: no Daily `/5` reconnect-attempt or infinite-retry surface is recovered. The activity-wide Trừng Ác recovery path explicitly proves a **60-second** reconnect wait with OK→continue / timeout→stop.
- Single-account Trừng Ác recovery directly proves `wait_pixel(common.active)`, Reader-cache invalidation and `wait_memory_ready(timeout=45.0, need=3)`; shared effective memory-ready interval is **1.0s** and timeout is fail-open. Exact single-worker active-wait numeric timeout is not independently instruction-bound.
- Low-HP treatment edges are exact: HP<30 check at cycle start and cycle end; start-heal failure skips the current cycle; final-heal failure is logged at the cycle tail. `_punish_heal` re-inject failure is fail-open to direct movement, uses Tô Châu treatment coordinates from the frozen table **(155,252)** and an exact movement tolerance **10**.
- No unconditional forced post-reconnect DLL reinjection edge is proven in the single-worker recovery block; do not invent one. Later heal/NPC movement helpers independently perform their own guarded reinjection attempts.
- First K07 artifact committed: `docs/daily/K07_RECOVERY_STATIC_EVIDENCE.tsv` at commit `07653a3f926ced5f5034646cbba2fbb1870ff0c6`.
- K07 remains **IN_PROGRESS** until flow/model/task documents, runtime/image cross-check summary, STATE closure, and PROJECT_STATUS advancement are persisted.

## K07 INTERIM NEXT_ACTION
1. Persist K07 recovery flow/model/task artifacts from the completed EXE-first extraction.
2. Preserve Daily-specific reconnect policy; do not copy Farm/TrainLSV 5-attempt infinite reconnect logic.
3. Cross-check B08 only as visible recovery-control state, after static extraction.
4. Cross-check packaged automove_log only for correlated K07 runtime traces; generic unrelated logs are not proof.
5. Close K07 in STATE.md and PROJECT_STATUS.md, then advance NEXT_ACTION to K08.

## K07 VERIFIED RESULTS
- GitHub-first continuity check passed: no K07 artifact/completion commit existed before this work; K01-K06 were already complete and were not redone.
- The newly supplied `TLMTool_2.1.2(7).zip` was revalidated first. Archive SHA-256 remains `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, size **93,715,901** bytes. Inner `TLMTool.dist/TLMTool.exe` remains SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, size **47,450,112** bytes.
- The exact `.daily_tab` Nuitka constant blob was fully decoded and consumed exactly: **35,163 bytes / 1,186 top-level constants**. K07 used that Daily authority plus directly-called shared `.utils`, `.memory_items`, and frozen `.pixel_data`.
- Trừng Ác recovery settings are frozen as three separate controls: low-HP treatment, reconnect, and death/Địa-phủ respawn. Settings-load fallbacks are `daily_punish_heal="0"`, `daily_punish_dc_reconnect="1"`, and `daily_punish_respawn="1"`. B08 current captured state has all three controls checked; current screenshot state is not treated as a fresh-install default.
- `DailyTab._diaphu_monitor` is exact: **4-second** cadence; HP0 uses state surface `Về Địa phủ` and exact revive click **(792,441)**; MapID **87** sets `respawn_event`. Locals `hp_latched` and `detected` prove duplicate-suppression latches exist; exact re-arm expressions remain UNKNOWN.
- The Trừng Ác execution cycle consumes death recovery instead of terminally stopping: exact entry text says `respawn_event đang set → clear, cho heal/move rời map 87`. Combined with K06's death-early-break, death/Map87 is a recoverable cycle transition.
- Start-of-cycle HP treatment is exact: read `HpPercent`; when treatment is enabled and HP<30%, call `_punish_heal`. Exact failure text `Heal thất bại → skip vòng này` makes start-heal failure current-cycle fail-soft, not terminal account stop.
- The combat tail has a second HP-treatment check and exact `Heal cuối vòng thất bại` text. No independent terminal-account stop surface is attached to final-heal failure.
- `DailyTab._punish_heal` is bound to the frozen Tô Châu treatment coordinate surface: **map 4, tile (155,252)**. Its movement kwargs are `wait_for_arrival/stop_check/tolerance`; exact tolerance is **10**.
- Treatment injection repair is fail-open: exact text `inject cho heal thất bại, thử di chuyển trực tiếp`. Injection failure does not terminate treatment before a direct movement attempt.
- Daily's manual treatment helper independently has exact clicks **(892,474)** and **(514,424)**, but readable static evidence does not independently bind those same two clicks inside automatic `_punish_heal`; automatic treatment-click microsequence remains EXPLICIT_UNKNOWN rather than being copied by analogy.
- `DailyTab._punish_disconnect_monitor` is exact: **2-second** per-account cadence; it exits on dead/reused window identity instead of reconnecting a stale HWND.
- Daily directly uses `memory_items.is_connected`, whose shared exact semantics are TCPGame `Connected`: True=connected, False=disconnected, None=read error. Daily's own doc binds memory True as a false-positive veto/reset, not as the sole disconnect detector.
- Frozen disconnect probes were directly decoded from `.pixel_data`:
  - `login.ngatKetNoi1`: **(640,244)**, RGB **(160,145,52)**, timeout 5, tolerance 5.
  - `login.ngatKetNoi2`: **(702,453)**, RGB **(212,28,34)**, timeout 5, tolerance 5.
- Both disconnect pixels must persist for **3 consecutive 2-second ticks** (~6s). Exact confirmed text is `MAT KET NOI (dialog 3/3) → halt`; exact reconnect click is **(616,455)**.
- Important Daily-specific correction: no `/5` reconnect counter, five-attempt batch, 30-second retry-batch delay, or infinite retry scheduler is recovered in Daily. Do **not** import H08/I08 Farm reconnect semantics into K07.
- Activity-wide Trừng Ác recovery owns nested `_punish_monitor_stops`: state `Mất kết nối`, exact **60-second** reconnect wait, exact success `Kết nối lại OK → tiếp tục`, exact failure `Kết nối lại timeout → dừng`.
- The single-account/per-row Trừng Ác worker owns separate state `Chờ kết nối lại` and directly calls `wait_pixel("common","active",...)`. Exact call metadata proves interval constant **0.5** and kwargs `window_hwnd/timeout/interval/debug`. Frozen `common.active` is **(1330,33)** RGB **(34,8,11)** tolerance 5. The activity-wide path proves Daily's 60s timeout; the single-worker numeric timeout is a strong 60s inference but not independently native-instruction-bound.
- Single-worker reconnect success directly includes `invalidate_character_cache`, current-PID resolution, and `wait_memory_ready(timeout=45.0, need=3)`.
- Shared `wait_memory_ready` defaults are exactly **(45.0,3,1.0)**. Daily overrides timeout/need only, so the effective sampling interval is **1.0s**. A valid sample requires a clear RoleName and MapID != None, and the Reader cache is invalidated before each sample.
- Memory-ready timeout is fail-open: exact shared docs say timeout returns False/logs and lets the caller continue rather than wedging automation indefinitely.
- No unconditional forced post-reconnect DLL reinjection edge is proven in the Daily single-worker recovery block. Do not invent one. Later `_punish_heal` and `_punish_goto_bodau` independently perform their own guarded reinjection attempts before movement.
- Only after static extraction, frozen B08 evidence was cross-checked. It confirms the currently captured Daily recovery controls and Tô Châu location, but contains no live reconnect/death/heal runtime behavior.
- Exact packaged `automove_log.txt` remains SHA-256 `17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`, 15,741,058 bytes / 387,238 text lines. Correlated K07 markers for Trừng Ác, disconnect, MemReady, Địa phủ, HP0, heal failure, reconnect OK/timeout, and the reconnect/revive coordinate strings all returned **0**.
- K07 classification is **STATIC_VERIFIED / END_TO_END_RUNTIME_ENV_REQUIRED**.
- Stage S reconstructed application source has not started, so product build verification remains **NOT_APPLICABLE_YET**, not failed.

## K07 FILES
- docs/tasks/K07.md
- docs/daily/K07_RECOVERY_FLOW.md
- docs/daily/K07_RECOVERY_MODEL.json
- docs/daily/K07_RECOVERY_STATIC_EVIDENCE.tsv

## BLOCKERS
- Phase J live runtime parity remains deferred by environment.
- K06 and K07 end-to-end Daily runtime parity require a real Windows + live Thần Long environment; no packaged correlated Daily trace exists.
- Reconstructed application build verification is not applicable yet because Stage S/application source has not started and no product build target exists.
- No known static blocker for K08.

## DO_NOT_TOUCH
- Preserve K01-K07 Daily/Trừng Ác contracts unchanged.
- Preserve Daily-specific reconnect behavior; do not copy Train/TrainLSV's five-attempt/infinite retry scheduler into Daily.
- Preserve 4s death monitor, revive click (792,441), Map87 respawn_event, and cycle-entry clear/recovery semantics.
- Preserve HP<30 treatment at cycle start/end, start-heal fail-soft skip, Tô Châu map4 tile (155,252), movement tolerance 10, and fail-open injection repair.
- Do not copy manual treatment clicks into automatic `_punish_heal` until stronger evidence binds them.
- Preserve 2s disconnect monitor, memory True veto, both exact disconnect pixels, 3-strike confirmation, and reconnect click (616,455).
- Preserve activity-wide exact 60s reconnect wait. Keep the single-worker numeric timeout as strong-static/not independently instruction-bound.
- Preserve post-reconnect Reader-cache invalidation and `wait_memory_ready(45,3)` with effective 1.0s interval and fail-open timeout.
- Do not invent unconditional post-reconnect DLL reinjection.
- Keep exact setting-gate placement, latch reset expressions, automatic-heal click microsequence, single-worker timeout binding, reconnect failure unwind micro-order, same-scheduling-window death/disconnect ordering, and live runtime parity as explicit UNKNOWNs.
- TLMTool 2.1.2 remains sole authority.
- Do not start Stage S or create placeholder app/build files before PLAN reaches implementation.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md.
2. Read STATE.md.
3. Check GitHub first for any K08 artifacts/commits; if already complete and verified, do not redo them.
4. Execute **K08 — Trừng Ác discard worker / equipment filtering and discard lifecycle audit** only.
5. Re-inspect the exact frozen original EXE first, primarily `_toggle_punish_discard`, `_start_punish_discard`, `_stop_punish_discard`, `_punish_discard_worker`, `_punish_discard_one`, and only directly-called `bag_filter/memory_items` helpers required by that path.
6. Audit checkbox/config gating, generation/thread ownership, active-account scope, inventory/equipment filter semantics, packet/action used for discard, pacing/retry/inflight protection, stop behavior, and whether discard is run-scoped or persists across Trừng Ác cycles.
7. Preserve K01-K07 contracts unchanged; do not reopen reconnect/heal/combat unless a direct discard dependency requires it.
8. Do not start Tàng Bảo Đồ K10+ work.
9. Cross-check B08 only after static extraction; B08 shows the discard checkbox but no discard runtime behavior.
10. Persist K08 artifacts, update STATE.md/PROJECT_STATUS.md, and advance only after K08 verification.

## CURRENT CODE/BUILD AUDIT — 2026-10-07 16:36 +07
- User explicitly requested a full current-code audit before continuing.
- GitHub tree was re-read from current `main`: **577 entries**.
- Current code-bearing repository content is exactly **7 Python forensic scripts + 1 shell forensic verifier** under `tools/`; all were fetched in full and reviewed. No blocking source defect was found. One non-blocking cleanup issue exists: unused `defaultdict` import in `D04_BUILD_INTERNAL_GRAPH.py`; it was intentionally left unchanged.
- No application `src/` tree, reconstructed TLMTool/tab source, `pyproject.toml`, setup/requirements file, Nuitka spec, Make/CMake target, or GitHub Actions workflow exists.
- Latest pre-audit commit had **0 CI statuses** and **0 workflow runs**. Product build verification is therefore **NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED**, not a failed build. PLAN explicitly defers source reconstruction to Stage S and Nuitka build to Stage T.
- The newly supplied `TLMTool_2.1.2(7).zip` passed the exact A08 forensic contract: SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, CRC clean, 1050 entries / 1002 files / 48 dirs / 260,061,035 uncompressed file bytes.
- K01-K07 were reclassified as already-correct/complete and were not rewritten.
- First unfinished work remains exactly **K08 — Trừng Ác discard worker / equipment filtering and discard lifecycle audit**.
- Persistent audit file: `docs/audits/CURRENT_CODE_BUILD_AUDIT_2026-10-07_1636.md` (commit `2e1b29481b491a77c6c93a76ca7a813e5982ce02`).
- No code/build regression was introduced by the audit because it added documentation only.

## K08 AUDIT START
- K08 is now the active task.
- Preserve K01-K07 unchanged.
- Do not create Stage-S placeholder application/build files just to manufacture a build result.

## K08 STATIC EXTRACTION MILESTONE — IN PROGRESS
- Full current-code/build audit was completed first and persisted; K01-K07 were not rewritten.
- Re-inspected exact TLMTool_2.1.2(7).zip and inner EXE before K08 analysis.
- Fully decoded exact .daily_tab (**35,163 bytes / 1,186 constants**), .bag_filter (**5,162 bytes / 145 constants**), and directly-needed .memory_items evidence.
- K08 worker ownership is frozen: punish_discard_equip_var, _punish_discard_stop, _punish_discard_thread, _punish_discard_gen.
- Checkbox/config contract is exact: visible "Lọc trang bị (vứt vũ khí, trang bị trong quá trình làm nhiệm vụ)", persisted key daily_punish_discard_equip, load fallback **"0"**. B08 current captured state is OFF.
- Exact toggle contract: ON + running Trừng Ác accounts starts worker; ON + no running accounts waits until account start; OFF stops worker immediately; worker rechecks tick; config is saved.
- Worker scope is only current running Trừng Ác HWNDs, explicitly excluding stopped/disconnected rows.
- Worker runs one child thread per active account in parallel. Exact doc says packet pacing is 1 second inside each account; per-account inflight prevents a new discard pass when the prior pass for that account is still running.
- Worker passes activity="daily", preset key discard_equip, and kwargs keys/delay/stop_check to shared bag_filter.discard_for_activity.
- Daily discard_equip semantic is exact from worker doc: discard all non-weapon equipment + weapons, same equipment preset as Phó Bản.
- Shared bag_filter is opt-in: empty/no keys means no scan/no packet; rules are OR, fields inside a rule are AND; Site10 is default; dbID targets are deduplicated; weapons are protected unless an explicit weapon rule is used; protected IDs/names have highest priority.
- Shared discard defaults prove **1.0 second** pacing, stop-aware early termination, per-HWND send-lock surfaces, and action **4** abandon packet 100005 "4:dbID". The action discards the full stack in that slot.
- Important degradation surface: if embedded/item metadata is missing, non-weapon matching can drop out; the exact bag_filter warning says only weapon-ID discard remains. This is not silently “fixed” in parity work.
- DAILY_DISCARD_POLL symbol and periodic-worker contract are proven, but its numeric value is **EXPLICIT_UNKNOWN**; no guessing.
- Exact generation state/captured gen is proven; exact increment/event/thread replacement statement order remains **EXPLICIT_UNKNOWN**.
- Packaged runtime log contains **22,734** generic action=4 records (22,732 spts + 2 plain) but **0 Daily/Trừng Ác/discard-correlated markers**. These validate the low-level packet primitive only, not K08 end-to-end behavior.
- First K08 artifact committed: docs/daily/K08_PUNISH_DISCARD_STATIC_EVIDENCE.tsv (commit b82181bc38c66bedcda66d6c49ec7e53fa2903be).
- K08 remains IN_PROGRESS until flow/model/task docs, B08/runtime cross-check summary, STATE closure and PROJECT_STATUS advancement are persisted.

## K08 VERIFIED RESULTS
- Full current-code/build audit was performed before K08 per user instruction. K01-K07 were confirmed already-correct and were not rewritten.
- Exact frozen TLMTool_2.1.2(7).zip remains SHA-256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd, size **93,715,901** bytes; inner TLMTool.dist/TLMTool.exe remains SHA-256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22, size **47,450,112** bytes.
- Current repository code audit found exactly **7 Python forensic scripts + 1 shell verifier**, no reconstructed application source/build target, no CI workflow, and no blocking source defect. Product-build classification remains **NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED**, not failed. K08 changed docs/evidence only.
- Exact .daily_tab blob was decoded as **35,163 bytes / 1,186 constants**; exact .bag_filter blob as **5,162 bytes / 145 constants**; directly-needed .memory_items packet constants were also decoded.
- Visible/persisted K08 control is "Lọc trang bị (vứt vũ khí, trang bị trong quá trình làm nhiệm vụ)" / punish_discard_equip_var / config key daily_punish_discard_equip; load fallback is **"0"**. B08 current captured state is OFF.
- K08 is a separate run/session-level background subsystem with _punish_discard_stop, _punish_discard_thread, _punish_discard_gen; it is **not** a once-per-_punish_exec_sequence action.
- Exact toggle behavior: ON + running Trừng Ác account → start worker; ON + no running account → remain armed and wait for a later Trừng Ác start; OFF → stop worker immediately; worker rechecks checkbox state; config is saved.
- _punish_running_hwnds scopes the worker only to currently-running Trừng Ác HWNDs and excludes stopped/disconnected rows.
- Exact worker contract: every DAILY_DISCARD_POLL interval, active Trừng Ác accounts are processed **in parallel**, one child thread per account. Numeric DAILY_DISCARD_POLL is **EXPLICIT_UNKNOWN** and was not guessed.
- Per-account inflight protection is exact: if the previous discard pass for one account is still running, skip that account for the current worker tick rather than overlap it. Other accounts can still proceed.
- Worker calls bag_filter.discard_for_activity with activity daily, preset key discard_equip, and keyword surface keys/delay/stop_check.
- Exact Daily preset semantic is **all non-weapon equipment + weapons**, same equipment preset meaning as Phó Bản; this is deliberately opt-in/dangerous and is not a keep-weapons mode.
- Shared bag_filter contract is frozen: empty/no keys means no scan/no packet; Site 10 default; fields inside a rule are AND, multiple rules OR; targets dedupe by dbID; weapons protected by default unless explicit weapon matching is enabled; protected IDs/names have highest priority.
- Original degradation behavior is preserved: if embedded/item metadata is unavailable, non-weapon matching can drop out while weapon-ID filtering still works. This is not silently fixed during parity.
- Shared discard ultimately uses internal memory_items.abandon_item: command **100005**, action **4**, payload **4:<dbID>**, discarding the **full stack** in that bag slot. No visible bag GUI click belongs to this path.
- Shared discard defaults and Daily worker docs independently lock **1.0-second** per-account packet pacing. Daily passes stop_check, so a long pass can stop early between item actions when the feature/session is stopped.
- bag_filter also owns lower-level per-HWND send locks (_SEND_LOCKS_GUARD/_SEND_LOCKS/_send_lock_for). Preserve these in addition to Daily's inflight layer.
- No immediate action-4 retry loop is recovered. Current-pass failures are counted/returned; later periodic scans may encounter still-present items again.
- One-account child errors are fail-soft/account-local. A worker-level error surface also exists, but exact unexpected outer-exception continue-vs-exit micro-order is **EXPLICIT_UNKNOWN**.
- Generation state/captured gen is proven, but exact generation increment / stop-event / thread-replacement statement ordering remains **EXPLICIT_UNKNOWN**.
- Only after static extraction, B08 was cross-checked. It confirms the discard checkbox is OFF in the captured state and provides no runtime discard evidence.
- Packaged automove_log.txt has **22,734 generic action=4 records** (22,732 spts + 2 plain), proving the low-level discard primitive was exercised somewhere. It contains **0 correlated Daily/K08 markers** for [Trừng ác], lọc trang bị, DAILY_DISCARD_POLL, discard_for_activity, or discard_equip; end-to-end K08 runtime provenance is therefore not claimed.
- K08 classification is **STATIC_VERIFIED / END_TO_END_RUNTIME_ENV_REQUIRED**.

## K08 FILES
- docs/tasks/K08.md
- docs/daily/K08_PUNISH_DISCARD_FLOW.md
- docs/daily/K08_PUNISH_DISCARD_MODEL.json
- docs/daily/K08_PUNISH_DISCARD_STATIC_EVIDENCE.tsv
- docs/audits/CURRENT_CODE_BUILD_AUDIT_2026-10-07_1636.md

## BLOCKERS
- End-to-end Daily parity still requires a real Windows + live Thần Long runtime.
- Reconstructed application build remains not applicable until Stage S source exists; no product build target exists yet by design.
- No known static blocker for K09.

## DO_NOT_TOUCH
- Preserve K01-K08 contracts unchanged.
- Preserve discard as a run-scoped background subsystem, not a per-cycle tail action.
- Preserve current-running-Trừng-Ác-only scope and exclusion of stopped/disconnected accounts.
- Preserve parallel-account fanout + per-account inflight protection + lower-level per-HWND bag_filter send locks.
- Preserve daily + discard_equip preset semantics including weapon discard.
- Preserve packet 100005 action 4 / full-stack behavior and 1-second pacing.
- Preserve original metadata-degradation behavior; do not silently replace it with a new classifier.
- Do not invent an immediate retry loop or a numeric DAILY_DISCARD_POLL.
- Keep generation mutation ordering and worker outer-exception micro-order UNKNOWN.
- TLMTool 2.1.2 remains sole authority.
- Do not start Stage S before PLAN reaches implementation.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md.
2. Read STATE.md.
3. Check GitHub first for any K09 artifacts/commits; if already complete and verified, do not redo them.
4. Execute **K09 — Trừng Ác integrated lifecycle / failure matrix / static handoff audit** only.
5. Re-inspect the exact frozen original EXE and K03-K08 persisted evidence first; do not re-research already-closed details unless a contradiction appears.
6. Build the integrated Trừng Ác state/failure matrix: terminal per-account stops vs current-cycle skips vs fail-soft/log-only vs recoverable reconnect/death transitions; batch vs single-account orchestration; discard worker scope; UI reset/stop handoff; and any remaining Trừng Ác callable not yet accounted for.
7. Identify contradictions/UNKNOWNs across K03-K08 and correct only real conflicts; do not rewrite correct artifacts.
8. Close the Trừng Ác static handoff only if every K03-K08 surface is internally consistent. K10 remains the first Tàng Bảo Đồ task afterward.
9. Re-check current repository code/build state after K09 changes; docs-only work must not create a fake Stage-S build target.
10. Persist K09 artifacts, update STATE.md/PROJECT_STATUS.md, and advance only after K09 verification.

## POST-K08 CODE/BUILD RECHECK
- Current main tree after K08 closure: **582 entries**.
- Python code files remain exactly the same 7 forensic scripts under tools/; K08 added no executable source.
- Application source paths remain absent.
- Build-system files/workflows remain absent.
- Latest K08 closure commit has **0 CI statuses** and **0 workflow runs**, consistent with the repository having no CI/build target yet.
- All four K08 artifacts were fetched back successfully after commit.
- Therefore K08 introduced no code/build regression. Product build remains **NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED** rather than PASS/FAIL.

## K09 STATIC HANDOFF MILESTONE — IN PROGRESS
- GitHub-first continuity check passed: no pre-existing K09 artifact/completion commit existed; K03-K08 were already closed and were not re-researched from scratch.
- Exact frozen TLMTool_2.1.2(7).zip was revalidated again: archive SHA-256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd, inner EXE SHA-256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22.
- The exact .daily_tab blob was re-decoded and K03-K08 evidence was integrated into one lifecycle/failure model.
- No blocking contradiction was found across K03-K08.
- Important layering resolution: UI construction seed for Trừng Ác combat duration is 15, while _load_config missing-key fallback is "5". These are distinct static layers, not a contradiction; do not collapse them into one universal default.
- Important state-layer resolution: B08 captured heal/reconnect/respawn checkbox values are saved/current UI state, while missing-key config fallbacks are separate; no contradiction.
- Important scope resolution: Daily reconnect remains bounded/Daily-specific and must not inherit Train/TrainLSV five-attempt infinite retry semantics.
- Important helper boundary remains unchanged: _wait_movement_stopped is audited but the explicit recovered Daily call belongs to Tàng Bảo Đồ, not Trừng Ác.
- Integrated failure classes are now frozen: terminal-current-account, skip-current-cycle, recover-next-cycle, fail-soft/log-only, recoverable interrupt, external/control stop, and explicit UNKNOWN effect.
- Top-level Trừng Ác callable coverage is complete against K01_HANDLER_INVENTORY.tsv; no unaccounted top-level Trừng Ác handler remains. _punish_target_fail is a tracking surface, not a top-level handler; _punish_monitor_stops is a nested activity-wide recovery surface.
- First K09 artifacts committed:
  - docs/daily/K09_PUNISH_HANDOFF_STATIC_EVIDENCE.tsv at 0c324523d57543b6d71ac9d44ec9f71ed005e036
  - docs/daily/K09_PUNISH_HANDOFF_MODEL.json at a45e98b6dfc69b6d3b3393aef3bd4aa6b27318da
- K09 remains IN_PROGRESS until the integrated flow/task docs, repository/build recheck, STATE closure and PROJECT_STATUS advancement are persisted.

## K09 VERIFIED RESULTS
- GitHub-first continuity check passed: K09 did not exist before this work; K03-K08 remained unchanged because no real contradiction required rewriting them.
- Exact frozen archive was revalidated again before integration: TLMTool_2.1.2(7).zip SHA-256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd, size **93,715,901** bytes, CRC clean, 1050 entries / 1002 files / 48 dirs / 260,061,035 uncompressed bytes. Inner TLMTool.dist/TLMTool.exe remains SHA-256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22, size **47,450,112** bytes.
- Exact .daily_tab was re-decoded as **35,163 bytes / 1,186 constants**.
- K09 integrated the two Trừng Ác execution architectures without collapsing them:
  - activity-wide: _punish_start_worker -> _punish_toggle -> _punish_run_worker, start-time selected rows/PID snapshot, _punish_cancel, open-ended loop_idx;
  - row/bottom coordinator: _toggle_single_acc/_start_all_accs -> _punish_single_worker, row real Event + generation through _GenStop, its own open-ended loop_idx.
- Integrated normal cycle is frozen: stop check -> respawn clear -> optional HP<30 start heal -> optional teleport pre-step -> bổ đầu map4 tile(224,285) -> fixed return/receive quest clicks -> 30/30 check -> item40004000 target acquisition -> fast travel -> second item use + Triệu hồi -> monotonic combat -> 160px drift check -> optional final heal -> Kết thúc -> next outer cycle.
- Discard is explicitly outside that per-cycle sequence: it remains a run-scoped background worker spanning multiple Trừng Ác cycles.
- Terminal current-account logical conditions are frozen:
  - confirmed 30/30 daily limit;
  - missing Trừng Ác Lệnh during target acquisition;
  - activity-wide reconnect timeout path (exact 60s -> dừng).
- Control-stop/session invalidation paths remain distinct: batch cancel, row stop Event, generation mismatch, window/PID death.
- Current-cycle skip conditions are frozen: start-heal failure, bổ đầu move fail/wrong-map, exhausted first-stage item use, target travel failure, missing item at summon stage, and summon use/dialog/button/click failure.
- Recover-next-cycle conditions are frozen: missing target coordinates -> cancel quest -> next cycle; repeated same-target stuck beyond unknown threshold -> cancel/reset -> next cycle.
- Fail-soft/log-only paths are frozen: move/heal reinjection failure -> direct movement, 30/30 read/ack failure -> treat as not-full, auto-train start failure -> continue fight, final heal failure -> log/cycle tail, discard child failures -> account-local.
- Recoverable interrupt paths are frozen:
  - death: combat can end early, 4s monitor, HP0 click(792,441), Map87 respawn_event, next cycle clear/recover;
  - disconnect: 2s monitor, memory True veto, exact dual pixels for 3 ticks, halt + click(616,455), activity-wide bounded 60s recovery, single-worker common.active -> cache invalidation -> wait_memory_ready(45,3).
- The >160px drift detector remains DETECTED with exact return effect UNKNOWN.
- No blocking contradiction was found across K03-K08.
- Layering resolution #1: UI construction seed for punish duration is **15**, while _load_config missing-key fallback for daily_punish_duration is **"5"**. Both are exact and represent different layers; do not merge them into one universal default.
- Layering resolution #2: B08 visible recovery checkbox state is current/saved UI state, while config missing-key fallbacks are separate. Different values are not contradictions.
- Scope resolution remains: Daily reconnect must not inherit Train/TrainLSV five-attempt/infinite-batch reconnect behavior.
- _wait_movement_stopped remains outside the Trừng Ác lifecycle: K06 audited it, but the explicit recovered Daily call belongs to Tàng Bảo Đồ.
- Top-level Trừng Ác callable coverage is complete against K01_HANDLER_INVENTORY.tsv. No unaccounted top-level Trừng Ác handler remains.
- _punish_target_fail is a target-failure tracking surface, not a top-level handler. _punish_monitor_stops is nested activity-wide recovery logic.
- UI stop/reset handoff is integrated: activity button running/stopping/idle tuple, _punish_reset_ui idle reset, bottom coordinator stop signals, singleton _daily_all_monitor auto-reset after all row sessions stop, and _sync_start_tab_btns external sync. Exact teardown statement order remains UNKNOWN.
- K09 classification is **STATIC_VERIFIED / END_TO_END_RUNTIME_ENV_REQUIRED**.
- From the Trừng Ác perspective the static handoff is complete enough for later Stage-S reconstruction, but the overall project is not Stage-S-ready yet because Phase K Tàng Bảo Đồ/shared/runtime tasks and later PLAN phases remain.
- K09 artifacts:
  - docs/daily/K09_PUNISH_HANDOFF_STATIC_EVIDENCE.tsv — commit 0c324523d57543b6d71ac9d44ec9f71ed005e036
  - docs/daily/K09_PUNISH_HANDOFF_MODEL.json — commit a45e98b6dfc69b6d3b3393aef3bd4aa6b27318da
  - docs/daily/K09_PUNISH_HANDOFF_FLOW.md — commit 7f88ce02ba8610c063f94501a4daf49025af632c
  - docs/tasks/K09.md — commit 98bb61c0ee5654a611b5eff892141298ca861c0d
- PROJECT_STATUS.md was advanced by commit 32ac7610000a3fccdd992875d0190390447d6a82.

## POST-K09 CODE/BUILD RECHECK
- Current main tree after K09 status update: **586 entries**.
- Python code files remain exactly the same **7 forensic scripts** under tools/.
- No application source path exists.
- No build-system file or GitHub Actions workflow exists.
- Latest checked commit has **0 CI statuses** and **0 workflow runs**.
- All four K09 artifacts were fetched back successfully after commit.
- K09 introduced documentation/evidence only and no executable-code regression.
- Product build remains **NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED**, not PASS/FAIL.

## BLOCKERS
- End-to-end Trừng Ác runtime parity still requires a real Windows + live Thần Long environment.
- Reconstructed application build remains not applicable until Stage S because no product source/build target exists yet.
- No known static blocker for K10.

## DO_NOT_TOUCH
- Preserve K01-K09 contracts unchanged unless future exact evidence exposes a real contradiction.
- Keep activity-wide Trừng Ác batch and per-row/bottom coordinator as separate ownership models.
- Preserve the failure classes exactly; do not convert current-cycle skips or fail-soft paths into terminal stops.
- Preserve 30/30 and missing target-stage Trừng Ác Lệnh as terminal-current-account conditions.
- Preserve death and successful disconnect handling as recoverable transitions.
- Preserve Daily-specific bounded reconnect semantics.
- Preserve discard as run-scoped background work, not part of one execution cycle.
- Preserve the two duration layers: UI seed 15 and missing-key config fallback "5".
- Do not insert _wait_movement_stopped into Trừng Ác.
- Keep unresolved values/orderings UNKNOWN instead of guessing.
- Do not create Stage-S source/build placeholders before PLAN reaches reconstruction.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md.
2. Read STATE.md.
3. Check GitHub first for any K10 artifacts/commits; if already complete and verified, do not redo them.
4. Execute **K10 — Tàng Bảo Đồ configuration / selection / top-level run-loop contract audit** only.
5. Re-inspect the exact frozen original EXE first and use K01/K02 shared Daily evidence only where directly applicable.
6. Audit Tàng Bảo Đồ visible/config values, apply-all selection, activity-wide toggle/run worker, per-row single-worker ownership, batch selection/PID snapshot, loop termination, reconnect/death monitor shell at the top-level boundary, and UI reset handoff.
7. Do not deep-audit treasure-item/bag/mount/tomb/combat/heal internals yet; reserve those for later K11+ tasks.
8. Preserve the completed Trừng Ác handoff unchanged.
9. Cross-check B08 only after static extraction.
10. Persist K10 artifacts, update STATE.md/PROJECT_STATUS.md, and advance only after K10 verification.

## K10 STATIC EXTRACTION MILESTONE — IN PROGRESS
- GitHub-first continuity check passed: no pre-existing K10 artifact/completion commit existed; K01-K09 were preserved.
- Exact TLMTool_2.1.2(7).zip was materialized and revalidated before analysis: archive SHA-256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd, CRC clean. Inner TLMTool.dist/TLMTool.exe remains SHA-256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22, size **47,450,112** bytes.
- The exact .daily_tab Nuitka constants blob was fully decoded again: **35,163 bytes / 1,186 top-level constants**, consumed exactly to the end marker.
- Visible Tàng Bảo Đồ config is now statically frozen:
  - tomb combat duration UI seed **30s**;
  - low-HP treatment checkbox;
  - treatment-map visible/default value **Tô Châu**;
  - reconnect checkbox;
  - respawn checkbox;
  - Apply-all button.
- Config-load fallbacks are exact: daily_treasure_map_tomb_dur="30", daily_treasure_heal="0", daily_treasure_heal_map="Tô Châu", daily_treasure_dc_reconnect="1", daily_treasure_respawn="1".
- TREASURE_HEAL_COORDS exact dictionary is frozen at this UI/config boundary: Đại Lý=(43,178), Lạc Dương=(255,126), Tô Châu=(155,252), Lâu Lan=(27,183). Heal movement/click semantics remain later K tasks.
- Apply-all contract is exact: set every current row activity combobox to **Tàng bảo đồ**; it is configuration only, not execution.
- Activity start wrapper is exact: inject first, then call _treasure_map_toggle.
- Top-level activity run worker is exact: _treasure_map_run_worker owns tomb_dur, selected, selected_pids, loop_idx, alive, still_active, halt/respawn/monitor state and per-account threads.
- Batch terminal surfaces are exact: no selected rows -> bỏ qua; no live rows -> dừng; all selected rows stopped -> auto-stop. Exact iteration log [TÀNG BẢO ĐỒ] Lần ... proves an open-ended outer loop; no repeat-count config exists.
- Per-row/bottom coordinator path is distinct and exact: _treasure_single_worker owns hwnd, tomb_dur, row, gen_snap, halt, respawn_event, monitor_stop, Reader-cache invalidation and wait_memory_ready recovery surfaces. It calls _treasure_map_exec_sequence.
- Dedicated treasure disconnect-monitor and nested activity-wide recovery surfaces are proven. K10 intentionally freezes only the top-level shell: disconnect detected -> wait -> OK continue / timeout stop. Treasure-specific timeout numeric and detector internals are deferred and remain UNKNOWN here.
- Death/respawn top-level shell is proven through batch/single respawn_event ownership plus exec-cycle exact clear text. Exact death-monitor thread-launch order is not instruction-bound in K10.
- Treasure reset tuple is exact: Tàng bảo đồ / RoyalBlue / normal. Dedicated btn_treasure_start and shared run/stopping literals are present; exact assignment/teardown source-line order remains UNKNOWN.
- B08 was cross-checked only after EXE extraction: tomb duration 30, heal OFF, heal location Tô Châu, reconnect ON, respawn ON.
- First K10 artifact committed: docs/daily/K10_TREASURE_TOPLEVEL_STATIC_EVIDENCE.tsv at commit 6a92d5c563ca58672303b164abb6222bfad7632f.
- K10 remains IN_PROGRESS until model/flow/task docs, runtime/build recheck, STATE closure and PROJECT_STATUS advancement are persisted.

## K10 VERIFIED RESULTS
- GitHub-first continuity check passed: no K10 artifact/completion commit existed; K01-K09 were already complete and were not rewritten.
- Exact TLMTool_2.1.2(7).zip was revalidated before K10: SHA-256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd, size **93,715,901** bytes, CRC clean. Inner TLMTool.dist/TLMTool.exe remains SHA-256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22, size **47,450,112** bytes.
- Exact .daily_tab constants blob was decoded again as **35,163 bytes / 1,186 top-level constants**, consumed exactly to its end marker.
- Tàng Bảo Đồ visible/config surface is locked:
  - tomb-combat duration UI seed **30 seconds**;
  - post-dig heal if HP<30 checkbox;
  - treatment location selector with visible seed **Tô Châu**;
  - reconnect checkbox;
  - respawn checkbox;
  - Apply-all button.
- Exact load fallbacks are:
  - daily_treasure_map_tomb_dur="30"
  - daily_treasure_heal="0"
  - daily_treasure_heal_map="Tô Châu"
  - daily_treasure_dc_reconnect="1"
  - daily_treasure_respawn="1"
- Exact selectable treatment-coordinate dictionary is frozen at the config boundary: Đại Lý=(43,178), Lạc Dương=(255,126), Tô Châu=(155,252), Lâu Lan=(27,183). K10 does not deep-audit heal movement/click behavior.
- Apply-all is configuration-only: exact doc says set every current row activity combobox to Tàng bảo đồ. It does not itself start execution.
- Activity-wide start ownership is exact: inject/preparation wrapper -> _treasure_map_toggle -> _treasure_map_run_worker.
- Activity batch local model is exact: tomb_dur, selected, selected_pids, loop_idx, alive, still_active, wins, halt, threads, respawn_event, monitor_stop and child-thread state.
- Exact batch outcomes:
  - no selected Tàng Bảo Đồ rows -> bỏ qua;
  - no live selected rows -> dừng;
  - all selected rows stopped -> auto-stop;
  - [TÀNG BẢO ĐỒ] Lần ... -> outer iteration counter.
- No user treasure repeat-count config exists in the decoded Daily blob. tomb_dur is a per-cycle tomb-combat-duration parameter, not an N-run count.
- Per-row/bottom coordinator path remains distinct: _treasure_single_worker receives hwnd/tomb_dur/row/gen_snap, owns halt/respawn/monitor state plus Reader-cache invalidation and wait_memory_ready surfaces, and directly calls _treasure_map_exec_sequence.
- No explicit single-worker loop_idx local is recovered. K10 therefore does not invent per-row cycle numbering or exact source-form repetition.
- Dedicated treasure reconnect shell is proven:
  - _treasure_map_disconnect_monitor exists;
  - activity-wide nested _treasure_monitor_stops exists;
  - exact messages cover disconnect detected -> wait -> reconnect OK continue / timeout stop.
- Treasure-specific reconnect timeout numeric is **EXPLICIT_UNKNOWN in K10** rather than copied from Trừng Ác. Detector internals are deferred to later Tàng Bảo Đồ recovery work.
- Death/respawn top-level shell is proven: batch/single workers own respawn_event/monitor_stop and _treasure_map_exec_sequence has exact cycle-entry text clearing respawn_event so heal/move can leave map 87. Exact death-monitor launch/thread ordering remains UNKNOWN.
- Exact treasure idle/reset tuple is **Tàng bảo đồ / RoyalBlue / normal**. Dedicated btn_treasure_start and shared running/stopping literal pool are present; exact toggle-assignment/teardown source-line order remains UNKNOWN.
- K02 shared _daily_all_monitor and _sync_start_tab_btns remain the global UI-reset/synchronization boundary.
- Only after static extraction, frozen B08 was cross-checked: tomb duration 30, heal OFF, treatment location Tô Châu, reconnect ON, respawn ON.
- Exact packaged automove_log.txt remains SHA-256 17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500, **15,741,058 bytes / 387,238 lines**. Correlated Tàng Bảo Đồ top-level markers are **0**, so no end-to-end runtime parity is claimed.
- K10 classification is **STATIC_VERIFIED / END_TO_END_RUNTIME_ENV_REQUIRED**.
- K10 artifacts:
  - docs/daily/K10_TREASURE_TOPLEVEL_STATIC_EVIDENCE.tsv — commit 6a92d5c563ca58672303b164abb6222bfad7632f
  - docs/daily/K10_TREASURE_TOPLEVEL_MODEL.json — commit 85c9e6de79f7892439d84be35f6290d8dd64896f
  - docs/daily/K10_TREASURE_TOPLEVEL_FLOW.md — commit 5ebdcebd0494a1348df33a7bd2c7968a8f85ba96
  - docs/tasks/K10.md — commit 7b22925d7fbee33223303dcc10602e1625994970
- PROJECT_STATUS.md advanced K10 -> VERIFIED and K11 -> NEXT at commit f00c82fd21238d91777ac2fd6377b3ce26aacd9e.

## POST-K10 CODE/BUILD RECHECK
- Current main tree after K10 status update: **590 entries**.
- Python executable-code files remain exactly the same **7 forensic scripts** under tools/.
- No reconstructed application source path exists.
- No build-system file or GitHub Actions workflow exists.
- Latest checked commit has **0 CI statuses** and **0 workflow runs**.
- All four K10 artifacts were fetched back successfully after commit.
- K10 changed documentation/evidence only and introduced no executable-code regression.
- Product build remains **NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED**, not PASS/FAIL.

## BLOCKERS
- End-to-end Tàng Bảo Đồ runtime parity requires a real Windows + live Thần Long environment.
- Reconstructed product build is still not applicable before Stage S because there is no app source/build target.
- No known static blocker for K11.

## DO_NOT_TOUCH
- Preserve K01-K10 contracts unchanged unless exact new evidence exposes a real contradiction.
- Preserve Apply-all as selection-only.
- Preserve activity-wide Tàng Bảo Đồ batch and per-row/bottom single-worker ownership as separate models.
- Preserve duration 30 and exact config fallbacks.
- Preserve open-ended activity batch; do not invent a user repeat-count.
- Do not copy Trừng Ác reconnect timeout numeric into Treasure without independent evidence.
- Preserve respawn_event recovery shell but do not invent death-monitor thread ordering.
- Preserve exact idle/reset tuple and shared Daily UI reset infrastructure.
- Do not deep-audit item/bag/mount/map96/combat/heal internals inside K10 artifacts.
- Keep unresolved values/orderings UNKNOWN.
- Do not create Stage-S source/build placeholders before PLAN reaches reconstruction.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md.
2. Read STATE.md.
3. Check GitHub first for any K11 artifacts/commits; if already complete and verified, do not redo them.
4. Execute **K11 — Tàng Bảo Đồ bag/item detection and treasure-map activation audit** only.
5. Re-inspect the exact frozen original EXE first.
6. Audit the treasure-map item/bag activation portion of _treasure_map_exec_sequence: mount pre-step only where directly required, bag-open signal, tuido.tangBaoDo_multi recognition, click/activation, not-found terminal behavior, second-check behavior, and the exact stop/wait boundary immediately after activation.
7. Follow only directly-called pixel/memory helpers needed by that path; do not deep-audit map96 tomb combat/heal/reconnect yet.
8. Preserve K10 top-level ownership/config shell unchanged.
9. Cross-check B08 only after static extraction; B08 does not show the runtime activation flow.
10. Persist K11 artifacts, update STATE.md/PROJECT_STATUS.md, and advance only after K11 verification.

## K11 STATIC EXTRACTION MILESTONE — IN PROGRESS
- GitHub-first continuity check passed: no pre-existing K11 artifact/completion commit existed; K01-K10 were preserved.
- Exact TLMTool_2.1.2(7).zip was revalidated before K11: archive SHA-256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd, CRC clean. Inner TLMTool.exe remains SHA-256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22, size **47,450,112** bytes.
- Exact .daily_tab blob was fully decoded again: **35,163 bytes / 1,186 constants**, exact end marker.
- K11 freezes the Tàng Bảo Đồ activation portion of _treasure_map_exec_sequence only; map96 tomb combat/heal/reconnect remain deferred.
- Mount pre-step is exact at the static boundary: B0 log, character field (IsRiding,0), already-riding skip, 0.3s settle, common.nguaActive pixel check, and exact logged fallback click (1306,340). Additional fixed mount coordinates (1131,121), (1073,123), (906,688) are serialized in the same B0 block; their exact source-line purposes are kept strong-static rather than guessed.
- Pixel config common.nguaActive is exact: region (903,683), RGB(193,162,96), timeout1, tolerance10.
- Bag-open block is exact at the static boundary: B1 log, fixed coordinate (1296,421), wait_pixel call surface with window_hwnd/timeout, pixel key tuido.active, and adjacent drag coordinates (870,635)->(910,145). Pixel tuido.active is region(1123,631), RGB(150,166,78), timeout5, tolerance10.
- Current treasure-map recognizer is explicitly tuido.tangBaoDo_multi. Its frozen pixel config is region [702,163,1132,517,20,30], base RGB [2,30,35], offset RGB [228,215,170], timeout5, tolerance1. Legacy tangBaoDo / tangBaoDo_multi_old entries exist but are not the current Daily call surface.
- Shared pixel.find_multipixel contract is exact: one window capture, scan all base matches, verify offset color, return the base client (x,y) or None.
- On success Daily logs: Found tuido.tangBaoDo_multi at <found> → click. Daily uses the shared mouse.click_at background-click stack; helper docs prove DLL sync + PostMessage behavior with HWND targeting and no physical cursor requirement.
- The activation-success constant block also contains fixed coordinates (950,370), (490,427), (1173,105) and keyword surface window_hwnd/count/jitter/delay. Exact source-line mapping and exact override values for count/jitter/delay are not independently instruction-bound and remain UNKNOWN.
- First recognizer failure is terminal for the current Treasure account: exact text says not found → dừng tàng bảo đồ cho acc này.
- A fixed (1155,108) click surface is serialized immediately before _wait_movement_stopped. Its exact UI purpose is not text-bound and is not guessed.
- The Treasure movement-stop call is now bound exactly: _wait_movement_stopped with keyword names stop_check/skip_set and no by_memory override. Since helper default by_memory=False, this Treasure call uses the MovementDetector 10-pixel branch, not the Direction+Pos memory branch.
- After movement stops, exact log Đã dừng is followed by a second tangBaoDo_multi checkpoint. Exact second failure text says not found (lần 2) → dừng tàng bảo đồ cho acc này.
- Therefore K11 freezes a two-checkpoint activation shape around the movement wait: first map-item find/use -> movement-stop wait -> second map-item find/use/check -> post-activation outcome. Exact repeated second-success click microsequence is only strong-static reuse, not separately logged.
- Immediate next deep-flow boundary after successful second activation is MapID=96 (huyệt mộ) handling, deferred to K12.
- Packaged automove_log contains **0 correlated K11 markers** for Tàng Bảo Đồ, tangBaoDo_multi, B0/B1/B2, movement-stop Treasure text, or fixed activation coordinates.
- B08 was cross-checked only after static extraction and contains no runtime bag/item activation evidence.
- First K11 artifact committed: docs/daily/K11_TREASURE_ITEM_ACTIVATION_STATIC_EVIDENCE.tsv at commit 1de855a3f4941c426e9494cbbaef49811778f2da.
- K11 remains IN_PROGRESS until model/flow/task docs, code/build recheck, STATE closure and PROJECT_STATUS advancement are persisted.

## K11 VERIFIED RESULTS
- GitHub-first continuity check passed: no K11 artifact/completion commit existed; K01-K10 remained unchanged.
- Exact TLMTool_2.1.2(7).zip was revalidated before K11: SHA-256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd, size **93,715,901** bytes, CRC clean. Inner TLMTool.exe remains SHA-256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22, size **47,450,112** bytes.
- Exact .daily_tab constants blob was decoded again as **35,163 bytes / 1,186 constants**, exact end marker.
- K11 covers only the Treasure activation slice of _treasure_map_exec_sequence; map96/tomb combat and deep Treasure recovery remain deferred.
- Mount prep is frozen: B0 log, IsRiding fallback0, already-riding skip, 0.3s settle, common.nguaActive pixel, exact fallback click (1306,340). Extra B0 coords (1131,121), (1073,123), (906,688) remain strong-static without speculative labels.
- common.nguaActive exact pixel config: region(903,683), RGB(193,162,96), timeout1, tolerance10.
- Bag-open stage is frozen: B1 log, fixed coord (1296,421), wait_pixel keyword surface window_hwnd/timeout, key tuido.active, and strong-static drag pair (870,635)->(910,145).
- tuido.active exact pixel config: region(1123,631), RGB(150,166,78), timeout5, tolerance10. Exact explicit timeout override/false-return behavior at the Daily call remains UNKNOWN.
- Current recognizer is exactly find_multipixel("tuido","tangBaoDo_multi"), not the legacy tangBaoDo/tangBaoDo_multi_old keys.
- Exact current multipixel config: search rectangle (702,163)-(1132,517), offset(20,30), base RGB(2,30,35), offset RGB(228,215,170), timeout5, tolerance1.
- Shared find_multipixel helper contract is frozen: single capture, scan all base matches, validate offset pixel, return base client (x,y) or None.
- Success text exactly says Found tuido.tangBaoDo_multi at <found> -> click.
- Daily uses shared mouse.click_at; helper docs prove DLL-sync + PostMessage background HWND clicks without physical cursor movement.
- Activation-success block also serializes fixed coords (950,370), (490,427), (1173,105) plus keyword surface window_hwnd/count/jitter/delay. Exact source-line role/order and override values remain UNKNOWN rather than guessed.
- First tangBaoDo_multi not-found is terminal for the affected Treasure account: exact text says dừng tàng bảo đồ cho acc này.
- _treasure_map_skipped exists as activity skip state; exact mutation statement/order at the terminal branch is not independently native-bound.
- Fixed coord (1155,108) is serialized immediately before the movement-stop wait; exact UI purpose remains UNKNOWN.
- Treasure then calls _wait_movement_stopped with exact keyword names stop_check/skip_set and no by_memory override. K06 helper defaults prove by_memory=False, so this call uses the MovementDetector/is_moving **10-pixel** branch, not Direction+Pos memory wait.
- Exact post-wait success text is [Tàng bảo đồ] Đã dừng.
- After movement stops, the code performs a second tangBaoDo_multi checkpoint. Exact second failure says not found (lần 2) -> dừng tàng bảo đồ cho acc này, so second not-found is also terminal for the affected Treasure account.
- K11 therefore freezes a two-stage item activation shape: mount prep -> bag open/verify -> first map-item find/use -> movement-stop wait -> second map-item find/use -> post-activation MapID outcome.
- Exact second-success repeated click statement sequence is only strong-static reuse; it is not separately logged and was not falsely promoted to line-by-line proof.
- Immediate next exact deep-flow boundary is MapID=96 (huyệt mộ) -> đánh, reserved for K12.
- Packaged automove_log SHA-256 remains 17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500, **15,741,058 bytes / 387,238 lines**. Correlated K11 markers are all **0**.
- B08 has no runtime activation state and was used only after static extraction.
- K11 classification is **STATIC_VERIFIED / END_TO_END_RUNTIME_ENV_REQUIRED**.
- K11 artifacts:
  - docs/daily/K11_TREASURE_ITEM_ACTIVATION_STATIC_EVIDENCE.tsv — commit 1de855a3f4941c426e9494cbbaef49811778f2da
  - docs/daily/K11_TREASURE_ITEM_ACTIVATION_MODEL.json — commit f0707f2332b418e947efe5da39e2116efbad7343
  - docs/daily/K11_TREASURE_ITEM_ACTIVATION_FLOW.md — commit 3ababb15542f7f1382f0bf7c55a352540f9d6b37
  - docs/tasks/K11.md — commit 95a5060e351d036c96116a19a5d33b564e70dfac
- PROJECT_STATUS.md advanced K11 -> VERIFIED and K12 -> NEXT at commit eab4d28af6d25737b83ebe68422a4a6d0d3fb5c1.

## POST-K11 CODE/BUILD RECHECK
- Current main tree after K11 status update: **594 entries**.
- Python executable-code files remain exactly the same **7 forensic scripts** under tools/.
- No reconstructed application source path exists.
- No build-system file or GitHub Actions workflow exists.
- Latest checked commit has **0 CI statuses** and **0 workflow runs**.
- All four K11 artifacts were fetched back successfully.
- K11 changed documentation/evidence only and introduced no executable-code regression.
- Product build remains **NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED**, not PASS/FAIL.

## BLOCKERS
- End-to-end Treasure activation parity still requires a real Windows + live Thần Long runtime.
- Reconstructed product build is still not applicable before Stage S because there is no app source/build target.
- No known static blocker for K12.

## DO_NOT_TOUCH
- Preserve K01-K11 contracts unchanged unless exact new evidence exposes a real contradiction.
- Preserve the current tangBaoDo_multi recognizer and its exact pixel pattern.
- Preserve background HWND click semantics; do not replace with physical mouse automation.
- Preserve first and second not-found as terminal Treasure-account conditions.
- Preserve the exact movement-stop call boundary and by_memory=False / MovementDetector 10-pixel behavior.
- Do not invent labels/order for unresolved fixed coordinates or click override values.
- Do not deep-audit map96/tomb combat in K11 artifacts.
- Keep unresolved micro-orderings UNKNOWN.
- Do not create Stage-S source/build placeholders before PLAN reaches reconstruction.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md.
2. Read STATE.md.
3. Check GitHub first for any K12 artifacts/commits; if already complete and verified, do not redo them.
4. Execute **K12 — Tàng Bảo Đồ map96 movement / tomb combat / post-activation outcome audit** only.
5. Re-inspect the exact frozen original EXE first.
6. Start exactly at the post-K11 MapID outcome boundary: map96 detection, tomb state transition, move-to-map96/tile(50,16), common.active wait, tomb combat duration semantics, non-map96 outcome, and immediate final-heal boundary.
7. Follow only directly-called movement/auto-fight/pixel helpers required by that branch; do not deep-audit Treasure reconnect/death internals unless a direct K12 dependency requires it.
8. Preserve K10-K11 ownership and activation contracts unchanged.
9. Cross-check packaged runtime/B08 only after static extraction.
10. Persist K12 artifacts, update STATE.md/PROJECT_STATUS.md, re-check code/build state, and advance only after K12 verification.
## K12 STATIC EXTRACTION MILESTONE — IN PROGRESS
- GitHub-first continuity check passed: no pre-existing K12 artifact/completion commit existed; K01-K11 were preserved.
- Exact TLMTool_2.1.2(7).zip was revalidated before K12: archive SHA-256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd, size **93,715,901** bytes, CRC clean. Inner TLMTool.exe remains SHA-256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22, size **47,450,112** bytes.
- Exact .daily_tab was decoded again as **35,163 bytes / 1,186 constants**, exact end marker.
- K12 starts exactly at the K11 post-activation MapID boundary.
- _treasure_map_exec_sequence hidden helper defaults are statically frozen as **(5,None,None,None)** after required self/hwnd, so direct helper fallback tomb_dur is 5 seconds. This is a helper default layer, not the normal UI worker value.
- K10 production workers own/pass configured tomb_dur; UI seed/load fallback are both **30 seconds**. Thus normal configured path uses the worker snapshot, while an unparameterized direct helper call would fall back to 5.
- Exact map96 combat log/state are frozen: MapID=96 (huyệt mộ) → đánh <tomb_dur>... and state Đánh trong mộ.
- Two fixed coordinates **(1135,124)** and **(955,123)** are serialized in the map96/tomb-combat block. Their exact per-button meaning/order is not independently source-line-bound and remains UNKNOWN.
- Duration semantic is exact: tomb_dur is seconds for one tomb-combat stage, not a repeat count. Unlike K06 Trừng Ác, Treasure exec has no _t_end local and no Treasure-local monotonic constant; exact timing primitive (sleep/Event.wait/other stop-aware wait) remains UNKNOWN.
- Exact movement surface is frozen: log Di chuyển đến map 96, tọa độ (50, 16), state Đi huyệt mộ, move x/y constants **1600/512 = tile 50/16 × 32**, and kwargs map_id/x_tile/y_tile/wait_for_arrival/stop_check.
- Shared utils.move_character optional defaults are exact: wait_for_arrival=False, stop_check=None, home_priority=None, follow_mode=False, tolerance=48. K12 explicitly passes wait_for_arrival and stop_check; exact Boolean value of wait_for_arrival is not separately instruction-bound in this audit.
- No K12-specific move-failure log/branch is recovered before the later active/MapID outcome checks, so exact caller reaction to move_character False remains UNKNOWN.
- Exact common.active boundary is frozen: log Chờ common.active..., wait_pixel kwargs window_hwnd/timeout/debug/cancel_flag, and shared key common.active.
- Frozen common.active pixel remains **(1330,33)** RGB **(34,8,11)**, configured timeout100, tolerance5. K12 passes an explicit timeout override, but its numeric value is not independently instruction-bound; do not assume 100.
- Shared wait_pixel contract is exact: True if configured pixel appears before timeout, False on timeout/cancel. K12's exact False-return caller effect is not independently text-bound.
- Post-wait non-tomb outcome is exact: [Tàng bảo đồ] MapID=<...> — không phải huyệt mộ, bỏ qua. No account-terminal dừng text is attached to this branch; it skips the tomb outcome/combat path and reaches the immediate final-heal/cycle-tail boundary.
- Exact immediate final-heal boundary is frozen: % — kiểm tra trị liệu and [Tàng bảo đồ] Heal cuối vòng thất bại, using the existing _treasure_heal subsystem. Deep heal routing/click behavior remains deferred to K13.
- Exact Treasure cycle-end prefix [Tàng bảo đồ] === HWND and shared — Kết thúc === tail are present. Exact success return scalar remains UNKNOWN.
- Packaged automove_log contains **0 correlated K12 markers** for MapID=96, Đánh trong mộ, Đi huyệt mộ, Chờ common.active, tile(50,16), or huyệt mộ.
- B08 was cross-checked only after static extraction and shows configured duration30/idle controls, not map96 runtime behavior.
- First K12 artifact committed: docs/daily/K12_TREASURE_MAP96_COMBAT_STATIC_EVIDENCE.tsv at commit e8f51327bf6a1f0b8c2da91b36c9f759288269de.
- K12 remains IN_PROGRESS until model/flow/task docs, code/build recheck, STATE closure and PROJECT_STATUS advancement are persisted.
## K12 VERIFIED RESULTS
- GitHub-first continuity check passed: no K12 artifact/completion commit existed; K01-K11 remained unchanged.
- Exact TLMTool_2.1.2(7).zip was revalidated before K12: SHA-256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd, size **93,715,901** bytes, CRC clean. Inner TLMTool.exe remains SHA-256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22, size **47,450,112** bytes.
- Exact .daily_tab constants blob was decoded again as **35,163 bytes / 1,186 constants**, exact end marker.
- _treasure_map_exec_sequence hidden helper defaults are exactly **(5,None,None,None)** after required self/hwnd. By recovered arg/local order, direct helper fallback is tomb_dur=5, halt=None, respawn_event=None, stop_event=None.
- K10's production UI/config layer remains **30 seconds** and the workers own/pass configured tomb_dur. The 5-second helper fallback and 30-second normal worker value are separate layers, not a contradiction.
- Exact map96/tomb text is [Tàng bảo đồ] MapID=96 (huyệt mộ) → đánh <tomb_dur>... and exact state is Đánh trong mộ.
- tomb_dur is a per-tomb combat duration in seconds, not a repeat count. No Treasure repeat-count config exists.
- Unlike K06 Trừng Ác, Treasure exec has no recovered _t_end local and no Treasure-local monotonic reference. Exact duration timing primitive remains **EXPLICIT_UNKNOWN**; do not copy K06's monotonic implementation.
- Exact fixed click coordinates **(1135,124)** and **(955,123)** are serialized inside the tomb-combat block. Their exact button labels/order relative to the duration wait remain UNKNOWN.
- Exact movement surface is [Tàng bảo đồ] Di chuyển đến map 96, tọa độ (50, 16), state Đi huyệt mộ, with move values **1600/512 = tile50/16 × 32**.
- Exact K12 move keyword surface is map_id/x_tile/y_tile/wait_for_arrival/stop_check, using shared utils.move_character.
- Shared move_character optional defaults are exact: wait_for_arrival=False, stop_check=None, home_priority=None, follow_mode=False, tolerance=48. K12 explicitly passes wait_for_arrival and stop_check, but the exact Boolean value passed for wait_for_arrival is not independently instruction-bound.
- No K12-specific movement-failure message is recovered before later active/MapID checks; exact caller handling of move_character=False remains UNKNOWN.
- Exact common.active boundary is [Tàng bảo đồ] Chờ common.active... with wait_pixel kwargs window_hwnd/timeout/debug/cancel_flag.
- Frozen common.active pixel is **(1330,33)** RGB **(34,8,11)**, configured timeout100, tolerance5. Because K12 explicitly supplies timeout, the effective call timeout is not assumed to be 100; numeric override remains UNKNOWN.
- Shared wait_pixel contract is True if pixel appears before timeout, False on timeout/cancel. Exact K12 branch on False remains UNKNOWN.
- Exact post-wait non-tomb text is [Tàng bảo đồ] MapID=<...> — không phải huyệt mộ, bỏ qua. This is **not** an account-terminal dừng surface; K12 classifies it as SKIP_TOMB_OUTCOME / NOT_ACCOUNT_TERMINAL.
- Immediate final-heal boundary is exact: % — kiểm tra trị liệu plus [Tàng bảo đồ] Heal cuối vòng thất bại, reusing _treasure_heal. Deep Treasure healing internals remain K13.
- Final-heal failure is fail-soft/log-only at the cycle tail; no independent terminal account-stop surface is attached.
- Treasure normal tail owns [Tàng bảo đồ] === HWND plus shared — Kết thúc === and returns to the K10 worker/session shell. Exact success return scalar remains UNKNOWN.
- Packaged automove_log SHA-256 remains 17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500, **15,741,058 bytes / 387,238 lines**. Correlated K12 counts are all **0** for MapID=96, Đánh trong mộ, Đi huyệt mộ, Chờ common.active, tile(50,16), and huyệt mộ.
- B08 was cross-checked only after static extraction and provides only configured duration30/idle Treasure controls, not K12 runtime behavior.
- K12 classification is **STATIC_VERIFIED / END_TO_END_RUNTIME_ENV_REQUIRED**.
- K12 artifacts:
  - docs/daily/K12_TREASURE_MAP96_COMBAT_STATIC_EVIDENCE.tsv — commit e8f51327bf6a1f0b8c2da91b36c9f759288269de
  - docs/daily/K12_TREASURE_MAP96_COMBAT_MODEL.json — commit 933830b9fe8d83e93a824db2090fa2013a36d63e
  - docs/daily/K12_TREASURE_MAP96_COMBAT_FLOW.md — commit 90d18e899ffe3a8824437b15537a3c60af28008f
  - docs/tasks/K12.md — commit ce64189f9bebfbeeaccb4dd845ed26d8e7d3983a
- PROJECT_STATUS.md advanced K12 -> VERIFIED and K13 -> NEXT at commit 4716fee3abaee1dbc6e6a06cf99bf27a16ab98d5.

## POST-K12 CODE/BUILD RECHECK
- Current main tree after K12 status update: **598 entries**.
- Python executable-code files remain exactly the same **7 forensic scripts** under tools/.
- No reconstructed application source path exists.
- No build-system file or GitHub Actions workflow exists.
- Latest checked commit has **0 CI statuses** and **0 workflow runs**.
- All four K12 artifacts were fetched back successfully.
- K12 changed documentation/evidence only and introduced no executable-code regression.
- Product build remains **NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED**, not PASS/FAIL.

## BLOCKERS
- End-to-end Treasure map96/combat parity still requires a real Windows + live Thần Long runtime.
- Reconstructed product build is still not applicable before Stage S because there is no app source/build target.
- No known static blocker for K13.

## DO_NOT_TOUCH
- Preserve K01-K12 contracts unchanged unless exact new evidence exposes a real contradiction.
- Preserve the two Treasure duration layers: production UI/config 30 and direct exec helper fallback 5.
- Preserve tomb_dur as seconds, not run count.
- Do not copy the Trừng Ác monotonic timer into Treasure without direct evidence.
- Preserve exact fixed combat coordinates without inventing button labels/order.
- Preserve map96 tile(50,16) / move values1600/512 and the common.active wait boundary.
- Do not assume common.active effective timeout=100 because K12 passes an explicit override.
- Preserve non-96 as non-terminal skip of the tomb outcome.
- Preserve final-heal failure as fail-soft/log-only.
- Keep all unresolved move/wait/timer microeffects UNKNOWN.
- Do not create Stage-S source/build placeholders before PLAN reaches reconstruction.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md.
2. Read STATE.md.
3. Check GitHub first for any K13 artifacts/commits; if already complete and verified, do not redo them.
4. Execute **K13 — Tàng Bảo Đồ heal / reconnect / respawn recovery audit** only.
5. Re-inspect the exact frozen original EXE first.
6. Audit _treasure_heal, _treasure_map_disconnect_monitor, the Treasure activity-wide reconnect shell, per-row reconnect/cache-ready handoff, respawn/death-event integration, and how successful recovery returns to the next Treasure cycle.
7. Resolve the Treasure-specific reconnect timeout numeric only if independently bound; do not copy Trừng Ác values by analogy.
8. Preserve K10-K12 top-level/activation/map96 contracts unchanged.
9. Cross-check B08/runtime only after static extraction.
10. Persist K13 artifacts, update STATE.md/PROJECT_STATUS.md, re-check code/build state, and advance only after K13 verification.
## K13 STATIC EXTRACTION MILESTONE — IN PROGRESS
- GitHub-first continuity check passed: no pre-existing K13 artifact/completion commit existed; K01-K12 were preserved.
- Exact TLMTool_2.1.2(7).zip was materialized and revalidated before K13: archive SHA-256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd, CRC clean. Inner TLMTool.exe remains SHA-256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22, size **47,450,112** bytes.
- Exact .daily_tab blob was decoded/re-inspected again: **35,163 bytes / 1,186 constants**, exact end marker.
- K13 start-of-cycle recovery boundary is exact: if respawn_event is set, Treasure clears it so heal/move can leave map87, then reads HP and if Treasure heal is enabled with HP<30 calls _treasure_heal. Start-heal failure is exact `Heal thất bại → skip vòng này`.
- Final-heal boundary remains exact from K12: same Treasure heal subsystem, with `Heal cuối vòng thất bại` as fail-soft/log-only cycle-tail behavior.
- _treasure_heal exact locals are self,hwnd,stop_check,heal_map,coords,heal_tile_x,heal_tile_y,map_id,name,mid,e,ok.
- Treasure heal exact validation chain is now frozen: selected heal-map required -> coordinate lookup required -> resolve selected name through MAP_LIST to map_id -> reject invalid map_id -> call movement helper -> movement failure returns failure -> success logs `trị liệu tại <map> thành công`.
- TREASURE_HEAL_COORDS remains exact: Đại Lý=(43,178), Lạc Dương=(255,126), Tô Châu=(155,252), Lâu Lan=(27,183).
- Treasure heal move surface contains only wait_for_arrival/stop_check kwargs; no tolerance kw is present, so shared move_character default tolerance **48** is the effective default unless later native evidence proves an internal override.
- No Treasure-specific fixed treatment-click coordinates are serialized in the _treasure_heal compact block. Manual Tô Châu click sequences and _punish_heal click/reinject behavior are **not** copied into Treasure by analogy.
- Treasure-specific reinjection behavior inside _treasure_heal is NOT_PROVEN; no Treasure-specific reinjection failure/log surface is recovered.
- Activity-wide Treasure reconnect shell is exact: `_treasure_monitor_stops`, `Phát hiện mất kết nối → chờ kết nối lại...`, `Kết nối lại OK → tiếp tục`, `Kết nối lại timeout → dừng`.
- The Treasure-specific reconnect timeout numeric is still **EXPLICIT_UNKNOWN**. K13 does not copy the exact Trừng Ác 60s value without an independent Treasure binding.
- _treasure_map_disconnect_monitor exact local mapping is self,hwnd,halt,respawn_event,stop_event,ev,real_set. This is an event-adapter shape rather than a second full detector local model.
- Unlike _punish_disconnect_monitor, the Treasure adapter has no local check_pixel/dc_strikes/MI/conn/dc1/dc2 detector state. Strong static evidence therefore supports reuse/delegation to the existing Daily disconnect detector, but the exact native call edge and ev/real_set propagation order remain not line-by-line proven.
- The shared Daily detector contract itself remains K07-verified: 2s cadence, memory-connected True veto, both exact disconnect pixels for 3 consecutive ticks (~6s), then halt + click(616,455). K13 preserves this as the shared detector layer while keeping Treasure adapter wiring micro-order explicit UNKNOWN.
- Treasure single-worker exact locals include halt,respawn_event,monitor_stop,rm,invalidate_character_cache,_get_pid_from_hwnd,wait_memory_ready,_exit_why. This freezes a post-reconnect/session memory-refresh boundary.
- Shared cache/memory-ready semantics remain exact: invalidate stale Reader cache after reconnect; wait_memory_ready requires clear RoleName + MapID!=None and fail-opens on timeout. Shared defaults are 45.0s / need3 / interval1.0, but the exact Treasure call override arguments are not independently instruction-bound.
- No unconditional post-reconnect Treasure DLL reinjection edge is proven.
- Shared Daily death/Địa-phủ monitor contract remains exact from K07: 4s cadence, HP0 click(792,441), MapID87 -> respawn_event.set(). Treasure batch/single workers own respawn_event and rm monitor handles, and Treasure exec consumes/clears respawn_event at cycle entry. Exact thread-launch statement order remains UNKNOWN.
- Death/Map87 is therefore a recoverable Treasure transition: signal respawn_event -> next Treasure exec clears it -> immediate HP/start-heal boundary -> normal movement/activation can leave map87.
- Exact same-scheduling-window precedence between disconnect halt and respawn_event remains UNKNOWN.
- B08 was cross-checked only after static extraction: Treasure heal OFF, heal map Tô Châu, reconnect ON, respawn ON.
- Packaged automove_log has **0 correlated K13 markers** for Treasure heal/reconnect/respawn/Địa-phủ/cache-ready behavior.
- First K13 artifact committed: docs/daily/K13_TREASURE_RECOVERY_STATIC_EVIDENCE.tsv at commit 36f613669c837fa3b6d0d695ef148dc2deb2b2fa.
- K13 remains IN_PROGRESS until model/flow/task docs, code/build recheck, STATE closure and PROJECT_STATUS advancement are persisted.
## K13 VERIFIED RESULTS
- GitHub-first continuity check passed: no K13 artifact/completion commit existed; K01-K12 remained unchanged.
- Exact TLMTool_2.1.2(7).zip was revalidated before K13: SHA-256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd, size **93,715,901** bytes, CRC clean. Inner TLMTool.exe remains SHA-256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22, size **47,450,112** bytes.
- Exact .daily_tab constants blob was re-inspected as **35,163 bytes / 1,186 constants**, exact end marker.
- Treasure recovery config fallbacks are preserved: heal OFF, heal-map Tô Châu, reconnect ON, respawn ON. B08 current captured state matches heal OFF / Tô Châu / reconnect ON / respawn ON.
- Exact Treasure recovery-entry text says respawn_event set -> clear so heal/move can leave map87. The next exact boundary is HP checking.
- Start-of-cycle Treasure heal is exact: if enabled and HP<30, call _treasure_heal; failure logs `Heal thất bại → skip vòng này`, so start-heal failure is current-cycle skip, not account terminal.
- _treasure_heal exact locals are self,hwnd,stop_check,heal_map,coords,heal_tile_x,heal_tile_y,map_id,name,mid,e,ok.
- Exact Treasure heal validation chain: selected heal location required -> coordinate lookup required -> selected name resolved through MAP_LIST to map_id -> invalid map_id fails -> movement attempted -> movement failure fails -> success logs `trị liệu tại <map> thành công`.
- Exact selectable heal coordinates remain Đại Lý=(43,178), Lạc Dương=(255,126), Tô Châu=(155,252), Lâu Lan=(27,183).
- Treasure heal compact movement kwargs are wait_for_arrival/stop_check only; there is no tolerance kw. Shared move_character default tolerance **48** therefore remains the effective default unless later exact evidence proves an override.
- No Treasure-specific fixed treatment-click coordinates are serialized in the _treasure_heal compact block, and no Treasure-specific `inject cho heal thất bại` surface is recovered. Do not copy manual Tô Châu click sequences, _punish_heal tolerance10, or _punish_heal reinjection behavior into Treasure by analogy.
- The exact Treasure heal wait_for_arrival Boolean and any post-arrival treatment microaction remain UNKNOWN.
- Final Treasure heal failure remains exact `Heal cuối vòng thất bại` and is fail-soft/log-only at the cycle tail.
- Activity-wide Treasure reconnect shell is exact: _treasure_monitor_stops + disconnect detected/wait + reconnect OK/continue + timeout/dừng.
- Treasure reconnect timeout numeric remains **EXPLICIT_UNKNOWN**; K13 does not copy Trừng Ác's exact 60s value without independent Treasure binding.
- _treasure_map_disconnect_monitor exact local model is self,hwnd,halt,respawn_event,stop_event,ev,real_set.
- This Treasure monitor is an event-adapter shape rather than a second full detector local model. It lacks the full detector locals check_pixel/dc_strikes/MI/conn/dc1/dc2 owned by _punish_disconnect_monitor.
- Strong static evidence supports reuse/delegation to the already-verified Daily detector layer, while exact native call edge and ev/real_set propagation order remain UNKNOWN.
- Shared Daily detector semantics remain K07-verified and are preserved as the detector layer: 2s cadence, memory True veto, both exact disconnect pixels for 3 consecutive ticks (~6s), then halt + click(616,455).
- Treasure single-worker locals exactly include halt,respawn_event,monitor_stop,rm,invalidate_character_cache,_get_pid_from_hwnd,wait_memory_ready,_exit_why, freezing a post-reconnect/session memory-refresh boundary.
- Shared cache/memory-ready contract remains exact: invalidate stale Reader cache after reconnect/reload; valid sample requires usable RoleName + MapID!=None; timeout False/log/fail-open. Shared defaults are 45.0s / need3 / interval1.0. Exact Treasure call override args remain UNKNOWN.
- No unconditional Treasure post-reconnect DLL reinjection edge is independently proven.
- Shared Daily death/Địa-phủ monitor remains exact: 4s cadence, HP0 click(792,441), MapID87 -> respawn_event.set(). Treasure batch/single workers own respawn_event plus rm monitor handles and Treasure exec explicitly consumes/clears the event at next cycle entry.
- Death/Map87 is therefore recoverable for Treasure: shared death event -> Treasure recovery boundary -> next exec clears event -> HP/start-heal -> normal movement/activation can leave map87.
- Exact death-monitor thread-launch order and same-scheduling-window disconnect-vs-death precedence remain UNKNOWN.
- Packaged automove_log SHA-256 remains 17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500, **15,741,058 bytes / 387,238 lines**. Correlated K13 Treasure heal/reconnect/respawn/cache-ready markers are all **0**.
- K13 classification is **STATIC_VERIFIED / END_TO_END_RUNTIME_ENV_REQUIRED**.
- K13 artifacts:
  - docs/daily/K13_TREASURE_RECOVERY_STATIC_EVIDENCE.tsv — commit 36f613669c837fa3b6d0d695ef148dc2deb2b2fa
  - docs/daily/K13_TREASURE_RECOVERY_MODEL.json — commit d95b26f6368c2a9bb2b87f632cfcf3465301f770
  - docs/daily/K13_TREASURE_RECOVERY_FLOW.md — commit c7d2ddfb8b2d3d37fe4e8b84c6e102bed01d6779
  - docs/tasks/K13.md — commit bd5eee472777130cbd5f3f5a41fde5292a043972
- PROJECT_STATUS.md advanced K13 -> VERIFIED and K14 -> NEXT at commit eaefa701b9ca735f4f68859c3236237671423008.

## POST-K13 CODE/BUILD RECHECK
- Current main tree after K13 status update: **602 entries**.
- Python executable-code files remain exactly the same **7 forensic scripts** under tools/.
- No reconstructed application source path exists.
- No build-system file or GitHub Actions workflow exists.
- Latest checked commit has **0 CI statuses** and **0 workflow runs**.
- All four K13 artifacts were fetched back successfully.
- K13 changed documentation/evidence only and introduced no executable-code regression.
- Product build remains **NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED**, not PASS/FAIL.

## BLOCKERS
- End-to-end Treasure recovery parity still requires a real Windows + live Thần Long runtime.
- Reconstructed product build is still not applicable before Stage S because there is no app source/build target.
- No known static blocker for K14.

## DO_NOT_TOUCH
- Preserve K01-K13 contracts unchanged unless exact new evidence exposes a real contradiction.
- Preserve selected-map Treasure heal instead of hardwiring Tô Châu.
- Preserve Treasure heal movement tolerance layer at shared default48; do not import _punish_heal tolerance10.
- Do not invent Treasure treatment clicks or Treasure-specific heal reinjection.
- Preserve start-heal current-cycle skip and final-heal fail-soft/log-only.
- Preserve Treasure disconnect adapter/event-bridge shape and shared Daily detector layer without inventing adapter micro-order.
- Do not copy Trừng Ác reconnect timeout60 into Treasure.
- Preserve Reader-cache invalidation/memory-ready boundary but keep Treasure override args UNKNOWN.
- Preserve shared death/Map87 respawn_event recovery and keep launch ordering/dual-event precedence UNKNOWN.
- Do not create Stage-S source/build placeholders before PLAN reaches reconstruction.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md.
2. Read STATE.md.
3. Check GitHub first for any K14 artifacts/commits; if already complete and verified, do not redo them.
4. Execute **K14 — Tàng Bảo Đồ skipped-account / stop-reset / failure-lifecycle audit** only.
5. Re-inspect the exact frozen original EXE first and reuse K10-K13 evidence without reopening already-closed internals unless a contradiction appears.
6. Audit _treasure_map_skipped ownership/mutation/use, first/second item-not-found account exclusion, activity batch still_active filtering, user/cancel/window/gen stop classes, reconnect/death interruption classes, non96 skip versus terminal conditions, and _treasure_map_reset_ui / shared Daily UI-reset handoff.
7. Build a Treasure failure/lifecycle matrix but do not yet perform the final integrated static handoff; reserve full Treasure closure for the following task.
8. Preserve K10-K13 contracts unchanged.
9. Cross-check runtime/B08 only after static extraction.
10. Persist K14 artifacts, update STATE.md/PROJECT_STATUS.md, re-check code/build state, and advance only after K14 verification.
## K14 STATIC EXTRACTION MILESTONE — IN PROGRESS
- GitHub-first continuity check passed: no pre-existing K14 artifact/completion commit existed; K01-K13 were preserved.
- Exact TLMTool_2.1.2(7).zip and inner TLMTool.exe were revalidated again before K14: archive SHA-256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd, inner EXE SHA-256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22, inner size **47,450,112** bytes.
- Exact .daily_tab was re-inspected as **35,163 bytes / 1,186 constants**.
- DailyTab owns exact Treasure activity/session fields _treasure_map_running, _treasure_map_cancel, _treasure_map_btn and _treasure_map_skipped.
- Shared stop diagnostic has an exact Treasure-specific cancel reason `cancel(batch-tàng-bảo-đồ)` plus exact halt(mất-kết-nối), stop_event(dừng), gen(phiên-mới), window-chết/đổi-process and respawn(địa-phủ) classes.
- Activity-wide Treasure batch keeps exact selected/selected_pids start snapshots and recomputes alive/still_active inside its open-ended loop. Exact terminal batch surfaces remain no selected -> bỏ qua, no live -> dừng, all selected stopped -> tự động dừng.
- K11's two tangBaoDo_multi not-found branches remain terminal-current-Treasure-account conditions. Combined with the exact _treasure_map_skipped field, the exact `skip_set` keyword passed at the Treasure movement wait, and batch still_active filtering, strong static evidence supports persistent exclusion of terminally-skipped Treasure HWNDs during the active batch.
- Exact `_treasure_map_skipped.add/discard/clear` statement placement is **not** native-instruction-bound. K14 therefore does not invent whether the set is cleared in toggle/start/reset or the exact mutation order at first/second not-found.
- Start-heal failure remains current-cycle skip only; non96 remains skip-tomb-outcome/non-terminal; final-heal failure remains fail-soft/log-only.
- Reconnect OK remains recoverable, reconnect timeout remains terminal for the affected recovery/account path, and death/Map87 respawn_event remains recoverable rather than terminal.
- Bottom all-account stop contract remains exact from K02: while running, set each row _farming_acc=False + row _stop_event, return the bottom button to Bắt đầu/green, then workers unwind cooperatively.
- Singleton _daily_all_monitor exact contract remains: wait until all row sessions stop, call both _punish_reset_ui and _treasure_map_reset_ui, then log `[Bắt đầu] Tất cả acc đã dừng — tự động reset UI`.
- _sync_start_tab_btns remains the external StartTab sync boundary.
- Treasure activity reset tuple remains exact: `Tàng bảo đồ / RoyalBlue / normal`; shared activity running/stopping surfaces remain Dừng lại/FireBrick and Đang dừng.../disabled.
- Exact UI teardown source-line order (running flag/cancel/event/monitor/reset/sync) remains UNKNOWN.
- Packaged automove_log was rechecked after static extraction: exact SHA-256 17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500, 15,741,058 bytes / 387,238 lines, with zero correlated K14 lifecycle/skip/reset markers.
- B08 was cross-checked only after static extraction and remains idle configuration only.
- First K14 artifact committed: docs/daily/K14_TREASURE_FAILURE_LIFECYCLE_STATIC_EVIDENCE.tsv at commit 031e4cdf4785222cd38c7d73c6a029c1824359ff.
- K14 remains IN_PROGRESS until model/flow/task docs, code/build recheck, STATE closure and PROJECT_STATUS advancement are persisted.
## K14 VERIFIED RESULTS
- GitHub-first continuity check passed: no K14 artifact/completion commit existed; K01-K13 remained unchanged.
- Exact TLMTool_2.1.2(7).zip and inner EXE were revalidated before K14: archive SHA-256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd, inner EXE SHA-256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22, inner size **47,450,112** bytes.
- Exact .daily_tab was re-inspected as **35,163 bytes / 1,186 constants**.
- DailyTab exact Treasure lifecycle fields are _treasure_map_running, _treasure_map_cancel, _treasure_map_btn and _treasure_map_skipped.
- Shared exact stop diagnostic now freezes the Treasure lifecycle classes: cancel(batch-tàng-bảo-đồ), halt(mất-kết-nối), stop_event(dừng), gen(phiên-mới), window-chết/đổi-process, respawn(địa-phủ), plus fallback không-stop(?).
- Activity-wide Treasure batch keeps selected/selected_pids start snapshots, loop_idx, alive and still_active. Exact batch endings remain no-selection -> bỏ qua, no-live -> dừng, all-selected-stopped -> tự động dừng.
- K11's first and second tangBaoDo_multi not-found branches remain **TERMINAL_CURRENT_TREASURE_ACCOUNT**.
- Exact _treasure_map_skipped ownership, exact Treasure movement-wait `skip_set` keyword, terminal not-found branches and activity still_active filtering together provide strong static evidence that terminally-skipped HWNDs are excluded from later active work within the same Treasure batch.
- Exact _treasure_map_skipped add/discard/clear source statements and its exact clear boundary remain **EXPLICIT_UNKNOWN**. K14 did not invent them.
- Failure classes are now explicitly separated: start-heal failure = SKIP_CURRENT_CYCLE; non96 = SKIP_TOMB_OUTCOME / NOT_ACCOUNT_TERMINAL; final-heal failure = FAIL_SOFT_LOG_ONLY; reconnect success = RECOVERABLE_INTERRUPT; reconnect timeout = TERMINAL_AFFECTED_RECOVERY_PATH; death/Map87 = RECOVERABLE_INTERRUPT.
- User/session control stops remain separate from recovery interrupts: batch cancel Event, row _stop_event, _GenStop generation mismatch, and HWND/PID invalidation.
- Bottom all-account stop remains exact: set row _farming_acc=False + row _stop_event, return bottom UI toward Bắt đầu/green, and let per-row workers unwind cooperatively.
- Singleton _daily_all_monitor waits until all row sessions have actually stopped, calls both _punish_reset_ui and _treasure_map_reset_ui, then logs `[Bắt đầu] Tất cả acc đã dừng — tự động reset UI`.
- _sync_start_tab_btns remains the external StartTab synchronization boundary.
- Treasure activity exact idle tuple remains **Tàng bảo đồ / RoyalBlue / normal**; shared activity running/stopping surfaces remain **Dừng lại / FireBrick** and **Đang dừng... / disabled**.
- Exact teardown source-line order among running flag, cancel/event signal, monitor shutdown, child completion, reset helper and StartTab sync remains UNKNOWN.
- Packaged automove_log was rechecked only after static extraction: SHA-256 17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500, **15,741,058 bytes / 387,238 lines**; all correlated K14 Treasure lifecycle/skip/reset markers are **0**.
- B08 remains idle configuration only and contributes no runtime skipped-account/teardown evidence.
- K14 classification is **STATIC_VERIFIED / END_TO_END_RUNTIME_ENV_REQUIRED**.
- K14 artifacts:
  - docs/daily/K14_TREASURE_FAILURE_LIFECYCLE_STATIC_EVIDENCE.tsv — commit 031e4cdf4785222cd38c7d73c6a029c1824359ff
  - docs/daily/K14_TREASURE_FAILURE_LIFECYCLE_MODEL.json — commit 778788cc068ba2f2c504f04f0bda813c3aadfdf4
  - docs/daily/K14_TREASURE_FAILURE_LIFECYCLE_FLOW.md — commit 3c94e04d2ac9df3a09bcf4b5ab565a95d7d6d267
  - docs/tasks/K14.md — commit 33be99d270e71d1838fe78c7720fcd73211c968c
- PROJECT_STATUS.md advanced K14 -> VERIFIED and K15 -> NEXT at commit 985d273cc4cfebc8816beb85140975fd8fea801f.

## POST-K14 CODE/BUILD RECHECK
- Current main tree after K14 status update: **606 entries**.
- Python executable-code files remain exactly the same **7 forensic scripts** under tools/.
- No reconstructed application source path exists.
- No build-system file or GitHub Actions workflow exists.
- Latest checked commit has **0 CI statuses** and **0 workflow runs**.
- All four K14 artifacts were fetched back successfully.
- K14 changed documentation/evidence only and introduced no executable-code regression.
- Product build remains **NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED**, not PASS/FAIL.

## BLOCKERS
- End-to-end Treasure failure/teardown parity still requires a real Windows + live Thần Long runtime.
- Reconstructed product build is still not applicable before Stage S because there is no app source/build target.
- No known static blocker for K15.

## DO_NOT_TOUCH
- Preserve K01-K14 contracts unchanged unless exact new evidence exposes a real contradiction.
- Preserve first/second Treasure item-not-found as terminal-current-account and keep ordinary cycle/outcome skips separate.
- Preserve _treasure_map_skipped as Treasure lifecycle state but do not fabricate its add/clear micro-order.
- Preserve activity selected/PID snapshot plus recurring alive/still_active filtering.
- Preserve shared stop reason classes and generation/window identity protection.
- Preserve bottom all-account cooperative stop and singleton monitor reset semantics.
- Preserve exact Treasure idle/running/stopping UI states while keeping teardown statement order UNKNOWN.
- Do not create Stage-S source/build placeholders before PLAN reaches reconstruction.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md.
2. Read STATE.md.
3. Check GitHub first for any K15 artifacts/commits; if already complete and verified, do not redo them.
4. Execute **K15 — Tàng Bảo Đồ integrated lifecycle / failure matrix / static handoff audit** only.
5. Re-inspect the exact frozen original EXE first and integrate K10-K14 without reopening already-correct details unless an actual contradiction appears.
6. Build one end-to-end Treasure lifecycle model covering config/selection, batch vs per-row ownership, mount/bag/two-stage activation, movement-stop, map96/tomb branch, selected-map heal, reconnect/death recovery, skipped-account exclusion, stop/reset/UI handoff and all failure classes.
7. Audit every top-level Treasure callable from K01_HANDLER_INVENTORY.tsv for coverage and identify any remaining Treasure callable/surface not accounted for.
8. Resolve only real K10-K14 contradictions; do not rewrite correct artifacts. If internally consistent, close the Treasure static handoff.
9. Cross-check runtime/B08 only after the integrated static audit, then re-check repository code/build state.
10. Persist K15 artifacts, update STATE.md/PROJECT_STATUS.md, and only then advance to the shared-Daily tasks.
## K15 INTEGRATED TREASURE HANDOFF MILESTONE — IN PROGRESS
- GitHub-first continuity check passed: no K15 artifact/completion commit existed; K10-K14 were preserved unchanged.
- The exact library specimen TLMTool_2.1.2(7).zip was rematerialized before K15. Frozen authority remains archive SHA-256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd, size **93,715,901** bytes; inner TLMTool.exe SHA-256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22, size **47,450,112** bytes.
- K15 integrated K10-K14 into one Treasure lifecycle model without reopening already-correct internals.
- Full K01 handler inventory audit shows every top-level Treasure-related callable is accounted for: _build_ui, _apply_treasure_all, _treasure_start_worker, _treasure_single_worker, _wait_movement_stopped, _treasure_map_toggle, _treasure_map_run_worker, _treasure_map_disconnect_monitor, _treasure_map_exec_sequence, _treasure_heal and _treasure_map_reset_ui.
- No unaccounted top-level Treasure callable remains.
- Activity-wide and per-row ownership remain distinct: activity batch snapshots selected/selected_pids/configured tomb_dur and iterates open-ended with still_active filtering; per-row uses row HWND+PID + stop Event + generation identity and its own recovery shell.
- Integrated Treasure cycle is now frozen at handoff level: stop/session guard -> respawn_event consumption -> optional HP<30 start heal -> mount prep -> bag readiness -> first tangBaoDo_multi find/use -> MovementDetector movement-stop wait -> second tangBaoDo_multi checkpoint/use -> post-activation MapID/tomb region -> optional final heal -> cycle tail.
- K12's map96/tomb region remains intentionally micro-order-safe: exact surfaces are preserved, but exact order/meaning of fixed tomb clicks versus duration/movement/MapID read is not invented.
- No blocking contradiction was found across K10-K14.
- The only duration layering issue is resolved: production UI/config Treasure duration is 30s, while a direct _treasure_map_exec_sequence call defaults tomb_dur=5. Workers pass the configured value, so both are correct layers.
- Failure classes are integrated consistently: first/second item-not-found terminal current Treasure account; start-heal failure current-cycle skip; non96 tomb-outcome skip; final-heal fail-soft; reconnect/death recoverable when successful; reconnect timeout terminal for affected recovery path; cancel/row Event/gen/window identity are control stops.
- _treasure_map_skipped role remains strong-static persistent exclusion inside the active batch, while exact add/discard/clear statements and clear point remain UNKNOWN.
- Treasure recovery remains consistent with K13: thin Treasure disconnect adapter over shared Daily detector layer, bounded reconnect shell with numeric timeout UNKNOWN, Reader-cache/memory-ready recovery boundary, shared death/Map87 respawn_event model, no proven forced post-reconnect reinjection.
- UI/stop handoff remains consistent: activity Dừng lại/FireBrick -> Đang dừng.../disabled -> Tàng bảo đồ/RoyalBlue/normal; bottom all-account stop uses _farming_acc=False + row _stop_event; singleton _daily_all_monitor waits for all row sessions then calls both activity reset helpers; _sync_start_tab_btns handles external sync.
- Runtime/B08 remain cross-check only: no correlated end-to-end Treasure trace is present in the packaged log, and B08 is idle configuration only.
- K15 evidence/model committed:
  - docs/daily/K15_TREASURE_HANDOFF_STATIC_EVIDENCE.tsv — commit 9fe81d923b5490541b13c11d52ea1cee81359f04
  - docs/daily/K15_TREASURE_HANDOFF_MODEL.json — commit ee589223cf3ff5eccac238e8184c6a78d4d3926b
- K15 remains IN_PROGRESS until flow/task docs, PROJECT_STATUS advancement, code/build recheck and STATE closure are persisted.
## K15 VERIFIED RESULTS
- GitHub-first continuity check passed: no K15 artifact/completion commit existed; K10-K14 remained unchanged.
- Exact library specimen TLMTool_2.1.2(7).zip was rematerialized before K15. Frozen authority remains archive SHA-256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd, size **93,715,901** bytes; inner TLMTool.exe SHA-256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22, size **47,450,112** bytes.
- K01 top-level handler inventory was audited against K10-K14. Every Treasure-related top-level callable is covered: _build_ui, _apply_treasure_all, _treasure_start_worker, _treasure_single_worker, _wait_movement_stopped, _treasure_map_toggle, _treasure_map_run_worker, _treasure_map_disconnect_monitor, _treasure_map_exec_sequence, _treasure_heal, _treasure_map_reset_ui.
- No top-level Treasure callable remains unaccounted for.
- Activity-wide and per-row Treasure ownership stay distinct and must not be collapsed.
- Integrated cycle handoff is frozen: session/stop guard -> consume respawn_event -> optional start HP<30 heal -> mount prep -> bag readiness -> first tangBaoDo_multi find/use -> MovementDetector movement-stop wait -> second tangBaoDo_multi checkpoint/use -> post-activation MapID/tomb region -> optional final heal -> cycle tail -> owning worker.
- Treasure production duration default is **30s**; direct _treasure_map_exec_sequence helper fallback is **5s**. This is a resolved layer distinction, not a contradiction.
- Current Treasure recognizer remains exactly tuido.tangBaoDo_multi with the K11 pattern; legacy tangBaoDo/tangBaoDo_multi_old are not the active Daily call.
- First and second map-item not-found remain terminal-current-Treasure-account conditions.
- Treasure movement-stop remains _wait_movement_stopped(stop_check,skip_set), by_memory=False -> MovementDetector/is_moving 10-pixel branch.
- Post-activation map96/tomb region preserves exact MapID96 combat text/state, fixed combat coords, tile(50,16)/1600,512 move surface, common.active wait and non96 outcome, while exact fixed-click/timing/MapID micro-order remains UNKNOWN.
- Treasure treatment remains selected-map driven with Đại Lý/Lạc Dương/Tô Châu/Lâu Lan coordinates, dynamic MAP_LIST resolution, shared movement tolerance48, no recovered Treasure fixed treatment click and no proven Treasure-specific heal reinjection.
- Start-heal failure remains SKIP_CURRENT_CYCLE; final-heal failure remains FAIL_SOFT_LOG_ONLY.
- Treasure disconnect monitor remains a thin event-adapter shape over the shared Daily detector layer. Treasure reconnect timeout numeric remains UNKNOWN; no forced post-reconnect reinjection is proven.
- Shared death/Map87 respawn_event recovery remains recoverable; simultaneous disconnect/death priority remains UNKNOWN.
- _treasure_map_skipped remains strong-static persistent exclusion state for terminally skipped HWNDs during the active batch; exact add/discard/clear statements and clear boundary remain UNKNOWN.
- Integrated failure matrix is internally consistent: batch no-op/end, terminal-current-account, current-cycle skip, tomb-outcome skip, fail-soft, recoverable interrupt, terminal recovery path and control-stop classes remain distinct.
- UI/stop handoff remains consistent: activity running Dừng lại/FireBrick -> stopping Đang dừng.../disabled -> idle Tàng bảo đồ/RoyalBlue/normal; bottom all-account stop uses _farming_acc=False + row _stop_event; singleton _daily_all_monitor waits for all rows then calls both reset helpers; _sync_start_tab_btns handles external sync.
- No blocking contradiction was found across K10-K14 and no already-correct artifact required rewriting.
- Packaged runtime log still has no correlated end-to-end Treasure trace; B08 remains idle-config-only. K15 classification is **STATIC_VERIFIED / END_TO_END_RUNTIME_ENV_REQUIRED**.
- From the Treasure perspective, static handoff is complete enough for later Stage-S reconstruction, but overall project Stage S remains blocked by remaining Phase K shared/runtime work and later PLAN phases.
- K15 artifacts:
  - docs/daily/K15_TREASURE_HANDOFF_STATIC_EVIDENCE.tsv — commit 9fe81d923b5490541b13c11d52ea1cee81359f04
  - docs/daily/K15_TREASURE_HANDOFF_MODEL.json — commit ee589223cf3ff5eccac238e8184c6a78d4d3926b
  - docs/daily/K15_TREASURE_HANDOFF_FLOW.md — commit 4367218e8c9a1486e0553c454cd7a90f7cf6df6a
  - docs/tasks/K15.md — commit fe41bb0226eab825a48de7e8bbd96e9c15de25d7
- PROJECT_STATUS.md advanced K15 -> VERIFIED and K16 -> NEXT at commit 478eaa7fecc39b342bf04586c84b2d22103f3340.

## POST-K15 CODE/BUILD RECHECK
- Current main tree after K15 status update: **610 entries**.
- Python executable-code files remain exactly the same **7 forensic scripts** under tools/.
- No reconstructed application source path exists.
- No build-system file or GitHub Actions workflow exists.
- Latest checked commit has **0 CI statuses** and **0 workflow runs**.
- All four K15 artifacts were fetched back successfully.
- K15 changed documentation/evidence only and introduced no executable-code regression.
- Product build remains **NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED**, not PASS/FAIL.

## BLOCKERS
- End-to-end Treasure parity still requires a real Windows + live Thần Long runtime.
- Reconstructed product build is still not applicable before Stage S because there is no app source/build target.
- No known static blocker for K16.

## DO_NOT_TOUCH
- Preserve K01-K15 contracts unchanged unless exact new evidence exposes a real contradiction.
- Preserve separate activity-wide vs per-row ownership for both Daily activities.
- Preserve all Treasure failure classes exactly; do not collapse terminal item-not-found, cycle skip, non96 skip, fail-soft and recoverable interruption.
- Preserve Treasure duration layering 30 production / 5 direct helper fallback.
- Preserve current tangBaoDo_multi recognizer and MovementDetector by_memory=False call site.
- Preserve selected-map Treasure heal and shared tolerance48; do not import Trừng Ác heal behavior.
- Preserve Treasure disconnect adapter/shared detector boundary and keep timeout numeric UNKNOWN.
- Preserve _treasure_map_skipped lifecycle role without inventing mutation micro-order.
- Preserve cooperative bottom stop/global monitor reset semantics and keep teardown statement order UNKNOWN.
- Do not create Stage-S source/build placeholders before PLAN reaches reconstruction.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md.
2. Read STATE.md.
3. Check GitHub first for any K16 artifacts/commits; if already complete and verified, do not redo them.
4. Execute **K16 — Daily shared cross-activity lifecycle / persistence / UI-coordinator integration audit** only.
5. Re-inspect the exact frozen original EXE first and use K01/K02/K09/K15 as closed activity contracts.
6. Audit only the cross-activity/shared Daily surfaces: roster refresh + HWND/PID identity, per-row activity dispatch, row Event/generation lifecycle, all-account Bắt đầu/Dừng lại coordinator, singleton _daily_all_monitor, _sync_start_tab_btns, config load/save/destruction persistence, shared state-label/Tk marshalling, and how Trừng Ác/Tàng Bảo Đồ activity-level workers coexist with row-level workers without ownership collision.
7. Identify any shared Daily top-level callable from K01 not yet covered by K02/K09/K15 and close only those gaps; do not reopen activity-specific internals.
8. Audit cross-activity contradictions and race/ownership boundaries only; keep runtime-only ordering UNKNOWN where native evidence is insufficient.
9. Cross-check runtime/B08 only after static integration, then re-check repo code/build state.
10. Persist K16 artifacts, update STATE.md/PROJECT_STATUS.md, and advance only after K16 verification.

## K16 VERIFIED RESULTS
- GitHub-first continuity check passed: no K16 artifact/completion commit existed; K01/K02/K09/K15 were treated as closed contracts and activity-specific internals were not reopened.
- Exact TLMTool_2.1.2(7).zip was revalidated before K16: SHA-256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd, size **93,715,901** bytes, ZIP CRC clean. Inner TLMTool.exe remains SHA-256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22, size **47,450,112** bytes.
- K16 closes the remaining shared/cross-activity top-level Daily gaps from K01: _validate_repeat, _ensure_injected, _inject_all_windows, _move_bo_dau, _move_bo_dau_all, _heal_bo_dau, _heal_all, _save_on_destroy, _load_config, _save_config.
- After K16, no shared/cross-activity top-level Daily callable remains unaccounted for.
- Shared roster contract remains K02-exact: incremental refresh every 5s, HWND+bound-PID identity, PID-reuse row recreation, 30ms scroll debounce, row permission gating, transient row/session fields.
- Row session protection remains exact: real row _stop_event + row _gen through _GenStop. Generation mismatch stops a stale worker after rapid Stop->Start.
- Shared Tk state path remains exact: _set_state -> _schedule_state_label -> Tk after(0) -> _apply_state_label. Background workers must not directly mutate row state widgets.
- Shared injection is now integrated explicitly: _ensure_injected uses dll_injector, PID resolution and default resources.dat path; exact outcomes include no-PID/failure/error, `already loaded`, and OK. _inject_all_windows applies the same preparation to current game windows. Repeated start paths are compatible with an already-loaded DLL state.
- Manual _move_bo_dau is exact at the shared boundary: one HWND -> Tô Châu map4 tile(224,285); invalid/dead window and permission surfaces are checked; injection failure is fail-open to direct movement; shared move_character is used.
- _move_bo_dau_all performs shared injection/preparation and parallel per-account movement with child-thread join/completion.
- Manual _heal_bo_dau targets Tô Châu map4 tile(155,252) and owns an HWND-targeted click_at treatment surface. _heal_all fans out the treatment action in parallel.
- Manual Tới bổ đầu/Trị liệu are activity-agnostic HWND/account actions rather than Trừng Ác/Treasure worker dispatch. Exact overlap exclusion with a running activity worker is **EXPLICIT_UNKNOWN** and reserved for K17 runtime parity.
- Bottom all-account coordinator remains exact: idle -> shared preparation -> dispatch each eligible row by current activity -> per-row worker; running -> row _farming_acc=False + row _stop_event -> cooperative unwind. Missing Trừng Ác teleport hotkey may skip only that row at the coordinator boundary.
- _daily_all_monitor remains singleton, waits until all row sessions stop, then calls both activity reset helpers and logs the automatic reset. _sync_start_tab_btns remains the external StartTab synchronization boundary.
- Cross-activity ownership domains are explicitly separate.
  - activity-wide Trừng Ác: _punish_running/_punish_cancel
  - activity-wide Treasure: _treasure_map_running/_treasure_map_cancel
  - row/bottom: row _farming_acc/_stop_event/_gen
- No unified Daily owner token/mutex and no independently-bound same-HWND mutual-exclusion guard between activity-wide and row ownership was recovered. K16 does not invent a mutex and does not assume overlap is safe; K17 must test the original runtime behavior.
- Shared persistence is now integrated: CONFIG_PATH/CONFIG_DIR/_settings_lock/read_settings/write_settings/Settings section; exact Daily load-key surface includes both activity config families plus the old/new teleport compatibility keys.
- No durable Daily keys exist for row activity selection, bound PID, _farming_acc, _stop_event, _gen or row state. Those remain runtime/session state.
- daily_move_mode is exact on the load side, but exact save/migration expression remains UNKNOWN; absence of a second literal in the save region is not proof it is never written because Nuitka can backreference constants.
- Constructor owns _closing/_saving_enabled/refresh state; <Destroy> is exactly bound to _save_on_destroy; _save_config writes shared settings and exposes [DAILY] Save error:. Exact destroy cleanup order remains UNKNOWN.
- _validate_repeat uses an isdigit generator surface and is classified only as numeric-entry validation. Its name is not evidence of a user repeat-count feature. Exact empty-string/cleanup behavior remains UNKNOWN.
- Cross-activity contradiction audit found **0 blocking contradictions** across K02 shared infrastructure, K09 Trừng Ác handoff and K15 Treasure handoff.
- Exact packaged automove_log remains SHA-256 17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500, **15,741,058 bytes / 387,238 lines**. Correlated counts are zero for [Daily], [Bắt đầu], [Inject], DailyTab, Tới bổ đầu, [Trị liệu], Trừng ác and Tàng bảo đồ.
- B08 remains an idle empty-account-list cross-check and cannot prove concurrency/ownership races.
- K16 classification is **STATIC_VERIFIED / END_TO_END_RUNTIME_ENV_REQUIRED**.
- K16 artifacts:
  - docs/daily/K16_SHARED_INTEGRATION_STATIC_EVIDENCE.tsv — commit d8bcffa13d31bfb34709168f616cbb961287986f
  - docs/daily/K16_SHARED_INTEGRATION_MODEL.json — commit a88bcdb8d5c59db0204f17ed713c7db938ffa8e4
  - docs/daily/K16_SHARED_INTEGRATION_FLOW.md — commit dfb44f9d3061604a6c5c4979aca7b8f11839fbf3
  - docs/tasks/K16.md — commit dbba8650411436355a8b422660a6065e8bda533e
- PROJECT_STATUS.md advanced K16 -> VERIFIED and K17 -> NEXT at commit 729cb28a76dab03503e7f6211df17a4c8abdcd70.

## POST-K16 CODE/BUILD RECHECK
- Current main tree after K16 status update: **614 entries**.
- Python executable-code files remain exactly the same **7 forensic scripts** under tools/.
- No reconstructed application source path exists.
- No build-system file or GitHub Actions workflow exists.
- Latest checked commit has **0 CI statuses** and **0 workflow runs**.
- All four K16 artifacts were fetched back successfully.
- K16 changed documentation/evidence only and introduced no executable-code regression.
- Product build remains **NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED**, not PASS/FAIL.

## BLOCKERS
- End-to-end Daily concurrency/parity still requires a real Windows + live Thần Long runtime.
- Reconstructed product build is still not applicable before Stage S because there is no app source/build target.
- Static K16 cannot resolve same-HWND overlap between activity-wide and row/manual ownership domains; this is intentionally deferred to K17 runtime parity.

## DO_NOT_TOUCH
- Preserve K01-K16 contracts unchanged unless exact new evidence exposes a real contradiction.
- Preserve HWND+PID identity and row Event+generation stale-worker protection.
- Preserve Tk after(0) state marshalling.
- Preserve shared injection already-loaded/idempotent-ready semantics.
- Preserve manual all-account movement/heal as shared HWND actions; do not silently turn them into activity workers.
- Preserve separate activity-wide and row ownership domains; do not invent a cross-domain mutex before runtime evidence.
- Preserve transient row activity/session state; do not persist it without evidence.
- Preserve daily_move_mode compatibility ambiguity and _save_on_destroy teardown order as UNKNOWN.
- Do not create Stage-S source/build placeholders before PLAN reaches reconstruction.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md.
2. Read STATE.md.
3. Check GitHub first for any K17 artifacts/commits; if already complete and verified, do not redo them.
4. Execute **K17 — Daily integrated runtime/parity closure matrix and Phase-K handoff** only.
5. Treat K09 Trừng Ác, K15 Treasure and K16 shared static contracts as frozen. Do not reopen them unless a runtime contradiction is observed.
6. Build the exact runtime/parity test matrix required to validate the remaining environment-only boundaries: populated roster refresh/PID reuse, per-row rapid Stop->Start generation guard, activity-wide vs row same-HWND overlap, manual Tới bổ đầu/Trị liệu while workers run, all-account mixed Trừng Ác+Treasure start/stop, singleton monitor reset, reconnect/death recovery, config save/reload/destroy persistence, and UI/StartTab synchronization.
7. Use packaged runtime evidence where available, but explicitly mark tests requiring a real Windows + live Thần Long environment as NOT_EXECUTABLE_HERE rather than fabricating PASS.
8. Determine whether Phase K can be statically closed with a runtime-test handoff package; do not claim live parity PASS without real environment evidence.
9. Re-check repository code/build state after K17 docs/evidence changes.
10. Persist K17 artifacts, update STATE.md/PROJECT_STATUS.md, and only then advance from Phase K to Phase L.

## K17 VERIFIED RESULTS
- GitHub-first continuity check passed: no K17 artifact/completion commit existed; K09, K15 and K16 were treated as frozen inputs.
- Exact TLMTool_2.1.2(7).zip was revalidated: SHA-256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd, size **93,715,901** bytes, ZIP CRC clean. Inner TLMTool.exe remains SHA-256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22, size **47,450,112** bytes.
- Packaged automove_log was re-extracted and revalidated: SHA-256 17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500, **15,741,058 bytes / 387,238 lines**.
- Rechecked counts are zero for [Daily], [Bắt đầu], [Inject], DailyTab, Tới bổ đầu, [Trị liệu], Trừng ác, Tàng bảo đồ, Mất kết nối, Địa phủ and Tất cả acc đã dừng.
- Packaged runtime evidence is **VERIFIED_NEGATIVE_EVIDENCE**, not live parity proof.
- K17 produced a **20-case** Daily runtime/parity matrix. Cases requiring the original Windows + live Thần Long environment are explicitly **NOT_EXECUTABLE_HERE**; no fabricated PASS was recorded.
- Runtime matrix covers roster/PID reuse, rapid Stop->Start generation protection, mixed all-account activities, ownership overlap, manual shared-action overlap, injection re-entry, both activity lifecycles/recovery paths, Treasure terminal item-miss exclusion, config/destroy persistence, StartTab synchronization, window/PID invalidation and Tk state marshalling.
- Static closure audit confirms **0 blocking contradictions** across K09 Trừng Ác, K15 Treasure and K16 shared Daily.
- All Daily top-level callables are accounted for; no known static handler gap remains.
- Phase-K decision: **STATIC RESEARCH COMPLETE / LIVE RUNTIME PARITY PENDING**. This is not a live parity PASS.
- Remaining unresolved Daily items are runtime/environment-only: cross-domain ownership policy, manual-action overlap policy, Treasure reconnect timeout/event ordering, destroy cleanup order, live daily_move_mode persistence/migration, live thread timing and UI sync timing.
- K17 artifacts:
  - docs/daily/K17_RUNTIME_PARITY_MATRIX.tsv — commit dab0b3d6eead84cb1b06f3bb160b884d5b5ab1e6
  - docs/daily/K17_PHASE_K_HANDOFF_MODEL.json — commit 5294ced7ad04a315d892cbd411ed794b4b62b07e
  - docs/daily/K17_PHASE_K_HANDOFF.md — commit 2467f2b9babe07ce4d72092915d84cfd6c1594f6
  - docs/tasks/K17.md — commit e5d12679c12a59d4444ad2a48bcfe98e1161cf94
- PROJECT_STATUS.md marked K17 static closure and advanced to Phase L / L01 at commit 2490833d5969ddf9da784c5da58515129ab1442a.

## POST-K17 CODE/BUILD RECHECK
- Current main tree after K17 status update: **618 entries**.
- Python executable-code files remain exactly the same **7 forensic scripts** under tools/.
- No reconstructed application source path exists.
- No build-system file or GitHub Actions workflow exists.
- Latest checked commit has **0 CI statuses** and **0 workflow runs**.
- All four K17 artifacts were fetched back successfully.
- K17 changed documentation/evidence only and introduced no executable-code regression.
- Product build remains **NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED**, not PASS/FAIL.

## PHASE K GATE
- **STATIC_RESEARCH_CLOSED / LIVE_RUNTIME_PARITY_DEFERRED**.
- K17 runtime matrix is the required later parity checklist.
- Do not reopen K01-K16 unless future runtime evidence exposes a real contradiction.

## BLOCKERS
- Live Daily parity still requires Windows + live Thần Long runtime.
- Reconstructed product build is still not applicable before Stage S.
- No known static blocker for Phase L.

## DO_NOT_TOUCH
- Preserve K01-K17 Daily contracts and the distinction between static closure and live parity.
- Never convert K17 NOT_EXECUTABLE_HERE cases into PASS without real evidence.
- Preserve unresolved runtime-only ownership/overlap/teardown behaviors as UNKNOWN until tested.
- Do not create Stage-S source/build placeholders before PLAN reaches reconstruction.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md.
2. Read STATE.md.
3. Check GitHub first for any L01 artifacts/commits; if already complete and verified, do not redo them.
4. Execute **L01 — Dồn authority / visible surface / handler inventory / dependency boundary audit** only.
5. Re-inspect the exact frozen original EXE first; do not infer Dồn behavior from prior tools/projects.
6. Identify the active Dồn module/class in the main app, visible UI surface, top-level callable inventory and direct dependency boundary.
7. Separate visible/current behavior from dormant/static references.
8. Use screenshots/runtime evidence only after EXE-first static extraction.
9. Persist L01 artifacts, update STATE.md/PROJECT_STATUS.md, re-check code/build state, and advance only after L01 verification.
## K17 FINAL SYNC
- PROJECT_STATUS.md closure summary was finalized at commit 03b9f8ec08b0b98cfe770db4b8ab996a7211bbf9.
- Latest checked commit still has **0 CI statuses** and **0 workflow runs**.
- NEXT_ACTION remains L01 exactly as recorded above.
## PHASE-L TERMINOLOGY CORRECTION
- User correction applied: the project phase/function name is **Dồn**, not Đồn.
- Internal compiled identifiers remain `donvang_tab` / `DonVangTab` because those are exact original binary/source identifiers and must not be renamed in forensic evidence.
- Terminology was corrected in the planning/status/handoff documents before L01:
  - PLAN.md — commit 350c1a1a74bc536a7dd1d4d707d5c90bef5970a0
  - PROJECT_STATUS.md — commit b6f675177a91f6af4815f8f3629be2024964d495
  - STATE.md — commit 428d27a822c1f327e46763eb92d187d1bd620279
  - docs/tasks/K17.md — commit fdc63f99e88e2881556957604e9b477e69537ba9
  - docs/daily/K17_PHASE_K_HANDOFF.md — commit bf75d1c5a101dff85f83584e502a702961a7164d
  - docs/daily/K17_PHASE_K_HANDOFF_MODEL.json — commit 7a937862e84147ed5b1fe32b37c151d1310329ea

## L01 VERIFIED RESULTS
- GitHub-first continuity check passed: no pre-existing L01 artifact/completion commit existed.
- Exact TLMTool_2.1.2(7).zip was re-inspected before L01; frozen authority remains archive SHA-256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd, size **93,715,901** bytes, CRC clean; inner TLMTool.exe SHA-256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22, size **47,450,112** bytes.
- Active Dồn authority is exact: module `donvang_tab`, source label `donvang_tab.py`, class `DonVangTab`.
- Frozen module marker `.donvang_tab` is at **0x2920bc1**. Header size field is **65,260 bytes** and header constant-count field is **1,813**; next module marker `.emu_chat` is at **0x2930abd**.
- Source filename string `donvang_tab.py` is at 0x292e0da; module qualname `<module donvang_tab>` at 0x292e366; class `DonVangTab` at 0x292d1c6.
- L01 inventories **127 direct top-level DonVangTab methods**. Nested `<locals>` functions are excluded from the top-level handler inventory.
- Main-app wiring is exact: TLMMainApp owns `donvang_tab`, constructs `DonVangTab`, exposes visible tab label **Dồn**, and owns `_set_donvang_tab_visible`.
- Static visibility comment describes permission/dev-like gating. The captured run shows Dồn visible; the exact permission state causing that captured visibility remains **UNKNOWN** rather than inferred.
- StartTab wiring is exact: **Dồn vàng / Tới nơi nhận / Tới chỗ bán / Tới nơi train / Cấu hình**, with direct callables `_goto_donvang_tab`, `_donvang_action`, `_toggle_donvang_cmd`.
- Visible Dồn surface is frozen at L01 scope:
  - Cấu hình Về thành: Khi đầy túi / Theo chu kỳ (phút), navigation priority Phù1/Phù2/Phù3/Ngựa.
  - Cấu hình Train: quay lại train khi chết, dừng khi mất kết nối, tự gỡ kẹt, nhặt đồ không dùng hồ lô, lọc đồ, trị liệu sau khi chết, tọa độ trị liệu.
  - saved-coordinate editor;
  - shared Tọa độ dồn and dynamic Acc nhận rows;
  - per-account Đến tọa độ / Dồn đồ / Tới nơi dồn / Bán đồ;
  - elapsed-time / gold-donated / gold-per-hour metrics;
  - all-account Tới nơi nhận / Tới chỗ bán / Tới nơi train and bottom Bắt đầu.
- Screenshot cross-check was performed only after EXE-first extraction:
  - Dồn-tab capture SHA-256 dffb4da895d21dea87dd72a6601c29104f519dca89c2f716f5a7445bcbe4421a, 452x1032.
  - StartTab capture SHA-256 4f1b126ea4ba0034889545653046f552a226d5f0033d2329a8693342184c28cd, 452x1032.
  - Captured Dồn state: cycle mode 30 minutes, Phù1/Phù2/Phù3/Ngựa priority surface, Tự gỡ kẹt checked, filter Tất cả, heal map Trị liệu Tô Châu, saved coord Tọa độ1/Đại Lý/0/0, two receiver rows visible, no live game-account rows, bottom Bắt đầu.
- Persistence authority is frozen: `[DonVang]` settings section and exact autosave documentation of **30 seconds**. Exact per-key behavior is deferred.
- Direct/current dependency boundary is frozen: tkinter/ttk/font, os/configparser/shared settings, farm_data, start_tab, permission_guard, utils, dll_injector, don_logic, fast_travel, memory_items, bag_filter, pixel, HWND/mouse/window helpers, and constructor-supplied info_tab object.
- `farm_tab` remains a reference/docstring surface only for L01 and is not promoted to a current runtime import.
- Existing graph-only `donvang_tab -> emu_input/emu_reader` edges remain **STATIC_REFERENCE_NOT_IMPORT_PROOF**; no direct DonVang literal/call evidence was recovered for those edges.
- Dồn is therefore **ACTIVE/WIRED, NOT DORMANT**.
- L01 intentionally does not resolve return mechanism/priority, full-bag inventory logic, receiver selection, selling, train lifecycle, heal/reconnect, all-account execution semantics, or parity.
- L01 artifacts were committed together at commit **935a5f9645e5d4273b12c56b70eaebf60df9c530**:
  - docs/don/L01_HANDLER_INVENTORY.tsv
  - docs/don/L01_DEPENDENCIES.tsv
  - docs/don/L01_STATIC_EVIDENCE.tsv
  - docs/don/L01_MODEL.json
  - docs/don/L01_AUTHORITY_SURFACE.md
  - docs/tasks/L01.md
- PROJECT_STATUS.md advanced L01 -> VERIFIED and L02 -> NEXT at commit **971e0ae980384f87a427f973cb672c62992491b2**.

## POST-L01 CODE/BUILD RECHECK
- Current main tree after L01 status update: **625 entries**.
- Python executable-code files remain exactly the same **7 forensic scripts** under tools/.
- No reconstructed application source path exists.
- No build-system file or GitHub Actions workflow exists.
- Latest checked L01 status commit has **0 CI statuses** and **0 workflow runs**.
- All six L01 artifacts were fetched back successfully.
- L01 changed documentation/evidence only and introduced no executable-code regression.
- Product build remains **NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED**, not PASS/FAIL.

## BLOCKERS
- L01 has no known static blocker.
- Dồn end-to-end behavior will still require live Windows/game parity later in Phase L.
- Reconstructed product build remains not applicable before Stage S.

## DO_NOT_TOUCH
- Use **Dồn** in planning/user-facing documentation. Preserve `donvang_tab` / `DonVangTab` as exact original identifiers.
- Preserve L01 active-authority and 127-handler inventory unless exact new evidence exposes a contradiction.
- Preserve permission-controlled visibility as a separate layer from the captured visible state; do not infer account entitlement from screenshot text.
- Do not promote weak farm_tab/emulator references into active runtime dependencies without direct evidence.
- Do not infer later Dồn return/inventory/receiver/sell/train behavior from UI labels alone.
- Do not create Stage-S source/build placeholders before PLAN reaches reconstruction.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md.
2. Read STATE.md.
3. Check GitHub first for any L02 artifacts/commits; if already complete and verified, do not redo them.
4. Execute **L02 — Dồn return mechanism audit** only.
5. Re-inspect the exact frozen original EXE first, focusing on `_on_town_condition_changed`, `_on_nav_priority_changed`, `_get_nav_priority`, `_move_acc`, `_truyen_move_retry`, `_exec_truyen_steps`, `_move_truyen_to`, `_resolve_truyen_back`, `_run_farm_exit`, and only directly-called helpers needed by the return path.
6. Determine exact return triggers/mechanisms, route/fallback behavior, stop/cancel ownership, and how return-to-town hands off to receiver/sell/train boundaries without deep-auditing those later tasks.
7. Keep return **priority ordering** details separated if PLAN requires them for the following task; do not collapse L02 and later Phase-L tasks unnecessarily.
8. Cross-check screenshots/runtime only after static extraction.
9. Persist L02 artifacts, update STATE.md/PROJECT_STATUS.md, re-check code/build state, and advance only after L02 verification.
## L02 VERIFIED RESULTS
- GitHub-first continuity check passed: no pre-existing L02 artifact/completion commit existed; L01 remained unchanged.
- Exact TLMTool_2.1.2(7).zip was re-inspected before L02. Frozen authority remains archive SHA-256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd, size **93,715,901** bytes, CRC clean; inner TLMTool.exe SHA-256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22, size **47,450,112** bytes.
- Exact `.donvang_tab` was decoded/re-inspected for L02 as **65,260 bytes / 1,813 constants**, exact end.
- Dồn return trigger has two exact production modes:
  - internal `cycle` -> visible **Theo chu kỳ (phút)**;
  - internal `full_bag_timer` -> visible **Khi đầy túi**.
- Default return mode is `cycle`; default cycle value is **30 minutes**. The farm-cycle block owns `cycle_start/loop_minutes/elapsed/sleep_time` plus constant60, proving minute-based cycle timing while exact poll/sleep micro-order remains UNKNOWN.
- Full-bag return path reads memory bag-full state, then runs `_filter_before_don` before committing to return/Dồn.
- Exact full-bag semantics: filter frees space -> stay at farm and wait later cycle; still full after filtering -> continue return/Dồn path.
- Nearby constants 3/98/100 were preserved but **not interpreted** in L02. Exact inventory/full-bag thresholds are deferred to the later inventory task.
- `_farm_cycle` exact contract says donor callback replaces the ordinary return-to-town step with Dồn. Therefore donor Dồn and normal sell/town return are separate high-level handoff outcomes.
- `_resolve_truyen_back` exact return mechanism is frozen:
  - resolve current MapID first;
  - fall back to configured farm preset only if memory read fails;
  - obtain a map-specific `back` route from `farm_data.TRUYEN_DAI_LY_ROUTES`;
  - route None -> normal movement;
  - route present -> execute serialized steps -> invalidate Reader cache -> fresh `verify_exited_farm` check;
  - if verification fails and stop is requested -> abort;
  - if verification fails without stop -> **walk to the final destination**.
- Therefore the Truyền back route is an optimization/shortcut, not a mandatory success condition.
- Frozen back-route data includes:
  - 85/86 -> map85 tile(226,58);
  - 43 -> tile(135,168);
  - 49 -> tile(147,209);
  - 64 -> tile(196,156);
  - 60 -> tile(207,200);
  - 83 -> tile(158,75);
  - 75/76 -> map75 tile(131,123);
  - followed by serialized click(892,472), click(480,427) twice, sleep1, wait common.active30.
- Routes 1300/1400/1700 have serialized entries but empty `back` lists; they do not themselves provide a return-movement sequence.
- `_run_farm_exit` is the Dồn/receiver-return wrapper. Its direct defaults are `(None, "Về dồn")` for the optional stop/tag surface.
- `_run_farm_exit` exact behavior: execute Truyền back shortcut when applicable, then perform the final Dồn/receiver leg by **normal horse movement with no phù**. Ordinary maps with no back route use the normal `_move_acc` behavior.
- The standard sell-return path remains separate: `_sell_acc` resolves selling coordinates, may use the same back-shortcut boundary, and on shortcut failure logs `teleport hụt, vẫn ở farm → đi bộ về điểm bán`.
- Standard sell movement passes `_get_nav_priority()` to `move_character` as `home_priority` and has one explicit retry after first normal move failure.
- L02 intentionally freezes only the priority-list handoff. Exact Phù1/Phù2/Phù3/Ngựa ordering, deduplication and fallback semantics are deferred to L03.
- Automatic return is cooperative: farm-cycle `stop_check` propagates through `_run_farm_exit`, `_resolve_truyen_back`, `_exec_truyen_steps`, `_move_acc` and retry surfaces.
- Manual `_move_acc` is distinct: it can run with no stop callback, but exact guard rejects a manual move when the account is already auto-farming and asks that farm be stopped first.
- `_toggle_single_farm` builds a donor callback and passes it into `_farm_cycle`; donor-side state boundary includes **Về dồn -> Đang dồn** and actual Dồn transaction is delegated to `don_logic.don_move_and_execute`.
- Receiver choice/locking/transaction internals were not expanded. Receiver-cycle boundary from `don_logic` is only recorded as sell -> return to receiver point -> ready -> wait donated -> repeat.
- Outbound town->farm `to/to_from` routes exist but are train-state scope, not return-mechanism scope.
- `TEST_SKIP_TOWN` is preserved as a debug/test bypass surface and is not treated as production return policy.
- Packaged automove_log remains SHA-256 17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500, **15,741,058 bytes / 387,238 lines**. Correlated L02 Dồn-return markers are **0**, so L02 remains **STATIC_VERIFIED / END_TO_END_RUNTIME_ENV_REQUIRED**.
- L02 artifacts committed together at **de7c624a55d33f1c8bde97a0326b8827d99bfe94**:
  - docs/don/L02_RETURN_STATIC_EVIDENCE.tsv
  - docs/don/L02_RETURN_MODEL.json
  - docs/don/L02_RETURN_FLOW.md
  - docs/tasks/L02.md
- PROJECT_STATUS.md advanced L02 -> VERIFIED and L03 -> NEXT at commit **4a7e0d155f1f3fc5cbc8d419790ef09774973434**.

## POST-L02 CODE/BUILD RECHECK
- Current main tree after L02 status update: **629 entries**.
- Python executable-code files remain exactly the same **7 forensic scripts** under tools/.
- No reconstructed application source path exists.
- No build-system file or GitHub Actions workflow exists.
- Latest checked L02 status commit has **0 CI statuses** and **0 workflow runs**.
- All four L02 artifacts were fetched back successfully.
- L02 changed documentation/evidence only and introduced no executable-code regression.
- Product build remains **NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED**, not PASS/FAIL.

## BLOCKERS
- L02 has no known static blocker.
- Live Dồn return timing/parity still requires Windows + live Thần Long runtime.
- Exact navigation-priority policy is intentionally deferred to L03, not a blocker.

## DO_NOT_TOUCH
- Preserve L01 authority/handler inventory and L02 return mechanism unless exact new evidence exposes a contradiction.
- Preserve Dồn-specific back route as shortcut + fresh verify + walking fallback, not as a mandatory return requirement.
- Preserve final Dồn/receiver leg as normal horse movement with no phù.
- Keep normal sell path separate and keep `home_priority` ordering details for L03.
- Do not infer bag thresholds from constants 3/98/100 before the inventory task.
- Do not deepen receiver/transaction/train-state logic during L03 unless directly required by the priority call path.
- Do not create Stage-S source/build placeholders before PLAN reaches reconstruction.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md.
2. Read STATE.md.
3. Check GitHub first for any L03 artifacts/commits; if already complete and verified, do not redo them.
4. Execute **L03 — Dồn return priority audit** only.
5. Re-inspect the exact frozen original EXE first, focusing on `_on_nav_priority_changed`, `_get_nav_priority`, the UI variables for Phù1/Phù2/Phù3/Ngựa, persistence of priority selection, and the direct `move_character(home_priority=...)` consumers.
6. Determine exact ordering construction, duplicate/disabled-entry handling, default order, fallback semantics, and whether priority affects only normal return-to-town/sell movement or any other Dồn movement boundary.
7. Preserve L02's special Dồn/receiver final leg **no phù**; do not accidentally apply normal return priority there unless direct evidence contradicts L02.
8. Cross-check screenshots/runtime only after static extraction.
9. Persist L03 artifacts, update STATE.md/PROJECT_STATUS.md, re-check code/build state, and advance only after L03 verification.


## L03 VERIFIED RESULTS
- GitHub-first continuity check passed: no pre-existing L03 artifact/completion file existed before this task; L01/L02 remained unchanged.
- Exact original authority was revalidated before UI/image cross-check. Uploaded `TLMTool_2.1.2(8).zip` is byte-identical to the frozen archive SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, size **93,715,901** bytes; inner `TLMTool.exe` remains SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, size **47,450,112** bytes.
- Exact Dồn priority option list is `["", "Phù 1", "Phù 2", "Phù 3", "Ngựa"]`; exact defaults are `["Phù 1", "Phù 2", "Phù 3", "Ngựa"]`.
- The leading empty option is intentional and represents a disabled/unused priority slot.
- All four priority controls are readonly comboboxes. `_on_nav_priority_changed` exposes exact locals `NAV_OPTIONS, idx, var, used, other_var, val, current, available`, strongly fixing the normal UI duplicate-prevention model: available values are recomputed against the other used selections while preserving current state.
- Normal UI cannot newly select duplicate nonblank priorities after the available-choice refresh. Exact auto-normalization of a hand-edited/legacy config that is already duplicated remains an explicit config-fixture/runtime microcase rather than being guessed.
- Priority persistence is exact under `[DonVang]` with keys `nav_priority_1`, `nav_priority_2`, `nav_priority_3`, `nav_priority_4`; save-side prefix is `nav_priority_`.
- `_get_nav_priority` exact compiled documentation says the UI Phù1/2/3/Ngựa list is passed into `move_character`.
- Shared `utils.move_character` has `home_priority / has_phu / sel / key_num` state plus the exact `Ngựa` label and a return-home log shape `Về thành: thử <selection> → bấm phím <key_num>`. This fixes Phù entries as ordered hotkey attempts and Ngựa as the non-hotkey ordinary-movement fallback.
- Shared fast-travel documentation independently confirms `home_priority` passthrough for the return-town/walking leg and that callers forcing horse movement pass `None`.
- Inside exact `donvang_tab`, the only production `home_priority` literal is in `_sell_acc`, directly beside `_get_nav_priority`. Therefore the configured Dồn return priority applies to the normal/shared sell movement path, not every Dồn move.
- L02 remains unchanged: `_run_farm_exit` Dồn/receiver final leg is normal horse movement with **no phù**; Truyền back remains shortcut → fresh verify → walking fallback.
- Screenshot cross-check was performed only after EXE-first extraction. Dồn capture SHA-256 remains `dffb4da895d21dea87dd72a6601c29104f519dca89c2f716f5a7445bcbe4421a` and visually matches the static default order Phù1/Phù2/Phù3/Ngựa.
- Frozen packaged runtime log remains SHA-256 `17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`; correlated `Về thành: thử` / DonVang / Dồn priority traces are **0**, so live attempt timing/failure progression is not fabricated.
- L03 artifacts were committed together at commit **29105d93c3c4c928d2f318bc827b1c7599360217**:
  - `docs/don/L03_PRIORITY_FLOW.md`
  - `docs/don/L03_PRIORITY_MODEL.json`
  - `docs/don/L03_PRIORITY_STATIC_EVIDENCE.tsv`
  - `docs/tasks/L03.md`
- All four L03 artifacts were fetched back successfully after commit.

## POST-L03 CODE/BUILD RECHECK
- Current recursive main tree after L03 artifact commit contains **633 entries** and is not truncated.
- Python executable-code files remain exactly the same **7 forensic scripts** under `tools/`; L03 added documentation/evidence only.
- No reconstructed application source directory exists.
- No build-system file and no GitHub Actions workflow exists.
- L03 artifact commit has **0 combined CI statuses** and **0 workflow runs**.
- Therefore L03 introduced no executable-code/build regression.
- Product build remains **NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED**, not PASS/FAIL.

## BLOCKERS
- L03 has no known static blocker.
- Exact migration behavior for an already-duplicated legacy/hand-edited priority config still needs a controlled config fixture or live runtime.
- Live Phù-attempt timing and transition to Ngựa fallback still require Windows + live Thần Long runtime.
- Reconstructed product build remains not applicable before Stage S.

## DO_NOT_TOUCH
- Preserve L01/L02/L03 contracts unless exact new evidence exposes a contradiction.
- Do not apply `home_priority` to L02's `_run_farm_exit` final Dồn/receiver leg; that leg remains no-phù.
- Do not reinterpret the blank priority option as missing/corrupt data; it is a real disabled slot.
- Do not infer inventory thresholds from constants 3/98/100 before L04.
- Do not deepen receiver/coordinates/train logic during L04 unless directly required by the inventory call path.
- Do not create Stage-S application/build placeholders before PLAN reaches reconstruction.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md.
2. Read STATE.md.
3. Check GitHub first for any L04 artifacts/commits; if already complete and verified, do not redo them.
4. Execute **L04 — Dồn inventory/full-bag filtering audit** only.
5. Re-inspect the exact frozen original EXE first, focusing on `_get_bag_slots`, `_filter_before_don`, `get_pickup_preset_keys`, `_pickup_no_cankhon`, the full-bag branch inside `_farm_cycle`, exact nearby constants `3/98/100`, and only directly-called `bag_filter` / `memory_items` helpers needed to resolve the inventory path.
6. Determine the exact full-bag threshold/state interpretation, filtering/preset behavior, free-space recheck, pickup-mode interaction, and the handoff back into the already-proven return/Dồn boundary without deep-auditing receiver, coordinates or train lifecycle.
7. Cross-check screenshots/runtime only after static extraction.
8. Persist L04 artifacts, update STATE.md/PROJECT_STATUS.md, re-check code/build state, and advance only after L04 verification.


## L04 VERIFIED RESULTS
- GitHub-first continuity check passed: no pre-existing L04 artifact/completion existed; L01-L03 remained unchanged.
- Exact uploaded `TLMTool_2.1.2(8).zip` was revalidated before screenshot use: SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, size **93,715,901** bytes, **1,050** ZIP entries, CRC clean. Inner `TLMTool.exe` remains SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, size **47,450,112** bytes.
- Exact Dồn module remained `.donvang_tab` size **65,260 bytes / 1,813 constants**. Shared `.bag_filter` was revalidated at `0x28d5db3`, **5,162 bytes / 145 constants**; shared `.memory_items` at `0x2b69c5f`, **47,850 bytes / 895 constants**.
- `DonVangTab._get_bag_slots` exact compiled documentation fixes bag count as **occupied Site-10 slots**; read failure returns `None` and preserves the previous displayed value rather than synthesizing zero.
- Dồn keep-mode constants are exact:
  - modes `("all","weapons")`;
  - labels `all -> Tất cả`, `weapons -> Chỉ vũ khí`;
  - preset mapping `all -> []`, `weapons -> ["discard_nonweapon"]`;
  - default `all`.
- Therefore Dồn intentionally has only **Tất cả / Chỉ vũ khí**. There is no Dồn `Không` mode and Dồn does not opt into `discard_weapons`.
- `get_pickup_preset_keys` exact documentation says the Dồn radio maps into `bag_filter(train)` preset keys and `[]` means no discard.
- `_filter_before_don` exact call surface is `bag_filter.discard_for_activity(... activity="train", keys=..., stop_check=...)`; Dồn provides only `keys` and `stop_check`.
- Shared exact filter defaults therefore remain active: delay **1.0s**, empty keys/rules do nothing, selected rules OR-combine, targets dedupe by `dbID`, and discard uses packet/opcode **100005**, action **4**, payload `4:<dbID>`, whole stack.
- Temporary filter state is **Đang lọc đồ** with foreground `#8e24aa`; prior state is restored only if another actor has not changed it meanwhile.
- Hidden pickup remains a separate control. `_pickup_no_cankhon` has exact default delay `(5,)`, then calls `memory_items.set_auto_fields` with `PICKITEM.IsOn=True` (bool). Exact documentation says the old manual UI click sequence was removed. No recurring 5-second polling surface was recovered.
- Full-bag constants were resolved from one exact source-local region:
  - `full_bag_timer/full_bag`;
  - nested `stop_bag_check`;
  - exact callback-default tuple `(3,)`;
  - numeric constants **98** and **100**;
  - locals `no_cankhon/threshold/bag/slots` plus post-filter `_nc/_th/_after`.
- Strong static binding fixes the Dồn full threshold as **98 occupied slots when hidden pickup is ON, 100 when hidden pickup is OFF**.
- The nearby **3 is not a slot threshold**. It is the exact single default attached to nested `stop_bag_check`. Its exact parameter name and debounce/confirmation micro-order are not source-visible enough to claim, so L04 preserves that one detail as UNKNOWN rather than inventing “3 samples”.
- Full-bag handoff is exact at L04 scope: detect full -> `_filter_before_don` -> re-read occupied slots/current threshold. If filter frees enough space, exact log says `đầy túi nhưng lọc còn chỗ (...) ô) → ở lại, chờ vòng sau`; if still full, exact log says `lọc xong vẫn đầy (...)` and the flow continues into the already-proven L02 Dồn boundary. A `None` result does not fabricate free space.
- Screenshot cross-check happened only after static extraction. Dồn screenshot SHA-256 remains `dffb4da895d21dea87dd72a6601c29104f519dca89c2f716f5a7445bcbe4421a`; it shows hidden pickup unchecked and `Tất cả` selected, with only `Tất cả / Chỉ vũ khí` radios. Captured effective threshold is therefore **100** and pre-Dồn preset list is empty.
- Frozen packaged `automove_log.txt` remains SHA-256 `17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`, **387,238 lines**. Correlated DonVang/full-bag/filter/PICKITEM/IsOn/Đang-lọc markers are **0**. Raw `action=4` appears **22,734** times but remains primitive-only evidence, not attributable to Dồn.
- L04 artifacts committed together at **9c7b32bd16251817583930dbbc36f777f6e5aa1c**:
  - `docs/don/L04_INVENTORY_FLOW.md`
  - `docs/don/L04_INVENTORY_MODEL.json`
  - `docs/don/L04_INVENTORY_STATIC_EVIDENCE.tsv`
  - `docs/tasks/L04.md`
- All four L04 artifacts were fetched back successfully.

## POST-L04 CODE/BUILD RECHECK
- Recursive main tree after L04 artifact commit contains **637 entries**, not truncated.
- Python executable-code files remain exactly the same **7 forensic scripts** under `tools/`.
- No reconstructed application source directory exists.
- No build-system file and no GitHub Actions workflow exists.
- L04 artifact commit has **0 combined CI statuses** and **0 workflow runs**.
- L04 changed documentation/evidence only and introduced no executable-code/build regression.
- Product build remains **NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED**, not PASS/FAIL.

## BLOCKERS
- L04 has no known static blocker.
- Exact callback-local meaning/micro-order behind `stop_bag_check` default **3** still needs stronger source recovery or controlled runtime/config instrumentation.
- Live post-discard memory propagation and end-to-end Dồn full-bag parity require Windows + live Thần Long runtime.
- Reconstructed product build remains not applicable before Stage S.

## DO_NOT_TOUCH
- Preserve L01-L04 contracts unless exact new evidence exposes a contradiction.
- Preserve Dồn keep policy as exactly two modes; do not import ordinary Train's third `Không` mode into Dồn.
- Preserve hidden pickup and keep/discard policy as separate controls.
- Preserve full thresholds **98 with hidden pickup ON / 100 with hidden pickup OFF**.
- Do not relabel callback default 3 as a proven 3-sample confirmation without stronger evidence.
- Preserve L02 return boundary and L03 priority boundary; do not re-open them during coordinates work.
- Do not deepen receiver selection/transaction while auditing coordinates unless directly required by the coordinate call path.
- Do not create Stage-S application/build placeholders before PLAN reaches reconstruction.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md.
2. Read STATE.md.
3. Check GitHub first for any L05 artifacts/commits; if already complete and verified, do not redo them.
4. Execute **L05 — Dồn coordinates audit** only.
5. Re-inspect the exact frozen original EXE first, focusing on `_coord_name_list`, `_preset_to_vars`, `_name_to_coords`, `_apply_coord_to_all`, `_on_map_select`, `_on_sep_select`, `_add_coord_row`, `_remove_coord_row`, `_schedule_save_all_coords`, `_don_point_coords`, `_move_to_recv_point`, `_get_sell_coords`, and only directly-called map/coordinate helpers needed by those paths.
6. Determine exact saved-coordinate representation, map ID/name conversion, shared Dồn coordinate semantics, receiver-coordinate relation, per-account Farm/Sell selectors, apply-all/delete/persistence behavior, and coordinate validation/fallback boundaries.
7. Keep receiver selection/locking/transaction policy deferred unless coordinate resolution directly requires it.
8. Cross-check screenshots/runtime only after static extraction.
9. Persist L05 artifacts, update STATE.md/PROJECT_STATUS.md, re-check code/build state, and advance only after L05 verification.


## L05 VERIFIED RESULTS
- GitHub-first continuity passed: no pre-existing L05 completion; L01-L04 remain unchanged.
- Exact original archive and inner EXE were revalidated before screenshot cross-check. Archive SHA-256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd, 93,715,901 bytes, 1,050 entries, CRC clean. Inner EXE SHA-256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22, 47,450,112 bytes.
- Saved-coordinate rows are dynamic name/map/X/Y records with Train apply + delete. Preset display name is the live identity; rename propagates to account selectors.
- _name_to_coords resolves built-in sell, built-in Dồn/receive, or saved manual presets to (map_id,x,y), otherwise None.
- Exact Dồn targets: Lạc Dương map3 (247,93); Đại Lý map2 (258,124); Tô Châu map4 (416,239); Lâu Lan map5 (249,275).
- Exact sell targets: Đại Lý map2 (103,188); Lạc Dương map3 (231,219); Tô Châu map4 (191,257); Lâu Lan map5 (37,126).
- Current UI uses one shared _recv_coord_var / Tọa độ dồn across receiver rows. Receiver rows contain account selection + delete; deleting a row does not delete the shared coordinate.
- Current account coordinate selector is role-switched: receiver role gets sell built-ins + manual presets; donor role gets manual train presets.
- Saved-row Train action applies the preset name to all train selectors.
- [DonVang] coordinate rows persist as coord_<n>=preset_name|map_id|x|y. Unknown maps on save and stale maps on load are skipped rather than guessed.
- Per-account coordinate selector persists as acc_<character>_farm. Receiver config surface also contains recv_count, recv_<n>_acc, recv_<n>_coord, receiver and recv_coord; conflicting legacy/per-row precedence is deferred to L06.
- No dedicated numeric X/Y clamp/validator was recovered; no range was invented.
- Screenshot cross-check after static extraction matches one shared Tọa độ dồn and saved row Train action. Frozen runtime log has 0 correlated Dồn-coordinate markers, so live parity remains deferred.
- L05 artifacts committed at 2d2e776d8592790596b307ac8208cdd9224e0ef0:
  - docs/don/L05_COORDINATES_FLOW.md
  - docs/don/L05_COORDINATES_MODEL.json
  - docs/don/L05_COORDINATES_STATIC_EVIDENCE.tsv
  - docs/tasks/L05.md

## POST-L05 CODE/BUILD RECHECK
- Recursive main tree after L05 artifact commit: 641 entries, not truncated.
- Python executable-code files remain exactly 7 forensic scripts under tools/.
- No reconstructed application source directory, build-system file, or GitHub Actions workflow exists.
- L05 artifact commit has 0 combined CI statuses and 0 workflow runs.
- Product build remains NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED.

## BLOCKERS
- Receiver-coordinate migration precedence is deferred to L06.
- Exact fresh-row map/X/Y defaults independent of captured config remain unresolved where binding is insufficient.
- Live coordinate movement/parity requires Windows + live game runtime.

## DO_NOT_TOUCH
- Preserve L01-L05 contracts.
- Preserve one shared Dồn coordinate; do not create per-receiver Dồn coordinates.
- Preserve exact built-in coordinate tables and role-switched selector.
- Preserve stale/unknown map skip behavior; do not fuzzy-remap or invent numeric clamps.
- Receiver account selection/readiness behavior belongs to L06.
- Do not create Stage-S application/build placeholders before PLAN reaches reconstruction.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md.
2. Read STATE.md.
3. Check GitHub first for existing L06 artifacts; do not redo verified work.
4. Execute L06 — Dồn receiver accounts / readiness / selection audit only.
5. Re-inspect the frozen original EXE first, focusing on _sync_recv_aliases, _add_receiver_row, _renumber_receiver_rows, _remove_receiver_row, _refresh_receiver_combo, _reset_receiver_rows, _is_receiver_hwnd, _selected_receiver_hwnd, _all_receiver_hwnds, _find_recv_row_for_hwnd, _receiver_speed, _any_ready_receiver, _pick_ready_receiver, _fallback_receiver, _apply_receiver_style, _on_receiver_selected, _start_trade_watch and _ensure_trade_watch, plus directly-called receiver-state helpers.
6. Determine receiver-row lifecycle, duplicate-account handling, receiver identity mapping, ready/busy/offline state ownership, ranking/fallback behavior, watcher scope, serialization behavior, and config migration precedence when directly bound.
7. Keep deeper donor transaction/train-state behavior deferred unless directly required.
8. Cross-check screenshots/runtime only after static extraction.
9. Persist L06 artifacts, update STATE.md/PROJECT_STATUS.md, re-check code/build state, and advance only after L06 verification.


## L06 VERIFIED RESULTS
- PLAN.md and STATE.md were read first and GitHub was checked before analysis. No pre-existing L06 artifact/completion existed; L01-L05 remain unchanged.
- Exact uploaded archive was materialized and revalidated before screenshot/runtime use: SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, size **93,715,901** bytes, **1,050** ZIP entries, CRC clean. Inner `TLMTool.dist/TLMTool.exe` remains SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, size **47,450,112** bytes.
- Receiver rows are dynamic account-selection + delete rows. Deleting a row renumbers labels and always preserves at least one row. The one shared L05 Dồn coordinate is outside `_recv_rows` and survives row deletion.
- `_sync_recv_aliases` keeps old singular receiver APIs compatible with the first receiver row while all rows continue to reference the single shared Dồn coordinate.
- `_refresh_receiver_combo` rebuilds every receiver combobox from current managed account rows and preserves an existing choice while the account still exists.
- Strong static mapping of `hwnd_map / dup / " (" / hwnd / _receiver_hwnd_map` fixes duplicate character-name disambiguation as a parenthesized HWND display suffix mapped back to real HWND.
- No cross-row candidate exclusion was recovered: every receiver combo receives the same account list. `_all_receiver_hwnds` returns a **set**, so repeated selection of the same receiver account collapses for downstream membership.
- `_is_receiver_hwnd` checks any selected receiver row; `_selected_receiver_hwnd` is the legacy first-selected-row helper; `_find_recv_row_for_hwnd` resolves the receiver configuration row for a HWND.
- Receiver-selection UI updates style and moves receiver account rows to the top; receiver names/levels are highlighted semantically yellow while nonreceiver names return to black. The button set remains shared.
- Authoritative receiver readiness lives in `don_logic`, not GUI text. `_recv_registry` is protected by `_recv_reg_lock` and stores per receiver: `ready Event`, `donated Event`, `aborted Event`, and `donor_hwnd`.
- Receiver registration/unregistration is idempotent/per-loop. `ready_receiver_hwnds()` is the authoritative set of receiver HWNDs whose ready Event is set.
- `recv_cycle` is frozen as: sell -> move back to receive point -> set ready -> wait donated/abort/donor-death -> repeat; unregister on cycle exit. A failed move back does not mark ready.
- Receiver GUI phases are exact:
  - **Sẵn sàng nhận** → `#2e7d32`;
  - **Chuẩn bị nhận** → `#1565c0`;
  - **Đang nhận** → `#1565c0`.
- `prep_cb` represents the claimed receiver preparing while donor moves to the Dồn point. `_on_recv_phase(...,"start")` sets **Đang nhận**; `"done"` restores **Sẵn sàng nhận** only if the row is still in **Đang nhận**.
- `_receiver_speed` uses receiver tracker speed = donated gold / elapsed hours.
- `_pick_ready_receiver` only considers ready receivers, excludes the donor itself, requires valid coordinate resolution, selects the **lowest gold/hour** candidate, and uses `random.choice` for equal minimum-speed ties.
- `_fallback_receiver` is first receiver with valid coordinates and is used beside `_pick_ready_receiver` in the manual/move-only path; it is **not** a replacement for automatic-ready selection.
- Automatic `don_move_and_execute` waits for ready receiver availability. Frozen static log text explicitly contains `ready=[] trong 5s`; if no receiver becomes ready it skips that Dồn cycle and farming continues.
- After selecting a candidate, automatic Dồn acquires that receiver's own lock and rechecks readiness. A receiver that became non-ready is rejected after lock. Busy receivers are skipped; if all are busy the cycle is skipped and farm continues.
- `_don_lock_for(receiver_hwnd)` is a dedicated per-receiver lock. This allows donor A→receiver1 and donor B→receiver2 concurrently, while the same receiver can serve only one donor at a time. Manual `don_single` and automatic `don_move_and_execute` share this lock policy.
- New attempts clear stale receiver abort state only after the receiver lock is held. Donor stop/disconnect/abort marks only that receiver aborted; a dead claimed donor window causes immediate stale-trade cleanup and receiver-cycle reset instead of indefinite waiting. Other receivers remain isolated.
- Each receiver is ensured to have **one** background trade-invite watcher. The watcher lives until that game window closes and remains active outside Dồn cycles.
- Watcher whitelist is all account names managed by the tool. `normalize_name` normalizes case/diacritics/server suffix representation for comparison. Managed inviter → accept; unknown inviter → cancel and continue; unreadable/non-invite → ignore.
- The watcher explicitly yields while a real donor claim is active on that receiver so it does not race `_don_flow` for the same invitation MessageBox.
- Persistence surface remains `recv_count`, `recv_<n>_acc`, `recv_<n>_coord`, legacy `receiver`, and legacy `recv_coord`. Current runtime coordinate remains one shared variable. Exact winner for a deliberately conflicting legacy/per-row coordinate config remains **EXPLICIT_UNKNOWN**.
- Screenshot cross-check was performed only after static extraction. Dồn screenshot SHA-256 remains `dffb4da895d21dea87dd72a6601c29104f519dca89c2f716f5a7445bcbe4421a`; it visibly shows one shared Dồn coordinate plus Acc nhận 1/2 and per-row delete buttons.
- Frozen packaged `automove_log.txt` remains SHA-256 `17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`, **387,238 lines**. Correlated `[RECV]`, `[RECV-DBG]`, `[DON]`, ready/prep/receiving, watcher, claim and busy markers are all **0**; live timing/race parity is not fabricated.
- L06 artifacts committed together at **fed8264afe81dd4ae931d9e2548a4ff81d7d7d54**:
  - `docs/don/L06_RECEIVERS_FLOW.md`
  - `docs/don/L06_RECEIVERS_MODEL.json`
  - `docs/don/L06_RECEIVERS_STATIC_EVIDENCE.tsv`
  - `docs/tasks/L06.md`
- All four L06 artifacts were fetched back successfully.

## POST-L06 CODE/BUILD RECHECK
- Recursive main tree after L06 artifact commit contains **645 entries**, not truncated.
- Python executable-code files remain exactly the same **7 forensic scripts** under `tools/`.
- No reconstructed application source directory exists.
- No build-system file and no GitHub Actions workflow exists.
- L06 artifact commit has **0 combined CI statuses** and **0 workflow runs**.
- L06 changed documentation/evidence only and introduced no executable-code/build regression.
- Product build remains **NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED**, not PASS/FAIL.

## BLOCKERS
- Exact load precedence when legacy `recv_coord` conflicts with differing per-row `recv_<n>_coord` values remains source-insufficient and requires stronger source recovery or a controlled config fixture.
- Exact pre-`random.choice` stable ordering of equal-speed candidates is not material to policy and remains unproven.
- Live ready/claim/lock/watcher race timing requires Windows + live Thần Long runtime.
- Reconstructed product build remains not applicable before Stage S.

## DO_NOT_TOUCH
- Preserve L01-L06 contracts unless exact new evidence exposes a contradiction.
- Preserve one shared Dồn coordinate architecture.
- Preserve per-receiver registry and per-receiver lock; do not replace it with one global Dồn lock.
- Preserve lowest-gold/hour ready-receiver selection and random equal-speed tie break.
- Preserve post-lock readiness recheck and skip/farm-continuation behavior when no ready/all busy.
- Preserve one background trade watcher per receiver and its yield-to-real-Dồn rule.
- Do not turn manual `_fallback_receiver` into an automatic no-ready fallback.
- Keep broader Train/Dồn lifecycle integration for L07.
- Do not create Stage-S application/build placeholders before PLAN reaches reconstruction.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md.
2. Read STATE.md.
3. Check GitHub first for any L07 artifacts/commits; if already complete and verified, do not redo them.
4. Execute **L07 — Dồn train-state / receiver-donor lifecycle integration audit** only.
5. Re-inspect the exact frozen original EXE first, focusing on `_toggle_single_farm`, receiver and donor subpaths, `_farm_acc`, `_farm_cycle`, `_run_farm_exit`, `_on_recv_phase`, `_set_state`, `_state_of`, `_start_extra_track`, receiver/donor stop paths, generation guards, and the directly-called `don_logic.recv_cycle / don_move_and_execute` integration boundary.
6. Determine exact receiver-vs-donor start/stop classification, state transitions, when receiver sell/return loop starts, when donor train cycle substitutes Dồn, generation/stop ownership, what happens if role selection changes while running, and how both roles converge back to stopped/train states.
7. Preserve L02-L06 return, inventory, coordinate and receiver-locking contracts; do not reopen their internals without contradiction.
8. Cross-check screenshots/runtime only after static extraction.
9. Persist L07 artifacts, update STATE.md/PROJECT_STATUS.md, re-check code/build state, and advance only after L07 verification.


## L07 VERIFIED RESULTS
- PLAN.md and STATE.md were read first and GitHub was checked before analysis. No pre-existing L07 artifact/completion existed; L01-L06 remain unchanged.
- Exact original specimen was revalidated before UI/runtime cross-check: archive SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, size **93,715,901** bytes, **1,050** entries, CRC clean; inner EXE SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, size **47,450,112** bytes.
- Dồn full-session state ownership is shared by both roles: global `_farming`, per-account `_farming_acc`, worker collection `_farm_threads`, per-row stop-drain sentinel `_stopping_play`, and row generation `_gen`.
- Full-session role is selected at start. Receiver role starts `_run_receiver -> don_logic.recv_cycle`; normal/donor role starts `_farm_cycle(..., don_callback=_don_cb)` and uses `don_logic.don_move_and_execute`.
- `_farm_acc` is not the Dồn Farm FSM. It is only the memory/internal StartAutoFight Train primitive (`start_auto_train`), with no game-UI click.
- Receiver start also initializes receiver donated-gold/time tracking via `_start_extra_track`; row3 is receiver-only. Receiver worker owns generation snapshot plus death/respawn/disconnect session guards and then enters `recv_cycle`.
- Receiver engine remains exact: sell -> move back to receive point -> ready -> wait donated/abort/dead donor -> repeat.
- Dồn state table and colors are frozen exactly:
  - Đã dừng #555555;
  - Sẵn sàng nhận #2e7d32;
  - Chuẩn bị nhận #1565c0;
  - Đang nhận #1565c0;
  - Chờ giao #2e7d32;
  - Chờ dồn #2e7d32;
  - Về dồn #1565c0;
  - Đang dồn #1565c0;
  - Về địa phủ #c62828;
  - Bán đồ #555555;
  - Tới nơi nhận #555555;
  - Trị liệu #555555;
  - Đi train #555555;
  - Đang train #555555;
  - Đang lọc đồ #8e24aa;
  - Gỡ kẹt #ef6c00;
  - unknown/default #555555.
- `_on_recv_phase(receiver,"start")` maps transaction start to **Đang nhận**. `"done"` restores **Sẵn sàng nhận** only if the row is still **Đang nhận**. recv_cycle fixes sell -> move -> ready semantic order; the exact assignment instruction for every first-cycle intermediate GUI label remains explicit UNKNOWN.
- Donor `_farm_cycle` preserves the normal Train lifecycle and substitutes only its return-town/sell leg with `don_callback`. After Dồn, ordinary move-to-train/fight behavior remains.
- The per-row donor path exposes **Về dồn** and **Đang dồn** and explicitly sends a failed donor back toward farm/Train with **Đi train**.
- The global large-button donor callback has an additional static pre-stage/wait surface: `_don_point_coords -> don_mark_waiting -> Chờ dồn -> _any_ready_receiver -> don_move_and_execute`. This static distinction from the single-account callback is preserved for parity instead of being normalized away.
- Stop remains cooperative. `_stop_acc` stops the character and clears the per-account Farm flag. `_check_stop`, `_is_acc_farming`, stop events, generation, window/PID ownership and relevant halt/hard_stop guards terminate subflows.
- `_stopping_play` prevents normal restart/projection while an old worker is draining. `_wait_farm_stop` uses `join`: if other accounts remain they continue; if none remain the large control resets after drain.
- `row._gen` is the stale-worker barrier. Existing worker docs bind generation change to user stop/start. `_restore_play_button` only restores the old worker's button when generation still matches, preventing stale exit from overwriting a newer run.
- Exact `_gen` increment/assignment statement and mutation order versus `_farming_acc`/thread collection remain source-insufficient and are not invented.
- Receiver role changes while an account is already running are **not hot worker migration**. `_on_receiver_selected` only restyles/reorders and retains the same button set.
- Removing receiver role while its `recv_cycle` remains alive does not turn it into a donor; the existing receiver callback has an explicit `[Nhận đồ] ... không nằm trong danh sách acc nhận` failure path.
- Selecting an already-running donor as receiver does not create `recv_cycle` or a ready registry entry for that current generation. The newly selected role becomes a full worker role on a later stop/start.
- State writes are worker-safe: canonical row state is `_state`; UI update is marshaled through `_schedule_state_label -> after(0) -> _apply_state_label`.
- Screenshot cross-check after static extraction preserved hash `dffb4da895d21dea87dd72a6601c29104f519dca89c2f716f5a7445bcbe4421a`.
- Frozen runtime log remains SHA-256 `17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`, **387,238 lines**. Correlated receiver/donor lifecycle markers are all **0**, so live worker/state timing is not fabricated.
- L07 artifacts committed together at **8209aa78559f8f44cdc9da2921d9e98e8d6305c2**:
  - `docs/don/L07_LIFECYCLE_FLOW.md`
  - `docs/don/L07_LIFECYCLE_MODEL.json`
  - `docs/don/L07_LIFECYCLE_STATIC_EVIDENCE.tsv`
  - `docs/tasks/L07.md`
- All four L07 artifacts were fetched back successfully.

## POST-L07 CODE/BUILD RECHECK
- Recursive main tree after L07 artifact commit contains **649 entries**, not truncated.
- Python executable-code files remain exactly the same **7 forensic scripts** under `tools/`.
- No reconstructed application source directory exists.
- No build-system file and no GitHub Actions workflow exists.
- L07 artifact commit has **0 combined CI statuses** and **0 workflow runs**.
- L07 changed documentation/evidence only and introduced no executable-code/build regression.
- Product build remains **NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED**, not PASS/FAIL.

## BLOCKERS
- Exact `_gen` assignment/increment statement ordering remains static-unknown.
- Exact first-cycle assignment statement for every receiver intermediate state label remains static-unknown where only engine order/state vocabulary are recovered.
- Exact Farm worker join timeout/drain timing remains unbound.
- Live role-change/thread race parity requires Windows + live Thần Long runtime.
- Reconstructed product build remains not applicable before Stage S.

## DO_NOT_TOUCH
- Preserve L01-L07 contracts unless exact new evidence contradicts them.
- Do not replace the start-time receiver/donor worker split with dynamic hot-role migration.
- Do not reconstruct the full Dồn Farm button as a direct `_farm_acc` call.
- Preserve cooperative stop/drain and generation stale-worker guard.
- Preserve the single-account versus global donor callback distinction until runtime parity proves equivalence.
- Keep death/heal/disconnect/reconnect internals for L08.
- Do not create Stage-S application/build placeholders before PLAN reaches reconstruction.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md.
2. Read STATE.md.
3. Check GitHub first for any L08 artifacts/commits; if already complete and verified, do not redo them.
4. Execute **L08 — Dồn heal / death / disconnect / reconnect audit** only.
5. Re-inspect the exact frozen original EXE first, focusing on `_diaphu_monitor`, `_heal_at_death`, `_disconnect_monitor`, `_wait_for_disconnect_or_stop`-style helpers if present, receiver/donor halt/hard_stop integration, the visible respawn/heal/auto-reconnect controls and their config keys, and only directly-called memory/pixel helpers needed by those paths.
6. Determine exact death triggers (MapID/HP), respawn action, heal routing/click sequence, receiver-vs-donor differences, disconnect detection cadence/thresholds, meaning of the visible auto-reconnect control versus current monitor behavior, and which conditions end the full session versus resume it.
7. Preserve L02-L07 movement/inventory/receiver/lifecycle contracts; do not reopen them without contradiction.
8. Cross-check screenshots/runtime only after static extraction.
9. Persist L08 artifacts, update STATE.md/PROJECT_STATUS.md, re-check code/build state, and advance only after L08 verification.


## L08 VERIFIED RESULTS
- PLAN.md and STATE.md were read first and GitHub was checked before analysis. No pre-existing L08 artifact/completion existed; L01-L07 remain unchanged.
- Exact original specimen was revalidated before screenshot/runtime use: archive SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, size **93,715,901** bytes, **1,050** entries, CRC clean; inner EXE SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, size **47,450,112** bytes.
- Current Dồn controls/config mapping is frozen:
  - `respawn_var` / `respawn` → **Quay lại train khi chết**;
  - legacy `auto_reconnect_var` / `auto_reconnect` → current visible **Dừng khi mất kết nối mạng**;
  - `trist_var` / `trist` → **Trị liệu sau khi chết**;
  - `heal_map_var` / `heal_map` → treatment destination.
- Both receiver and donor full sessions start the same Dồn `_diaphu_monitor` and `_disconnect_monitor` surfaces.
- Dồn death monitor cadence is **4s**. `MapID == 87` raises `respawn_event` once per continuous map-87 episode using `detected`; leaving map 87 rearms it.
- A real numeric `HpPercent == 0` causes exactly one client click at **(792,441)** per zero-HP episode; `hp_latched` blocks repeat clicks until HP becomes nonzero. Unreadable HP is not treated as zero.
- Map87 recovery event and HP0 click are separate semantics: map87 signals recovery intent; HP0 performs the one-shot respawn click.
- Receiver recovery explicitly logs **acc nhận đang ở Địa phủ → hồi sinh**, may invoke `_heal_at_death`, and then returns to its receiver lifecycle unless stop/halt/failure ends it. No Train-target move surface exists in the receiver runner.
- Donor Farm consumes the same `respawn_event` and exposes **đang ở Địa phủ → hồi sinh**. The `respawn` checkbox is post-death return/relocation policy, not the HP0 click gate. Exact unchecked donor continuation remains explicit UNKNOWN.
- Dồn treatment uses the shared `TRAIN_HEAL_COORDS` contract:
  - Đại Lý map2 **(43,178)**;
  - Lạc Dương map3 **(255,126)**;
  - Tô Châu map4 **(155,252)**;
  - Lâu Lan map5 **(294,170)**.
- `_heal_at_death` supports built-in or saved manual coordinates, moves with shared `move_character`, then uses the frozen two-point treatment interaction **(892,474)** and **(514,424)** repeated **4** times. Exact 0.2 pacing binding/readiness placement remains unbound.
- Treatment failure surface **trị liệu sau chết thất bại** is recovered, but the exact next lifecycle branch remains explicit UNKNOWN.
- Critical Dồn-specific correction: **Dồn does not automatically reconnect**. The old internal/config name `auto_reconnect` is compatibility only; current visible semantics are stop-on-disconnect.
- Dồn disconnect watchdog cadence is **2s**. `TCPGame.Instance.tcpClient.Connected == True` vetoes/reset false positives. Otherwise both pixel probes must match for **3 consecutive ticks (~6s)**:
  - `login.ngatKetNoi1` → **(640,244)**, RGB **(160,145,52)**, tolerance **5**;
  - `login.ngatKetNoi2` → **(702,453)**, RGB **(212,28,34)**, tolerance **5**.
- On 3/3 confirmation Dồn logs **MAT KET NOI**, asserts `halt`, uses `stop_character`, and hard-stop-aware movement/treatment/Dồn subflows exit. Receiver path says **mất kết nối → dừng acc nhận**; donor path says **mất kết nối → dừng acc**.
- Negative static evidence is decisive: Dồn disconnect monitor has **no** `reconnect_ok`, no reconnect click **(616,455)**, no `wait_pixel(common.active)` retry path, no five-attempt batch and no infinite reconnect retry loop.
- The EXE's exact embedded text states: **KHÔNG tự kết nối lại — user bấm Start để chạy lại.**
- Disconnect monitor exits when user/session/gen ends, real window/process dies, or **Dừng khi mất kết nối mạng** is turned off. No hot re-arm after re-enabling is assumed without stronger evidence.
- `is_trade_active` is consulted by the disconnect monitor, but its exact conditional branch semantics are not source-visible enough and remain explicit UNKNOWN.
- Confirmed disconnect halt can interrupt death-treatment/movement once halt becomes visible. Exact same-scheduling-window death/disconnect arbitration before halt remains runtime-required.
- Screenshot cross-check was performed only after static extraction. Capture SHA-256 remains `dffb4da895d21dea87dd72a6601c29104f519dca89c2f716f5a7445bcbe4421a`; it shows respawn unchecked, stop-on-disconnect unchecked, treatment unchecked, unstuck checked and **Trị liệu Tô Châu** selected.
- Frozen `automove_log.txt` remains SHA-256 `17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`, **387,238 lines**. Correlated HP/death/treatment/disconnect Dồn markers are all **0**, so live timing is not fabricated.
- L08 artifacts committed at **13efed0fadc49c909a50f5f18b572cfb922e0373**:
  - `docs/don/L08_RECOVERY_DISCONNECT_FLOW.md`
  - `docs/don/L08_RECOVERY_DISCONNECT_MODEL.json`
  - `docs/don/L08_RECOVERY_DISCONNECT_STATIC_EVIDENCE.tsv`
  - `docs/tasks/L08.md`
- All four L08 artifacts were fetched back successfully.

## POST-L08 CODE/BUILD RECHECK
- Recursive main tree after L08 artifact commit contains **653 entries**, not truncated.
- Python executable-code files remain exactly the same **7 forensic scripts** under `tools/`.
- No reconstructed application source directory exists.
- No build-system file and no GitHub Actions workflow exists.
- L08 artifact commit has **0 combined CI statuses** and **0 workflow runs**.
- L08 changed documentation/evidence only and introduced no executable-code/build regression.
- Product build remains **NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED**, not PASS/FAIL.

## BLOCKERS
- Exact donor continuation when **Quay lại train khi chết** is unchecked remains source-insufficient.
- Exact treatment-failure next lifecycle branch remains source-insufficient.
- Exact first 4s monitor tick timing and `is_trade_active` branch semantics remain unresolved.
- Same-tick death/disconnect arbitration and live stop timing require Windows + live Thần Long runtime.
- Reconstructed product build remains not applicable before Stage S.

## DO_NOT_TOUCH
- Preserve L01-L08 contracts unless exact new evidence contradicts them.
- Do not import ordinary Train's reconnect loop into Dồn.
- Preserve the legacy config key `auto_reconnect` while implementing current **Dừng khi mất kết nối mạng** semantics.
- Do not gate the HP0 respawn click on `Quay lại train khi chết`; that option is post-death relocation policy.
- Preserve receiver recovery as receiver lifecycle, not Train-role conversion.
- Keep all-account action behavior for L09.
- Do not create Stage-S application/build placeholders before PLAN reaches reconstruction.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md.
2. Read STATE.md.
3. Check GitHub first for any L09 artifacts/commits; if already complete and verified, do not redo them.
4. Execute **L09 — Dồn all-account actions audit** only.
5. Re-inspect the exact frozen original EXE first, focusing on `_move_all`, `_move_all_recv`, `_farm_all`, `_sell_all`, `_stop_all`, the bottom all-account buttons, StartTab Dồn quick controls, per-role filtering, concurrency/thread ownership, and only directly-called movement/Dồn/sell helpers required by those actions.
6. Determine exact target universe for each all-account action, whether receiver accounts are included/excluded per action, parallel vs sequential behavior, how current shared receiver coordinate/role mapping affects action dispatch, stop/cancel semantics, and StartTab parity.
7. Preserve L02-L08 movement/receiver/lifecycle/recovery contracts; do not reopen them without contradiction.
8. Cross-check screenshots/runtime only after static extraction.
9. Persist L09 artifacts, update STATE.md/PROJECT_STATUS.md, re-check code/build state, and advance only after L09 verification.


## L09 VERIFIED RESULTS
- PLAN.md and STATE.md were read first and GitHub was checked before analysis. No pre-existing L09 artifact/completion existed; L01-L08 remain unchanged.
- Exact original specimen was revalidated before screenshot/runtime use: archive SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, size **93,715,901** bytes, **1,050** entries, CRC clean; inner EXE SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, size **47,450,112** bytes.
- Current Dồn all-account toolbar is exactly **Điều khiển tất cả:** with three visible quick movement buttons:
  - **Tới nơi nhận** -> `_move_all_recv`;
  - **Tới chỗ bán** -> `_move_sell_acc`;
  - **Tới nơi train** -> `_move_all`.
- The exact current UI constant block shows these quick commands dispatched through `threading.Thread` / `target` / `daemon` / `start`, keeping them off the Tk main thread.
- The separate bottom **Bắt đầu** button is wired to `_toggle_farm`; it is not one of the quick movement commands.
- `_checked_rows` exact documentation says current bulk helper scope is **all account rows in the list except receiver accounts**. The old “được tick” wording is legacy naming and must not be reconstructed as a missing current checkbox requirement.
- `_move_all` exact documentation says configured-account movement is **parallel**. Combined with current `_checked_rows`, **Tới nơi train** targets all nonreceiver/donor rows and moves each toward its configured Train preset.
- `_move_sell_acc` exact documentation says it moves **all receiver accounts** to each receiver's selected sell destination. It is move-only and is not the actual inventory-selling helper `_sell_all`.
- `_move_all_recv` exact documentation is role-aware:
  - donor accounts move to the receiver selected by the current manual receiver-selection policy;
  - receiver accounts move to the receive coordinate attached to their receiver row.
- L06 manual selection remains authoritative for **Tới nơi nhận**: prefer a ready receiver with the lowest current gold/hour and random equal-speed tie; if ready selection is unavailable, the manual/move-only path may use `_fallback_receiver` = first receiver with valid coordinates. This fallback must not be imported into automatic Dồn no-ready behavior.
- L05 remains authoritative for receiver coordinates: every receiver row's compatibility `recv_coord_var` currently aliases the one shared `_recv_coord_var`, so old “tọa độ riêng của dòng” wording resolves to the same shared current Dồn point.
- Real class helpers `_stop_all`, `_farm_all`, `_sell_all` remain present with exact docs:
  - **Dừng các acc được tick — song song.**
  - **Farm các acc được tick — song song.**
  - **Bán đồ các acc được tick — song song.**
- Their effective current ordinary universe is the same `_checked_rows` nonreceiver set.
- `_farm_all` wraps `_farm_acc`; L07 already proves `_farm_acc` is only the internal StartAutoFight Train primitive, so `_farm_all` is **not** equivalent to the current full **Bắt đầu/_toggle_farm** lifecycle.
- `_sell_all` is the actual selling-flow helper and is **not** the visible **Tới chỗ bán** movement action.
- No current visible Dồn toolbar or StartTab binding was recovered for `_stop_all/_farm_all/_sell_all`. They must be preserved as real methods without inventing new visible buttons.
- StartTab Dồn parity is frozen:
  - **Dồn vàng** -> `_toggle_donvang_cmd` -> Dồn `_toggle_farm`, with StartTab + DonVangTab text/state synchronization;
  - **Tới nơi nhận** -> `_donvang_action("_move_all_recv")`;
  - **Tới chỗ bán** -> `_donvang_action("_move_sell_acc")`;
  - **Tới nơi train** -> `_donvang_action("_move_all")`;
  - **Cấu hình** -> `_goto_donvang_tab`.
- `_donvang_action` is a generic `method_name` worker-thread wrapper, so StartTab reuses the same Dồn backends rather than implementing a second behavior.
- No dedicated quick-action cancel token/queue was recovered. The three standalone movement commands are not the same worker ownership as `_toggle_farm`; exact cross-command overlap/cancellation if Farm is started/stopped while a quick move is already running remains runtime-required.
- Screenshot cross-check was performed only after static extraction. Capture SHA-256 remains `dffb4da895d21dea87dd72a6601c29104f519dca89c2f716f5a7445bcbe4421a`; it visibly shows the three quick buttons plus **Bắt đầu** and no visible Dừng/Farm/Bán-all helper buttons.
- Frozen `automove_log.txt` remains SHA-256 `17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`, **387,238 lines**. Correlated current Dồn bulk-action markers are all **0**, so live action ordering/timing is not fabricated.
- L09 artifacts committed at **db1bcf3f81b71f644b17aeb28740aae7401b4b1f**:
  - `docs/don/L09_ALL_ACCOUNT_ACTIONS_FLOW.md`
  - `docs/don/L09_ALL_ACCOUNT_ACTIONS_MODEL.json`
  - `docs/don/L09_ALL_ACCOUNT_ACTIONS_STATIC_EVIDENCE.tsv`
  - `docs/tasks/L09.md`
- All four L09 artifacts were fetched back successfully.

## POST-L09 CODE/BUILD RECHECK
- Recursive main tree after L09 artifact commit contains **657 entries**, not truncated.
- Python executable-code files remain exactly the same **7 forensic scripts** under `tools/`.
- No reconstructed application source directory exists.
- No build-system file and no GitHub Actions workflow exists.
- L09 artifact commit has **0 combined CI statuses** and **0 workflow runs**.
- L09 changed documentation/evidence only and introduced no executable-code/build regression.
- Product build remains **NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED**, not PASS/FAIL.

## BLOCKERS
- Exact internal ordering/join policy inside `_move_all_recv` remains source-insufficient.
- Exact `_move_sell_acc` per-receiver worker join policy remains source-insufficient.
- Standalone quick-action overlap/cancellation against concurrent Farm start/stop remains runtime-required.
- Hidden/plugin reachability of currently unwired `_stop_all/_farm_all/_sell_all` is not recovered from the current visible UI surface.
- Live StartTab/Dồn-tab synchronization timing requires Windows + live Thần Long runtime.

## DO_NOT_TOUCH
- Preserve L01-L09 contracts unless exact new evidence contradicts them.
- Do not add visible Dừng/Farm/Bán-all buttons just because the helper methods exist.
- Do not use `_farm_all` in place of the full `_toggle_farm` lifecycle.
- Do not use `_sell_all` for **Tới chỗ bán**; that button is movement-only via `_move_sell_acc`.
- Preserve manual **Tới nơi nhận** fallback separately from automatic no-ready Dồn behavior.
- Preserve the one shared Dồn receive coordinate.
- Keep parity/reconstruction consolidation for L10.
- Do not create Stage-S application/build placeholders before PLAN reaches reconstruction.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md.
2. Read STATE.md.
3. Check GitHub first for any L10 artifacts/commits; if already complete and verified, do not redo them.
4. Execute **L10 — Dồn parity / reconstruction contract audit** only.
5. Consolidate L01-L09 into one exact reconstruction contract without redoing their analyses: visible UI, config schema, state table, receiver architecture, movement, inventory thresholds, recovery/disconnect, quick controls, StartTab parity, and all explicit UNKNOWN/runtime-required edges.
6. Build a Dồn parity matrix that marks each behavior as STATIC_VERIFIED, RUNTIME_REQUIRED, EXPLICIT_UNKNOWN, or NOT_CURRENTLY_WIRED.
7. Identify contradictions across L01-L09 and resolve only when exact evidence is stronger; otherwise preserve the uncertainty.
8. Define the minimum reconstruction acceptance tests for Stage S without writing application source yet.
9. Persist L10 artifacts, update STATE.md/PROJECT_STATUS.md, re-check code/build state, and advance Phase L only after L10 verification.


## L10 VERIFIED RESULTS
- PLAN.md and STATE.md were read first and GitHub was checked before consolidation. No pre-existing L10 artifact/completion existed; L01-L09 remain unchanged.
- L10 intentionally did **not** redo EXE analysis. It consolidates the already frozen L01-L09 evidence into one Stage-S implementation contract.
- One authoritative Dồn reconstruction contract now freezes:
  - visible dedicated-tab and StartTab surfaces;
  - [DonVang] persistence families;
  - cycle/full-bag return behavior;
  - sell-only home-priority semantics;
  - Site10 inventory thresholds/filtering;
  - one shared Dồn coordinate and role-switched account coordinate selector;
  - exact Dồn/sell/treatment coordinate tables;
  - multi-receiver registry/readiness/locking/watcher behavior;
  - start-time receiver/donor worker split and cooperative generation-guarded stop;
  - exact state/color table;
  - Map87/HP0 death monitor and treatment flow;
  - current stop-on-disconnect behavior with **no Dồn auto reconnect**;
  - current three quick all-account movement actions;
  - StartTab delegation parity.
- L10 parity matrix classifies every important boundary into:
  - **STATIC_VERIFIED**
  - **RUNTIME_REQUIRED**
  - **EXPLICIT_UNKNOWN**
  - **NOT_CURRENTLY_WIRED**
- Cross-L01-L09 apparent contradictions were resolved only where direct/current evidence is stronger:
  - legacy `auto_reconnect` key -> current **Dừng khi mất kết nối mạng**, not reconnect;
  - old per-row receiver-coordinate wording -> one current shared `_recv_coord_var`;
  - old separate Bán/Train wording -> one current role-switched account selector;
  - old “được tick” wording -> current `_checked_rows` = all listed nonreceiver accounts;
  - `_farm_all` exists but **Bắt đầu** remains `_toggle_farm`;
  - `_sell_all` exists but **Tới chỗ bán** remains movement-only `_move_sell_acc`;
  - manual `_fallback_receiver` remains manual-only and must not alter automatic no-ready Dồn;
  - sell-home Phù priority remains separate from the no-Phù Dồn/receiver final leg;
  - duplicate receiver UI rows collapse to HWND-set runtime identity;
  - “heal/reconnect” phase wording does not override exact no-auto-reconnect behavior.
- Captured screenshot/config values are explicitly separated from universal defaults where default binding was not proven.
- 103 minimum Stage-S Dồn acceptance checks were defined. Static Dồn parity and live Dồn parity are separate claims/gates.
- Remaining unknowns are preserved rather than guessed, including:
  - stop_bag_check default-3 semantic;
  - conflicting legacy/per-row receiver-coordinate migration winner;
  - exact _gen mutation order;
  - exact receiver intermediate-state assignment sites;
  - exact worker join/drain timing;
  - donor continuation when Quay lại train khi chết is unchecked;
  - treatment-failure next branch;
  - first death-monitor tick timing;
  - exact is_trade_active disconnect branch;
  - same-window death/disconnect ordering;
  - quick-move join/cancel overlap;
  - live StartTab synchronization timing;
  - exact captured permission state.
- L10 artifacts committed at **a9c1a4285bfbf2cff2a14b513fd49b6cf0b4d3fd**:
  - `docs/don/L10_RECONSTRUCTION_CONTRACT.md`
  - `docs/don/L10_PARITY_MATRIX.tsv`
  - `docs/don/L10_ACCEPTANCE_TESTS.md`
  - `docs/don/L10_CONTRADICTIONS.md`
  - `docs/tasks/L10.md`
- All five L10 artifacts were fetched back successfully.

## POST-L10 CODE/BUILD RECHECK
- Recursive main tree after L10 artifact commit contains **662 entries**, not truncated.
- Python executable-code files remain exactly the same **7 forensic scripts** under `tools/`.
- No reconstructed application source directory exists.
- No build-system file and no GitHub Actions workflow exists.
- L10 artifact commit has **0 combined CI statuses** and **0 workflow runs**.
- L10 changed documentation/evidence only and introduced no executable-code/build regression.
- Product build remains **NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED**, not PASS/FAIL.

## PHASE L GATE
**STATIC_RESEARCH_CLOSED / LIVE_RUNTIME_PARITY_DEFERRED**

## BLOCKERS
- Phase L has no remaining static-research blocker.
- The preserved L10 EXPLICIT_UNKNOWN/RUNTIME_REQUIRED items require either a controlled config fixture, stronger source recovery, or future Windows + live Thần Long parity testing.
- Reconstructed product build remains not applicable before Stage S.

## DO_NOT_TOUCH
- Preserve the L10 Dồn reconstruction contract as the normative Stage-S input unless later exact evidence proves a contradiction.
- Do not reopen L01-L09 merely to restate already frozen behavior.
- Do not convert EXPLICIT_UNKNOWN or RUNTIME_REQUIRED rows into guessed original behavior.
- Do not add unwired Dồn UI controls.
- Do not import ordinary Train reconnect logic into Dồn.
- Do not create Stage-S source/build placeholders while the research plan is still progressing through later feature phases.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md.
2. Read STATE.md.
3. Check GitHub first for any M01 artifacts/commits; if already complete and verified, do not redo them.
4. Begin **Phase M — Rao** with **M01 — Rao authority / UI surface audit** only.
5. Re-inspect the exact frozen original EXE before using screenshots, identify the active Rao module/class, direct methods, main-app construction, StartTab exposure if any, visible controls, current screenshot surface, persistence section, permission/visibility boundary, and direct dependency boundary.
6. Do not deep-audit message storage/channel/interval/account assignment/start-stop in M01 except to inventory their visible/handler boundaries for later M tasks.
7. Persist M01 artifacts, update STATE.md/PROJECT_STATUS.md, re-check code/build state, and advance only after M01 verification.


## M01 VERIFIED RESULTS
- PLAN.md and STATE.md were read first and GitHub was checked before analysis. No pre-existing M01 artifact/completion existed.
- The exact original archive was materialized and revalidated before screenshot use: SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, size **93,715,901** bytes, **1,050** entries, CRC clean. Inner `TLMTool.dist/TLMTool.exe` remains SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, size **47,450,112** bytes.
- Active Rao authority is `rao_tab.py / RaoTab`.
- Exact serialized `.rao_tab` header at `0x2bd7850` decodes to size **11,774 bytes** and constant count **582**. Source filename `rao_tab.py` is at `0x2bd9ea7`; exact `<module rao_tab>` marker is at `0x2bd9f72`.
- **40** direct top-level `RaoTab` methods, including `__init__`, were inventoried and divided into UI, message/storage, channel/interval, account assignment, identity/refresh, permission and worker boundaries.
- TLMMainApp current shell integrates Rao:
  - visible label **Rao**;
  - tab key `rao_tab`;
  - `RaoTab` class reference in current build/rebuild path;
  - `_set_rao_tab_visible`;
  - exact visibility documentation: **Show/hide Rao tab — chỉ hiện khi có quyền (như donvang_tab).**
- Rao is therefore current/wired, not dormant. The supplied screenshot shows the tab visible/active; exact server/license-plan value at capture remains UNKNOWN.
- No current Rao-specific StartTab quick action was recovered. Exact `.start_tab` serialized block is size **37,643 bytes / 1,536 constants** and contains **0** case-insensitive Rao/rao strings. This does not contradict Rao's `start_tab` dependency, because Rao directly reuses shared `get_windows`, `get_character_info`, settings-lock/read/write helpers rather than a StartTab Rao button.
- Dedicated visible Rao surface frozen from EXE before screenshot cross-check:
  - **Cấu hình rao tự động**;
  - columns **Tên / Nội dung rao / Kênh / Lặp (s) / Xóa**;
  - **+ Thêm rao**;
  - **Danh sách tài khoản**;
  - headers **Nhân vật / Nội dung rao**;
  - bottom **Bắt đầu**.
- Current module carries `RAO_CHANNELS` and `RAO_DEFAULT_CHANNEL`. Visible labels are **Thế giới / Bang hội / Môn phái / Tổ đội / Liên minh / Quân đoàn / Lân cận**; static default channel is **Thế giới**. Channel ID/packet mapping is deliberately deferred to M03.
- Rao auto-name boundary is `Rao 1, Rao 2, ...`, with exact docs saying the smallest unused positive number is chosen. Detailed message/storage semantics remain M02.
- Static account-row surface exposes exactly **4 Rao-selection combobox slots**, a per-account **▶** control and stopped state **Đã dừng**. Account assignment semantics remain M05; start/stop semantics remain M06.
- Exact account refresh documentation says **Tự động refresh danh sách acc mỗi 5 giây.** Tab refresh has start/stop/schedule methods and HWND/PID identity cleanup including bind/unbind window-identity symbols.
- Permission boundary is frozen:
  - shell visibility is permission-controlled;
  - newly created rows are disabled without `rao_tab` permission;
  - `_check_perm` contains `has_permission_with_limit` with adjacent `rao_tab / rao` arguments.
- Persistence boundary is frozen to section **[Rao]**, shared `_settings_lock/read_settings/write_settings`, dynamic `rao_` message family and `acc_` account family. Exact schemas remain M02/M05.
- The module's own embedded documentation says Rao sends through **memory_items.send_chat / Network.SendPacket CMD_CLIENT_CHAT** in the background and does not need to open the chat panel. M01 inventories this send boundary only; worker/channel/interval behavior remains deferred.
- Direct/current dependency boundary:
  - module surface: tkinter/ttk/messagebox/font, os, start_tab;
  - shared direct helpers: get_windows, get_character_info, settings lock/read/write;
  - runtime symbols: threading, time, json, memory_items, utils, win32gui, permission_guard;
  - bind/unbind window-identity symbols are direct but their exact owner module is not frozen here;
  - info_tab/notebook/parent are constructor/context surfaces;
  - D03 requests and D04 graph edges remain weak/static-only, not import proof.
- Screenshot cross-check was performed only after static extraction. It matches the exact group/column/button layout and shows captured row **Rao 1 / empty content / Thế giới / 30**, no account rows, bottom **Bắt đầu**. The captured **30** is not promoted to final interval semantics before M04.
- M01 artifacts committed at **6c8f0662cb742aa05c00c98fa6ac6b3a125b9160**:
  - `docs/rao/M01_AUTHORITY_SURFACE.md`
  - `docs/rao/M01_MODEL.json`
  - `docs/rao/M01_HANDLER_INVENTORY.tsv`
  - `docs/rao/M01_DEPENDENCIES.tsv`
  - `docs/rao/M01_STATIC_EVIDENCE.tsv`
  - `docs/tasks/M01.md`
- All six M01 artifacts were fetched back successfully.

## POST-M01 CODE/BUILD RECHECK
- Recursive main tree after M01 artifact commit contains **669 entries**, not truncated.
- Python executable-code files remain exactly the same **7 forensic scripts** under `tools/`.
- No reconstructed application source directory exists.
- No build-system file and no GitHub Actions workflow exists.
- M01 artifact commit has **0 combined CI statuses** and **0 workflow runs**.
- M01 changed documentation/evidence only and introduced no executable-code/build regression.
- Product build remains **NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED**, not PASS/FAIL.

## BLOCKERS
- M01 has no static authority/UI blocker.
- Exact license/plan permission value at the screenshot capture is not recovered.
- Current StartTab negative finding is strong static evidence, but hidden/plugin invocation paths are not claimed absent.
- Message serialization, channel IDs, interval normalization, account assignment and worker semantics remain intentionally deferred by PLAN.

## DO_NOT_TOUCH
- Preserve Phase-L gate and L10 Dồn contract.
- Preserve M01 Rao authority/module/UI/permission/persistence boundaries unless stronger exact evidence contradicts them.
- Do not invent a Rao StartTab button.
- Do not deep-freeze Rao message/channel/interval/account/worker semantics from M01 boundary strings.
- Do not create Stage-S source/build placeholders during Phase M research.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md.
2. Read STATE.md.
3. Check GitHub first for any M02 artifacts/commits; if already complete and verified, do not redo them.
4. Execute **M02 — Rao message storage audit** only.
5. Re-inspect the exact frozen Rao block first, focusing on `_rao_names`, `_next_rao_name`, `_add_rao_row`, `_remove_rao_row`, `_resolve_rao`, `_save_config`, `_load_config`, `_save_on_destroy`, message-row trace callbacks, section `[Rao]`, and `rao_` dynamic key serialization.
6. Determine exact row identity/name behavior, content storage, add/delete/rename behavior, persistence encoding/order, invalid/duplicate/stale handling, and what account selections do when a referenced Rao definition is renamed/deleted — but defer channel ID semantics to M03, interval normalization/timing to M04, and account assignment persistence to M05 except where message-row identity directly affects it.
7. Cross-check the supplied Rao screenshot only after static extraction.
8. Persist M02 artifacts, update STATE.md/PROJECT_STATUS.md, re-check code/build state, and advance only after M02 verification.


## M02 VERIFIED RESULTS
- PLAN.md and STATE.md were read first and GitHub was checked before analysis. No pre-existing M02 artifact/completion existed; M01 and Phase-L contracts remain unchanged.
- M02 re-inspected the exact frozen `rao_tab` serialized block and its post-marker local-variable metadata before screenshot cross-check.
- Live Rao definition row identity is name-based:
  - `name_var`
  - `msg_var`
  - `chan_var`
  - `sec_var`
  - no persistent message-row UUID recovered.
- Exact `_rao_names` documentation: **Danh sách tên rao hiện có (giữ thứ tự dòng).**
- Exact `_next_rao_name` documentation: **Tên tự động Rao 1, Rao 2, ... (số nhỏ nhất chưa dùng).**
- Automatic names therefore choose the smallest unused positive `Rao N`. No current manual duplicate-name validation/warning surface was recovered.
- `_add_rao_row` owns nested `_rao_save`; compiled row surface exposes `trace_add("write", ...)`, the four row variables, `_save_config`, and `_refresh_acc_rao_options`. Rao row edits therefore save live and refresh account Rao-name options.
- `_remove_rao_row` exact documentation: **Xóa một dòng rao (nút ✕ đỏ).** Static surface includes row destroy/pop and the same save/refresh family; no tombstone/hidden persistent ID layer is recovered.
- `_resolve_rao(rao_name)` exact contract is **Tên rao → (nội dung, interval_giây, channel_id, tên_kênh); (None, lý_do) nếu không dùng được.**
- Exact fail-closed resolution reasons recovered:
  - **Chưa chọn nội dung rao**
  - **Rao '<name>' chưa có nội dung**
  - **'<name>' chưa chọn kênh**
  - **'<name>' chưa đặt thời gian lặp**
  - **'<name>' không còn tồn tại**.
- Account Rao combobox options are rebuilt through `_refresh_acc_rao_options`; exact doc: **Đổ lại combobox nội dung rao của mọi acc theo danh sách tên hiện tại.** Recovered locals include `names/prev/row/cb/var/cur`, proving reconciliation of current selection state against the new name universe rather than a static options-only constant.
- No old-name→new-name alias/UUID rename propagation surface was recovered. After a Rao rename/delete, the old name is no longer a valid definition and cannot resolve. Later `load_acc_config` only applies Rao names that still exist.
- Exact immediate account StringVar behavior after rename/delete (clear immediately versus retain stale text until subsequent assignment handling) remains **EXPLICIT_UNKNOWN / deferred M05**; M02 does not invent it.
- Persistence is under **[Rao]**, with separate dynamic families:
  - `rao_` = Rao definitions
  - `acc_` = account selections.
- Current Rao definition storage is strongly mapped as **name-keyed**:
  `rao_<trimmed Rao display name> = JSON payload`.
  Evidence: save locals include `cname` but no row-index local; payload literals are `content/channel/sec`; load uses a dynamic key plus `split` and `name/content/seconds/channel` row reconstruction.
- Current JSON payload fields are:
  - `content`
  - `channel`
  - `sec`.
- `json.dumps(..., ensure_ascii=False)` is exact static evidence, preserving Vietnamese/unicode content in config.
- The name is carried by the `rao_<name>` option-key suffix rather than a separate persistent UUID. M02 recovered no separate row-order field.
- Message-definition save rewrites the `rao_` family while preserving the distinct `acc_` family in the same section; deletion/rename therefore removes/replaces the prior message key without wiping account settings.
- `_load_config` exact surface includes `sorted`, a load lambda, `json.loads`, dynamic keys, `split`, default text `30`, `TypeError/ValueError`, and call keywords `name/content/seconds/channel`.
- High-level load contract is frozen:
  1. collect/sort `rao_` keys;
  2. derive display name from key suffix;
  3. JSON-decode;
  4. recover content/channel/sec with validation/defaults;
  5. recreate through `_add_rao_row(name=..., content=..., seconds=..., channel=...)`.
- Exact sort comparator and malformed-JSON fallback/skip branch remain **EXPLICIT_UNKNOWN**.
- Interval scalar type/default/clamp/timing remains deferred to M04; channel fallback/ID mapping remains M03.
- Because storage is name-keyed, two live rows with the same trimmed name cannot persist as two independent definition records. Auto-generated names avoid this collision, but exact manual-duplicate save winner and live duplicate-resolution winner remain **EXPLICIT_UNKNOWN**.
- Blank Rao name is not a normal addressable account-selection identity. Exact save behavior for a manually blank row remains **EXPLICIT_UNKNOWN**.
- `_saving_enabled` and `_save_on_destroy`/`<Destroy>` surfaces are recovered. Exact trace-suppression transition order and destroy-event filtering remain implementation-detail UNKNOWN rather than guessed.
- Screenshot cross-check after static extraction remains consistent with one definition row **Rao 1 / empty content / Thế giới / 30**. M02 does not promote interval behavior before M04.
- M02 artifacts committed at **eb0cac2e0726315a26c1fdd1903264ee324bd150**:
  - `docs/rao/M02_MESSAGE_STORAGE_FLOW.md`
  - `docs/rao/M02_MODEL.json`
  - `docs/rao/M02_STATIC_EVIDENCE.tsv`
  - `docs/tasks/M02.md`
- All four M02 artifacts were fetched back successfully.

## POST-M02 CODE/BUILD RECHECK
- Recursive main tree after M02 artifact commit contains **673 entries**, not truncated.
- Python executable-code files remain exactly the same **7 forensic scripts** under `tools/`.
- No reconstructed application source directory exists.
- No build-system file and no GitHub Actions workflow exists.
- M02 artifact commit has **0 combined CI statuses** and **0 workflow runs**.
- M02 changed documentation/evidence only and introduced no executable-code/build regression.
- Product build remains **NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED**, not PASS/FAIL.

## BLOCKERS
- M02 has no message-storage authority blocker.
- Exact immediate stale account StringVar clear/preserve behavior belongs to M05.
- Exact manual duplicate-name winner, blank-name save behavior, sorted-key comparator and malformed-record fallback remain static-insufficient.
- Channel mapping and interval normalization are intentionally deferred by PLAN.

## DO_NOT_TOUCH
- Preserve M01 authority/UI boundary and Phase-L gate.
- Treat the visible trimmed Rao name as message identity unless later exact evidence proves otherwise.
- Preserve name-keyed `rao_<name>` + JSON `content/channel/sec` storage and `ensure_ascii=False`.
- Do not invent a hidden row UUID or rename alias table.
- Do not collapse M03 channel or M04 interval behavior into M02 guesses.
- Do not create Stage-S application/build placeholders during Phase M research.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md.
2. Read STATE.md.
3. Check GitHub first for any M03 artifacts/commits; if already complete and verified, do not redo them.
4. Execute **M03 — Rao channel selection/mapping audit** only.
5. Re-inspect the exact frozen Rao block first, focusing on `RAO_CHANNELS`, `RAO_DEFAULT_CHANNEL`, `_resolve_rao`, `memory_items.send_chat` call surface, channel display names, recovered channel IDs/constants, invalid/stale channel handling, and persistence interaction only where channel value participates.
6. Determine exact display-name→chat-channel-ID mapping, default/fallback behavior, whether persisted values are names or IDs, how invalid/retired values fail or normalize, and what argument is passed to `send_chat`.
7. Defer interval timing to M04, account assignment to M05, and slot start/stop lifecycle to M06.
8. Cross-check the supplied Rao screenshot only after static extraction.
9. Persist M03 artifacts, update STATE.md/PROJECT_STATUS.md, re-check code/build state, and advance only after M03 verification.


## M03 VERIFIED RESULTS
- PLAN.md and STATE.md were read first and GitHub was checked before analysis. No pre-existing M03 artifact/completion existed; M01-M02 and Phase-L contracts remain unchanged.
- The exact frozen original archive was materialized again; inner EXE SHA-256 remained `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- The current `RAO_CHANNELS` constant block was decoded directly from the original EXE. Exact display-name→ID mapping:
  - **Thế giới → 8**
  - **Bang hội → 2**
  - **Môn phái → 6**
  - **Tổ đội → 4**
  - **Liên minh → 3**
  - **Quân đoàn → 11**
  - **Lân cận → 5**.
- Exact raw Rao integer sequence immediately after the seven labels is `08,02,06,04,03,0b,05` in the same map order.
- `RAO_DEFAULT_CHANNEL` is statically **Thế giới**, therefore default Rao channel ID is **8**.
- The independent shared `memory_items.CHAT_CHANNELS` block was decoded and cross-checks the same IDs:
  - Đặc biệt 9; Lân cận 5; Nói thầm 7; Tổ đội 4; Thế giới 8; Bang hội 2; Liên minh 3; Môn phái 6; Liên máy chủ 10; Quân đoàn 11.
- Rao is therefore a strict seven-channel subset. **Đặc biệt/9, Nói thầm/7, Liên máy chủ/10 are not current Rao choices** and must not be added during reconstruction.
- M02's JSON `channel` field stores the Rao **display-name string**, not the numeric channel ID. The live row owns `chan_var`; runtime resolution maps that string through current `RAO_CHANNELS`.
- `_resolve_rao` exact documented success contract remains `(content, interval_seconds, channel_id, channel_name)`. Exact no-channel failure text remains `'<name>' chưa chọn kênh`.
- Shared `memory_items` post-marker local metadata gives the exact `send_chat` parameter order: **hwnd, channel_id, content** followed by internal locals `text/chan/lua_msg/code`.
- Rao `_slot_loop` independently carries `content, interval, chan_id, chan_name, ok, stamp, hit` and the `MI/send_chat` call surface. The frozen send boundary is therefore:
  `memory_items.send_chat(hwnd, chan_id, content)`.
- Do not pass the Vietnamese display-name string directly as the packet channel.
- Shared send packet constants/doc surface confirms:
  - packet contains numeric `Channel=`;
  - content is Base64 encoded in Lua for Vietnamese text;
  - `Network.SendPacket(G_TCPPacketDefine.CMD_CLIENT_CHAT, packetData)`;
  - embedded documentation explicitly gives examples **8=Thế giới, 2=Bang hội**;
  - a True return means the Lua send command was queued, not that server echo is guaranteed.
- Newly created Rao rows use the `RAO_DEFAULT_CHANNEL` policy. Screenshot cross-check after static extraction shows **Thế giới**, matching default ID 8.
- Exact load-time UI normalization of a **non-empty stale/retired channel string** remains **EXPLICIT_UNKNOWN**. M03 does not invent whether it is cleared, preserved or defaulted.
- Exact layer applying the default to missing/empty legacy channel data (load parser versus row constructor) remains **EXPLICIT_UNKNOWN**. Effective current default remains `RAO_DEFAULT_CHANNEL`.
- Safety/parity boundary is exact: only a current `RAO_CHANNELS` member may yield a normal sendable numeric channel ID. Do not synthesize a replacement ID for stale data.
- Frozen packaged `automove_log.txt` remains SHA-256 `17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`; correlated Rao/channel/send_chat/CMD_CLIENT_CHAT traces are **0**, so live packet/server-echo parity is not fabricated.
- M03 artifacts committed at **587ce1211e8ea90e8ccaf76cf3a52254dbeaddd1**:
  - `docs/rao/M03_CHANNEL_MAPPING_FLOW.md`
  - `docs/rao/M03_MODEL.json`
  - `docs/rao/M03_STATIC_EVIDENCE.tsv`
  - `docs/tasks/M03.md`
- All four M03 artifacts were fetched back successfully.

## POST-M03 CODE/BUILD RECHECK
- Recursive main tree after M03 artifact commit contains **677 entries**, not truncated.
- Python executable-code files remain exactly the same **7 forensic scripts** under `tools/`.
- No reconstructed application source directory exists.
- No build-system file and no GitHub Actions workflow exists.
- M03 artifact commit has **0 combined CI statuses** and **0 workflow runs**.
- M03 changed documentation/evidence only and introduced no executable-code/build regression.
- Product build remains **NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED**, not PASS/FAIL.

## BLOCKERS
- M03 has no channel-mapping blocker.
- Exact non-empty stale-channel normalization remains source-insufficient.
- Exact missing/empty defaulting layer remains source-insufficient.
- Live packet/server-echo timing requires Windows + live Thần Long runtime.
- Interval normalization/timing is intentionally deferred to M04.

## DO_NOT_TOUCH
- Preserve M01-M03 Rao authority/storage/channel contracts unless stronger exact evidence contradicts them.
- Preserve exact seven-channel Rao subset and IDs.
- Preserve persisted display-name channel values and runtime numeric mapping.
- Do not add Đặc biệt, Nói thầm or Liên máy chủ to Rao.
- Do not pass channel display names into `memory_items.send_chat`.
- Do not guess stale-channel migration behavior.
- Do not create Stage-S source/build placeholders during Phase M research.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md.
2. Read STATE.md.
3. Check GitHub first for any M04 artifacts/commits; if already complete and verified, do not redo them.
4. Execute **M04 — Rao interval normalization/timing audit** only.
5. Re-inspect the exact frozen Rao block first, focusing on `sec_var`, digits-only validation, `_resolve_rao` interval parsing, `_load_config` default/clamp surface, `_slot_loop` wait/sleep logic, current minimum/maximum if any, first-send timing, per-slot independence, and how interval changes while running are observed.
6. Determine exact default, storage type, parse/clamp policy, invalid/blank handling, send-before-wait versus wait-before-send behavior, timer reset semantics after send failure/success, and whether a live edit affects the next loop without restart.
7. Defer account assignment to M05 and start/stop ownership to M06 except where interval scheduling directly depends on slot worker state.
8. Cross-check the supplied Rao screenshot only after static extraction.
9. Persist M04 artifacts, update STATE.md/PROJECT_STATUS.md, re-check code/build state, and advance only after M04 verification.


## M04 VERIFIED RESULTS
- PLAN.md and STATE.md were read first and GitHub was checked before analysis. No pre-existing M04 artifact/completion existed; M01-M03 and Phase-L contracts remain unchanged.
- M04 re-inspected the exact frozen `rao_tab` constant/local surfaces before screenshot cross-check.
- Visible interval is **Lặp (s)** backed by `sec_var`.
- Rao interval entry uses nested `_only_digits` with Tk `%P` and recovered `isdigit`; normal UI input is decimal digits or temporarily blank text.
- Exact `_load_config` interval surface contains textual **30** as missing-value default and again as `TypeError/ValueError` fallback.
- Current default/fallback interval is therefore **30 seconds**.
- The exact load normalization cluster around `sec` contains:
  - `min`
  - integer **0**
  - integer **60**
  - `sec`
  - another integer **0**
  - `TypeError`
  - `ValueError`
  - fallback **30**.
- Together with the reused module `max` builtin and single `_sec` load local, this freezes the current normalized storage/UI semantic domain as **0..60 seconds**. M04 does not pretend the serialized constant stream is source code; exact min/max expression syntax is not reconstructed.
- `_resolve_rao` has exact invalid text **'<name>' chưa đặt thời gian lặp** and returns numeric `interval_giây` on success. Blank/zero is therefore not a usable repeat setting; normal runnable interval domain is positive **1..60 seconds**.
- Exact `_slot_loop` documentation: **Vòng lặp rao độc lập của 1 slot: gửi nội dung slot đó, nghỉ đúng hẹn giờ của dòng rao rồi lặp. Tối đa 4 slot chạy song song / acc.**
- This fixes first-send timing: **send first, then wait the configured interval, then repeat**. A newly started valid slot does not wait one full interval before its first send.
- Slot-loop static surface includes `_stop_event -> wait -> max` plus local `interval`; the interval delay is an **interruptible event wait**, not an unconditional `time.sleep(interval)`.
- Stop can therefore interrupt a long interval wait. Full ownership/stop semantics remain M06.
- Each account may run up to **4 independent slot loops/timers**; no global Rao timer shared by all slots was recovered.
- `_slot_loop` locals include `want/resolved/content/interval/chan_id/chan_name` and the loop carries `_resolve_rao` inside the repeating worker surface. It does not cache the resolved Rao definition only once at startup.
- M02 already proved Rao row edits are live trace writes and do not themselves restart the worker. Therefore changing interval while a slot is running:
  - does **not** retroactively reschedule the wait already in progress;
  - is observed when the next loop re-resolves the definition;
  - does **not** require stop/start for subsequent cycles.
- Static send sequence contains `send_chat`, send-exception/status/echo surfaces, and then the common interval-wait boundary. No separate fast-retry/backoff interval or retry queue was recovered for normal send/no-echo failure.
- Normal completed attempts therefore return to the configured interval. Hard invalid/window/stop conditions may terminate the slot instead.
- Exact doc **Dừng 1 slot (rao bị xóa/lỗi giữa chừng).** plus per-loop re-resolution means a definition deleted/renamed/blanked/otherwise invalid between cycles fails closed/stops the affected slot instead of continuing forever on stale cached content/interval.
- Persistence field remains `sec`; row source is a StringVar/textual decimal seconds, while runtime resolution yields numeric seconds. No hidden milliseconds/minutes representation was recovered.
- Screenshot cross-check after static extraction shows **30**, matching the recovered current default/fallback.
- Frozen runtime log contains no Rao send/interval trace, so exact Windows scheduling jitter and server-echo timing remain runtime-required.
- M04 artifacts committed at **96e9540ef959e270fb187fb4534e4c5d96cce014**:
  - `docs/rao/M04_INTERVAL_FLOW.md`
  - `docs/rao/M04_MODEL.json`
  - `docs/rao/M04_STATIC_EVIDENCE.tsv`
  - `docs/tasks/M04.md`
- All four M04 artifacts were fetched back successfully.

## POST-M04 CODE/BUILD RECHECK
- Recursive main tree after M04 artifact commit contains **681 entries**, not truncated.
- Python executable-code files remain exactly the same **7 forensic scripts** under `tools/`.
- No reconstructed application source directory exists.
- No build-system file and no GitHub Actions workflow exists.
- M04 artifact commit has **0 combined CI statuses** and **0 workflow runs**.
- M04 changed documentation/evidence only and introduced no executable-code/build regression.
- Product build remains **NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED**, not PASS/FAIL.

## BLOCKERS
- M04 has no interval-model blocker.
- Exact Tk validator boolean expression is not source-reconstructed; accepted-input semantics are frozen.
- Exact Windows scheduler jitter/server echo latency remains runtime-required.
- Exact account-row state text after a running slot becomes invalid belongs to M06.
- Account assignment/persistence is intentionally deferred to M05.

## DO_NOT_TOUCH
- Preserve M01-M04 Rao authority/storage/channel/interval contracts unless stronger exact evidence contradicts them.
- Preserve 30s default, 0..60 normalized storage domain, and positive 1..60 runnable domain.
- Preserve first-send-before-wait behavior and interruptible event wait.
- Do not replace per-slot timers with one global Rao timer.
- Do not force a worker restart just to observe a valid live interval edit on the next cycle.
- Do not invent a separate retry/backoff interval.
- Do not create Stage-S source/build placeholders during Phase M research.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md.
2. Read STATE.md.
3. Check GitHub first for any M05 artifacts/commits; if already complete and verified, do not redo them.
4. Execute **M05 — Rao account assignment/persistence audit** only.
5. Re-inspect the exact frozen Rao block first, focusing on `_add_or_update_row`, `_refresh_acc_rao_options`, `_on_rao_var_changed`, `load_acc_config`, `_sanitize_name`, `_get_char_info`, `_get_char_name`, HWND/PID identity binding, four `rao_vars`/comboboxes, `acc_` persistence, stale/renamed Rao reconciliation, and refresh/reuse behavior.
6. Determine exact per-character key format, slot ordering/count, save encoding, restore rules, duplicate character-name/HWND/PID behavior, what happens when account disappears/reappears, exact immediate stale-name clear/preserve behavior after Rao rename/delete when recoverable, and whether running-slot state changes when assignment is edited.
7. Defer full slot start/stop ownership to M06 except where assignment edits directly stop/restart a slot.
8. Cross-check supplied Rao screenshot only after static extraction.
9. Persist M05 artifacts, update STATE.md/PROJECT_STATUS.md, re-check code/build state, and advance only after M05 verification.


## M05 VERIFIED RESULTS
- User explicitly asked to check GitHub first and skip anything already correct. GitHub was re-checked before M05: `main` HEAD was **5e884a36d59bdd13dcb689aa0e9fa0aaac26f245**, M01-M04 were complete, M05 was still NEXT, and **no M05 artifacts/task existed**. No completed Rao work was repeated.
- Exact frozen archive was revalidated again: ZIP SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; inner EXE SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Rao runtime account identity and persistence identity are separate:
  - live row registry uses **HWND + expected PID**;
  - persisted account assignment uses the **real sanitized character name**.
- `_sanitize_name` exact documentation is **Loại bỏ HTML tags khỏi tên nhân vật.** with current pattern `<[^>]+>`. `RoleName` is the real character-name source. No lower/casefold normalization surface was recovered.
- The account path has an explicit temporary pseudo-name prefix **Window **. `load_acc_config` contains `startswith("Window ")`, so this fallback is not a normal persistent restore identity.
- Persistent key format is frozen as **[Rao] acc_<real sanitized character name>**. No HWND/PID suffix belongs to the persistent key.
- Each account owns exactly **4 Rao-selection slots**. Exact load documentation: **Khôi phục 4 combobox nội dung rao đã lưu theo tên nhân vật. Chỉ áp tên rao còn tồn tại. Trả True nếu đã áp ít nhất 1 slot.**
- Save/load surfaces (`cname/_vals/_v`, `json.dumps`, `raw/vals/parsed`, `json.loads`, literal 4 and four `rao_vars`) establish one **ordered JSON list of four Rao display-name strings** under the single `acc_<name>` key.
- Slot order is positional 1→4. No separate `acc_<name>_1..4` family was recovered. No uniqueness guard between the four selected Rao names was recovered.
- `_on_rao_var_changed` exact documentation: **Trace combobox nội dung rao: đánh dấu user đổi + lưu setting.** Manual account assignment edits therefore mark the row user-touched and persist current selections.
- M02's family boundary remains valid: `rao_` definitions and `acc_` account assignments coexist independently under `[Rao]`; message-definition rewrites do not replace the whole section.
- M02's unresolved immediate stale-name behavior was narrowed in M05. `_refresh_acc_rao_options` has current `names/row/cb/var/cur` locals plus an exact empty-string constant and documentation **Đổ lại combobox nội dung rao của mọi acc theo danh sách tên hiện tại.** A selected Rao name that is no longer in the current definition universe is therefore **cleared from the live account combobox**.
- Rename/delete does **not** propagate old name to new name: no alias table or row UUID exists. `Rao X -> Rao Y` makes the old `Rao X` reference stale and it is cleared.
- Exact disk-save timing of this automatic stale clear remains **EXPLICIT_UNKNOWN** because the `prev` local is consistent with temporary trace/save suppression during option refresh. Later reload is safe because `load_acc_config` only restores names that still exist.
- Row state includes both `_has_real_name` and `_rao_touched`. In the add/update path these sit directly beside delayed RoleName resolution and `load_acc_config`; the frozen semantic boundary is that late real-name config restore must not overwrite a row the user already edited manually.
- Exact boolean statement ordering for `_has_real_name/_rao_touched` remains unknown and is not invented.
- Same HWND reused by a different PID is explicitly treated as a dead old process. Exact log surface: **[Rao] hwnd=... đổi process (pid ... → ...) — cửa sổ cũ đã mất, tạo lại row mới**. Rao uses bind/unbind window identity and recreates the runtime row.
- Exact stale-row documentation: **Xóa acc của window đã đóng HOẶC đã đổi process (HWND tái sử dụng).**
- Because persistence is real-name keyed and the Rao section is not replaced with only current live accounts, a disappeared account's saved `acc_<name>` assignment remains available. When the same real character reappears in a new window/PID, the fresh row can restore its four slots by name.
- Duplicate real character names are separate live HWND/PID rows but **not** separate persistence identities. No Rao HWND suffix/disambiguator was recovered; both map to the same `acc_<name>` key. Exact save winner if their assignments differ remains **EXPLICIT_UNKNOWN**.
- Editing a slot's Rao assignment while that slot is already running does not have a recovered forced restart surface. Combined with M04's per-loop re-resolution:
  - current in-progress wait is not rescheduled;
  - next loop reads the new selected Rao name;
  - a valid new name changes subsequent content/channel/interval;
  - blank/stale/invalid new name fails closed and the slot stops on the next resolution.
- Exact state-label/worker shutdown timing belongs to M06.
- Supplied Rao screenshot contains no account rows, so M05 account behavior is EXE-static evidence rather than inferred from an empty capture.
- Frozen packaged `automove_log.txt` remains SHA-256 `17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`; correlated Rao assignment/window traces are **0**, so live PID/refresh races are not fabricated.
- M05 artifacts committed at **b417cb3da063422a1ba0a4353bc9cc18615b32a0**:
  - `docs/rao/M05_ACCOUNT_ASSIGNMENT_FLOW.md`
  - `docs/rao/M05_MODEL.json`
  - `docs/rao/M05_STATIC_EVIDENCE.tsv`
  - `docs/tasks/M05.md`
- All four M05 artifacts were fetched back successfully.

## POST-M05 CODE/BUILD RECHECK
- Recursive main tree after M05 artifact commit contains **685 entries**, not truncated.
- Python executable-code files remain exactly the same **7 forensic scripts** under `tools/`.
- No reconstructed application source directory exists.
- No build-system file and no GitHub Actions workflow exists.
- M05 artifact commit has **0 combined CI statuses** and **0 workflow runs**.
- M05 changed documentation/evidence only and introduced no executable-code/build regression.
- Product build remains **NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED**, not PASS/FAIL.

## BLOCKERS
- Exact malformed/non-list account JSON fallback remains source-insufficient.
- Exact same-callback disk-save timing of automatic stale-selection clearing remains source-insufficient.
- Duplicate-character-name persistent collision winner remains source-insufficient.
- Exact `_has_real_name/_rao_touched` mutation order remains source-insufficient.
- Live window-disappearance worker/state timing is intentionally deferred to M06.

## DO_NOT_TOUCH
- Preserve M01-M05 Rao authority/storage/channel/interval/account-assignment contracts unless stronger exact evidence contradicts them.
- Keep runtime row identity HWND/PID separate from persistent real-character-name identity.
- Do not add HWND/PID suffixes to current Rao `acc_<name>` persistence.
- Preserve exactly four ordered account Rao slots and JSON-list semantics.
- Preserve immediate live stale-selection clearing without inventing old→new rename propagation.
- Do not guess duplicate-name collision winner or stale-clear disk timing.
- Do not force a worker restart for a valid live assignment edit unless M06 exact evidence contradicts the next-cycle model.
- Do not create Stage-S source/build placeholders during Phase M research.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md.
2. Read STATE.md.
3. Check GitHub first for any M06 artifacts/commits; if already complete and verified, do not redo them.
4. Execute **M06 — Rao start/stop worker audit** only.
5. Re-inspect the exact frozen Rao block first, focusing on `_slot_loop`, `_stop_slot`, `_set_state`, `_any_slot_running`, `_ui_after_stop`, `_paint_stopped`, `_stop_acc`, `_start_slot`, `_toggle_single_acc`, `_start_all_accs`, row `_state`, `_stop_event`, per-slot generation/running state, account play button, permission limit guard, window/PID loss, and thread ownership.
6. Determine exact per-slot start/stop ownership, account ▶/stop toggle semantics, start-all inclusion/exclusion, slot-generation stale-worker guard, state text/color transitions, what happens when one of four slots fails, when the account is considered running/stopped, handling of window/PID loss, permission failure, and stop behavior during interval wait/send.
7. Preserve M01-M05 message/channel/interval/account-assignment contracts; do not reopen them unless direct contradiction appears.
8. Cross-check screenshots/runtime only after static extraction.
9. Persist M06 artifacts, update STATE.md/PROJECT_STATUS.md, re-check code/build state, and advance only after M06 verification.


## M06 VERIFIED RESULTS
- Checked GitHub `main` first (HEAD `eedf0a1f31fc27ae4b63b582b1967785a70d8037`); M01–M05 already existed, M06 did not.
- Supplied `TLMTool_2.1.2(9).zip` is byte-identical to Gate-A frozen authority: ZIP SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, inner EXE SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Binary-first audit of exact `rao_tab` block: bottom `Bắt đầu` delegates to `_start_all_accs` on a daemon Thread; account ▶ delegates to `_toggle_single_acc` via background work.
- Four independent per-account slot loops, `row._stop_event`, `_gen`, `_slot_running`; one-slot stop `_stop_slot`, per-account all-slot stop `_stop_acc`.
- `_start_slot` starts only a valid definition and returns a started boolean. `_any_slot_running` is true if **at least one** of four slots remains active.
- Current worker resolves/send_chat/optional echo-diagnostic and performs send-first then interruptible Event.wait; preserves M02–M05 interval, ID and live-edit behavior.
- `_ui` marshals Tk status changes; original status/button surfaces include `Đã dừng`, `Đang rao ... /4 nhóm...`, `Dừng lại`.
- Bulk start's exact doc says to start every account with assigned content and skip accounts without it. Per-account and bulk permission-denial surfaces are explicitly present.
- Loop guards current HWND/PID and yields `Cửa sổ đã đóng` for invalid window; exact generation/race/worker interruption ordering remains UNKNOWN.
- User Rao screenshot was consulted only after static extraction; it has no account rows, so worker state and colors remain visually/runtime-unverified.
- Packaged runtime automove_log has no Rao traces. Windows live runtime parity **NOT_RUN**, and source reconstruction **NOT_STARTED**.
- M06 status = **STATIC_WORKER_CONTRACT_AUDITED_LIVE_PARITY_DEFERRED**.
- M06 artifacts: `docs/rao/M06_WORKER_LIFECYCLE_FLOW.md`, `docs/rao/M06_MODEL.json`, `docs/rao/M06_STATIC_EVIDENCE.tsv`, `docs/tasks/M06.md`.

## POST-M06 CODE/BUILD RECHECK
- No application source, build script, or GitHub Actions workflow was introduced or modified.
- The seven forensic scripts under `tools/` remain the only Python executable-code sources on main.
- Product build **NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED** — not a claimed PASS.

## BLOCKERS
- Exact `_gen` increment/comparator and stale Tk callback ordering are not directly reconstructed.
- Bottom-button repeat/reentrancy behavior remains unknown despite `_start_all_busy` evidence.
- Exact in-flight send/echo cancellation, thread join behavior, multiple-slot partial-stop UI state, and HWND/PID race ordering require deeper evidence or Windows runtime.

## DO_NOT_TOUCH
- Preserve Phase M01–M05 Rao contracts: channel IDs, 30s default, per-slot timings, name-keyed persistence and live edits.
- Preserve permission checks; no bypass.
- No global Rao stop-all behavior may be invented from the `Bắt đầu` button.
- No Stage-S source/EXE placeholders and no unrelated UI changes.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md and STATE.md.
2. Check GitHub for M07 artifacts and recent commits; do not redo if complete.
3. Execute **M07 — Rao parity/reconstruction handoff** only: reconcile M01–M06 message/channel/interval/account/worker contracts into one evidence-tiered reconstruction contract plus an acceptance matrix distinguishing static checks, Windows live tests and explicit unknowns.
4. Recheck exact frozen EXE evidence where needed; only after that compare Rao screenshots.
5. Persist M07 report/model/parity matrix/task, update STATE.md and PROJECT_STATUS.md.
6. Recheck code/build status; do not claim build until Stage-S reconstructed application source and Stage-T workflow exist.


## M07 VERIFIED RESULTS — RAO PHASE HANDOFF
- GitHub checked first: parent HEAD `e3784b7b23b464632517e2487445e5cd925db53d`; M01–M06 existed and M07 did not. No earlier Phase-M artifacts reimplemented or modified.
- Supplied archive `TLMTool_2.1.2(9).zip` SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; inner EXE SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`. Frozen original remains normative.
- M01–M06 reconciled into an evidence-tiered reconstruction contract. No direct contradiction across six frozen Rao contracts found.
- UI, [Rao] definition/account config, exact seven chat channel IDs, 30s default/0..60 normalization/positive 1..60 runnable, four independent send-first slot workers, HWND/PID guards, permission limit and UI-state text preserved.
- `docs/rao/M07_RAO_PARITY_MATRIX.tsv` contains **70 acceptance cases**: 30 STATIC, 5 VISUAL, 28 WINDOWS, 7 RESEARCH. All cases have status NOT_EXECUTED_STAGE_S_NOT_STARTED, never fictitious PASS.
- Explicit unknowns include bulk double-press policy, generation comparison/order, in-flight send/echo cancellation, stale-PID/UI races, malformed config collision winners and unverified account-row visuals.
- Phase M gate: **STATIC_RESEARCH_CLOSED / LIVE_RUNTIME_PARITY_DEFERRED**. Stage S/T product source/build **NOT_STARTED**.
- New files: `docs/rao/M07_RECONSTRUCTION_CONTRACT.md`, `docs/rao/M07_MODEL.json`, `docs/rao/M07_RAO_PARITY_MATRIX.tsv`, `docs/tasks/M07.md`.

## POST-M07 CODE/BUILD RECHECK
- No product source, build scripts or CI workflow added. Only documentation, model and milestone status files changed.
- Build remains **NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED**, not PASS/FAIL.

## BLOCKERS / DO_NOT_TOUCH
- Live Rao parity needs controlled Windows + actual game; original screenshot has zero account rows.
- Do not fabricate exact original Python flow where only serialized constants were recovered.
- Preserve all M01–M06 specs, no extra Rao StartTab button, no Proxy implementation, no unrelated UI changes.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md and STATE.md and check current GitHub first for N01 artifacts.
2. If N01 exists, audit/skip completed items; else begin **N01 — Tối ưu module/active UI authority audit**.
3. Inspect original frozen `toiuu_tab` EXE evidence first: active class/UI creation, CPU/GPU monitor, detached monitor, graphics configuration, per-account and global actions and permission guard.
4. Only after static extraction compare user-supplied Tối ưu screenshot; do not overclaim GPU live data from capture.
5. Persist N01 task/evidence/model, update STATE.md/PROJECT_STATUS.md, and re-check source/build state.


## N01 VERIFIED RESULTS — TỐI ƯU ACTIVE AUTHORITY / UI
- Read PLAN.md/STATE.md/PROJECT_STATUS.md and checked GitHub main HEAD `76fc32fb8cc6f3790e30cceaafece18ff1f4e82f` first; no pre-existing N01 artifacts. Reused B11 visual baseline; no previous complete task repeated.
- Frozen uploaded TLM archive SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; active inner standalone EXE SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`; 1,050 entries, CRC clean.
- Original `.toiuu_tab` serialized block starts `0x2c01fb5`, 22,485-byte payload, 940 constant entries; active class `ToiuuTab`, module file marker `toiuu_tab.py`.
- Distinct `.cpu_monitor` block starts `0x28d82e9`, 2,019-byte payload/127 constants; `CPUMonitor` uses psutil CPU-high warning and is NOT the tab CPU/GPU plotting engine.
- Tab UI authority recovered: monitor charts, `Tách theo dõi`, account rows, bulk mode buttons, `Bắt đầu`, status labels; B11 screenshot retained as baseline, no populated account row fabricated.
- Exact original EXE doc confirms **1s CPU/GPU sample worker -> main-thread redraw**, GPU query via nvidia-smi and N/A state.
- Native performance `dll_injector`/TLMP helper path exists. Original docs distinguish **assigning a mode in combobox only** from **applying native perf upon Start**; no dummy command is permitted.
- Monitor `toiuu_monitor_open`, running `toiuu_running`, StartTab Theo dõi/Tối ưu button sync, permission guards, account HWND/PID identity, TLMP-5 watch/Treo tick recovery intent inventoried; behavior depth deferred N02–N09.
- N01 artifacts: `docs/toiuu/N01_AUTHORITY_UI_FLOW.md`, `docs/toiuu/N01_AUTHORITY_MODEL.json`, `docs/toiuu/N01_STATIC_EVIDENCE.tsv`, `docs/tasks/N01.md`.
- N01 gate **STATIC_AUTHORITY_AND_UI_SURFACE_AUDITED / LIVE_PARITY_DEFERRED**. No Windows game execution, source application or build workflow.

## POST-N01 BUILD/CODE CHECK
- Changes are documentation/model/status only; original binary and 7 forensic scripts unchanged.
- Product EXE build **NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED**. Do not claim PASS or functional parity.

## N01 BLOCKERS / DO_NOT_TOUCH
- Exact reconstructed source statements, GPU monitoring errors, graph history/timer bounds, populated account UI and DLL native command outcomes require later evidence/runtime.
- Preserve previous N/M/B11 contracts; no Proxy runtime development; no unrelated UI/code changes.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md/STATE.md, check GitHub main for N02 artifact/commit; skip if complete.
2. Execute **N02 — CPU monitoring sample/history/redraw audit** only, EXE-first: `ToiuuTab._start_graphs`, `_sample_loop`, `_schedule_redraw`, `_fmt_pct`, `_draw_one`, `_redraw_graphs`, `GRAPH_HIST`, `GRAPH_TICK_MS`, `psutil`, Tk-after and shutdown.
3. Keep `cpu_monitor.CPUMonitor` high-CPU warning distinct from Tối ưu plotted history. GPU reader is N03, detached view N04, native apply N05 onward.
4. Compare B11 screenshot after static evidence; never infer unseen populated rows.
5. Persist N02 model/evidence/task, update STATE.md/PROJECT_STATUS.md, recheck source/build without claiming running parity.


## N02 VERIFIED RESULTS — CPU SAMPLING / GRAPH HISTORY / REDRAW
- Re-read PLAN.md/STATE.md/PROJECT_STATUS.md, checked GitHub main HEAD `bddfbcb8a20641b3b53c1abee45a4273552f24d6` and confirmed N02 absent before work. N01/B11 artifacts were reused unchanged.
- Original frozen uploaded ZIP SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, inner EXE SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`; ZIP CRC clean, 1,050 entries.
- ToiuuTab original graph path statically recovered: `HAS_PSUTIL_TOIUU`, `cpu_percent`, `interval=None`-like local signature, `_sample_loop`, `_schedule_redraw`, `_redraw_graphs`, `_fmt_pct`, `_draw_one`, `Canvas.delete/create_line`.
- Original doc states **“Sample 1s/lần (thread phụ) + vẽ lại (main thread).”** Worker-to-Tk separation is recorded, no live timing is claimed.
- Bounded graph history uses `deque(maxlen=GRAPH_HIST)` family with distinct `_cpu_hist` and `_gpu_hist`.
- Crucial unresolved timer detail: original EXE stores `GRAPH_TICK_MS`, `sleep`, double 1000.0 and separately tagged numeric values 750 and 64. Exact variable assignment was not decompiled; **documented 1s vs candidate 750ms remains EXPLICIT_UNKNOWN**. Exact `GRAPH_HIST` buffer size also UNKNOWN. Never silently bind these values.
- Plotting primitives `delete`, `create_line`, `.0f`/unavailable `--%`, grid fractions 0.25/0.5/0.75, bound 100.0, CPU #1565c0 and guide grid #e0e0e0 recovered. B11 visual baseline (CPU 15%, blue line) cross-checked only after binary review.
- Separate `cpu_monitor.CPUMonitor` high-CPU warning intentionally NOT merged into Tối ưu graph; GPU deep reader remains N03.
- N02 status **STATIC_CPU_SAMPLE_HISTORY_REDRAW_AUDITED_WITH_EXPLICIT_TIMER_UNCERTAINTY / LIVE_RUNTIME_DEFERRED**.
- Artifacts: `docs/toiuu/N02_CPU_SAMPLE_REDRAW_FLOW.md`, `docs/toiuu/N02_MODEL.json`, `docs/toiuu/N02_STATIC_EVIDENCE.tsv`, `docs/tasks/N02.md`.

## POST-N02 CODE/BUILD RECHECK
- Documentation/status files only. No product source, launcher, workflow or previous implementation code altered.
- Product build remains **NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED**, no live Windows result or runtime PASS asserted.

## N02 BLOCKERS / DO_NOT_TOUCH
- Exact GRAPH_TICK_MS assignment (1s documentation vs potential 750ms), history length, CPU-error sample policy, render/update coalescing and close races require source-level or live instrumentation. Never mark DONE for functionality based solely on UI/evidence.
- Preserve A–M, B11, N01 and original executable; Proxy remains explicitly outside development scope.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md and STATE.md; check GitHub first for N03 artifacts and skip if already verified.
2. Execute **N03 — GPU collection / nvidia-smi failure and chart integration audit** only. Inspect exact frozen `toiuu_tab._read_gpu` original EXE block: command argv, CREATE_NO_WINDOW, subprocess timeout, decode/CSV parse, missing executable, invalid values/None, GPU history availability, label and drawing.
3. Preserve N02 CPU sampler; do not merge CPUMonitor; detached window belongs to N04; native TLMP belongs to N05+.
4. Cross-check GPU N/A screenshot only after static analysis, not as proof of all GPU error paths.
5. Persist N03 report/model/evidence/task, update STATE.md/PROJECT_STATUS.md and re-check source/build status.


## N03 VERIFIED RESULTS — GPU COLLECTION / GRAPH INTEGRATION
- Checked PLAN.md and STATE.md and GitHub HEAD 326090e7b7ec8b44a4f9bf767bd0f50ac9ca8831 first; N01/N02 complete, N03 absent. Original ZIP c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd (1050 entries, CRC clean); inner EXE 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22 unchanged.
- Exact ToiuuTab._read_gpu command strings: nvidia-smi, --query-gpu=utilization.gpu, --format=csv,noheader,nounits, plus subprocess.check_output, CREATE_NO_WINDOW, STDOUT/stderr, timeout/creationflags.
- Parse symbols decode/utf-8/ignore/errors/replace/split/isdigit, locals self/flags/out/vals; original embedded doc: % GPU qua nvidia-smi; None nếu không có/không đọc được.
- GPU UI uses _gpu_avail, bounded _gpu_hist, _sample_loop/_redraw_graphs/_draw_one, orange #e65100, GPU: N/A (không có nvidia-smi). Reused B11 screenshot after binary-first review.
- Exact timeout, stderr routing, multi-GPU selection, error/zero-None and missing-history semantics EXPLICIT_UNKNOWN. Tagged integer 3 near command is not proven timeout. N02 timer unresolved unchanged.
- N03 status STATIC_GPU_READER_FAILURE_INTERFACE_AUDITED / LIVE_PARITY_DEFERRED. 43 row evidence table and eight future tests (all NOT_RUN).
- New docs: docs/toiuu/N03_GPU_COLLECTION_FLOW.md; docs/toiuu/N03_MODEL.json; docs/toiuu/N03_STATIC_EVIDENCE.tsv; docs/tasks/N03.md.

## POST-N03 CODE/BUILD CHECK
- Four new docs/models + status files only. No original EXE or code modified. Application source/workflow absent, build NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED.

## BLOCKERS / DO_NOT_TOUCH
- Actual GPU/Windows execution, original timeout/error path, multi-GPU parser and history gaps still unverified. Preserve N01/N02/B11, A–M, and Proxy exclusion; no fake runtime PASS.

## NEXT_ACTION
On CONTINUE read PLAN.md/STATE.md, check GitHub for existing N04, then execute **N04 — detached CPU/GPU monitor lifecycle/layout/persistence audit** only. EXE-first inspect _toggle_monitor_view, _open_monitor_view, _close_monitor_view, _update_monitor_view, _restore_monitor_view and toiuu_monitor_open; screenshot after binary. Persist N04 model/evidence/task, update state, recheck source/build.

## N04 VERIFIED RESULTS — DETACHED CPU/GPU MONITOR
- On CONTINUE checked PLAN.md, STATE.md and GitHub HEAD `0d18f577b3be9d23893595d8e88c69570642c832`, confirmed N01–N03 completed and N04 absent. Preserved old evidence unchanged.
- Revalidated original ZIP SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd` (1,050 entries, CRC clean) and inner EXE SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Exact ToiuuTab method markers: `_toggle_monitor_view`, `_open_monitor_view`, `_close_monitor_view`, `_update_monitor_view`, `_restore_monitor_view`, `_save_monitor_state`.
- Toggle uses `winfo_exists` plus open/close; embedded doc **Mở/đóng view bar CPU/GPU tách rời (sát cạnh trái GUI chính, cao 768).** Startup has `after/_restore_monitor_view` and exact auto-reopen doc.
- Real Tk `Toplevel` titled `CPU / GPU`; `winfo_rootx/y`, `geometry`, `minsize/maxsize`, `overrideredirect`, `-topmost`, `WM_DELETE_WINDOW`; CPU/GPU columns built via `_make_bar_col`, `Đóng theo dõi`, `create_rectangle/create_text`.
- Open-state settings key `[Settings] toiuu_monitor_open`, shared read/write lock, `_save_monitor_state`, error trace, truth-like parsing. Exact method-call flags/serialized expression and save/close order remain UNKNOWN.
- `_update_monitor_view` is in original `_redraw_graphs` symbol region; reuse N02/N03 histories is a strong static architectural model, not source-level call-order proof.
- Reused B11 Tối ưu screenshot AFTER EXE inspection; screenshot has pop-out **button** but no detached Toplevel. No invented detached-window geometry/visuals.
- N04 status **STATIC_DETACHED_MONITOR_LIFECYCLE_AND_UI_AUDITED / LIVE_PARITY_DEFERRED**. 71 evidence rows, 16 future acceptance cases all NOT_RUN.
- N04 files: `docs/toiuu/N04_DETACHED_MONITOR_FLOW.md`, `docs/toiuu/N04_MODEL.json`, `docs/toiuu/N04_STATIC_EVIDENCE.tsv`, `docs/tasks/N04.md`.

## POST-N04 BUILD/CODE CHECK
- N04 modifies documentation and STATE/PROJECT_STATUS only; no source app, build workflow or original EXE changed. Build **NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED**; Windows parity NOT_RUN.

## N04 BLOCKERS / DO_NOT_TOUCH
- Detached panel not shown in B11 screenshot; width/position equation, multi-monitor DPI, Tk teardown and exact Boolean flags not source-reconstructed. Keep N01–N03, B11, A–M, Proxy scope exclusion unchanged; do not simulate fake functional controls.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md/STATE.md and inspect current GitHub for N05 artifacts; skip if complete.
2. Execute **N05 — Tối ưu graphics-mode mapping, per-account configuration and selection-versus-application audit** only. Inspect exact frozen original `toiuu_tab` first for MODE_ORDER/MODE_NAMES/MODE_TO_TLMP, `Không`, row combobox, gray bulk buttons, per-account mode, settings persistence and `_cfg_assign_worker`.
3. Lock distinction selection-only versus native application. Defer `dll_injector` native packet/handshake implementation audit to N06; avoid any functionality bypass.
4. Compare B11 screenshot only after EXE; persist N05 model/evidence/task; update STATE.md/PROJECT_STATUS.md and recheck build status.


## N05 VERIFIED RESULTS — TỐI ƯU MODE CONFIG AND SELECTION VERSUS APPLY
- GitHub HEAD a24d3be5bf9d488f4dee7dba47256d7f9a454e58 checked first; PLAN.md and STATE.md read, N01–N04 complete and N05 absent. Frozen ZIP SHA c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd (1050 entries CRC clean), inner EXE 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22 unchanged.
- Internal medium/low/max map to current Thấp vừa/Cực thấp/Cực đại and tagged TLMP values 1/2/3. Không maps to skip/keep current, not an immediate restore command; _mode_of_row doc returns None for Không.
- Original _cfg_assign_worker and _set_single_worker docs prove gray all-account/row mode controls only assign combobox values, NO native perf send. _set_all_combobox/_set_single_apply use Tk thread; bulk change saves once; bottom Bắt đầu/row ▶ own actual apply.
- Per-account toiuu_cfg_ + sanitized RoleName persistent key; temporary Window prefix excluded; load_acc_config restores only valid selections. _has_real_name/_cfg_touched protects delayed restore from user edits, exact mutation order UNKNOWN. _on_config_var_changed caches _mode_key and saves config, with bulk trace/save suppression.
- _send_perf_single/_send_perf_all/dll_injector/TLMP_RESTORE and expected_pid guard are actual native boundaries, detailed N06, not N05; permissions stay enforced.
- INI section/default priority, duplicate-character-name winner, malformed config and runtime parity UNKNOWN. B11 screenshot has no account rows.
- N05 status STATIC_MODE_ACCOUNT_CONFIGURATION_AND_SELECTION_APPLY_BOUNDARY_AUDITED / LIVE_PARITY_DEFERRED. 52 evidence records; 18 future tests all NOT_RUN.
- Files added: docs/toiuu/N05_MODE_CONFIG_SELECTION_FLOW.md, docs/toiuu/N05_MODEL.json, docs/toiuu/N05_STATIC_EVIDENCE.tsv, docs/tasks/N05.md.

## POST-N05 BUILD/CODE CHECK
- Only documentation and STATE/PROJECT_STATUS updated. No application source or build workflow. Product build NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED.

## N05 DO_NOT_TOUCH AND BLOCKERS
- Preserve completed A–M, B11, N01–N04 and original EXE. Proxy remains outside development. No fake buttons, bypasses or claimed Windows parity. N06 must distinguish actual DLL payload from selected UI values.

## NEXT_ACTION
On CONTINUE read PLAN.md and STATE.md, check GitHub for N06 artifacts, then execute N06 — native TLMP graphics/performance command path, DLL send/restore and expected PID-guarded per-account/all-account execution audit ONLY. Original EXE first; avoid guessing native packet/protocol details. Persist N06 report/model/evidence/task and state, recheck build.


## N06 VERIFIED RESULTS — NATIVE TLMP, DLL AND EXPECTED PID
- Checked PLAN.md, STATE.md, PROJECT_STATUS.md and GitHub main HEAD d0d6bfd1148b267386575b9f35d55139bcefaeb0 first; N01–N05 complete, N06 absent. No completed module rewritten.
- Frozen ZIP SHA256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd (1050 entries CRC clean); original EXE SHA256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22.
- Original compiled .dll_injector at 0x2918f40 documents WM_COPYDATA with PerfCmd and WM_PERF_TOKEN TLMP, native OnTick handling. Modes: 0 normal/FPS40; 1 Thấp vừa/FPS30; 2 Cực thấp AA/LOD/far/URP; 3 Cực đại black background; 4 restore original snapshot; 5 diagnostic ping. N05 Không selection remains SKIP, not mode 0 or 4.
- Bundled data/resources.dat is real x64 PE DLL, 39424 bytes SHA256 1375240c85abb9c211c66d3e8157a6dbfbc5551aabec465375b68e5301e645d4; packed UPX2 sections and MinHook-like exports. DLL original handler source not recovered and was NOT executed.
- _send_perf_single returns bool with expected_pid HWND-owner guard; _send_perf_all returns ok_count,total and injects if needed. Original failure logs cover missing PID, changed ownership, missing DLL, injection error, outdated/nonresponding TLMP. Bool result not proven as game-state success.
- _stop_restore_single doc contains staged Cực đại -> Cực thấp -> wait STAGE_DOWN_DELAY -> TLMP_RESTORE to avoid model rebuild visual hang. Numeric delay and exact error branches UNKNOWN.
- _start_all_accs busy/scan/start/stop strings recovered but scheduling belongs N07. Single-account code has literal acc bắt đầu — TODO logic; investigate rather than assume complete or broken.
- Historical packed data/automove_log.txt SHA256 17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500, 71247 Perf lines with 122 PID labels, 4134 ping lines, 737 snapshot restored, 1282 unity-low applies, 532 cam black ON. This is **PACKAGED HISTORICAL RUNTIME EVIDENCE**, not current Windows validation. No [Toiuu marker found in packaged log.
- N06 status STATIC_NATIVE_TLMP_AND_DLL_BOUNDARY_AUDITED_WITH_HISTORICAL_PERF_LOG / LIVE_PARITY_DEFERRED.
- N06 artifacts: docs/toiuu/N06_NATIVE_TLMP_DLL_FLOW.md, docs/toiuu/N06_MODEL.json, docs/toiuu/N06_STATIC_EVIDENCE.tsv, docs/tasks/N06.md. 79 evidence records; 18 planned tests all NOT_RUN.

## POST-N06 CODE/BUILD CHECK
- No product app source or workflow exists, only existing 7 forensic Python tools. Changed only N06 docs/model and STATE.md / PROJECT_STATUS.md. No native binary changed. Product build NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED.

## N06 BLOCKERS / DO_NOT_TOUCH
- Exact PerfCmd packet field/value and acknowledgment, DLL hook behavior, current Windows test, native stop/race behavior not source-proof. No bypass, no Proxy development, no arbitrary edits to N01–N05 / A–M / PLAN / original EXE.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md and STATE.md and check GitHub for N07 before work.
2. Execute **N07 — Tối ưu per-account/all-account start-stop lifecycle, worker concurrency, UI-state and HWND/PID/permission orchestration audit** only, original EXE-first. Focus _start_all_accs, _toggle_single_acc, _all_monitor, _restore_targets, _ensure_rows_loaded, and TODO-logic branch.
3. Preserve N05 selection-only semantics and N06 mode/restore contract, no DLL/source guesses.
4. Compare screenshots only after static extraction; account rows absent from B11 capture.
5. Save N07 docs/model/evidence/task, update STATE.md/PROJECT_STATUS.md and recheck build status.
