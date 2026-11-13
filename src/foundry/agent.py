"""The loop: plan → policy → tool → observe. It stops for five reasons, and says which."""
from __future__ import annotations

from dataclasses import dataclass, field

from . import policy, tools
from .budget import Budget, BudgetExceeded
from .config import Config
from .trace import Trace


@dataclass
class RunResult:
    run_id: str
    stop_reason: str
    answer: str
    tool_calls: list = field(default_factory=list)
    pending_approval: dict | None = None
    spent: dict = field(default_factory=dict)
    trace_path: str = ""


class Agent:
    def __init__(self, provider, cfg: Config, trace: Trace | None = None) -> None:
        self.provider = provider
        self.cfg = cfg
        self.budget = Budget(cfg)
        self.trace = trace or Trace(trace_dir=cfg.trace_dir)

    def run(self, ticket: dict, approved_tools: set[str] | None = None) -> RunResult:
        approved_tools = approved_tools or set()
        self.trace.event("start", ticket=ticket.get("id"), subject=ticket.get("subject", "")[:80])

        messages = [{"role": "system", "content": __import__("foundry.llm", fromlist=["system_prompt"]).system_prompt()},
                    {"role": "user", "content": _ticket_text(ticket)}]

        calls: list[dict] = []
        answer = ""
        stop_reason = "step_ceiling"

        while True:
            try:
                self.budget.step()
            except BudgetExceeded as e:
                stop_reason = f"budget: {e.reason}"
                self.trace.event("stop", reason=stop_reason, spent=e.spent.as_dict())
                break

            action = self.provider.next_action(messages)
            try:
                self.budget.charge(action.get("tokens_in", 0), action.get("tokens_out", 0), "model")
            except BudgetExceeded as e:
                stop_reason = f"budget: {e.reason}"
                self.trace.event("stop", reason=stop_reason, spent=e.spent.as_dict())
                break

            tool = action.get("tool")
            if not tool:
                answer = action.get("text") or ""
                stop_reason = "completed"
                self.trace.event("answer", text=answer[:400])
                break

            args = action.get("args") or {}
            verdict = policy.check(tool, args, approved=tool in approved_tools)
            self.trace.event("policy", tool=tool, args_summary=_summarize(args),
                             decision=verdict.decision.value, reason=verdict.reason)

            if verdict.decision is policy.Decision.DENY:
                stop_reason = f"denied: {verdict.reason}"
                self.trace.event("stop", reason=stop_reason, spent=self.budget.spent.as_dict())
                break

            if verdict.decision is policy.Decision.NEEDS_APPROVAL:
                stop_reason = "needs_approval"
                pending = {"tool": tool, "args": args, "reason": verdict.reason}
                self.trace.event("await_approval", **pending)
                return RunResult(self.trace.run_id, stop_reason, answer, calls, pending,
                                 self.budget.spent.as_dict(), str(self.trace.path))

            try:
                observation = tools.call(tool, args)
            except KeyError as e:
                stop_reason = f"unknown_tool: {e}"
                self.trace.event("stop", reason=stop_reason)
                break

            calls.append({"tool": tool, "args": _summarize(args)})
            self.trace.event("tool", tool=tool, args=_summarize(args), result=_summarize(observation))
            messages.append({"role": "assistant", "content": f'{{"tool":"{tool}"}}'})
            messages.append({"role": "user",
                             "content": "OBSERVATION: " + str(observation)[:800]})

        return RunResult(self.trace.run_id, stop_reason, answer, calls, None,
                         self.budget.spent.as_dict(), str(self.trace.path))


def _ticket_text(ticket: dict) -> str:
    return (f"Ticket {ticket.get('id')}\n"
            f"Subject: {ticket.get('subject')}\n"
            f"Body: {ticket.get('body')}\n"
            f"Customer: {ticket.get('customer', 'n/a')}")


def _summarize(obj, limit: int = 120) -> str:
    s = str(obj)
    return s[:limit] + ("…" if len(s) > limit else "")
