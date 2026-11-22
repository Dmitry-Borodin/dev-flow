# dev-flow — agent instructions

This is a **public** repository. Everything here is generic and in English: no private data,
names of people, hosts, accounts, incidents or project-specific rules. Those belong to the
projects that adopt the skill.

- `skills/dev-flow/` is the installable skill: `SKILL.md` plus `roles/*.md`. Each fact has one
  owning section; other sections and role files link to it instead of restating it.
- Keep it clear and without filler; prefer moving a detail to the adopting project over adding it.
- Check with `python3 -m unittest discover -s tests` (also runs in CI): line budgets, line width,
  no project, tool or model names, links between files.
- Develop it by its own process: [dev-flow](skills/dev-flow/SKILL.md).
