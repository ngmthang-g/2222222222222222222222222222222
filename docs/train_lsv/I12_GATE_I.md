# I12 — Gate I closure

## Decision

**CLOSED_FOR_STATIC_VISUAL_RESEARCH_HANDOFF / END_TO_END_RUNTIME_PARITY_DEFERRED**

Gate I can close at the research-handoff level because:
- the frozen TrainLSV module has been exhaustively split across I01-I11;
- all 44 I01-I11 artifacts were re-inspected;
- the final parity matrix has 80 rows and 0 blocked rows;
- all remaining uncertainty is explicitly classified as runtime-environment-required or micro-detail unknown;
- B06 remains consistent with the frozen UI contract;
- no contradiction was found that invalidates the Phase-I static model.

## Matrix totals

- STATIC_VERIFIED: 24
- RUNTIME_VERIFIED_FROM_EXISTING_EVIDENCE: 3
- RUNTIME_ENV_REQUIRED: 53
- BLOCKED: 0
- TOTAL: 80.

## Existing-runtime scope

Packaged runtime evidence may be reused only for the primitive directly logged.

Safe examples:
- AutoMove / StartAutoPath / StopAutoPath prove movement primitives execute.
- AutoFight_Main proves the shared fight primitive executes.
- action=4 proves the low-level item-action/discard primitive executes.

Unsafe inference:
- those lines do not prove which TrainLSV button/Farm cycle/recovery branch invoked them.

There is no correlated packaged top-level TrainLSV trace.

## Required later runtime work

The authoritative runtime test plan is:

`docs/train_lsv/I12_RUNTIME_TEST_PLAN.json`

It contains 53 Windows/live-game scenarios and must be executed before claiming end-to-end Train LSV parity.

## Frozen Phase-I contract

Do not reopen I01-I11 merely because a later implementation differs.

Only reopen a narrow contract if:
1. the original frozen TLMTool is executed in a controlled Windows/live-game test;
2. the observed original behavior contradicts the current frozen/static contract;
3. the contradiction is captured with evidence;
4. the related I-task artifact and parity row are updated.

## Scope locks that survive Gate I

- TLMTool 2.1.2 remains authority.
- Do not import behavior from older Than Long tools/projects unless the frozen TLM module directly reuses the same shared helper.
- Proxy runtime/network development remains locked.
- Stage S source reconstruction remains locked until the PLAN reaches it.
- B06 is visual evidence only, never behavioral proof.
- RUNTIME_ENV_REQUIRED is not PASS.
- Static absence findings such as no direct TrainLSV PICKITEM enable and no ordinary-Train sell/town cycle remain authoritative unless original runtime directly disproves them.

## Next phase

Proceed to **Phase J — Phó Bản**.

Start from the frozen TLM Phó Bản module/UI and the first PLAN concern: **party formation**.

Do not reuse dungeon automation logic from older external projects as a substitute for TLM evidence.
