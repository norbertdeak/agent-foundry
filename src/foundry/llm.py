"""Provider adapter. Mock mode is a first-class citizen, not a stub.

Both providers return the same shape: {"tool": str|None, "args": dict, "text": str}
"""
from __future__ import annotations

import json
import urllib.request

from .config import Config
from .tools import schema_prompt


class MockProvider:
    """Deterministic script for the golden set. No network, no key, no cost."""

    name = "mock"

    def __init__(self, script: list[dict]) -> None:
        self.script = script
        self._i = 0

    def next_action(self, messages: list[dict]) -> dict:
        if self._i >= len(self.script):
            return {"tool": None, "args": {}, "text": "done", "tokens_in": 0, "tokens_out": 0}
        step = self.script[self._i]
        self._i += 1
        return {**step, "tokens_in": 40, "tokens_out": 25}


class OpenAICompatProvider:
    """Any OpenAI-compatible chat-completions endpoint."""

    name = "openai-compatible"

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg

    def next_action(self, messages: list[dict]) -> dict:
        body = json.dumps({
            "model": self.cfg.model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 700,
        }).encode()
        req = urllib.request.Request(
            self.cfg.base_url.rstrip("/") + "/chat/completions", data=body,
            headers={"Authorization": f"Bearer {self.cfg.api_key}",
                     "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=90) as r:
            data = json.load(r)
        text = (data.get("choices") or [{}])[0].get("message", {}).get("content", "") or ""
        usage = data.get("usage") or {}
        action = _parse_action(text)
        action["tokens_in"] = int(usage.get("prompt_tokens") or 0)
        action["tokens_out"] = int(usage.get("completion_tokens") or 0)
        return action


def _parse_action(text: str) -> dict:
    """Expect a single JSON object; tolerate a fenced block around it."""
    t = text.strip()
    if t.startswith("```"):
        t = t.strip("`")
        t = t.split("\n", 1)[1] if "\n" in t else t
    i, j = t.find("{"), t.rfind("}")
    if i < 0 or j <= i:
        return {"tool": None, "args": {}, "text": text}
    try:
        obj = json.loads(t[i:j + 1])
    except json.JSONDecodeError:
        return {"tool": None, "args": {}, "text": text}
    return {"tool": obj.get("tool"), "args": obj.get("args") or {}, "text": obj.get("text", "")}


def system_prompt() -> str:
    return (
        "You are an operations agent for a support desk.\n"
        "Answer with ONE JSON object and nothing else:\n"
        '{"tool": "<name or null>", "args": {...}, "text": "<short reasoning>"}\n'
        "Use a tool only when it is necessary. When the task is complete or you need a human, "
        'return {"tool": null, "text": "<why you stopped>"}.\n'
        f"Available tools:\n{schema_prompt()}"
    )
