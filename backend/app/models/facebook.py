"""Facebook connection and account models."""
from datetime import datetime
from flask import current_app
from cryptography.fernet import Fernet
from ..extensions import db


class FacebookConnection(db.Model):
    """Facebook OAuth connection."""
    __tablename__ = 'facebook_connections'

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)

    # Encrypted access token
    _access_token = db.Column('access_token', db.Text, nullable=True)
    token_expires_at = db.Column(db.DateTime, nullable=True)
    facebook_user_id = db.Column(db.String(100), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def _get_fernet(self):
        """Get Fernet instance for encryption/decryption."""
        key = current_app.config.get('ENCRYPTION_KEY')
        if not key:
            # Use a default key for development (NOT for production!)
            key = Fernet.generate_key()
            current_app.logger.warning("Using generated encryption key - set ENCRYPTION_KEY in production!")
        return Fernet(key.encode() if isinstance(key, str) else key)

    def set_access_token(self, token):
        """Encrypt and store access token."""
        if token:
            fernet = self._get_fernet()
            self._access_token = fernet.encrypt(token.encode()).decode()
        else:
            self._access_token = None

    def get_access_token(self):
        """Decrypt and return access token."""
        if self._access_token:
            try:
                fernet = self._get_fernet()
                return fernet.decrypt(self._access_token.encode()).decode()
            except Exception:
                return None
        return None

    def is_token_valid(self):
        """Check if token is still valid."""
        if not self._access_token:
            return False
        if self.token_expires_at and self.token_expires_at < datetime.utcnow():
            return False
        return True

    def __repr__(self):
        return f'<FacebookConnection for user {self.user_id}>'


class AdAccount(db.Model):
    """Facebook Ad Account."""
    __tablename__ = 'ad_accounts'

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    facebook_account_id = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(255), nullable=True)
    currency = db.Column(db.String(10), default='USD')
    timezone = db.Column(db.String(100), default='UTC')
    is_primary = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<AdAccount {self.name} ({self.facebook_account_id})>'


class FacebookPage(db.Model):
    """Facebook Page for running ads."""
    __tablename__ = 'facebook_pages'

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    facebook_page_id = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(255), nullable=True)
    profile_picture_url = db.Column(db.String(500), nullable=True)
    is_primary = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<FacebookPage {self.name}>'
