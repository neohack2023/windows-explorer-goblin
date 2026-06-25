# Daily Research Note - 2026-06-25

Status: candidate/working note for developer + LLM review. Do not treat as canon until reviewed.

## Repo context read
- Prior notes frame Windows Explorer Goblin as a local file/rename assistant with safety-first rename transactions, validation, and rollback logs.
- The project lane is local utility automation, not cloud sync or destructive cleanup.
- Recent cross-repo emphasis on local SLM helpers makes consent and rollback receipts more important.

## Why this matters
File rename tools can cause real damage quickly. The research target should be reversible transactions and preview-first actions.

## Useful findings with citations
- GitHub secure-use guidance recommends least-privilege automation and careful treatment of untrusted inputs. Source: https://docs.github.com/en/actions/reference/security/secure-use
- MCP’s tool model reinforces clear action boundaries and user consent before tools perform changes. Source: https://modelcontextprotocol.io/specification/2025-06-18
- Agentic workflow injection research is relevant if issue text or LLM plans become automation instructions. Source: https://arxiv.org/abs/2605.07135

## Candidate implementation ideas
1. Add `rename_transaction.json`: original path, proposed path, reason, collision status, checksum, preview status, applied status.
2. Add dry-run as the default mode.
3. Add rollback manifest generation before any rename batch applies.
4. Add SLM-only advisory mode for naming suggestions; deterministic validator owns execution.

## Risks / drift warnings
- Do not delete or overwrite files as part of rename flow.
- Do not execute model suggestions directly.
- Treat user-provided filenames and folder names as untrusted text.

## Next suggested dev / LLM actions
- Draft `docs/RENAME_TRANSACTION_SAFETY.md`.
- Add fixture folders for collision, invalid characters, and rollback tests.
- Add CI that validates transaction manifests without touching real user paths.
