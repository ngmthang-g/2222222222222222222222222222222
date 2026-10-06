# J14 — Windows runtime harness requirements

## Host

- Windows 10/11 x64.
- Administrator/equivalent permissions if required by the original injector.
- Real desktop session, not headless service session.
- Disable sleep during long watchdog/stress tests.

## Software

- Exact original TLMTool 2.1.2 frozen specimen.
- Matching supported Thần Long PC client.
- Original helper DLL/PYD/data files preserved.
- A process/HWND inspector.
- Screen/video capture.
- Timestamp-capable log collector.
- Optional debugger/native tracer for two unresolved conflicts.

## Accounts

Minimum:
- 3 accounts.

Preferred:
- 6 accounts.

Need enough accounts for:
- one three-account group with one intentional setup failure;
- two simultaneous groups;
- leader/follower scope checks;
- one-group failure while another continues.

## Evidence directory layout

```text
J14_runtime/
  environment/
  case_J14_01/
    config_before/
    screenshots/
    video/
    logs/
    observations.md
    result.json
  case_J14_02/
  ...
```

## Required case metadata

Each case must record:

```json
{
  "case_id": "J14-XX",
  "original_exe_sha256": "15c804...",
  "windows_version": "...",
  "game_version": "...",
  "account_count": 0,
  "groups": [],
  "checkbox_modes": {},
  "started_at": "...",
  "ended_at": "...",
  "expected": "...",
  "observed": "...",
  "result": "PASS|FAIL|BLOCKED|UNVERIFIED",
  "evidence": []
}
```

## Fault injection rules

Prefer black-box failures that do not modify the original executable:
- close one game client;
- deny/interrupt one setup target;
- make one character unavailable/offline;
- intentionally provide a Train target missing from farm_tab;
- create controlled map/start conditions.

For native-only conflicts:
- debugger tracing is allowed;
- do not overwrite the frozen original file;
- if any temporary in-memory modification is used, record it and do not treat modified behavior alone as proof.

## Timing capture

Use one synchronized host clock and capture:
- TLM log timestamp;
- video timestamp;
- test operator action timestamp.

This is required for:
- Start→Stop→Start races;
- barrier release delay;
- 0.3s/2s retry observations;
- 480s watchdog;
- group teardown timing.

## Runtime acceptance

A case passes only when its expected behavior is observable and backed by evidence.

No-run = UNVERIFIED.

No evidence bundle = UNVERIFIED.

A crash that prevents observation = FAIL/BLOCKED, not PASS.
