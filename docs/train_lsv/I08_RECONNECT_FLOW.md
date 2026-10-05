# I08 reconnect flow

auto_reconnect default False.

_disconnect_monitor runs every 2 seconds.

Detection:
- read TCPGame connected tri-state;
- memory True resets strikes;
- memory None lets pixels decide;
- both login.ngatKetNoi1 and login.ngatKetNoi2 must match for 3 consecutive ticks.

Frozen pixels:
- ngatKetNoi1: (640,244), RGB (160,145,52), timeout 5, tolerance 5.
- ngatKetNoi2: (702,453), RGB (212,28,34), timeout 5, tolerance 5.

On confirmed disconnect:
- signal halt;
- use stop_character;
- enter reconnect recovery.

Reconnect batch:
- 5 attempts;
- re-check dialog before each click;
- click (616,455) only while dialog remains;
- wait up to 30 seconds for common.active.
- common.active = (1330,33), RGB (34,8,11), tolerance 5.

On success:
- invalidate character Reader cache for current PID;
- set reconnect_ok;
- Farm cycle resets.

If 5 attempts fail:
- remain Chờ kết nối lại;
- wait 30 seconds;
- retry another batch indefinitely while the session/window remains valid.

Farm-cycle wait:
- reconnect_ok.wait(timeout=5).

Post-success memory gate:
- wait_memory_ready(timeout=45.0, need=3);
- inherited shared interval = 1.0 second;
- valid samples require clear RoleName and MapID != None;
- timeout is fail-open.

Not proven:
- unconditional post-reconnect _ensure_injected;
- exact wait_pixel interval/debug values;
- exact source placement of auto_reconnect gate.

Runtime packaged log has no correlated reconnect trace.

Next: I09 death handling.
