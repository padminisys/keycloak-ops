"""
Base Manager Class
Abstract base class for all Keycloak configuration managers
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from utils.keycloak_client import KeycloakClient
from utils.logger import PadminiLogger
from config.constants import Constants


class BaseManager(ABC):
    """Base class for all Keycloak configuration managers."""
    
    def __init__(self, keycloak_client: KeycloakClient, constants: Constants):
        self.keycloak_client = keycloak_client
        self.constants = constants
        self.logger = PadminiLogger(self.__class__.__name__)
        self.realm_name = constants.REALM_NAME
    
    @abstractmethod
    def create(self) -> bool:
        """Create the configuration component."""
        pass
    
    @abstractmethod
    def destroy(self) -> bool:
        """Destroy/rollback the configuration component."""
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """Validate the configuration component."""
        pass
    
    def _handle_api_error(self, operation: str, error: Exception) -> bool:
        """Common error handling for API operations."""
        self.logger.error(f"{operation} failed: {str(error)}")
        return False
    
    def _is_idempotent_create(self, resource_name: str, exists: bool) -> bool:
        """Handle idempotent creation."""
        if exists:
            self.logger.skip_operation(
                f"Create {resource_name}",
                "Already exists"
            )
            return True
        return False
    
    def _is_idempotent_destroy(self, resource_name: str, exists: bool) -> bool:
        """Handle idempotent destruction."""
        if not exists:
            self.logger.skip_operation(
                f"Destroy {resource_name}",
                "Does not exist"
            )
            return True
        return False
