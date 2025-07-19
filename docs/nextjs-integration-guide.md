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

**Expected JWT Claims after fix:**
```json
{
  "sub": "user-uuid-here",
  "preferred_username": "john.doe", 
  "given_name": "John",
  "family_name": "Doe",
  "name": "John Doe",
  "email": "john.doe@example.com",
  "email_verified": true,
  "mobile": "+919876543210"
}
```

## 🔍 Testing URLs

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
