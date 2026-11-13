# ADR 0001 — standard library instead of a web framework

- **Status:** accepted
- **Date:** 2026-11-12

## Context

The repo has to be readable end-to-end by a reviewer in twenty minutes, and it has to run
with `python3 -m foundry` on any machine without an install step.

## Decision

Use only the standard library: `urllib` for the provider call, `json` for everything structured,
`argparse` for the CLI, `unittest` for tests.

## Consequences

- Zero dependency surface: no `pip install`, no lockfile, no supply-chain risk for the demo.
- The HTTP call is ten lines; a framework would hide nothing important at this size.
- Moving to FastAPI later is a swap inside `llm.py` and a new `api.py`, not a rewrite.

## Alternatives

- **FastAPI + pydantic:** better for a public API with many endpoints; overkill for a CLI demo.
- **LangChain-style abstractions:** rejected — the loop is the product here, and hiding it defeats the purpose.
