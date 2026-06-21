# Daily Research Note - 2026-06-21

Status: candidate/working note for developer + LLM review. Do not treat as canon until reviewed.

## Repo context read
- README defines Windows Explorer Goblin as a Windows rename assistant using an AutoHotkey v2 overlay plus a Python suggestion brain.
- MVP includes Explorer/Desktop support, Ctrl+Space hotkey, live suggestions, Tab accept, Enter rename, fuzzy matching, rename-history learning, fallback suggestions, and optional Ollama SLM suggestions.
- Recent commits restored README with SLM notes and tested README updates.

## Why this matters
The tool is useful only if rename behavior stays safe, predictable, and reversible. Research should focus on guardrails around suggestions and rename execution before expanding model behavior.

## Current external findings
- MCP security guidance treats tools as arbitrary code execution paths that require consent, clear action understanding, and access controls. Source: https://modelcontextprotocol.io/specification/2025-06-18
- GitHub Actions secure-use guidance recommends least-privilege automation and careful handling of generated content. Source: https://docs.github.com/en/actions/reference/security/secure-use

## Candidate implementation ideas
1. Add a dry-run receipt for every rename: original path, proposed name, source of suggestion, accepted/rejected, timestamp.
2. Add reserved-character and collision checks before calling the actual rename.
3. Add a rollback log format for the last N successful renames.
4. Keep SLM suggestions advisory only; deterministic checks decide whether a name is allowed.

## Risks / drift warnings
- Do not allow an SLM to directly rename files.
- Avoid learning from private filenames without a clear local-only retention policy.
- Make failure modes boring: no partial rename chains, no silent overwrites, no unsafe characters.

## Next dev / LLM actions
- Draft rename receipt schema.
- Add tests for unsafe names, collisions, empty suggestions, and rollback records.
- Add a docs note explaining local history retention and deletion.
