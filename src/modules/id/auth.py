import logging
from typing import Dict

import pyotp

logger = logging.getLogger(__name__)


class MultiFactorAuthManager:
    """
    Manages multi-factor authentication for user profiles.
    Generates MFA secrets and validates TOTP tokens.
    """

    def __init__(self):
        # In a real system, this would be a secure database mapping user_id to MFA secret
        self._user_secrets: Dict[str, str] = {}

    def generate_mfa_secret(self, user_id: str) -> str:
        """
        Generates a new MFA secret for the given user.
        """
        secret = pyotp.random_base32()
        self._user_secrets[user_id] = secret
        logger.info(f"Generated new MFA secret for user {user_id}")
        return secret

    def get_provisioning_uri(self, user_id: str, issuer_name: str = "Auralis") -> str:
        """
        Generates a provisioning URI (for QR codes in authenticator apps).
        """
        if user_id not in self._user_secrets:
            raise ValueError(f"No MFA secret found for user {user_id}")

        secret = self._user_secrets[user_id]
        return pyotp.totp.TOTP(secret).provisioning_uri(name=user_id, issuer_name=issuer_name)

    def verify_token(self, user_id: str, token: str) -> bool:
        """
        Verifies a given TOTP token against the user's secret.
        """
        if user_id not in self._user_secrets:
            logger.warning(f"Attempted to verify token for user {user_id} with no secret")
            return False

        secret = self._user_secrets[user_id]
        totp = pyotp.TOTP(secret)

        # Verify the token
        is_valid = totp.verify(token)
        if is_valid:
            logger.info(f"MFA validation successful for user {user_id}")
        else:
            logger.warning(f"MFA validation failed for user {user_id}")

        return is_valid
