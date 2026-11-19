"""Synthetic case-block controls only: no SSH, model API or C execution."""
import copy
import hashlib
import io
from pathlib import Path
import tarfile
import tempfile
import unittest
import bp17_caseblock100_20261017_v1 as b


def fixtures():
    rows = [dict(anonymous_id='BP17-'+str(i).zfill(4), cluster_root='cluster-'+str(i),
                 private_case_id='private-'+str(i), cohort='exposed_exploratory' if i < 60 else 'previously_unexposed',
                 understanding_kind='native_behavior_projection') for i in range(100)]
    return rows


def block(row):
    result = []
    for g in b.r.GROUPS:
        for t in b.r.TASKS:
            request = dict(copy.deepcopy(b.r.PARAMS), messages=[dict(role='system', content='synthetic instructions'), dict(role='user', content='synthetic public material')])
            result.append(dict(job_id='original/'+row['anonymous_id']+'/'+g+'/'+t+'/1', protocol_id=b.r.ID,
                case_id=row['anonymous_id'], group=g, task=t, repetition=1, status='NOT_SENT', request=request, request_sha256=b.r.digest(request)))
    return result


def all_jobs(rows):
    return [j for row in rows for j in b.case_jobs(row, block(row))]


class Controls(unittest.TestCase):
    def test_exact_100_and_800(self):
        rows = fixtures(); self.assertTrue(b.validate_blocks(rows, all_jobs(rows)))

    def test_selection_deterministic(self):
        rows = fixtures(); self.assertEqual(b.select_cases(rows, []), b.select_cases(list(reversed(rows)), []))

    def test_confirm_prior_failed_request_excludes_whole_cluster(self):
        rows = fixtures(); rows.append(dict(rows[60], anonymous_id='BP17-1000', cluster_root='new-cluster'))
        chosen = b.select_cases(rows, [dict(case_id=rows[60]['anonymous_id'], status='transport_or_response_error')])
        self.assertNotIn(rows[60]['cluster_root'], {r['cluster_root'] for r in chosen})

    def test_confirmation_excludes_sibling(self):
        rows = fixtures(); rows.append(dict(rows[60], anonymous_id='BP17-1000'))
        with self.assertRaisesRegex(ValueError, 'insufficient'):
            b.select_cases(rows, [dict(case_id='BP17-1000')])

    def test_no_failed_case_substitution(self):
        with self.assertRaisesRegex(ValueError, 'insufficient'):
            b.select_cases(fixtures(), [dict(case_id='BP17-0060')])

    def test_unknown_exposure(self):
        with self.assertRaisesRegex(ValueError, 'known_prior'):
            b.select_cases(fixtures(), [dict(case_id='unknown')])

    def test_unique_source_case(self):
        rows = fixtures(); rows.append(rows[0])
        with self.assertRaisesRegex(ValueError, 'unique_source'):
            b.select_cases(rows, [])

    def test_no_cross_cohort_cluster(self):
        rows = fixtures(); rows[60]['cluster_root'] = rows[0]['cluster_root']
        with self.assertRaisesRegex(ValueError, 'disjoint'):
            b.select_cases(rows, [])

    def test_no_UB_pooling(self):
        rows = fixtures(); rows[0]['understanding_kind'] = 'uninitialized_read_classification'
        with self.assertRaisesRegex(ValueError, 'insufficient'):
            b.select_cases(rows, [])

    def test_original_request_bytes_unchanged(self):
        row = fixtures()[0]; originals = block(row); jobs = b.case_jobs(row, originals)
        source = {j['job_id']:j for j in originals}
        for job in jobs:
            self.assertEqual(job['request'], source[job['source_job_id']]['request'])
            self.assertEqual(job['request_sha256'], source[job['source_job_id']]['request_sha256'])
            self.assertNotEqual(job['job_id'], job['source_job_id'])

    def test_changed_source_request(self):
        row = fixtures()[0]; original = block(row); original[0]['request']['messages'][1]['content'] = 'tampered'
        with self.assertRaisesRegex(ValueError, 'serialized_request'):
            b.case_jobs(row, original)

    def test_not_eight_source_jobs(self):
        row = fixtures()[0]
        with self.assertRaisesRegex(ValueError, 'eight_source'):
            b.case_jobs(row, block(row)[:-1])

    def test_missing_group(self):
        row = fixtures()[0]; original = block(row); original[-1] = original[0]
        with self.assertRaisesRegex(ValueError, 'complete_four'):
            b.case_jobs(row, original)

    def test_cross_case_job(self):
        row = fixtures()[0]; original = block(row); original[0]['case_id'] = 'another'
        with self.assertRaisesRegex(ValueError, 'source_case'):
            b.case_jobs(row, original)

    def test_block_order_deterministic(self):
        row = fixtures()[0]; original = block(row)
        self.assertEqual(b.case_jobs(row, original), b.case_jobs(row, list(reversed(original))))

    def test_case_not_complete_cannot_advance(self):
        jobs = b.case_jobs(fixtures()[0], block(fixtures()[0]))
        with self.assertRaisesRegex(ValueError, 'case_must_complete'):
            b.block_gate(jobs, {j['job_id']:None for j in jobs[:-1]})

    def test_complete_case_can_advance(self):
        jobs = b.case_jobs(fixtures()[0], block(fixtures()[0])); b.block_gate(jobs, {j['job_id']:None for j in jobs})

    def test_no_mixed_case_wave(self):
        rows = fixtures(); jobs = all_jobs(rows); jobs[7], jobs[8] = jobs[8], jobs[7]
        with self.assertRaisesRegex(ValueError, 'contiguous'):
            b.validate_blocks(rows, jobs)

    def test_duplicate_job(self):
        rows = fixtures(); jobs = all_jobs(rows); jobs[-1] = jobs[0]
        with self.assertRaisesRegex(ValueError, '800_unique'):
            b.validate_blocks(rows, jobs)

    def test_duplicate_case(self):
        rows = fixtures(); rows[-1] = rows[0]
        with self.assertRaisesRegex(ValueError, '100_unique'):
            b.validate_blocks(rows, all_jobs(rows))

    def test_first_identity_gate_is_planned_task(self):
        jobs = all_jobs(fixtures())[:8]; waves = b.waves(jobs, True)
        self.assertEqual([len(w) for w in waves], [1, 3, 4])
        self.assertEqual([j for wave in waves for j in wave], jobs)

    def test_later_case_4_plus_4(self):
        jobs = all_jobs(fixtures())[:8]; self.assertEqual([len(w) for w in b.waves(jobs)], [4, 4])

    def test_new_pin_accepted(self):
        value = dict(b.PIN, status='completed', response_id='synthetic'); self.assertEqual(b.r.identity(value, b.PIN), b.PIN)

    def test_old_pin_refused(self):
        value = dict(b.PIN, status='completed', response_id='synthetic', system_fingerprint='aeb56401ca74e127821c4f9126dcb669')
        with self.assertRaisesRegex(ValueError, 'model_identity_changed'): b.r.identity(value, b.PIN)

    def test_another_new_pin_refused(self):
        value = dict(b.PIN, status='completed', response_id='synthetic', system_fingerprint='another')
        with self.assertRaisesRegex(ValueError, 'model_identity_changed'): b.r.identity(value, b.PIN)

    def test_API_failure_not_scored(self):
        with self.assertRaisesRegex(ValueError, 'API_failure'):
            b.r.identity(dict(status='transport_or_response_error'), b.PIN)

    def test_empty_fingerprint_refused(self):
        with self.assertRaisesRegex(ValueError, 'missing_model_fingerprint'):
            b.r.identity(dict(status='completed', response_id='synthetic', model_returned='deepseek-flash', system_fingerprint=''), b.PIN)

    def test_source_cohort_counts_unchanged(self):
        rows = fixtures(); rows[0]['cohort'] = 'previously_unexposed'
        with self.assertRaisesRegex(ValueError, 'cohort_counts'):
            b.validate_blocks(rows, all_jobs(rows))

    def test_new_job_id_required(self):
        rows = fixtures(); jobs = all_jobs(rows); jobs[0]['protocol_id'] = b.r.ID
        with self.assertRaisesRegex(ValueError, 'new_batch_job_identity'):
            b.validate_blocks(rows, jobs)

    def test_archive_streaming_multi_chunk(self):
        data = b'x'*(2*1024**2+31)
        with tempfile.TemporaryDirectory(dir=str(b.HERE)) as temp:
            path = Path(temp)/'small.tar.gz'
            with tarfile.open(path, 'w:gz') as tar:
                info = tarfile.TarInfo('record'); info.size = len(data); tar.addfile(info, io.BytesIO(data))
            b.verify_archive(path, {'record':hashlib.sha256(data).hexdigest()})
            with self.assertRaisesRegex(ValueError, 'archive_member_sha'):
                b.verify_archive(path, {'record':'0'*64})

    def test_archive_missing_member_refused(self):
        with tempfile.TemporaryDirectory(dir=str(b.HERE)) as temp:
            path = Path(temp)/'empty.tar.gz'
            with tarfile.open(path, 'w:gz'): pass
            with self.assertRaisesRegex(ValueError, 'archive_all_members'):
                b.verify_archive(path, {'missing':'0'*64})


if __name__ == '__main__': unittest.main()
