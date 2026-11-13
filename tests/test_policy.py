"""Policy is the security boundary; it gets the most tests."""
import unittest

from foundry import policy


class PolicyTests(unittest.TestCase):
    def test_read_tool_allowed(self):
        v = policy.check("search_kb", {"query": "refund"})
        self.assertIs(v.decision, policy.Decision.ALLOW)

    def test_unregistered_tool_denied(self):
        v = policy.check("page_manager", {})
        self.assertIs(v.decision, policy.Decision.DENY)

    def test_write_needs_approval(self):
        v = policy.check("draft_reply", {"body": "hi"})
        self.assertIs(v.decision, policy.Decision.NEEDS_APPROVAL)

    def test_write_allowed_with_approval(self):
        v = policy.check("draft_reply", {"body": "hi"}, approved=True)
        self.assertIs(v.decision, policy.Decision.ALLOW)

    def test_bcc_always_denied_even_with_approval(self):
        v = policy.check("send_email", {"to": "a@b", "bcc": "c@d"}, approved=True)
        self.assertIs(v.decision, policy.Decision.DENY)
        self.assertIn("bcc", v.reason)

    def test_deny_by_default_is_not_a_wildcard(self):
        self.assertNotIn("*", policy.DEFAULT_POLICY)


if __name__ == "__main__":
    unittest.main()
