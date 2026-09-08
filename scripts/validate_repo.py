#!/usr/bin/env python3
from pathlib import Path
import csv, re, sys

ROOT = Path(__file__).resolve().parents[1]
HEX64 = re.compile(r'^[0-9a-f]{64}$')
errors=[]

def read_csv(path):
    with path.open(newline='',encoding='utf-8') as f:
        return list(csv.DictReader(f))

required=[
 'README.md','ledgers/master-evidence-index.csv','ledgers/active-provenance-ledger.csv',
 'ledgers/active-provenance-ledger.xlsx','public/reach/20260907_reach.ods','public/reach/reach.csv',
 'git-history/git-milestones.csv','git-history/git-crosslinks.csv','chronology/phase-calculus-chronology.md',
 'historical/legacy-cf/legacy-cf-index.csv','ledgers/methodology-lineage.csv',
 'source-index/source-artifact-index.csv','methodology/ORCHESTRA/README.md','methodology/Cairn/README.md'
]
for rel in required:
    if not (ROOT/rel).exists(): errors.append(f'missing {rel}')

src=ROOT/'source-index/source-artifact-index.csv'
if src.exists():
    ids=set()
    for n,row in enumerate(read_csv(src),start=2):
        aid=row.get('Artifact_ID','').strip()
        if not aid: errors.append(f'{src}:{n}: missing Artifact_ID')
        elif aid in ids: errors.append(f'{src}:{n}: duplicate Artifact_ID {aid}')
        ids.add(aid)
        sha=row.get('SHA256','').strip()
        if not HEX64.match(sha): errors.append(f'{src}:{n}: invalid SHA256')
        inclusion=row.get('Public_Inclusion','').strip()
        copied=row.get('Copied_Path','').strip()
        if inclusion in {'INCLUDED','SELECTED_DOC','SELECTED_DOCS'} and copied:
            if not (ROOT/copied).exists(): errors.append(f'{src}:{n}: missing copied path {copied}')

master=ROOT/'ledgers/master-evidence-index.csv'
if master.exists():
    rows=read_csv(master)
    ids=set()
    for n,row in enumerate(rows,start=2):
        eid=row.get('Evidence_ID','').strip()
        if not eid: errors.append(f'{master}:{n}: missing Evidence_ID')
        elif eid in ids: errors.append(f'{master}:{n}: duplicate Evidence_ID {eid}')
        ids.add(eid)

if errors:
    print('FAIL')
    for e in errors: print(e)
    sys.exit(1)
print('PASS')
print('master evidence rows:', len(read_csv(master)))
print('source artifact rows:', len(read_csv(src)))
