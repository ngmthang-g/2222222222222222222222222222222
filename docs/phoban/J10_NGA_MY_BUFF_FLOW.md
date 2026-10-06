# J10 — Nga My buff flow

## UI/config

```text
Nga My buff (Sát Tinh)
        ↓
nga_my_buff_var
        ↓
phoban_nga_my_buff
clean default = OFF
```

Worker state:

```text
_buff_stop
_buff_thread
_buff_gen
```

## Toggle lifecycle

```text
_toggle_buff
    ↓
tick ON?
  ├─ yes + any group running
  │    → _start_buff
  │    → is_alive guard
  │    → current generation session
  │    → _buff_worker(gen)
  │
  ├─ yes + idle
  │    → mode remains armed
  │    → run start will create worker
  │
  └─ no
       → stop worker
       → worker final "untick" sweep
       → OFF known Nga My
```

## Nga My detection

```text
character info
   ↓
FactionID == 4?
  ├─ yes → Nga My
  └─ fallback FactionName == "Nga My"
```

## Desired state

Every poll, for each account in a currently-running group:

```text
is_nga_my(ci) AND in_dungeon_map?
     │
     ├─ yes → want_on = True
     │
     └─ no  → want_on = False
```

Despite the UI suffix “(Sát Tinh)”, the exact worker doc says `trong map phó bản`, not `MapID == 111`.

## Exact auto fields

ON:

```text
AUTOTRAIN.IsAttackMonsterInList = True
AUTOTRAIN.AttackMonsterList = "910"
```

OFF:

```text
AUTOTRAIN.IsAttackMonsterInList = False
AUTOTRAIN.AttackMonsterList = ""
```

`PB_BUFF_MONSTER_LIST = "910"`.

## Readback/repair

```text
_buff_ensure(hwnd, name, want_on)
      ↓
want_list = "910" if ON else ""
      ↓
read auto settings
      ↓
cur_on / cur_list already desired?
  ├─ yes → success, no write
  └─ no
       → write desired AUTOTRAIN pair
       → read back
       → retry up to PB_BUFF_RETRY
       → failed attempt waits 1s
```

Numeric `PB_BUFF_RETRY` is not statically bound.

## Worker loop

```text
_buff_worker(gen)
      ↓
every PB_BUFF_POLL seconds
      ↓
checkbox still ON?
  ├─ no
  │    → _sweep_off()
  │    → exit
  │
  └─ yes
       ↓
any running group?
  ├─ no → exit
  └─ yes
       ↓
members of currently-running groups
       ↓
resolve live HWND / get_character_info
       ↓
FactionID / FactionName / MapID
       ↓
want_on = Nga My AND in dungeon map
       ↓
_buff_ensure(...)
```

## Final untick sweep

```text
known Nga My roster
      ↓
_sweep_off()
      ↓
_buff_ensure(..., want_on=False)
      ↓
IsAttackMonsterInList=False
AttackMonsterList=""
      ↓
"[Phó bản] Buff quét cuối untick N acc Nga My"
```

This sweep is explicitly tied to untick.

No separate unconditional run-end sweep while the tick remains ON is independently recovered.

## Runtime unknowns

- PB_BUFF_POLL numeric;
- PB_BUFF_RETRY numeric;
- exact dungeon-map set construction;
- exact known-roster container type;
- generation mutation/teardown micro-order;
- no-running-group cleanup microbehavior;
- live Windows/game parity.
