# F07 — Captcha option flow

Per-row mode selection:

readonly captcha Combobox
→ Không / Tool / Proxy
→ _on_captcha_mode_change
→ _schedule_save
→ row action button is reconfigured

Không:
→ row action blank/disabled
→ Login worker uses direct network path
→ no row private proxy required

Tool:
→ row action ⇄
→ ordinary/free-proxy path
→ proxy pool / forwarder helpers are used
→ detailed allocation/rotation remains F08

Proxy:
→ row action ➜
→ if user selected this mode interactively:
   → auto-open private-proxy editor
→ if config was merely loaded:
   → do not auto-open editor
→ require row private proxy value
→ missing value: reject/skip that account
→ runtime path uses private/pinned proxy
→ pinning mechanics remain F08

Private-proxy editor:

permission check
→ denied:
   → show red permission warning
→ allowed:
   → open 440x100 popup
   → accept protocol://user:pass@ip:port
      or user:pass:ip:port
   → parse/validate
   → save row proxy state
   → pinned-file mechanics deferred to F08

Captcha/DLL readiness at Login init:

LoginTab.__init__
→ _check_dll_status
→ inspect local DLL/config source/path state
→ lbl_dll_status

not ready:
→ red "⚠️ Vượt captcha chưa hoạt động"

ready:
→ green "✅ Hệ thống vượt captcha sẵn sàng"

background freshness check:
→ _check_dll_hash_worker
→ hashlib.md5/hexdigest
→ Tk after callback
→ "Đã cập nhật cấu hình mới nhất"
   or
→ "Cần cập nhật cấu hình"

Important boundary:

readiness label/status
!= proven hard gate over captcha Combobox/login worker

No recovered Login-owned external captcha solver:
- no captcha HTTP service URL
- no 2Captcha/AntiCaptcha surface
- no OCR/pytesseract
- no Selenium/browser solver

Compatibility load surface:

proxy_mode = none/free/private
+
row tokens Không/Có/Tool/Proxy

Current runtime uses captcha_mode.
Exact Có migration and legacy proxy_mode mapping remain UNKNOWN.

F06 consumption:

resolved captcha_mode + row proxy
→ choose direct/free/private network route
→ F06 performs same background HWND login sequence

F08 owns:
- proxy parsing normalization
- free-proxy pool refresh/allocation
- forwarder ports/files
- private pinning
- proxy rotation/advance policy
