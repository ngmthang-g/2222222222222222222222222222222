# R01 — Immutable resources: loader/writer and Stage-S packaging gaps

## Scope and evidence
R01 resumes from the final NEXT_ACTION of P08. Verified docs/tasks/R01.md absent before work. Reused Gate A (A05/A07/A08), D06, D07, D08 and original_manifest/ORIGINAL_MANIFEST.tsv without modifying them.

The original ZIP TLMTool_2.1.2(10).zip was read-only. SHA256: c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd. CRC PASS; 1,050 archive entries, 1,002 regular files, 48 directories. Inner TLMTool.dist/TLMTool.exe: SHA256 15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22, 47,450,112 bytes.

## R01 per-file matrix
docs/resources/R01_RESOURCE_GAP_MATRIX.tsv records 26 resources relative to TLMTool.dist, with columns:
- path, size_bytes, sha256, header_hex16 (exact first 16 bytes), magic_class;
- reader_or_loader, writer, runtime_usage, confidence, stage_s_packaging, evidence.

This extends the existing 24 D06 rows (23 DATA + ppx/Default.ppx) with original emu_client.js and ld_remote.js. Every R01 row's name, size and SHA matches A07 ORIGINAL_MANIFEST: **26/26 PASS**. All D06 reused rows also match: **24/24 PASS**.

Groups: 14 opaque MZ/non-robust-PE .dat; five old/backup resources DLL-format files; one active resources.dat; version.dat; two JavaScript files; two text files (a log and a proxy working list); one Default.ppx XML. The first 16 bytes were independently read from the frozen ZIP. This 26-file data matrix does NOT replace the full 1,002-file dependency manifest.

## New exact compiled-filename name scan
Searched the complete inner EXE for each basename in both ASCII and UTF-16LE.
- Fourteen opaque .dat basenames: 0 occurrences.
- Five old/backup resources basenames: 0 occurrences.
- Active resources.dat: 7 ASCII occurrences; version.dat: 2; Default.ppx: 1.
- automove_log.txt: 1; proxy_working.txt: 10; emu_client.js: 2; ld_remote.js: 4.
- There were no UTF-16LE occurrences of these tracked exact names.

A missing literal name DOES NOT prove absence of runtime usage: dynamic path assembly, directory enumeration, alias resolution, or helper loading remain possible. Therefore the 14 opaque resources and five backups retain reader=UNKNOWN, writer=UNKNOWN and runtime_usage=UNKNOWN. In particular config.dat, settings.dat, or license.dat must not be treated as the actual config.ini, settings.ini or license state based on their filenames.

The two archived files data/resources.dat.bak-20260923 and data/resources.dat.old-locked are byte-identical in size/hash. This is not a live backup selection rule.

## Verified read/loader boundaries, not runtime-success claims
| Resource | Supported static reader/loader | Writer and runtime state |
|---|---|---|
| data/resources.dat | dll_injector.get_default_dll_path at 0x2919013; seven filename occurrences | Active injection payload by static reference; exact writer and live game attach UNKNOWN |
| version.dat | Start version DLL path logic at 0x2bfc36c | Copy/load/target writer UNKNOWN; Proxy feature development forbidden |
| data/automove_log.txt | Toiuu tick/performance watchdog 0x2c05bb8 | Historical diagnostics file; writer/append/rotation UNKNOWN |
| proxy_working.txt / ppx/Default.ppx | Proxy/forwarder/Proxifier setup references in D06 | Phase Q excluded; no runtime implementation |
| emu_client.js | emu_reader Frida RPC loader (D07/P02) | Live guest use NOT_RUN |
| ld_remote.js | emu_setup.push_script / AutoX overlay (P06) | emu_setup patches TEMP copy for PC_BASE; frozen source is not overwritten |

The outer launcher recovered in A05 sets the child process working directory to TLMTool.dist. The active payload path ./data/resources.dat is relative to that directory. This is a concrete packaging/working-directory compatibility constraint: changing the new launcher CWD risks breaking resource loading, even if the payload file is copied correctly.

Separate immutable package resources from runtime-generated files previously documented in D06: %APPDATA%/TLMTool/settings.ini, two config.ini path contexts, login*.json, Android guest /sdcard/TLM/tlm_*.json and generated logs. Do not rewrite opaque resources as INI/JSON.

## Open gaps and Stage-S handoff
| Gap ID | Remaining UNKNOWN / UNVERIFIED |
|---|---|
| G01 | Actual readers, writers and formats of the 14 opaque .dat files |
| G02 | Live selection, origin and writers of five historical resource DLL backups |
| G03 | Game process attachment, cleanup and file writes for active resources.dat |
| G04 | version.dat copy/load destination and runtime semantics; Phase Q no-development |
| G05 | Historical automove log exact writer, append and rotation behavior |
| G06 | Actual Frida/AutoX guest loading of two original JS scripts |
| G07 | Relative CWD behavior if inner TLMTool.exe launched directly |
| G08 | Windows runtime settings/config/login persistence verification |
| G09 | Full 1,002-file Nuitka DLL/PYD/Tk/asset packaging closure |
| G10 | Dynamic runtime access to opaque files despite zero literal name references |

Preserve all original binaries and files byte-for-byte. Do not select old payloads just because they exist, run the original injected code, implement Proxy or modify already-correct phase documents.

## Tests / gate result
- Read-only verifier tools/R01_VERIFY_RESOURCE_GAPS.py locally passed py_compile and ZIP-only integrity/name-scan verification, with 26 resources and 14+5 names unreferenced.
- Optional argument to verify TSV matrix against ZIP was NOT RUN locally; matrix was instead cross-joined on GitHub against A07 (26/26) and D06 (24/24) with zero differences. Do not label optional mode PASS.
- Windows runtime: NOT_RUN. Source app Stage S and Windows build Stage T remain missing (existing build audit); BUILD_BLOCKED_SOURCE_MISSING, not a compiler failure or PASS.

R01 status: **STATIC_RESOURCE_PROVENANCE_MATRIX_COMPLETE_WITH_RUNTIME_UNKNOWNS_PRESERVED**. Phase R required row-level fields are covered with UNKNOWN explicitly retained.

## NEXT_ACTION
S01 — read main app architecture and UI baseline first, then create the smallest genuine Stage-S source entrypoint/settings shell based only on verified original contracts. No fake functional controls, no unauthorized UI additions, preserve original tab gating and relative working directory; Stage-T build only after actual source exists.
