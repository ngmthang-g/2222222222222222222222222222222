# E05 — Config management flow

Shared config.ini:

%APPDATA%/TLMTool/config.ini
→ get_config_path / CONFIG_PATH
→ RawConfigParser
→ load section values
→ caller/tab consumes values

save_config(section, values)
→ ensure CONFIG_DIR exists
→ add missing section
→ set key/value pairs
→ write UTF-8 config.ini

Shared settings.ini:

%APPDATA%/TLMTool/settings.ini
→ read_settings
→ RawConfigParser with duplicate-tolerant behavior
→ optional sanitization/control-character handling
→ feature tab reads its own keys from [Settings]

feature save
→ acquire shared settings access path
→ update feature-owned keys
→ write_settings
→ create temp .tmp
→ write INI
→ create dated settings.YYYYMMDD.ini backup path/copy
→ os.replace temp into settings.ini
→ prune older settings.*.ini according to _BACKUP_KEEP

Tab ownership:

Start / Login / Party / Daily / Phó Bản / Farm / Train LSV / Đồn / Rao / Tối ưu
→ own key/default interpretation
→ shared read_settings/write_settings storage

Complex feature state:
rows/groups/schedules
→ json.dumps
→ store string inside [Settings]
→ json.loads on load

InfoTab separate config.ini path:

InfoTab._get_config_path
→ config.ini alongside script/frozen context
→ ConfigParser
→ simple dict load/save
→ Info/license/server state

Not part of shared INI:
- login_online.json
- last_login_times.json
- forwarder/proxy runtime state files
- /sdcard/TLM/tlm_*.json
- logs

Unknowns:
- numeric _BACKUP_KEEP value
- exact concrete lock class
- exact control-character sanitization scope
- no global hot-reload watcher recovered
