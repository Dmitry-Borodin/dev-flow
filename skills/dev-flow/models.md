# Models

Each role runs on a model class. The table below is a reference default: use it only when no
other instruction (project, local override, operator) says which model to use. Choose the least
capable class that does the job, and always state the model explicitly when assigning.

| Class | Roles | Claude | Codex | Effort |
| --- | --- | --- | --- | --- |
| Smart | developer, normal reviews | Opus | Sol | medium |
| Max | architecture and design reviews, design consult | Fable | Astra | high |
| Cheap | observer (reads logs and long runs, decides nothing), describer | Sonnet | Luna | low |
| Main session | coordinator | session's own | session's own | session's own |

## Overrides

The more specific layer wins, row by row: project instructions, a local override file, the
defaults above.

Keep the override in the skill's install scope (workspace or project, user, system) at that
scope's usual config location, e.g. `.dev-flow/models.md` in a workspace or
`$XDG_CONFIG_HOME/dev-flow/models.md` for a user. Keep a workspace file out of version control
unless the project shares it. Use the same table, changed rows only; installs and updates never
rewrite it.

When the operator says which models to use from now on, create or edit the override yourself,
changed rows only, never the defaults. Report what is in effect and where it is stored.
