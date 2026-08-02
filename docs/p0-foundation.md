# P0: Dev Flow Foundation Plan

Status: reviewed P0 baseline

Specification: [`spec.md`](spec.md)

## Goal

Deliver a reusable `dev-flow` skill that follows project-owned tasks and specifications, supports a minimal artifact-root adapter, preserves live task state across work, and requires fresh verification plus independent outcome critique and code review.

## Design sources

- Superpowers (`44c9b2d`): executable plans, review isolation, and evidence before completion claims.
- BMAD Method (`770d4259`): lean project context, configurable artifact roots, and adversarial review with human filtering.
- A mature private-project workflow: separate code/planning Git boundaries; source versus derived specifications; living tasks; durable decisions; open-question cleanup; `plan`, executable, external-check, and delete-on-done semantics.

The source project's exact paths and names remain in its project-local instructions. They are not dependencies or defaults of the universal skill.

## P0 deliverables

- canonical skill specification in `docs/spec.md`;
- concise runtime workflow in `skills/dev-flow/SKILL.md`;
- artifact discovery, semantic roles, lifecycle, safety, and fallback layout in `skills/dev-flow/references/artifacts.md`;
- valid Codex UI metadata;
- one-key project adapter through `.dev-flow.yaml`;
- a live project proof that routes to a nested private planning repository without copying its taxonomy into the skill.

## Acceptance criteria

- Existing project instructions override fallback paths, naming, language, mutability, and retention.
- The skill distinguishes source specs, derived specs, active work, decisions, questions, implementation maps, and review evidence.
- `plan`, `active`, `check`, and `done` have unambiguous transitions.
- Agent-accessible verification cannot be mislabeled as an external gate.
- Completed-item retention is project-defined; the default moves durable outcomes and deletes the transient task without a journal.
- Public/private and nested-repository boundaries are preserved and reported separately.
- Outcome critique and code review remain mandatory independent gates.
- Deterministic skill validation passes.
- Independent critic and code/skill review findings are resolved and re-reviewed.

## Deliberately deferred

- installation or plugin packaging;
- automated artifact generators or config parsers;
- external task-tracker integrations;
- graph-based scheduling or multi-agent claims;
- multi-layer or per-role configuration keys;
- mandatory worktrees, commit cadence, or workflow runtime.
