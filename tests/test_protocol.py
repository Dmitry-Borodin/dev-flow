import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "skills" / "dev-flow" / "assets"
PHASES = [
    "frame",
    "discover",
    "specify",
    "plan",
    "implement",
    "verify",
    "review",
    "close",
]


class ProtocolAssetsTest(unittest.TestCase):
    def load(self, name):
        with (ASSETS / name).open(encoding="utf-8") as source:
            return json.load(source)

    def test_workflow_defines_stable_v1_contract(self):
        workflow = self.load("workflow-v1.json")

        self.assertEqual(workflow["contract"], "dev-flow/workflow/v1")
        self.assertEqual(workflow["version"], "1")
        self.assertEqual(workflow["phases"], PHASES)
        self.assertEqual(
            workflow["results"],
            ["ready", "blocked", "stale", "inconsistent", "invalid", "complete", "terminated"],
        )

    def test_transition_graph_uses_only_stable_phase_ids(self):
        workflow = self.load("workflow-v1.json")
        transitions = workflow["transitions"]

        self.assertEqual(set(transitions), set(PHASES))
        for targets in transitions.values():
            self.assertLessEqual(set(targets), set(PHASES) | {"done"})
        self.assertEqual(transitions["close"], ["done"])

    def test_workflow_defines_phase_specific_evidence(self):
        workflow = self.load("workflow-v1.json")

        self.assertEqual(set(workflow["evidence"]), set(PHASES))
        self.assertEqual(workflow["evidence"]["frame"], "brief.md")
        self.assertEqual(workflow["evidence"]["verify"], "verification.md")
        self.assertEqual(workflow["evidence"]["close"], "closure.md")

    def test_profiles_materialize_every_phase(self):
        workflow = self.load("workflow-v1.json")

        self.assertEqual(set(workflow["profiles"]), {"feature", "bug", "refactor", "maintenance"})
        for required in workflow["profiles"].values():
            self.assertEqual(set(required), set(PHASES))
            self.assertTrue(all(isinstance(value, bool) for value in required.values()))
            self.assertTrue(required["frame"])
            self.assertTrue(required["implement"])
            self.assertTrue(required["close"])

    def test_change_schema_phase_keys_match_workflow(self):
        schema = self.load("change-v1.schema.json")
        manifest = schema["properties"]
        phase_map = manifest["phases"]

        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema["$id"], "https://dev-flow.local/change-v1.schema.json")
        self.assertEqual(set(phase_map["required"]), set(PHASES))
        self.assertEqual(set(phase_map["properties"]), set(PHASES))
        self.assertFalse(schema["additionalProperties"])
        self.assertFalse(phase_map["additionalProperties"])
        self.assertEqual(manifest["current_phase"]["type"], ["string", "null"])

    def test_schema_enums_match_workflow(self):
        workflow = self.load("workflow-v1.json")
        schema = self.load("change-v1.schema.json")
        properties = schema["properties"]
        phase = schema["$defs"]["phase"]["properties"]

        self.assertEqual(set(properties["kind"]["enum"]), set(workflow["profiles"]))
        self.assertEqual(properties["lifecycle"]["enum"], workflow["lifecycles"])
        self.assertEqual(phase["state"]["enum"], workflow["phase_states"])
        self.assertIn("terminated", workflow["results"])


if __name__ == "__main__":
    unittest.main()
