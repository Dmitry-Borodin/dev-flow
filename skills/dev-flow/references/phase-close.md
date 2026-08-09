# Phase: close

## Result

A durable final outcome in `closure.md` and terminal `done` state.

## Required when

Required for every completed change.

## Entry conditions

- Required phases passed and optional phases passed or were explicitly skipped.
- Verification and review evidence are current for the final workspace.
- No open blocker or confirmed blocking finding remains.

## Inputs

- All change artifacts, current project documentation, final workspace status,
  and accepted follow-ups or limitations.

## Produce

- `closure.md` with outcome, evidence links, durable decisions, remaining
  non-gating limitations, follow-ups, and publication state.

## Mechanical exit checks

- Status with `--workspace <path>` is ready and `close` is active.
- `closure.md` contains no placeholder and links current evidence.
- No open blocker remains; required artifacts exist.

## Semantic exit checks

- The delivered outcome matches the approved scope and final reviewed state.
- Durable project knowledge was synchronized before final verification and
  remains unchanged from the reviewed workspace.
- No unperformed publish, merge, deploy, or external action is implied complete.

## Allowed mutations

Write only excluded change-store closure artifacts. Rewind before changing
product code, tests, configuration, requirements, or durable project
documentation. Publish, merge, deploy, and external mutation still require
explicit authority.

## Allowed transitions

- `close -> done` with `closure.md` evidence.
- Rewind to the phase affected by stale evidence or a late finding.

## Blocking conditions

Block when required durable synchronization or an explicitly requested external
closure action needs missing authority or capability.
