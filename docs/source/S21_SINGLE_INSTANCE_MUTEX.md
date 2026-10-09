# S21 source contract — exact original mutex name, bounded Win32 implementation

Original E01 source fingerprints: `CreateMutexW`, `GetLastError`, named `TLMTool_SingleInstance`. Source does **not** prove exact numeric comparison or exact user dialogue. This implementation uses standard Windows ERROR_ALREADY_EXISTS=183 only as a documented, local native call interpretation.

```text
production run_with_info_factory(info_factory)
    -> SingleInstanceMutex("TLMTool_SingleInstance").__enter__()
       -> CreateMutexW(..., bInitialOwner=FALSE, name)
       -> captured GetLastError
       -> 183 duplicate: CloseHandle(our new handle); reject BEFORE Tk()
       -> other Win32 failure: fail closed
       -> acquired: keep kernel handle open
    -> Tk root + TLMMainApp genuine Info factory
    -> mainloop
    -> shutdown + Destroy
    -> CloseHandle(single-instance handle) even on exception

main() in reconstructed project:
    NO real Info auth/server yet -> return 2 BLOCKED; does not open GUI.
```

Native Windows smoke uses ONLY independent `S21_TEST_ONLY_<uuid>` names: first child acquires; a second child sees duplicate; first exits gracefully; third acquires; separate forced-termination holder also releases kernel registration. The native test **never** acquires production `TLMTool_SingleInstance` and does not kill game/client processes.

Actual [Windows S21 run 37892342942](https://github.com/ngmthang-g/2222222222222222222222222222222222222222222/actions/runs/37892342942): **267/267 unit PASS**, `PASS_NATIVE_S21_TWO_PROCESS_MUTEX_COLLISION_AND_CLEANUP`, S20 native 3-HWND rerun PASS. Stage S same-commit run 37892342899 SUCCESS.

Original error-message wording and original duplicate comparison integer UNKNOWN; signed Info service, real TLMTool EXE, game runtime NOT IMPLEMENTED / NOT RUN.
