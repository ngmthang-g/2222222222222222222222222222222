# P03 — Original `emu_input`: ADB actions, capture, pixels and error boundaries

## 0. Authority / scope
Continues the confirmed `NEXT_ACTION` after P02; no prior gate/task rewritten. Read `PLAN.md`, `STATE.md`, `PROJECT_STATUS.md`, `docs/tasks/P02.md`, earlier D07/P01 and the user-supplied original TLMTool 2.1.2 ZIP before analysis. Current GitHub had **no `docs/tasks/P03.md`** at task start. This is read-only static archaeology, **not** recovered Python source and **not** live emulator parity.

- Original ZIP SHA-256: `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; **1,050 entries, ZIP CRC clean**.
- Original inner EXE: `TLMTool_2.1.2/TLMTool.dist/TLMTool.exe`; 47,450,112 bytes; SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Exact module marker `<module emu_input>` at **0x293325f** (prefix `u` at 0x293325e). The serialized constants containing `.emu_input`, symbols, docs and method names are at **0x2932e35..0x293325f**, i.e., *before* the marker; `0x2932e35` is not the start of recovered Python source. The adjacent farm-tab marker is at 0x2932983; do **not** conflate their methods or take offsets after emu_input marker as a second source module.

## 1. Observed original AdbInput API (exact compiled method-name strings)
| Symbol | Binary offset | Contract / confidence |
|---|---:|---|
| `AdbInput.__init__` | 0x2933173 | Constructor; exact default argument order remains UNKNOWN |
| `AdbInput._run` | 0x2933198 | ADB subprocess command helper; source-level subprocess flags/exception branches UNKNOWN |
| `AdbInput.tap` | 0x29331a8 | ADB `shell input tap` primitive |
| `AdbInput.swipe` | 0x29331bb | ADB `shell input swipe` primitive |
| `AdbInput.key` | 0x29331d0 | ADB `shell input keyevent` primitive; accepts numeric or Android KEYCODE label per doc |
| `AdbInput.text` | 0x29331de | ADB `shell input text` primitive; Unicode/shell quoting behavior not proven |
| `AdbInput.size` | 0x29331ed | Queries `wm size`, documents (w,h) device pixels |
| `AdbInput.screencap` | 0x29331fc | ADB `exec-out screencap -p`, decode PNG with Pillow `BytesIO` and `convert RGB`; returns `None` on error by original doc |
| `AdbInput.save_cap` | 0x293321a | Save image from screencap; specific filename/overwrite/return status UNKNOWN |
| `AdbInput.from_pc` | 0x293323e | Convert reference PC coordinates using actual device size; precise integer rounding, origin and out-of-bounds handling UNKNOWN |

Method names prove an API surface; command components and documents in the same compiled module provide stronger evidence for intent. They do **not** prove every action successfully executed on every LDPlayer instance.

## 2. Transport, target and command semantics
Within the original `emu_input` constants:
- `subprocess`, `check_output`, `CREATE_NO_WINDOW`, `creationflags`, `timeout`, `decode`, `utf-8`, `ignore`, `errors` occur at 0x2932e46..0x2932ec7. This supports non-UI ADB process invocation, hidden console flag and text decode/error strategy. **Exact default timeout, retries, return-value/exception types and capture of stderr are UNKNOWN**, not recovered from source.
- `serial`, `adb`, `shell`, `input`, `tap`, `swipe`, `keyevent`, `text` occur at 0x2932e64..0x2932f46. ADB **target serial must be validated** against P02 EmuManager; actual placement of `-s` in command construction and return/ack semantics are not source-decompiled.
- Original key doc at 0x2932ef9 says numeric or name `KEYCODE_*`, with examples **4/BACK, 3/HOME, `KEYCODE_BACK`**. The `text` block contains `replace` and `%s` constants; encoding/escaping of spaces or arbitrary Unicode must not be asserted as proven based only on their proximity.
- Both an external LDPlayer ADB path `D:\\LDPlayer\\LDPlayer9\\adb.exe` (0x2933129) and `LD_ADB` symbol (0x2933148) exist. **There is no adb.exe binary packaged in the 1,050-entry original ZIP**; its selection, default/fallback precedence and installation requirement have to be tested. No file is pushed/installed during P03.

## 3. Capture path (separate binary/text handling)
- Exact constants: `exec-out` 0x2932f98; `screencap` 0x2932fa2; `-p` nearby; `raw` 0x2932fbf; `PIL`/`Image`/`BytesIO` 0x2932fc4..0x2932fd9; `convert`/`RGB` 0x2932fe2..0x2932fed.
- Original doc 0x2932ff2 explicitly specifies **PIL Image RGB in game/screen orientation or `None` on error**. Therefore PNG capture is binary and must **not** be UTF-8-decoded like ordinary ADB shell text output; maintain distinct raw/text paths. The precise `subprocess.check_output` shape must still be verified on live Windows.
- The debug Android module has `DebugAndroidTab._do_cap`, `_do_rgb`, `_do_tap` (0x290dd18, 0x290dd4a, 0x290dd31) and original strings `screencap FAIL` (0x290d0dc) and `_adb_input` (0x290dc25). This shows compiled UI integration, **not** that a screenshot was taken successfully in P03.

## 4. **Two distinct coordinate domains** (do not hard-code one UI scale)
1. **ADB device pixel coordinates:** original AdbInput description at 0x2933077 explicitly says device pixels and cites LD 960×540. `size()` returns actual `(w,h)`, backed by `wm size` constants; the example device resolution is not guaranteed.
2. **PC reference conversion `from_pc`:** compiled doc at 0x29330c2 describes translating baseline PC 1366×768 to LD 960×540 using illustrative scale **x×0.7027, y×0.7031**, *computed from actual wm size*. Do not copy these coefficients as universal constants or claim exact `round()`/clamp semantics.
3. **Windows LDPlayer client → device viewport:** separately, original `DebugAndroidTab._emu_client_pos`/`_to_device` and docs at 0x290d4ce–0x290d5b9 describe `GetCursorPos` + `ScreenToClient` to avoid DPI coordinate drift, accept LDPlayer window only, and a default viewport origin **(vp_x1,vp_y1)=(0,30)** with window-dependent far corner. It is a *different mapping* from 1366×768 reference conversion; click outside valid game viewport should not be guessed.
4. `EmuChat` uses its own `settings.ini [EmuChat]` calibrated spots `chat_open/input/send/kb_ok/link` to perform a chat-link route; **these are neither map tile coordinates nor ADB raw pixels interchangeably**. See future P04.

**Key parity guard:** original UI screenshots show only the standard 11 public tabs; do not expose a new Android tab from this evidence. P01 proved Train LD hidden/`emu_tab` gated and Debug Android developer-only.

## 5. Caller boundaries and lifecycle distinctions
- `EmuFarmTab` compiled block imports `.emu_input` at **0x2932e35**; this is adjacent to the service block, not independent proof of worker success.
- `DebugAndroidTab` has a dedicated ADB tap/cap/RGB and viewport calibration workbench; target serial selection is required.
- `EmuChat` imports `AdbInput` (0x2930bb9–0x2930bd0), and documents a pure-UI chat-link goto plus separate *memory-based* destination verification; this is a higher-level workflow, **not** equivalent to `tap` returning success.
- Emulator remote `/emu_steps` and `/emu_act` are separate PC HTTP wrappers documented by D07; HTTP ACK cannot be promoted to successful on-device input. The `/emu_farm_toggle` branch is original ACK-only/stub. P03 performed **no remote/network action**.
- `AdbInput` does not itself require moving the physical Windows cursor when sending ADB commands. This is a module-level observation; it does not certify that every other TLM UI action is hidden-mouse.

## 6. Error/timeout/race test matrix
| Situation | Current evidence / required parity check |
|---|---|
| ADB executable unavailable | External path/env evidence only; resolve and report error on Windows, no fabricated control success |
| Emulator serial missing/stale | Identity from P02 must be revalidated; do not target neighboring clone |
| Subprocess times out or returns error | `timeout`/check_output present; exact timeout number and exception handling UNKNOWN |
| Key name/number unsupported | KEYCODE docs; need verify error return vs silently ignored event |
| Text contains spaces, accents, shell characters | `replace` and `%s` seen; actual reliable encoding UNKNOWN |
| `wm size` missing, malformed, rotated or resized | Query/parse identified; exact None/fallback behavior UNKNOWN |
| Reference PC coordinates vs child viewport | Distinct conversions; avoid DPI/30px title offset bugs |
| `screencap -p` returns truncated/invalid PNG | Original RGB or None contract; distinguish error from black screen |
| Screenshot orientation or stale capture | Original doc says game orientation, but live resize/retry handling UNKNOWN |
| Concurrent input to cloned VMs | Guard by live serial; order/races across thread workers NOT proven |
| Screenshot/save fails | `save_cap` exists; exact error/overwrite semantics UNKNOWN |
| UI tap succeeds but game ignores action | Require higher-level state verify, not only ADB command completion |

## 7. Static test and status
**PASS (static only):** original ZIP SHA/CRC and original EXE SHA, exact compiled method markers and literal docs, independent debug/client-coordinate evidence, original package absence of adb.exe.

**NOT RUN:** Windows ADB, root/Frida, screenshot decode under live LDPlayer, actual tap/swipe/key/text on device, DPI/calibration, timeout and retry behavior, Windows reconstructed product EXE. The latter remains **BUILD_BLOCKED_SOURCE_MISSING**: repo has forensic scripts/docs but no reconstructed application source and no Stage-T Windows build workflow (see existing code/build audit). A pre-existing original EXE does **not** constitute a build artifact from repo source.

**Status:** `STATIC_EMU_INPUT_ADB_AND_VIEWPORT_CONTRACT_AUDITED / LIVE_INPUT_PARITY_DEFERRED`.

**NEXT_ACTION:** P04 — `emu_chat` pure-UI chat-link path, coordinate calibration and memory-based destination verification, original EXE and shipped scripts first. Preserve all earlier work and Proxy exclusion.
