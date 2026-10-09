# S50 — Failed native worker creation must not leave phantom clock

\`\`\`text
S49:
  clock.enable(now) -> _cancel.clear -> _thread=Thread(...)
  Thread.start raises RuntimeError    => catches / rollback
  Thread.start raises OSError         => UNCAUGHT [BUG]
    result: _cancel=False, _clock enabled, unstarted thread reference,
            misleading EVALUATING_ONLY_NO_ACTIONS and Tk callback exception

S50:
  clock.enable(now) -> _cancel.clear -> _thread=Thread(...)
  Thread.start raises RuntimeError or OSError (incl. PermissionError)
    => _cancel.set
       clock.disable
       _clock=None
       _thread=None
       status=CLOSED if permanent shutdown else BLOCKED_THREAD
       return False
  F09ReadOnlyTabLifetime catches False, stops Tk countdown preview
  Native Label Destroy remains instant; no orphan worker/Tk timer

No change to normal Event.wait(20), no actions, no Info/F05/F06 grant,
no Proxy or F02/F09 writes, S36 still NOT-PRODUCT.
\`\`\`
