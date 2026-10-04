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

Current task: **F10 — post-login routing**

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
- E04 — AUDITED_CLOSED_WITH_OWNERSHIP_BOUNDARIES
- E05 — VERIFIED_WITH_EXPLICIT_BACKUP_COUNT_AND_LOCK_TYPE_UNKNOWNS
- E06 — VERIFIED_WITH_EXPLICIT_SIZE_CONSTANT_AND_THREAD_SERIALIZATION_UNKNOWNS
- E07 — VERIFIED_WITH_EXPLICIT_PER-WORKER_DAEMON_AND_JOIN_ORDER_UNKNOWNS
- E08 — VERIFIED_WITH_EXPLICIT_NORMAL_DESTROY_ORDER_AND_START_RELOAD_MICRODETAIL_UNKNOWNS
- E09 — VERIFIED_WITH_EXPLICIT_LOCAL_EXCEPTION_SCOPE_AND_RETRY_TIMING_UNKNOWNS
- E10 — VERIFIED_DISTRIBUTED_COORDINATOR_WITH_EXPLICIT_NO_GLOBAL_MUTEX_ASSUMPTION

E01 recovered the main GUI lifecycle, special forwarder branch, diagnostic/single-instance setup, tab construction, Info startup/heartbeat service and distinct normal-vs-forced shutdown paths. Splash micro-order and normal destroy ordering remain explicit unknowns.

E02 recovered the Tk root construction: transient 250x20 startup geometry, topmost/withdraw/icon behavior, exact root default font Segoe UI 9, Notebook 5 px packing margin, and the top-right 450/80/10 positioning model. Gate-B B13 was corrected only for the root/global font; per-widget override sizes remain explicit unknowns.

E03 recovered the potential tab insertion order, Info fallback, conditional/dev visibility, lazy build/rebuild path, scroll wrapper and selected-tab refresh ownership while preserving the Gate-B 11-tab production order.

E04 was audited rather than redone. The shared-state ownership model was coherent; only the missing JSON model artifact needed completion. Current work advances to E05 config management.

E05 recovered the shared configuration layer, duplicate-tolerant settings reads, atomic settings writes/backups, tab-owned key semantics, and the separate InfoTab config contract. Backup-retention count and concrete settings-lock type remain explicit unknowns.

E06 recovered the stdout/stderr tee session logger, crash/faulthandler output, custom thread-exception hook, separate memory log, and injected automove watchdog log. Central size constants and explicit concurrent-write serialization remain unknown.

E07 recovered the original concurrency model: Tk jobs, worker threads, queue/listener services, subsystem-owned cancellation/locks and native/helper boundaries. Exact daemon/join details remain per-worker evidence rather than a global policy.

E08 separated normal Tk destruction, forced heartbeat exit, in-process tab/preview refresh, Start unstick reload, Login account reload, and full updater-driven process relaunch. Normal all-forwarder cleanup and exact Destroy ordering remain explicit unknowns.

E09 recovered layered error containment: global crash/thread diagnostics, owner-local worker errors, nonfatal config failures, staged heartbeat/server errors, fail-closed permission guards, hung-window timeouts/retries, stale input recovery and emulator request validation.

## Gate E closure
E01–E10 are complete for static core/lifecycle evidence. The core model now covers lifecycle, root/window creation, tab loading, shared state, config, logging, concurrency, shutdown/reload, error containment, and distributed start/stop coordination.

## Gate F
- F01 — VERIFIED_ORIGINAL_EXE_FIRST_WITH_SCREENSHOT_PARITY
- F02 — VERIFIED_WITH_EXPLICIT_CHECK_TOKEN_AND_LEGACY_CAPTCHA_MIGRATION_UNKNOWNS
- F03 — VERIFIED_VISUAL_MASK_ONLY_WITH_DIRECT_UNENCRYPTED_STORAGE_EVIDENCE
- F04 — VERIFIED_RESOLVER_WITH_EXPLICIT_REVALIDATION_MICROSEQUENCE_UNKNOWNS
- F05 — VERIFIED_SUSPEND_INJECT_LAUNCHER_WITH_EXPLICIT_GENERAL_PROFILE_ITERATION_AND_CWD_UNKNOWNS
- F06 — VERIFIED_BACKGROUND_WINDOW_INPUT_WITH_EXPLICIT_GLOBAL_RETRY_LIMIT_AND_DELAY_UNKNOWNS
- F07 — VERIFIED_THREE_MODE_PROXY_ROUTING_WITH_LOCAL_DLL_READINESS_AND_EXPLICIT_LEGACY_MIGRATION_UNKNOWNS
- F08 — VERIFIED_5MIN_RUNTIME_ROTATION_WITH_STALE_30MIN_DOC_AND_INTERNAL_COOLDOWNS_EXPLICITLY_BOUNDED
- F09 — VERIFIED_DAILY_NEXT_OCCURRENCE_SCHEDULER_WITH_EXPLICIT_RESTART_AUTORESUME_AND_CLOSE_MICROORDER_UNKNOWNS
- F10 — VERIFIED_STATIC_ROUTING_F11_RESOLVED_1S_SUBSET_READINESS_WITH_RUNTIME_ONLY_SUCCESS_GUARD_UNKNOWN
- F11 — VERIFIED_LOGIN_GATE_HANDOFF_WITH_1S_HWND_SUBSET_READINESS_AND_RUNTIME_ONLY_MIXED_ZERO_SUCCESS_UNKNOWN

F01 completed the original-EXE-first Login UI contract and reconciled it with the locked screenshot. It resolved the group widget classes, exact after-login label `Dồn vàng`, header toggle-all semantics, 100-row logical capacity and captcha/proxy-cell static states without inventing hidden-widget pixels.

F02 recovered Login account persistence: settings.ini [Settings]/accounts, newline rows with pipe-delimited fields, plain-dict cache synchronization, 300 ms autosave debounce, plan-hidden row preservation, and separation from online-session/history JSON files.

F03 recovered the Login credential lifecycle: UI masking is display-only, the underlying value remains in the Entry/cache, persistence uses the direct account-row field with no recovered encryption layer, and the runtime login path carries the same value forward as mk/mk_val. No explicit clipboard or credential-log path was recovered.

F04 recovered the original game-directory resolver: exact double-space executable name, directory picker, tolerant direct/Game/parent/one-level-child recognition, persistent game_dir, status/error UI, and the _get_exe_path handoff boundary. Actual process launch/injection remains F05.

F05 recovered the original Login launcher: permission/limit guards, safe per-profile environment, suspended process creation, resources.dat injection before resume, PID-bound HWND discovery, serialized multi-account window launch and window-size normalization. Exact generic profile-selection and cwd derivation remain explicit unknowns.

F06 recovered the account login action after HWND readiness: PrintWindow-based readiness checks, background click_at/press_at input, exact login coordinates, update-popup handling, Vào trò chơi/common.active waits, success/online marking, retry cleanup, and semaphore-limited parallel click-login after sequential launches.

F07 recovered the three captcha/network modes, per-row action transitions, private-proxy validation entry path, local captcha-DLL readiness/freshness status, and the absence of a recovered external captcha-solving API. Legacy migration details remain explicit unknowns; forwarder/proxy mechanics move to F08.

F08 recovered the Login proxy/forwarder subsystem: free-pool refresh and fastest-first persistence, 5-minute runtime rotation threshold, per-profile ports/IIDs and state files, forwarder reuse/readiness, private pinning, cross-process free-proxy allocation, selective game-server routing, advance confirmation, and row reload semantics. A conflicting 30-minute doc string was identified as stale against runtime evidence.

## Proxy runtime development scope lock
By explicit user instruction on 2026-10-04, Proxy/network runtime development is out of scope. F08 remains analysis/documentation evidence only; future work must not implement or extend proxy runtime behavior unless the user explicitly reopens that scope.

F09 recovered the daily next-occurrence Login scheduler, independent manual-vs-scheduled control, 20s event checks, 1s countdown UI, no catch-up late-enable fix, optional 60s PC-shutdown confirmation, scheduled close/open behavior and persistent schedule settings. Fresh-process auto-resume from saved schedule_on remains unknown.


## Gate G
- G01 — VERIFIED_STATIC_UI_WIRING_WITH_STALE_DOC_TOGGLE_CORRECTION
- G02 — VERIFIED_PARTY_3S_INCREMENTAL_HWND_PID_GENERATION_REFRESH
- G03 — VERIFIED_NAME_VS_ACTION_IDENTITY_SPLIT_WITH_TEAMID_SENTINELS
- G04 — VERIFIED_NO_PARTY_GRID_ARRANGER_WITH_LEADER_ONLY_1366x768_RESIZE_PRECONDITION
- G05 — VERIFIED_NO_PARTY_PREVIEW_OWNERSHIP_OR_DIRECT_PREVIEW_CALL_EDGE
- G06 — VERIFIED_NO_PARTY_KEYBOARD_SYNC_OWNERSHIP_OR_START_INPUT_SYNC_CALL_EDGE
- G07 — VERIFIED_NO_PARTY_MOUSE_SYNC_OWNERSHIP_WITH_DIRECT_TARGETED_CLICK_FALLBACK
- G08 — VERIFIED_ACTIVE_TEAM_CONFIG_WITH_MULTI_GROUP_JSON_AND_LEGACY_GROUP1
- G09 — VERIFIED_CONTROL_WORKER_CANCEL_RESET_LIFECYCLE
- G10 — VERIFIED_B0_B3_PACKET_FIRST_TEAM_PROTOCOL_WITH_TEAMID_CONFIRMATION
- G11 — VERIFIED_POST_PARTY_MAIN_THREAD_ROUTING_WITH_20S_HWND_READINESS
- G12 — VERIFIED_GATE_G_RESEARCH_HANDOFF_WITH_RUNTIME_PARITY_RESERVATIONS

Gate G closes the Party research/static reconstruction handoff. B04 remains the visual authority; Party refresh uses shared Start HWND discovery with 3000 ms Party cadence and HWND+PID generation identity. RoleName is display/config identity while RoleID/TeamID are live action state.

Party does not own Start's physical window layout, DWM preview, keyboard sync or mouse sync. Active persistence remains name/group based through party_after, party_groups and legacy party_group1.

Party global execution runs one cluster thread per group with separate cancellation and reuses the same _run_one_group engine for single-cluster actions. The active team protocol is B0 auto-accept → B1 leave/verify outside → B2 packet-first team create with fixed-coordinate fallback → B3 burst invite with one resend and TeamID verification.

Post-party routing is global-aggregate only: wait is no-op, Phó Bản is a whole-tab handoff, and Train/Train LSV/Dồn vàng use bounded 1s/20s destination readiness plus HWND-first/name-fallback per-account _toggle_single_farm dispatch.

Remaining Party unknowns are preserved in G12 and classified as implementation-safe, runtime-only, or stronger-decompilation-required. The mandatory Windows original-vs-reconstruction parity matrix contains 33 cases. Stage S has not started.

## Gate G closure
G01–G12 are complete for Party static/visual research and reconstruction handoff. Runtime parity and the explicitly classified unknowns remain deferred. The next PLAN phase is H — Train.


## Gate H
- H01 — VERIFIED_FARMTAB_UI_MODULE_WIRING_WITH_5S_INCREMENTAL_REFRESH_AND_30S_AUTOSAVE
- H02 — VERIFIED_TOWN_MODE_GATING_WITH_LOCK_TOWN_FORCE_NEVER_AND_LEGACY_FULL_BAG_ALIAS
- H03 — CURRENT

H01 recovered the FarmTab module/UI ownership contract without remeasuring B05. FarmTab owns Train UI/config/account rows, consumes shared Start window discovery, refreshes account rows incrementally every 5000 ms, and performs a 30000 ms periodic config autosave. The verified B05 screenshot hash remains unchanged.

H01 intentionally defers return-town semantics, inventory-full, periodic-town timing, movement, heal/death/reconnect, loot, mount, coordinate semantics and the farm FSM to later H tasks.

## Gate H current
H02 — Train return-town condition and town-panel gating audit.


H02 resolved the current return-town mode contract: never / full_bag_timer / cycle, default cycle with 30 minutes. The lower town panel is independently default-hidden. Legacy full_bag is a compatibility alias for the current full-bag mode, not a fourth visible option.

Any selected Farm route marked lock_town forces the shared return-town mode to never and disables the return-town radios; no automatic previous-mode restoration was recovered. Navigation priorities remain four readonly unique-choice slots with defaults Phù 1 / Phù 2 / Phù 3 / Ngựa.

H03 now owns inventory-full detection, bag threshold/filter interaction and the full_bag_timer early-stop path. Periodic loop-minute scheduler execution remains H04.
