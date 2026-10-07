# K10 — Tàng Bảo Đồ top-level configuration / selection / run-loop flow

## 1. Scope

K10 freezes only the Tàng Bảo Đồ top-level shell. It intentionally does not deep-audit the treasure item, mount/bag opening, pixel match, map-96 movement/combat, or treatment internals yet.

Exact frozen authority was re-inspected first:
- TLMTool_2.1.2(7).zip SHA-256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd;
- inner TLMTool.dist/TLMTool.exe SHA-256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22;
- .daily_tab decoded exactly as 35,163 bytes / 1,186 constants.

## 2. Visible/config surface

Frozen visible Tàng Bảo Đồ controls:
- Thời gian đánh trong huyệt mộ (giây): UI seed 30;
- Trị liệu sau khi đào nếu HP < 30%;
- Vị trí trị liệu: visible Tô Châu;
- reconnect toggle;
- respawn toggle;
- Áp dụng Tàng bảo đồ cho tất cả acc.

Exact missing-key config fallbacks:
- daily_treasure_map_tomb_dur = "30";
- daily_treasure_heal = "0";
- daily_treasure_heal_map = "Tô Châu";
- daily_treasure_dc_reconnect = "1";
- daily_treasure_respawn = "1".

Unlike the Trừng Ác duration layering issue, the Tàng Bảo Đồ UI seed and missing-key duration fallback both resolve to 30.

## 3. Treatment-location combobox boundary

TREASURE_HEAL_COORDS is already exact at the UI/config boundary:
- Đại Lý -> (43,178);
- Lạc Dương -> (255,126);
- Tô Châu -> (155,252);
- Lâu Lan -> (27,183).

K10 records these as selectable configuration values only. Actual heal movement/click semantics remain later work.

## 4. Apply-all is configuration only

_apply_treasure_all exact documentation:
Đặt combobox hoạt động = 'Tàng bảo đồ' cho tất cả acc.

Therefore:

Áp dụng Tàng bảo đồ cho tất cả acc
-> set each current Daily row activity_var to Tàng bảo đồ
-> do not start execution by itself.

This matches the K02 row/activity coordinator contract.

## 5. Activity-wide start path

Exact wrapper documentation:
Nút Bắt đầu (Tàng bảo đồ): inject trước rồi bật quy trình.

Top-level path:

_treasure_start_worker
-> shared injection/preparation
-> _treasure_map_toggle
-> _treasure_map_run_worker.

The dedicated activity button is btn_treasure_start.

## 6. Activity-wide batch ownership

_treasure_map_run_worker exact locals include:
- tomb_dur;
- selected;
- selected_pids;
- loop_idx;
- alive;
- still_active;
- wins;
- halt;
- threads;
- respawn_event;
- monitor_stop.

Therefore the activity-wide shell has the same architectural separation as Trừng Ác:
- start-time selection;
- PID identity snapshot;
- repeated live/still-active filtering;
- parallel account work through child threads;
- activity-level stop/recovery state.

## 7. Batch loop termination

Exact terminal/log surfaces:
- Chưa acc nào chọn Tàng bảo đồ — bỏ qua;
- Không còn acc nào sống — dừng;
- Tất cả ... acc đã dừng — tự động dừng;
- [TÀNG BẢO ĐỒ] Lần ...

There is no daily_treasure_repeat / repeat_count / max_repeat config in the decoded Daily blob.

Thus tomb_dur is a per-cycle tomb-combat duration parameter, not a user-configured number of repetitions. The activity batch is open-ended until cancelled or the eligible account set becomes empty/stopped.

## 8. Per-row / bottom all-account path

K02 already proves that a row selected as Tàng bảo đồ starts:
_treasure_single_worker.

K10 exact single-worker locals include:
- hwnd;
- tomb_dur;
- row;
- gen_snap;
- halt;
- respawn_event;
- monitor_stop;
- invalidate_character_cache;
- _get_pid_from_hwnd;
- wait_memory_ready;
- _exit_why.

The worker directly calls _treasure_map_exec_sequence and owns row/session recovery state.

Do not collapse this into _treasure_map_run_worker. The row/bottom path keeps the K02 Event + generation ownership model.

An explicit single-worker loop_idx local is not recovered. K10 therefore does not invent cycle-count logging for this path. The worker is preserved as a session wrapper around the execution sequence and recovery shell; exact source-form repetition remains a later/runtime microdetail.

## 9. Disconnect/reconnect shell

Dedicated per-row monitor:
_treasure_map_disconnect_monitor.

Activity-wide nested recovery surface:
_treasure_monitor_stops.

Exact batch messages:
- Phát hiện mất kết nối → chờ kết nối lại...;
- Kết nối lại OK → tiếp tục;
- Kết nối lại timeout → dừng.

K10 freezes only that bounded success/timeout shell. The treasure-specific numeric timeout is not independently instruction-bound here and remains UNKNOWN rather than being copied from Trừng Ác.

The single-worker locals also expose Reader-cache invalidation and wait_memory_ready, proving a post-reconnect memory-recovery boundary exists. Numeric/detail semantics are deferred to a later treasure recovery task.

## 10. Death/Địa-phủ shell

Both treasure batch and single-worker local models own respawn_event and monitor_stop.

_treasure_map_exec_sequence exact entry text:
respawn_event đang set → clear, cho heal/move rời map 87.

This proves Tàng Bảo Đồ is wired into the shared Daily death/respawn event model at the top-level boundary.

K10 does not re-audit the shared _diaphu_monitor cadence/click internals or exact monitor-thread launch order. Those details belong to the shared/recovery layer.

## 11. Activity UI reset

Exact treasure idle/reset tuple:
Tàng bảo đồ / RoyalBlue / normal.

The module also has the shared activity-running/stopping literal pool:
- Dừng lại / FireBrick;
- Đang dừng... / disabled.

btn_treasure_start and _treasure_map_run_worker are exact. K10 preserves the shared toggle-state behavior but leaves exact source-line assignment/teardown ordering UNKNOWN.

K02's _daily_all_monitor resets both activity UIs after all row sessions end, and _sync_start_tab_btns synchronizes the external StartTab controls.

## 12. Runtime cross-check

Only after EXE/static extraction, B08 was cross-checked:
- tomb duration 30;
- treasure heal OFF;
- heal location Tô Châu;
- reconnect ON;
- respawn ON.

The packaged automove_log.txt was also checked:
- SHA-256 17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500;
- 387,238 lines / 15,741,058 bytes;
- zero correlated Tàng Bảo Đồ top-level worker/session markers.

So K10 is STATIC_VERIFIED / END_TO_END_RUNTIME_ENV_REQUIRED.

## 13. Deferred to K11+

Not deep-audited in K10:
- treasure-map item/bag identification;
- mount-open/bag-open steps;
- tuido.tangBaoDo_multi pixel matching;
- _wait_movement_stopped treasure call semantics;
- map 96 movement and tomb combat;
- treatment internals;
- treasure disconnect detector internals;
- exact reconnect timeout numeric;
- exact death-monitor thread launch order.

Next: K11 — Tàng Bảo Đồ bag/item detection and treasure-map activation audit.