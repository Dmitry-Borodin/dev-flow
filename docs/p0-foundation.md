# P0: Dev Flow Foundation

Status: reviewed P0 baseline

## Goal

Create a reusable, project-agnostic `dev-flow` skill that carries a change from requirements through implementation and fresh verification, then always runs an independent outcome critic and code review before completion.

## Upstream references

The initial design adapts concepts from the local upstream checkouts without modifying or depending on their internals:

- Superpowers (`44c9b2d`): requirements before implementation, executable plans, review isolation, and evidence before completion claims.
- BMAD Method (`770d4259`): lean project context, configurable artifact paths, adversarial review with human filtering, and separate review lenses.

This project does not copy either workflow wholesale. It intentionally omits mandatory commits, worktrees, per-step files, installer machinery, personas, and deep configuration overlays from P0.

## Requirements

### R1. General-purpose skill

The skill must be usable across repositories and technology stacks. It must follow the target project's instructions and conventions rather than impose Subyard-specific paths or tools.

### R2. Durable, configurable artifacts

Non-trivial work must keep requirements and an executable plan in the target project. The default artifact root is `docs/dev-flow`; a project can override the whole root with one `artifact_root` key in `.dev-flow.yaml`, and the current user can override it for a task.

Only a path expressly designated as the artifact root overrides the project setting. Project configuration must stay repo-relative; a user-designated external or absolute destination requires explicit authorization. Invalid configuration fails closed, and both lexical and canonical containment must prevent symlink escapes unless the user explicitly authorizes the external destination. Nested Git repositories remain separate change and reporting boundaries.

### R3. Requirements and plan contract

Requirements must state the goal, scope, non-goals, acceptance criteria, constraints, risks, assumptions, and unresolved decisions. Plans must map acceptance criteria to bounded tasks and name concrete validation.

### R4. Scoped execution

Implementation must preserve unrelated work, follow existing patterns, avoid speculative abstractions, and stop only for material design or authorization blockers. Commits, pushes, deployments, installs, and other external mutations require explicit authorization.

### R5. Evidence before completion

Completion claims require fresh checks appropriate to the changed behavior. The final report must distinguish verified results, unverified limitations, and operator-owned gates.

### R6. Two mandatory post-implementation gates

After implementation and initial verification, launch two distinct review passes:

1. An outcome critic tries to falsify whether the result satisfies requirements and works safely for users and operators.
2. A code reviewer inspects the complete change for correctness, regressions, security, tests, conventions, and unnecessary complexity.

Use separate isolated agents with raw-artifact handoff. If isolated contexts are unavailable, fallback passes may still provide feedback but the independent gates remain unverified and the workflow cannot be claimed fully complete. Reviewers report findings; the implementer owns triage and fixes. Confirmed blocking findings require fixes, affected verification, and successful focused re-review. The reviewed implementation snapshot must match the final verified implementation state; only append-only review results and a plan-status transition may follow as closure metadata. One durable record must preserve both passes and their dispositions.

### R7. Proportional ceremony

Short changes may combine requirements and plan in one artifact. Long tasks may split into phases, but P0 must not require an issue tracker, graph database, worktree, commit cadence, or workflow runtime.

### R8. Portable skill package

The skill must follow the Agent Skills directory contract, keep `SKILL.md` concise, use relative internal references, and ship valid Codex UI metadata. P0 produces source only; installation and publication are separate operator decisions.

## P0 acceptance criteria

- `skills/dev-flow/SKILL.md` is valid and contains the complete core workflow.
- Project artifact resolution and path safety are documented in one reference file.
- `.dev-flow.yaml` can override the default artifact root with one repo-relative value.
- The workflow makes both post-implementation review gates mandatory and distinct.
- The upstream influences and deliberately excluded complexity are recorded.
- Deterministic skill validation passes.
- An independent critic and code/skill reviewer have reviewed this baseline, with accepted findings resolved.

## Deferred beyond P0

- installation or plugin packaging;
- automated evaluators and pressure scenarios;
- helper scripts for artifact generation or config validation;
- integrations with external task trackers;
- versioned schema migrations or multi-layer configuration.
