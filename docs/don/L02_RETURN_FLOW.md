# L02 — Dồn return mechanism audit

## 1. Scope

L02 audits only how an account decides to leave train, how the return shortcut works, how it falls back, and where the flow hands off to Dồn/sell/receiver/train subsystems.

It does not deep-audit navigation-priority ordering, bag thresholds, receiver selection, transaction logic, selling internals, or train-state recovery.

## 2. Exact trigger modes

The Dồn tab has one exact town_condition_var. Its default internal value is cycle.

Visible modes:
- full_bag_timer → Khi đầy túi
- cycle → Theo chu kỳ (phút)

The cycle value defaults to 30 minutes. The farm-cycle local model contains cycle_start / condition / is_full_bag / loop_minutes / elapsed / sleep_time, and the same block serializes constant 60. Therefore the normal cycle trigger is minute-based. Exact sleep/poll micro-order remains UNKNOWN.

## 3. Full-bag trigger

When full-bag mode is selected, the farm loop owns is_full_bag, stop_bag_check, and _filter_before_don.

Exact messages prove the branch:
- ĐẦY túi (memory ... ô) → dồn
- đầy túi nhưng lọc còn chỗ (...) → ở lại, chờ vòng sau
- lọc xong vẫn đầy (...)

So filtering is performed before the final return/Dồn decision. If filtering frees space, the account stays at farm for a later cycle. If it remains full, return/Dồn continues.

Nearby numeric constants 3/98/100 are preserved but not interpreted here; exact bag thresholds belong to the inventory task.

## 4. Farm-cycle handoff

Exact farm-cycle documentation states that the loop does sell/mua thuốc/tới/farm and then waits for the cycle. It also states that don_callback replaces the normal return-to-town step with Dồn for a donor account.

This creates two high-level outcomes: normal sell/town flow or donor Dồn flow. Receiver selection is not audited in L02.

## 5. Return shortcut resolver

The Dồn-specific shortcut entry is _resolve_truyen_back.

Its exact contract is:
- inspect current MapID first;
- if memory read fails, fall back to the account's farm preset;
- resolve a back route from TRUYEN_DAI_LY_ROUTES;
- ordinary maps return no special route and use normal movement.

When a route exists, the back sequence runs and the Reader cache is invalidated before a fresh exit verification through fast_travel.verify_exited_farm.

## 6. Back-route data

Frozen farm_data contains active return routes for:
- 85/86 through map85 tile (226,58);
- 43 through (135,168);
- 49 through (147,209);
- 64 through (196,156);
- 60 through (207,200);
- 83 through (158,75);
- 75/76 through map75 tile (131,123).

These then use the serialized click/sleep/wait shape: click (892,472), click (480,427) twice, sleep 1, wait common.active 30.

Maps 1300/1400/1700 have route entries but their back lists are empty; those entries do not themselves provide a movement-back sequence.

## 7. Shortcut verification and fallback

The Dồn-specific resolver contract is explicit:
- no route → normal movement;
- route succeeds and fresh MapID confirms exit → continue;
- route verification fails: stop if requested, otherwise walk to the final destination.

So the Truyền back route is an optimization, not a required completion condition.

## 8. Return to Dồn/receiver point

The wrapper is _run_farm_exit. Its recovered locals are self, hwnd, map_var, x_var, y_var, stop_check, tag, route, exited. The directly adjacent defaults tuple is (None, Về dồn).

Exact documentation says to run the Truyền back shortcut first, then move normally to the receiver/Dồn destination. Critically, the final Dồn/receiver leg is normal horse movement with no phù. On a normal map with no back route, this path is equivalent to the old _move_acc behavior.

## 9. Standard return-to-sell path

The normal sell path is different. _sell_acc resolves configured sell coordinates, may use the back shortcut, and on shortcut failure logs that teleport missed and it will walk to the sell point.

The subsequent normal movement passes wait_for_arrival, stop_check and home_priority. The priority list comes from _get_nav_priority.

Exact helper documentation says it returns the UI priority list Phù 1/2/3, Ngựa to move_character. L03 owns exact ordering, deduplication and fallback policy.

The sell movement has one explicit retry after the first normal movement failure.

## 10. Stop/cancel ownership

Automatic farm return is cooperative. The farm-cycle stop_check propagates through _run_farm_exit, _resolve_truyen_back, _exec_truyen_steps, _move_acc, and movement retries. The serialized step executor returns False on fail/stop.

A manual _move_acc call differs: it may run with stop_check=None, but it first rejects a manual move if the account is currently auto-farming and asks the user to stop farm first.

No separate hard-kill return-worker ownership domain was recovered.

## 11. Dồn callback boundary

Inside _toggle_single_farm, the Dồn callback is built and passed into _farm_cycle. The donor-side state boundary includes Về dồn → Đang dồn. The actual transaction is delegated to don_logic.don_move_and_execute.

Receiver selection, per-receiver locking and transaction details are deferred. One exact failure handoff is already visible: when Dồn fails after reaching the receiver point, the donor is sent back toward farm.

## 12. Receiver-cycle boundary

The directly-called don_logic documentation shows receiver lifecycle as sell -> return to receiver point -> ready -> wait donated -> repeat. L02 records only that boundary.

## 13. Outbound route boundary

The same Truyền data also has to/to_from steps for town -> farm. That is the outbound half and belongs to later train-state analysis.

## 14. Debug-only surface

TEST_SKIP_TOWN exists inside the farm-cycle block. It is preserved as a debug/test bypass surface and is not treated as normal production return policy.

## 15. Runtime cross-check

The packaged automove_log.txt contains zero correlated Dồn-return markers searched for L02. Therefore L02 remains STATIC_VERIFIED / END_TO_END_RUNTIME_ENV_REQUIRED.

## 16. Reconstruction boundary

Preserve the two trigger modes, donor callback substitution, map-specific back shortcut, fresh exit verification, walk fallback when not stopped, horse/no-phù final receiver leg, normal sell path's home_priority handoff, and cooperative stop propagation.

Do not guess full-bag numeric threshold semantics, exact priority order policy, receiver choice, Dồn transaction mechanics, or live timing of the click/teleport chain.

Next: L03 — Dồn return priority audit.
