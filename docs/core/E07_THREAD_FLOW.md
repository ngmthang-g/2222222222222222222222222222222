# E07 — Task/thread management flow

Tk/UI scheduling:
owner widget/tab
→ root.after / widget.after
→ scheduled callback id
→ after_cancel on stop/destroy
→ callback runs on Tk main thread

Worker/UI handoff:
blocking worker thread
→ compute / process / network / memory work
→ root.after(0, apply)
→ mutate Tk widgets on main thread

Start input sync:
master listener
→ queue.put(event)
→ single sync worker
→ ordered down/up work
→ task_done
→ watchdog/lock state

Start preview:
background preview worker
→ enumerate game windows + basic info (~3s)
→ heavier memory info (~8s)
→ write cache only
→ Tk preview loop consumes cache

Login:
_batch_cancel Event + _schedule_cancel Event
→ schedule/online/account workers
→ _launch_lock protects launch path
→ UI countdown/result pushed to main thread

Party:
_cancel Event + per-group cancels
→ one worker thread per group
→ group threads run in parallel
→ join(timeout)
→ after-party action on main thread

Daily/Farm/Train:
per-account threads
→ stop_event / generation / running flags
→ monitors/workers
→ root.after UI apply
→ bounded cleanup/join where present

CPU monitor:
daemon Thread(target=_check_loop)
→ shell-owned service
→ stop flag
→ join(timeout)

Emulator remote:
daemon service thread
→ ThreadingHTTPServer.serve_forever
→ shutdown/server_close on stop

Info heartbeat:
Tk after-id lifecycle
→ scheduled heartbeat/service callbacks
→ after_cancel on stop

Separate native/process boundaries:
- CreateRemoteThread = target-process injection thread, not Python Thread
- forwarder/update/Frida helpers = separate processes/services

Explicit unknowns:
- daemon flag for every worker
- every join timeout value
- exact global stop order when many owners stop simultaneously
