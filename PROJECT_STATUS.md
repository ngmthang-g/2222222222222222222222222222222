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
- L03 — VERIFIED_DON_RETURN_PRIORITY_DEFAULT_DEDUP_DISABLED_SLOT_AND_SELL_ONLY_HOME_PRIORITY
- L04 — VERIFIED_DON_SITE10_98_100_FULL_BAG_THRESHOLD_TWO_MODE_FILTER_RECHECK_AND_HIDDEN_PICKITEM
- L05 — VERIFIED_DON_SHARED_COORD_ROLE_SWITCHED_SELECTOR_BUILTIN_MANUAL_PERSISTENCE_AND_STRICT_STALE_SKIP
- L06 — VERIFIED_MULTI_RECEIVER_REGISTRY_PER_RECEIVER_LOCK_LOWEST_SPEED_SELECTION_BACKGROUND_TRADE_WATCH
- L07 — VERIFIED_START_TIME_ROLE_SPLIT_RECV_CYCLE_VS_DONOR_FARM_CYCLE_GEN_GUARDED_COOPERATIVE_STOP_AND_NO_DYNAMIC_ROLE_MORPH
- L08 — VERIFIED_4S_MAP87_HP0_LATCHED_RESPAWN_SHARED_HEAL_ROUTE_AND_2S_STOP_ON_DISCONNECT_3STRIKE_NO_RECONNECT
- L09 — VERIFIED_CURRENT_THREE_QUICK_MOVE_ACTIONS_ROLE_FILTERED_TARGETS_STARTTAB_PARITY_AND_LEGACY_BULK_HELPERS
- L10 — VERIFIED_DON_RECONSTRUCTION_CONTRACT_PARITY_MATRIX_CONTRADICTION_RESOLUTION_AND_STAGE_S_ACCEPTANCE_GATE

L01 locks `donvang_tab.py` / `DonVangTab` as the active Dồn authority. The exact Nuitka `.donvang_tab` module has size field **65,260 bytes** and count field **1,813**, and **127** direct top-level `DonVangTab` methods are inventoried. `TLMMainApp` constructs the tab under visible label `Dồn`, while StartTab exposes `Dồn vàng / Tới nơi nhận / Tới chỗ bán / Tới nơi train / Cấu hình`. The visible surface includes Về thành conditions/priorities, Train/death/disconnect/unstuck/pickup/filter/heal controls, saved coordinates, receiver rows, a shared Dồn coordinate, per-account move/Dồn/sell controls, and all-account actions. Dồn is current/wired rather than dormant; dedicated-tab visibility is permission-controlled, with the captured run showing it visible while the exact permission state remains unknown. Direct dependency boundaries are frozen, and weak emulator/farm-tab references are not promoted to active runtime imports.

L02 locks the Dồn return mechanism without consuming later return-priority/inventory/receiver tasks. The farm cycle has exact `cycle` and `full_bag_timer` return modes; cycle defaults to 30 minutes, while full-bag mode checks memory bag state, filters before returning, stays at farm if filtering frees space, and continues toward Dồn only if still full. Donor accounts substitute the normal return-to-town step with a Dồn callback. `_resolve_truyen_back` selects a map-specific `back` route from current MapID (farm preset fallback on memory-read failure), executes the serialized shortcut, invalidates Reader cache and performs fresh exit verification; no route uses normal movement, while failed verification aborts on stop or walks to the destination otherwise. `_run_farm_exit` then finishes the receiver/Dồn leg by normal horse movement with no phù. The normal sell path remains separate and passes `_get_nav_priority()` into `move_character` as `home_priority`; exact priority ordering is intentionally deferred to L03. Runtime parity remains environment-required.

L03 locks the exact Dồn return-priority surface: `NAV_OPTIONS = ["", "Phù 1", "Phù 2", "Phù 3", "Ngựa"]`, defaults `Phù 1 → Phù 2 → Phù 3 → Ngựa`, four readonly comboboxes, and an intentional blank/disabled slot. `_on_nav_priority_changed` recomputes available choices from already-used values, so normal UI selection prevents new duplicate nonblank priorities. Persistence is `[DonVang] nav_priority_1..4`. `_get_nav_priority` adapts the ordered UI list into `move_character(home_priority=...)`; the shared movement primitive treats Phù entries as ordered return-home hotkey attempts and Ngựa as the ordinary movement fallback. Within Dồn the only production `home_priority` consumer is `_sell_acc`; L02's `_run_farm_exit` Dồn/receiver final leg remains normal horse movement with no phù. Legacy/hand-edited already-duplicated config normalization and live attempt timing remain runtime/config-fixture unknowns.

L04 locks Dồn inventory/full-bag behavior. Bag count is occupied Site-10 slots. Dồn keep policy is intentionally only two modes: `Tất cả -> []` and `Chỉ vũ khí -> [discard_nonweapon]`; there is no Dồn `Không` mode and no `discard_weapons` selection. `_pickup_no_cankhon` is separate, waits 5 seconds and writes hidden `PICKITEM.IsOn=True`. Exact full-bag threshold policy is **98 occupied slots when hidden pickup is ON, 100 when OFF**. The nearby `(3,)` belongs to nested `stop_bag_check` as an exact callback default, not a slot threshold; its parameter/micro-order remains explicit UNKNOWN. Full detection runs `_filter_before_don`, then re-reads occupied slots: below threshold stays at farm, still full continues to the already-proven Dồn boundary. Shared `bag_filter.discard_for_activity(activity="train")` retains 1.0s pacing, OR rule merge, dbID dedupe and action-4/opcode-100005 whole-stack discard. Live end-to-end parity remains environment-required.

L05 locks Dồn coordinate architecture: saved coordinate rows are name/map/X/Y with Train apply + delete; exact Dồn and sell built-ins are frozen; one shared Tọa độ dồn is used across receiver rows; the account coordinate selector switches by receiver/donor role; and [DonVang] coordinate persistence uses coord_<n>=preset_name|map_id|x|y with stale/unknown maps skipped.

L06 locks the multi-receiver model. Receiver rows are account-only rows sharing the single L05 Dồn coordinate. don_logic owns independent per-receiver registry state (ready/donated/aborted/donor_hwnd) plus one lock per receiver. recv_cycle is sell -> return -> ready -> wait donated/abort/donor-death -> repeat. Automatic Dồn chooses only ready receivers, excludes the donor, requires valid coordinates, prioritizes the receiver with the lowest current gold/hour and randomizes equal-speed ties. Readiness is rechecked after acquiring the receiver lock; busy receivers are skipped and different receivers can be served in parallel while one receiver is serialized to one donor. Each receiver has one persistent background trade-invite watcher that accepts managed-account names, rejects unknown names, and yields while real Dồn owns that receiver. Legacy/per-row receiver-coordinate conflict precedence remains explicit UNKNOWN.

L07 locks Dồn full-session integration. Both roles share _farming/_farming_acc/_farm_threads/_stopping_play/row._gen ownership, but the worker is chosen at start: receiver -> _run_receiver/recv_cycle; donor -> _farm_cycle(don_callback=_don_cb). _farm_acc is only the StartAutoFight Train memory primitive, not the full FSM. Receiver cycle is sell -> return -> ready -> receive -> repeat; donor Dồn substitutes the return-town leg and then rejoins the Train leg. Stop/drain is cooperative and generation-guarded. Receiver combobox changes while running restyle/reorder only and do not hot-swap the active worker; a full stop/start is required for the newly selected role to receive the corresponding worker. Runtime timing remains environment-required.

L08 locks Dồn death/treatment/disconnect semantics. Both roles run a 4s death monitor: MapID 87 raises a latched respawn_event and real numeric HP==0 performs one client click at (792,441) per zero-HP episode. Optional post-death treatment reuses TRAIN_HEAL_COORDS plus the exact two-point ×4 treatment interaction. Crucially, Dồn's legacy auto_reconnect_var / auto_reconnect config no longer means reconnect: the visible control is Dừng khi mất kết nối mạng. The 2s watchdog uses connected-memory as a veto plus both disconnect pixels for 3 consecutive ticks (~6s), then halts/stops the account. Dồn contains no reconnect_ok/click/common.active retry loop; its own embedded documentation says KHÔNG tự kết nối lại — user bấm Start để chạy lại. Live timing remains environment-required.

L09 locks the current Dồn all-account command surface. The dedicated tab exposes exactly three quick movement actions: Tới nơi nhận -> _move_all_recv, Tới chỗ bán -> _move_sell_acc, Tới nơi train -> _move_all; each is dispatched off the Tk main thread, while the separate Bắt đầu button remains _toggle_farm. _checked_rows currently means all listed nonreceiver accounts, despite legacy “được tick” wording. Tới nơi nhận is role-aware and reuses L06 manual receiver selection/fallback; Tới chỗ bán moves receivers only; Tới nơi train moves nonreceiver donors to Train presets in parallel. Real _stop_all/_farm_all/_sell_all helpers remain in the class but no current visible Dồn/StartTab binding was recovered; _farm_all is not equivalent to the full lifecycle and _sell_all is not the visible Tới chỗ bán movement button. StartTab quick controls delegate to the same three backends and its Dồn vàng toggle delegates to _toggle_farm.

L10 closes Dồn static research by consolidating L01-L09 into one normative reconstruction contract. The parity matrix separates STATIC_VERIFIED, RUNTIME_REQUIRED, EXPLICIT_UNKNOWN and NOT_CURRENTLY_WIRED behavior. Cross-task compatibility traps are resolved without guessing: auto_reconnect is a legacy key for current stop-on-disconnect behavior; receiver rows share one Dồn coordinate; the current account coordinate selector is role-switched; _checked_rows means all listed nonreceivers; Bắt đầu is _toggle_farm rather than _farm_all; Tới chỗ bán is movement-only rather than _sell_all; and the manual receiver fallback is not used by automatic no-ready Dồn. A 103-item minimum Stage-S acceptance suite now defines separate static-parity and live-parity gates. Remaining migration/timing/race edges stay explicit UNKNOWN or runtime-required.

## Phase L gate
**STATIC_RESEARCH_CLOSED / LIVE_RUNTIME_PARITY_DEFERRED**

## Phase M — Rao
- M01 — VERIFIED_ACTIVE_RAO_AUTHORITY_VISIBLE_SURFACE_40_METHOD_INVENTORY_PERMISSION_PERSISTENCE_AND_DEPENDENCY_BOUNDARY
- M02 — VERIFIED_NAME_KEYED_RAO_DEFINITIONS_JSON_CONTENT_CHANNEL_SEC_LIVE_TRACE_AND_STALE_NAME_FAIL_CLOSED
- M03 — VERIFIED_EXACT_7_CHANNEL_NAME_TO_ID_MAP_DEFAULT_WORLD8_NAME_PERSISTENCE_AND_SEND_CHAT_NUMERIC_ID
- M04 — VERIFIED_30S_DEFAULT_0_60_NORMALIZATION_POSITIVE_1_60_RUNNABLE_SEND_THEN_INTERRUPTIBLE_WAIT_LIVE_NEXT_LOOP_REFRESH
- M05 — VERIFIED_HWND_PID_RUNTIME_IDENTITY_NAME_KEYED_4_SLOT_JSON_ASSIGNMENTS_STALE_CLEAR_REAPPEAR_RESTORE_AND_NEXT_CYCLE_LIVE_EDIT
- M06 — STATIC_WORKER_CONTRACT_AUDITED_LIVE_PARITY_DEFERRED
- M07 — STATIC_RESEARCH_CLOSED_LIVE_RUNTIME_PARITY_DEFERRED

M01 locks `rao_tab.py / RaoTab` as the active Rao authority. The exact serialized `.rao_tab` header is at `0x2bd7850`, size **11,774 bytes**, count **582**, with **40** direct top-level RaoTab methods inventoried. TLMMainApp creates the permission-controlled visible tab `Rao / rao_tab` and owns `_set_rao_tab_visible`; the supplied capture shows it visible, while the exact license-plan value remains unknown. The dedicated UI surface is frozen as Cấu hình rao tự động with Tên / Nội dung rao / Kênh / Lặp (s) / Xóa, + Thêm rao, Danh sách tài khoản with Nhân vật / Nội dung rao, four Rao-selection slots per account row, per-account ▶ / Đã dừng surfaces, and the bottom Bắt đầu action. Current channel labels are Thế giới, Bang hội, Môn phái, Tổ đội, Liên minh, Quân đoàn, Lân cận, with statically recovered default channel Thế giới; mapping semantics remain for M03. Persistence boundary is [Rao] with rao_ and acc_ families through shared start_tab settings helpers. No Rao-specific StartTab quick action was recovered: the exact serialized start_tab block contains zero case-insensitive Rao/rao strings, despite rao_tab reusing start_tab helper symbols. Deep message, channel, interval, account-assignment and worker behavior remain deferred.

M02 locks Rao message identity/storage. Each live definition owns name_var/msg_var/chan_var/sec_var and the trimmed visible Rao name is the account-facing identity; no persistent row UUID is recovered. Auto naming chooses the smallest unused Rao N. Row writes trigger immediate message-family save plus account-option refresh; deletion removes the row and rewrites the Rao definition family. Current persistence is name-keyed under [Rao] as rao_<trimmed display name>=JSON with content/channel/sec and ensure_ascii=False; account acc_ keys are a separate family that must survive Rao-definition saves. Load sorts rao_ keys, derives the display name from the key suffix, json.loads the payload and recreates rows through _add_rao_row(name/content/seconds/channel). No manual duplicate-name validation is recovered, so duplicate display names are not stable independent persistence identities. Renamed/deleted old names become invalid references; exact immediate account StringVar clear-vs-preserve behavior remains deferred to M05.

M03 locks Rao channel semantics. Exact current mapping is Thế giới→8, Bang hội→2, Môn phái→6, Tổ đội→4, Liên minh→3, Quân đoàn→11, Lân cận→5; RAO_DEFAULT_CHANNEL is Thế giới/8. The mapping independently matches the shared memory_items.CHAT_CHANNELS subset, while Đặc biệt/9, Nói thầm/7 and Liên máy chủ/10 remain intentionally unavailable in Rao. M02's persisted channel field stores the display-name string; _resolve_rao derives and returns the numeric channel_id at runtime. memory_items.send_chat exact argument surface is (hwnd, channel_id, content), and the shared send path builds CMD_CLIENT_CHAT with Base64 content and numeric Channel. A stale non-empty persisted channel's exact load-time UI normalization remains unknown, but only current RAO_CHANNELS members may produce a sendable ID.

M04 locks Rao interval semantics. The UI uses sec_var with digits-only/blank-edit validation. Current load/default fallback is 30 seconds; the exact load normalization cluster binds min + integer 0 + integer 60 + sec + TypeError/ValueError, yielding a normalized 0..60-second storage/UI domain, while blank/zero is not runnable and normal active intervals are positive 1..60 seconds. The exact _slot_loop documentation fixes send-before-wait behavior: each valid slot sends immediately, then performs an interruptible _stop_event.wait around its resolved interval, then repeats. Up to four slots per account have independent timers. A live interval edit does not reschedule the already-running wait; the next cycle re-resolves the Rao definition and uses the edited value without restarting the slot. No separate fast retry/backoff path was recovered for normal send/no-echo failures.

M05 locks Rao account assignment/persistence. Live account rows are HWND/PID-bound, while persisted assignments are keyed by real sanitized character name as [Rao] acc_<name>; temporary Window ... fallback names are not normal restore identities. Each account owns exactly four ordered Rao slots saved as one JSON list of four Rao display-name strings. load_acc_config restores only Rao names that still exist. Rename/delete rebuilds every account combobox and clears stale selected names from the live UI; there is no old-name→new-name alias/UUID propagation. _has_real_name/_rao_touched protect delayed RoleName restore from overwriting user edits. Same HWND with a new PID recreates the runtime row; a disappeared/reappeared character can restore from the same name-keyed config. Duplicate real character names remain separate live HWND/PID rows but collide on the same persistent acc_<name> key, with exact collision winner left UNKNOWN. Changing a running slot's assigned Rao does not force restart; the next loop observes the new selection.

## Phase M gate
**STATIC_RESEARCH_CLOSED / LIVE_RUNTIME_PARITY_DEFERRED** — M01–M07 complete. N01 Tối ưu active authority is NEXT.


M06 static audit closed: original EXE's four independent Rao slot workers, per-account/bulk entry points, stop semantics, generation/stop Event, Tk UI-state marshal, permission guard and HWND/PID liveness gates are documented. See docs/rao/M06_WORKER_LIFECYCLE_FLOW.md and docs/rao/M06_STATIC_EVIDENCE.tsv. This is static analysis, not verified original-vs-reconstructed runtime parity; no application source or build workflow exists yet.


## Phase M07 — Rao parity handoff
- Main authority ZIP: `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; inner EXE: `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- M07 integrates frozen M01–M06; exact UI/config/channel/timing/account/worker contracts preserved with explicit unknowns and evidence tiers.
- 70 acceptance cases in `docs/rao/M07_RAO_PARITY_MATRIX.tsv`: 30 STATIC, 5 VISUAL, 28 WINDOWS, 7 RESEARCH. None has run against a reconstructed product.
- Documents: `docs/rao/M07_RECONSTRUCTION_CONTRACT.md`, `docs/rao/M07_MODEL.json`, `docs/tasks/M07.md`.
- Stage-S application source absent, Stage-T build workflow absent; EXE product status NOT_APPLICABLE_YET, never claimed PASS.
- **NEXT** N01 — Tối ưu active module/UI authority audit; EXE-first then screenshot.


## Phase N — Tối ưu
- N01 — **STATIC_AUTHORITY_AND_UI_SURFACE_AUDITED / LIVE_PARITY_DEFERRED**. Active original `toiuu_tab.ToiuuTab` (0x2c01fb5; 22,485 bytes; 940 constants), frozen ZIP `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; EXE `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Separate high-CPU warning `CPUMonitor` is not Tối ưu graph. Original tabs show charts, N/A GPU fallback, detached monitor, per-account and bulk configurations. Selecting gray mode buttons is not native apply; actual DLL/TLMP send is separately documented.
- Permissions, HWND/PID, StartTab Theo dõi/Tối ưu synchronization, persistent monitor/running keys, TLMP watch/recovery intent are static surfaces only. Live runtime parity NOT_RUN.
- Files: `docs/toiuu/N01_AUTHORITY_UI_FLOW.md`, `docs/toiuu/N01_AUTHORITY_MODEL.json`, `docs/toiuu/N01_STATIC_EVIDENCE.tsv`, `docs/tasks/N01.md`.
- Stage-S product source and Stage-T build workflow absent; build NOT_APPLICABLE_YET.
- **NEXT N02 — CPU monitoring sample/history/redraw audit**, EXE-first; leave GPU N03.


## N02 — Tối ưu CPU sampling/history/redraw
- **STATIC_CPU_SAMPLE_HISTORY_REDRAW_AUDITED_WITH_EXPLICIT_TIMER_UNCERTAINTY / LIVE_RUNTIME_DEFERRED** (frozen EXE `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`).
- Tab chart uses guarded psutil CPU sampling; `deque(maxlen=GRAPH_HIST)`, per-series `_cpu_hist`; main-thread `_schedule_redraw/_redraw_graphs` and Canvas lines/grid.
- Original doc “Sample 1s/lần”; exact EXE also has `GRAPH_TICK_MS`, `sleep`, numeric tagged 750/64 and double 1000.0. These numerical mappings are not decompiled; exact tick/history remain UNKNOWN, not invented.
- `cpu_monitor.CPUMonitor` psutil high-CPU warning is a separate service, not the chart. Reused B11 screenshot CPU 15%/blue plot only for static visual crosscheck.
- Artifacts: `docs/toiuu/N02_CPU_SAMPLE_REDRAW_FLOW.md`, `docs/toiuu/N02_MODEL.json`, `docs/toiuu/N02_STATIC_EVIDENCE.tsv`, `docs/tasks/N02.md`.
- Stage-S reconstructed app/build workflow absent; Windows functional parity NOT_RUN.
- **NEXT N03 — GPU collection / nvidia-smi failure and chart integration audit.**


## N03 — GPU reader/failure/graph integration
- STATIC_GPU_READER_FAILURE_INTERFACE_AUDITED / LIVE_PARITY_DEFERRED; frozen original EXE 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22.
- Exact nvidia-smi utilization/CSV args, check_output/timeout/CREATE_NO_WINDOW, utf-8 parsing vocabulary and embedded None-if-unreadable doc; UI _gpu_avail/_gpu_hist, orange chart and GPU N/A status documented.
- Exact timeout and multi-GPU parsing plus None history remain UNKNOWN. No live GPU/runtime test or product build.
- New docs/toiuu/N03_GPU_COLLECTION_FLOW.md, N03_MODEL.json, N03_STATIC_EVIDENCE.tsv and docs/tasks/N03.md; source app/CI absent.
- **NEXT N04 — detached CPU/GPU monitor lifecycle/layout/persistence audit.**

## N04 — Tối ưu detached monitor lifecycle
- **STATIC_DETACHED_MONITOR_LIFECYCLE_AND_UI_AUDITED / LIVE_PARITY_DEFERRED**. Original frozen EXE `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22` inspected read-only.
- Six active detached monitor methods recovered; main `Tách theo dõi` toggles real `Tk.Toplevel` titled `CPU / GPU` with two bar columns, close action, topmost/geometry/WM_DELETE_WINDOW surfaces. Embedded doc specifies position next to left side of GUI, 768 px nominal height; exact width/placement math remains UNKNOWN.
- Monitor persisted under `[Settings] toiuu_monitor_open`; scheduled restart restoration and UI repaint path recorded. B11 screenshot has button but not a detached panel; no false visual parity.
- Files: `docs/toiuu/N04_DETACHED_MONITOR_FLOW.md`, `docs/toiuu/N04_MODEL.json`, `docs/toiuu/N04_STATIC_EVIDENCE.tsv`, `docs/tasks/N04.md`. 71 evidence items, 16 future tests all NOT_RUN.
- Application source/build workflow still absent. **NEXT N05 — graphics-mode mapping, per-account configuration and selection-versus-application audit.**


## N05 — Mode mapping and select/apply boundary
- STATIC_MODE_ACCOUNT_CONFIGURATION_AND_SELECTION_APPLY_BOUNDARY_AUDITED / LIVE_PARITY_DEFERRED; frozen original EXE 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22.
- Không=skip; Thấp vừa/medium=1, Cực thấp/low=2, Cực đại/max=3. Original exact docs establish all-account and per-row gray mode controls select COMBOBOX ONLY; bottom Bắt đầu/row play owns actual perf.
- toiuu_cfg_<sanitized RoleName> persisted per character; _cfg_touched, _mode_key and trace-save. Exact INI section, default priority and duplicate-name collision UNKNOWN.
- N06 owns native dll_injector/TLMP_RESTORE/expected_pid details, preserving licensing. 52 evidence records, 18 planned tests all NOT_RUN.
- Files docs/toiuu/N05_MODE_CONFIG_SELECTION_FLOW.md, docs/toiuu/N05_MODEL.json, docs/toiuu/N05_STATIC_EVIDENCE.tsv and docs/tasks/N05.md. Stage-S application/build remains absent.
- NEXT N06 — native TLMP command and PID-guarded send/restore audit.


## N06 — Native TLMP + bundled DLL
- STATIC_NATIVE_TLMP_AND_DLL_BOUNDARY_AUDITED_WITH_HISTORICAL_PERF_LOG / LIVE_PARITY_DEFERRED. Original EXE 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22 inspected read-only.
- Compiled dll_injector documents native WM_COPYDATA/TLMP PerfCmd and mode 0 normal, 1 medium, 2 low, 3 max, 4 restore, 5 ping. Combobox Không still skip. _send_perf_single expected_pid guard, _send_perf_all (ok_count,total), stage-down from max to low before TLMP_RESTORE documented.
- resources.dat is 39424-byte x64 PE DLL SHA256 1375240c85abb9c211c66d3e8157a6dbfbc5551aabec465375b68e5301e645d4, native handler/hook success unverified.
- Historical automove_log.txt 17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500 contains 71247 Perf lines (4134 pings etc). NOT a fresh live Windows test or tool UI proof.
- Single-account TODO logic string flagged as unknown, not marked complete. Detailed bulk/row concurrency will be N07.
- New docs/toiuu/N06_NATIVE_TLMP_DLL_FLOW.md, N06_MODEL.json, N06_STATIC_EVIDENCE.tsv and docs/tasks/N06.md (79 evidence records; 18 future tests NOT_RUN). Stage-S source/workflow absent.
- **NEXT N07 — per-account/all-account start-stop orchestration and UI-state audit.**


## N07 — Single/all-account start-stop and worker state audit
- STATIC_START_STOP_WORKER_STATE_AND_PID_BOUNDARY_AUDITED_WITH_TODO_UNCERTAINTY / LIVE_PARITY_DEFERRED. Frozen original EXE SHA 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22.
- Per-row ▶ invokes threaded _toggle_single_acc with _stop_event/_gen; original TODO logic literal means individual start is not proven complete, even though separate _send_perf_single and restore helpers exist. Bulk Bắt đầu invokes _start_all_accs with busy scan/eligible start, global stop and _all_monitor auto-reset surfaces.
- Background-tab lazy scan and targeted unresolved names are documented worker-only. _restore_targets differentiates selected mode and pre-tool-boot survivor; per-HWND PID guard required. Exact concurrency, TODO branch and state paint need Windows tests.
- 86 static evidence rows, 22 future tests NOT_RUN. Files docs/toiuu/N07_START_STOP_ORCHESTRATION_FLOW.md, docs/toiuu/N07_MODEL.json, docs/toiuu/N07_STATIC_EVIDENCE.tsv, docs/tasks/N07.md. Previous studies unchanged.
- Stage-S source and Stage-T build absent. **NEXT N08 — TLMP-5 ping/watch, Treo tick and Login recovery audit.**

## N08 — TLMP-5 ping watchdog and LoginTab hung recovery
- STATIC_WATCH_PING_AND_LOGIN_RECOVERY_INTERFACE_AUDITED_WITH_HISTORICAL_PING_LOG / LIVE_PARITY_DEFERRED.
- Exact original EXE method markers for _tick_watch_loop/_tick_watch_round/_recover_row; WATCH_INTERVAL/PING_WAIT/MAX_MISS and embedded two-consecutive-misses Treo tick doc. Watcher reads automove_log.txt pongs matching \[pid=(\d+)\] Perf: ping rather than treating send=True as game health.
- Packaged historical log 17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500 contains 4134 matching ping lines over 88 PIDs, but no [Toiuu markers; no live game watchdog/relogin run.
- LoginTab _close_single_account and _login_single_account original methods exist; _recover_row has explicit manual fallback when LoginTab absent, no PID row mapping or timeout. _auto_revive default and exact timing/guard remain unverified.
- 82 evidence records and 22 acceptance cases (0 run), in docs/toiuu/N08_WATCH_PING_RECOVERY_FLOW.md, N08_MODEL.json, N08_STATIC_EVIDENCE.tsv and docs/tasks/N08.md. No Stage-S rebuilt app source or workflow.
- NEXT N09 — persisted running set, old-game/old-tool session reconcile and safe restore/resume audit.

## Phase N09 — Tối ưu persisted running set and stale-game reconciliation
- **STATIC_STALE_RUNNING_PERSISTENCE_BOOT_GUARD_AND_PERMISSION_RECONCILE_AUDITED / LIVE_PARITY_DEFERRED**; exact original EXE `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22` audited read-only.
- Real running-session JSON `{name: mode_key}` stored under `toiuu_running`, distinct from selected `toiuu_cfg_` and auxiliary `toiuu_monitor_open`. `toiuu_was_running` detected but exact legacy role unverified.
- `psutil.Process.create_time`, `_boot_ts` and `_game_predates_boot` establish saved-name + living old-game condition before relabel red Dừng lại. New games after tool boot never qualify by name alone.
- `_reconcile_stale_worker` has scan incomplete retry 30s; no-permission try `/5` retry 60s; later safe restore to normal/start after definitive missing permission. Times from original status strings, not new runtime trace.
- `84` binary evidence/unknown records, 22 future acceptance cases all NOT_RUN. Artifacts `docs/toiuu/N09_STALE_RUNNING_RECONCILE_FLOW.md`, `docs/toiuu/N09_MODEL.json`, `docs/toiuu/N09_STATIC_EVIDENCE.tsv`, `docs/tasks/N09.md`.
- Stage-S source and Stage-T build workflow still absent. **NEXT N10 — Tối ưu reconstruction contract/parity handoff**, then Phase O.

## N10 / Phase N Tối ưu research handoff
- N01–N09 research consolidated without changing completed work. N10 gate PHASE_N_STATIC_RESEARCH_HANDOFF_COMPLETE / LIVE_PARITY_DEFERRED.
- New docs/toiuu/N10_RECONSTRUCTION_CONTRACT.md, N10_MODEL.json, N10_TOIUU_PARITY_MATRIX.tsv and docs/tasks/N10.md.
- 152 unique acceptance cases across N01 14, N02 12, N03 8, N04 16, N05 18, N06 18, N07 22, N08 22, N09 22. Gates {"STATIC":13,"VISUAL":9,"WINDOWS":122,"RESEARCH":8}. ALL case results NOT_EXECUTED_STAGE_S_NOT_STARTED.
- Native send semantics/permissions/row identity, selector-only gray buttons and Không skip, ping/old-session boundaries, N07 TODO and original evidence unknowns preserved.
- Stage-S product source and Stage-T build workflow absent; no runnable EXE or Windows parity. **NEXT O01 — memory/item subsystem authority audit.** Proxy development excluded.

## O01 — Memory/Item module authority and active cross-tab import edges
- **STATIC_MEMORY_ITEM_MODULE_AUTHORITY_AND_CROSS_TAB_WIRING_AUDITED / DEEP_LAYOUT_AND_LIVE_PARITY_DEFERRED**. Original ZIP c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd (1050 CRC clean) / inner EXE 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22 (47450112 bytes) inspected without execution.
- Exact 5 compiled modules: memory_reader (11804), memory_items (47850), bag_filter (5162), item_meta_data (1989514 embedded data), weapon_ids (27719 embedded set). Actual metadata/weapon entry count and numeric pointer layouts UNKNOWN.
- Reader uses WinAPI OpenProcess/ReadProcessMemory/GameAssembly and caches; inventory read_bag returns dbID/itemID/site/pos/qty, bag Site10 and metadata. bag_filter opt-in presets and weapon-protection/no-rule-no-packet; compiled import wiring with Farm/Phó bản/Daily/Đôn vàng/Debug/Train LSV confirmed.
- Artifacts docs/memory/O01_MODULE_AUTHORITY_AND_WIRING.md, docs/memory/O01_MODEL.json, docs/memory/O01_STATIC_EVIDENCE.tsv, docs/tasks/O01.md (77 evidence items). 15 acceptance requirements; live Windows NOT_RUN. No Stage-S product source or build workflow.
- **NEXT O02 — memory_reader process discovery/attach, GameAssembly base, pointer chains, cache/validation.** Stage N and Proxy lock preserved.

## O02 — Memory reader process/GameAssembly/chain validation
- STATIC_MEMORY_READER_PROCESS_GA_RVA_CHAIN_AND_VALIDATION_AUDITED / WINDOWS_PARITY_DEFERRED; frozen EXE 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22 examined read-only.
- Actual EXE documentation: GA+0x355B208 -> +0xB8/+0x88 RoleData; AutoFlag GA+0x356ED08/0x356E288 +0x2C; SessionData get_RoleData GA+0x6F4030 anchored RoleData+0x88 and collections ItemPacks+0x18 Monsters+0x20 NPCs+0x50.
- WinAPI module discovery/read, cache validation, VirtualQueryEx error states and close/elevation diagnostics audited. Exact PROCESS_RIGHTS/GA cache TTL/process predicate and Windows portability UNKNOWN. Original Reader contains writes/inject but none performed by O02.
- docs/memory/O02_READER_PROCESS_POINTER_FLOW.md, O02_MODEL.json, O02_STATIC_EVIDENCE.tsv and docs/tasks/O02.md (104 evidence records, 20 acceptance tests all NOT_RUN). No rebuilt product source/build workflow.
- NEXT O03 — memory_items bag Site10 and separate trade Site200 structure/error audit.

## O03 — Memory Items Bag Site 10 versus Trade Site 200
- STATIC_BAG_SITE10_SCHEMA_AND_TRADE_SITE200_BOUNDARY_AUDITED / LIVE_MEMORY_PARITY_DEFERRED (original inner EXE 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22 read only).
- `read_bag` tuple rows/info {dbID,itemID,site,pos,qty}; Reader unattached, Items null and genuine count=0 are different states. `get_bag` summarizes Site10 and enriches embedded metadata with slots/distinct/total_qty/non_bag/info; exact memory entry offsets/arithmetic unproven.
- Trade Site200 separately queries Lua `Game.GetItemsAtSite`: [] no items, None failure, count -1 error, PutItemTrade acknowledgment send-only; `get_bag_items_by_type` uses Lua Game.GetItemType on Site10. No live game requests sent.
- Artifacts docs/memory/O03_BAG_TRADE_READ_FLOW.md, O03_MODEL.json, O03_STATIC_EVIDENCE.tsv and docs/tasks/O03.md; 73 evidence rows, 20 planned tests NOT_RUN; reconstructed product source/build absent.
- NEXT O04 — embedded META/weapon ItemID data/classifier audit; no Proxy development.


## O04 — Complete embedded ItemID / weapon audit
- Frozen original EXE 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22 includes exactly 29983 META records; sources {"Equips":22776,"Items":5289,"Gems":1154,"Medicines":694,"PetEquips":70}; 12835 distinct Names and 4082 Icons. Exactly 5477 unique weapon ItemIDs from twelve types; all matched META Equips/allowed types, no missing/mismatches.
- Artifacts: docs/memory/O04_EMBEDDED_METADATA_AND_WEAPONS.md, O04_MODEL.json, O04_DATA_METRICS.json, O04_STATIC_EVIDENCE.tsv and docs/tasks/O04.md. 47 evidence entries / 20 NOT_RUN cases. No app code/build or live game test.
- NEXT O05 — bag_filter rules and safe destructive discard. Proxy excluded.


## O05 / Phase O memory/item research handoff
- Static bag_filter rules/presets and destructive item safeguards audited. Default no rules => no scan/packet; AND/OR, dbID dedupe, Site10 default, weapon-protection and protect list priority, dry_run and stop_check. Packet 100005 action 4:dbID may remove entire stack; no game actions performed.
- Decoded Phoban 204 Items+10 Medicines unique ItemID templates in O04 META, none weapons. Keep-mode none/weapons/all maps to 2/1/0 discard presets, default all safe.
- O05 docs/memory/O05_BAG_FILTER_SAFETY_FLOW.md, O05_MODEL.json, O05_STATIC_EVIDENCE.tsv, docs/tasks/O05.md; 61 evidence and 27 acceptance checks NOT_RUN. Stage-S source/Stage-T workflow absent. Phase O STATIC research complete, live parity deferred.
- **NEXT P01 — emulator module authority/active vs dormant audit.** Proxy excluded.

## Code/build audit and P01 original emulator conditional UI — 2026-10-08
- Full original GitHub code/tree audited: seven Python D01–D07 forensic scripts, A08 shell; **no Stage-S application source and no Stage-T Windows workflow**, product build **BLOCKED_SOURCE_MISSING**, Windows app tests NOT_RUN. Original SHA/CRC verified PASS, standalone O04 verifier tested and missing script restored in earlier one-file commit.
- docs/audit/CODE_BUILD_BASELINE_2026-10-08.md records precise code/source counts, blockers, no invented runtime bugs. No existing application code overwritten (none exists).
- P01 static EXE-first: Train LD registered but hidden/license-gated; Debug Android developer-only; seven compiled emulator modules referenced and asset JS verified. Emulator remote farm toggle ACK-only according to original doc, live emulator/RPC/HTTP NOT_RUN.
- P01 docs/emulator/P01_AUTHORITY_AND_DORMANCY.md, P01_MODEL.json, P01_STATIC_EVIDENCE.tsv and docs/tasks/P01.md: 33 evidence records and 18 future tests NOT_RUN. Stage N/O and Proxy excluded scope unchanged.
- NEXT_ACTION **P02 — AndroidReader/EmuManager ADB/Frida identity and connection lifecycle**. Build remains blocked pending Stage S/T.


## P02 — AndroidReader/EmuManager emulator identity and Frida lifecycle
- Original TLMTool EXE + Frida JS static authority checked first (same Gate-A/P01 hashes and ZIP CRC PASS). Compiled reader/manager API and connection stages confirmed: ADB serial, per-VM Frida server/session, ping/reload, RoleID targeted/blind scan, stale-character live name validation, poll_rows/force_discover and Site10 slot response.
- Device identities serial/aid/guest IPv4/hwid differentiated. Clone collision and UID key ambiguities explicitly UNKNOWN. Android ID cache documented 5min and device coordinate cache 30s; exact worker retry timing UNKNOWN.
- docs/emulator/P02_READER_MANAGER_CONNECTION_LIFECYCLE.md, P02_MODEL.json (25 deferred runtime cases), P02_STATIC_EVIDENCE.tsv (42 evidence items), docs/tasks/P02.md. Static CRC/hashes/JS syntax PASS; live Windows/LD/ADB/Frida NOT_RUN.
- No reconstructed app source, no Windows build workflow: BUILD_BLOCKED_SOURCE_MISSING. No Proxy work and original Gate-B UI contract unchanged.
- **NEXT_ACTION P03 — emu_input ADB event/capture, per-serial control/coordinates/errors static audit.**


## P03 — Original ADB input, screenshot and coordinate domain audit
- `emu_input` original compiled marker 0x293325f and 10 `AdbInput` API method symbols confirmed by direct original EXE. ADB subprocess, hidden console flag, shell `input`, `wm size`, `exec-out screencap -p` raw PNG and Pillow RGB/None error doc statically audited.
- PC reference 1366x768 conversion to actual Android device pixels is distinct from `DebugAndroidTab` Win32 LDPlayer client viewport mapping (default origin 0,30). Do not hardcode the LD 960x540 example. APK/device runtime and exact rounding/timeout UNKNOWN.
- Packaged original ZIP does not contain adb.exe; EXE references external LDPlayer adb.exe path and `LD_ADB`, precedence UNKNOWN. Clone-safe device selection and permission gates stay unchanged. **No UI invented from screenshots.**
- Artifacts docs/emulator/P03_INPUT_CAPTURE_COORDINATES.md, P03_MODEL.json, P03_STATIC_EVIDENCE.tsv, docs/tasks/P03.md; 49 evidence items, 26 planned runtime tests, 0 executed. Original hash+CRC PASS; no game/ADB/Frida/HTTP actions.
- **Product BUILD_BLOCKED_SOURCE_MISSING**: no rebuilt Stage-S app source or Stage-T Windows workflow in previous code/build audit; this task only added research docs. Proxy excluded.
- **NEXT_ACTION P04 — emu_chat chat-link UI route, settings calibration and memory destination verification, EXE first.**


## P04 — EmuChat original coordinate chat-link goto and memory-confirmed arrival
- Original EXE module 0x293100c includes pure-UI `@GOTO_m_x_y` chat-link sequence, calibrated `settings.ini [EmuChat]` ten x/y keys, `goto` returning (ok,msg), early arrival within 2 tiles, 30-second stuck threshold and global timeout status strings. Live movement and detailed branch/timing NOT_RUN/UNKNOWN.
- Verified `emu_chat` uses EmuManager MapID/PosX/PosY and ADB input; shipped JS exports raw PosX/PosY and X_UI/Y_UI shifted by 5 bits. Exact memory-to-tile arithmetic not recovered. Debug Android calibration and train per-device presets are separate coordinate domains.
- Original emu_farm_tab imports `emu_chat.goto` and has per-serial [EmuCoords:serial] presets, Android-ID keyed row identity; original contains literal `farm cycle: phase sau`: full automatic farm unproven/partially deferred. Conditional Train LD, developer-only Debug Android preserved.
- P04 artifacts docs/emulator/P04_EMU_CHAT_GOTO_CONTRACT.md, P04_MODEL.json, P04_STATIC_EVIDENCE.tsv, docs/tasks/P04.md; 46 evidence rows, 26 future tests, 0 live executed. Original ZIP/hash/CRC checked; no game/ADB/Frida/Proxy executed.
- **Stage S product source and Stage T build still absent**: BUILD_BLOCKED_SOURCE_MISSING. This task only wrote P04 documentation/checkpoint.
- **NEXT_ACTION P05 — emu_farm_tab Train LD device/row/preset and button wiring audit, distinguish working goto from incomplete farm cycle.**


## P05 — Train LD per-device UI, presets and partial automation truth
- Verified current GitHub P05 absent; original inner EXE emu_farm_tab marker 0x2932983 and original ld_remote.js compared before documentation. Source fingerprints/ZIP CRC PASS, 15 compiled offset checks PASS, 5 shipped JS token checks PASS; no game/device run.
- Tk dynamic account rows/scroll/refresh with daemon worker emu_manager.poll_rows; per-device [EmuCoords:serial] presets, row identity android_id and [EmuFarm]↔[TrainLD] fallback. Original metrics HP/Level/Map/Bag/EXP/money/deaths and per-account settings references recovered; actual runtime accuracy unknown.
- _toggle_this/btn_play/status is wired but explicit original `farm cycle: phase sau` means cannot claim full farming engine. _goto_acc -> emu_chat.goto (emu_tab/trainld guard); _setup_acc -> emu_setup.setup_instance (trainld_setup guard).
- Guest AutoX `btnGoTrain` seven-step fixed click route and `/emu_steps` returns success label after transport ACK, without in-handler memory arrival proof. Guest Train On/Off flips local state after `/emu_farm_toggle` ACK-only endpoint. PC EmuChat separately has documented memory-based arrival. These paths must not be conflated.
- Artifacts docs/emulator/P05_TRAIN_LD_AUTHORITY.md; P05_MODEL.json; P05_STATIC_EVIDENCE.tsv; docs/tasks/P05.md. **81 evidence records; 30 runtime acceptance tests all NOT_RUN**. No Proxy, user-visible tab or old task changes.
- **BUILD_BLOCKED_SOURCE_MISSING**: Stage S application source and Stage T Windows EXE workflow not present in audit; no built product in this task.
- **NEXT_ACTION P06 — emu_setup device installation, push, permissions, AutoX and launch lifecycle EXE-first.**


## P06 — Setup research checkpoint
- P06 completed as static research only, with original package checksum and ZIP integrity verified.
- Added docs/emulator/P06_EMU_SETUP_DEPLOYMENT.md, P06_MODEL.json, P06_STATIC_EVIDENCE.tsv, and docs/tasks/P06.md.
- Recorded 63 static evidence items and 29 deferred runtime acceptance checks.
- No reconstructed application source or Windows build pipeline exists yet; build remains blocked pending implementation.
- Previous completed research and project scope remain unchanged.
- NEXT_ACTION: P07 — audit original emulator remote service protocol and runtime boundaries.


## P07 — Emulator HTTP remote research checkpoint
- P07 compiled EXE/AutoX script static authority verified: 34/34 exact symbol-offset checks, 10/10 JS token checks, original SHA/CRC PASS; 72 evidence records and 33 deferred runtime acceptance tests.
- Original emu_remote optional ThreadingHTTPServer listens 0.0.0.0:8765 default with token tlm, socket peer IPv4 serial selection, emu_tab permission/limit references. Six GET and seven POST route contracts documented. GET auth coverage and actual network security unverified; no listener started.
- /emu_goto accepts asynchronous work (not arrived); /emu_farm_toggle original engine ACK-only. AutoX ld_remote.js post() returns local ok:true on nonthrowing postJson/body read without parsing server ok or status code. UI train/move confirmation may not represent game success.
- Added docs/emulator/P07_REMOTE_AUTH_ENDPOINTS.md, P07_MODEL.json, P07_STATIC_EVIDENCE.tsv, docs/tasks/P07.md. Prior stages/PLAN untouched, Proxy excluded.
- Build status BUILD_BLOCKED_SOURCE_MISSING: app reconstruction and Windows workflow absent, no product EXE or runtime parity test.
- NEXT_ACTION P08 — debug_android_tab developer-only capture/viewport/Frida/remote workbench audit.


## P08 — Debug Android developer workbench static research handoff
- Original compiled debug_android_tab at 0x290df6c checked directly from locked EXE. Static test 53/53 symbol-offset anchors PASS and original ZIP hash/CRC PASS. 92 evidence rows, 33 future runtime checks not executed.
- Developer-only Tk UI/control inventory: serial/refresh, Frida/rescan, push script, listener control, Tap/Screencap/RGB, RoleData/Site10 bag, chat-goto stages, tracker/log. Win32 cursor-client-viewport device coordinate conversion plus Alt two-corner calibration documented; public tab parity unchanged.
- Files added docs/emulator/P08_DEBUG_ANDROID_WORKBENCH.md, P08_MODEL.json, P08_STATIC_EVIDENCE.tsv, docs/tasks/P08.md. No original modules, PLAN, prior research, emulator, game or Proxy touched.
- Phase P01–P08 original static emulator subsystem research complete, runtime Windows/LD parity deferred. Product build **BLOCKED_SOURCE_MISSING** until Stage S app and Stage T Windows workflow exist.
- NEXT_ACTION R01 — Phase R resource provenance/loader GAP audit building on Gate A/D06/D07; never repeat completed manifest work.


## R01 — Resource provenance closure / Stage S handoff
- Direct frozen ZIP verified SHA/CRC: 1050 entries, 1002 regular files, 48 dirs. Reused Gate A and D06/D07. Added 26-row immutable resource matrix with SHA/size/header/reader/writer/runtime confidence; matched A07 26/26 and D06 24/24.
- Fourteen opaque .dat and five old/backup DLL basenames have zero exact ASCII or UTF-16LE occurrences in frozen EXE; UNKNOWN readers/writers preserved. Strong relative path dependency: outer launcher CWD TLMTool.dist and dll_injector ./data/resources.dat. Full 1002-file build manifest remains authoritative.
- New artifacts docs/resources/R01_RESOURCE_GAP_MATRIX.tsv, R01_DATA_RESOURCE_GAPS.md, R01_MODEL.json, R01_STATIC_EVIDENCE.tsv, docs/tasks/R01.md, tools/R01_VERIFY_RESOURCE_GAPS.py. Local verifier syntax+ZIP-only PASS; optional matrix mode NOT_RUN; zero runtime tests.
- R01 closes Phase R static Plan fields with UNKNOWN explicitly; still no Stage S rebuilt app or Stage T Windows build: BUILD_BLOCKED_SOURCE_MISSING. No Proxy development or earlier data changed.
- NEXT_ACTION S01 — smallest real Stage S source bootstrap from verified MainApp/UI/launcher contracts; do not fake feature functionality.


## S01 — Real reconstructed source bootstrap, seven tests PASS
- GitHub first real application files: src/TLMTool.py, src/shell.py, src/settings_store.py and tests/test_s01.py. This replaces earlier “no application source at all” state with **PARTIAL SOURCE PRESENT**. 15 original Notebook slots, Info-only by default, conditional/dev tab visibility, lazy real factories, Info fallback, selected refresh lifecycle; never fake missing feature controls.
- Shared settings.ini access: RawConfigParser(strict=False), UTF8, atomic same-dir temp replacement, pre-existing file dated backup, no invented backup pruning. Original lock class and sanitization edge cases unverified.
- User correction **Dồn** applied instead of original static-doc **Đồn**.
- Tests on latest local byte-matching committed code: compileall PASS; 7/7 unittest PASS; entrypoint exit 2 is intentional until real InfoTab/auth exists; Windows/Tk/exe/LDPlayer runtime NOT_RUN.
- Artifacts docs/source/S01_BOOTSTRAP.md, S01_MODEL.json, docs/tasks/S01.md and source/test files committed. Frozen ZIP, PLAN, prior research, Proxy exclusion preserved.
- **CURRENT BLOCKER SOURCE_PARTIAL_APP_STARTUP_BLOCKED_INFO_AUTH_AND_WINDOWS_BUILD_WORKFLOW_MISSING** — genuine source exists but no end-to-end app/EXE build. Do not report old SOURCE_MISSING as current.
- **NEXT_ACTION S02 — InfoTab/auth permission_guard real minimal service, original source evidence first, fail-closed tests.**


## S02 — Auth state source slice / optional game client DATA lookup
- Continuation from S01: current GitHub and original EXE info/permission modules audited. User-authorized data client repo (ngmthang-g/clinent-game-than-long-DATA-2222) README/bootstrap/router consulted READ-ONLY; TLM license server claims are not inferred from game client data.
- Added src/permission_guard.py and src/info_state.py with verified-token adapter boundary, deny-by-default snapshot, dev/banned/version/expiry/limit gates, Info change callback. src/shell.py add root.after(0, ...) for UI permission updates. No token signature or endpoint faked; src/TLMTool.py still intentionally exits 2.
- Tests PASS: combined Python source compileall and **15/15** headless tests (S01 7 + S02 8). Real Windows InfoTab/heartbeat/HTTP/auth and GUI/EXE not tested.
- Artifacts: docs/source/S02_AUTH_STATE.md, S02_MODEL.json, docs/tasks/S02.md, tests/test_s02.py. Original ZIP, PLAN and completed research unchanged; no Proxy implementation.
- S02 status SOURCE_PARTIAL_AUTH_VERIFIER_INFO_UI_FEATURES_AND_WINDOWS_BUILD_MISSING. Original default FREE permissions + heartbeat grace unknown, so conservative denial is explicitly partial parity, not original exact behavior. Stage-T build still missing.
- NEXT_ACTION S03 — recover genuine InfoTab token verification/RPC/FREE and heartbeat contract, then implement only evidenced read-only Info UI controller/tests; user client DATA permitted only for client-specific unknowns.


## S03 — Original Info authorization research and passive real Tk fields
- Direct frozen EXE static scan confirmed Info RPC, token verification branch and permission guard/grace variables: 18/18 selected binary string offsets PASS; original ZIP CRC PASS; no secret reuse, no live server calls.
- Real partial source src/info_tab.py and tests/test_s03.py committed. Info screen fields are B12-original headings and safe explicit unknown values, no fake activation or Copy controls. New S03 headless unit tests 6/6 PASS; previous S01/S02 15/15 are historical (NOT rerun combined in S03).
- Artifacts docs/source/S03_INFO_VIEW_AND_AUTH_BOUNDARY.md, S03_MODEL.json, S03_STATIC_EVIDENCE.tsv (21 entries), docs/tasks/S03.md. No prior modules/PLAN/Proxy changed.
- Product still partial source with blocked authentic server verification and incomplete feature tabs, no Windows EXE or screenshot parity. Status S03_READONLY_INFO_VIEW_6_TESTS_PASS_AUTH_RPC_RUNTIME_UNVERIFIED.
- NEXT_ACTION S04: Info state-to-Tk binding, full combined regressions, preserve original license boundaries and no fake grants.


## S04 — Info Tk lifecycle binding and 31/31 Windows unit tests
- Added true source src/info_binding.py: InfoState connects to partial read-only TLMInfoTab/TLMMainApp via root.after, suppresses stale queued grants after revocation, and cleans up on root destroy; default Info-only, no fake dev/feature controls. tests/test_s04.py adds 10 focused tests.
- Added .github/workflows/s04-source-tests.yml (Windows latest / Python 3.10). Actual run 37867454367 at https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37867454367, job 113617493218, SUCCESS: compileall PASS and **combined S01–S04 31/31 unittest PASS**; verified actual Actions job log "Ran 31 tests in 0.035s".
- docs/source/S04_INFO_LIFECYCLE.md, S04_MODEL.json, S04_STATIC_EVIDENCE.tsv, docs/tasks/S04.md completed; previous PLAN and S01–S03 code untouched, no Proxy.
- **Status:** partial application source with real Info-only lifecycle, **NOT** a launched Windows GUI, verified server/heartbeat, runnable game tool or Nuitka EXE. Normal src/TLMTool.py intentionally exits 2, authentication and functional tabs remain missing. GUI raster/real integration NOT_RUN.
- NEXT_ACTION **S05** — real Windows Tk Info-only preview and B12 screenshot parity/clean close if an actual display runner is available; otherwise document GUI blocker and progress original-backed Info startup contract without inventing auth.


## S05 — Windows native Tk Info smoke passed, original B12 raster parity deferred
- New tools/S05_WINDOWS_TK_SMOKE.py and .github/workflows/s05-native-info-preview.yml run real tkinter/ttk Info-only shell, geometry, safe unknown license fields, screenshot capture and root destroy cleanup; src/TLMTool.py product startup and S01–S04 correct source unchanged.
- **Real GitHub Actions run 37868251319** (Windows latest Python 3.10), SUCCESS: compileall PASS, 31/31 S01–S04 unittests PASS, native Tk smoke PASS. Runner 1024×768; client 450×688 px follows E02 formula; B12 reference client 450×1000 at different desktop height, hence not exact pixel parity.
- 15 potential tabs, only Info selected/visible while feature and genuine license controllers are absent; original B12 screenshot had 11 visible tabs. PNG+JSON artifact ID 11589735180 at https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37868251319/artifacts/11589735180. Original B12 image not raster-compared.
- New docs/source/S05_NATIVE_TK_PREVIEW.md, S05_MODEL.json, docs/tasks/S05.md; no Proxy or game action changes. Still no authentic license/heartbeat or full Windows Nuitka EXE.
- STATUS S05_NATIVE_WINDOWS_INFO_TK_PASS_B12_PIXEL_PARITY_NOT_YET_VERIFIED. NEXT_ACTION **S06** — improve only B12-proven read-only Info layout and native Tk geometry tests; keep action buttons absent until functional.


## S06 — B12 Info passive layout native Windows PASS (37/37 source tests)
- Updated only existing src/info_tab.py: original-backed status panel 416×44, six read-only white value surfaces with 25px pitch, real disabled Text/Scrollbar in 416×109 changelog. Preserved all S03/S04 safe unknown/server semantics; no fake actions/license rights, no other old code changed.
- Added tests/test_s06.py (6), tools/S06_WINDOWS_INFO_LAYOUT.py and .github/workflows/s06-native-info-layout.yml. Actual GitHub Actions run 37869205674 on Windows Python 3.10 completed SUCCESS: source compileall and **37/37 combined tests PASS**; native Tk exact B12 Info-frame-relative rectangles PASS, scrollbar/readonly PASS, PNG captured and Tk shutdown/cleanup PASS. Artifact ID 11589915070.
- Full B12 visual/raster parity still not proven: 1024×768 test host yields 450×688 client vs original screenshot 450×1000; eleven authorized tabs/server-fed content unavailable. No original working TLMTool EXE rebuild, real token/server/heartbeat, game/controller runtime, or Proxy development. Normal source entrypoint still fails closed exit 2.
- Artifacts docs/source/S06_B12_READONLY_LAYOUT.md, docs/source/S06_MODEL.json and docs/tasks/S06.md, with append-only STATE and status. **NEXT_ACTION S07** — remaining passive Info pricing/contact/catalog sections and native Windows tests, then verified functional Start/Login development, without inventing data/buttons.


## S07 — Passive B12 Info lower sections, native Windows 43/43 PASS
- src/info_tab.py updated *only* for read-only B12 pricing region, support heading, nonclickable original Facebook/Zalo labels, system catalog heading and placeholder. Server prices/catalog remain Chưa xác minh; no false buttons/links/auth. Prior S06 geometry and user-corrected Dồn unchanged.
- New tests/test_s07.py (6), tools/S07_WINDOWS_INFO_SECTIONS.py, .github/workflows/s07-info-sections.yml. Actual Windows Python 3.10 GitHub Actions run **37869958702** completed SUCCESS: compileall, **43/43** combined unittest PASS, prior S06 native geometry PASS, S07 live Tk PASS (0 action buttons, screenshot, clean destroy). Artifact **11589688653**.
- Honest limitation: 1024x768 desktop / 450x688 client clips the catalog starting frame-relative y656; exact location matches B12, full view does NOT. Original reference 450x1000 with 11 licensed tabs, no full pixel parity; real server/token/heartbeat, product executable and Start/Login controllers missing. Proxy remains excluded.
- Artifacts docs/source/S07_PASSIVE_INFO_SECTIONS.md, S07_MODEL.json, S07_STATIC_EVIDENCE.tsv and docs/tasks/S07.md. Current status **S07_WINDOWS_NATIVE_PASSIVE_SECTIONS_43_TESTS_PASS_CATALOG_CLIPPED_ON_768P**.
- **NEXT_ACTION S08** — start genuine functional Start-tab source using original Start/Win32 window discovery contracts and native Windows tests; do not revisit Info cosmetics without a blocker, do not fake HWND, license permissions or game actions.


## S08 — Real read-only Windows Start HWND discovery, 55/55 regression PASS
- User approved S08. Starting GitHub S07 NEXT_ACTION, consulted original compiled Start HWND/PID research C01/C02 and shell B02/B03/E01/E03. No previously correct code/docs, original game client, frozen binary, PLAN or Proxy Phase Q changed.
- New src/start_windows.py is **actual operational source**: EnumWindows, visible-window filtering, timed 150ms SendMessageTimeoutW title, GetWindowThreadProcessId, GetClassNameW, query-only QueryFullProcessImageNameW, conservative process/class/title filtering, and WindowRegistry anti-stale HWND+PID reconciliation. Exact original Boolean filter expression UNKNOWN. No game memory, click, injection or fake account handles.
- New tests/test_s08.py (12), tools/S08_WINDOWS_DISCOVERY_SMOKE.py and .github/workflows/s08-windows-start-discovery.yml. **ACTUAL Windows Python 3.10 GitHub Actions run 37872770792 SUCCESS:** compileall PASS, 55/55 combined S01–S08 tests PASS, real Win32 smoke PASS. 63 top-level HWND, 11 visible, live own Tk HWND/title/PID/process verified, 0 fabricated HWNDs. Runner has **NO Thần Long Mobile game process**; positive game matching not validated. Artifact ID 11591140628.
- docs/source/S08_START_WIN32_DISCOVERY.md, S08_MODEL.json, docs/tasks/S08.md completed. Partial Start service only; no production StartTab, native game scan, auth server, Nuitka EXE; main entry still exits 2. S07 small-screen Info catalog clipping deferred, not reworked.
- **STATUS S08_REAL_WIN32_DISCOVERY_55_TESTS_PASS_GAME_RUNTIME_NOT_PRESENT. NEXT_ACTION S09** — real 3s background HWND producer/cache + 2s Tk Start-tab poll/stop lifecycle, Win32 tests, no fake permissions or game control.


## S09 — Actual native Windows 3s worker + Tk 2s Start cache lifecycle, 67/67 PASS
- Read current S08 NEXT_ACTION, C01/C02/C04/E03 and Stage S source first; S09 absent. Existing correct source, original package, PLAN, client DATA, Dồn text and Proxy lock untouched.
- Added src/start_polling.py with true threaded read-only EnumWindows producer (3s default), immutable HWND/PID snapshots, epoch/event stopping, no stale-window or overlapping producer after shutdown; independent Tk root.after consumer polling at 2s, C02 HWND/PID added/removed/reused deltas, callback cancellation on leaving Start and restart on re-entry. No fake game control or authorized tab creation.
- Added tests/test_s09.py (12), tools/S09_WINDOWS_START_POLLING_SMOKE.py and .github/workflows/s09-windows-start-polling.yml. **REAL Windows Python 3.10 GitHub Actions run 37873565602 SUCCESS**: compileall PASS, combined **67/67 unittest PASS**, native worker and Tk smoke PASS, background scan of 68 top-level HWNDs; valid empty game snapshot consumed on Tk main thread, stop invalidated cache. Game not installed in CI: positive game recognition NOT_RUN. Artifact 11591396593.
- docs/source/S09_START_THREADED_CACHE.md, docs/source/S09_MODEL.json and docs/tasks/S09.md completed. App remains partial; no verified server token/heartbeat, full Start/other tabs, or Windows Nuitka EXE. Production entrypoint exit 2 unchanged.
- **STATUS S09_NATIVE_WINDOWS_WORKER_TK_67_TESTS_PASS_NO_GAME_RUNTIME; NEXT_ACTION S10**: real read-only Start widget connected to S09 producer/Tk lifecycle using B04/C03/C05/C06/C08 original evidence, with unit and native Windows tests, no fake action buttons, permissions, game clicks or Proxy.


## S10 — Read-only Start Tk view + real Windows auth lifecycle (77/77 PASS)
- Continued from S09 GitHub NEXT_ACTION. Verified newly supplied ZIP and inner TLMTool.exe SHA256 match exact original frozen evidence. Original package, PLAN, preexisting source/tests, Dồn spelling and Proxy freeze unchanged.
- src/start_tab.py: real Tk readonly HWND/PID/title table from S09 3s background worker/2s selected-tab cache, safe pending/empty/error states, remove stale rows after tab leave/license revocation; does not pretend DWM or game clicks work. Start only exposed by existing verified-permissions shell; src/TLMTool.py still fail-closed.
- Added tests/test_s10.py (10), tools/S10_WINDOWS_START_VIEW_SMOKE.py and .github/workflows/s10-native-start-readonly.yml.
- **Windows CI 37874342004 SUCCESS:** Python compileall PASS, **77/77 unit regressions PASS**, native `PASS_NATIVE_READONLY_START_AUTH_AND_POLLING`, initial Info-only and Start not built; test-only verified claim activates polling; clearing claim hides Start/stops worker and clears HWND rows. CI has no Thần Long Mobile game; game-positive parity, screenshot parity, DWM and standalone EXE NOT_RUN/NOT_BUILT.
- docs/tasks/S10.md and docs/source/S10_* evidence added. **NEXT_ACTION S11**: native read-only DWM live thumbnail preview for grounded HWND+PID, test-owned window only for API smoke, strict cleanup and no fake game/action/license/Proxy.


## S11 — Native DWM Start previews with guarded HWND/PID; 90 tests PASS
- Resumed from GitHub S10 NEXT_ACTION. Real DWM compositor thumbnail API implemented in new src/dwm_preview.py; existing src/start_tab.py extended minimally with live 205×137 preview items and 197×110 anchors on genuine S09 HWND/PID/title rows, Win32 owned popup and exact DWM register/update/unregister lifecycle. Revoke, stale PID, close and invalid cache delete overlays; no game clicks/input or fake preview.
- Two native smoke problems fixed from actual CI failures: wintypes.HCURSOR missing in Python 3.10; Tk widget HWND not top-level (GetAncestor GA_ROOT). Native WIN32 37878364061 SUCCESS, **90/90 S01–S11 tests PASS**, real DWM register/update/reposition/teardown PASS with **test-owned Tk window**, not game. Compiled source passes. Source regression CI 37878364020 also SUCCESS.
- New tests/test_s11.py, tools/S11_WINDOWS_DWM_SMOKE.py, .github/workflows/s11-native-dwm-preview.yml, docs/tasks/S11.md, docs/source/S11_*; previous work and PLAN unchanged. Original game positive, actual pixel parity, many HWND concurrent DWM, licensed server and product EXE remain unverified/unbuilt.
- **NEXT_ACTION S12:** real Windows multi-source (2–3 test-owned native HWNDs) DWM overlay Tk resize/move/missing-window cleanup stress and partial visual geometry parity, no fake game input or permission bypass, keep working S01–S11 unchanged.


## S12 — 3 native Win32 DWM test-owned sources, Tk root move/revoke; 98/98 PASS
- Continued exactly from S11 NEXT_ACTION; no replan. One existing source edited: `src/start_tab.py` gains root/configure+map/unmap DWM lifecycle and C04 exact 60ms resize debounce, unbinds handlers at destroy. New `tests/test_s12.py` (8), `tools/S12_WINDOWS_MULTI_DWM_SMOKE.py`, workflow `s12-native-multi-dwm.yml`; unrelated source, original, Info/license, Dồn naming and Proxy exclusion unchanged.
- Native GitHub Windows CI **37878962348 SUCCESS**: compileall, **98/98** S01–S12 unit PASS, real three test-owned HWND registration/move/resize/closed source/PID invalidation/owner hide/restore; **5 created = 5 destroyed** DWM destinations. Isolated Start Tk test with two real test-owned source HWNDs verified root moving triggers reposition; owner hidden/restored and authorization revocation clean up resources. S10 37878962283/S11 37878962259/full-source 37878962249 regressions all SUCCESS.
- No real Thần Long game in runner, no original raster proof, no live entitlement server, no standalone EXE. **STATUS S12_THREE_NATIVE_DWM_98_TESTS_PASS_GAME_NOT_RUN; NEXT_ACTION S13** = selected-tab C04 preview maintenance scheduler, bounded 800/2000ms and documented count-6 unknown, no fake FPS or game actions.


## S13 — Independent C04 Start preview maintenance / Windows 112/112 PASS
- Continued live S12 NEXT_ACTION without replan. Added src/preview_maintenance.py and minimal src/start_tab.py integration; selected-tab-only Tk after maintenance at **800ms for 0–5 windows, 2000ms at 6+** (equality at 6 source UNKNOWN, S13 conservative choice). Independent of S09 3s producer and 2s cache poll, no screenshots/FPS trickery, no worker-side Tk.
- New tests/test_s13.py (14), native tools/S13_WINDOWS_PREVIEW_MAINTENANCE_SMOKE.py and s13 workflow. Actual Windows run **37880150984 SUCCESS**, compileall, **112/112 unit tests PASS**, native real test-owned HWND 1/6 cadence, cache loss/recovery, DWM stale HWND rejection and permission revoke timer stop PASS. Same-code S10 37880151057, S11 37880151065, S12 37880151024 and Stage S source 37880151015 all SUCCESS.
- All prior working modules, PLAN, original binary, Info auth gate and Proxy exclusion unchanged. No real game/HP source/pixel parity/signed token/full EXE. **STATUS S13_ADAPTIVE_NATIVE_PREVIEW_112_TESTS_PASS; NEXT_ACTION S14 C09/C17 functioning 1x–5x Start grid and per-source HWND ordering with explicit unknown edge policy.**


## S14 — C09/C17 real Start 1x–5x preview grid / per-HWND order, 128/128 Windows PASS
- Resumed GitHub S13 NEXT_ACTION; implemented evidence-backed functional `Cột:` 1x,2x,3x,4x,5x combobox default 2x and ◀/▶ one-step reorder inside Start live DWM items, not game input. New src/preview_layout.py maps HWND+PID to logical preview order, prevents stale PID button usage. Edge no-wrap and new HWND append are documented S14 local policies, NOT original source proof.
- Windows native GitHub Actions **37881002761 SUCCESS**, compileall + **128/128 S01–S14** unit PASS + actual test-owned four-source HWND DWM previews retaining compositor handles through all five modes, arrows moving tiles, refresh retaining order, wrong PID rejected, revoke cleanup. Same-code S10/S11/S12/S13/Stage-S regressions all SUCCESS (37881002747/37881002713/37881002772/37881002748/37881002704).
- Only src/start_tab.py existing module changed. New tests/test_s14.py, tools/S14_WINDOWS_PREVIEW_GRID_SMOKE.py, workflow s14-native-preview-grid.yml, docs/tasks/S14.md and docs/source/S14_*. Original binary, PLAN, previous verified features, Info gate, user Dồn spelling and Proxy exclusion retained. **STATUS S14_REAL_DWM_GRID_ORDER_128_TESTS_PASS_NO_REAL_GAME, NEXT_ACTION S15: C15 manual DWM full-list refresh from genuine cache with column/order persistence.** Real game, pixel parity, token service and product EXE NOT_RUN/NOT_BUILT.


## S15 — Real C15 manual native DWM full list rebuild / 142/142 Windows PASS
- Resumed S14 NEXT_ACTION. Modified existing production `src/start_tab.py` only, adding functional `Làm mới` that unregisters/disposes DWM thumbnails before Tk tile teardown, rebuilds from one O(1) immutable S09 snapshot, retains C09 1x–5x and C17 order; invalid cache and revoked Start fail closed. Added 14 unit tests, test-owned Windows native smoke, new Windows CI workflow. No game control, forced scanning or fake auth.
- First S15 CI run 37883811777 failed only at printing Unicode status through Windows cp1252 after successful tests/native simulation; corrected log output in commit d609880. **Windows run 37883868392 COMPLETED SUCCESS**, compileall PASS, **142/142 S01–S15 tests PASS**, real Win32 DWM **3×(4 old removed then 4 re-registered)**, order/grid stable, resource-balanced/revocation PASS, actual HWNDs test-owned not game. Same production implementation S10/S11/S12/S13/S14/Stage-S regressions all SUCCESS.
- New `docs/tasks/S15.md` and `docs/source/S15_*`; STATE/PROJECT_STATUS append-only. Original ZIP, PLAN, user Dồn naming, previously working features, Info/auth and Proxy exclusion untouched. **STATUS S15_NATIVE_DWM_142_TESTS_PASS_GAME_NOT_RUN. NEXT_ACTION S16** original C16 `Đóng hết` genuine guarded WM_CLOSE on verified HWND/PID, **native CI only test-owned**; no crash-handler forced kill or authorization bypass, do not claim finished EXE.


## S16 — C16 Đóng hết real test-owned HWND normal Win32 WM_CLOSE, 163/163 PASS
- Continued from live S15 NEXT_ACTION. New src/close_windows.py per-HWND/PID/top-level/exe/class/title/IsWindow/visible fail-closed WM_CLOSE native, not TerminateProcess. Real `Đóng hết` button in src/start_tab.py active only in selected authorized visible Start, one current S09 cache read, reports sent WM_CLOSE rather than already exited; no forced UnityCrashHandler kill or invented immediate post-close refresh.
- tests/test_s16.py (**21** new), native tools/S16_WINDOWS_TEST_OWNED_CLOSE_SMOKE.py, Windows s16-native-wmclose workflow. First implementation CI 37884562214 failed test-only hidden-root guard; fixture corrected bd0678f. **Windows run 37884623539 COMPLETED SUCCESS**, compileall PASS, **163/163 S01–S16 unit PASS**, real native PostMessageW to 3 explicitly test-owned Tk top-level HWNDs leads to real Tk close callback/destruction while other window survives; fake identity/reused/dead sources refused; cache cleanup and permission revoke verified. S10/S11/S12/S13/S14/S15 and combined Stage S source workflows on same implementation all SUCCESS.
- Docs S16/C16 native lifecycle + STATE/PROJECT_STATUS append-only; PLAN/original file, other working modules and Proxy prohibition untouched. Actual Thần Long game, real auth server and final production EXE NOT_RUN. **STATUS S16_NATIVE_TEST_OWNED_WMCLOSE_163_UNIT_PASS; NEXT_ACTION S17 C18 careful layout sync from existing original evidence, no invented timer/arithmetic or C19 input.**


## S17 — C18 native HWND grid sync; 187/187 Windows test PASS
- New src/layout_windows.py actual Win32 SetWindowPos on validated cache HWND/PID with S17 explicit local move-only geometry, no original exact-grid/cadence claim. src/start_tab.py real layout toggle/worker, src/shell.py verified PermissionSnapshot.max_windows grant only. New 24-unit tests/native four-test-owned-HWND smoke/workflow; historic S02/S10 compatibility restored.
- GitHub Actions 37887093950 SUCCESS native 4 source window positioning, master-first, original dimensions preserved, unrelated HWND untouched, manual drag corrected and revoke stops. Final same-code dc4921f **all 9 workflows S10–S17 plus Stage S SUCCESS** (37887172714/37887172750/37887172677/37887172668/37887172726/37887172698/37887172703/37887172760/37887172697), **187/187 tests PASS**. Real game/auth server/production EXE NOT_RUN.
- S17 docs + STATE/PROJECT_STATUS append only. PLAN/original and Proxy exclusion untouched. **NEXT_ACTION S18: C05/C08 master selection and grid column/row functioning controls, no C19 input/Proxy, keep source buildable and 187 passing tests.**


## S18 — C05/C08 working master radio/grid settings, 210/210 Windows PASS
- New src/grid_master.py and true Start Cột/Hàng +/- controls + dynamic PID-guarded ttk Master radio. Persist only Settings.grid_cols/grid_rows using existing atomic E05 settings writer; master never persisted. Original min/max formula unknown => explicit local 1..12 safety policy; fallback auto-master first current HWND is local only; RoleName not yet available so uses real S09 window title+HWND. S17 worker takes live changed grid/master.
- New tests/test_s18.py (23), S18 native smoke and workflow; historical S10 assertion narrowed for now-real C05 master handler; S17 native smoke updated to invoke actual UI. Windows [run 37888218013] SUCCESS, 210/210 units + native real four test-owned HWND position changes (2x2→3x3 while enabled), Master radio moves actual top-left target, ini persistence, unrelated HWND untouched, revoke stops. All ten same-head runs S10–S18 + Stage-S SUCCESS on b6adf2c.
- docs S18 + STATE/PROJECT_STATUS append-only. PLAN, frozen original game, spelling Dồn and Proxy exclusion unchanged. Actual Thần Long, real character cache, signed auth server and full EXE still NOT_RUN/NOT_BUILT. **NEXT_ACTION S19** C19 bounded original-evidenced input coordinate scaling/ordered press-release safety model for test-owned native HWNDs only; do not fabricate WM_MY_SYNC_KEY message payload or pretend complete input sync.


## S19 — C19 input-client geometry/ordered queue model, 239/239 Windows PASS
- New src/input_sync_core.py pure verified C19 planner: proportional master-client/slave-client scaling with explicit LOCAL floor/clamp, FIFO serialized left/right/middle down/up queue, per-message permission+HWND/PID identity gate, model watchdog 10s and no-auto-restart master change. Read-only Win32 GetClientRect, no native mouse/key message sender, listeners, DLL input lock, original unknown WM_MY_SYNC_KEY payload, fake functioning UI button or Proxy. All S01–S18 production source unchanged.
- New tests/test_s19.py (29), test-owned Windows native tools/S19_WINDOWS_CLIENT_FIFO_SMOKE.py and workflow. Windows [37889666893] SUCCESS: compileall PASS, **239/239** combined tests PASS, real 3 test-owned HWND client geometry 280×190/410×260/360×310; Tk-only test slave sinks verify scaled coordinates and strict DOWN/DOWN/UP/UP FIFO; permission revoke, stale native HWND and model watchdog pass, unrelated window receives none. Stage S [37889666867] SUCCESS; no new S10–S18 workflows run on this commit because code untouched.
- docs S19 + STATE/PROJECT_STATUS append-only; PLAN, original archived source, Dồn, no-Proxy rule unchanged. **STATUS S19_NATIVE_TEST_OWNED_239_PASS_GAME_NOT_RUN; NEXT_ACTION S20** original C20 screenshot 3-HWND combined preview/layout/master separation integration test, no unknown game input payload or fictitious RoleName/HP, preserve 239 unit tests.


## S20 — C20 3 real test-owned HWND native integration / 252/252 PASS
- Combined unchanged S01–S19 actual preview/DWM, physical C18 layout, C05 radio Master, C17 preview order and S19 SAFE FIFO model using 3 real TEST-created HWNDs. Physical grid **3×4** stays distinct from preview **2x**; 2nd preview is Master but physical index0; reorder preview does not change Master. S19 models two slave events only, NO native game input. Verified 3→2 native DWM cleanup, surviving Master, stale model HWND guard, revoke/Info and no late layout; unrelated HWND untouched.
- 13 new tests, S20 native Windows smoke/CI, **run 37890935461 COMPLETED SUCCESS**: Python3.10 compileall, **252/252** S01–S20 units, PASS_NATIVE_S20_THREE_HWND_DWM_MASTER_LAYOUT_INPUT_MODEL; Stage S source run 37890935189 SUCCESS same commit 6776bee. No existing production files changed.
- New docs/tasks/S20.md, docs/source/S20_*, append-only STATE/PROJECT_STATUS, PLAN and original frozen EXE unchanged. Real game/server/RoleName/HP/EXE parity still NOT_RUN.
- **NEXT_ACTION S21:** read E01 already audited, implement bounded Windows TLMTool_SingleInstance mutex guard in fail-closed bootstrap; test two test-owned Windows processes with isolated name, no fake startup auth/Proxy or C19 live input. Preserve 252 tests.


## S21 — E01 real Win32 named single-instance mutex / 267/267 Windows PASS
- Added src/single_instance.py real kernel32 CreateMutexW/GetLastError(captured via ctypes)/CloseHandle guard with original exact name TLMTool_SingleInstance; failure/duplicate handle cleanup, context lifetime and no UI before win32 registration. src/TLMTool.py only wraps existing run_with_info_factory, **main() still refuses without genuine Info/server auth**.
- 15 new unit tests, S21 test-owned TWO-PROCESS Windows native mutex fixture with unique isolated names (second refused, incumbent survives, graceful/forced test-child exit enables next process), and S21 Windows CI. [run 37892342942] SUCCESS, compileall PASS, **267/267 unit PASS**, PASS_NATIVE_S21_TWO_PROCESS_MUTEX_COLLISION_AND_CLEANUP, same-HEAD S20 three-window DWM integration PASS; Stage S run 37892342899 SUCCESS. Original named production mutex never used by tests, exact original collision message/error compare unknown.
- docs S21 and STATE/PROJECT_STATUS append only. PLAN/original, other working source, Dồn and Proxy exclusion untouched. Full original app/game/Info/auth/product EXE NOT_DONE. **NEXT_ACTION S22** E01 recovered early diagnostics, faulthandler + threading.excepthook with TEST-only paths, preserve fail-closed GUI and all 267 tests/native mutex/S20.


## S22 — E01 startup diagnostics real Win32 test-owned process, 285/285 PASS
- NEW src/startup_diagnostics.py true faulthandler + threading.excepthook contextual crash logger, safe pre-existing hook preservation and file cleanup. src/TLMTool.py minimally nests diagnostics inside existing named mutex before Tk construction; recording failures and closing mutex; main() remains BLOCKED / return2 without genuine Info authorization. Local crash log path/format NOT source-equivalent original. tests/test_s21.py adapts 3 old Tk mock fixtures with nullcontext to avoid test pollution.
- NEW 18 S22 unit cases and native Windows 3-process scenario tool/workflow. [S22 run 37893509454] COMPLETED SUCCESS: **285/285** unit tests PASS, real thread exception and faulthandler wrote TEST-only log, Info constructor failure logged, bad log denies GUI; all three isolate mutex registrations become available again to other native process. S21 and S20 native reruns PASS; separate S21 workflow 37893509414 and Stage S 37893509490 SUCCESS same commit 6498db1.
- New S22 docs, STATE/PROJECT_STATUS append-only; all original existing features and PROXY EXCLUDED unchanged. Live server/game and product EXE not run. **NEXT_ACTION S23:** E06 central stdout/stderr tee log/tlmtool.log original-backed bounded implementation, test-only temp logs; numeric rotation/partial-line formatting unknown; do not fabricate, preserve 285 tests/native regressions.


## S23 — E06 append-only stdout/stderr session tee, 306/306 native Windows PASS
- Added src/session_logger.py scoped debug_logger.setup replacement tee: both stdout+stderr mirror console/file; frozen `<exe-dir>/log/tlmtool.log`, append Start/End sessions with markers/exe/Python metadata, atexit+explicit context restoration of original sys streams and original sys._fl_tee_out/_err attributes, fail closed on unwritable/double-hook. Optional tail trim only with explicitly given bounds; original MAX_SIZE/KEEP_SIZE/timestamp UNKNOWN, no fabricated auto trim. Local RLock is safety choice, not claimed original lock mechanism.
- src/TLMTool.py inserts SessionTee within mutex before S22 StartupDiagnostics/Tk (local ordering). main() STILL BLOCKED pending genuine signed Info. Three S21 and two S22 bare Tk fixtures adapted for no log writes, 21 new S23 tests/native separate test-owned Windows child processes. Initial S23 CI failed two tests-only fixtures, corrected commit 45d3ada, production untouched.
- Windows [S23 37894932947] COMPLETED SUCCESS: **306/306** unit tests, PASS_NATIVE_S23_TWO_SESSION_STDOUT_STDERR_TEE_AND_FAILURE_CLEANUP, same-head S22/S21/S20 native reruns PASS, Stage S source [37894932886] SUCCESS. Two sessions append, stdout/stderr worker prints mirror console/file, bad log blocks GUI, crash log separate, independent next process can reclaim test-only mutex. Actual game, Info auth and EXE NOT_RUN/NOT_BUILT.
- docs S23 plus STATE/PROJECT_STATUS append-only. PLAN/original Dồn and no-Proxy unchanged. **NEXT_ACTION S24:** original E08 normal Tk Destroy lifecycle and per-tab-owned cleanup test-owned HWND integration, no forced heartbeat/updater/forwarder assumptions, keep 306 tests and native S23/S22/S21/S20.

## S24 — E08 real normal Tk root/widget Destroy; 315/315 units + native Windows PASS
- src/shell.py now calls each built tab OWNER shutdown once after active refresh stop, has guarded root-only <Destroy> observation and no late Tk regrant; src/start_tab.py closes before touching destroyed C18 button, skips Tk repaint after destroyed and closes S09/DWM/maintenance. No global helper/game kill, no new WM_DELETE_WINDOW, no Proxy.
- 9 new tests, actual Win32 native DWM shutdown script and Windows workflow. First CI fixture failures (Info Start/Stop trace + S02 __new__ no _closed) corrected at d7c36af. **Final [37899237476](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37899237476) SUCCESS: 315/315 unit tests; two real TEST-OWNED HWND DWM root/app close scenarios destroy overlay HWND, stop producer once and reject late auth; S23/S22/S21/S20/S10 native regressions PASS.** Source run [37899237521](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37899237521) SUCCESS. Artifact 11601159680.
- Original source ZIP matching Gate A, PLAN, other modules, Dồn naming and Proxy exclusion unchanged. Production main() still blocked without signed Info, actual game/runtime/parity/EXE not done. New docs/tasks/S24.md, docs/source/S24_*, STATE append.
- **NEXT_ACTION S25:** F01/F04 original-backed Login folder selector + persistent game-path slice only if verified, actual native Tk/test-owned path with shell/auth gating. Do not implement Proxy or invented login/game actions.

## S25 — F01/F04 real Login "Chọn thư mục game" and settings, 331/331 Windows PASS
- NEW src/login_path.py and src/login_tab.py. Real blue Tk button uses askdirectory; recognizes canonical `Thần Long  Mobile.exe` (two spaces) direct, inside Game, parent or preferred one-child scan. E05 atomic `[Settings] game_dir` persistence and reload keep existing config keys; invalid/canceled choice doesn't overwrite. No fake Open game, Login or Proxy control. Verified Login still hidden without external test-only rights.
- 16 new tests + real Windows native Tk/test-only game-filename placeholder smoke. First CI red only for ttk LabelFrame inset/geometry; corrected actual widget location at c1f3ca9. **[S25 37900241256](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37900241256) COMPLETED SUCCESS: 331/331 unit, native Tk chooser/path/persistence/revoke/destroy PASS; same run S24/S23/S22/S21/S20/S10 Windows native regression PASS.** Artifact 11602351174.
- PLAN, original ZIP, all existing S01–S24 production and user Dồn/NO-PROXY directives untouched. Real game, signed Info/heartbeat, F05 injection, full Login UI and EXE still missing. New S25 task/source docs + STATE append.
- **NEXT_ACTION S26:** inspect already-audited F05 and existing S08 HWND backend first; implement only bounded launch permission+account-limit preflight / PID-bound HWND selection with TEST-owned native HWND, no guessed injection or Proxy and no fake game button.

## S26 — F05 permission/extra-one launch preflight + native PID-scoped HWND finder
- Existing S08 Win32 backend fully reused; no duplicate enum WinAPI or changes to other production modules. New src/login_launch_preflight.py enforces an **already verified** Info Login right and **actual supplied count + 1 ≤ limit**, missing/stale two-space F04 game EXE, then selects only visible HWNDs of specific PID (UnityWndClass, Thần Long title, fallback) with title 150ms timeout and identity rechecks. Not an injector or real game launcher. No fake Mở game button, login, Proxy or license grant.
- S26 tests/test_s26.py + native test-owned Win32 Tk HWND proof. **[S26 Windows run 37901273260](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37901273260) COMPLETED SUCCESS: 348/348 units, native S26 PASS, S25/S24/S23/S22/S21/S20/S10 native PASS.** Evidence artifact 11602416816; Stage S source 37901273207 SUCCESS.
- Game suspend/inject, real signed Info/count supplier, 25s handoff, full UI/EXE are NOT DONE. PLAN/old source/Dồn unchanged; Proxy runtime excluded. S26 reports+STATE updated.
- **NEXT_ACTION S27:** F05 bounded 25s PID-to-visible HWND readiness wait with native delayed test-only Tk, cancellation, rechecks; no invented stabilization or game process creation.

## S27 — F05 cancellable serialized 25s PID→HWND wait; Windows 368/368 PASS
- NEW `src/login_window_handoff.py` reuses S26 finder/S08 native Win32, polls for a caller-supplied PID-owned visible HWND under original-evidenced **25-second maximum**, accepts cancel events, rechecks HWND identity at handoff, reports FOUND/TIMEOUT/CANCELLED; serialized wait lock also bounded/cancellable. Exact original poll/stabilization timings UNKNOWN; 100ms local poll policy. No game process spawned or injected and no Proxy work.
- NEW 20 units + real Win32 TEST-OWNED Tk delayed window, foreign PID, disappearance/timeout/cancel native proof. **[S27 Windows 37901945848](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37901945848) COMPLETED SUCCESS: 368/368 full S01–S27 tests, native S27 PASS and S26/S25/S24/S23/S22/S21/S20/S10 native regressions PASS.** Artifact 11602743621; Stage S source 37901945877 SUCCESS.
- Original PLAN/ZIP, S01–S26 working source and user's Dồn/NO-PROXY constraints preserved. Real game, signed Info, F05 suspended injection, full Login/game parity and product EXE **NOT BUILT/NOT RUN**. S27 source/docs checkpoint saved.
- **NEXT_ACTION S28:** reuse original-audited F05/D06 to implement only proven safe environment and x64 payload/executable file preflight with TEST-owned filesystem/env; no guessing launch flags, no real injection or Proxy.

## S28 — F05/D06 testable x64 PE input/env preflight 390/390 PASS
- New `src/login_launch_inputs.py` read-only structural x64 PE EXE vs DLL classification and active `data/resources.dat` location with explicit Windows-essentials allowlist + TLM_PROFILE, refusing Python/virtualenv and Proxy env leakage. Original F05 precise essentials list/cwd remains UNKNOWN, no guessed fallback; only game/resource data preflight, **no real launcher/injection**.
- 22 new tests, synthetic TEST-owned PE fixtures, native actual Windows SystemRoot/temp filesystem. First run red due NEW test Path separators only, fixed test-only at a58951c. **[S28 Windows 37906555448](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37906555448) SUCCESS: 390/390 unit, native S28 PASS and all S27/S26/S25/S24/S23/S22/S21/S20/S10 native regressions PASS.** Artifact 11603899644. Independent Stage S 37906555280 SUCCESS.
- No edits PLAN, original ZIP, S01–S27 working production, Dồn label, Proxy lock. Signed Info, combined process/emulator count, real game launch/injection/full UI and product EXE still NOT DONE.
- **NEXT_ACTION S29:** inspect E04 counts and native S08/S09 first; implement only read-only native count evidence with explicit partial/complete distinction to avoid licensing via missing emulator count.

## S29 — E04 Win32 Toolhelp game EXE count vs S08 visible HWND evidence / 409 tests PASS
- Added `src/running_count_evidence.py` read-only native `CreateToolhelp32Snapshot/Process32FirstW/NextW` and unique PID match for exact two-space `Thần Long  Mobile.exe`. Reused S08 visible HWND discovery. Independently report game image PID count, visible game HWND count and visible game PID count; errors are UNKNOWN not zero. **Emulator process and combined running total remain None; never passed as an integer to license/limit checks.**
- 19 units and true Windows native test with current `python.exe` Toolhelp PID and two TEST-owned Tk HWND under same PID (neither mislabeled real Thần Long). [S29 Windows 37907306562](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37907306562) SUCCESS: **409/409 units**, native S29 PASS and S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native PASS; artifact 11604554741. Stage S 37907306661 SUCCESS.
- No change to S01–S28 source, PLAN, original ZIP, Dồn; **Proxy excluded**. Genuine game, signed Info, emulator count and suspend/inject/product EXE still unavailable.
- **NEXT_ACTION S30:** audit original emulator/LD process-name/count evidence first; implement scoped read-only emulator process scan only if exact evidence exists, else document blocker and improve partial snapshot provenance, never auto-grant.

## S30 — E04 emulator Windows EXE count unproven; double Toolhelp/HWND provenance, 428/428 PASS
- Audited P01/P02/P05/P06 emulator/LD and E04/C18/E09. ADB serial, android_id and guest game PID are documented, but **no proven original Windows emulator host EXE/count rule**. Therefore no made-up emulator filenames or zero/default count and still no authoritative account-limit aggregate.
- NEW src/running_count_provenance.py wraps existing S29 read-only Toolhelp process snapshots before/after S08 visible game HWND scan. Detects PID churn, mismatched game HWNDs, errors, invalid clocks and stale observations. 2s diagnostic threshold is S30 local (not original). Combined running count always None; no rights grant, game launch, injection or Proxy.
- **[S30 Windows CI 37907996507](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37907996507) SUCCESS: 428/428 S01–S30 tests, native S30 PASS + S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native regressions PASS**. Evidence artifact 11605510692; Stage S 37907996521 SUCCESS.
- All S01–S29 production, frozen ZIP, PLAN, user Dồn spelling unchanged. Real game, signed Info, inject and complete product EXE still NOT AVAILABLE.
- **NEXT_ACTION S31:** audit original ADB serial/Android ID clone mapping; if no exact Windows emulator account formula, add only observational non-authoritative emulator-device identity with staleness, not launch entitlement or ADB auto-start.

## S31 — P02/P05 offline captured ADB serial / clone identity; Windows 450/450 PASS
- New src/adb_identity_evidence.py observes **caller-supplied/captured** ADB transport rows and aid/hwid/IP/guest PID hints only; flags duplicate serials, clone aid/hwid/IP collision, offline or unauthorized rows, stale 30s-local captures and possible serial rebound without automatic rebind. Identity evidence is NOT Windows host emulator-count evidence. No actual `adb.exe`, adb server, ADB/Frida/game process, Proxy or license permission.
- [S31 Windows 37909199630](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37909199630) COMPLETED SUCCESS: **450/450 full S01–S31 units**, native S31 PASS, all S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native regressions PASS. Evidence artifact 11606181801; Stage S 37909199512 SUCCESS.
- Main application still fail-closed until genuine Info service; actual LD/emulator account count, game launch/injection and product EXE NOT BUILT. PLAN/frozen source/S01–S30/Dồn unchanged; no Proxy dev.
- **NEXT_ACTION S32:** independent hint timestamps/expiry and serial reconnect/clone ambiguities in existing offline parser; do not execute adb or infer account total.

## S32 — Offline per-field ADB identity timestamps / 475 Windows tests PASS
- NEW `src/adb_hint_provenance.py` adds independent timestamps for every S31 per-serial Android ID, HWID, guest IPv4 and Android guest PID. Old/unknown/future hints blocked even if the captured ADB transport list is fresh; reverse identity lookup needs all online peers' hint values fresh, clone collisions blocked. Offline→online/appeared/disappeared transitions tracked; new serial sharing fresh aid only POSSIBLE rebind, never verified ownership. Local 30s TTL, not original P02 aid cache.
- **[S32 Windows run 37910397034](https://github.com/ngmthang-g/2222222222222222222222222222222222222222222/actions/runs/37910397034) SUCCESS: 475/475 S01–S32 tests, native S32 PASS and S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 all native PASS.** Artifact 11606311244; Stage S 37910397059 SUCCESS.
- All original source ZIP/PLAN, Dồn label and S01–S31 working source preserved. No actual adb daemon/LD game run, Proxy or license grant; combined emulator/game running total remains UNKNOWN; product EXE still NOT BUILT.
- **NEXT_ACTION S33:** per-serial observation epoch guard after reconnect/reboot, invalidating stale cached hints and never auto-rebinding across clones.

## S33 — Offline serial epoch guard invalidates stale cached aid/IP after reconnect; 497/497 PASS
- NEW `src/adb_serial_epochs.py`: uses existing S31/S32 read-only captured ADB and independent hint timestamps, tracks immutable per-serial online epoch/generation; observed offline/disappearance and externally reported reboot invalidate previously cached aid/hwid/guest IP/guest PID even if their 30s S32 TTL hasn't expired. First-online and reconnected epochs require newly observed hint strictly after boundary; clone identity not automatically rebound; every account-count result remains UNKNOWN.
- **[S33 Windows CI 37911372037](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37911372037) COMPLETED SUCCESS: 497/497 full S01–S33 units + native S33 PASS, all S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native PASS**. Evidence artifact 11606572419; Stage S 37911371950 SUCCESS.
- No real adb.exe/server, LDPlayer/game, license bypass, Proxy or injection; S01–S32 functional source, original ZIP/PLAN/Dồn remain unchanged. Product executable still not built.
- **NEXT_ACTION S34:** offline facade enforcing S31→S32→S33 provenance and replay checks, without exposing authority or guessing emulator counts.

## S34 — Ordered offline ADB intake (S31→S32→S33), 523/523 PASS
- NEW `src/adb_offline_intake.py` ensures caller-provided offline ADB capture passes S31 transport/clone parsing, S32 per-hint provenance and S33 per-serial epoch boundaries in order. Missing/stale/replayed/bad frames reset history; strict diagnostic-only lookup calls S33, never direct weaker S31/S32. Receipt doesn't expose raw legacy structs or authority; no serial can be used to grant device control or compute an authenticated emulator count.
- **[S34 Windows CI 37913166723](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37913166723) SUCCESS: 523/523 S01–S34 units, native S34 PASS and all S33/S32/S31/S30/S29/S28/S27/S26/S25/S24/S23/S22/S21/S20/S10 native regressions PASS**. Artifact 11607239078; independent Stage S 37913166829 SUCCESS.
- No actual ADB/LDPlayer/game, original signed Info, launcher injection or product EXE. PLAN/frozen ZIP/Dồn and existing S01–S33 working code unchanged; Proxy runtime excluded.
- **NEXT_ACTION S35:** audit real app/bootstrap and build path first; prioritize smallest actually verifiable functional UI/runtime slice rather than another purely diagnostic ADB safety abstraction.
