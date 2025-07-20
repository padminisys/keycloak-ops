# Quarkus Integration with Keycloak

This guide shows how to integrate Quarkus microservices with Keycloak for authentication and authorization.

## Configuration

### 1. Add Dependencies

```xml
<dependencies>
    <dependency>
        <groupId>io.quarkus</groupId>
        <artifactId>quarkus-oidc</artifactId>
    </dependency>
    <dependency>
        <groupId>io.quarkus</groupId>
        <artifactId>quarkus-security</artifactId>
    </dependency>
</dependencies>
```

### 2. Application Properties

```properties
# OIDC Configuration
quarkus.oidc.auth-server-url=https://iam.padmini.systems/realms/padmini-systems
quarkus.oidc.client-id=asm-microservices
quarkus.oidc.credentials.secret=<client-secret>

# Security Configuration
quarkus.oidc.verification-strategy=VERIFY_JWT_AUDIENCE
quarkus.oidc.token.audience=asm-microservices

# Role Mapping
quarkus.security.users.embedded.enabled=false
```

### 3. Secure Endpoints

```java
@Path("/api/users")
@RolesAllowed("user")
public class UserResource {
    
    @GET
    @RolesAllowed("admin")
    public List<User> getAllUsers() {
        // Admin only endpoint
    }
    
    @GET
    @Path("/profile")
    @RolesAllowed("user")
    public UserProfile getCurrentUser(@Context SecurityContext context) {
        String username = context.getUserPrincipal().getName();
        // Return user profile
    }
}
```

### 4. JWT Claims Access

```java
@Inject
JsonWebToken jwt;

public void processUser() {
    String userId = jwt.getSubject();
    String username = jwt.getClaim("preferred_username");
    String email = jwt.getClaim("email");
    String mobile = jwt.getClaim("mobile");
    String fullName = jwt.getClaim("name");
}
```

## Client Configuration in Keycloak

The `asm-microservices` client is configured with:
- **Access Type**: Confidential
- **Standard Flow**: Disabled
- **Service Account**: Enabled
- **Authorization**: Enabled

### Available Scopes
- `openid`
- `profile` 
- `email`
- `mobile`
- `roles`

### JWT Token Claims
```json
{
  "sub": "user-uuid",
  "preferred_username": "username",
  "given_name": "First",
  "family_name": "Last", 
  "name": "First Last",
  "email": "user@domain.com",
  "email_verified": true,
  "mobile": "+919876543210",
  "realm_access": {
    "roles": ["user", "admin"]
  }
}
```

## Testing

### 1. Get Access Token
```bash
curl -X POST \
  https://iam.padmini.systems/realms/padmini-systems/protocol/openid-connect/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=client_credentials&client_id=asm-microservices&client_secret=<secret>'
```

### 2. Call Protected Endpoint
```bash
curl -X GET \
  http://localhost:8080/api/users/profile \
  -H 'Authorization: Bearer <access-token>'
```

## Role-Based Access

### Define Roles in Keycloak
1. **Realm Roles**: `user`, `admin`, `manager`
2. **Client Roles**: `service-admin`, `api-access`

### Map Roles in Quarkus
```java
@RolesAllowed({"admin", "manager"})
@Path("/admin")
public class AdminResource {
    // Admin endpoints
}
```

## Best Practices

1. **Always validate JWT signatures**
2. **Use HTTPS in production**
3. **Implement proper error handling**
4. **Cache JWKS for performance**
5. **Use service accounts for service-to-service communication**
6. **Implement proper logging and monitoring**
