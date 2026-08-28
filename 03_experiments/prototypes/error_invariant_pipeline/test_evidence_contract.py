import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from error_invariant_pipeline.verify_evidence_contract import verify


class EvidenceContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[2]
        cls.trajectory = json.loads(
            (root / "outputs/evidence_trajectories/Seed01_update_sign.json").read_text(encoding="utf-8")
        )

    def test_accepts_grounded_direct_write(self):
        response = {
            "ranked_candidates": [
                {"analysis_location": 7, "evidence_refs": ["L7"], "reason": "updates z"}
            ],
            "causal_chain": [
                {"claim_type": "direct_write", "claim": "L7 decrements z", "evidence_refs": ["L7"]}
            ],
        }
        self.assertTrue(verify(self.trajectory, response)["valid"])

    def test_rejects_ungrounded_claim(self):
        response = {
            "ranked_candidates": [
                {"analysis_location": 99, "evidence_refs": ["L99"], "reason": "unknown"}
            ],
            "causal_chain": [
                {"claim_type": "direct_write", "claim": "guard writes z", "evidence_refs": ["L6"]}
            ],
        }
        result = verify(self.trajectory, response)
        self.assertFalse(result["valid"])
        self.assertIn("candidate_1_unknown_location", result["violations"])
        self.assertIn("chain_1_write_claim_not_supported", result["violations"])


if __name__ == "__main__":
    unittest.main()
