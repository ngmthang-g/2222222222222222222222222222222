# C03 — DWM preview flow

## Core architecture

```text
src_hwnd = game window
↓
Tk preview item
  ├─ title/header
  └─ black preview frame
↓
_is_hung(src_hwnd)
├─ true → error state "Cửa sổ không phản hồi"
└─ false
   ↓
   winfo_rootx/y/width/height
   ↓
   create top-level overlay HWND class ThlDwmThumbDst
   ↓
   destination HWND styles:
     WS_EX_LAYERED
     WS_EX_TOOLWINDOW
     WS_EX_NOACTIVATE
     WS_POPUP | WS_VISIBLE
   ↓
   click-target map: dst_hwnd → src_hwnd
   ↓
   DwmRegisterThumbnail(dst_hwnd, src_hwnd)
   ↓
   DwmUpdateThumbnailProperties
     RECTDESTINATION
     OPACITY (255)
     VISIBLE
     SOURCECLIENTAREAONLY
   ↓
   live preview
```

## Reposition

```text
Tk <Configure>
↓
_schedule_window_preview_reposition
↓
debounce
↓
_reposition_window_previews
↓
read current preview widget screen geometry
↓
SetWindowPos destination overlay
↓
destination remains aligned over preview frame
```

## Activation

```text
WM_LBUTTONDOWN / WM_LBUTTONUP / WM_LBUTTONDBLCLK
on ThlDwmThumbDst
↓
_dwm_dst_click_targets[dst_hwnd]
↓
source game HWND
↓
IsWindow
↓
_activate_game_window
↓
IsIconic
├─ minimized → ShowWindow(SW_RESTORE)
└─ otherwise → ShowWindow(SW_SHOW)
↓
SetForegroundWindow(source)
```

Tk preview/title widgets also bind <Button-1> to the same source activation closure.

## Teardown

```text
preview item removed/rebuilt
↓
DwmUnregisterThumbnail(thumb)
↓
remove dst_hwnd from click-target map
↓
DestroyWindow(dst_hwnd)
↓
destroy Tk frame
```
