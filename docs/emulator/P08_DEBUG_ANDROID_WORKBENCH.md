# P08 — Original DebugAndroidTab developer workbench, calibration, capture, memory and safety

## Locked inputs and exact module provenance
Continue from current GitHub `STATE.md` `NEXT_ACTION = P08`. Re-read PLAN, STATE, PROJECT_STATUS, P01, P03, P04, P07. GitHub `docs/tasks/P08.md` did **not** exist. Inspected *actual original* `TLMTool_2.1.2(10).zip` and its inner `TLMTool.dist/TLMTool.exe` directly in a read-only process; no original program executed.

- ZIP SHA-256: `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; 1,050 files and full ZIP CRC PASS.
- Inner EXE: 47,450,112 bytes; SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Exact serialized marker `<module debug_android_tab>` at offset **0x290df6c**. Associated constant/description range about `0x290bb8c..0x290df6b`. String offsets are Nuitka serialization provenance, **not** recovered Python source code or execution order.
- Checked **53/53** selected exact byte-offset/serialized-string anchors PASS using a corrected local verification script. An earlier draft check mistakenly used five inexact offsets/prefix assumptions; those errors were fixed in the *test harness* before the final 53/53 PASS. No game/product binary modified.
- `PLAN.md` and MainApp/P01 explicitly establish that **Debug Android is developer-only**. Its presence in the compiled EXE does not entitle a public tab or imply it is shown in baseline user screenshots.

## 1. Actual compiled UI/control inventory

| Region | Compiled widgets/handlers | Scope and fidelity |
|---|---|---|
| Emulator selection | Read-only `ttk.Combobox` serial; Refresh; device status | Uses `adb_devices` and `emu_manager.status_all`. Exact list refresh delay/status formatting only static |
| Frida | Start frida-server; `_start_server`; Force rescan `_emu_scan` | `_server_start`, `_server_alive`, `force_discover` referenced. No actual Frida connection tested |
| Script setup | Push script (one), Push all; `_adb_push_one/_adb_push_all` | References `emu_setup.push_script`, ADB path resolution; no guest deployment executed |
| Remote | Listener toggle `_remote_toggle` | `emu_remote.is_running/start/stop/remote_port`; optional service, no default auto-start verified |
| Capture | Screencap button; Tap entry; RGB sample entry with 30×30-style canvas swatch | `AdbInput` `save_cap/tap/screencap`, `Pillow getpixel`, drawing canvas |
| Memory | RoleData + bag slots (Site 10) | Uses `EmuManager.poll_rows/get_bag_slots` and RoleID/Name, MapID, PosX/Y, HP/MaxHP, Level, Exp, BoundMoney, ServerID |
| Chat travel | Input values for `chat_open/input/send/kb_ok/link`; `goto_map/x/y` | Six handlers `_step_open/_step_type/_step_send/_step_link/_step_full/_step_close`; P04 chat-link API exists separately |
| Live tracking | Track on/off; text/log label | `_toggle_track/_track_loop` plus desktop mapping/character-state refresh |

These are real serialized widget labels, named callbacks and imports in EXE. **None are claimed to be successfully functional in a live LDPlayer session** without Windows/game testing. The original embedded module doc at 0x290d6de..0x290d7f4 explicitly classifies it as an Android equivalent of PC Debug focused on serial, screenshot, RGB, Tap, Frida RoleData and staged chat-goto; it explicitly **does not contain** PC NPC test, fake accounts or plan-limit test.

## 2. Calibrating Win32 client → Android device coordinates

This is separate from `emu_input.AdBInput.from_pc` and from game tile coordinates.

- Original `_emu_client_pos` references `GetCursorPos`, `WindowFromPoint`, `GetAncestor(GA_ROOT)`, `GetWindowText`, title filtering for LDPlayer/dnplayer, then `ScreenToClient` and `GetClientRect`. Embedded original doc at 0x290d4ce says to avoid pyautogui DPI coordinate drift. It is a **Windows client** mapping, not identical to raw Android device pixels.
- `_to_device` maps selected viewport client rectangle into actual/sampled device size. Embedded doc at 0x290d57c gives a **default viewport origin (vp_x1,vp_y1)=(0,30)**, with X2/Y2 derived from the window when entries are empty. Original reference example device 960×540 is **not** guaranteed for every LDPlayer instance.
- `_arm_corners` + `_capture_corner` original doc says **Alt first corner = game's upper-left; Alt second = lower-right**; invalid/wrong order rejected. `_alt_freeze_pin` can pin current converted device coords into Tap field. `pynput.mouse.Listener(on_click)` and `Button.middle` are compiled references for a coordinate-capture trigger. Their precise OS listener startup/stop and interaction/priority with Alt require live verification.
- The original UI stores `vp_x1/y1/x2/y2` and `[EmuChat]` ten `chat_open_x/y`, `input_x/y`, `send_x/y`, `kb_ok_x/y`, `link_x/y` plus `goto_map/x/y` fields. `_load_cfg/_save_cfg` reference `utils.read_settings/write_settings` and `_settings_lock`.
- Several numeric examples embedded near the constructor (such as `200, 505` and `480, 270`) are baseline defaults/examples. Do **not** freeze these as universal tap points; P03/P04 established multiple coordinate domains and runtime viewport changes.

**Critical parity rule:** Windows cursor observation/Alt or middle-button capture is for calibration. The actual Android device action uses ADB tap. There is no evidence that `DebugAndroidTab` physically moves the Windows mouse to click game objects, and there is no proof that *all* TLMTool features avoid the physical cursor. Keep the claim local to this subsystem.

## 3. Capture/RGB and memory read are separate diagnostic paths

`_do_cap` calls the ADB/PIL capture path; EXE labels `cap FAIL`, `screencap FAIL`, `save_cap` and `CONFIG_DIR/emu_cap_*.png`. `_do_rgb` reads pixel `(x,y)` from screenshot and paints a Tk canvas swatch. It must handle missing image/out-of-range pixel separately from a black pixel and must not claim success from a file-name label alone. Directory/path, concurrency and partial PNG failures are not source-reconstructed.

`_do_mem` queries EmuManager live rows and displays fields `RoleName/RoleID/Level/MapID/PosX/PosY/CurrentHP/MaxHP/Exp/BoundMoney/ServerID`. `_do_bag` queries Site10 slot summary. P02/P03 warn `get_bag_slots` `None` denotes read error/unavailable and `0` may be unloaded/empty depending on JS; a failed reader must never become "inventory empty" or trigger actions.

## 4. Debug actions, permissions and failure reporting

The presence of `_run` and `threading.Thread(daemon=True)` supports nonblocking action designs, not confirmed concurrency or cancellation order. `_guard` and `_serial` ensure a target is selected in compiled UI. Device permission/licensing is **main-tab developer visibility policy** from P01; do not assert `_guard` itself authorizes `emu_tab` unless source/run proves it. Starting the remote listener is an actual network action if used, but **P08 did not start one**. Original P07 found weak default listener token: no security hardening work is authorized in this parity task and Proxy phase is excluded.

Staged chat tests support individual chat-panel opening, entering `@GOTO`, send, link tap, complete goto and close/back. `_step_full` and `_track_loop` do **not** by themselves establish in-game arrival. Only fresh MapID and correct tile comparison can verify it; original source's exact unit conversion between raw PosX/Y and shifted X_UI/Y_UI remains UNKNOWN from P04.

## 5. Static results and gates
- **Static PASS:** original locked ZIP CRC/hash and EXE hash; 53/53 exact selected symbol-offset anchors, original UI callbacks/docs, 92 new evidence entries in the P08 table.
- **Runtime NOT_RUN:** 33 explicit Windows/LDPlayer acceptance cases; no original TLM.exe, game, ADB command, Frida service, screen capture, listener, account control or product build executed.
- **Blocker:** reconstructed Stage-S source app and Stage-T Windows build workflow remain missing according to existing repo audit; subsequent P01–P08 docs do not change that. **BUILD_BLOCKED_SOURCE_MISSING**. This is neither a successful rebuilt EXE nor a diagnosed compiler failure.
- Earlier A–O, P01–P07 and PLAN remain untouched, Proxy no-development retained.

**P08 status**: `STATIC_DEBUG_ANDROID_DEV_WORKBENCH_AND_COORDINATES_AUDITED / LIVE_PARITY_DEFERRED`.

**Phase P**: P01–P08 emulator **static research** complete; device + reconstructed Windows parity deferred (do not mark complete functional parity).

**NEXT_ACTION = R01**: In PLAN Phase R, conduct **gap-focused immutable resource/data provenance check**, reusing existing Gate-A/D06/D07 inventories rather than duplicating completed work. Specifically reconcile `.old/.bak/.dat` immutable originals, readers/writers/runtime use and known/unknown cross references for later Stage-S packaging. No Proxy implementation.
