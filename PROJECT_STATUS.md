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
- K04 — NEXT

K01 locks `.daily_tab` / `daily_tab.py` / `DailyTab` as the active Daily authority, verifies the explicit Trừng Ác versus Tàng Bảo Đồ UI split, freezes the shared account-row/global-control surface, records the exact 70-member top-level callable inventory, and separates direct Daily module references from weaker non-import emulator edges.

K02 locks the five-second incremental roster refresh, HWND+PID anti-reuse identity, create/update/stale-row lifecycle, 30ms scroll debounce, permission-gated row controls, exact state styles, Tk after(0) state marshalling, generation-protected per-row stop semantics, per-row activity dispatch, all-account Bắt đầu/Dừng lại coordinator, singleton Daily monitor and transient row-session persistence boundary.

K03 locks the clean Trừng Ác duration/move/hotkey configuration, old/new teleport-config compatibility boundary, Apply-all selection semantics, distinct activity-batch versus per-row worker ownership, exact activity-level button states, selected/PID start snapshot, per-loop live/active filtering, open-ended iteration semantics, and separate batch-cancel versus row Event/generation stop identities.

## Phase K current
K04 — Trừng Ác NPC return / quest acquisition / 30-of-30 / stuck-quest cancellation audit.
