# Manual Secret Setup Guide

This guide explains the **3 secrets** that need to be created manually before the automated deployment.

## 🔐 **Secret 1: PostgreSQL Database Secret**

**Purpose**: Database credentials for Keycloak backend

```bash
# Create PostgreSQL namespace
kubectl create namespace postgresql

# Create PostgreSQL secret
kubectl create secret generic postgresql-secret \
  --from-literal=username=postgres \
  --from-literal=password=your-secure-db-password \
  --from-literal=database=keycloak \
  -n postgresql
```

**Verification**:
```bash
kubectl get secret postgresql-secret -n postgresql
```

---

## 📧 **Secret 2: SMTP Configuration Secret**

**Purpose**: Email functionality for user verification and notifications

### **Option A: Use Setup Script (Recommended)**
```bash
# Edit the script with your SMTP credentials
nano scripts/setup-smtp.sh

# Set your SMTP credentials in the script:
SMTP_USER="your-email@gmail.com"
SMTP_PASSWORD="your-app-password"

# Run the script
chmod +x scripts/setup-smtp.sh
./scripts/setup-smtp.sh
```

### **Option B: Manual Creation**
```bash
# Create Keycloak namespace
kubectl create namespace keycloak

# Create SMTP secret manually
kubectl create secret generic padmini-keycloak-smtp \
  --from-literal=SMTP_HOST="smtp.gmail.com" \
  --from-literal=SMTP_PORT="587" \
  --from-literal=SMTP_USER="your-email@gmail.com" \
  --from-literal=SMTP_PASSWORD="your-app-password" \
  --from-literal=SMTP_FROM="noreply@padmini.systems" \
  --from-literal=SMTP_FROM_DISPLAY_NAME="Padmini Systems" \
  -n keycloak
```

**Verification**:
```bash
kubectl get secret padmini-keycloak-smtp -n keycloak
```

---

## 👤 **Secret 3: Keycloak Admin Secret (Create AFTER Steps 1-6)**

**Purpose**: Admin API access for configuration job

⚠️ **IMPORTANT**: Create this secret **ONLY AFTER**:
1. Keycloak instance is deployed and running
2. HTTPS is configured for iam.padmini.systems
3. You've accessed admin console and created permanent admin user

```bash
# Create admin secret for configuration job
kubectl create secret generic padmini-keycloak-admin \
  --from-literal=KEYCLOAK_ADMIN_USERNAME=ramanuj \
  --from-literal=KEYCLOAK_ADMIN_PASSWORD='rbd@6321P' \
  -n keycloak
```

**Verification**:
```bash
kubectl get secret padmini-keycloak-admin -n keycloak
```

---

## 🔍 **Verify All Secrets**

```bash
# Check all secrets are ready
echo "Checking PostgreSQL secret..."
kubectl get secret postgresql-secret -n postgresql

echo "Checking SMTP secret..."
kubectl get secret padmini-keycloak-smtp -n keycloak

echo "Checking Admin secret (create after step 6)..."
kubectl get secret padmini-keycloak-admin -n keycloak || echo "Admin secret not created yet (normal for initial deployment)"
```

---

## 📝 **Secret Summary**

| Secret | Namespace | When to Create | Purpose |
|--------|-----------|----------------|---------|
| `postgresql-secret` | `postgresql` | **Before Step 1** | Database credentials |
| `padmini-keycloak-smtp` | `keycloak` | **Before Step 1** | Email configuration |
| `padmini-keycloak-admin` | `keycloak` | **After Step 6** | Admin API access |

✅ Once secrets 1 & 2 are created, you can proceed with the GitHub Actions deployment!
