# L10 — Minimum reconstruction acceptance tests for Dồn

These tests define the minimum Stage-S acceptance bar for the Dồn feature. They do not authorize writing source during Phase L.

## A. Static/UI contract tests

1. Dedicated Dồn tab contains the exact current visible groups and labels from L01.
2. StartTab contains Dồn vàng / Tới nơi nhận / Tới chỗ bán / Tới nơi train / Cấu hình.
3. Dồn filter exposes exactly Tất cả and Chỉ vũ khí; no Không option exists.
4. One and only one shared Tọa độ dồn selector exists above receiver rows.
5. Receiver rows contain account selector + delete; no per-row Dồn coordinate widget exists.
6. Saved-coordinate row contains name/map/X/Y + Train apply + delete.
7. Bottom quick actions are exactly Tới nơi nhận / Tới chỗ bán / Tới nơi train.
8. Big Bắt đầu is separate from the three quick actions.
9. No visible Dừng-all / Farm-all / Bán-all buttons are added.
10. State/color table exactly matches L07.

## B. Config round-trip tests

11. [DonVang] nav_priority_1..4 round-trip without rewriting valid values.
12. coord_<n>=preset_name|map_id|x|y round-trips and recreates dynamic rows.
13. Unknown/stale map IDs/names are skipped rather than guessed.
14. acc_<character>_farm restores only currently valid saved/sell values.
15. recv_count + recv_<n>_acc load dynamic receiver rows.
16. Legacy receiver/recv_coord keys remain accepted without inventing an unverified conflict winner.
17. respawn, auto_reconnect, trist, heal_map round-trip.
18. Legacy config key auto_reconnect must drive the visible **Dừng khi mất kết nối mạng** control, not an auto-reconnect loop.

## C. Return and inventory unit tests

19. cycle trigger default is 30 minutes.
20. full-bag mode uses occupied Site-10 slots.
21. hidden pickup OFF -> threshold 100.
22. hidden pickup ON -> threshold 98.
23. unreadable bag memory returns unknown/None and is never interpreted as zero.
24. Tất cả -> empty discard preset.
25. Chỉ vũ khí -> discard_nonweapon.
26. Hidden pickup helper writes PICKITEM.IsOn=True after its 5s helper delay.
27. Filter result below threshold stays at farm.
28. Filter result at/above threshold continues toward Dồn.
29. Filter no-result/error does not fabricate free space.
30. Dồn final receiver leg does not consume sell-home Phù priority.
31. Standard sell movement does consume ordered home priority.

## D. Coordinate tests

32. Exact Dồn built-in coordinate table matches L05.
33. Exact sell built-in coordinate table matches L05.
34. Exact treatment coordinate table matches L08.
35. Saved preset rename updates active account selector values.
36. Apply-all sends the saved preset **name**, not copied coordinate values.
37. Role-switched account selector exposes donor Train choices and receiver sell choices.
38. Invalid coordinate resolution fails closed.
39. All receiver rows resolve the same current shared Dồn coordinate.

## E. Receiver/locking tests

40. Receiver registry is per HWND and contains ready/donated/aborted/donor ownership.
41. Receiver cycle does not mark ready until successful return to receive point.
42. Automatic candidate excludes donor itself.
43. Automatic candidate requires ready + valid coordinate.
44. Minimum current donated-gold/hour receiver wins.
45. Equal minimum-speed candidates are tie-randomized.
46. Readiness is rechecked after receiver lock acquisition.
47. Same receiver cannot be served by two donors simultaneously.
48. Different receivers can be served in parallel.
49. No-ready/all-busy automatic Dồn skips cycle and donor continues farm.
50. Manual Tới nơi nhận may use first-valid fallback.
51. Manual fallback is never substituted into automatic no-ready behavior.
52. Receiver abort/dead-donor reset is isolated to that receiver.
53. Background watcher accepts managed inviter, rejects unknown inviter, and yields while receiver is claimed.

## F. Lifecycle tests

54. Start selected receiver -> recv_cycle worker.
55. Start normal account -> donor _farm_cycle with Dồn callback.
56. _farm_acc alone does not create full Dồn lifecycle state.
57. Changing receiver selection while running does not hot-swap worker role.
58. Stop/start after role change creates worker for new role.
59. Partial account stop leaves other active sessions running.
60. Final active account stop drains then resets global Bắt đầu projection.
61. Old-generation worker cannot overwrite a newer run's play button/state.
62. Worker state updates marshal through the Tk main thread.

## G. Death/treatment tests

63. MapID 87 sets one respawn event per continuous episode.
64. Leaving map87 rearms detection.
65. Real numeric HP 0 clicks client (792,441) once per zero-HP episode.
66. Unreadable HP must not cause respawn click.
67. Receiver death recovery returns to receiver lifecycle rather than Train-role conversion.
68. Treatment resolves built-in/manual destination, moves there, then uses (892,474) + (514,424) ×4.
69. Quay lại train khi chết must not gate the HP0 respawn click.
70. Unknown donor continuation when respawn is unchecked remains fixture-driven rather than guessed.

## H. Disconnect tests

71. Watchdog cadence contract is 2s.
72. Connected=True resets/vetoes the disconnect strike chain.
73. Memory False/None alone does not stop the account.
74. Both disconnect pixels must be present.
75. Three consecutive hits are required.
76. Confirmed disconnect halts/stops receiver session.
77. Confirmed disconnect halts/stops donor session.
78. Dồn must not execute reconnect_ok, reconnect click, common.active reconnect batch, or retry loop.
79. User restart is required after confirmed Dồn disconnect.

## I. All-account quick-action tests

80. Dedicated-tab Tới nơi nhận delegates to _move_all_recv.
81. Dedicated-tab Tới chỗ bán delegates to _move_sell_acc and does not sell inventory.
82. Dedicated-tab Tới nơi train delegates to _move_all.
83. _move_all excludes receivers and uses donor Train destinations.
84. _move_sell_acc targets receivers and their selected sell destinations.
85. _move_all_recv applies donor/receiver role-specific movement and current shared Dồn coordinate semantics.
86. Big Bắt đầu delegates to _toggle_farm, not _farm_all.
87. Legacy _stop_all/_farm_all/_sell_all methods may remain internal but must not be exposed as new visible buttons.

## J. StartTab parity tests

88. StartTab Dồn vàng and dedicated Dồn Bắt đầu control the same lifecycle state.
89. StartTab Tới nơi nhận delegates to the same _move_all_recv implementation.
90. StartTab Tới chỗ bán delegates to the same _move_sell_acc implementation.
91. StartTab Tới nơi train delegates to the same _move_all implementation.
92. StartTab Cấu hình navigates to Dồn tab rather than duplicating configuration UI.

## K. Runtime-required fixtures

The following cannot be declared PASS from Linux/static reconstruction alone and must remain a separate live parity suite:

93. exact cycle polling timing;
94. live Truyền click/exit timing;
95. discard-memory propagation timing;
96. receiver lock/readiness race timing;
97. trade watcher vs live transaction race behavior;
98. generation/drain/join timing;
99. role-change while live workers are in subflows;
100. death/treatment timing against real game UI;
101. disconnect third-strike timing against real dialog;
102. quick-move overlap with a simultaneously started/stopped Farm session;
103. StartTab/Dồn-tab synchronization timing.

## Gate rule

A Stage-S implementation may claim **static Dồn parity** only when tests 1–92 pass or when a test explicitly depends on an L10 EXPLICIT_UNKNOWN fixture and remains marked unresolved rather than guessed.

It may claim **live Dồn parity** only after the runtime-required fixtures are executed successfully on Windows with a live Thần Long client.
