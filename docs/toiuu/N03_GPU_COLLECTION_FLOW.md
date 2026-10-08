# N03 — GPU collection, failure and chart integration

## Authority
Read PLAN.md, STATE.md and PROJECT_STATUS.md and checked GitHub main HEAD 326090e7b7ec8b44a4f9bf767bd0f50ac9ca8831 before work. N01/N02 already complete, no N03 artifacts. Original user ZIP SHA-256 c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd, 1050 entries, clean CRC. Original inner TLMTool.dist/TLMTool.exe is 47450112 bytes, SHA-256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22. Binary was statically inspected, never executed. This document does not reconstruct source statements from constants.

## GPU reader, command and timeout
Original ToiuuTab._read_gpu block includes subprocess, check_output, CREATE_NO_WINDOW, STDOUT, stderr, timeout and creationflags. Exact utility command components:
- nvidia-smi
- --query-gpu=utilization.gpu
- --format=csv,noheader,nounits

This supports a current NVIDIA GPU utilization reading path with a subprocess timeout and no-console handling. The exact Python subprocess keyword expressions and exception ordering remain UNKNOWN. A nearby tagged integer candidate 3 is NOT enough to conclude timeout=3.

## Parsing, unavailable result, multiple GPUs
Read-gpu symbol family includes decode, utf-8, errors, ignore, replace, split, isdigit and local names self, flags, out, vals. Exact original embedded documentation:
> % GPU qua nvidia-smi; None nếu không có/không đọc được.

It therefore intends to return utilization or None when missing/unreadable. This is a static intent and interface, not proof of all error branches. It is not established how multiple GPU rows are selected or combined, how invalid CSV is handled, which exceptions are caught, or whether a valid zero utilization is distinguished in every branch from None. No other independent AMD/Intel reader appeared in this exact active function; do not overgeneralize that negative evidence.

## GPU history and chart
ToiuuTab has _gpu_avail and _gpu_hist separate from CPU; graph construction includes deque, GRAPH_HIST and maxlen. N02 already found shared _sample_loop, _schedule_redraw and _redraw_graphs in the sample/paint pipeline. The GPU text resources are GPU: and GPU: N/A (không có nvidia-smi). _draw_one uses orange #e65100. Detached _update_monitor_view is present; its lifecycle belongs to N04.

Static integration model (not reconstructed call order):
nvidia-smi query -> decode/parse -> percentage or None -> GPU availability/history -> Tk redraw -> text and orange plot.

Whether None is appended to history, skipped, clears data, or recovers after reconnect is not proven. N02 timing ambiguity (1s doc versus unbound numeric constants) is preserved.

## Screenshot AFTER EXE review
Reused original B11 Tối ưu screenshot: GPU: N/A (không có nvidia-smi) and no GPU history line, alongside CPU: 15%. That is consistent with fallback UI; it cannot establish absent NVIDIA hardware, a specific command failure, timeout or dynamic chart behavior.

## Future acceptance, all NOT_RUN
1. Exact command argument/timeout/creation flags and stderr behavior.
2. Working numeric single-GPU output; zero versus unavailable None.
3. Missing executable, nonzero exit, timeout, empty/invalid output.
4. Multiple-GPU output selection/aggregation follows original.
5. Availability changes do not leave stale data/labels.
6. Bounded GPU graph history, orange plotted samples, main-thread Tk updates.
7. Detached monitor uses correct shared data without duplicate workers (N04).
8. Original-vs-reconstructed Windows visual and live functional parity.

Evidence tiers: exact binary strings/doc and prior B11 screenshot are VERIFIED STATIC/VISUAL; runtime behavior and unbound constants are UNKNOWN or NOT_RUN. No product source, build scripts or UI placeholders were created.

## NEXT_ACTION
N04 — Tối ưu detached CPU/GPU monitor lifecycle/layout/persistence audit. Original EXE first: _toggle_monitor_view, _open_monitor_view, _close_monitor_view, _update_monitor_view, _restore_monitor_view, toiuu_monitor_open. Reuse B11 only after static analysis. Keep N01–N03 unchanged and Proxy excluded.
