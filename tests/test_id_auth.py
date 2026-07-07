import unittest
from src.modules.id.auth import MultiFactorAuthManager

class TestMultiFactorAuthManager(unittest.TestCase):
    def setUp(self):
        self.auth_manager = MultiFactorAuthManager()
        self.user_id = "test_user_123"

    def test_generate_mfa_secret(self):
        secret = self.auth_manager.generate_mfa_secret(self.user_id)
        self.assertIsNotNone(secret)
        self.assertTrue(len(secret) > 0)
        self.assertIn(self.user_id, self.auth_manager._user_secrets)

    def test_get_provisioning_uri(self):
        self.auth_manager.generate_mfa_secret(self.user_id)
        uri = self.auth_manager.get_provisioning_uri(self.user_id)
        self.assertTrue(uri.startswith("otpauth://totp/"))
        self.assertIn("Auralis", uri)
        self.assertIn(self.user_id, uri)

    def test_get_provisioning_uri_no_secret(self):
        with self.assertRaises(ValueError):
            self.auth_manager.get_provisioning_uri("unknown_user")

    def test_verify_token_success(self):
        secret = self.auth_manager.generate_mfa_secret(self.user_id)
        import pyotp
        totp = pyotp.TOTP(secret)
        valid_token = totp.now()

        self.assertTrue(self.auth_manager.verify_token(self.user_id, valid_token))

    def test_verify_token_failure(self):
        self.auth_manager.generate_mfa_secret(self.user_id)
        self.assertFalse(self.auth_manager.verify_token(self.user_id, "000000"))

    def test_verify_token_no_secret(self):
        self.assertFalse(self.auth_manager.verify_token("unknown_user", "123456"))

if __name__ == '__main__':
    unittest.main()
