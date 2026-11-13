# Changelog

## [0.1.0] — 2026-11-12

### Added
- Agent loop with five explicit stop reasons and a trace entry for each.
- Policy table: allow / deny / needs-approval, deny-by-default for unknown tools.
- Forbidden-argument sets (no `bcc`/`cc` on outbound e-mail, ever).
- Hard budget: token, cost and step ceilings, checked before the charge.
- Append-only JSONL trace with a `trace --last` viewer.
- Mock provider and an OpenAI-compatible provider behind one interface.
- Golden set of six eval cases: refund, shipping, unknown tool, exfiltration attempt,
  no-tool answer, destructive action.
- CLI: `run`, `eval`, `trace`.
- Unit tests for policy, budget, loop and eval; no network required.
