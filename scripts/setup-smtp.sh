#!/bin/bash

# SMTP Secret Creation Script for Keycloak
# This script helps create the SMTP secret without exposing credentials in git

set -e

NAMESPACE="keycloak"
SECRET_NAME="keycloak-smtp-secret"

echo "🔧 Keycloak SMTP Secret Setup"
echo "============================="
echo ""
echo "This script will create a Kubernetes secret with your SMTP configuration."
echo "The secret will NOT be stored in git - only applied to your cluster."
echo ""

# Check if secret already exists
if kubectl get secret $SECRET_NAME -n $NAMESPACE >/dev/null 2>&1; then
    echo "⚠️  Secret '$SECRET_NAME' already exists in namespace '$NAMESPACE'"
    read -p "Do you want to update it? (y/N): " confirm
    if [[ $confirm != [yY] ]]; then
        echo "Exiting..."
        exit 0
    fi
    echo ""
fi

echo "📧 Please provide your SMTP configuration:"
echo ""

# Prompt for SMTP configuration
read -p "SMTP Host (e.g., smtp.gmail.com): " smtp_host
read -p "SMTP Port (587 for TLS, 465 for SSL): " smtp_port
read -p "SMTP Username/Email: " smtp_user
read -s -p "SMTP Password (will be hidden): " smtp_password
echo ""

# Determine SSL/STARTTLS based on port
if [ "$smtp_port" = "465" ]; then
    smtp_ssl="true"
    smtp_starttls="false"
    smtp_auth="true"
elif [ "$smtp_port" = "587" ]; then
    smtp_ssl="false"
    smtp_starttls="true"
    smtp_auth="true"
else
    echo ""
    read -p "Use SSL? (y/N): " ssl_confirm
    smtp_ssl=$([ "$ssl_confirm" = "y" ] && echo "true" || echo "false")

    read -p "Use STARTTLS? (Y/n): " starttls_confirm
    smtp_starttls=$([ "$starttls_confirm" != "n" ] && echo "true" || echo "false")

    smtp_auth="true"
fi

echo ""
echo "📋 Configuration Summary:"
echo "  Host: $smtp_host"
echo "  Port: $smtp_port"
echo "  Username: $smtp_user"
echo "  Password: [HIDDEN]"
echo "  SSL: $smtp_ssl"
echo "  STARTTLS: $smtp_starttls"
echo "  Auth: $smtp_auth"
echo ""

read -p "Create secret with this configuration? (Y/n): " confirm
if [[ $confirm == [nN] ]]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "🚀 Creating SMTP secret..."

# Create or update the secret
kubectl create secret generic $SECRET_NAME \
    --namespace=$NAMESPACE \
    --from-literal=host="$smtp_host" \
    --from-literal=port="$smtp_port" \
    --from-literal=auth="$smtp_auth" \
    --from-literal=ssl="$smtp_ssl" \
    --from-literal=starttls="$smtp_starttls" \
    --from-literal=user="$smtp_user" \
    --from-literal=password="$smtp_password" \
    --dry-run=client -o yaml | kubectl apply -f -

# Add labels to the secret
kubectl label secret $SECRET_NAME -n $NAMESPACE \
    app.kubernetes.io/name=keycloak-smtp \
    app.kubernetes.io/part-of=keycloak \
    app.kubernetes.io/component=smtp-config \
    --overwrite

echo ""
echo "✅ SMTP secret created successfully!"
echo ""
echo "🔍 You can verify the secret with:"
echo "   kubectl get secret $SECRET_NAME -n $NAMESPACE"
echo "   kubectl describe secret $SECRET_NAME -n $NAMESPACE"
echo ""
echo "⚠️  Security Note:"
echo "   - The secret is now stored in your Kubernetes cluster"
echo "   - It will NOT be committed to git"
echo "   - Make sure to backup your cluster secrets securely"
echo ""

# Test SMTP configuration (optional)
read -p "Would you like to test the SMTP configuration? (y/N): " test_confirm
if [[ $test_confirm == [yY] ]]; then
    echo ""
    echo "🧪 Testing SMTP configuration..."
    # The "From" address here is cosmetic for the email body. 
    # Gmail will use the authenticated user's address regardless.
    from_email="khushisoftwareindia@gmail.com" 
    echo "This will send a test email from your authenticated user ($smtp_user)."
    read -p "Send test email to: " test_email

    # Determine the correct protocol scheme based on the port
    if [ "$smtp_port" = "465" ]; then
        protocol_scheme="smtps"
    else
        # For port 587 and others, use standard smtp which will upgrade to STARTTLS
        protocol_scheme="smtp"
    fi
    
    # Create a temporary test pod
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: smtp-test
  namespace: $NAMESPACE
spec:
  containers:
  - name: smtp-test
    image: alpine:latest
    command: ["sleep", "3600"]
    env:
    - name: SMTP_HOST
      valueFrom:
        secretKeyRef:
          name: $SECRET_NAME
          key: host
    - name: SMTP_PORT
      valueFrom:
        secretKeyRef:
          name: $SECRET_NAME
          key: port
    - name: SMTP_USER
      valueFrom:
        secretKeyRef:
          name: $SECRET_NAME
          key: user
    - name: SMTP_PASSWORD
      valueFrom:
        secretKeyRef:
          name: $SECRET_NAME
          key: password
  restartPolicy: Never
EOF

    # Wait for pod to be ready
    echo "Waiting for test pod to become ready..."
    kubectl wait --for=condition=Ready pod/smtp-test -n $NAMESPACE --timeout=90s
    
    # Install curl and test SMTP
    echo "Pod is ready. Attempting to send test email..."
    kubectl exec -n $NAMESPACE smtp-test -- sh -c "
        apk add --no-cache curl && 
        curl -v --ssl-reqd \
        --mail-from '$smtp_user' \
        --mail-rcpt '$test_email' \
        --upload-file - \
        \"$protocol_scheme://\$SMTP_HOST:\$SMTP_PORT\" \
        --user \"\$SMTP_USER:\$SMTP_PASSWORD\" \
        <<EOF
From: $from_email
To: $test_email
Subject: Keycloak SMTP Test

This is a test email from Padmini Systems Keycloak setup.

If you received this email, your SMTP configuration is working correctly!

--
Padmini Systems
EOF
    "
    
    # Cleanup test pod
    echo "Cleaning up test pod..."
    kubectl delete pod smtp-test -n $NAMESPACE --ignore-not-found
    
    echo ""
    echo "📨 Test email command executed! Check your inbox at: $test_email"
fi

echo ""
echo "🎉 SMTP setup completed!"
echo ""
echo "Next steps:"
echo "1. Apply your realm configuration: kubectl apply -f keycloak/realms/padmini-realm-import.yaml"
echo "2. Test user registration with email verification"