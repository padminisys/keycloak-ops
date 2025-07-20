"""
Keycloak REST API Client
Handles all HTTP interactions with Keycloak Admin API
"""
import requests
import json
import time
from typing import Dict, Any, Optional, List
from utils.logger import PadminiLogger


class KeycloakClient:
    """Keycloak Admin REST API Client."""
    
    def __init__(self, server_url: str, username: str, password: str):
        self.server_url = server_url.rstrip('/')
        self.username = username
        self.password = password
        self.access_token = None
        self.logger = PadminiLogger(__name__)
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def connect(self) -> bool:
        """Authenticate and get access token."""
        try:
            self.logger.start_operation("Keycloak authentication")
            
            # Wait for Keycloak to be ready
            if not self._wait_for_keycloak():
                return False
            
            # Get access token
            token_url = f"{self.server_url}/realms/master/protocol/openid-connect/token"
            
            data = {
                'grant_type': 'password',
                'client_id': 'admin-cli',
                'username': self.username,
                'password': self.password
            }
            
            response = self.session.post(
                token_url,
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                
                # Update session headers
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                
                self.logger.success("Keycloak authentication successful")
                return True
            else:
                self.logger.error(f"Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Authentication error: {str(e)}")
            return False
    
    def _wait_for_keycloak(self, max_attempts: int = 30) -> bool:
        """Wait for Keycloak to be ready."""
        self.logger.start_operation("Waiting for Keycloak readiness")
        
        for attempt in range(max_attempts):
            try:
                health_url = f"{self.server_url}/health/ready"
                response = requests.get(health_url, timeout=5)
                
                if response.status_code == 200:
                    self.logger.success("Keycloak is ready")
                    return True
                    
            except Exception:
                pass
            
            self.logger.debug(f"Attempt {attempt + 1}/{max_attempts}, retrying...")
            time.sleep(10)
        
        self.logger.error("Keycloak not ready after maximum attempts")
        return False
    
    def get(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """GET request to Keycloak API."""
        try:
            url = f"{self.server_url}/admin{endpoint}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                self.logger.error(f"GET {endpoint} failed: {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"GET {endpoint} error: {str(e)}")
            return None
    
    def post(self, endpoint: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """POST request to Keycloak API."""
        try:
            url = f"{self.server_url}/admin{endpoint}"
            response = self.session.post(url, json=data)
            
            if response.status_code in [200, 201]:
                if response.content:
                    return response.json()
                else:
                    # Extract ID from Location header if present
                    location = response.headers.get('Location', '')
                    if location:
                        return {'id': location.split('/')[-1]}
                    return {'success': True}
            elif response.status_code == 409:
                self.logger.skip_operation(
                    f"POST {endpoint}",
                    "Resource already exists"
                )
                return {'exists': True}
            else:
                self.logger.error(f"POST {endpoint} failed: {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"POST {endpoint} error: {str(e)}")
            return None
    
    def put(self, endpoint: str, data: Dict[str, Any]) -> bool:
        """PUT request to Keycloak API."""
        try:
            url = f"{self.server_url}/admin{endpoint}"
            response = self.session.put(url, json=data)
            
            if response.status_code in [200, 204]:
                return True
            else:
                self.logger.error(f"PUT {endpoint} failed: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"PUT {endpoint} error: {str(e)}")
            return False
    
    def delete(self, endpoint: str) -> bool:
        """DELETE request to Keycloak API."""
        try:
            url = f"{self.server_url}/admin{endpoint}"
            response = self.session.delete(url)
            
            if response.status_code in [200, 204]:
                return True
            elif response.status_code == 404:
                self.logger.skip_operation(
                    f"DELETE {endpoint}",
                    "Resource not found"
                )
                return True
            else:
                self.logger.error(f"DELETE {endpoint} failed: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"DELETE {endpoint} error: {str(e)}")
            return False
    
    # Realm Operations
    def create_realm(self, realm_config: Dict[str, Any]) -> bool:
        """Create a new realm."""
        return self.post('/realms', realm_config) is not None
    
    def get_realm(self, realm_name: str) -> Optional[Dict[str, Any]]:
        """Get realm configuration."""
        return self.get(f'/realms/{realm_name}')
    
    def update_realm(self, realm_name: str, realm_config: Dict[str, Any]) -> bool:
        """Update realm configuration."""
        return self.put(f'/realms/{realm_name}', realm_config)
    
    def delete_realm(self, realm_name: str) -> bool:
        """Delete a realm."""
        return self.delete(f'/realms/{realm_name}')
    
    # Client Scope Operations
    def create_client_scope(
        self,
        realm_name: str,
        scope_config: Dict[str, Any]
    ) -> Optional[str]:
        """Create client scope and return ID."""
        result = self.post(f'/realms/{realm_name}/client-scopes', scope_config)
        return result.get('id') if result else None
    
    def get_client_scope_by_name(
        self,
        realm_name: str,
        scope_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get client scope by name."""
        scopes = self.get(f'/realms/{realm_name}/client-scopes')
        if scopes:
            for scope in scopes:
                if scope.get('name') == scope_name:
                    return scope
        return None
    
    def delete_client_scope(self, realm_name: str, scope_id: str) -> bool:
        """Delete client scope."""
        return self.delete(f'/realms/{realm_name}/client-scopes/{scope_id}')
    
    # Protocol Mapper Operations
    def create_protocol_mapper(
        self,
        realm_name: str,
        scope_id: str,
        mapper_config: Dict[str, Any]
    ) -> bool:
        """Create protocol mapper for client scope."""
        endpoint = f'/realms/{realm_name}/client-scopes/{scope_id}/protocol-mappers/models'
        return self.post(endpoint, mapper_config) is not None
    
    # Client Operations
    def create_client(
        self,
        realm_name: str,
        client_config: Dict[str, Any]
    ) -> Optional[str]:
        """Create client and return ID."""
        result = self.post(f'/realms/{realm_name}/clients', client_config)
        return result.get('id') if result else None
    
    def get_client_by_client_id(
        self,
        realm_name: str,
        client_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get client by clientId."""
        clients = self.get(f'/realms/{realm_name}/clients?clientId={client_id}')
        return clients[0] if clients else None
    
    def update_client(
        self,
        realm_name: str,
        client_uuid: str,
        client_config: Dict[str, Any]
    ) -> bool:
        """Update client configuration."""
        return self.put(f'/realms/{realm_name}/clients/{client_uuid}', client_config)
    
    def delete_client(self, realm_name: str, client_uuid: str) -> bool:
        """Delete client."""
        return self.delete(f'/realms/{realm_name}/clients/{client_uuid}')
    
    # Client Scope Assignment Operations
    def assign_default_client_scope(
        self,
        realm_name: str,
        client_uuid: str,
        scope_id: str
    ) -> bool:
        """Assign default client scope to client."""
        endpoint = f'/realms/{realm_name}/clients/{client_uuid}/default-client-scopes/{scope_id}'
        return self.put(endpoint, {})
    
    def assign_optional_client_scope(
        self,
        realm_name: str,
        client_uuid: str,
        scope_id: str
    ) -> bool:
        """Assign optional client scope to client."""
        endpoint = f'/realms/{realm_name}/clients/{client_uuid}/optional-client-scopes/{scope_id}'
        return self.put(endpoint, {})
    
    # Role Operations
    def create_realm_role(
        self,
        realm_name: str,
        role_config: Dict[str, Any]
    ) -> bool:
        """Create realm role."""
        return self.post(f'/realms/{realm_name}/roles', role_config) is not None
    
    def delete_realm_role(self, realm_name: str, role_name: str) -> bool:
        """Delete realm role."""
        return self.delete(f'/realms/{realm_name}/roles/{role_name}')
    
    # Group Operations
    def create_group(
        self,
        realm_name: str,
        group_config: Dict[str, Any]
    ) -> Optional[str]:
        """Create group and return ID."""
        result = self.post(f'/realms/{realm_name}/groups', group_config)
        return result.get('id') if result else None
    
    def delete_group(self, realm_name: str, group_id: str) -> bool:
        """Delete group."""
        return self.delete(f'/realms/{realm_name}/groups/{group_id}')
