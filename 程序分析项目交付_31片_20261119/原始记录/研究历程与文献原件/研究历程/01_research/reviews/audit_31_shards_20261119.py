"""Recount the user-selected 31 host archive mappings without running experiments."""
from collections import Counter, defaultdict
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
R=ROOT/'03_experiments/results/bp17_remainder_2026-10-17'
P=R/'batch_v1'
files=sorted((P/'sealed_shards').glob('shard_*.json'))
docs=[json.loads(p.read_text(encoding='utf-8')) for p in files]
docs.append(json.loads((R/'continuation_20261021_v5/recovered_shard8.json').read_text(encoding='utf-8')))
ids=[c for d in docs for c in d['case_ids']]
assert len(docs)==31 and len(ids)==len(set(ids))
segments=json.loads((R/'final_case_segments_20261118_v1.json').read_text(encoding='utf-8'))
results=defaultdict(lambda:defaultdict(Counter)); groups=Counter(); kinds=Counter(); keys=Counter(); pairs=defaultdict(Counter)
for case in ids:
    receipt=json.loads((P/'case_receipts'/f'{case}.json').read_text(encoding='utf-8'))
    assert receipt['case_id']==case
    segment=segments.get(case,'unknown'); groups[segment]+=1
    case_results={}
    for row in receipt['rows']:
        task=row['task']; group=row['group']; keys[(case,group,task)]+=1
        c=results[segment][f'{task}_{group}']; c['rows']+=1
        if task=='understanding':
            kinds[row.get('understanding_kind','unknown')]+=1
            score=row.get('score') or {}; c['valid']+=bool(score.get('valid'))
            correct=bool(score.get('valid') and score.get('total',0)>0 and score.get('correct')==score.get('total'))
            c['whole_correct']+=correct
            sub=results[segment][f"{row.get('understanding_kind','unknown')}_{group}"]
            sub['rows']+=1; sub['valid']+=bool(score.get('valid')); sub['whole_correct']+=correct
            case_results[(task,group)]=correct
        else:
            c['repair_pass']+=row.get('repair_pass') is True
            c['heldout_pass']+=row.get('heldout_pass') is True
            c['all_tests_passed']+=row.get('status')=='all_tests_passed'
            c['test_failed']+=row.get('status')=='test_failed'
            c['other_status']+=row.get('status') not in ('all_tests_passed','test_failed')
            case_results[(task,group)]=row.get('status')=='all_tests_passed'
    for task in ('repair','understanding'):
        for a,b in [('BP1','BP0'),('BP2','BP1'),('BP3','BP2')]:
            va=case_results.get((task,a),False); vb=case_results.get((task,b),False)
            pairs[(segment,task,a+'-'+b)][('both' if va and vb else 'a_only' if va else 'b_only' if vb else 'neither')]+=1
assert all(v==1 for v in keys.values()) and len(keys)==len(ids)*8
print(json.dumps({'scope':'31 local receipt mappings, not archive payload audit','cases':len(ids),'slots':len(keys),'segments':groups,'understanding_kind_rows':kinds,'results':results,'paired':{'|'.join(k):v for k,v in pairs.items()},'exclusion_1477': 'BP17-1477' not in ids,'mixed_0431': 'BP17-0431' in ids,'indices':sorted(d['index'] for d in docs)},ensure_ascii=False,indent=2))
