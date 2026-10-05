# Gate H — Train research handoff

## Result
**CLOSED_FOR_STATIC_VISUAL_RESEARCH_HANDOFF / END_TO_END_RUNTIME_PARITY_DEFERRED**

H01–H14 recovered and locked the Train contracts for:
- UI/module/config lifecycle;
- return-town modes;
- bag/full behavior;
- periodic timing;
- movement/Truyền;
- treatment;
- death/respawn;
- reconnect;
- pickup/filter;
- mount/remount;
- saved coordinates;
- account rows/tracker;
- manual all-account commands;
- full Farm start/stop FSM.

H15 then audited available runtime evidence instead of treating static recovery as runtime proof.

## Existing runtime evidence
The exact frozen archive includes:
- live UI screenshots supplied in this project;
- `data/automove_log.txt` with actual helper execution records.

Those records verify low-level execution primitives such as:
- AutoMove / StartAutoPath / StopAutoPath;
- AutoFight_Main invocation;
- Game.SendToggleRideState;
- Game.GoTo;
- NPCShop probing;
- ItemAction action=4.

They do **not** prove full top-level Train transitions or successful end-to-end completion.

## Runtime reservation
The current environment cannot execute the Windows original tool against a live game client.

Therefore all top-level user-visible runtime cases are explicitly preserved as `RUNTIME_ENV_REQUIRED` with a concrete Windows test plan.

No runtime result has been fabricated.

## Gate meaning
Gate H is closed in the same sense as earlier research gates:
- enough evidence exists to hand the Train subsystem to later reconstruction without reopening the research plan;
- unresolved runtime-only edges remain named and testable;
- Stage S has not begun;
- future original-vs-reconstruction testing must run H15's Windows matrix before claiming Train runtime parity.

## Next phase
Proceed to **I — Train LSV** research.
