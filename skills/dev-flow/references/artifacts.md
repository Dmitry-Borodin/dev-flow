# Project Artifact Contract

Resolve one artifact root, then use the target project's own artifact taxonomy and retention rules.

## Authority and discovery

1. Follow an artifact root expressly designated in the current user request.
2. Otherwise read the top-level `artifact_root` value in `{project-root}/.dev-flow.yaml`.
3. Otherwise use `{project-root}/docs/dev-flow`.

After resolving the root, read instruction files at both the project root and artifact root. Before reading or writing a target artifact, also read every instruction file applicable along the path from those boundaries to the target. The nearest applicable instructions define exact paths, naming, language, mutability, and retention. They override the fallback layout below.

A path that merely names source material is not an artifact-root override. If the user names an existing task or specification, reuse that artifact and keep root resolution unchanged.

## Project configuration

Do not create `.dev-flow.yaml` automatically. A project opts in explicitly:

```yaml
artifact_root: private
```

P0 requires exactly one YAML document. Its root must be a mapping containing exactly one scalar key, `artifact_root`, with one non-empty scalar string value. Reject additional documents, malformed YAML, duplicate or unknown keys, non-string values, an empty value, `.`, an absolute configured path, a `..` segment, or a root that resolves to an existing file. If configuration exists but is invalid, stop before writing; do not fall back elsewhere.

Resolve configured and relative user paths from the project root. If a user-designated path normalizes or resolves outside the project, obtain authorization for that exact external destination.

Confirm lexical and canonical containment before every write. Resolve existing ancestors, reject unapproved symlink escapes, and treat an authorized external root as the exact write boundary.

If the artifact root is a nested repository, inspect and report its instructions, status, diff, and validation separately from the code repository.

## Semantic roles

Map these roles onto existing project artifacts; one file may serve multiple roles when project rules allow:

- **source specification** — authoritative user or contract requirements; immutable unless explicitly authorized;
- **derived specification** — project-maintained behavior or design documentation; update when accepted behavior changes;
- **current work item** — goal, priority, remaining steps, acceptance, blockers, verification, and review state;
- **decision reference** — durable accepted decisions and rationale, not a work log;
- **open questions** — only unresolved questions; remove answered entries;
- **implementation map** — current system model and near-term ordering, not a second backlog;
- **review evidence** — active findings, dispositions, fixes, and re-review state; retain or remove per project policy.

Do not create new role directories when project instructions already map these concepts.

## Lifecycle

- **plan:** unresolved design, authorization, or operator decision remains. Split independent executable slices into current work items in the active state.
- **active:** work can proceed now. Keep the artifact current and focused on remaining work.
- **check:** only an external verification remains. Agent-accessible tests and allocated environments do not qualify as external.
- **done:** acceptance evidence exists, durable decisions and specification changes are already included in the reviewed manifest, and no external gate remains. Treat this as a transient state and immediately close, archive, or delete the current item according to project policy.

| From | Condition | To |
|---|---|---|
| plan | Blocking decisions resolved | active |
| active | New blocking decision appears | plan |
| active | Implementation and all agent-accessible checks pass; only external verification remains | check |
| check | External verification fails without a new decision | active |
| check | External verification exposes a new decision | plan |
| check | External verification passes | done, then retention |
| active | All acceptance evidence exists and no external gate is required | done, then retention |

File prefixes, priority notation, status fields, and completed-item retention are project-defined. Without project rules, use `plan-<slug>.md`, `task-<slug>.md`, and `check-<slug>.md`; move durable outcomes before final review, then delete the finished work item after the gates pass. Do not keep a completion journal by default.

## Fallback layout

Only when the project has no existing taxonomy, use:

```text
docs/dev-flow/
  tasks/
  specs/
  reference/decisions.md
  questions.md
```

Every fallback file under `specs/` must declare `Role: source specification` or `Role: derived specification` and identify its authority or provenance. Keep review state in the current task. Reuse an existing artifact for the same work instead of creating a duplicate.
