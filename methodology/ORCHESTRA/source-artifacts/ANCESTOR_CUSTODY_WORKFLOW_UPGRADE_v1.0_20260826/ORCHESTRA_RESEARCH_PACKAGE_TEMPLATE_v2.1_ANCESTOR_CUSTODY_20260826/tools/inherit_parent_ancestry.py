#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path

def digest(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def safe_id(s:str)->str:return re.sub(r'[^A-Za-z0-9_]+','_',s).upper()

def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--parent',type=Path,required=True);a=ap.parse_args()
 root=a.root.resolve(); parent=a.parent.resolve()
 cur=json.loads((root/'ANCESTRY.json').read_text()); pm=json.loads((parent/'PACKAGE.json').read_text()); pa=json.loads((parent/'ANCESTRY.json').read_text())
 pid=pm['package_id']; rid='PARENT_'+safe_id(pid)
 root_record={'root_id':rid,'kind':'package_directory','exact_path':str(parent.parent),'uri':None,'description':f'direct parent package root for {pid}'}
 roots={r['root_id']:r for r in cur['roots']}
 if rid not in roots:cur['roots'].append(root_record)
 mp=parent/'MANIFEST.json'; msha=digest(mp) if mp.is_file() else None
 existing={x.get('ancestor_id') for x in cur['ancestors']}
 direct_id='PARENT_'+safe_id(pid)
 if direct_id not in existing:
  cur['ancestors'].append({'ancestor_id':direct_id,'kind':'package','relation':'direct_parent','depth':1,'root_id':rid,'relative_path':parent.name,'uri':None,'sha256':None,'manifest_sha256':msha,'authored_at':pm.get('created_at'),'discovered_at':None,'inherited_via':None,'current_relevance':'controlling','scope':'parent package lineage and closure state','why_relevant':'direct package ancestor'})
 # Import parent's declared roots, failing on conflicting reused IDs.
 roots={r['root_id']:r for r in cur['roots']}
 for r in pa.get('roots',[]):
  old=roots.get(r['root_id'])
  if old is None:
   cur['roots'].append(r);roots[r['root_id']]=r
  elif old.get('exact_path')!=r.get('exact_path') or old.get('uri')!=r.get('uri'):
   raise SystemExit(f"root id collision with different coordinate: {r['root_id']}")
 # Import transitive ancestors with stable IDs where possible.
 existing={x.get('ancestor_id'):x for x in cur['ancestors']}
 for x in pa.get('ancestors',[]):
  aid=x.get('ancestor_id')
  if aid in existing:
   continue
  y=dict(x);y['depth']=int(x.get('depth',1))+1;y['inherited_via']=direct_id
  cur['ancestors'].append(y)
 (root/'ANCESTRY.json').write_text(json.dumps(cur,indent=2)+'\n')
 print(f'inherited {pid}: {len(pa.get("ancestors",[]))} transitive ancestor records');return 0
if __name__=='__main__':raise SystemExit(main())
