"""
Main Orchestrator
Coordinates all Keycloak configuration operations
"""
import sys
from config.environment import Environment
from config.constants import Constants
from utils.logger import PadminiLogger
from utils.keycloak_client import KeycloakClient
from actions.realm_manager import RealmManager
from actions.client_scope_manager import ClientScopeManager
from actions.ppcs_client.ppcs_client_manager import PPCSClientManager
from actions.asm_client.asm_client_manager import ASMClientManager
from actions.user_profile_manager import UserProfileManager


class KeycloakOrchestrator:
    """
    Main orchestrator for Keycloak configuration.
    Handles the complete setup/teardown of Padmini Systems realm.
    """
    
    def __init__(self):
        self.env = Environment()
        self.constants = Constants()
        self.logger = PadminiLogger(__name__)
        self.keycloak_client = None
        self.managers = {}
        
    def initialize(self) -> bool:
        """Initialize Keycloak client and all managers."""
        try:
            self.logger.start_operation("Keycloak orchestrator initialization")
            
            # Initialize Keycloak client
            self.keycloak_client = KeycloakClient(
                server_url=self.env.KEYCLOAK_URL,
                username=self.env.KEYCLOAK_ADMIN_USERNAME,
                password=self.env.KEYCLOAK_ADMIN_PASSWORD
            )
            
            if not self.keycloak_client.connect():
                self.logger.error("Failed to connect to Keycloak")
                return False
                
            # Initialize all managers
            self.managers = {
                'realm': RealmManager(self.keycloak_client, self.constants),
                'client_scopes': ClientScopeManager(
                    self.keycloak_client, self.constants
                ),
                'ppcs_client': PPCSClientManager(
                    self.keycloak_client, self.constants
                ),
                'asm_client': ASMClientManager(
                    self.keycloak_client, self.constants
                ),
                'user_profile': UserProfileManager(
                    self.keycloak_client, self.constants
                )
            }
            
            self.logger.success(
                "Keycloak orchestrator initialized successfully"
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize orchestrator: {str(e)}")
            return False
    
    def create_configuration(self) -> bool:
        """Create complete Keycloak configuration."""
        try:
            self.logger.start_operation("Keycloak configuration creation")
            
            # Step 1: Create/Update Realm
            self.logger.info("Step 1: Creating realm...")
            if not self.managers['realm'].create():
                self.logger.error("Failed to create realm")
                return False
                
            # Step 2: Create Client Scopes (openid, profile, email, mobile)
            self.logger.info("Step 2: Creating client scopes...")
            if not self.managers['client_scopes'].create():
                self.logger.error("Failed to create client scopes")
                return False
                
            # Step 3: Create PPCS Web App Client
            self.logger.info("Step 3: Creating PPCS web client...")
            if not self.managers['ppcs_client'].create():
                self.logger.error("Failed to create PPCS client")
                return False
                
            # Step 4: Create ASM Microservices Client
            self.logger.info("Step 4: Creating ASM microservices client...")
            if not self.managers['asm_client'].create():
                self.logger.error("Failed to create ASM client")
                return False
                
            # Step 5: Configure User Profile with Roles and Groups
            self.logger.info("Step 5: Configuring user profile...")
            if not self.managers['user_profile'].create():
                self.logger.error("Failed to configure user profile")
                return False
            
            self._print_success_summary()
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration creation failed: {str(e)}")
            return False
    
    def destroy_configuration(self) -> bool:
        """Destroy Keycloak configuration (rollback)."""
        try:
            self.logger.start_operation("Keycloak configuration destruction")
            
            # Destroy in reverse order
            success = True
            
            self.logger.info("Step 1: Destroying user profile...")
            if not self.managers['user_profile'].destroy():
                self.logger.warning("Failed to destroy user profile")
                success = False
                
            self.logger.info("Step 2: Destroying ASM client...")
            if not self.managers['asm_client'].destroy():
                self.logger.warning("Failed to destroy ASM client")
                success = False
                
            self.logger.info("Step 3: Destroying PPCS client...")
            if not self.managers['ppcs_client'].destroy():
                self.logger.warning("Failed to destroy PPCS client")
                success = False
                
            self.logger.info("Step 4: Destroying client scopes...")
            if not self.managers['client_scopes'].destroy():
                self.logger.warning("Failed to destroy client scopes")
                success = False
                
            self.logger.info("Step 5: Destroying realm...")
            if not self.managers['realm'].destroy():
                self.logger.warning("Failed to destroy realm")
                success = False
                
            if success:
                self.logger.success("Configuration destroyed successfully!")
            else:
                self.logger.warning("Some components failed to destroy")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Configuration destruction failed: {str(e)}")
            return False
    
    def validate_configuration(self) -> bool:
        """Validate that configuration is working correctly."""
        try:
            self.logger.start_operation("Keycloak configuration validation")
            
            # Validate each component
            validations = [
                self.managers['realm'].validate(),
                self.managers['client_scopes'].validate(),
                self.managers['ppcs_client'].validate(),
                self.managers['asm_client'].validate(),
                self.managers['user_profile'].validate()
            ]
            
            if all(validations):
                self.logger.success("All configurations validated successfully!")
                return True
            else:
                self.logger.error("Some configurations failed validation")
                return False
                
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {str(e)}")
            return False
    
    def _print_success_summary(self):
        """Print success summary with business requirements."""
        self.logger.success("Padmini Systems Keycloak Configuration Completed!")
        self.logger.info("=" * 60)
        self.logger.info("")
        self.logger.info("✅ Business Requirements Fulfilled:")
        self.logger.info("   - Name: ✓ (given_name, family_name, name)")
        self.logger.info("   - Username: ✓ (preferred_username)")
        self.logger.info("   - UUID: ✓ (sub)")
        self.logger.info("   - Mobile: ✓ (mobile attribute)")
        self.logger.info("   - Email: ✓ (email, email_verified)")
        self.logger.info("")
        self.logger.info("🔗 Test URLs:")
        self.logger.info(f"   Admin Console: {self.env.KEYCLOAK_URL}/admin")
        self.logger.info(f"   OIDC Discovery: {self.env.KEYCLOAK_URL}/realms/"
                        f"{self.constants.REALM_NAME}/.well-known/openid_configuration")
        self.logger.info("")
        self.logger.info("📝 NextJS Configuration:")
        self.logger.info("   Scope: 'openid profile email mobile'")
        self.logger.info("   Claims: sub, preferred_username, given_name,")
        self.logger.info("           family_name, name, email, email_verified, mobile")
        self.logger.info("")
        self.logger.info("✅ Mobile field configured automatically")
        self.logger.info("   If mobile field doesn't appear, check:")
        self.logger.info("   Keycloak Admin → Realm Settings → User Profile")


def main():
    """Main entry point."""
    orchestrator = KeycloakOrchestrator()
    
    if not orchestrator.initialize():
        sys.exit(1)
    
    # Get action from environment
    action = orchestrator.env.ACTION
    
    if action == 'create':
        success = orchestrator.create_configuration()
    elif action == 'destroy':
        success = orchestrator.destroy_configuration()
    elif action == 'validate':
        success = orchestrator.validate_configuration()
    else:
        orchestrator.logger.error(f"Unknown action: {action}")
        orchestrator.logger.info("Valid actions: create, destroy, validate")
        sys.exit(1)
    
    if success:
        orchestrator.logger.success(f"Action '{action}' completed successfully!")
        sys.exit(0)
    else:
        orchestrator.logger.error(f"Action '{action}' failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
