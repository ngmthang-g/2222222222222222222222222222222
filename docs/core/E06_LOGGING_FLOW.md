# E06 — Logging flow

Main startup:

debug_logger.setup()
→ resolve frozen executable/log directory
→ ensure log/ exists
→ open/append log/tlmtool.log
→ trim oldest central-log content if MAX_SIZE exceeded
→ write session Start marker + executable/runtime info
→ replace sys.stdout/sys.stderr with tee wrappers
→ return log_path

Worker/main diagnostics:

feature print/log text
→ process stdout/stderr
→ tee to original console/stream
→ tee to tlmtool.log

Unhandled worker exception:

threading.excepthook
→ [THREAD-EXC] marker
→ thread/exception metadata
→ traceback.print_exception
→ central log path

Native/fatal diagnostic:

crash_fault.log file handle
→ faulthandler.enable(file=...)
→ separate crash diagnostics

Normal exit:

atexit _on_exit
→ write End marker
→ flush/restore original stdout/stderr tee state

Specialized memory log:

memory_reader/items diagnostic
→ timestamp YYYY-MM-DD HH:MM:SS
→ tlm_memory.log
→ truncate/remove path when >1MB

Injected/automove diagnostic:

resources/automove path
→ data/automove_log.txt
→ Tối ưu watchdog tracks file size/position
→ parse [pid=N] Perf: ping
→ missing ping contributes to recovery decision

Boundaries:
- logs are not feature configuration state
- automove log is monitored by Python but can be written by injected/native payload
- no explicit central write lock/queue recovered
- exact MAX_SIZE/KEEP_SIZE values remain unknown
