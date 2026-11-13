"""Golden set runner.

An eval case is a ticket plus the behaviour we expect:
  - the tool sequence (order matters)
  - the stop reason
A change that alters behaviour without changing the expectation is a regression.
"""
from __future__ import annotations

import json
from pathlib import Path

from .agent import Agent
from .config import Config
from .llm import MockProvider
from .trace import Trace


def load_cases(directory: str = "evals/cases") -> list[dict]:
    return [json.loads(p.read_text()) for p in sorted(Path(directory).glob("*.json"))]


def run_case(case: dict, cfg: Config) -> dict:
    provider = MockProvider(case["script"])
    trace = Trace(trace_dir=str(Path(cfg.trace_dir) / "eval"))
    agent = Agent(provider, cfg, trace)
    result = agent.run(case["ticket"])
    expected_tools = case.get("expect_tools", [])
    expected_stop = case.get("expect_stop", "completed")
    actual_tools = [c["tool"] for c in result.tool_calls]
    ok = actual_tools == expected_tools and result.stop_reason == expected_stop
    return {
        "case": case["name"],
        "ok": ok,
        "expected": {"tools": expected_tools, "stop": expected_stop},
        "actual": {"tools": actual_tools, "stop": result.stop_reason},
        "tokens": result.spent.get("tokens"),
        "cost_huf": result.spent.get("cost_huf"),
    }


def run_all(cfg: Config, directory: str = "evals/cases") -> list[dict]:
    return [run_case(c, cfg) for c in load_cases(directory)]


def format_table(rows: list[dict]) -> str:
    if not rows:
        return "no eval cases found"
    w = max(len(r["case"]) for r in rows)
    lines = [f"{'case'.ljust(w)}  result  tools                    stop",
             "-" * (w + 56)]
    for r in rows:
        mark = "PASS" if r["ok"] else "FAIL"
        tl = ",".join(r["actual"]["tools"]) or "-"
        lines.append(f"{r['case'].ljust(w)}  {mark:<6}  {tl:<24} {r['actual']['stop']}")
    passed = sum(1 for r in rows if r["ok"])
    lines.append("")
    lines.append(f"{passed}/{len(rows)} passed")
    return "\n".join(lines)
