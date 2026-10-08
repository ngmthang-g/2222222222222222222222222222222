# P05 — TLMTool 2.1.2 original EmuFarmTab / Train LD: UI, device accounts, presets, authority, runtime limits

## Scope, sources and reproducibility
**Starting point:** `STATE.md` final `NEXT_ACTION=P05`; `PLAN.md` Phase P; `PROJECT_STATUS.md`; P01–P04 reports. Current GitHub `docs/tasks/P05.md` was absent at start. No previous completed task rewritten. Proxy Phase Q remains **non-development**.

**Original binaries read, never executed:**
- User ZIP `TLMTool_2.1.2(10).zip`: SHA256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`; 1050 entries, CRC PASS.
- Inner `TLMTool.dist/TLMTool.exe`: 47,450,112 bytes, SHA256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`.
- Original AutoX `ld_remote.js`: SHA256 `3bd84a2b433ee679b7a049f5aa5cba2e8725d1e09b14d5deb3f42b6bf919edfb`; 1,297 lines. Frida `emu_client.js` was already audited P02/P04, no redundant recovery.

**Compiled data provenance:** `<module emu_farm_tab>` marker **0x2932983**. Module serialized constants approximately **0x293110b–0x2932982**, preceding module marker; `emu_input` begins immediately after, at 0x293325f. Hex offsets refer to bytes in this precise inner EXE; Nuitka strings/method-name markers are **not** recovered Python AST. Static method presence ≠ Windows/LDPlayer runtime success.

A repeatable byte-level check passed: exact original archive integrity and two asset hashes; 15 module method/key/permission constants at their expected offsets (with serialized type prefix accounted for); five JS token checks. A preliminary raw-offset assertion incorrectly assumed no serialized `a`/`u` prefix and an intermediate test used misspelled Python encoding; both were **test-harness mistakes**, corrected before the reported passing test. No application code was modified by that diagnostic.

## 1. What the PC Train LD surface actually contains
**Registration/visibility:** Main app registers potential `Train LD` via `EmuFarmTab`, but P01 verified it starts hidden and is only shown with `emu_tab` entitlement; `Debug Android` is developer-only. Do not add a visible Train LD tab to the baseline 11-tab screenshot for an unentitled user.

**UI construction, original EXE:**
- `EmuFarmTab.__init__`, `_build_ui` and refresh methods (0x293270d–0x293279c).
- `ttk.LabelFrame`, frame/canvas/vertical scrollbar, embedded rows and mouse-wheel binding (0x293134f–0x29315b6) present. These establish a real dynamically refreshed list, but **exact widget geometry/row count on a live account remains unverified**.
- `_acc_rows`, `_refresh_id`, `_refresh_active`, `_refreshing` state in constructor (0x293123d–0x2931266).
- Per-account row `_add_or_update_row` and three-line status/tracking model; label/button widgets with the original style and `Train:` label (0x2931b51–0x2931fef). Colors/font strings are original serialized literals, not proof of final screenshot pixels.
- Row `_toggle_this` handler and `btn_play` indicator; references `permission_guard.has_permission`, `emu_tab`, `disabled`, `state`, `busy` and `_set_status` (0x2931be6–0x29320a3). This is **button wiring and status update**, not automatically a running autonomous farm engine.

**Refresh/data flow model (static evidence, not decompiled call order):**
```
EmuFarmTab: _start_refresh / _schedule_refresh / _refresh_acc_list
   -> background threading.Thread(daemon=True) _worker
   -> emu_reader.emu_manager.poll_rows()
   -> Tk scheduling / _apply to rows
   -> map virtual-machine names + RoleID / guest status / bag slots
   -> _add_or_update_row ; remove stale row widgets
   -> labels for name/status/presets/coordinates/track
```
The module contains `threading.Thread`, `daemon`, `poll_rows`, `_apply`, `get_bag_slots`, `after`, `after_cancel`. The exact polling cadence, thread stop/cancel ownership, window-close race and UI thread dispatch remain **UNKNOWN** and require Windows testing.

## 2. Character identity, metrics and presets
- **Identity collision risk:** the original class docs explicitly state `Rows key theo android_id (serial doi sau reboot)` (0x29325fb). Yet map/bag command target and per-emulator coordinates are keyed by ADB **serial**. P02 established that cloned VMs can share android_id/hwid. Whether all row bindings survive serial changes or a clone collision safely is **NOT PROVEN**; never guess a target.
- **Preset names and storage:** `get_dev_coords`, `get_dev_coord`, `_dev_presets`, `_sel_name`, `_sel_coords` are present. Original docs say each emulator has its own **`[EmuCoords:serial]`** set (0x29325b8–0x29325fb), with selected Sell/Train preset names from `ini` by character name as modified by the guest overlay (0x293182f).
- The legacy `map|x|y` format is expressly accepted, absent data gives display placeholders (`—`) rather than a valid coordinate; code string `_refresh_coord_labels` updates six map/X/Y labels (0x29318ad–0x29319c7). Exact parse failure handling and overlay/PC synchronization under missing serial or renamed character remain **UNKNOWN**.
- **Settings migration:** `read_settings`, `write_settings`, `_settings_lock` and `[EmuFarm]` with `[TrainLD]` fallback/migrate docs (0x293110b–0x29311d3; 0x293262d). Do not rewrite stored formats or claim migration writes a particular key without live/source proof.
- **Metrics/tracking**: `CurrentHP`, `MaxHP`, `RoleName`, `RoleID`, `Level`, `MapID`, `PosX`, `PosY`, `BoundMoney`, `_deaths`, `_last_death`, `_earned`, `_exp_g`, `get_bag_slots`, `bag_limit` are compiled references. Display supports loss/gain/duration text and “TÚI ĐẦY” state. **Data availability, accuracy, statistics formulas and numeric bag threshold are not proved** merely by the string `100` adjacent to `bag_limit`.
- **Minimal conditions only:** class doc defines “CO: config tối thiểu (chu kỳ về + ngưỡng túi), rows 3 dòng … preset Bán …, di chuyển chat-link goto + verify memory.” Distinguish configuration surface from actual scheduling engine. EXE explicitly says **KHÔNG** port the PC-heavy chain “về thành multi-bước, nav Phù/Ngựa, shop HP/MP, heal combo, buff F-key, bảng tọa độ” into this tab. Do **not** invent it.

## 3. Commands and permission-bound state machine
| Surface | Original compiled evidence | Highest supported confidence |
|---|---|---|
| Play/stop per row `_toggle_this` | `btn_play`, `busy`, `status`, `has_permission('emu_tab')`, `farm cycle: phase sau` | UI/event/status plumbing; **real farm loop not proved** |
| Go to selected Train `_goto_acc` | `_sel_name`, `train`, `map_to_id`, `has_permission_with_limit('emu_tab','trainld')`, `emu_chat.goto` | A real high-level goto call path exists; movement success requires memory verification, runtime NOT_RUN |
| Setup account `_setup_acc` | `emu_tab`, `trainld_setup` permission labels, `setup_busy`, `emu_setup.setup_instance` | Installer/push/grant/open-app setup path exists, but no install executed or completion proven |
| Refresh rows | `_start_refresh`, `_stop_refresh`, `poll_rows`, Tk `after`, daemon worker | Background refresh designed; exact worker synchronization/lifetime UNKNOWN |

Do not bypass per-action entitlement/limits simply because the registered tab becomes visible. Goto and setup each have their own guards; `btn_play` may become disabled without access. Exact entitlement token argument shapes and license response from compiler are not reconstructable solely from adjacent strings.

## 4. Guest AutoX `ld_remote.js` is **NOT** the same as PC `EmuFarmTab`
**Direct source inspection of shipped AutoX JS:** 
- GUI labels: `btnGoTrain` “Đến” (line 53), `btnPlay` “Train Off” (line 56), `btnTrain` preset selection (line 147). Saved guest config supports `town_condition`, `town_method`, `sell_preset`, `train_preset`, `heal_preset`, `respawn_fast`, `auto_reconnect`, `pickup_no_cankhon`, `trist`, `buff_0..2` (lines 1153–1168). These are **configuration inputs**, not evidence of running buff/reconnect/train automation.
- `buildGoSeq()` (lines 1030–1043) constructs a **fixed seven-step ADB-like UI sequence** including `@GOTO_` text from the chosen train preset and hardcoded tap points (e.g., first at 322,515), then `runSteps(seq,350,...)` (lines 1044–1054) calls `POST /emu_steps`.
- It labels “Di chuyển đến [preset] thành công” when HTTP `r.ok` is true. The JS in this handler has **no subsequent MapID/PosX/PosY arrival check**. That is a **confirmed difference of success criteria** from the PC `EmuChat.goto` *documented* memory-verified flow. This is a transport/step-ack UI message, not proof of actual arrival or a tested broken action.
- `btnGoSell` and `btnGoHeal` call `/emu_act` and similarly report only “Đã gửi lệnh” on `r.ok` (lines 1057–1066). They do not prove sale or healing occurred.
- `toggleFarm()` posts `/emu_farm_toggle`; on `r.ok`, it flips local `farmOn = !farmOn` and paints the label “Train On/Off” (lines 1086–1109). Original compiled PC `emu_remote` doc, already audited D07/P01, explicitly calls the endpoint a **future-phase ACK**. Consequently **Train On is not evidence an autonomous farm worker started**.
- Guest config/presets use local `storages.create('tlm_tool')`, JSON under `/sdcard/TLM/tlm_<aid8>.json`, and PC `/emu_coords`/`/emu_config` interfaces. `saveCfgQuiet`/debounce (700 ms in lines 1068–1084) and loading support UI state persistence; cross-platform synchronization/recovery after crashes is NOT tested.
- The guest's fixed tap locations are **not** equivalent to the PC `_goto_acc` calibrated `[EmuChat]` click path (P04). Do not merge them or silently replace one with the other.

## 5. Known risks, distinguishing evidence from proposed runtime tests
1. **Source partiality is confirmed**: literal original `farm cycle: phase sau` at 0x29320a3, and AutoX `Train On` is based on transport ACK. Claim: *compiled surface and partial navigation/control framework exist; complete farm-cycle runtime is not established*.
2. **Possible row-key collision**: stable Android ID vs potentially duplicated cloned VMs, while device preset storage uses changing serial. Live rebind/uniqueness NOT_RUN.
3. **Potential false success UI**: guest “Đến train thành công” checks `r.ok` after `/emu_steps`, not memory arrival. The original source demonstrates this difference; real-world error rate UNKNOWN.
4. **Missing-memory versus empty/full bag**: P02 bagSlots `None`/0 ambiguity; avoid silently assuming full/empty when reader not attached. Numeric bag threshold derived from compiled value not proven.
5. **Permissions**: `emu_tab`, `trainld`, `trainld_setup` guards/limits should be preserved; do not auto-expose restricted UI or start a listener.
6. **Runtime incomplete**: no Windows compiled reconstructed source, no LDPlayer attach, ADB action or gameplay validation, and no original Python source recovered.

## 6. Static test and phase result
**Static tests PASSED**:
- Full original ZIP CRC (1050 entries), binary EXE & AutoX JS SHA256.
- **15** selected exact-offset module markers/constants verified with Nuitka-serialized prefix correction.
- **5** shipped AutoX JS tokens independently verified. Source-side lines 998–1109/1153–1188 inspected as code, *not merely screenshots*.

**Live tests NOT RUN**: all planned device/action/permission/movement/account automation checks in `P05_MODEL.json`.

**Build/source check:** Latest GitHub commits before P05 are P04 documentation/checkpoint. Existing full source audit `docs/audit/CODE_BUILD_BASELINE_2026-10-08.md` recorded no rebuilt Stage-S application source or Stage-T Actions Windows build pipeline. P05 creates only research artifacts; therefore build stays **BUILD_BLOCKED_SOURCE_MISSING**, not a compiler result. A Windows EXE in the user ZIP is original forensic input, **not built by this repository**.

**STATUS**: `STATIC_EMU_FARM_TAB_PARTIAL_UI_PRESETS_AND_PERMISSION_AUDITED / LIVE_TRAIN_PARITY_DEFERRED`.

**NEXT_ACTION**: **P06 — original `emu_setup` guest setup/ADB package installation, file push, AutoX permissions and launch chain audit**. First inspect original compiled EXE and guest JS, do not implement Proxy or widen UI.
