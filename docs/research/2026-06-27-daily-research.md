# Daily Research Note - 2026-06-27

Status: candidate/working note for developer + LLM review. Do not treat as canon until reviewed.

## Repo context read
- Prior passes identify this as a Windows file-organization/rename helper with safe rename transactions, validation, rollback, and local-first behavior.
- Recent notes focused on rename receipts and rollback safety.

## Why this matters
A file goblin must be reversible. The first trust layer should be a ledger that proves exactly what would change before anything changes.

## Useful findings with citations
- GitHub Actions secure-use guidance recommends least-privilege automation and safe handling of untrusted input: https://docs.github.com/en/actions/reference/security/secure-use
- MCP security best practices emphasize consent and tool safety before actions that can modify user data: https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices

## Candidate implementation ideas
1. Add a `rename-transaction-ledger.json` schema with old_path, new_path, reason, collision_status, dry_run_status, applied_status, rollback_status.
2. Add a dry-run-only CLI mode as the default.
3. Add path normalization tests for Windows edge cases.
4. Add a rollback script that reads the ledger and validates target existence before moving anything.

## Risks / drift warnings
- Do not perform destructive actions without a dry-run receipt.
- Do not trust LLM rename suggestions without collision checks.
- Avoid scanning secret folders unless explicitly configured.

## Next suggested dev / LLM actions
- Draft ledger schema.
- Add dry-run sample output.
- Add tests for collision and rollback logic.
