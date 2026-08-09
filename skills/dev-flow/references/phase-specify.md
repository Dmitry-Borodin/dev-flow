# Phase: specify

## Result

An observable behavior contract in `spec.md` with no blocking product question.

## Required when

Required when the manifest says so. Skip only when the change has no new or
changed behavior requiring an acceptance contract.

## Entry conditions

- `frame` passed.
- `discover` passed or was explicitly skipped.
- Evidence supports the proposed behavior boundary.

## Inputs

- `brief.md`.
- `research.md` when present.
- Authoritative source requirements and existing derived specifications.

## Produce

- `spec.md` with `AC-*` acceptance criteria, behavior boundaries, constraints,
  non-goals, failure behavior, and source provenance.

## Mechanical exit checks

- `spec.md` exists and contains no placeholder.
- Acceptance criteria have unique stable IDs.
- Every requirement is observable and testable.

## Semantic exit checks

- The specification states behavior, not an implementation wish list.
- Criteria cover relevant failure, safety, and compatibility boundaries.
- No implementer must choose product behavior or authorization policy.

## Allowed mutations

Write change artifacts and authorized derived specifications only. Do not edit
product code or immutable source requirements.

## Allowed transitions

- `specify -> plan` with `spec.md` evidence.
- Rewind to `discover` for missing evidence or `frame` for changed scope.
- Skip optional specification through `flowctl` with a reason.

## Blocking conditions

Block when an unresolved behavior, security, data, or authority choice changes
acceptance criteria materially.
