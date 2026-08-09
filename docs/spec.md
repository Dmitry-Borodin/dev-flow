# Dev Flow V1 Specification

Status: approved implementation baseline

## Outcome

`dev-flow` manages a non-trivial software change as a durable, resumable state
machine. Another agent must be able to determine the current phase, validate
the evidence, and continue without the previous chat.

The V1 runtime is self-contained. It uses local files, Git when available, and
Python 3.10+ from the standard library. It does not depend on Beads, OpenSpec,
Superpowers, MCP servers, hosted services, or another task tracker.

## Architecture

The canonical installable artifact remains `skills/dev-flow/`.

| Component | Responsibility |
|---|---|
| `SKILL.md` | Activation, invariant summary, runtime protocol, and phase routing |
| `assets/workflow-v1.json` | Stable phases, profiles, transitions, and result enums |
| `assets/change-v1.schema.json` | Portable machine-readable change-manifest contract |
| `scripts/flowctl.py` | Deterministic validation, diagnosis, and state transitions |
| `references/phase-*.md` | Semantic contract loaded only for the current phase |
| `change.json` | Lifecycle, current phase, phase states, blockers, and provenance |
| `events.jsonl` | Append-only workflow decisions and transitions |
| Markdown artifacts | Brief, research, spec, plan, verification, review, and closure evidence |

The agent owns semantic decisions. `flowctl` owns lifecycle invariants,
mechanical evidence checks, transition legality, provenance, and stable JSON
status output.

## V1 invocation boundary

Call `flowctl` with an explicit change directory. Initialize a genuinely new
directory before requesting status. After verification provenance exists,
status and every active-lifecycle mutation require an explicit workspace path.
Project discovery and project-to-artifact-root mapping remain agent-level in
V1; unresolved automation choices are tracked in `docs/questions.md`.

The helper exposes:

```text
init
validate
status
transition
skip
block
unblock
rewind
```

All operational command output is JSON; conventional `--help` is text. Success exits with code 0. Invalid input,
inconsistent state, illegal transitions, and stale evidence exit non-zero.

## State model

The ordered phases are:

```text
frame -> discover -> specify -> plan -> implement -> verify -> review -> close -> done
```

`discover` and `specify` may be skipped only when their manifest entry is not
required. A skip records a non-empty reason.

Lifecycle and phase state are independent:

- lifecycle: `active`, `blocked`, `done`, `cancelled`, `superseded`;
- phase state: `pending`, `active`, `passed`, `skipped`;
- computed health: `consistent`, `stale`, `inconsistent`, `invalid`.

`blocked` is an overlay: the current phase remains active and at least one
blocker remains open. Terminal lifecycles have no current or active phase.

## Profiles

V1 provides dependency-free defaults, materialized into every new manifest:

| Kind | Discover | Specify | Plan | Verify | Review |
|---|---|---|---|---|---|
| feature | optional | required | required | required | required |
| bug | required | optional | required | required | required |
| refactor | required | required | required | required | required |
| maintenance | optional | optional | required | required | optional |

`frame`, `implement`, and `close` are always required. Profile defaults do not
silently change after initialization.

## Invariants

`flowctl` must enforce:

1. Active or blocked changes have exactly one active phase and a matching
   `current_phase`.
2. Terminal changes have no active or current phase.
3. Passed phases have existing evidence files inside the change directory.
4. Skipped phases have a reason and are not required.
5. Blocked changes have at least one open blocker; active changes have none.
6. Done requires `close=passed`; required phases before close are passed.
7. Every state mutation increments `revision` and appends an event with the
   resulting revision.
8. Phase identifiers and contract versions retain their V1 meaning.
9. A plan becomes stale when its stored `spec.md` digest differs from the
   current file.
10. Verification and review become stale when their stored workspace
    fingerprint differs from the explicit current workspace. Change artifacts
    are excluded from the product-workspace fingerprint.

Mechanical checks never claim semantic sufficiency. Phase references define
the semantic exit checks the agent must perform before asking `flowctl` to
advance.

## Phase mutation boundaries

| Phase | Primary result | Product-code mutation |
|---|---|---|
| frame | `brief.md` | forbidden |
| discover | `research.md` when used | read-only; disposable experiments only |
| specify | `spec.md` | forbidden |
| plan | `plan.md` | forbidden |
| implement | scoped code and tests | allowed |
| verify | `verification.md` | forbidden; failures rewind to implement |
| review | `review.md` | forbidden; findings rewind to the affected phase |
| close | `closure.md` | forbidden; product-document sync must already be reviewed |

An implementation request authorizes scoped code, tests, and project
documentation changes. It does not authorize commit, push, publish, merge,
deployment, destructive external changes, or unrelated cleanup.

## Provenance

V1 tracks two critical edges:

- `spec.md -> plan`: passing plan records the current spec digest;
- workspace -> verify/review: passing those phases records a deterministic Git
  fingerprint when possible, otherwise a content fingerprint of the workspace;
  the resolved change directory is excluded from both forms.

`status` reports stale evidence and an executable rewind. It does not mutate
state while diagnosing it. Once workspace provenance exists, omitting the
workspace is an inconsistency rather than permission to skip freshness checks.
Terminal `done` records historical completion; `cancelled` and `superseded`
return `terminated`, never `complete`.

## Behavioral requirements

- Resume from the recorded phase instead of restarting brainstorming.
- Refuse silent selection when no explicit change path can be resolved.
- Do not implement with invalid, inconsistent, or stale upstream state.
- Use a compact profile for small maintenance work.
- Keep a bug in discover until reproduction evidence exists.
- Never create a fallback tracker when an external tracker is absent; V1 has no
  tracker contract at all.
- Rewind before fixing failures found during verify or review.
- Stop at plan when the user requested only a plan.
- Continue across phase boundaries until the target in the current user
  instruction, a real blocker, or completion. V1 does not persist authority or
  target scope; without an explicit current target it finishes at most the
  current phase.

## Validation

Completion requires:

- standard-library unit and fixture tests for every command and invariant;
- schema/workflow parity checks and broken-reference checks;
- behavioral eval scenarios covering activation, resume, stale state,
  blocking, rewind, restraint, and completion;
- independent outcome and code/skill reviews over the final manifest;
- a fresh full test run after accepted review fixes.

## V1 non-goals

- Beads or any other tracker integration;
- automatic adoption or migration of legacy work;
- automatic project or change discovery;
- plugin packaging or installation;
- worktree creation, commit cadence, publishing, deployment, or merge;
- task graph scheduling, dashboards, personas, or required subagents;
- complete semantic parsing of acceptance-criteria traceability;
- a full provenance graph for every artifact.
