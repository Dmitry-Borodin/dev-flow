#!/usr/bin/env python3
"""Deterministic state controller for the dev-flow v1 change protocol."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = SKILL_ROOT / "assets" / "workflow-v1.json"
MANIFEST_FIELDS = {
    "contract",
    "workflow_version",
    "revision",
    "id",
    "project",
    "title",
    "kind",
    "risk",
    "lifecycle",
    "current_phase",
    "phases",
    "blockers",
    "provenance",
}
PHASE_FIELDS = {"required", "state", "evidence", "reason"}
PROVENANCE_FIELDS = {"plan_inputs", "verified_workspace", "reviewed_workspace"}
TERMINAL_LIFECYCLES = {"done", "cancelled", "superseded"}
HEALTH_PRIORITY = {"consistent": 0, "stale": 1, "inconsistent": 2, "invalid": 3}
DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
FINGERPRINT_PATTERN = re.compile(r"^[0-9a-f]{64}$")
PLACEHOLDER_PATTERN = re.compile(r"\b(?:TBD|TODO|FIXME)\b", re.IGNORECASE)
BLOCKER_FIELDS = {"id", "kind", "message", "status", "opened_at", "closed_at", "resolution"}
EVENT_FIELDS = {
    "create": {"phase", "kind"},
    "transition": {"from", "to", "evidence", "reason"},
    "skip": {"phase", "to", "reason"},
    "block": {"phase", "blocker_id", "kind", "message"},
    "unblock": {"blocker_id", "reason"},
    "rewind": {"from", "to", "reason"},
    "terminate": {"from", "to", "reason"},
}


class FlowError(Exception):
    def __init__(self, code: str, message: str, *, result: str = "invalid", exit_code: int = 2):
        super().__init__(message)
        self.code = code
        self.message = message
        self.result = result
        self.exit_code = exit_code


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise FlowError("usage-error", message)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_workflow() -> dict[str, Any]:
    with WORKFLOW_PATH.open(encoding="utf-8") as source:
        return json.load(source)


WORKFLOW = load_workflow()
PHASES = WORKFLOW["phases"]


def read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as source:
            value = json.load(source)
    except FileNotFoundError as error:
        raise FlowError(f"{label}-missing", f"{path} does not exist") from error
    except (OSError, json.JSONDecodeError) as error:
        raise FlowError(f"{label}-invalid", f"Cannot read {path}: {error}") from error
    if not isinstance(value, dict):
        raise FlowError(f"{label}-invalid", f"{path} must contain a JSON object")
    return value


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def valid_timestamp(value: Any) -> bool:
    if not nonempty(value):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def valid_fingerprint(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and set(value) == {"algorithm", "value", "source"}
        and value.get("algorithm") == "sha256"
        and isinstance(value.get("value"), str)
        and FINGERPRINT_PATTERN.fullmatch(value["value"]) is not None
        and value.get("source") in {"git", "files"}
    )


def artifact_has_placeholder(path: Path) -> bool:
    try:
        return PLACEHOLDER_PATTERN.search(path.read_text(encoding="utf-8")) is not None
    except (OSError, UnicodeError):
        return True


def run_git(workspace: Path, *args: str) -> bytes | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(workspace), *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except OSError:
        return None
    return result.stdout if result.returncode == 0 else None


def workspace_fingerprint(workspace: Path, change: Path) -> dict[str, str]:
    workspace = workspace.resolve()
    excluded = change.absolute()
    if not workspace.is_dir():
        raise FlowError("workspace-missing", f"Workspace is not a directory: {workspace}")

    def include(path: Path) -> bool:
        try:
            path.absolute().relative_to(excluded)
            return False
        except ValueError:
            return True

    digest = hashlib.sha256()
    git_root_raw = run_git(workspace, "rev-parse", "--show-toplevel")
    if git_root_raw is not None:
        root = Path(os.fsdecode(git_root_raw).strip()).resolve()
        files_raw = run_git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard") or b""
        relative_paths = sorted(
            os.fsdecode(item)
            for item in files_raw.split(b"\0")
            if item and include(root / os.fsdecode(item))
        )
        digest.update(b"git\0")
        source = "git"
    else:
        root = workspace
        relative_paths = sorted(
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if (path.is_file() or path.is_symlink())
            and ".git" not in path.parts
            and "__pycache__" not in path.parts
            and path.suffix != ".pyc"
            and include(path)
        )
        digest.update(b"files\0")
        source = "files"

    for relative in relative_paths:
        path = root / relative
        digest.update(relative.encode("utf-8", errors="surrogateescape") + b"\0")
        try:
            path_stat = path.lstat()
        except OSError:
            digest.update(b"missing\0")
            continue
        digest.update(f"{stat.S_IFMT(path_stat.st_mode):o}:{stat.S_IMODE(path_stat.st_mode):o}".encode() + b"\0")
        if path.is_symlink():
            digest.update(os.fsencode(os.readlink(path)))
        elif path.is_file():
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
        elif path.is_dir():
            digest.update(run_git(path, "rev-parse", "HEAD") or b"directory")
        else:
            digest.update(b"missing")
        digest.update(b"\0")

    return {"algorithm": "sha256", "value": digest.hexdigest(), "source": source}


def violation(code: str, message: str, health: str) -> dict[str, str]:
    return {"code": code, "message": message, "health": health}


def add_violation(items: list[dict[str, str]], code: str, message: str, health: str) -> None:
    items.append(violation(code, message, health))


def validate_evidence_path(change: Path, value: Any) -> tuple[str | None, str | None]:
    if not isinstance(value, str) or not value:
        return None, "Evidence paths must be non-empty strings"
    raw = Path(value)
    if raw.is_absolute():
        return None, f"Evidence path must be relative: {value}"
    root = change.resolve()
    candidate = (root / raw).resolve()
    try:
        relative = candidate.relative_to(root).as_posix()
    except ValueError:
        return None, f"Evidence path escapes the change directory: {value}"
    if not candidate.is_file():
        return None, f"Evidence file does not exist: {value}"
    return relative, None


def structural_violations(manifest: dict[str, Any], change: Path) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    unknown = sorted(set(manifest) - MANIFEST_FIELDS)
    missing = sorted(MANIFEST_FIELDS - set(manifest))
    if unknown:
        add_violation(items, "unknown-manifest-field", f"Unknown fields: {', '.join(unknown)}", "invalid")
    if missing:
        add_violation(items, "missing-manifest-field", f"Missing fields: {', '.join(missing)}", "invalid")
    if missing:
        return items

    if manifest["contract"] != "dev-flow/change/v1":
        add_violation(items, "contract-mismatch", "contract must be dev-flow/change/v1", "invalid")
    if manifest["workflow_version"] != WORKFLOW["version"]:
        add_violation(items, "workflow-version-mismatch", "workflow_version is not supported", "invalid")
    if not isinstance(manifest["revision"], int) or isinstance(manifest["revision"], bool) or manifest["revision"] < 1:
        add_violation(items, "revision-invalid", "revision must be a positive integer", "invalid")
    for field in ("id", "project", "title"):
        if not nonempty(manifest[field]):
            add_violation(items, f"{field}-invalid", f"{field} must be a non-empty string", "invalid")
    if not isinstance(manifest["kind"], str) or manifest["kind"] not in WORKFLOW["profiles"]:
        add_violation(items, "kind-invalid", "kind is not a workflow profile", "invalid")
    if not isinstance(manifest["risk"], str) or manifest["risk"] not in {"low", "medium", "high"}:
        add_violation(items, "risk-invalid", "risk must be low, medium, or high", "invalid")
    if not isinstance(manifest["lifecycle"], str) or manifest["lifecycle"] not in WORKFLOW["lifecycles"]:
        add_violation(items, "lifecycle-invalid", "lifecycle is not recognized", "invalid")
    if manifest["current_phase"] is not None and (
        not isinstance(manifest["current_phase"], str) or manifest["current_phase"] not in PHASES
    ):
        add_violation(items, "current-phase-invalid", "current_phase is not recognized", "invalid")

    phases = manifest["phases"]
    if not isinstance(phases, dict):
        add_violation(items, "phases-invalid", "phases must be an object", "invalid")
    else:
        if set(phases) != set(PHASES):
            add_violation(items, "phase-id-mismatch", "phase keys must match workflow v1", "invalid")
        for phase_name in set(phases) & set(PHASES):
            phase = phases[phase_name]
            if not isinstance(phase, dict):
                add_violation(items, "phase-invalid", f"{phase_name} must be an object", "invalid")
                continue
            extra = sorted(set(phase) - PHASE_FIELDS)
            if extra:
                add_violation(items, "unknown-phase-field", f"{phase_name} has unknown fields: {', '.join(extra)}", "invalid")
            if set(phase) & {"required", "state", "evidence"} != {"required", "state", "evidence"}:
                add_violation(items, "phase-field-missing", f"{phase_name} lacks required fields", "invalid")
                continue
            if not isinstance(phase["required"], bool):
                add_violation(items, "phase-required-invalid", f"{phase_name}.required must be boolean", "invalid")
            if phase["state"] not in WORKFLOW["phase_states"]:
                add_violation(items, "phase-state-invalid", f"{phase_name}.state is invalid", "invalid")
            if not isinstance(phase["evidence"], list) or not all(isinstance(item, str) for item in phase["evidence"]):
                add_violation(items, "phase-evidence-invalid", f"{phase_name}.evidence must be a string array", "invalid")
                continue
            if len(phase["evidence"]) != len(set(phase["evidence"])):
                add_violation(items, "phase-evidence-duplicate", f"{phase_name}.evidence contains duplicates", "invalid")
            if "reason" in phase and not nonempty(phase["reason"]):
                add_violation(items, "phase-reason-invalid", f"{phase_name}.reason must be non-empty", "invalid")
            if phase["state"] == "passed":
                if not phase["evidence"]:
                    add_violation(items, "passed-without-evidence", f"{phase_name} passed without evidence", "inconsistent")
                expected_evidence = WORKFLOW["evidence"][phase_name]
                if expected_evidence not in phase["evidence"]:
                    add_violation(
                        items,
                        "phase-evidence-required",
                        f"{phase_name} must include {expected_evidence}",
                        "inconsistent",
                    )
                for evidence in phase["evidence"]:
                    normalized, error = validate_evidence_path(change, evidence)
                    if error:
                        add_violation(items, "evidence-missing", f"{phase_name}: {error}", "inconsistent")
                    elif normalized == expected_evidence and artifact_has_placeholder(change / normalized):
                        add_violation(
                            items,
                            "evidence-placeholder",
                            f"{phase_name} evidence contains a placeholder: {expected_evidence}",
                            "inconsistent",
                        )
            if phase["state"] == "skipped":
                if phase["required"]:
                    add_violation(items, "required-phase-skipped", f"{phase_name} is required but skipped", "inconsistent")
                if not nonempty(phase.get("reason")):
                    add_violation(items, "skip-reason-missing", f"{phase_name} skipped without a reason", "inconsistent")

    blockers = manifest["blockers"]
    if not isinstance(blockers, list):
        add_violation(items, "blockers-invalid", "blockers must be an array", "invalid")
        blockers = []
    else:
        ids: set[str] = set()
        for blocker in blockers:
            if not isinstance(blocker, dict):
                add_violation(items, "blocker-invalid", "blocker must be an object", "invalid")
                continue
            extra = sorted(set(blocker) - BLOCKER_FIELDS)
            if extra:
                add_violation(items, "blocker-field-unknown", f"Blocker has unknown fields: {', '.join(extra)}", "invalid")
            required = {"id", "kind", "message", "status", "opened_at"}
            if not required <= set(blocker):
                add_violation(items, "blocker-field-missing", "blocker lacks required fields", "invalid")
                continue
            if not all(nonempty(blocker.get(field)) for field in ("id", "kind", "message")):
                add_violation(items, "blocker-value-invalid", "Blocker ID, kind, and message must be non-empty", "invalid")
                continue
            if not valid_timestamp(blocker.get("opened_at")):
                add_violation(items, "blocker-timestamp-invalid", f"Invalid opened_at for {blocker['id']}", "invalid")
            if blocker["id"] in ids:
                add_violation(items, "blocker-id-duplicate", f"Duplicate blocker ID: {blocker['id']}", "invalid")
            ids.add(blocker["id"])
            if not isinstance(blocker["status"], str) or blocker["status"] not in {"open", "closed"}:
                add_violation(items, "blocker-status-invalid", f"Invalid blocker status: {blocker['status']}", "invalid")
                continue
            if blocker["status"] == "closed" and not all(blocker.get(key) for key in ("closed_at", "resolution")):
                add_violation(items, "blocker-closure-incomplete", f"Closed blocker {blocker['id']} lacks closure data", "inconsistent")
            if blocker["status"] == "closed" and (
                not valid_timestamp(blocker.get("closed_at")) or not nonempty(blocker.get("resolution"))
            ):
                add_violation(items, "blocker-closure-invalid", f"Closed blocker {blocker['id']} has invalid closure data", "invalid")
            if blocker["status"] == "open" and ({"closed_at", "resolution"} & set(blocker)):
                add_violation(items, "blocker-open-has-closure", f"Open blocker {blocker['id']} has closure data", "invalid")

    provenance = manifest["provenance"]
    if not isinstance(provenance, dict) or set(provenance) != PROVENANCE_FIELDS:
        add_violation(items, "provenance-invalid", "provenance fields do not match v1", "invalid")
    else:
        plan_inputs = provenance["plan_inputs"]
        if not isinstance(plan_inputs, dict):
            add_violation(items, "plan-inputs-invalid", "plan_inputs must be an object", "invalid")
        else:
            for name, digest in plan_inputs.items():
                if not nonempty(name) or not isinstance(digest, str) or DIGEST_PATTERN.fullmatch(digest) is None:
                    add_violation(items, "plan-input-digest-invalid", f"Invalid plan input digest: {name!r}", "invalid")
        for field in ("verified_workspace", "reviewed_workspace"):
            value = provenance[field]
            if value is not None and not valid_fingerprint(value):
                add_violation(items, "workspace-fingerprint-invalid", f"Invalid provenance field: {field}", "invalid")

    phase_objects = (
        isinstance(phases, dict)
        and set(PHASES) <= set(phases)
        and all(isinstance(phases[name], dict) for name in PHASES)
    )
    if phase_objects:
        active = [name for name in PHASES if phases[name].get("state") == "active"]
        lifecycle = manifest["lifecycle"]
        current = manifest["current_phase"]
        if lifecycle in {"active", "blocked"}:
            if len(active) != 1:
                add_violation(items, "active-phase-count", f"Expected one active phase, found {len(active)}", "inconsistent")
            if len(active) == 1 and current != active[0]:
                add_violation(items, "current-phase-mismatch", "current_phase does not match the active phase", "inconsistent")
        elif lifecycle in TERMINAL_LIFECYCLES:
            if active or current is not None:
                add_violation(items, "terminal-phase-active", "Terminal lifecycle cannot have an active phase", "inconsistent")

        open_blockers = [blocker for blocker in blockers if isinstance(blocker, dict) and blocker.get("status") == "open"]
        if lifecycle == "blocked" and not open_blockers:
            add_violation(items, "blocked-without-blocker", "Blocked lifecycle requires an open blocker", "inconsistent")
        if lifecycle == "active" and open_blockers:
            add_violation(items, "active-with-blocker", "Active lifecycle cannot have an open blocker", "inconsistent")
        if lifecycle == "done":
            if open_blockers:
                add_violation(items, "done-with-blocker", "Done lifecycle cannot have an open blocker", "inconsistent")
            if phases["close"].get("state") != "passed":
                add_violation(items, "done-without-close", "Done requires close=passed", "inconsistent")
            for name in PHASES:
                phase = phases[name]
                if phase.get("state") not in {"passed", "skipped"}:
                    add_violation(items, "terminal-phase-incomplete", f"Terminal phase is incomplete: {name}", "inconsistent")
                if phase.get("required") and phase.get("state") != "passed":
                    add_violation(items, "required-phase-incomplete", f"Required phase is incomplete: {name}", "inconsistent")

        provenance = manifest["provenance"]
        if isinstance(provenance, dict):
            if phases["verify"].get("state") == "passed" and provenance.get("verified_workspace") is None:
                add_violation(items, "verified-provenance-missing", "Passed verify requires workspace provenance", "inconsistent")
            if phases["review"].get("state") == "passed" and provenance.get("reviewed_workspace") is None:
                add_violation(items, "reviewed-provenance-missing", "Passed review requires workspace provenance", "inconsistent")

        if current in PHASES:
            current_index = PHASES.index(current)
            for name in PHASES[:current_index]:
                if phases[name].get("state") not in {"passed", "skipped"}:
                    add_violation(items, "phase-order-invalid", f"Upstream phase is incomplete: {name}", "inconsistent")
            for name in PHASES[current_index + 1 :]:
                if phases[name].get("state") != "pending":
                    add_violation(items, "phase-order-invalid", f"Downstream phase is not pending: {name}", "inconsistent")

    return items


def event_envelope_violations(event: dict[str, Any], label: str) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    action = event.get("action")
    base = {"at", "action", "actor", "revision"}
    if not isinstance(action, str) or action not in EVENT_FIELDS:
        return [violation("event-envelope-invalid", f"{label} has an invalid action", "invalid")]
    expected = base | EVENT_FIELDS[action]
    if set(event) != expected:
        add_violation(items, "event-envelope-invalid", f"{label} fields do not match action {action}", "invalid")
    if not valid_timestamp(event.get("at")) or not nonempty(event.get("actor")):
        add_violation(items, "event-envelope-invalid", f"{label} has invalid time or actor", "invalid")
    if not isinstance(event.get("revision"), int) or isinstance(event.get("revision"), bool) or event["revision"] < 1:
        add_violation(items, "event-envelope-invalid", f"{label} has an invalid revision", "invalid")
    for field in EVENT_FIELDS[action] - {"evidence"}:
        if not nonempty(event.get(field)):
            add_violation(items, "event-envelope-invalid", f"{label}.{field} must be non-empty", "invalid")
    if "evidence" in expected and (
        not isinstance(event.get("evidence"), list)
        or not event["evidence"]
        or not all(nonempty(item) for item in event["evidence"])
    ):
        add_violation(items, "event-envelope-invalid", f"{label}.evidence must be a non-empty string array", "invalid")
    return items


def event_violations(change: Path, manifest: dict[str, Any]) -> list[dict[str, str]]:
    path = change / "events.jsonl"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        return [violation("event-log-missing", f"Cannot read {path}: {error}", "inconsistent")]
    events: list[dict[str, Any]] = []
    for number, line in enumerate(lines, 1):
        try:
            event = json.loads(line)
        except json.JSONDecodeError as error:
            return [violation("event-json-invalid", f"Invalid event at line {number}: {error}", "invalid")]
        if not isinstance(event, dict):
            return [violation("event-invalid", f"Event at line {number} is not an object", "invalid")]
        envelope = event_envelope_violations(event, f"Event at line {number}")
        if envelope:
            return envelope
        events.append(event)
    revisions = [event.get("revision") for event in events]
    expected = list(range(1, manifest.get("revision", 0) + 1)) if isinstance(manifest.get("revision"), int) else []
    if revisions != expected:
        return [violation("event-revision-mismatch", f"Event revisions {revisions} do not match {expected}", "inconsistent")]
    if not events or events[0]["action"] != "create" or events[0]["revision"] != 1:
        return [violation("event-state-mismatch", "Event history must start with create revision 1", "inconsistent")]

    first = events[0]
    current = first["phase"]
    lifecycle = "active"
    replayed_blockers: dict[str, dict[str, str]] = {}
    if current != "frame" or first["kind"] != manifest.get("kind"):
        return [violation("event-state-mismatch", "Create event does not match initialized state", "inconsistent")]

    for event in events[1:]:
        action = event["action"]
        if action == "create":
            return [violation("event-state-mismatch", "Create may appear only once", "inconsistent")]
        if action == "transition":
            if lifecycle != "active" or event["from"] != current:
                return [violation("event-state-mismatch", "Transition source does not match replayed state", "inconsistent")]
            target = event["to"]
            if current not in WORKFLOW["transitions"] or target not in WORKFLOW["transitions"][current]:
                return [violation("event-state-mismatch", "Transition is not legal in workflow v1", "inconsistent")]
            if target == "done":
                lifecycle, current = "done", None
            else:
                current = target
        elif action == "skip":
            if lifecycle != "active" or event["phase"] != current:
                return [violation("event-state-mismatch", "Skip phase does not match replayed state", "inconsistent")]
            index = PHASES.index(current) if current in PHASES else -1
            expected_target = PHASES[index + 1] if 0 <= index < len(PHASES) - 1 else None
            if event["to"] != expected_target:
                return [violation("event-state-mismatch", "Skip target is not the next phase", "inconsistent")]
            current = event["to"]
        elif action == "block":
            blocker_id = event["blocker_id"]
            if lifecycle not in {"active", "blocked"} or event["phase"] != current or blocker_id in replayed_blockers:
                return [violation("event-state-mismatch", "Block event does not match replayed state", "inconsistent")]
            replayed_blockers[blocker_id] = {
                "kind": event["kind"],
                "message": event["message"],
                "status": "open",
            }
            lifecycle = "blocked"
        elif action == "unblock":
            blocker = replayed_blockers.get(event["blocker_id"])
            if lifecycle != "blocked" or blocker is None or blocker["status"] != "open":
                return [violation("event-state-mismatch", "Unblock target is not an open replayed blocker", "inconsistent")]
            blocker["status"] = "closed"
            blocker["resolution"] = event["reason"]
            if not any(item["status"] == "open" for item in replayed_blockers.values()):
                lifecycle = "active"
        elif action == "rewind":
            if lifecycle != "active" or event["from"] != current:
                return [violation("event-state-mismatch", "Rewind source does not match replayed state", "inconsistent")]
            if current not in WORKFLOW["rewinds"] or event["to"] not in WORKFLOW["rewinds"][current]:
                return [violation("event-state-mismatch", "Rewind is not legal in workflow v1", "inconsistent")]
            current = event["to"]
        elif action == "terminate":
            if lifecycle not in {"active", "blocked"} or event["from"] != current or event["to"] not in {"cancelled", "superseded"}:
                return [violation("event-state-mismatch", "Termination does not match replayed state", "inconsistent")]
            lifecycle, current = event["to"], None

    manifest_blockers = {
        item["id"]: item
        for item in manifest.get("blockers", [])
        if isinstance(item, dict) and nonempty(item.get("id"))
    }
    if set(manifest_blockers) != set(replayed_blockers):
        return [violation("event-state-mismatch", "Blocker IDs do not match event history", "inconsistent")]
    for blocker_id, replayed in replayed_blockers.items():
        recorded = manifest_blockers[blocker_id]
        if any(recorded.get(field) != replayed.get(field) for field in ("kind", "message", "status")):
            return [violation("event-state-mismatch", f"Blocker {blocker_id} does not match event history", "inconsistent")]
        if replayed["status"] == "closed" and recorded.get("resolution") != replayed.get("resolution"):
            return [violation("event-state-mismatch", f"Blocker {blocker_id} resolution does not match events", "inconsistent")]
    if manifest.get("lifecycle") != lifecycle or manifest.get("current_phase") != current:
        return [violation("event-state-mismatch", "Manifest lifecycle does not match event history", "inconsistent")]
    return []


def stale_violations(manifest: dict[str, Any], change: Path, workspace: Path | None) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    if manifest.get("lifecycle") in TERMINAL_LIFECYCLES:
        return items
    provenance = manifest.get("provenance")
    if not isinstance(provenance, dict):
        return items
    recorded_spec = provenance.get("plan_inputs", {}).get("spec.md") if isinstance(provenance.get("plan_inputs"), dict) else None
    if recorded_spec:
        spec = change / "spec.md"
        current_spec = digest_file(spec) if spec.is_file() else None
        if current_spec != recorded_spec:
            add_violation(items, "plan-input-stale", "plan.md was produced from a different spec.md", "stale")
    verified = provenance.get("verified_workspace")
    reviewed = provenance.get("reviewed_workspace")
    if workspace is None and (verified is not None or reviewed is not None):
        add_violation(items, "workspace-required", "Current workspace is required to validate recorded provenance", "inconsistent")
    elif workspace is not None:
        current_workspace = workspace_fingerprint(workspace, change)
        if verified is not None and verified != current_workspace:
            add_violation(items, "verified-workspace-stale", "Verification targets a different workspace state", "stale")
        if reviewed is not None and reviewed != current_workspace:
            add_violation(items, "reviewed-workspace-stale", "Review targets a different workspace state", "stale")
    return items


def health_for(items: list[dict[str, str]]) -> str:
    if not items:
        return "consistent"
    return max((item["health"] for item in items), key=HEALTH_PRIORITY.__getitem__)


def public_violations(items: list[dict[str, str]]) -> list[dict[str, str]]:
    return [{"code": item["code"], "message": item["message"]} for item in items]


def next_action(manifest: dict[str, Any], result: str, items: list[dict[str, str]]) -> dict[str, Any] | None:
    codes = {item["code"] for item in items}
    if result == "stale":
        if "plan-input-stale" in codes:
            return {"kind": "rewind", "phase": "plan"}
        if "verified-workspace-stale" in codes:
            return {"kind": "rewind", "phase": "verify"}
        return {"kind": "rewind", "phase": "review"}
    if result in {"invalid", "inconsistent"}:
        if "workspace-required" in codes:
            return {"kind": "provide-workspace"}
        return {"kind": "repair-state"}
    if result == "blocked":
        return {"kind": "resolve-blocker"}
    if result in {"complete", "terminated"}:
        return None
    phase = manifest["current_phase"]
    return {"kind": "execute-phase", "phase": phase, "reference": f"references/phase-{phase}.md"}


def diagnose(change: Path, workspace: Path | None = None) -> tuple[dict[str, Any], int]:
    manifest = read_json(change / "change.json", "manifest")
    items = structural_violations(manifest, change)
    if not any(item["health"] == "invalid" for item in items):
        items.extend(event_violations(change, manifest))
    mechanical_health = health_for(items)
    if mechanical_health == "consistent":
        items.extend(stale_violations(manifest, change, workspace))
    health = health_for(items)
    if health == "invalid":
        result, exit_code = "invalid", 2
    elif health == "inconsistent":
        result, exit_code = "inconsistent", 2
    elif health == "stale":
        result, exit_code = "stale", 3
    elif manifest["lifecycle"] == "blocked":
        result, exit_code = "blocked", 0
    elif manifest["lifecycle"] == "done":
        result, exit_code = "complete", 0
    elif manifest["lifecycle"] in TERMINAL_LIFECYCLES:
        result, exit_code = "terminated", 0
    else:
        result, exit_code = "ready", 0
    open_blockers = [item for item in manifest.get("blockers", []) if isinstance(item, dict) and item.get("status") == "open"]
    payload = {
        "result": result,
        "project": manifest.get("project"),
        "change_id": manifest.get("id"),
        "lifecycle": manifest.get("lifecycle"),
        "current_phase": manifest.get("current_phase"),
        "health": health,
        "revision": manifest.get("revision"),
        "violations": public_violations(items),
        "blockers": open_blockers,
    }
    payload["next_action"] = next_action(manifest, result, items)
    return payload, exit_code


def load_ready(change: Path, workspace: Path | None, allowed_results: set[str]) -> tuple[dict[str, Any] | None, tuple[dict[str, Any], int] | None]:
    status = diagnose(change, workspace)
    if status[0]["result"] not in allowed_results:
        payload = {
            "result": "invalid",
            "error": "state-not-ready",
            "message": f"Command cannot run while status is {status[0]['result']}",
            "status": status[0],
        }
        return None, (payload, 2)
    return read_json(change / "change.json", "manifest"), None


def atomic_write(path: Path, content: str) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False) as target:
        target.write(content)
        target.flush()
        os.fsync(target.fileno())
        return Path(target.name)


def commit_mutation(change: Path, manifest: dict[str, Any], event: dict[str, Any]) -> None:
    candidate_issues = structural_violations(manifest, change) + event_envelope_violations(event, "New event")
    if candidate_issues:
        issue = candidate_issues[0]
        raise FlowError("candidate-invalid", f"{issue['code']}: {issue['message']}")
    manifest_path = change / "change.json"
    events_path = change / "events.jsonl"
    old_events = events_path.read_text(encoding="utf-8") if events_path.exists() else ""
    manifest_content = json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    event_content = old_events + json.dumps(event, sort_keys=True, ensure_ascii=False) + "\n"
    manifest_temp: Path | None = None
    events_temp: Path | None = None
    try:
        manifest_temp = atomic_write(manifest_path, manifest_content)
        events_temp = atomic_write(events_path, event_content)
        os.replace(events_temp, events_path)
        os.replace(manifest_temp, manifest_path)
        if hasattr(os, "O_DIRECTORY"):
            directory = os.open(change, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
    finally:
        if manifest_temp is not None:
            manifest_temp.unlink(missing_ok=True)
        if events_temp is not None:
            events_temp.unlink(missing_ok=True)


def new_event(manifest: dict[str, Any], action: str, **details: Any) -> dict[str, Any]:
    return {"at": utc_now(), "action": action, "actor": "agent", "revision": manifest["revision"], **details}


def bump(manifest: dict[str, Any]) -> None:
    manifest["revision"] += 1


def command_init(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    change = args.change
    if (change / "change.json").exists() or (change / "events.jsonl").exists():
        raise FlowError("change-exists", f"Change state already exists in {change}")
    change.mkdir(parents=True, exist_ok=True)
    profile = WORKFLOW["profiles"][args.kind]
    phases = {
        name: {"required": profile[name], "state": "active" if name == "frame" else "pending", "evidence": []}
        for name in PHASES
    }
    manifest = {
        "contract": "dev-flow/change/v1",
        "workflow_version": WORKFLOW["version"],
        "revision": 1,
        "id": args.id,
        "project": args.project,
        "title": args.title,
        "kind": args.kind,
        "risk": args.risk,
        "lifecycle": "active",
        "current_phase": "frame",
        "phases": phases,
        "blockers": [],
        "provenance": {"plan_inputs": {}, "verified_workspace": None, "reviewed_workspace": None},
    }
    event = new_event(manifest, "create", phase="frame", kind=args.kind)
    commit_mutation(change, manifest, event)
    return diagnose(change, args.workspace)


def normalize_evidence(change: Path, phase: str, values: list[str]) -> list[str]:
    normalized: list[str] = []
    for value in values:
        path, error = validate_evidence_path(change, value)
        if error:
            code = "evidence-outside-change" if "escapes" in error or "relative" in error else "evidence-missing"
            raise FlowError(code, error)
        if path not in normalized:
            normalized.append(path)
    if not normalized:
        raise FlowError("evidence-required", "At least one evidence file is required")
    expected = WORKFLOW["evidence"][phase]
    if expected not in normalized:
        raise FlowError("phase-evidence-required", f"Passing {phase} requires {expected}")
    if artifact_has_placeholder(change / expected):
        raise FlowError("evidence-placeholder", f"{expected} contains TBD, TODO, or FIXME")
    return normalized


def command_transition(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    manifest, blocked = load_ready(args.change, args.workspace, {"ready"})
    if blocked:
        return blocked
    assert manifest is not None
    current = manifest["current_phase"]
    if args.to not in WORKFLOW["transitions"][current]:
        raise FlowError("transition-illegal", f"Cannot transition from {current} to {args.to}")
    evidence = normalize_evidence(args.change, current, args.evidence)
    if current in {"verify", "review"} and args.workspace is None:
        raise FlowError("workspace-required", f"Passing {current} requires --workspace")

    manifest["phases"][current]["state"] = "passed"
    manifest["phases"][current]["evidence"] = evidence
    manifest["phases"][current].pop("reason", None)
    if current == "plan":
        spec = args.change / "spec.md"
        manifest["provenance"]["plan_inputs"] = {"spec.md": digest_file(spec)} if spec.is_file() else {}
    if current == "verify":
        manifest["provenance"]["verified_workspace"] = workspace_fingerprint(args.workspace, args.change)
    if current == "review":
        manifest["provenance"]["reviewed_workspace"] = workspace_fingerprint(args.workspace, args.change)

    if args.to == "done":
        manifest["lifecycle"] = "done"
        manifest["current_phase"] = None
    else:
        manifest["phases"][args.to]["state"] = "active"
        manifest["current_phase"] = args.to
    bump(manifest)
    event = new_event(manifest, "transition", **{"from": current, "to": args.to, "evidence": evidence, "reason": args.reason})
    commit_mutation(args.change, manifest, event)
    return diagnose(args.change, args.workspace)


def command_skip(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    manifest, blocked = load_ready(args.change, args.workspace, {"ready"})
    if blocked:
        return blocked
    assert manifest is not None
    current = manifest["current_phase"]
    phase = manifest["phases"][current]
    if phase["required"]:
        raise FlowError("required-phase", f"Required phase cannot be skipped: {current}")
    current_index = PHASES.index(current)
    if current_index == len(PHASES) - 1:
        raise FlowError("skip-illegal", "close cannot be skipped")
    target = PHASES[current_index + 1]
    phase["state"] = "skipped"
    phase["evidence"] = []
    phase["reason"] = args.reason
    manifest["phases"][target]["state"] = "active"
    manifest["current_phase"] = target
    bump(manifest)
    commit_mutation(args.change, manifest, new_event(manifest, "skip", phase=current, to=target, reason=args.reason))
    return diagnose(args.change, args.workspace)


def command_block(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    manifest, blocked = load_ready(args.change, args.workspace, {"ready", "blocked"})
    if blocked:
        return blocked
    assert manifest is not None
    used = [int(item["id"][2:]) for item in manifest["blockers"] if item.get("id", "").startswith("B-") and item["id"][2:].isdigit()]
    blocker_id = f"B-{max(used, default=0) + 1}"
    manifest["blockers"].append(
        {"id": blocker_id, "kind": args.kind, "message": args.message, "status": "open", "opened_at": utc_now()}
    )
    manifest["lifecycle"] = "blocked"
    bump(manifest)
    commit_mutation(
        args.change,
        manifest,
        new_event(manifest, "block", phase=manifest["current_phase"], blocker_id=blocker_id, kind=args.kind, message=args.message),
    )
    return diagnose(args.change, args.workspace)


def command_unblock(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    manifest, blocked = load_ready(args.change, args.workspace, {"blocked"})
    if blocked:
        return blocked
    assert manifest is not None
    target = next((item for item in manifest["blockers"] if item.get("id") == args.id and item.get("status") == "open"), None)
    if target is None:
        raise FlowError("blocker-not-open", f"No open blocker with ID {args.id}")
    target["status"] = "closed"
    target["closed_at"] = utc_now()
    target["resolution"] = args.reason
    if not any(item.get("status") == "open" for item in manifest["blockers"]):
        manifest["lifecycle"] = "active"
    bump(manifest)
    commit_mutation(args.change, manifest, new_event(manifest, "unblock", blocker_id=args.id, reason=args.reason))
    return diagnose(args.change, args.workspace)


def clear_phase(phase: dict[str, Any]) -> None:
    phase["state"] = "pending"
    phase["evidence"] = []
    phase.pop("reason", None)


def command_rewind(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    manifest, blocked = load_ready(args.change, args.workspace, {"ready", "stale"})
    if blocked:
        return blocked
    assert manifest is not None
    current = manifest["current_phase"]
    if args.to not in WORKFLOW["rewinds"][current]:
        raise FlowError("rewind-illegal", f"Cannot rewind from {current} to {args.to}")
    target_index = PHASES.index(args.to)
    for name in PHASES[target_index:]:
        clear_phase(manifest["phases"][name])
    manifest["phases"][args.to]["state"] = "active"
    manifest["current_phase"] = args.to
    if target_index <= PHASES.index("plan"):
        manifest["provenance"]["plan_inputs"] = {}
    if target_index <= PHASES.index("verify"):
        manifest["provenance"]["verified_workspace"] = None
        manifest["provenance"]["reviewed_workspace"] = None
    elif target_index == PHASES.index("review"):
        manifest["provenance"]["reviewed_workspace"] = None
    bump(manifest)
    commit_mutation(args.change, manifest, new_event(manifest, "rewind", **{"from": current, "to": args.to, "reason": args.reason}))
    return diagnose(args.change, args.workspace)


def nonempty_arg(value: str) -> str:
    value = value.strip()
    if not value:
        raise argparse.ArgumentTypeError("value must be non-empty")
    return value


def path_arg(value: str) -> Path:
    return Path(nonempty_arg(value)).expanduser().resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = JsonArgumentParser(description=__doc__)
    parser.add_argument("--change", type=path_arg, required=True)
    parser.add_argument("--workspace", type=path_arg)
    commands = parser.add_subparsers(dest="command", required=True, parser_class=JsonArgumentParser)

    init = commands.add_parser("init")
    init.add_argument("--id", type=nonempty_arg, required=True)
    init.add_argument("--project", type=nonempty_arg, required=True)
    init.add_argument("--title", type=nonempty_arg, required=True)
    init.add_argument("--kind", choices=sorted(WORKFLOW["profiles"]), required=True)
    init.add_argument("--risk", choices=["low", "medium", "high"], default="medium")
    init.set_defaults(handler=command_init)

    for name in ("validate", "status"):
        command = commands.add_parser(name)
        command.set_defaults(handler=lambda args: diagnose(args.change, args.workspace))

    transition = commands.add_parser("transition")
    transition.add_argument("--to", choices=PHASES + ["done"], required=True)
    transition.add_argument("--evidence", nargs="+", required=True)
    transition.add_argument("--reason", type=nonempty_arg, required=True)
    transition.set_defaults(handler=command_transition)

    skip = commands.add_parser("skip")
    skip.add_argument("--reason", type=nonempty_arg, required=True)
    skip.set_defaults(handler=command_skip)

    block = commands.add_parser("block")
    block.add_argument("--kind", type=nonempty_arg, required=True)
    block.add_argument("--message", type=nonempty_arg, required=True)
    block.set_defaults(handler=command_block)

    unblock = commands.add_parser("unblock")
    unblock.add_argument("--id", type=nonempty_arg, required=True)
    unblock.add_argument("--reason", type=nonempty_arg, required=True)
    unblock.set_defaults(handler=command_unblock)

    rewind = commands.add_parser("rewind")
    rewind.add_argument("--to", choices=PHASES, required=True)
    rewind.add_argument("--reason", type=nonempty_arg, required=True)
    rewind.set_defaults(handler=command_rewind)
    return parser


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))


def main() -> int:
    try:
        args = build_parser().parse_args()
        payload, exit_code = args.handler(args)
    except FlowError as error:
        payload = {"result": error.result, "error": error.code, "message": error.message}
        exit_code = error.exit_code
    except (OSError, KeyError, TypeError, ValueError) as error:
        payload = {"result": "invalid", "error": "internal-error", "message": str(error)}
        exit_code = 2
    emit(payload)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
