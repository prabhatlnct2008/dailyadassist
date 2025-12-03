"""Security utilities."""
from cryptography.fernet import Fernet
from flask import current_app
import os


def get_fernet():
    """Get Fernet instance for encryption."""
    key = os.environ.get('ENCRYPTION_KEY')
    if not key:
        # Generate a key for development
        key = Fernet.generate_key()
        current_app.logger.warning("No ENCRYPTION_KEY set - using generated key")
    elif isinstance(key, str):
        key = key.encode()
    return Fernet(key)


def encrypt_token(token: str) -> str:
    """Encrypt a token."""
    fernet = get_fernet()
    return fernet.encrypt(token.encode()).decode()


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt a token."""
    fernet = get_fernet()
    return fernet.decrypt(encrypted_token.encode()).decode()
