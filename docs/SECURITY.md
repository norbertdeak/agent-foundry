# Security model

## Threats specific to agents

| # | Threat | Control | Where |
|---|---|---|---|
| A1 | **Prompt injection** in a ticket tells the agent to e-mail data out | Tools are gated by policy, not by the prompt; `send_email` needs approval; `bcc`/`cc` are denied outright | `policy.py` |
| A2 | **Tool hallucination** — the model calls a tool that does not exist | Registry lookup is a hard failure; unknown tools become `denied` | `tools.py`, `policy.py` |
| A3 | **Runaway cost** — a loop that never stops | Token, cost and step ceilings are checked *before* the charge is accepted | `budget.py` |
| A4 | **Silent action** — something happened, nobody knows what | Append-only JSONL trace, one file per run, replayed by `foundry trace` | `trace.py` |
| A5 | **Data exfiltration through arguments** | Forbidden-argument sets per tool, checked before execution | `policy.py` |
| A6 | **Secret leakage** | Key from env only, `.env` ignored, no key in code or logs | `config.py`, `.gitignore` |
| A7 | **Irreversible action** | Destructive tools are `write` + `needs_approval` | `policy.py` |

## The rule that matters

> The model proposes. The code decides.

If a control depends on the model *choosing* to behave, it is not a control — it is a hope.
Every gate in this repository sits in Python, between the model's output and the side effect.

## Approval flow

```
model → tool call → policy → NEEDS_APPROVAL → run parks (pending_approval)
                                    │
                            human reviews the exact call
                                    │
                    re-run with --approve <tool>  (or an approval UI)
```

The parked run is not resumed automatically. A human sees the tool name and the arguments
in the trace before anything happens.

## Out of scope

- Model-level jailbreaks that stay inside the text answer (no tool is called → no side effect).
- Network egress control: this skeleton assumes the host enforces it.
