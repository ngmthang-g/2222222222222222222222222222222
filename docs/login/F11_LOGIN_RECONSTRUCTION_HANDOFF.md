# F11 — Login reconstruction handoff

This is the compact implementation handoff for the later Stage-S source reconstruction. It does not authorize starting Stage S early.

## Locked UI
Use F01/B03/B14 directly. The current screenshot is byte-identical to the locked Login baseline.

Canonical after-login text/value map:
- Chờ = wait
- Party = party
- Train = train
- Train LSV = train_lsv
- Dồn vàng = don

Do not use “Đồn vàng”.

## Locked data path
Account rows:
- 100 logical rows
- plan-limited visible rows preserve hidden data FIFO
- settings.ini / [Settings] / accounts
- newline record separator
- pipe field separator
- save order: check | user | pass | captcha | proxy
- 300ms debounced save

Password:
- star masking is presentation only
- underlying password remains the real string
- original persistence evidence is direct/plain rather than encrypted

## Locked launch path
1. require permission/account limit
2. resolve canonical `Thần Long  Mobile.exe`
3. run launcher work off Tk thread
4. build minimal safe environment
5. apply only compatibility needed for the original contract; proxy runtime development is out of scope
6. create game suspended
7. inject `./data/resources.dat` using LoadLibraryW remote-thread path
8. wait injection
9. resume process
10. bind main window by returned PID
11. serialize account window launches
12. normalize non-1366×768 windows only when needed

## Locked login path
For each selected valid account:
- launch sequentially
- once HWND is ready, login click worker may run in parallel under the original semaphore model
- PrintWindow readiness works while game is covered
- close update popup at (630,457)
- username: click (613,302), type username
- password: click (573,362), type password
- Login: click (684,506)
- poll Vào trò chơi up to 150 checks
- click Vào trò chơi at (684,450)
- await common.active up to 30s
- mark row online and record successful-login time
- on failed retry close the failed window before relaunch

Mouse input must remain background/window-targeted. Do not move the physical cursor.

## Locked scheduler path
Manual Bắt đầu and schedule checkbox remain independent.

Schedule:
- event worker check: 20s
- next occurrence today if future, otherwise tomorrow
- no immediate catch-up
- after trigger: +1 day
- countdown UI: about 1s on main Tk thread
- close event closes game windows
- optional 60s PC-shutdown confirmation
- open event reuses normal checked-account Login batch
- skip scheduled open if a Login batch is already active
- scheduler remains alive after success/failure.

## Locked post-login path

### Chờ
No action.

### Party
- use dedicated Party ref/state
- select Party tab
- wait for Party scan readiness
- skip if already running
- call real Party start/toggle path.

### Train / Train LSV / Dồn vàng
- resolve real tab ref
- select tab first
- `want` = required HWND set
- every 1.0s build `have` from target `_acc_rows.get("hwnd")`
- ready when `want.issubset(have)`
- maximum 20s / 20 polls
- final activation on main Tk thread
- if target already running: skip
- if ref missing: warn and skip
- call real `_toggle_farm`; do not create a Login-owned substitute engine.

## Do not guess these values
Keep explicit until runtime or stronger evidence exists:
- F02 check-token encoding
- legacy Có migration
- credential delimiter escaping
- F04 exact revalidation/write microsequence
- F05 generic profile selection/cwd/stabilization/failure-cleanup microorder
- F06 MAX_LOGIN_RETRIES
- F06 MAX_PARALLEL_LOGIN
- F06 exact Vào trò chơi poll delay and lower-level input jitter
- F09 fresh-process schedule worker autoresume solely from saved schedule_on
- F09 scheduled-close cleanup microorder
- Party dedicated readiness set's instruction-level expression
- mixed-success post-login route guard
- zero-success post-login route guard.

## Mandatory runtime parity matrix once reconstructed
Run on Windows against original and reconstructed builds with the same settings.

1. UI-only screenshot baseline, schedule OFF.
2. Show/hide password.
3. save/load 1 account and multiple rows.
4. valid and invalid game folder.
5. open one game.
6. login one account with window unobscured.
7. login one account while game is covered.
8. two-account login proving sequential launch + parallel login.
9. cancel/close during each major login stage.
10. post-login Chờ.
11. post-login Party.
12. post-login Train.
13. post-login Train LSV.
14. post-login Dồn vàng.
15. destination automation already running.
16. destination tab hidden before routing; verify 1s polling and 20s bound.
17. all selected accounts succeed.
18. mixed success/failure.
19. zero successes.
20. scheduled open followed by post-login route, with scheduler still waiting for close.

For cases 18–19, record exact original behavior before locking reconstructed logic.

## F gate result
F01–F11 form the complete Login research handoff. Do not reopen earlier F tasks unless new evidence contradicts an established contract.
