#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, sys
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'hashes/SELECTED_ARTIFACTS_SHA256SUMS.txt'
TARGETS=['chronology','public','git-history','methodology','historical','records','ledgers','source-index','schemas','docs']
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
    return h.hexdigest()
def build():
    files=[]
    for rel in TARGETS:
        base=ROOT/rel
        if base.exists(): files += [p for p in base.rglob('*') if p.is_file() and p!=OUT]
    return ''.join(f'{digest(p)}  {p.relative_to(ROOT).as_posix()}\n' for p in sorted(files))
ap=argparse.ArgumentParser();g=ap.add_mutually_exclusive_group(required=True);g.add_argument('--write',action='store_true');g.add_argument('--check',action='store_true');a=ap.parse_args();cur=build()
if a.write:
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(cur,encoding='utf-8');print(OUT.relative_to(ROOT));sys.exit(0)
if not OUT.exists() or OUT.read_text(encoding='utf-8')!=cur:
    print('FAIL: selected artifact hashes are stale');sys.exit(1)
print('PASS')
