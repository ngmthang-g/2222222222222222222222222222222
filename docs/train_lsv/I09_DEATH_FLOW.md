# I09 — Train LSV death/recovery flow

## Config

respawn_var
→ [TrainLSV] respawn
→ clean default False
→ label: Quay lại train khi chết

trist_var
→ independent treatment option
→ treatment primitive frozen in I07.

## Farm-session startup

_farm_cycle
→ create internal respawn_event
→ start _diaphu_monitor from the beginning of Farm
→ monitor is active during movement/heal/train
→ normal train loop continues independently.

## _diaphu_monitor

inputs:
→ hwnd
→ respawn_event
→ stop_event

locals include:
→ detected
→ hp_latched
→ get_character_info
→ click_at
→ wait_pixel.

cadence:
→ 4 seconds.

### HP path

read real HpPercent

HP unreadable:
→ not equivalent to numeric zero

numeric HP == 0
AND current zero episode not already latched:
→ state Về Lạc Dương LSV
→ click (792,441) exactly once
→ increment row _extra_deaths
→ latch zero episode.

persistent HP0:
→ no repeated click spam
→ no repeated death counter every tick.

exact latch reset statement:
→ UNKNOWN.

### Map recovery path

MapID == 10000
AND continuous hub episode not already detected:
→ log recovery detection
→ set/hold respawn_event
→ wait shared common.active
→ success log common.active sau hồi sinh OK.

dedicated detected latch prevents every 4s sample from becoming a new recovery.

monitor block contains event clear surface.

exact detected reset / event-clear statement ordering:
→ UNKNOWN.

common.active:
→ (1330,33)
→ RGB (34,8,11)
→ tolerance 5

death-monitor-specific wait timeout/interval/debug:
→ UNKNOWN.

## Farm-cycle recovery

normal state:
→ Đang train LSV

respawn/map10000 recovery observed:
→ log đang ở map 10000 → xử lý hồi sinh
→ leave normal train work

optional treatment:
→ reuse I07 _heal_at_death
→ fixed hub 10000 treatment point
→ only when treatment enabled and HP gate requires it

auto return enabled:
→ selected saved Train LSV preset
→ I02 ensure/premove
→ I03 final direct saved-coordinate move
→ normal train resumes

auto return disabled:
→ exact Farm-worker continuation UNKNOWN.

## State/counter

recovery state:
→ Về Lạc Dương LSV
→ #1565c0

not present in TrainLsvTab:
→ Đang hồi sinh
→ Về địa phủ

new row:
→ Chết: 0

HP0 branch:
→ row _extra_deaths
→ one count per latched HP-zero episode

reset across Farm restart:
→ UNKNOWN.

## Stop / reconnect

monitor stop:
→ stop_event
→ does not depend on respawn_event

confirmed I08 disconnect:
→ halt
→ reconnect path takes over after halt assertion

same scheduling window before halt:
→ ordering UNKNOWN.

## Runtime

packaged automove_log:
→ no correlated HP-monitor/respawn/death trace

classification:
→ STATIC_VERIFIED / RUNTIME_ENV_REQUIRED.

## Next

I10:
→ saved-coordinate management and per-account coordinate persistence.
