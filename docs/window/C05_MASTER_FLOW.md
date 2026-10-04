# C05 — Master HWND flow

## Runtime model

```text
discovered game windows
↓
_update_master_combobox
├─ windows
├─ _master_hwnd_cache
├─ character-info cache
├─ build dynamic Radiobutton labels
└─ _hwnd_by_name[label] = hwnd
↓
_master_var
↓
_on_master_change
↓
hwnd_master
```

## Manual change

```text
user selects another radio
↓
_master_var label
↓
_hwnd = _hwnd_by_name[label]
↓
if mouse/keyboard sync active:
  stop sync
  unlock slaves
↓
new master becomes runtime source
↓
user re-enables input sync
```

## Layout role

```text
master HWND
↓
index 0
├─ stack/offset commands: first position
├─ grid: top-left
└─ auto tile: first before other name-sorted windows
```

## Input role

```text
master mouse/keyboard events
↓
_on_master_click / scroll / move / key
↓
client-coordinate transform where needed
↓
slave HWND targets
```

## Lifecycle

- Master list rebuilds only when current HWND set changes.
- Closed/reused HWND disappears/changes through C01/C02 discovery-generation handling.
- Stale blocked slaves have a watchdog unlock path for master close/change/exit.
- Master is not persisted as an HWND in the recovered Start settings block.

## Explicit unknowns
- exact automatic master-choice rule in `_auto_master_and_sync`;
- exact stale-master UI fallback after selected master disappears;
- exact full master-radio label formatting.
