# E10 — Distributed start/stop coordination flow

Permission / plan / account-limit service
→ TLMMainApp visibility/enabled state
→ StartTab quick facade and feature-tab controls

Start Xếp-lưới transition:

farm_tab_ref._is_farming?
→ yes: _toggle_farm to stop

daily _punish_running?
→ yes: _punish_toggle to stop

daily _treasure_map_running?
→ yes: _treasure_map_toggle to stop

then:
→ enable layout sync
→ enable input sync

Switch Auto/manual:
→ disable layout sync
→ disable input sync

Start quick action:

Start button
→ short delegated thread
→ call feature-tab method
→ feature tab owns actual FSM/workers
→ feature state changes
→ _sync_start_tab_btn(s)
→ Start button mirrors feature state

Feature-family run model:

Farm / Train LSV / Đồn
→ single-account toggle or all-account action
→ owner permission/limit checks
→ owner running/busy state
→ per-account workers
→ stop via Event/flag/generation/_check_stop
→ owner cleanup
→ Start-button mirror

Daily:
→ separate Trừng Ác FSM
or
→ separate Tàng Bảo Đồ FSM
→ all-account/per-account worker ownership
→ _sync_start_tab_btns

Other all-account guards:
Rao / Tối ưu
→ _start_all_busy prevents duplicate starts

Phó Bản
→ _stop_all_runs owns its run shutdown

Post-login routing:
Login _auto_start_after_login
→ wait for login readiness
→ route to configured Party / Train / Train LSV / Đồn / Chờ behavior

Post-party routing:
parallel party group workers
→ wait until all groups finish
→ _after_party_action exactly once
→ reset Party UI

Tab refresh:
selected-tab _start_refresh / _stop_refresh
→ UI polling only
→ does NOT imply feature execution start/stop

Important non-rule:
No universal "starting any feature stops every other feature" mutex was recovered.
Only explicit cross-feature exclusions are carried forward.
