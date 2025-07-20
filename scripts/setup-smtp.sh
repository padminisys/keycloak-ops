#!/bin/bash

# Setup SMTP Configuration for Keycloak
# This script creates the necessary Kubernetes secret for SMTP configuration

set -e

echo "🔧 Setting up SMTP configuration for Keycloak..."

# SMTP Configuration Variables
SMTP_HOST="smtp.gmail.com"
SMTP_PORT="587"
SMTP_USER=""  # Set your SMTP username
SMTP_PASSWORD=""  # Set your SMTP password/app password
SMTP_FROM="noreply@padmini.systems"
SMTP_FROM_DISPLAY_NAME="Padmini Systems"

# Check if variables are set
if [ -z "$SMTP_USER" ] || [ -z "$SMTP_PASSWORD" ]; then
    echo "❌ Error: SMTP_USER and SMTP_PASSWORD must be set in the script"
    echo "   Please edit this script and set the SMTP credentials"
    exit 1
fi

# Create namespace if it doesn't exist
kubectl create namespace keycloak --dry-run=client -o yaml | kubectl apply -f -

# Create SMTP secret
kubectl create secret generic padmini-keycloak-smtp \
    --from-literal=SMTP_HOST="$SMTP_HOST" \
    --from-literal=SMTP_PORT="$SMTP_PORT" \
    --from-literal=SMTP_USER="$SMTP_USER" \
    --from-literal=SMTP_PASSWORD="$SMTP_PASSWORD" \
    --from-literal=SMTP_FROM="$SMTP_FROM" \
    --from-literal=SMTP_FROM_DISPLAY_NAME="$SMTP_FROM_DISPLAY_NAME" \
    --namespace=keycloak \
    --dry-run=client -o yaml | kubectl apply -f -

echo "✅ SMTP secret created successfully!"

# Verify secret creation
echo "📋 Verifying secret..."
kubectl get secret padmini-keycloak-smtp -n keycloak

echo ""
echo "🔑 SMTP Configuration Summary:"
echo "   Host: $SMTP_HOST"
echo "   Port: $SMTP_PORT"
echo "   From: $SMTP_FROM"
echo "   Display Name: $SMTP_FROM_DISPLAY_NAME"
echo ""
echo "📝 Note: Make sure your SMTP credentials are correct and app passwords are used for Gmail"