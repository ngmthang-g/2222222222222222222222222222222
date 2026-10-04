# F06 — Account login action flow

Selected checked row:

row checkbox
→ read username/password/captcha/proxy
→ validate non-empty username/password
→ produce (row_idx, tk, mk, captcha_mode, proxy)

Per-row action:

disable row Login button
→ orange "Đang login..."
→ start _single_login_worker

Worker:

retry loop bounded by MAX_LOGIN_RETRIES
→ _launch_one_window
→ get correct PID-owned HWND
→ _login_click_worker(hwnd, tk, mk, ...)
→ success?
   yes:
   → _mark_row_online
   → _record_login_time
   → finish
   no:
   → _force_close_window
   → prepare next retry state
   → retry if budget/cancel allows

Background login mechanics:

target HWND exists?
→ no: abort

check login.update with PrintWindow
→ if present:
   → click_at(630,457) on target HWND

wait until BOTH:
- login.login1
- login.login2
match through check_multipixel/PrintWindow
→ timeout after 100s

Step 1:
click_at(613,302) username

Step 2:
press_at(tk) using target-window WM_CHAR path

Step 3:
click_at(573,362) password

Step 4:
press_at(mk)

Step 5:
click_at(684,506) Login

Then:
poll login.vaoTroChoi
→ recovered ceiling 150 checks
→ if never appears: fail
→ if appears: click_at(684,450)

Step 8:
await_pixel(common.active, timeout=30, cancel_flag=...)
→ timeout: fail
→ active: login complete

At every stage:
window/cancel guard
→ stale/closed HWND aborts immediately

Successful completion:

_login_click_worker returns success
→ _mark_row_online(row_idx, hwnd, pid, user, proxy/runtime metadata)
→ row painted online/green
→ login_online.json updated
→ _record_login_time
→ last_login_times.json updated

Multi-account:

prepare selected accounts
→ launch windows sequentially under _launch_lock
→ after each HWND is ready, click/login work may run in parallel
→ Semaphore(MAX_PARALLEL_LOGIN) limits simultaneous login click workers
→ wait until all workers finish
→ aggregate success/total
→ _login_reset_ui

Input boundary:

click_at
→ background/window-relative DLL-sync click
→ physical cursor does not move

press_at
→ target-window WM_CHAR / Unity activation
→ physical keyboard focus not required from user

Deferred:
- captcha mode internals → F07
- proxy policy/rotation/pinning → F08
- post-login routing → F10

Explicit unknowns:
- numeric MAX_LOGIN_RETRIES
- numeric MAX_PARALLEL_LOGIN
- exact poll delay for vaoTroChoi
- exact click/typing delay and jitter values
