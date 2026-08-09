# Phase: discover

## Result

Design-affecting unknowns are resolved with evidence in `research.md`.

## Required when

Required when the manifest says so. Otherwise skip with a concrete reason when
existing evidence already supports specification and planning.

## Entry conditions

- `frame` passed.
- `brief.md` identifies the goal and boundaries.
- `discover` is active and no blocker prevents useful investigation.

## Inputs

- `brief.md`.
- Relevant code, history, documentation, tests, logs, and reproducible behavior.

## Produce

- `research.md` containing questions investigated, evidence, conclusions,
  rejected options, risks, and explicitly deferred unknowns.
- Reproduction evidence for bugs.

## Mechanical exit checks

- `research.md` exists when the phase runs.
- Each investigated question has evidence or a named deferral.
- Bug reproduction records exact conditions and observed behavior.

## Semantic exit checks

- No unresolved unknown forces the next phase to invent architecture.
- Conclusions distinguish observed facts from assumptions.
- Investigation depth is proportional to change risk.

## Allowed mutations

Read product code. Use disposable experiments outside product code and remove
them after recording results. Write only change artifacts.

## Allowed transitions

- `discover -> specify` with `research.md` evidence.
- Skip optional discovery through `flowctl` with a reason.
- Rewind to `frame` when scope changes.

## Blocking conditions

Block when required evidence or a material user decision cannot be obtained
without new authority or an unavailable external capability.
