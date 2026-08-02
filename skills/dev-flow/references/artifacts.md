# Project Artifact Contract

Resolve one artifact root for requirements, plans, and review records.

## Resolution order

1. A path the current user expressly designates as the artifact root.
2. The top-level `artifact_root` value in `{project-root}/.dev-flow.yaml`.
3. The default `{project-root}/docs/dev-flow`.

Resolve a relative override against the project root. A path that merely names source material is not an artifact-root override. If the user names an existing requirement or plan file, reuse that file and keep the root resolution unchanged.

Do not create `.dev-flow.yaml` automatically. A project opts in by adding it explicitly.

Minimal project configuration:

```yaml
artifact_root: private/dev-flow
```

Use only this key in P0. If `.dev-flow.yaml` exists, require a valid YAML mapping containing exactly one non-empty string key, `artifact_root`. Reject malformed YAML, duplicate or unknown keys, non-string values, and a root that resolves to an existing file. Stop before writing; do not silently fall back to the default.

## Safety rules

- For `.dev-flow.yaml`, treat the configured value as relative to the project root. Reject an empty value, `.`, an absolute path, or any value containing a `..` segment.
- Resolve a relative user path against the project root. If its normalized or canonical destination is outside the project, obtain explicit authorization for that exact destination.
- For project configuration and user roots not authorized as external, confirm lexical normalization remains inside the project root. For an authorized external root, treat the exact authorized destination as the containment boundary.
- Resolve the canonical project root and every existing destination ancestor. Reject a symlink escape unless the user explicitly authorized the resulting external path. Re-check canonical containment immediately before creating a directory or writing a file.
- If the root crosses into a nested repository, read that repository's instructions, inspect its Git state separately, and report changes against the correct boundary.
- Preserve an existing project layout below the root. Otherwise use `requirements/`, `plans/`, and `reviews/` as needed. Store one review record per task with both review passes and their final dispositions.
- Reuse an existing artifact for the same work instead of creating a duplicate.

An expressly designated user artifact root wins over project configuration, but call out the override. If its canonical destination is outside the project root, obtain explicit authorization before writing there.
