# S106 — Windows user-function gap matrix (evidence and running source)

**Scope:** TLMTool 2.1.2 reproduction. Original `PLAN.md`, S105 `NEXT_ACTION`, frozen B04/S59 user screenshots and original source-derived functional contracts. This matrix compares original source evidence to code actually present as of S105, **without modifying working modules**.

## Functional user-visible Windows controls — reviewed against the source

| Original subsystem/control | Original evidence | Existing implementation | Demonstrated Windows-native behavior | Unsolved production parity |
| --- | --- | --- | --- | --- |
| C01/C02 Start HWND discovery | Original executable/class/title, HWND/PID cache flow | `src/start_windows.py`, `start_polling.py` | native enumeration/stale PID fences in S08/S09 tests | No live original game/Info validation |
| C03/C04/C15 Start embedded preview/refresh | DWM source→destination, teardown+refresh | `src/dwm_preview.py`, `src/start_tab.py` and preview modules | native DWM exercises S76/S88 | Some original visual/metadata parity unverified |
| C05 master switch and C17 preview arrows | Radio master identity, preview order HWND-keyed | `src/start_tab.py`, `src/preview_layout.py` | S14/S83 and S59 tests | Original live RoleName and C19 input sync unavailable |
| C10 **Xếp gọn** | move each current window to (0,0), preserve dimensions | `src/window_stacking.py`, `start_tab.py` S55/S56/S59 | S59 real *clickable* measured original control, S67 native move/readback | Info entitlement and 1s Auto-tiler precedence unresolved |
| C11 **Xếp chéo** | move master-first to (0,0),(50,50)… | Same S55/S56/S59 | Same native tests | Ditto |
| C12 **Ẩn hết** | native move (-2200,-2200), keep size, do not `SW_HIDE` | `src/window_hide.py` S57 | S57 genuine Win32 offscreen move, S58 genuine verified layout reset | **No end-user C12 toggle wired**: unproven combined hide→show behavior |
| C12 **Hiện hết** | generic restore old rectangle **conflicts with** explicit (0,0) restore log/doc | Deliberately no `show/restore` implementation | **Not tested/implemented** | Need original released binary execution branch evidence; DO NOT guess |
| C12 reset after layout | Re-layout visibly moves windows and clears hidden-state bookkeeping | `C12HideAll.reset_after_verified_layout`, S58 | Native S58 drives C11 real `SetWindowPos` then verifies reset; NOT a new function to rewrite | Full original Auto mode and C12 show still blocked |
| C14 detached preview | real DWM overlay host and C13 close / C14 refresh | `src/detached_host.py` et al. S68–S85 | S84 actual DWM **Đóng xem**, S85 actual DWM refresh with *external test-only placements* | Exact original detached tile geometry, embedded preview hide/restore sequencing, genuine open toggle unsupported |
| C16 **Đóng hết** | source-only normal `WM_CLOSE` to game HWND | `src/close_windows.py`, `start_tab.py` | native test-owned HWND closure in S16 | CrashHandler target/cleanup policy, exact post-close UI refresh not recovered |
| C18 layout maintenance | original Start grid-driven worker, master selection | `src/layout_windows.py`, `start_tab.py` | native SetWindowPos on test-owned HWNDs | Original exact grid arithmetic/cadence and true entitlement not verified |
| C19 input synchronization | original per-window/mouse/keyboard behaviors partly extracted | `docs/window/C19_INPUT_SYNC_FLOW.md` (partial contract) | **No production full input sync engine demonstrated** | Exact atomic event pipeline and trusted runtime/protocol not proven |
| F05/F06 launch/login | process package/launch/profile dependencies | offline input validation S26–S28, partial `login_tab.py` | safe local input/win32 tests only | Genuine Info, process lifecycle, game-end-to-end, no fake launch |
| E03 Info | signed permissions/heartbeat gate | passive Info + conservative permission model, `TLMTool.py` exits 2 | packaged S36 diagnosis | Original signed issuer, trusted RPC and live entitlement absent |
| Party G02/G03/G10 | account names, own RoleID, team state/actions | S89–S103 partial UI and test-external diagnostics | real Windows **test-owned** PID/HWND, no game reads | Genuine per-client readers, signed Info and actual team actions absent |

## S106 finding

**No uncovered Windows function with *both* a fully proven original end-to-end behavior and an actually missing implementation could be substantiated from this source audit.** Existing proven engine operations are already implemented and/or native tested. Gaps that appear usable are blocked by ambiguous original paths or absent live client/Info providers. Therefore adding another native wrapper or a visual-only control would be duplicate or false parity, prohibited by the authoritative PLAN.

The S106 improvement is an explicit cross-feature Windows native regression gate covering **original measured S59 clickable C10/C11 buttons, S57 hide/S58 real re-layout, S67 post-move Win32 readback, S84 C13 DWM native close, S85 C14 native refresh** and the most recent S102 Party Win32 regression. No original code and no permission policy are changed.

## Test/evidence boundaries

- The named tests use actual Win32 HWNDs and native DWM/SetWindowPos on **test-created Python/Tk windows**. A test identity wrapper presents original game-like class/title only in the smoke-test process. It is not a production entitlement or original game source.
- S85 native test uses an explicitly TEST-ONLY caller-provided detached geometry; it does **not** establish original unknown C14 tile coordinates.
- `python src/TLMTool.py` must continue to return code **2**, without opening a product GUI. A diagnostic EXE package can compile without the functional product existing.
- Tests can verify our implemented behavior, not original TLM/game end-to-end without authorized original executable and genuine game runtime.

## NEXT_ACTION — S107

Prioritize **closing a genuine product capability gap** by obtaining authoritative evidence of one missing full action path (C12 restored location branch and Auto state, C14 detached placement+embedded lifecycle, C19 input sync, F05 game-launch or real Info service) before implementing. Start by revisiting the existing untouched evidence rather than rewriting passing native primitives. Where original evidence cannot disambiguate behavior, classify it BLOCKED and explicitly record the exact proof required. Do not add another simulated Party name/UI adapter. Keep locked PLAN, ZIP, B04/S59 and Proxy no-development unchanged.
