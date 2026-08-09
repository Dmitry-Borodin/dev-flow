# Dev Flow V1 Foundation Implementation Plan

Specification: [`spec.md`](spec.md)

**Goal:** Replace the prompt-only P0 with a self-contained, repository-backed
workflow protocol and behavioral eval suite.

**Architecture:** Keep semantic judgment in concise phase references. Put
stable lifecycle data in JSON assets and enforce it with one Python
standard-library CLI. Keep the canonical skill name and directory `dev-flow`.

**Tech stack:** Markdown, JSON Schema 2020-12, Python 3.10+ standard library,
`unittest`, Git when available.

## Global constraints

- No Beads, external tracker, MCP, service, or third-party Python package.
- Preserve unrelated working-tree changes and use `apply_patch` for edits.
- All production behavior starts with a failing test.
- All state-changing `flowctl` commands emit JSON and append an event.
- The skill package contains only runtime instructions and required resources.

## Task 1: Freeze the protocol assets

**Files:**

- Create `skills/dev-flow/assets/workflow-v1.json`.
- Create `skills/dev-flow/assets/change-v1.schema.json`.
- Create `tests/test_protocol.py`.

**Produces:** stable phase/profile/result enums and a schema whose phase keys
match the workflow exactly.

- [x] Write tests that fail while the assets are absent and cover enum parity,
      required manifest fields, transition targets, and profile phase names.
- [x] Run `python3 -m unittest tests.test_protocol -v` and confirm the expected
      missing-file failure.
- [x] Add the smallest valid assets and rerun the focused test.

## Task 2: Implement deterministic state control

**Files:**

- Create `skills/dev-flow/scripts/flowctl.py`.
- Create `tests/test_flowctl.py`.

**Interface:**

```text
flowctl.py --change DIR init --id ID --project PROJECT --title TITLE --kind KIND
flowctl.py --change DIR [--workspace DIR] validate
flowctl.py --change DIR [--workspace DIR] status
flowctl.py --change DIR [--workspace DIR] transition --to PHASE|done --evidence PATH... --reason TEXT
flowctl.py --change DIR skip --reason TEXT
flowctl.py --change DIR block --kind KIND --message TEXT
flowctl.py --change DIR unblock --id ID --reason TEXT
flowctl.py --change DIR rewind --to PHASE --reason TEXT
```

- [x] Write failing tests for init, legal transition, illegal transition,
      evidence containment, skip, block/unblock, rewind, terminal close,
      event revisions, spec staleness, and workspace staleness.
- [x] Run each focused failing test before adding its behavior.
- [x] Implement only enough standard-library code to make the focused tests
      pass, then run `python3 -m unittest tests.test_flowctl -v`.

## Task 3: Route agents through phase contracts

**Files:**

- Rewrite `skills/dev-flow/SKILL.md`.
- Replace `skills/dev-flow/references/artifacts.md`.
- Create eight `skills/dev-flow/references/phase-*.md` files.
- Update `skills/dev-flow/agents/openai.yaml`.
- Create `tests/test_skill_structure.py`.

**Produces:** a short activation/runtime contract, direct one-level phase
routing, explicit authority boundaries, and no vendor-specific skill chaining.

- [x] Write structural tests for frontmatter, phase-reference routing, broken
      links, and forbidden third-party runtime dependencies; confirm RED.
- [x] Add the minimal skill and phase references; run the focused tests.
- [ ] Run the system `quick_validate.py` against `skills/dev-flow` (attempted;
      the bundled validator cannot start because its environment lacks
      `PyYAML`; the dependency-free structural suite covers its relevant V1
      checks).

## Task 4: Add and execute behavioral evals

**Files:**

- Create `evals/scenarios.json`.
- Create `tests/test_evals.py`.
- Create `docs/questions.md` for deferred design choices only.

**Produces:** machine-readable positive, negative, pressure, resume, stale,
rewind, restraint, and completion cases with explicit pass criteria.

- [x] Validate eval IDs, prompts, pressure factors, and pass criteria.
- [x] Run independent fresh-context evals on the current skill in parallel.
- [x] Compare raw decisions with the rubric and repair confirmed instruction
      gaps.
- [x] Rerun affected mechanical tests and evals.

## Task 5: Final verification and review

- [x] Run `python3 -m unittest discover -s tests -v`.
- [x] Run `python3 -m py_compile skills/dev-flow/scripts/flowctl.py`.
- [x] Run `flowctl` end-to-end through a temporary feature change.
- [x] Inspect `git diff --check` and the complete task diff.
- [x] Run independent outcome-critic and code/skill-review gates in parallel.
- [x] Fix confirmed blocking findings and rerun all affected gates.
