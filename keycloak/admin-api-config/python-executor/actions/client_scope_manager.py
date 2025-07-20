"""
Client Scope Manager
Handles OIDC client scopes creation and management
"""
from typing import Dict, Any, List
from actions.base_manager import BaseManager


class ClientScopeManager(BaseManager):
    """Manages OIDC client scopes for business requirements."""
    
    def create(self) -> bool:
        """Create all required client scopes."""
        try:
            self.logger.start_operation("client scopes creation")
            
            success = True
            for scope_name, scope_config in self.constants.CLIENT_SCOPES.items():
                if not self._create_single_scope(scope_name, scope_config):
                    success = False
            
            if success:
                self.logger.success("All client scopes created successfully")
            else:
                self.logger.error("Some client scopes failed to create")
            
            return success
            
        except Exception as e:
            return self._handle_api_error("Client scopes creation", e)
    
    def destroy(self) -> bool:
        """Destroy all created client scopes."""
        try:
            self.logger.rollback_operation("client scopes destruction")
            
            success = True
            for scope_name in self.constants.CLIENT_SCOPES.keys():
                if not self._destroy_single_scope(scope_name):
                    success = False
            
            if success:
                self.logger.success("All client scopes destroyed successfully")
            else:
                self.logger.warning("Some client scopes failed to destroy")
            
            return success
            
        except Exception as e:
            return self._handle_api_error("Client scopes destruction", e)
    
    def validate(self) -> bool:
        """Validate all client scopes exist and are configured correctly."""
        try:
            self.logger.start_operation("client scopes validation")
            
            validations = []
            for scope_name in self.constants.CLIENT_SCOPES.keys():
                validations.append(self._validate_single_scope(scope_name))
            
            if all(validations):
                self.logger.success("All client scopes validation passed")
                return True
            else:
                self.logger.error("Client scopes validation failed")
                return False
                
        except Exception as e:
            return self._handle_api_error("Client scopes validation", e)
    
    def _create_single_scope(self, scope_name: str, scope_config: Dict[str, Any]) -> bool:
        """Create a single client scope with protocol mappers."""
        try:
            # Check if scope already exists
            existing_scope = self.keycloak_client.get_client_scope_by_name(
                self.realm_name, scope_name
            )
            
            if existing_scope:
                self.logger.skip_operation(
                    f"Client scope '{scope_name}'",
                    "Already exists"
                )
                scope_id = existing_scope['id']
            else:
                # Create scope (without protocol mappers first)
                scope_data = {
                    'name': scope_config['name'],
                    'description': scope_config['description'],
                    'protocol': scope_config['protocol'],
                    'attributes': scope_config['attributes']
                }
                
                scope_id = self.keycloak_client.create_client_scope(
                    self.realm_name, scope_data
                )
                
                if not scope_id:
                    self.logger.error(f"Failed to create scope '{scope_name}'")
                    return False
                
                self.logger.success(f"Client scope '{scope_name}' created")
            
            # Create protocol mappers
            if 'protocolMappers' in scope_config:
                for mapper in scope_config['protocolMappers']:
                    if not self._create_protocol_mapper(scope_id, mapper):
                        self.logger.warning(
                            f"Failed to create mapper '{mapper['name']}' "
                            f"for scope '{scope_name}'"
                        )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating scope '{scope_name}': {str(e)}")
            return False
    
    def _create_protocol_mapper(self, scope_id: str, mapper_config: Dict[str, Any]) -> bool:
        """Create a protocol mapper for a client scope."""
        try:
            return self.keycloak_client.create_protocol_mapper(
                self.realm_name, scope_id, mapper_config
            )
        except Exception as e:
            self.logger.error(f"Error creating protocol mapper: {str(e)}")
            return False
    
    def _destroy_single_scope(self, scope_name: str) -> bool:
        """Destroy a single client scope."""
        try:
            # Get scope by name
            scope = self.keycloak_client.get_client_scope_by_name(
                self.realm_name, scope_name
            )
            
            if not scope:
                self.logger.skip_operation(
                    f"Client scope '{scope_name}' destruction",
                    "Does not exist"
                )
                return True
            
            # Delete scope
            if self.keycloak_client.delete_client_scope(
                self.realm_name, scope['id']
            ):
                self.logger.success(f"Client scope '{scope_name}' deleted")
                return True
            else:
                self.logger.error(f"Failed to delete scope '{scope_name}'")
                return False
                
        except Exception as e:
            self.logger.error(f"Error destroying scope '{scope_name}': {str(e)}")
            return False
    
    def _validate_single_scope(self, scope_name: str) -> bool:
        """Validate a single client scope."""
        try:
            scope = self.keycloak_client.get_client_scope_by_name(
                self.realm_name, scope_name
            )
            
            if not scope:
                self.logger.error(f"Client scope '{scope_name}' not found")
                return False
            
            # Validate basic properties
            expected = self.constants.CLIENT_SCOPES[scope_name]
            validations = [
                scope.get('name') == expected['name'],
                scope.get('protocol') == expected['protocol'],
                scope.get('description') == expected['description']
            ]
            
            if all(validations):
                self.logger.debug(f"✓ Client scope '{scope_name}' valid")
                return True
            else:
                self.logger.error(f"✗ Client scope '{scope_name}' invalid")
                return False
                
        except Exception as e:
            self.logger.error(f"Error validating scope '{scope_name}': {str(e)}")
            return False
    
    def get_scope_ids(self) -> Dict[str, str]:
        """Get all client scope IDs mapped by name."""
        scope_ids = {}
        
        for scope_name in self.constants.CLIENT_SCOPES.keys():
            scope = self.keycloak_client.get_client_scope_by_name(
                self.realm_name, scope_name
            )
            if scope:
                scope_ids[scope_name] = scope['id']
        
        return scope_ids
