# F03 — Password behavior flow

UI state:

password Entry
→ constructed with show='*'
→ checkbox "Hiện mật khẩu" unchecked in locked screenshot
→ password rendered as mask characters

Toggle display:

show_pass_var changes
→ _toggle_show_password
→ change Entry show property
→ checked: reveal real Entry text
→ unchecked: show mask '*'
→ apply to visible rows + _hidden_rows

Important:
masking changes presentation only.
It does not replace the underlying password string.

In-memory persistence path:

entry_pass
→ _sync_accounts_cache
→ plain dict field pass/password
→ _accounts_cache
→ account serializer

Persistent row:

check | user | pass | captcha | proxy
→ newline between rows
→ [Settings] accounts
→ settings.ini

No recovered credential transform:
- no encrypt/decrypt
- no Fernet/AES/DPAPI
- no base64 wrapper
- no keyring
- shared write_settings is INI persistence, not a credential vault

Login-use path:

selected checked row
→ entry_user.get().strip() evidence
→ entry_pass raw value
→ tuple (row_index, tk, mk, captcha_mode, proxy)
→ worker mk_val
→ _login_click_worker / _login_click_monitor
→ click game password field
→ enter mk
→ click Login

Validation:

missing username/password
→ warning
→ row is not launched through normal login path

Exposure boundaries:

No explicit password clipboard path recovered.
No explicit password log format recovered.
DLL hashlib/md5 logic belongs to DLL integrity checking, not password hashing.

Delimiter boundary:

password is stored inside a raw pipe/newline record
→ no escaping layer recovered
→ exact behavior for passwords containing delimiter/newline remains UNKNOWN

Deferred:
- exact game-input key/click mechanics → F06
