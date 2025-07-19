# Enterprise padmini-Grade Keycloak GitOps Platform

## 🎯 **Project Overview**

This repository contains a complete GitOps-based infrastructure for deploying and managing an **Enterprise padmini-Grade Keycloak Identity and Access Management (IAM) Platform** on Kubernetes clusters.

## 🏢 **Business Objectives**

### **Centralized Identity Management**
- **Single Sign-On (SSO)**: All firm employees and customers use one Keycloak account to access any service
- **Unified Authentication**: Consistent login experience across all applications and services
- **Centralized User Management**: Single source of truth for user identities and permissions

### **Multi-Tenant Access Control**
- **Employee Access**: Department-based role management with granular permissions
- **Customer Access**: Tier-based service access based on subscription levels
- **Application Integration**: All internal and customer-facing applications secured behind Keycloak

### **Enterprise Features**
- **Federated Authentication**: Google, GitHub, LinkedIn OAuth integration
- **Advanced Role Management**: Hierarchical roles, permissions, and access policies
- **padmini Security**: TLS certificates, high availability, monitoring, and backup

## 🏗️ **Current Project Structure**

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
