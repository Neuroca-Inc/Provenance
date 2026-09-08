#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

ALLOWED_RELEVANCE={'controlling','active_upstream','supporting','historical_only','superseded'}

def digest(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument('root',type=Path,nargs='?',default=Path('.'))
    p.add_argument('--id',required=True)
    p.add_argument('--kind',required=True)
    p.add_argument('--relation',required=True)
    p.add_argument('--depth',type=int,default=1)
    p.add_argument('--root-id')
    p.add_argument('--relative-path')
    p.add_argument('--uri')
    p.add_argument('--manifest-sha256')
    p.add_argument('--authored-at')
    p.add_argument('--discovered-at')
    p.add_argument('--inherited-via')
    p.add_argument('--relevance',choices=sorted(ALLOWED_RELEVANCE),required=True)
    p.add_argument('--scope',required=True)
    p.add_argument('--why',required=True)
    a=p.parse_args()
    root=a.root.resolve(); path=root/'ANCESTRY.json'
    data=json.loads(path.read_text())
    if any(x.get('ancestor_id')==a.id for x in data['ancestors']): raise SystemExit(f'duplicate ancestor id: {a.id}')
    if not a.uri and not (a.root_id and a.relative_path): raise SystemExit('provide --uri OR --root-id + --relative-path')
    sha=None
    if a.root_id and a.relative_path:
        roots={x['root_id']:x for x in data['roots']}
        if a.root_id not in roots: raise SystemExit(f'unknown root id: {a.root_id}')
        rp=Path(roots[a.root_id]['exact_path'])/a.relative_path
        if rp.is_file(): sha=digest(rp)
    rec={'ancestor_id':a.id,'kind':a.kind,'relation':a.relation,'depth':a.depth,'root_id':a.root_id,
         'relative_path':a.relative_path,'uri':a.uri,'sha256':sha,'manifest_sha256':a.manifest_sha256,
         'authored_at':a.authored_at,'discovered_at':a.discovered_at,'inherited_via':a.inherited_via,
         'current_relevance':a.relevance,'scope':a.scope,'why_relevant':a.why}
    data['ancestors'].append(rec); path.write_text(json.dumps(data,indent=2)+'\n')
    print(a.id)
    return 0
if __name__=='__main__': raise SystemExit(main())
