# Phase: verify

## Result

Fresh acceptance evidence for the current workspace in `verification.md`.

## Required when

Required for every implemented change.

## Entry conditions

- `implement` passed with a complete change manifest.
- Status with `--workspace <path>` reports `ready` and `verify` active.
- The workspace contains the exact candidate being verified.

## Inputs

- Acceptance criteria, plan, implementation manifest, project test commands,
  and the current workspace.

## Produce

- `verification.md` with `V-*` evidence, exact commands, environment, exit
  results, acceptance mapping, failures, and unverified limitations.

## Mechanical exit checks

- Focused tests and every relevant full project gate were run freshly.
- Commands, environments, exit codes, and skipped checks are recorded.
- Passing the phase records the explicit workspace fingerprint through
  `flowctl --workspace`.

## Semantic exit checks

- Evidence covers every applicable acceptance criterion at the strongest
  feasible boundary.
- A narrow unit check is not presented as lifecycle or integration evidence.
- Independent checks may run in parallel only without shared mutable state.

## Allowed mutations

Keep product code read-only. Write verification artifacts and disposable test
outputs only. A discovered product defect requires rewind before any fix.

## Allowed transitions

- `verify -> review` with `verification.md` evidence and current workspace.
- Rewind to `implement` for a defect or `frame` for a changed outcome boundary.

## Blocking conditions

Block only when required verification needs unavailable authority, environment,
credentials, hardware, or an external actor and no equivalent check exists.
