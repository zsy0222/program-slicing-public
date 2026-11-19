"""Synthetic control tests: no API, SSH or candidate execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch
import bp17_caseblocked_remainder_20261017_v1 as b


def rows():
    return [dict(anonymous_id='BP17-'+str(i).zfill(4),cluster_root='c'+str(i//2),cohort='exposed_exploratory',
        understanding_kind='native_behavior_projection' if i<2 else 'uninitialized_read_classification') for i in range(3)]


def source(row):
    values=[]
    for g in b.r.GROUPS:
        for t in b.r.TASKS:
            request=copy.deepcopy(b.r.PARAMS);request['messages']=[dict(role='system',content='synthetic'),dict(role='user',content='public only')]
            values.append(dict(job_id='/'.join((b.r.ID,row['anonymous_id'],g,t,'1')),protocol_id=b.r.ID,case_id=row['anonymous_id'],
                group=g,task=t,repetition=1,status='NOT_SENT',request=request,request_sha256=b.r.digest(request)))
    return values


def jobs(rs):return [b.metadata(j) for row in rs for j in b.case_jobs(row,source(row))]


class Controls(unittest.TestCase):
    def test_exact_scope(self):self.assertTrue(b.validate_blocks(rows(),jobs(rows()),set(),3))
    def test_sibling_clusters_allowed(self):self.assertEqual(rows()[0]['cluster_root'],rows()[1]['cluster_root']);self.assertTrue(b.validate_blocks(rows(),jobs(rows()),set(),3))
    def test_prefix_never_reissued(self):
        with self.assertRaisesRegex(ValueError,'no_prefix_reissue'):b.validate_blocks(rows(),jobs(rows()),{'BP17-0000'},3)
    def test_duplicate_case(self):
        rs=rows();rs[-1]=rs[0]
        with self.assertRaisesRegex(ValueError,'unique_remaining'):b.validate_blocks(rs,jobs(rs),set(),3)
    def test_duplicate_job(self):
        js=jobs(rows());js[-1]=js[0]
        with self.assertRaisesRegex(ValueError,'finite_unique'):b.validate_blocks(rows(),js,set(),3)
    def test_mixed_block(self):
        js=jobs(rows());js[7],js[8]=js[8],js[7]
        with self.assertRaisesRegex(ValueError,'complete_contiguous'):b.validate_blocks(rows(),js,set(),3)
    def test_wrong_execution_identity(self):
        js=jobs(rows());js[0]['protocol_id']='old'
        with self.assertRaisesRegex(ValueError,'new_job_identity'):b.validate_blocks(rows(),js,set(),3)
    def test_original_scientific_identity_required(self):
        js=jobs(rows());js[0]['scientific_protocol_id']='other'
        with self.assertRaisesRegex(ValueError,'scientific_protocol'):b.validate_blocks(rows(),js,set(),3)
    def test_U1_retained_not_pooled(self):self.assertEqual(rows()[2]['understanding_kind'],'uninitialized_read_classification');self.assertTrue(b.validate_blocks(rows(),jobs(rows()),set(),3))
    def test_unknown_kind(self):
        rs=rows();rs[0]['understanding_kind']='invented'
        with self.assertRaisesRegex(ValueError,'frozen_cohort'):b.validate_blocks(rs,jobs(rs),set(),3)
    def test_request_not_embedded_in_guest_metadata(self):self.assertNotIn('request',jobs(rows())[0])
    def test_actual_request_unchanged(self):
        row=rows()[0];original=source(row);lookup={v['job_id']:v for v in original}
        for j in b.case_jobs(row,original):self.assertEqual(j['request'],lookup[j['source_job_id']]['request'])
    def test_request_tamper(self):
        row=rows()[0];values=source(row);values[0]['request']['messages'][1]['content']='changed'
        with self.assertRaisesRegex(ValueError,'serialized_request'):b.case_jobs(row,values)
    def test_parameters_tamper(self):
        row=rows()[0];values=source(row);values[0]['request']['temperature']=1;values[0]['request_sha256']=b.r.digest(values[0]['request'])
        with self.assertRaisesRegex(ValueError,'parameters_changed'):b.case_jobs(row,values)
    def test_wrong_case_request(self):
        row=rows()[0];values=source(row);values[0]['case_id']='other'
        with self.assertRaisesRegex(ValueError,'source_case_binding'):b.case_jobs(row,values)
    def test_eight_source_jobs_required(self):
        with self.assertRaisesRegex(ValueError,'eight_source'):b.case_jobs(rows()[0],source(rows()[0])[:-1])
    def test_all_four_groups_required(self):
        row=rows()[0];values=source(row);values[-1]=values[0]
        with self.assertRaisesRegex(ValueError,'complete_four'):b.case_jobs(row,values)
    def test_stable_within_case_order(self):
        row=rows()[0];self.assertEqual(b.case_jobs(row,source(row)),b.case_jobs(row,list(reversed(source(row)))))
    def test_identity_gate_1_3_4(self):self.assertEqual([len(v) for v in b.base.waves(jobs(rows())[:8],True)],[1,3,4])
    def test_subsequent_4_4(self):self.assertEqual([len(v) for v in b.base.waves(jobs(rows())[:8])],[4,4])
    def test_incomplete_case_cannot_advance(self):
        js=jobs(rows())[:8]
        with self.assertRaisesRegex(ValueError,'case_must_complete'):b.base.block_gate(js,{j['job_id']:None for j in js[:-1]})
    def test_old_pin_refused(self):
        with self.assertRaisesRegex(ValueError,'model_identity_changed'):b.r.identity(dict(status='completed',model_returned='deepseek-flash',system_fingerprint='old',response_id='x'),b.PIN)
    def test_current_pin_required(self):self.assertEqual(b.r.identity(dict(status='completed',response_id='x',**b.PIN),b.PIN),b.PIN)
    def test_missing_pin_refused(self):
        with self.assertRaisesRegex(ValueError,'missing_model_fingerprint'):b.r.identity(dict(status='completed',response_id='x',model_returned='deepseek-flash',system_fingerprint=''),b.PIN)
    def test_api_failure_not_scored(self):
        with self.assertRaisesRegex(ValueError,'API_failure'):b.r.identity(dict(status='transport_or_response_error'),b.PIN)
    def test_finite_cap_no_extra_reservation(self):
        js=jobs(rows())[:1]
        with patch.object(b,'CALLS',1):
            with self.assertRaisesRegex(ValueError,'finite_unique'):b.reserve(Path('.'),js,{'already'})
    def test_duplicate_no_extra_reservation(self):
        js=jobs(rows())[:1]
        with self.assertRaisesRegex(ValueError,'finite_unique'):b.reserve(Path('.'),js,{js[0]['job_id']})
    def test_durable_new_cumulative_start(self):
        with tempfile.TemporaryDirectory(dir=b.HERE) as temp:
            root=Path(temp);js=jobs(rows())[:1];reserved=set();b.reserve(root,js,reserved)
            v=json.loads((root/'attempt_ledger.jsonl').read_text());self.assertEqual(v['cumulative_ordinal'],6494);self.assertEqual(reserved,{js[0]['job_id']})
    def test_pathlib_gzip_compatibility_roundtrip(self):
        with tempfile.TemporaryDirectory(dir=b.HERE) as temp:
            root=Path(temp);(root/'record').write_bytes(b'X'*(2*1024**2+7));files={'record':b.r.sha(root/'record')};path=root/'records.tar.gz'
            b.stream_pack(path,root,files);self.assertEqual(b.check_archive(path,files),1)
    def test_wrong_archive_hash_refused(self):
        with tempfile.TemporaryDirectory(dir=b.HERE) as temp:
            root=Path(temp);(root/'record').write_bytes(b'X');path=root/'r.tar.gz';b.stream_pack(path,root,{'record':b.r.sha(root/'record')})
            with self.assertRaisesRegex(ValueError,'SHA256'):b.check_archive(path,{'record':'0'*64})
    def test_archive_missing_member_refused(self):
        with tempfile.TemporaryDirectory(dir=b.HERE) as temp:
            path=Path(temp)/'r.tar.gz'
            with tarfile.open(str(path),'w:gz'):pass
            with self.assertRaisesRegex(ValueError,'all_manifest'):b.check_archive(path,{'missing':'0'*64})
    def test_no_model_key_in_guest_contract(self):self.assertEqual(b.REMOTE_TOOLS,'/home/vboxuser/bp17_remainder_tools_20261017_v1')
    def test_counts_and_budget(self):self.assertEqual((b.PAIRS,b.CALLS,b.CUMULATIVE_BEFORE+b.CALLS),(3158,25264,31757))


if __name__=='__main__':unittest.main()
