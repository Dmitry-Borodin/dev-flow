# Models

Each role runs on a model class. The table below is a reference default: use it only when no
other instruction (project, local override, operator) says which model to use. Choose the least
capable class that does the job, and always state the model explicitly when assigning.

| Class | Roles | Claude | Codex | Effort | Compact at |
| --- | --- | --- | --- | --- | --- |
| Smart | developer, normal reviews | Opus | Sol | medium | 400000 |
| Max | architecture and design reviews, design consult | Fable | Astra | high | 400000 |
| Cheap | observer, describer | Sonnet | Luna | low | default |
| Main session | coordinator | session's own | session's own | session's own | session's own |

The observer reads logs and long runs and decides nothing.

## Context window

Launch each worker with its class's `Compact at`, the context size in tokens at which it
auto-compacts: pass it through the launcher's option or use a role definition that sets it. If
neither exists, launch without it; add no workaround. For "default" pass nothing.

## Overrides

The more specific layer wins, row by row: the operator's instructions (the current request,
then the agent's saved memory), project instructions, a local override file, the defaults above.

Keep the override in the skill's install scope (workspace or project, user, system) at that
scope's usual config location, e.g. `.dev-flow/models.md` in a workspace or
`$XDG_CONFIG_HOME/dev-flow/models.md` for a user. Keep a workspace file out of version control
unless the project shares it. Use the same table, changed rows only; installs and updates never
rewrite it. A cell an override row leaves out, such as `Compact at` in an older table, keeps the
default value.

When the operator says which models to use from now on, create or edit the override yourself,
changed rows only, never the defaults. Report what is in effect and where it is stored.
