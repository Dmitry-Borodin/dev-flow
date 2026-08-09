import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "evals" / "scenarios.json"
RECORDED_RUN = ROOT / "evals" / "runs" / "2026-08-09.json"
PACKAGE_FILES = (
    "skills/dev-flow/SKILL.md",
    "skills/dev-flow/agents/openai.yaml",
    "skills/dev-flow/assets/change-v1.schema.json",
    "skills/dev-flow/assets/workflow-v1.json",
    "skills/dev-flow/references/artifacts.md",
    "skills/dev-flow/references/phase-close.md",
    "skills/dev-flow/references/phase-discover.md",
    "skills/dev-flow/references/phase-frame.md",
    "skills/dev-flow/references/phase-implement.md",
    "skills/dev-flow/references/phase-plan.md",
    "skills/dev-flow/references/phase-review.md",
    "skills/dev-flow/references/phase-specify.md",
    "skills/dev-flow/references/phase-verify.md",
    "skills/dev-flow/scripts/flowctl.py",
    "evals/scenarios.json",
)
REQUIRED_IDS = {
    "activation-start-change",
    "activation-adjacent-explanation",
    "activation-trivial-edit",
    "resume-plan-active",
    "ambiguous-change-selection",
    "missing-passed-evidence",
    "spec-changed-after-plan",
    "workspace-changed-after-verify",
    "maintenance-compact-profile",
    "bug-without-reproduction",
    "plan-only-authority",
    "verify-finds-production-defect",
    "finish-crosses-phase-boundaries",
    "blocked-unblock-resume",
    "resume-complete-change",
}


class BehavioralEvalCorpusTest(unittest.TestCase):
    def load(self):
        with SCENARIOS.open(encoding="utf-8") as source:
            return json.load(source)

    def test_corpus_has_bounded_unique_scenarios(self):
        scenarios = self.load()
        ids = [case["id"] for case in scenarios]

        self.assertGreaterEqual(len(scenarios), 10)
        self.assertLessEqual(len(scenarios), 15)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertLessEqual(REQUIRED_IDS, set(ids))

    def test_each_scenario_separates_prompt_from_rubric(self):
        for case in self.load():
            self.assertEqual(
                set(case),
                {
                    "id",
                    "category",
                    "skill_expected",
                    "pressure",
                    "prompt",
                    "expected_behaviors",
                    "forbidden_behaviors",
                },
                case["id"],
            )
            self.assertIsInstance(case["skill_expected"], bool)
            self.assertTrue(case["prompt"].strip())
            self.assertGreaterEqual(len(case["expected_behaviors"]), 1)
            self.assertGreaterEqual(len(case["forbidden_behaviors"]), 1)
            for expected in case["expected_behaviors"]:
                self.assertNotIn(expected, case["prompt"], case["id"])

    def test_pressure_cases_combine_at_least_three_pressures(self):
        pressure_cases = [case for case in self.load() if case["category"] == "pressure"]

        self.assertGreaterEqual(len(pressure_cases), 3)
        for case in pressure_cases:
            self.assertGreaterEqual(len(set(case["pressure"])), 3, case["id"])

    def test_activation_has_positive_and_adjacent_negative(self):
        activation = [case for case in self.load() if case["category"] == "activation"]

        self.assertTrue(any(case["skill_expected"] for case in activation))
        self.assertTrue(any(not case["skill_expected"] for case in activation))

    def test_recorded_run_covers_corpus_with_raw_outputs(self):
        scenarios = self.load()
        with RECORDED_RUN.open(encoding="utf-8") as source:
            run = json.load(source)

        self.assertTrue(run["metadata"]["fresh_context"])
        self.assertTrue(run["metadata"]["hidden_rubric"])
        self.assertEqual(run["metadata"]["eval_type"], "policy-decision")
        self.assertEqual(run["metadata"]["package_files"], list(PACKAGE_FILES))
        self.assertGreaterEqual(len(run["metadata"]["execution_evidence"]), 1)
        for field in ("skill_sha256", "workflow_sha256", "flowctl_sha256", "scenarios_sha256", "package_sha256"):
            self.assertRegex(run["metadata"][field], r"^[0-9a-f]{64}$")
        expected_hashes = {
            "skill_sha256": self.file_hash("skills/dev-flow/SKILL.md"),
            "workflow_sha256": self.file_hash("skills/dev-flow/assets/workflow-v1.json"),
            "flowctl_sha256": self.file_hash("skills/dev-flow/scripts/flowctl.py"),
            "scenarios_sha256": self.file_hash("evals/scenarios.json"),
            "package_sha256": self.package_hash(),
        }
        for field, expected in expected_hashes.items():
            self.assertEqual(run["metadata"][field], expected, field)
        self.assertEqual({result["id"] for result in run["results"]}, {case["id"] for case in scenarios})
        for result in run["results"]:
            self.assertEqual(result["verdict"], "pass", result["id"])
            self.assertTrue(result["raw_output"].strip(), result["id"])

    @staticmethod
    def file_hash(relative_path):
        return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()

    @staticmethod
    def package_hash():
        digest = hashlib.sha256()
        for relative_path in PACKAGE_FILES:
            digest.update(relative_path.encode("utf-8") + b"\0")
            digest.update((ROOT / relative_path).read_bytes())
            digest.update(b"\0")
        return digest.hexdigest()


if __name__ == "__main__":
    unittest.main()
