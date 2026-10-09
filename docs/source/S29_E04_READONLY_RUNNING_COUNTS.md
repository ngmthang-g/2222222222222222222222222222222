# S29 — E04 running-count evidence is not an account-limit grant

```text
READ-ONLY independent Win32 sources:
  NativeWin32ProcessBackend
    -> CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS)
    -> Process32FirstW / Process32NextW
    -> image basename exactly "Thần Long  Mobile.exe" (two spaces)
    -> unique PIDs of observed game-named processes (including invisible)

  S08 existing NativeWin32Backend
    -> EnumWindows, HWND visible, actual PID/executable/class/title
    -> discover_game_windows -> visible game HWNDs (may be 2+ for 1 PID)

  RunningCountEvidence
    game_process_count: int | None     # process snapshot success dependent
    visible_hwnd_count: int | None      # window snapshot success dependent
    visible_game_pid_count: int | None  # distinct PIDs of visible game HWNDs
    emulator_process_count: None       # not verified/implemented
    combined_running_count: None       # never guessed
    is_authoritative_account_total: False
      |
      -> S26 check_open_game_preflight(...running_windows=None)
         = RUNNING_WINDOW_COUNT_UNKNOWN, fail closed

No game process creation; native tests use python.exe as python.exe.
```

**Evidence from original E04:** shared `permission_guard` account limit includes running game EXE + emulator process counts. Exact emulator image/counting rules not recovered. Windows Toolhelp image name alone is observational and may race process lifecycle; no signed Info service or authoritative account total was created.

[Windows S29 CI 409/409 PASS](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37907306562) · [Test-owned native evidence](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37907306562/artifacts/11604554741).
