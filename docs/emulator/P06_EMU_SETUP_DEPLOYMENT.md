# P06 — Original emu_setup: remote APK / AutoX installation, ADB script delivery, permissions and launch

## 0. Scope and source authority
CONTINUE resumed from GitHub `PLAN.md`, `STATE.md` and `PROJECT_STATUS.md` at **P06**. `docs/tasks/P06.md` was **absent (404)** before this task. Earlier P01–P05 evidence/documents and the Proxy exclusion were preserved; no other original source or binary was modified.

Inspected user-supplied `TLMTool_2.1.2(10).zip` **read-only**. ZIP SHA256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`, 1,050 entries and CRC PASS. Frozen inner `TLMTool.dist/TLMTool.exe`: 47,450,112 bytes, SHA256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`. Shipped `ld_remote.js`: 56,174 bytes, SHA256 `3bd84a2b433ee679b7a049f5aa5cba2e8725d1e09b14d5deb3f42b6bf919edfb`.

**Direct binary provenance:** Nuitka serialized `emu_setup` module strings and references at roughly 0x29387a5–0x293942e, closing module marker `<module emu_setup>` exactly at **0x293942e**. The prior compiled `emu_remote` boundary is at 0x2938351. Bytes after the closing marker contain function-local variable strings and other module content: do not mistake those for reconstructed `emu_setup.py` source/AST. This task proves names, literal contracts and installed-script source intent, **not exact Python control-flow order, successful device operations or original source-code parity**.

## 1. The setup task is an optional per-device path, not the training worker

The PC Train LD `EmuFarmTab._setup_acc` references `emu_setup.setup_instance`, `log_cb`, and permission labels `emu_tab`/`trainld_setup` (P05, EXE 0x2932323–0x29323cf). Original compiled doc (0x2939275–0x2939331) describes **a background thread per selected ADB serial, setup by ADB, no root required**, with progress through `log_cb`.

The documented stages are:

1. `resolve_adb`; reject or report missing ADB rather than treating a stale serial as attached.
2. `detect_autox_pkg` by installed `package:` entries. Candidate remote packages include private APK and AutoX/Auto.js. If not installed, `find_autox_apk` chooses a candidate local APK and `adb install` is attempted.
3. Recheck installed package after installation. Embedded failure string **"install xong nhung khong thay package"** shows command completion is **not** the only check.
4. `push_script` copies `ld_remote*.js` into folders reachable by the Android guest; reports per-location status and `(ok,msg)`.
5. Attempt `pm grant` external-storage permissions and `appops set SYSTEM_ALERT_WINDOW allow`; overlay permission may still need a **manual one-time action**.
6. Open AutoX/remote package using `monkey` and launcher category. The original final instruction explicitly says: **open AutoX, then manually press Run on `ld_remote.js` once**.

That last manual click is an original task boundary: no proof of automatic script execution at boot, post-install readiness or remote listener connectivity. `setup_instance` returns a success boolean/message contract; the exact order, retries, and whether a partial permission failure returns false are **UNKNOWN** from serialized constants. A successful `adb install` or `monkey` response must not be called `overlay running` or `game farming`.

**Root separation:** this installer path is documented no-root. The unrelated P02 Frida memory reader requires its own guest frida-server/privileges. Do not silently combine installation with root attach.

## 2. APK discovery and **actual packaged-file limitation**
The original EXE contains `[Emu] remote_apk`, `[Emu] autox_apk`, `_find_remote_apk`, `_find_autox_apk` and descriptions of a private remote APK followed by an `autox*.apk` fallback (0x2938cf4–0x2938f35).

The **actual original ZIP has zero files with a `.apk` extension**. Thus the package on its own does not supply an APK for a fresh AutoX installation. Device may already have a suitable package; alternatively the operator must provide an APK externally in a supported location/configuration. The exact search ordering across `[Emu]` keys, tools directory, system/user profile and name patterns is not recoverable from these compiled strings. Do not pretend the compiled tool can always self-install successfully from this ZIP on a fresh computer.

Package-detection strings `autojs`, `tlmremote`, `remote_pkg`/other candidates are present; the **exact package name list** is not fully reconstructed. Verification must not accidentally launch the game APK or unrelated AutoX installation.

## 3. JS deployment to multiple guest script folders
Confirmed exact constants:
- `REMOTE_JS_FILES` enumerates **all local `ld_remote*.js` candidates** beside the tool/EXE (with name/path/size/mtime; 0x29387c6–0x293880a).
- `REMOTE_SCRIPT_DIRS` is a list of script locations to attempt (0x2938aaa). Explicit literal `/sdcard/Scripts` at 0x29393a5, names `ld_remote.js` and `ld_remote_new.js` near 0x29393c8; also `/ld_remote_new.js` at 0x2938b39. The **full exact destination list**, per-folder permissions, `adb mkdir/push` loop order, overwrite policy and fallback conditions are **UNKNOWN** without source-level reconstruction/runtime traces.
- `push_script` uses `adb shell mkdir` and `adb push` with subprocess `CREATE_NO_WINDOW`, timeout, and `pushed`/error-count/log strings (0x2938a29–0x2938c8e).
- The compiled doc explicitly says **try every AutoX-visible Scripts location, old and new local script variants**, with per-path status, final `(ok,msg)` response. A failure to push one location is not evidence all locations failed; likewise one successful file copy is not proof AutoX executed it.

## 4. PC LAN address patching of guest script
Compiled `_render_pc_base` source description at 0x293889f: temporary JS copy substitutes literal `__PC_BASE__` with `http://<lan_ip>:<remote_port>`, and the caller should remove its temporary file afterward. Uses `tempfile.mkstemp`, `_lan_ip` local IP logic with a UDP socket/bound route (8.8.8.8, 0x293884b–0x29388f0), `[Emu] remote_port` (0x2938909–0x293899f).

Original AutoX JS **line 6** sets `PC_BASE = "__PC_BASE__"`, and **line 7** falls back to `http://172.16.1.2:8765` if placeholder wasn't replaced. This is an **original source-level fact**, not an assertion that the fallback is correct for the user's LDPlayer network. A linked compiled description at 0x29388b1 says LDPlayer may not use `10.0.2.2`. The exact LAN IP fallback/multiple-NIC interface selection and how firewall/VM networking impacts reachability are unverified.

Security/scope limitation: shipped guest script sets **`TOKEN = "tlm"`** (JS line 8); previous D07/P01 found PC listener 0.0.0.0:8765 and a default token of `tlm`. P06 **does not start any listener or develop unrelated Proxy functionality**. Never present these defaults as a secure deployment recommendation; production network hardening would require a separate authorized change and parity review.

The temporary copy is a patch of a **copy for deployment**, not authorization to modify the frozen original JS/archive. Failure cleanup/retained temp artifacts and stale PC URL after host IP change remain unresolved.

## 5. Permissions and launch results
Compiled constants and diagnostics:
- `android.permission.READ_EXTERNAL_STORAGE`, `android.permission.WRITE_EXTERNAL_STORAGE` at 0x29390a5 / 0x29390cf; `grant` at 0x29390fa. Modern Android versions may reject obsolete storage grants; this is a test case, **not** a verified problem on the user's emulator.
- `appops set SYSTEM_ALERT_WINDOW allow` at 0x293914e–0x2939170; statuses include overlay granted or `cap quyen loi (bat tay 1 lan)`. Therefore overlay should be verified in the intended AutoX runtime rather than inferred solely from an ADB return code.
- `monkey` + `android.intent.category.LAUNCHER` at 0x29391b2–0x29391be; "da mo app AutoX" at 0x29391e8. Launching the package is **distinct** from manually running the AutoX JavaScript and connecting to the PC.
- `log_cb`, local `log` marker and "XONG" message document per-serial progress reporting; cancellation, setup_BUSY guard, retry cadence, maximum wait and exact `(ok,msg)` aggregation remain source/runtimely **UNKNOWN**.

## 6. Operational failure matrix and downstream verification
| Condition | Required interpretation |
|---|---|
| No ADB binary or offline serial | Show setup failure, never redirect actions to another emulator |
| No installed remote/AutoX and no external APK | **Confirmable package gap**; cannot freshly install solely from this ZIP |
| Install command exits but package absent | Original has explicit post-install package-missing diagnostic; report failure |
| Script copy to only some destinations | Summarize successful locations and errors separately; do not call all copied |
| No valid PC LAN binding/replaced URL | Host may be unreachable; script file present ≠ connected |
| Storage/overlay permission failed | Manual one-time grant might be necessary; not confirmed from subprocess return |
| `monkey` launch succeeded | Package open, not `ld_remote.js` currently running |
| Guest overlay shows Train On | D07/P05 `/emu_farm_toggle` was ACK-only; not gameplay completion |
| Two identical cloned Android IDs | P02 identity issues; require known selected live ADB serial for setup |
| APK updated or device rebooted | Permissions, scripts, app state must be reverified in live test |

**Deferred runtime:** Windows LDPlayer/ADB package install, script copy, AutoX permissions, floaty UI run and post-setup reconnect have **not** been executed. Avoid executing original unknown binary or third-party APK merely to fill those gaps.

## 7. Verification gate and build status
Read-only static check on the original ZIP:
- **ZIP CRC PASS**, 1050 entries.
- EXE and `ld_remote.js` SHA256 match frozen P01/P05 artifacts.
- **20/20** selected Nuitka compiled offset-token checks PASS.
- **6/6** AutoX JS source token checks PASS.
- **0** bundled APK files confirmed.

**No real setup or user Windows build**. Repository baseline `docs/audit/CODE_BUILD_BASELINE_2026-10-08.md` documents absence of Stage-S application source and Stage-T Windows build workflow. New commits since then are P01–P05 docs/checkpoints; P06 only creates evidence/checkpoints. Build remains **BUILD_BLOCKED_SOURCE_MISSING** (not compile test PASS/FAIL).

**STATUS = STATIC_EMU_SETUP_APK_SCRIPT_PERMISSIONS_LAUNCH_AUDITED / LIVE_SETUP_PARITY_DEFERRED**.

**NEXT_ACTION = P07 — emu_remote original HTTP listener auth, guest/PC device identification, action endpoint ACK versus execution, lifecycle and security boundaries**, documentation/read-only only; do not implement Proxy.
