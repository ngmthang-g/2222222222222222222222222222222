# L10 — Contradiction and ambiguity resolution

L10 compares L01-L09 and resolves only conflicts where one side has stronger/current evidence. Unresolved items stay UNKNOWN.

## Resolved contradictions

### 1. auto_reconnect name vs current behavior
Older/internal name:
`auto_reconnect_var / [DonVang] auto_reconnect`.

Current exact visible label and Dồn disconnect implementation:
**Dừng khi mất kết nối mạng**.

Resolution:
- preserve config/key name for compatibility;
- implement stop-on-disconnect;
- do not implement automatic reconnect.

Reason:
L08 direct current Dồn monitor evidence is stronger than the stale internal name.

### 2. receiver-row coordinate wording vs one shared coordinate
Some compatibility docs/keys refer to `recv_<n>_coord` or “tọa độ riêng của dòng”.

Current builder:
- one `_recv_coord_var`;
- every receiver row aliases it;
- screenshot shows one shared Tọa độ dồn selector.

Resolution:
one shared current Dồn coordinate wins.
Per-row coordinate fields remain compatibility/migration data only.

### 3. separate Bán/Train combo wording vs current role-switched selector
Legacy helper wording refers to separate Bán/Train selectors.

Current account-row builder exposes one `farm_var/cb_farm` pair whose label/value set changes by role.

Resolution:
reconstruct one role-switched current selector.

### 4. “acc được tick” bulk wording vs current _checked_rows
Legacy helper docs say “được tick”.

Current `_checked_rows` exact doc says all accounts in the list, excluding receiver accounts.

Resolution:
bulk donor helper universe = all listed nonreceivers.
Do not invent an absent current per-row selection checkbox requirement.

### 5. _farm_all vs visible Bắt đầu
`_farm_all` exists and wraps `_farm_acc`.

But:
- `_farm_acc` is only StartAutoFight Train primitive;
- current visible Bắt đầu binds `_toggle_farm`;
- `_toggle_farm` owns receiver/donor role split, monitors, generation and worker lifecycle.

Resolution:
Bắt đầu = `_toggle_farm`.
`_farm_all` remains legacy/internal.

### 6. Tới chỗ bán vs actual sell helper
Visible `Tới chỗ bán` binds `_move_sell_acc`.

`_sell_all` separately performs real sell flow.

Resolution:
Tới chỗ bán is movement-only.
Do not call `_sell_all` from that button.

### 7. manual receiver fallback vs automatic no-ready behavior
Manual `Tới nơi nhận` path has `_fallback_receiver`.

Automatic Dồn exact logs/flow say no ready/all busy -> skip cycle and farm.

Resolution:
fallback is manual/move-only.
Automatic Dồn must not use it.

### 8. sell-home Phù priority vs Dồn final leg
L03 proves `home_priority` is consumed by standard sell movement.

L02 proves the Dồn/receiver final leg is normal horse movement with no Phù.

Resolution:
keep the two movement policies separate.

### 9. receiver duplicate UI rows vs runtime receiver identity
Every receiver combo can show the same account candidate, so duplicate row selection is possible at UI level.

Runtime `_all_receiver_hwnds` returns a set.

Resolution:
duplicate selected rows do not create duplicate runtime receiver identities.

### 10. plan wording “heal/reconnect” vs Dồn's actual network behavior
Phase name suggested reconnect investigation.

L08 current Dồn implementation explicitly contains no reconnect engine.

Resolution:
the audit category may remain “heal/reconnect”, but reconstructed Dồn behavior is stop-on-disconnect only.

### 11. captured values vs defaults
Screenshots show values such as:
- Tọa độ 1 / Đại Lý / 0 / 0
- Trị liệu Tô Châu
- some checkboxes off/on.

Static code does not prove all captured values are universal fresh-install defaults.

Resolution:
treat screenshot values as captured runtime/config state unless exact default evidence exists.

## Preserved unresolved ambiguities

The following have no stronger evidence and must remain unresolved:

1. exact semantic of `stop_bag_check` default 3;
2. legacy duplicated nav-priority config migration;
3. exact fresh coordinate-row map/X/Y defaults;
4. exact winner for conflicting legacy `recv_coord` vs differing `recv_<n>_coord`;
5. exact stable candidate order before random equal-speed receiver choice;
6. exact `_gen` mutation statement/order;
7. exact assignment statement for each first-cycle receiver intermediate UI state;
8. exact worker join timeout/drain timing;
9. donor continuation when Quay lại train khi chết is unchecked;
10. treatment-failure next branch;
11. first death-monitor tick timing;
12. exact `is_trade_active` branch behavior in disconnect monitor;
13. same-window death/disconnect arbitration;
14. exact internal quick-move join/order;
15. quick-move overlap/cancellation against Farm start/stop;
16. live StartTab/Dồn-tab synchronization timing;
17. exact permission state used by the supplied capture.

## Rule for Stage S

If an implementation decision reaches one of the unresolved items above, it must either:

- preserve a neutral/fixture-driven boundary;
- or be explicitly labeled a reconstruction choice pending runtime parity.

It must not be recorded as recovered original behavior.
