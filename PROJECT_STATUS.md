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
- H03 — VERIFIED_SITE10_USED_SLOT_FULL_BAG_WATCH_WITH_FILTER_RECHECK_IN_NEVER_MODE_AND_EXPLICIT_THRESHOLD_BINDING_UNKNOWN
- H04 — VERIFIED_CYCLE_REMAINDER_WAIT_WITH_60S_MINUTE_CONVERSION_AND_FULL_BAG_EARLY_BREAK_WITH_EXPLICIT_WAIT_QUANTUM_UNKNOWN
- H05 — VERIFIED_SAVED_PRESET_TILE_MOVEMENT_WITH_8_TILE_NEAR_SKIP_AND_LIVE_TRUYEN_RETURN_WALK_FALLBACK
- H06 — VERIFIED_BUILTIN_OR_MANUAL_TREATMENT_ROUTE_WITH_EXACT_TWO_CLICK_POINTS_X4_AND_BOOLEAN_FAILURE_HANDOFF
- H07 — VERIFIED_4S_MAP87_HP0_RESPAWN_MONITOR_WITH_LATCHED_SINGLE_CLICK_EVENT_DRIVEN_RECOVERY_AND_EXPLICIT_RETURN_BRANCH_UNKNOWN
- H08 — VERIFIED_2S_MEMORY_VETO_3STRIKE_RECONNECT_WITH_5_ATTEMPT_30S_ACTIVE_BATCHES_INFINITE_RETRY_AND_45S_MEMORY_READY_FAILOPEN_DIRECT_REINJECT_EDGE_UNKNOWN
- H09 — VERIFIED_KEEP_MODE_TO_TRAIN_DISCARD_PRESETS_WITH_EVENT_DRIVEN_PRETOWN_FILTER_1S_DEFAULT_DISCARD_PACING_AND_SEPARATE_5S_HIDDEN_PICKUP_ENABLE
- H10 — VERIFIED_MEMORY_PACKET_MOUNT_WITH_ISRiding_FASTPATH_3S_VERIFY_AND_AUTOPATH_REMOUNT_REQUEUE_HOME_PRIORITY_HORSE_SENTINEL_RETRY_LIMIT_UNKNOWN
- H11 — VERIFIED_SEQUENTIAL_COORD_KEYS_PIPE_SCHEMA_LIVE_RENAME_PROPAGATION_WITH_UI_ONLY_LIST_VISIBILITY_AND_EXPLICIT_SAVE_SCHEDULER_DELAY_UNKNOWN
- H12 — VERIFIED_PID_BOUND_INCREMENTAL_ROW_MODEL_WITH_5S_BACKGROUND_REFRESH_MAIN_THREAD_APPLY_POSITIVE_DELTA_EXTRA_TRACKING_AND_GENERATION_GUARDS
- H13 — VERIFIED_ALL_ROW_FANOUT_WITH_DAEMON_UI_DISPATCH_PARALLEL_COMMANDS_AND_EXPLICIT_INNER_WAIT_UNKNOWNS
- H14 — VERIFIED_COOPERATIVE_MULTI_ACCOUNT_FSM_WITH_PER_ROW_STOPPING_SENTINEL_JOINED_DRAIN_AND_UI_MIRROR_EXPLICIT_UNKNOWNS
- H15 — CLASSIFIED_WITH_EXISTING_RUNTIME_PRIMITIVE_EVIDENCE_AND_WINDOWS_RUNTIME_MATRIX

H01–H14 complete the frozen Train static/visual reconstruction contract: FarmTab wiring and 5s refresh/30s autosave; return-town modes; Site-10 bag/full behavior; periodic timing; saved-preset movement and Truyền return routing; treatment; death/Địa phủ recovery; reconnect; keep-mode filtering and hidden pickup enable; memory/packet mount/remount; coordinate persistence; PID-bound row/tracker model; all-account commands; and the cooperative global/per-row Farm FSM.

H15 rechecked the frozen archive/EXE and inventoried actual runtime evidence instead of treating static recovery as runtime proof. The exact package contains `data/automove_log.txt` (SHA-256 `17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`, 15,741,058 bytes, 387,238 lines). It records real primitive execution including 16,040 AutoMove queue events, 15,993 StartAutoPath calls, 2,027 StopAutoPath calls, 8,511 AutoFight_Main records, 1,579 mount-toggle commands, 114 Game.GoTo calls, 114 NPCShop probes and 22,732 action=4 ItemAction sends.

Those records validate low-level primitives only. They do not identify which top-level Train button/Farm generation caused every record, nor prove arrival, sale completion, recovery completion or the H14 UI/FSM transitions. H15 therefore keeps end-to-end cases honest.

The H15 parity matrix contains 45 cases:
- 8 `RUNTIME_VERIFIED_FROM_EXISTING_EVIDENCE`
- 34 `RUNTIME_ENV_REQUIRED`
- 3 `STATIC_VERIFIED`
- 0 `BLOCKED`.

A 35-scenario Windows test plan now covers global/single Farm start-stop, partial/last-account stop, StartTab synchronization, all-account fan-out, full-bag threshold, cycle timing, movement/Truyền, treatment, death, reconnect, hidden pickup, filtering, mount/remount, coordinates, row refresh/tracker, PID reuse, permission limits, full Farm-cycle ordering, stale-generation cancellation, resize monitoring and actual sell completion.

## Gate H closure
**CLOSED_FOR_STATIC_VISUAL_RESEARCH_HANDOFF / END_TO_END_RUNTIME_PARITY_DEFERRED**

This closure means the Train subsystem no longer needs to be re-researched before later reconstruction. It does **not** claim that the original Windows tool has been fully runtime-tested in the current Linux environment. H15's Windows matrix remains mandatory before any final Train runtime-parity claim.

Stage S has not started. The next PLAN phase is **I — Train LSV**, beginning with I01 module/UI/config wiring audit.


## Gate I
- I01 — VERIFIED
- I02 — VERIFIED
- I03 — VERIFIED
- I04 — VERIFIED
- I05 — VERIFIED
- I06 — VERIFIED
- I07 — VERIFIED
- I08 — VERIFIED
- I09 — VERIFIED
- I10 — VERIFIED
- I11 — VERIFIED
- I12 — CLOSED_FOR_STATIC_VISUAL_RESEARCH_HANDOFF / END_TO_END_RUNTIME_PARITY_DEFERRED

Final TrainLSV parity matrix:
- 80 total rows
- 24 STATIC_VERIFIED
- 3 RUNTIME_VERIFIED_FROM_EXISTING_EVIDENCE
- 53 RUNTIME_ENV_REQUIRED
- 0 BLOCKED.

The exact frozen archive, inner EXE, TrainLSV module chunk, B06 and packaged runtime helper log were revalidated before closure. All 44 I01-I11 artifacts were re-inspected and no contradiction required reopening an earlier task.

Packaged runtime evidence remains primitive-scoped only:
- AutoMove queued 16,040
- StartAutoPath 15,993
- StopAutoPath 2,027
- AutoFight_Main 8,511
- action4 22,734 raw / 22,732 spts.

There is no correlated top-level TrainLSV trace in the packaged helper log, so end-to-end runtime parity is not claimed.

A 53-scenario Windows/live-game test plan now covers the remaining I02-I11 runtime edges. Unexecuted scenarios remain UNVERIFIED, never PASS.

**Gate I closure**
CLOSED_FOR_STATIC_VISUAL_RESEARCH_HANDOFF / END_TO_END_RUNTIME_PARITY_DEFERRED

Phase I research may hand off. Stage S remains locked and TrainLSV runtime parity must still be executed later before claiming full functional parity.

## Phase J — Phó Bản
- J01 — VERIFIED_PARTY_FORMATION
- J02 — VERIFIED_LEADER_METADATA_PROPAGATION_NO_TEAM_LEADER_MEMORY_DEPENDENCY
- J03 — VERIFIED_RUN_SCOPED_FOLLOWER_WITH_DUNGEON_ONLY_SAME_MAP_QUEUE_ONLY_FOLLOW_MODE_AND_COMMAND_CLASH_GUARDS
- J04 — VERIFIED_GROUP_LOCAL_ORDERED_SCHEDULE_MODEL_WITH_MODERN_PLUS_LEGACY_CONFIG_COMPATIBILITY
- J05 — VERIFIED_EXACT_DUNGEON_BINDING_TABLES_WITH_BASE_FALLBACK_AND_SATTINH_CUSTOM_HANDLER
- J06 — VERIFIED_MANUAL_DUNGEON_TIMES_WITH_ENTRY_DEFAULT1_SHARED_BARRIER_AND_TRAIN_TIMES_IGNORED
- J07 — VERIFIED_GROUP_ABORT_BARRIER_BREAK_IDENTITY_SAFE_TEARDOWN_WITH_J13_HOOK_AND_GENERIC_WORKER_CORRECTIONS
- J08 — VERIFIED_RUN_SCOPED_DISCARD_WORKER_WITH_PARALLEL_ACCOUNTS_SEQUENTIAL_PRESETS_AND_FINAL_PASS
- J09 — VERIFIED_RUN_SCOPED_PICKITEM_ISON_KEEPALIVE_WITH_ALL_SELECTED_MEMBERS_AND_NO_RECOVERED_OFF_SWEEP
- J10 — VERIFIED_NGA_MY_AUTOTRAIN_LIST910_KEEPALIVE_WITH_DUNGEON_GATE_AND_FINAL_UNTICK_OFF_SWEEP
- J11 — VERIFIED_DYNAMIC_MULTI_GROUP_COORDINATION_WITH_UNIQUE_MEMBERS_PARALLEL_JOBS_AND_LOCKED_WORKER_SCOPES
- J12 — VERIFIED_PERMISSION_GATED_INTEGRATED_START_STOP_WITH_PERSISTED_MODES_AND_LAST_GROUP_TEARDOWN
- J13 — VERIFIED_INTEGRATED_FAILURE_RECOVERY_WITH_PARTIAL_SETUP_TRAIN_FAIL_SOFT_AND_J07_CORRECTIONS
- J14 — STATIC_RESEARCH_CLOSED_LIVE_RUNTIME_PARITY_DEFERRED

J01 locks the six-slot group model and optional B0/B1/B2/B3 recreate-team pipeline.

J02 separates visible first-slot leader, recreate-team leader, run-local is_leader metadata and game FUBEN.FollowLeader.

J03 locks the optional "Theo sau đội trưởng" subsystem. `phoban_follow` defaults OFF. The follower worker exists only while at least one schedule group is running; enabling before a run keeps the mode armed and waits, while run start can create the worker. Run completion stops the worker without clearing the persisted checkbox.

For each running group, the leader-position source is the first combobox and followers are the remaining slots. Positions come from MapID/PosX/PosY memory reads. Follow only operates inside DUNGEON_MAP_IDS, requires follower and leader on the same map, and explicitly excludes Sát Tinh map 111.

Two independent safety gates are preserved: PB_FOLLOW_DIST_TILES controls when leader/follower distance warrants a follow move; PB_FOLLOW_MOVE_TILES detects large follower self/foreign movement and yields for that poll unless the previous poll was follow-commanded. Exact numeric PB_FOLLOW values remain unknown.

A second shared clash guard calls `is_move_poll_active`; the frozen shared helper has exact 0.5-second TTL and exists specifically so Follow does not steal an HWND currently controlled by a move_character wait-for-arrival poll.

Follow uses shared `move_character` in queue-only mode: effective `wait_for_arrival=False`, `follow_mode=True`. The frozen doc explicitly forbids Phù, stop-auto and mount toggles, preserving active auto FuBen.

No correlated PhoBanTab follow trace exists in the packaged helper log. Generic AutoMove/StartAutoPath/StopAutoPath lines remain primitive-only evidence.

J04 locks the original schedule-row architecture: per-group rows with fields enabled/activity/name/times, only Phó bản/Train activities, modern phoban_groups plus legacy phoban_group1/phoban_schedule compatibility, and the exact execution hierarchy of groups in parallel, rows sequential within each group, accounts parallel within each row. J05/J06/J07 boundaries remain deliberately deferred.

J05 locks the exact eight visible Phó Bản names, nine-key FuBen-code/MapID alias tables, the hidden plain-Sát-Tinh alias, BaseDungeon fallback architecture, and SatTinhDungeon as the only current custom handler. Both Sát Tinh aliases resolve semantically to SatTinhDungeon while ordinary dungeons stay on the shared BaseDungeon flow.

J06 locks the current Lần control as a free Entry with default 1, manual tool-side dungeon repetition, per-repetition memory config, shared-row barrier reuse, MapID enter→non-None-exit completion, and the fact that Train ignores the preserved Lần value and activates once. It also records the compiled 480-second map-watchdog branch that conflicts with a stale “vô thời hạn” helper doc, plus explicit run_idx/caller-literal unknowns.

J07 locks the two-layer cancel model, exact red/orange run-button states, current-group-only idempotent barrier-breaking abort, last-group-only global teardown, and identity-safe rapid-restart cleanup. J13 later corrected two J07 overclaims: hook exceptions are a static doc-vs-branch conflict, and generic acc-step worker exceptions have no independent abort wiring. The compiled 480-second watcher remains real while its exact timeout return expression is unresolved.

J08 locks the three discard controls, exact config/preset mappings, run-scoped generation-safe worker, parallel-account/sequential-preset execution, per-account inflight guard, internal action-4 packet path, and the normal-completion final discard pass. PB_DISCARD_POLL numeric value and late-cancel/final-pass races remain explicit runtime unknowns.

J09 locks Nhặt không hồ lô as a persisted run-scoped PICKITEM.IsOn keepalive: all selected Phó Bản members across all groups are de-duplicated and re-resolved to live HWNDs, IsOn is read back every PICK_POLL and repaired to True through set_auto_fields/SaveSetting, and no pickup-local OFF sweep is recovered. Pickup has stop/thread state but no generation field; PICK_POLL numeric and stop/start race microdetails remain explicit runtime unknowns.

J10 locks Nga My buff as a run-scoped AUTOTRAIN monster-list keepalive: FactionID 4 (fallback Nga My), ON = IsAttackMonsterInList True + list "910", OFF = False + empty list, readback-before-write with retry, currently-running-group scope, generation protection, and an explicit final OFF sweep on untick. Despite the UI suffix “Sát Tinh”, the frozen worker contract gates on being inside a dungeon map rather than a recovered map111-only check.

J11 locks the dynamic group container, delete-all behavior, six-member per-group cap with no recovered hard group-count cap, cross-group account uniqueness, per-group schedule/run ownership, start-all parallel job collection, independent group finish/stop semantics, and the intentionally different cross-group scopes of Follow/Discard/Pickup/Nga My buff. The reference B07 baseline has one group, while exact missing-config bootstrap microbehavior remains explicit rather than guessed.

J12 locks the integrated start/stop lifecycle: stop routing precedes start preflight, new starts are permission-gated and runnable-job-filtered, progress reset scope differs for one-group versus all-group starts, every run has fresh group cancel/job identity, stop-all is cooperative with orange winding-down UI, persisted mode checkboxes survive stop/end, and global teardown occurs only when the final group is gone. Run start must re-arm enabled Follow/Discard/Pickup/Buff modes, while the exact native call order relative to group Thread.start and the internal _on_destroy cleanup sequence remain explicit static unknowns.

J13 locks the integrated failure/recovery matrix: setup can degrade per-account, explicit dungeon stages hard-abort only the current group after local retries, Train and final-discard failures are fail-soft, background-worker errors do not independently abort the schedule, and recovery is manual fresh-start rather than automatic whole-group restart. J13 also corrected two prior J07 overclaims: hook exceptions are now a static doc-vs-branch conflict, and generic acc-step worker exceptions have no independent abort wiring.

J14 confirms the current execution environment cannot run the original Windows/game stack. No live result was fabricated. A 25-case Windows runtime/stress matrix and harness specification now preserve exactly what must be verified later, including rapid restart identity safety, multi-group independence, worker scopes, the 480-second watchdog and the hook-exception conflict.

## Phase J gate
**STATIC_RESEARCH_CLOSED / LIVE_RUNTIME_PARITY_DEFERRED**

## Phase K — Daily
- K01 — VERIFIED_ACTIVE_DAILY_AUTHORITY_VISIBLE_SURFACE_70_HANDLER_INVENTORY_AND_DEPENDENCY_BOUNDARY
- K02 — VERIFIED_SHARED_ROSTER_PID_IDENTITY_GENSTOP_TK_MARSHAL_AND_ALL_ACCOUNT_COORDINATOR
- K03 — VERIFIED_PUNISH_CONFIG_SELECTION_BATCH_VS_SINGLE_OPEN_ENDED_LOOP
- K04 — VERIFIED_NPC_RETURN_QUEST_30OF30_AND_STUCK_CANCEL_FLOW
- K05 — VERIFIED_ITEM40004000_DIALOG_USEITEMDATA_FAST_TRAVEL_STREAK_AND_SUMMON_FLOW
- K06 — VERIFIED_PUNISH_COMBAT_MONOTONIC_DURATION_AUTOTRAIN_FAILSOFT_DRIFT160_AND_MOVEMENT_HELPER_BOUNDARY
- K07 — VERIFIED_DAILY_PUNISH_HEAL_RESPAWN_AND_RECONNECT_RECOVERY
- K08 — VERIFIED_DAILY_PUNISH_DISCARD_RUN_SCOPED_PARALLEL_PER_ACCOUNT_PACKET4
- K09 — VERIFIED_TRUNG_AC_INTEGRATED_LIFECYCLE_FAILURE_MATRIX_AND_STATIC_HANDOFF
- K10 — VERIFIED_TREASURE_CONFIG_SELECTION_BATCH_SINGLE_TOPLEVEL_LOOP_AND_RECOVERY_SHELL
- K11 — VERIFIED_TREASURE_MOUNT_BAG_MULTIPIXEL_TWO_STAGE_ACTIVATION_AND_MOVEMENT_WAIT
- K12 — VERIFIED_TREASURE_MAP96_MOVE_COMMON_ACTIVE_TOMB_DURATION_NON96_SKIP_AND_FINAL_HEAL_BOUNDARY
- K13 — VERIFIED_TREASURE_HEAL_SELECTED_MAP_RECOVERY_ADAPTER_CACHE_READY_AND_RESPAWN
- K14 — VERIFIED_TREASURE_SKIPPED_ACCOUNT_STOP_RESET_AND_FAILURE_LIFECYCLE
- K15 — VERIFIED_TREASURE_INTEGRATED_LIFECYCLE_FAILURE_MATRIX_AND_STATIC_HANDOFF
- K16 — VERIFIED_DAILY_SHARED_CROSS_ACTIVITY_LIFECYCLE_PERSISTENCE_COORDINATOR_AND_OWNERSHIP_BOUNDARY
- K17 — STATIC_RESEARCH_CLOSED_RUNTIME_PARITY_MATRIX_PENDING_LIVE_ENV

K01 locks `.daily_tab` / `daily_tab.py` / `DailyTab` as the active Daily authority, verifies the explicit Trừng Ác versus Tàng Bảo Đồ UI split, freezes the shared account-row/global-control surface, records the exact 70-member top-level callable inventory, and separates direct Daily module references from weaker non-import emulator edges.

K02 locks the five-second incremental roster refresh, HWND+PID anti-reuse identity, create/update/stale-row lifecycle, 30ms scroll debounce, permission-gated row controls, exact state styles, Tk after(0) state marshalling, generation-protected per-row stop semantics, per-row activity dispatch, all-account Bắt đầu/Dừng lại coordinator, singleton Daily monitor and transient row-session persistence boundary.

K03 locks the clean Trừng Ác duration/move/hotkey configuration, old/new teleport-config compatibility boundary, Apply-all selection semantics, distinct activity-batch versus per-row worker ownership, exact activity-level button states, selected/PID start snapshot, per-loop live/active filtering, open-ended iteration semantics, and separate batch-cancel versus row Event/generation stop identities.

K04 locks map-4 NPC return to tile (224,285) with tolerance 96 and fail-open reinjection, the fixed return/receive quest click groups, memory/GameDialog 30-of-30 detection with terminal per-account stop, and the map4/NPC698 stuck-quest cancellation path that recovers into the next outer cycle. K04 was recovered from a partial GitHub state without redoing its already-correct task/flow/model artifacts; the missing evidence artifact was added before closure.

K05 locks Trừng Ác Lệnh item ID 40004000, internal action-3 item use, two-attempt target-acquisition use, GameDialog→UseItemData target extraction, fast_travel target movement, consecutive stuck-target recovery with unresolved numeric threshold, and the second-use GameDialog summon flow through internal Triệu hồi activation. A repository-wide continuity/build audit also confirmed that Stage S/application source has not started, so there is no reconstructed product build target yet rather than a broken build.

K06 locks the successful-summon → combat segment: `punish_duration` is a monotonic elapsed-time window; combat state is `Đánh ác tặc`; death can end the fight early; shared `start_auto_train` is the enable primitive and its default verification contract is Direction-based with 3 samples at 1.0s and up to 3 send attempts. Daily's exact failure policy is fail-soft (`gửi bật auto train thất bại → vẫn đánh tiếp`). The combat tail owns a 160-pixel `math.hypot` drift detector, final-HP/heal boundary, and normal `Kết thúc` return to the already-proven outer loop. No explicit Daily `stop_game_auto/AUTO_MODE_NONE/stop_auto_train` surface is recovered at combat end. K06 also freezes `_wait_movement_stopped`: `by_memory` defaults False, its memory helper uses timeout 300s / 6 stable polls / 0.5s / 16px defaults, and the explicit recovered Daily call surface is in Tàng Bảo Đồ rather than the Trừng Ác combat block. B08 was rechecked only after static extraction; packaged runtime log contains generic AutoFight primitives but no correlated Daily/K06 trace.

K07 locks Daily-specific Trừng Ác recovery without importing Farm semantics. `_diaphu_monitor` runs every 4s, clicks revive at (792,441) on HP0, and sets `respawn_event` on MapID 87; the next cycle clears that event so heal/movement can leave Địa phủ. Low-HP treatment is checked at cycle start and end; start-heal failure skips only the current cycle. `_punish_heal` targets Tô Châu map4 tile (155,252), uses movement tolerance 10, and injection failure is fail-open to direct movement. `_punish_disconnect_monitor` runs every 2s with `memory_items.is_connected` as a True-veto plus exact dual disconnect pixels, requiring 3 consecutive ticks (~6s) before `halt` + reconnect click (616,455). Activity-wide Daily reconnect has an exact 60s bounded wait with OK→continue / timeout→stop. The single-account recovery path uses `wait_pixel(common.active)`, cache invalidation and `wait_memory_ready(timeout=45, need=3)` with shared 1.0s sampling and fail-open timeout. No Daily `/5` attempt or infinite reconnect-batch surface is recovered, and no unconditional post-reconnect DLL reinjection edge is proven.

K08 locks the Trừng Ác equipment-discard subsystem as a separate run-scoped background worker rather than a per-cycle step. The persisted checkbox defaults OFF and, when armed, starts only when Trừng Ác accounts are running; it stops immediately on untick and can re-arm on a later run. The worker scopes to current running/non-disconnected Trừng Ác HWNDs, fans out one child thread per eligible account, and uses per-account `inflight` protection so slow passes do not overlap. Each child calls `bag_filter.discard_for_activity(activity="daily", keys=["discard_equip"], ... )`; the preset intentionally covers both non-weapon equipment and weapons. Shared bag filtering is Site-10, rule-AND/rules-OR, dbID-deduped, protect-list-first, weapon-protected by default unless explicitly enabled, and degrades to weapon-ID-only behavior when non-weapon metadata is missing. Discard sends internal packet command 100005 action 4 (`4:<dbID>`) and removes the full stack; pacing is 1 second per account with stop-aware early termination and lower-level per-HWND send locks. `DAILY_DISCARD_POLL` exists but its numeric value remains UNKNOWN. Packaged runtime logs contain 22,734 generic action=4 records but no Daily/K08-correlated discard trace.

K09 closes the Trừng Ác static handoff by integrating K03-K08 into one lifecycle/failure matrix. It distinguishes control stops, terminal-current-account conditions, current-cycle skips, next-cycle recoveries, fail-soft/log-only paths, and recoverable death/disconnect interrupts. The two orchestration modes remain separate: activity-wide `_punish_run_worker` with `_punish_cancel` and start-time selection/PID snapshot versus per-row `_punish_single_worker` with row Event + generation guard. No blocking contradiction was found. Two apparent conflicts were resolved as layered state rather than contradictions: UI combat-duration seed 15 versus `_load_config` missing-key fallback `"5"`, and B08 current recovery-checkbox state versus missing-key fallbacks. All top-level Trừng Ác handlers in K01 are now accounted for; `_punish_target_fail` is tracking state and `_punish_monitor_stops` is nested recovery logic. `_wait_movement_stopped` remains explicitly outside the Trừng Ác flow because its recovered Daily call is in Tàng Bảo Đồ. Trừng Ác is therefore static-handoff-complete, while end-to-end runtime parity still requires a live Windows/game environment.

K10 opens the Tàng Bảo Đồ branch at the top-level shell only. It locks the visible/config surface (tomb duration 30, post-dig HP<30 heal, treatment-map selector, reconnect, respawn), exact missing-key fallbacks, and the four treatment-map coordinates. Apply-all is configuration-only: it sets every current row activity to `Tàng bảo đồ`. The activity-wide path is `_treasure_start_worker -> _treasure_map_toggle -> _treasure_map_run_worker`; the batch worker owns `tomb_dur`, `selected`, `selected_pids`, `loop_idx`, live/still-active filtering, halt/respawn state and child threads. Exact no-selection/no-live/all-stopped logs plus `[TÀNG BẢO ĐỒ] Lần ...` prove an open-ended batch loop with no user repeat-count config. The K02 row/bottom coordinator remains a separate `_treasure_single_worker` path with row generation identity, `respawn_event`, reconnect/cache-ready recovery surfaces and direct `_treasure_map_exec_sequence` call. K10 also locks only the top-level reconnect/death shell and the exact idle reset tuple `Tàng bảo đồ / RoyalBlue / normal`; treasure item/bag/mount/map96/combat/heal internals are deferred to K11+.

K11 locks the Treasure activation slice inside `_treasure_map_exec_sequence`. The mount-prep stage reads `IsRiding`, skips if already mounted, checks `common.nguaActive`, and has an exact logged fallback click at (1306,340). The bag stage uses the `tuido.active` readiness pixel and a fixed bag-preparation surface. The current treasure recognizer is explicitly `find_multipixel("tuido","tangBaoDo_multi")` using region (702,163)-(1132,517), offset (20,30), base RGB (2,30,35), offset RGB (228,215,170), timeout 5 and tolerance 1; legacy pixel keys are not the active Daily call. Successful detection is clicked through the shared DLL-sync/PostMessage `mouse.click_at` background stack. First not-found and second not-found are both terminal for the affected Treasure account. Between the two item checkpoints Daily calls `_wait_movement_stopped(stop_check, skip_set)` with no `by_memory` override, so this call uses the MovementDetector 10-pixel branch. After the second successful checkpoint, control enters the MapID/post-activation branch; map96/tomb combat is K12.

K12 locks the post-activation map96/tomb branch. `_treasure_map_exec_sequence` has a direct-helper default `tomb_dur=5`, while the normal K10 UI/config worker layer is 30 seconds and passes its configured `tomb_dur`; these are distinct layers rather than a contradiction. Exact branch text is `MapID=96 (huyệt mộ) → đánh <tomb_dur>` with state `Đánh trong mộ`. Two fixed click surfaces `(1135,124)` and `(955,123)` belong to the tomb-combat block, but their button meanings/order remain explicit UNKNOWN. Treasure duration is a per-tomb time in seconds, not a repeat count, but unlike K06 no `_t_end`/monotonic timer is recovered, so the timing primitive is not copied from Trừng Ác. The same branch contains exact move-to-map96/tile(50,16) semantics through `move_character` values 1600/512, followed by an explicit `common.active` wait and a post-wait MapID outcome. Non-96 logs `không phải huyệt mộ, bỏ qua` and is not an account-terminal stop. The immediate next boundary is Treasure final HP/heal checking; heal internals are deferred to K13.

K13 locks Treasure healing and recovery. `_treasure_heal` is selected-map driven rather than hardwired to Tô Châu: it requires a configured heal map, resolves coordinates from `TREASURE_HEAL_COORDS`, resolves the map ID dynamically through `MAP_LIST`, moves with the shared movement helper, and fails cleanly for missing selection/coordinates/map ID or movement failure. Its compact move surface passes `wait_for_arrival/stop_check` only, so the shared default tolerance 48 remains the effective default; no Treasure-specific fixed treatment click or `_punish_heal`-style reinjection surface is recovered. Start-of-cycle heal failure skips only the current cycle, while final-heal failure is fail-soft/log-only. `_treasure_map_disconnect_monitor` has a thin event-adapter local model (`halt/respawn_event/stop_event/ev/real_set`) rather than a second full pixel/memory detector; strong static evidence supports reuse of the existing Daily detector layer while preserving adapter micro-order as UNKNOWN. Treasure activity recovery has exact disconnect-wait/OK/timeout messages but no independently bound timeout number, so Trừng Ác's 60s value is not copied. The single-worker owns Reader-cache invalidation and `wait_memory_ready` recovery surfaces, and Treasure reuses the shared death/Map87 `respawn_event` model; exact reconnect overrides, monitor thread ordering and simultaneous death/disconnect priority remain UNKNOWN.

K14 locks Treasure failure and teardown lifecycle without reopening K10-K13 internals. DailyTab owns `_treasure_map_skipped` beside the Treasure running/cancel/button state. The two exact `tangBaoDo_multi not found` branches remain terminal-current-Treasure-account conditions, while start-heal failure is current-cycle-only, non-96 is a nonterminal tomb-outcome skip, and final-heal failure is fail-soft. Strong static evidence from the Treasure skip-state field, the `skip_set` movement-wait surface, and activity `still_active` filtering supports persistent exclusion of terminally skipped HWNDs during the active batch; exact add/discard/clear source statements remain UNKNOWN. The shared stop diagnostic distinguishes Treasure batch cancel, disconnect halt, row stop Event, generation change, window/PID invalidation and Địa-phủ respawn. Bottom all-account stop still signals `_farming_acc=False` + row `_stop_event`; singleton `_daily_all_monitor` waits for all row sessions to end, calls both Daily reset helpers, and then performs the global UI reset. Treasure's exact idle tuple remains `Tàng bảo đồ / RoyalBlue / normal`; teardown statement order is still explicit UNKNOWN.

K15 closes the Tàng Bảo Đồ static handoff by integrating K10-K14 and auditing every Treasure-related top-level callable in K01. No callable remains uncovered. Activity-wide `_treasure_map_run_worker` and per-row `_treasure_single_worker` remain separate ownership models. The integrated cycle preserves respawn-event reentry, optional low-HP treatment, mount/bag preparation, two-stage `tangBaoDo_multi` activation, MovementDetector-based movement stop, the map96/tomb outcome region, optional final treatment, and cycle-tail return. The production duration layer is 30s while the direct exec-helper fallback is 5s; this is a resolved layering distinction, not a contradiction. First/second treasure-item not-found are terminal-current-account, start-heal failure is current-cycle-only, non-96 is a nonterminal tomb-outcome skip, final-heal failure is fail-soft, successful reconnect/death are recoverable, and reconnect timeout is terminal for the affected recovery path. No blocking contradiction was found across K10-K14, no correct artifact required rewriting, and Treasure is now static-handoff-complete while end-to-end runtime parity remains environment-required.

K16 closes the shared Daily static integration layer. It confirms the 5-second roster refresh, HWND+PID anti-reuse identity, row Event+generation stale-worker guard, Tk `after(0)` state marshalling, shared injection, manual all-account `Tới bổ đầu`/`Trị liệu`, bottom Bắt đầu/Dừng lại coordinator, singleton `_daily_all_monitor`, StartTab synchronization, and Daily config load/save persistence. The remaining shared top-level gaps from K01 (`_validate_repeat`, injection helpers, manual movement/heal helpers, and config/destroy methods) are now accounted for. Row activity/PID/session state remains transient and is not persisted. Activity-wide Trừng Ác/Treasure ownership remains separate from row `_farming_acc/_stop_event/_gen` ownership; no unified owner mutex or independently-bound same-HWND mutual-exclusion guard was recovered, so that concurrency boundary is reserved for K17 runtime parity rather than guessed. No blocking contradiction was found across K02/K09/K15.

K17 closes Phase K at the static-research level. The original archive, inner EXE and packaged Daily log were revalidated; the packaged log still has no correlated Daily lifecycle trace, so it is treated only as negative evidence. A 20-case runtime/parity matrix records every remaining environment-only validation point as `NOT_EXECUTABLE_HERE` where live Windows/game access is required. No blocking contradiction remains across the Trừng Ác, Tàng Bảo Đồ and shared Daily handoffs, and no Daily top-level callable remains unaccounted for. Phase K therefore advances with live runtime parity explicitly deferred rather than falsely marked PASS.

## Phase K gate
**STATIC_RESEARCH_CLOSED / LIVE_RUNTIME_PARITY_DEFERRED**

## Phase L — Dồn
- L01 — VERIFIED_ACTIVE_DONVANG_AUTHORITY_CAPTURED_VISIBLE_SURFACE_127_HANDLER_INVENTORY_AND_DEPENDENCY_BOUNDARY
- L02 — VERIFIED_DON_RETURN_TRIGGER_SHORTCUT_WALK_FALLBACK_AND_HANDOFF_BOUNDARY
- L03 — NEXT

L01 locks `donvang_tab.py` / `DonVangTab` as the active Dồn authority. The exact Nuitka `.donvang_tab` module has size field **65,260 bytes** and count field **1,813**, and **127** direct top-level `DonVangTab` methods are inventoried. `TLMMainApp` constructs the tab under visible label `Dồn`, while StartTab exposes `Dồn vàng / Tới nơi nhận / Tới chỗ bán / Tới nơi train / Cấu hình`. The visible surface includes Về thành conditions/priorities, Train/death/disconnect/unstuck/pickup/filter/heal controls, saved coordinates, receiver rows, a shared Dồn coordinate, per-account move/Dồn/sell controls, and all-account actions. Dồn is current/wired rather than dormant; dedicated-tab visibility is permission-controlled, with the captured run showing it visible while the exact permission state remains unknown. Direct dependency boundaries are frozen, and weak emulator/farm-tab references are not promoted to active runtime imports.

L02 locks the Dồn return mechanism without consuming later return-priority/inventory/receiver tasks. The farm cycle has exact `cycle` and `full_bag_timer` return modes; cycle defaults to 30 minutes, while full-bag mode checks memory bag state, filters before returning, stays at farm if filtering frees space, and continues toward Dồn only if still full. Donor accounts substitute the normal return-to-town step with a Dồn callback. `_resolve_truyen_back` selects a map-specific `back` route from current MapID (farm preset fallback on memory-read failure), executes the serialized shortcut, invalidates Reader cache and performs fresh exit verification; no route uses normal movement, while failed verification aborts on stop or walks to the destination otherwise. `_run_farm_exit` then finishes the receiver/Dồn leg by normal horse movement with no phù. The normal sell path remains separate and passes `_get_nav_priority()` into `move_character` as `home_priority`; exact priority ordering is intentionally deferred to L03. Runtime parity remains environment-required.

## Phase L current
L03 — Dồn return priority audit.
