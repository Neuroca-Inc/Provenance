#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument('root',type=Path,nargs='?',default=Path('.')); a=p.parse_args(); root=a.root.resolve()
    ancestry=json.loads((root/'ANCESTRY.json').read_text()); close=json.loads((root/'CLOSEOUT.json').read_text())
    close['package_id']=ancestry['package_id']; close['status']='WORKING'; close['closed_at']=None
    existing={x.get('ancestor_id'):x for x in close.get('ancestor_disposition',[]) if x.get('ancestor_id')}
    rows=[]
    for anc in ancestry['ancestors']:
        aid=anc['ancestor_id']
        rows.append(existing.get(aid,{'ancestor_id':aid,'relevance_after_close':'REPLACE_ME','why':'REPLACE_ME','successor_instruction':'REPLACE_ME'}))
    close['ancestor_disposition']=rows
    (root/'CLOSEOUT.json').write_text(json.dumps(close,indent=2)+'\n')
    print(root/'CLOSEOUT.json'); return 0
if __name__=='__main__': raise SystemExit(main())
