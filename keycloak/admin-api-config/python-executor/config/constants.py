"""
Constants Configuration
All Keycloak configuration constants in one place for easy management
"""


class Constants:
    """All configuration constants for Keycloak setup."""
    
    # Realm Configuration
    REALM_NAME = "padmini-systems"
    REALM_DISPLAY_NAME = "Padmini Systems"
    
    # Client IDs
    PPCS_CLIENT_ID = "ppcs-web-app"
    ASM_CLIENT_ID = "asm-microservices"
    
    # NextJS Client Configuration
    PPCS_CLIENT_CONFIG = {
        "clientId": PPCS_CLIENT_ID,
        "name": "PPCS Web Application",
        "description": "Padmini Private Cloud Service Web Application",
        "enabled": True,
        "publicClient": True,
        "standardFlowEnabled": True,
        "implicitFlowEnabled": False,
        "directAccessGrantsEnabled": True,
        "serviceAccountsEnabled": False,
        "authorizationServicesEnabled": False,
        "redirectUris": [
            "http://localhost:3000/api/auth/callback/keycloak",
            "https://ppcs.padmini.systems/api/auth/callback/keycloak",
            "https://app.padmini.systems/api/auth/callback/keycloak"
        ],
        "webOrigins": [
            "http://localhost:3000",
            "https://ppcs.padmini.systems",
            "https://app.padmini.systems"
        ],
        "attributes": {
            "oidc.ciba.grant.enabled": "false",
            "oauth2.device.authorization.grant.enabled": "false",
            "backchannel.logout.session.required": "true",
            "backchannel.logout.revoke.offline.tokens": "false"
        },
        "defaultClientScopes": [
            "openid", "profile", "email", "web-origins", "acr", "roles"
        ],
        "optionalClientScopes": [
            "mobile", "address", "phone", "offline_access"
        ]
    }
    
    # Microservices Client Configuration
    ASM_CLIENT_CONFIG = {
        "clientId": ASM_CLIENT_ID,
        "name": "ASM Microservices",
        "description": "Asset Management Microservices Client",
        "enabled": True,
        "publicClient": False,
        "standardFlowEnabled": True,
        "serviceAccountsEnabled": True,
        "authorizationServicesEnabled": True,
        "secret": "asm-microservices-secret-change-me",
        "rootUrl": "https://api.padmini.systems",
        "adminUrl": "https://api.padmini.systems",
        "baseUrl": "/",
        "redirectUris": [
            "https://api.padmini.systems/*",
            "http://localhost:8080/*"
        ],
        "webOrigins": [
            "https://api.padmini.systems",
            "http://localhost:8080"
        ],
        "defaultClientScopes": [
            "openid", "profile", "email", "web-origins", "acr", "roles"
        ],
        "optionalClientScopes": [
            "mobile", "address", "phone", "offline_access"
        ]
    }
    
    # Client Scopes Configuration
    CLIENT_SCOPES = {
        "openid": {
            "name": "openid",
            "description": "OpenID Connect built-in scope: openid",
            "protocol": "openid-connect",
            "attributes": {
                "include.in.token.scope": "true",
                "display.on.consent.screen": "false"
            },
            "protocolMappers": [
                {
                    "name": "sub",
                    "protocol": "openid-connect",
                    "protocolMapper": "oidc-sub-mapper",
                    "consentRequired": False,
                    "config": {
                        "access.token.claim": "true",
                        "id.token.claim": "true"
                    }
                }
            ]
        },
        "profile": {
            "name": "profile",
            "description": "OpenID Connect built-in scope: profile",
            "protocol": "openid-connect",
            "attributes": {
                "include.in.token.scope": "true",
                "display.on.consent.screen": "true"
            },
            "protocolMappers": [
                {
                    "name": "username",
                    "protocol": "openid-connect",
                    "protocolMapper": "oidc-usermodel-property-mapper",
                    "consentRequired": False,
                    "config": {
                        "user.attribute": "username",
                        "claim.name": "preferred_username",
                        "jsonType.label": "String",
                        "id.token.claim": "true",
                        "access.token.claim": "true",
                        "userinfo.token.claim": "true"
                    }
                },
                {
                    "name": "given name",
                    "protocol": "openid-connect",
                    "protocolMapper": "oidc-usermodel-property-mapper",
                    "consentRequired": False,
                    "config": {
                        "user.attribute": "firstName",
                        "claim.name": "given_name",
                        "jsonType.label": "String",
                        "id.token.claim": "true",
                        "access.token.claim": "true",
                        "userinfo.token.claim": "true"
                    }
                },
                {
                    "name": "family name",
                    "protocol": "openid-connect",
                    "protocolMapper": "oidc-usermodel-property-mapper",
                    "consentRequired": False,
                    "config": {
                        "user.attribute": "lastName",
                        "claim.name": "family_name",
                        "jsonType.label": "String",
                        "id.token.claim": "true",
                        "access.token.claim": "true",
                        "userinfo.token.claim": "true"
                    }
                },
                {
                    "name": "full name",
                    "protocol": "openid-connect",
                    "protocolMapper": "oidc-full-name-mapper",
                    "consentRequired": False,
                    "config": {
                        "id.token.claim": "true",
                        "access.token.claim": "true",
                        "userinfo.token.claim": "true"
                    }
                }
            ]
        },
        "email": {
            "name": "email",
            "description": "OpenID Connect built-in scope: email",
            "protocol": "openid-connect",
            "attributes": {
                "include.in.token.scope": "true",
                "display.on.consent.screen": "true"
            },
            "protocolMappers": [
                {
                    "name": "email",
                    "protocol": "openid-connect",
                    "protocolMapper": "oidc-usermodel-property-mapper",
                    "consentRequired": False,
                    "config": {
                        "user.attribute": "email",
                        "claim.name": "email",
                        "jsonType.label": "String",
                        "id.token.claim": "true",
                        "access.token.claim": "true",
                        "userinfo.token.claim": "true"
                    }
                },
                {
                    "name": "email verified",
                    "protocol": "openid-connect",
                    "protocolMapper": "oidc-usermodel-property-mapper",
                    "consentRequired": False,
                    "config": {
                        "user.attribute": "emailVerified",
                        "claim.name": "email_verified",
                        "jsonType.label": "boolean",
                        "id.token.claim": "true",
                        "access.token.claim": "true",
                        "userinfo.token.claim": "true"
                    }
                }
            ]
        },
        "mobile": {
            "name": "mobile",
            "description": "Mobile number information",
            "protocol": "openid-connect",
            "attributes": {
                "include.in.token.scope": "true",
                "display.on.consent.screen": "true"
            },
            "protocolMappers": [
                {
                    "name": "mobile number",
                    "protocol": "openid-connect",
                    "protocolMapper": "oidc-usermodel-attribute-mapper",
                    "consentRequired": False,
                    "config": {
                        "user.attribute": "mobile",
                        "claim.name": "mobile",
                        "jsonType.label": "String",
                        "id.token.claim": "true",
                        "access.token.claim": "true",
                        "userinfo.token.claim": "true"
                    }
                }
            ]
        }
    }
    
    # Realm Configuration Template
    REALM_CONFIG = {
        "id": REALM_NAME,
        "realm": REALM_NAME,
        "displayName": REALM_DISPLAY_NAME,
        "enabled": True,
        "sslRequired": "external",
        "registrationAllowed": True,
        "registrationEmailAsUsername": False,
        "rememberMe": True,
        "verifyEmail": True,
        "loginWithEmailAllowed": True,
        "duplicateEmailsAllowed": False,
        "resetPasswordAllowed": True,
        "editUsernameAllowed": False,
        "bruteForceProtected": True,
        "permanentLockout": False,
        "maxFailureWaitSeconds": 900,
        "minimumQuickLoginWaitSeconds": 60,
        "waitIncrementSeconds": 60,
        "quickLoginCheckMilliSeconds": 1000,
        "maxDeltaTimeSeconds": 43200,
        "failureFactor": 30,
        "loginTheme": "keycloak",
        "accountTheme": "keycloak.v2",
        "adminTheme": "keycloak.v2",
        "emailTheme": "keycloak",
        "accessTokenLifespan": 300,
        "accessTokenLifespanForImplicitFlow": 900,
        "ssoSessionIdleTimeout": 1800,
        "ssoSessionMaxLifespan": 36000,
        "offlineSessionIdleTimeout": 2592000,
        "offlineSessionMaxLifespan": 5184000,
        "accessCodeLifespan": 60,
        "accessCodeLifespanUserAction": 300,
        "accessCodeLifespanLogin": 1800,
        "actionTokenGeneratedByAdminLifespan": 43200,
        "actionTokenGeneratedByUserLifespan": 300,
        "internationalizationEnabled": True,
        "supportedLocales": ["en", "hi"],
        "defaultLocale": "en"
    }
    
    # User Profile Configuration
    USER_PROFILE_CONFIG = {
        "attributes": [
            {
                "name": "mobile",
                "displayName": "Mobile Number",
                "validations": {
                    "pattern": {
                        "pattern": "^[+]?[1-9]\\d{9,14}$",
                        "error-message": "Enter valid mobile with country code"
                    },
                    "length": {
                        "min": 10,
                        "max": 15
                    }
                },
                "annotations": {
                    "inputType": "phone"
                },
                "required": {
                    "roles": ["user"]
                },
                "permissions": {
                    "view": ["admin", "user"],
                    "edit": ["admin", "user"]
                }
            }
        ]
    }
    
    # Default Roles
    DEFAULT_ROLES = [
        {
            "name": "user",
            "description": "Default user role for all authenticated users"
        },
        {
            "name": "admin",
            "description": "Administrator role with full access"
        }
    ]
    
    # Default Groups
    DEFAULT_GROUPS = [
        {
            "name": "users",
            "path": "/users"
        },
        {
            "name": "admins",
            "path": "/admins"
        }
    ]
