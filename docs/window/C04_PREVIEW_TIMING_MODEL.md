# C04 — Preview timing model

## Do not confuse maintenance cadence with DWM FPS

The image itself is a live DWM Thumbnail. TLM's timers maintain layout/list/metadata; they are not a screenshot frame rate.

```text
DWM compositor
└─ live source HWND thumbnail
   └─ no TLM-defined FPS constant recovered

background worker
├─ EnumWindows + character info ~3 s
└─ heavier memory read ~8 s

Start UI list poll
└─ 2000 ms
   └─ stops when leaving Start tab

embedded preview maintenance
├─ _preview_proc_count
├─ threshold constant 6
├─ 800 ms low-count branch
├─ 2000 ms high-count branch
├─ reposition
├─ compare alive HWNDs / valid preview items
├─ conditional rebuild via need_refresh
├─ refresh cached RoleName/HP
├─ update slot combobox mapping
└─ schedule next cycle while _refresh_active

Configure/resize
└─ debounce 60 ms
   └─ reposition destination DWM HWNDs

detached preview
└─ _detached_update_loop
   ├─ independent of Start tab visibility
   └─ rebuild if game-window list changes
```

## Explicit unknowns
- exact comparison operator at account-count threshold 6;
- exact Boolean expression producing `need_refresh`;
- exact source use/comparison of the 3.0-second `cache_ts` constant;
- exact detached-loop timer interval;
- Windows DWM compositor FPS.
