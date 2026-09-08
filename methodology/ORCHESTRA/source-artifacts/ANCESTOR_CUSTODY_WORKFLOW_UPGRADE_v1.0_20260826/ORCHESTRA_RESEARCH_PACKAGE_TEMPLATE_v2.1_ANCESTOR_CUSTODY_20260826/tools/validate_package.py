#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

REQUIRED={
'README.md','PACKAGE.json','WORKFLOW.md','AUTHORITY.md','HANDOFF.md','CLAIMS.md','FINDINGS.md','LAB_JOURNAL.md','CHANGELOG.md',
'ANCESTRY.json','ANCESTRY.md','CLOSEOUT.json','CLOSEOUT.md',
'inputs/README.md','src/README.md','notebooks/README.md','figures/README.md','output_data/README.md','source_maps/README.md','trace_logs/README.md','lean/README.md','review/README.md',
'tools/build_manifest.py','tools/validate_package.py','tools/finalize_package.py','tools/add_ancestor.py','tools/prepare_closeout.py','tools/inherit_parent_ancestry.py'
}
ID_RE=re.compile(r'^p(?P<p>\d+)-b(?P<b>\d+)-v(?P<v>\d+)$')
PLACEHOLDER_RE=re.compile(r'REPLACE_ME|p#-b#-v#')
IMAGE_SUFFIXES={'.png','.jpg','.jpeg','.svg','.pdf'}
ALLOWED_DISPOSITION={'CONTROLLING','STILL_RELEVANT','SUPERSEDED_BY_THIS_PACKAGE','HISTORICAL_ONLY','NO_LONGER_RELEVANT'}

def digest(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def load_json(path:Path,errors:list[str]):
    try:return json.loads(path.read_text(encoding='utf-8'))
    except Exception as e: errors.append(f'invalid {path.name}: {e}'); return {}

def check_notebook(path:Path,errors:list[str],strict:bool)->None:
    nb=load_json(path,errors)
    if not nb:return
    code=[c for c in nb.get('cells',[]) if c.get('cell_type')=='code']; md=[c for c in nb.get('cells',[]) if c.get('cell_type')=='markdown']
    if md: errors.append(f'notebook contains markdown/infrastructure cells: {path}')
    if not code: errors.append(f'notebook contains no claim cells: {path}')
    for i,c in enumerate(code,1):
        s=''.join(c.get('source',[])); low=s.lower()
        for t in ('threshold','negative_control','pass','fail','plt.show'):
            if t not in low: errors.append(f'{path} cell {i} missing {t}')
        if any(t in low for t in ('open(','to_csv(','savefig(','write_text(','write_bytes(','np.save(')): errors.append(f'{path} cell {i} appears to perform file I/O')
        if strict:
            if PLACEHOLDER_RE.search(s) or 'NotImplementedError' in s: errors.append(f'{path} cell {i} retains placeholders')
            if c.get('execution_count') is None: errors.append(f'{path} cell {i} is not executed')
            outs=c.get('outputs',[]); fig=any('image/png' in o.get('data',{}) or 'image/svg+xml' in o.get('data',{}) for o in outs)
            if not fig: errors.append(f'{path} cell {i} has no rendered figure')
            txt='\n'.join(''.join(o.get('text',[]))+''.join(o.get('data',{}).get('text/plain',[])) for o in outs)
            if 'PASS' not in txt and 'FAIL' not in txt: errors.append(f'{path} cell {i} output has no PASS/FAIL')

def check_ancestry(root:Path,metadata:dict,errors:list[str],strict:bool)->set[str]:
    data=load_json(root/'ANCESTRY.json',errors)
    if not data:return set()
    if data.get('package_id')!=metadata.get('package_id') and metadata.get('package_type')!='orchestra_research_package_template': errors.append('ANCESTRY.json package_id differs from PACKAGE.json')
    roots=data.get('roots',[]); ancestors=data.get('ancestors',[])
    if not roots: errors.append('ANCESTRY.json has no declared roots')
    rootmap={}
    for r in roots:
        rid=r.get('root_id'); ep=r.get('exact_path'); uri=r.get('uri')
        if not rid or rid in rootmap: errors.append(f'invalid/duplicate root_id: {rid!r}')
        else: rootmap[rid]=r
        if not ep and not uri: errors.append(f'root {rid} has neither exact_path nor uri')
        if strict and ep and PLACEHOLDER_RE.search(str(ep)): errors.append(f'root {rid} retains placeholder exact_path')
    ids=[]
    for a in ancestors:
        aid=a.get('ancestor_id'); ids.append(aid)
        if not aid: errors.append('ancestor missing ancestor_id'); continue
        if a.get('depth') is None or int(a.get('depth',0))<1: errors.append(f'{aid} has invalid depth')
        rid=a.get('root_id'); rel=a.get('relative_path'); uri=a.get('uri')
        if not uri and not (rid and rel): errors.append(f'{aid} lacks exact root+relative_path or uri')
        if rid and rid not in rootmap: errors.append(f'{aid} references unknown root_id {rid}')
        if strict:
            for key in ('kind','relation','scope','why_relevant','current_relevance'):
                if not a.get(key) or PLACEHOLDER_RE.search(str(a.get(key))): errors.append(f'{aid} missing/placeholder {key}')
            if rel and PLACEHOLDER_RE.search(str(rel)): errors.append(f'{aid} retains placeholder relative_path')
            if uri and PLACEHOLDER_RE.search(str(uri)): errors.append(f'{aid} retains placeholder uri')
        if rid and rel and rootmap.get(rid,{}).get('exact_path'):
            target=Path(rootmap[rid]['exact_path'])/rel
            if strict and not target.exists(): errors.append(f'{aid} exact path does not exist: {target}')
            if target.is_file() and a.get('sha256') and not PLACEHOLDER_RE.search(str(a['sha256'])):
                if digest(target)!=a['sha256']: errors.append(f'{aid} SHA-256 mismatch: {target}')
            if a.get('kind')=='package' and target.is_dir() and a.get('manifest_sha256'):
                mp=target/'MANIFEST.json'
                if strict and not mp.is_file(): errors.append(f'{aid} package ancestor has no MANIFEST.json: {target}')
                elif mp.is_file() and digest(mp)!=a['manifest_sha256']: errors.append(f'{aid} manifest SHA-256 mismatch')
    if len(ids)!=len(set(ids)): errors.append('duplicate ancestor_id in ANCESTRY.json')
    if strict and not ancestors: errors.append('strict package has no material ancestors')
    return {x for x in ids if x}

def check_closeout(root:Path,metadata:dict,ancestor_ids:set[str],errors:list[str],strict:bool)->None:
    data=load_json(root/'CLOSEOUT.json',errors)
    if not data:return
    if data.get('package_id')!=metadata.get('package_id') and metadata.get('package_type')!='orchestra_research_package_template': errors.append('CLOSEOUT.json package_id differs from PACKAGE.json')
    if not strict:return
    if data.get('status') not in {'READY_TO_CLOSE','CLOSED'}: errors.append('CLOSEOUT.json status must be READY_TO_CLOSE or CLOSED for strict finalization')
    if not data.get('outcome') or PLACEHOLDER_RE.search(str(data.get('outcome'))): errors.append('CLOSEOUT.json outcome is missing/placeholder')
    arts=data.get('important_artifacts',[])
    if not arts: errors.append('CLOSEOUT.json has no important_artifacts')
    for i,a in enumerate(arts,1):
        p=a.get('path'); role=a.get('role'); why=a.get('why_important')
        if not p or PLACEHOLDER_RE.search(str(p)): errors.append(f'closeout artifact {i} missing/placeholder path'); continue
        fp=root/p
        if not fp.is_file(): errors.append(f'closeout important artifact does not exist: {p}')
        else:
            sha=a.get('sha256')
            if not sha or PLACEHOLDER_RE.search(str(sha)): errors.append(f'closeout important artifact lacks SHA-256: {p}')
            elif digest(fp)!=sha: errors.append(f'closeout important artifact SHA-256 mismatch: {p}')
        if not role or not why or PLACEHOLDER_RE.search(str(why)): errors.append(f'closeout important artifact incomplete: {p}')
    rows=data.get('ancestor_disposition',[]); row_ids=[r.get('ancestor_id') for r in rows]
    if set(row_ids)!=ancestor_ids: errors.append(f'closeout ancestor disposition must match ancestry exactly; missing={sorted(ancestor_ids-set(row_ids))} extra={sorted(set(row_ids)-ancestor_ids)}')
    if len(row_ids)!=len(set(row_ids)): errors.append('duplicate ancestor disposition')
    for r in rows:
        aid=r.get('ancestor_id'); disp=r.get('relevance_after_close')
        if disp not in ALLOWED_DISPOSITION: errors.append(f'{aid} invalid relevance_after_close: {disp!r}')
        for key in ('why','successor_instruction'):
            if not r.get(key) or PLACEHOLDER_RE.search(str(r.get(key))): errors.append(f'{aid} closeout disposition missing/placeholder {key}')
    start=data.get('successor_start_here',[])
    if not start: errors.append('CLOSEOUT.json successor_start_here is empty')
    for ref in start:
        if not ref or PLACEHOLDER_RE.search(str(ref)): errors.append('successor_start_here contains placeholder')

def check_manifest(root:Path,errors:list[str])->None:
    mp=root/'MANIFEST.json'; sp=root/'SHA256SUMS'
    if not mp.exists() or not sp.exists(): errors.append('MANIFEST.json and SHA256SUMS are required'); return
    m=load_json(mp,errors); listed={r.get('path'):r for r in m.get('files',[])}; actual={}
    for p in sorted(root.rglob('*')):
        if not p.is_file(): continue
        rel=p.relative_to(root).as_posix()
        if rel in {'MANIFEST.json','SHA256SUMS'} or '.git' in p.parts or '__pycache__' in p.parts: continue
        actual[rel]=p
    for rel in sorted(set(listed)-set(actual)): errors.append(f'manifest lists missing file: {rel}')
    for rel in sorted(set(actual)-set(listed)): errors.append(f'manifest omits file: {rel}')
    for rel,p in actual.items():
        r=listed.get(rel)
        if r and (r.get('size')!=p.stat().st_size or r.get('sha256')!=digest(p)): errors.append(f'manifest mismatch: {rel}')
    sums={}
    for line in sp.read_text().splitlines():
        if line.strip():
            c,rel=line.split('  ',1); sums[rel]=c
    if sums!={rel:r.get('sha256') for rel,r in listed.items()}: errors.append('SHA256SUMS differs from MANIFEST.json')

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument('root',type=Path,nargs='?',default=Path('.')); p.add_argument('--strict',action='store_true'); p.add_argument('--require-manifest',action='store_true'); a=p.parse_args()
    root=a.root.resolve(); errors=[]
    for rel in sorted(REQUIRED):
        if not (root/rel).is_file(): errors.append(f'missing required file: {rel}')
    meta=load_json(root/'PACKAGE.json',errors); ptype=meta.get('package_type'); template=ptype=='orchestra_research_package_template'
    if ptype not in {'orchestra_research_package_template','orchestra_research_package'}: errors.append(f'invalid package_type: {ptype!r}')
    if a.strict and template: errors.append('strict validation applies to active packages')
    if not template:
        m=ID_RE.fullmatch(str(meta.get('package_id','')))
        if not m: errors.append('active package_id must match p<phase>-b<branch>-v<version>')
        else:
            expected=(int(m.group('p')),int(m.group('b')),int(m.group('v'))); actual=(meta.get('phase'),meta.get('branch'),meta.get('version'))
            if actual!=expected: errors.append(f'phase/branch/version {actual} disagree with package_id {expected}')
    for path in root.rglob('*'):
        if path.is_file() and path.stat().st_size<=1: errors.append(f'empty or one-byte placeholder: {path.relative_to(root)}')
        if path.suffix=='.ipynb': check_notebook(path,errors,a.strict)
    ancestor_ids=check_ancestry(root,meta,errors,a.strict)
    check_closeout(root,meta,ancestor_ids,errors,a.strict)
    if a.strict:
        for rel in ('PACKAGE.json','AUTHORITY.md','HANDOFF.md','CLAIMS.md','FINDINGS.md','ANCESTRY.md','CLOSEOUT.md'):
            if PLACEHOLDER_RE.search((root/rel).read_text()): errors.append(f'placeholder marker remains in {rel}')
        if meta.get('branch_goal') in {None,'','REPLACE_ME'}: errors.append('branch_goal is not declared')
        if meta.get('terminal_condition') in {None,'','REPLACE_ME'}: errors.append('terminal_condition is not declared')
        if not meta.get('active_authority'): errors.append('active_authority is empty')
        figs=[x for x in (root/'figures').iterdir() if x.is_file() and x.suffix.lower() in IMAGE_SUFFIXES]
        if not figs: errors.append('strict Operator package requires a top-level decision figure')
        if not re.search(r'\| C\d{3,} \|',(root/'CLAIMS.md').read_text()): errors.append('CLAIMS.md contains no stable claim row')
        check_manifest(root,errors)
    elif a.require_manifest or (root/'MANIFEST.json').exists() or (root/'SHA256SUMS').exists(): check_manifest(root,errors)
    if errors:
        print('FAIL'); [print(f'- {e}') for e in errors]; return 1
    print('PASS'); print(f'- package_type: {ptype}'); print(f'- strict: {a.strict}'); print(f'- ancestors: {len(ancestor_ids)}'); return 0
if __name__=='__main__': raise SystemExit(main())
