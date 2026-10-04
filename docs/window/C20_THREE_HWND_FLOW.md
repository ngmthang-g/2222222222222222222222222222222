# C20 — Three-HWND combined flow

Original runtime evidence:
3 qualifying game HWNDs
→ per-HWND identity/cache
→ RoleName + HP
→ master candidates
→ selected master = TổngTài.S6

Embedded preview:
3 source HWNDs
→ independent HWND-backed preview order
→ 2-column preview layout
→ 75C.S6 | TổngTài.S6
→ ThápCa on second row

Physical game layout:
3-column × 4-row grid setting
→ master logical index 0
→ two follower HWNDs
→ layout maintenance

Input synchronization:
master events
→ two follower targets
→ size-aware client-coordinate mapping

Lifecycle:
preview reorder → does not change master
refresh → preserves surviving preview order
game close → HWND leaves discovery → stale preview/master state is rebuilt

Runtime parity deferred for exact physical geometry/timing and remaining explicit unknowns.
