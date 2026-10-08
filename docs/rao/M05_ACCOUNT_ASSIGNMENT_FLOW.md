# M05 — Rao account assignment / persistence audit

## Authority

M05 started by checking GitHub first. Current `main` was still exactly:

`5e884a36d59bdd13dcb689aa0e9fa0aaac26f245`

with M01-M04 complete, M05 marked NEXT, and no M05 artifacts. Nothing already completed was redone.

The exact frozen authority was then revalidated:

- archive SHA-256: `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`
- inner EXE SHA-256: `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`
- active module: `rao_tab.py / RaoTab`.

M01-M04 remain normative and unchanged.

## 1. Runtime account identity

Rao account rows are runtime-owned by HWND, not by character name.

`_acc_rows` is the live row registry, and the account path carries:

- HWND
- current PID
- bound window identity
- character info / RoleName
- per-row four Rao-selection variables.

This gives two separate identity layers:

1. **runtime row identity** = HWND + expected PID;
2. **persistent assignment identity** = real sanitized character name.

Do not replace one with the other.

## 2. Character-name resolution

The Rao module uses:

- `_get_char_info`
- `_get_char_name`
- `_sanitize_name`.

Exact `_sanitize_name` documentation:

> Loại bỏ HTML tags khỏi tên nhân vật.

The current pattern is:

`<[^>]+>`.

The character path carries the `RoleName` field.

When a real RoleName is not available, the module has an explicit pseudo-name surface beginning:

`Window `.

That pseudo-name is only a temporary row identity/display fallback. It is not a stable persistent character assignment identity.

No lowercase/casefold normalization surface was recovered in the current Rao block.

## 3. Persistent account key

`load_acc_config` receives a character name plus the row's four `rao_vars`.

Its exact constant surface contains:

- `startswith`
- `Window `
- section `Rao`
- prefix `acc_`
- `optionxform`
- `json.loads`.

The persistent account key is therefore:

`acc_<real sanitized character name>`

inside:

`[Rao]`.

The temporary `Window ...` fallback is explicitly screened before account-config restore and is not treated as a normal persistent character key.

No HWND or PID is part of the persistent key.

## 4. Four-slot assignment encoding

The current account row owns exactly **4** Rao-selection combobox/StringVar slots.

The account load block contains the literal 4 and exact documentation:

> Khôi phục 4 combobox nội dung rao đã lưu theo tên nhân vật.
> Chỉ áp tên rao còn tồn tại. Trả True nếu đã áp ít nhất 1 slot.

The save routine owns:

- account row
- character name `cname`
- `_vals`
- per-value `_v`
- shared `json.dumps`.

The load routine owns:

- `raw`
- `vals`
- `parsed`
- `json.loads`
- the four `rao_vars`.

The current account payload is therefore a **position-preserving JSON list of four Rao display-name strings**, stored under the one `acc_<character>` key.

Semantic form:

```json
["Rao 1", "Rao 3", "", "Rao 2"]
```

Slot order is significant:

- list index 0 -> slot 1
- index 1 -> slot 2
- index 2 -> slot 3
- index 3 -> slot 4.

No per-slot `acc_<name>_1` style key family is recovered.

No uniqueness rule between the four selections is recovered; the same Rao definition may be selected in more than one slot.

## 5. Save boundary

`_on_rao_var_changed` has exact documentation:

> Trace combobox nội dung rao: đánh dấu user đổi + lưu setting.

A manual account-combobox edit therefore:

1. marks the row as user-touched through the `_rao_touched` boundary;
2. persists the current assignment set.

The central `_save_config` routine saves both Rao definitions and current live account assignments while preserving the independent config families in `[Rao]`.

M02 already froze that `rao_` definitions are rewritten independently rather than replacing the whole section.

The save-local surface `cname/_vals/_v` confirms account values are gathered from the four live Rao vars.

The account payload uses the same JSON save family. The exact source statement around `ensure_ascii=False` is not reconstructed call-by-call, but the persistent assignment values are Rao display-name strings, not numeric IDs or HWNDs.

## 6. Restore rules

`load_acc_config(cname, rao_vars)`:

- refuses the temporary `Window ...` pseudo-name boundary;
- reads `[Rao]`;
- looks up `acc_<cname>`;
- JSON-decodes the saved assignment list;
- compares saved values with the current Rao-definition name universe;
- only applies a saved name when that Rao definition still exists;
- returns True if at least one slot was successfully applied.

Stale/deleted Rao names are therefore **not restored as runnable assignments**.

If a saved list contains fewer usable entries, the unmatched slots remain unassigned.

The account row still has only four live variables, so data beyond the four current slots cannot create additional active slots.

Exact malformed-JSON/non-list fallback details remain explicit UNKNOWN rather than being guessed.

## 7. Rename/delete reconciliation — immediate UI behavior

M02 left the immediate stale StringVar behavior open. M05 resolves the UI side more strongly.

`_refresh_acc_rao_options` owns:

- current `names`
- previous/suppression state `prev`
- row
- combobox
- variable
- current value `cur`
- an exact empty-string constant.

Its exact documentation:

> Đổ lại combobox nội dung rao của mọi acc theo danh sách tên hiện tại.

The current function therefore does more than replace combobox `values`: it checks each current account selection against the rebuilt Rao-name universe and clears a selection that is no longer valid.

Result:

- delete referenced `Rao X` -> affected account slot is cleared in the live UI;
- rename `Rao X -> Rao Y` -> old `Rao X` selection is not automatically aliased to `Rao Y`; it becomes stale and is cleared.

There is still no old-name -> new-name alias table or UUID-based rename propagation.

The exact persistence timing of that automatic clear is not fully source-visible: the `prev` local is consistent with temporary save/trace suppression while options are refreshed. Therefore **UI clearing is STATIC_VERIFIED**, while whether that auto-clear is written to disk in the same callback versus the next ordinary save remains **EXPLICIT_UNKNOWN**.

A later load is safe either way because `load_acc_config` only applies names that still exist.

## 8. Delayed RoleName and user-touch protection

The account row tracks both:

- `_has_real_name`
- `_rao_touched`.

The add/update path carries:

- temporary/fallback name;
- real `RoleName`;
- `load_acc_config`;
- the row's `rao_vars`;
- the user-touch flag.

This is a deliberate race guard for accounts whose real character name appears later than the window row.

Frozen semantic boundary:

- before real RoleName exists, the row may exist as `Window ...`;
- when a real name later appears, persisted `acc_<real name>` assignments may be restored;
- if the user already manually changed Rao selections on that temporary row, the delayed config restore must not overwrite those user choices.

The exact boolean assignment order for `_has_real_name/_rao_touched` is not reconstructed from the constants, but the protection boundary is direct static evidence.

## 9. HWND/PID reuse

`_add_or_update_row` has an exact diagnostic surface:

`[Rao] hwnd=<...> đổi process (pid <old> → <new>) — cửa sổ cũ đã mất, tạo lại row mới`.

The row path also directly uses:

- `bind_window_identity`
- `unbind_window_identity`
- current/old PID
- `_is_window_alive`.

Therefore:

- same HWND + same expected PID -> existing runtime row may be updated;
- same HWND reused by a different PID -> old runtime identity is invalidated and a new row is created;
- a reused HWND must not inherit old worker/window identity merely because the integer HWND is the same.

This is separate from assignment persistence: the newly created row can still restore by the real character-name key after identity is resolved.

## 10. Closed/disappeared accounts

Exact `_remove_stale_accs` documentation:

> Xóa acc của window đã đóng HOẶC đã đổi process (HWND tái sử dụng).

Its locals include:

- active HWND set
- bound/unbound identity
- row
- stale
- old PID
- current PID.

When an account disappears, the runtime row is removed/unbound.

The `[Rao]` persistence model does not use HWND as the account key, and `_save_config` does not replace the whole section with only current rows. Existing `acc_<character>` records therefore remain available for a later reappearance.

When the same real character reappears in a new window/PID, a fresh runtime row can restore its four saved assignments by character name.

Exact running-worker shutdown ordering when a window disappears belongs to M06.

## 11. Duplicate character names

Runtime rows are still distinct by HWND/PID.

Persistence is not.

No Rao equivalent of Dồn's “name + parenthesized HWND” persistent disambiguation is recovered.

Therefore two simultaneously managed windows whose sanitized real character names are identical map to the same:

`acc_<character name>`

persistent key.

Consequences:

- they may exist as separate live rows;
- they cannot have two independently addressable persisted assignment records under the current schema;
- if their four live selections differ, the exact last/first save winner under a collision is not safely source-visible and remains **EXPLICIT_UNKNOWN**.

Do not invent an HWND suffix in the Rao config key during reconstruction.

## 12. Assignment edits while a slot is running

`_on_rao_var_changed` is documented only as user-change marking + setting save; it has no recovered semantic requiring a worker restart.

M04 already froze that every active `_slot_loop` re-reads the currently selected Rao name and re-resolves the definition on each loop.

Therefore changing slot N's account assignment while slot N is running behaves as a **live next-cycle selection change**:

- the wait already in progress keeps its previously resolved interval;
- no full slot restart is required merely because the selected Rao name changed;
- after that wait, the next loop reads the new selected Rao name;
- valid new Rao -> subsequent send uses the new content/channel/interval;
- blank/deleted/invalid new Rao -> next resolution fails closed and the slot stops through the existing invalid-definition path.

This mirrors M04's live interval-edit boundary.

The exact state-label transition when a running slot stops because its newly selected Rao becomes invalid remains M06.

## 13. Refresh / reappearance policy

The account list refreshes incrementally every 5 seconds while the Rao tab refresh loop is active.

The refresh worker:

- discovers current game windows;
- binds current HWND/PID identity;
- adds new rows;
- updates existing rows;
- removes stale/reused identities.

It does not use character-name persistence as the live row dictionary key.

This protects against:
- HWND reuse;
- late character info;
- temporary window-title fallback.

At persistence time, the real sanitized character name remains the stable config identity.

## 14. Screenshot/runtime cross-check

The supplied Rao screenshot has no current account rows, so it does not provide visual evidence for the four-slot row itself.

M05 therefore relies on exact EXE static evidence for account assignment.

The frozen packaged `automove_log.txt` remains:

- SHA-256 `17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`
- no correlated `[Rao]`, `Đang rao`, assignment, or `Window ` traces.

Live HWND/PID timing and worker shutdown remain runtime-required.

## M05 boundary

Verified:

- runtime row identity = HWND/PID;
- persistence identity = real sanitized character name;
- temporary `Window ...` fallback is not a normal restore key;
- exact `acc_<character>` family;
- exactly four ordered account Rao slots;
- JSON four-value assignment payload;
- only currently existing Rao names restore;
- stale renamed/deleted live selections are cleared from account comboboxes;
- no rename alias/UUID propagation;
- delayed real-name restore protected by user-touch state;
- reused HWND/different PID recreates row;
- disappeared account can restore later by real name;
- duplicate real character names collide at the persistence-key layer;
- changing assignment while running takes effect on the next worker cycle without a forced restart.

Explicit unknown/runtime-required edges:

- exact malformed/non-list account JSON fallback;
- exact disk-save timing for automatic stale-selection clearing;
- exact save winner when duplicate character names collide;
- exact internal boolean mutation order for `_has_real_name/_rao_touched`;
- exact worker-stop/UI-state timing when account/window disappears;
- live refresh/identity race timing.

Deferred:

- M06 — full start/stop worker ownership/state behavior;
- M07 — Rao parity/reconstruction gate.
