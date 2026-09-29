import unittest
from database.security_vault import DatabaseSecurityVault, vault

class TestDatabaseSecurityVault(unittest.TestCase):
    def setUp(self):
        self.vault = DatabaseSecurityVault()

    def test_singleton_instance(self):
        v2 = DatabaseSecurityVault()
        self.assertIs(self.vault, v2)
        self.assertIs(self.vault, vault)

    def test_encrypt_and_decrypt_field(self):
        secret = "sk_live_enterprise_super_secret_token_12345"
        armored = self.vault.encrypt_field(secret)
        
        self.assertTrue(self.vault.is_encrypted(armored))
        self.assertTrue(armored.startswith("enc::v1::"))
        self.assertNotEqual(secret, armored)

        decrypted = self.vault.decrypt_field(armored)
        self.assertEqual(secret, decrypted)

    def test_decrypt_plaintext_passthrough(self):
        plain = "Normal unencrypted text"
        self.assertFalse(self.vault.is_encrypted(plain))
        self.assertEqual(self.vault.decrypt_field(plain), plain)

    def test_empty_and_none_handling(self):
        self.assertEqual(self.vault.encrypt_field(""), "")
        self.assertEqual(self.vault.encrypt_field(None), "")
        self.assertEqual(self.vault.decrypt_field(""), "")
        self.assertEqual(self.vault.decrypt_field(None), "")

    def test_double_encryption_prevented(self):
        secret = "confidential_meeting_notes"
        enc1 = self.vault.encrypt_field(secret)
        enc2 = self.vault.encrypt_field(enc1)
        self.assertEqual(enc1, enc2)
        self.assertEqual(self.vault.decrypt_field(enc2), secret)

    def test_tampered_ciphertext_graceful_error(self):
        secret = "classified_data"
        enc = self.vault.encrypt_field(secret)
        tampered = enc[:-5] + "XXXXX"
        res = self.vault.decrypt_field(tampered)
        self.assertEqual(res, "[DECRYPTION_ERROR_INTEGRITY_COMPROMISED]")

    def test_blind_indexing_deterministic(self):
        email = "Hriday.Code1119@gmail.com"
        bidx1 = self.vault.generate_blind_index(email)
        bidx2 = self.vault.generate_blind_index("hriday.code1119@gmail.com")
        
        self.assertTrue(bidx1.startswith("bidx::v1::"))
        self.assertEqual(bidx1, bidx2)
        self.assertEqual(len(bidx1), len("bidx::v1::") + 64)

    def test_encrypt_and_decrypt_dict(self):
        payload = {
            "id": "usr-101",
            "name": "Hriday Gupta",
            "role": "Lead Architect",
            "token": "secret_oauth_token_xyz",
            "credentials": {
                "api_key": "resend_api_key_live_999",
                "host": "api.resend.com"
            },
            "public_metric": 42
        }

        enc_payload = self.vault.encrypt_dict(payload)
        
        # Verify sensitive fields are encrypted
        self.assertTrue(self.vault.is_encrypted(enc_payload["token"]))
        self.assertTrue(self.vault.is_encrypted(enc_payload["credentials"]["api_key"]))
        
        # Verify non-sensitive fields are untouched
        self.assertEqual(enc_payload["name"], "Hriday Gupta")
        self.assertEqual(enc_payload["credentials"]["host"], "api.resend.com")
        self.assertEqual(enc_payload["public_metric"], 42)

        # Decrypt dictionary
        dec_payload = self.vault.decrypt_dict(enc_payload)
        self.assertEqual(dec_payload, payload)

    def test_pii_masking(self):
        self.assertEqual(self.vault.mask_email("hriday.code1119@gmail.com"), "h*************9@gmail.com")
        self.assertEqual(self.vault.mask_phone("+91 98765 43210"), "+91******3210")
        self.assertEqual(self.vault.mask_secret_token("sk_live_1234567890abcdef"), "sk_liv********cdef")

if __name__ == "__main__":
    unittest.main()
