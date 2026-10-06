# J14 — Runtime environment report

## Result

**LIVE_WINDOWS_TLM_RUNTIME_AVAILABLE = NO**

## Capability check

Observed from the execution container:

```text
kernel: Linux 6.18.44 x86_64
platform.system(): Linux
os.name: posix
wine: not installed / not found
TLMTool/Thần Long/Wine/LDPlayer Windows processes: none
DISPLAY: :0
exact TLM archive mounted: yes
```

The presence of an X display does not convert this into a Windows game environment.

## Original specimen availability

```text
/mnt/data/TLMTool_2.1.2(6).zip
size: 93,715,901 bytes
SHA-256:
c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd
```

Inner original executable contract:

```text
TLMTool_2.1.2/TLMTool.dist/TLMTool.exe
size: 47,450,112 bytes
SHA-256:
15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22
```

## Why runtime parity cannot be claimed

The Phó Bản runtime depends on real Windows/game facilities including:
- Windows HWNDs;
- game process memory;
- DLL injection/helper plumbing;
- game UI pixels/state;
- internal game auto settings;
- live MapID/position values;
- multiple simultaneous client processes.

None is available in the current execution environment.

## Decision

Do not attempt to substitute:
- Linux process mocks;
- synthetic HWND objects;
- Wine without the real game;
- mocked memory structs

as proof of original TLM runtime behavior.

Such tests can later validate rebuilt code structure, but they cannot close original-runtime parity.

## Classification

`J14 = ENVIRONMENT_BLOCKED_FOR_LIVE_RUNTIME`

`GATE_J = STATIC_RESEARCH_CLOSED / LIVE_RUNTIME_PARITY_DEFERRED`
