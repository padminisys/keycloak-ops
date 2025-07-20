"""
Realm Manager
Handles realm creation, configuration, and destruction
"""
from typing import Dict, Any, Optional
from actions.base_manager import BaseManager


class RealmManager(BaseManager):
    """Manages Keycloak realm operations."""
    
    def create(self) -> bool:
        """Create and configure the Padmini Systems realm."""
        try:
            self.logger.start_operation("realm creation")
            
            # Check if realm already exists
            existing_realm = self.keycloak_client.get_realm(self.realm_name)
            if existing_realm:
                self.logger.skip_operation(
                    "Realm creation",
                    f"Realm '{self.realm_name}' already exists"
                )
                return self._update_realm_config()
            
            # Prepare realm configuration
            realm_config = self._prepare_realm_config()
            
            # Create realm
            if self.keycloak_client.create_realm(realm_config):
                self.logger.success(f"Realm '{self.realm_name}' created")
                return True
            else:
                self.logger.error("Failed to create realm")
                return False
                
        except Exception as e:
            return self._handle_api_error("Realm creation", e)
    
    def destroy(self) -> bool:
        """Destroy the realm."""
        try:
            self.logger.rollback_operation("realm destruction")
            
            # Check if realm exists
            existing_realm = self.keycloak_client.get_realm(self.realm_name)
            if not existing_realm:
                self.logger.skip_operation(
                    "Realm destruction",
                    f"Realm '{self.realm_name}' does not exist"
                )
                return True
            
            # Delete realm
            if self.keycloak_client.delete_realm(self.realm_name):
                self.logger.success(f"Realm '{self.realm_name}' deleted")
                return True
            else:
                self.logger.error("Failed to delete realm")
                return False
                
        except Exception as e:
            return self._handle_api_error("Realm destruction", e)
    
    def validate(self) -> bool:
        """Validate realm configuration."""
        try:
            self.logger.start_operation("realm validation")
            
            # Get realm configuration
            realm = self.keycloak_client.get_realm(self.realm_name)
            if not realm:
                self.logger.error(f"Realm '{self.realm_name}' not found")
                return False
            
            # Validate key properties
            validations = [
                self._validate_property(realm, 'enabled', True),
                self._validate_property(realm, 'displayName', 
                                      self.constants.REALM_DISPLAY_NAME),
                self._validate_property(realm, 'registrationAllowed', True),
                self._validate_property(realm, 'verifyEmail', True),
                self._validate_property(realm, 'sslRequired', 'external'),
            ]
            
            if all(validations):
                self.logger.success("Realm validation passed")
                return True
            else:
                self.logger.error("Realm validation failed")
                return False
                
        except Exception as e:
            return self._handle_api_error("Realm validation", e)
    
    def _prepare_realm_config(self) -> Dict[str, Any]:
        """Prepare realm configuration with SMTP if available."""
        # Start with base configuration
        realm_config = self.constants.REALM_CONFIG.copy()
        
        # Add SMTP configuration if available
        from config.environment import Environment
        env = Environment()
        smtp_config = env.get_smtp_config()
        
        if smtp_config:
            realm_config['smtpServer'] = smtp_config
            self.logger.info("SMTP configuration added to realm")
        else:
            self.logger.warning("SMTP configuration not available")
        
        return realm_config
    
    def _update_realm_config(self) -> bool:
        """Update existing realm configuration."""
        try:
            realm_config = self._prepare_realm_config()
            
            if self.keycloak_client.update_realm(self.realm_name, realm_config):
                self.logger.success("Realm configuration updated")
                return True
            else:
                self.logger.error("Failed to update realm configuration")
                return False
                
        except Exception as e:
            return self._handle_api_error("Realm update", e)
    
    def _validate_property(
        self,
        realm: Dict[str, Any],
        property_name: str,
        expected_value: Any
    ) -> bool:
        """Validate a single realm property."""
        actual_value = realm.get(property_name)
        if actual_value == expected_value:
            self.logger.debug(f"✓ {property_name}: {actual_value}")
            return True
        else:
            self.logger.error(
                f"✗ {property_name}: expected {expected_value}, "
                f"got {actual_value}"
            )
            return False
