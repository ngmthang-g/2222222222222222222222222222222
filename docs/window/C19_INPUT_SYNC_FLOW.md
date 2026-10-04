# C19 — Input synchronization flow

Master input source
→ mouse and keyboard listeners

Mouse click:
screen point
→ convert to master client coordinates
→ scale to each slave client size
→ process click in ordered sequence
→ release slave state

Keepalive:
input synchronization rechecks slave state every 1.5 seconds.

Watchdog:
stale slave state older than about 10 seconds is released when a matching release can no longer arrive.

Scroll and mouse movement have dedicated synchronized paths; movement is throttled.

Keyboard press/release uses a dedicated key-synchronization path.

Changing the selected master while input synchronization is active disables input sync and releases slave state.

Explicit unknowns:
- exact low-level key payload;
- exact mouse-move throttle interval;
- exact listener startup timing;
- exact retry delay.
