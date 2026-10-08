# M02 — Rao message storage audit

## Authority

M02 re-used the exact frozen Rao authority verified by M01:

- archive SHA-256: `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`
- inner EXE SHA-256: `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`
- module: `rao_tab.py / RaoTab`
- serialized `.rao_tab` block: `0x2bd7850`, 11,774 bytes, 582 constants.

M02 does not reopen channel-ID semantics, interval timing, account assignment persistence, or start/stop workers beyond the message-identity boundary.

## 1. Live Rao definition model

A Rao definition row owns four live variables:

- `name_var`
- `msg_var`
- `chan_var`
- `sec_var`.

The row also owns its UI frame/channel combobox/delete button, but **the Rao identity used by account selections is the current trimmed display name**, not a hidden UUID.

There is no persistent message-row UUID recovered.

### Current name list

Exact `_rao_names` documentation:

> Danh sách tên rao hiện có (giữ thứ tự dòng).

Therefore the runtime selection surface is generated from the current row order.

### Automatic naming

Exact `_next_rao_name` documentation:

> Tên tự động Rao 1, Rao 2, ... (số nhỏ nhất chưa dùng).

So adding with `name=None` uses the smallest unused positive `Rao N`.

This only guarantees uniqueness for the **auto-generated name**. No current duplicate-name validation/warning surface was recovered for a user manually editing a row name.

## 2. Add/edit trace behavior

Exact `_add_rao_row` documentation:

> Thêm một dòng cấu hình rao. name=None → tự đặt Rao 1, Rao 2, ...

The compiled row surface contains a nested `_rao_save` callback plus `trace_add("write", ...)` and the four row variables.

The write callback directly exposes:

- `_save_config`
- `_refresh_acc_rao_options`.

Therefore edits to a Rao row are live configuration edits: changing its visible definition triggers persistence and refreshes the account-side Rao-name option lists rather than waiting for the main **Bắt đầu** button.

M02 freezes message identity as **name-based**.

## 3. Delete behavior

Exact `_remove_rao_row` documentation:

> Xóa một dòng rao (nút ✕ đỏ).

The static method surface contains:

- row-frame `destroy`
- list `pop`
- save/refresh dependencies from the same message-row family.

Deletion therefore removes the live row, persists the changed Rao-definition set, and causes account Rao-name options to be rebuilt from the remaining names.

There is no tombstone/message-row ID layer recovered.

## 4. Account selection reconciliation after rename/delete

`_refresh_acc_rao_options` has exact documentation:

> Đổ lại combobox nội dung rao của mọi acc theo danh sách tên hiện tại.

Its recovered locals include:

- `names`
- `prev`
- `row`
- `cb`
- `var`
- `cur`.

This is stronger than a simple static `values=names` boundary: the function explicitly carries both previous/current selection state while rebuilding account comboboxes.

M02 therefore freezes the following identity rule:

- account Rao selection is a **Rao-name reference**;
- rename/delete removes the old name from the valid option universe immediately;
- there is no recovered old-name→new-name alias table or UUID-based rename propagation;
- a stale old name is not a valid Rao definition and `_resolve_rao` rejects it as missing;
- a later config reload applies account selections only when the referenced Rao name still exists (exact account persistence mechanics remain M05).

The exact micro-choice between immediately clearing an already-displayed stale StringVar versus preserving that text until the account-assignment trace runs is not fully recoverable from M02's constant/local surface and remains an **EXPLICIT_UNKNOWN** for M05. It does not change the identity rule: the stale name cannot resolve.

This differs intentionally from Dồn L05, where preset rename propagation was directly proven.

## 5. Message resolution contract

`_resolve_rao(rao_name)` owns recovered locals:

- `rao_name`
- `want`
- `rd`
- `content`
- `chan_name`
- `total`.

Its exact documentation:

> Tên rao → (nội dung, interval_giây, channel_id, tên_kênh).
> (None, lý_do) nếu không dùng được.

Exact invalid reasons serialized in the current module include:

- **Chưa chọn nội dung rao**
- **Rao '<name>' chưa có nội dung**
- **'<name>' chưa chọn kênh**
- **'<name>' chưa đặt thời gian lặp**
- **'<name>' không còn tồn tại**.

Thus storage permits a row to exist with incomplete fields, but worker resolution fails closed until the selected definition is usable.

Channel-ID mapping is M03.
Interval parsing/clamping is M04.

## 6. Persistent storage location

Section:

`[Rao]`.

Two independent dynamic families coexist in that section:

- `rao_` — message definitions
- `acc_` — per-character selected Rao names.

M02 only freezes the `rao_` family.

Persistence uses the shared settings boundary:

- `_settings_lock`
- `read_settings`
- `write_settings`.

The settings writer preserves the account-family boundary; message save must not replace the entire `[Rao]` section.

## 7. Rao definition serialization

The exact current `_save_config` constant/local surface contains:

- locals: `cfg`, `cf`, `row`, `cname`, `_vals`, `_v`
- dynamic prefix: `rao_`
- `json.dumps`
- payload field literals:
  - `content`
  - `channel`
  - `sec`
- `ensure_ascii=False`
- `write_settings`.

The absence of an index local in the save-row loop, together with recovered `cname` and the load-side key split, fixes the current storage as a **name-keyed family**:

`rao_<trimmed Rao display name> = JSON payload`.

Current payload contract is:

```json
{
  "content": "<message text>",
  "channel": "<channel display value>",
  "sec": "<stored interval value>"
}
```

The Rao name itself is carried by the option-key suffix rather than requiring a separate persistent row UUID.

`ensure_ascii=False` preserves Vietnamese/unicode message text in the serialized JSON.

The exact stored scalar type/normalization of `sec` belongs to M04.

## 8. Save rewrite semantics

Because a rename changes the `rao_<name>` key and deletion must remove the old definition while `acc_` keys remain in the same section, the current save boundary is a **rao-family rewrite**:

1. read the existing settings object;
2. retain unrelated/`acc_` entries;
3. replace the current `rao_` definition family from live rows;
4. write settings.

No independent deleted-row tombstone is recovered.

This also means name identity is part of persistence, not merely a UI label.

## 9. Duplicate-name consequence

No manual duplicate-name rejection surface is recovered.

Because persistence is name-keyed, two live rows with the same trimmed Rao name cannot remain two independent persistent `rao_<name>` records.

Therefore:

- automatic naming avoids collisions;
- manual duplicates are not a stable persistent identity model;
- a duplicate-name save necessarily collapses/collides at the same config key.

The exact winner if two duplicate live rows are saved in one pass (first-vs-last assignment order) is not source-visible enough to freeze and remains **EXPLICIT_UNKNOWN**.

Likewise, exact duplicate-name winner in live `_resolve_rao` scanning is left unknown rather than guessed.

## 10. Blank-name boundary

`_rao_names` uses current trimmed names for the selection universe, and `_save_config` carries a trimmed `cname` key suffix.

No valid account-selection meaning for an empty Rao name is recovered.

M02 therefore treats a blank name as non-addressable by normal account selection. The exact save behavior for a manually blank row (skip versus a transient `rao_` key before normalization) is not source-visible enough and is left **EXPLICIT_UNKNOWN**.

## 11. Load behavior

The exact `_load_config` surface contains:

- section/key enumeration;
- `sorted`
- a local sort lambda;
- dynamic `rao_` keys;
- `json.loads`
- key `split`
- defaults containing `30`
- `TypeError` / `ValueError`
- load-side call keywords:
  - `name`
  - `content`
  - `seconds`
  - `channel`.

This freezes the high-level load contract:

1. collect `rao_` definition keys;
2. sort them deterministically;
3. derive the Rao display name from the `rao_` key suffix;
4. JSON-decode each payload;
5. obtain content/channel/sec with defaults/validation;
6. recreate a row through `_add_rao_row(name=..., content=..., seconds=..., channel=...)`.

There is no separate persistent row-order field recovered.

The exact comparator used by the sort lambda and exact malformed-record fallback/skip behavior are not safely recoverable from the constant surface and remain **EXPLICIT_UNKNOWN**.

Interval default/clamp details are M04.
Channel fallback details are M03.

## 12. Load/save trace suppression boundary

The class owns `_saving_enabled`.

Construction order exposes:

- build UI
- load config
- bind destroy/save hook
- start refresh.

This is consistent with suppressing recursive writes while initial definitions are being reconstructed and then enabling normal write traces.

The exact boolean transition instruction order is not recovered and is not invented.

## 13. Destroy save hook

The active class owns `_save_on_destroy` and binds `<Destroy>`.

This provides a final persistence path for Rao definitions at UI teardown.

The exact child-widget-vs-root destroy filtering guard is not source-visible enough for M02 and remains implementation detail for parity, not message schema.

## 14. Screenshot cross-check

Only after the static storage extraction, the user-supplied Rao screenshot was rechecked.

It shows one current definition row:

- name: **Rao 1**
- content: empty
- channel: **Thế giới**
- interval text: **30**.

This is consistent with the name-keyed row model and automatic `Rao N` naming.

The screenshot does **not** prove:
- universal message content default beyond empty captured state;
- interval normalization semantics;
- any persistent duplicate behavior.

## M02 boundary

Verified:

- Rao definition live variables
- display-name identity
- smallest-unused auto naming
- live write-trace save/option refresh
- delete/remove persistence boundary
- name-based account-reference invalidation boundary
- exact resolve error surfaces
- `[Rao]` / `rao_` message family
- name-keyed `rao_<display name>` storage
- JSON payload fields `content/channel/sec`
- `ensure_ascii=False`
- deterministic sorted load
- no persistent row UUID
- duplicate-name persistence collision boundary.

Deferred:

- M03 — channel display→packet ID/fallback behavior
- M04 — interval storage type, default, clamp and scheduling semantics
- M05 — exact account-selection persistence and immediate StringVar reconciliation
- M06 — slot worker/start-stop behavior
- M07 — parity/reconstruction gate.
