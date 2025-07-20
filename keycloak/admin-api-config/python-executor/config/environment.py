"""
Environment Configuration
Handles all environment variables from Kubernetes secrets
"""
import os
import logging
from typing import Optional

class Environment:
    """Environment variables configuration from Kubernetes secrets."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Keycloak Admin Connection (from padmini-keycloak-admin secret)
        self.KEYCLOAK_ADMIN_USERNAME = os.getenv('KEYCLOAK_ADMIN_USERNAME')
        self.KEYCLOAK_ADMIN_PASSWORD = os.getenv('KEYCLOAK_ADMIN_PASSWORD')
        
        # SMTP Configuration (from padmini-keycloak-smtp secret)
        self.SMTP_HOST = os.getenv('SMTP_HOST')
        self.SMTP_PORT = os.getenv('SMTP_PORT', '587')
        self.SMTP_USER = os.getenv('SMTP_USER')
        self.SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
        self.SMTP_FROM = os.getenv('SMTP_FROM')
        self.SMTP_FROM_DISPLAY_NAME = os.getenv('SMTP_FROM_DISPLAY_NAME')
        
        # Keycloak Server Configuration
        self.KEYCLOAK_URL = os.getenv('KEYCLOAK_URL', 'http://localhost:8080')
        
        # Operation Configuration
        self.ACTION = os.getenv('ACTION', 'create').lower()
        
        # Validation
        self._validate()
        
        self.logger.info("✅ Environment configuration loaded successfully")
    
    def _validate(self):
        """Validate required environment variables."""
        required_vars = {
            'KEYCLOAK_ADMIN_USERNAME': self.KEYCLOAK_ADMIN_USERNAME,
            'KEYCLOAK_ADMIN_PASSWORD': self.KEYCLOAK_ADMIN_PASSWORD,
        }
        
        missing = [var for var, value in required_vars.items() if not value]
        if missing:
            raise ValueError(f"❌ Missing required environment variables: {missing}")
        
        # Validate SMTP if provided
        smtp_vars = [self.SMTP_HOST, self.SMTP_USER, self.SMTP_PASSWORD]
        if any(smtp_vars) and not all(smtp_vars):
            self.logger.warning("⚠️  Partial SMTP configuration detected. Email features may not work.")
    
    def get_smtp_config(self) -> Optional[dict]:
        """Get SMTP configuration if complete."""
        if all([self.SMTP_HOST, self.SMTP_USER, self.SMTP_PASSWORD]):
            return {
                'host': self.SMTP_HOST,
                'port': self.SMTP_PORT,
                'auth': 'true',
                'ssl': 'false',
                'starttls': 'true',
                'user': self.SMTP_USER,
                'password': self.SMTP_PASSWORD,
                'from': self.SMTP_FROM or 'noreply@padmini.systems',
                'fromDisplayName': self.SMTP_FROM_DISPLAY_NAME or 'Padmini Systems'
            }
        return None
    
    def is_create_action(self) -> bool:
        """Check if action is create."""
        return self.ACTION == 'create'
    
    def is_destroy_action(self) -> bool:
        """Check if action is destroy."""
        return self.ACTION == 'destroy'
    
    def is_validate_action(self) -> bool:
        """Check if action is validate."""
        return self.ACTION == 'validate'
