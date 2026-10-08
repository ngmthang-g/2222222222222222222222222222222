#!/usr/bin/env python3
"""Read-only R01 resource integrity and static filename-reference verifier.

Usage: python R01_VERIFY_RESOURCE_GAPS.py original.zip [R01_RESOURCE_GAP_MATRIX.tsv]
No package member is extracted or executed. No user configuration is written.
"""
import csv
import hashlib
import json
import pathlib
import sys
import zipfile

ORIGINAL_SHA = 'c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd'
EXE_SHA = '15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22'
PREFIX = 'TLMTool_2.1.2/TLMTool.dist/'
OPAQUE = ('accounts.dat','app_state.dat','auth_token.dat','cache.dat','config.dat',
          'license.dat','logs.dat','manifest.dat','package.dat','sec_key.dat',
          'session.dat','settings.dat','signature.dat','user_profile.dat')
BACKUPS = ('resources.dat.bak-20260923','resources.dat.old','resources.dat.old-locked',
           'resources.old2.dat','resources.old3.dat')
CORE = ('data/resources.dat','data/automove_log.txt','version.dat','proxy_working.txt',
        'ppx/Default.ppx','emu_client.js','ld_remote.js')
TRACKED = tuple('data/'+x for x in OPAQUE+BACKUPS) + CORE


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def main(zip_path, matrix_path=None):
    zp = pathlib.Path(zip_path)
    with zp.open('rb') as f:
        zip_sha = hashlib.file_digest(f, 'sha256').hexdigest()
    assert zip_sha == ORIGINAL_SHA, 'frozen ZIP SHA mismatch'
    with zipfile.ZipFile(zp, 'r') as z:
        entries = z.infolist()
        files = [x for x in entries if not x.is_dir()]
        assert (len(entries), len(files)) == (1050, 1002), 'ZIP count changed'
        assert z.testzip() is None, 'ZIP CRC error'
        names = {x.filename for x in files}
        assert all(PREFIX+x in names for x in TRACKED), 'tracked resource missing'
        image = z.read(PREFIX+'TLMTool.exe')
        assert sha256_bytes(image) == EXE_SHA, 'inner EXE changed'
        observed = {}
        for rel in TRACKED:
            raw = z.read(PREFIX+rel)
            observed[rel] = {'size_bytes':len(raw),'sha256':sha256_bytes(raw),
                             'header_hex16':raw[:16].hex()}
        if matrix_path is not None:
            with open(matrix_path,'r',encoding='utf-8-sig',newline='') as f:
                table = list(csv.DictReader(f,delimiter='\t'))
            assert len(table) == len(TRACKED), 'matrix row count not 26'
            assert {r['path'] for r in table} == set(TRACKED), 'matrix names mismatch'
            for row in table:
                ref = observed[row['path']]
                assert int(row['size_bytes']) == ref['size_bytes'], 'matrix size differs: '+row['path']
                assert row['sha256'] == ref['sha256'], 'matrix SHA differs: '+row['path']
                assert row['header_hex16'] == ref['header_hex16'], 'matrix header differs: '+row['path']
        targets = OPAQUE+BACKUPS
        referenced = [n for n in targets if n.encode('ascii') in image or n.encode('utf-16le') in image]
        assert not referenced, 'unexpected exact opaque/backup filename literal'
        assert observed['data/resources.dat.bak-20260923']['sha256'] == observed['data/resources.dat.old-locked']['sha256']
        assert observed['data/resources.dat.bak-20260923']['size_bytes'] == observed['data/resources.dat.old-locked']['size_bytes']
        return {'status':'PASS','archive_entries':len(entries),'files':len(files),
                'directories':len(entries)-len(files),'tracked_files':len(observed),
                'opaque_files':len(OPAQUE),'backup_copies':len(BACKUPS),
                'opaque_and_backup_literal_references':len(referenced),
                'duplicate_backup_pair_equal':True,
                'matrix_rows_verified':len(TRACKED) if matrix_path else 'SKIPPED_NO_MATRIX',
                'original_sha256':zip_sha}


if __name__ == '__main__':
    if len(sys.argv) not in (2,3):
        raise SystemExit('Usage: python R01_VERIFY_RESOURCE_GAPS.py original.zip [matrix.tsv]')
    try:
        print(json.dumps(main(sys.argv[1],sys.argv[2] if len(sys.argv)==3 else None),indent=2))
    except Exception as exc:
        print(json.dumps({'status':'FAIL','error':str(exc)}))
        raise SystemExit(1)
