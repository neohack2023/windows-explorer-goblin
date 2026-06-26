# Daily Research Note - 2026-06-26

Status: candidate / working note for developer and LLM review.

## Repo context read
- Repo direction centers on safe Windows file organization, rename planning, validation, rollback logs, and advisory LLM assistance.
- Prior notes emphasized rename transactions and rollback safety.

## Why this matters
A file goblin is only useful if it can undo itself. Today’s best research slice is a transaction ledger that makes every rename reversible and reviewable.

## Useful findings
- GitHub Actions secure-use guidance recommends least-privilege automation and careful treatment of untrusted/generated content: https://docs.github.com/en/actions/reference/security/secure-use
- MCP/tool-security research highlights tool-poisoning and implicit trust risks, relevant to any assistant that can suggest or execute file operations: https://arxiv.org/abs/2603.22489

## Candidate implementation ideas
1. Add `RenameTransactionReceipt`: original path, proposed path, reason, collision check, dry-run status, applied status, and rollback command.
2. Add fixture tests for duplicate names, invalid Windows characters, path length, and reserved names.
3. Add a rule that LLM suggestions are advisory until a dry-run validator passes.
4. Add a `--receipt-json` output mode for future UI/SLM review.

## Risks / drift warnings
- Do not perform destructive moves without a rollback plan.
- Do not trust LLM classification for personal files without user review.
- Avoid scanning hidden/system folders unless explicitly allowed.

## Next suggested dev / LLM actions
- Draft receipt JSON shape.
- Add dry-run fixture cases.
- Add docs for safe user review before applying a batch rename.
