# Daily Research Note - 2026-06-23

Status: candidate/working note for developer + LLM review. Do not treat as canon until reviewed.

## Repo context read
- Windows Explorer Goblin focuses on safe file/rename automation, rollback logs, and reviewable transactions.
- Prior notes emphasize transaction receipts and SLM advisory boundaries.

## Why this matters
A file goblin must be funny in name only. The runtime needs dry-run receipts, rollback plans, and narrow approvals before touching a user’s filesystem.

## Useful findings with citations
- GitHub secure-use guidance recommends least-privilege automation and protecting secrets/logs. Source: https://docs.github.com/en/actions/reference/security/secure-use
- MCP security guidance emphasizes consent and access-control boundaries before tools operate over arbitrary data. Source: https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices

## Implementation ideas
1. Add a `rename_transaction_receipt` schema with original path, proposed path, reason, collision check, and rollback path.
2. Make dry-run the default mode in every example.
3. Add fixtures for duplicate names, illegal Windows characters, long paths, and rollback recovery.
4. Add an SLM route that suggests names but never executes moves directly.

## Risks / drift warnings
- Do not let generated names execute without a human-visible preview.
- Avoid recursive operations until rollback tests exist.
- Keep OS-specific path rules explicit.

## Next suggested dev / LLM actions
- Draft `docs/RENAME_TRANSACTIONS.md`.
- Add collision/rollback fixtures.
- Add a safety checklist before any live filesystem operation.
