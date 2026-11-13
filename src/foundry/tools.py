"""Tool registry. Every tool declares a JSON schema and a handler.

The agent never invents a tool: if it is not registered here, the call is a policy denial.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    schema: dict
    handler: Callable[[dict], dict]


def _search_kb(args: dict) -> dict:
    """Toy knowledge base. Replace with the real retrieval in a product."""
    kb = {
        "refund": "Refunds are available within 30 days of delivery, unopened.",
        "shipping": "Standard delivery is 2-4 business days inside the EU.",
        "warranty": "12 months manufacturer warranty; proof of purchase required.",
    }
    q = str(args.get("query", "")).lower()
    hits = [v for k, v in kb.items() if k in q]
    return {"query": q, "hits": hits or ["no entry found"], "count": len(hits)}


def _get_order(args: dict) -> dict:
    orders = {
        "A-1001": {"id": "A-1001", "status": "delivered", "days_since": 12, "total": 24900},
        "A-1002": {"id": "A-1002", "status": "in_transit", "days_since": 2, "total": 8900},
    }
    oid = str(args.get("order_id", "")).upper()
    return orders.get(oid, {"error": f"order {oid} not found"})


def _draft_reply(args: dict) -> dict:
    body = str(args.get("body", ""))
    return {"draft": body, "chars": len(body), "status": "drafted"}


def _send_email(args: dict) -> dict:
    # Never actually sends in this skeleton — a real adapter goes here.
    return {"sent": False, "reason": "skeleton: no transport configured", "to": args.get("to")}


def _delete_ticket(args: dict) -> dict:
    return {"deleted": args.get("ticket_id"), "irreversible": True}


TOOLS: dict[str, Tool] = {
    "search_kb": Tool(
        "search_kb", "Search the internal knowledge base.",
        {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
        _search_kb),
    "get_order": Tool(
        "get_order", "Look up an order by id.",
        {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]},
        _get_order),
    "draft_reply": Tool(
        "draft_reply", "Draft a customer-visible reply. Does not send it.",
        {"type": "object", "properties": {"body": {"type": "string"}}, "required": ["body"]},
        _draft_reply),
    "send_email": Tool(
        "send_email", "Send an e-mail to the customer. Leaves the system.",
        {"type": "object",
         "properties": {"to": {"type": "string"}, "subject": {"type": "string"},
                        "body": {"type": "string"}},
         "required": ["to", "body"]},
        _send_email),
    "delete_ticket": Tool(
        "delete_ticket", "Permanently delete a ticket.",
        {"type": "object", "properties": {"ticket_id": {"type": "string"}}, "required": ["ticket_id"]},
        _delete_ticket),
}


def schema_prompt() -> str:
    """Machine-readable tool list for the model, derived from the registry."""
    return json.dumps(
        [{"name": t.name, "description": t.description, "parameters": t.schema}
         for t in TOOLS.values()],
        indent=2, ensure_ascii=False)


def call(name: str, args: dict) -> dict[str, Any]:
    tool = TOOLS.get(name)
    if tool is None:
        raise KeyError(f"unknown tool: {name}")
    return tool.handler(args or {})
