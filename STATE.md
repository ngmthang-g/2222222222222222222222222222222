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
H08 — Train reconnect watchdog / reconnect recovery audit.

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
- `Đồng bộ các cửa sổ` is a real toggle backed by `_toggle_layout`.
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
- `Đồng bộ phím chuột` is a real persistent input-synchronization subsystem.
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
- Potential insertion order contains Start/Login/Party/Train/Train LSV/Train LD/Phó Bản/Daily/Đồn/Rao/Tối ưu/Info/Proxy/Debug/Debug Android.
- Gate-B visible production order is the same sequence with Train LD, Proxy, Debug and Debug Android hidden.
- Info is the invariant always-visible fallback; if selected tab becomes hidden, selection moves to Info.
- Debug/Android/Proxy are dev-gated; Đồn/Rao/Tối ưu are permission-controlled.
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
- Farm/Train LSV/Đồn/Daily expose synchronization helpers that mirror authoritative feature state back to Start buttons.
- Farm/Train LSV/Đồn have per-account plus all-account start/stop surfaces; Daily keeps separate Trừng Ác/Tàng Bảo Đồ FSMs.
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
- B03 screenshot transcription `Đồn văn` was corrected: source label is `Dồn vàng`; right-edge raster clipping hid/misled the final glyph.
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
- Final canonical label is **Dồn vàng** with internal mode `don`. PLAN.md was corrected from stale `Đồn vàng` occurrences to `Dồn vàng`.
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

## BLOCKERS
None known for H08.

## DO_NOT_TOUCH
- Preserve Gate A forensic baseline unchanged.
- Preserve B05 Train visual baseline and H01–H07 verified Train wiring/town/full-bag/timing/movement/heal/death contracts.
- Preserve Gate F Login handoff and Gate G Party handoff.
- Do not start Stage S source reconstruction early.
- Proxy runtime/network development remains locked out.
- Do not import behavior from older external Than Long projects as a substitute for frozen TLM evidence.
- Preserve H01 refresh 5000 ms and autosave 30000 ms.
- Preserve H02 return-town values/lock_town behavior.
- Preserve H03 occupied Site-10 bag metric and filter/no-town semantics.
- Preserve H04 loop_minutes × 60 remaining-cycle timing semantics.
- Preserve H05 movement conventions and active FarmTab Truyền ownership.
- Preserve H06 treatment routing/clicks and unresolved 0.2/common.active microbinding.
- Preserve H07 4s death monitor, MapID87 recovery event, HP0 single click (792,441), detected/hp latches, and death counter boundary.
- Do not import Train-LSV's post-respawn common.active wait into FarmTab.
- Keep exact treatment-failure continuation, respawn-off worker continuation, death-counter restart reset and monitor cleanup ordering UNKNOWN.
- H08 may analyze reconnect and its interaction with death, but must not reopen H07 monitor semantics unless contradictory evidence appears.

## NEXT_ACTION
On CONTINUE:
1. Read PLAN.md.
2. Read STATE.md.
3. Check GitHub first for any H08 artifacts/commits; if already complete and verified, do not redo them.
4. Execute H08 only if still pending.
5. Inspect the frozen original EXE first.
6. Audit Train reconnect end-to-end: _disconnect_monitor memory veto, disconnect pixel 3-strike detection, halt signaling, stop-character/auto interaction, exact reconnect click/pixel confirmation sequence, infinite retry policy, common.active waits, reconnect_ok cycle reset, cache invalidation/reinjection/memory-ready gate, and cancellation/window-generation exits.
7. Recover exact tick cadence, strike count, click coordinates, retry limits/wording and wait timeouts where safely bindable; keep unbound values UNKNOWN.
8. Resolve only death-vs-reconnect arbitration that is directly evidenced by the reconnect control flow; preserve H07 otherwise.
9. Cross-check B05 only after static extraction; no geometry work is needed.
10. Persist H08 evidence/report, update STATE.md, and advance to H09 only after verification.
