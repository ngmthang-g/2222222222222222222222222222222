# S23 source contract — E06 stdout/stderr tee and session lifecycle

Original E06 exact evidence: `debug_logger.setup`, `_TeeWriter`, `log/tlmtool.log` (beside frozen executable), `sys._fl_tee_out/_err`, `atexit`, "=== Start ... ==="/"=== End ... ===", executable/Python info, 60-`=` delimiter, original stdout/stderr **plus** file, oldest lines trimmed only if numeric bounds reached. **Original MAX_SIZE, KEEP_SIZE, partial-line timestamp format and lock implementation UNKNOWN**.

```text
S21 Windows SingleInstanceMutex acquired
  -> S23 SessionTee enters, creates append-only log/tlmtool.log
       + tees BOTH original stdout and stderr to file and console
       + records start marker, exe, Python
       + atexit close/stream restoration if ordinary shutdown
  -> S22 StartupDiagnostics enters, crash_fault.log separate
  -> provided real InfoTab/Tk GUI (NOT AVAILABLE IN main())
  -> reverse cleanup: Tk-owned objects, S22 diagnostics,
     S23 restore stdout/stderr/end session/close file,
     S21 CloseHandle
Without authentic server: main() remains BLOCKED and returns 2.
```

Only a **LOCAL safe ordering** is reconstructed; original logger/diagnostic/mutex/splash instruction ordering unavailable. Source fallback writes in project checkout `log/` only when authorized GUI helper invoked; all tests inject isolated temporary log locations.

`trim_if_needed` is available **only when caller explicitly supplies** trustworthy numeric thresholds. Production defaults to no trimming rather than fabricate E06 constants. No log rotation filenames, server reports, unproven timestamp algorithm or native game input.

Windows S23 [run 37894932947](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37894932947) SUCCESS: 306/306 unit, test-created Windows child process stdout/stderr and worker thread mirrored to same growing 2-session file, exception/startup and invalid-log cleanup freed Win32 mutex, native S22/S21/S20 reruns PASS; Stage S source [37894932886](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37894932886) SUCCESS. Real signed Info, game and complete EXE not implemented.
