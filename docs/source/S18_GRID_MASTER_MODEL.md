# S18 native grid/master/settings model

Original C05: dynamic master Radiobutton tied to HWND, with PID-generation cache protection; change of master affects physical window layout. Original C08: 3x4 grid, +/- controls, on-grid-change labels and Settings.grid_cols/grid_rows persisted through settings.ini. Master identity must NOT be persisted.

Bounded S18 reconstruction:
- GridSettingsStore uses existing src/settings_store.py to preserve unrelated sections and dated backups; local input limits 1..12 only (original bounds UNKNOWN). Current native workspace defaults 3x4; any changes persist under Settings section grid_cols/grid_rows.
- MasterSelection tracks current (HWND,PID) not arbitrary title; radio labels display S09 cached window titles plus HWND disambiguator, not fake RoleName. First discovered candidate fallback is explicitly local policy. Cache disappearance or numeric HWND PID reuse invalidates old master identity.
- Original master radios are actual ttk.Radiobutton widgets; invoking them updates C18 layout worker master at index 0. Grid +/- buttons update actual native layout inputs. New selection cancels stale native worker event and uses subsequent S13 maintenance callback; does not implement C19 keyboard/mouse sync.
- No original C06 formula or old +/- bounds implied, no game reading or network token issuance. Real native Windows test uses four TEST-OWNED Tk HWNDs and a fake game identity adapter confined to CI; real HWND rectangles/Win32 SetWindowPos and settings file effects checked. Unrelated HWND untouched; revoked authority stops moves.
- CI success: [S18 run 37888218013](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37888218013), **210/210 unit tests**, native PASS_NATIVE_S18_REAL_GRID_BUTTONS_RADIOS_PERSISTENCE_AND_REVOKE and S17 native rerun PASS. Same HEAD S10-S18 + Stage-S all SUCCESS.

Remaining UNKNOWN: original +/- bounds, original auto-master fallback, original title format, original X/Y math and worker cadence; real RoleName memory source, signed server and full Windows product EXE unavailable/not tested.
