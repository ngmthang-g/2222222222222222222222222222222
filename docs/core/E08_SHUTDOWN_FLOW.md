# E08 — Shutdown/reload flow

Normal user/Tk close:

root/widget destruction
→ child tab <Destroy> events
→ tab-owned _save_on_destroy / _on_destroy handlers
→ cancel/save/stop owner-specific state
→ normal interpreter shutdown when remaining worker state allows

No shell-level normal WM_DELETE_WINDOW handler was recovered.
Exact tab-destroy ordering is UNKNOWN.

Forced heartbeat exit:

heartbeat blocking state strike 1
→ wait for next heartbeat confirmation
→ second blocking strike
→ wait about 5 seconds
→ destroy app GUI
→ os._exit
→ independent forwarder remains running

In-app rebuild/refresh:

TLMMainApp._rebuild_tab
→ rebuild tab widget/content inside same process

refresh_window_preview_list
→ rebuild embedded DWM preview resources

_refresh_detached_preview
→ close then reopen detached DWM preview

Start Reload:

btn_reload / _unstick_all_cmd
→ _dll_unstick_windows / unstick_windows
→ recover tracked game-window/input-lock state
→ no TLM process restart

Login row Reload:

_reload_account
→ _reload_worker
→ advance that forwarder instance to next proxy
→ if tracked game HWND exists: close that game
→ login same account immediately with new proxy
→ UI done/error callback on Tk main thread

Full auto-update:

Info on_auto_update_click
→ confirm
→ close all tracked game windows
→ stop all forwarder processes
→ resolve update link
→ locate update.exe
→ Popen update.exe

external updater:
→ download package
→ tools/7z.exe extraction
→ replace TLMTool.dist
→ bootstrap.exe if updater self-replacement needed
→ relaunch TLMTool.exe

Important:
- forced heartbeat quit keeps forwarder alive
- auto-update stops forwarders
- normal user-close all-forwarder behavior is UNKNOWN
- preview/tab reload != account reload != process update/restart
