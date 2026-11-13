# ADR 0002 — policy as a table, not as a prompt

- **Status:** accepted
- **Date:** 2026-11-12

## Context

The cheap way to stop an agent from sending e-mail is to write "never send e-mail" in the system
prompt. It works until a ticket contains "ignore previous instructions".

## Decision

Every tool has a rule in `DEFAULT_POLICY`: risk class, approval requirement, reason.
Unknown tools are denied by default. Forbidden argument sets are checked before execution.

## Consequences

- The security property is testable, and it is tested (`tests/test_policy.py`).
- Product owners can read the table and change it without touching the loop.
- The model can still be wrong about *which* allowed tool to call — that is a quality issue,
  not a security issue, and it belongs to the eval set.

## Alternatives

- **Prompt-only guardrails:** rejected — a suggestion, not a control.
- **Model-based classifier:** adds latency, cost and a new failure mode for a decision a dict can make.
