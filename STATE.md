# STATE — TLMTool 2.1.2

## STATUS
IN_PROGRESS

## GATE A
**COMPLETE / VERIFIED**

## GATE B
**COMPLETE / VERIFIED**

## GATE C
IN_PROGRESS

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
- B13 VERIFIED_WITH_EXPLICIT_UNKNOWN_FONT_POINT_SIZE
- B14 VERIFIED
- C01 VERIFIED_WITH_EXPLICIT_UNKNOWN_BOOLEAN_FORMULA

## C01 VERIFIED RESULTS
- Recovered two original window-discovery paths:
  - `start_tab.get_windows()`
  - `coordinate_utils.get_game_windows()`
- Verified top-level enumeration with `EnumWindows`.
- Verified `IsWindowVisible` filtering.
- Verified non-blocking title read with `SendMessageTimeoutW`, timeout **150 ms**.
- Verified class/process lookup through:
  - `GetClassName`
  - `GetWindowThreadProcessId`
  - `psutil.Process`
- Verified discovery constants:
  - normalized process literal `thần long mobile.exe`
  - class `UnityWndClass`
  - title-side predicates `WINDOW_NAME` / `_title_matches_game`
- Shared coordinate helper contains title constants:
  - `Thần Long  Mobile`
  - `Thần Long Mobile`
  - `Lineage W`
  - `DEFAULT_WINDOW_TITLES`
- Exact final AND/OR grouping among process/class/title predicates remains explicit UNKNOWN because readable compiled constants do not prove the source expression.
- Verified refresh clocks:
  - Start UI window-list poll: **2 s**, stops when leaving Start, restarts on return
  - background EnumWindows + character info: **~3 s**
  - heavier memory info: **~8 s**
  - preview display delay: **800 ms / 2000 ms** depending on account count; threshold remains UNKNOWN
- Verified worker-cache architecture: UI consumes a background cache instead of blocking main Tk thread.
- Verified strict explicit-title resolver:
  - exact `FindWindow` title
  - no match => `(0, "")`
  - no first-HWND/default-title fallback
- Verified Start discovery contains a `FAKE_ACCOUNTS` synthetic/debug path separate from real EnumWindows HWNDs.
- Initial `WINDOW_BEHAVIOR_MATRIX.md` created.

## C01 FILES
- `docs/tasks/C01.md`
- `docs/window/C01_WINDOW_DISCOVERY_STATIC_EVIDENCE.tsv`
- `docs/window/C01_DISCOVERY_FLOW.md`
- `WINDOW_BEHAVIOR_MATRIX.md`

## CURRENT_TASK
C02 — mapping HWND ↔ nhân vật.

## BLOCKERS
None known for C02.

## DO_NOT_TOUCH
- Preserve Gate A forensic baseline unchanged.
- Preserve Gate B visual contract unchanged.
- Do not turn C01's unknown Boolean grouping into a claimed fact.
- Do not begin C03 before C02 is verified.
- C02 must determine how character identity is associated with each HWND from original evidence.

## NEXT_ACTION
On CONTINUE:
1. Read `PLAN.md`.
2. Read `STATE.md`.
3. Execute **C02 only**.
4. Inspect original binary/static evidence for HWND → PID/process → memory/character identity mapping.
5. Identify caches, keys, invalidation/rebind behavior and fallback rules only where evidence supports them.
6. Update `WINDOW_BEHAVIOR_MATRIX.md` and persist C02 evidence/report.
7. Advance to C03 only after C02 is verified.
