#!/bin/bash

# Verify NextJS Keycloak Configuration Script
# This script helps verify that the Keycloak realm is properly configured for NextJS integration

set -e

REALM_NAME="padmini-systems"
CLIENT_ID="ppcs-web-app"
KEYCLOAK_URL="https://iam.padmini.systems"

echo "🔍 Verifying Keycloak Configuration for NextJS Integration..."
echo "=================================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if curl is available
if ! command_exists curl; then
    echo "❌ curl is required but not installed. Please install curl."
    exit 1
fi

# Check if jq is available
if ! command_exists jq; then
    echo "⚠️  jq is not installed. JSON responses will not be formatted."
    JQ_AVAILABLE=false
else
    JQ_AVAILABLE=true
fi

echo "🌐 Checking Keycloak server accessibility..."
if curl -s -f "$KEYCLOAK_URL/realms/$REALM_NAME/.well-known/openid_configuration" > /dev/null; then
    echo "✅ Keycloak server is accessible"
else
    echo "❌ Keycloak server is not accessible at $KEYCLOAK_URL"
    exit 1
fi

echo ""
echo "🔑 Fetching OpenID Connect configuration..."
OIDC_CONFIG=$(curl -s "$KEYCLOAK_URL/realms/$REALM_NAME/.well-known/openid_configuration")

if [ "$JQ_AVAILABLE" = true ]; then
    echo "📋 Available endpoints:"
    echo "   Authorization: $(echo "$OIDC_CONFIG" | jq -r '.authorization_endpoint')"
    echo "   Token: $(echo "$OIDC_CONFIG" | jq -r '.token_endpoint')"
    echo "   UserInfo: $(echo "$OIDC_CONFIG" | jq -r '.userinfo_endpoint')"
    echo "   End Session: $(echo "$OIDC_CONFIG" | jq -r '.end_session_endpoint')"
    
    echo ""
    echo "🎯 Supported scopes:"
    echo "$OIDC_CONFIG" | jq -r '.scopes_supported[]' | while read scope; do
        echo "   ✓ $scope"
    done
    
    echo ""
    echo "🎫 Supported response types:"
    echo "$OIDC_CONFIG" | jq -r '.response_types_supported[]' | while read type; do
        echo "   ✓ $type"
    done
else
    echo "✅ OpenID Connect configuration retrieved successfully"
fi

echo ""
echo "📝 NextJS Environment Variables Template:"
echo "=================================================="
echo "# Add these to your NextJS .env.local file:"
echo ""
echo "NEXTAUTH_URL=http://localhost:3000"
echo "NEXTAUTH_SECRET=your-nextauth-secret-here"
echo ""
echo "KEYCLOAK_ISSUER=$KEYCLOAK_URL/realms/$REALM_NAME"
echo "KEYCLOAK_CLIENT_ID=$CLIENT_ID"
echo "KEYCLOAK_CLIENT_SECRET=  # Leave empty for public client"
echo ""

echo "🔧 Required Keycloak Admin Console Verification:"
echo "=================================================="
echo "Please manually verify these settings in Keycloak Admin Console:"
echo ""
echo "1. Navigate to: $KEYCLOAK_URL/admin"
echo "2. Go to: Realms → $REALM_NAME → Clients → $CLIENT_ID"
echo ""
echo "3. Verify Settings Tab:"
echo "   ✓ Client authentication: OFF"
echo "   ✓ Standard flow enabled: ON"
echo "   ✓ Valid redirect URIs includes: http://localhost:3000/api/auth/callback/keycloak"
echo "   ✓ Web origins includes: http://localhost:3000"
echo ""
echo "4. Verify Client Scopes Tab:"
echo "   ✓ Default Client Scopes should include:"
echo "     - openid"
echo "     - profile"
echo "     - email"
echo "     - web-origins"
echo ""
echo "5. Test the configuration:"
echo "   ✓ Try accessing: $KEYCLOAK_URL/realms/$REALM_NAME/protocol/openid-connect/auth?client_id=$CLIENT_ID&response_type=code&scope=openid%20profile%20email&redirect_uri=http://localhost:3000/api/auth/callback/keycloak"
echo ""

echo "✅ Configuration verification complete!"
echo ""
echo "Next steps:"
echo "1. Apply the updated realm configuration"
echo "2. Verify settings in Keycloak Admin Console"
echo "3. Configure your NextJS application with the environment variables above"
echo "4. Test the authentication flow"
