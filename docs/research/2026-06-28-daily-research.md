# Daily Research Note - 2026-06-28

Status: candidate / working note for developer + LLM review. Do not treat as canon until reviewed.

## Repo context read
- README defines Windows Explorer Goblin as an AutoHotkey v2 overlay plus Python suggestion brain for smarter Explorer/Desktop renaming.
- MVP features include fuzzy suggestions, rename history learning, deterministic fallback suggestions, and optional Ollama SLM suggestions.
- Design goal is IDE-style autocomplete for dataset, audio sample, texture, and project asset naming.
- Recent open PR history focused on rename transaction ledgers and rollback safety.

## Why this matters
Rename helpers touch real files. The next useful layer is a transaction ledger that proves what changed, why it changed, and how to undo it.

## Useful findings
- GitHub Actions secure-use guidance recommends least-privilege automation and careful handling of untrusted input. Source: https://docs.github.com/en/actions/reference/security/secure-use
- MCP/tool-security research highlights scoped tools and auditability for agent-assisted actions. Source: https://arxiv.org/abs/2511.20920
- Local SLM suggestions should remain advisory because the deterministic suggestion brain already provides a safe fallback.

## Implementation ideas
1. Add `RenameTransaction`: original path, proposed path, source of suggestion, accepted by user, timestamp, and rollback status.
2. Add a dry-run mode that shows rename collisions and invalid Windows filename characters before execution.
3. Add a small rollback script that replays the last accepted transaction in reverse.
4. Add config-level SLM timeout and max suggestion length tests.

## Risks / drift warnings
- Do not let SLM output rename files without explicit user acceptance.
- Avoid learning from sensitive folder names unless the storage policy is clear.
- Keep Explorer automation minimal; the overlay strategy is the stable lane.

## Next dev / LLM actions
- Draft `docs/rename-transaction-ledger.md`.
- Add one dry-run collision fixture.
- Add rollback instructions to README or docs before broader testing.
