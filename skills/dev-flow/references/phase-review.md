# Phase: review

## Result

Two explicit challenge passes and their dispositions in `review.md`.

## Required when

Required when the manifest says so. Optional low-risk review still requires an
explicit skip reason.

## Entry conditions

- `verify` passed on the current workspace.
- The reviewer receives raw requirements, artifacts, diff, and verification
  evidence rather than implementation reasoning.

## Inputs

- Brief, specification, plan, implementation manifest, verification evidence,
  complete diff or file set, and applicable project instructions.

## Produce

- An outcome critique that attempts to falsify requirements coverage,
  assumptions, safety, operability, and evidence.
- A separate code/skill review for correctness, regressions, security, error
  handling, tests, conventions, and unnecessary complexity.
- `review.md` with `RF-*` findings, severity, disposition, and re-review state.

## Mechanical exit checks

- Both passes examined the same final workspace and artifact manifest.
- Every finding has a location, consequence, severity, and disposition.
- Passing the phase records the current workspace fingerprint.

## Semantic exit checks

- No confirmed blocking finding remains open.
- Use isolated reviewers in parallel when available; otherwise run the passes
  separately and disclose the lack of isolation without dropping either pass.
- Accepted fixes have fresh verification and affected review evidence.

## Allowed mutations

Keep product code read-only. Write review evidence only. Rewind before fixing or
changing requirements, plans, code, tests, or behavioral documentation.

## Allowed transitions

- `review -> close` with `review.md` evidence and current workspace.
- Rewind to `verify`, `implement`, `plan`, `specify`, or `frame` according to
  the finding.
- Skip optional review through `flowctl` with a reason.

## Blocking conditions

Block when a finding requires a material user decision, new authority, or an
unavailable mandatory review capability.
