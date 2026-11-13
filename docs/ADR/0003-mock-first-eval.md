# ADR 0003 — mock-first evaluation

- **Status:** accepted
- **Date:** 2026-11-12

## Context

Tests that call a live model are slow, non-deterministic and cost money on every CI run.
Tests that never call the model prove nothing about the loop.

## Decision

Split the provider interface in two:

- `MockProvider` replays a scripted action list per eval case → deterministic, free, runs in CI.
- `OpenAICompatProvider` uses the same interface → the live path shares the loop.

The golden set asserts the **tool sequence** and the **stop reason**, not the wording of the answer.

## Consequences

- A prompt change can be evaluated for behavioural drift before it ships.
- Wording quality still needs a human or an LLM-judge pass; that is a separate, slower gate.
- Each case is a small JSON file, so adding a case is a pull request anyone can review.
