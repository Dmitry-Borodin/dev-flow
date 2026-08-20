# Skill Setup and Artifact Conventions

This note compares how the skill collections in this workspace configure project
artifacts and how they use terms such as _docs_, _specs_, _plans_, _tasks_,
_tickets_, and _ADRs_.

Matt Pocock's skills, Compound Engineering, BMAD, OpenSpec, and GSD have
project-level setup or configuration for planning-document paths and artifact
roots. Beads and Gas City also bootstrap projects, but initialize operational
issue/runtime state rather than a general documentation workspace. Superpowers
and `agent-skills` mostly declare default paths directly in the skills that
produce each artifact.

## Related comparisons

- [Planning and Specification Workflows](planning-and-specification-workflows.md)
  compares how ideas become requirements, specifications, designs, plans, and
  execution units.
- [Development Execution and Verification Workflows](development-execution-and-verification-workflows.md)
  compares implementation orchestration, tests, reviewer/critic agents,
  completion evidence, CI, and shipping gates.

## Main project setup entry points

### Matt Pocock's skills

[setup-matt-pocock-skills](mattpocock-skills/skills/engineering/setup-matt-pocock-skills/SKILL.md#L9)
configures the issue tracker, triage labels, and domain-document layout. It
writes:

- `docs/agents/issue-tracker.md`
- `docs/agents/domain.md`
- optionally `docs/agents/triage-labels.md`
- an `## Agent skills` section in `CLAUDE.md` or `AGENTS.md`

It does not configure a general `plans/` directory. Specs and tickets go to the
configured tracker. With the
[local Markdown tracker](mattpocock-skills/skills/engineering/setup-matt-pocock-skills/issue-tracker-local.md#L1),
they live under `.scratch/<feature>/`.

Related convention-producing skills:

- [domain-modeling](mattpocock-skills/skills/engineering/domain-modeling/SKILL.md#L10)
  lazily creates `CONTEXT.md`, `CONTEXT-MAP.md`, and `docs/adr/`.
- [to-spec](mattpocock-skills/skills/engineering/to-spec/SKILL.md#L7)
  publishes a feature spec to the configured tracker.
- [to-tickets](mattpocock-skills/skills/engineering/to-tickets/SKILL.md#L7)
  publishes tracer-bullet implementation tickets with dependency edges.
- [wayfinder](mattpocock-skills/skills/engineering/wayfinder/SKILL.md#L19)
  creates a planning map and child decision tickets.

### Compound Engineering

[ce-setup](compound-engineering-plugin/skills/ce-setup/SKILL.md#L15) is the
clearest configurable artifact-root implementation in this workspace. It reads
`docs_root` from `.compound-engineering/config.yaml`; the default is `docs`.
Everything is then placed under that root, for example:

- `<root>/plans/`
- `<root>/solutions/`
- `<root>/ideation/`
- `<root>/explainers/`
- `<root>/dogfood-reports/`
- `<root>/pulse-reports/`

The main lifecycle is:

1. [ce-ideate](compound-engineering-plugin/skills/ce-ideate/SKILL.md#L42) creates
   ranked ideas.
2. [ce-brainstorm](compound-engineering-plugin/skills/ce-brainstorm/SKILL.md#L33)
   creates a requirements-only unified plan.
3. [ce-plan](compound-engineering-plugin/skills/ce-plan/SKILL.md#L47) enriches
   that artifact until it is implementation-ready.
4. [ce-work](compound-engineering-plugin/skills/ce-work/SKILL.md#L36) executes
   the implementation-ready plan.
5. [ce-compound](compound-engineering-plugin/skills/ce-compound/SKILL.md#L49)
   records durable learnings under `<root>/solutions/`.

### GSD

[gsd-new-project](gsd-core/skills/gsd-new-project/SKILL.md#L22) initializes a
fixed `.planning/` workspace containing:

- `.planning/PROJECT.md`
- `.planning/config.json`
- `.planning/research/`, when research is enabled
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`

[gsd-onboard](gsd-core/skills/gsd-onboard/SKILL.md#L19) is the brownfield
equivalent. It maps an existing codebase, ingests documentation, establishes
the planning files, and writes `.planning/onboarding/SUMMARY.md`.

[gsd-ingest-docs](gsd-core/skills/gsd-ingest-docs/SKILL.md#L17) imports
existing ADRs, PRDs, specifications, RFCs, and general documentation into the
same `.planning/` model. [gsd-config](gsd-core/skills/gsd-config/SKILL.md#L13)
and [gsd-settings](gsd-core/skills/gsd-settings/SKILL.md#L12) configure workflow
behavior in `.planning/config.json`; they do not relocate `.planning/`.

Phase work is stored under `.planning/phases/<phase>-<slug>/`. Relevant skills
include [gsd-discuss-phase](gsd-core/skills/gsd-discuss-phase/SKILL.md#L20),
[gsd-spec-phase](gsd-core/skills/gsd-spec-phase/SKILL.md#L20), and
[gsd-plan-phase](gsd-core/skills/gsd-plan-phase/SKILL.md#L20).

### BMAD Method

BMAD does not expose one setup skill for artifact locations. Its
[module configuration](BMAD-METHOD/src/bmm-skills/module.yaml#L28) asks for
three roots:

- `planning_artifacts` for briefs, PRDs, UX designs, architecture, and epics
- `implementation_artifacts` for stories, sprint state, reviews, and retrospectives
- `project_knowledge` for long-lived docs, research, and references

Individual workflows further configure their directories:

- [bmad-product-brief configuration](BMAD-METHOD/src/bmm-skills/plan/bmad-product-brief/customize.toml#L47)
- [bmad-prd configuration](BMAD-METHOD/src/bmm-skills/plan/bmad-prd/customize.toml#L63)
- [bmad-architecture configuration](BMAD-METHOD/src/bmm-skills/plan/bmad-architecture/customize.toml#L53)
- [bmad-spec configuration](BMAD-METHOD/src/bmm-skills/plan/bmad-spec/customize.toml#L35)
- [bmad-ux configuration](BMAD-METHOD/src/bmm-skills/plan/bmad-ux/customize.toml#L59)

### OpenSpec

OpenSpec setup is a terminal command rather than a skill:
[run `openspec init`](OpenSpec/README.md#L137). Project configuration lives in
[`openspec/config.yaml`](OpenSpec/docs/customization.md#L15).

The normal active change is:

```text
openspec/changes/<change>/
├── proposal.md
├── design.md
├── tasks.md
└── specs/
    └── <capability>/spec.md
```

The CLI resolves the actual planning home, so skills must use its returned
paths rather than assuming a local directory. See
[openspec-new-change](OpenSpec/skills/openspec-new-change/SKILL.md#L14),
[openspec-propose](OpenSpec/skills/openspec-propose/SKILL.md#L17), and
[openspec-ff-change](OpenSpec/skills/openspec-ff-change/SKILL.md#L29).

After implementation, delta specs are merged into durable main specs under
`openspec/specs/<capability>/spec.md` by
[openspec-sync-specs](OpenSpec/skills/openspec-sync-specs/SKILL.md#L42). The
change is then moved under `openspec/changes/archive/`.

### Superpowers

Superpowers has no central project setup skill. Its default paths are declared
by the producing skills:

- [brainstorming](superpowers/skills/brainstorming/SKILL.md#L94) writes approved
  designs/specs to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`.
- [writing-plans](superpowers/skills/writing-plans/SKILL.md#L18) writes
  implementation plans to `docs/superpowers/plans/YYYY-MM-DD-<feature>.md`.
- [subagent-driven-development](superpowers/skills/subagent-driven-development/SKILL.md#L136)
  keeps temporary execution ledgers, briefs, reports, and review packages under
  `.superpowers/sdd/<plan-basename>/`.

User-selected paths can override the spec and plan defaults, but there is no
persistent project configuration mapping equivalent to `docs_root`.

### agent-skills

`agent-skills` also has no central artifact setup skill.
[context-engineering](agent-skills/skills/context-engineering/SKILL.md#L20) is
the closest project bootstrap: it establishes persistent agent instructions in
files such as `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, or
`.github/copilot-instructions.md`.

The default development artifacts are:

- `SPEC.md`, or `SPEC-<module>.md` for decomposed capabilities, from
  [spec-driven-development](agent-skills/skills/spec-driven-development/SKILL.md#L22)
- `tasks/plan.md` and `tasks/todo.md` from
  [planning-and-task-breakdown](agent-skills/skills/planning-and-task-breakdown/SKILL.md#L143)
- ADRs under `docs/decisions/` by default, from
  [documentation-and-adrs](agent-skills/skills/documentation-and-adrs/SKILL.md#L36)

An external tracker may replace `tasks/todo.md`, but `tasks/plan.md` remains the
design and sequencing document.

### Beads, Gas City, and Gastown

[beads](beads/plugins/beads/skills/beads/SKILL.md#L38) requires a human to run
`bd init`. Durable task state lives in `.beads/` or the directory selected by
`BEADS_DIR`; it is graph-backed state rather than a collection of Markdown
ticket files.

[gc-city](gascity/internal/bootstrap/packs/core/skills/gc-city/SKILL.md#L8)
creates `city.toml` and `.gc/`.
[gc-rigs](gascity/internal/bootstrap/packs/core/skills/gc-rigs/SKILL.md#L31)
establishes `<city-root>/rigs/<rig-name>`, with each rig owning a Beads store.
[gc-work](gascity/internal/bootstrap/packs/core/skills/gc-work/SKILL.md#L13)
creates tasks, messages, molecules, and convoys as Beads rather than files.

Gastown's [convoy skill](gastown/docs/skills/convoy/SKILL.md#L8) likewise uses
Beads for workflow state; it has no separate planning-document bootstrap.

### Ralph

[Ralph's PRD skill](ralph/skills/prd/SKILL.md#L18) writes
`tasks/prd-<feature>.md`. The [Ralph execution skill](ralph/skills/ralph/SKILL.md#L256)
converts the PRD into ordered stories in `prd.json` and records execution state
in `progress.txt`.

### Collections without a relevant bootstrap

- Backlog.md has no generated planning workspace. Its
  [technical project manager skill](Backlog.md/.codex/skills/backlog-technical-project-manager/SKILL.md#L75)
  only defines parallel task clones and branches.
- `claude-task-master` contains no `SKILL.md` files.
- `spec-kit` has no planning bootstrap skill; its
  [community-extension skill](spec-kit/.github/skills/add-community-extension/SKILL.md#L15)
  updates a fixed catalog and documentation page.

## Specialized setup skills

These configure infrastructure or domain-specific layouts rather than the
planning-document system:

- [setup-ts-deep-modules](mattpocock-skills/skills/in-progress/setup-ts-deep-modules/SKILL.md#L39)
  configures package structure and dependency boundaries.
- [setup-pre-commit](mattpocock-skills/skills/misc/setup-pre-commit/SKILL.md#L8)
  configures Husky, lint-staged, and Prettier.
- [git-guardrails-claude-code](mattpocock-skills/skills/misc/git-guardrails-claude-code/SKILL.md#L20)
  configures dangerous-Git hooks.
- [wizard](mattpocock-skills/skills/engineering/wizard/SKILL.md#L8) generates an
  interactive setup or migration script.
- [scaffold-exercises](mattpocock-skills/skills/misc/scaffold-exercises/SKILL.md#L8)
  establishes a course-exercise directory hierarchy.
- [setup-deploy](gstack/setup-deploy/SKILL.md#L23) records deployment
  configuration in `CLAUDE.md`.
- [setup-gbrain](gstack/setup-gbrain/SKILL.md#L25) configures the gbrain CLI,
  database, MCP connection, and trust policy.
- [setup-browser-cookies](gstack/setup-browser-cookies/SKILL.md#L19) imports
  authenticated browser state.

## Cross-collection artifact mapping

| Collection | Requirements and design | Plan | Execution units | Durable decisions and context |
| --- | --- | --- | --- | --- |
| Matt Pocock | Tracker-side spec; locally `.scratch/<feature>/spec.md` | No canonical plan file | `.scratch/<feature>/issues/NN-slug.md` or tracker tickets | `CONTEXT.md`, `CONTEXT-MAP.md`, `docs/adr/` |
| Superpowers | `docs/superpowers/specs/YYYY-MM-DD-topic-design.md` | `docs/superpowers/plans/YYYY-MM-DD-feature.md` | Tasks embedded in the plan | Temporary `.superpowers/sdd/<plan>/` ledger |
| agent-skills | `SPEC.md` or `SPEC-<module>.md` | `tasks/plan.md` | `tasks/todo.md` or an external tracker | `docs/decisions/` by default |
| OpenSpec | `proposal.md`, `specs/**/spec.md`, `design.md` | The change directory is the planning envelope | `tasks.md` | Main specs under `openspec/specs/` |
| GSD | `PROJECT.md`, `REQUIREMENTS.md`, phase `SPEC.md` | `ROADMAP.md`, then phase `PLAN.md` files | Tasks inside phase plans | `STATE.md`, phase `CONTEXT.md`, research and summaries |
| Compound Engineering | Requirements-only unified plan | Same artifact enriched to implementation-ready | Runtime task tracker | `<root>/solutions/`, `CONCEPTS.md` |
| BMAD | Product brief, PRD, UX design, architecture, `SPEC.md` | Planning artifacts grouped under configured root | Stories and sprint status | Research and project knowledge |
| gstack | [GitHub issue spec when filed](gstack/spec/SKILL.md#L1176) plus a [local spec archive](gstack/spec/SKILL.md#L1194) | Active host plan enriched in place with a terminal [review report](gstack/plan-eng-review/SKILL.md#L1074) | Issue or review-derived implementation tasks | Expansion-mode [CEO plans](gstack/plan-ceo-review/SKILL.md#L1324), decision log, test plans, and review history under gstack state |
| Ralph | `tasks/prd-<feature>.md` | PRD becomes execution input | Stories in `prd.json` | `progress.txt` |
| Beads/Gas City | Usually supplied by external docs | Dependency graph in database | Beads, issues, molecules, and convoys | `.beads/` database |

## Important semantic differences

- Matt Pocock uses _ticket_ for an implementation-sized vertical slice, but
  Wayfinder also uses tickets for unresolved decision questions.
- Superpowers calls its approved design document a _spec_, even though the
  filename ends in `-design.md`.
- Compound Engineering's _plan_ begins as requirements-only and is later
  enriched in place; it covers more than the usual meaning of implementation
  plan.
- OpenSpec separates proposal, behavioral specification, technical design, and
  tasks instead of calling the whole set a plan.
- GSD uses _roadmap_ for project-level sequencing and _plan_ for one phase's
  execution.
- BMAD distinguishes product brief, PRD, architecture, UX design, spec, epic,
  and story as separate artifact types.
- gstack uses _spec_ for an executable issue-shaped handoff, _plan_ for the
  active implementation plan being reviewed, _CEO plan_ for a persisted
  product/scope record in expansion modes, and _GSTACK REVIEW REPORT_ for the
  structured verdict appended to the reviewed plan.

## Terminology and approximate industry-standard meanings

There is no universal standard directory layout. The meanings below are more
stable than the filenames or paths.

| Term | Meaning | Approximate standardness |
| --- | --- | --- |
| `docs/` | Container for human-readable documentation, not a document type itself | Very common directory name |
| Product brief | Short explanation of opportunity, audience, value, and scope | Common but informal |
| PRD | Product Requirements Document: problem, users, outcomes, scope, and acceptance expectations | Common in product organizations |
| Requirement | A testable behavior, constraint, or quality the system must satisfy | Formal and widely understood |
| Spec or specification | Normative contract describing what must be true; ideally observable and testable | Strongest general-purpose term |
| Proposal | Request to make a change, emphasizing why it is needed and what changes | Common |
| RFC | Reviewable proposal for a significant technical or organizational change | Very common for cross-team work |
| Design document | How the proposed system will work: architecture, interfaces, data, and trade-offs | Very common |
| Architecture document | Higher-level system structure and boundaries | Common; often longer-lived than a feature design |
| ADR | Architecture Decision Record: context, selected option, rationale, and consequences | Widely recognized convention |
| Roadmap | Longer-horizon ordering of outcomes, milestones, or phases | Standard product and program term |
| Plan | Concrete implementation sequence, dependencies, affected areas, and verification | Common but not precisely standardized |
| Task | Small executable checklist unit | Universal generic term |
| Issue or ticket | Tracked unit with identity, status, owner, and discussion history | Standard tracker terminology |
| Story | User-valued behavioral slice, normally with acceptance criteria | Standard Agile term |
| Epic | Group of related stories or tickets delivering a larger outcome | Standard Agile term |
| Context | Background needed to interpret the work | Generic; `CONTEXT.md` is mainly an agent-tool convention |
| State, ledger, progress | Resume information recording what happened and what comes next | Mostly agent-framework terminology |
| Artifact | Generic umbrella term for any durable output | Standard process term but intentionally nonspecific |

## Recommended neutral convention

For a project that is not committed to OpenSpec, GSD, BMAD, or another
framework, a relatively interoperable structure is:

```text
AGENTS.md
docs/
├── product/
│   └── PRD.md
├── specs/
│   └── <feature>.md
├── plans/
│   └── YYYY-MM-DD-<feature>.md
└── adr/
    └── 0001-<decision>.md
```

Keep executable work in GitHub Issues, Linear, Jira, or another tracker. If a
repository-local tracker is required, use `tasks/` or `.tasks/` with one file
per ticket.

A clean generic lifecycle is:

```text
brief or PRD -> spec -> design and ADRs -> implementation plan -> tickets or tasks -> code
```

Do not create this generic structure alongside OpenSpec's `openspec/`, GSD's
`.planning/`, or BMAD's configured artifact roots. Pick one system as the
source of truth and use `AGENTS.md` to point agents to it.
