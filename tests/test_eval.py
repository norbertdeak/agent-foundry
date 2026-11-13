"""The golden set must be green on a clean checkout."""
import unittest

from foundry.config import Config
from foundry.eval import load_cases, run_case


class EvalTests(unittest.TestCase):
    def test_all_cases_pass(self):
        cfg = Config(trace_dir="traces/test")
        cases = load_cases("evals/cases")
        self.assertGreaterEqual(len(cases), 5)
        failures = [r for r in (run_case(c, cfg) for c in cases) if not r["ok"]]
        self.assertEqual(failures, [], f"failing cases: {failures}")

    def test_every_case_has_an_expectation(self):
        for c in load_cases("evals/cases"):
            self.assertIn("expect_stop", c)
            self.assertIn("expect_tools", c)


if __name__ == "__main__":
    unittest.main()
