# Daily Research Note - 2026-06-22

Status: candidate/working note for developer + LLM review. Do not treat as canon until reviewed.

## Repo context read
- README frames Windows Explorer Goblin as a Windows rename assistant using an AutoHotkey v2 overlay plus a Python suggestion brain.
- MVP direction includes Explorer/Desktop support, hotkey overlay, live suggestions, fuzzy matching, rename-history learning, fallback suggestions, and optional Ollama SLM suggestions.
- Prior notes identify safety, predictability, and rollback as the must-have layer before model behavior expands.

## Why this matters
A rename tool is one polite mistake away from becoming a file-system goblin with a tiny hat and a chainsaw. The next code work should make every rename reversible and inspectable.

## Useful findings with sources
- MCP security guidance treats tool actions as potentially dangerous operations that need consent, scoped permissions, and clear action understanding. Source: https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices
- GitHub Actions secure-use guidance recommends least-privilege automation and careful handling of generated/untrusted content. Source: https://docs.github.com/en/actions/reference/security/secure-use

## Candidate implementation ideas
1. Add `RenameTransaction`: original path, proposed path, suggestion source, deterministic validation result, accepted/rejected, timestamp, and rollback state.
2. Add preflight checks for reserved characters, collisions, extension changes, path length, and empty names before AutoHotkey calls the rename.
3. Add a local rollback log with a bounded retention policy and a clear delete-history command.
4. Keep SLM suggestions as advisory strings only; deterministic validation decides what can be renamed.

## Risks / drift warnings
- Do not let an SLM directly rename files.
- Do not learn from private filenames without local-only retention docs.
- No silent overwrites, chained partial renames, or extension changes without explicit acceptance.

## Next dev / LLM actions
- Draft the transaction schema.
- Add tests for collision, invalid character, empty suggestion, and rollback record.
- Add a docs note for local history retention and deletion.
