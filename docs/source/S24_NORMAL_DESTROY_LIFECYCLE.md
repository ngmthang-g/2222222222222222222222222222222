# S24 — Tk destroy, tab owner shutdown, no hidden global kill

Original **E08**: normal root/widget destruction -> each built tab's own `<Destroy>` cleanup and timer/worker/resource stop. Original shell-wide WM_DELETE_WINDOW and normal-close global forwarder/game stop not recovered. These are **not** the updater or heartbeat forced-`os._exit` paths.

```text
S21 original-name mutex (real guard; test uses S24_TEST_ONLY names)
 -> S23 append-only stdout/stderr session tee
  -> S22 startup diagnostics/faulthandler
   -> Tk GUI (production Info server missing, so main() still refuses)
    -> root.destroy() / app.shutdown()
      -> Start.container <Destroy> marks CLOSED before touching controls
      -> Stop C18 worker permission flag
      -> Stop preview maintenance and S09 UI polling / producer
      -> DWM UnregisterThumbnail + DestroyWindow test-owned destination
      -> root <Destroy> observer only for event.widget == root
      -> lifecycle stop active refresh once, shutdown each built owner once
      -> fence pending Tk authority callbacks and prevent rebuild after close
  -> S22 restore thread/crash hooks
 -> S23 write End session marker, restore stdout/stderr, close log
 -> S21 release single-instance mutex
```

**Important:** this lifecycle is S24 *safe reconstruction* using recovered owner boundaries, not proof of byte-for-byte original Python/Tk destroy ordering. Tabs never built remain unbuilt; exceptions in one tab shutdown do not block other already-built owners, with first error surfaced. Start root-destroy callbacks may run after descendant widgets are already destroyed; the `_closed` fence prevents reconfiguring deleted controls.

**Windows runtime evidence:** [S24 workflow 37899237476](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37899237476) SUCCESS: 315/315 units; two actual Tk native Win32 source HWNDs **test owned, not game**, real DWM destination creation+removal; both root-first and app-first shutdown paths idempotent, producer stopped and permission revoke stable. Same workflow reran S23/S22/S21/S20/S10 native tests successfully.

Auth signature/service, original normal-close forwarder behavior, real game and full EXE remain unavailable. No Proxy work or game input were added.
