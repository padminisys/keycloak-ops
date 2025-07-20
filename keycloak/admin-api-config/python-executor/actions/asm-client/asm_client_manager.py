"""
ASM Client Manager
Handles microservices client configuration
"""
from typing import Dict, Any
from actions.base_manager import BaseManager
from actions.client_scope_manager import ClientScopeManager


class ASMClientManager(BaseManager):
    """Manages ASM (microservices) client."""
    
    def __init__(self, keycloak_client, constants):
        super().__init__(keycloak_client, constants)
        self.client_id = constants.ASM_CLIENT_ID
        self.client_config = constants.ASM_CLIENT_CONFIG
    
    def create(self) -> bool:
        """Create and configure ASM microservices client."""
        try:
            self.logger.start_operation("ASM client creation")
            
            # Check if client already exists
            existing_client = self.keycloak_client.get_client_by_client_id(
                self.realm_name, self.client_id
            )
            
            if existing_client:
                self.logger.skip_operation(
                    f"ASM client '{self.client_id}'",
                    "Already exists"
                )
                client_uuid = existing_client['id']
                
                # Update configuration
                if not self._update_client_config(client_uuid):
                    return False
            else:
                # Create new client
                client_uuid = self.keycloak_client.create_client(
                    self.realm_name, self.client_config
                )
                
                if not client_uuid:
                    self.logger.error("Failed to create ASM client")
                    return False
                
                self.logger.success(f"ASM client '{self.client_id}' created")
            
            # Assign client scopes
            if not self._assign_client_scopes(client_uuid):
                return False
            
            self.logger.success("ASM client configuration completed")
            return True
            
        except Exception as e:
            return self._handle_api_error("ASM client creation", e)
    
    def destroy(self) -> bool:
        """Destroy ASM client."""
        try:
            self.logger.rollback_operation("ASM client destruction")
            
            # Get client
            client = self.keycloak_client.get_client_by_client_id(
                self.realm_name, self.client_id
            )
            
            if not client:
                self.logger.skip_operation(
                    f"ASM client '{self.client_id}' destruction",
                    "Does not exist"
                )
                return True
            
            # Delete client
            if self.keycloak_client.delete_client(
                self.realm_name, client['id']
            ):
                self.logger.success(f"ASM client '{self.client_id}' deleted")
                return True
            else:
                self.logger.error("Failed to delete ASM client")
                return False
                
        except Exception as e:
            return self._handle_api_error("ASM client destruction", e)
    
    def validate(self) -> bool:
        """Validate ASM client configuration."""
        try:
            self.logger.start_operation("ASM client validation")
            
            # Get client
            client = self.keycloak_client.get_client_by_client_id(
                self.realm_name, self.client_id
            )
            
            if not client:
                self.logger.error(f"ASM client '{self.client_id}' not found")
                return False
            
            # Validate key properties
            validations = [
                self._validate_property(client, 'enabled', True),
                self._validate_property(client, 'publicClient', False),
                self._validate_property(client, 'serviceAccountsEnabled', True),
                self._validate_property(client, 'authorizationServicesEnabled', True),
                self._validate_redirect_uris(client),
                self._validate_web_origins(client)
            ]
            
            if all(validations):
                self.logger.success("ASM client validation passed")
                return True
            else:
                self.logger.error("ASM client validation failed")
                return False
                
        except Exception as e:
            return self._handle_api_error("ASM client validation", e)
    
    def _update_client_config(self, client_uuid: str) -> bool:
        """Update existing client configuration."""
        try:
            # Update basic configuration
            update_config = {
                'redirectUris': self.client_config['redirectUris'],
                'webOrigins': self.client_config['webOrigins'],
                'enabled': True,
                'publicClient': False,
                'serviceAccountsEnabled': True,
                'authorizationServicesEnabled': True
            }
            
            if self.keycloak_client.update_client(
                self.realm_name, client_uuid, update_config
            ):
                self.logger.success("ASM client configuration updated")
                return True
            else:
                self.logger.error("Failed to update ASM client configuration")
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating ASM client: {str(e)}")
            return False
    
    def _assign_client_scopes(self, client_uuid: str) -> bool:
        """Assign client scopes to ASM client."""
        try:
            # Get scope IDs
            scope_manager = ClientScopeManager(
                self.keycloak_client, self.constants
            )
            scope_ids = scope_manager.get_scope_ids()
            
            # Assign default scopes
            default_scopes = ['openid', 'profile', 'email']
            for scope_name in default_scopes:
                if scope_name in scope_ids:
                    success = self.keycloak_client.assign_default_client_scope(
                        self.realm_name, client_uuid, scope_ids[scope_name]
                    )
                    if success:
                        self.logger.debug(f"✓ Default scope '{scope_name}' assigned")
                    else:
                        self.logger.warning(f"Failed to assign default scope '{scope_name}'")
            
            # Assign optional scopes
            optional_scopes = ['mobile']
            for scope_name in optional_scopes:
                if scope_name in scope_ids:
                    success = self.keycloak_client.assign_optional_client_scope(
                        self.realm_name, client_uuid, scope_ids[scope_name]
                    )
                    if success:
                        self.logger.debug(f"✓ Optional scope '{scope_name}' assigned")
                    else:
                        self.logger.warning(f"Failed to assign optional scope '{scope_name}'")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error assigning client scopes: {str(e)}")
            return False
    
    def _validate_property(self, client: Dict[str, Any], prop: str, expected: Any) -> bool:
        """Validate a client property."""
        actual = client.get(prop)
        if actual == expected:
            self.logger.debug(f"✓ {prop}: {actual}")
            return True
        else:
            self.logger.error(f"✗ {prop}: expected {expected}, got {actual}")
            return False
    
    def _validate_redirect_uris(self, client: Dict[str, Any]) -> bool:
        """Validate redirect URIs."""
        actual_uris = set(client.get('redirectUris', []))
        expected_uris = set(self.client_config['redirectUris'])
        
        if expected_uris.issubset(actual_uris):
            self.logger.debug("✓ Redirect URIs valid")
            return True
        else:
            missing = expected_uris - actual_uris
            self.logger.error(f"✗ Missing redirect URIs: {missing}")
            return False
    
    def _validate_web_origins(self, client: Dict[str, Any]) -> bool:
        """Validate web origins."""
        actual_origins = set(client.get('webOrigins', []))
        expected_origins = set(self.client_config['webOrigins'])
        
        if expected_origins.issubset(actual_origins):
            self.logger.debug("✓ Web origins valid")
            return True
        else:
            missing = expected_origins - actual_origins
            self.logger.error(f"✗ Missing web origins: {missing}")
            return False
