"""Package source records without altering originals or connecting to the guest."""
from pathlib import Path
import hashlib, json, time, zipfile

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'01_research/reviews/项目交付_31片_20261119/原始记录'
BP=ROOT/'03_experiments/results/bp17_remainder_2026-10-17'
EARLY=ROOT/'03_experiments/results/bp17_caseblock100_2026-10-17'

def files_below(base):
    if base.is_file():
        yield base
    elif base.is_dir():
        yield from (p for p in base.rglob('*') if p.is_file() and not p.is_symlink())

def package(name, roots):
    target=OUT/name
    if target.exists(): raise FileExistsError(target)
    seen=set(); total=0
    with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=1,allowZip64=True) as z:
        for root in roots:
            for f in files_below(root):
                if OUT in f.parents: continue
                rel=f.relative_to(ROOT).as_posix()
                if rel not in seen:
                    z.write(f,rel); seen.add(rel); total+=f.stat().st_size
                    if len(seen)%20000==0: print(name,len(seen),flush=True)
    digest=hashlib.sha256()
    with target.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): digest.update(block)
    print(json.dumps({'archive':name,'files':len(seen),'original_bytes':total,'zip_bytes':target.stat().st_size,'sha256':digest.hexdigest()},ensure_ascii=False),flush=True)

package('实验原始记录.zip',[
    BP/'batch_v1', BP/'continuation_20261021_v5/recovered_shard8.json',
    *BP.glob('final_*20261118_v1.*'), EARLY/'batch_v1', EARLY/'joint_review_20261017_v1'
])
package('研究历程与文献原件.zip',[
    ROOT/'90_local_only/legacy/early_framework_documents',
    ROOT/'90_local_only/literature_sources/sources/paper_list.docx',
    ROOT/'paper/matrix/literature_matrix.csv',ROOT/'paper/matrix/evidence_map.csv',
    ROOT/'paper/notes',ROOT/'01_research/reviews',ROOT/'01_research/workflow'
])
