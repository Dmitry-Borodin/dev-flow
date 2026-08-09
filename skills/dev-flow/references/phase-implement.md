# Phase: implement

## Result

The smallest complete product change, its tests, and `implementation.md`.

## Required when

Required for every tracked change that proceeds beyond planning.

## Entry conditions

- `plan` passed against the current `spec.md` when present.
- `status` reports `ready` and `implement` active.
- The requested authority covers product-code mutation.

## Inputs

- `brief.md`, `plan.md`, and applicable `spec.md` and `research.md`.
- Current code, tests, project instructions, and clean task baseline.

## Produce

- Scoped product code, tests, and authorized derived documentation.
- `implementation.md` listing completed `IU-*` units, repository-qualified
  changed paths, deviations, assumptions, and checks already run.
- Durable derived specifications and decision references required by the
  delivered behavior, so they are included in later verification and review.

## Mechanical exit checks

- Every planned unit is complete or a blocker is recorded.
- `implementation.md` exists and contains the complete change manifest.
- Focused tests for changed behavior pass.

## Semantic exit checks

- Behavior matches current acceptance criteria and project patterns.
- Deviations are justified and do not silently expand scope.
- No known implementation failure is relabeled as verification work.
- Product documentation and durable decisions match the candidate before
  verification begins.

## Allowed mutations

Modify scoped product code, tests, and project documentation. Do not commit,
push, publish, merge, deploy, or mutate unrelated or external systems without
explicit authority.

## Allowed transitions

- `implement -> verify` with `implementation.md` evidence.
- Rewind to `plan`, `specify`, `discover`, or `frame` when inputs change.

## Blocking conditions

Block for missing authority, a material design choice, destructive risk, or an
external capability required to continue implementation safely.
