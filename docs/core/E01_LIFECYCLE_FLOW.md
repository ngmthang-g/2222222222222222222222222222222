# E01 — Main application lifecycle flow

Normal GUI branch:

process entry
→ optional diagnostic logger setup
→ faulthandler crash log
→ custom threading exception hook
→ single-instance mutex `TLMTool_SingleInstance`
→ Tk root
→ TLMMainApp
→ root/notebook/tab-frame setup
→ create potential tabs
→ create/start CPU monitor
→ construct Info tab
→ Info startup server call
→ plan/license/permission application
→ start heartbeat
→ selected-tab refresh lifecycle
→ splash/root visibility contract
→ Tk mainloop

Special branch:

process entry
→ `--forwarder`
→ forwarder main(initial_mode)
→ no normal TLM notebook lifecycle

Normal destruction:

Tk root/widget destruction
→ per-tab `<Destroy>` / stop / save handlers
→ Info stops heartbeat
→ interpreter exits when remaining worker ownership allows it

Forced heartbeat shutdown:

blocked plan/version/account state
→ repeated heartbeat failure/blocked strike
→ delay
→ destroy GUI
→ `os._exit`
→ forwarder child intentionally not killed by this path

Explicit unknowns:
- exact instruction order among root creation, TLMMainApp construction, show_splash and close_splash;
- exact normal user-close cleanup ordering across all tabs;
- exact duplicate-instance GetLastError comparison/message;
- final root geometry/style belongs to E02.
