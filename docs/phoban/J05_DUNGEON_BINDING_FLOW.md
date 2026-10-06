# J05 — Phó Bản dungeon binding flow

## Visible selection

```text
PHOBAN_MAP_LIST (8 visible names)
  1 Tô Châu  - Thủy Lao
  2 Tô Châu 1 - Tống Liêu
  3 Tô Châu 2 - Trúc Lâm
  4 Tô Châu 3 - Dã Ngoại
  5 Lâu Lan 1 - Hoàng Kim
  6 Lâu Lan 2 - Huyền Phật Châu
  7 Lâu Lan 3 - Dung Nham
  8 Sát Tinh - Thử nghiệm
```

`Sát Tinh` exists as an alias in binding tables/handler registry but is not a ninth visible dropdown item.

## Canonical key fan-out

```text
J04 schedule row.name
        │
        ├───────────────> DUNGEON_FUBEN_CODE[name]
        │                    ↓
        │              FUBEN.SelectedFuBen
        │
        ├───────────────> DUNGEON_MAP_IDS[name]
        │                    ↓
        │                dungeon MapID
        │
        ├───────────────> DUNGEON_CLICK_POS[name]
        │                    ↓
        │              pre-dungeon click point
        │
        └───────────────> get_dungeon_handler(name)
                             ↓
                    DUNGEON_HANDLERS
                         │       │
                         │       └─ unregistered → BaseDungeon
                         │
                         ├─ Sát Tinh - Thử nghiệm
                         └─ Sát Tinh
                                  ↓
                            SatTinhDungeon
```

## Exact binding table

| Name | FuBen code | MapID | Click |
|---|---|---:|---:|
| Tô Châu  - Thủy Lao | ThuyLao | 92 | 540,246 |
| Tô Châu 1 - Tống Liêu | Q1_ToChau | 93 | 515,273 |
| Tô Châu 2 - Trúc Lâm | Q2_ToChau | 94 | 498,301 |
| Tô Châu 3 - Dã Ngoại | Q3_ToChau | 95 | 493,328 |
| Lâu Lan 1 - Hoàng Kim | Q1_LauLan | 108 | 502,296 |
| Lâu Lan 2 - Huyền Phật Châu | Q2_LauLan | 109 | 488,323 |
| Lâu Lan 3 - Dung Nham | Q3_LauLan | 110 | 498,350 |
| Sát Tinh - Thử nghiệm | SatTinh | 111 | 0,0 |
| Sát Tinh | SatTinh | 111 | 0,0 |

## Handler chain

```text
_do_dungeon(dungeon=name)
        ↓
handler = get_dungeon_handler(name)
ctx = DungeonCtx(...)
        ↓
pre_config(ctx)
        ↓
common _config_dungeon_memory
  SelectedFuBen = DUNGEON_FUBEN_CODE[name]
        ↓
post_config(ctx)
        ↓
pre_move(ctx)
        ↓
common movement/barrier
        ↓
post_move(ctx)
        ↓
pre_start_fuben(ctx)
        ↓
common start_auto_fuben stage
        ↓
post_start_fuben(ctx)
        ↓
common dungeon cycle wait
        ↓
post_cycle(ctx)
```

## Handler module

```text
BaseDungeon
  pre_config
  post_config
  pre_move
  post_move
  pre_start_fuben
  post_start_fuben
  on_entered
  post_cycle

SatTinhDungeon(BaseDungeon)
  custom hooks:
    on_entered
    post_cycle
  helpers/session:
    _stop_session
    _run
    _halted
    _loop_revive
    _move_to_center
    _train_once
```

Only `SatTinhDungeon` is a current custom `*Dungeon` implementation in the exact module.

## Deferred

J05 deliberately does not expand:
- J06: exact `times` iteration / run count;
- J07: deep status/cancel/abort/barrier failure state machine;
- later item-drop/loot/Nga My/start-stop/failure-recovery behavior.
