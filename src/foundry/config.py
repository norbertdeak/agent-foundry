"""Configuration. Secrets come from the environment, never from code."""
from __future__ import annotations

import os
from dataclasses import dataclass


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class Config:
    max_tokens: int = 20000
    max_cost_huf: float = 120.0
    max_steps: int = 6
    price_in: float = 2.0      # HUF per 1k input tokens
    price_out: float = 6.0     # HUF per 1k output tokens
    base_url: str = ""
    api_key: str = ""
    model: str = "mock-1"
    trace_dir: str = "traces"

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            max_tokens=int(_env_float("FOUNDRY_MAX_TOKENS", 20000)),
            max_cost_huf=_env_float("FOUNDRY_MAX_COST_HUF", 120.0),
            max_steps=int(_env_float("FOUNDRY_MAX_STEPS", 6)),
            price_in=_env_float("FOUNDRY_PRICE_IN", 2.0),
            price_out=_env_float("FOUNDRY_PRICE_OUT", 6.0),
            base_url=os.environ.get("FOUNDRY_BASE_URL", ""),
            api_key=os.environ.get("FOUNDRY_API_KEY", ""),
            model=os.environ.get("FOUNDRY_MODEL", "mock-1"),
            trace_dir=os.environ.get("FOUNDRY_TRACE_DIR", "traces"),
        )
