# K12 — Tàng Bảo Đồ map96 movement / tomb combat / post-activation outcome flow

## 1. Scope

K12 begins exactly where K11 stopped: after the second successful `tuido.tangBaoDo_multi` activation and the post-activation MapID outcome boundary.

K12 covers:
- MapID 96/tomb recognition;
- tomb-combat duration semantics;
- the fixed combat click surfaces;
- the map96/tile(50,16) movement surface;
- `common.active` wait;
- the non-map96 outcome;
- the immediate final-heal boundary and normal cycle tail.

Deep `_treasure_heal`, Treasure disconnect detector internals, and death-monitor internals remain for K13.

## 2. Exact original verified first

Frozen specimen:
- archive SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`;
- archive size 93,715,901 bytes;
- CRC clean;
- inner `TLMTool.exe` SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`;
- inner EXE size 47,450,112 bytes;
- `.daily_tab` = 35,163 bytes / 1,186 constants.

## 3. Duration has three distinct layers

K10 already froze the normal UI/config layer:
- visible tomb duration seed = 30 seconds;
- missing-key config fallback = 30 seconds.

K12 adds the hidden direct-helper layer.

Immediately before `DailyTab._treasure_map_exec_sequence`, the frozen default tuple is:
`(5, None, None, None)`.

Given the recovered argument/local order:
`self, hwnd, tomb_dur, halt, respawn_event, stop_event, ...`

the direct helper fallback is:
- `tomb_dur=5`;
- `halt=None`;
- `respawn_event=None`;
- `stop_event=None`.

This does not contradict the 30-second UI setting. The K10 workers own/pass configured `tomb_dur`. The 5-second value is the helper fallback if the method is called without a duration.

## 4. Map96/tomb branch

Exact text:
`[Tàng bảo đồ]   MapID=96 (huyệt mộ) → đánh <tomb_dur>...`

Exact state:
`Đánh trong mộ`.

This proves `tomb_dur` is a duration in seconds for the current tomb-combat stage.

There is no user Treasure repeat-count configuration, so this value must not be interpreted as number of tomb runs.

## 5. Combat timing primitive is not the Trừng Ác timer

K06 Trừng Ác combat had `_t_end` + `monotonic` evidence.

The Treasure execution local model has no `_t_end`, and no Treasure-local monotonic reference is recovered.

Therefore K12 freezes:
- duration semantic = exact;
- exact underlying timer primitive = UNKNOWN.

Do not silently copy the K06 monotonic-deadline implementation into Treasure merely because both are timed combat stages.

## 6. Fixed tomb-combat click surfaces

Immediately in the map96/tomb block, exact tuples exist:
- `(1135,124)`;
- `(955,123)`.

They are fixed UI click surfaces associated with the tomb branch.

Their exact per-button meaning, order relative to the duration dwell, and whether they bracket the dwell are not independently source-line-bound. K12 preserves the coordinates but does not invent labels such as 'start auto fight' or 'stop auto fight'.

## 7. Move to map96 tile (50,16)

Exact log:
`[Tàng bảo đồ]   Di chuyển đến map 96, tọa độ (50, 16)`.

Exact state:
`Đi huyệt mộ`.

Serialized movement values:
- `1600`;
- `512`.

These equal:
- `50 * 32 = 1600`;
- `16 * 32 = 512`.

So the visible tile target `(50,16)` is passed to the movement subsystem in pixel/world units `(1600,512)`.

Exact keyword surface:
`map_id / x_tile / y_tile / wait_for_arrival / stop_check`.

The directly-called shared helper is `utils.move_character`.

## 8. Shared move_character defaults at this boundary

Frozen shared optional defaults:
- `wait_for_arrival=False`;
- `stop_check=None`;
- `home_priority=None`;
- `follow_mode=False`;
- `tolerance=48`.

K12 explicitly passes `wait_for_arrival` and `stop_check`.

The exact Boolean value supplied to `wait_for_arrival` is not separately instruction-bound by current evidence, so K12 does not promote it to exact.

No K12-specific movement-failure text is recovered before the later active/MapID checks. The exact caller action on `move_character=False` therefore remains UNKNOWN.

## 9. common.active wait after movement

Exact log:
`[Tàng bảo đồ]   Chờ common.active...`.

Exact `wait_pixel` keyword surface:
`window_hwnd / timeout / debug / cancel_flag`.

The shared key is:
`('common','active')`.

Frozen `common.active` pixel:
- point `(1330,33)`;
- RGB `(34,8,11)`;
- configured timeout `100`;
- tolerance `5`.

However K12 explicitly supplies a timeout argument, so the `pixel_data` timeout of 100 cannot automatically be treated as the effective call timeout.

The explicit K12 timeout numeric value remains UNKNOWN.

Shared `wait_pixel` contract is exact:
- True when the configured pixel appears before timeout;
- False on timeout/cancel.

K12 has no independently bound text for the exact caller branch after a False result, so that micro-effect remains UNKNOWN.

## 10. Post-wait MapID outcome

Exact prefix:
`[Tàng bảo đồ]   MapID=`.

Exact non-tomb suffix:
` — không phải huyệt mộ, bỏ qua`.

This is not an account-terminal `dừng tàng bảo đồ cho acc này` message like the K11 item-not-found branches.

K12 therefore classifies non-96 as:
`SKIP_TOMB_OUTCOME / NOT_ACCOUNT_TERMINAL`.

The immediate following static boundary is the final-heal check.

## 11. Final-heal boundary

Exact text:
`% — kiểm tra trị liệu`.

Exact failure text:
`[Tàng bảo đồ]   Heal cuối vòng thất bại`.

The existing helper is:
`_treasure_heal`.

Combined with K10's visible/config contract, this is the Treasure low-HP treatment subsystem at the cycle tail.

K12 does not deep-audit treatment movement/click internals; K13 owns that work.

Final-heal failure is a cycle-tail fail-soft/log-only surface, not an independently recovered account-terminal stop.

## 12. Normal cycle tail

Exact Treasure prefix:
`[Tàng bảo đồ] === HWND `.

The module already owns the shared cycle suffix:
` — Kết thúc ===`.

Normal completion therefore returns control to the K10 Treasure worker/session shell for later work/iterations.

The exact Python success return scalar remains UNKNOWN.

## 13. Runtime/B08 cross-check

Only after static extraction, the packaged runtime log was searched.

Counts are zero for:
- `MapID=96`;
- `Đánh trong mộ`;
- `Đi huyệt mộ`;
- `Chờ common.active`;
- `tọa độ (50, 16)`;
- `huyệt mộ`.

Exact log SHA-256 remains:
`17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`.

B08 confirms configured tomb duration 30 and idle Treasure controls only. It does not show map96/combat runtime behavior.

K12 remains:
`STATIC_VERIFIED / END_TO_END_RUNTIME_ENV_REQUIRED`.

## 14. Reconstruction boundary

Preserve:
1. configured worker duration layer = 30 by default;
2. direct exec helper fallback duration = 5;
3. `MapID=96 -> đánh <tomb_dur>` semantic;
4. state `Đánh trong mộ`;
5. exact fixed click coordinates `(1135,124)` and `(955,123)` without invented labels;
6. map96 tile `(50,16)` / movement values `(1600,512)`;
7. move_character keyword surface;
8. common.active wait and exact configured pixel;
9. explicit-timeout override boundary;
10. non-96 = skip tomb outcome, not account-terminal;
11. immediate final-heal boundary;
12. Treasure cycle-tail handoff.

Keep UNKNOWN:
- exact tomb click meanings/order;
- exact tomb duration timing primitive;
- exact Boolean passed to `wait_for_arrival`;
- exact move failure caller effect;
- explicit common.active timeout numeric;
- common.active False-return caller effect;
- exact source micro-order around MapID read / fight / move;
- exact success return scalar;
- live runtime parity.

Next: K13 — Tàng Bảo Đồ heal / reconnect / respawn recovery audit.