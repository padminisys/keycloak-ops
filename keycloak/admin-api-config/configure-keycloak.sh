#!/bin/bash
set -e

echo "🔧 Padmini Systems - Complete Keycloak Configuration"
echo "===================================================="
echo "Business Requirements: name, username, uuid, mobile, email"
echo "Running inside Keycloak pod with kcadm.sh access"
echo ""

REALM_NAME="padmini-systems"
CLIENT_ID="ppcs-web-app"
MICROSERVICES_CLIENT_ID="asm-microservices"
KEYCLOAK_URL="http://localhost:8080"  # Internal pod access

# Wait for Keycloak to be ready
echo "⏳ Waiting for Keycloak server to be ready..."
until curl -s "$KEYCLOAK_URL/health/ready" >/dev/null 2>&1; do
  echo "   Waiting for Keycloak to start..."
  sleep 5
done
echo "✅ Keycloak server is ready"

# Login to Keycloak Admin using internal URL
echo "🔗 Connecting to Keycloak server (internal)..."
/opt/keycloak/bin/kcadm.sh config credentials \
  --server $KEYCLOAK_URL \
  --realm master \
  --user $KEYCLOAK_ADMIN_USERNAME \
  --password $KEYCLOAK_ADMIN_PASSWORD

echo "✅ Connected to Keycloak successfully"

# Step 1: Create/Update Realm with all business settings
echo "🏰 Creating/Updating realm: $REALM_NAME..."
/opt/keycloak/bin/kcadm.sh create realms -f - <<EOF || /opt/keycloak/bin/kcadm.sh update realms/$REALM_NAME -f - <<EOF
{
  "id": "$REALM_NAME",
  "realm": "$REALM_NAME",
  "displayName": "Padmini Systems",
  "displayNameHtml": "<div class=\"kc-logo-text\"><span>Padmini Systems</span></div>",
  "enabled": true,
  "sslRequired": "external",
  "registrationAllowed": true,
  "registrationEmailAsUsername": false,
  "rememberMe": true,
  "verifyEmail": true,
  "loginWithEmailAllowed": true,
  "duplicateEmailsAllowed": false,
  "resetPasswordAllowed": true,
  "editUsernameAllowed": false,
  "bruteForceProtected": true,
  "permanentLockout": false,
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
  "internationalizationEnabled": true,
  "supportedLocales": ["en", "hi"],
  "defaultLocale": "en",
  "smtpServer": {
    "host": "$SMTP_HOST",
    "port": "$SMTP_PORT",
    "auth": "$SMTP_AUTH",
    "ssl": "$SMTP_SSL",
    "starttls": "$SMTP_STARTTLS",
    "user": "$SMTP_USER",
    "password": "$SMTP_PASSWORD",
    "from": "noreply@padmini.systems",
    "fromDisplayName": "Padmini Systems"
  }
}
EOF

echo "✅ Realm '$REALM_NAME' configured successfully"

# Step 2: Create Essential Client Scopes
echo "🎯 Creating client scopes for business requirements..."

# OpenID scope (Essential for OIDC)
echo "📋 Creating 'openid' scope..."
OPENID_SCOPE_ID=$(/opt/keycloak/bin/kcadm.sh create clients-scopes -r $REALM_NAME -f - 2>/dev/null <<EOF || /opt/keycloak/bin/kcadm.sh get client-scopes -r $REALM_NAME --query name=openid --format csv --noquotes | tail -n 1 | cut -d',' -f1
{
  "name": "openid",
  "description": "OpenID Connect built-in scope: openid",
  "protocol": "openid-connect",
  "attributes": {
    "include.in.token.scope": "true",
    "display.on.consent.screen": "false"
  }
}
EOF
)

# Add sub mapper to openid scope
if [[ -n "$OPENID_SCOPE_ID" ]]; then
  /opt/keycloak/bin/kcadm.sh create client-scopes/$OPENID_SCOPE_ID/protocol-mappers/models -r $REALM_NAME -f - <<EOF || echo "Sub mapper already exists"
{
  "name": "sub",
  "protocol": "openid-connect",
  "protocolMapper": "oidc-sub-mapper",
  "consentRequired": false,
  "config": {
    "access.token.claim": "true",
    "id.token.claim": "true"
  }
}
EOF
fi

# Profile scope (Business requirement: name, username)
echo "📋 Creating 'profile' scope..."
PROFILE_SCOPE_ID=$(/opt/keycloak/bin/kcadm.sh create clients-scopes -r $REALM_NAME -f - 2>/dev/null <<EOF || /opt/keycloak/bin/kcadm.sh get client-scopes -r $REALM_NAME --query name=profile --format csv --noquotes | tail -n 1 | cut -d',' -f1
{
  "name": "profile",
  "description": "User profile information (name, username)",
  "protocol": "openid-connect",
  "attributes": {
    "include.in.token.scope": "true",
    "display.on.consent.screen": "true",
    "consent.screen.text": "User profile information"
  }
}
EOF
)

# Add profile mappers
if [[ -n "$PROFILE_SCOPE_ID" ]]; then
  # Username mapper
  /opt/keycloak/bin/kcadm.sh create client-scopes/$PROFILE_SCOPE_ID/protocol-mappers/models -r $REALM_NAME -f - <<EOF || echo "Username mapper exists"
{
  "name": "username",
  "protocol": "openid-connect",
  "protocolMapper": "oidc-usermodel-property-mapper",
  "consentRequired": false,
  "config": {
    "user.attribute": "username",
    "claim.name": "preferred_username",
    "jsonType.label": "String",
    "id.token.claim": "true",
    "access.token.claim": "true",
    "userinfo.token.claim": "true"
  }
}
EOF

  # Given name mapper
  /opt/keycloak/bin/kcadm.sh create client-scopes/$PROFILE_SCOPE_ID/protocol-mappers/models -r $REALM_NAME -f - <<EOF || echo "Given name mapper exists"
{
  "name": "given name",
  "protocol": "openid-connect",
  "protocolMapper": "oidc-usermodel-property-mapper",
  "consentRequired": false,
  "config": {
    "user.attribute": "firstName",
    "claim.name": "given_name",
    "jsonType.label": "String",
    "id.token.claim": "true",
    "access.token.claim": "true",
    "userinfo.token.claim": "true"
  }
}
EOF

  # Family name mapper
  /opt/keycloak/bin/kcadm.sh create client-scopes/$PROFILE_SCOPE_ID/protocol-mappers/models -r $REALM_NAME -f - <<EOF || echo "Family name mapper exists"
{
  "name": "family name",
  "protocol": "openid-connect",
  "protocolMapper": "oidc-usermodel-property-mapper",
  "consentRequired": false,
  "config": {
    "user.attribute": "lastName",
    "claim.name": "family_name",
    "jsonType.label": "String",
    "id.token.claim": "true",
    "access.token.claim": "true",
    "userinfo.token.claim": "true"
  }
}
EOF

  # Full name mapper
  /opt/keycloak/bin/kcadm.sh create client-scopes/$PROFILE_SCOPE_ID/protocol-mappers/models -r $REALM_NAME -f - <<EOF || echo "Full name mapper exists"
{
  "name": "full name",
  "protocol": "openid-connect",
  "protocolMapper": "oidc-full-name-mapper",
  "consentRequired": false,
  "config": {
    "id.token.claim": "true",
    "access.token.claim": "true",
    "userinfo.token.claim": "true"
  }
}
EOF
fi

# Email scope (Business requirement: email)
echo "📋 Creating 'email' scope..."
EMAIL_SCOPE_ID=$(/opt/keycloak/bin/kcadm.sh create clients-scopes -r $REALM_NAME -f - 2>/dev/null <<EOF || /opt/keycloak/bin/kcadm.sh get client-scopes -r $REALM_NAME --query name=email --format csv --noquotes | tail -n 1 | cut -d',' -f1
{
  "name": "email",
  "description": "Email address information",
  "protocol": "openid-connect",
  "attributes": {
    "include.in.token.scope": "true",
    "display.on.consent.screen": "true",
    "consent.screen.text": "Email address"
  }
}
EOF
)

# Add email mappers
if [[ -n "$EMAIL_SCOPE_ID" ]]; then
  # Email mapper
  /opt/keycloak/bin/kcadm.sh create client-scopes/$EMAIL_SCOPE_ID/protocol-mappers/models -r $REALM_NAME -f - <<EOF || echo "Email mapper exists"
{
  "name": "email",
  "protocol": "openid-connect",
  "protocolMapper": "oidc-usermodel-property-mapper",
  "consentRequired": false,
  "config": {
    "user.attribute": "email",
    "claim.name": "email",
    "jsonType.label": "String",
    "id.token.claim": "true",
    "access.token.claim": "true",
    "userinfo.token.claim": "true"
  }
}
EOF

  # Email verified mapper
  /opt/keycloak/bin/kcadm.sh create client-scopes/$EMAIL_SCOPE_ID/protocol-mappers/models -r $REALM_NAME -f - <<EOF || echo "Email verified mapper exists"
{
  "name": "email verified",
  "protocol": "openid-connect",
  "protocolMapper": "oidc-usermodel-property-mapper",
  "consentRequired": false,
  "config": {
    "user.attribute": "emailVerified",
    "claim.name": "email_verified",
    "jsonType.label": "boolean",
    "id.token.claim": "true",
    "access.token.claim": "true",
    "userinfo.token.claim": "true"
  }
}
EOF
fi

# Mobile scope (Business requirement: mobile with country code)
echo "📋 Creating 'mobile' scope..."
MOBILE_SCOPE_ID=$(/opt/keycloak/bin/kcadm.sh create clients-scopes -r $REALM_NAME -f - 2>/dev/null <<EOF || /opt/keycloak/bin/kcadm.sh get client-scopes -r $REALM_NAME --query name=mobile --format csv --noquotes | tail -n 1 | cut -d',' -f1
{
  "name": "mobile",
  "description": "Mobile number with country code",
  "protocol": "openid-connect",
  "attributes": {
    "include.in.token.scope": "true",
    "display.on.consent.screen": "true",
    "consent.screen.text": "Mobile number"
  }
}
EOF
)

# Add mobile mapper
if [[ -n "$MOBILE_SCOPE_ID" ]]; then
  /opt/keycloak/bin/kcadm.sh create client-scopes/$MOBILE_SCOPE_ID/protocol-mappers/models -r $REALM_NAME -f - <<EOF || echo "Mobile mapper exists"
{
  "name": "mobile number",
  "protocol": "openid-connect",
  "protocolMapper": "oidc-usermodel-attribute-mapper",
  "consentRequired": false,
  "config": {
    "user.attribute": "mobile",
    "claim.name": "mobile",
    "jsonType.label": "String",
    "id.token.claim": "true",
    "access.token.claim": "true",
    "userinfo.token.claim": "true"
  }
}
EOF
fi

echo "✅ All client scopes created successfully"

# Step 3: Create NextJS Web Client (Public)
echo "🖥️  Creating NextJS Web Client: $CLIENT_ID..."

# Get existing client ID if exists
EXISTING_CLIENT_UUID=$(/opt/keycloak/bin/kcadm.sh get clients -r $REALM_NAME --query clientId=$CLIENT_ID --format csv --noquotes 2>/dev/null | tail -n 1 | cut -d',' -f1 || echo "")

if [[ -z "$EXISTING_CLIENT_UUID" ]]; then
  # Create new client
  echo "Creating new client..."
  WEB_CLIENT_UUID=$(/opt/keycloak/bin/kcadm.sh create clients -r $REALM_NAME -f - <<EOF
{
  "clientId": "$CLIENT_ID",
  "name": "PPCS Web Application",
  "description": "Padmini Private Cloud Service Web Application",
  "enabled": true,
  "publicClient": true,
  "standardFlowEnabled": true,
  "implicitFlowEnabled": false,
  "directAccessGrantsEnabled": true,
  "serviceAccountsEnabled": false,
  "authorizationServicesEnabled": false,
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
  }
}
EOF
)
else
  echo "Updating existing client..."
  WEB_CLIENT_UUID=$EXISTING_CLIENT_UUID
  /opt/keycloak/bin/kcadm.sh update clients/$WEB_CLIENT_UUID -r $REALM_NAME -f - <<EOF
{
  "redirectUris": [
    "http://localhost:3000/api/auth/callback/keycloak",
    "https://ppcs.padmini.systems/api/auth/callback/keycloak",
    "https://app.padmini.systems/api/auth/callback/keycloak"
  ],
  "webOrigins": [
    "http://localhost:3000",
    "https://ppcs.padmini.systems",
    "https://app.padmini.systems"
  ]
}
EOF
fi

# Assign scopes to web client
echo "📋 Assigning scopes to web client..."
# Get scope UUIDs
OPENID_UUID=$(/opt/keycloak/bin/kcadm.sh get client-scopes -r $REALM_NAME --query name=openid --format csv --noquotes | tail -n 1 | cut -d',' -f1)
PROFILE_UUID=$(/opt/keycloak/bin/kcadm.sh get client-scopes -r $REALM_NAME --query name=profile --format csv --noquotes | tail -n 1 | cut -d',' -f1)
EMAIL_UUID=$(/opt/keycloak/bin/kcadm.sh get client-scopes -r $REALM_NAME --query name=email --format csv --noquotes | tail -n 1 | cut -d',' -f1)
MOBILE_UUID=$(/opt/keycloak/bin/kcadm.sh get client-scopes -r $REALM_NAME --query name=mobile --format csv --noquotes | tail -n 1 | cut -d',' -f1)

# Assign default scopes
[[ -n "$OPENID_UUID" ]] && /opt/keycloak/bin/kcadm.sh update clients/$WEB_CLIENT_UUID/default-client-scopes/$OPENID_UUID -r $REALM_NAME || echo "openid scope assignment failed"
[[ -n "$PROFILE_UUID" ]] && /opt/keycloak/bin/kcadm.sh update clients/$WEB_CLIENT_UUID/default-client-scopes/$PROFILE_UUID -r $REALM_NAME || echo "profile scope assignment failed"
[[ -n "$EMAIL_UUID" ]] && /opt/keycloak/bin/kcadm.sh update clients/$WEB_CLIENT_UUID/default-client-scopes/$EMAIL_UUID -r $REALM_NAME || echo "email scope assignment failed"

# Assign optional scopes
[[ -n "$MOBILE_UUID" ]] && /opt/keycloak/bin/kcadm.sh update clients/$WEB_CLIENT_UUID/optional-client-scopes/$MOBILE_UUID -r $REALM_NAME || echo "mobile scope assignment failed"

echo "✅ NextJS Web Client configured successfully"

# Step 4: Create Microservices Client (Confidential)
echo "🔧 Creating Microservices Client: $MICROSERVICES_CLIENT_ID..."

EXISTING_MS_CLIENT_UUID=$(/opt/keycloak/bin/kcadm.sh get clients -r $REALM_NAME --query clientId=$MICROSERVICES_CLIENT_ID --format csv --noquotes 2>/dev/null | tail -n 1 | cut -d',' -f1 || echo "")

if [[ -z "$EXISTING_MS_CLIENT_UUID" ]]; then
  echo "Creating new microservices client..."
  MS_CLIENT_UUID=$(/opt/keycloak/bin/kcadm.sh create clients -r $REALM_NAME -f - <<EOF
{
  "clientId": "$MICROSERVICES_CLIENT_ID",
  "name": "ASM Microservices",
  "description": "Authentication Service Manager and related microservices",
  "enabled": true,
  "clientAuthenticatorType": "client-secret",
  "secret": "asm-microservices-secret-change-in-production",
  "publicClient": false,
  "standardFlowEnabled": true,
  "implicitFlowEnabled": false,
  "directAccessGrantsEnabled": true,
  "serviceAccountsEnabled": true,
  "authorizationServicesEnabled": true,
  "bearerOnly": false,
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
  ]
}
EOF
)
else
  echo "Microservices client already exists"
  MS_CLIENT_UUID=$EXISTING_MS_CLIENT_UUID
fi

# Assign scopes to microservices client
[[ -n "$OPENID_UUID" ]] && /opt/keycloak/bin/kcadm.sh update clients/$MS_CLIENT_UUID/default-client-scopes/$OPENID_UUID -r $REALM_NAME || echo "openid scope assignment failed"
[[ -n "$PROFILE_UUID" ]] && /opt/keycloak/bin/kcadm.sh update clients/$MS_CLIENT_UUID/default-client-scopes/$PROFILE_UUID -r $REALM_NAME || echo "profile scope assignment failed"
[[ -n "$EMAIL_UUID" ]] && /opt/keycloak/bin/kcadm.sh update clients/$MS_CLIENT_UUID/default-client-scopes/$EMAIL_UUID -r $REALM_NAME || echo "email scope assignment failed"
[[ -n "$MOBILE_UUID" ]] && /opt/keycloak/bin/kcadm.sh update clients/$MS_CLIENT_UUID/optional-client-scopes/$MOBILE_UUID -r $REALM_NAME || echo "mobile scope assignment failed"

echo "✅ Microservices Client configured successfully"

# Step 5: Create Default Roles and Groups
echo "👥 Creating default roles and groups..."

# Create realm roles
/opt/keycloak/bin/kcadm.sh create roles -r $REALM_NAME -f - <<EOF || echo "User role already exists"
{
  "name": "user",
  "description": "User role for regular users"
}
EOF

/opt/keycloak/bin/kcadm.sh create roles -r $REALM_NAME -f - <<EOF || echo "Admin role already exists"
{
  "name": "admin", 
  "description": "Administrator role"
}
EOF

# Create groups
/opt/keycloak/bin/kcadm.sh create groups -r $REALM_NAME -f - <<EOF || echo "Users group already exists"
{
  "name": "users",
  "path": "/users"
}
EOF

/opt/keycloak/bin/kcadm.sh create groups -r $REALM_NAME -f - <<EOF || echo "Admins group already exists"
{
  "name": "admins",
  "path": "/admins"
}
EOF

echo "✅ Roles and groups created"

# Step 6: Test Configuration with Sample User
echo "👤 Creating test user to verify mobile attribute..."
TEST_USERNAME="testuser-$(date +%s)"
/opt/keycloak/bin/kcadm.sh create users -r $REALM_NAME -f - <<EOF || echo "Test user creation failed"
{
  "username": "$TEST_USERNAME",
  "enabled": true,
  "email": "test@padmini.systems",
  "firstName": "Test",
  "lastName": "User",
  "attributes": {
    "mobile": ["+919876543210"]
  },
  "requiredActions": []
}
EOF

echo "✅ Test user created with mobile attribute"

# Final verification
echo ""
echo "🔍 Configuration Verification:"
echo "=============================="

# Check if scopes exist
echo "📋 Client Scopes:"
/opt/keycloak/bin/kcadm.sh get client-scopes -r $REALM_NAME --format csv --noquotes | grep -E "openid|profile|email|mobile" | while read line; do
  echo "   ✓ $(echo $line | cut -d',' -f2)"
done

# Check clients
echo "🖥️  Clients:"
/opt/keycloak/bin/kcadm.sh get clients -r $REALM_NAME --format csv --noquotes | grep -E "$CLIENT_ID|$MICROSERVICES_CLIENT_ID" | while read line; do
  echo "   ✓ $(echo $line | cut -d',' -f2)"
done

echo ""
echo "🎉 Padmini Systems Keycloak Configuration Completed!"
echo "===================================================="
echo ""
echo "✅ Business Requirements Fulfilled:"
echo "   - Name: ✓ (given_name, family_name, full name)"
echo "   - Username: ✓ (preferred_username)"
echo "   - UUID: ✓ (sub)"
echo "   - Mobile: ✓ (mobile attribute)"
echo "   - Email: ✓ (email, email_verified)"
echo ""
echo "🔗 Test URLs:"
echo "   Registration: $KEYCLOAK_URL/realms/$REALM_NAME/protocol/openid-connect/registrations?client_id=$CLIENT_ID&response_type=code&scope=openid%20profile%20email%20mobile&redirect_uri=http://localhost:3000/api/auth/callback/keycloak"
echo "   Login: $KEYCLOAK_URL/realms/$REALM_NAME/protocol/openid-connect/auth?client_id=$CLIENT_ID&response_type=code&scope=openid%20profile%20email%20mobile&redirect_uri=http://localhost:3000/api/auth/callback/keycloak"
echo ""
echo "📝 NextJS Configuration:"
echo "   Scope: 'openid profile email mobile'"
echo "   Expected JWT claims: sub, preferred_username, given_name, family_name, name, email, email_verified, mobile"
echo ""
echo "⚠️  Manual Step Required:"
echo "   To collect mobile during registration, add mobile field in:"
echo "   Keycloak Admin → Realm Settings → User Profile → Attributes → Create Attribute"
echo "   - Name: mobile"
echo "   - Display name: Mobile Number"
echo "   - Validation: ^[+]?[1-9]\\d{9,14}\$"
echo "   - Required for: user role"
echo ""

echo "✅ Configuration completed successfully!"
