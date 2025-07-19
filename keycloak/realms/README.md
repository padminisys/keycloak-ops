# Padmini Systems Keycloak Integration Guide

## Overview

This configuration sets up a complete Keycloak realm for Padmini Systems with two clients:
- **PPCS Web Application**: Public client for Next.js frontend
- **ASM Microservices**: Confidential clien### 2. Update Client Secret
⚠️ **IMPORTANT**: Change the default client secret for `asm-microservices`

1. Login to Keycloak Admin Console: `https://iam.padmini.systems`
2. Navigate to Realm: `padmini-systems`
3. Go to Clients → `asm-microservices`
4. Go to Credentials tab
5. Generate new secret or set custom secret
6. Update your Quarkus application configuration

### 3. Test Email Verificationd services

## Realm Configuration

**Realm Name**: `padmini-systems`
**Display Name**: Padmini Systems

### Key Features
- User registration enabled with email verification
- Login with username OR email
- Mobile number as required custom attribute
- International mobile number format support
- Secure token configuration
- Brute force protection enabled

## Clients Configuration

### 1. PPCS Web Application (Public Client)

**Client ID**: `ppcs-web-app`
- **Type**: Public (for Next.js frontend)
- **Grant Types**: Authorization Code + PKCE
- **Redirect URIs**: 
  - `http://localhost:3000/*` (development)
  - `https://ppcs.padmini.systems/*` (production)
  - `https://app.padmini.systems/*` (alternative production)

**Token Claims**:
- `sub`: User UUID (Keycloak ID)
- `preferred_username`: Username
- `email`: Email address
- `mobile`: Mobile number
- `name`: Full name (firstName + lastName)

### 2. ASM Microservices (Confidential Client)

**Client ID**: `asm-microservices`
- **Type**: Confidential (for Quarkus backend)
- **Client Secret**: `asm-microservices-secret-change-me` ⚠️ **CHANGE THIS**
- **Grant Types**: Authorization Code, Client Credentials, Direct Access
- **Service Account**: Enabled for service-to-service communication

## User Profile Configuration

### Required Fields for Registration
1. **Username**: 3-255 characters, alphanumeric with dots, underscores, hyphens
2. **Email**: Valid email format, used for verification
3. **First Name**: User's first name
4. **Last Name**: User's last name
5. **Mobile Number**: International format (e.g., +919876543210)

### Mobile Number Validation
- **Pattern**: `^[+]?[1-9]\\d{9,14}$`
- **Length**: 10-15 digits
- **Format**: International format with country code

## Integration Examples

### Next.js Frontend Integration

```javascript
// next-auth configuration example
import NextAuth from 'next-auth'
import KeycloakProvider from 'next-auth/providers/keycloak'

export default NextAuth({
  providers: [
    KeycloakProvider({
      clientId: 'ppcs-web-app',
      clientSecret: '', // Not needed for public client
      issuer: 'https://iam.padmini.systems/realms/padmini-systems',
    })
  ],
  callbacks: {
    async jwt({ token, account, profile }) {
      if (account) {
        token.accessToken = account.access_token
        token.mobile = profile.mobile
      }
      return token
    },
    async session({ session, token }) {
      session.accessToken = token.accessToken
      session.user.mobile = token.mobile
      session.user.sub = token.sub
      return session
    }
  }
})
```

### Quarkus Microservice Integration

```properties
# application.properties
quarkus.oidc.auth-server-url=https://iam.padmini.systems/realms/padmini-systems
quarkus.oidc.client-id=asm-microservices
quarkus.oidc.credentials.secret=asm-microservices-secret-change-me
quarkus.oidc.application-type=service
quarkus.oidc.token.verify-access-token-with-user-info=true
```

```java
// Example JAX-RS endpoint
@Path("/api/user")
@RolesAllowed("user")
public class UserResource {
    
    @Inject
    JsonWebToken jwt;
    
    @GET
    @Path("/profile")
    public UserProfile getUserProfile() {
        return UserProfile.builder()
            .userId(jwt.getSubject())
            .username(jwt.getClaim("preferred_username"))
            .email(jwt.getClaim("email"))
            .mobile(jwt.getClaim("mobile"))
            .name(jwt.getClaim("name"))
            .build();
    }
}
```

## Authentication Flow

### User Registration Flow
1. User visits web application
2. Clicks "Sign Up"
3. Redirected to Keycloak registration page
4. Fills required fields (username, email, name, mobile)
5. Keycloak sends verification email
6. User verifies email and activates account
7. User can now login

### User Login Flow
1. User visits web application
2. Clicks "Login"
3. Redirected to Keycloak login page
4. Can login with either username OR email + password
5. Keycloak returns authorization code
6. Frontend exchanges code for tokens
7. Frontend calls ASM API with access token
8. ASM validates token and processes onboarding

## Token Structure

### Access Token Claims
```json
{
  "sub": "uuid-keycloak-user-id",
  "preferred_username": "john.doe",
  "email": "john.doe@example.com",
  "mobile": "+919876543210",
  "name": "John Doe",
  "given_name": "John",
  "family_name": "Doe",
  "realm_access": {
    "roles": ["user"]
  },
  "resource_access": {
    "asm-microservices": {
      "roles": ["api-access"]
    }
  }
}
```

## Security Configuration

### Token Lifespans
- **Access Token**: 5 minutes (300 seconds)
- **Refresh Token**: 30 minutes (1800 seconds)
- **SSO Session**: 10 hours (36000 seconds)
- **Offline Session**: 30 days (2592000 seconds)

### Brute Force Protection
- **Max Failures**: 30 attempts
- **Max Wait Time**: 15 minutes
- **Quick Login Check**: 1 second

## Deployment Instructions

### 1. Apply the Realm Configuration
```bash
kubectl apply -f keycloak/realms/padmini-realm-import.yaml
```

### 2. Deploy via ArgoCD (Recommended)
```bash
kubectl apply -f argocd-apps/keycloak-realm-app.yaml
```

### 3. Verify Deployment
```bash
kubectl get keycloakrealmimport -n keycloak
kubectl describe keycloakrealmimport padmini-realm-import -n keycloak
```

## Post-Deployment Configuration

### 1. Configure SMTP for Email Verification

**Important**: SMTP credentials are stored in Kubernetes secrets, NOT in git.

#### Option A: Automated Setup (Recommended)
```bash
# Run the interactive SMTP setup script
./scripts/setup-smtp.sh
```

#### Option B: Manual Setup
```bash
# Create SMTP secret manually
kubectl create secret generic keycloak-smtp-secret \
  --namespace=keycloak \
  --from-literal=host="smtp.gmail.com" \
  --from-literal=port="587" \
  --from-literal=auth="true" \
  --from-literal=ssl="false" \
  --from-literal=starttls="true" \
  --from-literal=user="your-email@gmail.com" \
  --from-literal=password="your-app-password"

# Add labels
kubectl label secret keycloak-smtp-secret -n keycloak \
  app.kubernetes.io/name=keycloak-smtp \
  app.kubernetes.io/part-of=keycloak \
  app.kubernetes.io/component=smtp-config
```

#### Common SMTP Configurations

**Gmail (App Password Required)**:
- Host: `smtp.gmail.com`
- Port: `587` 
- SSL: `false`, STARTTLS: `true`
- Note: Use App Password, not regular password

**Outlook/Hotmail**:
- Host: `smtp-mail.outlook.com`
- Port: `587`
- SSL: `false`, STARTTLS: `true`

**AWS SES**:
- Host: `email-smtp.us-east-1.amazonaws.com`
- Port: `587`
- SSL: `false`, STARTTLS: `true`

### 2. Update Client Secret
⚠️ **IMPORTANT**: Change the default client secret for `asm-microservices`

1. Login to Keycloak Admin Console: `https://iam.padmini.systems`
2. Navigate to Realm: `padmini-systems`
3. Go to Clients → `asm-microservices`
4. Go to Credentials tab
5. Generate new secret or set custom secret
6. Update your Quarkus application configuration

### 2. Configure SMTP for Email Verification
1. Login to Keycloak Admin Console
2. Navigate to Realm Settings → Email
3. Configure your SMTP settings:
   - Host: Your SMTP server
   - Port: 587 (or 465 for SSL)
   - From: `noreply@padmini.systems`
   - Username/Password: SMTP credentials

### 3. Test Email Verification
1. Visit your Next.js application
2. Click "Sign Up"
3. Fill all required fields including mobile number
4. Check email for verification link
5. Complete verification and login

## Troubleshooting

### Common Issues

#### 1. Realm Import Failed
```bash
kubectl logs -n keycloak deployment/keycloak-operator
kubectl describe keycloakrealmimport padmini-realm-import -n keycloak
```

#### 2. Client Authentication Issues
- Verify client secret is correct
- Check redirect URIs match exactly
- Ensure HTTPS for production

#### 3. Token Validation Issues
- Verify issuer URL is correct
- Check client ID in token audience
- Ensure proper role mappings

### Verification Commands
```bash
# Check Keycloak status
kubectl get keycloak -n keycloak

# Check realm import status
kubectl get keycloakrealmimport -n keycloak

# Get Keycloak logs
kubectl logs -n keycloak -l app.kubernetes.io/name=keycloak

# Test token endpoint
curl https://iam.padmini.systems/realms/padmini-systems/.well-known/openid_configuration
```

## Integration Checklist

### Next.js Frontend
- [ ] Configure NextAuth.js with Keycloak provider
- [ ] Set up proper redirect URIs
- [ ] Implement token refresh logic
- [ ] Add mobile number to user profile display
- [ ] Handle registration redirects

### Quarkus Microservices
- [ ] Configure OIDC properties
- [ ] Set up role-based authorization
- [ ] Implement token validation
- [ ] Create user profile endpoints
- [ ] Add mobile number to business database schema

### Security
- [ ] Change default client secret
- [ ] Configure SMTP for email verification
- [ ] Test user registration flow
- [ ] Verify token claims contain required fields
- [ ] Test API authorization with tokens

## Support

For issues or questions:
1. Check Keycloak operator logs
2. Verify realm import status
3. Test with Keycloak admin console
4. Review client configuration

## URLs

- **Keycloak Admin**: https://iam.padmini.systems
- **Realm**: https://iam.padmini.systems/realms/padmini-systems
- **OIDC Discovery**: https://iam.padmini.systems/realms/padmini-systems/.well-known/openid_configuration
