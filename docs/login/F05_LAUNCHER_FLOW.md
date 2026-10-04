# F05 — Launcher flow

Generic Open Game:

_open_game
→ runtime permission guard login_tab
→ check_account_limit(login, extra=1)
→ require game_dir
→ _get_exe_path
→ start daemon _launch_worker

_launch_worker
→ build _make_safe_env(TLM_PROFILE)
→ overlay _apply_proxy_hook_env
→ spawn_and_inject(exe_path, cwd, env, timeout_ms=15000)
→ collect success/failure
→ log per-profile failure/exception
→ log successful launch count

Profile-specific launch:

_open_profile(profile_idx)
→ require usable game path
→ show blue busy text "⏳ Mở game profile N"
→ _launch_profile_worker
→ spawn one instance via suspend+inject
→ success: "✅ Đã mở game profile N"
→ inject failure/general error: red error state

Shared spawn_and_inject:

Popen(exe, CREATE_SUSPENDED, cwd, env)
→ target process exists but game code has not run
→ inject ./data/resources.dat
   OpenProcess
   → VirtualAllocEx
   → WriteProcessMemory(dll_path)
   → CreateRemoteThread(LoadLibraryW)
   → WaitForSingleObject
→ NtResumeProcess
→ return (success, pid, error_msg)

Safe environment:

Windows-essential variables
+ TLM_PROFILE
→ excludes Python/VirtualEnv leakage

Login proxy overlay:
minimal env
→ TLM_PROXY_ENABLE/HOST/PORT/FAIL overlay when applicable
→ exact enable encoding belongs to F08

HWND handoff:

spawn result PID
→ find_main_window_by_pid
→ EnumWindows
→ keep windows owned by PID
→ prefer UnityWndClass
→ prefer title containing "Thần Long"
→ fallback first visible PID-owned top-level window

Account multi-launch foundation:

acquire _launch_lock
→ launch one account/profile
→ wait up to 25s for PID-bound HWND
→ wait for window stabilization
→ return hwnd
→ only then launch next game window

After windows are ready:
→ account click/login can run in parallel
→ F06 owns that part

Forwarder-enabled launch:
→ required forwarder port must be listening
→ otherwise do not launch into dead network path

Window normalization:
_login_resize_monitor
→ every second inspect visible game windows
→ if size != 1366x768
   → resize_window
→ if already correct
   → no SetWindowPos churn

Explicit unknowns:
- exact generic _launch_worker profile-index selection/iteration
- exact cwd derivation
- exact post-HWND stability duration
- exact per-failure cleanup branch order
- exact UnityCrashHandler64 taskkill timing
