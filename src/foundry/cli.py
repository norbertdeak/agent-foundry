"""CLI: run, eval, trace. No magic, no hidden state."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .agent import Agent
from .config import Config
from .eval import format_table, run_all
from .llm import MockProvider, OpenAICompatProvider
from .trace import latest, pretty


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="foundry", description="agent-foundry CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="run one ticket")
    run.add_argument("--case", default="evals/cases/01-refund.json")
    run.add_argument("--mock", action="store_true")
    run.add_argument("--approve", action="append", default=[])

    sub.add_parser("eval", help="run the golden set")
    tr = sub.add_parser("trace", help="show a trace")
    tr.add_argument("--last", action="store_true")
    tr.add_argument("--id")

    a = p.parse_args(argv)
    cfg = Config.from_env()

    if a.cmd == "run":
        case = json.loads(Path(a.case).read_text())
        provider = MockProvider(case["script"]) if a.mock else OpenAICompatProvider(cfg)
        agent = Agent(provider, cfg)
        res = agent.run(case["ticket"], approved_tools=set(a.approve))
        print(json.dumps({
            "run_id": res.run_id,
            "stop_reason": res.stop_reason,
            "tools": [c["tool"] for c in res.tool_calls],
            "pending_approval": res.pending_approval,
            "answer": res.answer,
            "spent": res.spent,
            "trace": res.trace_path,
        }, indent=2, ensure_ascii=False))
        return 0

    if a.cmd == "eval":
        rows = run_all(cfg)
        print(format_table(rows))
        return 0 if all(r["ok"] for r in rows) else 1

    if a.cmd == "trace":
        path = (Path(cfg.trace_dir) / f"{a.id}.jsonl") if a.id else latest(cfg.trace_dir)
        if not path or not path.exists():
            print("no trace found", file=sys.stderr)
            return 1
        print(pretty(path))
        return 0

    return 2
