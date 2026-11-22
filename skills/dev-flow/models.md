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

The more specific layer wins, row by row:

1. the project's instructions;
2. the local override file in the config directory that matches where the skill is installed:
   `$XDG_CONFIG_HOME/dev-flow/models.md` (default `~/.config/dev-flow/models.md`) for a user
   install, the system config directory, such as `/etc/dev-flow/models.md`, for a system-wide one;
3. the defaults above.

An override uses the same table and lists only the rows it changes. No install or update
rewrites it.

When the operator says which models to use from now on, create or edit the local override file
yourself with only the changed rows; never edit the defaults above. Report what is now in effect.
