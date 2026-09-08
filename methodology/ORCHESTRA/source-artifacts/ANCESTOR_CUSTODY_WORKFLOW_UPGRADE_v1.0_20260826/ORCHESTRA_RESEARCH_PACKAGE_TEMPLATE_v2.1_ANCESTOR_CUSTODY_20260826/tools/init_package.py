#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, shutil
from datetime import datetime, timezone
from pathlib import Path

SLUG_RE=re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')

def parse_root(spec:str):
    if '=' not in spec: raise argparse.ArgumentTypeError('--root must be ROOT_ID=/exact/path')
    rid,path=spec.split('=',1)
    if not rid or not path: raise argparse.ArgumentTypeError('--root must be ROOT_ID=/exact/path')
    return rid,path

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument('--phase',type=int,required=True); p.add_argument('--branch',type=int,required=True); p.add_argument('--version',type=int,required=True)
    p.add_argument('--name',required=True); p.add_argument('--title'); p.add_argument('--origin-role',required=True); p.add_argument('--target-role',required=True)
    p.add_argument('--parent-package-id'); p.add_argument('--parent-manifest-sha256'); p.add_argument('--root',action='append',type=parse_root,required=True,help='repeatable ROOT_ID=/exact/path')
    p.add_argument('--output',type=Path,required=True); a=p.parse_args()
    if min(a.phase,a.branch,a.version)<0: raise SystemExit('phase, branch, version must be nonnegative')
    if not SLUG_RE.fullmatch(a.name): raise SystemExit('--name must be lowercase kebab-case')
    template=Path(__file__).resolve().parents[1]; pid=f'p{a.phase}-b{a.branch}-v{a.version}'
    stamp=datetime.now().astimezone().strftime('%Y%m%d_%H%M%S'); dest=a.output.resolve()/f'{pid}_{a.name}_{stamp}'
    if dest.exists(): raise SystemExit(f'destination exists: {dest}')
    shutil.copytree(template,dest)
    for name in ('MANIFEST.json','SHA256SUMS','TEMPLATE_STATUS.md'):
        q=dest/name
        if q.exists(): q.unlink()
    meta=json.loads((dest/'PACKAGE.json').read_text()); meta.update({'package_type':'orchestra_research_package','package_id':pid,'title':a.title or a.name.replace('-',' ').title(),'slug':a.name,'created_at':datetime.now(timezone.utc).isoformat(),'phase':a.phase,'branch':a.branch,'version':a.version,'parent_package_id':a.parent_package_id,'parent_manifest_sha256':a.parent_manifest_sha256,'origin_role':a.origin_role,'target_role':a.target_role,'branch_goal':'REPLACE_ME','terminal_condition':'REPLACE_ME','active_authority':[],'authority_exclusions':[],'status':'WORKING'})
    (dest/'PACKAGE.json').write_text(json.dumps(meta,indent=2)+'\n')
    anc=json.loads((dest/'ANCESTRY.json').read_text()); anc['package_id']=pid; anc['roots']=[{'root_id':rid,'kind':'repository','exact_path':str(Path(path).resolve()),'uri':None,'description':'declared at package creation'} for rid,path in a.root]; anc['ancestors']=[]
    (dest/'ANCESTRY.json').write_text(json.dumps(anc,indent=2)+'\n')
    clo=json.loads((dest/'CLOSEOUT.json').read_text()); clo['package_id']=pid; clo['status']='WORKING'; clo['closed_at']=None; clo['important_artifacts']=[]; clo['important_claims']=[]; clo['ancestor_disposition']=[]; clo['successor_start_here']=[]
    (dest/'CLOSEOUT.json').write_text(json.dumps(clo,indent=2)+'\n')
    (dest/'STATUS.md').write_text(f'# Working Package\n\n- Package ID: `{pid}`\n- Status: `WORKING`\n- No review verdict is implied.\n')
    h=(dest/'HANDOFF.md').read_text().replace('- Package ID: `REPLACE_ME`',f'- Package ID: `{pid}`',1).replace('- Origin role: `REPLACE_ME`',f'- Origin role: `{a.origin_role}`',1).replace('- Target role: `REPLACE_ME`',f'- Target role: `{a.target_role}`',1)
    (dest/'HANDOFF.md').write_text(h)
    print(dest); return 0
if __name__=='__main__': raise SystemExit(main())
