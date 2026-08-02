---
name: dev-flow
description: Use when implementing a non-trivial feature, fix, refactor, migration, or other multi-step project change that needs durable requirements, an executable plan, fresh verification, and independent post-implementation critique and code review.
---

# Dev Flow

Use a lightweight requirements-to-verification workflow. Scale the artifacts to the risk and size of the change, but do not omit the final critique and code-review gates.

## Non-negotiable rules

- Follow direct user instructions and project-local instructions before this workflow.
- Inspect the current repository, existing conventions, and working-tree state before planning edits.
- Resolve the project artifact root before writing requirements, plans, or review reports. Read `./references/artifacts.md` for the resolution and safety contract.
- Keep requirements, implementation, and completion claims aligned. Do not silently change scope.
- Require fresh verification evidence before claiming that work is complete or correct.
- After implementation, run both an outcome critic and a code reviewer. They are separate gates with different prompts.
- Review passes are read-only. The implementer evaluates findings, applies accepted fixes, reruns affected checks, and requests focused re-review.
- Do not commit, push, publish, deploy, install, or mutate external systems unless the user authorized that action.

## Workflow

### 1. Establish context

Identify the project root and every applicable instruction file. Inspect relevant code, documentation, tests, recent decisions, and Git state. Preserve unrelated changes and treat nested repositories as separate boundaries.

Record a task baseline before editing: the starting revision when one exists, staged and unstaged changes, untracked files, and the state of every relevant nested repository. Use it later to distinguish task changes from pre-existing work.

Resolve the artifact root, then locate any existing requirement or plan for the requested work. Extend the existing artifact instead of creating a competing source of truth.

### 2. Frame the change

For non-trivial work, create or update a requirement artifact containing:

- goal and user-visible outcome;
- scope and explicit non-goals;
- acceptance criteria that can be checked;
- constraints and project conventions;
- material risks, assumptions, and unresolved decisions.

Ask the user only about decisions that would materially change the result or exceed the authorized scope. Otherwise, state bounded assumptions and proceed.

### 3. Write the executable plan

Map every acceptance criterion to one or more bounded tasks. For each task name the relevant files, intended result, and exact validation. Keep tasks independently reviewable; avoid speculative abstractions and unrelated cleanup.

Record plan status durably. Update it as facts change, and explain any scope change rather than rewriting history.

### 4. Execute

Implement the smallest complete change that follows existing project patterns. Validate incrementally and keep documentation synchronized with behavior. Stop for a genuine authorization or design blocker; do not stop merely to ask whether to continue an already approved plan.

### 5. Verify

Run the strongest feasible checks for the changed behavior: focused tests first, then the repository's relevant build, lint, integration, or real-environment checks. Read exit codes and full failure summaries. Record commands, results, and anything that could not be verified.

### 6. Run the post-implementation gates

Launch two isolated reviewers after implementation and initial verification. Give them raw artifacts, not the implementer's reasoning history. Run them in parallel when the environment supports independent agents.

**Outcome critic**

Give the critic the requirement, plan, complete change manifest, produced behavior, and verification evidence. Ask it to try to falsify the outcome: find missing requirements, invalid assumptions, unhandled operating conditions, user or operator friction, unsafe boundaries, and evidence gaps.

**Code reviewer**

Give a separate reviewer the requirement, plan, complete change manifest, complete diff or file set, and verification evidence. The manifest must include every task-created, modified, renamed, or deleted file; staged, unstaged, and untracked changes; separate nested-repository changes; and identified pre-existing work. Ask it to inspect correctness, regressions, security and data safety, error handling, test quality, project conventions, and unnecessary complexity.

Require both reviewers to return actionable findings with locations, consequences, and `Critical`, `Important`, or `Minor` classification. Critical means a confirmed safety, security, data-loss, or fundamental requirement failure. Important means a likely correctness, regression, operability, or verification failure. Minor means a non-blocking clarity or maintainability issue.

If isolated reviewer contexts are unavailable, run the two checklists sequentially as a fallback, but record both independent gates as unverified. Do not claim independent review or fully complete the workflow. One combined self-review does not count as two gates.

### 7. Resolve findings and close

Validate each finding against the actual code and requirements; adversarial review can produce false positives. Fix every confirmed requirement, correctness, safety, or security blocker regardless of its assigned label. Rerun affected verification and complete a focused re-review after every accepted fix. Record justified rejections instead of silently discarding them.

Persist one review record under the resolved artifact root with both passes, reviewer-isolation status, findings, dispositions, fixes, verification, and re-review results.

After the gates pass, permit only append-only review results and a plan-status transition as closure metadata. These entries must not change requirements, acceptance semantics, or behavior. Any post-review product, test, configuration, requirement, plan-content, or behavioral-documentation edit reopens affected verification and review.

Mark the plan complete only when acceptance criteria have evidence, both independent gates passed, the reviewed implementation snapshot matches the final verified implementation state, confirmed blocking findings are resolved, and remaining limitations are explicit. Report the outcome, changed artifacts, verification, review disposition, and any operator-owned next step.

## Right-size the workflow

For a small but non-trivial change, the requirement and plan may be short sections in one artifact. For a long or multi-phase effort, split the plan into independently verifiable phases and preserve completion state in the artifact root. Do not introduce worktrees, frequent commits, step-file engines, or extra tracking systems unless the project or user requires them.
