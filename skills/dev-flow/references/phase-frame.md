# Phase: frame

## Result

A `brief.md` that makes the intended outcome and completion boundary explicit.

## Required when

Required for every tracked change.

## Entry conditions

- The change is initialized and `frame` is active.
- Applicable user and project instructions are known.
- The selected change does not conflict with another active candidate.

## Inputs

- User request and authority.
- Existing project tasks, specifications, decisions, code, tests, and Git state.
- Relevant constraints and known risks.

## Produce

- `brief.md` with goal, scope, non-goals, constraints, assumptions, risk, and
  observable success conditions.
- Confirm the initialized `kind` and `risk`. If either is wrong, stop and request
  reinitialization or reclassification direction; V1 has no metadata-update
  command and the manifest must not be hand-edited.

## Mechanical exit checks

- `brief.md` exists and contains no placeholder.
- Goal, scope, non-goals, constraints, and success are present.
- Every unresolved material choice is recorded as a blocker.

## Semantic exit checks

- Success is observable by a user, operator, or test.
- Defaults do not change security, data integrity, irreversible cost, or scope.
- The work is small enough for one change; independent work is separated.

## Allowed mutations

Write only change artifacts. Keep product code and external systems read-only.

## Allowed transitions

- `frame -> discover` with `brief.md` evidence.
- Record a blocker and remain in `frame`.

## Blocking conditions

Block only for an unresolved choice that materially changes scope, behavior,
security, data integrity, irreversible actions, or substantial cost.
