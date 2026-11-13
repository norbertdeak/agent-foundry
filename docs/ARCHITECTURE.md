# Architecture

## The loop

```
            ┌──────────────┐
  ticket ──►│  agent.run   │
            └──────┬───────┘
                   │ 1. budget.step()
                   ▼
            ┌──────────────┐        ┌──────────────┐
            │  provider    │───────►│   action     │  {tool, args, text}
            └──────────────┘        └──────┬───────┘
                   ▲                       │
                   │ 5. observation        │ 2. policy.check()
                   │                       ▼
            ┌──────┴───────┐        ┌──────────────┐
            │    tool      │◄───────│ allow / deny │
            └──────────────┘        │ / approval   │
                                    └──────────────┘
```

The loop has exactly five exit reasons, and every one of them is written to the trace:

| stop_reason | Meaning |
|---|---|
| `completed` | The model returned no tool call — the task is done. |
| `needs_approval` | A tool requires a human; the run parks with the pending call. |
| `denied: …` | Policy refused the tool or its arguments. |
| `budget: …` | Token, cost or step ceiling reached. |
| `step_ceiling` | Defensive default if the loop ends without a reason. |

## Layers

| Layer | Responsibility | Never does |
|---|---|---|
| `llm.py` | Talk to the model, normalise the response | Execute anything |
| `agent.py` | Drive the loop, charge the budget, emit trace | Decide policy |
| `policy.py` | Answer "may this run?" | Know about the model |
| `tools.py` | Validate and execute a tool | Decide whether it is allowed |
| `budget.py` | Hard ceilings | Warn and continue |
| `trace.py` | Append-only record | Interpret |

The separation is the product: every layer can be tested alone, and a failure has one owner.

## Why mock mode is first-class

The mock provider replays a scripted sequence. That makes the loop, the policy gate and the
stop reasons **deterministic** — which is the only way to run them in CI on every commit.
Live mode uses the same interface, so the behaviour under test is the behaviour in production.
