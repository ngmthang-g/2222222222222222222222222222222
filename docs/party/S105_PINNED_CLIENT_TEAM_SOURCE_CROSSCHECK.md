# S105 — Cross-repository Party client state-source audit (pinned evidence)

**Status: original client-side state semantics SOURCE-DOCUMENTED; external EXE reader NOT ESTABLISHED.** This report intentionally makes no source/runtime modifications. The selected S105 task was to verify a legitimate live-data route, not to add yet another TEST-only adapter.

## Reproducible inputs

- Reconstruction target: `ngmthang-g/2222222222222222222222222222222`, LIVE unchanged `PLAN.md` and S104 `STATE.md`, `docs/party/S104_REAL_PROVIDER_DEPENDENCY_INVENTORY.md`, plus original-derived G02/G03/G10.
- Separate frozen-client analysis repository **`ngmthang-g/clinent-game-than-long-DATA-2222`**, `main` commit **`9dbcbe2bf6c83b016dde2a1a9084d40882153d46`** (fetched live on S105). No code copied from this repo.
- [Client team runtime analysis](https://github.com/ngmthang-g/clinent-game-than-long-DATA-2222/blob/9dbcbe2bf6c83b016dde2a1a9084d40882153d46/analysis/25_TEAM_RUNTIME_FOLLOW.md), [client party build context](https://github.com/ngmthang-g/clinent-game-than-long-DATA-2222/blob/9dbcbe2bf6c83b016dde2a1a9084d40882153d46/contexts/BUILD_PARTY.md), [game semantic API catalog](https://github.com/ngmthang-g/clinent-game-than-long-DATA-2222/blob/9dbcbe2bf6c83b016dde2a1a9084d40882153d46/database/AUTO_TOOL_API_CATALOG.md), [runtime snapshot contract](https://github.com/ngmthang-g/clinent-game-than-long-DATA-2222/blob/9dbcbe2bf6c83b016dde2a1a9084d40882153d46/analysis/35_RUNTIME_SNAPSHOT_CONTRACT.md), [main-thread bridge context](https://github.com/ngmthang-g/clinent-game-than-long-DATA-2222/blob/9dbcbe2bf6c83b016dde2a1a9084d40882153d46/contexts/BUILD_MAINTHREAD_BRIDGE.md), and [bootstrapping evidence rules](https://github.com/ngmthang-g/clinent-game-than-long-DATA-2222/blob/9dbcbe2bf6c83b016dde2a1a9084d40882153d46/AI_BOOTSTRAP.md).
- These are source-analysis documents reporting Lua/runtime semantics. This S105 audit did **not** independently run the original game, inspect live game memory, make network calls, or verify TLM's externally delivered reader.

## What the client knowledge DOES supply

| Question | Client-side evidence | Relevance to original TLM Party | Access from reconstructed EXE |
| --- | --- | --- | --- |
| Current local team state | `Game.RoleData.TeamID` consumed by shipped Lua | Possible source of per-character TeamID, but not proof of the same value returned by original TLM `memory_items.read_team_id(hwnd)` | **No authenticated/external reader exists in current repo** |
| Team member roster | `C_TeamData.TeamMember[]` under a joined local team; observed fields `RoleID, RoleName, Level, FactionID, MapID, Hp, MaxHp, AvartaID, PosX, PosY` | Candidate semantic source for current-team snapshot; G03's action `read_own_ids` is NOT equivalent to reading teammates | Not exported to TLM's Windows process; no valid bridge demonstrated |
| Update lifecycle | `G_TCPEventType.UpdateTeamData` updates `C_TeamData`; a disband event clears transient state | Suggests observing events could reduce stale state, but does NOT prove a thread-safe external subscription or freshness guarantees | Not established |
| Local role data | Client `Game.RoleData` has `Name`, `TeamID`, `Level` in shipped Lua | Candidate for the actual per-window display name; TLM expects `utils.get_character_info(hwnd)['RoleName']`, and `Game.RoleData.Name` is a **different source/schema** until runtime parity is proven | Unavailable |
| Other player records | `Game.GetNearByPeacePlayers` and selected-target APIs give nearby player's Name/RoleID | Nearby-player state is NOT a reliable all-logged-in-account `read_own_ids()` replacement | No general own-account aggregation evidence |
| Main-thread requirements | Client KB documents Unity `MainThread.Execute(Action)` queue, safe call/thread ownership, snapshot-copy rules | Matters for any future in-client adapter; S105 does not construct callbacks/hooks or install any plugin | No verified authorized integration pipeline in TLM reconstruction |
| Original TLM role records | G03 `memory_items.read_own_ids()` returns `(pid, RoleID, Name, Lv)`; `read_team_id(hwnd)` returns sentinel-aware TeamID | This is **authoritative original TLM contract**; cannot be replaced with client team-member roster or name guessed from window title | S94 models it with external TEST callbacks, not real readers |
| License/entitlement | TLM Info service requires an independently verified signed entitlement and heartbeat | Must precede production tab activation and any real user action; not supplied by the game Lua repository | **BLOCKED**, do not simulate |

### Important non-equivalences

1. `C_TeamData.TeamMember` lists **members of one in-game team**; TLM's `read_own_ids` lists separate local logged-in player windows/pids. There is no evidence that one may substitute for the other.
2. `Game.RoleData.TeamID` is client-local current team state, whereas TLM's `read_team_id(hwnd)` is an **external per-Windows-HWND** query. Matching numeric semantics in documents is not proof of a stable or permitted external bridge.
3. `Game.RoleData.Name` is not automatically the exact (possibly markup-bearing) `utils.get_character_info(hwnd)['RoleName']`. Name normalization must be validated on the same actual character and HWND/PID.
4. `MainThread.Execute` semantics in a separate client research project do **not** supply authorization, a safe loader or a verified external game-process connection for this TLM EXE.
5. Static client configuration and metadata cannot reveal what team or player data is **currently loaded** in a running session.

## Integration acceptance sequence (not yet fulfilled)

First establish a **documented, legitimate, authorized** supported read-only client snapshot boundary, with a current per-PID process identity and copy-out semantics that do not rely on stale managed object pointers. Demonstrate actual game values for local name, local TeamID, local role identity if exposed, and consistent revision/epoch on changing windows/map/team states. Validate these against actual game UI and distinct multi-account HWND/PIDs, including logout, closed/reused HWND, maps and disband. Only then compare fields with the original TLM's `utils.get_character_info`, `read_own_ids` and `read_team_id` behavior. Never silently fill unknown RoleID or guess source offsets.

Separately establish genuine TLM Info licensing/provider permission using the authorized issuer and real service specifications. There is no reason to infer TLM authorization from the game client's local state. The original G09/G10 team actions and B04 UI are a later gated stage; **no game/team actions were implemented or issued by this task**.

## Alternative original-backed feature review

- C12 original "Ẩn hết" has a proven offscreen move; S57 already implemented/tested that hide primitive. "Hiện hết" retains a documented original conflict: restore previous window rect vs force (0,0), so adding a guessed show-side button would violate `PLAN.md` and `docs/tasks/C12.md`.
- C14 Tách rời has original DWM geometry/bars, but its exact embedded preview visibility/restoration sequence remains unknown. A fake detached button cannot count as a completed working feature.
- F05 launcher inputs and PID-specific HWND discovery were already validated offline (S26–S28), but production launch authorization and exact loader/process lifecycle remain blocked. Rewriting existing validation provides no value.
- The safer next high-value step is a narrow **verified existing Windows-native lifecycle or UI behavior** only where original-source evidence is complete, *not* another synthetic Party identity wrapper. If no such behavior can be chosen, retain the missing-provider blocker and request legitimate runtime evidence rather than guessing.

## Tests and file scope

S105 performed source verification and documentation only. **No `src/`, `tests/`, native Windows workflow or packed EXE was changed, so this is NOT a new Windows CI run.** Most recent real baseline remains [S103 Windows CI 38062644606](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38062644606) (**1564/1564**, **269** AST+compiled, inherited native S102–S76 passes); the separate [S36 diagnostic build 38062487870](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38062487870) passes but exits **EXPLICITLY_BLOCKED_NO_GUI** as intended.

Changed in S105: this evidence document; `docs/tasks/S105.md`; append-only `STATE.md` and `PROJECT_STATUS.md`. Locked original ZIP, original B04/S59, `PLAN.md`, previously verified sources, and the ban on Proxy development unchanged.

## NEXT_ACTION — S106

1. Reread LIVE `PLAN.md`, `STATE.md`, S105 and the original evidence for **one real original-backed user-facing Windows lifecycle task**. Do not repeat S89–S103 or invent in-game data readers.
2. Prioritize a complete, demonstrable non-auth-dependent native capability that original TLM uses and is missing from implemented source, if original branch behavior is fully evidenced. Only change the scoped module after identifying exact source differences and a real two-PID Windows proof; otherwise explicitly mark candidate blocked and choose another proven feature. C12 show/C14 detach cannot be marked done while their original ambiguity persists.
3. Run Windows 1564-test baseline, S86 269 compiled, relevant native regressions and S36 diagnostic if code changes. Append actual results, blockers, changed files and `NEXT_ACTION S107`. All original, license, Proxy and UI locks remain intact.
