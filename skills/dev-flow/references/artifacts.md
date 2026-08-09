# Change Artifact Contract

Use one directory per tracked change. Follow a user-designated location or the
project's own planning convention. Without either, use:

```text
<project-root>/docs/dev-flow/changes/<change-id>-<slug>/
```

An exact user-authorized external directory is allowed. Keep the product
workspace and change directory as separate command arguments. `flowctl`
excludes the resolved change directory from product-workspace fingerprints, so
state and phase artifacts cannot invalidate their own verification.

## Durable files

| File | Purpose |
|---|---|
| `change.json` | Machine-owned lifecycle, phase, blockers, and provenance |
| `events.jsonl` | Machine-owned append-only workflow events |
| `brief.md` | Goal, scope, constraints, and success |
| `research.md` | Discovery evidence when discovery is used |
| `spec.md` | Observable behavior and acceptance criteria |
| `plan.md` | Implementation units, paths, dependencies, and checks |
| `implementation.md` | Changed paths, deviations, and implementation evidence |
| `verification.md` | Commands, results, environments, and acceptance coverage |
| `review.md` | Outcome and code-review findings and dispositions |
| `closure.md` | Final outcome, durable links, limitations, and follow-ups |

Create Markdown files only when their phase uses them. Optional phases still
remain explicit in `change.json` and must be skipped through `flowctl`.

## Initialization

If `change.json` is absent because the user is starting a new tracked change,
initialize only after selecting one unambiguous directory:

```text
python3 <skill-directory>/scripts/flowctl.py --change <directory> init \
  --id <id> --project <project> --title <title> \
  --kind feature|bug|refactor|maintenance --risk low|medium|high
```

The kind materializes phase requirements once. Later skill versions must not
silently change an existing manifest's profile.

## Path and content rules

- Store evidence paths relative to the change directory.
- Refer to product files as logical repository aliases such as
  `code:src/server.py`; do not store machine-local absolute paths.
- Keep source requirements immutable unless the user authorizes changes. A
  local `spec.md` may cite or summarize an external source and must name it.
- Do not store secrets, raw environment values, transcripts, hidden reasoning,
  or every shell command.
- Store decisions, evidence, blockers, transitions, overrides, and approvals.
- Use `flowctl` for every lifecycle mutation. Treat direct edits to machine-owned
  files as recovery work requiring explicit reconciliation.
