# Dev Flow Skill Specification

Status: P0

## Purpose

`dev-flow` is a reusable Agent Skill for non-trivial project changes. It keeps requirements, live task state, implementation, verification, critique, and code review aligned without replacing a project's existing planning and documentation system.

The skill is technology-agnostic and supports public/private documentation boundaries and nested repositories.

## Authority

Apply instructions in this order:

1. the current user's explicit request and authorization;
2. every project-local instruction file applicable from the code root and resolved artifact root down to the target artifact;
3. this specification and the skill defaults.

Project instructions own artifact names, paths, language, mutability, and retention. `.dev-flow.yaml` routes to an artifact root; it is not a second policy language.

## Artifact-root contract

Resolve the artifact root from an expressly designated user path, then `{project-root}/.dev-flow.yaml`, then the default `{project-root}/docs/dev-flow`.

P0 configuration contains one repo-relative key:

```yaml
artifact_root: private
```

Invalid configuration fails closed. Normal and configured roots must stay inside the project after lexical and canonical resolution. A user may explicitly authorize an exact external destination. Nested Git repositories remain separate change, validation, and reporting boundaries.

## Semantic artifact model

The skill recognizes roles rather than fixed directories:

| Role | Contract |
|---|---|
| Source specification | Authoritative requirements; do not edit without explicit authorization. |
| Derived specification | Project-maintained behavior or design; update with accepted behavior. |
| Current work item | Goal, priority, remaining steps, acceptance, blockers, verification, and review state. |
| Decision reference | Durable accepted decisions and rationale; not a completed-work log. |
| Open questions | Only unresolved questions; answered entries are removed. |
| Implementation map | Current system model and near-term ordering; not a second backlog. |
| Review evidence | Findings, dispositions, fixes, and re-review state; retention is project-defined. |

Projects may combine roles or map them to existing files. The skill must discover and reuse that mapping before creating artifacts.

## Work-item lifecycle

Every non-trivial change has one current work item before implementation begins. Projects choose the filename or status representation; the semantic states are:

- **plan** — an unresolved design choice, authorization question, or operator decision remains;
- **active** — the work is executable now;
- **check** — implementation is complete and only genuinely external verification remains;
- **done** — acceptance evidence exists and no blocking work remains.

Executable slices must not remain blocked behind a plan-only decision. Checks available to the agent through project tools, disposable environments, or allocated test systems remain active work rather than external gates.

| From | Condition | To |
|---|---|---|
| plan | Blocking decisions are resolved | active |
| active | A new blocking decision appears | plan |
| active | Implementation and all agent-accessible checks pass; only external verification remains | check |
| check | External verification fails without a new decision | active |
| check | External verification exposes a new decision | plan |
| check | External verification passes | done, then retention |
| active | All acceptance evidence exists and no external gate is required | done, then retention |

`done` is transient and cannot coexist with an external gate. On completion, move durable outcomes into decision references or derived specifications, then immediately apply the project's close/archive/delete policy. The default is to delete the transient work item and not maintain a completed-work journal.

## Planning and execution contract

Before editing, inspect code, instructions, specifications, decisions, tests, and all relevant Git boundaries. Record a baseline that distinguishes pre-existing work from task changes.

Find the matching current work item before implementation. If it does not exist, create it under the project-mapped taxonomy before editing code. The current work item must state:

- goal and user-visible outcome;
- priority and remaining steps;
- scope and non-goals;
- testable acceptance criteria;
- constraints, risks, and assumptions;
- unresolved decisions or external gates;
- exact validation required.

Implementation must remain scoped, preserve unrelated work, follow existing patterns, and keep editable specifications synchronized. Commits, pushes, installation, deployment, and external mutation require user authorization.

## Verification and review contract

Completion requires fresh evidence from the strongest feasible project checks. Record exact commands, environments, results, and unverified limitations.

After implementation and initial verification, run two isolated gates:

1. an outcome critic attempts to falsify requirements coverage, assumptions, safety, operability, and evidence;
2. a separate code reviewer examines the complete task change for correctness, regressions, security, tests, conventions, and unnecessary complexity.

Reviewers receive raw specifications, task state, complete change manifests, and verification evidence rather than implementation reasoning. Confirmed blocking findings require fixes and affected verification. Update durable decisions and derived specifications before the final-manifest review. Both gates must receive that final manifest; any later behavior, specification, or acceptance change requires both full gates to pass again. If isolated contexts are unavailable, fallback self-review is useful but does not satisfy the independent gates.

No behavioral change may follow final review without reopening affected verification and review. Review evidence lives where project instructions require, otherwise in the current work item.

## Completion contract

Claim completion only when:

- every acceptance criterion has current evidence;
- both independent review gates passed;
- the reviewed implementation matches the final verified state;
- confirmed blockers are resolved;
- durable decisions and derived specifications are updated;
- no external gate remains;
- remaining non-gating limitations are explicit;
- the current item is transitioned according to project retention policy.

## Default behavior without a project adapter

Use `docs/dev-flow` with `tasks/`, `specs/`, `reference/decisions.md`, and `questions.md`. Mark every specification as source or derived and name its authority or provenance. Use `plan-`, `task-`, and `check-` filename prefixes. Keep review state in the current task, migrate durable outcomes, then delete the completed task.

## Non-goals for P0

- installing or publishing the skill;
- requiring worktrees, commits, pull requests, or external trackers;
- maintaining a database or task graph;
- adding project-specific paths to the universal runtime skill;
- generating a permanent completed-work journal;
- implementing multi-layer configuration or a workflow engine.
