# Daily Research Note - 2026-06-29

Status: candidate / working note. Review before promotion.

## Repo context read
- Prior repo context frames windows-explorer-goblin as a local file/rename automation helper with safety receipts, validation, and rollback paths.
- Previous research work emphasized transaction logs and keeping rename automation reversible.

## Why this matters
File rename tools can cause real local damage if they act too confidently. The most useful research lane is a strict dry-run/transaction/rollback contract before any smarter local agent behavior.

## Useful findings
- GitHub Actions secure-use guidance recommends least privilege and careful handling of untrusted inputs, relevant to testing rename plans and generated file lists: https://docs.github.com/en/actions/reference/security/secure-use
- MCP governance research recommends scoped authorization, provenance, sandboxing, and end-to-end audit trails for tool-using agents: https://arxiv.org/abs/2511.20920
- MCP tool-poisoning research reinforces the need to treat tool descriptions and agent-proposed actions as untrusted until validated: https://arxiv.org/abs/2512.06556

## Candidate implementation ideas
1. Define a `RenameTransaction` record: original path, proposed path, rule ID, collision status, dry-run result, applied status, rollback path.
2. Add a mandatory dry-run report before any apply command.
3. Add fixtures for collisions, illegal Windows characters, case-only renames, duplicate stems, and rollback failure.
4. Keep any SLM helper suggestion-only; deterministic validators choose whether a rename plan is safe.

## Risks / drift warnings
- Do not allow drive-wide recursive edits by default.
- Do not accept generated rename rules without preview and collision checks.
- Do not delete files as part of rename cleanup unless a separate review gate exists.

## Next suggested dev / LLM actions
- Add a transaction schema doc and one rollback fixture.
- Implement or document dry-run as the default mode.
- Keep local filesystem access scoped to user-selected folders.