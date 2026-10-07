# K11 — Tàng Bảo Đồ bag/item detection and treasure-map activation flow

## 1. Scope

K11 starts inside the already-frozen K10 top-level Tàng Bảo Đồ shell and audits only the activation portion of `_treasure_map_exec_sequence`.

It covers:
- mount pre-step only as far as needed to prepare treasure-map use;
- bag-open readiness;
- active treasure-map multipixel recognition;
- first use/click;
- movement-stop boundary;
- second recognition/use checkpoint;
- terminal not-found behavior.

Map96 movement/combat, final heal, and Treasure-specific reconnect/death internals are deferred.

## 2. Exact specimen first

The exact original was revalidated before using B08:
- TLMTool_2.1.2(7).zip SHA-256 `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`;
- inner TLMTool.exe SHA-256 `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`;
- `.daily_tab` = 35,163 bytes / 1,186 constants, exact end marker.

## 3. Mount pre-step

Exact log:
`[Tàng bảo đồ]   B0: mở ngựa`

The sequence reads character info field:
`IsRiding`, fallback `0`.

If already riding:
`Đã cưỡi thú → bỏ qua`.

If not already riding, the block contains:
- a 0.3-second settle constant;
- fixed coordinates `(1131,121)` and `(1073,123)`;
- configured pixel key `common.nguaActive`;
- exact fallback log `Ngựa chưa active → click (1306, 340)`;
- exact fallback coordinate `(1306,340)`;
- another fixed coordinate `(906,688)`.

`common.nguaActive` is frozen in pixel_data as:
- region `(903,683)`;
- RGB `(193,162,96)`;
- timeout `1`;
- tolerance `10`.

The existence/scope of the other fixed B0 coordinates is exact. Their exact source-line purpose/order is not safely instruction-bound, so K11 does not invent labels for them.

## 4. Bag-open stage

Exact log:
`[Tàng bảo đồ]   B1: mở túi`.

The compact constant block contains:
- fixed coordinate `(1296,421)`;
- a `wait_pixel` call surface with keywords `window_hwnd` and `timeout`;
- pixel key `tuido.active`;
- fixed coordinate pair `(870,635)` and `(910,145)`.

`tuido.active` frozen config:
- region `(1123,631)`;
- RGB `(150,166,78)`;
- timeout `5`;
- tolerance `10`.

Daily imports `drag_drop`, and the `(870,635) -> (910,145)` pair is serialized directly between the `tuido.active` check and the treasure-map search. This is a strong-static bag-preparation/drag surface.

The exact explicit timeout value passed by the Daily `wait_pixel` call and the exact false-return branch are not independently instruction-bound in K11.

## 5. Current treasure-map recognizer

Exact step log:
`[Tàng bảo đồ]   B2/2: Find multi tuido.tangBaoDo_multi`.

Exact helper:
`find_multipixel`.

Exact key:
`('tuido', 'tangBaoDo_multi')`.

Current `pixel_data` config:
- base search rectangle: `(702,163)` to `(1132,517)`;
- offset vector: `(20,30)`;
- base RGB: `(2,30,35)`;
- offset RGB: `(228,215,170)`;
- timeout: `5s`;
- tolerance: `1%`.

The shared `find_multipixel` helper contract is exact: one window capture, scan all base-color matches, verify the offset color for each candidate, and return the base client coordinate `(x,y)` for the first valid pair or `None`.

Legacy pixel definitions `tuido.tangBaoDo` and `tuido.tangBaoDo_multi_old` still exist in pixel_data, but the Daily K11 call explicitly names only `tuido.tangBaoDo_multi`.

## 6. First recognition success and background click

Exact success text:
`✓ Found tuido.tangBaoDo_multi at <found> → click`.

Daily imports the shared `mouse.click_at` helper. Its frozen helper documentation proves:
- background click;
- synchronous caller-thread operation;
- DLL synchronization protocol;
- `PostMessage` mouse delivery;
- explicit `window_hwnd` targeting takes priority;
- no physical mouse movement is required for the click path.

General helper defaults are:
- count = 1;
- delay = 0.5s;
- left click;
- jitter = True;
- hung_check = True.

The Treasure activation success block also serializes:
- `(950,370)`;
- `(490,427)`;
- `(1173,105)`;
- keyword surface `window_hwnd / count / jitter / delay`.

These fixed activation coordinates are unquestionably part of the success block, but the exact source-line role/order and exact override values for `count/jitter/delay` are not independently instruction-bound. K11 preserves them without assigning speculative button names.

## 7. First not-found is terminal for that Treasure account

Exact text:
`tuido.tangBaoDo_multi not found → dừng tàng bảo đồ cho acc này`.

This is not merely a one-cycle retry message. It explicitly terminates Tàng Bảo Đồ for the affected account.

The module also owns `_treasure_map_skipped`. Its role as activity account-skip state is exact, but the precise mutation statement/order at this not-found branch is not native-instruction-bound.

## 8. Movement-stop boundary after first activation

A fixed coordinate `(1155,108)` is serialized immediately before the movement-stop call. Its exact UI purpose is not text-bound and remains UNKNOWN.

Exact helper call:
`_wait_movement_stopped`.

Exact keyword names:
`stop_check`, `skip_set`.

No `by_memory` override is present.

K06 already recovered the helper defaults as `(None, None, False)`, therefore this Treasure call uses:
`by_memory=False`.

That means the active branch is the older `MovementDetector / is_moving` **10-pixel** path, not the `Direction+Pos` memory path.

The helper also owns:
- cancellation/timeout return behavior;
- post-stop `is_window_hung` probe;
- `HUNG_TIMEOUT` recovery shell.

Exact K11 success log after this boundary:
`[Tàng bảo đồ]   Đã dừng`.

## 9. Second treasure-map checkpoint

After movement has stopped, the flow checks `tuido.tangBaoDo_multi` again.

Exact failure text:
`tuido.tangBaoDo_multi not found (lần 2) → dừng tàng bảo đồ cho acc này`.

So K11 freezes a two-checkpoint structure:

1. find map item;
2. first use/click;
3. wait until movement stops;
4. find the map item again;
5. second use/click path;
6. continue to post-activation map outcome.

Both first and second not-found conditions are terminal for Tàng Bảo Đồ on that account.

The second successful path reuses the already-existing find/click constants and proceeds into MapID outcome handling. The exact repeated second-success click statement sequence is not separately logged, so K11 marks that microsequence strong-static rather than pretending to have source-line proof.

## 10. Immediate next boundary

The very next exact deep-flow text is:
`MapID=96 (huyệt mộ) → đánh ...`.

That is the boundary for K12. K11 stops before auditing map96 movement/combat.

## 11. Runtime cross-check

Only after static extraction, the packaged runtime log was searched.

Exact log SHA-256:
`17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`.

Correlated counts are zero for:
- `[Tàng bảo đồ]` / `[TÀNG BẢO ĐỒ]`;
- `tangBaoDo_multi`;
- `B0: mở ngựa`;
- `B1: mở túi`;
- `B2/2`;
- Treasure movement-stop text;
- the fixed activation coordinate strings.

B08 also shows only idle configuration and contains no runtime bag/item activation evidence.

K11 is therefore `STATIC_VERIFIED / END_TO_END_RUNTIME_ENV_REQUIRED`.

## 12. Reconstruction boundary

Preserve:
1. IsRiding pre-check and already-riding skip;
2. common.nguaActive configured check and exact `(1306,340)` fallback click;
3. bag-open readiness through `tuido.active`;
4. current recognizer = `tuido.tangBaoDo_multi`, not legacy keys;
5. exact multipixel region/colors/offset/timeout/tolerance;
6. background HWND-targeted click stack;
7. first not-found = terminal current Treasure account;
8. `_wait_movement_stopped(stop_check, skip_set)` with `by_memory=False`;
9. MovementDetector 10-pixel branch at this call site;
10. second `tangBaoDo_multi` checkpoint after movement stop;
11. second not-found = terminal current Treasure account;
12. successful second checkpoint hands off to MapID/post-activation processing.

Keep explicit UNKNOWN:
- exact role/order of B0 extra fixed coordinates;
- exact bag-open timeout override and failure effect;
- exact role/order of activation fixed coordinates;
- exact click `count/jitter/delay` overrides;
- purpose of `(1155,108)`;
- exact `_treasure_map_skipped` mutation micro-order;
- exact second-success repeated click statement sequence;
- live Windows/game parity.

Next: K12 — Tàng Bảo Đồ map96 movement / tomb combat / post-activation outcome audit.