# F02 — Account storage flow

Persistent account rows:

Login row widgets
→ account/password/captcha/proxy/check values
→ _schedule_save
→ 300 ms debounce
→ _save_accounts
→ _sync_accounts_cache
→ plain-dict cache records
→ serialize one row per line
→ pipe-separated fields
→ [Settings] accounts
→ %APPDATA%/TLMTool/settings.ini

On-disk logical field order:

check | user | pass | captcha | proxy

Normalized in-memory row keys:

check
username
password
captcha_mode
proxy_env

Destroy safety path:

<Destroy>
→ _save_on_destroy
→ shared _settings_lock
→ read_settings
→ update [Settings] accounts
→ write_settings
→ catch/log destroy-save failure

Plan row limiting:

logical 100 rows
→ plan decreases
→ move excess visible rows into _hidden_rows FIFO
→ preserve data

plan increases
→ restore _hidden_rows first
→ add blank rows only if still required

Visibility is not deletion.

Runtime online tracking is separate:

successful account login
→ _mark_row_online
→ tracked live-window/session metadata
→ login_online.json

TLMTool restart
→ read login_online.json
→ validate stored HWND alive
→ restore tracking/row online appearance

Dead runtime HWND
→ remove online tracking state
→ account row in settings.ini remains

Login-time history is separate:

successful login
→ _record_login_time
→ last_login_times.json

Storage boundaries:

settings.ini
= persistent account/config rows

login_online.json
= runtime live-window/session tracking

last_login_times.json
= login timestamp/history

Explicit unknowns:
- exact textual encoding of the check boolean in each pipe row
- exact compatibility mapping of legacy captcha token Có
- exact JSON indentation/order for online-state serialization
- exact source statement ordering visible+hidden row collection during every save path
