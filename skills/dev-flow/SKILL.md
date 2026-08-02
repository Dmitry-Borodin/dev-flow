---
name: dev-flow
description: Use when implementing a non-trivial feature, fix, refactor, migration, or other multi-step project change that needs project-owned specifications and task state, an executable plan, fresh verification, and independent post-implementation critique and code review.
---

# Dev Flow

Use a lightweight requirements-to-verification workflow without replacing the target project's planning system. Scale ceremony to risk, but do not omit the final critique and code-review gates.

## Non-negotiable rules

- Follow direct user instructions and project-local instructions before this workflow.
- Inspect the current repository, conventions, and working-tree state before planning edits.
- Resolve the artifact root and project artifact model before writing. Read `./references/artifacts.md` completely.
- Reuse project-owned tasks, specifications, decisions, and questions. Do not create a parallel `dev-flow` taxonomy when one already exists.
- Preserve source specifications unless the user explicitly authorizes changing them; keep derived specifications synchronized with accepted behavior.
- Keep requirements, implementation, and completion claims aligned. Do not silently change scope.
- Require fresh verification evidence before claiming completion.
- After implementation, run separate outcome-critic and code-review gates.
- Do not commit, push, publish, deploy, install, or mutate external systems unless the user authorized it.

## Workflow

### 1. Establish context

Identify the project root, resolved artifact root, and every applicable instruction file at both boundaries. Inspect relevant code, tasks, specifications, decisions, tests, and Git state. Treat nested repositories separately and preserve unrelated changes.

Record the starting revision when one exists, staged and unstaged changes, untracked files, and relevant nested-repository states. Use this baseline to distinguish task changes from pre-existing work.

Map the project's artifact roles before writing. Find the matching current work item; if none exists, create it under the project-defined taxonomy before editing code. Extend that item instead of creating a competing source of truth.

### 2. Frame and classify the work

Ensure the current work item contains the goal, priority, remaining steps, acceptance criteria, constraints, risks, assumptions, and unresolved blockers. A short change may keep these in one file.

Use the project's names for these semantic states:

- **plan** — unresolved design choice, authorization question, or operator decision remains;
- **active** — the work is executable without that unresolved decision;
- **check** — implementation is finished and only a genuinely external verification remains;
- **done** — acceptance evidence exists and no blocking work remains.

Split executable slices out of a blocked plan. Do not classify a check the agent can perform with available tools or test environments as external.

Transition `plan → active` when blocking decisions are resolved, and `active → plan` when a new blocking decision appears. Transition `active → check` only after implementation and every agent-accessible check passes. When no external gate is required, transition `active → done` directly. A failed external check returns to `active`, or to `plan` when it exposes a new decision. A passed external check transitions to transient `done`, followed immediately by project retention. `check` and `done` are mutually exclusive.

### 3. Write the executable plan

Map every acceptance criterion to bounded tasks. For each task name the relevant files, intended result, and exact validation. Keep tasks independently reviewable; avoid speculative abstractions and unrelated cleanup.

Keep only current and remaining work in the current item unless project instructions require history. Update it as facts change, and explain scope changes rather than rewriting accepted requirements.

### 4. Execute and verify

Implement the smallest complete change that follows existing project patterns. Validate incrementally and keep editable specifications synchronized with behavior. Stop for a genuine authorization or design blocker, not merely to ask whether to continue an approved plan.

Run the strongest feasible checks for the changed behavior: focused tests first, then the relevant build, lint, integration, or real-environment checks. Read exit codes and full failure summaries. Record exact commands, results, and anything that could not be verified.

### 5. Run the post-implementation gates

Launch two isolated reviewers after implementation and initial verification. Give them raw artifacts, not the implementer's reasoning history. Run them in parallel when independent agents are available.

**Outcome critic:** provide the specifications, current work item, complete change manifest, produced behavior, and verification evidence. Ask it to falsify the outcome by finding missing requirements, invalid assumptions, unsafe boundaries, user or operator friction, and evidence gaps.

**Code reviewer:** provide a separate reviewer the same requirements plus the complete diff or file set. Include every task-created, modified, renamed, or deleted file; staged, unstaged, and untracked changes; nested-repository changes; and identified pre-existing work. Ask it to inspect correctness, regressions, security, data safety, error handling, test quality, conventions, and unnecessary complexity.

Require actionable findings with locations, consequences, and `Critical`, `Important`, or `Minor` classification. If isolated contexts are unavailable, run both checklists as a fallback but mark the independent gates unverified; one combined self-review does not count.

### 6. Resolve findings and close

Validate findings against the actual code and requirements. Fix every confirmed requirement, correctness, safety, or security blocker regardless of label. Before the final-manifest review, move durable outcomes into the project's decision references or editable specifications. Rerun affected verification after every accepted fix and durable update. Give the final manifest to both gates again; any behavior, specification, or acceptance change requires both full gates to pass again. Record justified rejections.

Store review state where project instructions require; otherwise keep it in the current work item. After both final gates pass, only record their results, mark already-executed verification/review steps complete, transition status, and apply project retention. These closure-only updates do not reopen the gates and must not change requirements, acceptance, behavior, or add or substantively alter remaining work. Any other product-code, test, configuration, requirement, plan-content, or behavioral-documentation change reopens affected verification and both review gates.

Then close, rename, archive, or delete the current item according to project retention policy. Do not create a completed-work journal by default.

Claim completion only when acceptance criteria have evidence, both independent gates passed on the final manifest, the reviewed implementation matches the final verified state, blocking findings are resolved, no external gate remains, and remaining non-gating limitations are explicit.

## Right-size the workflow

For long work, split independently verifiable phases and preserve live state in project artifacts. Do not introduce worktrees, forced commits, step-file engines, external trackers, or extra directories unless the project or user requires them.
