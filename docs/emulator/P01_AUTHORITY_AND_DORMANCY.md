# P01 — Original emulator modules: active, conditional or dormant?

## Authority and current blocker
- Verified original TLMTool 2.1.2 ZIP SHA256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd and inner EXE SHA256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22; neither original EXE nor ADB/Frida services executed. Main GitHub at fe23b809d55641351fa7dcd69a70e0b767b47799 already contains N01–N10 and O01–O05 research; this task reads and models P01 only.
- A parallel full repository/source audit is in `docs/audit/CODE_BUILD_BASELINE_2026-10-08.md`. Stage-S reconstructed source and Stage-T build workflow are absent; P01 cannot produce a runnable application.

## 1. Seven exact compiled modules and original intent
| Module | EXE marker | Role | Classification |
|---|---|---|---|
| `emu_input` | `0x293325f` | ADB tap/swipe/keyevent/screencap device pixels | REFERENCED_SERVICE |
| `emu_reader` | `0x29361cc` | Frida RPC read/validate/bagSlots, device discovery | REFERENCED_SERVICE |
| `emu_remote` | `0x2938352` | Optional HTTP listener, emu_tab entitlement and ACK-only branch | CONDITIONAL_SERVICE |
| `emu_setup` | `0x293942e` | APK/AutoX and ld_remote.js push, template PC_BASE | REFERENCED_ON_SETUP |
| `emu_chat` | `0x293100c` | Coordinates [EmuChat], UI chat-goto sequence | REFERENCED_SERVICE |
| `emu_farm_tab` | `0x2932983` | Train LD account rows, device presets, start/stop refresh | CONDITIONAL_REGISTERED_TAB |
| `debug_android_tab` | `0x290df6c` | Capture/viewport calibration/ADB/Frida/remote workbench | DEVELOPER_ONLY_TAB |

## 2. Active original UI registration is different from visibility
- In `TLMMainApp.create_tabs` the original module contains `Train LD` at 0x28d0f3c, key emu_farm_tab, immediately associated with `hidden`, and directly references class EmuFarmTab. The tab is **registered but not always shown**.
- Main also references DebugAndroidTab and has a separate visibility setter; original doc says `Debug Android` only appears with dev permission. Both are not simply dead code, but no runtime proof for any particular account permission or worker success.
- Original permission state includes `emu_tab` and general rule that only Info stays always visible. Do not instantiate extra emulator UI based only on module existence or bypass entitlement.

## 3. Services and potentially incomplete branches
- `emu_input` wraps ADB tap/swipe/keyevent/screencap; `emu_reader` includes AndroidReader/EmuManager and Frida RPC RoleData/bagSlots; `emu_chat` uses per-device UI coordinates; `emu_setup` installs/copies optional AutoX/remote resources.
- `emu_remote` has opt-in listener and emulator endpoints; original docs explicitly describe `/emu_farm_toggle` as a future-phase ACK. Treat ACK as a transport response rather than confirmed automation.
- Security caveat from original docs: remote default token `tlm`, listener bind `0.0.0.0`, port 8765. Do not auto-launch or publish a listener based on static evidence alone. This is NOT the excluded Proxy Phase Q; only emulator evidence is recorded.

## 4. Packaged original JS files
- `emu_client.js`: 5368 bytes SHA256 384ccee9a2ddf236db377fca3abd36cbc17df81a94a286551a749a3132d02db1. Frida RPC exports ping, setBase, readAll, validate, scanRoleId, scanShape, bagSlots. Static Node syntax check passed; actual Frida runtime untested.
- `ld_remote.js`: 56174 bytes SHA256 3bd84a2b433ee679b7a049f5aa5cba2e8725d1e09b14d5deb3f42b6bf919edfb. AutoX/Auto.js uses XML-layout UI; standard Node syntax checker fails at `<frame>` but is **not a valid test for AutoX**. Its device actions/HTTP were NOT executed.

## 5. Dormancy classification
- `Train LD` / EmuFarmTab: **CONDITIONALLY_REGISTERED_ACTIVE_UI_SURFACE**, initial hidden state; no full live functionality claimed.
- `Debug Android`: **DEVELOPER_REGISTERED_UI_SURFACE**, controlled by developer permissions.
- `emu_input`, `emu_reader`, `emu_chat`: **REFERENCED_SUPPORT_MODULES**; meaningful compiled code, runtime effect unverified.
- `emu_setup`: **OPTIONAL_SETUP_PATH**. `emu_remote`: **OPTIONAL_PERMISSION_GATED_LISTENER_WITH_PARTIAL_ACK_ENDPOINT**.
- No seven-module conclusion may be promoted to always-visible or fully runnable without original Windows/LDPlayer tests.

## 6. Future tests — 0 executed
| ID | Requirement |
|---|---|
| P01-01 | All 7 compiled module markers match original EXE |
| P01-02 | Train LD is originally registered but hidden until permission |
| P01-03 | Debug Android is developer-only, not general public UI |
| P01-04 | Lazy EmuFarmTab construction and refresh calls function |
| P01-05 | emu_tab entitlement blocks restricted emulator controls |
| P01-06 | EmuManager identity/serial mapping and ADB discovery |
| P01-07 | AdbInput screen/click coordinates match device pixels |
| P01-08 | Frida AndroidReader RPC readAll/validate/bagSlots works |
| P01-09 | Frida base change/reconnect validates current device |
| P01-10 | Chat settings and per-device coordinate persistence |
| P01-11 | EmuSetup optional APK/remote JS deploy works |
| P01-12 | Remote listener does not start without user action |
| P01-13 | Remote authentication/bind policy is safe |
| P01-14 | Remote farm toggle ACK is not mislabeled completed farming |
| P01-15 | Debug capture/RGB/tap/memory UI works only with dev permission |
| P01-16 | Original Frida JS and AutoX JS run in correct runtimes |
| P01-17 | No dormant UI invented and no Proxy feature implemented |
| P01-18 | Stage-S rebuilt app/Stage-T Windows build and emulator parity |

All 18 acceptance cases remain **NOT_RUN** on a reconstructed app.

## Next step
**P01 = STATIC_EMULATOR_MODULE_AUTHORITY_AND_CONDITIONAL_UI_AUDITED / LIVE_EMULATOR_PARITY_DEFERRED.**
NEXT_ACTION: **P02 — AndroidReader/EmuManager, Frida RPC and ADB device/connection lifecycle audit**. Continue from original binary/packaged JS, preserve conditional tab permissions. Proxy remains outside development scope. Product build remains BLOCKED_SOURCE_MISSING until actual Stage-S app source exists.
