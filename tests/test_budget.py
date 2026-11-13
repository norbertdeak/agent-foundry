"""Budgets must be hard stops, not warnings."""
import unittest

from foundry.budget import Budget, BudgetExceeded
from foundry.config import Config


class BudgetTests(unittest.TestCase):
    def test_token_ceiling_stops(self):
        b = Budget(Config(max_tokens=100, max_cost_huf=1000))
        b.charge(60, 30)
        with self.assertRaises(BudgetExceeded):
            b.charge(60, 30)

    def test_cost_ceiling_stops(self):
        b = Budget(Config(max_tokens=10**6, max_cost_huf=0.01))
        with self.assertRaises(BudgetExceeded):
            b.charge(10_000, 10_000)

    def test_step_ceiling_stops(self):
        b = Budget(Config(max_steps=2))
        b.step(); b.step()
        with self.assertRaises(BudgetExceeded):
            b.step()

    def test_remaining_never_negative_after_stop(self):
        b = Budget(Config(max_tokens=100))
        b.charge(50, 40)
        self.assertEqual(b.remaining()["tokens"], 10)


if __name__ == "__main__":
    unittest.main()
