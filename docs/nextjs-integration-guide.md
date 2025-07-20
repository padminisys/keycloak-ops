# NextJS Keycloak Integration Quick Reference

## 🔧 Updated Configuration Summary

After applying the updated realm configuration, your Keycloak setup will have:

### ✅ Fixed Issues
- ✅ Added essential OIDC scopes: `openid`, `profile`, `email`
- ✅ Fixed redirect URI format for NextAuth.js: `/api/auth/callback/keycloak`
- ✅ Added proper OIDC protocol mappers
- ✅ Configured client as public client with correct settings

### 🎯 Client Configuration (ppcs-web-app)
```yaml
Client ID: ppcs-web-app
Client Type: Public
Standard Flow: Enabled
Valid Redirect URIs: 
  - http://localhost:3000/api/auth/callback/keycloak
  - https://ppcs.padmini.systems/api/auth/callback/keycloak
Web Origins:
  - http://localhost:3000
  - https://ppcs.padmini.systems
```

### 🔑 Default Client Scopes
- `openid` - Essential for OIDC
- `profile` - User profile information
- `email` - Email address and verification status
- `web-origins` - CORS support
- `roles` - User roles
- `acr` - Authentication context

### 📋 Available Claims in JWT Token
```json
{
  "sub": "user-uuid",
  "preferred_username": "john.doe",
  "email": "john.doe@example.com", 
  "email_verified": true,
  "given_name": "John",
  "family_name": "Doe",
  "name": "John Doe",
  "mobile": "+919876543210"
}
```

## 🚀 NextJS Integration

### Environment Variables (.env.local)
```bash
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-random-secret-here

KEYCLOAK_ISSUER=https://iam.padmini.systems/realms/padmini-systems
KEYCLOAK_CLIENT_ID=ppcs-web-app
KEYCLOAK_CLIENT_SECRET=  # Leave empty for public client
```

### NextAuth.js Configuration Example
```typescript
// pages/api/auth/[...nextauth].ts or app/api/auth/[...nextauth]/route.ts
import NextAuth from "next-auth"
import KeycloakProvider from "next-auth/providers/keycloak"

export default NextAuth({
  providers: [
    KeycloakProvider({
      clientId: process.env.KEYCLOAK_CLIENT_ID!,
      clientSecret: process.env.KEYCLOAK_CLIENT_SECRET || "",
      issuer: process.env.KEYCLOAK_ISSUER,
      authorization: {
        params: {
          scope: "openid profile email mobile"
        }
      }
    })
  ],
  callbacks: {
    async jwt({ token, account, profile }) {
      if (account && profile) {
        token.mobile = profile.mobile
        token.accessToken = account.access_token
        token.userId = profile.sub
      }
      return token
    },
    async session({ session, token }) {
      session.accessToken = token.accessToken
      session.user.mobile = token.mobile
      session.user.id = token.userId
      return session
    }
  }
})
```

### Troubleshooting Step-by-Step Fix

**If you get "invalid_scope" error:**

1. **Use only `openid` scope first** to test basic connectivity:
   ```typescript
   scope: "openid"
   ```

2. **Once `openid` works, gradually add scopes:**
   ```typescript
   scope: "openid profile"  // Test this
   ```

3. **Then add email:**
   ```typescript
   scope: "openid profile email"  // Test this
   ```

4. **Finally add mobile:**
   ```typescript
   scope: "openid profile email mobile"  // Final scope
   ```

# NextJS Keycloak Integration Guide

## 🎯 Business Requirements Fulfilled

This configuration provides exactly what you need:
- **Name**: Full name (given_name, family_name, name)
- **Username**: Login identifier (preferred_username)
- **UUID**: User ID (sub)
- **Mobile**: Mobile number with country code (mobile)
- **Email**: Email address (email, email_verified)

## 🔧 Complete Admin API Configuration

This project uses **Admin API only** - no CRD limitations!

### ✅ What's Configured:
- ✅ Padmini Systems realm with all security settings
- ✅ Essential OIDC scopes: `openid`, `profile`, `email`, `mobile`
- ✅ NextJS public client (ppcs-web-app) 
- ✅ Microservices confidential client (asm-microservices)
- ✅ Protocol mappers for all business requirements
- ✅ SMTP configuration from secrets
- ✅ Default roles and groups

### 📋 Expected JWT Token Claims:
```json
{
  "sub": "user-uuid-here",
  "preferred_username": "ramanuj",
  "given_name": "Ramanuj", 
  "family_name": "Kumar",
  "name": "Ramanuj Kumar",
  "email": "ramanuj@padmini.systems",
  "email_verified": true,
  "mobile": "+919876543210"
}
```

## 🚀 NextJS Integration

### Environment Variables (.env.local)
```bash
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-random-secret-here

KEYCLOAK_ISSUER=https://iam.padmini.systems/realms/padmini-systems
KEYCLOAK_CLIENT_ID=ppcs-web-app
KEYCLOAK_CLIENT_SECRET=  # Leave empty for public client
```

### NextAuth.js Configuration
```typescript
// app/api/auth/[...nextauth]/route.ts
import NextAuth from "next-auth"
import KeycloakProvider from "next-auth/providers/keycloak"

export default NextAuth({
  providers: [
    KeycloakProvider({
      clientId: process.env.KEYCLOAK_CLIENT_ID!,
      clientSecret: process.env.KEYCLOAK_CLIENT_SECRET || "",
      issuer: process.env.KEYCLOAK_ISSUER,
      authorization: {
        params: {
          scope: "openid profile email mobile"
        }
      }
    })
  ],
  callbacks: {
    async jwt({ token, account, profile }) {
      if (account && profile) {
        token.mobile = profile.mobile
        token.accessToken = account.access_token
        token.userId = profile.sub
      }
      return token
    },
    async session({ session, token }) {
      session.accessToken = token.accessToken
      session.user.mobile = token.mobile
      session.user.id = token.userId
      return session
    }
  }
})
```

## 🔗 Test URLs

### 1. User Registration
```
https://iam.padmini.systems/realms/padmini-systems/protocol/openid-connect/registrations?client_id=ppcs-web-app&response_type=code&scope=openid%20profile%20email%20mobile&redirect_uri=http://localhost:3000/api/auth/callback/keycloak
```

### 2. User Login
```
https://iam.padmini.systems/realms/padmini-systems/protocol/openid-connect/auth?client_id=ppcs-web-app&response_type=code&scope=openid%20profile%20email%20mobile&redirect_uri=http://localhost:3000/api/auth/callback/keycloak
```

### 3. OIDC Discovery
```
https://iam.padmini.systems/realms/padmini-systems/.well-known/openid_configuration
```

## ⚠️  One Manual Step Required

After deployment, add mobile field to registration form:

1. Go to: **Keycloak Admin Console** → `https://iam.padmini.systems/admin`
2. Navigate to: **Realm Settings** → **User Profile** → **Attributes**
3. Click: **Create Attribute**
4. Configure:
   - **Name**: `mobile`
   - **Display name**: `Mobile Number`
   - **Validation**: `^[+]?[1-9]\d{9,14}$`
   - **Required for**: `user` role
   - **Permissions**: view=[admin,user], edit=[admin,user]

## 🛠️ Troubleshooting

### Issue: "Invalid scopes" error
**Solution**: Verify scopes are properly assigned in Keycloak Admin Console:
- Go to: **Clients** → **ppcs-web-app** → **Client Scopes**
- **Default scopes**: openid, profile, email
- **Optional scopes**: mobile

### Issue: Missing mobile in JWT
**Solution**: 
1. Verify mobile attribute exists in user profile
2. Check mobile scope has correct mapper
3. Ensure mobile scope is assigned to client

## 📦 Deployment Architecture

1. **Keycloak Operator**: Manages Keycloak instance
2. **PostgreSQL**: Database backend  
3. **Admin API Job**: Configures realm, clients, scopes
4. **SMTP Secrets**: Email configuration
5. **ArgoCD**: GitOps deployment management

## 🎯 Production Checklist

- [ ] Update client secrets for production
- [ ] Configure production redirect URIs  
- [ ] Set up proper SMTP configuration
- [ ] Add mobile field to user registration form
- [ ] Test complete authentication flow
- [ ] Verify JWT token contains all required claims

### Complete Authentication Flow Test

1. **User Registration URL with Mobile Collection:**
   ```
   https://iam.padmini.systems/realms/padmini-systems/protocol/openid-connect/registrations?client_id=ppcs-web-app&response_type=code&scope=openid%20profile%20email%20mobile&redirect_uri=http://localhost:3000/api/auth/callback/keycloak
   ```

2. **Registration Form Fields:**
   - Username
   - Email  
   - First Name
   - Last Name
   - **Mobile Number** (with validation pattern)

3. **NextJS Scope Configuration:**
   ```typescript
   scope: "openid profile email mobile"
   ```## 🔍 Testing URLs

### 1. Test Authentication URL
```
https://iam.padmini.systems/realms/padmini-systems/protocol/openid-connect/auth?client_id=ppcs-web-app&response_type=code&scope=openid%20profile%20email%20mobile&redirect_uri=http://localhost:3000/api/auth/callback/keycloak
```

### 2. OIDC Discovery Endpoint
```
https://iam.padmini.systems/realms/padmini-systems/.well-known/openid_configuration
```

### 3. User Registration URL
```
https://iam.padmini.systems/realms/padmini-systems/protocol/openid-connect/registrations?client_id=ppcs-web-app&response_type=code&scope=openid%20profile%20email&redirect_uri=http://localhost:3000/api/auth/callback/keycloak
```

## 🛠️ Troubleshooting

### Common Issues & Solutions

1. **"Invalid redirect URI"**
   - Ensure redirect URI in NextJS exactly matches Keycloak configuration
   - Format: `http://localhost:3000/api/auth/callback/keycloak`

2. **"Invalid scopes"**
   - Verify `openid`, `profile`, `email` are in Default Client Scopes
   - Check that custom `mobile` scope is in Optional Client Scopes

3. **CORS errors**
   - Ensure `http://localhost:3000` is in Web Origins
   - Verify `web-origins` scope is assigned

4. **Missing user information**
   - Check protocol mappers are configured correctly
   - Verify user attributes are set in Keycloak user profile

### Verification Steps
1. Run verification script: `./scripts/verify-nextjs-config.sh`
2. Check Keycloak Admin Console settings
3. Test authentication flow manually
4. Verify JWT token contains expected claims

## 📦 Required NextJS Dependencies

```bash
npm install next-auth
# or
npm install @keycloak/keycloak-js
```

## 🔐 Security Best Practices

1. **Never expose client secrets** (not needed for public clients)
2. **Use HTTPS in production** for all endpoints
3. **Validate JWT tokens** on the server side
4. **Implement proper session management**
5. **Use secure cookies** with appropriate flags

## 🎯 Production Checklist

- [ ] Update redirect URIs to production domains
- [ ] Configure HTTPS endpoints
- [ ] Set up proper CORS policies
- [ ] Implement token validation middleware
- [ ] Set up proper session storage
- [ ] Configure security headers
- [ ] Test user registration flow
- [ ] Test password reset flow
- [ ] Verify email verification works
