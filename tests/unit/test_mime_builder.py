"""
Unit tests for RFC 2822 MIME message construction and URL-safe Base64 encoding.
"""

import base64
import unittest
from email import message_from_bytes
from email import policy
from integrations.gmail_client import create_mime_message

class TestMimeBuilder(unittest.TestCase):

    def test_create_mime_plain_text(self):
        payload = create_mime_message(
            to="recipient@example.com",
            subject="Test Subject Line",
            body_text="Hello, this is a plain text body.",
        )
        self.assertIn("raw", payload)
        raw_b64 = payload["raw"]

        # Decode base64 bytes using modern email policy
        decoded_bytes = base64.urlsafe_b64decode(raw_b64.encode("utf-8"))
        msg = message_from_bytes(decoded_bytes, policy=policy.default)

        self.assertEqual(msg["To"], "recipient@example.com")
        self.assertEqual(msg["Subject"], "Test Subject Line")
        self.assertIn("Hello, this is a plain text body.", msg.get_content())

    def test_create_mime_multipart_html(self):
        payload = create_mime_message(
            to="director@institution.edu",
            subject="Formal Report",
            body_text="Dear Director, here is the report.",
            body_html="<p>Dear Director, here is the <b>report</b>.</p>",
            from_email="sender@institution.edu",
        )
        raw_b64 = payload["raw"]
        decoded_bytes = base64.urlsafe_b64decode(raw_b64.encode("utf-8"))
        msg = message_from_bytes(decoded_bytes, policy=policy.default)

        self.assertEqual(msg["To"], "director@institution.edu")
        self.assertEqual(msg["From"], "sender@institution.edu")
        self.assertEqual(msg["Subject"], "Formal Report")
        self.assertTrue(msg.is_multipart())

if __name__ == "__main__":
    unittest.main()
