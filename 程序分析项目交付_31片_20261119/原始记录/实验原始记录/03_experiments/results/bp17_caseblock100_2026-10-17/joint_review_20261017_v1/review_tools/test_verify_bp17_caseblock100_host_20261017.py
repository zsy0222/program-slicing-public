import copy
import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
import verify_bp17_caseblock100_host_20261017 as a

HERE=Path(__file__).resolve().parent
TRUTH=dict(exit_class='normal_exit',stdout_bytes=2,stdout_prefix_hex='310a')


def answer(value=None):return json.dumps({'answers':[dict(id='P1',**(TRUTH if value is None else value))]})


class HostAuditControls(unittest.TestCase):
    def test_exact_P1(self):self.assertEqual(a.score_p1(answer(),TRUTH),dict(valid=True,correct=1,total=1,components_correct=3,components_total=3))
    def test_one_component_wrong(self):
        value=dict(TRUTH,exit_class='runtime_error');score=a.score_p1(answer(value),TRUTH)
        self.assertTrue(score['valid']);self.assertEqual(score['correct'],0);self.assertEqual(score['components_correct'],2)
    def test_not_JSON(self):self.assertFalse(a.score_p1('text',TRUTH)['valid'])
    def test_duplicate_JSON_key(self):self.assertFalse(a.score_p1('{"answers":[],"answers":[]}',TRUTH)['valid'])
    def test_bool_not_integer(self):self.assertFalse(a.score_p1(answer(dict(TRUTH,stdout_bytes=True)),TRUTH)['valid'])
    def test_uppercase_hex_rejected(self):self.assertFalse(a.score_p1(answer(dict(TRUTH,stdout_prefix_hex='310A')),TRUTH)['valid'])
    def test_bad_prefix_length(self):self.assertFalse(a.score_p1(answer(dict(TRUTH,stdout_prefix_hex='31')),TRUTH)['valid'])
    def test_wrong_question_id(self):self.assertFalse(a.score_p1(answer().replace('P1','U1'),TRUTH)['valid'])
    def test_extra_field(self):
        value=json.loads(answer());value['answers'][0]['explanation']='not allowed';self.assertFalse(a.score_p1(json.dumps(value),TRUTH)['valid'])
    def test_scope_unchanged(self):a.scope('#include <stdio.h>\nint main(){return 0;}','#include <stdio.h>\nint main(){return 0;}')
    def test_scope_directive_change(self):
        with self.assertRaisesRegex(ValueError,'preprocessor'):a.scope('#include <stdlib.h>\nint main(){return 0;}','#include <stdio.h>\nint main(){return 0;}')
    def test_scope_new_external(self):
        with self.assertRaisesRegex(ValueError,'new_external'):a.scope('int main(){system("x");}','int main(){return 0;}')
    def test_runtime_error_not_pass(self):self.assertEqual(a.observation_status(dict(timeout=False,output_limited=False,returncode=1),True),'runtime_error')
    def test_timeout_not_pass(self):self.assertEqual(a.observation_status(dict(timeout=True,output_limited=False,returncode=-9),True),'timeout')
    def test_output_limit_not_pass(self):self.assertEqual(a.observation_status(dict(timeout=False,output_limited=True,returncode=0),True),'output_limited')
    def test_mismatch_not_pass(self):self.assertEqual(a.observation_status(dict(timeout=False,output_limited=False,returncode=0),False),'output_mismatch')
    def test_streaming_archive(self):
        with tempfile.TemporaryDirectory(dir=HERE) as temp:
            root=Path(temp);data=b'X'*(2*1024**2+11);archive=root/'archive.tar.gz'
            with tarfile.open(archive,'w:gz') as tar:
                info=tarfile.TarInfo('folder/data.bin');info.size=len(data);tar.addfile(info,io.BytesIO(data))
            self.assertEqual(a.unpack(archive,{'folder/data.bin':hashlib.sha256(data).hexdigest()},root/'out'),1)
    def test_path_escape_refused(self):
        with tempfile.TemporaryDirectory(dir=HERE) as temp:
            root=Path(temp);archive=root/'archive.tar.gz'
            with tarfile.open(archive,'w:gz') as tar:
                info=tarfile.TarInfo('../escape');info.size=1;tar.addfile(info,io.BytesIO(b'x'))
            with self.assertRaisesRegex(ValueError,'safe_unique'):a.unpack(archive,{'../escape':hashlib.sha256(b'x').hexdigest()},root/'out')
            self.assertFalse((root/'escape').exists())
    def test_sha_mismatch_refused(self):
        with tempfile.TemporaryDirectory(dir=HERE) as temp:
            root=Path(temp);archive=root/'archive.tar.gz'
            with tarfile.open(archive,'w:gz') as tar:
                info=tarfile.TarInfo('data');info.size=1;tar.addfile(info,io.BytesIO(b'x'))
            with self.assertRaisesRegex(ValueError,'archive_member_bytes'):a.unpack(archive,{'data':'0'*64},root/'out')


if __name__=='__main__':unittest.main()
