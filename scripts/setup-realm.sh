#!/bin/bash

# Padmini Systems Keycloak Setup Script
# This script helps deploy and verify the Keycloak realm configuration

set -e

NAMESPACE="keycloak"
REALM_NAME="padmini-systems"

echo "🚀 Deploying Padmini Systems Keycloak Realm Configuration"
echo "==========================================================="

# Check if Keycloak operator is running
echo "📋 Checking Keycloak operator status..."
if ! kubectl get deployment keycloak-operator -n $NAMESPACE >/dev/null 2>&1; then
    echo "❌ Keycloak operator not found in namespace $NAMESPACE"
    echo "Please ensure Keycloak operator is deployed first"
    exit 1
fi
echo "✅ Keycloak operator is running"

# Check if Keycloak instance is running
echo "📋 Checking Keycloak instance status..."
if ! kubectl get keycloak padmini-keycloak -n $NAMESPACE >/dev/null 2>&1; then
    echo "❌ Keycloak instance 'padmini-keycloak' not found in namespace $NAMESPACE"
    echo "Please ensure Keycloak instance is deployed first"
    exit 1
fi

# Wait for Keycloak to be ready
echo "⏳ Waiting for Keycloak instance to be ready..."
kubectl wait --for=condition=Ready keycloak/padmini-keycloak -n $NAMESPACE --timeout=300s
echo "✅ Keycloak instance is ready"

# Apply the realm configuration
echo "📋 Applying realm configuration..."
kubectl apply -f keycloak/realms/padmini-realm-import.yaml

# Wait for realm import to complete
echo "⏳ Waiting for realm import to complete..."
sleep 10

# Check realm import status
echo "📋 Checking realm import status..."
REALM_STATUS=$(kubectl get keycloakrealmimport padmini-realm-import -n $NAMESPACE -o jsonpath='{.status.condition}' 2>/dev/null || echo "NotFound")

if [ "$REALM_STATUS" = "NotFound" ]; then
    echo "❌ Realm import not found"
    exit 1
fi

# Display realm import details
echo "📋 Realm import status:"
kubectl describe keycloakrealmimport padmini-realm-import -n $NAMESPACE

# Get Keycloak URL
KEYCLOAK_URL=$(kubectl get keycloak padmini-keycloak -n $NAMESPACE -o jsonpath='{.status.instances[0].status.externalURL}' 2>/dev/null || echo "Not available")

echo ""
echo "🎉 Deployment Summary"
echo "===================="
echo "✅ Realm Name: $REALM_NAME"
echo "✅ Namespace: $NAMESPACE"
echo "✅ Keycloak URL: $KEYCLOAK_URL"
echo ""
echo "📋 Clients Created:"
echo "   - ppcs-web-app (Public client for Next.js)"
echo "   - asm-microservices (Confidential client for Quarkus)"
echo ""
echo "🔧 Next Steps:"
echo "1. Access Keycloak Admin Console: $KEYCLOAK_URL"
echo "2. Configure SMTP: Run './scripts/setup-smtp.sh' for secure email setup"
echo "3. Change the client secret for 'asm-microservices'"
echo "4. Test user registration and login flow"
echo ""
echo "📖 For detailed integration instructions, see:"
echo "   keycloak/realms/README.md"

# Test realm accessibility
if [ "$KEYCLOAK_URL" != "Not available" ]; then
    echo ""
    echo "🧪 Testing realm accessibility..."
    REALM_URL="$KEYCLOAK_URL/realms/$REALM_NAME/.well-known/openid_configuration"
    if curl -s "$REALM_URL" >/dev/null; then
        echo "✅ Realm is accessible at: $REALM_URL"
    else
        echo "⚠️  Realm may not be fully accessible yet. Please wait a few minutes."
    fi
fi

echo ""
echo "✅ Setup completed successfully!"
