
# STATE — TLMTool 2.1.2 reconstruction

_Last verified checkpoint 2026-10-12 Asia/Bangkok. Authority PLAN.md + SCOPE_LOCK.md. History append-only PROJECT_STATUS.md._

## S146 VERIFIED — native Win64 C12 specifically documented show-to-(0,0) branch; FULL UI TOGGLE STILL BLOCKED

### Original evidence / scope
- Resumed LIVE PLAN.md / STATE.md S145 NEXT_ACTION S146 / PROJECT_STATUS.md, S145, F06, E05, C12, S57/S60 and current Start/Win32 modules. Pinned original TLMTool ZIP SHA256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd and inner EXE SHA256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22 statically inspected without running them. No verified F06 login1/login2 original x/y/RGB/tolerance reference was found; data/config.dat is an opaque MZ/PE, not a plaintext pixel definition. DO NOT fabricate.
- C12 original SPECIFIC show doc/log says move every HWND to (0,0) and PRESERVE sizes; original hide is (-2200,-2200) without SW_HIDE. The original GENERIC toggle doc separately says return to previous positions and saved rectangles are recorded. This contradiction is explicitly UNSOLVED, so do not wire or claim the complete Start two-way “Hiện hết” control.

### Actually completed
- Narrow EDIT only src/window_hide.py: C12HideAll.show_documented_origin() implements specifically proven zero-origin branch, NOT general show()/restore() and NOT wired to GUI. Requires fully verified HIDDEN state, positive external window limit, live separately authorized callback, complete matching cached+saved HWND/PID and native top-level game identity proof. Precheck ALL HWNDs are still at (-2200,-2200), same original size, before native action.
- Real NativeLayoutBackend.move_no_resize(hwnd,0,0) uses SetWindowPos(SWP_NOSIZE|SWP_NOZORDER|SWP_NOACTIVATE), then actually reads GetWindowRect and checks target (0,0), same width/height, fresh PID after EACH move. Only after ALL succeed is hidden state cleared. PARTIAL/no-op/stale/permission revoked transitions cannot claim success or silently retry. No mouse, keyboard, game process, native DLL, Info or Proxy touched.
- NEW tests/test_s146.py 20 cases, tools/S146_WINDOWS_C12_SHOW_ORIGIN_SMOKE.py native proof with TWO real Windows Tk test-owned HWNDs and original hide→show action, .github/workflows/s146-c12-document-origin.yml, docs/tasks/S146.md, docs/memory/S146_C12_ORIGIN_BRANCH_EVIDENCE.json. Prior source modules S01–S145 preserved apart from narrow C12 module extension; original zip/assets/PLAN immutable, DATA-2222 READ-ONLY, Proxy excluded.

### Verified final Windows evidence
- [S146 full Win64 run 38163848439](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38163848439), job 114542178613 COMPLETED SUCCESS: 2,311 / 2,311 full Python unit tests, 376 compiled .py, 97 production src modules; PASS_S146_REAL_WIN64_C12_DOCUMENTED_ZERO_ORIGIN_TEST_OWNED_NO_GAME; 11 / 11 actual Win32 two-HWND position/size/IsWindowVisible/authorization tests PASS. Inherited S145 PrintWindow, S144 WM_CHAR, S143 C19 real geometry, S142/S141 Login, S140 12/12 actual self-owned Win64 reads and all S139–S116 Train/Party/Login native PASS. Original Info product gate S146_PRODUCT=EXPLICITLY_BLOCKED_NO_GUI_NOT_PRODUCT; test artifact 11710374577 TEST ONLY.
- [Independent S36 diagnostic Windows run 38163848387](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38163848387) COMPLETED SUCCESS — EXE remains DIAGNOSTIC ONLY, NOT TLM product. [Stage S regression 38163848465](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/38163848465) SUCCESS. Initial intermediate S36 38163665031 and Stage S 38163665085 failed because newly authored test AST referred to the uncommitted native S146 smoke; complete source/tests final builds GREEN.

### Blocking / immutable
- Exact released app C12 previous-position vs zero-origin show branch UNKNOWN; GUI toggle NOT wired. Original signed Info server/heartbeat, compatible live GameAssembly+RoleData/bag, real game login RGB and F05/F06, C07 auto role sorter, C14 detached geometry, C19 slave hooked native input, multiple missing tab builders, full source/UI/runtime parity and product EXE still BLOCKED. Test-owned two-HWND movement is not game runtime proof.
- Original ZIP/EXE, PLAN.md, SCOPE_LOCK.md, B04/S59 screenshot and previously passed source frozen; DATA client repo READ ONLY; no Proxy development.

## NEXT_ACTION S147
1. Read LIVE PLAN.md / STATE.md / PROJECT_STATUS.md / docs/tasks/S146.md and original C12 conflict; recover the genuine released UI show branch from verifiable source or authorized game tracing BEFORE wiring Start toggle. If unavailable, prioritize another source-backed meaningful user-facing Windows/Tk action with real native test rather than adding merely synthetic fixtures.
2. Do not infer old-position restoration, game auth, login pixels or DLL input messages from tests; do not modify previously correct sections.
3. For source edits demand >=2311 full Win64 tests, >=376 compiled, inherited S146–S116 native and separate S36 packaged diagnostic+Stage S fail-closed; update exact files, blockers and NEXT_ACTION S148 in STATE.md and append PROJECT_STATUS.md.
