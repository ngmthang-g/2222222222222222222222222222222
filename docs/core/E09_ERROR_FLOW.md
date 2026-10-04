# E09 — Error handling flow

Process-level diagnostics:

fatal/native Python fault
→ faulthandler
→ crash_fault.log

unhandled worker exception
→ threading.excepthook
→ [THREAD-EXC] + traceback
→ central diagnostic log

Feature worker:

worker starts
→ operation
→ success: main-thread done callback
or
→ error: log error
→ main-thread error callback
→ restore button/busy state
→ optional user-facing messagebox

Configuration:

read/write/parse
→ catch local I/O/ValueError/TypeError/AttributeError paths
→ log [CONFIG]/Error...
→ return default/None or retain prior tab-owned state
→ do not terminate main Tk process

Server/heartbeat:

HTTP/RPC call
→ timeout/status/token/decode validation
→ record success or failure
→ schedule next heartbeat
→ permission_guard consumes current normalized state
→ repeated blocking state may escalate to forced app close

Permission-sensitive action:

UI state alone is not trusted
→ runtime permission_guard
→ has_permission/check_account_limit
→ allowed: execute
→ blocked/missing invalid server state: deny + notifier
→ special documented limit<=0 trial/unlimited semantics can allow

Game HWND message:

SendMessageTimeout / SMTO_ABORTIFHUNG
→ success: continue
→ transient Unity busy: short retry up to 2
→ still failed: skip that slave/current action
→ keep sync worker alive

Input stale state:

missing release/master closed/changed
→ watchdog sees stale block
→ idempotent unblock/restore

Emulator remote:

request
→ authenticate token
→ validate action/aid/fields/value format
→ structured {ok,error}
→ only dispatch valid action

Key boundary:
diagnostic logging != recovery policy.
Retry/skip/fallback/deny/notify are subsystem-owned.
