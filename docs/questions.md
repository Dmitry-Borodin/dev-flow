# Open Questions After V1

These choices are intentionally deferred. None blocks the self-contained V1.

1. **Project and change discovery.** Should a later version introduce a local
   project registry, a repository-owned config, or only explicit paths?
2. **External artifact roots.** Should private sibling repositories be resolved
   by logical repository aliases, and where should machine-local paths live?
3. **Multiple repositories.** Is one combined workspace fingerprint sufficient,
   or should verification evidence record one fingerprint per logical repo?
4. **Crash atomicity.** Is revision parity plus atomic replacement sufficient,
   or should `change.json` and `events.jsonl` use a recoverable transaction
   journal?
5. **Concurrency.** Should a later `flowctl` reject concurrent writers with a
   lock, or support optimistic revision preconditions?
6. **Acceptance traceability.** Should `AC-* -> IU-* -> V-*` coverage become a
   mandatory machine check, or remain a semantic phase check?
7. **Terminal operations.** Which authorization and evidence should dedicated
   `cancel` and `supersede` commands require?
8. **Legacy adoption.** If `adopt` is added, which existing artifacts may count
   as evidence without explicit user confirmation?
9. **Behavioral eval runner.** Which model/harness matrix and scoring transport
   should become the reproducible automated gate?
10. **State recovery and reclassification.** Should invalid/inconsistent state
    gain an auditable `repair` command, and how should changing `kind` or `risk`
    rematerialize phase requirements without rewriting history?
11. **Durable authority target.** Should the manifest persist a requested stop
    target and mutation authority, how are they narrowed or extended, and which
    user instruction is sufficient to update them across handoffs?
