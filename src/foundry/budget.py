"""Hard budget: tokens, cost and steps. A run that exceeds it stops, with a reason."""
from __future__ import annotations

from dataclasses import dataclass, field

from .config import Config


class BudgetExceeded(Exception):
    """Raised when a run would exceed its token, cost or step ceiling."""

    def __init__(self, reason: str, spent: "Spend") -> None:
        super().__init__(reason)
        self.reason = reason
        self.spent = spent


@dataclass
class Spend:
    tokens_in: int = 0
    tokens_out: int = 0
    steps: int = 0
    cost_huf: float = 0.0
    history: list = field(default_factory=list)

    @property
    def tokens(self) -> int:
        return self.tokens_in + self.tokens_out

    def as_dict(self) -> dict:
        return {
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "tokens": self.tokens,
            "steps": self.steps,
            "cost_huf": round(self.cost_huf, 2),
        }


class Budget:
    """A ledger with a ceiling. Every charge is checked before it is accepted."""

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.spent = Spend()

    def charge(self, tokens_in: int, tokens_out: int, label: str = "") -> None:
        cost = (tokens_in / 1000.0) * self.cfg.price_in + (tokens_out / 1000.0) * self.cfg.price_out
        next_tokens = self.spent.tokens + tokens_in + tokens_out
        next_cost = self.spent.cost_huf + cost
        if next_tokens > self.cfg.max_tokens:
            raise BudgetExceeded("token ceiling", self.spent)
        if next_cost > self.cfg.max_cost_huf:
            raise BudgetExceeded("cost ceiling", self.spent)
        self.spent.tokens_in += tokens_in
        self.spent.tokens_out += tokens_out
        self.spent.cost_huf = next_cost
        self.spent.history.append({"label": label, "in": tokens_in, "out": tokens_out,
                                   "cost": round(cost, 3)})

    def step(self) -> None:
        self.spent.steps += 1
        if self.spent.steps > self.cfg.max_steps:
            raise BudgetExceeded("step ceiling", self.spent)

    def remaining(self) -> dict:
        return {
            "tokens": self.cfg.max_tokens - self.spent.tokens,
            "cost_huf": round(self.cfg.max_cost_huf - self.spent.cost_huf, 2),
            "steps": self.cfg.max_steps - self.spent.steps,
        }
