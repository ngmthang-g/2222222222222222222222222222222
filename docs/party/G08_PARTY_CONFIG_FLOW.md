# G08 — Party configuration flow

## Initialization

PartyTab.__init__
→ _saving_enabled guard exists
→ _build_ui
   → create _after_party = wait
   → trace_add("write", save callback)
   → build active team section
      → cfg_groups = party_groups
      → cfg_group1 = party_group1
      → default first cluster
→ _load_config
→ later normal user edits may persist

Exact flag-enable instruction timing remains UNKNOWN.

## Load

CONFIG_PATH
→ shared _settings_lock
→ read_settings
→ Settings
→ party_after
   → default wait
   → accepted internal values:
      wait / train / train_lsv / don / phoban

For active team section:
→ raw current key = party_groups
→ json.loads
→ current multi-group shape:
   [{num:n, members:[names...]}, ...]

Legacy compatibility path:
→ party_group1
→ first-group name list
→ used when legacy compatibility path is needed

Restore:
→ group/member StringVars receive character names
→ live Party refresh later reconciles ready/online choices

Never restore:
→ HWND
→ PID
→ RoleID
→ TeamID
as config identity.

## Save

ensure CONFIG_DIR exists
→ gather current Party group data
→ party_after
→ party_groups = JSON current multi-group data
→ party_group1 = first-group compatibility data
→ json.dumps(... ensure_ascii=False)
→ process dormant legacy-key set:
   party_corps_groups
   party_corps_group1
   party_follow
   party_pick
→ write_settings
→ on error: [PARTY] Save error: ...

Exact syntax used to remove/clean the four dormant keys is UNKNOWN.

## Identity boundary

Persisted:
→ after-party mode
→ character/member names
→ group structure

Runtime-only:
→ HWND/PID generation
→ RoleID
→ TeamID
→ running/cancel/refresh/join state

## Important negative rule

Old key exists
≠ active feature.

party_follow / party_pick / party_corps_*
→ compatibility residue/cleanup only
→ must not create current Party controls.
