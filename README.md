# dev-flow

A short, generic developer process skill: task, plan, delegation, review, pull request, merge,
and syncing tasks and instructions. Each project declares what stands behind its terms.
`skills/dev-flow/roles/` holds the briefs for each role: coordinator, developer, reviewer,
observer, describer and design consult. `skills/dev-flow/models.md` names the model for each
role; overrides go in the project instructions or a local file in the skill's install scope.

## Install

From the repository root:

```sh
mkdir -p ~/.claude/skills ~/.agents/skills
ln -s "$PWD/skills/dev-flow" ~/.claude/skills/dev-flow   # Claude Code
ln -s "$PWD/skills/dev-flow" ~/.agents/skills/dev-flow   # Codex
```

OpenCode may already read these directories; add a link to its own skills directory only if not.

## Adopt in a project

Add a line to the project instructions, such as "Use the dev-flow skill for development;
parameters: …", and declare the parameters listed at the top of
[SKILL.md](skills/dev-flow/SKILL.md).

`python3 -m unittest discover -s tests` checks the skill's structure.
