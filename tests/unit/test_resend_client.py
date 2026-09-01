"""
Unit tests for ResendClient email dispatch integration.
"""

import unittest
from integrations.resend_client import ResendClient

class TestResendClient(unittest.TestCase):

    def setUp(self):
        self.client = ResendClient()

    def test_singleton_instance(self):
        c1 = ResendClient()
        c2 = ResendClient()
        self.assertIs(c1, c2)

    def test_mock_send_email_formatting(self):
        response = self.client.send_email(
            to="recipient@example.com",
            subject="Test Subject for Resend",
            text="Hello from Resend client unit test.",
        )
        self.assertIn("id", response)
        self.assertEqual(response["subject"], "Test Subject for Resend")
        self.assertIn("recipient@example.com", response["to"])
        self.assertEqual(response["status"], "sent")

    def test_configure_runtime_credentials(self):
        self.client.configure("re_test_dummy_key_123", "AIRA <test@domain.com>")
        self.assertEqual(self.client.api_key, "re_test_dummy_key_123")
        self.assertEqual(self.client.default_from, "AIRA <test@domain.com>")
        self.assertTrue(self.client.is_configured())

if __name__ == "__main__":
    unittest.main()
