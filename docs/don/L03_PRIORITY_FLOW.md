# L03 — Dồn return priority flow

## Authority first

Frozen specimen rechecked before this audit:

- archive SHA-256: `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`
- archive size: **93,715,901 bytes**
- inner `TLMTool.dist/TLMTool.exe` SHA-256: `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`
- inner EXE size: **47,450,112 bytes**
- Dồn authority: `donvang_tab.py / DonVangTab`

The uploaded `TLMTool_2.1.2(8).zip` is byte-identical to the frozen authority used by L01/L02. Screenshot comparison was performed only after static extraction.

## UI priority model

The compiled Dồn UI contains two exact serialized lists:

```text
NAV_OPTIONS  = ["", "Phù 1", "Phù 2", "Phù 3", "Ngựa"]
NAV_DEFAULTS = ["Phù 1", "Phù 2", "Phù 3", "Ngựa"]
```

Therefore:

- there are four visible priority slots;
- the initial order is Phù 1 → Phù 2 → Phù 3 → Ngựa;
- the empty string is an intentional selectable disable/unused value, not a missing extraction;
- each slot is a readonly combobox.

The user screenshot hash `dffb4da895d21dea87dd72a6601c29104f519dca89c2f716f5a7445bcbe4421a` cross-checks the exact default visible order after the EXE-first analysis.

## Duplicate prevention

`_on_nav_priority_changed` has the exact local-name surface:

```text
NAV_OPTIONS, idx, var, used, other_var, val, current, available
```

and is bound to the priority combobox selection path.

This is strong static evidence for the current UI policy:

1. recompute which values are already used by the other priority slots;
2. preserve the slot's current value;
3. rebuild the values available to that slot from `NAV_OPTIONS`;
4. exclude values already used elsewhere, while retaining the explicit blank option/current selection.

Because the controls are readonly, the normal UI cannot newly select a duplicate priority after the available-value lists are recomputed.

A hand-edited/legacy config that already contains duplicates is a migration edge case. The static artifact does not expose enough source-level branch detail to prove whether such an already-duplicated persisted state is automatically rewritten, so that one migration microcase remains runtime/config-fixture verification rather than being guessed.

## Persistence

Dồn persists the four slots under section `[DonVang]` using exact keys:

```text
nav_priority_1
nav_priority_2
nav_priority_3
nav_priority_4
```

The save-side compiled surface also contains prefix `nav_priority_`, while the load-side contains all four exact keys. The values are the StringVar labels selected by the UI.

Missing/new UI state starts from the exact compiled defaults above. Priority state is therefore per Dồn configuration, not per account row.

## Runtime adapter

`DonVangTab._get_nav_priority` has the exact compiled documentation:

> Trả list ưu tiên về thành từ UI (Phù 1/2/3, Ngựa) — truyền vào move_character.

The generic `utils.move_character` consumer has `home_priority`, `has_phu`, `sel`, and `key_num` locals plus the exact special label `Ngựa`. Its return-home block logs:

```text
[di chuyển]   Về thành: thử <selection> → bấm phím <key_num>
```

for teleport-key attempts. `Ngựa` is handled as the non-hotkey movement fallback rather than being converted to a Phù key.

The shared fast-travel documentation additionally states that `home_priority` is passed through for the return-town/walking leg and that callers which force horse movement pass `None`.

So the current policy is:

```text
ordered nonblank UI priorities
        ↓
_get_nav_priority()
        ↓
move_character(home_priority=...)
        ↓
try Phù entries in UI order
        ↓
Ngựa / ordinary movement fallback
```

The blank UI option disables that slot and is not a distinct travel mechanism.

## Dồn consumer boundary

Inside the exact Dồn module, the only production `home_priority` literal is in `_sell_acc`, immediately beside the `_get_nav_priority` call.

Therefore Dồn return priority applies to the normal/shared **sell movement** path only.

It does **not** automatically apply to:

- the L02 Dồn/receiver final leg, which is explicitly normal horse movement with **no phù**;
- the Truyền `back` shortcut executor itself;
- ordinary train-target movement;
- receiver-point movement that uses the L02 no-phù return wrapper.

Any caller that reaches the shared `_sell_acc` movement inherits the configured order; this does not widen the priority policy to unrelated Dồn movement helpers.

## Fallback and cancellation

L03 does not replace L02:

- Truyền back remains shortcut → fresh verify → walk fallback.
- Dồn/receiver final leg remains no-phù.
- `_sell_acc` still supports `stop_check` and its existing retry/cancel behavior.
- Priority selection only changes which return-home mechanisms `move_character` attempts before ordinary movement.

The exact timing between successive Phù attempts is owned by the shared movement primitive and is not redefined by Dồn.

## Runtime evidence

The packaged `automove_log.txt` remains SHA-256 `17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`.

Counts in that frozen log:

- `Về thành: thử`: 0
- `[DonVang]`: 0
- `[Donvang]`: 0
- `Dồn`: 0

Therefore the ordering contract is **STATIC_VERIFIED** but live attempt timing/failure progression still requires Windows + game runtime.

## L03 boundary

Resolved here:

- exact UI option set;
- exact default order;
- explicit blank/disabled slot;
- duplicate-prevention UI model;
- persistence keys;
- `_get_nav_priority` adapter;
- generic Phù/Ngựa consumer semantics;
- Dồn consumer boundary.

Deferred:

- legacy-config duplicate migration microbehavior;
- live Phù success/failure timing;
- inventory/full-bag thresholds and filtering internals → L04.
