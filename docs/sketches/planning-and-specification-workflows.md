# Planning and Specification Workflows

This note compares how the skill collections in this workspace turn an idea or
request into implementation-ready work. It focuses on artifact meaning and
authority: which document records product intent, which records technical
design, which decomposes execution, what each collection calls those documents,
and which human or automated gates separate them.

For setup paths and artifact-root configuration, see
[Skill Setup and Artifact Conventions](skills-setup-and-artifact-conventions.md).
For implementation and completion gates, see
[Development Execution and Verification Workflows](development-execution-and-verification-workflows.md).

## High-level comparison

| Collection | Planning pipeline | Primary requirements authority | Technical planning term | Execution-unit term |
| --- | --- | --- | --- | --- |
| Matt Pocock | grilling → spec → tickets | Spec issue is a snapshot; durable language and decisions move to `CONTEXT.md` and ADRs | Implementation Decisions inside the spec | Ticket or issue |
| Superpowers | classify → collaborative design → design/spec → implementation plan | Approved design/spec | Implementation plan | Task inside the plan |
| agent-skills | idea one-pager → capability map → SPECIFY → PLAN → TASKS | Living `SPEC.md` or `SPEC-<module>.md` | `tasks/plan.md` | Task in `tasks/todo.md` or tracker |
| OpenSpec | proposal → delta specs → optional design → tasks | Main specs after delta synchronization | `design.md`; the change directory is the planning envelope | Checkbox in `tasks.md` |
| Compound Engineering | ideate → requirements-only unified plan → implementation-ready unified plan | One versioned unified-plan artifact, enriched in place | Implementation-ready unified plan | Runtime task derived from plan |
| GSD | PROJECT → REQUIREMENTS → ROADMAP → phase CONTEXT/SPEC → phase PLAN | `REQUIREMENTS.md` plus phase specification | Phase `PLAN.md` files | Plan task or phase unit |
| BMAD | brief → PRD → UX/architecture → spec/epics/stories | Finalized PRD or approved spec, depending workflow | Architecture, epics, stories, sprint plan | Story/task |
| spec-kit | constitution → specification → plan → tasks | Feature `spec.md`, governed by constitution | `plan.md` plus design artifacts | Checkbox in `tasks.md` |
| gstack | five-phase `/spec` → issue handoff/text + local archive → optional agent; or rough plan → CEO/design/eng/DX review | GitHub issue when filed for executable intent; active plan file for reviewed implementation approach | Plan plus terminal `GSTACK REVIEW REPORT`; optional CEO plan and test plan | GitHub issue or aggregated implementation task |
| Ralph | PRD → `prd.json` | PRD for intent; JSON for runnable status | No separate technical plan | User story |
| Task Master | PRD → parsed task graph → expansion/update | PRD is input; `tasks.json` is operational authority | Task details and dependencies | Task/subtask |
| Backlog.md | documents/decisions/milestones → backlog task | Project-specific document or decision record | Optional document; no mandatory planning pipeline | Task/subtask |
| Beads | external request → dependency graph | External spec or issue body | No prescribed plan document | Bead/issue |
| Gas City/Gastown | external work source → beads/formulas/molecules/convoys | Configured work provider | Formula/molecule describes orchestration | Bead, molecule step, convoy member |

## The biggest semantic differences

The collections do not agree on what a _spec_ or _plan_ is:

- Matt Pocock treats a spec as a useful record of decisions already made, but
  explicitly allows it to age. Lasting domain vocabulary belongs in
  `CONTEXT.md`, and lasting architectural choices belong in ADRs.
- Superpowers calls the approved technical design a design/spec. Its later plan
  is intentionally much more operational and may prescribe exact files, tests,
  interfaces, commands, and commits.
- `agent-skills` calls the SPEC a living source of truth and expects it to be
  updated before code when scope or decisions change.
- OpenSpec separates four concerns: proposal = why/high-level what, specs =
  observable behavior, design = how, tasks = execution checklist.
- Compound Engineering uses one _unified plan_ for both requirements and
  implementation planning, distinguished by readiness metadata.
- GSD uses _roadmap_ for project sequencing and _plan_ for executable work
  inside one phase.
- BMAD uses more product-management vocabulary than the other collections:
  product brief, PRD, user journey, functional requirement, non-functional
  requirement, architecture, epic, and story are distinct artifacts.
- gstack calls a backlog-ready GitHub issue a spec. Separately, its review
  skills refine an active implementation plan and append a structured review
  report; a CEO plan is a durable product/scope record, not the same artifact.

## Matt Pocock's skills

### Lifecycle

```text
grilling + domain-modeling
        ↓
to-spec
        ↓
to-tickets
        ↓
implement
```

The documented full path is `grill-with-docs → to-spec → to-tickets →
implement → code-review`. Work that fits in one context can skip the durable
spec/ticket branch and move from grilling directly to implementation. See the
[workflow explanation](mattpocock-skills/docs/engineering/to-spec.md#L11).

[grill-with-docs](mattpocock-skills/skills/engineering/grill-with-docs/SKILL.md#L1)
combines decision-focused interviewing with
[domain-modeling](mattpocock-skills/skills/engineering/domain-modeling/SKILL.md#L8).
Domain modeling maintains:

- `CONTEXT.md`: project glossary, explicitly not a specification or
  implementation-decision store.
- `CONTEXT-MAP.md`: index for multiple bounded contexts.
- `docs/adr/`: durable, consequential architectural decisions.

### What “spec” means

[to-spec](mattpocock-skills/skills/engineering/to-spec/SKILL.md#L7) does not run
a new interview. It synthesizes the conversation, codebase understanding,
glossary, and ADRs. Before publishing, it proposes test seams and confirms them
with the user ([line 13](mattpocock-skills/skills/engineering/to-spec/SKILL.md#L13)).

Its template contains:

- Problem Statement
- Solution
- extensive User Stories
- Implementation Decisions
- Testing Decisions
- Out of Scope
- Further Notes

The template deliberately avoids volatile file paths and code snippets
([template start](mattpocock-skills/skills/engineering/to-spec/SKILL.md#L21)).
The result is published as one tracker issue with `ready-for-agent`. A local
tracker instead places it at `.scratch/<feature-slug>/spec.md` through the
[local tracker contract](mattpocock-skills/skills/engineering/setup-matt-pocock-skills/issue-tracker-local.md#L3).

The collection describes this spec as long-lived relative to its tickets, but
still a snapshot that will eventually become stale. Lasting learning should be
promoted to the glossary or an ADR instead of continuously rewriting old specs
([snapshot discussion](mattpocock-skills/docs/engineering/to-spec.md#L38)).

### What “ticket” means

[to-tickets](mattpocock-skills/skills/engineering/to-tickets/SKILL.md#L25)
breaks the approved material into tracer-bullet vertical slices. Every ticket
declares blocker edges and should fit one fresh context window. The proposed
breakdown is shown to the user and revised before publication
([approval gate](mattpocock-skills/skills/engineering/to-tickets/SKILL.md#L42)).

Local tickets use one file per unit:

```text
.scratch/<feature>/issues/
├── 01-<slug>.md
├── 02-<slug>.md
└── 03-<slug>.md
```

Remote tickets become tracker issues with native blocking relationships where
possible ([publication rules](mattpocock-skills/skills/engineering/to-tickets/SKILL.md#L58)).

Wayfinder uses the same word differently. In
[wayfinder](mattpocock-skills/skills/engineering/wayfinder/SKILL.md#L19), a
ticket can be a decision question—research, prototype, grilling, or a manual
task—rather than an implementation slice. A map is the effort-level index; the
answer lives in the child ticket.

## Superpowers

### Three planning depths

[brainstorming](superpowers/skills/brainstorming/SKILL.md#L22) classifies work
before planning:

- **Spike:** approved probe, then a recommendation. No retained spec or plan.
- **Bounded:** short design in chat, explicit approval, then implementation. No
  plan file.
- **Architectural:** collaborative design, written design/spec, review, then a
  separate implementation plan.

The approval gate is universal: implementation cannot begin until intent and
design are approved ([hard gate](superpowers/skills/brainstorming/SKILL.md#L14)).

### Design/spec

Architectural work proceeds through context discovery, one-question-at-a-time
clarification, two or three approaches, trade-off discussion, and
section-by-section design approval
([architectural checklist](superpowers/skills/brainstorming/SKILL.md#L94)). The
approved artifact is:

```text
docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md
```

Despite the `-design.md` filename, the skill also calls this the spec. It covers
architecture, components, data flow, error handling, and testing. It is
self-reviewed for placeholders, contradictions, scope, and ambiguity, then
sent through a second user-review gate
([self-review and handoff](superpowers/skills/brainstorming/SKILL.md#L202)).

### Implementation plan

[writing-plans](superpowers/skills/writing-plans/SKILL.md#L8) writes:

```text
docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md
```

The plan cites the upstream spec, maps files and responsibilities, defines
interfaces between tasks, and gives bite-sized TDD, verification, and commit
steps. The plan is not a competing requirements authority: it “argues from the
spec” ([plan header contract](superpowers/skills/writing-plans/SKILL.md#L54)).
Before handoff it is checked for spec coverage, placeholders, and type/interface
consistency ([plan self-review](superpowers/skills/writing-plans/SKILL.md#L141)).

Afterward the user chooses between subagent-driven execution and inline plan
execution ([execution handoff](superpowers/skills/writing-plans/SKILL.md#L153)).

## agent-skills

### From idea to capability map

[idea-refine](agent-skills/skills/idea-refine/SKILL.md#L10) uses an
expand/converge flow and, after confirmation, can save a one-page idea at:

```text
docs/ideas/<idea-name>.md
```

The one-pager records the problem, recommended direction, assumptions, MVP,
“Not Doing,” and open questions
([output contract](agent-skills/skills/idea-refine/SKILL.md#L108)).

[spec-driven-development](agent-skills/skills/spec-driven-development/SKILL.md#L22)
then defines:

```text
Capability Map, when needed
    ↓
SPECIFY
    ↓
PLAN
    ↓
TASKS
    ↓
IMPLEMENT
```

Every phase requires human validation. Multi-capability initiatives first get
an approved capability map: stable module IDs, responsibilities, dependency
edges, and build order
([capability map](agent-skills/skills/spec-driven-development/SKILL.md#L44)).
Each module then receives its own `SPEC-<module-id>.md`.

### Living SPEC

The SPEC is explicitly the shared source of truth. It includes objective,
technology, exact commands, project structure, style, testing strategy,
boundaries, success criteria, and open questions
([spec contents](agent-skills/skills/spec-driven-development/SKILL.md#L84)).

For a single project the command convention is root `SPEC.md`, established by
[the spec command](agent-skills/commands/spec.toml#L14). Unlike Matt's snapshot,
this document is living: update it before implementation when scope or
decisions change, commit it, and reference it from pull requests
([living-spec rules](agent-skills/skills/spec-driven-development/SKILL.md#L204)).

### Plan and task register

[planning-and-task-breakdown](agent-skills/skills/planning-and-task-breakdown/SKILL.md#L22)
is canonical for decomposition mechanics. It writes:

```text
tasks/plan.md
tasks/todo.md
```

The plan remains Markdown because design choices, risks, and open questions do
not map cleanly to tracker items. The task register may be replaced by an
external tracker, with the plan retaining an ordered index of issue links
([output rules](agent-skills/skills/planning-and-task-breakdown/SKILL.md#L143)).
Tasks are dependency-ordered vertical slices with acceptance criteria and a
verification step.

## OpenSpec

### Schema-defined artifact graph

OpenSpec does not define these words only in prose. Its default
[spec-driven schema](OpenSpec/schemas/spec-driven/schema.yaml#L1) defines an
artifact dependency graph:

```text
proposal
   ↓
delta specs
   ↓
optional design
   ↓
tasks
```

OpenSpec instructions returned for the selected schema are authoritative even
when an artifact name looks familiar
([instruction authority](OpenSpec/skills/openspec-propose/SKILL.md#L131)).

### Artifact meanings

- **Proposal:** concise WHY, high-level WHAT, impact, and capability list. Its
  capability declarations determine which specs must follow
  ([proposal schema](OpenSpec/schemas/spec-driven/schema.yaml#L10)).
- **Delta specs:** externally observable behavioral changes, not implementation
  internals. They use ADDED/MODIFIED/REMOVED/RENAMED requirements, normative
  SHALL/MUST language, and testable WHEN/THEN scenarios
  ([spec schema](OpenSpec/schemas/spec-driven/schema.yaml#L43)).
- **Design:** optional HOW for cross-cutting architecture, dependencies, data,
  security, performance, or migration complexity
  ([design schema](OpenSpec/schemas/spec-driven/schema.yaml#L131)).
- **Tasks:** dependency-ordered, single-session checkboxes consumed by apply
  ([task schema](OpenSpec/schemas/spec-driven/schema.yaml#L166)).

Default active paths look like:

```text
openspec/changes/<change>/
├── proposal.md
├── specs/<capability>/spec.md
├── design.md
└── tasks.md
```

The CLI-returned `planningHome`, `changeRoot`, and artifact paths are the real
authority; skills must not hardcode those defaults
([path resolution](OpenSpec/skills/openspec-propose/SKILL.md#L70)).

### Main specs versus delta specs

Active-change specs describe proposed deltas. Durable main specs live under:

```text
openspec/specs/<capability>/spec.md
```

[openspec-sync-specs](OpenSpec/skills/openspec-sync-specs/SKILL.md#L39) merges
the deltas intelligently into one canonical requirements representation. A
delta is not copied verbatim
([merge semantics](OpenSpec/skills/openspec-sync-specs/SKILL.md#L66)).

[openspec-new-change](OpenSpec/skills/openspec-new-change/SKILL.md#L52) only
scaffolds. `continue-change` creates one next-ready artifact. `propose` may
generate all implementation prerequisites but remains strictly planning-only;
implementation needs a separate explicit apply request
([planning boundary](OpenSpec/skills/openspec-propose/SKILL.md#L14)).

## Compound Engineering

### One plan, two readiness states

[ce-brainstorm](compound-engineering-plugin/skills/ce-brainstorm/SKILL.md#L11)
produces a requirements-only unified plan: the WHAT, including product contract,
scope, success criteria, and settled decisions. The artifact carries:

```yaml
artifact_contract: ce-unified-plan/v1
artifact_readiness: requirements-only
```

[ce-plan](compound-engineering-plugin/skills/ce-plan/SKILL.md#L11) enriches the
same artifact with the HOW until it is implementation-ready. It adds ordered
work, technical decisions, validation, and handoff context. Writing the file is
not completion; research, confidence checks, document review, and the mandatory
handoff must also finish
([planning phases](compound-engineering-plugin/skills/ce-plan/SKILL.md#L33)).

Plans live under the configured `<root>/plans/`, and durable learnings under
`<root>/solutions/`
([artifact-root contract](compound-engineering-plugin/skills/ce-plan/SKILL.md#L47)).
The plan can be Markdown or HTML, but never both for one output
([format choice](compound-engineering-plugin/skills/ce-plan/SKILL.md#L73)).

The autonomous LFG pipeline accepts only a plan whose metadata says
`artifact_readiness: implementation-ready` and `execution: code`
([readiness gate](compound-engineering-plugin/skills/lfg/references/plan-brief.md#L17)).

### Decision vocabulary

Compound Engineering calls important plan decisions **KTDs** (Key Technical
Decisions). Session-settled choices include the decision, provenance, rejected
alternative, and reason, then become canonical labeled entries in the plan
([settled-decision bridge](compound-engineering-plugin/skills/lfg/references/plan-brief.md#L19)).

## GSD

### Project-level planning

The project workflow is:

```text
questioning
    ↓
optional research
    ↓
PROJECT.md
    ↓
REQUIREMENTS.md
    ↓
ROADMAP.md + STATE.md
```

The user explicitly confirms readiness before `PROJECT.md` is created
([questioning gate](gsd-core/gsd-core/workflows/new-project.md#L199)).

- `PROJECT.md` is living project context: vision, validated requirements,
  active requirements, out-of-scope items, constraints, and key decisions
  ([template](gsd-core/gsd-core/templates/project.md#L1)).
- `REQUIREMENTS.md` provides [testable requirement IDs](gsd-core/gsd-core/templates/requirements.md#L79)
  and [phase traceability](gsd-core/gsd-core/templates/requirements.md#L99).
- `ROADMAP.md` groups requirements into phases.
- `STATE.md` is resumable execution memory rather than requirements authority.

Requirement states are Pending, In Progress, Complete, or Blocked, and every
requirement maps to exactly one roadmap phase
([traceability rules](gsd-core/gsd-core/templates/requirements.md#L99)).

### Phase-level planning

The phase workflow uses context, optional spec/research, one or more `PLAN.md`
files, execution summaries, and verification. The
[plan-phase workflow](gsd-core/gsd-core/workflows/plan-phase.md#L1) coordinates
researcher, planner, and checker roles. Plans can revise through a maximum of
three checker loops
([role and revision model](gsd-core/gsd-core/workflows/plan-phase.md#L22)).

This is the important vocabulary split:

- **Roadmap:** project/milestone ordering.
- **Phase:** coherent delivery stage owning a group of requirements.
- **Context:** phase-specific decisions and constraints.
- **Spec:** detailed phase behavior or acceptance contract when required.
- **Plan:** executable work inside that phase.
- **Summary:** durable account of what a completed plan delivered.

## BMAD Method

### Product and delivery vocabulary

BMAD has the most differentiated document set:

```text
discovery / research
        ↓
product brief
        ↓
PRD
        ↓
UX design + architecture
        ↓
spec / epics / stories
        ↓
sprint planning
```

[bmad-product-brief](BMAD-METHOD/src/bmm-skills/plan/bmad-product-brief/SKILL.md#L31)
creates the early product framing. [bmad-prd](BMAD-METHOD/src/bmm-skills/plan/bmad-prd/SKILL.md#L24)
supports Create, Update, and read-only Validate modes.

The PRD vocabulary includes:

- user journeys (`UJ-N`)
- functional requirements (FRs)
- non-functional requirements (NFRs)
- open questions
- assumptions
- phase blockers

Finalization audits the run memory, reconciles inputs, runs reviewer gates,
resolves blockers, and sets `prd.md` to `status: final`
([PRD gate](BMAD-METHOD/src/bmm-skills/plan/bmad-prd/SKILL.md#L71)).

UX deliberately separates
[DESIGN.md from EXPERIENCE.md](BMAD-METHOD/src/bmm-skills/plan/bmad-ux/SKILL.md#L11):
how it looks versus how it works. Architecture and feature specs are separate
planning workspaces.

### The memlog

Each major document workspace maintains `.memlog.md` as an append-only audit
trail of decisions, changes, assumptions, overrides, and events. The brief or
PRD is the distilled reader-facing document; the memlog is canonical workflow
memory
([PRD memory contract](BMAD-METHOD/src/bmm-skills/plan/bmad-prd/SKILL.md#L14)).

This differs from both a conventional ADR and a plan:

- ADR: one durable decision and its rationale.
- Plan: future implementation work.
- Memlog: the evolving audit trail from which the current document was derived.

## spec-kit

spec-kit is explicitly specification-driven: the specification is primary and
code is its expression
([principle](spec-kit/spec-driven.md#L5)). Its standard pipeline is:

```text
constitution
    ↓
/speckit.specify → specs/<branch>/spec.md
    ↓
/speckit.plan → plan.md + design artifacts
    ↓
/speckit.tasks → tasks.md
```

The **constitution** records durable project principles and drives planning
gates ([constitution role](spec-kit/spec-driven.md#L274)). The feature directory
can contain:

- `spec.md`: user stories and acceptance criteria
- `plan.md`: implementation plan
- `research.md`: Phase 0 decisions and unknown resolution
- `data-model.md`
- `contracts/`
- `quickstart.md`
- `tasks.md`

See the [plan template](spec-kit/templates/plan-template.md#L1). A Constitution
Check must pass before Phase 0 research and be repeated after Phase 1 design
([plan gates](spec-kit/templates/plan-template.md#L39)).

## gstack

### Executable issue specification

[gstack `/spec`](gstack/spec/SKILL.md#L5) means a backlog-ready specification,
not a permanent repository-local PRD. Its strict five-phase sequence is:

```text
Why and observable done condition
        ↓
scope, boundaries, MVP, failure modes, rollback
        ↓
code-grounded technical interrogation
        ↓
human review of the complete draft
        ↓
quality/redaction gates → issue handoff/text + local archive
```

Phase 1 requires the affected party, verified current behavior, target behavior,
reason for acting now, and a measurable done condition
([Why gate](gstack/spec/SKILL.md#L880)). Phase 2 locks exclusions, touched
systems, ordering, the smallest valuable cut, failure modes, and rollback
([scope gate](gstack/spec/SKILL.md#L934)). Phase 3 must inspect code before
asking technical questions ([evidence gate](gstack/spec/SKILL.md#L946)), and
Phase 4 iterates on a full draft until the user confirms it
([draft gate](gstack/spec/SKILL.md#L981)).

A default-on second-model gate scores whether an unfamiliar implementer could
execute the spec. Low scores enter a bounded revise-or-human-disposition loop
([quality outcomes](gstack/spec/SKILL.md#L1114)); semantic and fail-closed
redaction checks run before the draft is sent or filed
([redaction boundary](gstack/spec/SKILL.md#L1025)).

When GitHub CLI authentication is available, Phase 5 files the approved spec as
a GitHub issue and logs its central approach as an issue-scoped durable
decision. Otherwise it emits paste-ready issue text, making the issue the normal
intended external handoff rather than an unconditional output
([issue handoff](gstack/spec/SKILL.md#L1176)). It also archives an atomic local
copy at:

```text
$GSTACK_STATE_ROOT/projects/$SLUG/specs/
  <timestamp>-<pid>-<title-slug>.md
```

The archive records the issue URL/number, branch, plan mode, and optional
worktree execution metadata. It stays local unless `--sync-archive` is selected
([archive contract](gstack/spec/SKILL.md#L1194)). In plan mode the default is
file-only and the spec is loaded into the active plan file; in execution mode it
can spawn an agent from a pinned SHA in a fresh worktree after explicit dirty-tree
and final-spawn gates ([dispatch modes](gstack/spec/SKILL.md#L1143)).

### Plan review artifacts

gstack's other planning route starts from an existing rough plan. `/autoplan`
means “rough plan in, fully reviewed plan out”
([contract](gstack/autoplan/SKILL.md#L934)) and applies review phases strictly in
this order:

```text
CEO/scope → Design, when applicable → Engineering → DX, when applicable
```

Each phase must write its outputs before the next begins
([sequencing gate](gstack/autoplan/SKILL.md#L1000)). The pipeline preserves the
original plan in
`~/.gstack/projects/$SLUG/<branch>-autoplan-restore-<timestamp>.md`
([restore point](gstack/autoplan/SKILL.md#L1057)), produces diagrams, failure
registries, an audit trail, and a separate test-plan artifact, then aggregates
review findings into implementation tasks
([engineering deliverables](gstack/autoplan/SKILL.md#L1432)).

The vocabulary is deliberately distinct:

- **Spec:** an executable, GitHub-issue-shaped backlog item.
- **Issue:** the external work item and primary handoff link.
- **Plan:** the current implementation approach being reviewed and edited.
- **CEO plan:** when Expansion or Selective Expansion mode persists one, a
  durable vision and explicit scope-decision record under
  `~/.gstack/projects/$SLUG/ceo-plans/`
  ([format and path](gstack/plan-ceo-review/SKILL.md#L1324)).
- **GSTACK REVIEW REPORT:** the structured terminal section of a reviewed plan,
  including runs/status/findings, verdict, and unresolved decisions. It is a
  blocking exit requirement, not a substitute for the plan body
  ([report gate](gstack/plan-eng-review/SKILL.md#L1074)).
- **Implementation Tasks:** actionable findings aggregated across plan-review
  phases before final approval
  ([task aggregation](gstack/autoplan/SKILL.md#L1679)).

Ordinary review decisions may be automated, but premise confirmation and a
cross-model proposal to reverse the user's direction remain human decisions
([decision boundary](gstack/autoplan/SKILL.md#L1011)).

## Ralph

[Ralph's PRD skill](ralph/skills/prd/SKILL.md#L15) asks clarifying questions
and writes `tasks/prd-<feature-name>.md`. The
[Ralph conversion skill](ralph/skills/ralph/SKILL.md#L46) translates it into
`prd.json` with one user story per fresh-agent iteration.

The JSON vocabulary is:

- `branchName`
- `userStories`
- story `id`, `title`, `description`
- `acceptanceCriteria`
- `priority`
- `passes`
- `notes`

See [prd.json.example](ralph/prd.json.example#L1). There is no separate design
or technical-plan artifact in this collection. `passes: false` means the story
has not yet been completed by the runtime; it is status, not proof.

## Task Master

Task Master turns a PRD into a tagged, dependency-aware task collection.
Default locations are:

```text
.taskmaster/docs/prd.txt
.taskmaster/tasks/tasks.json
.taskmaster/state.json
```

See the [path constants](claude-task-master/src/constants/paths.js#L23) and
[task structure](claude-task-master/docs/task-structure.md#L351).

Its vocabulary is operational rather than document-heavy:

- **Tag:** isolated task-list context.
- **Task:** ID, title, description, details, priority, dependencies, test
  strategy, and status.
- **Subtask:** smaller child execution unit.
- **Next:** the first eligible task whose dependencies are satisfied.

Statuses include pending, in-progress, done, review, deferred, and cancelled
([status model](claude-task-master/docs/task-structure.md#L143)). It does not
prescribe discovery, design, ADR, or roadmap documents; those remain PRD input
or task detail.

## Backlog.md

Backlog.md is a filesystem-backed work-management model rather than a mandatory
specification pipeline. Its configurable directories support:

- tasks, drafts, and completed tasks
- documents
- decisions
- milestones

See the [default path constants](Backlog.md/src/constants/index.ts#L4).

Its durable vocabulary includes Task, Draft, Completed Task, Milestone,
Document, Decision, acceptance criteria, Definition of Done, comments, and
parent/subtask relationships. Default task status is To Do → In Progress → Done
([status and type constants](Backlog.md/src/constants/index.ts#L43)).

Because documents and decisions are independent entities, a project can model
a PRD, spec, design, or ADR, but Backlog.md itself does not force one of those
planning lifecycles.

## Beads, Gas City, and Gastown

### Beads

Beads is a durable dependency-graph issue tracker, not a product-planning
method. Its core flow is create → relate dependencies → ready → claim → close
([overview](beads/README.md#L15)). It explicitly discourages Markdown TODO
lists and stores durable memory through the database
([agent workflow](beads/README.md#L49)). Requirements and designs therefore
come from an external document or the issue body.

### Gas City

Gas City is an orchestration substrate. Its planning vocabulary—order, bead,
formula, molecule, convoy, run, rig, gate, and convergence—describes how work is
routed and coordinated, not how product requirements are authored. The
configured provider, normally Beads, owns work identity and status
([provider overview](gascity/README.md#L71)).

### Gastown

Gastown likewise keeps durable work in Beads. A **convoy** bundles work; a
**formula** is a reusable workflow definition; a **molecule** is a formula
instantiated as trackable steps
([concepts](gastown/README.md#L72)). These can execute a supplied plan, but do
not replace the plan's requirements authority.

## Terminology crosswalk

| Word | Approximate meaning across these collections | Important exceptions |
| --- | --- | --- |
| Idea | Uncommitted opportunity or problem worth exploring | CE may persist ranked ideation; most collections keep it conversational |
| Brief | Concise product framing before detailed requirements | BMAD gives it a formal workspace; agent-skills calls a similar artifact an idea one-pager |
| PRD | Product requirements: users, outcomes, scope, behavior, success | Ralph treats it as direct input to story generation; BMAD puts it inside a larger product workflow |
| Requirement | Normative behavior or constraint that can be checked | OpenSpec uses SHALL/MUST and scenarios; GSD uses IDs and phase traceability |
| Spec | Shared behavioral/decision contract | Superpowers' spec is also technical design; Matt's is a snapshot; OpenSpec active specs are deltas; gstack's spec is an executable issue |
| Proposal | Why and high-level what should change | Formal in OpenSpec; other collections often fold it into a brief/spec |
| Design | How the system or experience will work | Superpowers calls the design its spec; BMAD splits UX look and experience behavior |
| Architecture | System-level structure, boundaries, technology, and consequential trade-offs | Matt records only durable choices as ADRs rather than one mandatory architecture document |
| ADR | One architectural decision, its context, alternatives, and consequences | BMAD memlog is an audit trail, not an ADR replacement |
| Plan | Ordered implementation approach with dependencies and verification | CE's plan also contains requirements; GSD reserves plan for phase-level execution; gstack review skills enrich an existing plan in place |
| Review report | Structured findings, verdict, and unresolved decisions after artifact review | gstack requires it as the terminal section of a reviewed plan; it is not the implementation plan itself |
| Roadmap | Project-level sequence of phases/outcomes | Explicit in GSD; often absent elsewhere |
| Phase | Coherent delivery stage grouping requirements and plans | GSD and spec-kit use the term systematically |
| Task | Small executable checklist unit | Can be document-local, tracker-backed, or runtime-only |
| Ticket/issue | Identified work item with status, ownership, discussion, and dependencies | Matt Wayfinder tickets can be decision questions rather than implementation work |
| Story | User-valued behavior with acceptance criteria | BMAD, Ralph, and Agile-derived systems use it most explicitly |
| Epic | Large user/business outcome decomposed into stories | Prominent in BMAD, optional or absent elsewhere |
| Context | Background and constraints needed to interpret current work | Matt uses it as domain glossary; GSD uses project and phase context |
| State/progress/memlog | Resumption and audit memory | Usually not requirements authority, though BMAD memlog is canonical workflow memory |

## Choosing a planning model

- Choose **Matt Pocock** for intensive decision clarification followed by
  tracker-native, context-sized work.
- Choose **Superpowers** for explicit approval gates and an unusually detailed
  spec-to-plan handoff.
- Choose **agent-skills** for a conventional living SPEC plus separate plan and
  task register.
- Choose **OpenSpec** when capability requirements need durable main specs and
  explicit change deltas.
- Choose **Compound Engineering** when one enriched plan should travel through
  an automated implementation and shipping pipeline.
- Choose **GSD** for a complete project → milestone → phase hierarchy with
  persistent state.
- Choose **BMAD** when product discovery, PRD, UX, architecture, and Agile
  delivery need separately governed artifacts.
- Choose **spec-kit** for constitution-governed feature specifications and
  feature-local design artifacts.
- Choose **gstack** for issue-shaped executable specs plus multi-lens product,
  design, engineering, and DX review of an active plan.
- Use **Ralph**, **Task Master**, **Backlog.md**, or **Beads** when requirements
  already exist and the main need is execution-unit management.

These models should not be overlaid casually. Select one requirements authority
and one execution tracker, then make every other artifact link back to those
sources instead of duplicating them.
