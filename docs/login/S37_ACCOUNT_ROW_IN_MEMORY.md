# S37 — Verified in-memory F01 Login accounts UI (NO F02 writer)

```text
Existing S35 guarded E03 Login builder (only visible with true Info claims)
  -> S25 TLMLoginPathTab
      -> existing real blue Chọn thư mục game (unchanged)
      -> S37 TLMAccountRows:
         ttk.LabelFrame: Cấu hình tài khoản
         Canvas + vertical Scrollbar + rows_inner
         prompt + Hiện mật khẩu ttk.Checkbutton
         header ✅ Button
         100 rows (logical 100, pitch 35 px):
            ⬜ / ✅️  -> real row-selected bool
            username tk.Entry (in-memory only)
            password tk.Entry, show='*' until show-password checked
            captcha readonly ttk.Combobox Không / Tool / Proxy
            NO unimplemented Login/Proxy action buttons
         header:
            any unchecked -> check all 100
            all checked -> uncheck all
         shutdown -> clear live password variables; NO account file writer

F02 UNKNOWN original check-field serialized token, legacy Có migration:
  Settings.accounts existing raw value == UNMODIFIED before and after
  S37 in-memory editing / closing / password-toggle. NEVER normalize.
  No original account data loaded yet (S38 candidate), no persistence claim.

Real product main() still refuses with exit code 2 until authentic Info.
S36 packaged EXE remains DIAGNOSTIC_NOT_PRODUCT and fail-closed.
```

**Evidence:** [S37 Windows 558/558 PASS](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37920868815) · [native test artifact 11611976959](https://github.com/ngmthang-g/2222222222222222222222222222222222222222222/actions/runs/37920868815/artifacts/11611976959). No native test passwords exported.
