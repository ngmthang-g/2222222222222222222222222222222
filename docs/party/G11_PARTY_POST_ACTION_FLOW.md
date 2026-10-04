# G11 — Party post-party dispatch flow

## Global aggregate only

global Bắt đầu
→ one thread per Party cluster
→ all cluster threads settle
→ _after_party_action once
→ _reset_run_button once

Single ▶ Tạo nhóm N worker
→ _run_one_group
→ _reset_single_button
→ NO independent post-party action.

## Mode dispatch

_after_party_action

wait
→ no-op

phoban
→ phoban_tab_ref exists?
   → NO: log missing ref
→ already running?
   → YES: skip
→ main thread
   → select notebook tab text "Phó bản"
   → start Phó Bản tab's own process

train
→ farm_tab_ref / Train

train_lsv
→ train_lsv_tab_ref / Train LSV

don
→ donvang_tab_ref / Dồn vàng

generic mode:
→ no ref: log/skip
→ no just-partied targets: log/skip
→ main thread selects destination tab
→ background readiness wait

## Target set

Party aggregate store:
→ _targets_lock
→ _last_targets

post-party generic target shape:
→ (name, Party-HWND)

No RoleID/TeamID is passed to farm dispatch.

## Hidden-tab readiness

after destination tab selection:
→ background _wait_and_dispatch_after_party
→ want = original Party target HWND set
→ read have from destination _acc_rows hwnd values
→ if want.issubset(have): ready early
→ else sleep 1.0s
→ max 20 polls / 20s

then:
→ main-thread lambda
→ _after_dispatch_main

## Main-thread destination matching

destination tab
→ must expose _toggle_single_farm
→ rows = _acc_rows

for each (name, Party-HWND):
1. exact HWND lookup
2. if not found, name lookup
   → exact/lowercase maps exist
   → log Party-HWND → destination-HWND
3. fresh re-resolution fallback
   → may yield new HWND
4. still missing
   → log + skip this account
5. found row already _farming_acc
   → skip, never blindly toggle off
6. otherwise
   → use current HWND from found destination row
   → _toggle_single_farm(current_row_hwnd)
   → log OK

used_hwnd state prevents accidental repeated consumption of the same destination row.

## Failure/cancel boundary

Ordinary cluster failures:
→ global _run_worker has no recovered success/result aggregation
→ after all threads settle, static flow still reaches once-only post-party phase
→ therefore no all-clusters-success gate is recovered.

Explicit global/manual cancellation:
→ exact post-party suppression/continuation branch remains UNKNOWN.
→ mandatory runtime parity case.
