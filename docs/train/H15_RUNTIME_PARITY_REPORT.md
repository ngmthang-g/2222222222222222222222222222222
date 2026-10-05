# H15 — Train runtime parity report

## 1. Scope and method

H15 does not re-derive H01–H14. It asks a stricter question: **which Train contracts have actual runtime evidence, and which still require the original Windows TLMTool + live game?**

The allowed classifications are exactly:

- `STATIC_VERIFIED` — frozen binary/config/screenshot structure is sufficient for the stated contract, but this is not a runtime behavior claim.
- `RUNTIME_VERIFIED_FROM_EXISTING_EVIDENCE` — a supplied live capture or packaged runtime trace directly demonstrates the stated limited behavior.
- `RUNTIME_ENV_REQUIRED` — end-to-end behavior requires Windows + live Than Long and cannot be truthfully executed in the current Linux analysis environment.
- `BLOCKED` — no viable verification path is currently known.

H15 has **no BLOCKED user-visible cases**. The unresolved runtime cases all have explicit Windows tests.

## 2. Frozen specimen recheck

The archive and executable were re-hashed before classification:

- archive: `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`
- inner EXE: `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`

The Train screenshot was also re-hashed:
- `17d98f6b6a263daa5857224d100355379672eae7bd7c72794323f31417d8bc53`

It remains byte-identical to B05.

## 3. Existing runtime evidence discovered in the supplied package

The frozen archive itself contains a large runtime trace:

`TLMTool.dist/data/automove_log.txt`

Properties:
- SHA-256 `17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`
- 15,741,058 bytes
- 387,238 lines
- extracted/archive timestamp: 2026-10-01 20:13:16 UTC

High-signal observations:

| primitive | records | runtime scope |
|---|---:|---|
| AutoMove queued | 16,040 | queue primitive observed |
| StartAutoPath called | 15,993 | autopath start primitive observed |
| StopAutoPath called | 2,027 | autopath stop primitive observed |
| AutoFight_Main | 8,511 | internal auto-fight UI/Lua invocation observed |
| SendToggleRideState | 1,579 | mount toggle command observed |
| Game.GoTo | 114 | native cross-map helper observed |
| NPCShop probe | 114 | shop-UI probe observed |
| ItemAction action=4 | 22,732 | whole-stack/action=4 item operation observed |

Examples from one PID show a real sequence containing AutoFight invocation, mount toggle, AutoMove/StartAutoPath and later action=4 item operations. That is meaningful primitive-level runtime evidence.

However, the trace does not annotate each record with:
- Train button name;
- Farm cycle generation;
- H02/H03 town mode;
- H11 preset name;
- H14 global/single start source;
- success/arrival result for every operation.

Therefore it cannot be used to claim end-to-end Train parity.

## 4. What is genuinely runtime-verified already

The existing evidence directly verifies only limited scopes:

### Visible stopped UI
The supplied Train screenshot directly proves the stopped/default Train page rendering. The StartTab screenshot directly proves its stopped quick Farm label is `Train`.

### Movement primitives
The packaged trace proves the original package has actually executed:
- AutoMove queueing;
- StartAutoPath;
- StopAutoPath;
- Game.GoTo.

This supports H05's low-level execution surfaces, but does not prove:
- 8-tile near-skip correctness;
- arrival tolerance;
- Truyền retry/fallback semantics;
- which Train button caused an invocation.

### Fight primitive
`AutoFight_Main` appears 8,511 times across 91 PID-tagged processes. This proves internal auto-fight invocation executes in real sessions.

It does not prove H13's all-account fan-out, sell-conflict skip, or H14 full Farm FSM.

### Mount primitive
`Game.SendToggleRideState(Game.CurrentMountSlot)` appears 1,579 times across 28 PID-tagged processes.

It does not prove the 3-second IsRiding verification or remount/requeue result.

### Discard/item-action primitive
`ItemAction ... action=4 dbID=...` appears 22,732 times.

This is consistent with H09's whole-stack action=4 discard primitive, but it does not identify which keep-mode or pre-town filter branch caused a given action.

### Shop probe
The trace contains 114 `GUI.FindUI('NPCShop')` executions. It proves the shop-probe primitive ran.

No literal `RequestSellItem` or packet `200036` was found in this packaged trace, so actual Train sale completion remains runtime-required.

## 5. What remains Windows-runtime required

The runtime matrix intentionally keeps all top-level/stateful cases open, including:

- global Bắt đầu/Dừng transitions;
- per-row ▶ / II / … lifecycle;
- partial stop and last-account stop;
- ordinary orange `Đang dừng...` coverage;
- StartTab/FarmTab active-state synchronization;
- all-account parallel fan-out;
- sell/fight conflict skips;
- full-bag threshold;
- periodic timing;
- near-skip/arrival and Truyền fallback;
- treatment;
- death/Địa phủ;
- reconnect;
- hidden PICKITEM enable;
- keep-mode end-to-end filtering;
- IsRiding verification/remount;
- saved-coordinate persistence/rename;
- 5s row refresh behavior;
- tracker arithmetic;
- PID-reuse teardown;
- denied permission/account-limit behavior;
- full Farm-cycle sequence;
- rapid stop/start stale-generation protection;
- worker-drain UI timing;
- resize monitor;
- actual sell completion.

These are not failures. They are simply not executable in the current environment.

## 6. Existing evidence that must NOT be overinterpreted

The packaged log has no per-line version marker. Its presence inside the exact frozen archive makes it evidence associated with the supplied package, but H15 does not assert that every line was produced by the final 2.1.2 UI path.

Similarly:
- no `PICKITEM` string in the log does not mean hidden pickup never works;
- no `200036` string does not mean sale never works;
- no reconnect labels do not mean reconnect never ran.

Absence from this helper log is not a negative runtime verdict.

## 7. Gate H result

H01–H14 are complete static/visual research tasks. H15 now provides:
- runtime evidence inventory;
- explicit parity classification;
- exact Windows test matrix;
- exact unresolved observations to collect later.

Therefore:

**Gate H static/visual research and reconstruction handoff: CLOSED.**

**End-to-end Train runtime parity: DEFERRED / WINDOWS ENVIRONMENT REQUIRED.**

Stage S remains out of scope at this point. The next PLAN research phase is Train LSV.
