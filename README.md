# Padmini Systems - Keycloak Operations

Complete Keycloak setup for Padmini Private Cloud Service (PPCS) using GitOps with ArgoCD.

## 🎯 Business Requirements

This configuration provides authentication for:
- **NextJS Web Application** (ppcs-web-app)
- **Quarkus Microservices** (asm-microservices)

### Required User Data in JWT:
- ✅ **Name**: Full name (given_name, family_name, name)
- ✅ **Username**: Login identifier (preferred_username)  
- ✅ **UUID**: User ID (sub)
- ✅ **Mobile**: Mobile number with country code (mobile)
- ✅ **Email**: Email address (email, email_verified)

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   ArgoCD        │───▶│   Keycloak       │───▶│   Applications  │
│   GitOps        │    │   Admin API      │    │   - NextJS      │
│                 │    │   Configuration  │    │   - Microservices│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Components:
- **Keycloak Operator**: Manages Keycloak instance lifecycle
- **PostgreSQL**: Database backend for Keycloak
- **Admin API Job**: Configures realm, clients, and scopes
- **SMTP Integration**: Email verification and notifications
- **ArgoCD**: GitOps deployment and management

## 📁 Project Structure

```
keycloak-ops/
├── argocd-apps/                    # ArgoCD Application definitions
│   ├── keycloak-operator-app.yaml  # Keycloak Operator deployment
│   ├── keycloak-admin-config-app.yaml # Realm configuration job
│   ├── postgresql-app.yaml         # Database deployment
│   └── certificates-app.yaml       # TLS certificates
├── keycloak/
│   ├── instances/                  # Keycloak instance configuration
│   │   └── production-keycloak.yaml
│   └── admin-api-config/          # Complete realm configuration
│       ├── configure-keycloak.sh   # Configuration script
│       ├── keycloak-config-script.yaml # ConfigMap
│       ├── keycloak-config-job.yaml    # Kubernetes Job
│       └── kustomization.yaml
├── keycloak-operator/             # Operator deployment
│   └── kustomization.yaml
├── postgresql/                    # Database configuration
│   └── values.yaml
├── certificates/                  # TLS certificate management
│   └── certificate.yaml
├── docs/                         # Documentation
│   ├── nextjs-integration-guide.md
│   └── quarkus-integration-guide.md
├── scripts/                      # Utility scripts
│   └── setup-smtp.sh
└── runbooks/                     # Manual operations
    ├── manual-secret/
    └── manual-ingress/
```

## 🚀 Deployment

### Prerequisites
- Kubernetes cluster
- ArgoCD installed
- Domain: `iam.padmini.systems`

### 1. Deploy ArgoCD Applications
```bash
# Deploy Keycloak Operator
kubectl apply -f argocd-apps/keycloak-operator-app.yaml

# Deploy PostgreSQL
kubectl apply -f argocd-apps/postgresql-app.yaml

# Deploy TLS Certificates  
kubectl apply -f argocd-apps/certificates-app.yaml

# Deploy Keycloak Instance
kubectl apply -f argocd-apps/keycloak-instance-app.yaml

# Deploy Realm Configuration
kubectl apply -f argocd-apps/keycloak-admin-config-app.yaml
```

### 2. Setup Secrets
```bash
# SMTP Configuration
./scripts/setup-smtp.sh

# Admin Credentials (already created)
kubectl create secret generic padmini-keycloak-admin \
  --from-literal=KEYCLOAK_ADMIN_USERNAME=ramanuj \
  --from-literal=KEYCLOAK_ADMIN_PASSWORD='rbd@6321P' \
  -n keycloak
```

### 3. Verify Deployment
```bash
# Check ArgoCD applications
kubectl get applications -n argocd

# Check Keycloak pods
kubectl get pods -n keycloak

# Check configuration job
kubectl logs job/keycloak-admin-config-job -n keycloak
```

## 🔧 Configuration Details

### Realm: `padmini-systems`
- **Display Name**: Padmini Systems
- **Registration**: Enabled with email verification
- **Themes**: Keycloak default with custom branding
- **Security**: Brute force protection, SSL required

### Clients
1. **ppcs-web-app** (Public Client)
   - NextJS web application
   - Redirect URIs: `http://localhost:3000/api/auth/callback/keycloak`
   - Scopes: `openid profile email mobile`

2. **asm-microservices** (Confidential Client)  
   - Quarkus microservices
   - Service account enabled
   - Authorization services enabled

### Client Scopes & JWT Claims
```json
{
  "sub": "user-uuid",
  "preferred_username": "username", 
  "given_name": "First",
  "family_name": "Last",
  "name": "First Last",
  "email": "user@domain.com",
  "email_verified": true,
  "mobile": "+919876543210"
}
```

## 🔗 Integration Guides

- [NextJS Integration](docs/nextjs-integration-guide.md)
- [Quarkus Integration](docs/quarkus-integration-guide.md)

## 🔍 Testing URLs

### User Registration
```
https://iam.padmini.systems/realms/padmini-systems/protocol/openid-connect/registrations?client_id=ppcs-web-app&response_type=code&scope=openid%20profile%20email%20mobile&redirect_uri=http://localhost:3000/api/auth/callback/keycloak
```

### Admin Console
```
https://iam.padmini.systems/admin
```

### OIDC Discovery
```
https://iam.padmini.systems/realms/padmini-systems/.well-known/openid_configuration
```

## ⚠️ Manual Configuration Required

After deployment, add mobile field to user registration:

1. **Keycloak Admin Console** → **Realm Settings** → **User Profile** → **Attributes**
2. **Create Attribute**:
   - Name: `mobile`
   - Display name: `Mobile Number`
   - Validation: `^[+]?[1-9]\d{9,14}$`
   - Required for: `user` role

## 🛠️ Operations

### View Logs
```bash
# Keycloak instance logs
kubectl logs -f deployment/padmini-keycloak -n keycloak

# Configuration job logs  
kubectl logs job/keycloak-admin-config-job -n keycloak

# Operator logs
kubectl logs -f deployment/keycloak-operator -n keycloak
```

### Update Configuration
1. Modify configuration in `keycloak/admin-api-config/`
2. Commit changes to Git
3. ArgoCD will automatically sync and run the job

### Backup & Restore
- Database backups via PostgreSQL operator
- Realm export via Keycloak Admin API
- Configuration stored in Git

## 🔒 Security Considerations

- ✅ HTTPS enforced (SSL required: external)
- ✅ Brute force protection enabled
- ✅ Email verification required
- ✅ Secrets managed via Kubernetes secrets
- ✅ RBAC with roles and groups
- ⚠️ Change default client secrets in production
- ⚠️ Configure proper SMTP credentials

## 📞 Support

For issues and questions:
- Check ArgoCD application status
- Review job logs for configuration errors
- Verify secrets are properly configured
- Test authentication flows step by step

```
keycloak-ops/
├── .github/
│   └── workflows/
│       └── deploy-argocd-app.yaml      # GitHub Actions workflow for Keycloak operator
├── keycloak-operator/
│   └── kustomization.yaml              # Kustomize config with remote Keycloak resources
├── keycloak/
│   ├── instances/
│   │   └── production-keycloak.yaml    # Keycloak instance configuration
│   └── realms/
│       ├── padmini-realm-import.yaml   # Padmini Systems realm configuration
│       ├── kustomization.yaml          # Realm resources management
│       └── README.md                   # Realm setup documentation
├── argocd-apps/
│   ├── keycloak-operator-app.yaml      # ArgoCD application for operator
│   ├── keycloak-instance-app.yaml      # ArgoCD application for instance
│   └── keycloak-realm-app.yaml         # ArgoCD application for realm
├── docs/
│   ├── nextjs-integration.md           # Next.js integration guide
│   └── quarkus-integration.md          # Quarkus integration guide
├── scripts/
│   └── setup-realm.sh                  # Automated realm setup script
└── README.md                           # This documentation
```

### **Current Implementation Status**
- ✅ **Keycloak Operator**: Deployed using Kustomize with remote resources
- ✅ **Keycloak Instance**: Production-ready instance with PostgreSQL backend
- ✅ **Padmini Systems Realm**: Complete realm with two clients configured
- ✅ **ArgoCD Integration**: Automated deployment via ArgoCD
- ✅ **GitOps Workflow**: GitHub Actions with kubeconfig from secrets
- ✅ **Integration Guides**: Complete Next.js and Quarkus documentation

## 🚀 **Planned Enterprise Architecture**

### **Phase 1: Infrastructure Foundation** ✅ **COMPLETED**
- [x] Keycloak Operator deployment
- [x] Keycloak instance with PostgreSQL backend
- [x] Certificate management (TLS certificates)
- [x] Complete realm configuration for Padmini Systems

### **Phase 2: Application Integration** 🔄 **IN PROGRESS**
- [x] Padmini Systems realm with user registration
- [x] PPCS Web Application client (Next.js)
- [x] ASM Microservices client (Quarkus)
- [x] Custom user attributes (mobile number)
- [x] Username/email login support
- [ ] SMTP configuration for email verification
- [ ] Client secret rotation

### **Phase 3: Business Applications** 📋 **PLANNED**
- [ ] Next.js web application deployment
- [ ] Quarkus microservices deployment
- [ ] User onboarding flow implementation
- [ ] Business database integration

### **Phase 2: Keycloak Core Setup**
- [ ] padmini Keycloak instance
- [ ] High availability configuration
- [ ] Backup and disaster recovery
- [ ] TLS certificate configuration

### **Phase 3: Realm and User Management**
- [ ] Employee realm configuration
- [ ] Customer realm configuration
- [ ] Identity provider setup (Google, GitHub, LinkedIn)
- [ ] User import and group management

### **Phase 4: Application Integration**
- [ ] Internal application clients
- [ ] Customer application clients
- [ ] API gateway configuration
- [ ] Service mesh integration

## 🔐 **Keycloak Configuration Strategy**

### **Realm Structure** (Planned)
1. **Employee Realm**
   - Department-based groups (Engineering, Sales, HR, etc.)
   - Role-based access control (RBAC)
   - Internal application clients
   - Google/GitHub SSO for employees

2. **Customer Realm**
   - Subscription tier groups (Basic, Premium, Enterprise)
   - Service-based access permissions
   - Customer application clients
   - LinkedIn SSO for customers

### **Identity Providers** (Planned)
- **Google OAuth**: Primary SSO for employees
- **GitHub OAuth**: Developer access and code repositories
- **LinkedIn OAuth**: Customer authentication and professional verification

### **Client Applications** (Planned)
- **Internal Apps**: HR portal, project management, internal tools
- **Customer Apps**: Customer portal, service dashboard, billing system
- **API Gateway**: Secured API access with JWT tokens

## 🔧 **Current Technical Stack**

### **Core Infrastructure**
- **Kubernetes**: Container orchestration platform
- **ArgoCD**: GitOps continuous deployment
- **Keycloak Operator**: Kubernetes-native Keycloak management (v26.3.1)
- **Kustomize**: Remote resource management

### **CI/CD Pipeline**
- **GitHub Actions**: Automated deployment workflow
- **ArgoCD**: Application lifecycle management
- **Kustomize**: Configuration management

## 📋 **Prerequisites**

- Kubernetes cluster (v1.24+)
- ArgoCD installed and configured
- GitHub repository with webhook configured
- GitHub Actions secrets:
  - `PSYS_CENTOS_1_KUBE_CONFIG`: Base64 encoded kubeconfig

## 🛠️ **Current Usage**

### **Deployment**
The Keycloak operator is automatically deployed via GitHub Actions when changes are pushed to the main branch.

### **Manual Deployment**
```bash
# Apply ArgoCD application manually
kubectl apply -f argocd-apps/keycloak-operator-app.yaml

# Verify deployment
kubectl get pods -n keycloak
kubectl get crd | grep keycloak
```

### **Local Testing**
```bash
# Test Kustomize configuration
kubectl kustomize keycloak-operator --dry-run
```

## 📊 **Current Monitoring**

### **ArgoCD Dashboard**
- Application deployment status
- Sync history and rollback capabilities
- Resource health monitoring

### **Kubernetes Resources**
```bash
# Check operator status
kubectl get pods -n keycloak
kubectl get crd | grep keycloak
kubectl get keycloaks -n keycloak
```

## � **Quick Deployment Guide**

### **Deploy Padmini Systems Realm**

1. **Automatic Deployment (Recommended)**:
   ```bash
   # Run the setup script
   ./scripts/setup-realm.sh
   ```

2. **Manual Deployment**:
   ```bash
   # Apply realm configuration
   kubectl apply -f keycloak/realms/padmini-realm-import.yaml
   
   # Or deploy via ArgoCD
   kubectl apply -f argocd-apps/keycloak-realm-app.yaml
   ```

3. **Verify Deployment**:
   ```bash
   kubectl get keycloakrealmimport -n keycloak
   kubectl describe keycloakrealmimport padmini-realm-import -n keycloak
   ```

### **Post-Deployment Configuration**

1. **Access Keycloak Admin Console**: https://iam.padmini.systems
2. **Change Client Secret**: Update `asm-microservices` client secret
3. **Configure SMTP**: Set up email verification settings
4. **Test Registration**: Create a test user and verify email flow

### **Integration Setup**

- **Next.js**: See `docs/nextjs-integration.md`
- **Quarkus**: See `docs/quarkus-integration.md`
- **Realm Details**: See `keycloak/realms/README.md`

## �🔒 **Security Considerations**

- **Network Security**: All traffic encrypted with TLS
- **Secret Management**: Kubernetes secrets with client credentials
- **Access Control**: RBAC for all Kubernetes resources
- **Email Verification**: Required for user registration
- **Brute Force Protection**: Enabled with configurable limits

## 🚧 **Future Enhancements**

### **Infrastructure Components** (Planned)
- **PostgreSQL**: padmini database cluster
- **cert-manager**: Automated certificate management
- **Prometheus/Grafana**: Monitoring and alerting
- **Fluentd**: Log aggregation
- **Backup Solution**: Automated backups with encryption

### **Keycloak Features** (Planned)
- **High Availability**: Multi-instance Keycloak deployment
- **Federated Authentication**: OAuth providers integration
- **Advanced RBAC**: Hierarchical roles and permissions
- **API Security**: JWT token management
- **User Provisioning**: Automated user management

### **Application Integration** (Planned)
- **Internal Applications**: HR, project management, internal tools
- **Customer Applications**: Portal, dashboard, billing
- **API Gateway**: Secured API access
- **Service Mesh**: Advanced networking and security

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 **Support**

For questions and support:
- Create an issue in this repository
- Check the documentation in `/docs/` (planned)
- Review troubleshooting guide (planned)

## 📄 **License**

This project is licensed under the MIT License.

---

**Note**: This is an enterprise-grade setup in development. The current implementation provides the foundation for Keycloak operator deployment. Future phases will add padmini-grade features, security, and monitoring capabilities.
