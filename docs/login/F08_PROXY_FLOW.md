# F08 — Proxy / forwarder flow

## Free-pool refresh
Login Tool mode checks proxy_working.txt age.
- age <= 5 minutes: keep current pool
- age > 5 minutes: run proxy_refresh

proxy_refresh:
- prevents overlapping refresh runs
- can skip a very recent refresh (<60s unless forced)
- downloads embedded proxy lists
- deduplicates entries
- checks candidates in parallel
- keeps live entries
- sorts live entries fastest-first
- writes proxy_working.txt and proxy_last_refresh.txt

After a real refresh Login resets rotation state:
- forwarder_idx*.txt -> 0
- stale forwarder_advance*.txt removed
- old proxy_alloc.txt claims cleared

## Account rotation
last_login_times.json provides previous successful-login timestamps.

Runtime threshold is 300 seconds / 5 minutes.
- older than threshold: advance
- within threshold: keep current proxy

A stale original doc says 30 minutes; runtime constant and call-site logs both support 5 minutes.

Advance handshake:
forwarder_advance[_IID].txt signal
-> forwarder changes index
-> Login polls forwarder_idx[_IID].txt
-> success only after index change is observed.

## Instance mapping
profile_idx N -> port 22200 + N; iid=str(N).
Port 22200 is reserved for the default instance.
Multi-account instances use IID-suffixed mode/index/stats/pid/advance/pinned files.

## Mode routing
Không -> direct.
Tool -> free/ordinary proxy pool; private pin cleared.
Proxy -> row-specific private proxy; missing private value rejects/skips the account.

Private pin states:
- literal direct -> direct connections
- missing pin -> round-robin free pool
- valid private proxy -> pinned-only route
- private pinned failure does not fall back to the free pool.

## Shared free-pool coordination
proxy_alloc.lock serializes proxy_alloc.txt updates across forwarder instances.
Each proxy claim is associated with iid + timestamp.
Selection avoids other active claims and entries in proxy_bad.txt.

## Target routing
Only configured game-server targets are proxied.
Original diagnostics explicitly identify 103.147.34.81 ports 3001/4001 as proxied game traffic.
CDN/SDK traffic on 443 must remain direct.

## Row reload
User row reload:
1. advance that row's forwarder once
2. confirm the index changed
3. close that row's tracked game session
4. immediately login the same account with the new proxy
5. do not advance again during that immediate relogin

## Lifecycle
A healthy listening forwarder is reused.
A stale/non-listening instance is replaced before launch.
Game launch waits until the required loopback forwarder is ready.
forwarder_stats[_IID].json is read asynchronously for UI state.

## Explicit unknowns
- numeric ALLOC_TTL
- numeric BAD_COOLDOWN / PROXY_COOLDOWN_SECS
- numeric forwarder ROTATE_INTERVAL
- exact lower-level worker-count and socket-timeout mappings not directly bound
