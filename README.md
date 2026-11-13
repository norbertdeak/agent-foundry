# agent-foundry

A production-shaped AI agent service in one small Python codebase — **stdlib only**.

Most agent demos prove that a loop can call a tool. This one proves the four things that
decide whether an agent survives contact with a real business:

| | Question it answers | Where |
|---|---|---|
| **Policy** | Which tool may the agent call, and when does a human have to say yes? | `src/foundry/policy.py` |
| **Budget** | How many tokens and how much money may a run spend before it stops? | `src/foundry/budget.py` |
| **Trace** | Can I reconstruct exactly what happened, step by step? | `src/foundry/trace.py` |
| **Eval** | Does a change make the agent better, or just different? | `src/foundry/eval.py` |

## Run it in 30 seconds (no API key)

```bash
make demo          # triage a support ticket in mock mode, deterministic
make eval          # run the golden set, print a pass/fail table
make trace         # pretty-print the last trace
```

Mock mode is not a toy: it is how the loop and the policy are tested in CI, with no network
and no cost. Live mode swaps the provider behind the same interface.

## Live mode

```bash
cp .env.example .env      # set FOUNDRY_BASE_URL / FOUNDRY_API_KEY / FOUNDRY_MODEL
make demo-live
```

Any OpenAI-compatible endpoint works. The key is read from the environment, never from code.

## The example that matters

A support ticket arrives. The agent may read the knowledge base and the order, and it may
**draft** a reply. It may not send it: `send_email` is an `external` tool and the policy
requires human approval. The run stops with `stop_reason: needs_approval` and a trace entry
that says exactly which tool and which arguments were waiting.

That single behaviour — *stop instead of improvise* — is the difference between an agent you
can deploy and an agent you have to babysit.

## Architecture (one screen)

```
ticket ──► agent loop ──► policy gate ──► tool ──► observation
              │  ▲            │
              │  └────────────┘ (deny / needs_approval / allow)
              ├──► budget     (tokens, cost, steps)
              └──► trace      (jsonl, replayable)
```

## Layout

```
src/foundry/     config, budget, policy, tools, trace, llm, agent, eval, cli
evals/cases/     golden set: ticket → expected tool sequence → expected stop reason
tests/           policy, budget, tools, loop, eval — no network
docs/            architecture, security, ADRs
```

## Design rules

1. **The model proposes, the code decides.** Tool execution never happens inside the model call.
2. **Policy is data, not prose.** `policy.py` is the single place where "may I?" is answered.
3. **Budgets are hard stops.** A run that exceeds its token or cost ceiling stops with a reason.
4. **Every run leaves a trace.** No trace, no incident review.
5. **Eval before vibe.** A prompt change ships with a golden-set result.

## License

MIT
