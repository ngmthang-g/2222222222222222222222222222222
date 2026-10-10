# S104 — Party original data dependencies and practical integration blockers

## Purpose and scope

This is an evidence-only inventory. It does not modify runtime code or claim that the tool reads actual game characters. Reviewed the LIVE locked `PLAN.md`, `STATE.md` S103 checkpoint, G02/G03/G10/G12 Party records, S87 provider assessment and the current `src/` tree on GitHub (1,394 tree entries; 66 Python source modules). It also reviewed `src/TLMTool.py`, `permission_guard.py`, `info_state.py`, `info_binding.py`, `party_roster.py`, `party_rolename_source.py`, `party_team_identity.py`, `party_action_coordinator.py` and S100–S103.

## The exact dependency chain

| Layer | Original-backed contract | Implemented and testable today | Missing to achieve real game parity |
| --- | --- | --- | --- |
| Start identities | Shared live HWND/PID cache | S08/S09 producer and native checks; S90 Party consumer | Validate against actual supported client processes |
| Display role name | `utils.get_character_info(hwnd)['RoleName']`, tag-filtered | S64 `RoleReading`, S90 roster, S100 externally supplied callback | Real, reliable and authorized character information reader. No `src/utils.py` is present in the HEAD tree |
| Saved Party configuration | Human-readable group names in shared settings.ini | S89 config, S91 existing ready Combo, S101/S102 stale-handling and saved/offline metadata | Bind production widget lifecycle only after genuine role display source exists |
| Own-account ID | `memory_items.read_own_ids()` providing (PID, RoleID, Name, level) | S94 parser, name matching, native generation checks; S103 read-only comparison | Actual supported and authorized own-account data source. No `src/memory_items.py` is present in the HEAD tree |
| Team state | `memory_items.read_team_id(hwnd)` where 0 and max unsigned indicate no team; None unreadable | S94/S95 classification/wait, S96–S99 immutable observations | Actual live team-state reader and life-cycle confirmation |
| Permission and startup | Verified Info state and permitted feature access | S02 `PermissionGuard` state, S03 passive Info, S04 binding, S92 fail-closed coordinator | Legitimate externally verified production Info service; existing S87 evidence reports missing trustworthy provider and lifecycle |
| Team orchestration | G09 worker lifecycle and original G10 B0–B3 team state transition | S92 coordinator; S94–S103 read-only tests | Production team interaction/execution source with real-game evidence and authorization; no `src/party_protocol.py` is present |
| Full Party UI | B04/G01 actual controls, running/stop states | S89 config editor + S91 ready list as composable partial widgets | Original full PartyTab wiring and complete verified user actions |
| Packaged user product | Correct Info service, functionality and visual/runtime parity | S36 packaged diagnostic artifact | `src/TLMTool.py:main()` intentionally exits 2 with `EXPLICITLY_BLOCKED_NO_GUI`; not a functioning product |

## Important findings

1. **Existing models and native test infrastructure are not the missing live reader.** S100's character callback, S94's own-account and team callbacks, and S103's matching records are explicitly supplied by test/external code. Their successful fixtures cannot establish that any real game bytes were read.
2. **No permission should be inferred from a callback success.** `PermissionGuard` requires independently verified claims, `InfoState` accepts a verifier dependency rather than implementing transport, and S87 already records the absence of a legitimately configured issuer/service. Native process ownership checks are necessary but not proof of feature authorization.
3. **Runtime names and IDs have separate roles.** A saved name or S90 display label must never stand in for current process-specific own-ID data. Original G03 resolves numeric action identity at use time; neither TeamID nor RoleID belongs in saved group configuration.
4. **Do not add another presentation-only layer as if it were product progress.** The S90–S103 read-only path has comprehensive synthetic regression coverage, but genuine input providers and game operation wiring are the actual blockers. A new unit test around invented data is not a substitute for a real-world integration proof.
5. **Scope remains locked.** Proxy development stays disabled; do not change frozen original ZIP, PLAN, baseline B04 or S59, or edit previously passing modules for an evidence-only audit.

## Minimal next integration acceptance gates

Before claiming a user-facing Party tool works, verify a legitimate data source and reproducible test environment that demonstrate: (a) a real running supported client window with a stable native HWND/PID generation; (b) a correct real RoleName that agrees with character data; (c) current own account identity and team state read through documented, permitted interfaces; (d) explicitly verified Info permissions; (e) tested real Party behaviors, UI lifecycle, failure/cancellation paths; (f) packaged EXE launched successfully with these inputs. A test-only callback cannot satisfy any missing gate.

This report does not claim those preconditions have been obtained. It recommends auditing available original client documentation and sanctioned interfaces before implementing actual providers. Distinguish proven contracts, unavailable dependencies and uncertainty.

## Technical evidence

- Original Party: `docs/party/G02_PARTY_HWND_FLOW.md`, `G03_PARTY_CHARACTER_STATE_FLOW.md`, `G10_PARTY_TEAM_PROTOCOL_FLOW.md`, `G12_PARTY_RECONSTRUCTION_HANDOFF.md`.
- Reconstructed state: `src/party_rolename_source.py`, `party_team_identity.py`, `party_roster.py`, `party_ready_list.py`, `party_saved_role_identity.py`, `party_action_coordinator.py`, `info_state.py`, `permission_guard.py`, `TLMTool.py`.
- Prior report: `docs/tasks/S87.md`; test evidence: `docs/tasks/S103.md`.

## Test claim boundary

No source code was changed in S104, so no new GitHub Actions run was triggered or required for this documentation-only milestone. Immediately previous **S103 verified** [Windows workflow 38062644606](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38062644606) completed successfully with **1564/1564** Python tests, **269** AST/compiled files, and inherited test-owned native checks. [S36 diagnostic run 38062487870](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38062487870) was successful but remains diagnostic only.

## NEXT_ACTION — S105

Reread LIVE PLAN.md/STATE.md and this report. Check whether any genuine, explicitly available, permitted original client API or adapter specification satisfies one of the missing data-source inputs. If evidence is absent, do not fake the provider or make a runtime implementation claim; document the exact requirement and prioritize another original-backed, demonstrably working functional gap. Preserve the S103 passing baseline and locked original scope.
