# S28 — Offline F05/D06 launch-input path

```text
future genuine Info verified rights + actual running counts (not available)
    -> existing S26 check_open_game_preflight (no fabricated grant)
    -> S28 prepare_launch_inputs(LaunchPreflight, caller-supplied package_root,
                                 explicit profile_index=1..5, audited environment keys)
        -> verify F04 exact "Thần Long  Mobile.exe" still file
        -> inspect PE DOS MZ + NT signature + AMD64 machine + PE32+ magic
           + executable image + non-DLL + section bounds
        -> inspect ONLY package_root/data/resources.dat as x64 PE DLL-format
           (no backup fallback; no load)
        -> build restricted env from CALLER-PROVIDED audited Windows essentials
           + TLM_PROFILE; no Python/VirtualEnv/Proxy environmental keys
        -> STRUCTURAL_INPUTS_ONLY_NOT_LAUNCHED (input validation only)

No original whitelist guessed
No cwd invented
No signed Info token, injection, CreateRemoteThread, game process, Proxy
```

F05 original documents `_make_safe_env(tlm_profile) → minimal Windows essentials + TLM_PROFILE`, but **exact key whitelist is not recovered**. `SystemRoot` guard and synthetic header checks are S28 local safety measures, not proofs of original source parity. D06 identifies `data/resources.dat` active x64 PE DLL payload and separates opaque fake-MZ data files.

Evidence: [S28 Windows success 390/390 tests](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37906555448), [artifact 11603899644](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37906555448/artifacts/11603899644).
