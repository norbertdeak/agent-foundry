"""End-to-end loop behaviour in mock mode: no network, deterministic."""
import unittest

from foundry.agent import Agent
from foundry.config import Config
from foundry.llm import MockProvider
from foundry.trace import Trace

TICKET = {"id": "T-1", "subject": "x", "body": "y", "customer": "c@example.test"}


def run(script, approve=()):
    cfg = Config(trace_dir="traces/test")
    agent = Agent(MockProvider(script), cfg, Trace(trace_dir="traces/test"))
    return agent.run(TICKET, approved_tools=set(approve))


class AgentTests(unittest.TestCase):
    def test_completes_without_tools(self):
        r = run([{"tool": None, "args": {}, "text": "nothing to do"}])
        self.assertEqual(r.stop_reason, "completed")
        self.assertEqual(r.tool_calls, [])

    def test_approval_gate_stops_the_run(self):
        r = run([{"tool": "send_email", "args": {"to": "c@example.test", "body": "hi"}}])
        self.assertEqual(r.stop_reason, "needs_approval")
        self.assertEqual(r.pending_approval["tool"], "send_email")

    def test_approval_lets_the_call_through(self):
        r = run([{"tool": "draft_reply", "args": {"body": "hi"}},
                 {"tool": None, "args": {}, "text": "done"}], approve=("draft_reply",))
        self.assertEqual([c["tool"] for c in r.tool_calls], ["draft_reply"])
        self.assertEqual(r.stop_reason, "completed")

    def test_step_ceiling_is_reported(self):
        script = [{"tool": "search_kb", "args": {"query": "x"}}] * 10
        r = run(script)
        self.assertTrue(r.stop_reason.startswith("budget: step"))

    def test_trace_has_a_policy_entry_per_tool(self):
        r = run([{"tool": "search_kb", "args": {"query": "refund"}},
                 {"tool": None, "args": {}, "text": "ok"}])
        from pathlib import Path
        import json
        recs = [json.loads(l) for l in Path(r.trace_path).read_text().splitlines()]
        self.assertTrue(any(x["kind"] == "policy" for x in recs))
        self.assertEqual(recs[0]["kind"], "start")


if __name__ == "__main__":
    unittest.main()
