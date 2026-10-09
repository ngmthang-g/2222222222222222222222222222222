# S38 legacy Login read-only flow

```text
%APPDATA%/TLMTool/settings.ini  [Settings] accounts
        |
E05 read_settings (read-only, no write_settings)
        |
S38 parse_legacy_accounts:
  check_raw | username | password | captcha_raw | proxy_raw
  1..100 rows; each exactly 5 fields
  captcha literal in Không / Tool / Proxy / Có
  any unexpected input --> BLOCKED_* --> no hydration / no partial data
        |
validated immutable records --> real S37 Tk rows:
  username Entry: exact original string
  password Entry: exact string, visually mask '*'
  captcha readonly Combobox: literal Có shown (NO migration)
  checkbox marker ❔: unknown disk token (NO bool inference)
  proxy_raw never shown/acted on (NO Proxy runtime)
        |
S37 in-memory current-session controls
        |
close/destroy --> wipe Tk password variables --> NO account file write

Original settings.ini remains byte-for-byte untouched by S38.
Original E03 Info gate + S36 fail-closed diagnostic entrypoint unchanged.
```
