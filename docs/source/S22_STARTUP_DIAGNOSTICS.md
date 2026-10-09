# S22 — E01 diagnostic logging and exception lifecycle

## Recoverable original fingerprints
- `debug_logger.setup`, `faulthandler.enable`, `crash_fault.log`, `threading.excepthook`, `traceback.print_exception`.
- The original log location, line formatting and exact startup ordering are not source-proven in E01. The separate E06 logging forensic is already written and must be consulted for the later stdout/stderr tee service. S22 does not invent it.

## New bounded implementation

```text
Production run_with_info_factory (real, still requiring missing auth)
   └─ S21 SingleInstanceMutex (native named kernel32)
       └─ S22 StartupDiagnostics context
           -> open local writable append crash_fault.log
              (LOCALAPPDATA/TLMTool is S22 POLICY, original UNKNOWN)
           -> if no global faulthandler active:
                faulthandler.enable(file=log, all_threads=True)
           -> install threading.excepthook (record then chain previous)
           -> create Tk and real TLMMainApp provided Info factory
              -> on startup exception, record traceback then propagate
           -> on exit, restore own hook + disable own faulthandler
              + close log
       └─ on any failure, release mutex handle
   main() without real Info: BLOCKED / exit code 2, never starts a GUI
```

A pre-existing faulthandler stays unchanged; only code-owned fault handler may be disabled on shutdown. A thread hook replaced later by other code is NOT overwritten on cleanup. If the crash log cannot be opened, the diagnostic context fails closed before GUI starts; mutex handle is released.

## Real Windows proof
[GitHub Actions S22 run 37893509454](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37893509454), Windows Python 3.10, **285/285** unit tests PASS and `PASS_NATIVE_S22_DIAGNOSTICS_THREAD_FAULT_MUTEX_RECOVERY`. Native test-owned process raises real worker thread exception and faulthandler dumps a genuine native/Python stack to a temp log; separately failed Info startup and failed writable log produce expected failure with safe mutex cleanup, each confirmed by subsequent other Windows process acquiring its own isolated TEST_ONLY mutex. Existing S21 and S20 native smoke reruns PASS on same implementation commit; Stage S source run 37893509490 SUCCESS.

**Explicit exclusions:** finished auth/server and real game, exact original crash file path, exact original logger format/size limits, original splash/forced os._exit, Proxy. S22 is diagnostic startup groundwork, not a finished game tool.
