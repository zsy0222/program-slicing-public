"""Local tests for V2 job privacy, evidence contract, and patch validation."""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from validate_v2_patches import apply_one_line_replacement, compile_and_run
from verify_v2_contract import verify


PIPELINE = Path(__file__).resolve().parent
EXPERIMENT_ROOT = PIPELINE.parents[1]
JOB_PATH = EXPERIMENT_ROOT / "outputs" / "v2_jobs_2026-08-23" / "P_V2b_ei_audited.jsonl"
SEED_DIR = EXPERIMENT_ROOT / "benchmarks" / "seeded_faults"


class V2WorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.jobs = [json.loads(line) for line in JOB_PATH.read_text(encoding="utf-8").splitlines()]
        cls.jobs_by_case = {job["user"]["case_id"]: job for job in cls.jobs}

    def test_jobs_do_not_leak_oracle_fields(self) -> None:
        serialized = json.dumps(self.jobs, ensure_ascii=False)
        for forbidden in ("correct_reference", "ground_truth", "faulty_source_line", "z = z + 1"):
            self.assertNotIn(forbidden, serialized)

    def test_evidence_contract_accepts_grounded_role_answer(self) -> None:
        job = self.jobs_by_case["Seed03_initial_value_v2"]
        response = {
            "candidates": [
                {
                    "source_line": 3,
                    "role": "fault_origin",
                    "proposed_replacement": "int z = 12;",
                    "reason": "The initial state participates in the error-reaching path.",
                    "confidence": 0.6,
                    "evidence_refs": ["L3"],
                },
                {
                    "source_line": 6,
                    "role": "error_mechanism",
                    "proposed_replacement": "",
                    "reason": "The loop update decreases z.",
                    "confidence": 0.8,
                    "evidence_refs": ["L7"],
                },
            ],
            "mechanism_claims": [
                {"claim_type": "initialization", "claim": "z begins at 11.", "evidence_refs": ["L3"]},
                {"claim_type": "direct_write", "claim": "The loop decreases z.", "evidence_refs": ["L7"]},
            ],
            "mechanism_summary": "The initial value and loop update lead to the assertion state.",
            "uncertainty": "A reference or test is needed to determine the intended edit.",
        }
        self.assertTrue(verify(job["user"], response, require_evidence=True)["valid"])

    def test_evidence_contract_rejects_unknown_reference(self) -> None:
        job = self.jobs_by_case["Seed01_update_sign"]
        response = {
            "candidates": [{"source_line": 6, "role": "fault_origin", "proposed_replacement": "z = z + 1;", "evidence_refs": ["L99"]}],
            "mechanism_claims": [{"claim_type": "direct_write", "claim": "z changes.", "evidence_refs": ["L99"]}],
        }
        result = verify(job["user"], response, require_evidence=True)
        self.assertFalse(result["valid"])
        self.assertIn("candidate_1_unknown_evidence_refs", result["violations"])

    @unittest.skipUnless(shutil.which("gcc"), "gcc is not available")
    def test_counterfactual_patch_changes_failure_to_success(self) -> None:
        source = SEED_DIR / "Seed03_initial_value_v2_faulty.c"
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            baseline_source = work / "baseline.c"
            shutil.copy2(source, baseline_source)
            baseline = compile_and_run(baseline_source, work / "baseline.exe", "gcc", 10)
            self.assertFalse(baseline["runtime_pass"])
            patched_source = work / "patched.c"
            self.assertEqual(
                "  int z = 11;",
                apply_one_line_replacement(source, 3, "int z = 12;", patched_source),
            )
            patched = compile_and_run(patched_source, work / "patched.exe", "gcc", 10)
            self.assertTrue(patched["runtime_pass"])


if __name__ == "__main__":
    unittest.main()
