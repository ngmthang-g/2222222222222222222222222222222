# J13 — Failure / recovery flow

## Top-level classification

```text
request
  ├─ pre-run invalid/denied
  │    → no run created
  │
  ├─ per-account setup failure
  │    → drop failed account
  │    → ready subset continues
  │    → if ready empty: stop group
  │
  ├─ hard dungeon/party failure
  │    → _abort_cycle / group cancel
  │    → barrier peers released
  │    → this group winds down
  │    → other groups continue
  │
  └─ fail-soft maintenance/activity error
       → log
       → no independent group cancel
```

## Party stage

```text
B0 AutoAccept write/readback issue → warning / continue
B1 leave timeout                  → warning / continue
member RoleID unresolved          → skip member
zero RoleID targets               → stop group
B2 create retries exhausted       → stop group
B3 still-missing after resend     → continue best-effort
```

## Setup stage

```text
targets
  ↓ parallel _acc_setup
results[name] = ok
  ↓
ready subset
  ├─ non-empty → schedule uses ready accounts
  └─ empty     → "không acc nào online" → group ends
```

## Hard dungeon shell

```text
config
  5 × 2s
  exhausted → abort group

move
  3 total attempts
  exhausted → abort group

barrier
  no normal timeout
  failure/stop aborts barrier
  → peers exit

start FuBen
  5 × 0.3s
  exhausted outside target map
  → abort group

cycle watcher
  False
  → "chờ cycle map FAIL"
  → abort group
```

## 480s watcher

```text
deadline
done
480
"theo dõi map timeout (...) — hoàn thành ..."
```

Exact timeout return expression remains unresolved.

## Hook correction

```text
_call_hook frozen doc:
  missing/error → pass
  False → abort

same exact helper branch strings:
  "trả False → dừng chu trình"
  _abort_cycle
  "lỗi:"
  "→ abort"
```

Therefore:

```text
explicit False → abort current group
hook exception → STATIC CONFLICT / UNKNOWN
```

Do not preserve the old unconditional “exception pass” claim.

## Worker-shell correction

```text
_acc_step_worker
   ├─ _do_dungeon(...)
   ├─ _do_train(...)
   └─ exception → "worker lỗi:"
```

No own `_abort_cycle` reference and no schedule-worker result aggregation are recovered.

So:

```text
dungeon explicit hard failure
  → dungeon method already aborts group

generic worker exception only
  → log / worker returns
  → no independent group-abort wiring

Train returns failure
  → return value ignored by worker shell
  → row batch can still join
  → normal Xong path can be reached
```

## Final discard

```text
final discard
  ├─ success → "xong vứt lượt cuối"
  └─ error   → "vứt lượt cuối lỗi:"
                     ↓
                 HOÀN THÀNH
```

Fail-open.

## Background workers

```text
Follow error   ┐
Discard error  ├─ feature-local log/retry/lifecycle
Pickup error   │  NO schedule _abort_cycle linkage
Buff error     ┘
```

## Recovery

```text
hard group abort
   ↓
identity-safe finish
   ↓
idle/startable
   ↓
manual Start
   ↓
reset group progress
fresh cancel/job identity
re-run setup/config
re-arm persisted modes
```

No automatic whole-group restart recovered.
