import sys, os, pathlib
import unittest
import json
from unittest.mock import MagicMock

# Add scripts to path
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "scripts"))
import run_evaluator

class TestEvaluatorHardening(unittest.TestCase):
    def test_resolve_artifact_paths_new_format(self):
        # Setup mock files
        docs = pathlib.Path("docs")
        docs.mkdir(exist_ok=True)
        (docs / "kjtcom-design-10.69.0.md").touch()
        (docs / "kjtcom-plan-10.69.0.md").touch()
        (docs / "kjtcom-build-10.69.1.md").touch()
        (docs / "kjtcom-bundle-10.69.1.md").touch()
        
        paths = run_evaluator.resolve_artifact_paths("10.69.1")
        self.assertEqual(str(paths['design']), "docs/kjtcom-design-10.69.0.md")
        self.assertEqual(str(paths['build']), "docs/kjtcom-build-10.69.1.md")
        self.assertEqual(str(paths['bundle']), "docs/kjtcom-bundle-10.69.1.md")

    def test_compute_synthesis_ratios_weighted(self):
        ws_data = [
            {"id": "W1", "synthesis_ratio": 0.8}, # Fail individually
            {"id": "W2", "synthesis_ratio": 0.2},
            {"id": "W3", "synthesis_ratio": 0.2}
        ]
        # Weighted average = (0.8 + 0.2 + 0.2) / 3 = 0.4
        results = run_evaluator.compute_synthesis_ratios(ws_data, mode="weighted", threshold=0.5)
        self.assertFalse(results["should_fail"])
        self.assertAlmostEqual(results["average"], 0.4)

    def test_compute_synthesis_ratios_strict(self):
        ws_data = [
            {"id": "W1", "synthesis_ratio": 0.8},
            {"id": "W2", "synthesis_ratio": 0.2}
        ]
        results = run_evaluator.compute_synthesis_ratios(ws_data, mode="strict", threshold=0.5)
        self.assertTrue(results["should_fail"])

    def test_repair_gemini_schema_markdown(self):
        raw = "Here is the JSON: ```json\n{\"iteration\": \"10.69.1\", \"summary\": \"test\"}\n```"
        schema = {"required": ["iteration", "summary", "workstreams"]}
        data, repaired, log = run_evaluator.repair_gemini_schema(raw, schema)
        self.assertTrue(repaired)
        self.assertEqual(data["iteration"], "10.69.1")
        self.assertEqual(data["workstreams"], []) # Filled missing

    def test_resolve_workstream_id_alias(self):
        gt = ["W1", "W2", "W3a"]
        self.assertEqual(run_evaluator.resolve_workstream_id_alias("W3", gt), "W3a") # sub-lettered
        self.assertEqual(run_evaluator.resolve_workstream_id_alias("W1", gt), "W1")   # exact
        self.assertEqual(run_evaluator.resolve_workstream_id_alias("W3a", gt), "W3a") # exact

if __name__ == "__main__":
    unittest.main()
