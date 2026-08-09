# Phase: plan

## Result

An implementation-ready `plan.md` usable without new architectural decisions.

## Required when

Required for every tracked production change; use a compact form for one
obvious maintenance edit.

## Entry conditions

- `frame` passed.
- Discovery and specification passed or were explicitly skipped.
- No open blocker changes the technical approach.

## Inputs

- `brief.md`, `spec.md`, and `research.md` when present.
- Project conventions, relevant code and tests, and current Git boundaries.

## Produce

- `plan.md` with stable `IU-*` units, acceptance coverage, repository-qualified
  paths, dependencies, intended result, and exact verification.
- Explicit independent units that may safely run in parallel.

## Mechanical exit checks

- `plan.md` exists and contains no placeholder.
- Every unit names affected paths, result, and verification.
- Every applicable `AC-*` is covered by at least one unit.

## Semantic exit checks

- An implementer need not invent design, scope, or behavior decisions.
- Unit boundaries are independently reviewable and avoid speculative layers.
- Planned validation is strong enough for the stated risk.

## Allowed mutations

Write only change artifacts. Do not modify product code.

## Allowed transitions

- `plan -> implement` with `plan.md` evidence.
- Rewind to `specify`, `discover`, or `frame` when inputs are incomplete.

## Blocking conditions

Block only when choosing a default materially changes the plan, authority,
scope, security, data integrity, or irreversible cost.
