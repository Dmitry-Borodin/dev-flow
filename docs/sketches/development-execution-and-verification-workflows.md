# Development Execution and Verification Workflows

This note compares how the skill collections in this workspace implement
planned work and decide that development is done. It distinguishes task
completion from test evidence, specification compliance, code-quality review,
human acceptance, CI success, merge readiness, and actual shipment.

For the upstream artifact lifecycles, see
[Planning and Specification Workflows](planning-and-specification-workflows.md).
For setup and artifact locations, see
[Skill Setup and Artifact Conventions](skills-setup-and-artifact-conventions.md).

## The central finding

“Done” has materially different meanings across these collections:

- Matt Pocock, Superpowers, BMAD, GSD, and Compound Engineering explicitly
  separate implementation from at least one independent review or verification
  stage.
- Among the compared collections, GSD, Compound Engineering, and gstack provide
  the most extensive end-to-end delivery pipelines.
- Superpowers provides one of the strictest generic evidence-before-claim rules,
  while leaving project-specific CI, security, UX, and deployment policy to the
  repo.
- OpenSpec verifies artifact alignment, but archiving a change can proceed with
  user-confirmed warnings; archive completion is not synonymous with production
  readiness.
- `agent-skills` provides a broad catalog of testing, review, security, CI, and
  shipping practices, but composes them as independent skills rather than one
  mandatory orchestrator.
- Beads and Gas City track and route work; closing a bead does not prove the
  associated code was tested or shipped.

## Recommended state vocabulary

The most reliable interpretation is a state machine rather than one overloaded
word:

```text
planned
  ↓
implemented
  ↓
test-verified
  ↓
spec-validated
  ↓
quality/adversarial-reviewed
  ↓
human/UAT-accepted, when needed
  ↓
committed and PR-open
  ↓
CI/security/UX green
  ↓
merge-ready
  ↓
merged/released/shipped
```

A checkbox, agent report, archive operation, or issue closure should advance
only the state it actually proves.

## High-level comparison

| Collection | Execution model | Independent review model | Strongest completion gate | Shipping scope |
| --- | --- | --- | --- | --- |
| Matt Pocock | Implement spec/tickets with agreed test seams and TDD | Parallel Standards and Spec reviewer agents | Type/tests/full suite plus two-axis review reports | Commit-oriented; finding disposition and PR/CI/release policy remain external |
| Superpowers | Inline plan execution or fresh implementer per task | Task reviewer after every task, then whole-branch reviewer | Fresh command evidence before any success claim | Branch-finishing choices; project-specific CI/deploy |
| agent-skills | Incremental vertical slices | Separate quality/security/browser skills, not mandatory reviewer topology | Project CI sequence and explicit skill checklists | CI/CD and launch guidance available |
| OpenSpec | Apply pending `tasks.md` checkboxes | One verifier checks completeness/correctness/coherence | Evidence-backed artifact alignment report | Archive/sync lifecycle, not production shipping |
| GSD | Dependency waves with specialized executor roles | Plan checker, code reviewer, verifier, UI/security/integration roles | Passed verification plus fail-closed ship gates | Explicit verify → ship workflow |
| Compound Engineering | `ce-work` or autonomous LFG pipeline | Simplify, code review, browser test, PR-feedback triage/fix | Evidence receipts, review/fix, PR, CI babysitting | PR opened and watched; final merge remains human-owned |
| BMAD | Approved spec → isolated implementer → controller diff inspection | Parallel adversarial review lenses plus bounded fix loop | Acceptance matrix and test coverage, independently checked | Robust build loop; no universal push/release in build skill |
| spec-kit | Execute `tasks.md` phases | Analyze/converge commands and reviewer-owned checklists | Checklist gates plus spec/plan/task convergence | PR/release remains project-defined |
| gstack | Project-owned implementation or optional `/spec`-spawned worktree agent | Core review, parallel specialists, fresh-context adversarial and optional cross-model passes | Fresh exact-command evidence tied to tested tree plus review/coverage/plan gates | `/ship` creates/updates PR; `/land-and-deploy` owns human merge and live canary |
| Ralph | External runtime executes one JSON story per fresh iteration | No reviewer workflow in checked-out skills | Checkable acceptance criteria and type/test/browser expectations | No built-in PR/CI/ship loop here |
| Task Master | Select dependency-ready task/subtask | `review` status available, policy external | Task status and test strategy fields | Tracker only |
| Backlog.md | Human/agent works task and changes status | Review policy external | Acceptance criteria and Definition of Done fields | Tracker only |
| Beads | Ready → atomic claim → close | None prescribed | Issue lifecycle closure only | None prescribed |
| Gas City | Routes orders/beads/formulas/molecules | Runtime-specific convergence/gates | Caller-defined | Orchestration substrate |
| Gastown | Mayor/polecats/Witness/Refinery merge queue | Mayor review and Refinery gates | Merge-queue validation and recovery | Operational merge machinery |

## Reviewer and critic topology

| Collection | Who implements? | Who reviews? | Isolation and feedback loop |
| --- | --- | --- | --- |
| Matt Pocock | Main implementation flow | Standards agent and Spec agent in parallel | Review agents receive independent prompts and their reports are aggregated; finding disposition is not prescribed |
| Superpowers SDD | Fresh implementer agent per task | Fresh task reviewer after each task; final whole-branch reviewer | Reviewer receives task brief, diff/review package, and binding constraints; failed review returns to implementer or escalates to fresh agent |
| BMAD build | Implementation subagent | Adversarial, edge-case, verification-gap, structural, or prose lenses | Controller stages and reads actual diff, verifies consequences, then fixes/defers/re-derives with a bounded loop |
| GSD | Phase executors dispatched in dependency waves | Planner/checker before execution; verifier, code reviewer, UI/security/integration roles afterward | Orchestrator checks git and summaries rather than trusting completion signals |
| Compound/LFG | `ce-work` implementation engine | Simplifier, code reviewer, browser tester, PR-feedback legitimacy triager and fixer agents | Evidence receipts gate stages; only approved PR feedback reaches fixer agents; CI is watched after push |
| gstack | Project implementation or `/spec`-spawned agent | Core reviewer, conditional parallel specialists, fresh-context red team/adversarial agents, and optional Codex passes | Evidence-bearing findings enter Fix-First; failed optional passes are reported as missing coverage; ship reruns mandatory gates |
| OpenSpec | Current agent applies tasks | Current verifier examines three axes | Logical separation exists, but not necessarily a separate agent or fresh context |
| agent-skills | Current agent or project-specific workers | Separate optional review/security/browser skills | Composition is caller-owned; no universal independent reviewer requirement |
| Gastown | Polecats | Mayor workflow and Refinery | Persistent hooks/beads allow recovery; failed merge gates can bisect and re-dispatch |

## Matt Pocock's skills

### Implementation loop

[implement](mattpocock-skills/skills/engineering/implement/SKILL.md#L7) works
from a spec or ticket set. Its essential sequence is:

```text
read spec/ticket and domain context
        ↓
use the pre-agreed test seams
        ↓
TDD implementation
        ↓
regular type and focused-test checks
        ↓
full suite
        ↓
code review
        ↓
commit
```

The [TDD skill](mattpocock-skills/skills/engineering/tdd/SKILL.md#L37) requires
the test seams to be made explicit and confirmed with the user. This is a
notable design choice: the verification boundary is agreed before implementation,
instead of discovered after the code is already coupled to hard-to-test seams.

### Two-axis parallel review

[code-review](mattpocock-skills/skills/engineering/code-review/SKILL.md#L55)
dispatches two independent reviewers in parallel:

1. **Standards reviewer:** maintainability, readability, conventions, smells,
   architecture, and code quality.
2. **Spec reviewer:** whether the diff actually implements the requested
   behavior and satisfies the spec/tickets.

The separation is explicit at
[the reviewer prompts](mattpocock-skills/skills/engineering/code-review/SKILL.md#L64).
This prevents “clean code” from being mistaken for correct behavior, and
prevents a literal but poor-quality implementation from passing as complete.

### Meaning of done

Matt's workflow reaches local implementation completion after type/tests/full
suite, the two review reports, and commit. The skills aggregate findings but do
not require a particular fix/disposition loop. Finding resolution, PR, CI,
security, deployment, and release gates remain repository or user policy
([report aggregation](mattpocock-skills/skills/engineering/code-review/SKILL.md#L74)).

## Superpowers

### Inline execution

[executing-plans](superpowers/skills/executing-plans/SKILL.md#L18) first reads
and critically reviews the plan. It then creates task tracking, executes every
task, and runs each specified verification. Verification failure stops the
workflow rather than becoming a warning
([task loop](superpowers/skills/executing-plans/SKILL.md#L25)). After all tasks
are verified it invokes the branch-finishing workflow
([completion handoff](superpowers/skills/executing-plans/SKILL.md#L33)).

### Subagent-driven development

[subagent-driven-development](superpowers/skills/subagent-driven-development/SKILL.md#L8)
uses a stronger topology:

```text
plan preflight
   ↓
fresh implementer for task N
   ↓
implementer tests + self-review
   ↓
fresh task reviewer
   ├── spec-compliance verdict
   └── code-quality verdict
   ↓
fix/re-review loop when needed
   ↓
record task completion
   ↓
next task
   ↓
whole-branch final reviewer
```

Per-task review is mandatory, and implementer self-review never substitutes for
it
([review gate](superpowers/skills/subagent-driven-development/SKILL.md#L308)).
The reviewer receives a generated review package based on the complete task diff,
not merely the last commit
([review package](superpowers/skills/subagent-driven-development/SKILL.md#L290)).

Fixes normally return to the same implementer while its context is useful. Later
rounds can use a fresh, more capable implementer; the loop is capped and
residuals must be adjudicated rather than silently ignored
([fix-loop rules](superpowers/skills/subagent-driven-development/SKILL.md#L356)).

### TDD and evidence

[test-driven-development](superpowers/skills/test-driven-development/SKILL.md#L47)
requires red → green → refactor rather than tests added after implementation.

[verification-before-completion](superpowers/skills/verification-before-completion/SKILL.md#L25)
defines a particularly strict generic claim gate:

1. Identify the command that proves the claim.
2. Run the complete command freshly.
3. Read output and exit status.
4. Decide whether the evidence supports the claim.
5. Only then report success.

Different claims need different evidence. Passing tests does not prove the build
or lint is clean, and an agent/reviewer report is not proof
([evidence table](superpowers/skills/verification-before-completion/SKILL.md#L40)).

[requesting-code-review](superpowers/skills/requesting-code-review/SKILL.md#L32)
requires critical and important findings to be fixed before proceeding. The
[finishing-a-development-branch](superpowers/skills/finishing-a-development-branch/SKILL.md#L1)
skill then determines how verified work is integrated, but project CI,
security, UX, and deployment policies remain external.

## agent-skills

### Incremental vertical slices

[incremental-implementation](agent-skills/skills/incremental-implementation/SKILL.md#L21)
implements one thin, working slice at a time:

```text
implement slice → test → verify → commit → next slice
```

Each slice should be independently useful or demonstrably functional, with
small commits and immediate feedback
([slice rules](agent-skills/skills/incremental-implementation/SKILL.md#L36)).

### Composable quality catalog

Instead of one mandatory reviewer topology, `agent-skills` offers separate
capabilities:

- [test-driven-development](agent-skills/skills/test-driven-development/SKILL.md#L1)
- [code-review-and-quality](agent-skills/skills/code-review-and-quality/SKILL.md#L1)
- [browser-testing-with-devtools](agent-skills/skills/browser-testing-with-devtools/SKILL.md#L1)
- [security-and-hardening](agent-skills/skills/security-and-hardening/SKILL.md#L1)
- [ci-cd-and-automation](agent-skills/skills/ci-cd-and-automation/SKILL.md#L1)
- [shipping-and-launch](agent-skills/skills/shipping-and-launch/SKILL.md#L1)

This is flexible, but the caller must ensure the right skills are actually
composed. There is no universal guarantee that a separate reviewer agent ran.

The CI skill's recommended ordering is lint → type-check → unit tests → build →
integration tests → E2E → security audit/bundle checks
([quality-gate order](agent-skills/skills/ci-cd-and-automation/SKILL.md#L31)).
It explicitly warns against skipping an earlier gate because a later one passed
([gate semantics](agent-skills/skills/ci-cd-and-automation/SKILL.md#L54)).

PR policy recommends required review approval and passing checks
([branch protection](agent-skills/skills/ci-cd-and-automation/SKILL.md#L302)).
Deployment guidance includes staged rollout, manual verification, and rollback
([release stages](agent-skills/skills/ci-cd-and-automation/SKILL.md#L232)). The
security skill has its own post-implementation checklist
([security completion](agent-skills/skills/security-and-hardening/SKILL.md#L485)).

## OpenSpec

### Apply

[openspec-apply-change](OpenSpec/skills/openspec-apply-change/SKILL.md#L41)
loads the schema-supplied context and pending task list. It works through tasks
and marks a checkbox only after the described behavior is fully implemented.
It pauses for:

- ambiguous requirements
- design conflicts
- scope beyond the current specs/tasks
- blockers that prevent correct implementation

See the [implementation loop](OpenSpec/skills/openspec-apply-change/SKILL.md#L90)
and [pause conditions](OpenSpec/skills/openspec-apply-change/SKILL.md#L165).

### Three-axis verification

[openspec-verify-change](OpenSpec/skills/openspec-verify-change/SKILL.md#L50)
checks:

1. **Completeness:** artifacts and tasks are complete; every requirement has
   implementation evidence.
2. **Correctness:** behavior and tests cover requirements and scenarios.
3. **Coherence:** implementation follows the design and repository patterns.

Correctness and scenario evidence are detailed at
[line 79](OpenSpec/skills/openspec-verify-change/SKILL.md#L79), and design/code
coherence at [line 98](OpenSpec/skills/openspec-verify-change/SKILL.md#L98).

This verifier is primarily an evidence-inspection and reasoning workflow. It
does not universally mandate a particular build, lint, security, browser, or CI
command; those must come from the project and artifacts.

### Archive is not shipment

[openspec-archive-change](OpenSpec/skills/openspec-archive-change/SKILL.md#L70)
warns about incomplete artifacts or tasks but can continue after explicit user
confirmation. It synchronizes eligible delta specs and proves the sync before
moving the change
([sync gate](OpenSpec/skills/openspec-archive-change/SKILL.md#L119)).

Therefore:

- “verified” means the implementation aligns with artifacts according to the
  verification report.
- “archived” means the change lifecycle was closed and its spec deltas handled.
- neither word, alone, means deployed or released.

## GSD

### Multi-role phase execution

The [execute-phase workflow](gsd-core/gsd-core/workflows/execute-phase.md#L8)
groups plans by dependency and dispatches executor waves. The orchestrator is
deliberately lean; specialized roles cover planning, execution, verification,
debugging, integration, Nyquist/test analysis, and UI review
([role inventory](gsd-core/gsd-core/workflows/execute-phase.md#L47)).

The controller does not trust an agent's completion signal by itself. It
spot-checks Git state and generated summaries
([trust boundary](gsd-core/gsd-core/workflows/execute-phase.md#L34)).

### Verification layers

GSD exposes separate workflows for different claims:

- [gsd-add-tests](gsd-core/skills/gsd-add-tests/SKILL.md#L1)
- [gsd-code-review](gsd-core/skills/gsd-code-review/SKILL.md#L1)
- [gsd-verify-work](gsd-core/skills/gsd-verify-work/SKILL.md#L1)
- [gsd-validate-phase](gsd-core/skills/gsd-validate-phase/SKILL.md#L1)
- [gsd-ui-review](gsd-core/skills/gsd-ui-review/SKILL.md#L1)
- [gsd-review](gsd-core/skills/gsd-review/SKILL.md#L1)
- [gsd-debug](gsd-core/skills/gsd-debug/SKILL.md#L1)

Its MVP+TDD mode fails the execution gate when behavior-adding work lacks a
prior RED commit
([red-commit gate](gsd-core/gsd-core/workflows/execute-phase.md#L197)).

### Fail-closed shipping

The [ship workflow](gsd-core/gsd-core/workflows/ship.md#L8) is explicitly the
end of plan → execute → verify → ship. It accepts only verification status
`passed` and blocks missing reports, gaps, human-needed checks, or unknown
status. It also requires a clean working tree, valid branch/remote state, and
GitHub tooling
([ship preconditions](gsd-core/gsd-core/workflows/ship.md#L50)).

Security fails closed: open threats prevent shipping
([security gate](gsd-core/gsd-core/workflows/ship.md#L111)). This makes GSD's
“ship” substantially stronger than task completion or milestone bookkeeping.

## Compound Engineering

### Standalone work execution

[ce-work](compound-engineering-plugin/skills/ce-work/SKILL.md#L25) executes an
implementation-ready plan, specification, or concrete work request. It requires
verification evidence for behavior-bearing units and returns structured
receipts rather than a bare success assertion
([receipt contract](compound-engineering-plugin/skills/ce-work/SKILL.md#L152)).

### LFG autonomous pipeline

[lfg](compound-engineering-plugin/skills/lfg/SKILL.md#L3) composes one of the
broadest single autonomous pipelines among these collections:

```text
ce-plan readiness gate
        ↓
ce-work + verification receipt
        ↓
simplify/code review/fix
        ↓
browser testing where relevant
        ↓
durable residual findings
        ↓
commit + push + open PR
        ↓
babysit review and CI
        ↓
merge-ready report
```

The plan gate is defined at
[LFG step 1](compound-engineering-plugin/skills/lfg/SKILL.md#L21), and the work
receipt/evidence gate at
[step 2](compound-engineering-plugin/skills/lfg/SKILL.md#L27). Review fixes and
residuals must be made durable before DONE
([review closure](compound-engineering-plugin/skills/lfg/SKILL.md#L39)). The
shipping tail requires an open PR and CI babysitting
([shipping stages](compound-engineering-plugin/skills/lfg/SKILL.md#L49)).

### Specialized evidence and review

- [ce-code-review](compound-engineering-plugin/skills/ce-code-review/SKILL.md#L1)
  reviews code and can remain report-only or enter an explicitly authorized
  apply mode.
- [ce-simplify-code](compound-engineering-plugin/skills/ce-simplify-code/SKILL.md#L1)
  looks for unnecessary complexity after correctness exists.
- [ce-test-browser](compound-engineering-plugin/skills/ce-test-browser/SKILL.md#L9)
  enumerates every affected route as Pass, Fail, or Skip; silent omission is
  disallowed.
- [ce-resolve-pr-feedback](compound-engineering-plugin/skills/ce-resolve-pr-feedback/SKILL.md#L8)
  independently legitimacy-triages feedback before dispatching fixer agents.
- [ce-babysit-pr](compound-engineering-plugin/skills/ce-babysit-pr/SKILL.md#L59)
  watches review and CI but ends with “looks merge-ready, your call”; it does
  not merge autonomously.

External/OAuth/payment flows that cannot be exercised become explicit human
checks or documented pipeline skips rather than fabricated passes
([browser-test boundary](compound-engineering-plugin/skills/ce-test-browser/SKILL.md#L43)).

## BMAD Method

### Implement from frozen intent

BMAD build treats the approved spec as the sole execution source. The
[implementation step](BMAD-METHOD/src/bmm-skills/ship/bmad-build/step-03-implement.md#L29)
dispatches an implementation subagent, then the controller independently stages
and reads the actual diff. Tasks and acceptance criteria are marked satisfied
only after that inspection
([controller verification](BMAD-METHOD/src/bmm-skills/ship/bmad-build/step-03-implement.md#L39)).

An edge-case/acceptance matrix requires every relevant row to have a test that
actually ran and passed. Ambiguous frozen intent halts for a human rather than
being silently invented
([matrix gate](BMAD-METHOD/src/bmm-skills/ship/bmad-build/step-03-implement.md#L45)).

### Adversarial lenses

[bmad-review](BMAD-METHOD/src/core-skills/bmad-review/SKILL.md#L6) can apply
multiple independent lenses:

- adversarial critique
- edge-case hunting
- verification-gap analysis
- structural/editorial review
- prose review where relevant

Independent lenses run in parallel where possible
([parallel review](BMAD-METHOD/src/core-skills/bmad-review/SKILL.md#L32)). The
build controller does not accept findings blindly. It validates consequences,
triages them, fixes or defers them, and can re-derive the implementation. The
loop is capped at five re-derivations, after which unresolved ambiguity or
failure escalates to a human
([review loop](BMAD-METHOD/src/bmm-skills/ship/bmad-build/step-04-review.md#L31)).

The build skill does not push during implementation
([mutation boundary](BMAD-METHOD/src/bmm-skills/ship/bmad-build/step-03-implement.md#L8)).
It is a strong build/review workflow, but not by itself a universal production
release pipeline.

## spec-kit

### Before implementation

[speckit.analyze](spec-kit/templates/commands/analyze.md#L54) performs a
strictly read-only consistency and quality analysis across `spec.md`, `plan.md`,
and `tasks.md`. Constitution conflicts are CRITICAL and require the artifacts to
change rather than weakening the governing principle
([constitution authority](spec-kit/templates/commands/analyze.md#L60)).

Reviewer-owned checklists have deliberately narrow semantics: `[x]` means a
requirements-quality criterion was reviewed and satisfied; it does not mean the
implementation is complete
([checklist semantics](spec-kit/templates/checklist-template.md#L8)).

### Implementation gates

[speckit.implement](spec-kit/templates/commands/implement.md#L56) reads all
feature checklists as a gate. If unchecked items remain, it stops and asks
whether to proceed; it must not change reviewer-owned markers. It then loads
`tasks.md`, `plan.md`, data models, contracts, research, and quickstart material
as applicable.

The [task template](spec-kit/templates/tasks-template.md#L73) groups work by
independently testable user story. When tests are requested, they are written
first and must fail before implementation
([TDD tasks](spec-kit/templates/tasks-template.md#L81)). Each story ends in an
independent checkpoint, and the recommended strategy explicitly says “STOP and
VALIDATE” after the MVP story
([incremental validation](spec-kit/templates/tasks-template.md#L213)).

### Convergence

[speckit.converge](spec-kit/templates/commands/converge.md#L60) reads the spec,
plan, and tasks as the sole expected-work authority, compares them with the
codebase, and appends remaining actionable work to `tasks.md`. It reports
convergence only when implementation satisfies all three artifacts
([converged outcome](spec-kit/templates/commands/converge.md#L225)).

This is stronger than checking boxes alone, but PR review, CI, security,
deployment, and release remain project/constitution policy.

## gstack

### Implementation boundary and browser QA

gstack does not prescribe one canonical implementation or TDD executor skill.
Implementation happens through the project workflow or an agent optionally
spawned by `/spec` in a pinned fresh worktree
([spawn boundary](gstack/spec/SKILL.md#L1252)). Its distinctive controls surround
that implementation: optional plan review before coding, then browser QA, diff
review, proof-carrying ship, and a separately authorized merge/deploy workflow.

[gstack `/qa`](gstack/qa/SKILL.md#L1204) is browser-first user-behavior
verification. In diff-aware mode it maps changed files to affected routes and,
for each route, captures a screenshot, checks console errors, exercises the
workflow, and compares accessibility state. It explicitly refuses to substitute
unit tests or source inspection for browser evidence
([QA rules](gstack/qa/SKILL.md#L1465)).

Its repair loop is issue-scoped:

```text
reproduce with evidence
        ↓
minimal fix + one focused commit
        ↓
browser retest + before/after evidence
        ↓
verified / best-effort / reverted
        ↓
regression test when appropriate
```

See the [fix/retest loop](gstack/qa/SKILL.md#L1529). Every five fixes or after a
revert, a risk heuristic can stop for human direction, and the final phase
reruns all affected pages and compares the health score with the baseline
([final QA](gstack/qa/SKILL.md#L1652)).

### Review army and adversarial separation

[gstack `/review`](gstack/review/SKILL.md#L860) starts by comparing stated
intent with the actual diff to detect both scope creep and missing requirements
([scope check](gstack/review/SKILL.md#L874)). Its core pass examines data safety,
concurrency, LLM and shell trust boundaries, value completeness, frontend,
time-window, testing, and distribution risks
([core review](gstack/review/SKILL.md#L1221)). A finding cannot enter the main
report without quoted motivating source lines; unverified claims are
confidence-lowered and suppressed
([pre-emit evidence gate](gstack/review/SKILL.md#L1259)).

For diffs of at least 50 changed lines, testing and maintainability specialists
run by default, with security, performance, migration, API-contract, and design
specialists selected from the diff surface
([selection rules](gstack/review/SKILL.md#L1338)). All selected reviewers run in
parallel with fresh context
([parallel dispatch](gstack/review/SKILL.md#L1370)). Findings are merged by
evidence fingerprint, cross-specialist agreement raises confidence, and every
accepted finding enters the same Fix-First classification
([merge and handoff](gstack/review/SKILL.md#L1421)). Large or critical diffs add
a red-team agent whose job is specifically to find what the specialists missed
([red-team trigger](gstack/review/SKILL.md#L1483)).

Independently, every diff gets a fresh-context Claude adversarial pass looking
for production failures, security gaps, races, leaks, silent corruption, and
trust-boundary failures
([adversarial stage](gstack/review/SKILL.md#L1661),
[fresh-context prompt](gstack/review/SKILL.md#L1721)). An available Codex model
adds a cross-model adversarial pass; for large diffs, structured Codex review
turns P1 findings into an explicit fix-or-continue human gate
([large-diff gate](gstack/review/SKILL.md#L1770)). Optional-pass failure is
reported as missing coverage rather than misreported as a clean review.

### Evidence ledger, PR, and live delivery

`/ship` first integrates the base branch, then runs the project's tests plus
coverage, plan-completion, pre-landing review, PR-feedback, and adversarial
sections in a fixed workflow
([base integration](gstack/ship/SKILL.md#L1050),
[required sections](gstack/ship/SKILL.md#L1064)). Its final verification gate
binds evidence records to the exact commands that ran and to the tested
working-tree content. Stale or missing evidence triggers a fresh run; changed
code requires retesting, an available build must run, and a failed test blocks
the push
([evidence ledger](gstack/ship/SKILL.md#L1285)).

After coherent, bisectable commits, `/ship` pushes and creates or updates the PR;
push alone is explicitly not completion
([push boundary](gstack/ship/SKILL.md#L1329),
[mandatory PR tail](gstack/ship/SKILL.md#L1410)). The word **ship** here therefore
means verified branch-to-PR preparation, not unilateral merge.

The separate
[land-and-deploy](gstack/land-and-deploy/SKILL.md#L1472) workflow produces a
pre-merge readiness report covering review freshness, tests/E2E/evals,
documentation, and PR accuracy. A human chooses merge, hold/fix, or knowingly
merge with warnings; only the merge choices advance to the actual merge step
([authorization gate](gstack/land-and-deploy/SKILL.md#L1524)). After merge it
waits for deployment and performs a scope-sensitive live canary with HTTP,
console, performance, content, and screenshot evidence
([deploy monitoring](gstack/land-and-deploy/SKILL.md#L1773),
[canary](gstack/land-and-deploy/SKILL.md#L1838)). A failed canary returns to a
human expected/revert/investigate decision.

Consequently, gstack uses three useful scopes of “done”:

- **QA-verified:** observed user behavior passed the browser evidence loop.
- **Ship-complete:** checks passed and the PR was prepared/pushed, but not merged.
- **Landed/deployed:** a human authorized merge and post-deploy health was
  assessed.

## Ralph

The checked-out Ralph skills generate the PRD and convert it to runtime JSON;
they are not the loop executor itself. The conversion skill insists that each
story fit one fresh-agent iteration and be ordered by dependency
([story sizing](ralph/skills/ralph/SKILL.md#L46)).

Acceptance criteria must be mechanically checkable. Type checking is always
included; logic stories require tests, and UI stories require browser
verification
([verification criteria](ralph/skills/ralph/SKILL.md#L83)).

The `passes` field in `prd.json` is runtime status, not independent evidence.
There is no reviewer/critic or PR/CI/shipping skill in this checkout.

## Task Master and Backlog.md

### Task Master

Task Master stores `testStrategy` and supports statuses including `review`, but
it does not prescribe how a reviewer proves correctness. Dependency-ready work
is selected by `next`, and task completion can close subtasks
([task lifecycle](claude-task-master/docs/task-structure.md#L99)). CI,
spec-compliance review, and shipment are external policies.

### Backlog.md

Backlog.md tasks can carry acceptance criteria and a Definition of Done, and
move through To Do → In Progress → Done
([status model](Backlog.md/src/constants/index.ts#L43)). The tool persists task
state, comments, decisions, and milestones, but does not impose TDD, reviewer
agents, CI, or release gates. “Done” therefore means backlog status unless the
project's Definition of Done says more.

## Beads, Gas City, and Gastown

### Beads

Beads provides durable, atomic task orchestration: ready → claim/in-progress →
close, which releases dependents
([workflow](beads/README.md#L19)). It has no normative test, lint, build,
security, browser, review, CI, or release policy. `bd close` proves only issue
lifecycle closure.

### Gas City

Gas City supplies infrastructure for multi-agent runtimes, routing, formulas,
health patrol, providers, and convergence
([purpose](gascity/README.md#L15)). A caller can build a strong review pipeline
with it, but the collection does not define one generic
planned-work-to-production workflow.

### Gastown

Gastown is more opinionated operational machinery:

- the Mayor delegates work
- polecats execute from persistent hooks/beads
- the Witness detects and recovers stuck work
- the Refinery runs merge-queue gates, bisects failures, and re-dispatches work

See the [role overview](gastown/README.md#L50) and
[merge-queue behavior](gastown/README.md#L88).

`gt done` pushes the branch and creates the merge request, after which Refinery
validates and merges
([completion flow](gastown/README.md#L323)). Formula-defined gates control the
exact acceptance policy; for example, a formula can make `run-tests` a
predecessor to later steps
([formula example](gastown/README.md#L376)).

Gastown therefore provides shipping mechanics and recovery, but the formula and
project define what evidence is sufficient.

## Verification coverage matrix

Legend: **required** means the collection's main pipeline mandates it;
**available** means a dedicated skill or optional stage exists; **external**
means project/caller policy must supply it.

| Collection | TDD/unit | Type/lint/build | Spec/acceptance | Independent review | Browser/UX | Security | CI/PR | Release |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Matt Pocock | Required in implement flow | Required project checks | Required Spec reviewer | Required Standards + Spec agents | External | External | External | External |
| Superpowers SDD | Required for behavior changes | Fresh evidence when claimed | Required task/spec verdict | Required per task + final branch | External/project-specific | External/project-specific | Branch finishing available | External |
| agent-skills | Available | Available CI gates | Available via SPEC/tasks | Available skill | Available skill | Available skill | Available skill | Available skill |
| OpenSpec | Project-defined | Project-defined | Required verifier axis | Same verifier, not necessarily fresh agent | Project-defined | Project-defined | External | Archive only |
| GSD | Required in configured MVP+TDD mode | Pipeline/project checks | Required verification status | Multiple dedicated roles | Available/required when applicable | Fail-closed ship gate | Explicit ship prerequisites | Ship workflow |
| Compound/LFG | Evidence required | Project checks in work receipt | Plan/work receipt gates | Review/fix pipeline | Required when applicable | Project/review dependent | PR + CI babysit | Human merge decision |
| BMAD build | Matrix tests required | Project checks | Acceptance matrix required | Parallel adversarial lenses | Workflow-dependent | Workflow-dependent | External to build | External to build |
| spec-kit | Conditional on spec/request | Project-defined tasks | Checklist + converge | Analyze/converge, same agent allowed | Project-defined | Constitution/project-defined | External | External |
| gstack | Ship requires project test suites; TDD is external | Build required when present; other gates project-defined | Plan completion + scope-drift gates | Parallel specialists + fresh-context adversarial passes | QA available; live canary after deploy | Conditional specialists + adversarial review | `/ship` pushes and creates/updates PR | Human-gated `/land-and-deploy` |
| Ralph | Criteria require appropriate checks | Typecheck always expected | Story acceptance criteria | None | Expected for UI stories | External | External | External |
| Task Master/Backlog/Beads | External | External | Fields can record criteria | External | External | External | External | External |
| Gastown | Formula-defined | Formula-defined | Bead/formula-defined | Mayor/Refinery | Formula-defined | Formula-defined | Merge queue | Operational merge |

## Terminology crosswalk

| Word | Recommended precise meaning |
| --- | --- |
| Implement/execute | Change code or configuration to satisfy assigned work. It does not imply testing, review, or deployment. |
| Test | Run an automated behavior check. |
| TDD | Demonstrate RED → GREEN, normally followed by refactor, for each behavior slice. |
| Verify | Gather fresh evidence for an explicit claim: commands, output, exit status, browser/manual observation, or another inspectable result. |
| Validate | Assess fitness against a contract, model, policy, acceptance matrix, or user intent; judgment may be required. |
| Review | Independently inspect an artifact or diff for defects and quality. Review is not automatically proof of requirements compliance. |
| Critique/adversarial review | Deliberately seek failures, counterexamples, edge cases, contradictions, and missing verification. |
| Spec compliance/correctness | Implementation matches stated requirements, scenarios, and accepted decisions. |
| Code quality/standards | Implementation is maintainable, idiomatic, comprehensible, and consistent with architecture and repository conventions. |
| Acceptance | The contract owner agrees the behavior and criteria are satisfied; often a human gate for UX or external systems. |
| Complete/done | A scoped workflow state. Always qualify it: task-complete, tests-complete, review-complete, PR-open, or archive-complete. |
| Merge-ready | Required code, review, CI, security, UX/UAT, and policy gates are green; authorization to merge may still be separate. |
| Ship | Deliver as far as the named workflow promises, and state that boundary. For example, gstack `/ship` ends at a verified PR rather than merge. |
| Release/deploy | Publish or make the authorized artifact live after merge; production health verification and rollback remain separate evidence. |
| Evidence/receipt | Durable proof linking claims to commands/results, tests, matrices, diffs, commits, PRs, CI states, reviewer findings, and dispositions. |
| Fix loop | Finding/failure → independently confirm → patch or re-plan → rerun affected checks → re-review → record disposition. |

## Practical synthesis

A robust workflow assembled from the ideas compared here would use:

1. An explicit requirements authority and implementation plan.
2. Context-sized, dependency-aware execution units.
3. A test seam agreed before implementation.
4. Red-green evidence for behavior changes.
5. Fresh type/lint/build/test output rather than remembered results.
6. Separate spec-compliance and code-quality verdicts.
7. Adversarial edge-case and verification-gap review for consequential work.
8. Browser, UX, security, integration, and human checks when the change surface
   requires them.
9. A bounded fix/re-review loop with explicit escalation.
10. Durable evidence: task mapping, commands/results, diff/commits, reviewer
    findings/dispositions, PR URL, and CI state.
11. A distinct final authorization for merge or release.

No single collection dominates every dimension. Superpowers emphasizes generic
evidence discipline and per-task isolation; Matt Pocock has an unusually clean
spec-versus-standards review split; BMAD formalizes independent adversarial
lenses; GSD supplies a comprehensive role and ship hierarchy; Compound
Engineering offers an autonomous plan-to-PR pipeline; gstack combines
multi-specialist and cross-model review with browser evidence and a separately
authorized live-delivery path; OpenSpec emphasizes
artifact-to-implementation traceability; and `agent-skills` offers a broad
composable quality catalog.
