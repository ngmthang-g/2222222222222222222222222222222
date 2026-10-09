# S40 F09 schedule config — read-only, no game actions

```text
%APPDATA%/TLMTool/settings.ini
    │
    ├─ E05 read_settings [Settings]
    │       schedule_close + schedule_open  → strict verified HH:MM
    │       schedule_on                    → raw string / UNKNOWN encoding
    │       shutdown_after_close           → raw string / UNKNOWN encoding
    │       accounts                        → UNTOUCHED/NOT READ
    │
    ├─ no settings file                    → DEFAULTS_ONLY (04:00 / 04:20)
    ├─ valid text                          → READ_ONLY_VALIDATED
    ├─ invalid time/control token          → BLOCKED_*
    └─ read/parse error                    → BLOCKED_SETTINGS_READ
                  │
           preview(now) only if valid
                  │
          S39 LoginScheduleClock.enable(now) for PURE math
                  │
          next_close + next_open + countdown string
                  │
               NO side effect
               NO background worker
               NO Tk controls that pretend to open games
               NO native game launch/close/OS shutdown
               NO account write or captcha/proxy manipulation

F05/F06 product launch/login handlers and true Info signed gate are absent.
Original stored bool encodings remain UNKNOWN. Next S41.
```
