import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FLOWCTL = ROOT / "skills" / "dev-flow" / "scripts" / "flowctl.py"


class FlowctlTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.change = self.root / "change"
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def run_flow(self, *args, workspace=None, expected=0, env=None):
        command = [sys.executable, str(FLOWCTL), "--change", str(self.change)]
        if workspace is not None:
            command.extend(["--workspace", str(workspace)])
        command.extend(args)
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False, env=env)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as error:
            self.fail(f"flowctl did not emit JSON: {error}\nstdout={result.stdout!r}\nstderr={result.stderr!r}")

    def init(self, kind="feature"):
        return self.run_flow(
            "init",
            "--id",
            "DF-1",
            "--project",
            "demo",
            "--title",
            "Durable flow",
            "--kind",
            kind,
        )

    def artifact(self, name, content=None):
        path = self.change / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content or f"# {name}\n", encoding="utf-8")
        return path

    def transition(self, target, evidence, workspace=None):
        return self.run_flow(
            "transition",
            "--to",
            target,
            "--evidence",
            *evidence,
            "--reason",
            f"ready for {target}",
            workspace=workspace,
        )

    def prepare_maintenance_to_implement(self):
        self.init("maintenance")
        self.artifact("brief.md")
        self.transition("discover", ["brief.md"])
        self.run_flow("skip", "--reason", "No design-affecting unknowns")
        self.run_flow("skip", "--reason", "No user-visible behavior")
        self.artifact("plan.md")
        self.transition("implement", ["plan.md"])

    def test_init_materializes_profile_and_create_event(self):
        output = self.init()
        manifest = json.loads((self.change / "change.json").read_text(encoding="utf-8"))
        events = [json.loads(line) for line in (self.change / "events.jsonl").read_text().splitlines()]

        self.assertEqual(output["result"], "ready")
        self.assertEqual(output["current_phase"], "frame")
        self.assertEqual(manifest["revision"], 1)
        self.assertEqual(manifest["phases"]["frame"]["state"], "active")
        self.assertFalse(manifest["phases"]["discover"]["required"])
        self.assertTrue(manifest["phases"]["specify"]["required"])
        self.assertEqual(events[0]["action"], "create")
        self.assertEqual(events[0]["revision"], 1)

    def test_transition_passes_current_phase_and_activates_next(self):
        self.init()
        self.artifact("brief.md")

        output = self.transition("discover", ["brief.md"])
        manifest = json.loads((self.change / "change.json").read_text())

        self.assertEqual(output["current_phase"], "discover")
        self.assertEqual(manifest["phases"]["frame"]["state"], "passed")
        self.assertEqual(manifest["phases"]["frame"]["evidence"], ["brief.md"])
        self.assertEqual(manifest["phases"]["discover"]["state"], "active")

    def test_transition_rejects_missing_or_escaping_evidence(self):
        self.init()
        missing = self.run_flow(
            "transition",
            "--to",
            "discover",
            "--evidence",
            "brief.md",
            "--reason",
            "not present",
            expected=2,
        )
        self.assertEqual(missing["result"], "invalid")
        self.assertEqual(missing["error"], "evidence-missing")

    def test_transition_rejects_illegal_target(self):
        self.init()
        self.artifact("brief.md")

        output = self.run_flow(
            "transition",
            "--to",
            "specify",
            "--evidence",
            "brief.md",
            "--reason",
            "skip a phase",
            expected=2,
        )

        self.assertEqual(output["error"], "transition-illegal")

    def test_transition_rejects_evidence_outside_change_directory(self):
        self.init()
        outside = self.root / "outside.md"
        outside.write_text("outside", encoding="utf-8")

        output = self.run_flow(
            "transition",
            "--to",
            "discover",
            "--evidence",
            "../outside.md",
            "--reason",
            "not valid evidence",
            expected=2,
        )
        self.assertEqual(output["result"], "invalid")
        self.assertEqual(output["error"], "evidence-outside-change")

    def test_transition_requires_phase_specific_evidence_without_placeholders(self):
        self.init()
        self.artifact("wrong.md", "# Not the brief\n")
        wrong = self.run_flow(
            "transition",
            "--to",
            "discover",
            "--evidence",
            "wrong.md",
            "--reason",
            "wrong artifact",
            expected=2,
        )
        self.assertEqual(wrong["error"], "phase-evidence-required")

        self.artifact("brief.md", "# Brief\nTODO decide scope\n")
        placeholder = self.run_flow(
            "transition",
            "--to",
            "discover",
            "--evidence",
            "brief.md",
            "--reason",
            "not actually complete",
            expected=2,
        )
        self.assertEqual(placeholder["error"], "evidence-placeholder")

    def test_skip_records_reason_only_for_optional_phase(self):
        self.init()
        self.artifact("brief.md")
        self.transition("discover", ["brief.md"])

        output = self.run_flow("skip", "--reason", "Existing evidence is sufficient")
        manifest = json.loads((self.change / "change.json").read_text())

        self.assertEqual(output["current_phase"], "specify")
        self.assertEqual(manifest["phases"]["discover"]["state"], "skipped")
        self.assertEqual(manifest["phases"]["discover"]["reason"], "Existing evidence is sufficient")
        refused = self.run_flow("skip", "--reason", "Too busy", expected=2)
        self.assertEqual(refused["error"], "required-phase")

    def test_block_and_unblock_preserve_current_phase(self):
        self.init()

        blocked = self.run_flow("block", "--kind", "user-decision", "--message", "Choose storage")
        self.assertEqual(blocked["result"], "blocked")
        self.assertEqual(blocked["current_phase"], "frame")
        self.assertEqual(blocked["blockers"][0]["id"], "B-1")

        active = self.run_flow("unblock", "--id", "B-1", "--reason", "SQLite selected")
        self.assertEqual(active["result"], "ready")
        self.assertEqual(active["current_phase"], "frame")
        self.assertEqual(active["blockers"], [])

    def test_multiple_blockers_resume_only_after_all_are_closed(self):
        self.init()
        self.run_flow("block", "--kind", "evidence", "--message", "Need reproduction")
        second = self.run_flow("block", "--kind", "user-decision", "--message", "Choose policy")
        self.assertEqual([item["id"] for item in second["blockers"]], ["B-1", "B-2"])

        still_blocked = self.run_flow("unblock", "--id", "B-1", "--reason", "Reproduced")
        self.assertEqual(still_blocked["result"], "blocked")
        self.assertEqual([item["id"] for item in still_blocked["blockers"]], ["B-2"])

        ready = self.run_flow("unblock", "--id", "B-2", "--reason", "Policy selected")
        self.assertEqual(ready["result"], "ready")
        self.assertEqual(ready["current_phase"], "frame")

    def test_cancelled_lifecycle_is_terminated_not_complete(self):
        self.init()
        manifest_path = self.change / "change.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["revision"] = 2
        manifest["lifecycle"] = "cancelled"
        manifest["current_phase"] = None
        manifest["phases"]["frame"]["state"] = "pending"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        events_path = self.change / "events.jsonl"
        events_path.write_text(
            events_path.read_text()
            + json.dumps(
                {
                    "at": "2026-08-09T00:00:00Z",
                    "action": "terminate",
                    "actor": "user",
                    "revision": 2,
                    "from": "frame",
                    "to": "cancelled",
                    "reason": "No longer needed",
                }
            )
            + "\n",
            encoding="utf-8",
        )

        output = self.run_flow("status")

        self.assertEqual(output["result"], "terminated")
        self.assertEqual(output["lifecycle"], "cancelled")
        self.assertIsNone(output["next_action"])

    def test_mutation_in_wrong_lifecycle_returns_nonzero_error(self):
        self.init()
        self.artifact("brief.md")
        self.run_flow("block", "--kind", "user-decision", "--message", "Choose storage")

        output = self.run_flow(
            "transition",
            "--to",
            "discover",
            "--evidence",
            "brief.md",
            "--reason",
            "should not run",
            expected=2,
        )

        self.assertEqual(output["error"], "state-not-ready")

    def test_rewind_resets_target_and_downstream_state(self):
        self.prepare_maintenance_to_implement()

        output = self.run_flow("rewind", "--to", "plan", "--reason", "Scope changed")
        manifest = json.loads((self.change / "change.json").read_text())

        self.assertEqual(output["current_phase"], "plan")
        self.assertEqual(manifest["phases"]["plan"]["state"], "active")
        self.assertEqual(manifest["phases"]["plan"]["evidence"], [])
        self.assertEqual(manifest["phases"]["implement"]["state"], "pending")
        self.assertEqual(manifest["phases"]["verify"]["state"], "pending")

    def test_status_reports_inconsistent_for_two_active_phases(self):
        self.init()
        manifest_path = self.change / "change.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["phases"]["plan"]["state"] = "active"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        output = self.run_flow("status", expected=2)

        self.assertEqual(output["result"], "inconsistent")
        self.assertIn("active-phase-count", {item["code"] for item in output["violations"]})

    def test_plan_becomes_stale_after_spec_changes(self):
        self.init()
        self.artifact("brief.md")
        self.transition("discover", ["brief.md"])
        self.run_flow("skip", "--reason", "No discovery needed")
        self.artifact("spec.md", "# Spec\nAC-1: old\n")
        self.transition("plan", ["spec.md"])
        self.artifact("plan.md")
        self.transition("implement", ["plan.md"])

        self.artifact("spec.md", "# Spec\nAC-1: changed\n")
        output = self.run_flow("status", expected=3)

        self.assertEqual(output["result"], "stale")
        self.assertEqual(output["health"], "stale")
        self.assertEqual(output["next_action"], {"kind": "rewind", "phase": "plan"})
        self.assertIn("plan-input-stale", {item["code"] for item in output["violations"]})

    def test_plan_stale_rewind_is_executable_from_verify(self):
        self.init()
        self.artifact("brief.md")
        self.transition("discover", ["brief.md"])
        self.run_flow("skip", "--reason", "No discovery needed")
        self.artifact("spec.md", "# Spec\nAC-1: old\n")
        self.transition("plan", ["spec.md"])
        self.artifact("plan.md")
        self.transition("implement", ["plan.md"])
        self.artifact("implementation.md")
        self.transition("verify", ["implementation.md"])
        self.artifact("spec.md", "# Spec\nAC-1: changed\n")

        stale = self.run_flow("status", expected=3)
        self.assertEqual(stale["next_action"], {"kind": "rewind", "phase": "plan"})
        rewound = self.run_flow("rewind", "--to", "plan", "--reason", "Spec changed")
        self.assertEqual(rewound["result"], "ready")
        self.assertEqual(rewound["current_phase"], "plan")

    def test_verification_becomes_stale_after_workspace_changes(self):
        self.prepare_maintenance_to_implement()
        self.artifact("implementation.md")
        self.workspace.joinpath("app.py").write_text("value = 1\n", encoding="utf-8")
        self.transition("verify", ["implementation.md"])
        self.artifact("verification.md")
        self.transition("review", ["verification.md"], workspace=self.workspace)

        self.workspace.joinpath("app.py").write_text("value = 2\n", encoding="utf-8")
        output = self.run_flow("status", workspace=self.workspace, expected=3)

        self.assertEqual(output["result"], "stale")
        self.assertEqual(output["next_action"], {"kind": "rewind", "phase": "verify"})
        self.assertIn("verified-workspace-stale", {item["code"] for item in output["violations"]})

        rewound = self.run_flow(
            "rewind",
            "--to",
            "verify",
            "--reason",
            "Workspace changed after verification",
            workspace=self.workspace,
        )
        self.assertEqual(rewound["result"], "ready")
        self.assertEqual(rewound["current_phase"], "verify")

    def test_workspace_is_required_after_verification_provenance_exists(self):
        self.prepare_maintenance_to_implement()
        self.artifact("implementation.md")
        self.transition("verify", ["implementation.md"])
        self.workspace.joinpath("app.py").write_text("value = 1\n", encoding="utf-8")
        self.artifact("verification.md")
        self.transition("review", ["verification.md"], workspace=self.workspace)

        output = self.run_flow("status", expected=2)

        self.assertEqual(output["result"], "inconsistent")
        self.assertIn("workspace-required", {item["code"] for item in output["violations"]})

    def test_change_artifacts_inside_workspace_do_not_stale_fingerprint(self):
        self.change = self.workspace / "docs" / "dev-flow" / "changes" / "DF-1"
        self.prepare_maintenance_to_implement()
        self.workspace.joinpath("app.py").write_text("value = 1\n", encoding="utf-8")
        self.artifact("implementation.md")
        self.transition("verify", ["implementation.md"])
        self.artifact("verification.md")
        output = self.transition("review", ["verification.md"], workspace=self.workspace)
        self.artifact("review-notes.md", "# Review notes\n")

        status = self.run_flow("status", workspace=self.workspace)

        self.assertEqual(output["result"], "ready")
        self.assertEqual(status["result"], "ready")

    def test_close_moves_change_to_terminal_done(self):
        self.prepare_maintenance_to_implement()
        self.artifact("implementation.md")
        self.transition("verify", ["implementation.md"])
        self.workspace.joinpath("app.py").write_text("value = 1\n", encoding="utf-8")
        self.artifact("verification.md")
        self.transition("review", ["verification.md"], workspace=self.workspace)
        self.run_flow("skip", "--reason", "Low-risk mechanical maintenance", workspace=self.workspace)
        self.artifact("closure.md")
        output = self.transition("done", ["closure.md"], workspace=self.workspace)
        manifest = json.loads((self.change / "change.json").read_text())

        self.assertEqual(output["result"], "complete")
        self.assertEqual(manifest["lifecycle"], "done")
        self.assertIsNone(manifest["current_phase"])
        self.assertFalse(any(phase["state"] == "active" for phase in manifest["phases"].values()))
        self.assertEqual(manifest["phases"]["close"]["state"], "passed")

    def test_done_rejects_pending_optional_phase_and_open_blocker(self):
        self.prepare_maintenance_to_implement()
        self.artifact("implementation.md")
        self.transition("verify", ["implementation.md"])
        self.workspace.joinpath("app.py").write_text("value = 1\n", encoding="utf-8")
        self.artifact("verification.md")
        self.transition("review", ["verification.md"], workspace=self.workspace)
        self.run_flow("skip", "--reason", "Low-risk maintenance", workspace=self.workspace)
        self.artifact("closure.md")
        self.transition("done", ["closure.md"], workspace=self.workspace)
        manifest_path = self.change / "change.json"
        valid = json.loads(manifest_path.read_text(encoding="utf-8"))

        pending = json.loads(json.dumps(valid))
        pending["phases"]["review"] = {"required": False, "state": "pending", "evidence": []}
        manifest_path.write_text(json.dumps(pending), encoding="utf-8")
        output = self.run_flow("status", workspace=self.workspace, expected=2)
        self.assertIn("terminal-phase-incomplete", {item["code"] for item in output["violations"]})

        blocked = json.loads(json.dumps(valid))
        blocked["blockers"].append(
            {
                "id": "B-1",
                "kind": "external",
                "message": "Unresolved approval",
                "status": "open",
                "opened_at": "2026-08-09T00:00:00Z",
            }
        )
        manifest_path.write_text(json.dumps(blocked), encoding="utf-8")
        output = self.run_flow("status", workspace=self.workspace, expected=2)
        self.assertIn("done-with-blocker", {item["code"] for item in output["violations"]})

    def test_passed_verify_and_review_require_workspace_provenance(self):
        self.prepare_maintenance_to_implement()
        self.workspace.joinpath("app.py").write_text("value = 1\n", encoding="utf-8")
        self.artifact("implementation.md")
        self.transition("verify", ["implementation.md"])
        self.artifact("verification.md")
        self.transition("review", ["verification.md"], workspace=self.workspace)
        manifest_path = self.change / "change.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["provenance"]["verified_workspace"] = None
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        output = self.run_flow("status", expected=2)

        self.assertIn("verified-provenance-missing", {item["code"] for item in output["violations"]})

        manifest["provenance"]["verified_workspace"] = {
            "algorithm": "sha256",
            "value": "0" * 64,
            "source": "files",
        }
        manifest["phases"]["review"]["state"] = "passed"
        manifest["phases"]["review"]["evidence"] = ["review.md"]
        self.artifact("review.md")
        manifest["phases"]["close"]["state"] = "active"
        manifest["current_phase"] = "close"
        manifest["provenance"]["reviewed_workspace"] = None
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        output = self.run_flow("status", expected=2)
        self.assertIn("reviewed-provenance-missing", {item["code"] for item in output["violations"]})

    def test_feature_change_runs_end_to_end_in_a_temporary_workspace(self):
        self.init("feature")
        self.artifact("brief.md", "# Brief\nAdd durable authentication.\n")
        self.transition("discover", ["brief.md"])
        self.run_flow("skip", "--reason", "The behavior and constraints are already known")
        self.artifact("spec.md", "# Specification\nAC-1: reject invalid credentials.\n")
        self.transition("plan", ["spec.md"])
        self.artifact("plan.md", "# Plan\nImplement AC-1 and its focused test.\n")
        self.transition("implement", ["plan.md"])
        self.workspace.joinpath("auth.py").write_text("def authenticate(valid): return valid\n", encoding="utf-8")
        self.artifact("implementation.md", "# Implementation\nImplemented AC-1.\n")
        self.transition("verify", ["implementation.md"])
        self.artifact("verification.md", "# Verification\nFocused checks passed.\n")
        self.transition("review", ["verification.md"], workspace=self.workspace)
        self.artifact("review.md", "# Review\nNo blocking findings.\n")
        self.transition("close", ["review.md"], workspace=self.workspace)
        self.artifact("closure.md", "# Closure\nAcceptance evidence is current.\n")

        output = self.transition("done", ["closure.md"], workspace=self.workspace)
        events = [json.loads(line) for line in (self.change / "events.jsonl").read_text().splitlines()]

        self.assertEqual(output["result"], "complete")
        self.assertEqual(output["lifecycle"], "done")
        self.assertEqual(output["revision"], 9)
        self.assertEqual([event["revision"] for event in events], list(range(1, 10)))

    def test_empty_mutation_values_are_rejected_before_state_is_written(self):
        output = self.run_flow(
            "init",
            "--id",
            " ",
            "--project",
            "demo",
            "--title",
            "Durable flow",
            "--kind",
            "feature",
            expected=2,
        )
        self.assertEqual(output["error"], "usage-error")
        self.assertFalse((self.change / "change.json").exists())

        self.init()
        skipped = self.run_flow("skip", "--reason", " ", expected=2)
        self.assertEqual(skipped["error"], "usage-error")
        manifest = json.loads((self.change / "change.json").read_text())
        self.assertEqual(manifest["revision"], 1)

    def test_empty_global_paths_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [
                    sys.executable,
                    str(FLOWCTL),
                    "--change",
                    "",
                    "init",
                    "--id",
                    "DF-empty",
                    "--project",
                    "demo",
                    "--title",
                    "Empty path",
                    "--kind",
                    "feature",
                ],
                cwd=directory,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["error"], "usage-error")

        self.init()
        result = subprocess.run(
            [sys.executable, str(FLOWCTL), "--change", str(self.change), "--workspace", "", "status"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["error"], "usage-error")

    def test_event_revisions_track_every_mutation(self):
        self.init()
        self.run_flow("block", "--kind", "external", "--message", "Need approval")
        self.run_flow("unblock", "--id", "B-1", "--reason", "Approved")

        manifest = json.loads((self.change / "change.json").read_text())
        events = [json.loads(line) for line in (self.change / "events.jsonl").read_text().splitlines()]

        self.assertEqual(manifest["revision"], 3)
        self.assertEqual([event["revision"] for event in events], [1, 2, 3])
        self.assertEqual([event["action"] for event in events], ["create", "block", "unblock"])

    def test_event_semantics_reject_unblock_for_unknown_blocker(self):
        self.init()
        self.run_flow("block", "--kind", "external", "--message", "Need approval")
        self.run_flow("unblock", "--id", "B-1", "--reason", "Approved")
        events_path = self.change / "events.jsonl"
        events = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines()]
        events[-1]["blocker_id"] = "B-999"
        events_path.write_text("".join(json.dumps(event) + "\n" for event in events), encoding="utf-8")

        output = self.run_flow("status", expected=2)

        self.assertIn("event-state-mismatch", {item["code"] for item in output["violations"]})

    def test_validate_rejects_unknown_manifest_fields_and_event_gaps(self):
        self.init()
        manifest_path = self.change / "change.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["unexpected"] = True
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        unknown = self.run_flow("validate", expected=2)
        self.assertEqual(unknown["result"], "invalid")
        self.assertIn("unknown-manifest-field", {item["code"] for item in unknown["violations"]})

        manifest.pop("unexpected")
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        (self.change / "events.jsonl").write_text("", encoding="utf-8")
        events = self.run_flow("validate", expected=2)
        self.assertEqual(events["result"], "inconsistent")
        self.assertIn("event-revision-mismatch", {item["code"] for item in events["violations"]})

    def test_validate_rejects_schema_invalid_provenance_and_event_envelope(self):
        self.init()
        manifest_path = self.change / "change.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["provenance"]["verified_workspace"] = {
            "algorithm": "md5",
            "value": "not-a-digest",
            "source": "unknown",
        }
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        invalid = self.run_flow("validate", expected=2)
        self.assertEqual(invalid["result"], "invalid")
        self.assertIn("workspace-fingerprint-invalid", {item["code"] for item in invalid["violations"]})

        manifest["provenance"]["verified_workspace"] = None
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        events_path = self.change / "events.jsonl"
        event = json.loads(events_path.read_text())
        event.pop("action")
        events_path.write_text(json.dumps(event) + "\n", encoding="utf-8")
        event_invalid = self.run_flow("validate", expected=2)
        self.assertEqual(event_invalid["result"], "invalid")
        self.assertIn("event-envelope-invalid", {item["code"] for item in event_invalid["violations"]})

    def test_validate_reports_malformed_phase_as_json(self):
        self.init()
        manifest_path = self.change / "change.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["phases"]["close"] = []
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        output = self.run_flow("validate", expected=2)

        self.assertEqual(output["result"], "invalid")
        self.assertIn("phase-invalid", {item["code"] for item in output["violations"]})

    def test_core_lifecycle_and_order_invariants_have_diagnostics(self):
        self.init()
        manifest_path = self.change / "change.json"
        baseline = json.loads(manifest_path.read_text(encoding="utf-8"))

        cases = {
            "current-phase-mismatch": lambda item: item.update(current_phase="plan"),
            "blocked-without-blocker": lambda item: item.update(lifecycle="blocked"),
            "active-with-blocker": lambda item: item["blockers"].append(
                {
                    "id": "B-1",
                    "kind": "external",
                    "message": "Need approval",
                    "status": "open",
                    "opened_at": "2026-08-09T00:00:00Z",
                }
            ),
            "terminal-phase-active": lambda item: item.update(lifecycle="done"),
            "phase-order-invalid": lambda item: (
                item["phases"]["frame"].update(state="pending"),
                item["phases"]["plan"].update(state="active"),
                item.update(current_phase="plan"),
            ),
        }
        for code, mutate in cases.items():
            with self.subTest(code=code):
                manifest = json.loads(json.dumps(baseline))
                mutate(manifest)
                manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                output = self.run_flow("status", expected=2)
                self.assertIn(code, {item["code"] for item in output["violations"]})

    def test_git_fingerprint_excludes_committed_change_artifacts(self):
        self.change = self.workspace / ".dev-flow" / "DF-1"
        subprocess.run(["git", "init", "-q", str(self.workspace)], check=True)
        subprocess.run(["git", "-C", str(self.workspace), "config", "user.email", "dev-flow@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(self.workspace), "config", "user.name", "Dev Flow Test"], check=True)
        self.workspace.joinpath("app.py").write_text("value = 1\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.workspace), "add", "app.py"], check=True)
        subprocess.run(["git", "-C", str(self.workspace), "commit", "-q", "-m", "product"], check=True)
        self.prepare_maintenance_to_implement()
        self.artifact("implementation.md")
        self.transition("verify", ["implementation.md"])
        self.artifact("verification.md")
        self.transition("review", ["verification.md"], workspace=self.workspace)
        subprocess.run(["git", "-C", str(self.workspace), "add", ".dev-flow"], check=True)
        subprocess.run(["git", "-C", str(self.workspace), "commit", "-q", "-m", "change evidence"], check=True)

        output = self.run_flow("status", workspace=self.workspace)

        self.assertEqual(output["result"], "ready")

    def test_reviewed_workspace_staleness_is_reported(self):
        self.init("feature")
        self.artifact("brief.md")
        self.transition("discover", ["brief.md"])
        self.run_flow("skip", "--reason", "No discovery needed")
        self.artifact("spec.md", "# Spec\nAC-1: stable\n")
        self.transition("plan", ["spec.md"])
        self.artifact("plan.md")
        self.transition("implement", ["plan.md"])
        self.workspace.joinpath("app.py").write_text("value = 1\n", encoding="utf-8")
        self.artifact("implementation.md")
        self.transition("verify", ["implementation.md"])
        self.artifact("verification.md")
        self.transition("review", ["verification.md"], workspace=self.workspace)
        self.artifact("review.md")
        self.transition("close", ["review.md"], workspace=self.workspace)
        self.workspace.joinpath("app.py").write_text("value = 2\n", encoding="utf-8")

        output = self.run_flow("status", workspace=self.workspace, expected=3)

        self.assertIn("reviewed-workspace-stale", {item["code"] for item in output["violations"]})

    def test_workspace_fingerprint_falls_back_without_git_and_tracks_mode_not_symlink_target(self):
        self.prepare_maintenance_to_implement()
        outside = self.root / "outside.txt"
        outside.write_text("secret-v1\n", encoding="utf-8")
        app = self.workspace / "app.sh"
        app.write_text("#!/bin/sh\n", encoding="utf-8")
        link = self.workspace / "outside-link"
        link.symlink_to(outside)
        self.artifact("implementation.md")
        self.transition("verify", ["implementation.md"])
        self.artifact("verification.md")
        env = {"PATH": ""}
        recorded = self.run_flow(
            "transition",
            "--to",
            "review",
            "--evidence",
            "verification.md",
            "--reason",
            "verified without git",
            workspace=self.workspace,
            env=env,
        )
        self.assertEqual(recorded["result"], "ready")

        outside.write_text("secret-v2\n", encoding="utf-8")
        unchanged = self.run_flow("status", workspace=self.workspace, env=env)
        self.assertEqual(unchanged["result"], "ready")

        app.chmod(0o755)
        changed = self.run_flow("status", workspace=self.workspace, env=env, expected=3)
        self.assertIn("verified-workspace-stale", {item["code"] for item in changed["violations"]})


if __name__ == "__main__":
    unittest.main()
