import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from error_invariant_pipeline.parse_error_invariants import build_trajectory


class ErrorInvariantParserTest(unittest.TestCase):
    def test_sv01_extracts_clean_error_state_and_tool_ranking(self):
        experiments_root = Path(__file__).resolve().parents[2]
        trajectory = build_trajectory(
            "SV01_Mono5_1",
            "03_experiments/benchmarks/pilot/normalized/Mono5_1_errorinv.c",
            experiments_root / "outputs/error_invariants_pilot_2026-08-09/Mono5_1_errorinv-full.out",
        )

        self.assertEqual(trajectory["error"]["location_id"], 13)
        self.assertEqual(trajectory["error"]["error_invariant"], "z == 0")
        self.assertEqual(trajectory["error"]["variables"], ["z"])
        self.assertEqual(
            trajectory["pure_tool_baseline"]["candidates"][0]["location_id"], 8
        )
        for item in trajectory["evidence_locations"]:
            if item["error_invariant"] in {"top", "bottom"}:
                self.assertIn("z :=", item["statement"])


if __name__ == "__main__":
    unittest.main()
