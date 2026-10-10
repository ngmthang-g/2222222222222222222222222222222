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


## N07 VERIFIED RESULTS — TỐI ƯU START/STOP LIFECYCLE
- GitHub main parent HEAD 5ac47f041091fff57d0b33826427126738033172 checked first; PLAN.md/STATE.md/PROJECT_STATUS.md read. N01–N06 completed, N07 absent. Frozen ZIP sha256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd (1050 CRC clean) and inner EXE sha256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22.
- ToiuuTab row creates ▶ initial Đã dừng, _toggle_single_acc dispatched via daemon thread; row _state, _stop_event, _gen, _mode_key and PID binding; main-thread UI state marshal.
- EXACT original single-row region contains acc bắt đầu — TODO logic; cannot prove entire per-account start works or is broken. Separate native _apply_single_acc/_send_perf_single/_stop_restore_single exist; requires live test.
- Bulk green Bắt đầu -> _start_all_accs background, _start_all_busy, scan/disabled/Đang quét..., no-account skip, _start_one, bulk stop/restored messages and _all_monitor auto reset. Exact second-click arbitration and partial state UI UNKNOWN.
- Background tab rows can be stale/empty; original _ensure_rows_loaded doc requires worker-only full scan + targeted real-name refresh, immediate false after empty completed scan. _restore_targets doc filters alive accounts with mode OR pre-tool-boot survivor; detailed ordering/eligibility UNKNOWN.
- HWND reuse with different PID invalidates old row; source running records keyed by real character names but cannot override PID guard. Permission with limits persists.
- N05 selection-only gray buttons and Không=skip, N06 TLMP+staged max->low->restore preserved unchanged; N08 watch/ping and N09 prior-session reconcile explicitly separated.
- Prior B11 Tối ưu screenshot has no account rows: no functional transition/parity claimed.
- N07 status STATIC_START_STOP_WORKER_STATE_AND_PID_BOUNDARY_AUDITED_WITH_TODO_UNCERTAINTY / LIVE_PARITY_DEFERRED. 86 evidence records, 22 acceptance checks NOT_RUN.
- New artifacts: docs/toiuu/N07_START_STOP_ORCHESTRATION_FLOW.md, docs/toiuu/N07_MODEL.json, docs/toiuu/N07_STATIC_EVIDENCE.tsv, docs/tasks/N07.md.

## POST-N07 CODE/BUILD CHECK
- No product app source or build/CI workflow exists. Only N07 docs/models and existing STATE/PROJECT_STATUS updated. No original native binary, scripts, N01–N06 or PLAN changed. Build NOT_APPLICABLE_YET/STAGE_S_NOT_STARTED.

## N07 BLOCKERS / DO_NOT_TOUCH
- Exact TODO branch, worker generation/timing, bulk concurrency, GUI start/stop paint on populated rows, native ack and Windows performance parity remain unknown. Preserve all completed components and Proxy development exclusion; do not fake controls or mark live PASS.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md and STATE.md; verify GitHub main for completed N08 before work.
2. Execute N08 — Tối ưu TLMP-5 ping/watch, Treo tick and Login recovery audit from exact frozen EXE. Inspect _start_watch, _tick_watch_loop, _tick_watch_round, _ping_one, _recover_row, WATCH_INTERVAL, WATCH_PING_WAIT, WATCH_MAX_MISS, packaged Perf ping log and Login tab integration.
3. Distinguish source-intended recovery from actual runtime; preserve N05–N07, no DLL/proxy changes.
4. Compare B11 screenshot only after static extraction. Persist N08 report/model/evidence/task; update STATE.md/PROJECT_STATUS.md and recheck build.

## N08 VERIFIED RESULTS — TLMP-5 WATCHDOG, TREO TICK AND LOGIN RECOVERY
- Read PLAN.md, STATE.md, PROJECT_STATUS.md and verified GitHub parent HEAD 87cf332be49e963239611bd2c9be0910316e3ea0; N01–N07 complete, N08 previously absent.
- Original ZIP SHA256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd (1050 entries, CRC clean), inner EXE SHA256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22 and packaged automove_log.txt SHA256 17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500 remained unchanged.
- Original ToiuuTab _start_watch/_tick_watch_loop/_tick_watch_round/_recover_row symbols present; WATCH_INTERVAL, WATCH_PING_WAIT, WATCH_MAX_MISS and WATCH_RECOVER_TIMEOUT exist but exact numeric bindings unproven.
- Exact embedded doc: TLMP-5 ping for running accounts, 2 consecutive misses -> Treo tick/red -> recovery intent. _ping_miss, _recovering, _auto_revive, _watch_running and login_tab_ref present, default/guard semantics not decompiled.
- Watcher matches regex \[pid=(\d+)\] Perf: ping from automove_log.txt using getsize/fstat/st_size/seek/finditer/pongs; exact ordering and log-rotation safety unknown.
- Offline packaged historical log is 15741058 bytes / 387238 newlines, with 4134 Perf: ping lines all matching the watch regex across 88 unique PID labels; no [Toiuu watcher lines. Historical log != current Windows functional test.
- Original _recover_row documents kill hung game -> LoginTab relogin -> reapply eco+start. Actual LoginTab compiled methods _close_single_account and _login_single_account confirmed. If LoginTab is not connected, mapping of PID to login row fails, or relogin waits too long, explicit manual-recovery strings exist. No unconditional kill/relogin success is inferred.
- Potential log-delay/truncation/PID reuse/false hang and concurrent recovery races are required runtime tests, not proven bugs. N08 status STATIC_WATCH_PING_AND_LOGIN_RECOVERY_INTERFACE_AUDITED_WITH_HISTORICAL_PING_LOG / LIVE_PARITY_DEFERRED.
- New artifacts docs/toiuu/N08_WATCH_PING_RECOVERY_FLOW.md, docs/toiuu/N08_MODEL.json, docs/toiuu/N08_STATIC_EVIDENCE.tsv, docs/tasks/N08.md. 82 evidence records, 22 planned Windows/static acceptance tests (all NOT_RUN).

## POST-N08 SOURCE/BUILD CHECK
- Only documentation/models and STATE.md/PROJECT_STATUS.md changed; no source app or GitHub Actions workflow, and original binaries and completed N01–N07 untouched. Product build NOT_APPLICABLE_YET / STAGE_S_NOT_STARTED.

## N08 BLOCKERS / DO_NOT_TOUCH
- Exact watch timeout numbers, log acknowledgment freshness, _auto_revive default, safe PID->Login row mapping, permission/relogin retries and real Windows game results remain UNKNOWN. Preserve all completed work, original EXE and Proxy excluded.

## NEXT_ACTION
On CONTINUE: reread PLAN.md and STATE.md; check GitHub for N09 artifacts before work. Execute **N09 — Tối ưu persisted running-set / tool crash-restart reconciliation and old-game restore/resume audit** using frozen original EXE first: _save_running_set, _load_running_set, _reconcile_stale_running, _reconcile_stale_worker, _resume_running_rows, _game_predates_boot, _restore_targets, toiuu_running/toiuu_was_running and permissions. Distinguish mode selection and watchdog. Compare B11 screenshot only after binary evidence; persist report/model/evidence/task, update STATE.md and PROJECT_STATUS.md, recheck source/build. No previous tasks rewritten.

## N09 VERIFIED RESULTS — TỐI ƯU INTERRUPTED SESSION / RESTART RECOVERY
- Read PLAN.md and STATE.md, verified GitHub main parent HEAD `d3ee4531e324a619444e913dd5ba7987c196085c` and confirmed N01–N08 complete, N09 absent. Reused all completed research without redoing or modifying it.
- Frozen original ZIP SHA256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, 1050 entries and CRC test clean; inner EXE SHA256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`, 47450112 bytes. Examined exact binary static constants and embedded docs; did not execute original EXE/DLL.
- `_save_running_set` persists `{tên: mode_key}` using JSON under `toiuu_running`; `_load_running_set` returns empty set for no interrupted session. `toiuu_was_running` also appears near cleanup/pop but migration semantics unproven.
- `_boot_ts`, `_game_predates_boot` and `psutil.Process.create_time` plus explicit original doc establish critical survivor test: only saved name AND live game started before current tool boot may resume; new game started after tool boot is fresh and must not inherit red state.
- `_reconcile_stale_running/_reconcile_stale_worker`, `_ensure_rows_loaded`, `_check_perm`, `_resume_running_rows`, `_restore_targets`, `_stop_restore_single` and `_reconcile_tries` recovered. A new session already running skips old reconciliation.
- Original logs document keeping old saved intent if no scan completed then retry after 30s, uncertain permission attempts numbered `/5` then retry after 60s, and eventual loss of permission leading to native safe restore of old game, green Bắt đầu, and shortcut sync. These are literal strings, NOT observed runtime scheduling.
- Authorized surviving matching rows get `Đang chạy` and red `Dừng lại` #f44336; `_resume_running_rows` returns count. Other cases (old process gone/new PID) should not inherit running state.
- Distinguish N08 relogin (new game process) from N09 tool restart (old surviving game), and N05 saved combo choices from N09 actual interrupted running intent.
- B11 screenshot has empty account rows; cannot show red resumed screen. N09 status **STATIC_STALE_RUNNING_PERSISTENCE_BOOT_GUARD_AND_PERMISSION_RECONCILE_AUDITED / LIVE_PARITY_DEFERRED**.
- New N09 artifacts `docs/toiuu/N09_STALE_RUNNING_RECONCILE_FLOW.md`, `docs/toiuu/N09_MODEL.json`, `docs/toiuu/N09_STATIC_EVIDENCE.tsv`, `docs/tasks/N09.md`. 84 evidence rows, 22 acceptance cases all NOT_RUN.

## POST-N09 SOURCE/BUILD CHECK
- Original binary/PLAN/N01–N08 unchanged. Only new N09 docs/models and existing STATE.md/PROJECT_STATUS.md updated. Stage-S reconstructed app source and Stage-T build workflow absent; product build NOT_APPLICABLE_YET, not PASS.

## N09 BLOCKERS / DO_NOT_TOUCH
- Legacy `_was_running` semantics, precise retry clock/counter, permission stability, malformed JSON, partial multiple-account name collision, PID timestamp races and native restoration outcome remain UNKNOWN. Do not implement Proxy or license bypass or falsely assert Windows tests.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md and STATE.md and check current GitHub N10 artifacts; skip if already done.
2. Execute **N10 — Tối ưu reconstruction contract and parity-matrix phase handoff** only. Reconcile N01–N09 evidence into stable UI/CPU/GPU/detached monitor/config/TLMP/worker/watchdog/stale-session contracts and an acceptance matrix separated by STATIC, VISUAL, WINDOWS and RESEARCH.
3. Include unknowns and failure paths; mark all unexecuted product tests NOT_RUN. Keep B11 evidence fixed and Proxy excluded.
4. Persist N10 report/model/matrix/task; update STATE.md and PROJECT_STATUS.md; recheck main/source/build state.
5. When N10 is complete, next plan phase is O01 — memory/item subsystem authority audit.

## N10 VERIFIED RESULTS — PHASE N TỐI ƯU RECONSTRUCTION HANDOFF
- GitHub HEAD 7b1a728c7dae4c91b461b217a1cb975ce6eee6c0 verified and PLAN.md / STATE.md read; N01–N09 pre-existed and N10 was absent. Reused nine original static reports, all earlier evidence unchanged.
- Frozen original ZIP SHA256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd (1050 members/CRC proven in prior milestones), inner EXE SHA256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22. Active ToiuuTab and original B11 empty-account screenshot retained as authority.
- N10 consolidated UI/CPU/GPU/detached monitor/config selection/native TLMP/per-account and global worker/ping watchdog/Login recovery/old-tool-session reconciliation.
- Unified parity matrix 152 UNIQUE cases: N01=14, N02=12, N03=8, N04=16, N05=18, N06=18, N07=22, N08=22, N09=22; verification gates STATIC=13, VISUAL=9, WINDOWS=122, RESEARCH=8. ALL results NOT_EXECUTED_STAGE_S_NOT_STARTED.
- Cross-component invariants: gray modes assign combobox only, Không is skip, TLMP mode4 restore/5 ping distinct, live HWND/PID guard, real-name config vs running set, fresh log ping health, old game predates new tool boot, no authorization bypass.
- Known original uncertainties preserved: CPU 1s/750, GPU fallback/multi-GPU, detached geometry, config collisions, native ACK, N07 TODO, N08 ping/log/rel-login races, N09 stale-session clock/retry/collision.
- New docs/toiuu/N10_RECONSTRUCTION_CONTRACT.md, docs/toiuu/N10_MODEL.json, docs/toiuu/N10_TOIUU_PARITY_MATRIX.tsv, docs/tasks/N10.md; this STATE.md and PROJECT_STATUS.md appended.
- **N10 STATUS PHASE_N_STATIC_RESEARCH_HANDOFF_COMPLETE / LIVE_PARITY_DEFERRED.** Research handoff is NOT implementation or a Windows PASS.

## POST-N10 SOURCE/BUILD CHECK
- Repo continues with forensic helper scripts but no reconstructed Stage-S app source, no Stage-T build workflow, no new Windows test. Original binary, PLAN, completed N01–N09 and Proxy exclusion untouched.

## NEXT_ACTION
On CONTINUE: read PLAN.md and STATE.md, check GitHub for O01 artifacts first; execute **O01 — memory/item subsystem authority audit** from original frozen EXE. Inspect memory_reader, memory_items, bag_filter, item_meta_data and weapon_ids + active UI/module wiring before inferring features. Do not rework N tasks or develop Proxy. Save O01 model/evidence/task, update state and recheck build.

## O01 VERIFIED RESULTS — MEMORY/ITEM MODULE AUTHORITY AND CROSS-TAB WIRING
- Read PLAN.md, STATE.md, PROJECT_STATUS.md and verified GitHub main parent `d45a0efb4c781f73e7f465e39dc98425fcda8b40`; Stage N01–N10 complete, O01 absent. No previous work repeated or modified.
- Frozen `TLMTool_2.1.2(9).zip` SHA256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd (1050 entries CRC clean), original inner TLMTool.exe SHA256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22 (47450112 bytes) statically scanned read-only, no EXE/game run.
- Five exact serialized module headers: memory_reader 0x2b7575a (11804 bytes/494 const), memory_items 0x2b69c5f (47850/895), bag_filter 0x28d5db3 (5162/145), item_meta_data 0x2977206 (1989514/7), weapon_ids 0x2c54798 (27719/11). The constants count is NOT item entry count.
- memory_reader uses process_iter, OpenProcess, GameAssembly/UnityPlayer enumeration, ReadProcessMemory, VirtualQueryEx, cache TTL/invalidation; STORE/CHAIN/ROLE/ITEMPACK offsets present but exact numeric values O02 unknown. Writing helpers also exist but O01 does NOT write memory.
- memory_items imports Reader, embedded item_meta_data.META and weapon_ids.is_weapon; read_bag rows {dbID,itemID,site,pos,qty}, get_bag Site10 enrich; action packet 100005 with use/drop/destroy commands statically present. No packets sent.
- bag_filter imports memory_items and defines opt-in presets/rules, dry-run, stop_check/progress. Original docs: empty rules/preset = no discard/no scan/no packet; weapons protected by default except explicit opt-in; protect_ids/protect_names priority. Drop packet 4:dbID may remove complete stack, so never silently invoke.
- Direct bag_filter references from farm_tab, phoban_tab, daily_tab, donvang_tab, debug_tab and train_lsv_tab; this proves compiled wiring, not actual runtime success. Farm UI references Radio Nhặt đồ -> bag_filter preset selection.
- item_meta_data is embedded catalog (META[id]=(Name,Icon,Source,EquipType)), weapon_ids classified by integer ItemID. Original ZIP lacks matching separate metadata CSV/XML but embedded data exists; cannot conclude metadata empty.
- O01 status **STATIC_MEMORY_ITEM_MODULE_AUTHORITY_AND_CROSS_TAB_WIRING_AUDITED / DEEP_LAYOUT_AND_LIVE_PARITY_DEFERRED**. 77 evidence items, 15 future acceptance checks, Windows live NOT_RUN.
- Created docs/memory/O01_MODULE_AUTHORITY_AND_WIRING.md; O01_MODEL.json; O01_STATIC_EVIDENCE.tsv; docs/tasks/O01.md.

## POST-O01 SOURCE/BUILD CHECK
- Source application/CI workflow still absent; no Stage-S reconstruction or Stage-T EXE build. Only O01 docs+STATE.md+PROJECT_STATUS.md updated; all Stage N and PLAN intact.

## O01 BLOCKERS / DO_NOT_TOUCH
- O02 needed for exact process discovery/GA base/RVA pointer validation; O03 for actual bag entries, O04 for embedded META/weapon set, O05 filter rules. Do not use old-game data or infer runtime success from import references. No Proxy development.

## NEXT_ACTION
On CONTINUE: read PLAN.md/STATE.md and check current GitHub for existing O02. Execute **O02 — memory_reader process discovery, OpenProcess rights, GameAssembly/UnityPlayer module enumeration, GA cache, pointer chain/RVA and memory validation/error audit** from frozen original EXE first, read-only. Reuse O01, do not duplicate or rewrite completed stages. Save O02 report/model/evidence/task, update STATE.md/PROJECT_STATUS.md, recheck product source/build.

## O02 VERIFIED RESULTS — MEMORY_READER PROCESS / RVA / CHAIN AUDIT
- GitHub HEAD ccb9def1b1cdd2db2e1e4f95995632bab308fa04 and PLAN.md/STATE.md checked first; O01 complete, O02 previously absent. Frozen original ZIP SHA256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd (1050 entries CRC-clean), original EXE SHA256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22 (47450112 bytes) examined read-only; no process attached.
- Active .memory_reader module at 0x2b7575a, payload start 0x2b7576f (11804 bytes/494 constants); exact original Reader.start/_enum_modules/_r32/_r64/read_all/_resolve_chain/session_block method markers.
- Process discovery psutil.process_iter and name normalization tokens; OpenProcess + rights/elevation probe; EnumProcessModulesEx(LIST_MODULES_ALL) retry fallback and GetModuleBaseNameW GameAssembly.dll/UnityPlayer identification. Exact process predicate, rights bitmask and retry counts not source-decompiled.
- VirtualQueryEx distinguishes unmapped/committed/query-fail; ReadProcessMemory 8/32/64 and UTF16 primitives; GA cache lock/TTL, stale rd/unmapped base rescan and garbage RoleName evict. GA_CACHE_TTL numeric UNKNOWN; mount TTL separately documented 30 seconds.
- Original Reader v10 embedded doc **GA+0x355B208 -> +0xB8 -> +0x88 -> RoleData**. Generic _resolve_chain: deref chain[:-1], returns object before last offset, 0 if broken. AutoFlag paths GA+0x356ED08 / GA+0x356E288 final +0x2C, use -1 on broken; read_auto_state uses None when invalid.
- Original anchored SessionData: get_RoleData GA+0x6F4030; SessionData.RoleData @0x88 must equal live rd, then dict offsets Monsters@0x20 NPCs@0x50 ItemPacks@0x18. Getter first RIP relative match can be wrong; validation required. All RVAs are specific to original compiled/game version, not live proof.
- Reader also exposes WriteProcessMemory and injection/AutoPath helpers but O02 does NOT run/use them; Proxy development excluded. Bag Site10 schema deferred O03.
- O02 status STATIC_MEMORY_READER_PROCESS_GA_RVA_CHAIN_AND_VALIDATION_AUDITED / WINDOWS_PARITY_DEFERRED. 104 evidence rows, 20 acceptance cases all NOT_RUN on reconstructed app.
- Files: docs/memory/O02_READER_PROCESS_POINTER_FLOW.md; O02_MODEL.json; O02_STATIC_EVIDENCE.tsv; docs/tasks/O02.md.

## POST-O02 SOURCE/BUILD CHECK
- No Stage-S product app source and no Stage-T workflow; build NOT_APPLICABLE. Prior O01, N01–N10, PLAN, original ZIP/EXE unchanged.

## O02 BLOCKERS / DO_NOT_TOUCH
- PID matching criteria, PROCESS_RIGHTS bitmask, module enumerate exact retry/timing, GA_CACHE_TTL, unknown assignments and Windows/RPM outcomes require further proof. No read failure may be silently converted to empty bag; no unsafe game writes; no Proxy.

## NEXT_ACTION
On CONTINUE read PLAN.md and STATE.md, verify GitHub for O03 first. Execute **O03 — original memory_items bag Site10 schema, read_bag/get_bag, RoleData/SessionData dictionary and error/race analysis**, distinct from Site200 trade. Do original EXE static analysis first; preserve O01/O02 and Stage-N; document O03 model/evidence/task, update state, recheck source/build.

## O03 VERIFIED RESULTS — MEMORY_ITEMS BAG SITE10 / TRADE SITE200
- GitHub main HEAD 98678985ca5c857e3dc57d98c5dee34232b2983f checked with PLAN.md/STATE.md and O01/O02; O03 not previously present. Frozen ZIP c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd (1050 entries CRC-clean prior) and inner EXE 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22 (47450112 bytes) directly inspected without execution.
- Original memory_items block (0x2b69c5f, 47850 bytes/895 constants) imports memory_reader.Reader, caches Reader by HWND/PID. `get_reader` returns attached Reader or None; a missing Reader does not imply empty bag.
- `read_bag` embedded return doc `(rows, info)` and rows `{dbID,itemID,site,pos,qty}`. Exact diagnostics `Reader chua attach`, `Items null (nhan vat chua load?)`, `Tui rong (count=0)` establish distinct failure/unloaded/empty states. Live dictionary pointer reads not run.
- `_r64`, `rd`, tagged `0xC8`, `_r32`, entries, KNOWN_SITES, candidate 0x18/0x20 and caps found; O02 original doc separately corroborates RoleData.Items (rd+0xC8). Exact C-level entry stride/count/array offsets NOT source reconstructed; do not guess from serialized-order neighbors.
- `get_bag` exact doc is Site 10 metadata-enriched dict or None. Surface fields `name, icon, src, type, etype, slots, distinct, total_qty, non_bag, info`; sort and aggregate formulas remain unknown. `pos` is container position, not screen click coordinates; `dbID` is instance identity vs ItemID template.
- Separate `get_trade_items` uses `Game.GetItemsAtSite` via Lua Site 200 with rows `{dbID,itemID,qty}`, `[]` empty and `None` read error; `count_trade_items` returns -1 on error. `put_item_trade` True means command sent, not success; follow-up trade query required.
- `get_bag_items_by_type` is different Lua Site10 path via Game.GetItemType independent of local embedded metadata; `Game.GetFreeBagSpace()` is its own query, not computed blindly from summary `slots`.
- Item packet 100005 drop(4), destroy(9), use(3) exists but is out of this task. NO game process attach, action, trade, packet or unsafe item loss performed. O01 bag_filter default no-drop and weapon protection preserved.
- O03 status **STATIC_BAG_SITE10_SCHEMA_AND_TRADE_SITE200_BOUNDARY_AUDITED / LIVE_MEMORY_PARITY_DEFERRED**. 73 static/evidence/unknown rows, 20 planned acceptance cases NOT_RUN.
- New docs/memory/O03_BAG_TRADE_READ_FLOW.md; O03_MODEL.json; O03_STATIC_EVIDENCE.tsv; docs/tasks/O03.md.

## POST-O03 SOURCE/BUILD CHECK
- No Stage-S reconstructed app code, no Stage-T GitHub build workflow. Original frozen source artifacts/Stage N/O01/O02/PLAN unchanged; build NOT_APPLICABLE.

## O03 BLOCKERS / DO_NOT_TOUCH
- Dictionary memory offsets/caps, pointer race, read_bag exception shapes, result aggregate arithmetic and actual Windows accuracy require deeper proof. O04 owns embedded ItemID/weapon metadata; O05 owns filter/discard safety. No Proxy development.

## NEXT_ACTION
On CONTINUE reread PLAN.md and STATE.md and verify GitHub for O04 first. Execute **O04 — item_meta_data.META / weapon_ids embedded record, ItemID coverage, source fallback, weapon classification and schema validation audit** (original EXE first, do not invent data counts). Persist O04 docs/model/evidence/task, update STATE.md/PROJECT_STATUS.md, recheck product source/build. Preserve O01–O03 and all N stages.


## O04 VERIFIED RESULTS — COMPLETE EMBEDDED META/WEAPON DECODE
- GitHub main parent 38e7629d9110c73aa237c13b9a45bc372b4d626d, PLAN.md/STATE.md verified before O04; previous O01–O03 and Phase N complete and left unchanged. Frozen ZIP SHA c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd CRC clean and inner EXE SHA 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22 read-only.
- Full 29983-entry META D map decoded from 0x29772d3: 29983 unique numeric-text keys, 29983 T4 Name/Icon/Source/EquipType tuples through aMETA 0x2b5cd71. Sources {"Equips":22776,"Items":5289,"Gems":1154,"Medicines":694,"PetEquips":70}; 12835 distinct names, 4082 distinct icons and 7207 None types.
- Full WEAPON_TYPES 0,1,2,3,4,5,6,7,8,16,17,100 and 5477 unique ID set S at 0x2c548b8 decoded through ais_weapon 0x2c5b3b4; all 5477 in META Source Equips with allowed type, all eligible META in weapon set; zero mismatch, 17299 other Equips.
- Actual runtime string-key/int normalization, unknown ID/fallback and newer game coverage UNKNOWN. O01 protection no-weapon-default/no-rule-discard preserved; no item/game actions executed.
- O04 research status EMBEDDED_META_AND_WEAPON_DATA_FULLY_DECODED_STATIC_AUDIT / LIVE_CLASSIFIER_AND_BAG_PARITY_DEFERRED; 47 evidence records, 20 future test cases NOT_RUN on rebuilt app.
- Created docs/memory/O04_EMBEDDED_METADATA_AND_WEAPONS.md, O04_MODEL.json, O04_DATA_METRICS.json, O04_STATIC_EVIDENCE.tsv and docs/tasks/O04.md. No Stage-S product source or Stage-T Actions workflow, build NOT_APPLICABLE. No Proxy development.

## NEXT_ACTION
On CONTINUE read PLAN.md/STATE.md and inspect GitHub for O05; execute O05 original bag_filter activity presets, rule matching, protect_ids/protect_names and allow_weapons, dry_run, stop_check and discard safety; EXE first, no game item action. Persist O05 docs and update STATE/PROJECT_STATUS. Preserve all prior work.


## O05 VERIFIED RESULTS — BAG_FILTER PRESETS AND DESTRUCTIVE-ITEM SAFETY
- GitHub HEAD 76a1d9a47830ccbde501b2e41302eaf0cab01e38 verified with PLAN.md/STATE.md; O01–O04 completed, O05 absent. Frozen ZIP SHA c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd CRC clean and inner EXE SHA 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22 read-only; no game or packet.
- bag_filter original 0x28d5db3: empty rules -> no scan/no packet; field AND / rule OR, default Site10, dbID dedupe, weapon protection default allow_weapons False, match_weapons opt-in, protect_ids/names highest priority by doc. plan_discard returns preview; discard_items has dry_run, counters, stop_check, on_progress, delay, _send_lock_for(hwnd). Packet 100005 4:dbID may discard whole stack; GUI confirm delegated and NOT proven on all callers.
- Full decoded P204 PHOBAN_DISCARD_ITEM_IDS are O04 Source Items; P10 PHOBAN_DISCARD_MED_IDS are Source Medicines; 214 distinct template IDs, no weapon overlaps. Keep mode none=[discard_weapons,discard_nonweapon], weapons=[discard_nonweapon], all=[], default all. **Keep none is NOT empty-rules** and can discard.
- Original Farm, Donvang, Phoban, Daily, TrainLSV and Debug callers verified by compiled imports/docs, not Windows runtime. Phoban parallel accounts sequential presets/busy skip; TrainLSV only when full; Debug read-only.
- O05 = STATIC_BAG_FILTER_RULE_PRESET_AND_DESTRUCTIVE_SAFETY_AUDITED / LIVE_DISCARD_PARITY_DEFERRED; 61 evidence records, 27 future tests NOT_RUN. Created docs/memory/O05_BAG_FILTER_SAFETY_FLOW.md, O05_MODEL.json, O05_STATIC_EVIDENCE.tsv, docs/tasks/O05.md. O01–O04/N01–N10/PLAN unchanged.

## PHASE O RESEARCH HANDOFF / BUILD
O01 module authority, O02 Reader, O03 bag/trade, O04 metadata/weapons, O05 filter all statically analyzed. Stage-S product app/Stage-T Actions build absent, live parity NOT_RUN. No Proxy development.

## NEXT_ACTION
On CONTINUE read PLAN.md/STATE.md and GitHub, check for P01. Execute **P01 — emulator subsystem original authority and active vs dormant module audit**: emu_input, emu_reader, emu_remote, emu_setup, emu_chat, emu_farm_tab, debug_android_tab. No invented dormant UI. Save P01 docs/model/evidence/task, update states and build status; Proxy Phase Q excluded.

## AUDIT 2026-10-08 — CURRENT REPOSITORY CODE/BUILD
- User requested full actual-code audit before continuing. GitHub baseline `00f95aea9acf1c24f4dcae710fc229ce5cc20004`, 756 tree entries/173 task files A01–O05: reviewed seven D01–D07 Python forensic scripts + A08 shell and source tree. No rebuilt TLMTool application source/entrypoint/packager/Windows workflow. This is **BUILD_BLOCKED_SOURCE_MISSING**, not a compiler failure and not build PASS.
- A08 SHA256/ZIP CRC/inventory PASS on frozen original, inner EXE hash verified. Local standalone O04 Python verifier py_compile and run PASS (29983 META +5477 weapons). Confirmed O04 verifier was missing from GitHub and added EXACT existing read-only source in commit `fe23b809d55641351fa7dcd69a70e0b767b47799`, with no rewrite of O04 or earlier docs.
- Other seven Python scripts statically reviewed, but not individually py_compiled or executed from GitHub source in this audit: do not mark PASS. emu_client.js node --check PASS; ld_remote.js AutoX XML layout is not Node-compatible, not an established runtime bug.
- Audit file docs/audit/CODE_BUILD_BASELINE_2026-10-08.md lists completed/research, missing source/build, actual blockers, unproven runtime risks. Original ZIP/EXE, N/O docs, PLAN and Proxy lock unchanged.

## P01 VERIFIED RESULTS — ORIGINAL EMULATOR MODULES AND CONDITIONAL UI
- Parent HEAD fe23b809d55641351fa7dcd69a70e0b767b47799 used; original compiled 7 modules: emu_chat 0x293100c, emu_farm_tab 0x2932983, emu_input 0x293325f, emu_reader 0x29361cc, emu_remote 0x2938352, emu_setup 0x293942e, debug_android_tab 0x290df6c. Static EXE/module references verified.
- `TLMMainApp.create_tabs` registers Train LD via EmuFarmTab but hidden initially, emu_tab permission; DebugAndroidTab dev-only. Neither is permanently dormant in original UI registration, neither proved fully functioning in Windows/LD test.
- Support: ADB input, AndroidReader/EmuManager Frida RPC, EmuChat coords, optional setup and emulator remote. /emu_farm_toggle original doc says future ACK only; no HTTP listener started or network/runtime logic developed. RPC/JS original assets hash-verified.
- P01 status STATIC_EMULATOR_MODULE_AUTHORITY_AND_CONDITIONAL_UI_AUDITED / LIVE_EMULATOR_PARITY_DEFERRED. 33 static evidence records and 18 planned acceptance cases all NOT_RUN. docs/emulator/P01_AUTHORITY_AND_DORMANCY.md, P01_MODEL.json, P01_STATIC_EVIDENCE.tsv, docs/tasks/P01.md created.

## NEXT_ACTION
On CONTINUE read PLAN.md/STATE.md and main GitHub; verify P02 not completed. Execute P02 — original AndroidReader/EmuManager ADB/Frida data flow, device identity/cache/connect lifecycle and error semantics, original EXE+JS first. Preserve permissions/hidden/dev UI and Proxy no-development scope. Publish P02 docs/model/evidence/task, append STATE.md/PROJECT_STATUS.md. Recheck Stage-S source/build; do not claim EXE can build until source and workflow exist.


## P02 VERIFIED RESULTS — ANDROIDREADER / EMUMANAGER ADB+FRIDA IDENTITY/LIFECYCLE
- Continued from P01 after rereading PLAN.md/STATE.md/PROJECT_STATUS.md. Checked GitHub: docs/tasks/P02.md was absent before this milestone. Earlier gates and Proxy exclusion untouched.
- Current uploaded TLMTool_2.1.2(10).zip SHA256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd, 1050 entries CRC PASS; original frozen inner EXE 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22 (47,450,112 bytes) and original emu_client.js 384ccee9a2ddf236db377fca3abd36cbc17df81a94a286551a749a3132d02db1 matched previous Gate A/P01.
- Read ORIGINAL compiled AndroidReader/EmuManager constants/methods around 0x29333d9e..0x29361a6 (module terminator 0x29361cc), not merely the UI screenshots. ADB discovery; per-VM frida-server ensure/start; device attach, script ping/reload; target RoleID scan or blind shape scan; pick_validated rejecting stale character names; per-serial background poll/force discovery. Static documentation does NOT reconstruct exact Python branch/order.
- EmuManager identity: serial current transport; aid Android ID used as UI key and cached approx 5min; guest IP can disambiguate LDPlayer clones sharing Android ID/hwid; serial reverse mapping must be unique. UI-key-by-aid clone collision remains unproven. Per-device preset cache 30s, worker retry cadence UNKNOWN.
- Shipped Frida JS has 7 exports ping/setBase/readAll/validate/scanRoleId/scanShape/bagSlots; static syntax check PASS, live Frida NOT_RUN. RoleID+readable name candidate validation, bag Site10 occupied slot counting, read error None vs possible 0 ambiguity documented. No game/ADB/Frida/HTTP/remote action run.
- P02 status **STATIC_ADB_FRIDA_IDENTITY_CONNECTION_LIFECYCLE_AUDITED / LIVE_EMULATOR_PARITY_DEFERRED**. Evidence 42 rows; 25 future acceptance tests enumerated, all runtime NOT_RUN.
- Files created docs/emulator/P02_READER_MANAGER_CONNECTION_LIFECYCLE.md, docs/emulator/P02_MODEL.json, docs/emulator/P02_STATIC_EVIDENCE.tsv and docs/tasks/P02.md. STATE.md/PROJECT_STATUS.md updated as checkpoint.
- Existing earlier code/build audit remains true: Gate S application source absent, Gate T Windows build workflow absent, so product EXE cannot yet be built; **BUILD_BLOCKED_SOURCE_MISSING**. This is not a successful product build and not an encountered compiler error.

## P02 BLOCKERS / SCOPE
- Windows LDPlayer/ADB/Frida and current APK real-world validation not available; runtime timing, colliding aid row identity, session cleanup, Root/ACL, exact retries and live bag counts remain UNKNOWN. Preserve original conditional Train LD + developer-only Debug Android. Do not write Proxy functionality. Do not rewrite previously completed studies.

## NEXT_ACTION
On CONTINUE reread PLAN.md/STATE.md, check GitHub docs/tasks/P03.md first. Execute **P03 — original emu_input ADB tap/swipe/keyevent/screencap and capture/coordinate/timeout/error contract static audit**. Inspect original EXE and shipped scripts FIRST; do not invent emulator UI from screenshots or mark runtime PASS. Publish P03 evidence/model/task, append STATE.md/PROJECT_STATUS.md and recheck Stage-S app source/Stage-T Windows build status.


## P03 VERIFIED RESULTS — ORIGINAL EMU_INPUT ADB / CAPTURE / COORDINATE CONTRACT
- Continued from current NEXT_ACTION after reading PLAN.md, STATE.md, PROJECT_STATUS.md, P01/P02 and D07 source-oriented reports. GitHub docs/tasks/P03.md did not exist before task; no previous completed task was repeated or rewritten.
- Original user ZIP `TLMTool_2.1.2(10).zip`: SHA256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd; 1050 entries, ZIP CRC PASS. Original inner TLMTool.dist/TLMTool.exe SHA256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22, 47450112 bytes. No original binary executed/modified.
- Compiled `emu_input` marker 0x293325f. Static method names `AdbInput.__init__/_run/tap/swipe/key/text/size/screencap/save_cap/from_pc` and ADB subprocess, `CREATE_NO_WINDOW`, `check_output`, timeout, UTF8 errors ignore, keycode/doc, `wm size`, `exec-out screencap -p`, PIL/BytesIO/RGB and capture `None` error contract recovered at 0x2932e35..0x293325f. Exact Python source/exception ordering/timing not recovered.
- Input operates on actual device pixels (LD example 960x540). `from_pc` has reference PC 1366x768 illustrative x*.7027/y*.7031 based on real wm size. Separate `DebugAndroidTab` Windows `GetCursorPos`+`ScreenToClient`, LDPlayer-only viewport coordinate conversion and default (0,30) origin documented. Do not unify these coordinate domains or hardcode sample scaling.
- Original ZIP does not package adb.exe; EXE references external `D:\\LDPlayer\\LDPlayer9\\adb.exe` plus `LD_ADB` symbol, exact fallback/precedence UNKNOWN. P02 ADB serial/cloned VM identity guards remain essential. Compiled DebugAndroidTab _do_cap/_do_tap/_do_rgb and EmuChat AdbInput wiring statically recorded.
- P03 status **STATIC_EMU_INPUT_ADB_AND_VIEWPORT_CONTRACT_AUDITED / LIVE_INPUT_PARITY_DEFERRED**: 49 exact provenance/evidence rows, 26 acceptance cases enumerated, 0 live runtime cases run. Static original ZIP/hash/CRC and symbols PASS; NO emulator input, ADB, Frida, network, capture execution.
- Files CREATED: docs/emulator/P03_INPUT_CAPTURE_COORDINATES.md, docs/emulator/P03_MODEL.json, docs/emulator/P03_STATIC_EVIDENCE.tsv, docs/tasks/P03.md. STATE.md and PROJECT_STATUS.md checkpoint append only. PLAN.md and earlier P02/P01/N/O/A–D/Gate B original untouched.
- Stage-S application source and Stage-T Windows EXE workflow still absent per current code/build audit; no app built. Status **BUILD_BLOCKED_SOURCE_MISSING** is not a compiler failure or PASS.

## P03 BLOCKERS / DO_NOT_TOUCH
- Real ADB executable availability, exact CLI args/timeout/retries, Unicode input, screenshot/PIL error cases, rotation, dynamic viewport rounding, DPI and multi-VM live targeting remain UNVERIFIED. `Train LD` stays entitlement-gated, `Debug Android` dev-only. Proxy Phase Q development forbidden.

## NEXT_ACTION
On CONTINUE read PLAN.md and STATE.md and confirm GitHub has not already completed P04. Execute **P04 — original `emu_chat` pure-UI chat-link navigation, [EmuChat] coordinate calibration, memory-backed map/tile destination verification and failure/recovery analysis** from original compiled EXE plus shipped JS first. Do not invent UI or replay completed P03. Create P04 report/model/evidence/task, update STATE.md/PROJECT_STATUS.md, recheck source/build and avoid Proxy.


## P04 VERIFIED RESULTS — ORIGINAL EMU_CHAT CHAT-LINK GOTO AND MEMORY VERIFICATION
- Read current PLAN.md/STATE.md/PROJECT_STATUS.md, confirmed GitHub docs/tasks/P04.md absent before execution, then used original archived EXE and shipped emu_client.js read-only. ZIP SHA256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd (1050 entries CRC PASS), EXE SHA256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22 (47,450,112 bytes), Frida JS SHA256 384ccee9a2ddf236db377fca3abd36cbc17df81a94a286551a749a3132d02db1 match prior frozen originals.
- Compiled `emu_chat` module marker 0x293100c with serialized constants at 0x2930abd–0x293100b: original `goto` described pure UI chat-link `@GOTO_m_x_y` in TILE coordinates, steps open/focus/clear/type/dismiss keyboard/send/tap newly sent own link, verify movement/map change via EmuManager `poll_rows` MapID PosX PosY.
- Original embedded docs say already within <=2 tiles => success without spamming chat; return (ok,msg), stuck 30s => failure, timeout/tap error outcomes. Exact default global timeout, arrival distance metric, stuck clock reset, retry/cancel/sleep order and Python source control-flow remain UNKNOWN. Not a successful live movement test.
- `settings.ini [EmuChat]` calibration: chat_open_x/y, input_x/y, kb_ok_x/y, send_x/y, link_x/y; original DebugAndroidTab `_save_cfg` and step-wise goto workbench support. Numeric default positions and global vs per-device storage details unproven; do not guess from screenshots.
- Distinct coordinate units: chat-link input is tile coordinates; shipped Frida JS `readAll` has raw PosX/PosY and X_UI=PosX>>5, Y_UI=PosY>>5. Actual EmuChat conversion between raw/shifted/tile units NOT recovered. Do not silently compare incompatible units.
- Real compiled `emu_farm_tab` references `emu_chat.goto` (0x2932300..0x2932312) and docs say goto+memory verify, [EmuCoords:serial] presets, android_id keyed rows and [EmuFarm]/[TrainLD] fallback; critically original source text `farm cycle: phase sau` at 0x29320a3 indicates the main farm loop was deferred/partial, not a proven complete original feature.
- P04 status **STATIC_EMU_CHAT_GOTO_COORDINATE_AND_MEMORY_VERIFICATION_AUDITED / LIVE_PARITY_DEFERRED**. Created docs/emulator/P04_EMU_CHAT_GOTO_CONTRACT.md, P04_MODEL.json, P04_STATIC_EVIDENCE.tsv (46 static records), docs/tasks/P04.md; 26 runtime acceptance cases listed, all NOT_RUN. No Windows/LD/game/ADB/Frida/proxy action executed.
- Existing complete static research and original ZIP unchanged. Gate-S app source and Gate-T Windows build workflow still absent according to repo audit; only docs/checkpoints introduced: **BUILD_BLOCKED_SOURCE_MISSING**, NOT a compiler PASS/FAIL.

## P04 BLOCKERS / SCOPE LOCK
- Exact chat-text keyboard clearing/tapping behavior, per-device calibration, moving map IDs/position readiness, stale Frida readings, collision between android_ids, 30s stuck timing and overall timeout require Windows/game runtime. Train LD permission emu_tab/Debug Android dev-only unchanged. Proxy Phase Q not developed.

## NEXT_ACTION
On CONTINUE reread PLAN.md and STATE.md, check GitHub for existing P05 artifacts; execute **P05 — original emu_farm_tab Train LD UI and per-device account/preset management, permissions, button/worker wiring, actual implemented versus 'farm cycle: phase sau' stub/ACK**. First analyze original compiled EXE and packaged JS, preserve previous stages and avoid Proxy. Save P05 model/evidence/task, update STATE.md/PROJECT_STATUS.md and recheck Stage-S source/Stage-T build.


## P05 VERIFIED RESULTS — ORIGINAL TRAIN LD PARTIAL FARM TAB / GUEST ACK LIMITS
- Read PLAN.md/STATE.md/PROJECT_STATUS.md from current GitHub and verified P05 absent before starting. Original `TLMTool_2.1.2(10).zip` SHA256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd: 1050 entries CRC PASS; inner compiled EXE SHA256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22 (47450112 bytes); shipped AutoX ld_remote.js SHA256 3bd84a2b433ee679b7a049f5aa5cba2e8725d1e09b14d5deb3f42b6bf919edfb. Binary and scripts only read, not executed.
- emu_farm_tab module marker 0x2932983; original module constants 0x293110b..0x2932982 examined. Tk LabelFrame/Canvas/Scrollbar and dynamic 3-line account rows, _start_refresh/_stop_refresh/_schedule_refresh, daemon background _refresh_acc_list worker emu_manager.poll_rows, per-row _add_or_update_row, get_bag_slots, RoleID, CurrentHP, MaxHP, Level, MapID, PosX/PosY, BoundMoney/death/EXP tracking fields recovered. Exact refresh scheduling/stat formulas and true live reading remain unknown.
- Device/account identity original doc: rows keyed by android_id for serial changes after reboot; per-VM coordinates in [EmuCoords:serial]; selected Sell/Train preset according to character name, overlay-edited, fallback accepts legacy map|x|y; [EmuFarm] config with [TrainLD] fallback. Clone android_id/hwid collisions and serial rebind not proven safe.
- Per-row _toggle_this button/btn_play/status/busy and permission_guard.has_permission("emu_tab") statically found. Crucially original `farm cycle: phase sau` at 0x29320a3 means main farm loop not proven complete. _goto_acc has `has_permission_with_limit` with emu_tab and trainld and calls emu_chat.goto. _setup_acc has emu_tab/trainld_setup rights and calls emu_setup.setup_instance. No entitlement bypass or new tab implemented.
- Original class doc explicitly says emulator tab does not port the heavy PC actuator chain: multi-step town, Phù/Ngựa navigation, shop HP/MP, heal combo, F-key buffs and PC coordinate board. Do not invent them.
- Shipped `ld_remote.js` source-level audit: guest `btnGoTrain` runs a hardcoded seven-step UI path to /emu_steps (gap 350 ms); its success label reflects HTTP `r.ok`, NOT observed MapID/PosX/PosY arrival (contrast PC EmuChat memory-verified goto). Guest Train On/Off toggles local `farmOn` on /emu_farm_toggle `r.ok`; original PC endpoint is an ACK-only future-phase stub (P01/D07). GUI On is NOT proof full auto-train started. Guest /emu_act sale/heal is send ACK, not task completion.
- P05 status **STATIC_EMU_FARM_TAB_PARTIAL_UI_PRESETS_AND_PERMISSION_AUDITED / LIVE_TRAIN_PARITY_DEFERRED**. Static verification PASS: exact ZIP/inner EXE/AutoX hashes and CRC, 15 selected compiled offsets, 5 JS tokens. Original byte-string prefixes required corrected static test harness; no product code changed. 81 evidence rows, 30 future live tests NOT_RUN.
- Created docs/emulator/P05_TRAIN_LD_AUTHORITY.md, docs/emulator/P05_MODEL.json, docs/emulator/P05_STATIC_EVIDENCE.tsv, docs/tasks/P05.md; STATE.md and PROJECT_STATUS.md checkpoint. Previous stages/PLAN and original archives unchanged.
- Stage S reconstructed application source and Stage T GitHub Windows build workflow still missing as of prior full code audit plus latest docs-only commits. Product **BUILD_BLOCKED_SOURCE_MISSING**; no Windows EXE built or tested in P05.

## P05 BLOCKERS / SCOPE
- Cannot establish original compiled Python call order, actual farm FSM, worker cancellation, full emulator automation, clone UID safety, preset migration precedence, numeric bag threshold, UI calibration or real success from action ACK without LDPlayer/Windows execution. Keep Train LD gated by emu_tab, Debug Android dev-only, Proxy Phase Q no-development.

## NEXT_ACTION
On CONTINUE reread PLAN.md/STATE.md and verify GitHub P06 absent. Execute **P06 — original emu_setup emulator setup process: ADB APK install, Frida/AutoX resource push, grant/overlay permissions, script deployment, Android app launch, platform/device selection and error/return semantics**. Analyze original compiled EXE and packaged JS first, save P06 evidence/model/task, update STATE.md/PROJECT_STATUS.md, recheck source/build. Do not develop Proxy or repeat P01–P05.


## P06 VERIFIED RESULTS — EMU_SETUP APK / AUTOX JS / ADB PERMISSIONS / MANUAL START
- CONTINUE read PLAN.md/STATE.md/PROJECT_STATUS.md and confirmed docs/tasks/P06.md absent. Inspected original uploaded `TLMTool_2.1.2(10).zip` and inner EXE/ld_remote.js read-only before documentation. Original ZIP SHA256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd (1050 entries, CRC PASS), inner TLMTool.exe SHA256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22 (47450112 bytes), ld_remote.js SHA256 3bd84a2b433ee679b7a049f5aa5cba2e8725d1e09b14d5deb3f42b6bf919edfb matched frozen originals.
- Original emu_setup module marker 0x293942e, serialized constants 0x29387a5..0x293942e. Original setup_instance docs specify ADB-only **NO ROOT** setup for a selected emulator serial in worker/log_cb: resolve ADB; detect installed AutoX or private remote APK; find externally supplied autox*.apk/private remote APK and install if needed; post-install verify package; push ld_remote*.js into AutoX-visible script dirs; pm grant storage, appops SYSTEM_ALERT_WINDOW, monkey open AutoX; then **user must manually Run ld_remote.js once in AutoX**. This manual action is not automated in the original described installer.
- **Confirmable missing package artifact:** current original ZIP has **zero APK files**, so a fresh emulator without AutoX cannot self-install from the frozen package alone; must have a suitable existing package or a separate externally provided APK. Candidate settings [Emu] remote_apk/autox_apk/remote_pkg; exact search precedence unknown.
- PUSH documented: REMOTE_JS_FILES and REMOTE_SCRIPT_DIRS, /sdcard/Scripts one explicit path, ld_remote.js and ld_remote_new.js; mkdir/push and per-location status. _render_pc_base creates a temporary JS copy substituting __PC_BASE__ to http://<pc_lan_ip>:<remote_port>; shipped JS lines 6–8 include placeholder, fallback http://172.16.1.2:8765, token tlm. LAN IP/net interface, network reachability, exact destination list, temp cleanup and partial push aggregation remain unknown.
- Storage permissions READ_EXTERNAL_STORAGE/WRITE_EXTERNAL_STORAGE and overlay appops grant attempted; fallback can require one-time manual permission. monkey app launch is **NOT** proof guest JS/remote listener/game automation has started. This ADB installation path distinct from P02 Frida root runtime.
- **P06 = STATIC_EMU_SETUP_APK_SCRIPT_PERMISSIONS_LAUNCH_AUDITED / LIVE_SETUP_PARITY_DEFERRED**. Actual static tests: original ZIP CRC PASS, exact hashes, 20/20 EXE token+offset checks PASS, 6/6 AutoX JS token checks PASS, 0 bundled APK; 63 evidence rows and 29 future acceptance tests all NOT_RUN. No game, ADB, Frida, app install, overlay, network listener or Proxy executed.
- New docs/emulator/P06_EMU_SETUP_DEPLOYMENT.md, P06_MODEL.json, P06_STATIC_EVIDENCE.tsv and docs/tasks/P06.md. Existing P01–P05 and PLAN unchanged; only STATE.md/PROJECT_STATUS.md appended. Full rebuild app source Stage S and Windows EXE workflow Stage T still absent per latest previous source audit and docs-only subsequent commits: **BUILD_BLOCKED_SOURCE_MISSING**; no product EXE built/tested here.

## P06 BLOCKERS / SCOPE LOCK
- Exact Python branch/timeout/retry/setup success aggregation, APK selection, full script folder list, updated Android permission behavior, multi-NIC LAN IP, UI launch permission, user pressing Run, and actual remote overlay connectivity require Windows/LDPlayer tests. Train LD stays emu_tab-gated, Debug Android dev-only. Proxy development is excluded.

## NEXT_ACTION
On CONTINUE read PLAN.md/STATE.md and check GitHub for existing P07 first. Execute **P07 — emu_remote optional PC HTTP listener: authentication, emulator peer-IP/ADB serial identity, permission gates, GET/POST endpoint actions, ACK-vs-game-success, startup/shutdown/error and security boundaries**; original compiled EXE and bundled ld_remote.js first, read-only. Publish P07 evidence/model/task, update STATE.md/PROJECT_STATUS.md, recheck product source/build; no Proxy development and no invented public tab.


## P07 VERIFIED RESULTS — ORIGINAL EMU_REMOTE HTTP IDENTITY/AUTH/ACK
- Read current PLAN.md, STATE.md, PROJECT_STATUS.md and GitHub task inventory; docs/tasks/P07.md was absent before task. Original ZIP `TLMTool_2.1.2(10).zip` SHA256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd, 1050 entries CRC PASS; frozen inner TLMTool.exe SHA256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22; ld_remote.js raw SHA256 3bd84a2b433ee679b7a049f5aa5cba2e8725d1e09b14d5deb3f42b6bf919edfb. Static read only, no server/game execution.
- Original compiled emu_remote terminator marker 0x2938352 and constants 0x29369f6..0x2938352: ThreadingHTTPServer, optional background listener idempotent start/stop, bind 0.0.0.0, default port 8765, default token tlm, configurable [Emu] remote_port/remote_token, JSON/query token auth method, socket peer-IP and emu_tab permission/account-limit guard methods. Exact GET authorization coverage and source branching UNKNOWN.
- Six GET routes: /ping, /maps, /emu_status, /emu_config, /emu_heal_presets, /emu_coords. Seven POST: /emu_goto, /emu_save_coord, /emu_del_coord, /emu_steps, /emu_act, /emu_farm_toggle, /emu_config. /emu_goto returns accepted for async background movement, not arrived. /emu_steps tap/text/key/wait returns action dispatch, not character state. /emu_farm_toggle remains original ACK-only state recording with disconnected farm engine.
- Original EmuManager serial_for_ip contract prioritizes socket peer IP, must not guess device on ambiguity; guest script AID in this version is its guest IPv4, distinct from Android ID used by some PC-side row keys. Exact fallback/selection via _serial_for_aid remains UNKNOWN.
- **Confirmed shipped JS code-level discrepancy**: ld_remote.js post() sets AID/token, calls http.postJson and returns local {ok:true,body:r.body.string()} on any nonexceptional call, WITHOUT parsing JSON server ok or checking response HTTP status. Guest UI "Train On" toggle or /emu_steps "Di chuyển thành công" therefore can reflect local request non-exception not actual server or game success. AutoX HTTP 4xx/5xx throw behavior not executed/unknown. getp() is different and JSON parses; pingOk checks j.ok.
- P07 status **STATIC_EMU_REMOTE_ENDPOINT_AUTH_IDENTITY_AND_ACK_AUDITED / LIVE_PARITY_DEFERRED**. Static checks PASS: 34/34 original EXE token-offset matches, 10/10 JS source strings, archive SHA/CRC; 72 provenance/evidence records, 33 future runtime acceptance cases all NOT_RUN.
- Created docs/emulator/P07_REMOTE_AUTH_ENDPOINTS.md, P07_MODEL.json, P07_STATIC_EVIDENCE.tsv, docs/tasks/P07.md; checkpoint STATE.md/PROJECT_STATUS.md only. Previous work and frozen binary unchanged. No HTTP listener, ADB, game or Proxy action executed.
- Rebuilt Stage-S product source and Stage-T GitHub Windows workflow still missing according to prior code/build audit; recent commits research/docs only. **BUILD_BLOCKED_SOURCE_MISSING** rather than build success/compiler failure.

## P07 BLOCKERS / DO_NOT_TOUCH
- Actual GET auth coverage, token handling under malformed requests, port reuse/stop races, cloned emulator identity through NAT/reboot, per-endpoint permission calls, HTTP library status semantics and game action completion require runtime or original source. Do not expose gated Train LD or developer-only Debug Android; no Proxy development.

## NEXT_ACTION
On CONTINUE reread PLAN.md, STATE.md and GitHub, verify P08 absent, then execute **P08 — original debug_android_tab developer-only workbench controls, capture/RGB/viewport/Frida/remote callbacks and permission-gated UI integration audit**, original EXE and packaged JS first. Create P08 report/model/evidence/task, update STATE.md/PROJECT_STATUS.md, recheck product source/build. Preserve all verified previous stages and Proxy exclusion.


## P08 VERIFIED RESULTS — DEBUG ANDROID DEV WORKBENCH / PHASE P STATIC HANDOFF
- Checked GitHub PLAN.md, STATE.md, PROJECT_STATUS.md, P01/P03/P04/P07, and verified docs/tasks/P08.md absent before work. Direct read-only original ZIP `TLMTool_2.1.2(10).zip` SHA256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd (1050 entries CRC PASS); inner TLMTool.exe SHA256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22 (47450112 bytes).
- Original compiled `debug_android_tab` marker 0x290df6c; inspected serialized symbols/docs near 0x290bb8c..0x290df6b. Dev-only visibility is explicitly constrained by MainApp/P01; no new public tab. Original UI has selected ADB serial/Refresh, Frida start, force rescan, push script one/all, remote listener toggle, Tap, Screencap/RGB, RoleData and Site10 bag slots, step-wise chat-goto, tracking and logs. Exact working callback names recorded.
- Original Win32 calibration: GetCursorPos, WindowFromPoint, GetAncestor, GetWindowText/LDPlayer title check, ScreenToClient, GetClientRect, client viewport to device pixel conversion. Default viewport top-left (0,30), x2/y2 auto by window; Alt picks upper-left and lower-right corners; mouse listener/middle-button can capture measurement and pin Tap. These use input observation/calibration, while game Android tap is through ADB; no global hidden-mouse claim.
- `[EmuChat]` configuration fields chat_open/input/send/kb_ok/link x,y and goto_map/x/y; sample raw tap/RGB values are not universal. Read settings/write settings/lock, save cfg, original debug capture log and RGB swatch, EmuManager poll_rows/get_bag_slots fields statically audited; live game/memory freshness and UI orientation unverified.
- Original doc explicitly says debug tab does NOT include PC NPC test, fake accounts or plan-limit test. Do not invent these as Android features.
- P08 = **STATIC_DEBUG_ANDROID_DEV_WORKBENCH_AND_COORDINATES_AUDITED / LIVE_PARITY_DEFERRED**. CRC/hash verified, **53/53 selected EXE byte-offset symbol checks PASS** (corrected transient test-harness offsets before final pass). Created docs/emulator/P08_DEBUG_ANDROID_WORKBENCH.md; P08_MODEL.json; P08_STATIC_EVIDENCE.tsv (92 evidence rows); docs/tasks/P08.md. 33 planned Windows/LD live parity cases, all NOT_RUN. No game, listener, Frida, device or product build executed.
- Phase P P01–P08 researched for original static contract; complete does NOT mean an emulator automation implementation or live parity PASS. Earlier original/data/docs and PLAN unchanged; Proxy Phase Q remains excluded.
- Repo rebuilt Stage S application source and Stage T Windows workflow still absent per code/build audit and current research-only changes: **BUILD_BLOCKED_SOURCE_MISSING**. Do not claim new EXE built.

## P08 BLOCKERS / NEXT_ACTION
- Live developer entitlement, Tk event/after teardown, Alt/middle listener behavior, viewport DPI/clipping/resize, capture/RGB, Frida state, bag error vs zero and chat arrival require Windows/LDPlayer runtime. 
- NEXT_ACTION on CONTINUE: reread PLAN.md and STATE.md, check GitHub docs/tasks/R01.md first. Execute **R01 — immutable data/resource provenance and loader/reader-writer GAP audit for .dat/.old/.bak and essential assets**, **reuse** completed Gate A / D06 / D07 manifests (do not repeat prior correct work); identify only missing source-loader relationships, unknowns and Stage S packaging necessities. Do not change files in original ZIP or develop Proxy.


## R01 VERIFIED — IMMUTABLE RESOURCE PROVENANCE MATRIX AND PHASE R HANDOFF
- User CONTINUE resumed from P08 NEXT_ACTION after reading current PLAN.md/STATE.md/PROJECT_STATUS.md; verified docs/tasks/R01.md was absent. Reused A05/A07/A08 and D06/D07/D08 instead of redoing correct earlier research. Original user ZIP TLMTool_2.1.2(10).zip SHA256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd; 1050 ZIP entries/1002 files/48 directories and CRC PASS; inner EXE SHA256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22 (47,450,112 bytes), read-only.
- New docs/resources/R01_RESOURCE_GAP_MATRIX.tsv: **26 resource rows** containing filename, size, SHA256, exact first-16-byte header, magic, reader/loader, writer, runtime usage, confidence, Stage-S packaging guidance and sources. Reused 24 D06 rows plus 2 scripts from D07. Cross-checked new GitHub matrix against A07 ORIGINAL_MANIFEST for **26/26** name/size/SHA PASS, and original D06 for **24/24** PASS; no mismatches.
- Direct frozen inner EXE ASCII+UTF-16LE basename scan: 14 opaque MZ/non-robust-PE .dat and 5 old/backup resources filenames **zero occurrences**; never claim unused from no literal name. Active resources.dat 7 ASCII references; version.dat 2; Default.ppx 1; automove_log.txt 1; proxy_working.txt 10; emu_client.js 2; ld_remote.js 4. Actual reader/writer/runtime semantics for all 14 opaque and 5 old backups remain **UNKNOWN**. Two archived backup variants bak-20260923/old-locked byte-identical.
- A05 outer launcher explicitly sets working directory to TLMTool.dist; D06 dll_injector.get_default_dll_path points to ./data/resources.dat. Preserve runtime CWD/resource layout when rebuilding; original packed DLL/JS never modified/executed. Temporary _render_pc_base patch applies to AutoX script COPY only (P06). Do not conflate config.dat/settings.dat/license.dat with runtime .ini/JSON.
- New docs/resources/R01_DATA_RESOURCE_GAPS.md, R01_MODEL.json, R01_STATIC_EVIDENCE.tsv (18 evidence items), docs/tasks/R01.md and tools/R01_VERIFY_RESOURCE_GAPS.py, all read-only. Local Python py_compile PASS, ZIP-only verifier PASS for 26 files and no 14+5 compiled name references; matrix optional filename argument **NOT_RUN**, separately GitHub A07/D06 joins PASS. No Windows binary, injection, emulator or game run.
- Gate R status **STATIC_RESOURCE_PROVENANCE_MATRIX_COMPLETE_WITH_RUNTIME_UNKNOWNS_PRESERVED**. The 26-file resource matrix does NOT replace A07 all-1002-file dependency manifest for Stage S/T. Stage-S product source and Stage-T Windows workflow still absent in previously audited repository; no new application source was introduced in R01. **BUILD_BLOCKED_SOURCE_MISSING** (not build success/failure).
- Scope unchanged: no Proxy Phase Q development, no prior docs rewritten, no original binary or package member changed.

## R01 BLOCKERS / NEXT_ACTION
- Runtime owners/writers of opaque .dat and old backups, true dynamic path enumeration, active DLL live integration, version.dat exact copy/load lifecycle, automove log writer, guest JS runtime, launch-without-wrapper CWD and all DLL/Tk packaging parity need eventual Windows testing. All unverified are explicit UNKNOWN/NOT_RUN.
- NEXT_ACTION on CONTINUE: **S01 — begin Stage S with a smallest genuine source bootstrap**. Read PLAN.md, STATE.md and original MainApp/UI/launcher contracts and baseline before editing; create only verified app entrypoint/settings shell and accurate tab registration/gating as a small independently testable slice. Never fake active feature functionality, add public dev tabs, change Proxy or claim Windows parity from smoke-only tests. Save source/test artifacts, update STATE.md/PROJECT_STATUS.md; Stage T reproducible Windows EXE build to follow real app source.


## S01 VERIFIED IMPLEMENTATION — FIRST REAL STAGE-S SOURCE BOOTSTRAP
- User CONTINUE resumed from R01 NEXT_ACTION. Read current PLAN.md, STATE.md, PROJECT_STATUS.md, SCOPE_LOCK.md, original A05/B01/B02/E01–E05 MainApp and settings contracts, checked GitHub: no docs/tasks/S01.md, src/TLMTool.py or tests/test_s01.py before creation. Did NOT rewrite earlier completed tasks, PLAN, resource assets or Proxy.
- **First application source actually created and pushed**: src/TLMTool.py (1074 UTF-8 bytes), src/shell.py (7564 bytes), src/settings_store.py (2292 bytes), tests/test_s01.py (5665 bytes). GitHub returned matching post-commit sizes. Source, not forensic-only documents.
- TLMMainApp: real Tk notebook and 15 E03 potential tab registrations; normal 11-tab screenshot is a *permission-granted target state*, NOT the initial unlicensed state. All optional tabs initially hidden; only Info visible. Actual content must be injected as verified factory and is built once; missing constructors stay hidden. Server-verified granted keys are passed in from separate missing auth service; dev tabs need dev authorization; version/plan block and lost tab fall back to Info; selected refresh stop/start/shutdown represented by methods, no fake functional controls.
- Tk defaults anchored E02: TLMTool title, initial 250x20 withdrawal, topmost, Segoe UI 9, notebook margin 5, top-right geometry formula a HIGH-CONFIDENCE reconstructed arithmetic (not source-proof), NOT Windows-screenshot parity. User-requested corrected visible tab spelling **Dồn** (not “Đồn”) applied to shell + regression test.
- settings.ini REAL minimal service: %APPDATA%/TLMTool/settings.ini, RawConfigParser(strict=False) duplicate key last-wins, UTF8, synchronized reads/writes, same-directory mkstemp/flush/fsync/os.replace and dated settings.YYYYMMDD.ini backup before existing-file replacement. Unknown original backup retention count and control-character sanitization scope not invented; no backup pruning. This does not implement central config.ini or feature-specific defaults.
- src/TLMTool.py entrypoint exists but **deliberately exits code 2 with explicit blocker** until genuine TLMInfoTab/server-license/heartbeat module is reconstructed. No blank/dummy Info tab or action buttons are presented; therefore NO functional UI/startup PASS claim.
- **LOCAL TESTS PASS:** python -m compileall -q src tests and python -m unittest discover -s tests -v **7/7** after GitHub-applied spelling + backup updates; production entrypoint verified exit=2; all four GitHub file byte sizes match tested local files (1074, 7564, 2292, 5665). Tests use headless fake Tk adapters, NOT real Windows Tk/LDPlayer or GUI raster.
- Added docs/source/S01_BOOTSTRAP.md, docs/source/S01_MODEL.json, docs/tasks/S01.md; STATE.md and PROJECT_STATUS.md append-only checkpoint; previous A–R and frozen ZIP unchanged. No Phase Q Proxy development.
- **BUILD BLOCKER UPDATED:** Previous BUILD_BLOCKED_SOURCE_MISSING should NOT remain a current-state description. Real rebuilt source NOW EXISTS but is PARTIAL, has no InfoTab/server authorization, no real game-tab modules, no Stage-T Windows/Nuitka workflow; no compiled Windows EXE and no functional or visual parity. Use **SOURCE_PARTIAL_APP_STARTUP_BLOCKED_INFO_AUTH_AND_WINDOWS_BUILD_WORKFLOW_MISSING**, not successful build.

## S01 BLOCKERS / NEXT_ACTION
- Real InfoTab/permission_guard/heartbeat, single-instance mutex, splash, logger, CPU monitor, tab controllers, exact widget timing/layout, account limits, finished backup-retention semantics and Windows standalone packaging absent. No original Windows GUI/game runtime tests executed.
- NEXT_ACTION on CONTINUE: reread PLAN.md/STATE.md, GitHub src/TLMTool.py/shell.py/settings_store.py, and original Info/permission_guard evidence (E01/E04/E05 and Info-tab tasks). Execute **S02 — first genuine Info startup/permission state slice with fail-closed authorization and unit tests**; do not fabricate server endpoints, invoke unknown license services, auto-grant feature permission, alter proxy, or display fake tabs. After source/tests, update STATE.md/PROJECT_STATUS.md and identify Stage-T prerequisites. Do not recreate S01.


## S02 VERIFIED IMPLEMENTATION — INFO AUTHORIZATION STATE / CLIENT DATA ROUTER SEPARATION
- CONTINUE from S01 NEXT_ACTION after fresh PLAN.md, STATE.md, PROJECT_STATUS.md, SCOPE_LOCK.md, original S01 source/tests and E01/E04/E05/E07/E08/B12. GitHub docs/tasks/S02.md absent before implementation. Original compiled EXE consulted read-only, SHA256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22, markers <module permission_guard> at 0x2b84c35, <module info_tab> at 0x2975ca9. Original static contract includes token validation/signature, startup RPC, heartbeat, plan-tabs, server max windows and dev/version/plan status. Python source AST and real server token verification NOT recovered.
- User authorized fallback lookups in separate GitHub game-client DATA repo `ngmthang-g/clinent-game-than-long-DATA-2222`. Read its README.md, AI_BOOTSTRAP.md, AI_ROUTER.md read-only. It is for client Lua/game state, not TLM license/auth server; did NOT infer entitlement, signed token or server endpoints from client KB, did NOT edit DATA.
- Real new source: `src/permission_guard.py` implements immutable VerifiedClaims/PermissionSnapshot, deny by default for features, callback-only verified-token handoff, malformed/raw JSON/boolean/dict rejection, dev-only gating, ban/version/server/expiry handling, and server-claim max_windows gate without guessing from plan name. **NO ACTUAL CRYPTOGRAPHIC VERIFIER** is shipped: test-only verifier in tests/test_s02.py is not production auth and cannot be used to grant real access. Original default FREE permissions/heartbeat-grace branch exists but exact policy UNKNOWN; S02 conservative no-unverified-feature/clear-on-error is not full parity.
- New `src/info_state.py`: TLMInfo state handoff, current-version 2.1.2 from B12, permission change callback, server-invalid/offline state; no fake RPC URL, no startup connection, no heartbeat scheduler or Info widget. `src/shell.py` extended only with `apply_info_snapshot` scheduling Notebook permission changes via `root.after(0,...)`; preserves user-corrected Dồn label, original S01 source functions, hidden unsupported tab behavior. Original `src/TLMTool.py` remains intentional exit code 2; no pretend working UI/EXE.
- **LOCAL TESTS PASS**: python -m compileall -q on combined S01+S02 and python -m unittest discover: **15/15 PASS** (7 retained S01 + 8 new S02). Tests include revoked rights on invalid token/offline, dev+permission, no plan-string inference, limit input checking, Tk thread-marshal check. GitHub src/permission_guard.py, src/info_state.py, src/shell.py, tests/test_s01.py, tests/test_s02.py re-fetched, required methods and test counts verified; no real HTTP/Windows Tk/game build executed.
- Added `docs/source/S02_AUTH_STATE.md`, `docs/source/S02_MODEL.json`, `docs/tasks/S02.md`; only shell.py updated among prior app modules. Existing S01 settings/test/source, PLAN, A–R research, frozen binaries and Proxy Phase Q lock unchanged. **CURRENT STATUS = SOURCE_PARTIAL_AUTH_VERIFIER_INFO_UI_FEATURES_AND_WINDOWS_BUILD_MISSING**: source exists but true Info server/token verifier, real 11-tab feature controllers and Stage-T workflow absent; NOT a compiled or playable app.

## S02 BLOCKERS / NEXT_ACTION
- Original token signature parameters/public key validity, RPC endpoint and request fields, FREE plan default grants, time-based token expiry/heartbeat grace, PC+emulator running count integration, authentic InfoTab UI/activation, Windows Tk/EXE runtime all UNKNOWN or NOT_RUN. Keep no dev tab exposure without signed rights; do not develop Proxy.
- NEXT_ACTION on CONTINUE: **S03 — source-first original info_tab token verification/startup RPC and permission_guard default-FREE/heartbeat grace contract audit**, use frozen EXE and existing docs first; then implement a bounded real InfoTab read-only UI/controller only where evidence supports, without inventing server, permissions, endpoint, public key or activity buttons. Add tests and update STATE.md/PROJECT_STATUS.md; use client DATA 222222 only to fill relevant *game client* knowledge, read-only.


## S03 VERIFIED — ORIGINAL INFO AUTH CONTRACT / PASSIVE INFO TAB SOURCE
- CONTINUE resumed from S02 NEXT_ACTION after current PLAN.md/STATE.md/PROJECT_STATUS.md and S01–S02 source read. docs/tasks/S03.md absent at start. Original user ZIP read-only, frozen inner TLMTool.exe SHA256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22, CRC PASS.
- InfoTab compiled module marker 0x2975ca9 and permission_guard marker 0x2b84c35; original static symbols show startup Supabase RPC, app_heartbeat_v2, signed Base64 token HMAC/RSA verification branches, _DEFAULT_FREE_PERMISSIONS, token_expiry_ts, heartbeat_failures, heartbeat_grace_seconds and server_max_windows. **18/18 selected exact-offset binary anchor checks PASS** after correcting one string-window length in verification code; no original program or server executed. Active signature policy, default FREE permission set, heartbeat grace values and exact JSON/HTTP server contract remain UNKNOWN; no secret/key material extracted or reused.
- Added actual **src/info_tab.py**: passive real ttk InfoTab fields supported by B12 original UI (version 2.1.2, application code, key, license type, windows, expiry and changelog) and explicit Chưa xác minh for unavailable server state. This is a partial read-only slice **not complete screenshot/runnable app parity**. No fake Copy/Enter/activation/update/upload log functionality. Existing S01/S02 modules, SCOPE_LOCK and user-corrected Dồn tab unchanged. Normal src/TLMTool.py still fails closed with exit code 2 pending authentic Info and remaining feature controller implementations.
- Added tests/test_s03.py: **6/6 S03 headless unit tests PASS**, local compileall PASS. Existing 15/15 S01+S02 tests are from previous checkpoint and **were NOT combined/rerun in this S03 session**; Windows live Tk/Info RPC/heartbeat/Nuitka/LDPlayer all NOT_RUN. Original package not modified.
- New docs/source/S03_INFO_VIEW_AND_AUTH_BOUNDARY.md, docs/source/S03_MODEL.json, docs/source/S03_STATIC_EVIDENCE.tsv (21 rows), docs/tasks/S03.md; appended STATE.md and PROJECT_STATUS.md checkpoint. No Proxy development and no new public dev tabs.
- CURRENT STATUS **S03_READONLY_INFO_VIEW_6_TESTS_PASS_AUTH_RPC_RUNTIME_UNVERIFIED**; partial source exists, no functional app/Windows EXE. Avoid old SOURCE_MISSING status.

## NEXT_ACTION
On CONTINUE read PLAN.md/STATE.md and verify docs/tasks/S04.md absent. **S04 — bind read-only Info state to real Tk lifecycle safely and run full combined S01–S04 tests, continuing source-side reconstruction from verified original InfoTab contracts**. Do not invent real licensing endpoint/signature/public key, offline FREE grants or heartbeat values. Do not develop Proxy. Preserve correct S01–S03 and consult DATA client repo read-only only for actual game-client-specific unknowns.


## S04 VERIFIED — INFO TK LIFECYCLE INTEGRATION / FULL WINDOWS 31-TEST REGRESSION
- CONTINUE resumed from S03 NEXT_ACTION after re-reading live GitHub PLAN.md, STATE.md, PROJECT_STATUS.md, S01–S03 source/tests and original E04/E07/E08/B12 evidence. Confirmed docs/tasks/S04.md absent before work. Existing correct research and source unchanged; no client DATA modifications or Proxy Phase Q work.
- **Real source added:** src/info_binding.py. create_info_only_shell constructs ONE actual InfoState, partial S03 TLMInfoTab and S01 TLMMainApp; keeps all unimplemented feature/dev tabs hidden with Info-only visible. Root.after(0) dispatches verified state change to Tk; no app widget modified from source worker callback. Callback revision+current-snapshot identity rejects stale queued *grant* arriving after latest revocation. Root-only <Destroy> cleanup, already-queued callbacks dropped after close, stop_heartbeat placeholder and selected-tab refresh shutdown; no false license or functional buttons. Existing src/TLMTool.py production entrypoint still **fails closed exit 2** due to missing genuine Info RPC/verifier/features.
- Added tests/test_s04.py (**10 test cases**) with fake Tk widgets: visibility, read-only controls, queued updates, reversed grant/revocation ordering, revoke-after-applied, pending callback suppression, root vs child destroy, Tk after TclError shutdown, wrong input type rejection, identity of InfoState shared with Info view.
- **Real Windows CI executed successfully on committed GitHub source** via .github/workflows/s04-source-tests.yml. GitHub Actions run https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37867454367 (head commit dcb154fc00846c382f7bec571a6da6c61d171a66, job 113617493218): setup Python **3.10 PASS**, compileall src/tests PASS, **full combined S01–S04 unittest 31/31 PASS**. The actual job log shows "Ran 31 tests in 0.035s" and OK, composed of S01=7 + S02=8 + S03=6 + S04=10. This confirms on GitHub runner—not simply inferring from previously run tasks.
- New docs/source/S04_INFO_LIFECYCLE.md, S04_MODEL.json, S04_STATIC_EVIDENCE.tsv (14 evidence rows), docs/tasks/S04.md; appended to STATE.md and PROJECT_STATUS.md. Prior PLAN, S01–S03 code, frozen ZIP and Proxy restriction unchanged.
- **Scope/status = S04_INFO_TK_BINDING_AND_WINDOWS_31_TESTS_PASS / REAL_APP_RUNTIME_BLOCKED_AUTH_AND_FEATURES**. Tests use simulated Tk widgets (no actual native window/raster), test-only fake decoded claims, no real server RPC/heartbeat, original FREE permissions still UNKNOWN, no game/LDPlayer/real account controller, no Nuitka runnable EXE or actual authenticated startup. Partial source exists; do not claim full app build success.

## S04 BLOCKERS / NEXT_ACTION
- Windows-Tk live geometry and screenshot parity, actual signed license token verification, Info RPC/heartbeat original flow, active normal 11-tab feature controllers and Stage T Windows standalone packaging remain NOT_RUN/UNIMPLEMENTED.
- NEXT_ACTION on CONTINUE: read current PLAN.md/STATE.md, check docs/tasks/S05.md on GitHub, then **S05 — exercise genuine Info-only Tk preview and compare with B12 screenshot/clean close on Windows (if runner permits GUI), while keeping production src/TLMTool.py exit 2**. If there is no true GUI/display runtime, mark WINDOW_GUI_NOT_RUN and use CI/headless tests for a real, original-backed small Info startup contract slice; do not fabricate server endpoints/keys, default FREE permission, fake feature buttons or Proxy.


## S05 VERIFIED — NATIVE WINDOWS TK INFOTAB SMOKE / B12 PARITY GAP
- CONTINUE from S04 NEXT_ACTION; read current PLAN.md, STATE.md, PROJECT_STATUS.md, B12 Info screenshot/geometry docs and S01–S04 real source. `docs/tasks/S05.md` was absent before task. Reused existing correct code; original frozen ZIP, TLM source for prior stages, client DATA, PLAN and Proxy exclusion untouched.
- Created real Windows verification code **tools/S05_WINDOWS_TK_SMOKE.py** and `.github/workflows/s05-native-info-preview.yml` (Windows/latest Python 3.10 with optional Pillow screenshot). Script uses actual Tk root + ttk Notebook + real S04 InfoState/InfoTab binding to measure widget geometry, Info-only fail-closed state, save screenshot and verify root destroy cleanup. It never calls production src/TLMTool.py startup, server, game, ADB or Proxy.
- **GitHub Actions run 37868251319** (https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37868251319), Windows job 113620048879, HEAD 88d99b18a7e6a21e49b8fe23dea2c41d20b5f9c0: completed **SUCCESS**. Python 3.10 compileall PASS; combined original **31/31** S01–S04 unittest PASS (actual job log "Ran 31 tests in 0.017s"); native Tk Info-only smoke status **PASS_NATIVE_TK_INFO_ONLY_SMOKE**. Real screenshot ImageGrab successful; two-file artifact **ID 11589735180** (PNG+machine-readable JSON).
- Actual runner desktop **1024x768**, root geometry **450x688+564+0**, matches E02 high-confidence screenheight-80 formula; client width original B12 **450 px MATCH**, height **688 px** vs B12 reference **1000 px** due to different screen heights. Actual ttk Notebook 15 potential slots; **only info_tab visible and selected**, reflecting missing trusted license/feature factories; B12 reference had 11 visible tabs and Info at right. Actual native notebook screen bounds x577/y36 width440/height678; Info frame x578/y59 width436/height652. UI read-only; status and license values **Chưa xác minh**; no false FREE/plan values. Window destroyed cleanly with binding closed.
- Original B12 PNG raster was NOT loaded in this task: no pixel diff/SSIM comparison performed. Native client-only PNG 450x688 captured but does **NOT** mean 450x1000 B12 screenshot parity. Original Info status colored 416x44 panel/changelog scroll box/button handlers not yet rebuilt; current status is simple ttk labels (incomplete layout), still marked NOT_PARITY.
- New docs/source/S05_NATIVE_TK_PREVIEW.md, docs/source/S05_MODEL.json, docs/tasks/S05.md; append-only checkpoints. Status **S05_NATIVE_WINDOWS_INFO_TK_PASS_B12_PIXEL_PARITY_NOT_YET_VERIFIED**. Product entry src/TLMTool.py remains exit 2; no authentic server/token/heartbeat, game feature tabs or Stage-T Nuitka Windows EXE. Do not claim full product built.
- **NEXT_ACTION S06:** reread PLAN.md/STATE.md and check S06 GitHub task first, then implement only original-backed **passive Info version status panel/rows/changelog scroll layout** based on B12, preserving actual safe unverified data; add real native Windows Tk geometry tests using S05 workflow/artifacts. No fake Copy/Nhập/log upload buttons, no server or token inventions, no Proxy development.


## S06 VERIFIED — ORIGINAL B12 READ-ONLY INFO LAYOUT AND WINDOWS 37-TEST REGRESSION
- CONTINUE resumed from GitHub S05 NEXT_ACTION. Re-read PLAN.md, STATE.md, PROJECT_STATUS.md, docs/tasks/B12.md, docs/ui/B12_INFO_GEOMETRY.tsv, S05 tests and current src/info_tab.py; verified docs/tasks/S06.md absent. Original data, prior S01–S05 logic, frozen TLM binary, GitHub client DATA, SCOPE_LOCK and Proxy Phase Q exclusion untouched. User spelling **Dồn** preserved.
- Updated **src/info_tab.py** (only existing source changed this task): retained exact S03 `InfoDisplay` / `display_from_info_state` model and interfaces while replacing passive plain status/changelog labels with **native measured Tk Info layout**: status border at Info-frame relative **[3,51,416,44]** using B12 blue checking status palette when server not verified; six white value surfaces at x107 y=105/130/155/180/205/230, heights19, widths 312 for version/license/windows/validity and 256 for device/key; true read-only `tk.Text` and `ttk.Scrollbar` in changelog region **[3,295,416,109]**. No Copy/Nhập/license activation/upload buttons generated without real handlers; unverified license values remain `Chưa xác minh`.
- Added `tests/test_s06.py` (6 new unit cases), `tools/S06_WINDOWS_INFO_LAYOUT.py` (real Windows Tk geometry, scrollbar/state, safe Info-only, PNG and JSON, root close), `.github/workflows/s06-native-info-layout.yml` (Windows Python 3.10 native test and entire Stage-S regression).
- **ACTUAL GITHUB ACTIONS PASS:** run https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37869205674 HEAD 09302f5c241d302c5ebfe68c282b2bfaeeba438b, job 113623105567, completed success. Actual job log read: compileall PASS, **37/37 combined S01–S06 unittest PASS** (`Ran 37 tests in 0.018s`); **S06_LAYOUT_STATUS=PASS_NATIVE_READONLY_LAYOUT_ANCHORS**; status rect [3,51,416,44], all six exact value positions/widths, changelog [3,295,416,109], scrollbar TRUE, screenshot CAPTURED_CLIENT_REGION, binding_closed TRUE. Runner 1024x768 -> Tk root client 450x688, not original screenshot B12 450x1000. PNG+JSON stored in Github Actions artifact **11589915070**.
- New `docs/source/S06_B12_READONLY_LAYOUT.md`, `docs/source/S06_MODEL.json`, `docs/tasks/S06.md` and append-only STATE/PROJECT_STATUS checkpoint. **S06 status NATIVE_WINDOWS_B12_INFO_ANCHORS_37_TESTS_PASS / FULL_UI_AND_GAME_PARITY_BLOCKED**. Mark relative widget rectangles PASS but original 452x1032 full screenshot pixel diff NOT_RUN; authorized original 11-tab/raster, dynamic server fields/changelog, genuine token/heartbeat, functional game tabs and Nuitka Windows EXE still absent. Production src/TLMTool.py intentionally exits 2.
- **NEXT_ACTION on CONTINUE: S07** — read current PLAN.md/STATE.md and check GitHub docs/tasks/S07.md first. Implement only B12-supported **remaining passive Info price/contact/catalog regions** and separators without hardcoding server prices/changelog or adding fake interactive buttons. Verify via full combined Windows CI/native Tk and preserve the now-passing S06 geometry. After S07, prioritize genuine original Start/Login functional source slices. No Proxy development, no invented entitlement/server or unconditional dev tab.


## S07 VERIFIED — B12 PASSIVE PRICE/CONTACT/CATALOG; 43 WINDOWS TESTS PASS
- CONTINUE resumed from S06 NEXT_ACTION; reread PLAN.md, STATE.md, PROJECT_STATUS.md, original B12 Info screenshot/geometry and current S06 code/tests. `docs/tasks/S07.md` absent at task start. Original package, PLAN, all prior research, frozen client DATA, user spelling **Dồn** and Proxy Phase Q lock unchanged.
- **Only existing source edited:** src/info_tab.py. Preserved S06-measured status [3,51,416,44], value rows with 25px pitch, disabled scrollable changelog [3,295,416,109], InfoState/auth safety. Added B12-measured passive price [6,427,416,88], contact heading [7,539,300,19], blue non-clickable original Facebook/Zalo labels, catalog heading [7,630,320,19] and catalog region [30,656,340,58], plus y526/y616 separators. Price/catalog data remain explicitly **Chưa xác minh** because original values are server-supplied, NOT hardcoded screenshot defaults. No fake Copy, Nhập, Gửi log, support click action or entitlement created.
- New tests/test_s07.py (6 headless regressions), tools/S07_WINDOWS_INFO_SECTIONS.py (actual Windows Tk measurements/readonly/safe labels/no buttons/close/screenshot), .github/workflows/s07-info-sections.yml. New docs/source/S07_PASSIVE_INFO_SECTIONS.md, docs/source/S07_MODEL.json, docs/source/S07_STATIC_EVIDENCE.tsv (14), docs/tasks/S07.md, append-only checkpoints.
- **GitHub Actions VERIFIED:** run https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37869958702, head 77af1943f9cea686efebfdb8c56a3324bb87c7b0, job 113625514299, completed SUCCESS. Actual log fetched: compileall PASS, combined **43/43 S01–S07 unittests PASS** (`Ran 43 tests in 0.017s`); preserved S06 native layout PASS, S07 `PASS_NATIVE_PASSIVE_SECTIONS`, price/contact/catalog rectangles and separators matched, 0 action buttons, root cleanly closed, client PNG captured. GitHub artifact ID **11589688653**.
- **New explicit visual blocker:** S07 runner desktop 1024x768 -> client 450x688; catalog region at y656+58 exceeds the visible frame. `catalog_fully_within_frame=false`; placement passed but complete visibility FAILED on short monitor. Original B12 captured 450x1000 and 11 visible authorized tabs. No original pixel diff and NO full visual parity claim.
- Current status **S07_WINDOWS_NATIVE_PASSIVE_SECTIONS_43_TESTS_PASS_CATALOG_CLIPPED_ON_768P**. Partial app source, production src/TLMTool.py still deliberately exits 2. Genuine token verification/heartbeat, server-fed content, Start/Login/game controllers and reproducible Nuitka Windows EXE remain unavailable; no Proxy work.
- **NEXT_ACTION S08:** before edits reread PLAN.md/STATE.md, check docs/tasks/S08.md absent, inspect B02/B03/E01/E03/Start original audit and original compiled start_tab/Win32 window-discovery contracts. Implement the **smallest real functional Start-tab slice**, beginning with read-only discovery of actual game windows if original supports it; add native Windows tests and keep auth-gated UI closed until actual licensing service. No fabricated HWND/process, game clicking, Proxy or screenshot-only fake Start controls. Preserve Info S01–S07 completed work; separate small-screen catalog clipping as deferred visual gap.


## S08 VERIFIED IMPLEMENTATION — REAL WIN32 START WINDOW DISCOVERY / 55 WINDOWS TESTS
- User said DUYỆT (approval) to S08; resumed from S07 NEXT_ACTION. Read live PLAN.md, STATE.md, PROJECT_STATUS.md, C01/C02 full original-window/identity audits, B02/B03/E01/E03/F01/D08. Checked docs/tasks/S08.md absent first. Existing S01–S07 source, B12 layout, original archive, client DATA and Proxy Phase Q exclusion were NOT modified; corrected user tab wording Dồn preserved.
- Created **genuine operational READ-ONLY Start discovery source** `src/start_windows.py` with Win32 ctypes backend: `EnumWindows` top-level list, `IsWindow/IsWindowVisible`, `SendMessageTimeoutW` WM_GETTEXTLENGTH+WM_GETTEXT each bounded 150ms, GetClassNameW, GetWindowThreadProcessId, query-only OpenProcess+QueryFullProcessImageNameW; strict game executable normalized 'thần long mobile.exe', UnityWndClass or exact normalized 'Thần Long Mobile' title. This process-AND-(class-OR-title) is deliberately conservative and explicitly **NOT proven to equal original compiled Boolean grouping** (C01 UNKNOWN). No fake accounts/HWNDs, game click, memory reading, DLL/injection, window rearrangement, Proxy or server rights. Missing original 3s background producer and 2s Start UI consumer are S09, not fake-implemented.
- Added WindowRegistry tracking HWND+PID snapshots and reporting added/removed/reused rows, rejecting conflicting PID observations. This follows C02 anti-wrong-account identity protection; real game-specific positive matching remains NOT_RUN.
- New `tests/test_s08.py` **12** regression tests (process/class/title, invisible/invalid/duplicate HWND, non-game Unity false positive, 150ms title, hung-failure, mid-enumeration reused PID, stale closure, HWND/PID reconciler).
- New `tools/S08_WINDOWS_DISCOVERY_SMOKE.py`, `.github/workflows/s08-windows-start-discovery.yml`: real Windows/Python 3.10 CI tests create an actual Tk HWND in the test process, enumerate native HWNDs, safely fetch title/PID/process path, reject it as game. Combined unit tests and compileall on GitHub.
- **ACTUAL GitHub Actions run [37872770792](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37872770792), commit dd63c3b5b14b756e8cb389ae9fac7d08a734ad95, job 113634367516: SUCCESS**, log inspected: compileall PASS, **55/55 S01–S08 unittest PASS** ('Ran 55 tests in 0.044s'); `PASS_READONLY_NATIVE_WIN32_ENUMERATION`, 63 top-level HWNDs, 11 visible, one visible own Tk HWND, title via actual SendMessageTimeoutW 150ms PASS, executable and class real Win32 API PASS. CI had **0 Thần Long game windows** (real_game_present=false); therefore positive game discovery + hung GAME-window behavior NOT_RUN. 0 synthetic game HWNDs. Artifact 11591140628 `win32_discovery.json`. Never claim game runtime tested.
- Created `docs/source/S08_START_WIN32_DISCOVERY.md`, `docs/source/S08_MODEL.json`, `docs/tasks/S08.md`; STATE and PROJECT_STATUS append-only. Source exists and Windows read-only API is actually exercised, but original complete Start UI/game process interaction, authentication service and executable remain missing; public `src/TLMTool.py` still deliberate exit 2, no Nuitka EXE.
- **CURRENT_STATUS S08_REAL_WIN32_DISCOVERY_55_TESTS_PASS_GAME_RUNTIME_NOT_PRESENT**. Important caveat: original C01 final Boolean grouping and exact whitespace normalization UNKNOWN; actual game may require a filter adjustment once a real Windows game process can be tested. QueryFullProcessImageNameW is a read-only practical substitute for original psutil.Process; do NOT mislabel as identical source.

## S08 BLOCKERS / NEXT_ACTION
- Missing background 3s producer/cache and Tk Start 2s consumer (stop on leaving Start); exact original view/widget/control/preview and physical game-positive validation, real Info token and feature entitlement; no product Windows EXE. S07 768p catalog clipping separate deferred visual gap; do not redo Info.
- NEXT_ACTION on CONTINUE **S09: implement bounded/cancellable read-only Start 3s Win32 discovery worker with immutable HWND/PID snapshot cache and 2s UI polling lifecycle**, handling stale/reused HWND without UI-thread blocking, and test on actual Windows. Do not grant Start tab via fake authorization, do not create game clicks, game-process memory readers, DLL injection or Proxy. Preserve S01–S08 correct code/tests and update STATE/PROJECT_STATUS with evidence.


## S09 VERIFIED — REAL 3-SECOND START HWND WORKER AND 2-SECOND TK CACHE POLLER
- CONTINUE from live GitHub S08 NEXT_ACTION, after PLAN.md, STATE.md, PROJECT_STATUS.md, source S08, and original C01/C02/C04/E03 contract read. docs/tasks/S09.md absent at start. Kept all S01–S08 code/known-correct tests and PLAN, original binary, client DATA, spelling Dồn and Proxy Phase Q exclusion unchanged.
- Added **src/start_polling.py** implementing a genuine read-only `StartWindowProducer` with default ~3s Win32 enum/cache interval on a dedicated daemon thread, immutable revision-tagged `WindowSnapshot`, error/invalid/empty snapshot on failed enumeration, immediate cache invalidation on stop, epoch+event stale-result fencing, at-most-one live worker (restart waits for the old thread), backend creation on worker, bounded <=0.2-second stop join; no game commands or memory reads.
- Added **TkStartCachePoller** with original Start `_start_refresh/_stop_refresh` interface from E03, real `root.after` UI polling default 2000ms, thread-safe cache *read only* on Tk, updates only when revision changed, `WindowRegistry` HWND+PID stale/reuse delta, cancellation+generation guard when leaving tab and on shutdown. No actual visible StartTab or local bypass of Info permission. Original 800/2000ms preview maintenance and 8s game memory clock are separate not implemented.
- Created **tests/test_s09.py (12 unit tests)** covering original cadence constants, live thread snapshots, stopped mid-blocking scan, late publish rejection, backend/scan failures, invalidation, PID reuse, UI callback cancellation and restart, TabLifecycle test-only authorized Start construction, repeat start/stop. Created native Windows **tools/S09_WINDOWS_START_POLLING_SMOKE.py** and **.github/workflows/s09-windows-start-polling.yml**, tested Win32 worker and Tk callback on actual Windows; no simulated game process.
- **GitHub Actions run 37873565602** https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37873565602, commit 10aa388164c71e9c75b607e4e05235107192596f, job 113636843382, COMPLETED SUCCESS. Actual job log read: Windows Python 3.10 compileall PASS, **67/67 combined S01–S09 unittest PASS** (`Ran 67 tests in 0.211s`), native `PASS_NATIVE_WINDOWS_THREADED_START_CACHE`, default worker 3.0s and Tk cache poll 2000ms; 1 real background enumeration of 68 top-level HWNDs, Tk cache receiver main thread true, revision 1 pending/invalid then revision 2 valid zero game results, stop revoked cache, producer stopped and poller closed. JSON artifact id 11591396593. Game absent from CI: positive Thần Long matching **NOT_RUN**, no original game runtime parity.
- New docs/source/S09_START_THREADED_CACHE.md, docs/source/S09_MODEL.json, docs/tasks/S09.md. Project still partial source, real signed token server/heartbeat and Start/other game tabs absent, `src/TLMTool.py` intentionally returns 2, Nuitka Windows EXE not built. No fake clicks, account handles, title fallbacks, dev rights or Proxy work.
- **CURRENT STATUS S09_NATIVE_WINDOWS_WORKER_TK_67_TESTS_PASS_NO_GAME_RUNTIME**.
- **NEXT_ACTION on CONTINUE: S10** — reread PLAN.md/STATE.md and original B04 Start UI screenshot plus C03/C05/C06/C08/E03. Build the **smallest genuine read-only Start tab widget** consuming S09 real immutable HWND/PID/title cache with correct `_start_refresh/_stop_refresh` hooks and verified authorization gating; use actual Windows Tk tests, no fake preview/layout/click handlers and no default Start grant. Preserve all S01–S09 source and tests; no Proxy. Full token/license server, actual Thần Long runtime and EXE remain explicit blockers.


## S10 VERIFIED — READ-ONLY START WIDGET / 77 WINDOWS TESTS PASS
- Resumed from live GitHub S09 NEXT_ACTION; checked S10 absent and consulted PLAN, original B01/B02/B04 correction, C01/C02/C03/C05/C06/C08/E03, S09 actual source/tests. User ZIP SHA256 **c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd** and internal EXE SHA256 **15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22**, exact Gate-A forensic baseline; no reanalysis or original asset modification.
- Created **src/start_tab.py**: real Tk passive HWND/PID/title view consuming S09 immutable Win32 cache (3s worker, 2s selected-tab UI poll); states PENDING/EMPTY/ERROR/LIVE; clear stale rows on Stop, failed scan or revoked permission; widget destroy shuts poller down. No DWM thumbnail/master/HP, game clicking or dummy UI buttons. Source S01–S09 unchanged.
- Created tests/test_s10.py (10 cases), tools/S10_WINDOWS_START_VIEW_SMOKE.py, .github/workflows/s10-native-start-readonly.yml. Production src/TLMTool.py still exits 2 and does not grant Start. An **isolated test-only** verified claims adapter was used to prove existing E03 gate, not a new server/token implementation.
- **ACTUAL Windows GitHub Actions run [37874342004](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37874342004) commit dcf76fb2222a27c715a21f17c65a4d5582a0a751 job 113639345676 SUCCESS:** Python 3.10 compileall PASS, **77/77 S01–S10 unit tests PASS** (`Ran 77 tests in 0.251s`), native `PASS_NATIVE_READONLY_START_AUTH_AND_POLLING`. Initial Info-only, no Start without test-verified grant, real threaded Win32 cache consumed on Tk, no game candidates in runner (EMPTY), no game action buttons, revoking rights returned to Info, hid Start, stopped worker and cleared rows.
- New docs/tasks/S10.md, docs/source/S10_START_READONLY_VIEW.md, docs/source/S10_MODEL.json; STATE.md and PROJECT_STATUS.md appended. PLAN, frozen binary, all prior verified code, Dồn spelling and Proxy exclusion unchanged.
- **CURRENT STATUS S10_NATIVE_WINDOWS_READONLY_START_77_TESTS_PASS_NO_GAME_RUNTIME**. Still NOT_RUN real Thần Long game candidate + original visual/behavior parity + licensed server/heartbeat; DWM previews and feature controllers missing; product Windows EXE NOT_BUILT. No fake full-product build claim.
- **NEXT_ACTION on CONTINUE: S11** — reread PLAN.md/STATE.md and check docs/tasks/S11.md first; inspect C03/C04 + actual Start preview screenshot geometry + S10 UI/Windows cache. Implement the smallest genuine **read-only DWM preview** with HWND/PID identity and cleanup on selection/permission/PID-change/destroy. Native Windows smoke can use an explicitly test-owned window to verify DWM mechanics but must not treat it as game. Do not add click activation, fake source HWND/game controls/license/Proxy; preserve existing code and all 77 tests.


## S11 VERIFIED — TRUE WINDOWS DWM THUMBNAIL CORE / 90/90 TESTS PASS
- Continued directly from S10 NEXT_ACTION. Read live PLAN.md/STATE.md/PROJECT_STATUS.md, original C03/C04/C05/C06 and preview screenshot 205×137/197×110 geometry; confirmed docs/tasks/S11.md absent. Did not rewrite completed S01–S10, Info/auth, original package, plan, client data, user spelling Dồn or Proxy exclusion.
- Added **src/dwm_preview.py** using real Win32/DWM functions to create top-level owned `ThlDwmThumbDst` overlay, register/update compositor thumbnail, reposition to Tk preview anchor, unregister/destroy. Native source HWND+PID must match and not be hung before registration/update; PID reuse/revocation/close/failure clears old overlays. Read-only: NO game input/activation, no invented entitlement.
- Existing **src/start_tab.py** changed only to consume S09 verified HWND/PID/title cache and create dynamic DWM 205×137/197×110 preview items, with Tk-owned lifecycle, delayed reposition and teardown when leaving/revoking Start. Existing S10 read-only window list preserved.
- Added **tests/test_s11.py** (13 tests), **tools/S11_WINDOWS_DWM_SMOKE.py**, **.github/workflows/s11-native-dwm-preview.yml**. Two early native CI failures were identified and fixed: Python 3.10 has no wintypes.HCURSOR (use HANDLE field), and Tk winfo_id can be a child HWND unsuitable for DWM source registration (resolve native root via GetAncestor(GA_ROOT)).
- **ACTUAL GitHub Actions Windows Python 3.10 [run 37878364061](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37878364061) head 03073edf37569ba366c184b1bda7bd8c5f17853e job 113652046835 SUCCESS**: compileall PASS, **90/90 S01–S11 unittest PASS** (`Ran 90 tests in 0.202s`), native status **PASS_NATIVE_DWM_THUMBNAIL_LIFECYCLE**. Real test-owned Tk source HWND/PID, actual DwmRegisterThumbnail/update/reposition PASS, negative mismatched PID rejection/cleanup PASS, shutdown cleanup PASS. No actual game in CI. Stage S CI 37878364020 SUCCESS; S10 native regression on the first S11 code commit 37878185336 SUCCESS.
- New docs/tasks/S11.md, docs/source/S11_DWM_LIFECYCLE.md, docs/source/S11_MODEL.json. Only S11 files + append-only STATE/PROJECT_STATUS changed; original package, PLAN, previous functional modules left intact.
- **CURRENT STATUS S11_NATIVE_WINDOWS_DWM_90_TESTS_PASS_ACTUAL_GAME_AND_PIXEL_PARITY_NOT_RUN**. Original game positive, 3-account simultaneous preview, original pixel parity/occlusion, genuine auth server/token, full product EXE still NOT_RUN/NOT_IMPLEMENTED; do not claim full tool completed.
- **NEXT_ACTION on CONTINUE: S12** — reread live PLAN.md/STATE.md, check docs/tasks/S12.md first, review C03/C04/C17 and S11 code. Test native DWM with 2–3 *test-owned* real top-level Win32 HWNDs, Tk resize/move, disappearance/PID guarding and explicit tab permission revoke/teardown. Do not fake game sources in product, add game actions, change Proxy, or rewrite working code; keep 90 tests passing.


## S12 VERIFIED — THREE REAL WINDOWS TEST-OWNED DWM SOURCES / 98 TESTS PASS
- CONTINUE resumed from live S11 NEXT_ACTION; read PLAN.md and STATE.md, checked S12 file absent, reviewed C03/C04/C17 and existing S11 Tk/DWM source. Frozen TLM ZIP, user spelling Dồn, Info/token guard, Proxy lock and every unrelated module untouched.
- Existing source change limited to **src/start_tab.py**: listens to root move/resize `<Configure>` even if child dimensions don't change; cleanup on root/container `<Unmap>`, fresh on `<Map>`; restores C04 verified **60ms** reposition debounce instead of provisional S11 80ms; unbinds Tk root handlers on shutdown. NO game input or new fake buttons.
- New tests/test_s12.py (8), tools/S12_WINDOWS_MULTI_DWM_SMOKE.py, .github/workflows/s12-native-multi-dwm.yml. **ACTUAL Windows Python 3.10 GitHub Actions [37878962348](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37878962348) implementation commit b5b68ed3ea198c71148190f13b64905234241e74 SUCCESS**: compileall PASS, **98/98 S01–S12 unit tests PASS** (`Ran 98 tests in 0.222s`), `PASS_NATIVE_S12_THREE_HWND_DWM_AND_AUTH_LIFECYCLE`. 3 actual **test-owned Tk** native HWNDs [524308,262264,196736] + owner: Win32 DWM registration, exact geometry move/resize, source closure leaves two previews, PID mismatch tears down stale source, root hide/restore, 5/5 native handles created/destroyed all PASS. Isolated test-only producer then fed 2 genuine test-owned HWNDs to real Start Tk; root translation same destinations, owner unmap/restore, permission revocation/fallback to Info all PASS.
- All same-commit S10 native CI 37878962283, S11 DWM CI 37878962259 and general Stage-S source CI 37878962249 SUCCESS. New docs/tasks/S12.md, docs/source/S12_THREE_HWND_LIFECYCLE.md, docs/source/S12_MODEL.json; STATE/PROJECT_STATUS append-only.
- **STATUS S12_THREE_NATIVE_DWM_98_TESTS_PASS_ACTUAL_GAME_NOT_RUN**: source/test-owned Windows lifecycle genuine; 3 actual Thần Long game instances, original screenshot raster parity, minimized-game GPU details, server/auth/heartbeat and full release EXE NOT_RUN/NOT_BUILT; do not conflate.
- **NEXT_ACTION S13 on CONTINUE:** read PLAN.md/STATE.md and check S13 existence, inspect C04/E03 and actual Start UI source. Add a bounded C04 preview maintenance scheduler (800/2000ms with 6-threshold operator explicit UNKNOWN) separate from S09 3s producer and 2s cache poll, selected-Start only; test stale HWND/PID and geometry/disconnect without inventing game FPS/permissions. Keep S01–S12 correct code and all 98 tests.


## S13 VERIFIED — C04 ADAPTIVE SELECTED-START PREVIEW MAINTENANCE / 112 TESTS PASS
- Followed live S12 NEXT_ACTION; reread PLAN.md, STATE.md, PROJECT_STATUS.md, C04/C03/E03 and S09–S12 source, verified docs/tasks/S13.md absent before task. Kept all prior passing work, original archived TLM binary, user spelling Dồn and Proxy exclusion unchanged.
- Added **src/preview_maintenance.py**: true Tk after scheduler independent of S09 3s worker and 2s UI poll; 800ms for 0–5 cached windows, 2000ms for 6+ cached windows, source threshold literal 6 confirmed but **exact original comparison at count=6 remains UNKNOWN; S13 chose conservative 2000ms**. 800/2000 is maintenance, NOT DWM compositor FPS. Generation/stop/closed fences reject late callbacks; cached O(1) snapshot only, no game memory/process scan on Tk, no fake character names/HP.
- Changed existing **src/start_tab.py** minimally: starts/stops maintenance with E03 selected-tab _start_refresh/_stop_refresh, reconciles HWND/PID/title and invalid cache conditionally from immutable S09 snapshots, native DWM HWND validity checked at each tick. Keeps previously working 60ms reposition, read-only list, DWM, Info/permissions and all other source intact.
- Added tests/test_s13.py (**14 tests**), tools/S13_WINDOWS_PREVIEW_MAINTENANCE_SMOKE.py native real test-owned Win32 HWND Tk fixture, workflow .github/workflows/s13-native-preview-maintenance.yml.
- **ACTUAL Windows Python 3.10 GitHub Actions [run 37880150984](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37880150984), job 113657739751, implementation head 0816fcabd9a725ddfcaeb629ca9c3182f0f5515f SUCCESS**: compileall PASS, combined **112/112 S01–S13 tests PASS** (`Ran 112 tests in 0.160s`), native `PASS_NATIVE_S13_ADAPTIVE_CACHE_MAINTENANCE_AND_REVOCATION`: 1 HWND→800ms, 6 HWND→2000ms; native Tk test-owned source DWM live; invalid cache clears UI/DWM, restoration works, HWND closed outside cache invalidates thumbnail; permission revoke stops S09+S13 timers with no late cycles. No Thần Long game or live server in runner.
- Same head existing S10 native run 37880151057, S11 DWM run 37880151065, S12 3-window native run 37880151024, overall Stage-S source run 37880151015 all COMPLETED SUCCESS.
- New docs/tasks/S13.md, docs/source/S13_C04_PREVIEW_MAINTENANCE.md, docs/source/S13_MODEL.json; STATE/PROJECT_STATUS append-only.
- **STATUS S13_ADAPTIVE_WINDOWS_PREVIEW_MAINTENANCE_112_TESTS_PASS_GAME_RUNTIME_NOT_RUN**. Original real game, HP metadata, exact count-six comparator/3s freshness Boolean, original pixel parity, signed server token and full Windows EXE NOT_RUN/UNIMPLEMENTED. Do not claim full reconstruction.
- **NEXT_ACTION on CONTINUE S14:** reread live PLAN.md/STATE.md, check S14 task first, inspect C09/C17 and screenshot 2-column geometry. Add **functional original-evidenced 1x–5x Start embedded preview columns (default 2x)** and per-item **◀/▶ logical HWND reorder** without game-window activation; keep DWM binding and HWND/PID life cycle, preserve existing 112 tests, mark unknown edge/insertion behavior as local policy, no Proxy/no fake controls.


## S14 VERIFIED — REAL 1x–5x START PREVIEW GRID + HWND ORDER / 128 WINDOWS TESTS PASS
- CONTINUE from live S13 NEXT_ACTION; read PLAN.md/STATE.md/PROJECT_STATUS.md, C09/C17/C03, S13 source/tests, checked docs/tasks/S14.md absent. No S01–S13 reimplementation, PLAN/original binary change, unrelated tab/Proxy work, or unverified game activation.
- New **src/preview_layout.py**: exact recovered 1x,2x,3x,4x,5x, 2x default; pure row/column model and retained logical preview order keyed by source HWND. C17 per-item ◀ delta=-1 / ▶ delta=+1. Safe reconstruction policies explicit UNKNOWN original: edge no-wrap, append new HWND, changed PID treats reused numeric HWND as new to avoid carrying wrong identity.
- Existing **src/start_tab.py** extended with functioning `Cột:` readonly ttk combobox and native ttk per-tile ◀/▶ buttons. Moving/reordering real Tk previews keeps DWM HWND/PID identity and thumbnail/destination handles; no Win32 game activation, clicks, keyboard, server grants, screenshots or fake buttons. Previous S09 polling, S13 maintenance and C04 60ms reposition unchanged.
- Added **tests/test_s14.py** (**16** cases), tools/S14_WINDOWS_PREVIEW_GRID_SMOKE.py (4 *real test-owned* top-level Windows HWNDs), .github/workflows/s14-native-preview-grid.yml.
- **ACTUAL Windows Python 3.10 GitHub Actions [run 37881002761](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37881002761), implementation commit 82e871d3023464b738944ef9760df47d8d16c3d5, job 113660441462 SUCCESS**: compileall PASS, **128/128 S01–S14 unit tests PASS** (`Ran 128 tests in 0.174s`), native `PASS_NATIVE_S14_REAL_DWM_GRID_AND_ORDER_LIFECYCLE`. Tested ttk control selection all 1x..5x and actual ◀/▶ invoke, DWM sources/thumbnail identity stable through all layout changes, manual order stays through reversed cache, stale PID refuses source, Info fallback and native teardown on revoked grant.
- Same implementation commit all regression workflows **SUCCESS**: Stage S run 37881002704, S10 native 37881002747, S11 native 37881002713, S12 3-HWND native 37881002772, S13 maintenance native 37881002748.
- docs/tasks/S14.md, docs/source/S14_PREVIEW_GRID_ORDER.md, docs/source/S14_MODEL.json added; STATE/PROJECT_STATUS checkpoint append-only. **STATUS S14_REAL_DWM_GRID_ORDER_128_TESTS_PASS_GAME_NOT_RUN.** Native test HWNDs belong to isolated Tk fixture, not actual Thần Long; original other-mode pixel parity, real token/heartbeat, all other game feature controllers and full EXE still unknown/unbuilt.
- **NEXT_ACTION S15 on CONTINUE:** reread PLAN.md/STATE.md, check docs/tasks/S15.md, consult C15/C03/C04. Implement the verified main Start **Làm mới** preview button that actually unregisters/destroys old DWM thumbnails and re-registers/rebuilds from the current immutable S09 cache, **retaining C09 selected columns and C17 surviving-HWND manual order**. Native Windows test resources and authorization; no fake game scanning, game commands, Proxy, or claims of product build. Keep all 128 tests working.


## S15 VERIFIED — C15 REAL FULL NATIVE DWM THUMBNAIL REFRESH / 142 UNIT TESTS PASS
- Followed LIVE S14 NEXT_ACTION; read PLAN.md, STATE.md, original C15/C03/C04 and S14 actual Start code; docs/tasks/S15.md absent at start. No re-plan or rewrite S01–S14, original specimen or unrelated tabs/Proxy. Changed production source only `src/start_tab.py` to add genuine working **Làm mới** (`btn_refresh_preview`, `refresh_window_preview_list`, `_clear_window_preview_list`).
- A real click in active authorized selected Start consumes exactly ONE immutable S09 cached WindowSnapshot (no invented process/game memory scan), cancels stale 60ms callback, unregisters all old DWM thumbnail handles, destroys native destinations BEFORE old Tk tile frames; rebuilds real DWM placements from current cache **retaining C09 1x–5x grid setting and C17 manual surviving-HWND order**. Invalid/empty/duplicate/failed cache drops all native resources and renders error/no-game UI. Hidden/revoked tab blocks manual refresh.
- Added tests/test_s15.py **14 unit cases**, tools/S15_WINDOWS_PREVIEW_REFRESH_SMOKE.py (4 actual **test-owned Tk Win32 HWND** with real DWM registration lifetime tracing), .github/workflows/s15-native-dwm-refresh.yml.
- Implementation commit 7be3cc1d8d32519e7ef61038bf3b91518a01f999 initially **142/142 units PASS** and native smoke generated `PASS_NATIVE_S15_MANUAL_FULL_DWM_REFRESH_AND_REVOCATION`, but GitHub Actions run 37883811777 **FAILED overall** solely because Windows cp1252 stdout could not print Vietnamese `Không tìm thấy...` UTF-8. Fixed only smoke log output with ASCII escapes (`ensure_ascii=True`), retaining UTF-8 artifact in commit **d6098800f4bb8e79a02ac8abac490df122c7f3b7**; do not count the initial failed run as success.
- **ACTUAL Windows Python 3.10 [GitHub Actions 37883868392](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37883868392) job 113669391783 COMPLETED SUCCESS**: compileall PASS; **142/142 combined S01–S15 unit tests PASS** (`Ran 142 tests in 0.209s`), native `PASS_NATIVE_S15_MANUAL_FULL_DWM_REFRESH_AND_REVOCATION`: **three repeated 4-old-DWM-freed → 4-native-DWM-reregistered** cycles, grid+order preserved, cache empty/recovery, stale PID refused, revoked UI command refused, register/unregister balance PASS.
- Same production code commit S10 native 37883811742, S11 DWM 37883811596, S12 three-source 37883811690, S13 adaptive 37883811878, S14 grid/order 37883811757 and Stage S combined source 37883811678 **all SUCCESS**.
- New docs/tasks/S15.md, docs/source/S15_C15_DWM_FULL_REFRESH.md, docs/source/S15_MODEL.json, append-only STATE.md/PROJECT_STATUS.md. PLAN, frozen binary, license shell, game scanner, HWND reader, other tabs, user spelling Dồn and Proxy exclusion unchanged.
- **STATUS S15_NATIVE_WINDOWS_FULL_DWM_REFRESH_142_TESTS_PASS_REAL_GAME_NOT_RUN.** Windows test-owned HWND success does NOT prove actual game-positive preview/pixel parity, original callback immediate scan behavior, live entitlement, other feature tabs or releasable Windows EXE.
- **NEXT_ACTION on CONTINUE S16:** Read LIVE PLAN.md/STATE.md, check docs/tasks/S16.md first, inspect original C16 and currently working Start. Analyze/implement narrow `Đóng hết` real WM_CLOSE behavior ONLY with rigorous HWND/PID and selected authorized Start guards; native CI must close exclusively test-owned Windows, never Thần Long; document original confirmation and post-close immediate refresh as UNKNOWN. Do not invent crash-handler kill, force terminate real game, Proxy feature, server claims or UI that only pretends to work. Keep all 142 tests and working S01–S15 untouched.


## S16 VERIFIED — C16 AUTH-GUARDED WM_CLOSE FOR REAL TEST-OWNED WINDOWS / 163 TESTS PASS
- CONTINUE started at live S15 NEXT_ACTION, read PLAN.md/STATE.md/PROJECT_STATUS.md and C16/C02/C06 plus actual Start source; checked docs/tasks/S16.md absent; did not rewrite S01–S15, archived binary or Proxy. C16 exact original: visible Đóng hết, _close_all_preview_windows/_close_all, shared close_all_game_windows with PostMessage(WM_CLOSE) (NOT main-game process force kill).
- Added **src/close_windows.py** real native PostMessageW(WM_CLOSE=16), cautious per-HWND/PID process/executable/class/title, top-level and visible verification, duplicate/invalid cache fail-closed, PID recheck immediately pre-post. Existing **src/start_tab.py** gains actual functional `Đóng hết` ttk button with E03 selected/authorized/visible Start gate, reads only S09 immutable cache, shows **WM_CLOSE sent not actual exit**. No post-close forced preview refresh (C16 UNKNOWN), no UnityCrashHandler forced cleanup (separate original path NOT_IMPLEMENTED), no game-memory reading or Ctrl/Proxy changes.
- New tests/test_s16.py **21 unit cases**; tools/S16_WINDOWS_TEST_OWNED_CLOSE_SMOKE.py, .github/workflows/s16-native-wmclose.yml. Test fixture *hard asserts* all native posts are to its own three real test-created Win32 top-level HWNDs. Its test-only identity shim simulates game executable/class only for explicitly test-owned HWND and is not production.
- First implementation commit **e1d0713b05784a1190e8dc2fe81dbe0014b79f00** CI 37884562214 **FAILED** native due solely to intentionally withdrawn S01 Tk shell in test: `winfo_viewable` blocked the test's own click; same run 163/163 unit PASS. Corrected test fixture visibility with existing S10/S14 `position_window_top_right`, commit **bd0678f6cb7170743d11019b69b252e9bd8a1892**.
- **ACTUAL Windows Python 3.10 [run 37884623539](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37884623539), job 113671723160, COMPLETED SUCCESS**: compileall PASS, **163/163 unit S01–S16 tests PASS** (`Ran 163 tests in 0.142s`), native `PASS_NATIVE_S16_TEST_OWNED_WM_CLOSE_WITH_AUTH_PID_GUARDS`: 3 real test HWNDs posted exactly WM_CLOSE 16 and Tk WM_DELETE_WINDOW callbacks fired, all 3 native HWND destroyed; separate unrelated HWND survived, fake identity refused, second click with stale snapshot posted ZERO further messages, S09/S13 cleans previews only when new cache available; permission revoked => Info and no further close.
- Same implementation code regressions all COMPLETED SUCCESS: Stage S source 37884562313, S10 37884562274, S11 37884562195, S12 37884562223, S13 37884562299, S14 37884562273, S15 37884562229.
- New docs/tasks/S16.md, docs/source/S16_C16_WMCLOSE_SAFETY.md, docs/source/S16_MODEL.json; append-only STATE.md/PROJECT_STATUS.md. PLAN, original ZIP, existing good code, Info authorization service and no-Proxy rule unchanged.
- **STATUS S16_NATIVE_TEST_OWNED_WMCLOSE_163_TESTS_PASS_GAME_NOT_RUN.** Native proof is only test-owned Tk, not actual Thần Long client; unknown original post-close refresh/confirmation, unimplemented UnityCrashHandler cleanup, original signed server auth and full product EXE still NOT_RUN/NOT_IMPLEMENTED.
- **NEXT_ACTION on CONTINUE S17:** reread live PLAN.md/STATE.md and check docs/tasks/S17.md; study original C18 with C06/C08 before implementing narrow **Đồng bộ các cửa sổ** layout sync native slice. Never invent original worker cadence/initial ON state/exact grid arithmetic/max-limit comparator. Test on real *test-owned* HWNDs only; do not confuse with C19 keyboard/mouse sync, do not develop Proxy; keep all 163 tests.


## S17 VERIFIED — C18 BOUNDED NATIVE LAYOUT SYNC / 187 TESTS PASS
- Recovered from LIVE S16 NEXT_ACTION after PLAN/STATE/C18/C06/C08. No S17 task document existed. C18 original: real "Đồng bộ các cửa sổ" layout toggle, worker cache, master-first, grid defaults 3x4 and SetWindowPos, server-backed window limit. Original exact grid geometry, original C18 cadence, initial state, limit comparator and C19 coupling UNKNOWN, explicitly not reconstructed.
- New src/layout_windows.py: REAL target-validated native Win32 SetWindowPos (SWP_NOSIZE|SWP_NOZORDER|SWP_NOACTIVATE), strict HWND/PID/process/class/title, verified max_windows, preflight full batch. LOCAL S17 policy: master width/height plus 8px pitch, move only, default off, refuse out-of-screen geometry. Native worker uses immutable S09 cache; S13 UI maintenance triggers retry only; no Tk worker mutation. Revoke/stop event guard prevents late moves.
- src/start_tab.py implements actual toggle; src/shell.py supplies ONLY verified PermissionSnapshot.max_windows, never fallback 999. Historic S02 unconstructed shell mocked fixture compatibility restored; S10 outdated prohibition of now-real C18 toggle narrowed without enabling C19/input or game activation. tests/test_s17.py **24** new unit cases and actual Windows test-owned HWND native smoke/workflow added.
- Initial CI failed S02/S10 compatibility assumptions and was corrected; **Windows run 37887093950 COMPLETED SUCCESS**, compileall PASS, **187/187 unit tests PASS** and PASS_NATIVE_S17_TEST_OWNED_LAYOUT_SYNC_REVOKE with FOUR real test-owned Win32 HWNDs, manual displacement recovery, unrelated HWND not moved, size preserved, max-window authorization and revocation STOP/no late actions.
- Final same-code implementation commit dc4921fac73a7d232d817189ba5d509dd896170a: ALL NINE Windows workflows SUCCESS: S10 37887172714; S11 37887172750; S12 37887172677; S13 37887172668; S14 37887172726; S15 37887172698; S16 37887172703; S17 37887172760; Stage S source 37887172697.
- Files added docs/tasks/S17.md, docs/source/S17_C18_LAYOUT.md, docs/source/S17_MODEL.json; STATE/PROJECT_STATUS append-only. PLAN/original binary, user Dồn spelling and do-not-develop Proxy unchanged. Actual game/real license server/full EXE NOT_RUN/NOT_BUILT.
- **NEXT_ACTION on CONTINUE S18:** reread PLAN.md/STATE.md, check docs/tasks/S18.md, inspect original C05/C08. Implement functional Cột/Hàng grid adjustment and real master selection on current S17 native layout, persist settings only as source-supported, mark original +/- bounds and exact C06 formula UNKNOWN. Native test test-owned HWND; keep 187 tests, don't develop C19 keyboard/mouse or Proxy.


## S18 VERIFIED — C05 MASTER RADIO + C08 PERSISTED GRID CONTROLS / 210 NATIVE WINDOWS TESTS PASS
- Continued from live S17 NEXT_ACTION, read PLAN.md/STATE.md/C05/C08/C06 and actual source/settings_store, checked docs/tasks/S18.md absent. Original C05 verifies dynamic radiobutton master backed by HWND/PID, not saved in settings; original C08 verifies Cột/Hàng +/- grid 3x4 default and Settings.grid_cols/grid_rows in APPDATA/TLMTool/settings.ini. Exact original +/- min/max, master auto-selection fallback and C06 geometry remain UNKNOWN.
- New src/grid_master.py: reuse atomic E05 settings store; preserve unrelated keys/backup, strict ini numeric validation, local safety dimensions 1..12 clearly NOT original bound. MasterSelection uses (HWND,PID), rejects reused/stale identities; local first-discovered fallback when current dies is NOT original guaranteed behavior. Master is runtime only and never persisted.
- Existing src/start_tab.py: four REAL ttk +/- controls with live Cột/Hàng labels/persistence; dynamic actual C05 ttk.Radiobutton group, keeps HWND/PID master identity in selection, source titles from current S09 cache only (RoleName not yet available), feeds native S17 worker. Grid or master changes cancel older layout generation, layout remains authorized/active. No C19 input, fake names, forced Win32 injection or Proxy.
- Historical tests/test_s10.py updated narrowly for now-real _on_master_change callback; old S17 native smoke updated to invoke actual new Master radio rather than manually set internal property. New tests/test_s18.py **23 unit cases**, tools/S18_WINDOWS_GRID_MASTER_SMOKE.py and .github/workflows/s18-native-master-grid.yml.
- **ACTUAL Windows Python3.10 [GitHub Actions S18 run 37888218013](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37888218013) COMPLETED SUCCESS**: compileall PASS, **210/210 unit tests PASS** (Ran 210 tests in 0.234s). Real Win32 four TEST-OWNED HWNDs: defaults 3x4; actual +/- controls changed 2x2 and persisted; native layout rebuilt 3x3 while running; real master radio switched native HWND index0; source sizes preserved; unrelated window unchanged; user manual move corrected; verified test limit3 refused four/max4 allowed; rights revoke stopped worker/no late moves; no master persisted. Native S17 smoke rerun PASS in S18 workflow.
- All same-implementation HEAD **b6adf2c8aa71f34064533fcc467fb583ec715204** workflows COMPLETED SUCCESS: Stage-S 37888217990, S10 37888218099, S11 37888218101, S12 37888217997, S13 37888218042, S14 37888218020, S15 37888218026, S16 37888217987, S17 37888218065, S18 37888218013.
- New docs/tasks/S18.md, docs/source/S18_GRID_MASTER_MODEL.md, docs/source/S18_MODEL.json and append-only STATE/PROJECT_STATUS. Original binary/PLAN, user Dồn naming, no-Proxy directive, earlier tested source untouched. Actual Thần Long runtime, real RoleName/HP, signed server/auth, final EXE and exact original pixel/behavior parity NOT_RUN/UNKNOWN.
- **NEXT_ACTION on CONTINUE S19:** read LIVE PLAN.md/STATE.md, verify docs/tasks/S19.md first; inspect C19/C05 and S18. Build only verified testable C19 groundwork: master-client/slave-client size-aware coordinate transforms, serialized down/up queue and watchdog/permission stop state using TEST-OWNED targets. No fabricated original WM_MY_SYNC_KEY payload, listener activation, background input bypass, fake functioning button, or Proxy. Preserve 210 tests and previous native Windows controls.


## S19 VERIFIED — C19 CLIENT-RELATIVE INPUT FIFO MODEL, NATIVE CLIENTRECT TEST-OWNED / 239 TESTS PASS
- Continued from S18 LIVE `NEXT_ACTION S19` after reading PLAN.md, STATE.md, C19/C05/C08, current S18 and checking docs/tasks/S19.md absent. Built only new narrow **src/input_sync_core.py**; no existing production source/tabs rewritten, no user-unrequested physical mouse capture/hook, C19 fake button or Proxy.
- Original C19 verified: selected master client coordinate scaling by slave client RECT; click down/up serialized queue, C19-only 1.5s re-block keepalive (NOT C18), ~10s slave stale-lock watchdog; master change stops/unlocks input. Exact original WM_MY_SYNC_KEY payload, listener startup, throttle, retry, rounding and DLL protocol **UNKNOWN**.
- Source **InputSyncModel** is PURE safe explicit-sink-only planner: valid S09 snapshot, positive max-window bound, game identity/HWND/PID and master checks; proportional **LOCAL FLOOR/CLAMP** client mapping; serialized L/R/M down/up enqueue/dispatch with per-item explicit identity+permission callbacks, stale/permission failure clears whole queue, watchdog after 10s clears MODEL logical pressed state (NOT actual DLL unlock), Master change always stops without auto-start. Read-only **NativeClientRectReader** actually uses GetClientRect and rechecks HWND/PID; DOES NOT SEND input, register listeners or native lock slaves.
- New tests/test_s19.py **29 tests** + real Windows native test-owned fixture tools/S19_WINDOWS_CLIENT_FIFO_SMOKE.py; new .github/workflows/s19-native-input-model.yml. `src/start_tab.py` unchanged, no fake C19 functional button.
- **ACTUAL Windows Python3.10 [S19 run 37889666893](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37889666893), job 113687490762, COMPLETED SUCCESS**: compileall PASS; **239/239 all Stage S unit tests PASS** (Ran 239 tests in 0.233s, OK), **PASS_NATIVE_S19_WIN32_CLIENTRECT_TEST_OWNED_FIFO_REVOKE**. Three actual TEST-OWNED Tk top-level HWND client sizes 280×190,410×260,360×310 observed by real Win32 GetClientRect; master→two slaves mapped to distinct scaled positions (136,64),(119,76); FIFO real Tk callback order DOWN A/DOWN B/UP A/UP B; unrelated HWND zero events; permissions revoke queued events discarded, stale HWND fails, watchdog logical state cleared, master switch no automatic restart. Test-only Tk event_generate is NOT native OS/game input. Artifact final delivered list includes additional fifth event from later intentionally stale-HWND scenario, unrelated to initial 4-event FIFO proof.
- Same implementation head **c2583e79ae75204dd8e7594fef03a3073c040799** [Stage S source run 37889666867](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37889666867) COMPLETED SUCCESS. No same-code separate S10–S18 native workflow reruns triggered because their production source remained untouched; do NOT falsely claim rerun.
- New docs/tasks/S19.md, docs/source/S19_C19_INPUT_MODEL.md, docs/source/S19_MODEL.json; append-only STATE.md and PROJECT_STATUS.md. PLAN, original frozen EXE, native preview/layout/shell, User Dồn spellings and no-Proxy directive unchanged.
- **STATUS S19_NATIVE_WIN32_CLIENTRECT_TEST_OWNED_FIFO_239_PASS_GAME_NOT_RUN.** No live Thần Long keyboard/mouse sync, no original custom key message, no slave DLL lock, signed server/heartbeat, real game or finished Windows EXE. This is independent tested groundwork, not whole C19 functional parity.
- **NEXT_ACTION on CONTINUE S20:** reread LIVE PLAN.md/STATE.md, check docs/tasks/S20.md; inspect original C20 3-HWND screenshot/model and S18/S19. Build combined native *TEST-OWNED* 3-HWND proof: physical game grid 3×4 is separate from preview grid 2x; master selected second preview while first card remains first; C17 preview reorder doesn't change master; S19 pure input model maps to exactly two slaves. Verify 3→2 changes, revoke/Info fallback, DWM/resource cleanup with native TEST HWND only. Original RoleName/HP/game payload/DWM screenshot parity UNKNOWN; don't add fake data or Proxy, preserve 239 unit tests.


## S20 VERIFIED — C20 COMBINED THREE REAL TEST-OWNED HWND INTEGRATION / 252 UNIT PASS
- Resumed LIVE S19 NEXT_ACTION; read PLAN.md/STATE.md, original C20, current S18/S19 source; docs/tasks/S20.md absent. Original locked C20 proves **physical 3×4 game layout separate from embedded 2x preview**, Master may be SECOND preview while first card remains first; preview arrows do not change Master; input Master targets exactly two other HWNDs. C20 itself was original static+visual, not reconstructed runtime.
- **NO S01–S19 production source modified.** New tests/test_s20.py (13 model integration unit cases), tools/S20_WINDOWS_THREE_HWND_COMBINED_SMOKE.py (actual three TEST-OWNED Win32/Tk top-level HWNDs + unrelated), .github/workflows/s20-native-three-hwnd.yml.
- S20 native test: 3 real DWM thumbnail sources and preview 2x tiles [(0,0),(0,1),(1,0)], genuine GUI Master radio selects 2nd preview HWND, independently active C18 Win32 SetWindowPos physical grid 3×4 places Master at (0,0). C17 real arrow reorders embedded preview while Master untouched and DWM source slot identities unchanged. S19 explicit-sink-only input MODEL reads actual native 180×135/205×160/220×180 client sizes and generates FIFO DOWN/DOWN/UP/UP to exactly two slaves; **NO native/game input ever sent**. 3→2 via destruction of test-owned HWND and cache reconciliation removes stale thumbnail, preserves surviving Master; S19 model refuses dead third HWND; revoke TEST token falls back Info, destroys remaining DWM native resources and stops layout with no late native move. Unrelated HWND unchanged, actual game RoleName/HP not invented.
- **ACTUAL Windows Python3.10 [S20 run 37890935461](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37890935461), job 113691475538, COMPLETED SUCCESS:** compileall PASS, **252/252 S01–S20 unit tests PASS** (Ran 252 tests / OK), native **PASS_NATIVE_S20_THREE_HWND_DWM_MASTER_LAYOUT_INPUT_MODEL**. Same implementation head 6776bee6898008260376e71f9a180280443a20a1 **Stage S source 37890935189 COMPLETED SUCCESS**. Prior native S10–S19 workflows were NOT rerun on S20 source commit because no existing production code changed; do not claim otherwise.
- New docs/tasks/S20.md, docs/source/S20_COMBINED_THREE_HWND.md, docs/source/S20_MODEL.json; append-only STATE/PROJECT_STATUS. PLAN, archived EXE, known good features, spelling **Dồn**, no-Proxy restriction untouched. Real game-positive, RoleName/HP memory reader, original C06 geometry, C19 live mouse/keyboard payload, signed server and production EXE still NOT_RUN/UNKNOWN.
- **NEXT_ACTION on CONTINUE S21:** reread LIVE PLAN.md/STATE.md; check docs/tasks/S21.md. Original **D01/D02** inventory and E01 startup audit already completed — DO NOT redo. Inspect src/TLMTool.py fail-closed entrypoint, E01 original exact Windows named **TLMTool_SingleInstance** mutex. Implement narrow Windows CreateMutexW/GetLastError/CloseHandle lifecycle guard with native Windows test-owned unique mutex names and two-process competition. Keep real Info server missing → startup blocked (no local fake auth or completed GUI), and original duplicate-instance message UNKNOWN. Preserve 252 unit tests and successful native S20 test; no C19 input, no Proxy.


## S21 VERIFIED — E01 NATIVE WINDOWS TLMTOOL SINGLE INSTANCE MUTEX / 267 UNIT PASS
- Continued LIVE S20 NEXT_ACTION; reread PLAN.md/STATE.md/E01/source `src/TLMTool.py`, checked docs/tasks/S21.md ABSENT. Original D01/D02/E01 audits already complete and NOT repeated. Original `CreateMutexW`, `GetLastError`, name `TLMTool_SingleInstance` recovered, but original exact comparison integer/dialog UNKNOWN. Standard Win32 error=183 is a **local implementation constant**, not claimed recovered source.
- New **src/single_instance.py**: real kernel32 CreateMutexW/GetLastError capture/CloseHandle, transparent fail-closed on null/unexpected error, duplicate process closes only its own temporary handle and refuses Tk startup, idempotent context-managed lifecycle, normal/exception handle cleanup. Narrow **src/TLMTool.py** update wraps existing `run_with_info_factory` Tk lifecycle in actual mutex before Tk creation. Production `main()` still **BLOCKED / return 2** until genuine InfoTab/server signed authorization exists. No synthetic auth grant or full product GUI.
- New **tests/test_s21.py (15 unit cases)**; tools/S21_WINDOWS_MUTEX_SMOKE.py spawns actual TWO Windows processes with isolated `S21_TEST_ONLY_<uuid>` named kernel mutex; NEVER touches the real name or user's tool. New workflow .github/workflows/s21-native-mutex.yml tests those plus same-commit S20 native DWM integration.
- **ACTUAL Windows Python3.10 [S21 run 37892342942](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37892342942), job 113695841265, COMPLETED SUCCESS**: compileall PASS; **267/267 S01–S21 unit PASS** (`Ran 267 tests / OK`), **PASS_NATIVE_S21_TWO_PROCESS_MUTEX_COLLISION_AND_CLEANUP**. First test-owned child holds registered mutex, second child receives 183 duplicate / exit23, incumbent still alive; after graceful release or forced test-child termination another separate process acquires. Isolated name independence proven; real TLMTool mutex never acquired by tests. **S20 combined three test-owned HWND native rerun PASS** on same commit 7213b817abe86dc61befcd5327e96efd83cd89e3. Stage S source [37892342899](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37892342899) COMPLETED SUCCESS same HEAD. Do NOT pretend S10–S19 dedicated workflows reran.
- New docs/tasks/S21.md, docs/source/S21_SINGLE_INSTANCE_MUTEX.md, docs/source/S21_MODEL.json; append-only STATE/PROJECT_STATUS. PLAN/original EXE, all earlier working features, "Dồn" spelling and **do-not-develop Proxy** all untouched.
- **STATUS S21_WIN32_TEST_ONLY_TWO_PROCESS_MUTEX_267_UNIT_PASS_REAL_GAME_NOT_RUN.** Actual original error message/condition and splash order UNKNOWN; no real signed Info/heartbeat, game-positive or complete product EXE.
- **NEXT_ACTION on CONTINUE S22:** reread LIVE PLAN.md/STATE.md, check docs/tasks/S22.md. Implement original E01-supported early startup diagnostics (`debug_logger.setup`, `faulthandler.enable`, `crash_fault.log`, `threading.excepthook`) **only where exact behavior can be tested**, with TEST-owned isolated temp logs and robust shutdown/release, keeping authentic Info/service blocker. Don't fabricate original logger format, splash order or force `os._exit`, don't touch Proxy/C19. Keep 267 tests and recheck native mutex/S20 Windows.


## S22 VERIFIED — E01 REAL WINDOWS STARTUP FAULTHANDLER + THREAD EXCEPTION LOGGING / 285 UNIT PASS
- Continued from LIVE S21 NEXT_ACTION: reread PLAN.md/STATE.md, original E01, current S21 mutex/bootstrap, verified docs/tasks/S22.md absent. D01/D02/E01 forensic reports already exist, NOT repeated. E01 original evidence includes debug_logger.setup, faulthandler.enable, crash_fault.log, threading.excepthook, traceback output. Exact log path/format and diagnostic vs splash instruction order UNKNOWN; original debug_logger tee source not reconstructed S22.
- NEW src/startup_diagnostics.py: fail-safe context writes to file using actual Python faulthandler and threading.excepthook. Default %LOCALAPPDATA%/TLMTool/crash_fault.log only **LOCAL RECONSTRUCTION POLICY**, original directory UNKNOWN. Own faulthandler enabled only if no pre-existing one, leaves old handler intact on exit; prior thread hook chained and restored if still owned; setup failure closes log and refuses startup. STARTUP_EXCEPTION / THREAD_EXCEPTION marker lines are S22 LOCAL, not original format. No fake logger framework or forced os._exit.
- Narrow src/TLMTool.py changes: S21 mutex context → S22 diagnostics context → existing Tk/Info factory path. On failure records traceback, restores own hook, closes log and releases mutex; no Tk on diagnostics setup failure. Original main() unchanged: BLOCKED with code 2 until genuine signed Info/server service exists. Historical tests/test_s21.py only adjusted 3 mock Tk fixtures with test no-op diagnostics so test suite never writes local user crash log.
- NEW tests/test_s22.py (18 cases), tools/S22_WINDOWS_DIAGNOSTICS_SMOKE.py, .github/workflows/s22-native-diagnostics.yml. Native Windows tests isolated S22_TEST_ONLY_<uuid> kernel mutexes and temp log files; real thread raises RuntimeError and both threading.excepthook/faulthandler write actual traceback; test-only Info construction fails and records error; bad writable file path prevents Tk; all three errors release mutex so independent later Windows process can acquire.
- **ACTUAL Windows Python3.10 [S22 run 37893509454](https://github.com/ngmthang-g/2222222222222222222222222222222222222/actions/runs/37893509454), job 113699507051 COMPLETED SUCCESS**: compileall PASS; **285/285 combined S01–S22 unit tests PASS**, native **PASS_NATIVE_S22_DIAGNOSTICS_THREAD_FAULT_MUTEX_RECOVERY**. Same HEAD 6498db1507a759239734bca7a2791b9aaf58e628 **S21 2-process mutex native PASS** and **S20 3-HWND DWM/layout native PASS**, independent S21 workflow 37893509414 SUCCESS and Stage S source 37893509490 SUCCESS. Do not claim dedicated S10–S19 native reruns.
- New docs/tasks/S22.md, docs/source/S22_STARTUP_DIAGNOSTICS.md, docs/source/S22_MODEL.json; append-only STATE/PROJECT_STATUS. Existing S01–S21 production except tiny bootstrap insertion untouched, PLAN/frozen original EXE, user 'Dồn', no Proxy unchanged.
- **STATUS S22_NATIVE_STARTUP_FAULTHANDLER_285_TESTS_PASS_GAME_NOT_RUN.** Signed Info/license/heartbeat, real game, original logger format/thresholds and product EXE still NOT_IMPLEMENTED/UNKNOWN/NOT_RUN.
- **NEXT_ACTION on CONTINUE S23:** reread LIVE PLAN.md/STATE.md, check docs/tasks/S23.md, consult ALREADY COMPLETED E06 logging forensic (no repeating static research), implement narrow original-evidenced debug_logger.setup stdout/stderr tee to isolated log/tlmtool.log with session markers. Exact MAX_SIZE/KEEP_SIZE numeric constants/partial-line timestamp formatting UNKNOWN: do not invent thresholds. Test own temporary paths and native Windows child processes, restores streams/handles on failure, preserves S22 diagnostic hook/S21 mutex and blocked real Info. No Proxy/C19 live input, keep 285 unit tests and native S22/S21/S20 PASS.


## S23 VERIFIED — E06 CENTRAL STDOUT/STDERR TWO-SESSION TEE / 306 WINDOWS TESTS PASS
- Continued from LIVE S22 NEXT_ACTION; read PLAN.md/STATE.md/E06 original forensic and actual S22 bootstrap, verified docs/tasks/S23.md absent. E06 evidence: `debug_logger.setup`, `_TeeWriter`, frozen-executable-local `log/tlmtool.log`, stdout/stderr console+append-file tee, original `sys._fl_tee_out/_err`, 60-equals session start/end separators, exe/Python metadata and atexit restore. Original numeric MAX_SIZE/KEEP_SIZE, partial-line timestamp and writer-lock mechanics UNKNOWN; NO fabricated default automatic trimming.
- NEW src/session_logger.py scoped SessionTee writes stdout/stderr to original streams plus one UTF-8 append-only session file, 60-equals Start/End markers with exe and Python, restores old global streams/backup attrs after normal or exceptional close, unregisters atexit callback, refuses double hook/unwritable log. Thread RLock only S23 local safety policy. `trim_if_needed` accepts TEST-caller explicit thresholds but production auto trim disabled until original numeric sizes found. Source checkout fallback for non-frozen and frozen original exe/local log dir distinguished.
- src/TLMTool.py narrowly nests startup `SingleInstanceMutex → SessionTee → StartupDiagnostics → Tk + genuine Info` (S23 LOCAL ordering; exact original micro-order UNKNOWN). `main()` still fail-closed returns 2 without genuine signed Info/server; no spoofed authentication. Historical tests/test_s21.py (3) and test_s22.py (2) mock Tk paths patched with no-op tee for test isolation. New tests/test_s23.py **21 unit cases**; tools/S23_WINDOWS_TEE_SMOKE.py and .github/workflows/s23-native-session-tee.yml.
- Initial source commit f0093ff141427bef4017b8747475bdf3fe1478a6 CI 37894850605 **FAILED** two NEW TEST fixtures only (missing mock __exit__, keep_size11 insufficient for requested penultimate line). Fixed test only commit **45d3adab874a6903cf2d5d6c7255ee535e9a7f4a**, no production logger change.
- **ACTUAL Windows Python3.10 [S23 run 37894932947](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37894932947), job 113704034986, COMPLETED SUCCESS**: compileall PASS, **306/306 S01–S23 unit tests PASS** (`Ran 306 tests in 0.325s`, OK), **PASS_NATIVE_S23_TWO_SESSION_STDOUT_STDERR_TEE_AND_FAILURE_CLEANUP**: independent Windows test-owned subprocess logged two sessions into same file, stdout+stderr console mirror, worker prints captured, bootstrap failure separate crash_fault.log, badlog denies Tk, independent process re-acquired unique S23_TEST_ONLY mutex after each. Same-commit S22 `PASS_NATIVE_S22_DIAGNOSTICS_THREAD_FAULT_MUTEX_RECOVERY`, S21 `PASS_NATIVE_S21_TWO_PROCESS_MUTEX_COLLISION_AND_CLEANUP`, S20 `PASS_NATIVE_S20_THREE_HWND_DWM_MASTER_LAYOUT_INPUT_MODEL`. Stage S source run 37894932886 COMPLETED SUCCESS. S21/S22 dedicated workflows on original failing f0093ff failed due shared unit suite; NOT rerun on final test-only 45d3ada commit (S23 workflow itself did rerun S22/S21 native), do not claim otherwise.
- New docs/tasks/S23.md, docs/source/S23_E06_SESSION_TEE.md, docs/source/S23_MODEL.json and append-only STATE.md/PROJECT_STATUS.md. Original frozen EXE/PLAN, existing S01–S22 functional production except narrow bootstrap, user "Dồn", Proxy prohibition unchanged. Real game, signed Info server, C19 real input and full product EXE remain NOT_RUN/NOT_BUILT.
- **STATUS S23_WIN32_NATIVE_TWO_SESSION_TEE_306_UNIT_PASS_GAME_NOT_RUN.**
- **NEXT_ACTION on CONTINUE S24:** reread LIVE PLAN.md/STATE.md, verify docs/tasks/S24.md absent/present and consult already completed E08 normal close/Destroy semantics and E07 ownership. Implement/test bounded REAL normal Tk root/widget <Destroy> tab-owner cleanup lifecycle, keep S20 DWM native resources and S23/S22/S21 reverse cleanup correct; no unproven normal-close game/forwarder kill, no heartbeat os._exit, no updater/reload conflation, no Proxy. Preserve 306 unit tests and native S23/S22/S21/S20 successes, append checkpoint.


## S24 VERIFIED — E08 NORMAL TK ROOT DESTROY / 315 UNIT AND NATIVE DWM CLEANUP PASS
- Continued from LIVE S23 NEXT_ACTION; reread PLAN.md/STATE.md/PROJECT_STATUS.md and already-complete E08/E07. docs/tasks/S24.md absent at task start. New user ZIP SHA256 **c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd** matches locked Gate A; main nested exe SHA256 **15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22**; neither rewritten.
- Exact gap: TabLifecycle.shutdown previously stopped only selected refresh, not all built owner shutdown services. src/shell.py now closes each built owner exactly once (continue if other owner fails), accepts normal root-only <Destroy>, prevents late authority/cache revival; no invented WM_DELETE_WINDOW, no global game or forwarder kill. src/start_tab.py closes before reconfiguring already-destroyed Tk controls, and avoids tile/label access after closed while stopping DWM/maintenance/worker. Production main() remains BLOCKED code 2 with missing real Info server.
- NEW tests/test_s24.py (9), tools/S24_WINDOWS_DESTROY_SMOKE.py, .github/workflows/s24-native-destroy.yml, docs/tasks/S24.md, docs/source/S24_NORMAL_DESTROY_LIFECYCLE.md and S24_MODEL.json. Existing S01–S23 code outside narrowly edited shell/Start untouched; PLAN, Dồn label and Proxy runtime prohibition unchanged.
- First S24 CI runs on b35823be / 47f7bbf **FAILED** 4 new wrong Info start/stop test fixture expectations and 1 S02 __new__ missing _closed attribute. Corrected only fixture expectations plus defensive getattr shell test seam in final source **d7c36af9056bea778576482568418f975e612697**.
- **ACTUAL Windows Python 3.10 [S24 run 37899237476](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37899237476), job 113717657783 COMPLETED SUCCESS**: compileall PASS; **315/315 S01–S24 units PASS**. Native **PASS_NATIVE_S24_TK_DESTROY_DWM_OWNER_LOG_MUTEX_CLEANUP**: actual test-owned Tk source HWND native DWM overlay registered; 2 separate root-first/app-first close paths each destroyed native destination HWND, stopped cache once, cleared DWM and prevented late grant; S23 tee log End marker and S21 isolated mutex released. Artifact **11601159680**.
- Same S24 workflow completed native reruns: **S23 PASS**, **S22 PASS**, **S21 PASS**, **S20 PASS**, **S10 PASS**. Independent Stage S source [37899237521](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37899237521) completed SUCCESS on same code. These prove only Windows test-owned resources, NOT actual game.
- STATUS **S24_NATIVE_WIN32_TK_DESTROY_315_UNIT_PASS_GAME_NOT_RUN**. Real Thần Long, original 11-tab visual/game/controller parity, signed Info/token/heartbeat and production Windows EXE still MISSING / NOT_RUN / NOT_BUILT. Original exact Tk destructor event order and normal forwarder cleanup UNKNOWN; forced heartbeat/updater not altered.

## S24 CHANGED FILES
- src/shell.py; src/start_tab.py
- tests/test_s24.py; tools/S24_WINDOWS_DESTROY_SMOKE.py
- .github/workflows/s24-native-destroy.yml
- docs/tasks/S24.md; docs/source/S24_NORMAL_DESTROY_LIFECYCLE.md; docs/source/S24_MODEL.json
- STATE.md; PROJECT_STATUS.md (append-only checkpoint)

## NEXT_ACTION on CONTINUE — S25
- Reread LIVE PLAN.md / STATE.md; check docs/tasks/S25.md first; consult ALREADY AUDITED F01/F04 Login tab game-folder path, E05 settings and current shell gate. Build the smallest genuinely operational Login folder-chooser/path persistence slice with native Windows test-owned filesystem path tests, authentic lazy/auth gating, no fake game login/captcha, no Proxy development, no new entitlement. Preserve 315 tests and S24/S23/S22/S21/S20/S10 native proofs; append next checkpoint.


## S25 VERIFIED — F01/F04 REAL LOGIN GAME-FOLDER PICKER / 331 WINDOWS UNIT PASS
- Continued exactly LIVE S24 NEXT_ACTION: reread PLAN.md, STATE.md; checked docs/tasks/S25.md ABSENT. Used already-audited F01 original screenshot and F04 exact EXE resolver, E05 atomic settings path. Did NOT modify frozen ZIP/PLAN or redo S01–S24 modules. Original executable name `Thần Long  Mobile.exe` (TWO spaces) preserved.
- NEW **src/login_path.py**: bounded direct/Game/one-parent/one-child F04 resolver, typed path+note, EXE presence recheck, saves only `Settings.game_dir` using existing E05 read_settings/write_settings; retains all other config keys and dated backup, invalid paths not written. Deterministic child ordering and immediate write-on-success explicitly LOCAL because original exact order/save microtiming UNKNOWN.
- NEW **src/login_tab.py**: real `ttk.LabelFrame` "Cấu hình game", blue original `tk.Button` "Chọn thư mục game" invoking real tkinter.filedialog.askdirectory, conditional path status, original invalid-path dialog; functional Cancel/invalid safety, reloads saved path after tab restart. Auth-gated lazy Login factory is **only installed by test fixture**; production still without genuine Info auth and `main()` returns 2. NO fake Mở game/Login/captcha/Proxy button, no spawn/injection.
- NEW tests/test_s25.py (16 cases), tools/S25_WINDOWS_LOGIN_FOLDER_SMOKE.py (real Tk and TEST-owned Windows file tree), .github/workflows/s25-native-login-folder.yml, docs/tasks/S25.md, docs/source/S25_LOGIN_PATH_FLOW.md + S25_MODEL.json.
- Initial Windows CI 37900085233 **FAILED native geometry only**, 331 units passed. tkinter ttk.LabelFrame content padding placed button at [7,28] within group. Corrected actual tab-relative button placement (not only test expectation) in source commit **c1f3ca9f651c50620e9336cc84f34e09b95202a0**, native screenshot-derived button rect is [11,24,135,24], LabelFrame group [6,10,428,65] on Login content frame.
- **ACTUAL Windows Python3.10 [S25 run 37900241256](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37900241256), job 113720838384 COMPLETED SUCCESS:** compileall PASS, **331/331 S01–S25 unit tests PASS**, **PASS_NATIVE_S25_LOGIN_CHOOSER_STORAGE_AUTH_GUARD**. Native Tk Button.invoke selects TEST-only installer parent, finds Game/EXE, writes/loads real temp INI, invalid path shows error and does not overwrite, Cancel leaves valid config, restarted widget reloads saved path; permission revocation hides Login and root destruction releases owners. No process launches, no Proxy. Artifact **11602351174**.
- SAME commit workflow S24/S23/S22/S21/S20/S10 native regressions all PASS. Full original Login page, F05 real suspended injection, game/RoleName/HP, signed license/heartbeat and product EXE remain NOT_IMPLEMENTED/NOT_RUN. **STATUS S25_NATIVE_WINDOWS_LOGIN_PATH_331_UNIT_PASS_GAME_NOT_RUN**.

## S25 CHANGED FILES
- src/login_path.py; src/login_tab.py
- tests/test_s25.py; tools/S25_WINDOWS_LOGIN_FOLDER_SMOKE.py
- .github/workflows/s25-native-login-folder.yml
- docs/tasks/S25.md; docs/source/S25_LOGIN_PATH_FLOW.md; docs/source/S25_MODEL.json
- STATE.md; PROJECT_STATUS.md (append-only)

## NEXT_ACTION on CONTINUE — S26
- Read LIVE PLAN.md and STATE.md, check docs/tasks/S26.md; inspect completed F05 and existing src/start_windows.py for overlap. Implement next smallest original-evidenced **F05 launch preflight + PID-bound Windows HWND selection** only if not already present, using test-owned native Windows windows, verified login-tab permission/account limit extra=1 and S25 validated `get_exe_path`. Do not add a fake Mở game, unsuspended launch, guessed inject/proxy/forwarder. Retain 331 tests and S25/S24/S23/S22/S21/S20/S10 native success, append checkpoint.


## S26 VERIFIED — F05 LAUNCH PREFLIGHT + PID-BOUND WIN32 HWND / 348 WINDOWS TESTS PASS
- Continued exactly LIVE S25 NEXT_ACTION: reread PLAN.md/STATE.md, checked docs/tasks/S26.md ABSENT; consulted F05 evidence and found S08 Win32 EnumWindows/GetWindowThreadProcessId/IsWindowVisible/GetClassNameW/SendMessageTimeoutW already fully present in src/start_windows.py. Reused it, did not rewrite any S01–S25 existing production code or PLAN.
- NEW src/login_launch_preflight.py: `check_open_game_preflight(snapshot,game,running_windows=...)` rejects unverified/no login_tab/blocked Info, invalid/unknown running count (DO NOT GUESS 0), `running_windows+1 > max_windows`, and F04 stale/missing exact `Thần Long  Mobile.exe`. Its ALLOW means PREFLIGHT ONLY, not launch or entitlement. `find_main_window_by_pid(pid, backend)` uses existing S08 native backend, read-only 150ms timed title, visible top-level HWND with matching real PID only; ranks UnityWndClass then title containing Thần Long then PID-window fallback and rechecks final HWND/PID; exact tie rank S26 LOCAL, original UNKNOWN. No spawn, injection, Proxy or fake buttons.
- NEW tests/test_s26.py (17), tools/S26_WINDOWS_F05_PREFLIGHT_HWND_SMOKE.py actual native Win32 with two TEST-OWNED Tk top-level HWNDs/PID and ephemeral test-only placeholder game EXE, .github/workflows/s26-native-f05-preflight.yml. No game or signed Info live.
- Implementation commit **ee6ab363f3c2b279c46a81ddee27161c0fe31ff9**. **ACTUAL Windows Python 3.10 [S26 run 37901273260](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37901273260), job 113724161744 COMPLETED SUCCESS**: compileall PASS, **348/348 S01–S26 units PASS**, **PASS_NATIVE_S26_F05_EXTRA_ONE_PID_HWND_FALLBACK_REUSE_GUARD**. Native demonstrated verified TEST-only rights and extra-one last window, unverified/revoked/overlimit denies, actual Tk native PID-target title preference, PID+1 refuse, fallback after preferred HWND destroyed and None after all test HWNDs destroyed. S25/S24/S23/S22/S21/S20/S10 native regressions SAME run all PASS; artifact **11602416816**. Independent Stage S source [37901273207](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37901273207) completed SUCCESS.
- S26 status **S26_NATIVE_WINDOWS_F05_PREFLIGHT_348_UNIT_PASS_GAME_NOT_RUN**. Product launcher still requires original suspend→inject→resume, authentically signed Info/heartbeat and actual window/emulator counts; game and Windows EXE product **NOT_RUN/NOT_BUILT**. No Proxy dev. S26 adds no UI buttons, no authorization, no actual login. Documentation files docs/tasks/S26.md, docs/source/S26_F05_PREFLIGHT_PID_FLOW.md and S26_MODEL.json.

## S26 CHANGED FILES
- src/login_launch_preflight.py; tests/test_s26.py; tools/S26_WINDOWS_F05_PREFLIGHT_HWND_SMOKE.py
- .github/workflows/s26-native-f05-preflight.yml
- docs/tasks/S26.md; docs/source/S26_F05_PREFLIGHT_PID_FLOW.md; docs/source/S26_MODEL.json
- STATE.md; PROJECT_STATUS.md (append-only checkpoint)

## NEXT_ACTION on CONTINUE — S27
- Reread LIVE PLAN.md/STATE.md and check docs/tasks/S27.md, inspect F05 original and existing S26 PID finder/S09 polling. Implement/test a bounded genuine F05 25s max **PID→HWND readiness handoff** starting from external real PID, with caller cancel and native Windows TEST-owned delayed Tk HWND; do NOT guess undocumented post-HWND stabilization seconds or real process spawn/inject. Preserve all 348 unit tests and S26/S25/S24/S23/S22/S21/S20/S10 native green; no fake UI or Proxy, update docs and checkpoint.


## S27 VERIFIED — F05 SERIALIZED CANCELLABLE PID→HWND 25S HANDOFF / 368 WINDOWS TESTS PASS
- Continued from LIVE S26 NEXT_ACTION: reread PLAN.md, STATE.md, original F05 and S26 `find_main_window_by_pid` + S09 Start polling; `docs/tasks/S27.md` ABSENT before edit. S08 native Win32 and S26 PID finder are reused without modification. No changes to original ZIP, PLAN or S01–S26 production.
- NEW `src/login_window_handoff.py`: bounded `wait_for_pid_window` after externally supplied PID, **F05-evidenced 25s MAX**; cancellation before/after Win32 scans, event-wake while waiting, no HWND fabrication, final IsWindow/visibility/PID recheck, typed FOUND/TIMEOUT/CANCELLED/errors. `SerializedPidWindowHandoff` serializes waiters with a cancellable shared lock; each waiter's 25s includes lock queueing. S27 100ms poll, 50ms lock retry are LOCAL, original unknown. No implementation of original unverified post-HWND stabilization seconds, no game spawn/inject/login or Proxy.
- NEW `tests/test_s27.py` **20** unit cases + `tools/S27_WINDOWS_PID_HWND_HANDOFF_SMOKE.py` real Windows Tk main-thread **delayed** TEST-owned HWND creation, background genuine S08 native Win32 discovery via S26 picker, wrong PID, destroyed/empty timeout, cancel; `.github/workflows/s27-native-pid-handoff.yml`; docs/tasks/S27.md and docs/source/S27_F05_PID_HANDOFF_FLOW.md + S27_MODEL.json.
- Implementation commit **78fe8fd835013caa5c045efd81c1b7ffee073db2**. **ACTUAL Windows Python3.10 [S27 run 37901945848](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37901945848), job 113726306489 COMPLETED SUCCESS**: compileall PASS, **368/368 S01–S27 units PASS**, **PASS_NATIVE_S27_DELAYED_HWND_25S_BOUNDED_CANCEL_TIMEOUT**; delayed real Windows TEST-only HWND found after multiple polls, foreign PID denied, destroyed window/short timeout denied, native cancellation promptly stopped. S26/S25/S24/S23/S22/S21/S20/S10 native reruns SAME run all PASS. Artifact **11602743621**. Independent Stage S source [37901945877](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37901945877) COMPLETED SUCCESS.
- **STATUS S27_NATIVE_WINDOWS_DELAYED_HWND_368_UNIT_PASS_GAME_NOT_RUN**. Original future real game PID supplier, signed Info/heartbeat, launcher suspend→inject→resume, known stabilization, full UI and product EXE **NOT_DONE/NOT_RUN/NOT_BUILT**. No Proxy runtime development.

## S27 CHANGED FILES
- src/login_window_handoff.py; tests/test_s27.py; tools/S27_WINDOWS_PID_HWND_HANDOFF_SMOKE.py
- .github/workflows/s27-native-pid-handoff.yml
- docs/tasks/S27.md; docs/source/S27_F05_PID_HANDOFF_FLOW.md; docs/source/S27_MODEL.json
- STATE.md; PROJECT_STATUS.md (append-only checkpoint)

## NEXT_ACTION on CONTINUE — S28
- Read LIVE PLAN.md/STATE.md and check docs/tasks/S28.md; inspect ALREADY AUDITED F05/D06 original launcher/safe-env/resources.dat contract and existing source for overlap. Implement next smallest evidenced **F05 safe launch environment / executable+x64 payload preflight** with TEST-owned files/environment, no guessed original whitelist, game spawn/injection, fake Mở game, license grant or Proxy runtime. Keep 368 unit and S27/S26/S25/S24/S23/S22/S21/S20/S10 native regressions green. Update docs/status checkpoint.


## S28 VERIFIED — F05/D06 X64 PE STRUCTURAL INPUTS + EXPLICIT WINDOWS ENV / 390 WINDOWS TESTS PASS
- Continued from LIVE S27 NEXT_ACTION, reread PLAN.md/STATE.md, checked docs/tasks/S28.md ABSENT; audited original F05/D06 and the existing S25/S26/S27 source, verified no safe environment/PE inspection module existed. No original ZIP, PLAN or S01–S27 production changes.
- NEW src/login_launch_inputs.py: `inspect_x64_pe` checks MZ/PE32+ AMD64 headers, executable image/EXE vs DLL bits, section metadata and file bounds READ-ONLY, rejects opaque/truncated x86/PE imposters; `build_audited_windows_env` requires caller-supplied explicit Windows essentials allowlist (original exact list UNKNOWN), adds `TLM_PROFILE` profile 1..5, filters Python/VirtualEnv/Proxy keys, requires local SystemRoot. `prepare_launch_inputs` consumes S26 preflight, validates game `Thần Long  Mobile.exe` non-DLL and ONLY active `package_root/data/resources.dat` x64 DLL; result is STRUCTURAL_INPUTS_ONLY_NOT_LAUNCHED; no guessed original cwd/flags, no spawn/inject/Proxy.
- NEW tools/S28_TEST_PE_FIXTURE.py produces synthetic TEST-only PE headers **NOT loadable game exe**, tests/test_s28.py (22 cases), tools/S28_WINDOWS_LAUNCH_INPUTS_SMOKE.py real Windows test-owned temp filesystem + native SystemRoot input, .github/workflows/s28-native-launch-inputs.yml. Existing modules unchanged.
- First source commit f1bc4ec5f2e9766b2e969565636a3b5879269404, Windows CI 37906449674 **FAILED 1 NEW TEST only**, because test compared Windows Path backslash against POSIX slash. Fixed just test assertion via Path.parts in final code commit **a58951c2e4e1b522dc0ceafadd4138c188b0e915**.
- **ACTUAL Windows Python3.10 [S28 run 37906555448](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37906555448), job 113741305612 COMPLETED SUCCESS**: compileall PASS, **390/390 S01–S28 units PASS**, **PASS_NATIVE_S28_F05_ENV_X64_PE_INPUTS_NO_LAUNCH**. Windows confirms structural synthetic x64 non-DLL/DLL, actual SystemRoot restricted env, exact active resources.dat, rejects x86/truncated file, denied/revoked fake-test-only authority. Same workflow native S27/S26/S25/S24/S23/S22/S21/S20/S10 ALL PASS, artifact **11603899644**. Independent Stage S source [37906555280](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37906555280) COMPLETED SUCCESS on same implementation.
- **STATUS S28_NATIVE_WINDOWS_X64_PE_ENV_390_UNIT_PASS_NO_GAME_LAUNCH**. Real signed Info, actual combined running game+emulator count, original env whitelist, cwd, injection, game and production EXE remain MISSING/UNKNOWN/NOT_RUN/NOT_BUILT. Synthetic structural PE is not proof of runnable game or payload. No Proxy runtime.

## S28 CHANGED FILES
- src/login_launch_inputs.py; tests/test_s28.py; tools/S28_TEST_PE_FIXTURE.py
- tools/S28_WINDOWS_LAUNCH_INPUTS_SMOKE.py; .github/workflows/s28-native-launch-inputs.yml
- docs/tasks/S28.md; docs/source/S28_F05_D06_LAUNCH_INPUTS_FLOW.md; docs/source/S28_MODEL.json
- STATE.md; PROJECT_STATUS.md (append-only checkpoint)

## NEXT_ACTION on CONTINUE — S29
- Read LIVE PLAN.md/STATE.md and check docs/tasks/S29.md. Inspect original E04 shared running EXE/emulator count and existing S08/S09 native Windows discovery to avoid duplication. Add genuine read-only TEST-owned native **game process/window count evidence**, explicitly mark that partial window view is NOT total combined game+emulator count and MUST NOT directly grant `check_account_limit` rights. No fake Mở game/injection or Proxy. Preserve 390 unit and S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native success; append checkpoint.


## S29 VERIFIED — E04 WIN32 TOOLHELP GAME IMAGE PID vs VISIBLE HWND / 409 WINDOWS TESTS PASS
- Continued exactly LIVE S28 NEXT_ACTION: reread PLAN.md/STATE.md, verified docs/tasks/S29.md ABSENT, inspected already-audited E04 and S08/S09 native window/poller + S26 guard. **E04 account limits require game EXE processes + emulators**, never simply visible HWND count; emulator identity/count rule still UNKNOWN. No duplicate S08 or changes to S01–S28 source.
- NEW src/running_count_evidence.py: read-only NativeWin32ProcessBackend calls Toolhelp32 Process32FirstW/NextW + CloseHandle for actual Windows process image/PID snapshot; F04 `Thần Long  Mobile.exe` (two spaces) name matched exactly casefold and PIDs de-duplicated. Existing S08 `discover_game_windows` supplies separate visible HWND list. RunningCountEvidence exposes **game_process_count** and **visible_hwnd_count** independently with typed failed-scan UNKNOWN, but ALWAYS `emulator_process_count=None`, `combined_running_count=None`, `is_authoritative_account_total=False` so cannot grant S26 window limit. `visible_hwnds_for_pid` adds diagnostics-only live HWND/PID recheck, not a game claim.
- NEW tests/test_s29.py (**19** units), tools/S29_WINDOWS_PARTIAL_COUNT_SMOKE.py and .github/workflows/s29-native-process-count.yml. Native smoke uses Win32 Toolhelp to count real runner `python.exe` PID and two real test-owned Tk HWNDs under SAME PID; misleading "Thần Long" test title never counted as game. S26 rejects missing total, real emulator count not guessed, destroyed HWND removed. No actual game, Proxy, process spawning or injection.
- **Implementation commit 2384a800fa3e23cfd40bc6264cff0fcdb19a7db9**. **ACTUAL Windows Python 3.10 [S29 run 37907306562](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37907306562), job 113743764797 COMPLETED SUCCESS**: compileall PASS, **409/409 S01–S29 units PASS**, **PASS_NATIVE_S29_TOOLHELP_PROCESS_VS_VISIBLE_HWND_INCOMPLETE_GATE**. Same run S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native all PASS; evidence artifact **11604554741**. Independent Stage S [37907306661](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37907306661) SUCCESS on same implementation.
- **STATUS S29_NATIVE_WINDOWS_TOOLHELP_PARTIAL_COUNT_409_UNIT_PASS_GAME_NOT_RUN**. Unknown original emulator process identities, signed Info, full count/real game/injection and production runnable EXE remain NOT_AVAILABLE/NOT_DONE. Source S01–S28, PLAN, original ZIP, Dồn label, user ban on Proxy runtime preserved.

## S29 CHANGED FILES
- src/running_count_evidence.py; tests/test_s29.py; tools/S29_WINDOWS_PARTIAL_COUNT_SMOKE.py
- .github/workflows/s29-native-process-count.yml
- docs/tasks/S29.md; docs/source/S29_E04_READONLY_RUNNING_COUNTS.md; docs/source/S29_MODEL.json
- STATE.md; PROJECT_STATUS.md (append-only)

## NEXT_ACTION on CONTINUE — S30
- Reread LIVE PLAN.md/STATE.md, check docs/tasks/S30.md, inspect already-audited emulator/LD and E04 original process-count names/rules. Only if evidence proves emulator image identities, add narrowly scoped native read-only emulator observation, otherwise record blocker/evidence and improve provenance/staleness without guessing. **NEVER** convert S29 partial window/process count into complete game+emulator total to authorize account opening. Preserve 409 units and S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native proof; update docs and checkpoint, no fake UI, real game inject/Proxy.


## S30 VERIFIED — E04 EMULATOR COUNT UNKNOWN + S29/S08 PROCESS/HWND PROVENANCE / 428 WINDOWS TESTS PASS
- Continued from LIVE S29 NEXT_ACTION: reread PLAN.md/STATE.md, verified docs/tasks/S30.md ABSENT. Audited already-completed P01/P02/P05/P06 emulator/LD docs, E04/C18/E09 process/counter evidence, D07 helper architecture. **No exact original Windows emulator host EXE name(s), clone-to-count rule or ADB guest PID→Windows process/account mapping proven.** Did NOT invent LD process names, zero-emulator default or grant account limit.
- NEW **src/running_count_provenance.py** read-only observation with **TWO S29 Toolhelp32 exact `Thần Long  Mobile.exe` PID snapshots enclosing ONE S08 native visible game HWND scan**. Immutable RunningSnapshotProvenance captures monotonic start/end, PID churn even if counts equal, HWND PID mismatch, scan failures and aging; exposes **diagnostic-only** process/HWND counts. `diagnostic_freshness` uses explicitly S30-LOCAL 2.0s age/span default, distinguishes fresh/aged/non-atomic/invalid-clock; no claims of original exact cadence. Emulator/combined account counts ALWAYS None; is_authoritative_account_total ALWAYS False. No S29/S08/S09/permission_guard change.
- NEW tests/test_s30.py (**19** units), tools/S30_WINDOWS_COUNT_PROVENANCE_SMOKE.py true Windows Toolhelp + native S08 HWND/Tk TEST-owned process evidence, .github/workflows/s30-native-provenance.yml; docs/tasks/S30.md, docs/source/S30_E04_PROVENANCE_STALENESS.md and docs/source/S30_MODEL.json.
- Implementation commit **9a1fdb31f03639534f033381f68dba0a681107d1**. **ACTUAL Windows Python3.10 [S30 run 37907996507](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37907996507), job 113746024936 COMPLETED SUCCESS**: compileall PASS, **428/428 S01–S30 unit tests PASS**, native **PASS_NATIVE_S30_DOUBLE_PROCESS_SCAN_STALE_SAFE_GATE**. Native confirms two real Process32 snapshot reads, actual HWND/title not spoofing game PID, staleness at 3s, partial aggregate rejects S26 preflight. SAME workflow S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native ALL PASS; artifact **11605510692**. Independent Stage S source [37907996521](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37907996521) SUCCESS on same source.
- **STATUS S30_NATIVE_WINDOWS_DOUBLE_SNAPSHOT_428_UNIT_PASS_EMULATOR_UNKNOWN**. Android guest serial/aid and guest PID not verified Windows host process-account counts; genuine Info/heartbeat, game suspended injection and product EXE NOT_DONE. PLAN/original ZIP/S01–S29 working source/Dồn untouched. Proxy runtime remains excluded.

## S30 CHANGED FILES
- src/running_count_provenance.py; tests/test_s30.py
- tools/S30_WINDOWS_COUNT_PROVENANCE_SMOKE.py; .github/workflows/s30-native-provenance.yml
- docs/tasks/S30.md; docs/source/S30_E04_PROVENANCE_STALENESS.md; docs/source/S30_MODEL.json
- STATE.md; PROJECT_STATUS.md (append-only)

## NEXT_ACTION on CONTINUE — S31
- Read LIVE PLAN.md and STATE.md, check docs/tasks/S31.md; inspect P02/P05 original emulator identity and E04 permission/count boundaries, plus S29/S30 modules. If original Windows emulator count still unproven, implement only **read-only, non-authoritative ADB device/serial identity evidence** with duplicate aid/clone risks and stale/not-connected status; DO NOT turn it into game+emulator account total, execute game, auto-start ADB server or develop Proxy. Preserve **428** units and S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native PASS, append checkpoint with exact NEXT_ACTION.


## S31 VERIFIED — P02/P05 OFFLINE ADB SERIAL/CLONE IDENTITY PROVENANCE / 450 WINDOWS TESTS PASS
- Continued exact LIVE S30 NEXT_ACTION: reread PLAN.md, STATE.md, checked docs/tasks/S31.md ABSENT; audited original P02 ADB serial/aid/hwid/IP/guest PID and P05 Train LD UI row-by-aid vs per-serial commands, plus E04 running-count auth boundary. Original Windows emulator HOST EXE image/counter rule remains UNKNOWN, no guessed emulator count/permissions.
- NEW **src/adb_identity_evidence.py** pure **offline parser of already-captured adb devices text**, with optional caller-supplied GuestIdentityHint (aid/hwid/guest IPv4/guest game PID). Preserves device/offline/unauthorized, invalid/no-capture states, duplicate serials and clone aid/hwid/IP collisions, unique reverse serial only with fresh unambiguous online records, possible aid→new serial `POSSIBLE_ONLY_NOT_VERIFIED` (not an auto-rebind). **30s capture diagnostic TTL S31 LOCAL, not original P02 5min aid cache.** No subprocess, real ADB call/server start, Frida/game access, emulator-account count or combined grant: account+emulator totals None permanently.
- NEW tests/test_s31.py (**22** cases), tools/S31_WINDOWS_OFFLINE_ADB_IDENTITY_SMOKE.py Windows test-owned captured text + genuine Win32 Toolhelp `python.exe` own PID evidence, .github/workflows/s31-native-offline-adb-identity.yml; docs/tasks/S31.md, docs/source/S31_ADB_IDENTITY_OFFLINE_FLOW.md + docs/source/S31_MODEL.json.
- Implementation commit **463d07b0fa24bb505830ce1a4b59eec1d27b038c**. **ACTUAL Windows Python3.10 [S31 run 37909199630](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37909199630), job 113749970955 COMPLETED SUCCESS**: compileall PASS, **450/450 S01–S31 units PASS**, native **PASS_NATIVE_S31_OFFLINE_ADB_CLONE_IDENTITY_NO_COUNT_GRANT**; logs prove duplicate aid/hwid, distinct guest IP, dup serial, offline/stale refused, no ADB server, no game, S26 missing total blocked. Same run S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native ALL PASS, evidence artifact **11606181801**. Independent Stage S source [37909199512](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37909199512) SUCCESS.
- **STATUS S31_NATIVE_WINDOWS_OFFLINE_ADB_IDENTITY_450_UNIT_PASS_REAL_ADB_NOT_RUN**. Original emulator host-count formula/real device connection and signed Info, game suspended injection/product EXE still NOT_DONE. No modification to S01–S30 functional code, frozen ZIP, PLAN or Dồn label; no Proxy runtime.

## S31 CHANGED FILES
- src/adb_identity_evidence.py; tests/test_s31.py
- tools/S31_WINDOWS_OFFLINE_ADB_IDENTITY_SMOKE.py; .github/workflows/s31-native-offline-adb-identity.yml
- docs/tasks/S31.md; docs/source/S31_ADB_IDENTITY_OFFLINE_FLOW.md; docs/source/S31_MODEL.json
- STATE.md; PROJECT_STATUS.md (append-only)

## NEXT_ACTION on CONTINUE — S32
- Read LIVE PLAN.md/STATE.md, check docs/tasks/S32.md and P02/P05 evidence, inspect S31 offline ADB parser for overlap. Add **independent per-hint provenance timestamps/expiry** for caller-supplied aid/hwid/IP/guest PID, and detect offline→online/reboot serial change without assuming cloned aid uniqueness or authorizing device control. Keep offline/no adb server/Frida execution; E04 authoritative emulator count remains UNKNOWN and never passed to S26 permission guard. Preserve **450** units + S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native green, update docs and checkpoint, no Proxy or fake game.


## S32 VERIFIED — P02/P05 INDEPENDENT PER-HINT TIMESTAMPS / OFFLINE RECONNECT SAFETY / 475 WINDOWS TESTS PASS
- Continued exactly LIVE S31 NEXT_ACTION: reread PLAN.md/STATE.md, checked docs/tasks/S32.md **ABSENT**; inspected original P02 and P05, src/adb_identity_evidence.py (S31). S31 capture age alone does not attest separately cached android_id/hwid/guest IPv4/Android guest PID age. Added new strict wrapper, no changes to S01–S31 working production.
- NEW **src/adb_hint_provenance.py**: immutable copied HintTimes per field per serial (no silently inferred hint timestamp), invalid/orphan/future/missing timestamp refused; `TimedAdbIdentity.assess` checks capture freshness + field-specific freshness + unique online serial; `unique_serial_for` requires EVERY online peer have a fresh same-field value before claiming even diagnostic uniqueness. `compare_adb_lifecycle` detects serial appears/disappears, offline→online, online→unavailable; fresh unique aid serial change is **POSSIBLE_ONLY_NOT_VERIFIED** only, never auto rebind. **30s S32-local TTL**, not original P02 ~5min aid cache.
- `emulator_account_count=None`, `combined_running_count=None`, `is_authoritative_account_total=False` always. S26 still refuses unknown total. No adb.exe, daemon, Frida, game, injection, Proxy, license granting or fake UI.
- NEW tests/test_s32.py **25** units, tools/S32_WINDOWS_HINT_PROVENANCE_SMOKE.py Windows test-owned **captured ADB fixture** with real read-only Toolhelp `python.exe` PID (NOT real LDPlayer) and .github/workflows/s32-native-hint-provenance.yml. Added docs/tasks/S32.md, docs/source/S32_HINT_PROVENANCE_FLOW.md, docs/source/S32_MODEL.json.
- **Implementation commit 1ea1d89d240434bb1dbd652bd3246cebea86e9f2**. **ACTUAL Windows Python3.10 [S32 run 37910397034](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37910397034), job 113753886562 COMPLETED SUCCESS**: compileall PASS, **475/475 S01–S32 Python units PASS**, native **PASS_NATIVE_S32_INDEPENDENT_HINT_TTL_RECONNECT_NO_AUTH**. Native proves stale AID with fresh capture and fresh IP, clone aid conflict, offline→online state without rebind, actual Windows test Python PID and S26 fail-closed. SAME workflow S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native ALL PASS, artifact **11606311244**; independent Stage S source [37910397059](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37910397059) SUCCESS.
- **STATUS S32_NATIVE_WINDOWS_HINT_FRESHNESS_475_UNIT_PASS_NO_LIVE_ADB**. Original Windows emulator host-process count / real signed Info / game launcher suspend-inject-resume / product EXE remain UNKNOWN/MISSING/NOT_RUN/NOT_BUILT; original ZIP, PLAN, Dồn and S01–S31 features untouched.

## S32 CHANGED FILES
- src/adb_hint_provenance.py; tests/test_s32.py; tools/S32_WINDOWS_HINT_PROVENANCE_SMOKE.py
- .github/workflows/s32-native-hint-provenance.yml
- docs/tasks/S32.md; docs/source/S32_HINT_PROVENANCE_FLOW.md; docs/source/S32_MODEL.json
- STATE.md; PROJECT_STATUS.md (append-only)

## NEXT_ACTION on CONTINUE — S33
- Read LIVE PLAN.md/STATE.md; check docs/tasks/S33.md; inspect P02/P05 original emulator connection/reboot and S31/S32 identity models. Implement the smallest evidence-based **offline per-serial observation epoch guard**, invalidating previously cached aid/hwid/IP/guest-PID hints after observed disconnect/reconnect or reboot epoch, without guessing clone identity or launching ADB. Preserve **475** tests and S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native PASS; append checkpoint with code paths, blockers, NEXT_ACTION. Still NO real ADB, Proxy, game injection or entitlement grant.


## S33 VERIFIED — P02/P05 OFFLINE PER-SERIAL EPOCH GUARD / 497 WINDOWS UNIT TESTS PASS
- Continued exact LIVE S32 NEXT_ACTION: reread PLAN.md/STATE.md, checked docs/tasks/S33.md ABSENT; audited original P02/P05 mutable ADB serial and clone aid/hwid, checked existing S31/S32 sources and tests. S32 field TTL does not block replay of a recently read aid/IP over a fresh serial reconnect/observed reboot.
- NEW `src/adb_serial_epochs.py` implements only read-only `advance_serial_epochs`: immutable per-serial state/generation/online-epoch boundary; first observed online requires hint strictly after captured boundary; observed offline/unauthorized/disappearance clears epoch and later online reopens new generation, explicit caller-observed reboot similarly invalidates same-serial hints. Rejects invalid/duplicate serial capture, markers, nonincreasing time and disconnected history; conservatively rebaselines after gaps. Reuses S31 parser/S32 hint TTL unchanged. Clone same-aid cannot auto-rebind. All account/emulator totals remain None; no licensing grant or ADB process starts. LOCAL diagnostic adaptation; exact original epoch algorithm UNKNOWN.
- NEW tests/test_s33.py (**22** unit cases), tools/S33_WINDOWS_ADB_EPOCH_SMOKE.py true Windows read-only Toolhelp self-PID + offline TEST-only ADB capture fixture, .github/workflows/s33-native-adb-epochs.yml. New docs/tasks/S33.md, docs/source/S33_SERIAL_EPOCH_FLOW.md, docs/source/S33_MODEL.json.
- Implementation commit **83325a82eb685f7b4d676647436eed50a6a3868f**. **ACTUAL Windows Python3.10 [S33 run 37911372037](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37911372037), job 113757060694 COMPLETED SUCCESS**: compileall PASS, **497/497 S01–S33 units PASS**, native `PASS_NATIVE_S33_OFFLINE_EPOCH_RECONNECT_REBOOT_NO_GRANT`. Native proves fresh subsequent hints, stale aid invalidated after offline→online / caller-observed reboot, no arbitrary remap, Win32 own python PID and S26 missing total DENIED. SAME run S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native all PASS. Artifact **11606572419**. Independent Stage S source [37911371950](https://github.com/ngmthang-g/2222222222222222222222222222222222222222/actions/runs/37911371950) SUCCESS.
- **STATUS S33_NATIVE_WINDOWS_OFFLINE_SERIAL_EPOCH_497_UNIT_PASS_REAL_ADB_NOT_RUN**. No actual ADB/LD/Frida, real game, Info license, emulator host EXE count, game injection or product EXE; no Proxy. Original ZIP, locked PLAN, Dồn and S01–S32 working feature source preserved.

## S33 CHANGED FILES
- src/adb_serial_epochs.py; tests/test_s33.py
- tools/S33_WINDOWS_ADB_EPOCH_SMOKE.py; .github/workflows/s33-native-adb-epochs.yml
- docs/tasks/S33.md; docs/source/S33_SERIAL_EPOCH_FLOW.md; docs/source/S33_MODEL.json
- STATE.md; PROJECT_STATUS.md (append-only)

## NEXT_ACTION on CONTINUE — S34
- Read LIVE PLAN.md/STATE.md, check docs/tasks/S34.md and already audited P02/P05/S31/S32/S33 identity modules. Add a narrow **OFFLINE read-only intake/facade** that enforces S31 parse → S32 per-hint timestamps → S33 per-serial epochs in sequence, exposing only the strict diagnostic result, never direct weaker S31/S32 serial lookup as a future action authority. Test replay, lost capture, duplicate clones, reconnection and unknown count. Preserve **497** units and S33/S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native PASS. Update docs/STATE exact NEXT_ACTION; no real ADB/server/game/injection, no Proxy or fabricated entitlement.


## S34 VERIFIED — STRICT OFFLINE S31→S32→S33 ADB INTAKE / 523 WINDOWS TESTS PASS
- Continued exactly LIVE S33 NEXT_ACTION; reread PLAN.md/STATE.md and original-audited P02/P05 + S31/S32/S33 source; docs/tasks/S34.md ABSENT. Existing lower-level diagnostic lookup paths could fail to enforce the newer S33 epoch: added one strict façade, **without editing any S01–S33 production code**.
- NEW **src/adb_offline_intake.py**: `OfflineAdbIntake.ingest` enforces S31 parse → S32 independent hint timestamps → S33 per-serial epoch, in fixed order. Accepts only already-captured caller-supplied ADB text/hints; errors, missing capture, stale/future capture, replay/nonmonotonic timestamp and invalid reboot marker reset past epoch to fail closed. `lookup` uses S33 strict `unique_serial_for`, returns only **UNIQUE_DIAGNOSTIC_ONLY**, may_control_device=False, never a command target. `replay` preserves frame order and reset behavior; immutable `IntakeReceipt` returns status/epoch event summary, no weaker S31/S32 raw wrappers. This is diagnostic software flow, **not Python module isolation/authentication**. Combined emulator/game count always None; S26 denies unknown account total.
- NEW tests/test_s34.py (**26** unit cases), tools/S34_WINDOWS_OFFLINE_INTAKE_SMOKE.py genuine Windows self-PID via S29 read-only Toolhelp + fake captured ADB fixture, .github/workflows/s34-native-offline-intake.yml; docs/tasks/S34.md, docs/source/S34_STRICT_OFFLINE_INTAKE_FLOW.md, docs/source/S34_MODEL.json.
- Implementation commit **452889d3f47478e096d9c52976589bbe30fd3565**. **ACTUAL Windows [S34 run 37913166723](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37913166723), job 113762921245 COMPLETED SUCCESS**: compileall PASS, **523/523 S01–S34 Python tests PASS**, native **PASS_NATIVE_S34_STRICT_OFFLINE_S31_S32_S33_INTAKE_NO_GRANT**. SAME workflow S33/S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native ALL PASS, evidence artifact **11607239078**; independent Stage S [37913166829](https://github.com/ngmthang-g/2222222222222222222222222222222222222222222/actions/runs/37913166829) SUCCESS on same source.
- **STATUS S34_NATIVE_WINDOWS_STRICT_OFFLINE_ADB_INTAKE_523_UNIT_PASS_GAME_NOT_RUN**. Real ADB/LDPlayer, signed Info, emulator process-count policy, game injection/login and product EXE still unavailable. PLAN, original ZIP, Dồn, S01–S33 working code unchanged; no Proxy runtime.

## S34 CHANGED FILES
- src/adb_offline_intake.py; tests/test_s34.py
- tools/S34_WINDOWS_OFFLINE_INTAKE_SMOKE.py; .github/workflows/s34-native-offline-intake.yml
- docs/tasks/S34.md; docs/source/S34_STRICT_OFFLINE_INTAKE_FLOW.md; docs/source/S34_MODEL.json
- STATE.md; PROJECT_STATUS.md (append-only)

## NEXT_ACTION on CONTINUE — S35
- Reread LIVE PLAN.md and STATE.md; check docs/tasks/S35.md. Inspect actual S01–S34 application source, bootstrap, Stage-T Windows build workflow and original UI/functional evidence to identify next smallest **real functional user-visible slice**, rather than repeating offline ADB identity safety wrappers. Implement only grounded functionality (or document a blocker and build prerequisites) without fake controls. Preserve **523** tests and S34/S33/S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native proof. Update docs/STATE with concrete changed files, blockers and NEXT_ACTION; no Proxy, unverified signed Info, fake game launch, or false product EXE build claim.


## S35 VERIFIED — E03 REAL SOURCE-BACKED START/LOGIN WIRED INTO GUARDED BOOTSTRAP / 533 WINDOWS UNIT PASS
- Continued exact LIVE S34 NEXT_ACTION; reread PLAN.md/STATE.md, docs/tasks/S35.md ABSENT. Audited actual src tree, E03 lazy tabs, F01/F04 Login path, existing S10–S20 Start native Win32 and S25 Login; Stage-T build workflow, Nuitka/PyInstaller spec, requirements/pyproject/build.bat ABSENT in LIVE repo. `src/TLMTool.py main()` still returns 2: real Info signed verifier absent, no licensed product GUI.
- NEW **src/source_backed_tab_builders.py** registers only three proven real E03 builders: caller's required Info, existing native TLMStartTab S10–S20, existing TLMLoginPathTab S25. Lazy factory creation, default real native Start and Tk folder picker, shared E05 settings path for Start grid and Login game dir. No fake tab factories, no Proxy.
- Narrow REQUIRED edit **src/TLMTool.py** `run_with_info_factory` passes `source_backed_tab_builders(info_factory)` to existing `TLMMainApp` instead of Info-only dictionary. Does not alter E03/permission guard, main() fail-closed refusal, S21 mutex/S22 diagnostics/S23 tee/S24 cleanup.
- NEW tests/test_s35.py (**10** units), tools/S35_WINDOWS_E03_REAL_TAB_SMOKE.py Windows REAL ttk Notebook, real Login Tk Button invokes test-local folder picker and persists `Settings.game_dir` with exact two-space Thần Long EXE name, real Start Windows-native background HWND worker; initially only Info built and shown; TEST-ONLY verified claim builds Start/Login lazily; revoke hides both, stops Start, returns Info, closes owners. Actual native Win32 enumeration recognizes unrelated Python Tk HWND without marking it game. No actual game/Info server.
- New .github/workflows/s35-native-real-tabs.yml, docs/tasks/S35.md, docs/source/S35_E03_START_LOGIN_BOOTSTRAP_FLOW.md, docs/source/S35_MODEL.json. No existing Start/Login/Info/PLAN/ZIP/Dồn functionality modified.
- Implementation commit **29158c846731c670597ee6f18667924e034ef201**. **ACTUAL [Windows S35 run 37918643711](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37918643711), job 113780909013 COMPLETED SUCCESS**: compileall PASS, **533/533 S01–S35 units PASS**, native `PASS_NATIVE_S35_E03_SOURCE_BACKED_START_LOGIN_LAZY_AUTH`. SAME workflow S34/S33/S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native all PASS. Evidence artifact **11609993006**. Separate Stage S 37918643727 SUCCESS; also S21 37918643739, S22 37918643789, S23 37918643712, S24 37918643782 workflows ALL SUCCESS after changed bootstrap.
- **STATUS S35_NATIVE_WINDOWS_E03_REAL_START_LOGIN_INTEGRATION_533_UNIT_PASS_REAL_GAME_NOT_RUN**. Missing signed Info/heartbeat and real product launch, majority tabs, full pixel parity, Stage T packaging and EXE still NOT_DONE. Proxy excluded. Original frozen ZIP, PLAN and Dồn preserved.

## S35 CHANGED FILES
- src/source_backed_tab_builders.py (NEW); src/TLMTool.py (narrow builder registration)
- tests/test_s35.py; tools/S35_WINDOWS_E03_REAL_TAB_SMOKE.py
- .github/workflows/s35-native-real-tabs.yml
- docs/tasks/S35.md; docs/source/S35_E03_START_LOGIN_BOOTSTRAP_FLOW.md; docs/source/S35_MODEL.json
- STATE.md; PROJECT_STATUS.md (append only)

## NEXT_ACTION on CONTINUE — S36
- Reread LIVE PLAN.md/STATE.md; check docs/tasks/S36.md. Audit actual Stage-T packaging prerequisites, `src/TLMTool.py`, and original Nuitka packaging evidence. Determine if a **truthfully labeled, fail-closed Windows build smoke** can produce a diagnostic standalone artifact (NOT a working product EXE) without fake signed Info or game success; otherwise record blockers/reproducible prerequisites. No prematurely named 2.1.2 rebuilt product. Preserve **533** units and all S35/S34/S33/S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native Windows tests, with checkpoint and exact next task. No Proxy.


## S36 VERIFIED — REAL WINDOWS X64 ONEDIR DIAGNOSTIC EXE BUILT / FAIL-CLOSED / 544 UNIT PASS — NOT PRODUCT
- Continued exactly LIVE S35 NEXT_ACTION; reread PLAN.md/STATE.md, checked docs/tasks/S36.md ABSENT, audited actual source/bootstrap, original E01/E06 Nuitka evidence and Stage-T build inventory. No packaging spec/requirements/product workflow previously available; public `src/TLMTool.py main()` **continues explicit status=2 auth refusal** pending genuine Info.
- NEW `requirements-build-s36.txt` pinned **PyInstaller==6.16.0** for Python 3.10 x64, `.github/workflows/s36-native-packaging-diagnostic.yml` creates REAL `--onedir --console` Windows EXE named **`S36_DIAGNOSTIC_FAIL_CLOSED_NOT_PRODUCT.exe`**. Entire `_internal` folder REQUIRED alongside exe. It is a deliberately non-product build proof, not the target EXE.
- NEW `tools/S36_VERIFY_STANDALONE.py`: validates S28 read-only PE x64 structure (not signing/loader verification), runs actual packed binary from test-local unrelated working directory with no PYTHONPATH/PYTHONHOME (normal and one unsupported fake auth flag), requires exact **exit 2 + S01 BLOCKED missing genuine Info message on stderr**. Writes SHA-256/returncode/status JSON. NEW tests/test_s36.py (**11** unit tests) reject missing/wrong EXE, fake PE, successful/other exits, bogus error text and failed process.
- **Implementation commit 84e1cf9ba65639b739ba1a90ca0c80960e4b6104**. **ACTUAL [S36 Windows run 37919314787](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37919314787), job 113783131705 COMPLETED SUCCESS**: compileall PASS, **544/544 S01–S36 units PASS**, real PyInstaller one-dir build PASS, packaged actual EXE ran and **blocked both attempts exit=2**, Windows PE AMD64 structural PASS. EXE size **1,364,592 bytes**, SHA-256 **2c6da1cf213d0a347b387c4a292976287ab9469526adcdebc1f61fe15042f39d** (EXE only, not folder hash). SAME CI S35/S34/S33/S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native all PASS. [Artifact **11610949148**](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37919314787/artifacts/11610949148) includes packaged one-dir and JSON. Independent Stage S [37919314788](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37919314788) SUCCESS.
- Added docs/tasks/S36.md, docs/build/S36_DIAGNOSTIC_BUILD.md and docs/source/S36_MODEL.json. S01–S35 working production modules, original ZIP, PLAN.md and Dồn left untouched; NO Proxy, actual game/LD/real Info or product EXE. S36 cannot claim 2.1.2 functional/UI/runtime parity or real signed entitlement.

## S36 CHANGED FILES
- requirements-build-s36.txt
- tools/S36_VERIFY_STANDALONE.py; tests/test_s36.py
- .github/workflows/s36-native-packaging-diagnostic.yml
- docs/tasks/S36.md; docs/build/S36_DIAGNOSTIC_BUILD.md; docs/source/S36_MODEL.json
- STATE.md; PROJECT_STATUS.md (append only)

## NEXT_ACTION on CONTINUE — S37
- Reread LIVE PLAN.md/STATE.md, check docs/tasks/S37.md. Audit existing F01/F02 original Login account-row/scroll/save contract and `src/login_tab.py` / E05 settings: implement only the smallest **genuine functional and original-backed Login account list control/storage slice** rather than invent login automation. Original `check` on-disk boolean token, legacy captcha `Có` migration and hidden-plan reconciliation are UNKNOWN: do NOT guess; preserve data where uncertainty exists. Prefer functional Tk 100-row selection/scroll/masking if independently supported and native testable. Keep 544 unit suite, packaged S36 FAIL-CLOSED diagnostic and S35/S34/S33/S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 Windows native success; checkpoint with exact NEXT_ACTION. No fake executable product claims, no credential leak, no Proxy runtime.


## S37 VERIFIED — F01 REAL TK 100 ACCOUNT ROWS IN-MEMORY / 558 WINDOWS UNIT PASS, ORIGINAL F02 ACCOUNTS UNTOUCHED
- Continued exact LIVE S36 NEXT_ACTION: reread PLAN.md/STATE.md, docs/tasks/S37.md ABSENT; original F01/F02/F03 confirmed Canvas/Scrollbar, 100 rows, custom select-all, 35px pitch, masked Entry; **on-disk check token UNKNOWN** and legacy captcha `Có` mapping UNKNOWN. No arbitrary serialization or secret logging permitted.
- NEW **src/login_account_rows.py** builds actual ttk.LabelFrame `Cấu hình tài khoản` with scrollable Canvas+Scrollbar, Tk `✅/⬜` selector buttons, 100 real Entry username + Entry password masked via `show="*"`, readonly captcha `Không/Tool/Proxy`, `Hiện mật khẩu` toggle across every row, memory-only snapshot. Header click selects all if any unchecked, else clears all. No inactive fake Login or Proxy action buttons, no writing account credentials to disk.
- NARROW integration **src/login_tab.py** constructs the S37 account group inside existing S25 path chooser and closes it on shutdown; existing game path selection/persistence and E03 Info auth guard untouched. **S37 does NOT load or save F02 legacy accounts**; fake or guessed `check` token/captcha transformation NEVER written. Password strings cleared on shutdown. Config legacy `accounts` preserved.
- NEW tests/test_s37.py (**14** unit cases), native TEST-owned Windows `tools/S37_WINDOWS_LOGIN_100_ROWS_SMOKE.py`, workflow `.github/workflows/s37-native-login-rows.yml`; docs/tasks/S37.md, docs/login/S37_ACCOUNT_ROW_IN_MEMORY.md, docs/source/S37_MODEL.json.
- Implementation commit **7ff35100beb52ab81f8e38d5e9be0a11c41229b3**; test-only native smoke improvements/fixes at `bd0eaf4`, `30594d6`, `6a57f45`, `919085f`. Initial native test failed because Tk `state` required `str(cget(...))` for comparison (and an intermediate literal escaped newline caused compile failure); both identified and corrected with no GUI production change.
- **ACTUAL Windows Python3.10 [S37 run 37920868815](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37920868815), job 113788199604 COMPLETED SUCCESS**: compileall PASS, **558/558 S01–S37 units PASS**, native `PASS_NATIVE_S37_REAL_TK_100_ROWS_IN_MEMORY_PRESERVE_LEGACY`; real Tk checks 100 entries/selectors, last row, all toggles, all masks, editable test-only strings, functional readonly captcha selections, scroll to row 100, no fake actions, legacy `Settings.accounts` unchanged before and after shutdown. S35/S34/S33/S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native all PASS, artifact **11611976959**. Separate S36 PyInstaller **NOT-PRODUCT** packaging on S37 functional source [37920408511](https://github.com/ngmthang-g/2222222222222222222222222222222222222222222/actions/runs/37920408511) SUCCESS, Stage S [37920408457](https://github.com/ngmthang-g/2222222222222222222222222222222222222222222/actions/runs/37920408457) and S25 native [37920408496](https://github.com/ngmthang-g/2222222222222222222222222222222222222222222/actions/runs/37920408496) SUCCESS.
- **STATUS S37_NATIVE_WINDOWS_REAL_TK_100_ROWS_558_UNIT_PASS_LEGACY_ACCOUNT_WRITES_BLOCKED**. No real login, captcha service, Proxy, original UI pixel parity, save format or product EXE. PLAN, original ZIP, other existing working modules and spelling Dồn unchanged.

## S37 CHANGED FILES
- src/login_account_rows.py NEW; src/login_tab.py narrow integration
- tests/test_s37.py; tools/S37_WINDOWS_LOGIN_100_ROWS_SMOKE.py; .github/workflows/s37-native-login-rows.yml
- docs/tasks/S37.md; docs/login/S37_ACCOUNT_ROW_IN_MEMORY.md; docs/source/S37_MODEL.json
- STATE.md and PROJECT_STATUS.md append-only

## NEXT_ACTION on CONTINUE — S38
- Read LIVE PLAN.md/STATE.md and docs/tasks/S38.md, inspect F02/F03 and S37 account Tk implementation. Implement **STRICTLY READ-ONLY** legacy `Settings.accounts` record loader/hydration with unknown `check` token and `Có` migration preserved, or document precise blocker if safe parsing cannot be proven. Malformed/ambiguous records must fail closed, never silently drop original data or leak password to logs, never write/normalize account storage or fake login/Proxy. Preserve **558** Python units and S37/S35/S34/S33/S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native green, reverify S36 packaged diagnostic remains fail-closed if production source changes. Append changed files/blockers/exact NEXT_ACTION, no Proxy.

## S38 VERIFIED — READ-ONLY F02/F03 LEGACY LOGIN HYDRATION / 575 WINDOWS UNIT PASS / NATIVE Tk PASS (NO REAL GAME)
- Continued EXACT S37 NEXT_ACTION, reread LIVE PLAN.md and STATE.md, F02/F03 original static account evidence and S37 implementation. docs/tasks/S38.md initially ABSENT; did not restart PLAN or edit original ZIP.
- NEW `src/login_account_legacy.py`: E05 read-only `Settings.accounts` reader and strict five-field immutable records `check_raw|username|password|captcha_raw|proxy_raw`, 100-row cap, no trimming password, no writer. Unknown check encoding is left opaque; legacy captcha `Có` is preserved literally, not guessed to Tool/Proxy/Không. Any malformed row, extra delimiter, unsupported captcha or >100 records BLOCKS ENTIRE LOAD (no partial account list). Sanitized statuses never print credentials.
- NARROW `src/login_account_rows.py` safe Tk hydration of validated username/password and readonly raw captcha including literal `Có`; unverified persisted check is shown `❔` (not misrepresented as true/false). Existing S37 in-memory selection/mask/unmask, 100 rows, S25 game picker preserved. `src/login_tab.py` calls the read-only loader only and displays a sanitized status footer; no account writer or Proxy runtime.
- NEW tests/test_s38.py (**17** cases), tools/S38_WINDOWS_LOGIN_LEGACY_READONLY_SMOKE.py (genuine Windows Tk, dummy accounts only), .github/workflows/s38-native-login-legacy-readonly.yml, docs/tasks/S38.md, docs/login/S38_READONLY_ACCOUNT_FLOW.md, docs/source/S38_MODEL.json. First workflow c97cf2c was accidentally wired to run S37 twice: this was detected and FIXED at **a64ad7de26c4912be1ad5803a138c7f5d952b7b1**, then ACTUAL S38-native executed.
- **VERIFIED [S38 Windows run 37922147950](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37922147950), job 113792375254 COMPLETED SUCCESS**: compileall PASS; **575/575 S01–S38 Python units PASS**; native `PASS_NATIVE_S38_READ_ONLY_F02_TK`; genuine Windows Tk demonstrates original legacy `Có` visibly UNMIGRATED, opaque check not guessed, user/password real Tk entries, original settings.ini byte-identical after UI and Destroy, malformed batch rejected with no partial load. Same workflow S37/S35/S34/S33/S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native regressions ALL PASS. **Evidence artifact 11612755873**; logs contain NO actual credential values.
- S36 diagnostic fail-closed packaging after changed production source (run 37921768692) SUCCESS, but **NOT A PRODUCT EXE**; no live Info signed token, game/LDPlayer, F06 login or Proxy runtime. Original frozen ZIP, PLAN.md, Dồn spelling and other source logic unmodified. UI pixel parity, true game-runtime parity, original check token and exact legacy `Có` migration still NOT_DONE.
- **STATUS S38_NATIVE_WINDOWS_F02_READONLY_HYDRATION_575_UNIT_PASS_ACCOUNT_WRITES_BLOCKED**.

## S38 CHANGED FILES
- src/login_account_legacy.py NEW
- src/login_account_rows.py; src/login_tab.py (narrow F02 read-only integration)
- tests/test_s38.py; tools/S38_WINDOWS_LOGIN_LEGACY_READONLY_SMOKE.py
- .github/workflows/s38-native-login-legacy-readonly.yml
- docs/tasks/S38.md; docs/login/S38_READONLY_ACCOUNT_FLOW.md; docs/source/S38_MODEL.json
- STATE.md and PROJECT_STATUS.md append-only

## NEXT_ACTION on CONTINUE — S39
- Reread LIVE PLAN.md and STATE.md, check docs/tasks/S39.md. Examine ORIGINAL frozen EXE F02 `check` serialized token and legacy `Có` conversion with direct static/approved-runtime evidence. Do NOT guess, automatically migrate or save if semantics remain unknown. If evidence insufficient, document the precise blocker and implement only the next smallest **genuinely original-backed Login F01 schedule/F09 or other verified real UI/function slice** with tests; no fake Login/Proxy buttons. Keep **575** unit tests, S38/S37/S35/S34/S33/S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native Windows green and S36 NOT-PRODUCT packaged diagnostic fail-closed. Preserve existing working features, no Proxy runtime, and update STATE with exact NEXT_ACTION.

## S39 VERIFIED — F02 ORIGINAL BINARY AUDIT + F09 PURE SCHEDULER CLOCK / 597 WINDOWS UNITS PASS / NO GAME ACTIONS
- Continued exact LIVE S38 NEXT_ACTION; reread PLAN.md/STATE.md, F02/F01/F09 original evidence and actual S38 code; checked docs/tasks/S39.md initially ABSENT. Original user ZIP `TLMTool_2.1.2(20261009-110340).zip` SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, inner `TLMTool.dist/TLMTool.exe` SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`: MATCH prior F02 specimen. Examined only original read-only bytes at 0x2b5f452 and 0x2b670db; constants validate 5-field schema and legacy Có presence, NOT the runtime checkbox serialized token or conversion expression. No original settings.ini inside ZIP; no credential export, no EXE execution.
- F02 checkbox storage token / legacy Có migration remains **EXPLICIT UNKNOWN**, S38 legacy reader/write-block unchanged.
- NEW `src/login_schedule_clock.py`: genuine testable **F09 pure deterministic daily next-occurrence/time model** from verified F09 compiled evidence. Strict `HH:MM` parser, locked defaults close 04:00/open 04:20, future today else tomorrow (no immediate past-event catchup on enable), `LoginScheduleClock.enable/disable/upcoming/poll/countdown`, typed due open/close events each once per poll cycle and move to next future calendar day, text countdown matching F09 source. F09 evidence worker check ~20sec and main-thread UI refresh ~1sec recorded, BUT no worker/real GUI/action dispatcher installed.
- Defensive non-originally-proven choices: equality at exact time considered passed, simultaneous due close before open, multi-day sleep emits max 1 event per kind, backward clock move fails closed. These are **NOT full original parity claims** and subject to later runtime proof.
- NEW tests/test_s39.py (**22** new tests), tools/S39_WINDOWS_LOGIN_SCHEDULE_CLOCK_SMOKE.py; .github/workflows/s39-native-login-schedule-clock.yml. NEW docs/tasks/S39.md, docs/login/S39_SCHEDULE_CLOCK_FLOW.md, docs/source/S39_MODEL.json.
- **ACTUAL [S39 Windows run 37924390875](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37924390875), job 113799729458 COMPLETED SUCCESS**: compileall PASS, **597/597 S01–S39 Python units PASS**, actual `PASS_NATIVE_S39_F09_CLOCK_ONLY_NO_ACTION`, genuine S38/S37 native Tk and S35/S34/S33/S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native regressions ALL PASS. Artifact **11613203123**.
- Separate S36 packaged diagnostic build on S39 `src/**` commit [37924218588](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37924218588) SUCCESS, but still **FAIL-CLOSED NOT-PRODUCT EXE**. No real signed Info, game login, HWND game close-all, Windows shutdown, runtime Tk scheduler checkboxes or false EXE product. Existing S01–S38 production code, original ZIP, PLAN and Dồn label unchanged.
- **STATUS S39_NATIVE_WINDOWS_F09_CLOCK_MODEL_597_UNITS_PASS_RUNTIME_DISPATCH_NOT_CONNECTED**.

## S39 CHANGED FILES
- src/login_schedule_clock.py NEW
- tests/test_s39.py NEW
- tools/S39_WINDOWS_LOGIN_SCHEDULE_CLOCK_SMOKE.py NEW
- .github/workflows/s39-native-login-schedule-clock.yml NEW
- docs/tasks/S39.md; docs/login/S39_SCHEDULE_CLOCK_FLOW.md; docs/source/S39_MODEL.json NEW
- STATE.md; PROJECT_STATUS.md append-only

## NEXT_ACTION on CONTINUE — S40
- Reread LIVE PLAN.md and STATE.md and check docs/tasks/S40.md. Audit F01/F09 schedule UI controls, original E05 per-key settings encoding, current S39 pure clock and verified F05/F06 real launch/close-all availability. Continue with smallest independently source-backed **functional** F09 scheduling integration only if real action callbacks are genuinely available; otherwise implement a source-backed schedule configuration/controller slice with strict no-action guards rather than fake game buttons/OS shutdown. Preserve 597 units, native S39/S38/S37/S35…S10 successes, S36 packaged diagnostic FAIL-CLOSED; original F02 legacy check/Có unknown, no account writes; no Proxy runtime. Record files changed/blockers and exact NEXT_ACTION.

## S40 VERIFIED — REAL F09/E05 READ-ONLY SCHEDULE CONFIG + S39 FUTURE DATE PREVIEW / 617 WINDOWS UNITS PASS
- Continued exactly LIVE S39 NEXT_ACTION, reread PLAN.md/STATE.md, original F01/F09 static schedule evidence, E05 parser, real F05/F06 availability, and current S39 implementation; docs/tasks/S40.md initially ABSENT. Current F05/F06 product handlers are NOT wired (only guarded preflight and launch inputs), genuine signed Info absent; therefore **no schedule GUI that deceptively starts game**, no unguarded OS shutdown or fake launcher.
- NEW `src/login_schedule_settings.py`: real read-only E05 [Settings] reader for original F09 keys `schedule_on`, `schedule_close`, `schedule_open`, `shutdown_after_close`. Strict preview of valid HH:MM using existing real S39 `LoginScheduleClock` (default close 04:00/open 04:20); unknown schedule/power Boolean persisted encodings retained as **opaque raw strings**, never coerced or treated as permission/action. Missing file -> DEFAULTS_ONLY disarmed; bad time/oversized unsafe raw token/INI parse -> sanitized BLOCKED. No write, no account-deserialization, no Proxy, no real game or PC shutdown. Original legacy multiline F02 `Settings.accounts` byte-identical in actual Windows smoke test.
- NEW 20 cases `tests/test_s40.py`; native `tools/S40_WINDOWS_LOGIN_SCHEDULE_SETTINGS_SMOKE.py`; .github/workflows/s40-native-login-schedule-settings.yml; docs/tasks/S40.md, docs/login/S40_READONLY_CONFIG_FLOW.md and docs/source/S40_MODEL.json.
- Initial full unit execution had SIX TEST-FIXTURE ERRORS: per-case temp config folder was recreated without `exist_ok=True` within one loop. **Fixed test fixture only** in `d0b368f68c367a2b71ed0bbabf3b7c2cd307601d`; no production code change. Separate E05 test file whitespace-normalization expectation was aligned to existing parser without changing its behavior. Initial failed workflows not claimed as passing.
- **ACTUAL [S40 Windows run 37925270259](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37925270259), job 113802576969 COMPLETED SUCCESS**: compileall PASS, **617/617 S01–S40 Python units PASS**, actual `PASS_NATIVE_S40_E05_F09_READONLY_CONFIG_CLOCK`; real test-owned Windows file with two legacy account records kept byte-identical, 04:00/04:20 next day preview correct and disabled/unknown tokens not interpreted; S39/S38/S37/S35/S34/S33/S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native regressions ALL PASS. Artifact **11613194482**.
- **S36 original FAIL-CLOSED NOT-PRODUCT diagnostic** packaged with S40 production source [run 37925025741](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37925025741) SUCCESS, but no real rebuilt game EXE. No real signed Info, real launcher/injection/login, game close-all, OS shutdown, F01 scheduling UI, or actual multi-game runtime parity. Previous S01–S39 production, original ZIP, PLAN and Dồn unchanged.
- **STATUS S40_NATIVE_WINDOWS_E05_F09_READONLY_617_UNITS_PASS_NO_REAL_ACTIONS**.

## S40 CHANGED FILES
- src/login_schedule_settings.py NEW
- tests/test_s40.py NEW
- tools/S40_WINDOWS_LOGIN_SCHEDULE_SETTINGS_SMOKE.py NEW
- .github/workflows/s40-native-login-schedule-settings.yml NEW
- docs/tasks/S40.md; docs/login/S40_READONLY_CONFIG_FLOW.md; docs/source/S40_MODEL.json NEW
- STATE.md; PROJECT_STATUS.md append-only

## NEXT_ACTION on CONTINUE — S41
- Reread LIVE PLAN.md and STATE.md, check docs/tasks/S41.md. Audit original F09 scheduling coordination, S39 clock/S40 settings, and actual F05/F06 action availability + genuine Info gate. Implement smallest provable real cancellation/controller or Tk-main-thread countdown slice only if properly functional, **without** mock product activation; scheduled open/close require real verified/authenticated handlers and must remain blocked otherwise. Keep opaque F09 flags, legacy F02 checkbox/Có unknown, no accounts writes, no Proxy runtime. Preserve **617** tests and S40/S39/S38/S37/S35…S10 native Windows successes, S36 NOT-PRODUCT packaged diagnostic fail-closed, and write exact changed files/blockers/NEXT_ACTION.

## S41 VERIFIED — F09 REAL Tk MAIN-THREAD COUNTDOWN PREVIEW / CANCELLATION / 643 WINDOWS UNIT PASS
- Continued exactly from **LIVE S40 NEXT_ACTION**: reread PLAN.md/STATE.md, F09/F01 original evidence, S39 pure clock, S40 read-only E05 config, real F05/F06 available source and Info gate. `docs/tasks/S41.md` was ABSENT at start. F05/F06 remain guarded preflight only, real signed Info unavailable. **No genuine scheduled open/close-all or OS shutdown dispatcher**; no fake active Login scheduler UI.
- NEW `src/login_schedule_countdown.py`: `TkScheduleCountdownPreview` uses a **real Tk.Label** on creator main UI thread and actual `Tk.after(1000, ...)` recurring visual refresh to render verified F09 `Tắt ... | Mở ...` remaining times from validated S40 settings/S39 daily clock. Preview is **explicitly requested only**, never automatically armed from unknown F09 stored `schedule_on` flag; shutdown-after-close opaque token never interpreted. On crossing due time the preview re-arms display to next day using pure S39 clock, discards all returned due events with **NO launch/close/poweroff action**. Renderer has `stop()`, `shutdown()`, `after_cancel`, generation counter invalidation of stale callbacks, creator-thread guard, and graceful Tk destroyed/clock rollback failure handling. No Tk widget integration in production Login tab because a working scheduled game action pipeline is absent; actual Tk preview proven in test-owned native smoke, not fake product UI.
- NEW `tests/test_s41.py` (**26** cases), `tools/S41_WINDOWS_LOGIN_TK_COUNTDOWN_SMOKE.py`, `.github/workflows/s41-native-login-tk-countdown.yml`, `docs/tasks/S41.md`, `docs/login/S41_TK_COUNTDOWN_PREVIEW_FLOW.md`, `docs/source/S41_MODEL.json`.
- **ACTUAL [S41 Windows run 37926526563](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37926526563), job 113806683345 COMPLETED SUCCESS**: compileall PASS, **643/643 S01–S41 Python unit tests PASS**, actual `PASS_NATIVE_S41_REAL_TK_F09_AFTER_PREVIEW_CANCEL`: real Windows Tk widget + actual after(1000) refresh to tomorrow, after cancellation works, initial unknown saved boolean does not automatically start any worker, test-owned original multiline-account settings.ini byte-identical. Real S40/S39/S38/S37/S35/S34/S33/S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native regressions ALL PASS. Artifact **11613529167**.
- Separate S36 **FAIL-CLOSED NOT-PRODUCT diagnostic** packaging on updated S41 source [run 37926357456](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37926357456) COMPLETED SUCCESS. Still **NOT A PRODUCT EXE**; no real Info server, F05 suspended launcher/F06 click-login, auto game actions, OS shutdown, schedule_on persisted token interpretation, real game runtime or pixel parity. Previously verified S01–S40 production source untouched, original ZIP and PLAN untouched; no Proxy runtime.
- **STATUS S41_NATIVE_WINDOWS_TK_F09_AFTER_CANCEL_643_UNITS_PASS_PREVIEW_ONLY**.

## S41 CHANGED FILES
- src/login_schedule_countdown.py NEW
- tests/test_s41.py NEW
- tools/S41_WINDOWS_LOGIN_TK_COUNTDOWN_SMOKE.py NEW
- .github/workflows/s41-native-login-tk-countdown.yml NEW
- docs/tasks/S41.md; docs/login/S41_TK_COUNTDOWN_PREVIEW_FLOW.md; docs/source/S41_MODEL.json NEW
- STATE.md; PROJECT_STATUS.md append-only

## NEXT_ACTION on CONTINUE — S42
- Reread LIVE PLAN.md, STATE.md and check docs/tasks/S42.md. Verify F09 original 20-second worker/event evaluation + cancellation semantics against S39–S41, and **real actual** F05/F06 authenticated game action availability. If still unavailable, implement next smallest source-backed **genuine 20-second cancellable event-evaluation coordinator with a fail-closed action gate**, test-owned only and explicitly NOT dispatching missing game launch/close-all; avoid unverified persistence token conversions, fake Login/Proxy controls, and PC shutdown. Ensure no unsafe duplicate event actions, cancellation/restart lifecycle, and preserve S41 real Tk and prior 643 units/S40–S10 native regression and S36 NOT-PRODUCT diagnostic. Checkpoint exact changed files/blockers/NEXT_ACTION.

## S42 VERIFIED — F09 REAL 20-SECOND CANCELLABLE EVENT-EVALUATION WORKER, BLOCKED-ONLY / 672 WINDOWS UNIT PASS
- Continued exact LIVE S41 NEXT_ACTION: reread PLAN.md/STATE.md, F09 original EXE worker evidence, existing S39/S40/S41, true F05/F06 availability and Info gate. docs/tasks/S42.md ABSENT at start. Genuine authenticated game launch/login/close-all remain **UNAVAILABLE**; no fake production Login schedule, no Proxy.
- NEW `src/login_schedule_worker.py`: genuine daemon background thread with `threading.Event.wait(WORKER_CHECK_SECONDS=20)`, precise cancel `Event.set()`, bounded `join` before restart, duplicate-thread prevention, permanent shutdown guard, read-only strict S40 F09 settings and S39 next-occurrence time model. `poll_once()` evaluates due events, emits only immutable `BlockedScheduleOccurrence(kind,planned_time,status=BLOCKED_ACTION_UNAVAILABLE)` in **in-memory bounded 64-record safety audit**; NEVER executes game open/close, OS shutdown, HWND controls, account writer or Proxy. Tests verify native background thread actually executes, passes wait timeout exactly 20, emits close/open blocked once, restart doesn't catch up and unmodified Windows Event.wait(20) cancellation wakes immediately. Test-owned wait acceleration only for quickly exercising due events, **not product polling cadence**.
- Persisted F09 `schedule_on`/`shutdown_after_close` raw Boolean encoding remains UNKNOWN and never auto-arms anything. F02 legacy `check`/`Có` conversion also UNKNOWN, no writes. Exact F09 same-time tie order / multi-day policy / worker close-game micro-order remain NOT PROVEN; max64 audit size explicitly S42 local memory cap, not original TLM behavior. Existing S41 actual Tk 1s preview, S40 settings, S39 clock, Login UI untouched.
- NEW `tests/test_s42.py` (**29** tests), `tools/S42_WINDOWS_F09_EVENT_WORKER_SMOKE.py`, `.github/workflows/s42-native-f09-evaluation-worker.yml`, docs/tasks/S42.md, docs/login/S42_F09_EVAL_WORKER_FLOW.md, docs/source/S42_MODEL.json.
- **ACTUAL [S42 native Windows run 37927222472](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37927222472), job 113808955798 COMPLETED SUCCESS**: compileall PASS, **672/672 S01–S42 Python units PASS**, native `PASS_NATIVE_S42_REAL_EVENT_WAIT20_BLOCKED_ONLY` with actual Windows worker and no game dispatch, synthetic settings.ini byte-identical. Actual S41/S40/S39/S38/S37/S35/S34/S33/S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native Windows regressions ALL PASS. Artifact **11614153857**.
- S36 **FAIL-CLOSED NOT-PRODUCT diagnostic** packaging on updated S42 source [37927029048](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37927029048) COMPLETED SUCCESS, still no product EXE. Real signed Info, launcher F05, Login F06, scheduled HWND close-all/OS shutdown, true game runtime parity and full screenshot parity NOT DONE. PLAN, original ZIP and all prior production features untouched.
- **STATUS S42_NATIVE_WINDOWS_F09_WORKER_672_UNIT_PASS_BLOCKED_ONLY**.

## S42 CHANGED FILES
- src/login_schedule_worker.py NEW
- tests/test_s42.py NEW
- tools/S42_WINDOWS_F09_EVENT_WORKER_SMOKE.py NEW
- .github/workflows/s42-native-f09-evaluation-worker.yml NEW
- docs/tasks/S42.md; docs/login/S42_F09_EVAL_WORKER_FLOW.md; docs/source/S42_MODEL.json NEW
- STATE.md; PROJECT_STATUS.md append-only

## NEXT_ACTION on CONTINUE — S43
- Reread LIVE PLAN.md, STATE.md, check docs/tasks/S43.md. Inspect original F09 event/authorization semantics and S42 worker concurrency, S41 Tk countdown, current genuine E03 signed Info/F05/F06 availability. **Before any scheduled game action** obtain and verify authentic licensed open/close handlers; otherwise stay BLOCKED_ONLY, and implement smallest real source-backed functional correction (e.g. worker cancellation race/fail-closed transitions) with test evidence; do not introduce fake Login/Proxy controls, guessed persisted F09/F02 booleans, account writes, OS shutdown or misleading product EXE. Preserve all **672** Python units plus S42/S41/S40/S39/S38/S37/S35–S10 native Windows success and S36 NOT-PRODUCT fail-closed diagnostic. Append exact files/blockers/NEXT_ACTION.

## S43 VERIFIED — F09 STOP/START RACE + BLOCKED CLOCK CANCEL FIX / 686 WINDOWS UNIT PASS
- Continued exact LIVE S42 NEXT_ACTION: reread PLAN.md/STATE.md, original F09 scheduler semantics, existing S39–S42 source, real F05/F06/Info availability and CI. docs/tasks/S43.md initially ABSENT.
- Inspected actual S42 F09 worker and confirmed **three real concurrency defects**: (1) `start()` can run after old worker join but before old `stop()` cleanup, causing old stop to disable new clock while new thread alive; (2) a stalled clock provider holding `_lock` made old `stop(timeout)` block on lock BEFORE requesting cancellation, violating timeout; (3) the stalled provider could resume after cancellation and still publish a due-event audit. Some diagnostic property reads also stalled behind the same lock.
- NARROW `src/login_schedule_worker.py` corrections: dedicated `_lifecycle_lock` serializes entire start/stop/join/cleanup, `start()` refuses while stop in progress; stop Event.set() BEFORE any poll-lock acquisition, bounded join timeout returns STOPPING without waiting for blocked clock provider; `poll_once()` rechecks cancellation/closed AFTER source time retrieval AND after S39 clock poll, discarding results after stop; status/thread_alive/active reads cannot block on a hung source clock. All game-related dispatch remains **BLOCKED_ACTION_UNAVAILABLE**, no actual F05/F06 open/close/PC shutdown.
- NEW `tests/test_s43.py` (**14** unit methods), `tools/S43_WINDOWS_F09_STOP_RACE_SMOKE.py` (actual Windows thread deterministic post-join pause and blocked time provider), `.github/workflows/s43-native-f09-stop-races.yml`; NEW docs/tasks/S43.md, docs/login/S43_STOP_RACE_FLOW.md, docs/source/S43_MODEL.json.
- Initial S43 runs (37928427715 and 37928531612) failed, revealing the stale cancellation audit and lock-bound status access; fixed with scoped `src/login_schedule_worker.py` commit **708d7a45890bf06ee054b152ec559e06b010583b** before re-verification. Do NOT treat initial failed runs as success.
- **ACTUAL [S43 Windows run 37928620248](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37928620248), job 113813537652 COMPLETED SUCCESS**: compileall PASS, **686/686 S01–S43 Python units PASS**, native `PASS_NATIVE_S43_WORKER_STOP_RACES_FIXED`; joined-old-worker race now denies concurrent restart, time-stalled `stop(timeout)` bounded, eventually joins, no late due audits; dummy original INI byte-identical. S42/S41/S40/S39/S38/S37/S35/S34/S33/S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native regressions ALL PASS. Artifact **11614639975**.
- S36 FAIL-CLOSED **NOT-PRODUCT** Windows packaged diagnostic with current updated source [37928620198](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37928620198) SUCCESS. No signed Info, real F05/F06 launch/login or game close-all/PC shutdown action, no product EXE/game runtime parity. Original ZIP, PLAN, all unrelated code and working features untouched, no Proxy runtime, no guessed F02/F09 account/Boolean writers.
- **STATUS S43_NATIVE_WINDOWS_686_UNITS_PASS_LIFECYCLE_RACES_FIXED**.

## S43 CHANGED FILES
- src/login_schedule_worker.py (narrow verified bug fix)
- tests/test_s43.py NEW
- tools/S43_WINDOWS_F09_STOP_RACE_SMOKE.py NEW
- .github/workflows/s43-native-f09-stop-races.yml NEW
- docs/tasks/S43.md; docs/login/S43_STOP_RACE_FLOW.md; docs/source/S43_MODEL.json NEW
- STATE.md; PROJECT_STATUS.md append-only

## NEXT_ACTION on CONTINUE — S44
- Reread LIVE PLAN.md, STATE.md and check docs/tasks/S44.md. Inspect original F09 worker, S43 fixed lifecycle, S41 real Tk countdown and current genuine E03 signed Info / F05/F06 game action availability. Only implement a demonstrable source-backed F09 lifecycle integration or fix with test proof; do not create fake controls or authorize real game open/close/PC poweroff until authentic handlers/permission exist. Pay special attention to cancel/shutdown behavior when a blocked clock provider is released or a Tk callback is stale. Preserve **686** Python tests, native S43/S42/S41/S40/S39/S38/S37/S35–S10 Windows green and S36 diagnostic fail-closed NOT PRODUCT. No Proxy runtime, no F02 write/migration, no guessed F09 persisted bool format; append precise blockers/files and NEXT_ACTION.

## S44 VERIFIED — F09 REAL Tk DESTROY / CALLBACK CANCELLATION FIX / 704 WINDOWS UNIT PASS
- Continued **LIVE S43 NEXT_ACTION**: reread PLAN.md, STATE.md, S43/F09 original evidence, S39–S43 source and tests, checked `docs/tasks/S44.md` ABSENT. Original F09 verifies Tk main-thread 1s countdown with cooperative cancellation; genuinely authenticated Info/F05/F06 game actions remain missing. No fake Login scheduler or Proxy.
- Audited existing S41 `src/login_schedule_countdown.py` and confirmed two lifecycle gaps: (1) real Tk Label destruction before a pending `after(1000)` did NOT automatically invoke preview shutdown/cancel; (2) reentrant `stop()/shutdown()` inside `now()`, `Label.configure`, or `Label.after` could rearm an orphan timer, overwrite CLOSED status or arm a clock after shutdown.
- NARROW production fix only in `src/login_schedule_countdown.py`: `Label.bind("<Destroy>", callback, add="+")` recognizes exact owned Label and shuts down, cancels pending Tcl after and rejects restart; `_live(epoch)` rechecks after each external/reentrant call, cancels orphan newly created `after_id` if stop occurred during scheduling; initial time provider reentry cannot rearm a stopped/closed preview. Preserved F09 every-1s read-only countdown, S43 real 20s worker and full unrelated functions unchanged. Updated only `tests/test_s41.py` FakeLabel to implement the REAL Tk API `bind`, no original logic changed.
- NEW `tests/test_s44.py` **18 deterministic cases**, `tools/S44_WINDOWS_TK_DESTROY_COUNTDOWN_SMOKE.py` REAL Windows Tk+Tcl actual `Label.destroy()` BEFORE the 1000ms callback and `after info` cancellation proof, `.github/workflows/s44-native-tk-destroy-countdown.yml`. NEW `docs/tasks/S44.md`, `docs/login/S44_TK_DESTROY_FLOW.md`, `docs/source/S44_MODEL.json`.
- Initial S44 source-only CI `cdfe2dfe48` FAILED because existing test FakeLabel lacked `bind` (26 errors); fixed TEST FIXTURE in `a630d9822e`, initial runs not claimed as successes. All functionality verified AFTER correction.
- **ACTUAL [S44 native Windows run 37934270854](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37934270854), job 113832286506 COMPLETE SUCCESS**: compileall PASS, **704/704 S01–S44 Python unit tests PASS**; `PASS_NATIVE_S44_TK_DESTROY_CANCELS_COUNTDOWN`: real Tk Destroy cancels pending after ID, closes/disarms preview and rejects restart, test-owned original settings.ini byte-identical. Actual S43/S42/S41/S40/S39/S38/S37/S35/S34/S33/S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native Windows regressions ALL PASS. Artifact **11617551321**.
- Found S36 packaging CI trigger blindspot: workflow re-ran all unit tests but watched only `tests/test_s36.py` instead of all Stage S test files. Narrowly updated **`.github/workflows/s36-native-packaging-diagnostic.yml`** to watch `tests/test_s*.py` on push so S41 FakeLabel test-only dependency fix re-triggers packaging. **ACTUAL [S36 Windows run 37934597454](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37934597454), job 113833375510 COMPLETE SUCCESS**: complete unit gate PASS, PyInstaller packaged diagnostic, normal execution and unverified-cli execution return **2**/`EXPLICITLY_BLOCKED_NO_GUI`, native S35–S10 regression PASS. Artifact **11617885616**. **STILL NOT PRODUCT EXE** and no signed Info authorization, F05/F06 real game open/close-all, PC shutdown or live-game runtime parity.
- Unknown F02 `check` token/`Có` migration and F09 persisted bool encoding remain UNKNOWN and untouched: no account writes, no Proxy runtime, no guessed automation. PLAN/original source ZIP and other working modules untouched.
- **STATUS S44_NATIVE_WINDOWS_TK_DESTROY_704_UNITS_PASS_DIAGNOSTIC_FAIL_CLOSED**.

## S44 CHANGED FILES
- src/login_schedule_countdown.py (narrow genuine lifecycle correction)
- tests/test_s41.py (fake Label `bind` support only)
- tests/test_s44.py NEW
- tools/S44_WINDOWS_TK_DESTROY_COUNTDOWN_SMOKE.py NEW
- .github/workflows/s44-native-tk-destroy-countdown.yml NEW
- .github/workflows/s36-native-packaging-diagnostic.yml (path-trigger fix only)
- docs/tasks/S44.md; docs/login/S44_TK_DESTROY_FLOW.md; docs/source/S44_MODEL.json NEW
- STATE.md; PROJECT_STATUS.md append only

## NEXT_ACTION on CONTINUE — S45
- Reread LIVE PLAN.md + STATE.md and check docs/tasks/S45.md. Audit F09 original lifecycle, **S44 actual Tk auto-Destroy** and **S43 cancellable 20-second blocked-only worker** on tab closing while clock provider or Tk callback is in flight; use independently evidenced, minimal functionality or fix a demonstrated bug, never a fake Login scheduler. Real E03 signed Info/F05/F06 open/close handlers remain missing; do not dispatch real game open/close or PC poweroff, migrate unknown F02/F09 flags or develop Proxy. Preserve **704** units, S44/S43/S42/S41/S40/S39/S38/S37/S35–S10 native green, and S36 FAIL-CLOSED NOT-PRODUCT packaging green. Append exact blockers/changed files/NEXT_ACTION.

## S45 VERIFIED — F09 READ-ONLY TK + 20-SECOND WORKER LIFETIME COORDINATION / 723 WINDOWS UNIT PASS
- Continued exact LIVE S44 NEXT_ACTION: reread PLAN.md/STATE.md, original F09 worker + Tk display evidence, S44 real Tk auto-Destroy, S43 correct cancellable Event.wait(20) worker and real E03 signed Info/F05/F06 game-action availability; docs/tasks/S45.md initially ABSENT. Original F09 explicitly supports main-thread 1s countdown, 20s background checks, cooperative disabling independent of live game windows. Full authenticated F05/F06 handlers remain UNAVAILABLE.
- Found **integration-level lifecycle gap**: S44 Tk Label auto-Destroy cancels the countdown timer, but the independently enabled S43 read-only background worker is not owned by that Tk lifetime and would survive tab destruction. Added NEW test-owned `src/login_schedule_lifetime.py`, class `F09ReadOnlyTabLifetime`: owns independently verified S44 `TkScheduleCountdownPreview` and S43 `F09ScheduleEvaluationWorker`, both from S40 validated read-only HH:MM. `start_preview_and_evaluation()` is EXPLICIT test call only, never from persisted unknown schedule_on flags. Binds an additional `Label.bind("<Destroy>", ..., add="+")`; exact owned Label closure permanently disarms both components, cancels pending Tk.after and requests worker cancel with `shutdown(timeout=0)` to avoid blocking Tk on a stalled clock provider. For a still-running worker, status `CLOSING_WORKER`; separate `finish_close(timeout)` joins AFTER releasing the stalled clock, without touching Tk. Handles reentrant Label destroy during startup, partial-start rollback, duplicate/refused starts and no post-close blocked events. **No game actions, no HWND close, no PC shutdown, no actual production Login tab binding and no fake buttons.**
- NEW `tests/test_s45.py` (**19** unit cases), `tools/S45_WINDOWS_TK_WORKER_LIFETIME_SMOKE.py` (REAL native Tcl Label Destroy + REAL background worker blocked in injected test-owned time provider), `.github/workflows/s45-native-tk-worker-lifetime.yml`, docs/tasks/S45.md, docs/login/S45_LIFETIME_FLOW.md, docs/source/S45_MODEL.json. Prior S01–S44 modules and original ZIP/PLAN untouched.
- **ACTUAL [S45 native Windows run 37936875375](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37936875375), job 113841015888 COMPLETED SUCCESS**: compileall PASS, **723/723 S01–S45 Python units PASS**, real `PASS_NATIVE_S45_REAL_TK_WORKER_DESTROY_ASYNC_CANCEL`; real Tcl Destroy did not wait for stalled worker, both cancellation flags set, blocked worker safely joined after provider release, no late events or restarts, synthetic E05 settings.ini byte-identical. S44/S43/S42/S41/S40/S39/S38/S37/S35/S34/S33/S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native regressions ALL PASS. Artifact **11618688012**.
- **ACTUAL [S36 diagnostic Windows run 37936736175](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37936736175), job 113840541655 COMPLETED SUCCESS** with **723** unit tests: isolated packaged diagnostic exe normal and unverified CLI runs returned **2/`EXPLICITLY_BLOCKED_NO_GUI`**; artifact **11618980172**. S36 EXE remains strictly **FAIL-CLOSED NOT-PRODUCT**, not a real authenticated/live game product.
- No signed Info service, real F05 suspended launch/F06 login, game close-all, PC shutdown, full UI/game runtime parity. F09 persisted Boolean token meaning and restart auto-resume remain UNKNOWN, F02 account check / legacy captcha `Có` migration UNKNOWN; no writes to credentials/settings, no Proxy runtime.
- **STATUS S45_NATIVE_WINDOWS_723_TESTS_PASS_TK_WORKER_ASYNC_CANCEL_TEST_ONLY**.

## S45 CHANGED FILES
- src/login_schedule_lifetime.py NEW
- tests/test_s45.py NEW
- tools/S45_WINDOWS_TK_WORKER_LIFETIME_SMOKE.py NEW
- .github/workflows/s45-native-tk-worker-lifetime.yml NEW
- docs/tasks/S45.md; docs/login/S45_LIFETIME_FLOW.md; docs/source/S45_MODEL.json NEW
- STATE.md; PROJECT_STATUS.md append only

## NEXT_ACTION on CONTINUE — S46
- Reread LIVE PLAN.md/STATE.md, check docs/tasks/S46.md, original F09 and S45/Tk/workers. Inspect for demonstrated F09 lifecycle or F01 integration bug with strong evidence before changing working code. If no source-backed actual game-action handlers and signed Info are yet available, keep S45 **test-owned read-only**, do not attach fake schedule-on UI or dispatch any open/close/PC-shutdown actions. In particular audit unexpected exceptions during Tk destroy and finish_close while provider remains stalled, ensuring bounded close and no stale action. Preserve **723** unit tests and S45/S44/S43/S42/S41/S40/S39/S38/S37/S35–S10 native Windows passes, S36 packaged diagnostic fail-closed NOT PRODUCT, unknown F09/F02 boolean/migration untouched, no Proxy. Checkpoint exact blockers/paths and NEXT_ACTION.

## S46 VERIFIED — F09 TK DESTROY NONBLOCKING UNDER CONCURRENT WORKER STOP LIFECYCLE LOCK / 738 WINDOWS UNIT PASS
- Continued from LIVE S45 NEXT_ACTION: reread PLAN.md and STATE.md, F09 original worker evidence, S43 worker, S44 preview, S45 Tk/worker coordination and actual Info/F05/F06 readiness. docs/tasks/S46.md initially ABSENT.
- **Confirmed S45 GUI hang race:** `F09ReadOnlyTabLifetime.close()` called `worker.shutdown(timeout=0)` on real Tk `<Destroy>`. `shutdown()` enters S43 `stop(timeout)` and BLOCKS on `_lifecycle_lock` even with zero join timeout when another thread owns it in stop/join cleanup. Thus Tk could freeze under legitimate concurrent stop; S45 did not test that contention.
- NARROW fixes in `src/login_schedule_worker.py`: new `request_shutdown()` signals permanent `_closed` latch + `threading.Event.set()` **without acquiring lifecycle or poll locks or joining**. Existing `shutdown(timeout)` reuses that immediate request before stop to preserve API. Start now checks permanent closed state after potentially reentrant `now()` and after clearing cancel and starting worker to ensure no resurrected worker from asynchronous cancellation. No game/window/OS operations, account writer, or Proxy.
- NARROW changes in `src/login_schedule_lifetime.py`: Tk `close()` uses nonblocking `worker.request_shutdown()`, never locks or joins even if another stop owns lifecycle lock. Existing separate **non-Tk** `finish_close(timeout)` retains joining only after tab teardown. Forced preview.shutdown exceptions set explicit `BLOCKED_PREVIEW_TEARDOWN` while worker cancellation still occurs in `finally`, no false full success. Not attached to real product F09 controls (Info/F05/F06 real handlers still missing).
- NEW `tests/test_s46.py` (**15** deterministic tests; an initial test attempted writing read-only `worker` property, corrected TEST ONLY before final green), `tools/S46_WINDOWS_TK_LIFECYCLE_MUTEX_SMOKE.py` (REAL Windows Tk Label destroyed while a separate stop thread holds lifecycle mutex after actual join), `.github/workflows/s46-native-tk-lifecycle-mutex.yml`, docs/tasks/S46.md, docs/login/S46_LOCK_FREE_SHUTDOWN_FLOW.md, docs/source/S46_MODEL.json.
- **ACTUAL [S46 native Windows run 37940872719](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37940872719), job 113854623451 COMPLETE SUCCESS**: compileall PASS, **738/738 S01–S46 Python units PASS**, `PASS_NATIVE_S46_TK_DESTROY_LIFECYCLE_LOCK_NO_HANG`; real Tk GUI Destroy immediately returns while lifecycle lock held, eventual worker join succeeds, no late event audit, dummy original settings.ini byte-identical. Actual S45/S44/S43/S42/S41/S40/S39/S38/S37/S35/S34/S33/S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native Windows regressions ALL PASS. Artifact **11621223118**.
- **ACTUAL [S36 diagnostic Windows run 37940754104](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37940754104), job 113854212032 COMPLETE SUCCESS**: all **738** unit tests pass and one-dir diagnostic compiled; ordinary and unverified CLI invocations both exit **2/`EXPLICITLY_BLOCKED_NO_GUI`**. Artifact **11621108248**. This remains **FAIL-CLOSED NOT PRODUCT EXE**. Never claim true game running, F01 screenshot parity or account-login functionality.
- **Remaining blockers:** authentic signed Info source, complete F05/F06 native game launch/login and close-all still UNAVAILABLE; actual F09 scheduled game/PC actions blocked, no production schedule checkbox. Unknown F09 stored bool encoding/restart semantics and F02 `Settings.accounts` checkbox/Có encoding preserved read-only; no Proxy. PLAN, original ZIP and unrelated code untouched.
- **STATUS S46_WINDOWS_NATIVE_738_TESTS_PASS_TK_MUTEX_NONBLOCKING**.

## S46 CHANGED FILES
- src/login_schedule_worker.py (lock-free permanent request_shutdown and start race guards)
- src/login_schedule_lifetime.py (Tk close immediate cancel and failure resilience)
- tests/test_s46.py NEW
- tools/S46_WINDOWS_TK_LIFECYCLE_MUTEX_SMOKE.py NEW
- .github/workflows/s46-native-tk-lifecycle-mutex.yml NEW
- docs/tasks/S46.md; docs/login/S46_LOCK_FREE_SHUTDOWN_FLOW.md; docs/source/S46_MODEL.json NEW
- STATE.md; PROJECT_STATUS.md append-only

## NEXT_ACTION on CONTINUE — S47
- Reread LIVE PLAN.md and STATE.md, check docs/tasks/S47.md. Reinspect S46 request_shutdown() against genuinely concurrent start and long-blocking clock source, S43 `stop(timeout)` lifecycle-lock acquisition budget and S45 `finish_close(timeout)` under an external stopper. Implement only a **demonstrated** smallest source-backed fix (particularly bounded `finish_close` under mutex contention), verified by real Windows thread/Tk native tests; never add fake F09 product schedule controls or dispatch absent authenticated F05/F06 game/OS actions. Preserve **738** Python unit tests + S46/S45/S44/S43/S42/S41/S40/S39/S38/S37/S35–S10 native Windows green, S36 NOT-PRODUCT fail-closed green; no Proxy and no unknown F02/F09 writes. Append exact blockers/changed files/NEXT_ACTION.

## S47 VERIFIED — F09 STOP/FINISH_CLOSE TOTAL MUTEX+JOIN TIMEOUT, PENDING START/STOP FENCE / 754 WINDOWS UNIT PASS
- Continued LIVE S46 NEXT_ACTION: reread PLAN.md, STATE.md, F09 original schedule evidence, S43–S46 worker/Tk logic and tests, genuine signed Info and real F05/F06 action availability. docs/tasks/S47.md initially ABSENT.
- **Confirmed S46 bounded-cleanup defect**: `F09ReadOnlyTabLifetime.finish_close(timeout)` calls `F09ScheduleEvaluationWorker.stop(timeout)`. Old `stop()` waited for `_lifecycle_lock` WITHOUT A TIME BUDGET, then limited only `Thread.join`. If independent stopper held mutex after worker join but before cleanup, total `finish_close(timeout=0.03)` could wait indefinitely. A cancellation request during long-blocked `start` `now()` could also be erased by later `_cancel.clear()`.
- Narrow code change ONLY in `src/login_schedule_worker.py`: one `time.monotonic()` deadline covers both `_lifecycle_lock.acquire(timeout=remaining)` and `Thread.join(timeout=remaining)`; always signal `_cancel.set()` + new `_stop_requested` pending fence BEFORE mutex wait; on timeout return False promptly, status STOPPING and retain cancel fence; successful cleanup clears fence for next EXPLICIT legitimate start. `_start_locked()` checks `_stop_requested` on entry/after time provider/after event-clear/after thread-start; permanent `request_shutdown()` also marks pending stop. No changes to production Tk/UI, S45 lifetime, legacy F02 writers, Proxy, game/OS actions.
- NEW `tests/test_s47.py` **16** deterministic cases (including 0s/positive mutex timeout, slow clock during start, cancellation retention, separate stopper in joined-but-locked state, true blocked events never dispatched), `tools/S47_WINDOWS_FINISH_CLOSE_MUTEX_DEADLINE_SMOKE.py` REAL Windows Tk + live worker with independent held mutex, `.github/workflows/s47-native-finish-close-deadline.yml`, docs/tasks/S47.md, docs/login/S47_DEADLINE_FLOW.md, docs/source/S47_MODEL.json. Initial tests assumed `life.close()` necessarily had already joined and demanded CLOSING_WORKER after worker exited; adjusted TEST assertions to accept legitimate `CLOSED_PENDING_JOIN`, not source semantics. Early red CI runs not claimed success.
- **ACTUAL [S47 Windows run 37942444233](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37942444233), job 113859999702 COMPLETE SUCCESS**: compileall PASS, **754/754 S01–S47 Python units PASS**, real native `PASS_NATIVE_S47_FINISH_CLOSE_TOTAL_TIMEOUT_LOCK_BUDGET`, genuine Tcl/Tk destroy with mutex held, finish_close honors entire timeout, pending stop retained, successful join after release, no late game events, synthetic original settings.ini byte-identical. S46/S45/S44/S43/S42/S41/S40/S39/S38/S37/S35/S34/S33/S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native regressions ALL PASS. Artifact **11622740614**.
- **ACTUAL [S36 diagnostic packaging run 37942348540](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37942348540), job 113859667141 COMPLETE SUCCESS**: **754** Python tests PASS, packaged S36 diagnostic normal and unverified CLI both exit **2/`EXPLICITLY_BLOCKED_NO_GUI`**; artifact **11622935310**, STILL **FAIL-CLOSED NOT-PRODUCT EXE**.
- Still MISSING: authentic signed Info license input, real F05 suspended game launcher/F06 account login, verified game close-all and PC shutdown actions, full original Login/UI/game runtime parity. F09 persisted bool meanings/auto-resume and F02 account checkbox/Có mappings remain UNKNOWN/UNMODIFIED; no Account INI writes, no Proxy runtime, no fake product scheduler controls or real game actions. PLAN and original ZIP and unrelated code unchanged.
- **STATUS S47_NATIVE_WINDOWS_754_UNIT_PASS_TOTAL_MUTEX_JOIN_DEADLINE**.

## S47 CHANGED FILES
- src/login_schedule_worker.py (bounded lifecycle mutex+join, pending stop fence)
- tests/test_s47.py NEW
- tools/S47_WINDOWS_FINISH_CLOSE_MUTEX_DEADLINE_SMOKE.py NEW
- .github/workflows/s47-native-finish-close-deadline.yml NEW
- docs/tasks/S47.md; docs/login/S47_DEADLINE_FLOW.md; docs/source/S47_MODEL.json NEW
- STATE.md; PROJECT_STATUS.md append only

## NEXT_ACTION on CONTINUE — S48
- Reread LIVE PLAN.md + STATE.md, check docs/tasks/S48.md. Audit S47 pending stop request against TWO concurrent stop callers and in-flight `start()`, particularly whether a completed stopper may clear a second pending cancellation and whether `finish_close(timeout)` always stays bounded. Implement only independently reproduced defect or original-source-backed narrow feature. Keep F09 game open/close/PC actions BLOCKED until actual signed Info and functional F05/F06 handlers exist, no fake Login scheduler or Proxy, no F02/F09 unknown-flag writes. Preserve **754** full Python units + S47/S46/S45/S44/S43/S42/S41/S40/S39/S38/S37/S35–S10 native Windows green, S36 NOT-PRODUCT fail-closed green. Append exact files/blockers/NEXT_ACTION.

 
## S48 IMPLEMENTED — TWO CONCURRENT F09 STOP CALLERS FENCE / WINDOWS VERIFICATION PENDING
- Continued from LIVE S47 NEXT_ACTION; reread PLAN.md, STATE.md, S47 worker / S45 lifetime and original F09 schedule evidence. docs/tasks/S48.md ABSENT at start.
- Rechecked user ZIP TLMTool_2.1.2(20261009-142633).zip: inner TLMTool.dist/TLMTool.exe SHA-256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22 MATCHES frozen forensic reference. Gate A not repeated.
- Demonstrated source-level S47 race: stop A clears the shared _stop_requested after successful cleanup while stop B has already requested stop but remains blocked on lifecycle mutex; this briefly permits competing start(). Not claimed as recovered exact original behavior.
- NARROW change ONLY src/login_schedule_worker.py: per-stop registration with _stop_request_lock / _pending_stop_callers, cancel before mutex wait, completion tracking on every exit. Only last successful stopper may clear pending fence, unless permanently closed. Timed-out/failed stop retains fence for later explicit cleanup. S47 total mutex+join deadline and S46 lock-free request_shutdown preserved. No real scheduled actions.
- NEW tests/test_s48.py (9 deterministic methods), tools/S48_WINDOWS_TWO_STOP_CALLERS_SMOKE.py real Windows Tk/worker test, .github/workflows/s48-native-two-stoppers-fence.yml full S tests and S47–S10 native chain. NEW docs/tasks/S48.md; docs/login/S48_MULTI_STOP_FENCE_FLOW.md; docs/source/S48_MODEL.json.
- GitHub commits: source cddfc5d512620d59077b0dc99840e22351cdb918; tests 5e72a43e5239df089eeee5c85a5c65ac1ea4992c; Windows smoke f21e5b9eab25ce74270bced0fb5fb47c1dce0895; workflow b8ddbe3ffada5f9fb1b0c452608c05804e0cc9b9.
- S48 actual Windows run/log NOT VERIFIED during this checkpoint. The previously successful 754/754 Windows suite was S47, NOT S48. Do NOT claim S48 complete or EXE product ready until actual green job proof.
- BLOCKERS unchanged: genuine signed Info, F05/F06 game open/login, authorized close-all, actual scheduled game action, original runtime/UI parity. S36 packaged EXE FAIL-CLOSED NOT PRODUCT. No Proxy runtime; unknown F02 accounts/check/Có and F09 stored Boolean encodings untouched; no real account writes, PC shutdown or fake scheduler. PLAN, old source, original ZIP unchanged.
- STATUS S48_IMPLEMENTED_PENDING_FULL_WINDOWS_VERIFICATION.

## S48 CHANGED FILES
- src/login_schedule_worker.py (narrow stop concurrency fix)
- tests/test_s48.py NEW
- tools/S48_WINDOWS_TWO_STOP_CALLERS_SMOKE.py NEW
- .github/workflows/s48-native-two-stoppers-fence.yml NEW
- docs/tasks/S48.md; docs/login/S48_MULTI_STOP_FENCE_FLOW.md; docs/source/S48_MODEL.json NEW
- STATE.md; PROJECT_STATUS.md append-only

## NEXT_ACTION on CONTINUE — S48 CI VERIFICATION THEN S49
- Read LIVE PLAN.md and STATE.md. Check actual S48 full Windows unit/native Actions and S36 fail-closed diagnostic, record run IDs and fix any REAL test failure before marking VERIFIED. If CI green, progress to smallest independently justified S49 safety fix or original-backed action. Preserve prior 754 S01–S47 tests, S47–S10 Windows and S36 diagnostics. Do not develop Proxy, guessed F02/F09 persistence, fake auth/game login or OS shutdown.


## S48 FINAL WINDOWS VERIFICATION — PASSED
- ACTUAL [Windows S48 run 37945017911](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37945017911), job 113868933800 COMPLETE SUCCESS for commit b8ddbe3ffada5f9fb1b0c452608c05804e0cc9b9.
- Python 3.10 Windows compileall success, **763/763 full Stage S01–S48 unit tests PASS**, all nine S48 tests PASS. REAL Windows Tk/thread worker returns PASS_NATIVE_S48_TWO_STOPPERS_FENCE_REAL_TK. S47/S46/S45/S44/S43/S42/S41/S40/S39/S38/S37/S35/S34/S33/S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native regressions ALL SUCCESS. Artifact 11621999230.
- ACTUAL [Windows S36 packaged diagnostic run 37944863427](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37944863427), job 113868407847 COMPLETE SUCCESS on S48 source+unit tests commit 5e72a43e5239df089eeee5c85a5c65ac1ea4992c: **763/763 unit PASS**; diagnostic normal and unverified CLI both EXPLICITLY_BLOCKED_NO_GUI, NOT PRODUCT. Artifact 11622664380. Later S48 additions are test-only smoke/workflow/docs and did not alter worker after that run.
- S48 VERIFIED only for source-level stop-fence and Windows test-owned read-only functionality. NO authenticated real game actions, NO full product parity. Previous implementation-pending note preserved as history.

## S48 VERIFIED GATE / NEXT_ACTION on CONTINUE — S49
- Re-read LIVE PLAN.md/STATE.md. S48 Windows native 763/763 and S36 diagnostic both green (runs above); avoid reimplementation. Before S49, inspect current authentic Info/F05/F06 blockers and the actual F09 state/lifecycle concurrency; implement only independently reproduced narrow safety defect with real unit/native Windows proof or authenticated original-backed feature, no fake game functionality/Proxy. No unknown F02/F09 persisted bool conversion. Preserve 763 tests and Windows S48–S10 chain, checkpoint specific files, CI IDs, blockers, NEXT_ACTION.

## S49 VERIFIED — F09 PERMANENT SHUTDOWN FENCE AFTER IN-FLIGHT STOP CLEAR / 772 WINDOWS TESTS PASS
- Continued from LIVE S48 VERIFIED NEXT_ACTION after re-reading PLAN.md, STATE.md, F09 original static proof, S48 worker source and S46–S48 lifecycle/Tk tests. docs/tasks/S49.md was absent initially.
- Independently reproduced S48 source-level TOCTOU: successful stopper checks !closed and enters Event.clear while concurrent S46 lock-free Tk request_shutdown sets closed/fence/cancel; old clearer may then clear the permanently set fence. Reproduced with a deterministic equivalent Python threading.Event interleaving: closed=True, cancel=True, pending=0, shutdown_fence_lost=True. This is a verified source-design bug, NOT claimed to be original game's precise behavior; closed latch did continue to deny start.
- NARROW production correction ONLY in src/login_schedule_worker.py: after S48 successful stop-fence clear, re-check one-way _closed and restore _stop_requested.set() when true. S46 request_shutdown retains zero-lock immediate Tk cancellation; S47 total stop timeout, S48 outstanding stopper-count, S42 true 20s read-only worker, S41/S45 real Tk lifetimes preserved. No Proxy runtime, F02 account settings write, F09 guessed Boolean decode, actual game launch/close/poweroff or fake Login UI.
- NEW tests/test_s49.py **9** deterministic cases: paused Event.clear concurrent shutdown, FakeLabel Tk Destroy during clear, normal explicit stop/restart, two stopper permanent close, due-event BLOCKED_ONLY and no real actions.
- NEW tools/S49_WINDOWS_TK_SHUTDOWN_FENCE_SMOKE.py actual Windows Tk mainloop and Label.destroy while second real stopper is paused before Event.clear; .github/workflows/s49-native-tk-shutdown-fence.yml runs full Stage S tests and S49–S10 native regressions; NEW docs/tasks/S49.md, docs/login/S49_PERMANENT_SHUTDOWN_FENCE_FLOW.md, docs/source/S49_MODEL.json.
- **ACTUAL [S49 native Windows run 37946781496](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37946781496), job 113874986410 COMPLETED SUCCESS**: compileall PASS, **772/772 Python unit tests PASS**, real PASS_NATIVE_S49_LOCKFREE_TK_CLOSE_FENCE, S48 real Tk and S47/S46/S45/S44/S43/S42/S41/S40/S39/S38/S37/S35/S34/S33/S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native Windows regressions ALL PASS. Artifact **11624436578**.
- **ACTUAL [S36 Windows run 37946685182](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37946685182), job 113874652524 COMPLETED SUCCESS** on S49 source + unit tests: 772/772 Python tests PASS, packaged S36 diagnostic normal/unverified CLI = EXPLICITLY_BLOCKED_NO_GUI, unverified exit 2. Artifact **11624825970**. EXE remains **FAIL-CLOSED NOT PRODUCT**; actual signed Info, native F05/F06 login/launcher, game open/close, original runtime/pixel parity still MISSING.
- **STATUS S49_NATIVE_WINDOWS_772_TESTS_PASS_PERMANENT_STOP_FENCE**.

## S49 CHANGED FILES
- src/login_schedule_worker.py (one narrow permanent-closure post-clear correction)
- tests/test_s49.py NEW
- tools/S49_WINDOWS_TK_SHUTDOWN_FENCE_SMOKE.py NEW
- .github/workflows/s49-native-tk-shutdown-fence.yml NEW
- docs/tasks/S49.md; docs/login/S49_PERMANENT_SHUTDOWN_FENCE_FLOW.md; docs/source/S49_MODEL.json NEW
- STATE.md; PROJECT_STATUS.md append-only

## NEXT_ACTION on CONTINUE — S50
- Reread LIVE PLAN.md and STATE.md; check docs/tasks/S50.md before writing. Audit S49 worker exception/cleanup paths, particularly whether a throwing injected clock or thread failure can leave a stale STOPPING / pending cancel or block bounded stop, and whether S46 Tk Destroy remains strictly non-blocking. Implement ONLY independently reproduced narrow source bug or genuine original-backed feature with real functional verification; don't invent Login schedule game actions or create fake controls. Preserve 772 tests, Windows S49–S10 green, S36 diagnostic fail-closed NOT PRODUCT, no Proxy, no F02/F09 uncertain persistence, no unrelated source changes. Update checkpoint exact files/blockers/NEXT_ACTION.

## S50 VERIFIED — REAL NATIVE THREAD.START OSERROR ROLLBACK / WINDOWS 784 UNIT PASS
- Continued from LIVE S49 NEXT_ACTION after rereading PLAN.md / STATE.md and source/tests/native F09. `docs/tasks/S50.md` initially ABSENT. Verified prior S49 real Windows 772/772 pass and authentic E03/F05/F06 action blockers.
- **Demonstrated reconstructed-source failure:** `_start_locked()` caught `RuntimeError` from native `threading.Thread.start()` but NOT `OSError` / `PermissionError`. On native resource failure, start raised to caller while `_cancel` remained CLEAR, `_clock` enabled, `_thread` assigned to an unstarted worker, and diagnostic status misleadingly `EVALUATING_ONLY_NO_ACTIONS`. This is an S49 reconstructed-code exception cleanup bug; no claim of exact original EXE error semantics.
- NARROW source change ONLY in `src/login_schedule_worker.py`: catch `(RuntimeError,OSError)` in Thread.start failure path, set cancellation, disable/clear the clock, discard the unstarted worker, return False with `BLOCKED_THREAD`; if concurrent permanent closed latch set then `CLOSED` takes precedence. Healthy thread start, S47 deadline, S48 multi-stop, S49 permanent closed fence, authentic 20s wait and all original code unaffected.
- NEW `tests/test_s50.py` **12** deterministic regression tests (native OSError, PermissionError, old RuntimeError, recovery after resource failure, live worker normal stop, source clock failure, FakeLabel/Tk preview rollback/Destroy, shutdown race, no game/Proxy/account writes), `tools/S50_WINDOWS_THREAD_START_OSERROR_SMOKE.py` real Windows Tcl/Tk and worker native proof, `.github/workflows/s50-native-thread-start-oserror.yml` complete Stage S and native S50–S10 chain. NEW `docs/tasks/S50.md`, `docs/login/S50_THREAD_START_OSERROR_FLOW.md`, `docs/source/S50_MODEL.json`.
- Initial red test-first source-only / S36 runs on `cdb847eeff13e478df018d567c13ede95572a411` deliberately exposed the defect; only subsequent green results count. Source fix commit `aeba316c91ff527d9269fcac27b4cf52909cc3df`, native workflow `601cd8ece5b04ac6deb63bf7b49d8b1295b1e497`.
- **ACTUAL [S50 Windows native run 37949421968](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37949421968), job 113884015863 COMPLETE SUCCESS**: Windows Python 3.10 compileall PASS, **784/784 S01–S50 Python unit tests PASS**, real `PASS_NATIVE_S50_OS_THREAD_START_FAIL_CLOSED_REAL_TK`, all S49/S48/S47/S46/S45/S44/S43/S42/S41/S40/S39/S38/S37/S35/S34/S33/S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native regression chain PASS; test-owned artifact **11624843171**.
- **ACTUAL [S36 packaged diagnostic Windows run 37949326305](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37949326305), job 113883693338 COMPLETE SUCCESS** on S50 source/tests: **784** unit PASS, packaged S36 normal/unverified CLI `EXPLICITLY_BLOCKED_NO_GUI`, unverified CLI exit 2; artifact **11624819238**. **FAIL-CLOSED NOT PRODUCT EXE**: no authentic signed Info, genuine F05/F06 game launcher/Login, authorized game window close/PC shutdown, F09 scheduler action or full original runtime/UI parity.
- User scope lock preserved: NO Proxy runtime, F02 account persistence writers, unverified F09 booleans, mock product controls, other modifications, or original ZIP/PLAN mutation.
- **STATUS S50_NATIVE_WINDOWS_784_TESTS_PASS_THREAD_START_OSERROR_FAIL_CLOSED**.

## S50 CHANGED FILES
- src/login_schedule_worker.py (one narrow Thread.start OSError/PermissionError fallback)
- tests/test_s50.py NEW
- tools/S50_WINDOWS_THREAD_START_OSERROR_SMOKE.py NEW
- .github/workflows/s50-native-thread-start-oserror.yml NEW
- docs/tasks/S50.md; docs/login/S50_THREAD_START_OSERROR_FLOW.md; docs/source/S50_MODEL.json NEW
- STATE.md; PROJECT_STATUS.md append-only

## NEXT_ACTION on CONTINUE — S51
- Reread LIVE PLAN.md + STATE.md; check `docs/tasks/S51.md`. Audit concrete `_run()`, `poll_once()`, `stop()` exception and rollback paths, while confirming actual signed Info/F05/F06 availability before wiring ANY real scheduled actions. Only independently reproduce and fix smallest source fault (if present), otherwise document authenticated blocker without creating fake UI/product behavior. Preserve **784/784** Python units and S50–S10 real native Windows passes, S36 diagnostic fail-closed NOT PRODUCT. No Proxy, F02 account writes, guessed F09 saved token decoding, OS shutdown, unrelated feature edits. Record exact changed paths, CI proof/blockers and NEXT_ACTION.

## S51 VERIFIED — F09 CANCEL-DURING-BLOCKED-AUDIT PROJECTION / 793 WINDOWS TESTS PASS
- Continued exactly from LIVE S50 NEXT_ACTION after re-reading PLAN.md/STATE.md/F09 worker/Tk lifetime. `docs/tasks/S51.md` initially ABSENT. S50 prior 784 Windows tests VERIFIED; genuine E03 signed Info and F05/F06 actions remain unavailable; do not invent runtime Login scheduler.
- **Demonstrated S50 source-level race**: `F09ScheduleEvaluationWorker.poll_once()` checks cancellation after `_clock.poll()`, but later builds `BlockedScheduleOccurrence` objects and appends blocked-only records without another check. S46 lock-free Tk Destroy or S47 stop can set cancel while that construction is paused; pre-S51 then emitted/appended a stale event after shutdown. This is an independently reproduced local source bug, NOT claimed as original EXE precise behavior.
- NARROW source fix ONLY `src/login_schedule_worker.py`: check `_cancel.is_set() or _closed` again after event record projection and just before publishing, return empty when cancellation happened during construction. Explicit caveat: this fixes proven post-clock/projection race and narrows other window; stop/Tk callback remains lock-free, not a globally atomic publication claim. Preserves 20s Event.wait, S47–S50 stop and worker safety, normal blocked-only audit when running.
- NEW `tests/test_s51.py` **9** deterministic regression tests; test-first intentionally RED Stage S run 37952479893 and S36 run 37952479812 on pre-fix test commit 02d2bc452f5274ddedf1a021e024b2e087debaf5 (reproduction only). Source correction commit **b20e16e2ac57f02e26afdc27994e2aff3c96f37a**. New `tools/S51_WINDOWS_TK_CANCEL_AUDIT_SMOKE.py` actual Windows Tk Label Destroy amid event projection, `.github/workflows/s51-native-tk-cancel-due-audit.yml`; docs/tasks/S51.md; docs/login/S51_CANCEL_DURING_BLOCKED_AUDIT.md; docs/source/S51_MODEL.json.
- **ACTUAL [S51 Windows native run 37952621242](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37952621242), job 113895017624 COMPLETED SUCCESS** on commit 7923d3cd8c9cac28434279a9839cf8752c548a6a: compileall PASS, **793/793 S01–S51 Python units PASS**, `PASS_NATIVE_S51_TK_CANCEL_DURING_DUE_AUDIT`, all native S50/S49/S48/S47/S46/S45/S44/S43/S42/S41/S40/S39/S38/S37/S35/S34/S33/S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 regression chain PASS. Test artifact **11625999085**.
- **ACTUAL [S36 packaged diagnostic run 37952524937](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37952524937), job 113894680602 COMPLETED SUCCESS** on S51 source/tests: **793 Python units PASS**, packaged diagnostic normal/unverified CLI `EXPLICITLY_BLOCKED_NO_GUI`, unverified CLI exit 2, artifact **11626765949**. EXE remains **FAIL-CLOSED NOT PRODUCT**, no authentic signed Info, F05/F06 launcher/login, authorized game close-all, OS shutdown or original app runtime/UI parity.
- PLAN unchanged, original archive untouched. No Proxy runtime, no F02 account write, no guessing F09 persisted bools, no fake game scheduler/buttons, no real game actions.
- **STATUS S51_NATIVE_WINDOWS_793_TESTS_PASS_CANCEL_DURING_AUDIT_PROJECTION**.

## S51 CHANGED FILES
- src/login_schedule_worker.py (post-materialization cancellation check only)
- tests/test_s51.py NEW (9 tests)
- tools/S51_WINDOWS_TK_CANCEL_AUDIT_SMOKE.py NEW
- .github/workflows/s51-native-tk-cancel-due-audit.yml NEW
- docs/tasks/S51.md; docs/login/S51_CANCEL_DURING_BLOCKED_AUDIT.md; docs/source/S51_MODEL.json NEW
- STATE.md; PROJECT_STATUS.md append-only

## NEXT_ACTION on CONTINUE — S52
- Reread LIVE PLAN.md and STATE.md; check docs/tasks/S52.md. Audit another independently reproducible `_run`/`poll_once`/start-stop exception or lifecycle ordering bug OR original-backed authentic E03/F05/F06 dependency that can actually be developed. Do not redo any correct S01–S51 feature. Only commit demonstrated scoped change with full Windows CI proof. Preserve **793** S01–S51 unit tests, real native S51–S10 Windows green, S36 diagnostic fail-closed NOT PRODUCT. No Proxy, no guessed F02/F09 flag mapping or INI writes, no fake UI/login/game/OS action. Record CI, blockers, exact NEXT_ACTION.

## S52 VERIFIED — EXCEPTION-AFTER-CANCEL STATUS PRECEDENCE / 804 WINDOWS UNIT TESTS PASS
- Continued exact LIVE S51 NEXT_ACTION: reread PLAN.md/STATE.md/F09 worker/Tk lifetime source and prior tests; `docs/tasks/S52.md` initially ABSENT. S51 prior **793** Windows units and native S51–S10 VERIFIED. Confirmed original signed E03 Info and F05/F06 game/OS action blockers still unresolved.
- **Independently reproduced reconstructed-source exception/status race**: `_start_locked()` and `poll_once()` trap exceptions from injected `_now()`/clock provider and force `BLOCKED_CLOCK` even after S46 lock-free `request_shutdown()` or S47 stop timeout had already requested cancellation. A worker `_run()` callback exception can likewise overwrite the closed state with `BLOCKED_WORKER`. Reproducer: hold external callback in thread A, signal closed or stop from thread B, release callback to raise; prior S51 branch lost status priority. This does not claim original binary error-message semantics.
- Narrow production correction ONLY `src/login_schedule_worker.py`: in **three existing exception branches** (start, poll, worker loop) status priority `CLOSED` if permanently closed, otherwise `STOPPING` if pending stop, otherwise original `BLOCKED_CLOCK`/`BLOCKED_WORKER`. No new actions, no locks in Tk Destroy, no changed 20-second worker cadence, no schedule flag guessing; S47–S51 prior safety behavior preserved.
- NEW `tests/test_s52.py` **11** deterministic tests, NEW `tools/S52_WINDOWS_TK_CLOCK_CANCEL_PRIORITY_SMOKE.py` actual native Tk Label.destroy during stalled/then-failing clock provider, NEW `.github/workflows/s52-native-tk-clock-cancel-priority.yml` full Python units and native S52–S10 chain; NEW docs/tasks/S52.md, docs/login/S52_EXCEPTION_CANCEL_PRIORITY_FLOW.md, docs/source/S52_MODEL.json. Test-first red-only runs 37960438135 and 37960469236 reproduced bug; source fix commit **07b21bdd1b9d8920bc17158e02f7889417064dd0**.
- **ACTUAL [S52 native Windows run 37960576234](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37960576234), job 113922079858 COMPLETE SUCCESS** on workflow commit aaaa86733165fbe9eba2414b36af9d3ba3c63b81: Windows Python 3.10 compileall PASS, **804/804 S01–S52 Python tests PASS**, native `PASS_NATIVE_S52_TK_CLOCK_EXCEPTION_CANCEL_PRIORITY`, all native S51/S50/S49/S48/S47/S46/S45/S44/S43/S42/S41/S40/S39/S38/S37/S35/S34/S33/S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 regressions PASS. Artifact **11630403860** (test-only).
- **ACTUAL [S36 packaged diagnostic Windows run 37960492148](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37960492148), job 113921793030 COMPLETE SUCCESS** on S52 source and tests: **804/804 Python tests PASS**, diagnostic packaged normal/unverified CLI **EXPLICITLY_BLOCKED_NO_GUI**, unverified exit 2; artifact **11630303845**, **NOT A PRODUCT EXE**.
- Blockers unchanged: missing real signed Info E03 authorization, F05/F06 authenticated game launcher/login, authorized close-all/PC shutdown and complete original game runtime/UI parity; S36 fail-closed. User Proxy scope excluded; no F02 account writes or unknown F09 saved Boolean mappings; PLAN, original ZIP, unrelated source untouched.
- **STATUS S52_NATIVE_WINDOWS_804_TESTS_PASS_EXCEPTION_CANCEL_PRIORITY**.

## S52 CHANGED FILES
- src/login_schedule_worker.py (exception branches only)
- tests/test_s52.py NEW (11 cases)
- tools/S52_WINDOWS_TK_CLOCK_CANCEL_PRIORITY_SMOKE.py NEW
- .github/workflows/s52-native-tk-clock-cancel-priority.yml NEW
- docs/tasks/S52.md; docs/login/S52_EXCEPTION_CANCEL_PRIORITY_FLOW.md; docs/source/S52_MODEL.json NEW
- STATE.md; PROJECT_STATUS.md append-only

## NEXT_ACTION on CONTINUE — S53
- Reread LIVE PLAN.md and STATE.md; check `docs/tasks/S53.md` and original E03/F05/F06 authorization evidence. Audit concrete remaining `stop()`/worker exception cleanup and 20-second evaluation ordering, but NEVER redo correct S01–S52 code or invent source behavior. Implement ONLY independently reproducible narrow source bug OR authenticated original-backed game integration if real proof exists; otherwise document blocker. Preserve **804/804** unit tests and S52–S10 actual Windows native passing jobs, S36 diagnostic FAIL-CLOSED NOT PRODUCT. Do not develop Proxy, guessed F02/F09 flag decoding/INI writes, fake Login controls, game/OS actions without authorization. Append exact files, failure/run IDs and NEXT_ACTION.

## S53 VERIFIED — FINAL CLEANUP _LOCK TOTAL STOP DEADLINE / 813 NATIVE WINDOWS TESTS PASS
- Continued from LIVE S52 NEXT_ACTION after reading PLAN.md, STATE.md, docs/tasks/S53.md (initially ABSENT), actual F09 worker/Tk lifetime, S43/S47 timeout tests and original E03/F05/F06 blockers. No already-correct code rewritten; PLAN and original archive untouched.
- **Reproduced narrow S52 source defect** in `src/login_schedule_worker.py::stop(timeout)`: original monotonic deadline bounded `_lifecycle_lock.acquire` and background `thread.join`, but `with self._lock:` for final clock.disable/status cleanup had NO TIME LIMIT. A separate caller's `poll_once` can hold `_lock` inside stalled injected `_now()` while background Event.wait(20) worker exits immediately on cancellation. Thus bounded stop/shutdown/finish_close hangs AFTER worker joined; Tk GUI close remains nonblocking but cleanup caller blocked indefinitely. Deterministic test-first Windows source run **37963631168** failed FOUR S53 tests on old source commit 73636efb8de0f2755db9586aecb6bd3bf23d3088, exactly identifying bounded stop/final lock/finish_close/shutdown failures.
- **NARROW code correction ONLY in `src/login_schedule_worker.py`**: after existing `thread.join`, acquire last `_lock` with remaining `deadline - time.monotonic()`. If unavailable, set STOPPING, return False, maintain `_cancel` and `_stop_requested` until next successful stop; if acquired retain existing disable/status/cleaned=True and release in finally. No extra Tk creator-thread locks, no new handlers, no 20s worker cadence changes, no game/account/Proxy actions. Source commit **4b913bb0c847c4ae0757a159a55287123676c803**.
- NEW `tests/test_s53.py` **9** genuine thread tests: independently stalled poll, bounded stop/shutdown/finish_close, outstanding restart fence, retry after release, idle timeout0, normal worker stop/restart, blocked-only due audits and user scope guard.
- NEW `tools/S53_WINDOWS_TK_FINAL_LOCK_DEADLINE_SMOKE.py` runs actual Windows Tk Label Destroy while independent injected poll owns final cleanup lock; off-Tk finish_close(0.035) returns False in budget without releasing cancel fence; then after poll release eventual finish_close(2) succeeds. NEW `.github/workflows/s53-native-tk-final-lock-deadline.yml` runs complete Stage S01–S53 unit suite and S53–S10 Windows native chain; NEW docs/tasks/S53.md; docs/login/S53_STOP_FINAL_LOCK_DEADLINE.md; docs/source/S53_MODEL.json.
- **ACTUAL [S53 native Windows run 37963793887](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37963793887), job 113932945073 COMPLETED SUCCESS** on commit 83a94f89e2766dafede7c4e73682e8c77b0b9947: Windows Python 3.10 compileall PASS, **813/813 Stage S01–S53 Python unit tests PASS**, real `PASS_NATIVE_S53_TK_FINAL_POLL_LOCK_TOTAL_TIMEOUT`; S52/S51/S50/S49/S48/S47/S46/S45/S44/S43/S42/S41/S40/S39/S38/S37/S35/S34/S33/S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native Windows regression steps ALL PASS. Test-only artifact **11632497916**.
- **ACTUAL [S36 diagnostic Windows run 37963689713](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37963689713), job 113932595800 COMPLETED SUCCESS** on S53 corrected source/tests: **813/813 tests PASS**, packaged S36 EXE normal/unverified CLI both `EXPLICITLY_BLOCKED_NO_GUI`, unverified exit **2**; artifact **11632108310**. EXE is strictly FAIL-CLOSED DIAGNOSTIC NOT PRODUCT. Missing authentic signed Info, F05/F06 real game open/login, authorized close-all/PC actions, original full runtime/UI parity; none invented.
- Explicit user scope lock held: no Proxy runtime, no F02 account writes, F09 unknown stored boolean decodes, fake Login scheduler/buttons, native game operations, or original source ZIP mutation. No speculative new feature outside S53 cleanup timeout.
- **STATUS S53_VERIFIED_NATIVE_WINDOWS_813_TESTS_PASS_FINAL_LOCK_TIMEOUT**.

## S53 CHANGED FILES
- src/login_schedule_worker.py (only stop final _lock bounded by original deadline)
- tests/test_s53.py NEW (9 regression cases)
- tools/S53_WINDOWS_TK_FINAL_LOCK_DEADLINE_SMOKE.py NEW
- .github/workflows/s53-native-tk-final-lock-deadline.yml NEW
- docs/tasks/S53.md; docs/login/S53_STOP_FINAL_LOCK_DEADLINE.md; docs/source/S53_MODEL.json NEW
- STATE.md and PROJECT_STATUS.md append-only

## NEXT_ACTION on CONTINUE — S54
- Reread LIVE PLAN.md and STATE.md; check `docs/tasks/S54.md`. Audit remaining provably faulty S53 `stop` exception/release and worker lifecycle only if concrete source case is reproduced; otherwise prioritize original verified E03 signed Info / real F05/F06 game authentication dependencies without inventing product actions. Preserve **813** verified Windows units, S53–S10 native Windows regression proof and S36 FAIL-CLOSED diagnostic NOT PRODUCT. No Proxy runtime, guessed F02/F09 persisted bool conversion or account INI writes, fake Login controls or game/PC execution. Append checkpoint with completed/ongoing/blockers/changed files/NEXT_ACTION.

## S54 VERIFIED — PERMANENT CLOSED PRIORITY IN ALL STOP TIMEOUT PATHS / 822 WINDOWS TESTS PASS
- Continued from LIVE S53 NEXT_ACTION: reread PLAN.md, STATE.md, current F09 worker and native S53 tests; `docs/tasks/S54.md` initially absent. Confirmed S53 Windows **813/813 PASS** and original E03 signed Info/F05/F06 real action blockers. User explicitly prohibits Proxy development.
- **Independently reproduced S53 source-level state bug:** `F09ScheduleEvaluationWorker.stop()` wrote unconditional `STOPPING` on 3 deadline-exhaustion paths (lifecycle mutex acquire, real background thread join, final independent polling clock lock). A concurrent/earlier S46 lock-free `request_shutdown()` or real Tk Label Destroy permanently sets `_closed=True`, yet timeout overwrote status with `STOPPING`. The one-way authorization fence continued denying start, but diagnostic state was incorrect/inconsistent with S52 priority.
- NEW `tests/test_s54.py` **9** deterministic genuine-thread cases exercising all 3 permanently closed timeout paths, the corresponding nonclosed STOPPING paths, FakeLabel Destroy with mutex held, healthy shutdown and excluded Proxy/actions/writes. Actual initial [Stage S source run 37967870947](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37967870947), test-first commit `0976855ffec89f6d317d8fa784f6d6ac1c1fa4c8`, ran 822 tests and failed **4 S54** assertions CLOSED vs STOPPING. These pre-fix failures verified the defect and are NOT final CI status.
- **NARROW production fix ONLY in `src/login_schedule_worker.py`**: within `stop()`, all three timeout exits assign `"CLOSED" if self._closed else "STOPPING"`. No change to timeouts, cancellation/join, 20-second worker loop, F09 blocked-only audits, S47–S53 safe cleanup, UI, account or game actions. Source commit **b1b4a5785b2eed4f9bf4f4a79a115697e128592a**.
- NEW `tools/S54_WINDOWS_TK_CLOSED_STOP_TIMEOUT_SMOKE.py` uses real native Windows Tk Label.destroy and independent blocked clock evaluation; F09 worker remains CLOSED through timed-out cleanup, later joins successfully; synthetic settings.ini bytes unchanged. NEW `.github/workflows/s54-native-tk-closed-stop-timeout.yml` checks all S01–S54 Python units and S54–S10 real Windows native regressions; NEW docs/tasks/S54.md, docs/login/S54_STOP_TIMEOUT_CLOSED_PRIORITY_FLOW.md, docs/source/S54_MODEL.json.
- **ACTUAL [S54 real native Windows run 37967989294](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37967989294), job 113947085025 COMPLETED SUCCESS** on workflow commit df312daf323ca45cf85c4fb6a08d247bfcf9bfa2: compileall PASS, **822/822 S01–S54 Python unit tests PASS**, real `PASS_NATIVE_S54_PERMANENT_CLOSE_STOP_TIMEOUT`; all S53/S52/S51/S50/S49/S48/S47/S46/S45/S44/S43/S42/S41/S40/S39/S38/S37/S35/S34/S33/S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native Windows regressions ALL PASS. Test artifact **11634193223**.
- **ACTUAL [S36 Windows diagnostic run 37967905230](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37967905230), job 113946802770 COMPLETED SUCCESS** on S54 source+unit test commit b1b4a5785b2eed4f9bf4f4a79a115697e128592a: **822/822 Python tests PASS**, diagnostic normal/unverified CLI `EXPLICITLY_BLOCKED_NO_GUI`, unverified CLI exit **2**, artifact **11634675089**. EXE strictly DIAGNOSTIC FAIL-CLOSED NOT PRODUCT.
- Blockers unchanged: genuine signed E03 Info authentication, original verified F05/F06 game launch/login, authorized game close-all/OS shutdown, full TLM runtime/UI parity. Not changed: PLAN.md, original TLMTool ZIP, original behaviors; no Proxy runtime, F02 account writes, guessed F09 persisted booleans, fake product scheduler/buttons or game/OS effects.
- **STATUS S54_NATIVE_WINDOWS_822_TESTS_PASS_CLOSED_STOP_TIMEOUT**.

## S54 CHANGED FILES
- src/login_schedule_worker.py (three timeout status assignments only)
- tests/test_s54.py NEW (9 cases)
- tools/S54_WINDOWS_TK_CLOSED_STOP_TIMEOUT_SMOKE.py NEW
- .github/workflows/s54-native-tk-closed-stop-timeout.yml NEW
- docs/tasks/S54.md; docs/login/S54_STOP_TIMEOUT_CLOSED_PRIORITY_FLOW.md; docs/source/S54_MODEL.json NEW
- STATE.md; PROJECT_STATUS.md append-only

## NEXT_ACTION on CONTINUE — S55
- Reread LIVE PLAN.md and STATE.md; check `docs/tasks/S55.md` and current E03 signed Info/F05/F06 authentic action evidence. Only fix an independently reproduced narrow remaining worker lifecycle defect OR source-verified original dependency; avoid reworking correctly verified S01–S54 modules and do not invent Login product behavior. Preserve **822/822** Windows unit tests and S54–S10 real native regressions and S36 diagnostic fail-closed NOT PRODUCT. No Proxy, F02 settings/account write, guessed F09 booleans, unverified game/OS actions or fake product UI. Update completed/ongoing/blockers/exact changed files and NEXT_ACTION.

## USER PRIORITY LOCK — 2026-10-10 — HIGHEST-FIDELITY TLM 2.1.2 PARITY
- Explicit user decision: prioritize faithfully following LIVE PLAN.md over an assistant-proposed faster/reordered roadmap, even if a little slower. Target highest achievable 1:1 fidelity: interface, exact controls, timing, ordering, persistence, real Windows/game behavior, multi-account, failure handling, clean source, reproducible finished EXE. Functionality matters more than cosmetic demo or number of completed tasks.
- PLAN.md remains authoritative; this note does NOT change master-plan scope, bypass original evidence, claim a 1:1 result, or authorize new actions. Preserve user prohibition of Proxy runtime and all existing scope locks.
- Use the PLAN dependency order; optimize only within it by reusing already VERIFIED parts and batching related regression evidence when safe. Do NOT prioritize a quick product EXE over matching real original behavior. Equally, do not spend repeated S55+ turns patching speculative scheduler edge cases instead of following actual PLAN dependencies.
- A task is NOT functionally DONE merely because UI exists, source compiles, 822 tests pass, or S36 diagnostic EXE packages. Enforce original-backed UI parity + behavior parity + runtime parity separately. Do not invent authentication, F05/F06 game/login actions, permissions, settings boolean mapping, or "working" product. Evidence gaps remain explicit blockers.
- When a complete genuine original-backed product slice is ready, test the real Windows/Tk and game behavior (where feasible), then integrate/build. Keep S36 fail-closed until actual production prerequisites exist.

## NEXT_ACTION on CONTINUE — S55 (USER PRIORITY ALIGNED)
- Reread LIVE PLAN.md and STATE.md; check docs/tasks/S55.md. Execute actual NEXT PLAN prerequisite toward 1:1 source/runtime parity rather than a quick EXE shortcut. Start by auditing verified E03 Info/license and F05/F06 dependencies and existing authentic source/Windows evidence; pursue smallest original-backed missing functional dependency that can truly be implemented. Only fix additional stop/worker bug if independently reproduced and materially blocks the plan. Preserve 822 S01–S54 Windows tests, native S54–S10 regressions, diagnostic S36 FAIL-CLOSED NOT PRODUCT. Respect no Proxy runtime, no guessed F02/F09 persisted flags/INI writes, no fake UI/game/OS actions. After milestone append exact files, blockers, actual test/build results and next specific action.

## S55 VERIFIED — SOURCE-BACKED C10/C11 REAL WIN32 STACKING ENGINE / 836 WINDOWS TESTS PASS
- Followed LIVE PLAN.md and STATE.md USER PRIORITY LOCK (highest original 1:1 fidelity and real behavior over shortcut EXE/microfix repetition), checked docs/tasks/S55.md initially absent, E03 signed Info and F05/F06 original-backed blockers, and C10/C11 verified original EXE docs: docs/tasks/C10.md + docs/tasks/C11.md + docs/window/C10_STACK_TIGHT_MODEL.json + docs/window/C11_STACK_DIAGONAL_MODEL.json. Stage S54 prior 822/822 Windows native tests VERIFIED.
- **Concrete missing original-backed feature:** existing Start C18 local grid engine `src/layout_windows.py` did NOT implement C10/C11 shared movement. Original C10 `_stack_tight_cmd` moves all current HWNDs to **(0,0)** without resizing; C11 `_stack_diagonal_cmd` moves them by **(+50,+50) per index**, preserving size; master first. Auto UI/hidden-state reset and live game runtime remain independent parity gaps.
- NEW `src/window_stacking.py`: `C10C11WindowStacker` calls real Win32 `NativeLayoutBackend.move_no_resize` via existing native GetWindowRect/SetWindowPos; exact original C10/C11 target coordinates, master first, preserve size. Use existing S09 cached game HWND/PID, prevalidate entire batch executable+class/title+PID, recheck before each mutation, externally validated max_windows>0 and revocable callback, no invented grid layout or Auto tile timer. This source is a functional engine, **not** an exposed/integrated TLM 1:1 UI button.
- NEW `tests/test_s55.py` **14** original geometry and identity/cancellation tests. Test-first Stage S CI 37976839635 intentionally red with missing module; source implementation commit **658b7878ce75a1d271bb21cc2c6dd084cefdc9ec** and corrected Stage S run **37976877953 COMPLETED SUCCESS**.
- NEW `tools/S55_WINDOWS_C10_C11_MOVE_ONLY_SMOKE.py` exercises two genuine test-owned Tk Win32 HWNDs with actual SetWindowPos and GetWindowRect. An explicit local TEST-only identity adapter only admits those two Python/Tk windows; native backend itself recognizes them as **NOT GAME**, so never claim authentic game or Info token proof. NEW `.github/workflows/s55-native-c10-c11-stacking.yml` full S01–S55 unit and S55–S10 native windows regressions. NEW docs/tasks/S55.md; docs/window/S55_C10_C11_NATIVE_ENGINE.md; docs/source/S55_MODEL.json.
- **ACTUAL [S55 native Windows run 37976990927](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37976990927), job 113977679594 COMPLETED SUCCESS**, workflow commit ea3a115be46205eeb75e0e5023428cdbc5682eb5: **836/836 Windows S01–S55 Python unit tests PASS**, real `PASS_NATIVE_S55_C10_C11_TEST_OWNED_MOVE_ONLY`, and S54/S53/S52/S51/S50/S49/S48/S47/S46/S45/S44/S43/S42/S41/S40/S39/S38/S37/S35/S34/S33/S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native regressions PASS. Artifact **11638608497**, **TEST ONLY**.
- **ACTUAL [S36 Windows packaged diagnostic run 37976877949](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37976877949), job 113977298815 COMPLETED SUCCESS**, corrected source/tests commit 658b7878ce75a1d271bb21cc2c6dd084cefdc9ec: **836/836 unit tests PASS**, diagnostic normal/unverified CLI `EXPLICITLY_BLOCKED_NO_GUI`, unverified exit 2, artifact **11639372051**, strictly **NOT PRODUCT EXE**.
- Known blockers/parity distinctions: original C10/C11 buttons inside Auto frame are not integrated into Start; C12 `_reset_hidden_state` not connected; exact interaction with running 1s Auto tiling UNKNOWN; test-only Win32 proves window movement, NOT game authenticity or product 1:1 parity. E03 authentic signed Info, F05/F06 real login/game launch, broad Party/Train/Phó Bản/... controllers still missing. No Proxy runtime (user lock), no F02 account INI write or guessed F09 settings, no game process injection, no fake Login actions. PLAN/original archive untouched.
- **STATUS S55_NATIVE_WINDOWS_836_TESTS_PASS_C10_C11_ENGINE_ONLY**.

## S55 CHANGED FILES
- src/window_stacking.py NEW — source-backed C10/C11 backend, not UI wired
- tests/test_s55.py NEW — 14 regression cases
- tools/S55_WINDOWS_C10_C11_MOVE_ONLY_SMOKE.py NEW
- .github/workflows/s55-native-c10-c11-stacking.yml NEW
- docs/tasks/S55.md; docs/window/S55_C10_C11_NATIVE_ENGINE.md; docs/source/S55_MODEL.json NEW
- STATE.md; PROJECT_STATUS.md append-only

## NEXT_ACTION on CONTINUE — S56 (PLAN.md highest-fidelity priority)
- Reread LIVE PLAN.md and STATE.md; check docs/tasks/S56.md and original C05/C06/C07/C10/C11 Auto-frame screenshot geometry/static evidence. Integrate C10/C11 **already implemented true Win32 stack actions** into a faithful Start Auto control frame only once exact UI geometry/callbacks can be grounded; do not invent buttons, mode interactions, or assume an unimplemented C12 hide-state tracker. Keep Win32 actual movement off Tk UI thread and gated by verified max_windows/current HWND/PID and revocation. Validate real Windows/Tk with test-owned HWND; do not claim live game proof. If evidence insufficient, gather static original UI details and document blocker rather than a synthetic frame. Preserve **836/836** Windows unit tests, native S55–S10 and S36 diagnostic FAIL-CLOSED NOT PRODUCT. No Proxy, guessed F02/F09 flags, fake login, unauthorized game/OS action. Append exact paths, CI and NEXT_ACTION after milestone.

## S56 VERIFIED — START C10/C11 ASYNC CALLBACKS + REAL TK REVOCATION / 846 WINDOWS TESTS PASS
- Followed LIVE PLAN.md / STATE.md and user highest-fidelity lock; original C05/C06/C07/C10/C11 EXE static evidence, B01/B02/B13/B14 screenshot manifests, S55 true C10/C11 native Win32 engine. `docs/tasks/S56.md` initially absent. Did NOT make up unsupported Auto mode UI or change PLAN.md.
- **Exact gap:** original labels/callbacks Xếp gọn→`_stack_tight_cmd`, Xếp chéo→`_stack_diagonal_cmd` are verified, but currently shipped `src/start_tab.py` lacked both callback bindings and lifecycle integration. Existing B14 metadata references original `TLMTool_rARyQTv9Ta(2).png` SHA256 4f1b126ea4ba0034889545653046f552a226d5f0033d2329a8693342184c28cd, **but image bytes and exact Auto control rectangles are NOT in repository**. Preserving original 1:1 fidelity means NO fabricated button positions.
- Narrow actual source change ONLY `src/start_tab.py`: added S55 stack engine factory as optional injectable native component, verified original-named `_stack_tight_cmd()` and `_stack_diagonal_cmd()`; `_dispatch_auto_stack` checks Start selected/visible/poller active, genuine externally supplied positive `layout_max_windows`, valid S09 cached HWND snapshot, current master, no active conflicting grid sync and no concurrent native mover. Starts native C10/C11 Windows SetWindowPos in background worker; callback returns promptly without blocking Tk. Cancellation event + operation generation prevent later moves/status publication on master selection change, permission limit revoke, tab hide or shutdown; no Tk mutation from worker. **NO GUI BUTTONS ADDED** until pixel evidence, no original C07 tiler or C12 hidden-state reset invented.
- NEW `tests/test_s56.py` **10** deterministic tests for correct C10/C11 callbacks, master/limit/snapshot forwarding, nonblocking worker dispatch, overlapping request rejection, cancellation/revoke/close, stale result epoch, invalid preconditions/mode, and no fabricated UI/auth. NEW `tools/S56_WINDOWS_TK_START_STACK_LIFECYCLE_SMOKE.py`: actual Windows Tk Notebook/Start with TEST-ONLY permission grant + two TEST-OWNED Tk windows; actual native SetWindowPos C11/C10 exact original coordinates, size unchanged, asynchronous UI responsive, revoked permission cancels pending stack. Production native backend still recognizes Python/Tk windows as **NOT game**.
- First full native run **38012574137 FAILED TEST HARNESS**: test synchronously joined native worker from Tk main thread while Win32 needed UI thread to dispatch messages to Tk target windows. Corrected harness alone by pumping actual Tk messages, commit **a86c93b9f3848e6a78c2d8599ad07ec81f6e783b**, preserving product/source behavior. Deterministic source tests already passed.
- **ACTUAL [S56 native Windows run 38012667924](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38012667924), job 114095959034 COMPLETED SUCCESS**: Windows compileall PASS; **846/846 S01–S56 Python unit tests PASS**; `PASS_NATIVE_S56_START_C10_C11_ASYNC_LIFETIME` (real Tk/SetWindowPos and cancellation); all native Windows S55/S54/S53/S52/S51/S50/S49/S48/S47/S46/S45/S44/S43/S42/S41/S40/S39/S38/S37/S35/S34/S33/S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 regressions PASS; test-owned artifact **11655690342**.
- **ACTUAL [S36 diagnostic Windows run 38012474109](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38012474109), job 114095320538 COMPLETED SUCCESS** on S56 changed source/tests commit b455d488bb56fb061896cfc3c0a6c0ed70e2bfcf: **846/846 unit tests PASS**, normal/unverified CLI `EXPLICITLY_BLOCKED_NO_GUI`, unverified exit 2, artifact **11655640058**. Diagnostic EXE strictly FAIL-CLOSED NOT PRODUCT.
- Blockers unchanged: exact original Auto frame/button pixels absent from repo; original C07 1s tiler coexistence UNKNOWN, original C12 `_reset_hidden_state` not integrated, genuine E03 signed Info, real F05/F06 game launch/login and full TLM production UI/runtime not present. NO REAL game process was operated on in S56 CI. No Proxy runtime, guessed F02/F09 settings, or unauthorized game actions; PLAN/original archive untouched.
- **STATUS S56_NATIVE_WINDOWS_846_UNIT_PASS_REAL_TK_ASYNC_CALLBACKS_ONLY**.

## S56 CHANGED FILES
- src/start_tab.py — C10/C11 actual callback-to-native-engine dispatch, cancellation and lifetime integration ONLY
- tests/test_s56.py NEW (10 unit cases)
- tools/S56_WINDOWS_TK_START_STACK_LIFECYCLE_SMOKE.py NEW (real Tk and test-owned Windows HWND)
- .github/workflows/s56-native-start-stack-lifecycle.yml NEW
- docs/tasks/S56.md; docs/window/S56_START_ASYNC_STACK_FLOW.md; docs/source/S56_MODEL.json NEW
- STATE.md; PROJECT_STATUS.md append-only

## NEXT_ACTION on CONTINUE — S57 (USER FIDELITY PRIORITY)
- Read LIVE PLAN.md and STATE.md; check docs/tasks/S57.md and ORIGINAL screenshot pixel evidence `TLMTool_rARyQTv9Ta(2).png` (SHA256 4f1b126ea4ba0034889545653046f552a226d5f0033d2329a8693342184c28cd). Obtain genuine original bitmap from accessible user-supplied original image/forensic material; compare with B01/B02/B13/B14 and C07/C10/C11 static contracts. Then add measured faithful Start Auto frame/mode and Xếp gọn/Xếp chéo real Tk buttons wired to **already implemented S56 callbacks**, without guessing layout or additional feature buttons. If original raster unavailable, explicitly record blocker and continue substantive verified original C12 hidden-state mechanism or another Plan prerequisite without fabricating 1:1 UI. Preserve **846/846** native Windows tests, S56–S10 regressions, S36 diagnostic fail-closed EXE NOT PRODUCT. Do NOT develop Proxy, guess F02/F09 account flags/writes, inject, fake original Info/login, or claim actual game-runtime parity. Checkpoint files/evidence/CI/NEXT_ACTION.

## S57 VERIFIED — ORIGINAL-BACKED C12 HIDE-ONLY WIN32 / 858 WINDOWS TESTS PASS
- Read LIVE PLAN.md + STATE.md S56 NEXT_ACTION and original C12 static evidence, S55/S56 Start source, B14 Auto screenshot metadata; `docs/tasks/S57.md` initially absent. Highest-fidelity user priority remains mandatory: no fabricated Auto frame/button geometry or claimed product/game parity.
- **Original specimen newly verified from mounted original archive**: `TLMTool_2.1.2(20261009-142633).zip` SHA256 **c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd**, exactly Gate A; nested `TLMTool.dist/TLMTool.exe` SHA256 **15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22**, exactly frozen original. ZIP contains splash.png, no original `TLMTool_rARyQTv9Ta(2).png` screenshot. Search of accessible user/library images returned no original Auto bitmap. B14 hash alone cannot authorize a fabricated pixel UI.
- Read C12 original `docs/tasks/C12.md`: `_hide_all_game_windows` moves game HWNDs to EXACT **(-2200,-2200)** via position-only SetWindowPos and `GetWindowRect` saved state, preserves dimensions/Win32 visibility (avoid hiding Unity rendering). `_show_all_game_windows` has documented **CONFLICT**: generic restore to prior screen rects versus specific log/doc restore to (0,0). No actual runtime trace resolves this conflict; no guess is allowed.
- NEW `src/window_hide.py`: native real `C12HideAll.hide` with exact off-screen targets; master first; validate entire S09 source HWND/PID/game executable/class/title before movement, revalidate per HWND; externally VERIFIED positive `max_windows`, revocable `allowed()` flag; save pre-move HWND/PID/rect and avoid overwriting on repeat. Track VISIBLE/HIDDEN/PARTIAL; on mid-batch interruption return actual changed HWNDs and original rectangles, refuse repeat hide until authentic reconciliation instead of a false success. NO `show`/`restore` implementation or guessed Auto button.
- NEW `tests/test_s57.py` **12** deterministic original C12 conditions: (-2200,-2200), old-rect bookkeeping and size, master-first, repeat, license limit, stale identity, duplicate cache, cancellation/partial, no fabricated restore/Proxy. Test-first Stage S run **38013209567** intentionally red on missing module, corrected source commit **ac35265b88e2673b2b633254fe70a05a3059c4c6**, corrected Stage S run **38013244212 COMPLETED SUCCESS (858/858 tests)**. NEW `tools/S57_WINDOWS_C12_HIDE_ONLY_SMOKE.py`, `.github/workflows/s57-native-c12-hide-only.yml`; NEW docs/tasks/S57.md, docs/window/S57_C12_HIDE_ONLY_FLOW.md, docs/source/S57_MODEL.json.
- **ACTUAL [S57 native Windows run 38013306386](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38013306386), job 114097986667 COMPLETED SUCCESS**, workflow commit **0c0543ec7045cd044a4351f979e01c72abefd0a5**: compileall PASS, **858/858 Python S01–S57 unittest PASS**, `PASS_NATIVE_S57_C12_HIDE_ONLY_TEST_OWNED_WINDOWS`; actual Win32 SetWindowPos on two test-created Tk HWNDs to (-2200,-2200), original windows sizes and Win32 visibility preserved, original rects saved, repeat hide not rewriting, missing permission blocked, original native identity shows Python not game; S56–S10 native Windows regression jobs ALL PASS. Artifact **11654662005**, TEST-ONLY.
- **ACTUAL [S36 packaged diagnostic Windows run 38013244150](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38013244150), job 114097773624 COMPLETED SUCCESS**, corrected source/tests commit ac35265b88e2673b2b633254fe70a05a3059c4c6: **858/858 tests PASS**, `PASS_NATIVE_S36_PACKAGED_DIAGNOSTIC_FAIL_CLOSED_NOT_PRODUCT`, normal/unverified CLI `EXPLICITLY_BLOCKED_NO_GUI`, artifact **11654571939**; diagnostic EXE NOT PRODUCT.
- **Scope/parity blockers:** C12 restore branch unresolved, original Auto screenshot bitmap not accessible, no honest Start C12 button integration, existing S55/S56 C10/C11 native mechanics not game-tested, E03 signed Info/F05/F06 original game auth/actions missing, real production EXE unavailable. NO Proxy runtime, F02 account write, guessed F09 booleans, injection or unauthorized game/OS activities. PLAN.md/original archive unchanged.
- **STATUS S57_NATIVE_WINDOWS_858_TESTS_PASS_C12_HIDE_ONLY_ENGINE**.

## S57 CHANGED FILES
- src/window_hide.py NEW — original-backed actual hide-only Win32 engine
- tests/test_s57.py NEW — 12 tests
- tools/S57_WINDOWS_C12_HIDE_ONLY_SMOKE.py NEW
- .github/workflows/s57-native-c12-hide-only.yml NEW
- docs/tasks/S57.md, docs/window/S57_C12_HIDE_ONLY_FLOW.md, docs/source/S57_MODEL.json NEW
- STATE.md, PROJECT_STATUS.md append-only

## NEXT_ACTION on CONTINUE — S58 (highest-fidelity original PLAN priority)
- Reread LIVE PLAN.md and STATE.md; check `docs/tasks/S58.md` plus original C12 `_show_all_game_windows` evidence and Auto screenshot filename+SHA. Determine ACTUAL original "Hiện hết" restore behavior (saved HWND rectangles vs (0,0)) from authenticated original runtime evidence/compiled source, not guesses; reconcile HIDDEN/PARTIAL safely on real HWND+PID and connect `_hide_windows_cmd` to Start only when correct true toggle and original button geometry are established. If evidence remains insufficient, make a distinct substantive original-backed component in PLAN, without fake UI. Preserve **858/858** native Windows units, S57–S10 regressions, S36 fail-closed diagnostic NOT PRODUCT. No Proxy, guessed settings/account writes, fake Info/game actions or unverified production EXE. Checkpoint completed/blocked/source changes/exact CI IDs and NEXT_ACTION.

## S58 VERIFIED — ORIGINAL C12 HIDDEN RESET AFTER PROVEN C10/C11 RE-LAYOUT / 870 WINDOWS TESTS PASS
- Followed LIVE PLAN.md / STATE.md `S57 NEXT_ACTION`, inspected existing `docs/tasks/C12.md`, original verified Gate A inner TLMTool.exe C12 UTF-8 serialized strings in offset neighborhood 0x2bfb...: `_show_all_game_windows`, `_saved_window_rects`, `_reset_hidden_state`. Original generic toggle doc claims return to old positions; specific show doc/log states (0,0). **Actual executable branch remains UNRESOLVED**; no invented show() or restore() or false claim of product UI. Original Auto screenshot bitmap still inaccessible (B14 only name/metadata).
- **Independent original-backed behavior**: after a REAL re-layout to visible positions, `_reset_hidden_state` clears hide bookkeeping. EXTENDED ONLY `src/window_hide.py` `C12HideAll.reset_after_verified_layout(snapshot,mode,master_hwnd,allowed)` with pure read-only Win32 checks: all pre-hide saved HWND/PID still present and valid; currently visible genuine game process/class/title; exact original C10 tight (0,0) or C11 diagonal (50*i,50*i), master first; revocation guards. Clears HIDDEN/PARTIAL + saved rects only when all relevant actual HWNDs truly match the visible layout. No Win32 SetWindowPos here, no fake C12 restore. This geometry gate is an explicit **S58 local safety policy**, not claimed exact Nuitka source.
- NEW `tests/test_s58.py` **12** deterministic tests: genuine S57 hide then S55 C10/C11 visible movement, verified state reset; block premature/offscreen/one misplaced HWND, wrong mode/master, stale PID/reused missing/duplicated HWND, revoke, partial hide, no movement by reset. Test-first red [Stage S 38014548132](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38014548132), source commit **36e9ff38a0fdfd7845d15adf9702cdba714c9c6a**; corrected Stage S [38014593549](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38014593549) **870/870 PASS**.
- NEW `tools/S58_WINDOWS_C12_RELAYOUT_RESET_SMOKE.py` actual Windows Tk test-owned HWNDs: original C12 hide via SetWindowPos(-2200,-2200), C11 actual move to (0,0)/(50,50), then read-only hidden reset; native Python windows require an explicitly test-owned local identity adapter, **NOT authentic game**. NEW `.github/workflows/s58-native-hidden-state-reset.yml`, native regressions S58–S10, docs/tasks/S58.md; docs/window/S58_HIDDEN_RESET_AFTER_LAYOUT_FLOW.md; docs/source/S58_MODEL.json.
- Initial native S58 run **38014634555** had **all native assertions TRUE** and 870 unit tests passed, but test exited false negative because harness final success-code string remained outdated. Fixed ONLY test harness status comparison in **a2e05733c637fca71f51e8f93c1a5edade6bf56e**, source unchanged.
- **ACTUAL [S58 native Windows run 38014711926](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38014711926), job 114102317945 COMPLETED SUCCESS**: Windows compileall PASS, **870/870 S01–S58 Python units PASS**, `PASS_NATIVE_S58_C12_RELAYOUT_RESETS_HIDDEN_TEST_OWNED_WINDOWS`; S57/S56/S55/S54–S10 all native Windows regressions PASS; test-only artifact **11655259429**.
- **ACTUAL [S36 diagnostic Windows run 38014593484](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38014593484), job 114101954393 COMPLETED SUCCESS** on S58 updated source commit 36e9ff38a0fdfd7845d15adf9702cdba714c9c6a: **870/870 tests PASS**, packaged `PASS_NATIVE_S36_PACKAGED_DIAGNOSTIC_FAIL_CLOSED_NOT_PRODUCT`, normal and unverified CLI `EXPLICITLY_BLOCKED_NO_GUI`, exit 2, artifact **11655064286**, **NOT PRODUCT EXE**.
- Outstanding original parity blockers: C12 show/restore actual branch (old saved rect vs (0,0)) NOT recovered; no verified Auto screenshot pixel rectangles/UI controls; Start hidden-state owner/callback not wired; no genuine E03 signed Info/F05/F06 game actions, other functional tabs, or real live Thần Long parity. No Proxy runtime, F02 account writes, guessed F09 flags, game injection or fabricated UI. Original archive and PLAN untouched.
- **STATUS S58_NATIVE_WINDOWS_870_UNIT_PASS_C12_READONLY_RESET_ONLY**.

## S58 CHANGED FILES
- src/window_hide.py — read-only verified C12 hidden reset method and HiddenResetResult; original S57 hide preserved
- tests/test_s58.py NEW (12 cases)
- tools/S58_WINDOWS_C12_RELAYOUT_RESET_SMOKE.py NEW
- .github/workflows/s58-native-hidden-state-reset.yml NEW
- docs/tasks/S58.md, docs/window/S58_HIDDEN_RESET_AFTER_LAYOUT_FLOW.md, docs/source/S58_MODEL.json NEW
- STATE.md and PROJECT_STATUS.md append-only

## NEXT_ACTION on CONTINUE — S59 (ORIGINAL 1:1 PLAN PRIORITY)
- Reread LIVE PLAN.md + STATE.md, check docs/tasks/S59.md and original C12 `_show_all_game_windows` compiled flow AND original Start Auto screenshot `TLMTool_rARyQTv9Ta(2).png`. Do not choose an arbitrary restore rule (previous positions versus (0,0)); recover genuine source/runtime evidence first, then connect safe full C12 hide/show to measured faithful Tk Auto UI. If evidence still insufficient, move to next independent original-backed PLAN functionality with complete real Windows behavior, and record original parity blocker. Preserve **870/870 Windows tests**, native S58–S10 and S36 fail-closed DIAGNOSTIC NOT PRODUCT. No Proxy runtime, fabricated server rights, guessed F02/F09 writes, fake original Login/game activity or cosmetic-only buttons. Append actual files/run IDs/status/NEXT_ACTION.

## S59 IN PROGRESS — ORIGINAL AUTO BITMAP RECOVERED / REAL C10-C11 BUTTONS
- Base LIVE main: 72e2cd0e9a09b52a558068fd4e57b25d69ab3cb8. Read PLAN/STATE and reran 870 baseline tests PASS. `docs/tasks/S59.md` did not exist; no S59 implementation to redo.
- **Missing-original-image blocker RESOLVED**: user original `TLMTool_rARyQTv9Ta(10).png` exactly matches B14 SHA256 4f1b126ea4ba0034889545653046f552a226d5f0033d2329a8693342184c28cd. Committed exact raster `docs/ui/original/START_AUTO.png`; measured two 78x21 C10/C11 controls and #4169e1; EXE confirms Segoe UI 8 bold. ZIP/inner EXE hashes exactly Gate A.
- Added measured partial ttk Auto quick frame and real Xếp gọn/Xếp chéo Tk buttons to existing S56 async callbacks; no stack engine rewrite, no C07 fake mode radio or C12 guessed restore. Diagnostic controls remain below. Original full UI/runtime parity NOT claimed.
- Local test-first: three failures for absent builder, then **874/874 complete units PASS**, compileall PASS. Native S59 workflow tests actual Button.invoke through native Win32 on owned Tk windows; results PENDING. Full original-game runtime and product EXE still unavailable.
- Files: src/start_tab.py; tests/test_s56.py; tests/test_s59.py; tools/S59_WINDOWS_MEASURED_AUTO_BUTTONS_SMOKE.py; .github/workflows/s59-native-measured-auto-buttons.yml; docs/ui/original/START_AUTO.png; docs/tasks/S59.md; docs/source/S59_MODEL.json; STATE.md; PROJECT_STATUS.md.
- Rulings and limits recorded in docs/tasks/S59.md. PLAN, other functional tabs, Proxy and game auth unchanged.

## NEXT_ACTION — finish S59 verification, then S60
- Inspect S59 native Windows run and S36 diagnostic packaging on the S59 commit; fix only observed failures. Independently review branch, merge verified checkpoint to main, append actual run IDs/results. Then use repository original START_AUTO.png (now available) and original C12 compiled flow to recover true restore; no invented mode controls. Keep all completed S01–S58 mechanisms. Full original production executable remains NOT COMPLETE.

### S59 review checkpoint
- Independent reviewer reproduced overlapping S56 stack and S17 grid workers when the two exposed UI commands are invoked in succession. Two targeted tests were RED, then GREEN after adding mutual worker-liveness checks in Start dispatch; native engines unchanged. This is a local coexistence guard, not an invented claim about original C07 behavior.
- Re-graded the unused temporary-config assertion as evidence-integrity work: inject the actual GridSettingsStore(cfg) in the S59 native harness, so the existing no-settings-write assertion checks the file it really reads.
- Final local suite **876/876 PASS**; compileall and diff whitespace checks PASS. No deferred reviewer findings. Native Windows run still pending at this checkpoint.

## S59 VERIFIED — ORIGINAL BITMAP + PIXEL-EXACT C10/C11 BUTTONS / 876 WINDOWS TESTS
- Tested source commit **1312cf3f466e8661e3df99208caa986a6d4b9564**, tree **26e9a3d8aabf2be660cc9c58308e6bcd14c5cc7f** (same tree as local tested work). GitHub branch task/s59-original-auto-buttons. Independent reviewer found conflicting native movers; two tests reproduced RED, narrow UI-worker coexistence checks made them GREEN. Actual native engines unchanged.
- **[S59 Windows native run 38016032895](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38016032895), job 114106364563 COMPLETED SUCCESS**: Windows compileall; **876/876 S01–S59 tests**; PASS_NATIVE_S59_MEASURED_BUTTONS_REAL_MOVEMENT; actual Tk Button.invoke → original-backed C11/C10 native SetWindowPos, master-first, no resize, nonblocking, duplicate/grid conflict rejection and permission revocation all PASS. S58–S10 native regressions in that workflow all PASS. Test-owned artifact **11656705810**.
- Downloaded real native capture and inspected it. **Both button crops match original raster byte-for-byte as RGB pixels: 0 differing pixels out of 1,638 for each button (3,276 total)**. Labels, color, border, typography match in these two measured regions. Evidence: docs/ui/S59_NATIVE_AUTO_FRAGMENT.png, docs/ui/S59_PIXEL_COMPARISON.json, docs/source/S59_NATIVE_RESULT.json. **This proves ONLY two buttons, not whole Start UI parity.** Group/mode/remaining controls not counted as passed.
- **[S36 Windows diagnostic packaging run 38016033232](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38016033232), job 114106365825 COMPLETED SUCCESS**: 876 tests, actual PyInstaller EXE/COLLECT build, PASS_NATIVE_S36_PACKAGED_DIAGNOSTIC_FAIL_CLOSED_NOT_PRODUCT, both normal and unverified attempts EXPLICITLY_BLOCKED_NO_GUI. Artifact **11656241858**. It remains a DIAGNOSTIC, not a usable complete TLM product.
- All **16** workflows triggered on this source commit COMPLETED SUCCESS, including dedicated S10–S18, S24, S56/S57/S58, source regression, S59 and diagnostic packaging. No skipped failure treated as success.
- User's highest-fidelity priority retained. Source changes limited to Start measured fragment and worker coexistence; S56 lexical no-button assertions superseded by genuine raster evidence; all existing behavioral tests retained. No proxy runtime, auth fabrication, original game launch/login or unsupported Auto/hide/show control.
- Rulings: no C07 mode radio until its full sync/reset/tiler behavior exists; no C12 toggle until compiled restore branch is resolved; original-raster condition supersedes S56 no-button assertion. Cost: partial Start UI remains visibly incomplete, with only implemented controls. No deferred reviewer findings.

## S59 FINAL CHANGED FILES
- src/start_tab.py; tests/test_s56.py; tests/test_s59.py (6 new cases)
- tools/S59_WINDOWS_MEASURED_AUTO_BUTTONS_SMOKE.py; .github/workflows/s59-native-measured-auto-buttons.yml
- docs/ui/original/START_AUTO.png (EXACT ORIGINAL, use for future tasks)
- docs/ui/S59_NATIVE_AUTO_FRAGMENT.png; docs/ui/S59_PIXEL_COMPARISON.json
- docs/tasks/S59.md; docs/source/S59_MODEL.json; docs/source/S59_NATIVE_RESULT.json
- STATE.md; PROJECT_STATUS.md

## NEXT_ACTION on CONTINUE — S60 (S59 complete; do not redo)
1. Reread LIVE PLAN.md / STATE.md. Original Auto image is NOW AVAILABLE at docs/ui/original/START_AUTO.png, hash 4f1b126ea4ba0034889545653046f552a226d5f0033d2329a8693342184c28cd. Do NOT search for or re-create it; C10/C11 buttons are already wired and native/pixel verified.
2. Resolve C12 `_show_all_game_windows` from compiled executable control flow, not conflicting docstrings. Hash-verified original inner EXE 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22 can be obtained from original Library archive `TLMTool_2.1.2(20261010-020034).zip` (libfile_44eaa9a0e85481918bcd237f8d2e9c33; archive hash c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd). Scratch original exists this turn but may expire.
3. Initial binary lead ONLY (not a recovered behavior): image base 0x140000000; module constant initialization at VA 0x141e69280 loads module name start_tab at file offset 0x2c8dfa2 and constants-array address 0x142da6e00, then calls VA 0x142378140. `_show_all_game_windows` names appear at file offsets 0x2bfb168 and 0x2bffe28. Decode correct original constants mapping and trace actual native method before choosing old-rect vs (0,0). This lead has NOT resolved restore.
4. Once proven, implement complete hide/show lifecycle owner and measured original control using existing S57/S58 hide/reset plus S56 cancellation. If control-flow evidence still unavailable, move to another independent original-backed PLAN prerequisite; do not add fake UI or spend another task repeating evidence-only UNKNOWN.
5. Preserve **876/876** tests, S59–S10 native regressions, two-button pixel match and S36 fail-closed diagnostic. No Proxy, guessed F02/F09 writes, forged Info or claim of game-runtime/product parity. Record exact changed files/actual CI/NEXT_ACTION after each milestone.


## S60 IMPLEMENTED — REAL C12 POST-MOVE TRUTH CHECK (CI PENDING)
- Read live PLAN.md, STATE.md S59 NEXT_ACTION, original uploaded ZIP hash c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd and inner EXE hash 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22 (both original Gate A). PE method names confirmed but compiled C12 show branch STILL UNKNOWN; no guessed restore.
- Reproduced S57 hide source defect: true move return can be a false physical move, yet old code marked HIDDEN. Narrow safety change verifies HWND/PID and post-move GetWindowRect position (-2200,-2200), original dimensions, and marks PARTIAL on mismatch even when last HWND returned success.
- CHANGED src/window_hide.py; NEW tests/test_s60.py (6 tests), .github/workflows/s60-native-c12-readback.yml, docs/tasks/S60.md; STATE.md + PROJECT_STATUS.md append-only. No S59 redo, original ZIP/PLAN untouched, no Proxy, fake controls, signed Info or purported finished product EXE.
- Native Windows S60 CI PENDING at initial commit.

## NEXT_ACTION on CONTINUE — VERIFY S60 THEN S61
- Inspect Windows S60 native full Stage S units, test-owned S59–S10 native checks, S36 diagnostic fail-closed. Repair only genuine failures; append actual commit/run/test results and precise changes. Then S61 follow original-backed C07 mode/tiler/Start parity or another demonstrable PLAN prerequisite, no guessed C12 show or repeat of S59. Preserve original fidelity and no Proxy.


## S60 VERIFIED — 882/882 REAL WINDOWS REGRESSION, DIAGNOSTIC BUILD SUCCESS
- **SOURCE COMMIT d4d0a34b037580687710450bf0ceec938e614f2b**: exactly src/window_hide.py safety fix, 6 new S60 units, new S60 Windows workflow and S60 evidence docs; S59 authentic measured Start C10/C11 buttons/architecture unchanged.
- **ACTUAL [S60 Windows native run 38017757968](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38017757968), job 114111741498 COMPLETED SUCCESS**. Windows compileall succeeded; **882/882 S01–S60 unittest PASS** (10.504 sec), the six S60 false-success/resize/PID cases separately **6/6 PASS**, native S59 (real Tk buttons + real test-owned Win32 movement), S58 (verified visible reset), S57 (real -2200 off-screen hide), S56–S10 regression checks ALL PASS. Artifact **11657240229** (test-owned Windows evidence, not game).
- **ACTUAL [S36 Windows diagnostic packaged run 38017757852](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38017757852), job 114111741285 COMPLETED SUCCESS**: **882/882 tests PASS**, native S36 actual packaged executable test **PASS_NATIVE_S36_PACKAGED_DIAGNOSTIC_FAIL_CLOSED_NOT_PRODUCT**, normal and unverified CLI attempts **EXPLICITLY_BLOCKED_NO_GUI**. Artifact **11656998159**, strictly DIAGNOSTIC ONLY and NOT a usable TLM product.
- Other actual completed-success source commit checks: Stage S source **38017757850**, S59 native **38017757851**, S58 native **38017757868**, S57 native **38017757911**. No observed CI failure or attempted rewrite of prior S01–S59 code.
- Original C12 show/restore branch STILL UNRESOLVED (0,0 vs saved rects). No false UI toggle; original signed Info, F05/F06 game launch/login, C07 mode/input tiler, whole parity and production EXE remain missing. S60 post-move verification is conservative safety policy, not proof of matching internal Nuitka statements. No real game HWNDs in CI, no Proxy runtime, no account writes/forged entitlement.
- **STATUS S60_NATIVE_WINDOWS_882_UNIT_PASS_DIAGNOSTIC_ONLY_EXE**.

## S60 FINAL CHANGED FILES
- src/window_hide.py (single isolated C12 post-move readback check)
- tests/test_s60.py (6 new targeted tests)
- .github/workflows/s60-native-c12-readback.yml
- docs/tasks/S60.md
- STATE.md; PROJECT_STATUS.md (append-only)

## NEXT_ACTION on CONTINUE — S61 (ORIGINAL PARITY PRIORITY)
1. Read LIVE PLAN.md / STATE.md and check docs/tasks/S61.md; do not repeat S60/S59.
2. Study original C07 Auto mode/tiler from docs/tasks/C07.md, docs/tasks/C08.md and original locked PE, with screenshot docs/ui/original/START_AUTO.png. Source-backed C07: values auto/sync, selection transitions must stop active Train/Trừng ác/Tàng bảo đồ before sync, sync enables layout PLUS input, Auto disables both, Auto reset (0,0) 1366x768 and 1-second auto tile loop, sort RoleName + master first. Some code edges, tiling geometry, original input sync and condition ordering remain UNKNOWN: do NOT ship radio-only visual mock, destructive window resize or unsupported input-sync behavior.
3. Identify independently verifiable C07 subcomponent that can be completed/tested on test-owned native Windows, or another authentic PLAN component. Implement only proven narrow functionality, keep Win32 operations worker-threaded and verified permission/HWND/PID. If no valid source-backed implementation, document blocker rather than invent a 1:1 feature.
4. Preserve **882/882 Windows units**, native S60/S59–S10 regressions and S36 diagnostic EXE fail-closed. No Proxy, guessed F02/F09 saved values, fake Info/game actions, screenshots as proof of runtime, or false claim of completed product EXE. Append exact files, CI IDs and next action after each milestone.


## S61 IMPLEMENTED — ORIGINAL C07 (0,0) 1366x768 RESET PRIMITIVE (CI PENDING)
- Continued exactly from S60 VERIFIED NEXT_ACTION. Read PLAN/STATE, C07/C06 static proof and existing S17 native code. Original C07 exact Auto transition target (0,0) 1366x768, GetWindowPlacement/ShowWindow(SW_SHOWNORMAL)/SetWindowPos(SWP_NOMOVE) resize family confirmed; tiler layout and 1s transition edges UNKNOWN.
- NEW src/window_auto_reset.py: independent original-backed C07 final-geometry reset (verified HWND/PID, external max_windows, revocation, master first, native resize without move + native move without resize, final readback). Not exposed as a fake Auto mode UI, no guessed Auto 1s tiler, input sync or game actions. Original source ordering not asserted.
- NEW tests/test_s61.py (12 cases), tools/S61_WINDOWS_C07_RESET_NATIVE_SMOKE.py (test-owned Tk HWND and native SetWindowPos), .github/workflows/s61-native-c07-reset.yml, docs/tasks/S61.md; STATE.md and PROJECT_STATUS.md append-only. S60 and S59 source/controls untouched. S61 CI PENDING.

## NEXT_ACTION on CONTINUE — S61 WINDOWS VERIFY THEN S62
- Inspect S61 genuine native Windows test-owned HWND run and full 894 S01–S61 unit regressions, S60–S10 native chain and S36 diagnostic build; record exact CI run/artifact, fix only observed faults. Do NOT mark complete on mocks alone. Once verified continue another C07 original-backed safe prerequisite: worker coordination and source-grounded activation sequencing, but NO Auto radio without full sync/input/lifecycle and no invented tiler geometry. No Proxy, fake Info/launch or completed product claim.


## S61 VERIFIED — ORIGINAL C07 EXACT AUTO RESET / 894 NATIVE WINDOWS TESTS PASS
- Followed live S60 checkpoint NEXT_ACTION; read original C07/C06 static evidence and frozen original executable. Implemented only independent C07 transition **(0,0), 1366×768 final geometry** via NEW src/window_auto_reset.py, no visible Auto/sync radio or mock 1s tiling, no input sync/game/Proxy.
- Initial code commit **a884fd7488efa620c2e2b13ae6037562219dc33f**; first S61 Windows test CI **38018137568** reached 894 tests but one incorrect assertion expected RESIZE_UNVERIFIED instead of safety-correct RESIZE_UNVERIFIED_PARTIAL. Fixed test-only assertion and native report upload in **b2098b8d0af8f27708dfcb12cd906dc47d11d887**; Stage S source regression **38018249434 COMPLETED SUCCESS**, S36 diagnostic **38018249488 COMPLETED SUCCESS**.
- Native real-Win32 S61 attempts **38018249457** and **38018342441** exposed original target width clamping on hosted Windows TEST-OWNED Tk HWND: despite SetWindowPos(request width 1366), GetWindowRect returned width **1044**. Product code correctly returned RESIZE_UNVERIFIED_PARTIAL, never a false success; added read-only diagnostics **7cc1699abf39ed0203584e33a88b3fea72346cd0**. Fixed ONLY test-owned Tk fixture max-track size using maxsize(2000,1400) in commit **cbb8c8c7c89a006c895efbad6abb73726916a581**; native engine NEVER changed for this host workaround.
- **ACTUAL [S61 Windows native run 38018421702](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38018421702), job 114113816993 COMPLETED SUCCESS:** Windows compileall; **894/894 S01–S61 Python units PASS** (10.628s), `PASS_NATIVE_S61_C07_TEST_OWNED_RESIZE_RESET` and `S61_NATIVE_RESET_RESULT_CODE="AUTO_RESET_APPLIED"`; truly SetWindowPos/GetWindowRect on two current Python/Tk HWNDs reaches (0,0,1366,768), preservation of HWND/PID, permission and repeat-idempotence. All prior S60/S59–S10 native Windows regression steps PASS, original S59 measured pixel-verified buttons untouched. Artifact **11656679107** (test-only).
- **ACTUAL [S36 Windows packaged diagnostic run 38018249488](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38018249488), job 114113279327 COMPLETED SUCCESS**: 894/894 tests PASS, `PASS_NATIVE_S36_PACKAGED_DIAGNOSTIC_FAIL_CLOSED_NOT_PRODUCT`; both normal and unverified CLI `EXPLICITLY_BLOCKED_NO_GUI`. Artifact **11656678862** strictly DIAGNOSTIC and NOT complete TLM EXE. The later native-test fixture commits did not change production source or S36 runtime.
- **STATUS S61_NATIVE_WINDOWS_894_UNIT_PASS_C07_RESET_TEST_ONLY**. Exact original Auto mode sequencing, synchronized input, true 1-second tiler layout arithmetic, signed Info/real F05 F06 live game launch/login, entire UI/game runtime parity still UNKNOWN/MISSING. Never claim live-game test or product EXE. No Proxy work, account writes, forged license or guessing restored C12 show branch.

## S61 FINAL CHANGED FILES
- src/window_auto_reset.py NEW — C07 real native exact original final geometry engine with independently verified HWND/PID and revocable max_windows; NOT wired to partial mode UI
- tests/test_s61.py NEW 12 tests (minor correction to fail-closed partial assertion)
- tools/S61_WINDOWS_C07_RESET_NATIVE_SMOKE.py NEW — real test-owned Tk native smoke, diagnostic logs and fixture max-track size
- .github/workflows/s61-native-c07-reset.yml NEW (894 units + native chain, report upload)
- docs/tasks/S61.md NEW
- STATE.md and PROJECT_STATUS.md append-only. S59/S60 source, PLAN.md, original archive untouched.

## NEXT_ACTION on CONTINUE — S62 (1:1 PARITY PRIORITY)
1. Read LIVE PLAN.md / STATE.md and check docs/tasks/S62.md; do not redo S59–S61.
2. Audit original C07 mode/auto-tile serialized evidence, existing S61 exact reset and S59 C10/C11 mover threads, plus C18/Start sync thread interaction. Prioritize a **source-backed, independently reproducible** C07 lifecycle/worker primitive that does NOT pretend unknown full 1s tiler geometry or input-sync/Train/Daily boundary. Preserve source-backed Auto reset dimensions/timer distinction; no fake mode radio.
3. If sufficient original proof exists, implement one safe original C07 subcomponent with real native Windows test-owned HWND and actual retry/cancel/identity proof; otherwise move to another unimplemented verifiable PLAN task rather than invent TLM behavior. Do not alter already verified S59/S60/S61.
4. Preserve **894/894** full Windows Python tests and S61/S60–S10 native chain, S36 fail-closed diagnostic. Explicit C12 show restore conflict remains UNKNOWN. No Proxy, fake license, guessed F02/F09 writes, unauthorized game input/memory injection or false product EXE. Checkpoint exact source, CI IDs, blockers and NEXT_ACTION.


## S62 VERIFIED — START C07 INTERNAL ASYNC RESET, 906 REAL WINDOWS TESTS PASS
- Continued LIVE PLAN.md and STATE.md S61 NEXT_ACTION; verified docs/tasks/S62.md initially absent. Scoped source commit **0065bf6b0904068822de6820e2558cf3b337826e** extends src/start_tab.py only: genuine S61 C07AutoReset called by INTERNAL non-Tk worker with S09 HWND/PID cache, current master and externally verified max_windows. No fake mode radio, no fake 1-second tiler/placement, no Proxy, no authorization bypass.
- Original S59 two pixel-verified C10/C11 buttons and original C07 S61 engine unchanged; grid C18 and stack C10/C11 reject competing live C07 reset; C07 refuses alive cancelled grid/stack workers; revoke/master-change/tab unmap/shutdown cancels native C07 with no Tk join and drops stale result.
- NEW tests/test_s62.py **12 unit cases** commit **403667246d74f3f2d8b9642163463fd6bc6eba4e**; new real-Tk native test-owned smoke tools/S62_WINDOWS_C07_START_NATIVE_SMOKE.py commit **a4e972a9057a4a0304a359f5564cef0d1a7d8411**; .github/workflows/s62-native-c07-start-lifecycle.yml commit **f0296fccb34da876ea633fe7f22074696297c974**; docs/tasks/S62.md and STATE/PROJECT_STATUS append-only. PLAN, original TLM archive, S59/S60/S61 source unchanged.
- **ACTUAL [S62 Windows native run 38020541964](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38020541964), job 114120355241 COMPLETED SUCCESS**: Windows compileall; **906/906** S01–S62 Python units PASS; `PASS_NATIVE_S62_C07_START_WORKER_TEST_OWNED`; `AUTO_RESET_APPLIED` via actual Win32 GetWindowRect/SetWindowPos with test-owned Tk HWNDs, (0,0) 1366x768 master first; concurrent C10/C11/C18 blocked; revocation cancels before more native movement and drops late state. Entire S61–S10 native Windows smoke regression chain PASS. Artifact **11658470397**, TEST-ONLY, no real game process.
- **ACTUAL [S36 packaged diagnostic run 38020486859](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38020486859), job 114120191026 COMPLETED SUCCESS**: **906/906 units PASS**, `PASS_NATIVE_S36_PACKAGED_DIAGNOSTIC_FAIL_CLOSED_NOT_PRODUCT`; both normal/unverified CLI `EXPLICITLY_BLOCKED_NO_GUI`; artifact **11658031809**, strictly diagnostic and NOT complete TLM tool.
- Other successful source-commit runs include [Stage S source regression 38020486833](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38020486833) and all 18 Windows workflows on source commit 0065bf6b including S10/S11/S12/S13/S14/S15/S16/S17/S18/S24/S36/S56/S57/S58/S59/S60/S61. No code/test regression failure observed for S62.
- **STATUS S62_NATIVE_WINDOWS_906_UNIT_PASS_INTERNAL_C07_RESET_WORKER_ONLY**. Original full C07 Auto/sync mode switch, original 1-second tile geometry, input sync, Train/Daily stopping and genuine E03 signed Info/F05/F06 actions still missing or UNKNOWN. C12 original show restore branch unresolved. No complete product EXE or verified real-game parity.

## S62 FINAL CHANGED FILES
- src/start_tab.py — ONLY changed existing functional source file.
- tests/test_s62.py NEW — 12 tests.
- tools/S62_WINDOWS_C07_START_NATIVE_SMOKE.py NEW.
- .github/workflows/s62-native-c07-start-lifecycle.yml NEW.
- docs/tasks/S62.md NEW; STATE.md, PROJECT_STATUS.md append-only.

## NEXT_ACTION on CONTINUE — S63 (PARITY / C07 REAL TILER PREREQUISITES)
1. Read LIVE PLAN.md and STATE.md; check docs/tasks/S63.md before writing; no reimplementation of S59–S62.
2. Inspect original compiled C07 Auto tiler RoleName character-info ordering, master-first ordering, current S09 HWND/PID cache / true character name availability and S62 worker lifecycle, and original 1-second timer. Decide whether an independently verifiable, genuinely useful prerequisite (e.g. verified HWND/PID + RoleName ordering or timer cancellation) can be safely implemented without guessed name fallback, original x/y/w/h tile arithmetic, fake Input sync or UI-only mode radio. If not, use another authentic PLAN feature with evidence, do not fabricate original behavior.
3. Keep no overlapping native movers, no license invention, no Proxy, no unproved F02/F09 writes, no original C12 show guess, no false product or live game parity. Preserve **906/906** actual Windows Python tests, S62–S10 native regression and S36 diagnostic FAIL-CLOSED NOT PRODUCT. Checkpoint full CI and NEXT_ACTION on GitHub.


## S63 VERIFIED — ORIGINAL C07 1000MS Tk AUTO TILE CLOCK (918 NATIVE WINDOWS TESTS PASS)
- Continued LIVE PLAN.md and STATE.md S62 NEXT_ACTION. Original C07 compiled static evidence identifies `_auto_tile_loop`, `_auto_tile_id`, `auto_tile_active`, and **one-second repeated loop ONLY while auto_tile_active=True**; separate 1.5s interval is input-sync keepalive. Exact original first tick/tiler x/y/w/h, RoleName collation, mode transition triggers still UNKNOWN and NOT fabricated.
- NEW `src/auto_tile_clock.py` source commit **15e0d03450d4333f999889a4ec78476ed4021928**: standalone genuine Tk.after(1000) revocable C07 clock requiring supplied callable action AND externally controlled gate, one timer per epoch; stop, revoke and shutdown cancel safely and stale callbacks cannot act; fail-closed on action error is LOCAL policy (not a claim of original exact error code). Not wired into UI/tiler movement until genuine source-backed geometry/input-sync exists.
- NEW `tests/test_s63.py` (12 tests) commit **0f17d2a68ed458936173a93401b90d2f32874bba**; NEW `tools/S63_WINDOWS_C07_CLOCK_SMOKE.py` real native Tk timer commit **e9cd3e2612c17c3658fc7747a30a88a66045808d**; NEW `.github/workflows/s63-native-c07-clock.yml` commit **fdd84355e0048bb6d966e5a5777da26e5a7e5b6e**; NEW `docs/tasks/S63.md`; STATE.md/PROJECT_STATUS.md append-only. Existing S59 original two-button pixel fidelity, S60 hide, S61 reset, S62 Start native worker left unchanged. PLAN/archive untouched.
- **ACTUAL [S63 Windows native run 38020833928](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38020833928), job 114121247578 COMPLETED SUCCESS:** Windows compileall + **918/918 S01–S63 Python unit tests PASS**; `PASS_NATIVE_S63_REAL_TK_1000MS_REVOKED_NO_GAME`. Actual Windows Tk callback first due after **1.016s**, next spacing **1.000s**; revocation stops before third tick, shutdown permanently blocks restart. ALL native regression steps S62–S10 PASS (including S62 C07 native Start movement on TEST-owned Windows). Artifact **11657802429**, test-only.
- **ACTUAL [S36 packaged diagnostic run 38020795102](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38020795102), job 114121134801 COMPLETED SUCCESS:** **918/918 Python unit tests PASS**, `PASS_NATIVE_S36_PACKAGED_DIAGNOSTIC_FAIL_CLOSED_NOT_PRODUCT`; both normal/unverified CLI `EXPLICITLY_BLOCKED_NO_GUI`. Artifact **11658820717**, DIAGNOSTIC EXE ONLY, NOT PRODUCT.
- Source regression run **38020795101** COMPLETED SUCCESS. No product UI mode radio, no guessed game positioning/credential/login actions/Proxy, no real game session touched. C12 actual show restore remains ambiguous; genuine E03 signed Info, F05/F06 original launch/login and full original runtime/UI equivalence still unavailable.
- **STATUS S63_NATIVE_WINDOWS_918_UNIT_PASS_C07_ONE_SECOND_CLOCK_NOT_TILER**.

## S63 FINAL CHANGED FILES
- src/auto_tile_clock.py NEW
- tests/test_s63.py NEW (12 tests)
- tools/S63_WINDOWS_C07_CLOCK_SMOKE.py NEW
- .github/workflows/s63-native-c07-clock.yml NEW
- docs/tasks/S63.md NEW
- STATE.md and PROJECT_STATUS.md append-only. No existing functional source changed in S63.

## NEXT_ACTION on CONTINUE — S64 (C07 ROLE NAME AUTHENTIC ORDER / MASTER PROVENANCE)
1. Read LIVE PLAN.md / STATE.md and check docs/tasks/S64.md. Do not redo verified S59–S63.
2. Inspect authentic original C02/C05/C07 `RoleName` from HWND→PID→reader character-info cache, C07 `_sort_key` compiled evidence and master-first rule. Audit current S09 snapshots and whether real `RoleName` is actually available. Build a useful SAFE name/identity ordering prerequisite only if source-backed semantics can be verified; don't invent name fallback, case folding, Unicode collation or tile x/y/w/h. If essential evidence absent, explicitly document blocker and pick another proven PLAN subtask.
3. Preserve **918/918** Windows unit tests, S63–S10 real Windows native regressions, S36 diagnostic fail-closed NOT PRODUCT, original measured Start buttons. No Proxy, guessed F02/F09 settings, forged signed Info, game injection or unsupported Auto mode UI; do not claim complete product.
4. Append exact files, CI IDs/blockers and concrete NEXT_ACTION for next chat cycle.


## S64 VERIFIED — C07 ROLE NAME HWND/PID PROVENANCE GATE / 930 WINDOWS TESTS PASS
- Continued directly from LIVE PLAN.md and STATE.md S63 NEXT_ACTION, confirmed docs/tasks/S64.md was absent. Original C02/C05/C07 explicitly tie RoleName to shared PID-keyed character Reader, HWND/PID identity and master-first Auto tiler. Current `src/start_windows.py` and `src/start_polling.py` genuinely do NOT read RoleName; original C07 `_sort_key` expression and exact case/diacritic order are UNKNOWN. Absolutely no title-to-RoleName inference, synthetic game identity, fake sorter or completed Auto tiler.
- **SOURCE COMMIT 8e282ec3ff37386f4bd74164bb7c7d62b950e0e1** changed NO previous functional module. NEW `src/auto_role_provenance.py` read-only `C07RolePreflight` accepts externally supplied worker character-info reader with exact matching HWND/PID/RoleName, checks live process/class/title/current HWND/PID before and after read, requires verified max_windows and explicit master. Without real role source returns ROLE_READER_UNAVAILABLE. Under two windows, verified master-first order is unambiguous; three windows with two followers returns ORIGINAL_SORT_KEY_UNKNOWN + no ordered HWND list until actual original comparator recovered. Test-supplied RoleReading IS NOT authentication of actual game-memory RoleName.
- NEW `tests/test_s64.py` 12 cases, `tools/S64_WINDOWS_ROLE_PROVENANCE_SMOKE.py` real Win32/Tk on THREE test-owned Python HWND with test-only character strings (NO game process), `.github/workflows/s64-native-role-provenance.yml`, `docs/tasks/S64.md`. PLAN, source S59–S63, and locked original ZIP untouched. No Proxy, memory injection, credential or licensing writes.
- **ACTUAL [S64 native Windows run 38021841374](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38021841374), job 114124320325 COMPLETED SUCCESS:** compileall and **930/930 S01–S64 Python unit tests PASS** (10.284s), **PASS_NATIVE_S64_ROLE_PROVENANCE_TEST_ONLY**. All 3 real owned HWND/PID verified, 2-window master first proven, 3-window original sort not guessed, missing reader and stale name/PID refused, windows physically unchanged. ALL S63–S10 native smoke regression steps PASS. Artifact **11658193510** (TEST-OWNED, not real game).
- **ACTUAL [S36 Windows packaged diagnostic run 38021841337](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38021841337), job 114124320270 COMPLETED SUCCESS:** 930/930 tests, `PASS_NATIVE_S36_PACKAGED_DIAGNOSTIC_FAIL_CLOSED_NOT_PRODUCT`; normal and unverified CLI EXPLICITLY_BLOCKED_NO_GUI. Artifact **11658947347**, DIAGNOSTIC ONLY NOT PRODUCT. Source regression **38021841387 COMPLETED SUCCESS**.
- **STATUS S64_NATIVE_WINDOWS_930_UNIT_PASS_C07_READ_ONLY_ROLE_IDENTITY_ONLY**. Current production reader cannot populate RoleName, so original automated sorting and game runtime/UI parity remain unimplemented. C12 show/restore and signed Info/F05/F06 are still UNKNOWN/unimplemented.

## S64 FILES
- NEW src/auto_role_provenance.py; tests/test_s64.py; tools/S64_WINDOWS_ROLE_PROVENANCE_SMOKE.py; .github/workflows/s64-native-role-provenance.yml; docs/tasks/S64.md
- UPDATED checkpoint only STATE.md; PROJECT_STATUS.md. No other source files changed.

## NEXT_ACTION on CONTINUE — S65 (AUTHENTIC READER / SORT RECOVERY OR ANOTHER PROVEN PLAN FEATURE)
1. Read LIVE PLAN.md/STATE.md; check docs/tasks/S65.md and source code before changing anything. Do not rebuild S59–S64.
2. Investigate original role Reader evidence from C02 plus preserved original TLM archive and available game client DATA-2222; specifically determine whether trustworthy REAL RoleName reading and C07 _sort_key can be reproduced and safely gated to HWND/PID without guessing addresses, offsets, collation, or bypassing game restrictions. If no sufficient evidence, DOCUMENT BLOCKER, do not manufacture a fake RoleName, fake sort or nonfunctional UI. Pivot to next original-backed useful PLAN component.
3. Preserve 930/930 unit Windows regressions, S64–S10 Win32 native test-only smoke, S36 fail-closed diagnostic. No Proxy, guessed F02/F09 account writes, forged Info, original C12 show guess or full product claim. Update STATE with exact source/files/tests/CI/next action.


## S65 RESEARCH COMPLETE — AUTHENTIC LOCAL RoleName READER / C07 SORT STILL BLOCKED
- Reread S64 live checkpoint and C02/C05/C07 evidence, investigated second source repo `ngmthang-g/clinent-game-than-long-DATA-2222`. Client API catalog has local `Game.RoleData` semantic state and `Name` snapshot field; `C_TeamData.TeamMember[].RoleName` and peaceful nearby player `Name` are DIFFERENT character sources and cannot substitute for local account RoleName by HWND/PID. Original TLM Reader pointer offsets/reconnect handling and C07 exact `_sort_key` STILL absent.
- `GameAssembly.dll` and `global-metadata.dat` in GitHub Contents are 133-byte LFS pointers to large original binaries, not decoded live process offsets; code search no indexed results for TLM Reader/read_all/RoleName. Details in docs/tasks/S65.md. Do NOT guess external game memory addresses, use team names as local role, casefold/locale sort or fabricate TLM parity.
- **NO existing functional source changed, NO new tests claimed for S65**. S64 verified **930/930** Python Windows units, native test-owned HWND regressions and S36 diagnostic remain last real CI evidence. S65 status RESEARCH_COMPLETE_IMPLEMENTATION_BLOCKED. This avoids false parity and does not redo S64.
- ADDED docs/tasks/S65.md; STATE.md and PROJECT_STATUS.md append-only. Original archive, PLAN and existing UI untouched.

## NEXT_ACTION on CONTINUE — S66 (REAL C06 HORIZONTAL/VERTICAL WINDOW STACK)
1. Read LIVE PLAN.md/STATE.md and inspect `docs/tasks/C06.md` and current `src/window_stacking.py`, tests and native S55 regression. Do NOT redo S59–S65.
2. Original `_stack_horizontal_cmd` / `_stack_vertical_cmd` docs state master-first move-only: horizontal (50*index,0), vertical (0,50*index), preserve size. Verify evidence; extend existing C10/C11 underlying engine with those modes, WIN32 identity/PID/permission/mover fencing and failure semantics. NO unverified UI buttons, and no fake tiling.
3. Add targeted unit and true Windows TEST-OWNED HWND tests, preserve 930 existing unit tests, S64–S10 native regressions, S36 packaged diagnostic fail-closed NOT PRODUCT. Update actual CI results and NEXT_ACTION after task. No Proxy, source drift or game actions not covered by PLAN.


## S66 VERIFIED — ORIGINAL C06 HORIZONTAL/VERTICAL 50PX MOVE-ONLY, 942 REAL WINDOWS TESTS PASS
- Continued from S65 NEXT_ACTION (true Reader / comparator blocked, no guessed game memory). LIVE PLAN and S55 C06 engine read. Source original `docs/tasks/C06.md` documents exact `_stack_horizontal_cmd`: Xếp ngang (50*i,0) and `_stack_vertical_cmd`: Xếp dọc (0,50*i), shared `_move_windows_offset` master-first, preserve original HWND size.
- SCOPED existing-source commit **c73e2aecab7145615fb25087014d17738de36c46** modifies ONLY `src/window_stacking.py`: existing C10/C11 native shared engine gains two original-backed **internal** modes horizontal/vertical, with original 50px position formulas and explicit result codes. Reuses existing live HWND/PID/permission/revocation preflight; unchanged original C10/C11 Xếp gọn/Xếp chéo logic. Absolutely no new unverified UI controls, original B14 screenshot change, fake TLM Auto grid or Proxy code.
- NEW `tests/test_s66.py` **12 tests** commit **9f27bfe33d10136fe320f88c404d5b7ab8f35559**; NEW `tools/S66_WINDOWS_C06_HV_STACK_SMOKE.py` (real native Win32 test-owned THREE Tk HWNDs) commit **a5b248f3f0d4ddd26776728278de5b7038be1eb5**; NEW `.github/workflows/s66-native-c06-hv-stacks.yml` commit **9d6dcebf695dbb180db524f399712b407d5b8658**, NEW `docs/tasks/S66.md`. STATE/PROJECT_STATUS append-only. Original ZIP, PLAN and prior S59/S64 source untouched except precisely scoped shared stacking engine.
- **ACTUAL [S66 Windows native CI 38022225272](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38022225272), job 114125478876 COMPLETED SUCCESS:** `python -m unittest discover` **942/942 S01–S66 tests PASS** (10.626s), `PASS_NATIVE_S66_C06_HV_STACK_TEST_OWNED`: 3 real test-owned HWNDs horizontal +50 X, vertical +50 Y with selected master index 0, real native sizes preserved, no extra movement on identical repeat, verified-limit gate, current HWND/PID unchanged. Entire S64–S10 native Win32 regression PASS, including S59 pixel-measured real buttons and S55 original C10/C11 behavior. Artifact **11658313767** (TEST ONLY, no game).
- **ACTUAL [S36 Windows diagnostic EXE CI 38022186641](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38022186641), job 114125360482 COMPLETED SUCCESS:** **942/942** Python tests, `PASS_NATIVE_S36_PACKAGED_DIAGNOSTIC_FAIL_CLOSED_NOT_PRODUCT`, normal and unverified CLI both `EXPLICITLY_BLOCKED_NO_GUI`. Artifact **11657879112** DIAGNOSTIC ONLY NOT PRODUCT. S55 prior Windows run 38022162058 and S59 38022161993 were successful after source patch; Stage S source 38022186630 success.
- STATUS **S66_NATIVE_WINDOWS_942_UNIT_PASS_C06_HV_OFFSET_INTERNAL_ONLY**. Original user-facing buttons for horizontal/vertical not located/measured in B14, no new UI added. Original full Auto tiler/RoleName Reader, original C12 show semantics, signed Info/server and game launch/login parity remain UNVERIFIED/MISSING. No real game HWNDs in smoke, no completed EXE product claimed.

## S66 FINAL CHANGED FILES
- src/window_stacking.py — scoped horizontal/vertical original positions, preexisting C10/C11 retained.
- tests/test_s66.py NEW (12).
- tools/S66_WINDOWS_C06_HV_STACK_SMOKE.py NEW.
- .github/workflows/s66-native-c06-hv-stacks.yml NEW.
- docs/tasks/S66.md NEW.
- STATE.md / PROJECT_STATUS.md checkpoint only.

## NEXT_ACTION on CONTINUE — S67 (C06 SETWINDOWPOS POST-MOVE TRUTH / NO FALSE SUCCESS)
1. Read LIVE PLAN.md/STATE.md, inspect S66 native evidence, existing `src/window_stacking.py` and S60 `src/window_hide.py` verified post-move truth safety. Do not redo S59–S66.
2. Independently reproduce whether shared C10/C11/horizontal/vertical movement currently treats `move_no_resize=True` as success even if HWND actual Win32 rectangle did not move. If yes, add a **small** non-invasive check for actual `GetWindowRect`, HWND/PID and original dimensions after each move for all four modes; fail-closed on mismatch with explicit result; never report applied when final window ignored SetWindowPos. Preserve original 50px and C10/C11 formulas, master first, no GUI change.
3. Add targeted unit + real Windows TEST-OWNED HWND regressions (including a lying native backend and successful real resize-free moves), run full **942 existing unit tests**, S66–S10 native regression and S36 packaged fail-closed diagnostic. Checkpoint exact CI IDs, file list, blocker and NEXT_ACTION.
4. Do not guess original C07 Auto tile/RoleName, C12 show restore or fake Info/login, no Proxy. Production EXE remains NOT COMPLETE.


## S67 VERIFIED — C06 NATIVE POST-MOVE TRUTH, 954 FULL WINDOWS TESTS PASS
- Continued from LIVE PLAN.md/STATE.md S66 verified NEXT_ACTION; `docs/tasks/S67.md` initially absent. Independent code inspection confirmed genuine defect: `src/window_stacking.py` previously trusted `move_no_resize=True` for success and could incorrectly publish STACK_*_APPLIED if Win32 ignored a move, changed dimensions or HWND/PID was replaced after return.
- **SCOPED SOURCE COMMIT 623b9be13bd1804a89a6b4780286582ee1381138**: existing `src/window_stacking.py` ONLY adds non-invasive verification after moved OR unchanged Windows, checking live `is_window`, PID snapshot and actual `window_rect` origin/width/height. Fail-closed `STALE_AFTER_MOVE_PARTIAL` / `MOVE_UNVERIFIED_PARTIAL`; **ALL FOUR original C06 geometries unchanged**: tight origin, diagonal +50/+50, horizontal +50 X, vertical +50 Y, master first. Legacy cancellation return remains CANCELLED. This is local safety, not a recovered byte-for-byte original Win32 branch.
- NEW `tests/test_s67.py` 12 regression cases commit **382744370ceaa95a1de093788e63ec8478c38488** (no-op liar, last HWND fake success, illegal resize, PID reuse after native success, already-target rect drift, real 4 modes, master order, legacy cancellation/idempotence). NEW actual Win32 `tools/S67_WINDOWS_C06_POSTMOVE_SMOKE.py` commits **4f9b3a872e22851761e5b60899d961cb01e13fb0** and TEST-ONLY PID follower fixture correction **5cfbd96c61a6e2798c2c45276f1a9f691729f3fa**. NEW `.github/workflows/s67-native-c06-postmove.yml` commit **754bf46e52e93e8c8ec636e76896e070f12e81bd**, NEW `docs/tasks/S67.md`, STATE+PROJECT_STATUS append-only. No S59 UI pixel changes, no alteration to S60 hide / S61 Auto reset / original archive or PLAN.
- **ACTUAL [S67 Windows native run 38023429480](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38023429480), job 114129115991 COMPLETED SUCCESS**: Windows compileall and **954/954 S01–S67 Python units PASS** (10.450 seconds), `PASS_NATIVE_S67_C06_POSTMOVE_REAL_RECT_AND_PID` on 3 actual TEST-OWNED Python/Tk Win32 HWNDs: four real C06 native modes succeed with correct geometry, lying SetWindowPos return on last HWND rejected, stale PID immediately after move rejected, original sizes/identity preserved; all prior S66–S10 Windows native regression steps PASS including original S59 buttons. Artifact **11659760503** TEST-ONLY no actual game process.
- **ACTUAL [S36 packaged diagnostic run 38023366020](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38023366020), job 114128933669 COMPLETED SUCCESS**: **954/954** Python tests, `PASS_NATIVE_S36_PACKAGED_DIAGNOSTIC_FAIL_CLOSED_NOT_PRODUCT`, both normal/unverified CLI `EXPLICITLY_BLOCKED_NO_GUI`. Artifact **11659965218**, DIAGNOSTIC EXE ONLY NOT PRODUCT. Source regression **38023365964 COMPLETED SUCCESS**. No real-game HWND test, signed Info/real F05 F06, RoleName reader, full Auto tiler or production EXE claim.
- **STATUS S67_NATIVE_WINDOWS_954_UNIT_PASS_C06_POSTMOVE_NO_FALSE_SUCCESS**. Confirmed defect fixed, prior correct original C10/C11/HV behavior not redone.

## S67 FINAL FILES
- CHANGED existing: src/window_stacking.py only (post-move truthful readback).
- NEW: tests/test_s67.py (12); tools/S67_WINDOWS_C06_POSTMOVE_SMOKE.py; .github/workflows/s67-native-c06-postmove.yml; docs/tasks/S67.md.
- STATE.md, PROJECT_STATUS.md append-only checkpoint. Original TLM binary, screenshot and PLAN untouched.

## NEXT_ACTION on CONTINUE — S68 (GROW USER-VISIBLE ORIGINAL FEATURE COVERAGE)
1. Read LIVE PLAN.md, STATE.md and `docs/tasks/S68.md` (if present) and inspect `docs/tasks/C14.md`/`C13.md`, existing DWM preview lifecycle `src/dwm_preview.py` / Start tab, and original detached overlay geometry. Do NOT redo verified S59–S67.
2. Prioritize independently provable C14 **detached preview native host/region**: exact original origin x=0,y=768, width screen_width - 450 and height remaining to bottom; DWM destinations are separate from embedded preview. Evaluate whether existing S11/S12/S15 DWM manager can be safely reused to build a real independently owned detached preview lifecycle on TEST-OWNED Windows HWNDs with no fake UI. If full geometry/lifetime and source identity can be verified, add a narrow native prototype, else document blockers rather than putting a fake "Tách rời" button.
3. Preserve 954/954 full Windows tests, S67–S10 native and S36 diagnostic FAIL-CLOSED NOT PRODUCT. No invented hidden/embedded visibility after Hủy tách/Đóng xem, no unsigned entitlement bypass, no Proxy, no guessed game RoleName, no completed EXE claims. Update exact CI/files/blockers/NEXT_ACTION.


## S68 VERIFIED — C14 REAL SEPARATE DETACHED DWM REGION/SESSION, 966 WINDOWS TESTS PASS
- Continued exactly LIVE PLAN.md/STATE.md S67 NEXT_ACTION; docs/tasks/S68.md absent. Original C14 from docs/tasks/C14.md and docs/window/C14_DETACHED_PREVIEW_MODEL.json: detached overlay x=0 y=768, width screen_width-450, height screen_height-768, independent DWM destination thumbnails; exact detached tile spacing, Hủy tách/Đóng xem embedded visibility and actual auto-open sequencing UNKNOWN.
- NEW `src/detached_preview.py` source commit **07116bed7af3a05002fa0fb56010cd2761e50596**. `verified_detached_region` exactly derived from original C14 values, refuses noninteger/physical insufficient desktop height. `C14DetachedDwmSession` independent ReadOnlyDwmPreviews; accepts EXISTING native top-level owner HWND/PID, requires physical owner rect EXACT region; verified Start snapshot and max_windows; checks current source HWND/PID and executable/class/title, placement within exact owner region; reuses genuine S11 DWM registration/update/unregister/destroy and tears detached slots down on revocation/stale source, WITHOUT touching embedded preview manager. Supplied tile placements intentionally external because original detached per-item geometry/spacing still NOT RECOVERED. No UI button, no proxy, no game input, no source memory, no role name guessing.
- NEW `tests/test_s68.py` **12 tests**, commit **fce349694c4da38e71213621448c30b8f478648e**; NEW `tools/S68_WINDOWS_DETACHED_DWM_SMOKE.py` 3 real Windows test-owned Python/Tk source HWNDs + native detached top-level owner + separate embedded DWM, commit **70018170f2aad3be8c1da67c9e663f5417eef6d1**. NEW `.github/workflows/s68-native-detached-dwm.yml` commit **349a50b495d3ec08a1bb0e7c988e657d2398692f**. NEW docs/tasks/S68.md, STATE and PROJECT_STATUS append-only. Existing S59–S67 functional source, locked screenshot, original ZIP and PLAN untouched.
- **ACTUAL [S68 native Windows run 38024091346](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38024091346), job 114131114657 COMPLETED SUCCESS:** **966/966 S01–S68 Python tests PASS** (10.505s) and `PASS_NATIVE_S68_C14_SEPARATE_DWM_HOST_TEST_ONLY`; actual user32/DwmRegisterThumbnail/Update/Unregister/Destroy on real test-owned HWNDs; exactly measured native test owner region (0,768) + configured expected size, 3 DWM thumbnail destinations, dead source cleanup and remaining source retention, detached shutdown leaves embedded thumbnail alive, ALL destination registrations balanced. S67–S10 native Windows regression entire chain PASS. Artifact **11659306433**, TEST OWNED NO GAME.
- CRITICAL ENVIRONMENT TRUTH: actual GitHub Windows desktop **1024×768**; original C14 full region would have height=0, therefore production `verified_detached_region(1024,768)` correctly refuses it. Native smoke used transparently labeled **test-only virtual screen dimensions 1600×1000** to construct a real offscreen Tk top-level owner at original (0,768) and test actual Win32/DWM; THIS DOES NOT PROVE real C14 usability at 1024×768 or at user monitor resolution, original detached tiling and full UI parity.
- **ACTUAL [S36 packaged diagnostic run 38024030373](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38024030373), job 114130933914 COMPLETED SUCCESS:** **966/966** Python tests; `PASS_NATIVE_S36_PACKAGED_DIAGNOSTIC_FAIL_CLOSED_NOT_PRODUCT`; normal and unverified CLI `EXPLICITLY_BLOCKED_NO_GUI`, artifact **11660011480**, strictly diagnostic NOT product. Source regression **38024030384 COMPLETED SUCCESS**.
- **STATUS S68_NATIVE_WINDOWS_966_TEST_PASS_C14_DETACHED_DWM_INTERNAL_ONLY**. NO `Tách rời` user-visible button was added, no original embedded preview mode branch guessed, no real game test or production EXE claim. Missing original C14 item x/y/layout, detached window animation/mode/auto-open, signed E03 Info, F05/F06 real game runtime and full 1:1 tool.

## S68 FINAL CHANGED FILES
- NEW src/detached_preview.py, tests/test_s68.py (12), tools/S68_WINDOWS_DETACHED_DWM_SMOKE.py, .github/workflows/s68-native-detached-dwm.yml, docs/tasks/S68.md.
- STATE.md / PROJECT_STATUS.md append-only; no existing functional source changed.

## NEXT_ACTION on CONTINUE — S69 (C14 USER-SAFE SETTINGS / NATIVE HOST LIFECYCLE)
1. Read LIVE PLAN.md/STATE.md, inspect docs/tasks/S69.md, original C14/ E05 persisted `detached_auto_open` (boolean default true) / `detached_grid` (default 3), current `src/settings_store.py`, Start preview UI and S68 DWM session. Do not redo S59–S68.
2. Identify a genuinely source-backed subcomponent for C14 auto-open setting or detached grid setting persistence that can be implemented without pretending the actual detached preview auto-open works yet; only add if original read/write key/defaults and return semantics are sufficiently supported. Alternatively improve genuine native detached owner lifetime + cleanup upon HWND reuse/shutdown without guessing original closing/embedded state. NEVER expose an inert `Tách rời` button, guess exact tile coordinates, or attempt full mode transition without proof.
3. Preserve **966/966** Windows Python tests, S68–S10 native DWM/Win32 regression, S36 diagnostic fail-closed NOT PRODUCT, exact measured original Start UI. Run new true Windows tests for source changes, checkpoint exact results/blockers/file changes/NEXT_ACTION.


## S69 VERIFIED — C14 EXACT DETACHED SETTINGS / 978 REAL WINDOWS TESTS PASS
- Continued LIVE PLAN.md/STATE.md S68 NEXT_ACTION, confirmed docs/tasks/S69.md initially absent. Reviewed original docs/window/C14_DETACHED_PREVIEW_STATIC_EVIDENCE.tsv and E05 settings: **[Settings].detached_auto_open getboolean fallback True**, **[Settings].detached_grid default-like string "3"**, Start main grid and preview columns are separately owned. Exact original C14 readonly combobox full choice list and true auto-open timing/hide embedded transitions remain UNKNOWN.
- NEW `src/detached_settings.py` commit **58e0bd6b7363a3412fb5d16c56754d7983b3e5d5**: `DetachedSettings(auto_open=True,grid="3")` and `DetachedSettingsStore` read/write through the existing E05 shared `settings_store.read_settings/write_settings`; edits only the two evidenced keys, preserves all unrelated [Settings] and feature sections, atomic os.replace and dated settings backups. Malformed fields independently fall back, rejects invalid writes before touching files. Positive canonical decimal string grid validation is explicitly S69 LOCAL safety and original C14 combobox list/max UNKNOWN. `auto_open=True` stored as DATA ONLY, never triggers Tk/DWM windows, login, game action, fake button or non-evidenced mode.
- NEW `tests/test_s69.py` **12 tests**, commit **956a823c1d96fd9d04107e157c8617de12c3836d**; NEW `tools/S69_WINDOWS_C14_SETTINGS_SMOKE.py` Windows isolated temporary %APPDATA% + native HWND count proof, commit **06fa732f140e3098db7da2206015e2d43ea5b409**; NEW `.github/workflows/s69-native-detached-settings.yml` commit **a956d6d0c43e466d0ba8d6a06830d3162c68882f**; NEW docs/tasks/S69.md. STATE/PROJECT_STATUS append-only. Existing Start/DWM/S59-S68 source, PLAN and locked original image/archive untouched.
- **ACTUAL [S69 Windows native run 38025535688](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38025535688), job 114135480266 COMPLETED SUCCESS:** Windows compileall, **978/978 S01-S69 Python tests PASS** (10.625s), `PASS_NATIVE_S69_C14_SETTINGS_ONLY_NO_FAKE_AUTOOPEN`: real %APPDATA% TEMP sandbox path, E05 actual settings.ini writes and backup, verified exact original defaults, independent saved grid_cols/grid_rows, invalid write no mutation, native test-owned HWND inventory proves saving True does **not** create unproved preview. Full S68 original C14 real DWM and S67–S10 native Windows regressions PASS. Artifact **11659809284**, test-only and NO game.
- **ACTUAL [S36 Windows packaged diagnostic run 38025496184](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38025496184), job 114135361323 COMPLETED SUCCESS:** **978/978** unit tests (10.421s), `PASS_NATIVE_S36_PACKAGED_DIAGNOSTIC_FAIL_CLOSED_NOT_PRODUCT`; both normal and unverified CLI `EXPLICITLY_BLOCKED_NO_GUI`. Artifact **11659063438** DIAGNOSTIC ONLY, NOT PRODUCT. Stage S source regression run **38025496176** COMPLETED SUCCESS.
- **STATUS S69_NATIVE_WINDOWS_978_UNIT_PASS_C14_SETTINGS_DATA_ONLY**. Exact original C14 full detached tile layout, topmost host factory, auto-open runtime/embedded preview close or Hủy tách transitions, real account RoleName Reader, original Auto tile algorithm, signed E03 Info, F05/F06 game launch/login and full production EXE remain MISSING/UNKNOWN. No Proxy.

## S69 FINAL CHANGED FILES
- NEW src/detached_settings.py, tests/test_s69.py (12), tools/S69_WINDOWS_C14_SETTINGS_SMOKE.py, .github/workflows/s69-native-detached-settings.yml, docs/tasks/S69.md.
- STATE.md and PROJECT_STATUS.md append-only checkpoint. No existing functional source modified.

## NEXT_ACTION on CONTINUE — S70 (C14 REAL DETACHED TOPMOST OWNER LIFECYCLE)
1. Read LIVE PLAN.md / STATE.md and check docs/tasks/S70.md. Do not redo S59–S69. Inspect original C14 native topmost region evidence, current src/detached_preview.py (S68 requires existing externally supplied owner HWND/PID), NativeDwmBackend owner semantics and S68 Windows native test.
2. If original-backed safety/lifecycle is reproducible, implement independently owned ACTUAL Win32/Tk topmost detached host at x=0,y=768,width=screen_width-450,height=screen_height-768 with strict real desktop constraints and deterministic teardown after DWM unregister. No auto-open by merely stored True, no guessed detached per-tile slots or invisible fake buttons, no alteration of embedded preview. Require selected-window authorization/identity and perform Tk operations on owner thread only. Otherwise document blocker and move to another grounded PLAN subtask.
3. Add focused unit and true Windows test-owned native DWM/Win32 host tests, preserve **978/978** existing full Windows units, all S69–S10 native regression, and S36 diagnostic FAIL-CLOSED NOT PRODUCT. GitHub hosted screen was ACTUALLY 1024x768 at S68, so real C14 region MUST fail closed there; don't silently lie using a test-only virtual desktop to claim actual screen feature usability. Append exact CI/artifacts/blockers/files/NEXT_ACTION.


## S70 VERIFIED — C14 NATIVE TOPMOST OWNER PLUS DWM LIFETIME, 990 REAL WINDOWS TESTS PASS
- Continued LIVE PLAN.md/STATE.md S69 NEXT_ACTION. NEW `src/detached_host.py` commit **36e29f79e4bc47b2b587a65f6e8638631d8ddf9f**: explicit, Tk-owner-thread-only `C14DetachedHost` around S68 `C14DetachedDwmSession`; checks S09 source cached/live HWND/PID/exe/class/title, allowed revocation and independently verified positive max_windows BEFORE creating; calculates exact C14 region x=0/y=768/w=screen-450/h=screen-768 and refuses 1024x768 actual short screen. Creates real Tk owner `-topmost`, resolves native root HWND, checks GetWindowRect, actual PID, visibility and WS_EX_TOPMOST; no original UI toggle, guessed tile layout or detached auto-open. Owns detached DWM and unregisters/destroys before Tk owner. `overrideredirect(True)` is a labeled local host choice, NOT proven original details. Old S59–S69 modules intact.
- NEW `tests/test_s70.py` **12 tests** commit **7a1e984c0d59e918cfddf8457a12299f73d4b1c7**; NEW true Win32 test `tools/S70_WINDOWS_DETACHED_TOPMOST_HOST_SMOKE.py` commit **568e40c1bf0b567421397414d5f4c267c16ab359**; NEW `.github/workflows/s70-native-detached-topmost-host.yml` commit **cc2105b2f6d90255165ea283de91630959b47f06**; NEW docs/tasks/S70.md. Initial CI Stage S **38026413417** and S36 **38026413423** FAILED due to single **TEST ASSERTION** falsely rejecting the literal `auto_open=True` in explanatory docstring, NOT runtime auto-open; corrected only test in **c1d2eee669d2547373981d21de095ff7e1fe3acd** to reject callable auto-open behavior, did NOT alter production source.
- **ACTUAL [S70 native Windows run 38026533288](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38026533288), job 114138445241 COMPLETED SUCCESS:** **990/990 S01–S70 unit tests PASS** (10.444s), `PASS_NATIVE_S70_C14_TOPMOST_OWNER_AND_DWM_CLEANUP_TEST_ONLY`: actual CI desktop **1024×768**, source-backed region genuinely rejected with no native owner; test-only Tk desktop-method fixture uses `>=1600×1000` for a real offscreen native Win32/Tk topmost HWND, verified WS_EX_TOPMOST/native rect/PID, 3 genuine native DWM register/update, every unregister/destroy before owner HWND destruction; all S69–S10 real Windows regressions PASS. Artifact **11660565963** TEST ONLY.
- **ACTUAL [S36 packaged diagnostic run 38026533326](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38026533326), job 114138445439 COMPLETED SUCCESS:** **990/990** unit tests, `PASS_NATIVE_S36_PACKAGED_DIAGNOSTIC_FAIL_CLOSED_NOT_PRODUCT`, normal/unverified CLI `EXPLICITLY_BLOCKED_NO_GUI`; artifact **11659049670** diagnostic only. Stage S source regression **38026533327 COMPLETED SUCCESS**.
- **STATUS S70_NATIVE_WINDOWS_990_UNIT_PASS_C14_TOPMOST_HOST_INTERNAL_ONLY**. No added user-visible Tách rời/Hủy tách/Đóng xem, no original per-tile geometry, no game HWNDs or authentic runtime. Signed Info, game launch, login, RoleName etc remain BLOCKED. Source and EXE not product complete.

## S70 FILES
- NEW src/detached_host.py, tests/test_s70.py (12), tools/S70_WINDOWS_DETACHED_TOPMOST_HOST_SMOKE.py, .github/workflows/s70-native-detached-topmost-host.yml, docs/tasks/S70.md.
- TEST-ONLY FIX tests/test_s70.py. Append STATE/PROJECT_STATUS. Original archive, PLAN, visible UI untouched.

## NEXT_ACTION on CONTINUE — S71 (DWM NATIVE TEARDOWN EXCEPTION SAFETY)
1. Read LIVE PLAN.md and STATE.md, inspect `docs/tasks/S71.md`, `src/dwm_preview.py` S11 `ReadOnlyDwmPreviews.clear/shutdown` and S70 `C14DetachedHost.close`. Do NOT redo S59–S70.
2. Independently confirm that a single native `DwmUnregisterThumbnail` failure raises during `clear`, leaving remaining DWM slots uncleaned, and that S70 host might not destroy itself if session shutdown raises. Fix **minimally** so all remaining unregister/destroy attempts are made and host resources ultimately released with explicit failure code; do not silently report full success or remove S11 HWND/PID safeguards. Prefer fail-closed, owner-thread only, and native-owned test HWND proof.
3. Add targeted unit + genuine Windows test-owned DWM error-injection with clean resources, run **990 existing Windows tests** + new tests and S70–S10 native chain; S36 packaged EXE stays diagnostic NOT PRODUCT. Update exact CI/files/blockers/NEXT_ACTION S72. No Proxy, guessed RoleName, fake C14 buttons or full 1:1/EXE claim.


## S71 VERIFIED — DWM MULTI-SLOT FAIL-CLOSED NATIVE TEARDOWN, 1002 WINDOWS TESTS PASS
- Continued **automatically after S70** within the same user `CONTINUE`, as explicitly requested, without user prompting. Read LIVE PLAN.md/STATE.md S70 NEXT_ACTION and audited S11 `src/dwm_preview.py` and S70 `src/detached_host.py`. Confirmed reconstruction defect: a single native unregister/destroy exception caused `ReadOnlyDwmPreviews.clear` to exit early, leaving further slots registered, while `C14DetachedHost.close` could abort and not destroy Tk host. Original Nuitka exact exception semantics still UNKNOWN; these are local safety fixes, not claimed original byte-level parity.
- EXISTING `src/dwm_preview.py` SMALL change commit **b504c21c6ebcfa7b4aa5889ab1834ec8ec146402**: `clear` now attempts EVERY DWM slot regardless of earlier unregister/destination errors and rethrows first exception only after completing all attempts; the `_remove` unregister-then-finally-destroy order and S11 HWND/PID guards retained.
- EXISTING `src/detached_host.py` SMALL change commit **9e182763cc5cb49901d55a8570b419a6347e54b9**: `close` always attempts DWM session.shutdown and native Tk owner destroy; explicitly returns `HOST_CLOSED_NATIVE_CLEANUP_FAILED` if either failed instead of silently certifying cleanup. `shutdown` closes permanently with `CLOSED_NATIVE_CLEANUP_FAILED` when relevant. Native failure cannot be asserted to have successfully released every possible external handle; result keeps uncertainty explicit.
- NEW `tests/test_s71.py` **12 tests** commit **8b3931e3aff4e5dfaf8da421221b3e3cedc7d9f9**; NEW actual Win32 `tools/S71_WINDOWS_DWM_TEARDOWN_ERROR_SMOKE.py` commit **a3e67e61452e974579bfbdf9a0eb5171ee159a08** and test-only expected PASS exit-code correction **e85ec3773c72210a38d4ae27cb0b7b8a6ff2fbd5**. NEW `.github/workflows/s71-native-dwm-teardown.yml` commit **e710f1102e2087b8e940d267d771555a75b7f0cf**, NEW docs/tasks/S71.md. The first native workflow **38026832152** marked failed ONLY because test printed all PASS results but compared a stale PASS constant in exit logic. Corrected smoke only; no production code change.
- **ACTUAL [S71 native Windows CI 38026905049](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38026905049), job 114139555607 COMPLETED SUCCESS:** **1002/1002** S01–S71 unit tests PASS (10.547s), `PASS_NATIVE_S71_DWM_FAILURE_ALL_OWNED_HWND_RELEASED` on three real test-owned Tk Windows HWNDs + actual DWM registers/unregisters. Test-only wrapper threw after first REAL DwmUnregisterThumbnail, explicit failure code true, subsequent native thumbnails and destinations cleaned, native owner destroyed after DWM, all S70–S10 Win32 regression PASS. Actual hosted desktop still 1024×768: real C14 region refuses it, positive native test uses openly labeled test-only virtual desktop dimensions. Artifact **11660661570** TEST-OWNED NO GAME.
- **ACTUAL [S36 packaged diagnostic CI 38026799155](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38026799155), job 114139246826 COMPLETED SUCCESS:** **1002/1002** unit tests (10.735s), `PASS_NATIVE_S36_PACKAGED_DIAGNOSTIC_FAIL_CLOSED_NOT_PRODUCT`; normal and unverified CLI `EXPLICITLY_BLOCKED_NO_GUI`; artifact **11659234875**, diagnostic only. Stage S source regression **38026799184 COMPLETED SUCCESS**.
- **STATUS S71_NATIVE_WINDOWS_1002_UNIT_PASS_DWM_CLEANUP_EXCEPTION_HONEST**. Real TLM original detached tile layout, exact Hủy tách/Đóng xem embedded visibility and auto-open timing, signed server Info, F05/F06 live game runtime and complete product EXE remain UNKNOWN/MISSING. No Proxy, fake clickable C14 UI or game process touched.

## S71 FINAL CHANGED FILES
- SCOPED existing source src/dwm_preview.py (all-slot teardown despite first exception), src/detached_host.py (native owner finally closes, explicit result).
- NEW tests/test_s71.py (12), tools/S71_WINDOWS_DWM_TEARDOWN_ERROR_SMOKE.py, .github/workflows/s71-native-dwm-teardown.yml, docs/tasks/S71.md.
- STATE.md, PROJECT_STATUS.md append-only checkpoint; no changes to S59 measured UI, original TLM ZIP, PLAN, S70 geometry, role reader or signed permission.

## NEXT_ACTION on CONTINUE — S72 (C14 DETACHED CHANGE OBSERVER WITHOUT GUESSED SCHEDULING)
1. Read LIVE PLAN.md/STATE.md and docs/tasks/S72.md, original C14 `_detached_update_loop` evidence and existing S09 immutable WindowSnapshot/S68-S71 services. Do not redo S59–S71.
2. Source-backed original C14 detached preview maintenance exists independently of Start tab visibility and rebuilds when the *actual game HWND list changes*. Develop a small read-only HWND/PID epoch-change observer, **only if** it can be made useful without guessing original per-tile layout/auto-open timer/cadence, saving a fake preferred monitor resolution or building an inert visible button. Ensure source PID reuse treated as change, stale renderer revocation and explicit permission loss; never derive game identity from window label. Avoid any hidden Tk timer interval not source-backed.
3. Add tests and genuine Windows test-owned HWND/lifetime regression if implemented; maintain **1002/1002** existing units, S71–S10 real native regression, S36 diagnostic FAIL-CLOSED NOT PRODUCT. Update checkpoint actual CI IDs and NEXT_ACTION S73, otherwise document authentic blockers and pivot to higher-value original-backed PLAN component.


## S72 VERIFIED — C14 DETACHED HWND/PID LIST OBSERVER, 1014 REAL WINDOWS TESTS PASS
- Resumed LIVE PLAN.md / STATE.md from S71 NEXT_ACTION (S72 document initially missing) without redoing any S59–S71 feature. User ZIP `TLMTool_2.1.2(20261010-054635).zip` verified exact Gate A SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`: 93,715,901 bytes, 1,002 files/48 directories, zip.testzip() no errors. No original binary run.
- Original C14 `_detached_update_loop` static doc shows detached observer updates upon game-list changes, independently of Start visibility. Exact C14 loop interval, sorted equality order, per-thumbnail tile coordinates and auto-open timing UNKNOWN; intentionally not invented.
- NEW `src/detached_list_observer.py` commit **0f7769a9389c2e645e66f2c89fd9800bd8358abe**: Tk-owner-thread pure snapshot observer; identity is HWND+PID; source is supplied independently of Start-only poller; no self-scheduled timer. Any list change or reused HWND/new PID invalidates previously rendered native DWM before accepting new identity. Same list/new revision or changed label only is UNCHANGED. Permission loss, malformed/duplicate window, stale/conflicting revision or unavailable max_windows cause fail-closed preview invalidation; explicit renderer native cleanup failure never produces success; reset/shutdown explicit.
- NEW `tests/test_s72.py` **12 unit cases** commit **e2bf7f78fee28144fc9421a4e56ee71080d85e0c**. NEW `tools/S72_WINDOWS_C14_DETACHED_LIST_OBSERVER_SMOKE.py` commit **6664c7764a9ee5713e780f6bab80037749f74342**: two actual Windows test-owned native Tk HWND sources and real PID validated via user32; native DWM registered on real windows, one destroyed, two registrations torn down before accepting changed list, permission revoked; GAME_PROCESS/class/title markers only test fixture NOT a game. NEW workflow `.github/workflows/s72-native-c14-list-observer.yml` commit **8116946562d398b677939ab0b1082676865c07b5**; NEW `docs/tasks/S72.md` and its verified CI update.
- **ACTUAL [S72 Windows native CI 38028985234](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38028985234), job 114145756143 COMPLETED SUCCESS**: Windows compileall, **1014/1014** S01–S72 Python tests PASS, `PASS_NATIVE_S72_C14_HWND_CHANGE_RELEASES_DWM_TEST_ONLY`; all S71–S10 genuine Win32/Tk/DWM regression chain PASS. Artifact **11661435702**, TEST-OWNED NO GAME.
- **ACTUAL [S36 packaged diagnostic CI 38028936113](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38028936113), job 114145610873 COMPLETED SUCCESS**: **1014/1014** Python unit tests; `PASS_NATIVE_S36_PACKAGED_DIAGNOSTIC_FAIL_CLOSED_NOT_PRODUCT`, normal and unverified CLI both `EXPLICITLY_BLOCKED_NO_GUI`. Artifact **11661352311**, strictly DIAGNOSTIC NOT PRODUCT. Stage S source regression **38028936107** COMPLETED SUCCESS.
- **STATUS S72_NATIVE_WINDOWS_1014_TEST_PASS_INTERNAL_C14_CHANGE_OBSERVER**. Observer is not connected to user-visible detached mode or a guessed background cadence; original C14 tiles, complete C07 Auto, signed E03 Info, actual F05/F06 login and full interactive TLM tool/EXE parity still MISSING/UNKNOWN. No Proxy work, original PLAN/ZIP or S59 measured UI changes.

## S72 FINAL CHANGED FILES
- NEW src/detached_list_observer.py, tests/test_s72.py, tools/S72_WINDOWS_C14_DETACHED_LIST_OBSERVER_SMOKE.py, .github/workflows/s72-native-c14-list-observer.yml, docs/tasks/S72.md.
- APPEND STATE.md / PROJECT_STATUS.md. Original source/data ZIP and PLAN.md untouched.

## NEXT_ACTION on CONTINUE — S73 (C14 INDEPENDENT LIFETIME EVIDENCE, NOT GUESSED TIMER)
1. Read LIVE PLAN.md/STATE.md and docs/tasks/S73.md; do not repeat S59–S72.
2. Inspect C14 independent detached update loop and Start S09 producer/poller lifetime. Research whether an actual independent authorized read-only HWND/PID producer lifecycle can be added without inventing the original detached timer interval, wiring inactive GUI buttons, replacing source-backed game window predicate or secretly running Start-only 2s/3s cadence behind Start.
3. If precise original-backed component exists, implement/test narrowly using real Windows test-owned HWNDs. If C14 cadence/transition still UNKNOWN, DOCUMENT BLOCKER and move to another verifiable PLAN scope rather than invent behavior. Preserve **1014/1014** existing Windows units, S72–S10 native chain and S36 diagnostic fail-closed NOT PRODUCT. Record actual CI IDs, files and next S74 action; NO Proxy, real-game parity claims, fake Input/UI or authorization bypass.


## S73 VERIFIED — C14 INDEPENDENT EXPLICIT ONE-SHOT SCAN, 1026 WINDOWS TESTS PASS
- Continued automatically from verified S72 `NEXT_ACTION` in the SAME user task. Re-reviewed original C14 compiled `_detached_update_loop` text in exact Gate A frozen ZIP. Confirmed source doc: detached loop rebuilds when actual game-list changes and is INDEPENDENT OF TAB START visibility. Source C14 exact scan period remains UNKNOWN. Existing local S09 `StartWindowProducer` has START-ONLY 3s worker and 2s Tk poller and stops when Start hides. These unrelated timings were NOT copied/assumed for detached mode.
- NEW `src/detached_one_shot_scanner.py` commit **8e0c35f93c3b031ae4120b8de49a843e8b875bef**: separate single explicit bounded, permission/limit-gated READ-ONLY Win32 worker per caller request; uses existing S08 `discover_game_windows` and S09 immutable `WindowSnapshot` but NEVER creates or shares Start poller/timer. Native backend constructed only inside worker; overlapping scan blocked; revocation and shutdown invalidate late HWND/PID publication. No Tk timers, native DWM/user-visible controls, game I/O, Proxy, credential writes or original source mutation.
- NEW `tests/test_s73.py` **12 unit cases** commit **847967d486a297bf55625f3cc980e3c52e159939**; NEW `tools/S73_WINDOWS_C14_ONE_SHOT_SCANNER_SMOKE.py` commit **b00cdab4e591919ff193e2799fabe1e5a99edbdf**; NEW `.github/workflows/s73-native-c14-one-shot.yml` commit **f260ff300814b8bc56bfaae0399108a985be9944**, NEW `docs/tasks/S73.md` + verified update. Source S59-S72, PLAN and original package unchanged.
- First native S73 CI **38029333016** FAILED **ONLY** native smoke TEST fixture asserting Tk Windows title must contain TEST string; actual bounded Win32 timed title calls returned empty test top-level titles. 1026/1026 Python units already passed. Fixed ONLY the test fixture (source untouched) commit **aa48b480ceb02b902308584cc0cd2f586962872c** to record native raw test-title values `["", ""]` honestly, while explicit original game identity substitutions remain isolated to test. No arbitrary title assumption shipped to production.
- **ACTUAL [S73 Windows native CI 38029396580](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38029396580), job 114146969177 COMPLETED SUCCESS**: **1026/1026** S01–S73 Python unit tests PASS; `PASS_NATIVE_S73_ONE_SHOT_WIN32_C14_INDEPENDENT_TEST_ONLY`: two REAL test-owned Tk HWND/PID via native Win32, explicit scan catches one real destroyed HWND, S72 observer invalidates old renderer, test never constructs Start UI, no unverified periodic timer. ALL S72–S10 native Windows regression steps PASS. Artifact **11661098211**, TEST ONLY, NO REAL GAME.
- **ACTUAL [S36 packaged diagnostic CI 38029283735](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38029283735), job 114146634066 COMPLETED SUCCESS**: **1026/1026** units; `PASS_NATIVE_S36_PACKAGED_DIAGNOSTIC_FAIL_CLOSED_NOT_PRODUCT`, both normal and unverified CLI `EXPLICITLY_BLOCKED_NO_GUI`; artifact **11662050434**, DIAGNOSTIC ONLY. Stage S source regression **38029283715 COMPLETED SUCCESS**.
- **STATUS S73_NATIVE_WINDOWS_1026_UNIT_PASS_READONLY_C14_ONE_SHOT_ONLY**. Source-backed identity and detached scan prerequisites are safe but NOT wired to original C14 1:1 auto-open, schedule or per-tile geometry. Original full interactive TLM EXE, signed Info, F05/F06 real game launch/login and game parity remain UNVERIFIED/MISSING.

## S73 FINAL CHANGED FILES
- NEW src/detached_one_shot_scanner.py; tests/test_s73.py (12); tools/S73_WINDOWS_C14_ONE_SHOT_SCANNER_SMOKE.py (one TEST-ONLY fixture correction); .github/workflows/s73-native-c14-one-shot.yml; docs/tasks/S73.md.
- APPEND STATE.md/PROJECT_STATUS.md. PLAN.md, original ZIP and S59–S72 functional source untouched.

## NEXT_ACTION on CONTINUE — S74 (ORIGINAL C14 HOST CONNECTION SAFETY / PARITY PRIORITY)
1. Read LIVE PLAN.md and STATE.md, inspect docs/tasks/S74.md; do NOT rewrite S59–S73.
2. Audit original C14 Start detach visible transition/closure, existing S70 topmost host S68 DWM session, S72 observer and S73 independent on-demand native scanner. Try to prove an independently useful **owner-thread controller for safely detaching/closing on verified HWND list change**, ONLY IF exact original behavior is source-backed. Do NOT invent detached auto-open cadence, geometry of thumbnail tiles, hidden preview state, game HWND from window label or a fake active `Tách rời` control. If no genuine source-backed addition is possible, document precise missing facts and pivot to another PLAN feature.
3. Preserve **1026/1026** verified Windows tests, S73–S10 real native regressions, S36 packed diagnostic fail-closed NOT PRODUCT, strict original artifact SHA-256; do not touch Proxy or build a fake product EXE. Checkpoint actual CI/files/blockers and specific NEXT_ACTION S75.

 
## S74 VERIFIED — C14 EXPLICIT SCAN -> REAL DWM HOST TEARDOWN, 1039 WINDOWS UNITS PASS
- Resumed LIVE PLAN.md and STATE.md from S73 NEXT_ACTION, checked S74 missing, original C14 compiled evidence (detached update loop independent of Start visibility, rebuild on game HWND list change), current S70 topmost DWM host, S72 owner-thread list observer and S73 explicit independent scanner. Original C14 tile geometry, actual detached periodic cadence, embedded hide/show, auto-open and live game remain UNKNOWN; did NOT invent them.
- NEW `src/detached_lifecycle.py` commit **3d0ab36c3f5764e9c9c4abd0c1ad99ed7884d408**: Tk OWNER-thread `C14DetachedLifecycle` composes existing S70/S72/S73. Explicit scanner.request/consumer, NEVER auto-opens/auto-renders host or creates fake UI. Changed HWND/PID list -> S72 callback closes existing native S70 DWM host BEFORE new list is accepted. Unchanged list preserves host. Worker/permission revocation, invalid scan, shutdown fail closed. Native teardown failure latches NATIVE_CLEANUP_FAILED_LOCKED; no false success; no guessed C14 timer or native tile placement.
- S74 source-only safety fix **a500ae512e437eb589b3b3697ce6d23fb42e7aeb**: recheck authorized max_windows even for ALREADY consumed snapshot revision; a lowered entitlement cap closes prior DWM host instead of returning NO_NEW_SCAN. Focused regression test #13 commit **e73ce0c4733dfea5a1eb8e7803fb806ecdbc033a**.
- NEW `tests/test_s74.py` **13 total cases** (original 12 commit **b2e63bb503474a834c20cc68381aa904bfb4796c** + entitlement-cap test); new `tools/S74_WINDOWS_C14_HOST_CLOSE_ON_CHANGE_SMOKE.py` commit **a6804284b86088bba4d88776ec552f24f7da6418**; new `.github/workflows/s74-native-c14-host-lifecycle.yml` commit **af4fa29deaf3041aa3715b1b0d2ff4516f45c2d8** and `docs/tasks/S74.md` (verified CI added).
- Initial S74 unit CI **38029951792** FAILED 10/1038 cases because S70 TEST-ONLY `SourceBackend` also exposed FAKE detached owner HWND 900 as a third fake game source to S73 scanner. Corrected ONLY S74 test fixture **0e6ee7a0ffc160226c4ab5a2ef2c828042f42ef1** to enumerate the two test-owned game-like HWNDs; production predicate unchanged. This was not runtime original game proof.
- **ACTUAL [S74 Windows native run 38030088120](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38030088120), job 114149005195 COMPLETED SUCCESS**: Windows compileall, **1039/1039** S01–S74 unit tests PASS (10.613s). `PASS_NATIVE_S74_EXPLICIT_C14_HOST_CLOSE_ON_HWND_CHANGE_TEST_ONLY`: two genuine test-owned Python/Tk native HWND/PID, genuine DWM thumbnail register/update/unregister/destination destroy, identical list preserves topmost host, REAL source HWND destroyed -> native teardown of all old DWM BEFORE native host destroys. ALL S73–S10 Windows native regression PASS. Artifact **11661537275**, TEST OWNED NO GAME. Actual hosted screen **1024×768** refused by original C14 formula; positive test used clearly labeled TEST-only 1600×1000 Tk screen metrics override. No false monitor/game parity.
- **ACTUAL [S36 packaged diagnostic run 38030088138](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38030088138), job 114149005190 COMPLETED SUCCESS**: **1039/1039** Windows units, `PASS_NATIVE_S36_PACKAGED_DIAGNOSTIC_FAIL_CLOSED_NOT_PRODUCT`, normal and unverified CLI both `EXPLICITLY_BLOCKED_NO_GUI`. Artifact **11661173998**, DIAGNOSTIC EXE, NOT PRODUCT. Stage S source regression 38030088103 COMPLETED SUCCESS.
- **STATUS S74_NATIVE_WINDOWS_1039_UNIT_PASS_C14_TEST_OWNED_HOST_CLEANUP_ONLY**. Original detached auto-open, full user-facing Hủy tách/Đóng xem, thumbnail tile spacing, runtime game F05/F06 and signed E03 licensing still MISSING/UNKNOWN. No change to S59 pixel measured buttons, existing S70/S71/S72/S73 modules, original ZIP/PLAN, any Proxy work or game memory/input.

## S74 FINAL CHANGED FILES
- NEW src/detached_lifecycle.py, tests/test_s74.py (13), tools/S74_WINDOWS_C14_HOST_CLOSE_ON_CHANGE_SMOKE.py, .github/workflows/s74-native-c14-host-lifecycle.yml, docs/tasks/S74.md.
- APPEND STATE.md / PROJECT_STATUS.md. Existing verified source/ZIP/PLAN untouched.

## NEXT_ACTION on CONTINUE — S75 (ORIGINAL PARITY-FIRST)
1. Read LIVE PLAN.md, STATE.md and check docs/tasks/S75.md, do not redo S59–S74 or alter scoped previous source.
2. Investigate original C14 detached tile x/y geometry or C07 Auto real tiler from original frozen binary and archived static evidence. Avoid guessing timed loop, replica screenshot geometry, sorted RoleName or hidden visibility transitions. If geometry cannot be recovered, prioritize another independently testable, *source-backed* PLAN gap with tangible UI/behavior impact instead of adding speculative detached scaffolding.
3. Keep **1039/1039** Windows unit baseline, S74–S10 native Windows regressions and S36 packaged diagnostic FAIL-CLOSED NOT PRODUCT. Document actual evidence, CI IDs, changed files, blockers and NEXT_ACTION S76. NO Proxy development, no forged signed Info, no unauthorized game memory/input, no full product EXE claim.

 
## S75 AUDITED — ORIGINAL C14 TILE / C07 AUTO SORT STATIC BINARY MARKERS, EXACT GEOMETRY BLOCKED
- Automatically continued from VERIFIED S74 NEXT_ACTION. Read LIVE PLAN.md/STATE.md and checked S75 document did not exist; reverified uploaded original TLM ZIP SHA256 **c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd**, 93,715,901 bytes / 1,050 archive entries. Read actual original 47,450,112-byte inner Nuitka EXE binary 0x2bfc140–0x2bfc380 (C07) and 0x2bfee10–0x2bff540 (C14). NO original EXE executed.
- NEW **docs/window/S75_C14_C07_BINARY_MARKERS.tsv**, **docs/tasks/S75.md**. Verified C14 serialized tile_w 0x2bff18d, region_y 0x2bff195, tile_h 0x2bff19f, ambiguous gap-adjacent serialized token 0x2bff186, `user_initiated=True` distinction in close doc at 0x2bff380, independent C14 window-list loop at 0x2bff400. Verified C07 `_sort_key`, `RoleName`, one-second rearrange doc. The markers are ORIGINAL BINARY DATA locations, **not recovered Python statements/compiled instruction addresses**.
- **BLOCKER**: exact C14 per-tile x/y/w/h equations, numeric gap, C14 scan cadence, auto-open/hide/restore transition, actual C07 RoleName comparator and tiler layout remain UNKNOWN. Additional strings cannot justify guessed runtime geometry. S75 is **STATIC_EVIDENCE_AUDIT_COMPLETE** only, **not** a new built user feature or parity-runtime completion.
- NO production source, tests, workflow, original ZIP or PLAN modified in S75. **1039/1039** existing Windows units and S74–S10 native regressions remain previously verified at [S74 Windows 38030088120](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38030088120), job 114149005195, artifact 11661537275, and [S36 packaged diagnostic 38030088138](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38030088138), artifact 11661173998 DIAGNOSTIC ONLY. S75 no new CI run.
- **STATUS S75_STATIC_AUDIT_COMPLETE_C14_C07_GEOMETRY_UNKNOWN**. Full original UI/game runtime, E03 signed Info/F05 F06 launch-login and finished product EXE remain MISSING. No Proxy.

## S75 FINAL CHANGED FILES
- NEW docs/window/S75_C14_C07_BINARY_MARKERS.tsv, docs/tasks/S75.md.
- APPEND STATE.md / PROJECT_STATUS.md; no runtime code changed.

## NEXT_ACTION on CONTINUE — S76 (HIGHER-VALUE SOURCE-VERIFIABLE PLAN COMPONENT)
1. Read LIVE PLAN.md, STATE.md and docs/tasks/S76.md; do not redo S59–S75. Keep original S75 geometry and comparator blockers explicit.
2. Identify another **genuine original-backed PLAN feature** with recovered input/output and interaction semantics to implement/test without inventing an inert UI control, role reader, hidden game actions or timed loops; prefer visible/behavioral parity gains over additional C14 scaffolding. If source evidence is insufficient, document exact blocker instead of faking behavior.
3. Preserve **1039/1039** existing Windows unit baseline, S74–S10 real Win32/DWM regression, S36 EXPLICITLY_BLOCKED_NO_GUI diagnostic NOT PRODUCT, no Proxy development, no guessed C12 restore, no entitlement bypass. Record CI and NEXT_ACTION S77 after scoped changes.

 
## S76 VERIFIED — C15 REAL EMBEDDED DWM REFRESH NATIVE FAILURE CLEANUP, 1051 WINDOWS TESTS PASS
- Resumed LIVE PLAN.md/STATE.md from S75 NEXT_ACTION, checked S76 doc absent, read original docs/tasks/C15.md: C15 "Làm mới" must deregister old native DWM thumbnails/destination HWNDs and destroy ALL original preview Tk frames before rebuilding while maintaining HWND-keyed manual C17 order. Audited existing **working** src/start_tab.py C15, C17, S09/S11; did NOT reconstruct/rewrite completed functionality.
- CONFIRMED original-backed LOCAL BUG: before S76, `TLMStartTab._drop_previews` invokes native DWM controller.shutdown() before unlinking owner; if one DWM unregister throws, `_clear_window_preview_list` exits before destroying any of its old Tk preview frames; public `refresh_window_preview_list` throws and may leave ghost UI/native owner. S71 already fixed native per-slot cleanup but Start UI cleanup owner missed corresponding protection. Original Nuitka exception branch UNKNOWN.
- SCOPED **only existing** src/start_tab.py change commit **a396faa605cef71ad7169b7c6f3aab09ba72e12c**: DWM controller unlink before native shutdown, sticky `_preview_cleanup_faulted` on native failure, ALWAYS attempt all Tk tile-frame destruction after DWM failure, never incorrectly rebuild/publish successful refresh on uncertified cleanup. User-facing text `Preview lỗi: giải phóng DWM chưa xác minh`. Subsequent C04 callbacks and explicit C15 refresh refuse untrusted new native DWM registration while read-only HWND status remains available. Normal successful C15 and C17 manual ordering untouched; no fake TLM UI, new timers/game read/input or Proxy.
- NEW tests/test_s76.py **12 unit tests** commit **6653b850230437f770a91874623fd592d41278e8**; native real Windows tools/S76_WINDOWS_C15_REFRESH_DWM_FAULT_SMOKE.py commit **0bb5b2f2191160567c89eedf033b7c161207effa**; workflow .github/workflows/s76-native-c15-refresh-fault.yml commit **65ca2999a5b877c637a007309eb0b5756b8e864e**; docs/tasks/S76.md. Initial Stage S **38035711818** and S36 **38035711814** failed 1/1051 cases only because the reused S15 TEST fixture stubs out `_schedule_preview`; TEST-ONLY test fix **2d6356623843d2b150a66bf7dbf866e1b0dfd980** now invokes actual unbound production scheduler for the guard test; source unchanged.
- **ACTUAL [S76 Windows Native CI run 38035808995](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38035808995), job 114165865390 COMPLETED SUCCESS:** **1051/1051** S01–S76 Python tests PASS (10.607s), `PASS_NATIVE_S76_C15_REAL_DWM_FAULT_CLEANS_ALL_TK_FRAMES`; two test-owned native Tk HWND+PID verified with real Windows APIs, two real native DWM thumbnail registered/updated; injection *after* first genuine DwmUnregisterThumbnail, actual second unregister still attempted, BOTH real DWM destination HWNDs destroyed BEFORE two real Tk preview frames, no ghost frames or repeat DWM registration. Full S74–S10 real native regression PASS. Artifact **11664520921** TEST-OWNED NO GAME.
- **ACTUAL [S36 packaged diagnostic run 38035808991](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38035808991), job 114165865306 COMPLETED SUCCESS:** **1051/1051** Windows unit tests (11.182s), `PASS_NATIVE_S36_PACKAGED_DIAGNOSTIC_FAIL_CLOSED_NOT_PRODUCT` and both normal/unverified CLI `EXPLICITLY_BLOCKED_NO_GUI`. Artifact **11664021045**, DIAGNOSTIC NOT PRODUCT. Stage S source regression **38035808997 COMPLETED SUCCESS**.
- **STATUS S76_NATIVE_WINDOWS_1051_UNIT_PASS_C15_REFRESH_DWM_OWNER_FAIL_CLOSED**. This is genuine production Start C15 cleanup bug-fix validated on REAL test-owned native HWND/DWM, **NOT real game** nor original 1:1 product parity. Original signed E03, runtime F05/F06, role reader/C07 geometry remain BLOCKED. S75 original ZIP SHA-256 still locked; Proxy untouched.

## S76 FINAL CHANGED FILES
- Scoped existing src/start_tab.py (C15 full-refresh native failure safety).
- NEW tests/test_s76.py (12), tools/S76_WINDOWS_C15_REFRESH_DWM_FAULT_SMOKE.py, .github/workflows/s76-native-c15-refresh-fault.yml, docs/tasks/S76.md.
- APPEND STATE.md and PROJECT_STATUS.md; original PLAN/archive and existing S59 visual baseline unchanged.

## NEXT_ACTION on CONTINUE — S77 (E08 / C15 NATIVE EXIT CLEANUP OWNER)
1. Read LIVE PLAN.md/STATE.md, inspect docs/tasks/S77.md, original E08 app shutdown and S76 src/start_tab.py. Do not redo S59–S76.
2. Audit native `_drop_previews` errors during `_stop_refresh` (tab navigation/revocation) and `shutdown` (Tk <Destroy>), which may abort before owner callbacks, poller.shutdown, Tk unbind and cleanup of work subsystems. If proven, minimally ensure **all downstream lifecycle owners attempt teardown** even if native DWM cleanup failed, with honest error propagation and no native re-registration; do not invent original OS process terminate/WM_CLOSE or input/click.
3. Keep **1051/1051** existing Windows units, S76–S10 real native regressions and S36 packaged diagnostic fail-closed NOT PRODUCT. Add real native test-owned HWND/DWM failure proof for any S77 change and checkpoint actual CI/files/blockers/NEXT_ACTION S78.

 
## S77 VERIFIED — E08 START NATIVE EXIT CLEANUP AFTER DWM ERROR, 1063 WINDOWS TESTS PASS
- Continued automatically after S76 verified milestone per user preference. Read LIVE PLAN.md/STATE.md S76 NEXT_ACTION and original docs/tasks/E08.md. E08 proves normal app close is Tk owner-destroy-driven, distinctly NOT E03 forced shutdown/updater/Start Reload or game process-kill. Source-backed C15 owns native DWM cleanup. Identified additional LOCAL bugs: `_stop_refresh` escaped on S76 `_drop_previews()` native exception before old preview UI clear and STOPPED status; `shutdown` escaped on same native exception before Tk root handler unbinds and S09 poller.shutdown. No prior functionality rewritten.
- ONLY existing src/start_tab.py modified S77 commit **2f1b5a03d2f49e9c3078b1a208e8f14729aaf1a7**: tab exit catches uncertain DWM shutdown, permanently latches fault, finishes cache/frame UI cleanup/STOPPED label; normal app shutdown attempts EVERY independently owned reset/stack/sync/maintenance/DWM/Tk-unbind/poller release even if prior native work throws, propagates FIRST error only after all attempted. No fake normal-close helper/game/process kill or new UI; preserves S76 cleanup semantics and all C15/C17 cached HWND code.
- NEW tests/test_s77.py **12 cases** commit **d1e2082bbf79d7ebaec29c86b39bdf306f2eef29**; NEW tools/S77_WINDOWS_E08_NATIVE_EXIT_CLEANUP_SMOKE.py commit **d0751af13e4b04201a3f45a3f36ea96b5a92a58b**; NEW .github/workflows/s77-native-e08-exit-cleanup.yml commit **bc30981c2a15c0d70685936bd71c9ef8041a2763** plus self-trigger fix **de8ab5f587e967b0f766d931dbe10339bbd0516f**; NEW docs/tasks/S77.md.
- **ACTUAL [S77 Windows native run 38036235651](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38036235651), job 114167120556 COMPLETED SUCCESS:** Windows compileall, **1063/1063** full Python unit tests PASS (10.357s), `PASS_NATIVE_S77_E08_ALL_OWNERS_AFTER_DWM_FAULT_TEST_ONLY`. Two separate native scenarios STOP and SHUTDOWN with real TEST-OWNED Tk HWND+PID and 2 actual DWM registrations each: a test-only fault injected after REAL first native unregister, second unregister attempted; all DEST HWND destroyed before genuine Tk frames; tab stop renders STOPPED with explicit uncertainty; shutdown runs all parent Tk unbind/worker/maintenance/poller teardown and propagates first native error. ALL S76–S10 native Windows regression PASS. Artifact **11663912679** TEST-ONLY NO GAME.
- **ACTUAL [S36 diagnostic EXE run 38036116432](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38036116432), job 114166767571 COMPLETED SUCCESS:** **1063/1063** Windows units (10.469s), `PASS_NATIVE_S36_PACKAGED_DIAGNOSTIC_FAIL_CLOSED_NOT_PRODUCT`, both CLI `EXPLICITLY_BLOCKED_NO_GUI`; artifact **11664231434** DIAGNOSTIC NOT PRODUCT. Stage S source regression 38036116422 COMPLETED SUCCESS.
- **STATUS S77_NATIVE_WINDOWS_1063_UNIT_PASS_E08_FULL_OWNERS_ATTEMPT_RELEASE**. Native tests owned Tk HWNDs, not original game/TLM or license verification; exact original E08 child Destroy emission and app restart sequence still unknown. Preserve S75 original artifact SHA256; no Proxy.

## S77 FINAL CHANGED FILES
- Scoped existing src/start_tab.py (_stop_refresh and shutdown full-owner exception safety).
- NEW tests/test_s77.py (12), tools/S77_WINDOWS_E08_NATIVE_EXIT_CLEANUP_SMOKE.py, .github/workflows/s77-native-e08-exit-cleanup.yml, docs/tasks/S77.md.
- APPEND STATE.md / PROJECT_STATUS.md only, original PLAN, original immutable ZIP, existing measured S59 Auto UI untouched.

## NEXT_ACTION on CONTINUE — S78 (ORIGINAL C03 DWM PREVIEW ACTIVATION PARITY)
1. Read LIVE PLAN.md and STATE.md, inspect docs/tasks/S78.md and original docs/tasks/C03.md and C03 evidence plus real src/dwm_preview.py NativeDwmBackend WndProc and Start UI preview. Do NOT redo S59–S77.
2. User-visible C03 preview *click activation* is a bigger original-parity gap than continued teardown primitives. Recover original source-backed exact master/preview activation gesture and safe native HWND/PID checks; if enough evidence to implement a genuine native test-owned Windows source/focus path without guessing mouse game inputs, add scoped functional feature and test. Otherwise document exact blocker/pivot to another proven high-value Plan feature, without adding fake buttons or unconditional clicks.
3. Preserve **1063/1063** existing Windows units, S77–S10 native Windows regression and S36 packaged diagnostic FAIL-CLOSED NOT PRODUCT. Document actual CI/artifacts/files/blockers and NEXT_ACTION S79. No Proxy, no guessed RoleName/C07 tiles or full product parity claim.

 
## S78 VERIFIED — ORIGINAL C03 REAL DWM DESTINATION CLICK ACTIVATION, 1076 WINDOWS TESTS PASS
- Automatically continued LIVE PLAN.md/STATE.md from S77 NEXT_ACTION. Original docs/tasks/C03.md proves actual `ThlDwmThumbDst` popup destination WndProc handles WM_LBUTTONDOWN/UP/DBLCLK (513/514/515), maps native DEST HWND -> source game HWND via `_dwm_dst_click_targets`, rechecks source HWND and uses `IsIconic/ShowWindow(SW_RESTORE,SW_SHOW)/SetForegroundWindow`. S11 native DWM backend previously had DefWindowProc-only destination and a LOCAL WS_EX_TRANSPARENT hit-test passthrough that precluded real C03 click activation. Original exact return/branch/foreground Windows policy UNKNOWN.
- Scoped existing production `src/dwm_preview.py`: added native destination click map keyed DEST HWND holding exact source HWND+PID, bind only after genuine validated DWM register and before slot publication, remove map before destroying actual popup, native WndProc handles ONLY 513/514/515 then revalidates HWND current PID/not hung immediately before real Win32 ShowWindow/SetForegroundWindow attempt. S11 local WS_EX_TRANSPARENT removed to enable hit testing while keeping NOACTIVATE/TOOLWINDOW/LAYERED; original exact style branch not asserted. Pure helper `_dispatch_dwm_click` permits test and native callback to share same guard; no synthetic game mouse/keyboard, injection, memory read, fake tab/Proxy or entitlement grant. Initial source commits **83dfc252fefa74e642d5a7c0ab1237000b390d9c** and **a0dd926407367091a69b44f7970cde16aad28b2e**.
- Initial native CI **38036677204** FAILED only native mapping assertion after **1075** unit tests PASS. Diagnostic run **38036752564** showed both real click maps absent: verified REAL source bug, two new methods were accidentally inserted into DwmBackend **Protocol**, not NativeDwmBackend, due repeated method anchor. Production bug fix commit **656fcd06f6a2a391621f6860b03077396270d636** relocated actual functions to native class. NEW unit guard test #13 commit **cece6386a2d51c24e88a30f5141aca71fed6a17f** requires method implementation concretely in NativeDwmBackend.__dict__, preventing fake-backend-only false confidence.
- NEW tests/test_s78.py **13 cases** (initial commit **841ad7eef02ce38b337359736c8a8d01f4365b1d**); NEW true Win32 `tools/S78_WINDOWS_C03_PREVIEW_NATIVE_CLICK_SMOKE.py` commit **1bdada8aadadea8f30d5da4932bde5b5d09f1125** plus diagnostic-only readback **b3f542f2840c933d4f606b85474ed3ef4c4fff3b**; new `.github/workflows/s78-native-c03-click-activation.yml` commit **fdc70f7f4666995a4517901268bb14c9a4f82c1f**; NEW docs/tasks/S78.md.
- **ACTUAL [S78 Windows native run 38036835906](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38036835906), job 114168909518 COMPLETED SUCCESS**: **1076/1076** S01–S78 Python unit tests PASS (11.057s). `PASS_NATIVE_S78_C03_REAL_WNDPROC_LEFT_CLICK_HWND_PID_GUARDED`: two actual test-owned native Tk source HWND/PID plus two DWM popup destinations, exact source map read back, SendMessageW actual 513/514/515 handled in native WndProc and real native Win32 activation API attempts recorded for correct HWND, right mouse ignored, vanished source HWND denied, all mappings cleared on native destruction. FULL S77–S10 Windows native regression PASS. Artifact **11664098591** TEST-ONLY NO GAME; Win32 foreground focus OS policy may deny end-result, actual game not run.
- **ACTUAL [S36 packaged diagnostic CI 38036835883](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38036835883), job 114168909489 COMPLETED SUCCESS**: **1076/1076** Windows units (10.710s), `PASS_NATIVE_S36_PACKAGED_DIAGNOSTIC_FAIL_CLOSED_NOT_PRODUCT`; normal and unverified CLI both `EXPLICITLY_BLOCKED_NO_GUI`. Artifact **11663578805**, DIAGNOSTIC EXE NOT PRODUCT. Stage S source regression 38036835878 SUCCESS.
- **STATUS S78_NATIVE_WINDOWS_1076_UNIT_PASS_REAL_NATIVE_C03_CLICK**. This is a genuine Start DWM overlay click functionality improvement, but original C03 Tk header/surface binding remains missing; full UI/runtime parity, signed E03 Info, actual game login/F05 F06, role reader/C07 geometry, finished product EXE still UNKNOWN/MISSING. Original ZIP/PLAN/Proxy unchanged.

## S78 FINAL CHANGED FILES
- SCOPED existing src/dwm_preview.py (C03 real source activation, active mapping lifetime and WS_EX_TRANSPARENT local style correction).
- NEW tests/test_s78.py (13), tools/S78_WINDOWS_C03_PREVIEW_NATIVE_CLICK_SMOKE.py, .github/workflows/s78-native-c03-click-activation.yml, docs/tasks/S78.md.
- APPEND STATE.md / PROJECT_STATUS.md, original immutable TLM ZIP/PLAN, screenshot and already-working S59 buttons untouched.

## NEXT_ACTION on CONTINUE — S79 (C03 EMBEDDED TK PREVIEW CLICK ACTIVATION)
1. Read LIVE PLAN.md and STATE.md, docs/tasks/S79.md, original docs/tasks/C03.md and C03 evidence. Do not redo verified S59–S78.
2. Original C03 has an independent Tk preview-frame/header `<Button-1>` activation closure `_make_activate`, separate from native overlay WndProc. Audit existing real Start `src/start_tab.py` tile widgets and guard selected/visible Start authorization/true HWND/PID. If source-backed enough, wire native HWND activation ONLY for genuine live S09 sources and current allowed tab with fail-closed stale/hung PID checks, without faking clickable game controls/mouse events/roles. Test real Tk and Windows native DWM Win32 focus attempt, ensure click handlers removed when preview frames destroyed. Otherwise document blocker rather than fabricate handler.
3. Preserve **1076/1076** verified Windows units, S78–S10 native Windows regressions and S36 packaged DIAGNOSTIC EXPLICITLY_BLOCKED_NO_GUI NOT PRODUCT. Record exact CI/artifacts/files/blockers and NEXT_ACTION S80. No Proxy work or full game parity claim.

 
## S79 VERIFIED — C03 REAL TK TITLE/SURFACE CLICK TO REGISTERED WIN32 DWM SOURCE, 1091 WINDOWS TESTS PASS
- Resumed LIVE PLAN.md, STATE.md S78 NEXT_ACTION and docs/tasks/C03.md; docs/tasks/S79.md initially absent. Original frozen TLM C03 static source confirms independent Tk header and preview surface `<Button-1>` activation through `_make_activate` and S78 independently recovered native DWM popup 513/514/515. Existing real Tk Start native DWM tiles were functional but did not have any genuine Tk click-to-activate callback. No completed S59–S78 implementation rewritten.
- SCOPED src/start_tab.py commit **4635e50ea9369bd5015cb587613381924bb06e1c**: bound `<Button-1>` to **existing** preview outer tile/frame, title label, black Tk preview surface for precisely closure-captured source HWND+PID; existing C17 left/right buttons preserved exclusively logical reorder. New `_activate_preview_source` reuses S78 native controller/backend for actual IsIconic/ShowWindow/SetForegroundWindow after fail-closed selected Start poller/Tk visibility, verified positive max_windows/count, live S09 immutable snapshot HWND/PID generation, current tiles/active list, genuinely registered DWM slot, last-moment real source_matches (IsWindow/current process PID/hung) check. Reject OS denied foreground and native exceptions without success; no game mouse input, memory injection, Proxy or local grant.
- NEW tests/test_s79.py **15 cases** commit **7dc841fc5a10429f7c3f69b200d84780408d98d0**. First Stage S run 38037697644 and S36 38037697683 had one TEST-ONLY fixture error: S15 minimal object lacked preview_grid_var for an unrelated C17 relayout; corrected ONLY test by stubbing irrelevant Tk geometry commit **ed6d1e2c412842d53540c9cac39b65fcadbef86c**. No production regression fix.
- NEW tools/S79_WINDOWS_C03_TK_PREVIEW_ACTIVATION_SMOKE.py commit **3f302fab957e80b54d3f616e1f3f602e28d39d8d** uses ACTUAL Windows/Tk shell/Info tab with explicitly TEST-ONLY local permission, two real test-owned source HWND/PID and genuine DWM destination slots; original Tk label/surface/tile clicks via Tk event_generate call S78 real native Win32 activation for correct source. C17 arrow ONLY reorders; stale cache PID/physically destroyed source/refused Info grant block clicks; normal app shutdown valid. NEW .github/workflows/s79-native-c03-tk-activation.yml commit **ebc4e2e77a0c0bb38ff39ff20c5d3cdba0144d87**, docs/tasks/S79.md (now CI verified).
- **ACTUAL [S79 Windows native run 38037824479](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38037824479), job 114171850484 COMPLETED SUCCESS:** Python **1091/1091** S01–S79 unit tests PASS (10.584s), `PASS_NATIVE_S79_C03_TK_CLICK_REAL_WIN32_SOURCE_TEST_ONLY`: TWO real native HWND+PID, genuine DWM slots; real Tk header/surface/frame click to real Windows ShowWindow/SetForegroundWindow API attempt for correct HWND; C17 reorder doesn't activate; PID reused/current HWND closed, Info revoke all blocked; full S78–S10 native Windows regression PASS. Artifact **11664313473**, TEST-OWNED NOT GAME.
- **ACTUAL [S36 packaged diagnostic run 38037824469](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38037824469), job 114171850504 COMPLETED SUCCESS:** Python **1091/1091** units (10.377s), `PASS_NATIVE_S36_PACKAGED_DIAGNOSTIC_FAIL_CLOSED_NOT_PRODUCT`, normal and unverified CLI both `EXPLICITLY_BLOCKED_NO_GUI`. Artifact **11664755650**, DIAGNOSTIC EXE NOT PRODUCT. Stage S source regression **38037824484 COMPLETED SUCCESS**.
- **STATUS S79_NATIVE_WINDOWS_1091_UNIT_PASS_C03_REAL_TK_WNDPROC_PREVIEW_ACTIVATION**. Win32 OS foreground control may reject focus, original game and signed license not run, exact original UI/runtime parity and finished EXE still unverified. Original ZIP/PLAN, previous S59 UI measurements/Proxy not touched.

## S79 FINAL CHANGED FILES
- SCOPED existing src/start_tab.py only (C03 real Tk preview click closure and safe HWND activation).
- NEW tests/test_s79.py (15), tools/S79_WINDOWS_C03_TK_PREVIEW_ACTIVATION_SMOKE.py, .github/workflows/s79-native-c03-tk-activation.yml, docs/tasks/S79.md.
- APPEND STATE.md/PROJECT_STATUS.md, preserved original user ZIP and PLAN.

## NEXT_ACTION on CONTINUE — S80 (C03 REAL CLOSED/HUNG PREVIEW ERROR VISIBILITY)
1. Read LIVE PLAN.md, STATE.md, docs/tasks/S80.md, original C03 native IsHungAppWindow source text and exact `Cửa sổ không phản hồi` / `Đã đóng cửa sổ` / `Preview lỗi` / `#ff5555` evidence. Check existing native src/dwm_preview.py and src/start_tab.py per-tile labels. Do not redo S59–S79.
2. Audit **actual visual missing behavior**: existing S11 native DWM source_matches combines closed/hung with generic error, Start preview status prints internal English code, whereas original C03 has human per-item error text. If truly source-backed and closed vs hung can be distinguished via genuine native identity state, implement narrowly per-item original error text/red status in existing Start widgets without inventing character/HP or original exact layout. Test actual Win32 test-owned source HWND closed and TEST-ONLY hung simulation; do not infer hung from missing window. Otherwise document precise blocker and pivot to another Plan feature.
3. Preserve **1091/1091** verified Windows units, S79–S10 true Windows native regression, S36 packaged diagnostic FAIL-CLOSED NOT PRODUCT; checkpoint real CI/files/blockers/NEXT_ACTION S81. Original SHA256/PLAN/UI/Proxy unchanged; no game memory/input, fake license or complete EXE claims.

 
## S80 VERIFIED — ORIGINAL C03 PER-TILE LIVE/CLOSED/HUNG RED PREVIEW ERRORS, 1105 WINDOWS TESTS PASS
- Resumed LIVE PLAN.md, STATE.md S79 NEXT_ACTION, read docs/tasks/C03.md original frozen Nuitka evidence: exact `Cửa sổ không phản hồi` message, `Đã đóng cửa sổ:` prefix, generic `Preview lỗi:` and red `#ff5555` per preview tile, source `IsHungAppWindow` check before native DWM registration. docs/tasks/S80.md did not exist initially. Found REAL missing original-backed user-visible behavior: S11 source_matches collapsed closed, reused PID and hung into `STALE_CLOSED_OR_HUNG_SOURCE` and Start only showed one global diagnostics bar; each black preview tile remained blank without source-backed red status. Did NOT redo S59–S79.
- SCOPED src/dwm_preview.py commit **19cfd8958e9c66d976659d0420158fc84b416fcd**: native source_status(hwnd,pid) produces LIVE, CLOSED (actual IsWindow false), STALE_PID (current GetWindowThreadProcessId differs from remembered identity), HUNG (**ONLY** real IsHungAppWindow true on still-correct HWND/PID). Existing source_matches uses same true native source state. Closed/reused/invalid HWNDs cannot be misreported as hung by fallback guessing; no guessed timeout or game memory read.
- SCOPED src/start_tab.py commit **d07fb2f6441097983f78730174f91ddac1d215b5**: existing C03 black preview Tk surface gains initially hidden per-tile red #ff5555 error label. _refresh_dwm associates returned DWM error to each actual cached source HWND/PID; native source_status HUNG shows exact original `Cửa sổ không phản hồi`, CLOSED/STALE_PID shows original `Đã đóng cửa sổ: ` with already cached native window title; other errors show honest generic `Preview lỗi: DWM`, never false hung. DWM source recovery hides stale per-item error and preserves all existing C03 197x110 DWM frames/C17 arrows/S78–S79 real native click. Original exact pixel placement of error message is NOT recovered; Tk placement is local, no new controls or character/HP injection. Test fixture short tuples remain tolerated.
- NEW tests/test_s80.py **14** unit cases commit **a44b532ff84499b25f455d5af82c492fbc720d85**; NEW true Win32+Tk DWM smoke tools/S80_WINDOWS_C03_HUNG_CLOSED_PREVIEW_SMOKE.py commit **8a0ce2609708e44a201c1971bec8b944f203267c**; NEW .github/workflows/s80-native-c03-hung-closed.yml commit **47987dcc8b33c2b1f02f94cd2a7fd8a371a7068f**; NEW docs/tasks/S80.md.
- **ACTUAL [S80 Windows native run 38039335213](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38039335213), job 114176276631 COMPLETED SUCCESS:** `Ran 1105 tests in 11.314s` **1105/1105** PASS, `PASS_NATIVE_S80_REAL_C03_HUNG_CLOSED_PER_ITEM`. TWO genuinely registered DWM thumbnails attached to two REAL TEST-OWNED Win32 Tk source HWNDs/PIDs. Native states LIVE confirmed. A **TEST-ONLY IsHungAppWindow adapter** flags one still-valid source HUNG → exact per-tile red label Cửa sổ không phản hồi + actual DWM unregister; returning LIVE → actual DWM re-register and error label hidden; physically DESTROY second real test-owned native HWND → real IsWindow false classified CLOSED (not HUNG), exact Đã đóng cửa sổ: prefix in red and actual DWM unregister. Full S79–S10 real native Windows regression PASS. Artifact **11664763319**, TEST ONLY NO GAME.
- **ACTUAL [S36 diagnostic packaged Windows run 38039274534](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38039274534), job 114176103590 COMPLETED SUCCESS:** **1105/1105** Python tests (10.708s), `PASS_NATIVE_S36_PACKAGED_DIAGNOSTIC_FAIL_CLOSED_NOT_PRODUCT`, both standard and unverified CLI `EXPLICITLY_BLOCKED_NO_GUI`; artifact **11664997882** DIAGNOSTIC NOT PRODUCT. Stage S source regression **38039274484 COMPLETED SUCCESS**.
- **STATUS S80_NATIVE_WINDOWS_1105_UNIT_PASS_C03_REAL_CLOSED_HUNG_PER_ITEM**. Actual original TLMTool/game and authenticated Info not executed; hung source was test-adapter simulated, not a hung real game. Source-backed text/color but original exact pixel alignment unknown. Existing S59 baseline, original ZIP/PLAN, no Proxy development, no fake TLM EXE.
 
## S80 FINAL CHANGED FILES
- Existing src/dwm_preview.py (native source classification), src/start_tab.py (C03 per-tile error label/restore).
- NEW tests/test_s80.py (14), tools/S80_WINDOWS_C03_HUNG_CLOSED_PREVIEW_SMOKE.py, .github/workflows/s80-native-c03-hung-closed.yml, docs/tasks/S80.md.
- APPEND STATE.md and PROJECT_STATUS.md, no other original source/UI/PLAN/immutable ZIP changes.
 
## NEXT_ACTION on CONTINUE — S81 (VISIBLE C05/C09/C15 START INTERACTION AUDIT)
1. Read LIVE PLAN.md, STATE.md, docs/tasks/S81.md, original C05/C09/C15 contracts and current src/start_tab.py implementation; do NOT redo S59–S80.
2. Prioritize a *genuine end-user* UI behavior over new hidden scaffolding: compare original source-backed preview/master-radio/1x–5x grid/manual refresh behaviors to current working Start. Find a concrete missing original-backed behavior with enough input/output semantics to implement/test safely on real Windows test-owned HWND+Tk. If unavailable, document the original evidence blocker instead of guessing RoleName reader or tiling math. Do not add inert controls.
3. Preserve **1105/1105** verified Windows units, S80–S10 genuine native regression, S36 packaged DIAGNOSTIC EXPLICITLY_BLOCKED_NO_GUI NOT PRODUCT. Record exact CI artifacts and NEXT_ACTION S82. No Proxy, guessed C07 automatic grid x/y, signed entitlement bypass or claims of full 1:1 product game runtime.
