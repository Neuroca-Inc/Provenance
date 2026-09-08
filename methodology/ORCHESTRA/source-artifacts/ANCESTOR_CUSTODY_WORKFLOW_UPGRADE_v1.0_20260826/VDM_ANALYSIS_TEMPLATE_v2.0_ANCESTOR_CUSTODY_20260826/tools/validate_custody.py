#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
P=re.compile(r'REPLACE_ME')
ALLOWED={'CONTROLLING','STILL_RELEVANT','SUPERSEDED_BY_THIS_PACKAGE','HISTORICAL_ONLY','NO_LONGER_RELEVANT'}
def d(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def load(p,e):
 try:return json.loads(p.read_text())
 except Exception as x:e.append(f'invalid {p}: {x}');return {}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('root',type=Path,nargs='?',default=Path('.'));ap.add_argument('--strict',action='store_true');a=ap.parse_args();r=a.root.resolve();e=[]
 A=load(r/'ANCESTRY.json',e);C=load(r/'CLOSEOUT.json',e)
 roots={x.get('root_id'):x for x in A.get('roots',[])}
 if not roots:e.append('no ancestry roots declared')
 ids=[]
 for x in A.get('ancestors',[]):
  i=x.get('ancestor_id');ids.append(i)
  rid=x.get('root_id');rel=x.get('relative_path');uri=x.get('uri')
  if not i:e.append('ancestor missing id')
  if not uri and not(rid and rel):e.append(f'{i} lacks exact reference')
  if rid and rid not in roots:e.append(f'{i} unknown root {rid}')
  if a.strict:
   for k in ('kind','relation','scope','why_relevant','current_relevance'):
    if not x.get(k) or P.search(str(x.get(k))):e.append(f'{i} missing/placeholder {k}')
   if rid and rel and roots[rid].get('exact_path') and not P.search(str(roots[rid]['exact_path'])):
    p=Path(roots[rid]['exact_path'])/rel
    if not p.exists():e.append(f'{i} path missing: {p}')
    elif p.is_file() and x.get('sha256') and not P.search(str(x['sha256'])) and d(p)!=x['sha256']:e.append(f'{i} sha mismatch')
 if len(ids)!=len(set(ids)):e.append('duplicate ancestor ids')
 if a.strict:
  if C.get('status') not in {'READY_TO_CLOSE','CLOSED'}:e.append('closeout status must be READY_TO_CLOSE or CLOSED')
  disp=C.get('ancestor_disposition',[]); did=[x.get('ancestor_id') for x in disp]
  if set(did)!=set(ids):e.append(f'ancestor disposition mismatch missing={sorted(set(ids)-set(did))} extra={sorted(set(did)-set(ids))}')
  for x in disp:
   if x.get('relevance_after_close') not in ALLOWED:e.append(f"{x.get('ancestor_id')} invalid disposition")
   for k in ('why','successor_instruction'):
    if not x.get(k) or P.search(str(x.get(k))):e.append(f"{x.get('ancestor_id')} incomplete {k}")
  arts=C.get('important_artifacts',[])
  if not arts:e.append('no important artifacts')
  for x in arts:
   p=x.get('path')
   if not p or P.search(str(p)):e.append('important artifact path missing/placeholder');continue
   fp=r/p
   if not fp.is_file():e.append(f'important artifact missing: {p}')
   elif not x.get('sha256') or P.search(str(x.get('sha256'))):e.append(f'important artifact hash missing: {p}')
   elif d(fp)!=x['sha256']:e.append(f'important artifact sha mismatch: {p}')
  if not C.get('successor_start_here'):e.append('successor_start_here empty')
 if e:
  print('FAIL');[print('- '+x) for x in e];return 1
 print('PASS');print(f'- ancestors: {len(ids)}');return 0
if __name__=='__main__':raise SystemExit(main())
