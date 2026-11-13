"""Policy as code: the single place where 'may the agent do this?' is answered.

Three outcomes: ALLOW, DENY, NEEDS_APPROVAL. Nothing else.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Decision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    NEEDS_APPROVAL = "needs_approval"


@dataclass(frozen=True)
class Rule:
    risk: str                 # read | write | external
    needs_approval: bool
    reason: str


# The policy table. A tool that is not listed here is denied by default.
DEFAULT_POLICY: dict[str, Rule] = {
    "search_kb":  Rule("read",     False, "read-only knowledge base lookup"),
    "get_order":  Rule("read",     False, "read-only order lookup"),
    "draft_reply": Rule("write",   True,  "writes customer-visible text, needs a human"),
    "send_email": Rule("external", True,  "leaves the system, needs a human"),
    "delete_ticket": Rule("write", True,  "destructive, needs a human"),
}

# Tools that must never run in an automated context, whatever the model asks.
FORBIDDEN_ARGS = {
    "send_email": {"bcc", "cc"},   # exfiltration vector
}


@dataclass
class Verdict:
    decision: Decision
    reason: str


def check(tool: str, arguments: dict, approved: bool = False) -> Verdict:
    """Decide whether `tool` may run with `arguments`."""
    rule = DEFAULT_POLICY.get(tool)
    if rule is None:
        return Verdict(Decision.DENY, f"tool '{tool}' is not in the policy table")

    forbidden = FORBIDDEN_ARGS.get(tool)
    if forbidden:
        offending = forbidden.intersection(arguments or {})
        if offending:
            return Verdict(Decision.DENY, f"forbidden arguments for {tool}: {sorted(offending)}")

    if rule.needs_approval and not approved:
        return Verdict(Decision.NEEDS_APPROVAL, rule.reason)
    return Verdict(Decision.ALLOW, rule.reason)
