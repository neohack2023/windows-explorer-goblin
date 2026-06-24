# Daily Research Note - 2026-06-24

Status: candidate/working note for developer + LLM review. Do not treat as canon until reviewed.

## Repo context read
- Repo context and recent PRs frame this project around safe file rename transactions, validation, rollback, and local SLM advisory boundaries.

## Why this matters
File organization tools are only useful if every rename can be previewed, explained, reversed, and audited.

## Useful findings
- GitHub Actions secure-use guidance recommends least-privilege automation and careful handling of generated outputs: https://docs.github.com/en/actions/reference/security/secure-use
- MCP security guidance emphasizes access controls, consent, and clear tool descriptions for file-affecting tools: https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices

## Candidate implementation ideas
1. Define `RenamePlanReceipt` with old path, new path, reason, collision check, dry-run status, and rollback token.
2. Make dry-run the default path for all LLM/SLM suggestions.
3. Add rollback manifest tests with weird filenames, duplicates, and unicode.
4. Add a “never touch” denylist for system folders and hidden config files.

## Risks / drift warnings
- Do not let LLM suggestions perform direct destructive file moves.
- Avoid broad glob operations without preview and rollback.
- Keep local model advice explainable and optional.

## Next suggested dev / LLM actions
- Draft rename receipt schema.
- Add dry-run sample output.
- Add rollback manifest fixture tests.
