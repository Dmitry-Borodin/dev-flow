---
name: dev-flow
description: Use when starting, resuming, diagnosing, planning, implementing, verifying, reviewing, or closing a tracked non-trivial software change whose state must survive chat or agent boundaries.
---

# Dev Flow

Produce a verified change and state resumable without chat history.

## Runtime protocol

1. Follow user authority and applicable project instructions.
2. Resolve one change directory and read the [artifact contract](references/artifacts.md).
   For a new directory without `change.json`, run `init`. Otherwise never choose
   between candidates or reconstruct a missing manifest by guessing.
3. Resolve the workspace separately; keep absolute paths out of artifacts.
4. Run the bundled controller before phase work:

   ```text
   python3 <skill-directory>/scripts/flowctl.py \
     --change <change-directory> --workspace <workspace> status
   ```

5. Route the diagnostic result first:

   | Result | Action |
   |---|---|
   | `ready` | Load only the current phase reference and execute it. |
   | `blocked` | Close each resolved blocker with `unblock`; remain blocked while any stay open. |
   | `stale` | Use the exact rewind in `next_action`; do no downstream work first. |
   | `inconsistent` / `invalid` | Stop. Restore only unambiguous source-backed evidence; otherwise report violations and request recovery direction. |
   | `complete` | Confirm `lifecycle=done`, report the persisted outcome, and stop. |
   | `terminated` | Report cancellation or supersession without claiming completion. |

6. Make only phase-allowed mutations. Pass its exit checks, then persist through
   `flowctl`.
7. A target phase passes only after its transition is persisted, leaving the
   next phase active. Then continue until the current user target, a blocker, or
   completion. V1 stores neither authority nor target; if absent now, finish at
   most the current phase. An active next phase grants no mutation authority.

Use `flowctl.py --help` for syntax. Never hand-edit its state files in normal use.

## Invariants

- Keep exactly one active phase for active or blocked changes.
- Require evidence for passed phases and a reason for skipped phases.
- Rewind before fixing a failure found during read-only verify or review.
- Pass the workspace to status and to verify/review transitions so provenance is
  checked against current code.
- Define a capability and success condition before choosing a tool; do not
  silently substitute a missing capability.
- Parallelize independent, read-only gates with distinct outputs only.
- Never infer authority to commit, push, publish, merge, deploy, or perform
  destructive external actions.

## Phase routing

| Current phase | Load exactly this contract |
|---|---|
| `frame` | [Frame](references/phase-frame.md) |
| `discover` | [Discover](references/phase-discover.md) |
| `specify` | [Specify](references/phase-specify.md) |
| `plan` | [Plan](references/phase-plan.md) |
| `implement` | [Implement](references/phase-implement.md) |
| `verify` | [Verify](references/phase-verify.md) |
| `review` | [Review](references/phase-review.md) |
| `close` | [Close](references/phase-close.md) |

## Completion report

Always report the change ID, lifecycle, resulting phase, transition, evidence,
blockers, limitations, and next executable action. Claim completion only from a
fresh `complete` status with `lifecycle=done` on the final workspace.
