---
name: dev-flow
description: Use for any software development task (feature, fix, refactor, tests, docs, review, pull request) in a project that adopts the dev-flow process.
---

# Dev flow

One process from task to merge, run by a coordinator with fresh workers. The project defines what
stands behind each term.

Read in this order: the environment (tools, agents, machines, access), the project instructions,
docs and project skill, then this skill. The more specific layer wins; explicit operator
instructions win over all. Ask for a missing parameter or requirement as an operator question.

## Project parameters

The project declares:

- Tasks and instructions: location (repo directory, separate or nested repo), public or private;
  for a separate repo, who commits it. You keep progress there current.
- Where operator questions live.
- Checks mapped to the kinds under [Checks](#checks), with what each proves and how to run it.
- PR format details: statistics, labels, how to attach media and check links, and the code areas
  for the final report.
- Whether the developer commits and pushes its candidate; by default the coordinator does.
- Agents available per role, when it limits them, and model overrides; see [Roles](#roles).

## Terms

- **Candidate:** the exact source under check or review, including uncommitted and untracked
  files; identified by a recorded hash or manifest, or by commit SHA once pushed.
- **Freeze:** stop editing so later checks and review see the same candidate.
- **Receipt:** a check's own result (exit status, log, run link) bound to a candidate. A summary
  is not a receipt.
- **Substantial change:** changes behavior across components, or touches permissions, data
  retention, migrations, atomic updates or recovery.
- **Assignment:** a self-contained brief for one worker, built from its role file.
- **Round:** one review of a frozen candidate that returns confirmed P1 or P2 findings.

## Tasks

- One task file per task: goal, scope, status, remaining steps, acceptance checks. Keep remaining
  steps current and remove done ones. No activity log, history or secrets.
- Names: `pN-*` executable work, N is the priority; `plan-` open decisions, dropped once settled
  and before reporting it ready to implement; `b` before the priority for a pure defect fix
  (`bpN-*`); `bp0` for bugs blocking developers (red base branch, flaky CI, broken dev tools);
  `!` blocks release, with the reason in the status, dropped when fixed; `check-*` a deferred
  verification gate that needs external access.
- Plan only agent steps; operator decisions are questions, not steps.
- Repository docs are the source of truth, not agent memory; durable decisions go to project docs.
- Operator questions: ask once, record the question in the questions file, work on something else
  until it is answered, then delete the question.

## Operator consent

These steps need the operator's consent, each given separately:

- **Recording or changing a task** (goal, scope, acceptance, decisions): show the resulting text;
  consent confirms it matches the intent.
- **Open points** the task leaves undecided: questions as in [Tasks](#tasks).
- **Finished work:** a short overview of the result.
- **Merging code:** see [Pull requests](#pull-requests).

Consent to one step does not extend to another. Present the subject where the operator can see
it (chat, PR or commit): what changed and why, how it was verified, its limits; for UI changes
screenshots, a recording or a preview link, otherwise the observable behavior (output, an
example, a diff summary).

## Work

The coordinator runs these steps in order. A read-only answer needs no task file or PR. The branch
is named after the task slug without its prefixes (`plan-`, `!`, `b`, `pN`), so a rename does not
lose it. Before starting a task, resume your own open PR or branch for it; one owned by someone
else is an operator question.

1. Write the task file: take goal, scope and acceptance from the task, write the plan and get
   [operator consent](#operator-consent) on it. Plan-only: the task file is the whole change;
   skip steps 2 and 3, and steps 4 to 6 too when tasks live in a separate repo you do not commit.
2. Substantial change: the coordinator, or a fresh design consult, runs a read-only
   [design pass](roles/design-consult.md#design-pass-mode) and records it in the task file.
3. Implement: assign a developer, or work directly where [Roles](#roles) allows it.
4. Run local checks, freeze, required review if any, repair. The coordinator commits and pushes
   the accepted candidate unless the project gives that to the developer. For tasks in the repo,
   the PR that meets the task's goal deletes its task file (not for plan-only). Open a draft PR
   and run the expensive checks risk selects.
5. Once required review, if any, passed, request merge consent with the PR link; mark the PR ready
   when owed checks are green on the head.
6. After the merge: sync tasks and instructions, deleting a finished task file kept outside the
   repo; free stands; remove worktrees. Fixes after the merge need a new PR.

Delete a diagnosis plan that found no concrete defect. Before compaction or handoff, save
remaining work, decisions and candidate and receipt pointers in the task file. Once it is deleted,
use the PR body with public facts only; the coordinator may append a remaining-work section.

## Checks

| Kind | Where | Typical use |
| --- | --- | --- |
| Local | development machine | unit, contract, lint, build |
| VM pipelines | disposable machines | fixed scenarios that need a real system |
| Base CI | every push | the project's standard gate |
| Extended CI | on demand | broad or long runs |
| Stand | VM, emulator, web stage or preview | explore and reproduce by hand, root where allowed |

- Choose by risk from the project's check table. Start with the smallest check that proves the
  changed behavior; go bigger only when it cannot. A failed prerequisite stops dependent checks.
- Reproduce a defect first; use a stand when local checks cannot. Mocks do not prove external
  protocol or host compatibility.
- Docs or mechanical change: inspect the diff and run syntax, link or format checks.
- Add a regression test only for a distinct failure or uncovered contract; assert outcomes, not
  source text. Keep existing checks for permissions, data loss, migrations and recovery.
- Only green on the current head counts; after a push rerun what risk selects for the new
  changes. Blocked, pending or interrupted is not passed.
- Run short checks directly; give a long one to an observer.
- Report actual evidence and its limits; a focused pass proves no broader gate.

## Roles

| Role | Model class | Does |
| --- | --- | --- |
| [Coordinator](roles/coordinator.md) | main session | task, scope, rounds, acceptance, PR |
| [Developer](roles/developer.md) | smart | sole writer: implements, checks, repairs |
| [Reviewer](roles/reviewer.md) | smart, fresh; max for design | read-only review and re-review |
| [Observer](roles/observer.md) | cheap | runs or watches one long check |
| [Describer](roles/describer.md) | cheap, fresh | PR title and body from the diff |
| [Design consult](roles/design-consult.md) | max, fresh | step 2 design pass, stuck rounds |

[Models](models.md) maps each class to default models and a compact limit, and says how to
override them.

- **Required review:** a substantial change, or one with a risk you can name, gets one developer
  as sole writer and one independent reviewer; a second reviewer only on request or for a separate
  concrete risk. Everything else the coordinator does directly, without review: small mechanical
  or doc edits and small focused fixes.
- Self-review never replaces required review; without an available reviewer the change is blocked.

## Orchestration

### Assign

- The coordinator does not implement work that [Roles](#roles) gives to a developer. It discovers
  only what an assignment or a finding needs and delegates the rest.
- Each assignment is the role file plus goal, scope and exclusions, inputs as pointers (task file,
  candidate, receipts, findings, links), acceptance, stop conditions, report target and the file
  for the full report. A fresh worker gets no chat history.
- Choose the model from the roles table. Resume the same developer for repairs while its context
  is relevant; every review, description and design consult is a fresh session.
- One writer per candidate. Run workers in parallel only on work without shared files or state.
- Large outputs (diffs, logs, reports) go to files outside the repo; pass paths, not retold text.

### Accept

- Assign review only after the writer stopped and relevant checks reached a terminal result.
- A report missing a field of its role's format is incomplete; ask for the field.
- Check the reported candidate identity against the tree, read the receipts and read the diff
  against the requirements. A worker's "done" is a claim, not evidence.
- Accept when requirements, findings and receipts all match the final candidate.

### Rounds

- The developer fixes confirmed findings. The coordinator checks P3-only fixes itself, without a
  new round, and closes an unsupported finding with a reason.
- After a round, assign a re-review: the fixes and their reach, not a fresh full hunt. After a
  design change, assign a first review instead.
- Before repairing a candidate that does not converge, assign a design consult: after round 2 if a
  fix broke the same mechanism or the design must change, otherwise after round 3. After round 4,
  at the latest 5, stop and ask the operator.

### Wait

- While workers run, report only completion, failure or a needed decision. Silence, lost context
  or a missed deadline never implies success.
- On a stall, get one targeted status, then stop the worker or extend with a new bound. Take over
  a candidate only after its writer stopped.

## Pull requests

- Branch from the base (default or release branch); branching from an unmerged PR branch is an
  operator question.
- Public code, commits and PRs carry no private data, secrets or attribution to agents or models.
- A describer writes the title and body: the change shown as in
  [Operator consent](#operator-consent), with links to results of checks not shown on the PR,
  in the project's format. After the expensive checks, the coordinator adds their result links.
- Touch only your own PRs; fix findings and red checks with new commits. Rewrite reviewed history
  only by a rebase for a conflict or a needed base change; force-push only your branch, with lease.
- Merge (auto-merge where available) only a ready PR (Work step 5), only while owed checks are
  green on the current head, and only with merge consent: the operator's, or an approving review
  by a human maintainer on the platform. Watch for either; agent reviews never count. After a
  push, hold auto-merge until the owed checks are green again.
- Until the merge, merge consent covers its head and small fixes pushed after it; rework or a
  rebase with conflicts needs a new one.

## Completion

**Done:** every PR opened is merged and step 6, where it applies, is finished. Until then report
one state: **awaiting merge** (consent requested), **partial** (continue executable work) or
**blocked** (name what is needed). Moving a step elsewhere or ending a session completes nothing.

Final answer:

- the work-done overview from [Operator consent](#operator-consent); the PR link, if any;
- per task: closed and deleted, or what remains (task file or PR link, steps, reason);
- tasks and instructions sync: what is synced, what awaits consent, what is left to others;
- code written: lines added and removed per area the project defines, and the purpose of each.

## Common rationalizations

| Excuse | Response |
| --- | --- |
| "Too small for review." | See [Roles](#roles). |
| "It passed before the last push." | See [Checks](#checks). |
| "The developer says it works." | See [Accept](#accept). |
| "I will update the task file at the end." | See [Tasks](#tasks). |
| "Faster to implement it myself." | See [Assign](#assign). |
| "The reviewer needs my reasoning." | See [Assign](#assign). |
| "The PR is approved, so the task change is too." | See [Operator consent](#operator-consent). |
| "One more round will fix it." | Design consult, then the operator; see [Rounds](#rounds). |
