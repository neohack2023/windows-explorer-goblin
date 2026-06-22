# Daily Research Note - 2026-06-22

Status: candidate/working note for developer + LLM review. Do not treat as canon until reviewed.

## Repo context read
- Prior notes identify Windows Explorer Goblin as a Windows rename assistant using AutoHotkey v2 overlay plus a Python suggestion brain.
- MVP behavior includes Explorer/Desktop support, hotkey overlay, suggestions, accept/rename flow, fuzzy matching, local rename-history learning, fallback suggestions, and optional Ollama SLM suggestions.
- Previous research focused on dry-run receipts, rollback logs, collision checks, and SLM-as-advisory boundaries.

## Why this matters
A rename assistant is one wrong move away from turning file organization into a raccoon in a circuit closet. The next useful layer is reversible receipts before any smarter suggestion model.

## Useful findings with citations
- MCP security guidance treats tool actions as trust-boundary events requiring consent, clear action understanding, and access controls. Source: https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices
- GitHub Actions secure-use guidance recommends least-privilege automation and careful generated-content handling. Source: https://docs.github.com/en/actions/reference/security/secure-use
- Agentic Workflow Injection research reinforces that untrusted text should not become unchecked agent/tool behavior. Source: https://arxiv.org/abs/2605.07135

## Candidate implementation ideas
1. Add `RenameSafetyReceipt`: original path, proposed path, suggestion source, collision result, reserved-character check, user approval, rollback ID.
2. Add a local rollback file with last N accepted renames and a deletion command.
3. Add deterministic validation before SLM suggestions are displayed.
4. Add tests for collisions, empty suggestions, invalid characters, and duplicate extensions.

## Risks / drift warnings
- Do not let an SLM execute or auto-accept renames.
- Do not learn from private filenames without local-only retention and deletion docs.
- Do not overwrite or silently chain rename operations.

## Next dev / LLM actions
- Draft receipt schema and rollback doc.
- Add validation tests first.
- Keep SLM output as suggestion text only.
