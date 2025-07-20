# Padmini Systems Keycloak Configuration

## 🎯 Enterprise-Grade Python Solution

This directory contains a **complete enterprise-grade Python solution** for configuring Keycloak to meet Padmini Systems business requirements:

### ✅ Business Requirements Fulfilled
- **JWT Claims**: `name`, `username` (`preferred_username`), `uuid` (`sub`), `mobile`, `email`
- **Mobile Collection**: User profile configured for mobile number registration
- **NextJS Integration**: Scope `openid profile email mobile` ready
- **Microservices Support**: ASM client with service account capabilities

## 🏗️ Architecture

```
python-executor/
├── main.py                    # 🎯 Main orchestrator
├── requirements.txt           # 📦 Dependencies
├── config/
│   ├── environment.py         # 🔐 K8s secrets integration
│   └── constants.py          # ⚙️  All configurations
├── utils/
│   ├── logger.py             # 📝 Enhanced logging
│   └── keycloak_client.py    # 🌐 REST API client
└── actions/
    ├── base_manager.py       # 🏗️  Abstract base
    ├── realm_manager.py      # 🏛️  Realm operations
    ├── client_scope_manager.py # 🔑 OIDC scopes
    ├── user_profile_manager.py # 👤 Roles & groups
    ├── ppcs_client/
    │   └── ppcs_client_manager.py # 🖥️  NextJS client
    └── asm_client/
        └── asm_client_manager.py  # ⚙️  Microservices
```

## 🚀 Deployment

### Prerequisites
1. **Keycloak** running with Admin API accessible
2. **Kubernetes secrets** configured:
   - `padmini-keycloak-admin` (KEYCLOAK_ADMIN_USERNAME, KEYCLOAK_ADMIN_PASSWORD)
   - `padmini-keycloak-smtp` (SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD)

### Deploy with ArgoCD
```bash
kubectl apply -f /path/to/argocd-apps/keycloak-admin-config-app.yaml
```

### Manual Deployment
```bash
kubectl apply -f keycloak-python-config-job.yaml
```

### Monitor Execution
```bash
kubectl logs -n keycloak job/keycloak-python-config-job -f
```

## 🔧 Configuration Actions

The solution supports multiple actions via environment variable:

- `ACTION=create` - Create complete Keycloak configuration
- `ACTION=destroy` - Rollback/destroy configuration
- `ACTION=validate` - Validate existing configuration

## 🎉 NextJS Integration

Ready-to-use NextAuth.js configuration:

```javascript
providers: [
  {
    id: "keycloak",
    name: "Keycloak",
    type: "oauth",
    wellKnown: `${KEYCLOAK_URL}/realms/padmini-systems/.well-known/openid_configuration`,
    authorization: { params: { scope: "openid profile email mobile" } },
    clientId: "ppcs-client",
    clientSecret: process.env.KEYCLOAK_CLIENT_SECRET,
    profile(profile) {
      return {
        id: profile.sub,           // UUID
        name: profile.name,        // Full name
        username: profile.preferred_username,
        email: profile.email,
        mobile: profile.mobile,    // Mobile with country code
        emailVerified: profile.email_verified
      }
    }
  }
]
```

## 🏆 Enterprise Standards

- ✅ **Maintainable**: Each operation in separate files
- ✅ **Debuggable**: Comprehensive logging and error handling  
- ✅ **Robust**: Idempotent operations with validation
- ✅ **Scalable**: Modular design for easy extension
- ✅ **Production-ready**: Proper Kubernetes integration
- ✅ **Rollback capable**: Complete destroy operations

## 🔍 Troubleshooting

### View Job Status
```bash
kubectl get jobs -n keycloak
kubectl describe job keycloak-python-config-job -n keycloak
```

### View Logs
```bash
kubectl logs -n keycloak job/keycloak-python-config-job
```

### Force Rollback
```bash
# Edit job environment to set ACTION=destroy
kubectl patch job keycloak-python-config-job -n keycloak -p '{"spec":{"template":{"spec":{"containers":[{"name":"keycloak-python-config","env":[{"name":"ACTION","value":"destroy"}]}]}}}}'
```

---

**Note**: This replaces the previous shell script approach with a proper enterprise-grade Python solution that follows best practices for maintainability, debugging, and production deployment.
